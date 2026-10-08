"""P3 interval-bounded, independently attested offboarding outcome instrument.

This module does not establish the trustworthiness of observations. An
INTERVAL_ATTESTED segment is a *claim* by a separately qualified collector that
the supplied projection held throughout [start_s, end_s). Endpoint snapshots
never imply interval continuity. Unknown time and missing evidence widen an
outcome interval instead of being silently imputed to zero.

The measured subject-seconds are NOT the structural v1 exposure metric
("managed-subject-state-change-count-v1") and are not a calibrated loss model.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class AccessProbe(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    UNKNOWN = "unknown"


class EvidenceKind(str, Enum):
    INTERVAL_ATTESTED = "interval_attested"
    SNAPSHOT_ONLY = "snapshot_only"
    UNAVAILABLE = "unavailable"


class Phase(str, Enum):
    BEFORE_EFFECTIVE = "before_effective"
    TRANSITION_GRACE = "transition_grace"
    AFTER_DEADLINE = "after_deadline"
    CLOCK_UNCERTAIN = "clock_uncertain"


@dataclass(frozen=True)
class SubjectPolicy:
    """Frozen policy for a single explicitly enumerated identity binding.

    The pre-effective expected ability to access is a domain-specific contract
    assertion, not a universal property of all employees.
    """

    subject_id: str
    effective_at_s: int
    grace_s: int
    pre_effective_access_expected: bool = True

    def __post_init__(self) -> None:
        if not self.subject_id.strip():
            raise ValueError("subject_id must be nonempty")
        if self.grace_s < 0:
            raise ValueError("grace_s must be nonnegative")

    @property
    def deadline_s(self) -> int:
        return self.effective_at_s + self.grace_s


@dataclass(frozen=True)
class JointProjection:
    hris_active: bool | None
    iam_enabled: bool | None
    active_sessions: int | None
    access_probe: AccessProbe

    def __post_init__(self) -> None:
        if self.active_sessions is not None and self.active_sessions < 0:
            raise ValueError("active_sessions cannot be negative")


@dataclass(frozen=True)
class ObservationInterval:
    subject_id: str
    start_s: int
    end_s: int
    kind: EvidenceKind
    evidence_ref: str
    projection: JointProjection | None = None

    def __post_init__(self) -> None:
        if self.end_s <= self.start_s:
            raise ValueError("interval must have positive duration")
        if not self.evidence_ref.strip():
            raise ValueError("observation provenance must be explicit")
        if self.kind is EvidenceKind.INTERVAL_ATTESTED and self.projection is None:
            raise ValueError("interval attestation requires a projection")


@dataclass(frozen=True)
class DurationBounds:
    lower_s: int
    upper_s: int

    def __post_init__(self) -> None:
        if self.lower_s < 0 or self.upper_s < self.lower_s:
            raise ValueError("invalid outcome bounds")


@dataclass(frozen=True)
class SubjectOutcome:
    subject_id: str
    joint_violation: DurationBounds
    postdeadline_access: DurationBounds
    premature_access_denial: DurationBounds
    transition_grace_s: int
    clock_uncertain_s: int
    missing_or_unattested_s: int


@dataclass(frozen=True)
class TemporalOutcome:
    """Time-integrated bounds, denominated in subject-seconds."""

    joint_violation: DurationBounds
    postdeadline_access: DurationBounds
    premature_access_denial: DurationBounds
    subjects: tuple[SubjectOutcome, ...]

    @property
    def identified(self) -> bool:
        return self.joint_violation.lower_s == self.joint_violation.upper_s

    @property
    def fully_identified(self) -> bool:
        return all(
            bounds.lower_s == bounds.upper_s
            for bounds in (
                self.joint_violation,
                self.postdeadline_access,
                self.premature_access_denial,
            )
        )


def _bound(length: int, violation: bool | None) -> DurationBounds:
    if violation is True:
        return DurationBounds(length, length)
    if violation is False:
        return DurationBounds(0, 0)
    return DurationBounds(0, length)


def _or_unknown(conditions: tuple[bool | None, ...]) -> bool | None:
    if True in conditions:
        return True
    if all(c is False for c in conditions):
        return False
    return None


def _mismatch(actual: object | None, expected: object) -> bool | None:
    if actual is None:
        return None
    if isinstance(actual, AccessProbe) and actual is AccessProbe.UNKNOWN:
        return None
    return actual != expected


def _phase(start: int, end: int, policy: SubjectPolicy, clock_error: int) -> Phase:
    if end <= policy.effective_at_s - clock_error:
        return Phase.BEFORE_EFFECTIVE
    if start >= policy.deadline_s + clock_error:
        return Phase.AFTER_DEADLINE
    if (
        policy.grace_s > 0
        and start >= policy.effective_at_s + clock_error
        and end <= policy.deadline_s - clock_error
    ):
        return Phase.TRANSITION_GRACE
    return Phase.CLOCK_UNCERTAIN


def _split_points(
    start: int, end: int, policy: SubjectPolicy, clock_error: int
) -> list[int]:
    candidates = (
        start, end,
        policy.effective_at_s - clock_error,
        policy.effective_at_s + clock_error,
        policy.deadline_s - clock_error,
        policy.deadline_s + clock_error,
    )
    return sorted(set(x for x in candidates if start <= x <= end))


def _score_projection(
    projection: JointProjection | None,
    kind: EvidenceKind,
    phase: Phase,
    duration: int,
    pre_access_expected: bool,
) -> tuple[DurationBounds, DurationBounds, DurationBounds]:
    unknown = _bound(duration, None)
    zero = _bound(duration, False)
    if kind is not EvidenceKind.INTERVAL_ATTESTED or projection is None:
        if phase is Phase.BEFORE_EFFECTIVE:
            return unknown, zero, unknown if pre_access_expected else zero
        if phase is Phase.AFTER_DEADLINE:
            return unknown, unknown, zero
        return unknown, unknown, unknown

    if phase is Phase.BEFORE_EFFECTIVE:
        joint = _or_unknown((
            _mismatch(projection.hris_active, True),
            _mismatch(projection.iam_enabled, True),
            _mismatch(
                projection.access_probe,
                AccessProbe.ALLOW if pre_access_expected else AccessProbe.DENY,
            ),
        ))
        disruption = (
            _mismatch(projection.access_probe, AccessProbe.ALLOW)
            if pre_access_expected else False
        )
        return _bound(duration, joint), zero, _bound(duration, disruption)

    if phase is Phase.AFTER_DEADLINE:
        joint = _or_unknown((
            _mismatch(projection.hris_active, False),
            _mismatch(projection.iam_enabled, False),
            _mismatch(projection.active_sessions, 0),
            _mismatch(projection.access_probe, AccessProbe.DENY),
        ))
        access = _mismatch(projection.access_probe, AccessProbe.DENY)
        return _bound(duration, joint), _bound(duration, access), zero

    raise ValueError("unscored phase cannot be scored as a stable policy phase")


def _sum_bounds(items: Iterable[DurationBounds]) -> DurationBounds:
    items = tuple(items)
    return DurationBounds(
        sum(x.lower_s for x in items),
        sum(x.upper_s for x in items),
    )


def measure_offboarding(
    *,
    policies: tuple[SubjectPolicy, ...],
    observations: tuple[ObservationInterval, ...],
    horizon_start_s: int,
    horizon_end_s: int,
    max_clock_error_s: int = 0,
) -> TemporalOutcome:
    """Compute conservative outcome bounds for a frozen subject universe.

    The oracle is conditional on interval-attestation validity and the frozen
    temporal policy; it does not observe reality itself.
    """

    if horizon_end_s <= horizon_start_s:
        raise ValueError("invalid horizon")
    if max_clock_error_s < 0:
        raise ValueError("max_clock_error_s must be nonnegative")
    if not policies:
        raise ValueError("a nonempty subject universe must be declared")
    policy_by_subject = {p.subject_id: p for p in policies}
    if len(policy_by_subject) != len(policies):
        raise ValueError("subject policy ids must be unique")
    by_subject: dict[str, list[ObservationInterval]] = {
        subject: [] for subject in policy_by_subject
    }
    for observation in observations:
        if observation.subject_id not in by_subject:
            raise ValueError("observation subject is outside declared universe")
        if (
            observation.start_s < horizon_start_s
            or observation.end_s > horizon_end_s
        ):
            raise ValueError("observation extends beyond frozen horizon")
        by_subject[observation.subject_id].append(observation)

    subjects: list[SubjectOutcome] = []
    for subject_id, policy in policy_by_subject.items():
        entries = sorted(
            by_subject[subject_id], key=lambda x: (x.start_s, x.end_s)
        )
        cursor = horizon_start_s
        intervals: list[tuple[int, int, EvidenceKind, JointProjection | None]] = []
        for item in entries:
            if item.start_s < cursor:
                raise ValueError("overlapping evidence for the same subject")
            if item.start_s > cursor:
                intervals.append((cursor, item.start_s, EvidenceKind.UNAVAILABLE, None))
            intervals.append(
                (item.start_s, item.end_s, item.kind, item.projection)
            )
            cursor = item.end_s
        if cursor < horizon_end_s:
            intervals.append((cursor, horizon_end_s, EvidenceKind.UNAVAILABLE, None))

        joint: list[DurationBounds] = []
        late_access: list[DurationBounds] = []
        early_denial: list[DurationBounds] = []
        grace_seconds = 0
        clock_uncertain = 0
        unattributed_seconds = 0
        for start, end, kind, projection in intervals:
            if kind is not EvidenceKind.INTERVAL_ATTESTED:
                unattributed_seconds += end - start
            points = _split_points(start, end, policy, max_clock_error_s)
            for lo, hi in zip(points, points[1:]):
                if lo == hi:
                    continue
                phase = _phase(lo, hi, policy, max_clock_error_s)
                duration = hi - lo
                if phase is Phase.TRANSITION_GRACE:
                    grace_seconds += duration
                    continue
                if phase is Phase.CLOCK_UNCERTAIN:
                    clock_uncertain += duration
                    # Clock ambiguity may change the applicable temporal
                    # policy, so no "safe" time is silently imputed.
                    joint.append(_bound(duration, None))
                    late_access.append(_bound(duration, None))
                    early_denial.append(_bound(duration, None))
                    continue
                j, a, d = _score_projection(
                    projection, kind, phase, duration,
                    policy.pre_effective_access_expected,
                )
                joint.append(j)
                late_access.append(a)
                early_denial.append(d)
        subjects.append(
            SubjectOutcome(
                subject_id=subject_id,
                joint_violation=_sum_bounds(joint),
                postdeadline_access=_sum_bounds(late_access),
                premature_access_denial=_sum_bounds(early_denial),
                transition_grace_s=grace_seconds,
                clock_uncertain_s=clock_uncertain,
                missing_or_unattested_s=unattributed_seconds,
            )
        )

    return TemporalOutcome(
        joint_violation=_sum_bounds(s.joint_violation for s in subjects),
        postdeadline_access=_sum_bounds(s.postdeadline_access for s in subjects),
        premature_access_denial=_sum_bounds(
            s.premature_access_denial for s in subjects
        ),
        subjects=tuple(subjects),
    )


__all__ = [
    "AccessProbe",
    "DurationBounds",
    "EvidenceKind",
    "JointProjection",
    "ObservationInterval",
    "SubjectOutcome",
    "SubjectPolicy",
    "TemporalOutcome",
    "measure_offboarding",
]
