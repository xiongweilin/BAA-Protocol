# P3 Isolated Protected-Resource Access Probe — Qualification v1

> English | [简体中文](p3-offboarding-access-probe-qualification-v1-result.zh-CN.md)

## Evidence classification

**Accepted as isolated real-product point-probe qualification only.** This record does not claim an exact continuous loss duration, joint-risk factor identification, interaction-penalty calibration, operational production safety, or general delegation leverage.

- Frozen outcome instrument: `xiongweilin/BAA-Protocol@3ebd6e7b392d30063cd77d5015a3f2e288dfdb38`.
- Product execution: `xiongweilin/aios` PR [#38](https://github.com/xiongweilin/aios/pull/38), merged as `eb8cc19c92ea61e414fbd7f342f2583f8304a0be`.
- Qualified implementation head: `978367d0f52c166286403ab996ef610bafabbd60`.
- Isolation: ephemeral Odoo database, Keycloak 26.8 test realm, World Runtime and opt-in loopback-bound protected-resource sidecar on GitHub-hosted Linux Docker; no real employees or production tenant.
- The protocol is [P3 Temporal Outcome v1](p3-offboarding-temporal-outcome-v1.md). No metric or outcome threshold was retrospectively changed.

## Qualification history, including failures

| Attempt | GitHub Actions run | Artifact ID | Status and interpretation |
|---|---|---|---|
| 1 | [37709634277](https://github.com/xiongweilin/aios/actions/runs/37709634277) | `11520849286` | **Unqualified.** Target and control were enabled with live sessions, but the sidecar denied both baseline accesses. Instrument failure; not a revocation observation. |
| 2 | [37710011839](https://github.com/xiongweilin/aios/actions/runs/37710011839) | `11521342891` | **Unqualified.** Adding an audience mapper alone did not correct sidecar token verification; both baseline accesses were still denied. |
| 3 | [37710502830](https://github.com/xiongweilin/aios/actions/runs/37710502830) | `11521687493` | **Unqualified, diagnostic.** Both JWTs included the verifier in `aud`; host-side introspection showed `active=true` and UserInfo HTTP 200. A different in-container Keycloak origin still caused JWT verification failure. |
| 4 | [37710849397](https://github.com/xiongweilin/aios/actions/runs/37710849397) | `11521698006` | **Qualified for point-probe behavior.** Sidecar used the same Keycloak issuer origin as token issuance; original access and test controls passed. |

All four attempts remain in the qualification provenance. Attempts 1–3 are **not** substituted into the valid loss sample. Their failures constrain instrumentation validity.

The fourth artifact is identified by SHA-256 `9ba4d277a335c64653cdc4af2ddb24cf6b1b60468946fbf42ae3985505f84fc1`.

## Fourth-run observations

| Probe | Before offboarding | After offboarding | Expected interpretation |
|---|---|---|---|
| Target real bearer token at isolated protected resource | `ALLOW` | `DENY` | Direct point evidence of loss of protected-resource access; the **same issued bearer token** is reused after withdrawal |
| Independent control token for a different, still-authorized test identity | `ALLOW` | `ALLOW` | Control remains accessible |
| Isolated target HRIS / IAM read-back | active / enabled before | inactive / disabled after | Product-state corroboration, **not** a substitute for the probe |
| Offline-probe failure injection | — | `UNKNOWN` | Unreachable probe cannot be treated as verified access denial |

Actual AIOS offboarding reached `COMPLETED`, with three independently verified covered external effects, in the same isolated run. The verifier path and protection endpoint did not need to learn any bearer value from the experiment artifact.

The two point snapshots provide **no** independently qualified continuous-state proof between samples. The reference temporal instrument reported `[0,6]` **subject-seconds as an instrument/sample bracket**, and `exact_duration_identified=false`; the cross-source clock-error bound was **not independently qualified**. Consequently **do not promote** `[0,6]` to a validated real-world loss-duration confidence interval or a calibrated `Y_joint` value.

## Interface qualification defect and correction

Keycloak 26.8 live introspection checks issuer/audience semantics. The initial sidecar used `http://keycloak:8080` while the access token was issued through the host-published Keycloak origin `http://127.0.0.1:28180`. This mismatch produced false baseline denials even though host-side introspection recognized the token as active.

The accepted fixture uses the same host-published issuer origin for issuance and sidecar introspection in a **Linux-only disposable, loopback-bound** test setup. The realm's test session client has a dedicated audience mapper. This is a prerequisite correction to the probe interface, not a different outcome endpoint.

## Scientific and deployment restrictions

This result establishes that, for these isolated products and the recorded test identities, the independent live probe distinguishes currently permitted access, subsequently denied access, a still-entitled control, and an observation outage.

It does **not** establish:

- a continuous interval-observation source or qualified clock uncertainty;
- visibility into all cached bearer-token consumers, sessions, or physical access routes;
- subject-second violation duration, aggregate societal/business loss, or attribution to a particular effect;
- identification of `F_distinct`, `F_IAM_shared`, `F_all_shared`, or any interaction penalty;
- the existing `managed-subject-state-change-count-v1` metric being commensurate with subject-seconds;
- performance, reliability, or authorization for a production tenant.

`OFFBOARDING_RISK_FACTOR_IDS_V1` must remain empty.

## Next preregistered P3 dependency

Before loss identification, independently qualify a temporal collector: freeze test subjects and cross-system mappings, source times and clock-error bound, access probe availability, event/transition capture or a defensible bounded-interpolation model, observation coverage, missing-data treatment, competing factor predictions, and held-out validation. A new qualified workload must be prospectively registered before data collection. If these obligations cannot be met, report a non-identification result, not synthetic risk parameters.
