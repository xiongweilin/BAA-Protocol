import unittest

from autonomous_development.adapters.runtime_bound import RuntimeBoundTrafficDirector
from autonomous_development.domain.canary import (
    CanaryGuardrails as AIOSGuardrails,
    CanaryStageEvidence,
    evaluate_canary_stage,
)
from autonomous_development.domain.enums import CanaryDecisionKind
from autonomous_development.domain.models import CanaryStage, Experiment
from autonomous_development.ports.traffic import TrafficRouteState, TrafficSplit

from baa_protocol.canary_release import (
    CanaryEvidence,
    CanaryGuardrails,
    CanaryReleaseKernel,
    CanaryStagePolicy,
    TrafficProposal,
)
from baa_protocol.model import Decision


def aios_experiment() -> Experiment:
    return Experiment(
        id="experiment:1",
        target_id="target:1",
        control_release_id="release:0",
        candidate_deployment_id="deployment:1",
        stages=(
            CanaryStage(10, 60, 100),
            CanaryStage(50, 120, 200),
            CanaryStage(100, 180, 300),
        ),
        current_stage_index=0,
    )


def baa_kernel() -> CanaryReleaseKernel:
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
        guardrails=CanaryGuardrails(0.02, 0.01, 250.0, 1.25),
        state_version=7,
        rollback_available=True,
    )


def expose_first_stage(value: CanaryReleaseKernel) -> None:
    proposal = TrafficProposal(
        proposal_id="p:first",
        experiment_id="experiment:1",
        target_id="target:1",
        control_release_id="release:0",
        candidate_deployment_id="deployment:1",
        stage_index=0,
        candidate_weight_percent=10,
        state_version=7,
        operation_id="route:first",
    )
    admitted = value.admit_increase(proposal, evidence=None)
    assert admitted.capability is not None
    value.execute(admitted.capability)
    value.verify_route(
        admitted.capability,
        experiment_id="experiment:1",
        stage_index=0,
        candidate_weight_percent=10,
    )


def next_proposal() -> TrafficProposal:
    return TrafficProposal(
        proposal_id="p:second",
        experiment_id="experiment:1",
        target_id="target:1",
        control_release_id="release:0",
        candidate_deployment_id="deployment:1",
        stage_index=1,
        candidate_weight_percent=50,
        state_version=7,
        operation_id="route:second",
    )


def evidence(*, duration=60, total=100, candidate=10, control=90, candidate_error=0.005, complete=True):
    aios = CanaryStageEvidence(
        experiment_id="experiment:1",
        stage_index=0,
        weight_percent=10,
        observed_duration_seconds=duration,
        total_requests=total,
        candidate_requests=candidate,
        control_requests=control,
        candidate_error_rate=candidate_error,
        control_error_rate=0.004,
        candidate_p95_latency_ms=100.0,
        control_p95_latency_ms=95.0,
        evidence_refs=("evidence:canary:1",),
        telemetry_complete=complete,
    )
    baa = CanaryEvidence(
        experiment_id=aios.experiment_id,
        stage_index=aios.stage_index,
        weight_percent=aios.weight_percent,
        observed_duration_seconds=aios.observed_duration_seconds,
        total_requests=aios.total_requests,
        candidate_requests=aios.candidate_requests,
        control_requests=aios.control_requests,
        candidate_error_rate=aios.candidate_error_rate,
        control_error_rate=aios.control_error_rate,
        candidate_p95_latency_ms=aios.candidate_p95_latency_ms,
        control_p95_latency_ms=aios.control_p95_latency_ms,
        telemetry_complete=aios.telemetry_complete,
    )
    return aios, baa


