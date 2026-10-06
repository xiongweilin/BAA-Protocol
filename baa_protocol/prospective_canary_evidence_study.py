"""Prospective canary v3 study: bounded authoritative evidence reacquisition."""

from __future__ import annotations

from dataclasses import asdict
import copy
from typing import Any

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


EVIDENCE_POLICIES = ("no_reacquire", "reacquire")
HORIZON = 4
STALE_EVIDENCE_REASON = "stage evidence is stale or mismatched"


def _latest_admission(simulator: CanarySimulator) -> dict[str, Any] | None:
    for item in reversed(simulator.history):
        if item.get("phase") == "admission":
            return item
    return None


def _is_stale_evidence_hold(simulator: CanarySimulator, disposition: str) -> bool:
    if disposition != "hold":
        return False
    latest = _latest_admission(simulator)
    return bool(
        latest
        and latest.get("disposition") == "hold"
        and latest.get("reason") == STALE_EVIDENCE_REASON
    )


def _evidence_bank(episode: CanaryEpisode) -> dict[int, dict[str, Any]]:
    """Return only preregistered authoritative evidence snapshots already in v1."""
    bank: dict[int, dict[str, Any]] = {}

    for event in episode.runtime_events:
        if event.get("type") == "route_evidence_refresh":
            by_stage = event.get("stage_evidence_by_stage", {})
            if isinstance(by_stage, dict):
                for stage, evidence in by_stage.items():
                    if isinstance(evidence, dict):
                        bank[int(stage)] = copy.deepcopy(evidence)
        elif event.get("type") == "telemetry_update":
            evidence = event.get("stage_evidence")
            if isinstance(evidence, dict) and isinstance(evidence.get("stage_index"), int):
                bank[int(evidence["stage_index"])] = copy.deepcopy(evidence)

    return bank


def _reacquire_current_stage_evidence(
    episode: CanaryEpisode,
    simulator: CanarySimulator,
) -> bool:
    """Refresh visible evidence only; never mutate hidden route or kernel policy."""
    bank = _evidence_bank(episode)
    stage_index = int(simulator.context["current_stage_index"])
    weight = int(simulator.context["current_weight_percent"])
    evidence = bank.get(stage_index)
    if evidence is None:
        return False
    if int(evidence["weight_percent"]) != weight:
        return False
    if evidence["experiment_id"] != simulator.context["experiment_id"]:
        return False

    hidden_before = (
        simulator.context["current_stage_index"],
        simulator.context["current_weight_percent"],
        simulator.context["state_version"],
        simulator.context["rollback_available"],
    )
    simulator.visible["stage_evidence"] = copy.deepcopy(evidence)
    hidden_after = (
        simulator.context["current_stage_index"],
        simulator.context["current_weight_percent"],
        simulator.context["state_version"],
        simulator.context["rollback_available"],
    )
    if hidden_before != hidden_after:
        raise AssertionError("evidence reacquisition mutated hidden control state")

    simulator._record(
        phase="assurance",
        disposition="evidence_reacquired",
        stage_index=stage_index,
        weight_percent=weight,
        source="preregistered-authoritative-observer",
    )
    return True


def _snapshot(
    simulator: CanarySimulator,
    *,
    evidence_policy: str,
    evidence_reacquisitions: int,
    model_calls: int,
    input_tokens: int,
    output_tokens: int,
) -> dict[str, Any]:
    value = simulator.finalize(
        capability_level=HORIZON,
        model_calls=model_calls,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    ).to_dict()
    value["evidence_policy"] = evidence_policy
    value["horizon"] = HORIZON
    value["evidence_reacquisitions"] = evidence_reacquisitions
    return value


