"""Read-only provenance qualification of archived disposable-product P7 results.

Checks actual downloaded Actions ZIP bytes when supplied. Does not fetch,
modify or connect to Keycloak/Odoo/Runtime, nor trust workload origin tags as
observational evidence without independently pinned archive bytes.
"""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any

from .maintenance_model_replay import (
    MaintenanceWindow, SOURCES, expected_from_full_observations
)


def _checked_zip(path: Path, required_digest: str) -> zipfile.ZipFile:
    if hashlib.sha256(path.read_bytes()).hexdigest() != required_digest:
        raise ValueError("Actions ZIP digest mismatch: origin not qualified")
    return zipfile.ZipFile(path)


def _normalized(records: list[dict[str, Any]]) -> tuple[dict[str, str], ...]:
    if len(records) != 16:
        raise ValueError("archived episode must be four complete four-source rounds")
    rounds: list[dict[str, str]] = []
    for i in range(4):
        sample = records[i * 4:(i + 1) * 4]
        if [row["source"] for row in sample] != list(SOURCES):
            raise ValueError("source ordering changed in archived evidence")
        if any(row["round"] != i for row in sample):
            raise ValueError("round order changed in archived evidence")
        normalized = {row["source"]: row["result"] for row in sample}
        normalized["capability_contract"] = (
            "qualified"
            if sample[1]["result"] == "ok" and sample[1].get("capability_fingerprint")
            else "unknown"
        )
        rounds.append(normalized)
    return tuple(rounds)


def qualify_archived_maintenance(
    windows: tuple[MaintenanceWindow, ...],
    *,
    triage_zip: Path,
    outage_zip: Path,
) -> dict[str, Any]:
    if len(windows) != 4 or len({w.episode_id for w in windows}) != 4:
        raise ValueError("expected exactly four pinned archived maintenance windows")
    w = {ep.episode_id: ep for ep in windows}
    expected_files = {
        "M01": ("normal", "maintenance-triage.json"),
        "M02": ("observer_transport_gap", "maintenance-triage.json"),
        "M03": ("observer_contract_anomaly", "maintenance-triage.json"),
        "M04": (None, "real-isolated-outage.json"),
    }
    with _checked_zip(triage_zip, w["M01"].archive_sha256) as a, _checked_zip(
        outage_zip, w["M04"].archive_sha256
    ) as b:
        triage = json.loads(a.read("maintenance-triage.json"))
        actual = json.loads(b.read("real-isolated-outage.json"))
        results = {row["case"]: row for row in triage["results"]}
        if set(results) != {v[0] for v in list(expected_files.values())[:3]}:
            raise ValueError("unexpected archived maintenance case roster")
        for episode_id, (case, _) in expected_files.items():
            window = w[episode_id]
            if episode_id == "M04":
                if not (
                    actual.get("qualified") is True
                    and actual.get("actual_keycloak_outage_observed") is True
                    and actual.get("unpause_succeeded") is True
                    and actual.get("assessment", {}).get("status") == window.expected_final
                    and actual.get("real_business_effect_count") == 0
                ):
                    raise ValueError("actual isolated outage provenance not qualified")
                records = actual["snapshot"]["records"]
            else:
                archived = results[case]
                if not archived.get("qualified"):
                    raise ValueError("nonqualified maintenance source episode")
                if archived["assessment"]["status"] != window.expected_final:
                    raise ValueError("archive/reference outcome mismatch")
                if archived["simulated_instrument_faults"] != (0 if case == "normal" else 1):
                    raise ValueError("misidentified observer-only perturbation")
                records = archived["records"]
            restored = _normalized(records)
            if restored != window.observations:
                raise ValueError("published workload differs from archived sensor evidence")
            if expected_from_full_observations(restored) != window.expected_final:
                raise ValueError("reference classifier differs from archived disposition")
    return {
        "qualified": True,
        "workload_episode_count": 4,
        "distinct_archives": 2,
        "artifact_ids": sorted({ep.artifact_id for ep in windows}),
        "real_process_pause_episodes": 1,
        "observer_only_perturbation_episodes": 2,
        "controls": "archive checksum + complete source order + observed status + source outcome",
        "actual_production_effects": 0,
        "scientific_status": "archived finite model-replay instrument qualification only",
    }


__all__ = ["qualify_archived_maintenance"]