class CanaryContractTests(unittest.TestCase):
    def test_01_stage_contract_projects_exactly(self):
        experiment = aios_experiment()
        value = baa_kernel()
        self.assertEqual(
            tuple((s.weight_percent, s.min_duration_seconds, s.min_requests) for s in experiment.stages),
            tuple((s.weight_percent, s.min_duration_seconds, s.min_requests) for s in value.stages),
        )

    def test_02_sufficient_evidence_agrees_on_advance(self):
        experiment = aios_experiment()
        ai, baa = evidence()
        decision = evaluate_canary_stage(
            experiment,
            ai,
            AIOSGuardrails(0.02, 0.01, 250.0, 1.25),
        )
        self.assertEqual(decision.kind, CanaryDecisionKind.ADVANCE)

        value = baa_kernel()
        expose_first_stage(value)
        admission = value.admit_increase(next_proposal(), evidence=baa)
        self.assertEqual(admission.decision, Decision.ADMIT)

    def test_03_insufficient_evidence_agrees_on_hold(self):
        experiment = aios_experiment()
        ai, baa = evidence(duration=20, total=40, candidate=4, control=36)
        decision = evaluate_canary_stage(
            experiment,
            ai,
            AIOSGuardrails(0.02, 0.01, 250.0, 1.25),
        )
        self.assertEqual(decision.kind, CanaryDecisionKind.HOLD)

        value = baa_kernel()
        expose_first_stage(value)
        admission = value.admit_increase(next_proposal(), evidence=baa)
        self.assertEqual(admission.decision, Decision.HOLD)

    def test_04_guardrail_failure_blocks_increase_when_aios_rolls_back(self):
        experiment = aios_experiment()
        ai, baa = evidence(candidate_error=0.05)
        decision = evaluate_canary_stage(
            experiment,
            ai,
            AIOSGuardrails(0.02, 0.01, 250.0, 1.25),
        )
        self.assertEqual(decision.kind, CanaryDecisionKind.ROLLBACK)

        value = baa_kernel()
        expose_first_stage(value)
        admission = value.admit_increase(next_proposal(), evidence=baa)
        self.assertEqual(admission.decision, Decision.DENY)
        self.assertEqual(value.admit_restore(operation_id="rollback:1").decision, Decision.ADMIT)


class FakeBridge:
    def __init__(self):
        self.calls = []

    def execute_external_effect(self, **kwargs):
        self.calls.append(kwargs)
        return kwargs["invoke"]()


class FakeTraffic:
    def apply(self, split):
        return TrafficRouteState(
            experiment_id=split.experiment_id,
            stage_index=split.stage_index,
            candidate_weight_percent=split.candidate_weight_percent,
            generation=1,
            evidence_ref="evidence:route:apply",
            target_id=split.target_id,
            control_release_id=split.control_release_id,
            candidate_deployment_id=split.candidate_deployment_id,
        )

    def restore_control(self, **kwargs):
        return TrafficRouteState(
            experiment_id=kwargs["experiment_id"],
            stage_index=kwargs["stage_index"],
            candidate_weight_percent=0,
            generation=2,
            evidence_ref="evidence:route:restore",
        )

    def read_current(self):
        return None


class RuntimeTrafficCapabilityTests(unittest.TestCase):
    def test_05_aios_apply_and_restore_use_expected_capabilities(self):
        bridge = FakeBridge()
        director = RuntimeBoundTrafficDirector(bridge, FakeTraffic(), target_id="target:1")
        split = TrafficSplit(
            experiment_id="experiment:1",
            stage_index=0,
            control_base_url="http://127.0.0.1:4100",
            candidate_base_url="http://127.0.0.1:4200",
            candidate_weight_percent=10,
            operation_id="apply:1",
            target_id="target:1",
            control_release_id="release:0",
            candidate_deployment_id="deployment:1",
        )
        director.apply(split)
        director.restore_control(
            experiment_id="experiment:1",
            stage_index=0,
            control_base_url="http://127.0.0.1:4100",
            candidate_base_url="http://127.0.0.1:4200",
            operation_id="restore:1",
        )
        self.assertEqual(
            [call["capability"] for call in bridge.calls],
            ["development.traffic.apply", "development.traffic.restore"],
        )
        self.assertEqual(
            [call["resource"] for call in bridge.calls],
            ["traffic:target:1", "traffic:target:1"],
        )


if __name__ == "__main__":
    unittest.main()
