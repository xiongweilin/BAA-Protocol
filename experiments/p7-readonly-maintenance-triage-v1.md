# P7 Isolated Read-Only Maintenance Triage — v1 Qualification

> English | [简体中文](p7-readonly-maintenance-triage-v1.zh-CN.md)

**Evidence grade:** deterministic read-only operational diagnostic **instrument qualification** against three live disposable services. **Not** an Agent delegation comparison, production incident trial, actual provider fault injection, long-term reliability claim, or BAA attention-risk leverage estimate.

## Frozen experiment

[AIOS preregistration](https://github.com/xiongweilin/aios/blob/02360374af3a61e7e63aee911a69a6fb50007ca7/tests/acceptance/baa_offboarding/P7-MAINTENANCE-TRIAGE.md) fixed three cases before the accepted product run, reusing one isolated Keycloak/Odoo/World Runtime topology. Each case had four ordered rounds of the same four GET-only probes: World Runtime health, its three covered authorization-capability contracts, the Keycloak realm and Odoo root.

The test does not alter any product or user's privileges. The two non-normal cases perturb **only the local observation response**, not the actual identity provider, service health or Runtime contract.

| Case | Instrument perturbation | Preregistered final decision | Actual |
|---|---|---|---|
| `normal` | none | `verified_stable` | qualified |
| `observer_transport_gap` | round-1 Keycloak read skipped; `transport_unknown` | `verified_recovered_evidence` only after two complete clean reacquisition rounds | qualified |
| `observer_contract_anomaly` | round-1 Runtime contract response classified `schema_unknown` locally | sticky `escalate_contract_or_authority` even when subsequent reads pass | qualified |

The policy rejects missing/duplicated/out-of-order source evidence, does not silently treat a failed baseline as healthy, separates **UNKNOWN encountered** from **terminal unresolved**, and refuses to auto-close a contract/authorization discrepancy.

## Provenance and denominators

- AIOS [PR #42](https://github.com/xiongweilin/aios/pull/42): source branch HEAD `427002b8ddb26b5f54b6309ff40c6e60697d982b`; merged main SHA `02360374af3a61e7e63aee911a69a6fb50007ca7`.
- Qualified GitHub Actions [run 37718555268](https://github.com/xiongweilin/aios/actions/runs/37718555268), attempt 1. Evidence `maintenance-triage.json`, `observations.json`, `provenance.json` in artifact **11524233834**, archive digest `sha256:abb424b07aa953724029ef4bf18ed962afe54d2e42317b37f0106d3915a04134`.
- The artifact's workflow PR checkout merge ref is `6bd401579aa1a9e7716461c95404e23ff071fc2f`; this is not the source branch or later squash-merge SHA.
- New diagnostic tasks: **3 × 4 rounds × 4 sources = 48 observation slots**, **46 actual live GET requests + 2 explicitly injected observer-side missing/anomalous observations**. By case: `16+0`, `15+1`, `15+1` live + injected slots.
- All three diagnostic outcomes qualified. No final unresolved among these three *fixtures*. The transport-gap case encountered one UNKNOWN and required two full fresh rounds; the contract-anomaly case escalated instead of treating subsequent OK samples as closure.
- The pre-existing 40-second health-only shadow also qualified in that run: **9 rounds / 36 GETs**, 0 sampled failures, one unchanged three-capability fingerprint. These are **separate** from the diagnostic task slots and must not be conflated in denominators.
- PR #42's seven required workflows passed before merge.

The first source-head attempt [37718407816](https://github.com/xiongweilin/aios/actions/runs/37718407816) did **not** enter the diagnostic test: disposable `odoo-init` exited 2 during startup. It is a fixture qualification failure, not a negative or positive maintenance delivery episode. The same source head also had two import-order lint errors, subsequently repaired without changing the frozen decision criteria. No historical run is relabelled.

## Measurement boundary

These tasks are *read-only maintenance triage*, not actual incident remediation. A `verified_recovered_evidence` result confirms only that two later **sampled** full sets of GETs succeeded. It is not proof of recovery after a real Keycloak outage. A sticky escalation is a machine classification; no real principal attention, assurance labor, repair action or operator resolution was observed.

No LLM/Agent ran, no three-arm self-check/audit/BAA randomization occurred, no access authorization was changed, and no real joint loss `Y`, risk factor, P95/P99 SLO, or deployment authorization was measured. P3 factor registry remains empty and P7 sustained delegation is not qualified.

## Next discriminating task

Before extending this to a real internal maintenance workload, separately approve a *scoped read-only staging identity and resource inventory*. Pre-register a versioned set of genuine maintenance tickets with independent outcome verification, matched randomized Agent regimes, fixed attention/risk/delivery/assurance budgets, fault and escalation rules, an explicit recovery budget and a termination condition. The personal Windows self-hosted CI runner is **not** evidence of a qualified staging permission boundary.