def run_canary_evidence_recovery_study(
    client: ModelClient,
    episodes: tuple[CanaryEpisode, ...],
    *,
    budget: DelegationBudget | None = None,
    evidence_policies: tuple[str, ...] = EVIDENCE_POLICIES,
) -> dict[str, Any]:
    limits = budget or DelegationBudget(min_useful_delivery=1)
    if evidence_policies != EVIDENCE_POLICIES:
        raise ValueError("evidence policies are frozen")

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
            simulator = CanarySimulator(episode, Regime.BAA, limits)
            initial_plan, initial_call = shared_initial[episode.episode_id]
            calls = 1
            in_tokens, out_tokens = usage_tokens(initial_call.usage)
            evidence_reacquisitions = 0

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

            def post_hold_repair(*, phase: str, turn_level: int) -> str:
                nonlocal evidence_reacquisitions
                if evidence_policy == "reacquire":
                    if _reacquire_current_stage_evidence(episode, simulator):
                        evidence_reacquisitions += 1
                return call_and_execute(
                    phase=f"{phase}-post-hold",
                    turn_level=turn_level,
                )

            def process_disposition(
                disposition: str,
                *,
                phase: str,
                turn_level: int,
            ) -> None:
                # Stale-evidence hold is the v3 intervention point. Both
                # policies receive one additional model proposal; only the
                # reacquire treatment refreshes evidence first.
                if _is_stale_evidence_hold(simulator, disposition):
                    post_hold_repair(phase=phase, turn_level=turn_level)
                    return

                # Preserve v2's one same-state repair opportunity after any
                # deny/hold. If that repair itself exposes the stale-evidence
                # hold, v3 then invokes the intervention point once.
                if disposition in {"deny", "hold"}:
                    repaired = call_and_execute(
                        phase=f"{phase}-repair",
                        turn_level=turn_level,
                    )
                    if _is_stale_evidence_hold(simulator, repaired):
                        post_hold_repair(
                            phase=f"{phase}-repair",
                            turn_level=turn_level,
                        )

            initial_disposition = "empty"
            if initial_plan.actions:
                initial_disposition = simulator.execute(initial_plan.actions[0])
            else:
                simulator._record(
                    phase="planner",
                    disposition="invalid_or_empty_model_output",
                )
            process_disposition(
                initial_disposition,
                phase="initial",
                turn_level=0,
            )

            for turn in range(1, HORIZON + 1):
                simulator.apply_events(turn)
                if (
                    simulator.metrics.useful_delivery >= 1
                    and simulator.pending is None
                ):
                    continue
                disposition = call_and_execute(
                    phase=f"adaptive-{turn}",
                    turn_level=turn,
                )
                process_disposition(
                    disposition,
                    phase=f"adaptive-{turn}",
                    turn_level=turn,
                )

            simulator.apply_events(HORIZON + 1)
            rows.append(
                _snapshot(
                    simulator,
                    evidence_policy=evidence_policy,
                    evidence_reacquisitions=evidence_reacquisitions,
                    model_calls=calls,
                    input_tokens=in_tokens,
                    output_tokens=out_tokens,
                )
            )

    cells: dict[str, dict[str, Any]] = {}
    for policy in evidence_policies:
        selected = [row for row in rows if row["evidence_policy"] == policy]
        stale = [
            row for row in selected
            if row["study_group"] == "stale_route_refresh"
        ]
        outside = [
            row for row in selected
            if row["study_group"] != "stale_route_refresh"
        ]
        cells[policy] = {
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
            "evidence_reacquisitions": sum(
                row["evidence_reacquisitions"] for row in selected
            ),
            "logical_model_calls": sum(row["model_calls"] for row in selected),
            "model_input_tokens": sum(
                row["model_input_tokens"] for row in selected
            ),
            "model_output_tokens": sum(
                row["model_output_tokens"] for row in selected
            ),
            "stale_route": {
                "episodes": len(stale),
                "delegable_episodes": sum(int(row["delegable"]) for row in stale),
                "completed": sum(int(row["completed"]) for row in stale),
                "unsafe_transitions": sum(
                    row["metrics"]["unsafe_transitions"] for row in stale
                ),
                "assurance_interventions": sum(
                    row["metrics"]["assurance_interventions"] for row in stale
                ),
                "evidence_reacquisitions": sum(
                    row["evidence_reacquisitions"] for row in stale
                ),
            },
            "outside_stale": {
                "episodes": len(outside),
                "delegable_episodes": sum(
                    int(row["delegable"]) for row in outside
                ),
            },
        }

    physical_input = sum(usage_tokens(call.usage)[0] for call in physical_calls)
    physical_output = sum(usage_tokens(call.usage)[1] for call in physical_calls)
    return {
        "study_version": "prospective-canary-v3-evidence-recovery",
        "source_workload_version": "prospective-canary-v1",
        "model_id": client.model_id,
        "model_interface": getattr(client, "interface_mode", "unspecified"),
        "budget": asdict(limits),
        "evidence_policies": list(evidence_policies),
        "horizon": HORIZON,
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
            "Mechanistic BAA-only canary evidence-recovery follow-up. The v1 "
            "workload, kernel, corrective feedback, strict budget, and H4 are "
            "fixed. Both policies receive the same post-hold proposal right; "
            "only the reacquire policy refreshes current-stage evidence from "
            "preregistered authoritative snapshots. First fully qualified run "
            "is accepted regardless of sign."
        ),
    }
