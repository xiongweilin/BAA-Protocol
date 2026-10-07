"""Finite trace refinement helpers for the pinned AIOS offboarding gate.

This module checks an explicit semantic projection from integration events into
the abstract BAA lifecycle. It does not prove that every AIOS/runtime execution
is mediated by this gate; that remains an Omega assumption.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class AbstractPhase(str, Enum):
    PROPOSED = "proposed"
    DENIED = "denied"
    HELD = "held"
    RESERVED = "reserved"
    PENDING = "pending"
    SETTLED = "settled"


@dataclass(frozen=True)
class RefinementEvent:
    effect_id: str
    proposal_id: str
    prior: AbstractPhase
    next: AbstractPhase
    event: str
    obligation_id: str | None = None
    target_system: str | None = None
    operation: str | None = None
    request_identity: str | None = None


ALLOWED_TRANSITIONS = frozenset(
    {
        (AbstractPhase.PROPOSED, AbstractPhase.DENIED),
        (AbstractPhase.PROPOSED, AbstractPhase.HELD),
        (AbstractPhase.PROPOSED, AbstractPhase.RESERVED),
        (AbstractPhase.RESERVED, AbstractPhase.PENDING),
        (AbstractPhase.PENDING, AbstractPhase.PENDING),
        (AbstractPhase.PENDING, AbstractPhase.SETTLED),
    }
)


def assert_refines_protocol(events: Iterable[RefinementEvent]) -> None:
    """Reject an integration trace that cannot be projected to the abstract lifecycle."""

    last: dict[str, AbstractPhase] = {}
    terminal: set[str] = set()

    for event in events:
        if (event.prior, event.next) not in ALLOWED_TRANSITIONS:
            raise AssertionError(
                f"unsupported abstract transition: {event.prior.value}->{event.next.value}"
            )

        expected = last.get(event.effect_id, AbstractPhase.PROPOSED)
        if event.prior is not expected:
            raise AssertionError(
                f"non-contiguous refinement trace for {event.effect_id}: "
                f"expected {expected.value}, got {event.prior.value}"
            )

        if event.effect_id in terminal:
            raise AssertionError(
                f"terminal effect emitted another transition: {event.effect_id}"
            )

        if event.next in {AbstractPhase.DENIED, AbstractPhase.HELD, AbstractPhase.SETTLED}:
            terminal.add(event.effect_id)
        last[event.effect_id] = event.next

        if event.next in {AbstractPhase.RESERVED, AbstractPhase.PENDING, AbstractPhase.SETTLED}:
            if not all(
                (
                    event.obligation_id,
                    event.target_system,
                    event.operation,
                    event.request_identity,
                )
            ):
                raise AssertionError(
                    "reality-facing refinement event is missing scope identity"
                )


def phase_by_effect(
    events: Iterable[RefinementEvent],
) -> dict[str, AbstractPhase]:
    result: dict[str, AbstractPhase] = {}
    for event in events:
        result[event.effect_id] = event.next
    return result
