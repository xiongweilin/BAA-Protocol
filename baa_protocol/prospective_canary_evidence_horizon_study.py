"""Prospective canary v4: evidence reacquisition by adaptive horizon."""

from __future__ import annotations

from dataclasses import asdict
import copy
from typing import Any

from .delegation_frontier import DelegationBudget
from .experiment import Regime
from .prospective_canary_evidence_study import (
    EVIDENCE_POLICIES,
    _is_stale_evidence_hold,
    _reacquire_current_stage_evidence,
)
from .prospective_canary_feedback_study import _adaptive_feedback_prompt
from .prospective_canary_study import (
    CanaryEpisode,
    CanarySimulator,
    _call,
    _initial_prompt,
)
from .prospective_types import AdaptiveResource, ModelCall, ModelClient, usage_tokens


HORIZONS = (4, 8)


def _snapshot(
    simulator: CanarySimulator,
    *,
    evidence_policy: str,
    horizon: int,
    evidence_reacquisitions: int,
    model_calls: int,
    input_tokens: int,
    output_tokens: int,
) -> dict[str, Any]:
    """Score one frozen prefix without mutating the continuing trajectory."""
    frozen = copy.deepcopy(simulator)
    row = frozen.finalize(
        capability_level=horizon,
        model_calls=model_calls,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    ).to_dict()
    row["evidence_policy"] = evidence_policy
    row["horizon"] = horizon
    row["evidence_reacquisitions"] = evidence_reacquisitions
    return row


