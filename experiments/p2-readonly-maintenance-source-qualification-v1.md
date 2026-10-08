# P2 Read-only Maintenance: Source Archive Qualification Amendment v1

> English | [简体中文](p2-readonly-maintenance-source-qualification-v1.zh-CN.md)

## Status

**Pre-model-sampling provenance hardening of an already frozen five-window P2 replay.** This amendment does **not** modify the workload, model prompts, tool schema, baseline vs audit vs BAA regimes, C0/C1/C2 turn budgets, delivery/attention-risk accounting or preregistered success rules. The original [P2 study protocol](p2-readonly-maintenance-model-v1.md) remains canonical.

The existing P2 workload had recorded the GitHub Actions artifact origin and SHA-256 as metadata, but the sampling runner did not verify the **actual archive bytes** before sending the frozen evidence to a real model. A manually edited workload could therefore retain the metadata while changing the alleged product observations. This is an instrument qualification issue, not a finding that the original P7 observations were false.

## New, mandatory pre-sampling check

The model runner now requires:

`--source-zip <original-p7-actions-archive.zip>`

It rejects missing/changed archive bytes **before the first model call**. Offline use:

```bash
python scripts/run_p2_readonly_maintenance_model.py \
  --source-zip /path/to/original-actions-11526016609.zip \
  --qualify-source-only \
  --output /path/to/source-qualification.json
```

The procedure pins and verifies:

- Original [AIOS P7 run 37720702388](https://github.com/xiongweilin/aios/actions/runs/37720702388), artifact **11526016609**, ZIP SHA-256 `dfafd340bd3a10f2c4768c578b908cad1756e6f1009e3c5b153d49046ec16b60`.
- Source experiment head `d8439c17248b88e0fdd971477f3a28fb151c6e76`, distinct PR checkout SHA `2288420643148fd8a2aa56de8ba6f9def0cbe1cd`, recorded Actions run ID and attempt.
- The actual isolated Keycloak pause and observed outage, successful unpause, zero business effects and reference `verified_recovered_evidence` outcome.
- All 16 original status records, four source positions per round, the observed covered capability fingerprint (normalized to one fixed symbolic fingerprint ID), and the approved observer-only normal / transport gap / contract anomaly references.
- Exact five original workload projections: M01 first two healthy rounds; M02–M04 the same real service-outage trace with different evidence prefixes/reacquisition suffixes; M05 the observer-only Runtime contract anomaly.

**Important counterexample:** The observer-only Keycloak transport failure and a true isolated Keycloak pause yield indistinguishable *normalized GET-level status traces*. The observer cannot infer the underlying cause solely from those readbacks. This test is retained as a **negative semantic identifiability check**, not evidence of generalization.

Source bytes are checked without contacting the actual products or invoking the model. The new `--qualify-source-only` mode emits source-integrity status only. A full model run records a `source_qualification` object beside the existing result, but creates no additional model proposals and does not redefine outcomes.

## Limitations

This check proves **integrity of the frozen evidence projection relative to the pinned Actions ZIP**. It does not prove the real-world semantics of all sensors, independent witnesses for inaccessible states, continuous availability, causal incident origins, useful Agent work or BAA delegation leverage. The archive is one short-lived disposable environment; its five windows are correlated. Real-model sampling, new-stage performance, attention, assurance cost and deployment access remain separately unqualified until their own evidence exists.

If GitHub artifacts have expired or are missing, do **not** reconstruct source bytes or replace their SHA to force a positive result; record the source-qualification failure and leave the P2 model run unqualified.
