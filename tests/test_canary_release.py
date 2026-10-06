import unittest

from baa_protocol.canary_release import (
    CanaryEvidence,
    CanaryGuardrails,
    CanaryReleaseKernel,
    CanaryStagePolicy,
    RouteKnowledge,
    TrafficProposal,
)
from baa_protocol.model import Decision


def kernel(*, rollback_available: bool = True) -> CanaryReleaseKernel:
    return CanaryReleaseKernel(
        experiment_id="experiment:1",
        target_id="target:1",
        control_release_id="release:0",
        candidate_deployment_id="deployment:1",
        stages=(
            CanaryStagePolicy(10, 60, 100),
            CanaryStagePolicy(50, 120, 200),
            CanaryStagePolicy(100, 180, 300),
        ),
        guardrails=CanaryGuardrails(
            max_candidate_error_rate=0.02,
            max_error_rate_delta=0.01,
            max_candidate_p95_latency_ms=250.0,
            max_p95_latency_ratio=1.25,
        ),
        state_version=7,
        rollback_available=rollback_available,
    )


def proposal(stage: int, weight: int, *, suffix: str = "") -> TrafficProposal:
    return TrafficProposal(
        proposal_id=f"p:{stage}:{suffix}",
        experiment_id="experiment:1",
        target_id="target:1",
        control_release_id="release:0",
        candidate_deployment_id="deployment:1",
        stage_index=stage,
        candidate_weight_percent=weight,
        state_version=7,
        operation_id=f"route:{stage}:{suffix}",
    )


def evidence(
    stage: int,
    weight: int,
    *,
    duration: int,
    total: int,
    candidate: int,
    control: int,
    candidate_error: float = 0.005,
    control_error: float | None = 0.004,
    candidate_p95: float = 100.0,
    control_p95: float | None = 95.0,
    telemetry_complete: bool = True,
) -> CanaryEvidence:
    return CanaryEvidence(
        experiment_id="experiment:1",
        stage_index=stage,
        weight_percent=weight,
        observed_duration_seconds=duration,
        total_requests=total,
        candidate_requests=candidate,
        control_requests=control,
        candidate_error_rate=candidate_error,
        control_error_rate=control_error,
        candidate_p95_latency_ms=candidate_p95,
        control_p95_latency_ms=control_p95,
        telemetry_complete=telemetry_complete,
    )


