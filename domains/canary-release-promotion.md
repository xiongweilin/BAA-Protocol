# Canary Release Promotion Domain

> English | [简体中文](canary-release-promotion.zh-CN.md)

## Scope

This is the second concrete BAA task domain: canary-release-promotion.

Pinned AIOS source: xiongweilin/aios@34b9f4274487f856ac4c23266d1dd726b24ae53c.

The source domain is AIOS Autonomous Development progressive delivery. It changes the risk structure from revoking authority to progressively increasing real traffic exposure while preserving rollback.

The first BAA instance covers two existing AIOS traffic capabilities:

- development.traffic.apply
- development.traffic.restore

The interface binds experiment, target, control release, candidate deployment, stage index, candidate traffic weight, operation identity, and state version.

## Kernel properties

The reference kernel attempts to enforce:

1. no traffic change without an exact-scope capability;
2. no experiment, target, release, deployment, stage, or weight rebinding;
3. no stale state-version execution;
4. no skipping configured stages;
5. no later-stage increase without sufficient current-stage evidence;
6. no increase after deterministic guardrail violation;
7. no increase with incomplete required telemetry;
8. no increase while an earlier route effect is unresolved;
9. no blind replay of an unresolved route increase;
10. no exposure increase when rollback is unavailable;
11. restore-to-control may be admitted as a compensating action even while the prior increase is unresolved;
12. restore is complete only after independent observation of zero candidate weight.

These are interface/process guarantees, not a proof that candidate software is correct.

## Real-world bridge

The bounded claims are:

- candidate traffic does not intentionally exceed the admitted stage;
- stage increases are sequential;
- further exposure requires sufficient attributable evidence and satisfied guardrails;
- an ambiguous route change remains unknown and does not create replay permission;
- increased exposure requires an enforceable restore-to-control path.

These claims depend on explicit assumptions: the traffic director is the covered route-changing path; candidate_weight_percent reflects effective traffic exposure; identifiers bind the intended runtime objects; route read-back observes effective reality rather than a command receipt; telemetry is attributable and protected from admitted writes; guardrails are the intended contract; restore remains timely and enforceable.

## Information and exposure state

The minimum information state contains the experiment identity, target/control/candidate identities, configured stages, current verified stage and weight, state version, attributable stage evidence, guardrails, route-effect knowledge, rollback availability, and operation history.

The primary mechanical exposure is candidate traffic weight. The reference risk state is structured rather than scalar:

rho(q) = (candidate_weight, unresolved_route_effect, guardrail_violations, stale_or_skip_actions, out_of_scope_actions)

Guardrail violations and identity errors are constraints, not quantities that can be traded for more traffic.

## Sustainable safe region

A new exposure increase is admissible only while rollback remains enforceable, current exposure is within a configured stage, no prior increase remains unresolved, and current evidence permits the next stage.

If guardrails fail, no further increase is admitted. The mechanically available fallback is restore-to-control, not a human notification.

## Evidence semantics

For later-stage increases, the prior stage must satisfy its configured minimum duration, total requests, candidate requests, required control requests/metrics, telemetry completeness, and guardrails.

Insufficient evidence produces hold. Guardrail violation blocks exposure increase.

The protocol preserves:

command accepted != route changed != route independently observed

An ambiguous apply remains pending. While pending, another increase and replay are blocked. A separately authorized restore may reduce exposure.

## Deliberate non-guarantees

This domain does not prove program correctness, metric completeness, causal attribution of every metric change, absence of delayed regressions, correctness of open-ended product objectives, guaranteed rollback outside the stated assumptions, or production prevalence of failures.

## Validation boundary

Before any second-domain real-model comparison:

1. the BAA canary state machine must pass regression tests;
2. AIOS CanaryStage and Experiment semantics must project exactly;
3. BAA evidence/guardrail decisions must agree with AIOS evaluate_canary_stage on covered cases;
4. AIOS traffic changes must pass through development.traffic.apply and development.traffic.restore;
5. unknown traffic effects must remain reconciliation-required at the World Runtime boundary.
