# P3 Isolated Protected-Resource Probe — Qualification Record v1

> English | [简体中文](p3-protected-access-qualification-v1.zh-CN.md)

## Evidential status

**Qualified isolated-product point-probe instrument**, not a measured continuous temporal loss and not risk-factor calibration.

The original [P3 temporal-outcome protocol](p3-offboarding-temporal-outcome-v1.md) remains unchanged. This is a qualification record for its intended *access capability* observation prerequisite, not a change to its endpoint, treatment arms, grace policy, horizon, model hypotheses, or negative-result rule.

## Pinned execution and accepted observation

- Executor repository: `xiongweilin/aios`, PR [#38](https://github.com/xiongweilin/aios/pull/38), merged as [`eb8cc19c92ea`](https://github.com/xiongweilin/aios/commit/eb8cc19c92ea61e414fbd7f342f2583f8304a0be).
- Frozen execution head for the first accepted point-probe run: `978367d0f52c166286403ab996ef610bafabbd60`.
- Frozen BAA reference instrument: `3ebd6e7b392d30063cd77d5015a3f2e288dfdb38`.
- Qualified GitHub Actions [run 37710849397](https://github.com/xiongweilin/aios/actions/runs/37710849397), evidence artifact **11521698006**, archived digest `sha256:9ba4d277a335c64653cdc4af2ddb24cf6b1b60468946fbf42ae3985505f84fc1`.
- Environment: disposable GitHub-hosted Ubuntu runner, isolated ephemeral Odoo, Keycloak, World Runtime, and loopback-only protected resource; one target test principal and one unaffected test control.
- Protected resource calls live Keycloak token introspection on the **same issuer origin** that minted the test tokens; no raw tokens or client secrets are written to evidence.

### What the accepted run actually established

| Observation | Test target | Untouched control |
|---|---|---|
| Before offboarding | **ALLOW** | **ALLOW** |
| After BAA→AIOS→World Runtime offboarding and independent verification of three effects | **DENY** | **ALLOW** |

An explicitly unreachable protected-resource endpoint was classified **UNKNOWN**, not `DENY`. AIOS completed the authorized test offboarding and externally verified three covered product effects.

This validates the local protected-access *point* distinction under the test deployment and token-issuer configuration; it does not prove every deployed authorization channel behaves identically.

## Qualification failures remain in the record

These are **instrument/setup qualification failures**, not real observed loss and not silently excluded from provenance:

| Run | Artifact | Boundary observed |
|---|---|---|
| [37709634277](https://github.com/xiongweilin/aios/actions/runs/37709634277) | 11520849286 | Enabled baseline principals were denied: live protected-resource probe was not qualified |
| [37710011839](https://github.com/xiongweilin/aios/actions/runs/37710011839) | 11521342891 | Adding a disposable client audience mapper did not resolve baseline denial |
| [37710502830](https://github.com/xiongweilin/aios/actions/runs/37710502830) | 11521687493 | Host-origin token introspection was active and UserInfo returned 200, but container-alias issuer introspection still failed |
| [37710849397](https://github.com/xiongweilin/aios/actions/runs/37710849397) | 11521698006 | Same fixed access decision rule qualified after matching the issuer origin |

The only changes across these setup qualification attempts were implementation fixes to the **probe interface / test environment**. No new causal comparison or pre-registered joint-risk calibration was asserted.

## Temporal and semantic boundary

The accepted frozen reference `SNAPSHOT_ONLY` interval produced illustrative `[0,6]` **subject-seconds** and `exact_duration_identified=false`. The external wall-clock error was **not independently qualified**. Therefore **`[0,6]` must not be presented as a validated real-world duration or calibrated loss bound**. It is a reference-computation output under a local illustrative clock assumption.

Two or more successful point probes cannot establish all intermediate states. A token may be invalidated at an unknown time between calls; reversals and unobserved transient availability also remain possible. The current `managed-subject-state-change-count-v1` product exposure has a different unit from `subject-seconds` and cannot simply be reused as a risk penalty.

**P3 status:** access-capability point instrument qualified for one isolated deployment; independent time-continuity, clock qualification, multi-effect competing-model identification and real product `Y` calibration **not achieved**. The offboarding risk-factor registry remains intentionally empty.

## Next discriminating evidence

1. Record independently scheduled, per-request timestamped target/control probes **during** effect execution, including all UNKNOWN readings and actual request envelopes.
2. Verify external clock source and the allowed observation error, plus product-side event/transition provenance or explicitly report only unobserved-time bounds.
3. Preregister genuinely discriminating factor-partition contrasts and hold-out clusters, then execute only in approved isolated test infrastructure. Neither point success nor dense polling alone identifies interaction penalties.
