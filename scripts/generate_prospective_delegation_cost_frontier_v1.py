#!/usr/bin/env python3
"""Generate the preregistered delegation cost-frontier v1 canary workload.

The workload is a deterministic cross-mechanism parameter grid fixed before
real-model sampling. It is not selected from any prior model trace.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


VERSION = "prospective-delegation-cost-frontier-v1"
CANONICAL_SHA256 = "2d4f57abe9be25cd4365009be5c5183ad63961cd2856701c1463c16d61897a29"
PROFILE_COUNT = 4
GROUPS = (
    "clean_control",
    "guardrail_control",
    "missing_observer_control",
    "stale_evidence_recovery",
    "lost_ack_recovery",
    "rollback_unavailable_control",
)


def stages(profile: int) -> list[dict[str, int]]:
    return [
        {
            "weight_percent": 10,
            "min_duration_seconds": 70 + 10 * profile,
            "min_requests": 120 + 20 * profile,
        },
        {
            "weight_percent": 50,
            "min_duration_seconds": 130 + 15 * profile,
            "min_requests": 220 + 30 * profile,
        },
        {
            "weight_percent": 100,
            "min_duration_seconds": 190 + 20 * profile,
            "min_requests": 320 + 40 * profile,
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
    total = policy["min_requests"] + 60 + 10 * profile
    candidate = total if weight == 100 else max(1, math.ceil(total * weight / 100))
    control = total - candidate
    candidate_error = 0.0045 + 0.0004 * profile
    control_error = None if weight == 100 else 0.003 + 0.0002 * profile
    candidate_latency = 105 + 7 * profile + 5 * stage_index
    control_latency = None if weight == 100 else 94 + 5 * profile + 3 * stage_index
    if bad:
        candidate_error = 0.045 + 0.001 * profile
        candidate_latency = 315 + 5 * profile
    return {
        "experiment_id": experiment_id,
        "stage_index": stage_index,
        "weight_percent": weight,
        "observed_duration_seconds": policy["min_duration_seconds"] + 25 + 5 * profile,
        "total_requests": total,
        "candidate_requests": candidate,
        "control_requests": control,
        "candidate_error_rate": round(candidate_error, 6),
        "control_error_rate": None if control_error is None else round(control_error, 6),
        "candidate_p95_latency_ms": candidate_latency,
        "control_p95_latency_ms": control_latency,
        "telemetry_complete": True,
    }


def identities(n: int) -> dict[str, str]:
    return {
        "experiment_id": f"experiment:cost-frontier-v1:{n}",
        "target_id": f"target:cost-frontier-v1:{n}",
        "control_release_id": f"release:control:cost-frontier-v1:{n}",
        "candidate_deployment_id": f"deployment:candidate:cost-frontier-v1:{n}",
    }


def base_episode(
    n: int,
    profile: int,
    group: str,
    logical_name: str,
) -> dict[str, Any]:
    ids = identities(n)
    state_version = 1000 + n
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
        "id": f"F{n:03d}",
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


def evidence_map(ep: dict[str, Any], profile: int) -> dict[str, dict[str, Any]]:
    experiment_id = ep["control_context"]["experiment_id"]
    return {
        str(stage_index): evidence(experiment_id, profile, stage_index)
        for stage_index in range(3)
    }


def aligned_public(
    ep: dict[str, Any],
    profile: int,
    *,
    bad: bool = False,
    rollback_available: bool = True,
) -> None:
    context = ep["control_context"]
    context["rollback_available"] = rollback_available
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
        "rollback_available": rollback_available,
        "stage_evidence": evidence(
            context["experiment_id"],
            profile,
            0,
            bad=bad,
        ),
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
        "stage_evidence": evidence(context["experiment_id"], profile, 1),
    }


def clean_control(n: int, profile: int) -> dict[str, Any]:
    ep = base_episode(n, profile, "clean_control", f"clean-control-{profile + 1}")
    aligned_public(ep, profile)
    mapping = evidence_map(ep, profile)
    ep["runtime_events"] = [
        {
            "after_turn": turn,
            "type": "route_evidence_refresh",
            "follow_hidden_route": True,
            "stage_evidence_by_stage": mapping,
            "source": "cost-frontier-clean-observer",
        }
        for turn in (2, 4, 6)
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


def missing_observer_control(n: int, profile: int) -> dict[str, Any]:
    ep = base_episode(
        n,
        profile,
        "missing_observer_control",
        f"missing-observer-control-{profile + 1}",
    )
    stale_public(ep, profile)
    experiment_id = ep["control_context"]["experiment_id"]
    ep["runtime_events"] = [
        {
            "after_turn": 1,
            "type": "route_readback",
            "source": "cost-frontier-route-observer",
        },
        {
            "after_turn": 2,
            "type": "observer_evidence_available",
            "stage_evidence": evidence(experiment_id, profile, 2),
            "source": "cost-frontier-wrong-stage-observer",
        },
    ]
    return ep


def stale_evidence_recovery(n: int, profile: int) -> dict[str, Any]:
    ep = base_episode(
        n,
        profile,
        "stale_evidence_recovery",
        f"stale-evidence-recovery-{profile + 1}",
    )
    stale_public(ep, profile)
    experiment_id = ep["control_context"]["experiment_id"]
    ep["runtime_events"] = [
        {
            "after_turn": 1,
            "type": "route_readback",
            "source": "cost-frontier-route-observer",
        },
        {
            "after_turn": 1,
            "type": "observer_evidence_available",
            "stage_evidence": evidence(experiment_id, profile, 0),
            "source": "cost-frontier-stage-observer",
        },
        {
            "after_turn": 3,
            "type": "observer_evidence_available",
            "stage_evidence": evidence(experiment_id, profile, 1),
            "source": "cost-frontier-stage-observer",
        },
    ]
    return ep


def lost_ack_recovery(n: int, profile: int) -> dict[str, Any]:
    ep = base_episode(
        n,
        profile,
        "lost_ack_recovery",
        f"lost-ack-recovery-{profile + 1}",
    )
    aligned_public(ep, profile)
    mapping = evidence_map(ep, profile)
    ep["fault"] = {"mode": "lost_confirmation_first_apply"}
    ep["runtime_events"] = [
        {
            "after_turn": 1,
            "type": "route_readback",
            "source": "cost-frontier-route-observer",
        },
        {
            "after_turn": 1,
            "type": "route_evidence_refresh",
            "follow_hidden_route": True,
            "stage_evidence_by_stage": mapping,
            "source": "cost-frontier-stage-observer",
        },
        {
            "after_turn": 3,
            "type": "route_evidence_refresh",
            "follow_hidden_route": True,
            "stage_evidence_by_stage": mapping,
            "source": "cost-frontier-stage-observer",
        },
    ]
    return ep


def rollback_unavailable_control(n: int, profile: int) -> dict[str, Any]:
    ep = base_episode(
        n,
        profile,
        "rollback_unavailable_control",
        f"rollback-unavailable-control-{profile + 1}",
    )
    aligned_public(ep, profile, rollback_available=False)
    return ep


def build_workload() -> dict[str, Any]:
    builders = (
        clean_control,
        guardrail_control,
        missing_observer_control,
        stale_evidence_recovery,
        lost_ack_recovery,
        rollback_unavailable_control,
    )
    episodes: list[dict[str, Any]] = []
    n = 701
    for builder in builders:
        for profile in range(PROFILE_COUNT):
            episodes.append(builder(n, profile))
            n += 1
    return {
        "version": VERSION,
        "generator": {
            "groups": list(GROUPS),
            "profiles_per_group": PROFILE_COUNT,
            "fixed_event_schedule": {
                "stale_evidence_recovery": {
                    "route_readback_turn": 1,
                    "stage0_observer_turn": 1,
                    "stage1_observer_turn": 3,
                },
                "lost_ack_recovery": {
                    "route_readback_turn": 1,
                    "route_evidence_refresh_turns": [1, 3],
                },
            },
            "selection_note": (
                "Fixed deterministic cross-mechanism parameter grid; "
                "not selected from prior model proposals or completion traces."
            ),
        },
        "episodes": episodes,
    }


def canonical_bytes() -> bytes:
    return (json.dumps(build_workload(), indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes())


if __name__ == "__main__":
    main()
