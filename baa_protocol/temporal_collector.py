"""Independent read-only P3 collector contract (synthetic/isolated use).

A polling collector produces snapshots, never continuous interval attestations.
Reader/writer separation is checked on declared credential domains, but its
enforcement requires deployment evidence; no secret values are stored.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .temporal_outcome import (
    AccessProbe,
    EvidenceKind,
    JointProjection,
    ObservationInterval,
    SubjectPolicy,
)


@dataclass(frozen=True)
class CollectorSources:
    collector_id: str
    hris_source: str
    iam_source: str
    access_probe_source: str
    hris_reader_domain: str
    iam_reader_domain: str
    access_probe_domain: str
    hris_writer_domain: str
    iam_writer_domain: str

    def __post_init__(self) -> None:
        values = (
            self.collector_id,
            self.hris_source,
            self.iam_source,
            self.access_probe_source,
            self.hris_reader_domain,
            self.iam_reader_domain,
            self.access_probe_domain,
            self.hris_writer_domain,
            self.iam_writer_domain,
        )
        if any(not value.strip() for value in values):
            raise ValueError("collector identity, source and domain locators are required")
        if self.hris_reader_domain == self.hris_writer_domain:
            raise ValueError("HRIS reader must not share writer credential domain")
        if self.iam_reader_domain == self.iam_writer_domain:
            raise ValueError("IAM reader must not share writer credential domain")
        if self.access_probe_domain in (
            self.hris_writer_domain,
            self.iam_writer_domain,
        ):
            raise ValueError("access probe must not share a writer credential domain")


@dataclass(frozen=True)
class Snapshot:
    subject_id: str
    observed_at_s: int
    collector_id: str
    evidence_ref: str
    projection: JointProjection
    errors: tuple[str, ...]
    kind: EvidenceKind = EvidenceKind.SNAPSHOT_ONLY

    def __post_init__(self) -> None:
        if self.kind is not EvidenceKind.SNAPSHOT_ONLY:
            raise ValueError("polling evidence cannot claim interval attestation")


class ReadOnlyCollector:
    def __init__(
        self,
        *,
        sources: CollectorSources,
        read_hris_active: Callable[[str], bool],
        read_iam_state: Callable[[str], tuple[bool, int]],
        probe_access: Callable[[str], AccessProbe],
    ) -> None:
        self.sources = sources
        self.read_hris_active = read_hris_active
        self.read_iam_state = read_iam_state
        self.probe_access = probe_access

    def capture(self, *, subject_id: str, observed_at_s: int, sample_id: str) -> Snapshot:
        if not subject_id.strip() or not sample_id.strip():
            raise ValueError("subject and sample identity required")
        errors: list[str] = []
        active: bool | None = None
        enabled: bool | None = None
        sessions: int | None = None
        access = AccessProbe.UNKNOWN

        try:
            value = self.read_hris_active(subject_id)
            if type(value) is not bool:
                raise TypeError("expected boolean HRIS active")
            active = value
        except Exception as exc:
            errors.append(f"hris:{type(exc).__name__}")

        try:
            values = self.read_iam_state(subject_id)
            if (
                not isinstance(values, tuple)
                or len(values) != 2
                or type(values[0]) is not bool
                or type(values[1]) is not int
                or values[1] < 0
            ):
                raise TypeError("expected (enabled: bool, sessions: nonnegative int)")
            enabled, sessions = values
        except Exception as exc:
            errors.append(f"iam:{type(exc).__name__}")

        try:
            value = self.probe_access(subject_id)
            if not isinstance(value, AccessProbe):
                raise TypeError("expected explicit AccessProbe result")
            access = value
        except Exception as exc:
            errors.append(f"probe:{type(exc).__name__}")

        return Snapshot(
            subject_id=subject_id,
            observed_at_s=observed_at_s,
            collector_id=self.sources.collector_id,
            evidence_ref=f"{self.sources.collector_id}:{sample_id}",
            projection=JointProjection(active, enabled, sessions, access),
            errors=tuple(errors),
        )


def bracket_snapshots(first: Snapshot, second: Snapshot) -> ObservationInterval:
    """Preserve uncertainty between polls even when endpoint fields agree."""

    if first.subject_id != second.subject_id:
        raise ValueError("cannot bracket different subjects")
    if first.collector_id != second.collector_id:
        raise ValueError("different collectors need explicit reconciliation")
    if first.observed_at_s >= second.observed_at_s:
        raise ValueError("snapshot timestamps must increase")
    return ObservationInterval(
        subject_id=first.subject_id,
        start_s=first.observed_at_s,
        end_s=second.observed_at_s,
        kind=EvidenceKind.SNAPSHOT_ONLY,
        evidence_ref=f"{first.evidence_ref}|{second.evidence_ref}",
        projection=second.projection,
    )


def classify_point(
    snapshot: Snapshot, *, policy: SubjectPolicy
) -> bool | None:
    """Point diagnostic: True=known violation, False=known compliant.

    This function does not estimate violation *duration* and should only be
    used once external clocks and probe interpretation are qualified.
    """
    if snapshot.subject_id != policy.subject_id:
        raise ValueError("snapshot does not match subject policy")
    t = snapshot.observed_at_s
    fields = snapshot.projection
    if policy.effective_at_s <= t < policy.deadline_s:
        return None
    if t < policy.effective_at_s:
        expected_probe = (
            AccessProbe.ALLOW
            if policy.pre_effective_access_expected
            else AccessProbe.DENY
        )
        comparisons = (
            None if fields.hris_active is None else fields.hris_active is not True,
            None if fields.iam_enabled is None else fields.iam_enabled is not True,
            None if fields.access_probe is AccessProbe.UNKNOWN
            else fields.access_probe != expected_probe,
        )
    else:
        comparisons = (
            None if fields.hris_active is None else fields.hris_active is not False,
            None if fields.iam_enabled is None else fields.iam_enabled is not False,
            None if fields.active_sessions is None else fields.active_sessions != 0,
            None if fields.access_probe is AccessProbe.UNKNOWN
            else fields.access_probe is not AccessProbe.DENY,
        )
    if True in comparisons:
        return True
    return False if all(v is False for v in comparisons) else None


__all__ = [
    "CollectorSources",
    "ReadOnlyCollector",
    "Snapshot",
    "bracket_snapshots",
    "classify_point",
]
