"""Prospective canary v3: current-stage evidence availability under a fixed gate."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .canary_release import CanaryEvidence
from .delegation_frontier import DelegationBudget
from .experiment import Regime
from .prospective_canary_feedback_study import _adaptive_feedback_prompt
from .prospective_canary_study import (
    CanaryEpisode,
    CanarySimulator,
    _call,
    _initial_prompt,
)
from .prospective_types import AdaptiveResource, ModelCall, ModelClient, usage_tokens


EVIDENCE_POLICIES = ("latest_only", "versioned_current_stage")
HORIZONS = (4, 8)


class EvidenceRetentionSimulator(CanarySimulator):
    """BAA simulator with an assurance-side store of already observed evidence."""

    def __init__(
        self,
        episode: CanaryEpisode,
        budget: DelegationBudget,
        *,
        evidence_policy: str,
    ) -> None:
        if evidence_policy not in EVIDENCE_POLICIES:
            raise ValueError(f"unsupported evidence policy: {evidence_policy}")
        self.evidence_policy = evidence_policy
        self.evidence_store: dict[tuple[str, int, int], dict[str, Any]] = {}
        self.evidence_writes = 0
        self.evidence_retrievals = 0
        self.evidence_misses = 0
        self.evidence_events: list[dict[str, Any]] = []
        super().__init__(episode, Regime.BAA, budget)
        self._retain_visible_evidence(source="initial")

    @staticmethod
    def _evidence_key(raw: dict[str, Any]) -> tuple[str, int, int]:
        return (
            str(raw["experiment_id"]),
            int(raw["stage_index"]),
            int(raw["weight_percent"]),
        )

    def _retain_visible_evidence(self, *, source: str) -> None:
        raw = self.visible.get("stage_evidence")
        if not isinstance(raw, dict):
            return
        key = self._evidence_key(raw)
        previous = self.evidence_store.get(key)
        if previous != raw:
            self.evidence_store[key] = dict(raw)
            self.evidence_writes += 1
            self.evidence_events.append(
                {
                    "kind": "retain",
                    "source": source,
                    "stage_index": key[1],
                    "weight_percent": key[2],
                }
            )

    def apply_events(self, turn: int) -> None:
        super().apply_events(turn)
        self._retain_visible_evidence(source=f"turn:{turn}")

    def _evidence(self) -> CanaryEvidence | None:
        if self.evidence_policy == "latest_only":
            return super()._evidence()

        key = (
            str(self.context["experiment_id"]),
            int(self.visible["current_stage_index"]),
            int(self.visible["current_weight_percent"]),
        )
        raw = self.evidence_store.get(key)
        if raw is None:
            self.evidence_misses += 1
            self.evidence_events.append(
                {
                    "kind": "miss",
                    "stage_index": key[1],
                    "weight_percent": key[2],
                }
            )
            return None

        latest = self.visible.get("stage_evidence")
        if latest != raw:
            self.evidence_retrievals += 1
            self.evidence_events.append(
                {
                    "kind": "retrieve",
                    "stage_index": key[1],
                    "weight_percent": key[2],
                }
            )
        return CanaryEvidence(**raw)


def _snapshot(
    simulator: EvidenceRetentionSimulator,
    *,
    horizon: int,
    model_calls: int,
    input_tokens: int,
    output_tokens: int,
) -> dict[str, Any]:
    row = simulator.finalize(
        capability_level=horizon,
        model_calls=model_calls,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    ).to_dict()
    row["evidence_policy"] = simulator.evidence_policy
    row["horizon"] = horizon
    row["evidence_writes"] = simulator.evidence_writes
    row["evidence_retrievals"] = simulator.evidence_retrievals
    row["evidence_misses"] = simulator.evidence_misses
    row["evidence_events"] = list(simulator.evidence_events)
    return row


def run_canary_evidence_study(
    client: ModelClient,
    episodes: tuple[CanaryEpisode, ...],
    *,
    budget: DelegationBudget | None = None,
    evidence_policies: tuple[str, ...] = EVIDENCE_POLICIES,
    horizons: tuple[int, ...] = HORIZONS,
) -> dict[str, Any]:
    limits = budget or DelegationBudget(min_useful_delivery=1)
    if evidence_policies != EVIDENCE_POLICIES:
        raise ValueError("evidence policies are frozen")
    if horizons != HORIZONS:
        raise ValueError("horizons are frozen")

    initial_resource = AdaptiveResource(level=0, extra_turns=0)
    shared_initial: dict[str, tuple[Any, ModelCall]] = {
        episode.episode_id: _call(
            client,
            _initial_prompt(episode),
            episode=episode,
            capability=initial_resource,
            phase="initial-shared",
            regime=None,
        )
        for episode in episodes
    }
    physical_calls = [call for _, call in shared_initial.values()]
    adaptive_cache: dict[tuple[str, str, int, str], tuple[Any, ModelCall]] = {}
    rows: list[dict[str, Any]] = []

    for evidence_policy in evidence_policies:
        for episode in episodes:
            simulator = EvidenceRetentionSimulator(
                episode,
                limits,
                evidence_policy=evidence_policy,
            )
            initial_plan, initial_call = shared_initial[episode.episode_id]
            calls = 1
            in_tokens, out_tokens = usage_tokens(initial_call.usage)

            def call_and_execute(*, phase: str, turn_level: int) -> str:
                nonlocal calls, in_tokens, out_tokens
                prompt = _adaptive_feedback_prompt(
                    episode,
                    simulator,
                    feedback_policy="corrective",
                )
                cache_key = (episode.episode_id, phase, turn_level, prompt)
                cached = adaptive_cache.get(cache_key)
                if cached is None:
                    plan, call = _call(
                        client,
                        prompt,
                        episode=episode,
                        capability=AdaptiveResource(
                            level=turn_level,
                            extra_turns=turn_level,
                        ),
                        phase=phase,
                        regime=Regime.BAA,
                    )
                    adaptive_cache[cache_key] = (plan, call)
                    physical_calls.append(call)
                else:
                    plan, call = cached

                calls += 1
                a, b = usage_tokens(call.usage)
                in_tokens += a
                out_tokens += b
                if not plan.actions:
                    simulator._record(
                        phase="planner",
                        disposition="invalid_or_empty_model_output",
                    )
                    return "empty"
                return simulator.execute(plan.actions[0])

            initial_disposition = "empty"
            if initial_plan.actions:
                initial_disposition = simulator.execute(initial_plan.actions[0])
            else:
                simulator._record(
                    phase="planner",
                    disposition="invalid_or_empty_model_output",
                )

            if initial_disposition in {"deny", "hold"}:
                call_and_execute(phase="initial-repair", turn_level=0)

            completed_early = False
            snapshots_taken: set[int] = set()

            for turn in range(1, horizons[-1] + 1):
                simulator.apply_events(turn)
                if (
                    simulator.metrics.useful_delivery >= 1
                    and simulator.pending is None
                ):
                    completed_early = True

                if not completed_early:
                    disposition = call_and_execute(
                        phase=f"adaptive-{turn}",
                        turn_level=turn,
                    )
                    if disposition in {"deny", "hold"}:
                        call_and_execute(
                            phase=f"adaptive-{turn}-repair",
                            turn_level=turn,
                        )

                if turn in horizons:
                    simulator.apply_events(turn + 1)
                    rows.append(
                        _snapshot(
                            simulator,
                            horizon=turn,
                            model_calls=calls,
                            input_tokens=in_tokens,
                            output_tokens=out_tokens,
                        )
                    )
                    snapshots_taken.add(turn)

                if completed_early and len(snapshots_taken) < len(horizons):
                    continue

    cells: dict[str, dict[str, Any]] = {}
    for policy in evidence_policies:
        cells[policy] = {}
        for horizon in horizons:
            selected = [
                row for row in rows
                if row["evidence_policy"] == policy and row["horizon"] == horizon
            ]
            stale = [
                row for row in selected
                if row["study_group"] == "stale_route_refresh"
            ]
            non_stale = [
                row for row in selected
                if row["study_group"] != "stale_route_refresh"
            ]
            cells[policy][str(horizon)] = {
                "episodes": len(selected),
                "delegable_episodes": sum(int(row["delegable"]) for row in selected),
                "completed": sum(int(row["completed"]) for row in selected),
                "useful_delivery": sum(
                    row["metrics"]["useful_delivery"] for row in selected
                ),
                "unsafe_transitions": sum(
                    row["metrics"]["unsafe_transitions"] for row in selected
                ),
                "principal_attention": sum(
                    row["metrics"]["principal_attention"] for row in selected
                ),
                "terminal_unresolved_results": sum(
                    row["metrics"]["terminal_unresolved_results"] for row in selected
                ),
                "assurance_interventions": sum(
                    row["metrics"]["assurance_interventions"] for row in selected
                ),
                "logical_model_calls": sum(row["model_calls"] for row in selected),
                "model_input_tokens": sum(row["model_input_tokens"] for row in selected),
                "model_output_tokens": sum(row["model_output_tokens"] for row in selected),
                "evidence_writes": sum(row["evidence_writes"] for row in selected),
                "evidence_retrievals": sum(
                    row["evidence_retrievals"] for row in selected
                ),
                "evidence_misses": sum(row["evidence_misses"] for row in selected),
                "stale_route": {
                    "episodes": len(stale),
                    "delegable_episodes": sum(int(row["delegable"]) for row in stale),
                    "completed": sum(int(row["completed"]) for row in stale),
                    "unsafe_transitions": sum(
                        row["metrics"]["unsafe_transitions"] for row in stale
                    ),
                    "evidence_retrievals": sum(
                        row["evidence_retrievals"] for row in stale
                    ),
                },
                "non_stale": {
                    "episodes": len(non_stale),
                    "delegable_episodes": sum(
                        int(row["delegable"]) for row in non_stale
                    ),
                },
            }

    physical_input = sum(usage_tokens(call.usage)[0] for call in physical_calls)
    physical_output = sum(usage_tokens(call.usage)[1] for call in physical_calls)
    return {
        "study_version": "prospective-canary-v3-evidence",
        "source_workload_version": "prospective-canary-v1",
        "model_id": client.model_id,
        "model_interface": getattr(client, "interface_mode", "unspecified"),
        "budget": asdict(limits),
        "feedback_policy": "corrective",
        "evidence_policies": list(evidence_policies),
        "horizons": list(horizons),
        "physical_sampling": {
            "calls": len(physical_calls),
            "calls_with_errors": sum(int(call.error is not None) for call in physical_calls),
            "transport_errors": sum(
                int(call.error_stage == "transport") for call in physical_calls
            ),
            "schema_errors": sum(
                int(call.error_stage == "schema") for call in physical_calls
            ),
            "model_errors": sum(
                int(call.error_stage == "model") for call in physical_calls
            ),
            "input_tokens": physical_input,
            "output_tokens": physical_output,
        },
        "cells": cells,
        "episodes": rows,
        "qualification": (
            "Mechanistic BAA-only evidence-availability follow-up. The v1 workload, "
            "canary kernel, corrective feedback, action interface, event schedule, and "
            "strict budget remain fixed. Only assurance-side retention of already "
            "observed stage evidence varies."
        ),
    }
