# P3 Isolated Protected-Access Timeline — Qualification Record v1

> English | [简体中文](p3-protected-access-timeline-v1.zh-CN.md)

## Status

**One qualified isolated-product, independently scheduled point-probe timeline.** It does **not** qualify continuous HRIS/IAM/access observations, real subject-second loss, a general causal effect, or joint-risk factor parameters.

Builds on the frozen [P3 temporal-outcome protocol](p3-offboarding-temporal-outcome-v1.md) and [protected-access point-probe qualification record](p3-protected-access-qualification-v1.md). The point-probe access decision, target/control roles, and initial protocol stay unchanged.

## Reproducible provenance

- AIOS [PR #39](https://github.com/xiongweilin/aios/pull/39), merged as [`09a2b40241b2`](https://github.com/xiongweilin/aios/commit/09a2b40241b234e5d96c922226a4dc41c12e08f9).
- Source branch head for the qualified run: `1f5b6af1c6f79792a089ef06eae42a2eeb4b658d`.
- GitHub Actions PR checkout merge ref recorded by `provenance.json`: `90ceacfa9a716b237f3c2e9aeed924977772b0ff`. This is not the source branch head nor the later squash-merge main commit.
- Frozen BAA instrument: `3ebd6e7b392d30063cd77d5015a3f2e288dfdb38`.
- Qualified isolated [run 37712215991](https://github.com/xiongweilin/aios/actions/runs/37712215991), attempt 1; artifact **11522760649**, archive digest `sha256:81c19f0574599f54df5836d4bc07fb921b1e34299e668f445ebee5850dbebcb0`.
- One ephemeral Keycloak/Odoo/World Runtime test deployment and actual loopback-scoped protected resource. No production identities, tenants, or credentials.
- The same initial target bearer token is repeatedly probed; an untouched account serves as control. Background reads are separately scheduled from the real AIOS engine, but share one Python runner host and hence do not establish physical or administrative failure-domain independence.

## Qualification outcome

| Recorded signal | Value |
|---|---|
| AIOS case final state | `completed` |
| BAA-covered product effects independently verified | 3 |
| Observer rounds | 33 |
| Total online protected-resource observations | 66 |
| Target ALLOW / DENY / UNKNOWN | 3 / 30 / 0 |
| Untouched control ALLOW / DENY / UNKNOWN | 33 / 0 / 0 |
| Observed DENY→ALLOW reversals | 0 |
| Capacity exhausted | No |
| Target **conditional single-change candidate bracket width** | 0.204721406 s |
| Continuous outcome identified | **No** |

Every probe records its **local monotonic** request-start/request-end envelope and descriptive wall-clock timestamps. The candidate bracket spans the start of the last observed target `ALLOW` request to the end of the first observed `DENY` request. It is not the time of the real state transition.

One observed sequence with no reversals **cannot establish** the assumption of a unique, irreversible transition. Unobserved changes, backend clock divergence, gaps between polls, and transient reauthorization are not ruled out. The still-frozen illustrative `SNAPSHOT_ONLY` reference interval was `[0,7]` subject-seconds, with `exact_duration_identified=false` and **unqualified external clock error**. It must not be treated as a real calibrated loss interval.

## Qualification / engineering history

The earlier first timeline attempt on [run 37711849889](https://github.com/xiongweilin/aios/actions/runs/37711849889), artifact **11522022515**, already produced a qualified target/control point sequence: 32 rounds and a conditional candidate width of 0.17295116 s. The related CI was not accepted because of a lint import error. Subsequent implementation-only changes made the pinned BAA import path available to offline tests, corrected the Ruff import, and serialized foreground/background capture rounds to preserve causal ordering. The final **six** PR #39 check suites all passed. Earlier runs remain part of CI and evidence provenance and were not relabeled as final accepted qualification.

## Next scientific gate

1. Either provide qualified independent product transition journals and a bounded clock/error model **or** restrict the claim to descriptive point-level traces and conservative unknown time.
2. Establish explicit cross-system joint-state identity and interval-continuity evidence; access-only polling cannot identify the proposed joint policy violation integral.
3. Freeze a discriminating intervention design and independent hold-out validation for competing factor partitions before product trials. Without an identified mapping from the current count-based exposure formula to subject-second `Y`, do **not** estimate a pairwise-min penalty or populate `OFFBOARDING_RISK_FACTOR_IDS_V1`.

This is an improvement in **instrument resolution and execution observability**, not evidence that BAA expands the delegation frontier or that real joint loss is calibrated.
