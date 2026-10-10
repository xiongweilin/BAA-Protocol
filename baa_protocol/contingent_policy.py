"""Finite, adversarial-belief policy synthesis for a *declared* action interface.

A policy is valid only relative to a complete caller-supplied world abstraction.
This module does not mint execution authority, establish calibrated risk, or
prove that the abstraction covers reality. Runtime admission is still mandatory.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Effect:
    name: str
    # Each possible pre-state maps to ALL possible post-states, including
    # unresolved/ambiguous effects; omission means the effect is not enabled.
    outcomes: tuple[tuple[str, tuple[str, ...]], ...]
    authorized: bool = False
    cost: int = 1

    def as_map(self) -> dict[str, tuple[str, ...]]:
        return dict(self.outcomes)


@dataclass(frozen=True)
class Probe:
    name: str
    # The observation source must be independently qualified by the caller.
    readings: tuple[tuple[str, str], ...]
    trusted: bool = False
    cost: int = 1

    def as_map(self) -> dict[str, str]:
        return dict(self.readings)


@dataclass(frozen=True)
class Policy:
    kind: str  # done | effect | probe
    name: str = ""
    next: Policy | None = None
    branches: tuple[tuple[str, Policy], ...] = ()
    worst_cost: int = 0

    def as_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "name": self.name,
            "worst_cost": self.worst_cost,
            "next": self.next.as_dict() if self.next else None,
            "branches": {label: branch.as_dict() for label, branch in self.branches},
        }


def synthesize(
    *,
    possible_states: frozenset[str],
    goal_states: frozenset[str],
    safe_states: frozenset[str],
    effects: tuple[Effect, ...],
    probes: tuple[Probe, ...],
    max_steps: int,
) -> Policy | None:
    """Minimize worst-case operation cost; otherwise fail closed.

    Effects do not reveal which nondeterministic result occurred. Only a
    qualified probe may split the belief. At most one issuance of each effect
    is allowed in a policy branch, so unknown outcomes cannot trigger blind
    redispatch. This deliberately favors soundness over completeness.
    """
    if not possible_states or not possible_states <= safe_states:
        return None
    if not goal_states <= safe_states or max_steps < 0:
        raise ValueError("invalid goal, safety envelope, or planning horizon")
    names = [step.name for step in (*effects, *probes)]
    if len(names) != len(set(names)) or any(not name for name in names):
        raise ValueError("step names must be distinct nonempty identifiers")
    for step in (*effects, *probes):
        if step.cost <= 0:
            raise ValueError("step costs must be positive")
    for effect in effects:
        if len(effect.outcomes) != len(effect.as_map()):
            raise ValueError("duplicate effect pre-state")
        if any(not values for _, values in effect.outcomes):
            raise ValueError("effect result set cannot be empty")
    for probe in probes:
        if len(probe.readings) != len(probe.as_map()):
            raise ValueError("duplicate probe pre-state")

    @lru_cache(maxsize=None)
    def solve(
        belief: frozenset[str], used_effects: frozenset[str], remaining: int
    ) -> Policy | None:
        if belief <= goal_states:
            return Policy("done")
        if remaining == 0:
            return None
        candidates: list[Policy] = []
        for effect in effects:
            if not effect.authorized or effect.name in used_effects:
                continue
            successors = effect.as_map()
            if not belief <= successors.keys():
                continue
            next_belief = frozenset(
                after for before in belief for after in successors[before]
            )
            if not next_belief <= safe_states:
                continue
            child = solve(
                next_belief, used_effects | {effect.name}, remaining - 1
            )
            if child is not None:
                candidates.append(
                    Policy("effect", effect.name, next=child,
                           worst_cost=effect.cost + child.worst_cost)
                )
        for probe in probes:
            if not probe.trusted:
                continue
            mapping = probe.as_map()
            if not belief <= mapping.keys():
                continue
            parts: dict[str, set[str]] = {}
            for state in belief:
                parts.setdefault(mapping[state], set()).add(state)
            # Reading that changes no possible action is not useful.
            if len(parts) <= 1:
                continue
            branches: list[tuple[str, Policy]] = []
            for label, subset in sorted(parts.items()):
                child = solve(frozenset(subset), used_effects, remaining - 1)
                if child is None:
                    break
                branches.append((label, child))
            if len(branches) == len(parts):
                candidates.append(
                    Policy("probe", probe.name, branches=tuple(branches),
                           worst_cost=probe.cost +
                           max(branch.worst_cost for _, branch in branches))
                )
        return min(candidates, key=lambda p: (p.worst_cost, p.kind, p.name)) if candidates else None

    return solve(possible_states, frozenset(), max_steps)


def assert_structurally_safe(
    policy: Policy,
    *,
    possible_states: frozenset[str],
    goal_states: frozenset[str],
    safe_states: frozenset[str],
    effects: tuple[Effect, ...],
    probes: tuple[Probe, ...],
    max_steps: int,
) -> None:
    """Independently check *any* supplied policy; synthesis is not trusted.

    Raises ValueError for unsafe, incomplete, unverified, or overlong policies.
    """
    effect_map = {item.name: item for item in effects}
    probe_map = {item.name: item for item in probes}
    if not possible_states or not possible_states <= safe_states:
        raise ValueError("initial belief violates safety envelope")

    def check(
        node: Policy, belief: frozenset[str],
        used: frozenset[str], left: int,
    ) -> None:
        if left < 0:
            raise ValueError("planning horizon exceeded")
        if node.kind == "done":
            if not belief <= goal_states or node.next or node.branches:
                raise ValueError("premature or malformed completion")
            return
        if left == 0 or not node.name:
            raise ValueError("missing step/horizon")
        if node.kind == "effect":
            step = effect_map.get(node.name)
            if (step is None or not step.authorized or node.name in used
                    or node.branches or node.next is None):
                raise ValueError("unauthorized, replayed, or malformed effect")
            outcomes = step.as_map()
            if not belief <= outcomes.keys():
                raise ValueError("effect not enabled for all possible worlds")
            later = frozenset(s for before in belief for s in outcomes[before])
            if not later <= safe_states:
                raise ValueError("effect can leave safety envelope")
            check(node.next, later, used | {node.name}, left - 1)
            return
        if node.kind == "probe":
            step = probe_map.get(node.name)
            if step is None or not step.trusted or node.next:
                raise ValueError("unqualified or malformed observation")
            readings = step.as_map()
            if not belief <= readings.keys():
                raise ValueError("probe lacks world coverage")
            actual: dict[str, frozenset[str]] = {
                label: frozenset(s for s in belief if readings[s] == label)
                for label in {readings[s] for s in belief}
            }
            branches = dict(node.branches)
            if len(branches) != len(node.branches) or set(branches) != set(actual):
                raise ValueError("missing, fake or duplicate observation branch")
            for label, subset in actual.items():
                check(branches[label], subset, used, left - 1)
            return
        raise ValueError("unknown policy node")

    check(policy, possible_states, frozenset(), max_steps)
