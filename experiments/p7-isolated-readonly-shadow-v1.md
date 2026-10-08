# P7 Read-Only Isolated Shadow — First Instrument Baseline

> English | [简体中文](p7-isolated-readonly-shadow-v1.zh-CN.md)

**Status:** one qualified, short-duration, isolated *read-only observation drill*. **Not** a P7 production long-run, delegation-leverage, or unattended-safety acceptance.

## Versioned source

- AIOS [PR #41](https://github.com/xiongweilin/aios/pull/41), source branch HEAD `94ee3bf740ca5eb2af7b748f2b57516dbc48ee6e`, merged as `964a8b78119bd9e9f005b041a11a6919fee3086f`.
- [Actions run 37714124440](https://github.com/xiongweilin/aios/actions/runs/37714124440), attempt 1; workflow checkout merge SHA in the archived provenance: `bd32774b45dfbd1f0bc5c812108118aab81db0ea`.
- Evidence artifact **11523113319**, archive digest `sha256:b8e16a2dca58e573f87519c0ba2324c28cdfdd7e7bd115461210bff30adb0167`.
- The run started fresh isolated Odoo, Keycloak, and World Runtime containers with generated test credentials; it did not create offboarding subjects or dispatch business effects.

## Observed window and endpoints

The fixed PR test window was **40 seconds** after initial health-readiness qualification. The monitoring client issued only HTTP **GET** requests to `World Runtime /healthz`, `World Runtime /v1/capabilities`, `Keycloak /realms/master`, and the Odoo root endpoint.

| Evidence | Observation |
|---|---:|
| Completed shadow rounds | 9 |
| Total GET observations | 36 |
| Runtime-health non-OK | 0 |
| Runtime-capabilities non-OK | 0 |
| Keycloak realm non-OK | 0 |
| Odoo root non-OK | 0 |
| Observed covered authorization-contract fingerprints | 1 |
| Observed fingerprint changes | 0 |
| All three covered capability rules declared `authorization_required/resource_required/version_required=true` | yes, at sampled times |

The contract fingerprint covers exactly the three BAA offboarding capability names and their three declared enforcement flags; it does **not** prove actual execution mediation. The observer archives bounded monotonic request envelopes and a finite list of failure classes, but no response bodies, tokens, secrets or subject IDs.

## Important denominator and limitation

Zero **observed** non-OK samples out of 36 says nothing reliable about 24-hour availability, tail failure probabilities, unsampled outages, credential rotation, process restarts, workload delivery or incident response. There were no real effects in this shadow window, and no human attention, automatic assurance labor, cost or durable agent context was measured. It cannot qualify G2/G3/G4/G5 for production.

No periodic workflow schedule was installed. The new AIOS workflow supports *manual* bounded 1-, 5-, or 15-minute runs using disposable infrastructure. These are not a substitute for a preregistered long-duration trial.

The next P7 experiment requires a scoped and independently approved read-only staging observation principal, a meaningful maintenance workload, multi-agent/resource concurrency, policy/schema upgrades, rotations, bounded fault injection, explicit operator takeover, failure denominator, and frozen acceptance thresholds **before** any long-term deployment trial.

**P7 remains unqualified for production writes or unattended operational delegation.**
