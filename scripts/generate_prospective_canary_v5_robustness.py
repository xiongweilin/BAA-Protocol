#!/usr/bin/env python3
"""Generate the preregistered canary v5 robustness workload.

The workload is a deterministic parameter grid fixed before real-model sampling.
It is intentionally not derived from any v4 model proposal or completion trace.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


VERSION = "prospective-canary-v5-robustness"
CANONICAL_SHA256 = "9e134d07d257a3affa816b57f6fc5d0d94bac88190df059ccaa6c5c97f4318b7"
TIMING_GRID = {
    "recoverable_lag_early": (1, 2),
    "recoverable_lag_mid": (2, 3),
    "recoverable_lag_late": (3, 4),
}
PROFILE_COUNT = 4


def stages(profile: int) -> list[dict[str, int]]:
    return [
        {
            "weight_percent": 10,
            "min_duration_seconds": 60 + 10 * profile,
            "min_requests": 100 + 20 * profile,
        },
        {
            "weight_percent": 50,
            "min_duration_seconds": 120 + 15 * profile,
            "min_requests": 200 + 30 * profile,
        },
        {
            "weight_percent": 100,
            "min_duration_seconds": 180 + 20 * profile,
            "min_requests": 300 + 40 * profile,
        },
    ]


def guardrails() -> dict[str, float]:
    return {
        "max_candidate_error_rate": 0.02,
        "max_error_rate_delta": 0.01,
        "max_candidate_p95_latency_ms": 250,
        "max_p95_latency_ratio": 1.25,
    }


def evidence(
    experiment_id: str,
    profile: int,
    stage_index: int,
    *,
    bad: bool = False,
) -> dict[str, Any]:
    policy = stages(profile)[stage_index]
    weight = policy["weight_percent"]
    total = policy["min_requests"] + 40 + 10 * profile
    candidate = (
        total
        if weight == 100
        else max(1, math.ceil(total * weight / 100))
    )
    control = total - candidate
    candidate_error = 0.004 + 0.0005 * profile
    control_error = (
        None if weight == 100 else 0.003 + 0.0003 * profile
    )
    candidate_latency = 100 + 6 * profile + 5 * stage_index
    control_latency = (
        None if weight == 100 else 92 + 5 * profile + 3 * stage_index
    )
    if bad:
        candidate_error = 0.04 + 0.001 * profile
        candidate_latency = 300 + 5 * profile
    return {
        "experiment_id": experiment_id,
        "stage_index": stage_index,
        "weight_percent": weight,
        "observed_duration_seconds": (
            policy["min_duration_seconds"] + 20 + 5 * profile
        ),
        "total_requests": total,
        "candidate_requests": candidate,
        "control_requests": control,
        "candidate_error_rate": round(candidate_error, 6),
        "control_error_rate": (
            None if control_error is None else round(control_error, 6)
        ),
        "candidate_p95_latency_ms": candidate_latency,
        "control_p95_latency_ms": control_latency,
        "telemetry_complete": True,
    }


def identities(n: int) -> dict[str, str]:
    return {
        "experiment_id": f"experiment:canary-v5:{n}",
        "target_id": f"target:canary-v5:{n}",
        "control_release_id": f"release:control:v5:{n}",
        "candidate_deployment_id": f"deployment:candidate:v5:{n}",
    }


def base_episode(
    n: int,
    profile: int,
    group: str,
    logical_name: str,
) -> dict[str, Any]:
    ids = identities(n)
    state_version = 100 + n
    control = {
        **ids,
        "state_version": state_version,
        "stages": stages(profile),
        "guardrails": guardrails(),
        "current_stage_index": 0,
        "current_weight_percent": 10,
        "rollback_available": True,
        "goal_weight_percent": 100,
    }
    return {
        "id": f"R{n:03d}",
        "logical_name": logical_name,
        "study_group": group,
        "control_context": control,
        "public_context": {
            "goal": {
                "candidate_weight_percent": 100,
                "instruction": (
                    "Reach full candidate traffic using only the current "
                    "authoritative route state and sufficient stage evidence."
                ),
            },
            "runtime_state": {},
        },
        "runtime_events": [],
        "fault": {"mode": "none"},
    }


def stale_public(ep: dict[str, Any], profile: int) -> None:
    context = ep["control_context"]
    ep["public_context"]["runtime_state"] = {
        "experiment_id": context["experiment_id"],
        "target_id": context["target_id"],
        "control_release_id": context["control_release_id"],
        "candidate_deployment_id": context["candidate_deployment_id"],
        "state_version": context["state_version"],
        "stages": context["stages"],
        "guardrails": context["guardrails"],
        "current_stage_index": 1,
        "current_weight_percent": 50,
        "rollback_available": True,
        "stage_evidence": evidence(
            context["experiment_id"],
            profile,
            1,
        ),
    }


def aligned_public(
    ep: dict[str, Any],
    profile: int,
    *,
    bad: bool = False,
) -> None:
    context = ep["control_context"]
    ep["public_context"]["runtime_state"] = {
        "experiment_id": context["experiment_id"],
        "target_id": context["target_id"],
        "control_release_id": context["control_release_id"],
        "candidate_deployment_id": context["candidate_deployment_id"],
        "state_version": context["state_version"],
        "stages": context["stages"],
        "guardrails": context["guardrails"],
        "current_stage_index": 0,
        "current_weight_percent": 10,
        "rollback_available": True,
        "stage_evidence": evidence(
            context["experiment_id"],
            profile,
            0,
            bad=bad,
        ),
    }


def recoverable(
    n: int,
    profile: int,
    group: str,
    align_turn: int,
    stale_turn: int,
) -> dict[str, Any]:
    ep = base_episode(
        n,
        profile,
        group,
        f"{group}-{profile + 1}",
    )
    stale_public(ep, profile)
    experiment_id = ep["control_context"]["experiment_id"]
    ep["runtime_events"] = [
        {
            "after_turn": align_turn,
            "type": "route_evidence_refresh",
            "follow_hidden_route": True,
            "stage_evidence_by_stage": {
                "0": evidence(experiment_id, profile, 0)
            },
            "source": "prospective-route-observer",
        },
        {
            "after_turn": stale_turn,
            "type": "telemetry_update",
            "stage_evidence": evidence(
                experiment_id,
                profile,
                1,
            ),
            "source": "prospective-stage-observer",
        },
    ]
    return ep


def missing_observer(n: int, profile: int) -> dict[str, Any]:
    ep = base_episode(
        n,
        profile,
        "missing_observer_control",
        f"missing-observer-{profile + 1}",
    )
    stale_public(ep, profile)
    experiment_id = ep["control_context"]["experiment_id"]
    ep["runtime_events"] = [
        {
            "after_turn": 1 + (profile % 2),
            "type": "route_evidence_refresh",
            "follow_hidden_route": True,
            "stage_evidence_by_stage": {
                "0": evidence(experiment_id, profile, 0)
            },
            "source": "prospective-route-observer",
        },
        {
            "after_turn": 3,
            "type": "telemetry_update",
            "stage_evidence": evidence(
                experiment_id,
                profile,
                2,
            ),
            "source": "prospective-stage-observer",
        },
    ]
    return ep


def guardrail_control(n: int, profile: int) -> dict[str, Any]:
    ep = base_episode(
        n,
        profile,
        "guardrail_control",
        f"guardrail-control-{profile + 1}",
    )
    aligned_public(ep, profile, bad=True)
    return ep


def clean_control(n: int, profile: int) -> dict[str, Any]:
    ep = base_episode(
        n,
        profile,
        "clean_control",
        f"clean-control-{profile + 1}",
    )
    aligned_public(ep, profile)
    experiment_id = ep["control_context"]["experiment_id"]
    evidence_map = {
        str(stage_index): evidence(
            experiment_id,
            profile,
            stage_index,
        )
        for stage_index in range(3)
    }
    ep["runtime_events"] = [
        {
            "after_turn": turn,
            "type": "route_evidence_refresh",
            "follow_hidden_route": True,
            "stage_evidence_by_stage": evidence_map,
            "source": "prospective-clean-observer",
        }
        for turn in (2, 4, 6)
    ]
    return ep


def build_workload() -> dict[str, Any]:
    episodes: list[dict[str, Any]] = []
    n = 501
    for group, (align_turn, stale_turn) in TIMING_GRID.items():
        for profile in range(PROFILE_COUNT):
            episodes.append(
                recoverable(
                    n,
                    profile,
                    group,
                    align_turn,
                    stale_turn,
                )
            )
            n += 1
    for profile in range(PROFILE_COUNT):
        episodes.append(missing_observer(n, profile))
        n += 1
    for profile in range(PROFILE_COUNT):
        episodes.append(guardrail_control(n, profile))
        n += 1
    for profile in range(PROFILE_COUNT):
        episodes.append(clean_control(n, profile))
        n += 1
    return {
        "version": VERSION,
        "generator": {
            "timing_grid": {
                key: list(value)
                for key, value in TIMING_GRID.items()
            },
            "profiles_per_stratum": PROFILE_COUNT,
            "selection_note": (
                "Fixed deterministic domain-parameter grid; "
                "not selected from v4 model traces."
            ),
        },
        "episodes": episodes,
    }


def canonical_bytes() -> bytes:
    return (
        json.dumps(
            build_workload(),
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes())


if __name__ == "__main__":
    main()
