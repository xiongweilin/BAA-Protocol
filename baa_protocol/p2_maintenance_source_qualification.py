"""P2 source qualification against the actual pinned P7 Actions ZIP.

Requires exact archived bytes, a valid isolated real-process outage witness,
and byte-for-byte agreement between each frozen projected read-only episode
and its stated source observations. This changes NO episode, prompt, regime,
budget or success condition of the preregistered P2 v1 experiment.
"""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any

from .p2_readonly_maintenance_model import load_cases

SOURCE_ARCHIVE_SHA256 = (
    "dfafd340bd3a10f2c4768c578b908cad1756e6f1009e3c5b153d49046ec16b60"
)
SOURCE_RUN_ID = "37720702388"
SOURCE_PR_CHECKOUT_SHA = "2288420643148fd8a2aa56de8ba6f9def0cbe1cd"
SOURCE_HEAD_SHA = "d8439c17248b88e0fdd971477f3a28fb151c6e76"
SOURCE_ARTIFACT_ID = 11526016609
SOURCES = ("runtime_health", "runtime_capabilities", "keycloak_realm", "odoo_root")


def _archive_rows(observed: Any) -> list[dict[str, Any]]:
    if not isinstance(observed, list) or len(observed) != 16:
        raise ValueError("expected precisely four complete archived rounds")
    converted = []
    raw_fingerprints = set()
    for index, row in enumerate(observed):
        if (
            not isinstance(row, dict)
            or row.get("round") != index // 4
            or row.get("source") != SOURCES[index % 4]
            or row.get("result") not in (
                "ok", "schema_unknown", "transport_unknown", "http_error"
            )
        ):
            raise ValueError("archived source ordering or status invalid")
        fingerprint = (
            row.get("capability_fingerprint")
            if row["source"] == "runtime_capabilities" and row["result"] == "ok"
            else None
        )
        if fingerprint:
            raw_fingerprints.add(fingerprint)
        converted.append({
            "round": row["round"],
            "source": row["source"],
            "result": row["result"],
            "contract_qualified": bool(fingerprint),
            # Stable symbolic alias, not a fabricated source fingerprint.
            "fingerprint_id": "covered-policy-v1" if fingerprint else None,
        })
    if len(raw_fingerprints) != 1:
        raise ValueError("source contract drift/missing fingerprint")
    return converted


def qualify_p2_source_archive(
    workload: dict[str, Any],
    archive_path: Path,
) -> dict[str, Any]:
    provenance = workload["provenance"]
    if (
        provenance.get("source_archive_sha256") != SOURCE_ARCHIVE_SHA256
        or provenance.get("source_head") != SOURCE_HEAD_SHA
        or str(SOURCE_ARTIFACT_ID) not in provenance.get("source", "")
        or SOURCE_RUN_ID not in provenance.get("source", "")
    ):
        raise ValueError("P2 source metadata does not match frozen provenance")
    if hashlib.sha256(archive_path.read_bytes()).hexdigest() != SOURCE_ARCHIVE_SHA256:
        raise ValueError("P2 source Actions ZIP SHA-256 mismatch")
    with zipfile.ZipFile(archive_path) as archive:
        source_run = json.loads(archive.read("provenance.json"))
        real = json.loads(archive.read("real-isolated-outage.json"))
        diagnostic = json.loads(archive.read("maintenance-triage.json"))

    if (
        str(source_run.get("run_id")) != SOURCE_RUN_ID
        or source_run.get("AIOS_SHA") != SOURCE_PR_CHECKOUT_SHA
        or str(source_run.get("attempt")) != "1"
    ):
        raise ValueError("archived Actions run identity mismatch")

    if not (
        real.get("qualified") is True
        and real.get("actual_keycloak_outage_observed") is True
        and real.get("other_three_sources_remained_ok_in_fault_round") is True
        and real.get("unpause_succeeded") is True
        and real.get("real_business_effect_count") == 0
        and real.get("assessment", {}).get("status") == "verified_recovered_evidence"
    ):
        raise ValueError("archived real disposable Keycloak outage not qualified")

    by_case = {x["case"]: x for x in diagnostic["results"]}
    if set(by_case) != {
        "normal", "observer_transport_gap", "observer_contract_anomaly"
    } or any(not row.get("qualified") for row in by_case.values()):
        raise ValueError("archived P7 diagnostic source not qualified")

    # Compare source evidence, not pre-labelled outcome guesses.
    actual_rows = _archive_rows(real["snapshot"]["records"])
    normal_rows = _archive_rows(by_case["normal"]["records"])
    anomaly_rows = _archive_rows(by_case["observer_contract_anomaly"]["records"])
    simulated_gap = _archive_rows(by_case["observer_transport_gap"]["records"])
    if simulated_gap != actual_rows:
        raise ValueError(
            "actual isolated outage and observer-only gap are distinguishable "
            "in their frozen normalized readback: protocol counterexample invalid"
        )

    expected = {
        "M01": (normal_rows[:8], []),
        "M02": (actual_rows[:8], [actual_rows[8:12], actual_rows[12:16]]),
        "M03": (actual_rows[:12], [actual_rows[12:16]]),
        "M04": (actual_rows, []),
        "M05": (anomaly_rows, []),
    }
    if [x["id"] for x in workload["episodes"]] != list(expected):
        raise ValueError("frozen five-case sequence changed")
    for episode in workload["episodes"]:
        initial, next_rounds = expected[episode["id"]]
        if episode["initial"] != initial or episode["next_rounds"] != next_rounds:
            raise ValueError(
                "P2 model-visible workload is not a faithful projection of P7 archive"
            )
    if (
        by_case["observer_transport_gap"].get("simulated_instrument_faults") != 1
        or by_case["observer_contract_anomaly"].get("simulated_instrument_faults") != 1
        or by_case["normal"].get("simulated_instrument_faults") != 0
    ):
        raise ValueError("observer-only fault source misclassified")

    return {
        "schema": "p2-isolated-maintenance-source-qualification-v1",
        "qualified": True,
        "source_run_id": SOURCE_RUN_ID,
        "source_artifact_id": SOURCE_ARTIFACT_ID,
        "source_zip_sha256": SOURCE_ARCHIVE_SHA256,
        "verified_p2_episodes": 5,
        "independent_operational_incidents": None,
        "real_disposable_process_pause_qualified": True,
        "observer_only_gap_indistinguishable_at_sensor_level": True,
        "external_product_effects": 0,
        "new_model_calls": 0,
    }


__all__ = ["qualify_p2_source_archive"]