def _summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    stale = [
        row for row in rows
        if row["study_group"] == "stale_route_refresh"
    ]
    non_stale = [
        row for row in rows
        if row["study_group"] != "stale_route_refresh"
    ]
    return {
        "episodes": len(rows),
        "delegable_episodes": sum(int(row["delegable"]) for row in rows),
        "completed": sum(int(row["completed"]) for row in rows),
        "useful_delivery": sum(
            row["metrics"]["useful_delivery"] for row in rows
        ),
        "unsafe_transitions": sum(
            row["metrics"]["unsafe_transitions"] for row in rows
        ),
        "principal_attention": sum(
            row["metrics"]["principal_attention"] for row in rows
        ),
        "terminal_unresolved_results": sum(
            row["metrics"]["terminal_unresolved_results"] for row in rows
        ),
        "assurance_interventions": sum(
            row["metrics"]["assurance_interventions"] for row in rows
        ),
        "evidence_reacquisitions": sum(
            row["evidence_reacquisitions"] for row in rows
        ),
        "logical_model_calls": sum(row["model_calls"] for row in rows),
        "model_input_tokens": sum(
            row["model_input_tokens"] for row in rows
        ),
        "model_output_tokens": sum(
            row["model_output_tokens"] for row in rows
        ),
        "stale_route": {
            "episodes": len(stale),
            "delegable_episodes": sum(
                int(row["delegable"]) for row in stale
            ),
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
        "non_stale": {
            "episodes": len(non_stale),
            "delegable_episodes": sum(
                int(row["delegable"]) for row in non_stale
            ),
        },
    }


def run_canary_evidence_horizon_study(
    client: ModelClient,
    episodes: tuple[CanaryEpisode, ...],
    *,
    budget: DelegationBudget | None = None,
    evidence_policies: tuple[str, ...] = EVIDENCE_POLICIES,
    horizons: tuple[int, ...] = HORIZONS,
) -> dict[str, Any]:
    """Run the frozen 2x2 evidence-recovery by horizon mechanism study."""
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
    adaptive_cache: dict[
        tuple[str, str, int, str],
        tuple[Any, ModelCall],
    ] = {}
    rows: list[dict[str, Any]] = []

    for evidence_policy in evidence_policies:
        for episode in episodes:
            simulator = CanarySimulator(episode, Regime.BAA, limits)
            initial_plan, initial_call = shared_initial[episode.episode_id]
            calls = 1
            in_tokens, out_tokens = usage_tokens(initial_call.usage)
            evidence_reacquisitions = 0

            def call_and_execute(
                *,
                phase: str,
                turn_level: int,
                feedback_policy: str = "corrective",
            ) -> str:
                nonlocal calls, in_tokens, out_tokens
                prompt = _adaptive_feedback_prompt(
                    episode,
                    simulator,
                    feedback_policy=feedback_policy,
                )
                cache_key = (
                    episode.episode_id,
                    phase,
                    turn_level,
                    prompt,
                )
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

            def post_stale_hold(
                *,
                phase: str,
                turn_level: int,
            ) -> None:
                nonlocal evidence_reacquisitions
                # Preserve v3 exactly: each exact stale-evidence hold may
                # trigger one bounded current-route read before the same
                # post-hold proposal right. Longer horizon may therefore
                # encounter another later hold after a verified route change.
                if (
                    evidence_policy == "reacquire"
                    and _reacquire_current_stage_evidence(
                        episode,
                        simulator,
                        through_turn=turn_level,
                    )
                ):
                    evidence_reacquisitions += 1

                # Both policies keep the same post-hold proposal right.
                call_and_execute(
                    phase=f"{phase}-post-hold",
                    turn_level=turn_level,
                    feedback_policy="diagnostic",
                )

            def process_disposition(
                disposition: str,
                *,
                phase: str,
                turn_level: int,
            ) -> None:
                if _is_stale_evidence_hold(simulator, disposition):
                    post_stale_hold(
                        phase=phase,
                        turn_level=turn_level,
                    )
                    return

                if disposition in {"deny", "hold"}:
                    repaired = call_and_execute(
                        phase=f"{phase}-repair",
                        turn_level=turn_level,
                    )
                    if _is_stale_evidence_hold(simulator, repaired):
                        post_stale_hold(
                            phase=f"{phase}-repair",
                            turn_level=turn_level,
                        )

            initial_disposition = "empty"
            if initial_plan.actions:
                initial_disposition = simulator.execute(
                    initial_plan.actions[0]
                )
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

            for turn in range(1, HORIZONS[-1] + 1):
                simulator.apply_events(turn)

                if not (
                    simulator.metrics.useful_delivery >= 1
                    and simulator.pending is None
                ):
                    disposition = call_and_execute(
                        phase=f"adaptive-{turn}",
                        turn_level=turn,
                    )
                    process_disposition(
                        disposition,
                        phase=f"adaptive-{turn}",
                        turn_level=turn,
                    )

                if turn in HORIZONS:
                    # Preserve the historical endpoint convention: an event
                    # scheduled immediately after the last adaptive turn is
                    # visible at the frozen horizon even though no later
                    # proposal is credited to that horizon.
                    simulator.apply_events(turn + 1)
                    rows.append(
                        _snapshot(
                            simulator,
                            evidence_policy=evidence_policy,
                            horizon=turn,
                            evidence_reacquisitions=evidence_reacquisitions,
                            model_calls=calls,
                            input_tokens=in_tokens,
                            output_tokens=out_tokens,
                        )
                    )

    cells: dict[str, dict[str, Any]] = {}
    for policy in evidence_policies:
        cells[policy] = {}
        for horizon in horizons:
            selected = [
                row for row in rows
                if (
                    row["evidence_policy"] == policy
                    and row["horizon"] == horizon
                )
            ]
            cells[policy][str(horizon)] = _summarize(selected)

    def stale(policy: str, horizon: int) -> int:
        return int(
            cells[policy][str(horizon)]["stale_route"][
                "delegable_episodes"
            ]
        )

    h4, h8 = HORIZONS
    contrast_h4 = stale("reacquire", h4) - stale("no_reacquire", h4)
    contrast_h8 = stale("reacquire", h8) - stale("no_reacquire", h8)
    interaction = contrast_h8 - contrast_h4

    physical_input = sum(
        usage_tokens(call.usage)[0] for call in physical_calls
    )
    physical_output = sum(
        usage_tokens(call.usage)[1] for call in physical_calls
    )
    return {
        "study_version": "prospective-canary-v4-evidence-horizon",
        "source_workload_version": "prospective-canary-v1",
        "model_id": client.model_id,
        "model_interface": getattr(
            client,
            "interface_mode",
            "unspecified",
        ),
        "budget": asdict(limits),
        "feedback_policy": "corrective",
        "evidence_policies": list(evidence_policies),
        "horizons": list(horizons),
        "endpoints": {
            "stale_reacquire_contrast_h4": contrast_h4,
            "stale_reacquire_contrast_h8": contrast_h8,
            "stale_evidence_horizon_interaction": interaction,
        },
        "physical_sampling": {
            "calls": len(physical_calls),
            "calls_with_errors": sum(
                int(call.error is not None)
                for call in physical_calls
            ),
            "transport_errors": sum(
                int(call.error_stage == "transport")
                for call in physical_calls
            ),
            "schema_errors": sum(
                int(call.error_stage == "schema")
                for call in physical_calls
            ),
            "model_errors": sum(
                int(call.error_stage == "model")
                for call in physical_calls
            ),
            "input_tokens": physical_input,
            "output_tokens": physical_output,
        },
        "cells": cells,
        "episodes": rows,
        "qualification": (
            "Preregistered canary v4 2x2 mechanism study. The v1 workload, "
            "kernel, guardrails, submit_canary_proposal interface, corrective "
            "feedback, strict budget, observer corpus, and bounded one-read "
            "evidence intervention remain fixed. The factors are evidence "
            "policy (no_reacquire/reacquire) and adaptive horizon (H4/H8). "
            "H4 is a frozen prefix snapshot of the same H8 trajectory, not "
            "an independently resampled cell."
        ),
    }