class CanaryReleaseKernelTests(unittest.TestCase):
    def test_progresses_10_50_100_with_verified_evidence(self):
        value = kernel()

        first = value.admit_increase(proposal(0, 10), evidence=None)
        self.assertEqual(first.decision, Decision.ADMIT)
        value.execute(first.capability)
        value.verify_route(
            first.capability,
            experiment_id="experiment:1",
            stage_index=0,
            candidate_weight_percent=10,
        )

        second = value.admit_increase(
            proposal(1, 50),
            evidence=evidence(0, 10, duration=60, total=100, candidate=10, control=90),
        )
        self.assertEqual(second.decision, Decision.ADMIT)
        value.execute(second.capability)
        value.verify_route(
            second.capability,
            experiment_id="experiment:1",
            stage_index=1,
            candidate_weight_percent=50,
        )

        third = value.admit_increase(
            proposal(2, 100),
            evidence=evidence(1, 50, duration=120, total=200, candidate=100, control=100),
        )
        self.assertEqual(third.decision, Decision.ADMIT)
        value.execute(third.capability)
        value.verify_route(
            third.capability,
            experiment_id="experiment:1",
            stage_index=2,
            candidate_weight_percent=100,
        )

        self.assertEqual(value.current_weight_percent, 100)
        self.assertEqual(value.current_stage_index, 2)
        self.assertEqual(value.route_knowledge, RouteKnowledge.VERIFIED)

    def test_cannot_skip_stage(self):
        value = kernel()
        result = value.admit_increase(proposal(2, 100), evidence=None)
        self.assertEqual(result.decision, Decision.DENY)

    def test_insufficient_evidence_holds_next_increase(self):
        value = kernel()
        first = value.admit_increase(proposal(0, 10), evidence=None)
        value.execute(first.capability)
        value.verify_route(
            first.capability,
            experiment_id="experiment:1",
            stage_index=0,
            candidate_weight_percent=10,
        )

        result = value.admit_increase(
            proposal(1, 50),
            evidence=evidence(0, 10, duration=30, total=50, candidate=5, control=45),
        )
        self.assertEqual(result.decision, Decision.HOLD)

    def test_incomplete_telemetry_holds(self):
        value = kernel()
        first = value.admit_increase(proposal(0, 10), evidence=None)
        value.execute(first.capability)
        value.verify_route(
            first.capability,
            experiment_id="experiment:1",
            stage_index=0,
            candidate_weight_percent=10,
        )
        result = value.admit_increase(
            proposal(1, 50),
            evidence=evidence(
                0,
                10,
                duration=60,
                total=100,
                candidate=10,
                control=90,
                telemetry_complete=False,
            ),
        )
        self.assertEqual(result.decision, Decision.HOLD)

    def test_guardrail_violation_denies_increase(self):
        value = kernel()
        first = value.admit_increase(proposal(0, 10), evidence=None)
        value.execute(first.capability)
        value.verify_route(
            first.capability,
            experiment_id="experiment:1",
            stage_index=0,
            candidate_weight_percent=10,
        )
        result = value.admit_increase(
            proposal(1, 50),
            evidence=evidence(
                0,
                10,
                duration=60,
                total=100,
                candidate=10,
                control=90,
                candidate_error=0.05,
            ),
        )
        self.assertEqual(result.decision, Decision.DENY)

    def test_scope_mismatch_denied(self):
        value = kernel()
        p = proposal(0, 10)
        p = TrafficProposal(
            **{**p.__dict__, "candidate_deployment_id": "deployment:other"}
        )
        self.assertEqual(value.admit_increase(p, evidence=None).decision, Decision.DENY)

    def test_stale_state_version_denied(self):
        value = kernel()
        p = proposal(0, 10)
        p = TrafficProposal(**{**p.__dict__, "state_version": 6})
        self.assertEqual(value.admit_increase(p, evidence=None).decision, Decision.DENY)

    def test_missing_rollback_path_holds_increase(self):
        value = kernel(rollback_available=False)
        result = value.admit_increase(proposal(0, 10), evidence=None)
        self.assertEqual(result.decision, Decision.HOLD)

    def test_unknown_apply_blocks_replay_and_next_stage(self):
        value = kernel()
        first = value.admit_increase(proposal(0, 10), evidence=None)
        value.execute(first.capability)
        value.mark_unknown()

        replay = value.admit_increase(proposal(0, 10, suffix="retry"), evidence=None)
        next_stage = value.admit_increase(proposal(1, 50), evidence=None)

        self.assertEqual(replay.decision, Decision.HOLD)
        self.assertEqual(next_stage.decision, Decision.HOLD)
        self.assertEqual(value.route_knowledge, RouteKnowledge.PENDING)

    def test_restore_is_allowed_from_unknown_and_must_be_verified(self):
        value = kernel()
        first = value.admit_increase(proposal(0, 10), evidence=None)
        value.execute(first.capability)
        value.mark_unknown()

        restore = value.admit_restore(operation_id="restore:1")
        self.assertEqual(restore.decision, Decision.ADMIT)
        value.execute_restore(restore.capability)
        value.verify_restored(candidate_weight_percent=0)

        self.assertEqual(value.current_weight_percent, 0)
        self.assertEqual(value.route_knowledge, RouteKnowledge.VERIFIED)

    def test_restore_without_viable_path_holds(self):
        value = kernel(rollback_available=False)
        result = value.admit_restore(operation_id="restore:1")
        self.assertEqual(result.decision, Decision.HOLD)


if __name__ == "__main__":
    unittest.main()
