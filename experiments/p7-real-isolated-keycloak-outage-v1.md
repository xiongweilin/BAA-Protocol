# P7: Actual Isolated Keycloak Process Outage and Conservative Read-only Recovery — v1

> English | [简体中文](p7-real-isolated-keycloak-outage-v1.zh-CN.md)

## Evidence grade

A **single qualified real, reversible failure of an isolated service process** observed by a GET-only instrument. It is not a production failure, an autonomous Agent action, long-term soak, an SLO/MTTR distribution, or a BAA causal delegation comparison.

The previous [P7 read-only maintenance triage](p7-readonly-maintenance-triage-v1.md) only injected *local observation responses*. This experiment advances that instrument boundary by **actually pausing** an isolated test Keycloak process, using a fixed Docker Compose service name, and requiring the observer to detect loss and then reacquire evidence after an unconditional unpause attempt.

## Frozen scientific contract

The [AIOS v2 preregistration](https://github.com/xiongweilin/aios/blob/engineering/p7-real-isolated-keycloak-outage-recovery/tests/acceptance/baa_offboarding/P7-ISOLATED-REAL-OUTAGE.md) was committed **before the first fault trial**:

1. One full four-source GET-only baseline must be healthy, including the unchanged three covered World Runtime capability enforcement flags.
2. The isolated Keycloak test container is paused once by an explicit CI-only Docker controller.
3. During actual pause, the Keycloak realm GET must return `transport_unknown` while World Runtime health, capability contract and Odoo root remain `ok`.
4. The controller must attempt `unpause` even if the fault trial errors.
5. At most eight recovery rounds, two seconds apart, must lead to **two consecutive complete clean rounds**. The unchanged `assess_maintenance` rule must conclude `verified_recovered_evidence`. Otherwise, fail qualification.

No staff accounts, product write API, policy mutation, credential rotation or production system was involved.

## First qualified actual product-fault run

- AIOS [PR #43](https://github.com/xiongweilin/aios/pull/43), initial qualified fault source head `ab5f023844a73e13b9b04b6acfe4960c304f8f67`.
- [GitHub Actions 37720188025](https://github.com/xiongweilin/aios/actions/runs/37720188025), attempt 1, evidence artifact **11526115290**, archive SHA-256 `cd1fd2b0b3574feb623c48ae9e1aefde5c885388d6f00f24e89c511f35d2b900`.
- Artifact `provenance.json` PR checkout SHA `a01d456e4c30f401360a7422aa61b2dc829e7cab` is distinct from the source head.
- Isolated service fault sequence: baseline → actual Keycloak container pause → observed `transport_unknown` → successful unpause → two full clean read rounds.
- **4 rounds / 16 observed GET probes** for the actual interruption: exactly one Keycloak probe was not OK; **zero** non-OK readings on the other three source categories.
- `assess_maintenance`: `verified_recovered_evidence`, `observation_unknown_encountered=true`, `terminal_unresolved=false`, `evidence_reacquisition_rounds=2`.
- Measured local monotonic interval from completion of the Docker unpause command to completion of the second clean observation round: **2.076049 seconds**. This is **instrument reacquisition wall time**, not the underlying Keycloak repair instant or a representative mean time to recover.
- Existing same-run, separate observation tasks also qualified: a 40-second `9 × 4 = 36`-GET healthy shadow and the previous three deterministic read-only triage cases. **Do not combine their denominators** with the outage episode.

## Implementation / test-environment qualification failures

- The first scientific outage result succeeded but the source-head main PR CI failed `F401` (an unused imported constant), which was removed without modifying the procedure.
- A later [run 37720464278](https://github.com/xiongweilin/aios/actions/runs/37720464278) failed during disposable `odoo-init` bootstrap (exit code 2), **before baseline or any fault experiment**. It contributes a failed infrastructure qualification, not a recovery episode or statistical reliability point.
- A subsequent fixture-only change allows **at most two** fresh disposable Compose startup attempts. `fixture-startup.json` records attempts and failures, and both failed attempts abort the workflow. The root cause of sporadic Odoo initialization failure was **not established**. This change does not adjust the fault, controls, read criteria, number of recovery rounds, or conclusions.
- Final release/merge CI after this instrument-readiness change must be evaluated **separately** from the first qualified science run.

## Boundaries and remaining gates

A single induced Docker process pause demonstrates that the point-level observer can distinguish this reversible isolated failure from unaffected controls, and that two complete new GET rounds can be acquired after resuming it. This does **not** establish continuous correctness, actual administrative repair, incident diagnosis under natural faults, principal attention, automated assurance labor, useful Agent work, tail recovery latency, a causal BAA advantage, general high-availability robustness, or acceptance for production deployment.

The P3 joint-loss factor registry remains uncalibrated and unchanged. A real maintenance-delivery study must still use externally approved read-only staging access and independent task outcomes; it must compare matched Agent procedures under frozen risk, attention, delivery, horizon and assurance budgets.
