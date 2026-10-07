"""Finite-state structural model checker for the BAA reference protocol.

The checker proves invariants only for the finite abstract universe declared
below and only under OMEGA_FORMAL_V1. It is not a proof about arbitrary real
deployments, model semantics, or effects outside the represented interface.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class Phase(str, Enum):
    PROPOSED = "proposed"
    DENIED = "denied"
    HELD = "held"
    RESERVED = "reserved"
    PENDING = "pending"
    SETTLED = "settled"


@dataclass(frozen=True)
class ProposalSpec:
    proposal_id: str
    object_id: str
    operation: str
    quota: int
    exposure_bound: int
    risk_factor: str
    expires_at: int = 2
    state_version: int = 1
    protected_source: bool = False
    verification_available: bool = True
    bridge_valid: bool = True
    fallback_viable: bool = True
    composition_bounded: bool = True


@dataclass(frozen=True)
class FormalState:
    phases: tuple[Phase, ...]
    settled_exposure: tuple[int, ...]

    @classmethod
    def initial(cls, proposal_count: int) -> "FormalState":
        return cls(
            phases=(Phase.PROPOSED,) * proposal_count,
            settled_exposure=(-1,) * proposal_count,
        )


@dataclass(frozen=True)
class Action:
    kind: str
    slot: int
    object_id: str | None = None
    operation: str | None = None
    amount: int | None = None
    now: int | None = None
    state_version: int | None = None
    realized_exposure: int | None = None


@dataclass(frozen=True)
class Transition:
    before: FormalState
    action: Action
    after: FormalState
    accepted: bool
    capability_issued: bool
    reason: str


@dataclass(frozen=True)
class ModelCheckReport:
    reachable_states: int
    explored_transitions: int
    invariants: tuple[str, ...]
    omega: tuple[str, ...]


class InvariantViolation(AssertionError):
    def __init__(self, name: str, transition: Transition | None, detail: str):
        super().__init__(f"{name}: {detail}")
        self.name = name
        self.transition = transition
        self.detail = detail


OMEGA_FORMAL_V1 = (
    "the executor is the complete mediation path for represented actions",
    "proposal scope and exposure bounds are immutable after admission",
    "realized exposure used for settlement is non-negative and no greater than the declared bound",
    "protected guarantee sources are exactly the objects marked protected_source",
    "the declared joint-risk functional is the risk quantity being guaranteed",
    "no unmodelled external transition mutates the represented ledger",
)

INVARIANTS_FORMAL_V1 = (
    "capability_scope_non_expansion",
    "ledger_category_exclusivity",
    "joint_risk_budget",
    "pending_exposure_not_silently_released",
    "unknown_effect_not_blindly_replayed",
    "protected_guarantee_source_unreachable",
    "conservative_timeout_settlement",
)


class FiniteBAAModel:
    """Small immutable transition system mirroring the reference-kernel contract."""

    def __init__(
        self,
        proposals: tuple[ProposalSpec, ...],
        *,
        risk_budget: int,
        interaction_penalty: int,
    ) -> None:
        if risk_budget < 0 or interaction_penalty < 0:
            raise ValueError("risk parameters must be non-negative")
        self.proposals = proposals
        self.risk_budget = risk_budget
        self.interaction_penalty = interaction_penalty

    def exposure_items(self, state: FormalState) -> list[tuple[int, str]]:
        items: list[tuple[int, str]] = []
        for index, (phase, spec) in enumerate(zip(state.phases, self.proposals)):
            if phase in {Phase.RESERVED, Phase.PENDING}:
                items.append((spec.exposure_bound, spec.risk_factor))
            elif phase is Phase.SETTLED:
                value = state.settled_exposure[index]
                if value < 0:
                    raise InvariantViolation(
                        "ledger_category_exclusivity",
                        None,
                        "settled phase has no settled exposure",
                    )
                items.append((value, spec.risk_factor))
        return items

    def risk(self, items: Iterable[tuple[int, str]]) -> int:
        chosen = list(items)
        total = sum(bound for bound, _ in chosen)
        for index, (left_bound, left_factor) in enumerate(chosen):
            for right_bound, right_factor in chosen[index + 1 :]:
                if left_factor == right_factor:
                    total += self.interaction_penalty * min(
                        left_bound,
                        right_bound,
                    )
        return total

    def current_risk(self, state: FormalState) -> int:
        return self.risk(self.exposure_items(state))

    def projected_risk(self, state: FormalState, slot: int) -> int:
        spec = self.proposals[slot]
        return self.risk(
            [
                *self.exposure_items(state),
                (spec.exposure_bound, spec.risk_factor),
            ]
        )

    @staticmethod
    def _replace_phase(
        state: FormalState,
        slot: int,
        phase: Phase,
        *,
        settled: int | None = None,
    ) -> FormalState:
        phases = list(state.phases)
        settled_values = list(state.settled_exposure)
        phases[slot] = phase
        if phase is Phase.SETTLED:
            if settled is None:
                raise ValueError("settled phase requires exposure value")
            settled_values[slot] = settled
        else:
            settled_values[slot] = -1
        return FormalState(tuple(phases), tuple(settled_values))

    def step(self, state: FormalState, action: Action) -> Transition:
        if not 0 <= action.slot < len(self.proposals):
            raise IndexError("action slot out of range")
        spec = self.proposals[action.slot]
        phase = state.phases[action.slot]

        if action.kind == "evaluate":
            if phase is not Phase.PROPOSED:
                return Transition(
                    state, action, state, False, False, "proposal already evaluated"
                )
            if spec.protected_source:
                after = self._replace_phase(state, action.slot, Phase.DENIED)
                return Transition(
                    state, action, after, True, False, "protected source"
                )
            if not spec.composition_bounded:
                after = self._replace_phase(state, action.slot, Phase.HELD)
                return Transition(
                    state, action, after, True, False, "composition unbounded"
                )
            if not spec.verification_available:
                after = self._replace_phase(state, action.slot, Phase.HELD)
                return Transition(
                    state, action, after, True, False, "verification unavailable"
                )
            if not spec.bridge_valid:
                after = self._replace_phase(state, action.slot, Phase.HELD)
                return Transition(
                    state, action, after, True, False, "semantic bridge unavailable"
                )
            if not spec.fallback_viable:
                after = self._replace_phase(state, action.slot, Phase.HELD)
                return Transition(
                    state, action, after, True, False, "fallback unavailable"
                )
            if self.projected_risk(state, action.slot) > self.risk_budget:
                after = self._replace_phase(state, action.slot, Phase.DENIED)
                return Transition(
                    state, action, after, True, False, "joint risk exceeds budget"
                )
            after = self._replace_phase(state, action.slot, Phase.RESERVED)
            return Transition(state, action, after, True, True, "admitted")

        if action.kind == "execute":
            scope_ok = (
                action.object_id == spec.object_id
                and action.operation == spec.operation
                and action.amount is not None
                and 0 <= action.amount <= spec.quota
                and action.now is not None
                and action.now <= spec.expires_at
                and action.state_version == spec.state_version
            )
            if phase is not Phase.RESERVED:
                return Transition(
                    state, action, state, False, False, "capability not executable"
                )
            if not scope_ok:
                return Transition(
                    state, action, state, False, False, "capability scope mismatch"
                )
            after = self._replace_phase(state, action.slot, Phase.PENDING)
            return Transition(state, action, after, True, False, "effect attempted")

        if action.kind == "verify":
            realized = action.realized_exposure
            if phase is not Phase.PENDING:
                return Transition(
                    state, action, state, False, False, "effect not pending"
                )
            if (
                realized is None
                or realized < 0
                or realized > spec.exposure_bound
            ):
                return Transition(
                    state,
                    action,
                    state,
                    False,
                    False,
                    "verification result outside Omega exposure bound",
                )
            after = self._replace_phase(
                state,
                action.slot,
                Phase.SETTLED,
                settled=realized,
            )
            return Transition(state, action, after, True, False, "verified")

        if action.kind == "timeout":
            if phase is not Phase.PENDING:
                return Transition(
                    state, action, state, False, False, "effect not pending"
                )
            after = self._replace_phase(
                state,
                action.slot,
                Phase.SETTLED,
                settled=spec.exposure_bound,
            )
            return Transition(
                state,
                action,
                after,
                True,
                False,
                "conservative timeout settlement",
            )

        if action.kind == "observation_unavailable":
            if phase is not Phase.PENDING:
                return Transition(
                    state, action, state, False, False, "effect not pending"
                )
            return Transition(
                state,
                action,
                state,
                True,
                False,
                "pending knowledge preserved",
            )

        raise ValueError(f"unsupported action kind: {action.kind}")

    def actions(self) -> tuple[Action, ...]:
        output: list[Action] = []
        for slot, spec in enumerate(self.proposals):
            output.append(Action("evaluate", slot))
            output.extend(
                (
                    Action(
                        "execute",
                        slot,
                        object_id=spec.object_id,
                        operation=spec.operation,
                        amount=spec.quota,
                        now=1,
                        state_version=spec.state_version,
                    ),
                    Action(
                        "execute",
                        slot,
                        object_id=f"{spec.object_id}:wrong",
                        operation=spec.operation,
                        amount=spec.quota,
                        now=1,
                        state_version=spec.state_version,
                    ),
                    Action(
                        "execute",
                        slot,
                        object_id=spec.object_id,
                        operation=f"{spec.operation}:wrong",
                        amount=spec.quota,
                        now=1,
                        state_version=spec.state_version,
                    ),
                    Action(
                        "execute",
                        slot,
                        object_id=spec.object_id,
                        operation=spec.operation,
                        amount=spec.quota + 1,
                        now=1,
                        state_version=spec.state_version,
                    ),
                    Action(
                        "execute",
                        slot,
                        object_id=spec.object_id,
                        operation=spec.operation,
                        amount=spec.quota,
                        now=spec.expires_at + 1,
                        state_version=spec.state_version,
                    ),
                    Action(
                        "execute",
                        slot,
                        object_id=spec.object_id,
                        operation=spec.operation,
                        amount=spec.quota,
                        now=1,
                        state_version=spec.state_version + 1,
                    ),
                )
            )
            output.extend(
                (
                    Action("verify", slot, realized_exposure=0),
                    Action(
                        "verify",
                        slot,
                        realized_exposure=spec.exposure_bound,
                    ),
                    Action(
                        "verify",
                        slot,
                        realized_exposure=spec.exposure_bound + 1,
                    ),
                    Action("timeout", slot),
                    Action("observation_unavailable", slot),
                )
            )
        return tuple(output)

    def assert_state_invariants(self, state: FormalState) -> None:
        if len(state.phases) != len(self.proposals):
            raise InvariantViolation(
                "ledger_category_exclusivity",
                None,
                "phase vector length mismatch",
            )
        if len(state.settled_exposure) != len(self.proposals):
            raise InvariantViolation(
                "ledger_category_exclusivity",
                None,
                "settled vector length mismatch",
            )

        for index, (phase, settled) in enumerate(
            zip(state.phases, state.settled_exposure)
        ):
            if phase is Phase.SETTLED:
                if not 0 <= settled <= self.proposals[index].exposure_bound:
                    raise InvariantViolation(
                        "ledger_category_exclusivity",
                        None,
                        f"slot {index} has invalid settled exposure {settled}",
                    )
            elif settled != -1:
                raise InvariantViolation(
                    "ledger_category_exclusivity",
                    None,
                    f"slot {index} carries settled exposure outside SETTLED",
                )

            if (
                self.proposals[index].protected_source
                and phase in {Phase.RESERVED, Phase.PENDING, Phase.SETTLED}
            ):
                raise InvariantViolation(
                    "protected_guarantee_source_unreachable",
                    None,
                    f"protected slot {index} acquired reality-facing authority",
                )

        risk = self.current_risk(state)
        if risk > self.risk_budget:
            raise InvariantViolation(
                "joint_risk_budget",
                None,
                f"reachable risk {risk} exceeds budget {self.risk_budget}",
            )

    def assert_transition_invariants(self, transition: Transition) -> None:
        before = transition.before
        after = transition.after
        action = transition.action
        spec = self.proposals[action.slot]
        before_phase = before.phases[action.slot]
        after_phase = after.phases[action.slot]

        if action.kind == "execute" and transition.accepted:
            exact_scope = (
                before_phase is Phase.RESERVED
                and action.object_id == spec.object_id
                and action.operation == spec.operation
                and action.amount is not None
                and 0 <= action.amount <= spec.quota
                and action.now is not None
                and action.now <= spec.expires_at
                and action.state_version == spec.state_version
                and after_phase is Phase.PENDING
            )
            if not exact_scope:
                raise InvariantViolation(
                    "capability_scope_non_expansion",
                    transition,
                    "accepted execute escaped the issued capability scope",
                )

        if before_phase is Phase.PENDING:
            if action.kind in {"verify", "timeout"} and transition.accepted:
                if after_phase is not Phase.SETTLED:
                    raise InvariantViolation(
                        "pending_exposure_not_silently_released",
                        transition,
                        "terminal pending transition did not settle",
                    )
            elif after_phase is not Phase.PENDING:
                raise InvariantViolation(
                    "pending_exposure_not_silently_released",
                    transition,
                    "pending exposure changed category without verification/timeout",
                )

        if (
            action.kind == "execute"
            and before_phase is Phase.PENDING
            and transition.accepted
        ):
            raise InvariantViolation(
                "unknown_effect_not_blindly_replayed",
                transition,
                "pending effect was executed again",
            )

        if action.kind == "timeout" and transition.accepted:
            if after.settled_exposure[action.slot] != spec.exposure_bound:
                raise InvariantViolation(
                    "conservative_timeout_settlement",
                    transition,
                    "timeout did not charge the declared upper bound",
                )

        if transition.capability_issued:
            if spec.protected_source:
                raise InvariantViolation(
                    "protected_guarantee_source_unreachable",
                    transition,
                    "capability issued for a protected source",
                )
            if after_phase is not Phase.RESERVED:
                raise InvariantViolation(
                    "capability_scope_non_expansion",
                    transition,
                    "capability issued without a reserved proposal",
                )

        self.assert_state_invariants(after)

    def check(self) -> ModelCheckReport:
        initial = FormalState.initial(len(self.proposals))
        self.assert_state_invariants(initial)
        actions = self.actions()
        queue = deque([initial])
        seen = {initial}
        transitions = 0

        while queue:
            state = queue.popleft()
            for action in actions:
                transition = self.step(state, action)
                transitions += 1
                self.assert_transition_invariants(transition)
                if transition.after not in seen:
                    seen.add(transition.after)
                    queue.append(transition.after)

        return ModelCheckReport(
            reachable_states=len(seen),
            explored_transitions=transitions,
            invariants=INVARIANTS_FORMAL_V1,
            omega=OMEGA_FORMAL_V1,
        )


def reference_model_v1() -> FiniteBAAModel:
    """Return the frozen finite universe used by the v1 structural check."""

    return FiniteBAAModel(
        (
            ProposalSpec(
                "p-shared-a",
                "account:a",
                "transfer",
                1,
                1,
                "shared",
            ),
            ProposalSpec(
                "p-shared-b",
                "account:b",
                "transfer",
                1,
                1,
                "shared",
            ),
            ProposalSpec(
                "p-other",
                "account:c",
                "transfer",
                1,
                1,
                "other",
            ),
            ProposalSpec(
                "p-protected",
                "observer:trusted",
                "write",
                1,
                1,
                "observer",
                protected_source=True,
            ),
            ProposalSpec(
                "p-no-verifier",
                "account:d",
                "transfer",
                1,
                1,
                "other-2",
                verification_available=False,
            ),
        ),
        risk_budget=3,
        interaction_penalty=1,
    )
