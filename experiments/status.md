# Prototype Status

> English | [简体中文](status.zh-CN.md)

## Current claim level

The repository has reached six evidence layers for one concrete domain: employee offboarding.

1. Executable BAA reference semantics and deterministic fault fixtures.
2. Pinned AIOS contract compatibility and execution-engine gating.
3. Isolated production-like network acceptance across HTTP/process/Docker boundaries.
4. High-fidelity connector acceptance against real ephemeral Keycloak and Odoo product instances.
5. A composed single-episode BAA -> AIOS -> World Runtime -> real Keycloak/Odoo acceptance matrix with independent product read-back and fault recovery.
6. A preregistered prospective real-model three-regime study with version-pinned model/gateway evidence and explicit null-result retention.

The strongest current claim is:

> For the finite BAA model and the pinned AIOS offboarding implementation at commit `87f24f32a01c67a9246fc3cb127517c80798e169`, the tested path can constrain the covered offboarding action flow, preserve explicit uncertainty across ambiguous execution/read-back states, recover through independently observed product state, reject an unauthorized Runtime bypass before provider effect, and complete the covered IAM/HRIS obligations against real ephemeral Keycloak and Odoo instances with separate writer/verifier identities.

The fault-recovery result is a claim about stable logical request identity and tested no-blind-replay behavior, not a proof of physical exactly-once delivery.

The first prospective comparative result is separately negative: on the frozen seven-episode real-model study, all three regimes were delegable on 6/7 episodes at C0, C1, and C2, so BAA did not enlarge the tested delegation frontier.

This is not a production-tenant safety claim, a general unattended-autonomy theorem, or a certification result.

## What is executable

The prototype includes:

- generic bounded action admission;
- concrete employee-offboarding admission;
- exact-scope capabilities;
- authority-epoch and controlled state-version invalidation;
- effective-time and verification gating;
- explicit deferred/no-attempt semantics for admission HOLD;
- unresolved-effect preservation;
- retry suppression after ambiguous effect;
- recovery after independent read-back resolves ambiguity;
- protected guarantee-source isolation;
- a conservative unresolved-effect concurrency limit;
- VSAR event capture;
- self-check, post-hoc audit, and BAA experiment regimes;
- deterministic episode-level fault fixtures;
- finite exhaustive admission checks;
- projection from real AIOS Administrative obligations;
- CI against a pinned AIOS checkout;
- isolated Windows/Docker network acceptance;
- real ephemeral Keycloak connector acceptance;
- real ephemeral Odoo connector acceptance;
- composed real-product offboarding E2E for normal, lost-ack, read-back-outage, and unauthorized-bypass scenarios;
- a prospective real-model harness with shared initial sampling, adaptive-prefix reuse, JSON/SSE Responses compatibility, and separate physical versus counterfactual logical model-cost accounting.

## Pinned AIOS compatibility

BAA CI pins:

~~~text
xiongweilin/aios@87f24f32a01c67a9246fc3cb127517c80798e169
~~~

CI verifies:

1. AIOS offboarding policy effects equal the BAA hard-domain effect set.
2. AIOS-derived external obligations project without losing case, subject, authority epoch, governance basis, target system, or operation.
3. Covered AIOS reality postconditions map to the BAA verification surface.
4. Every covered effect maps to an AIOS World Runtime capability.
5. The BAA kernel can admit, execute, verify, recover, and externally complete obligations derived by the pinned AIOS code.
6. The BAA provider gate changes the actual AIOS execution path while preserving deferred/no-attempt versus outcome-unknown semantics.
7. The pinned World Runtime surface requires authorization, resource binding, version binding, and separated writer/verifier credential domains.

These checks detect contract drift. They do not prove completeness of the production threat model or production credential isolation.

## Isolated network evidence

AIOS workflow run `37302243172` passed on the repository-scoped Windows/Docker Desktop runner.

Observed evidence:

- normal episode: completed with exactly three unique external writes;
- lost acknowledgement: recovered to completion with three unique writes and zero duplicates;
- read-back outage: recovered to completion with three unique writes and zero duplicates;
- unauthorized Runtime bypass: HTTP 403 with zero provider writes.

This establishes that the bounded path can cross a real HTTP/process/Docker boundary while preserving the modeled no-replay and authorization properties for the synthetic effect service.

## Real Keycloak evidence

AIOS workflow run `37306648690` passed against Keycloak `26.8.0`.

Observed evidence:

- real OAuth client-credentials/Admin REST path;
- separate writer and verifier service accounts;
- real user session present before offboarding;
- identity disable succeeds and is independently read back;
- session revoke changes the real session count from one to zero;
- reconciliation succeeds through durable connector metadata;
- verifier mutation attempt is rejected with HTTP 403.

Evidence artifact: `real-keycloak-offboarding-37306648690`, artifact id `11344280550`.

## Real Odoo evidence

AIOS workflow run `37307582025` passed against Odoo `18.0-20260926` with PostgreSQL.

Observed evidence:

- real JSON-RPC path;
- separate writer and verifier Odoo users;
- exact `hr.employee` deactivation;
- durable deactivate request marker persisted;
- independent read-back observes `active = false`;
- reconciliation succeeds after deactivation;
- verifier write is denied.

The real-product run exposed a concrete semantic/implementation boundary: inactive Odoo employees are excluded by the default active filter. The connector now performs durable identity lookup with `active_test = false`; regression coverage locks that behavior.

Evidence artifact: `real-odoo-offboarding-37307582025`, artifact id `11344206985`.

## Composed real-product E2E evidence

AIOS workflow run `37315551794` passed at PR head `b0bb3705d5180557e35a5e6b103c912c32169b70`. That tree was merged unchanged as AIOS commit `87f24f32a01c67a9246fc3cb127517c80798e169`.

The workflow ran four isolated matrix scenarios.

### Normal

Observed evidence:

- the AIOS case reaches `completed`;
- Keycloak reports `enabled = false`;
- Keycloak reports `active_sessions = 0`;
- Odoo reports `active = false`;
- all three effects have realizations and confirmed outcomes;
- independent read-back observes the real product fields before frozen execution context is added to the semantic view;
- all three BAA obligations reach `verified_effected`;
- Keycloak and Odoo verifier credentials are denied mutation authority.

### Lost acknowledgement

Observed evidence:

- the first real Keycloak disable effect is present while acknowledgement is ambiguous;
- execution enters persisted reconciliation;
- `case.reconciliation_started` and `case.reconciliation_resolved_for_execution` are recorded;
- the disable durable request identity remains stable across recovery;
- the episode resumes and completes all three obligations.

This supports stable logical request identity and no blind replay in the tested recovery path. It is not a proof that the underlying product performed only one physical write.

### Read-back outage

Observed evidence:

- the effect is not treated as absent when independent read-back is unavailable;
- execution enters persisted reconciliation;
- recovery resumes after read-back becomes available;
- the same recovery state transitions are recorded;
- the episode completes without inventing a successful observation during the outage.

### Unauthorized Runtime bypass

Observed evidence:

- a direct effectful Runtime invocation without authorization returns HTTP 403;
- `provider_effect_observed = false`;
- Keycloak and Odoo before/after product state is unchanged.

The composed E2E result is still ephemeral test-environment evidence. It does not establish production network isolation, production credential custody, or production operating distributions.

## Prospective real-model evidence

AIOS workflow run `37393917221` is the accepted first prospective real-model result.

Pinned evidence:

~~~text
workload: prospective-offboarding-v1
model: gpt-6-luna
BAA-Protocol: 340dbd9a0bfbe72746e3666fa559fa7d812a25d0
AIOS experiment workflow: 6eeaed6874e67257f19d9dc1a66bdc796865804d
local gateway: 496ec69a5b1f578ae837498037f4badf6e4c2dbc
physical calls: 15
calls with errors: 0
~~~

Under the frozen strict budget, self-check, post-hoc audit, and BAA each produced 6/7 delegable episodes at C0, C1, and C2. This is a null result for delegation-frontier expansion.

The terminal lost-confirmation episode was non-delegable in every regime. BAA stopped later actions after the first unresolved effect, while the direct regimes continued two later obligations; this changed useful-delivery traces but not the final delegable set.

The model never proposed stale-authority, wrong-subject, or scope-probing actions in the accepted run, so BAA recorded zero admission-denial interventions. The real-model prompt explicitly preferred authoritative evidence and exact identifiers; this study therefore does not reproduce the adversarial proposal behavior in the deterministic fixtures.

Two earlier runs are excluded from the accepted result: `37392398429` exposed a JSON/SSE client compatibility bug, and `37393326558` exposed post-completion adaptive-call overcounting. Both were fixed and regression-tested before the accepted rerun.

See [prospective-model-result.md](prospective-model-result.md).

### v2 qualification outcome

The second preregistered real-model study, `prospective-offboarding-v2`, did not produce an accepted frontier result.

- formal run `37395717489` failed model-evidence qualification with transport and schema errors;
- diagnostic run `37397784048` reduced transport errors to zero but retained one schema error;
- the remaining failure was a model-produced execute object using `case_subject` while omitting required `obligation_id` and `subject_ref`;
- therefore the mechanically emitted 9/12 frontier summaries are not accepted comparative evidence.

The result is recorded as a qualification failure, not resampled until success. See [prospective-model-v2-result.md](prospective-model-v2-result.md).

## What remains unproved

The repository does not establish:

- completeness of the threat model;
- correctness of HR policy or termination decisions;
- production tenant configuration correctness;
- production credential, network, and infrastructure isolation;
- completeness or independence of production IAM/HRIS observations;
- absence of uncovered side channels;
- real-world failure probabilities;
- worst-case safety against arbitrary adaptive agents;
- production delegation leverage;
- principal attention savings;
- third-party assurance labor savings;
- the full semantic bridge from kernel invariants to all relevant real-world harms;
- physical exactly-once execution in external products.

## Experiment interpretation

Positive acceptance results remain falsification evidence, not open-world probability estimates. The prospective real-model comparison also retains its null result rather than treating absence of advantage as a failed run.

The evidence supports four statements that must remain separate:

- structural/reference: modeled forbidden transitions are mechanically excluded under stated assumptions;
- integration: the pinned AIOS runtime and bounded gate preserve the intended action-state distinctions and recovery behavior;
- product compatibility: the covered connector operations work against real ephemeral Keycloak/Odoo instances under explicit temporary test configuration;
- composed acceptance: one bounded offboarding episode can traverse the BAA/AIOS/World Runtime/product/read-back chain and recover from the tested ambiguous transport and observation faults;
- prospective comparison: the first frozen real-model workload did not show delegation-frontier expansion, while still showing a stricter BAA trajectory after an unresolved effect.

None implies that a production tenant is safe.

## Convergence criterion for this phase

The reference/network/product-composition phase is converged because:

1. one task domain is pinned to a source version;
2. guarantee boundary and semantic-bridge assumptions are explicit;
3. the protocol is executable;
4. safety and delivery are measured separately;
5. ambiguous effects remain unresolved rather than silently retried;
6. independently resolved ambiguity can resume bounded execution;
7. adaptive retry is present in threat fixtures;
8. finite admission-state exploration is automated;
9. CI runs regression tests and deterministic comparison harnesses;
10. source-domain contracts are pinned and checked;
11. the action path crosses an actual HTTP/process/Docker boundary;
12. isolated lost acknowledgement and read-back outage recover without duplicate fixture writes;
13. unauthorized Runtime bypass is rejected before provider execution;
14. real Keycloak disable/session-revoke behavior is exercised;
15. real Odoo deactivation/reconciliation behavior is exercised;
16. writer/verifier separation is tested on both products;
17. one composed real-product episode reaches externally verified completion;
18. real-product lost-ack and read-back-outage scenarios persist and recover explicit reconciliation state;
19. the Runtime bypass test leaves real ephemeral product state unchanged;
20. documentation states what is and is not proved;
21. one real-model comparative workload was preregistered before interpretation and run with version-pinned evidence;
22. implementation-invalid runs were excluded explicitly, and the final accepted run retained a null delegation-frontier result.

## Next phase boundary

Connector-only or composition-only expansion remains unjustified. The first prospective comparative study is now complete and produced a null frontier result.

The next phase is **prospective comparative generalization with a machine-constrained proposal interface**, using a new study version rather than modifying v1 or v2.

It should preserve the hidden-control evidence design, the same three regimes, and the same accounting contract, while replacing free-form JSON compliance with a machine-enforced structured-output proposal schema. Episode assignment must remain prospective, unresolved outcomes must remain in the denominator, and model-visible C must remain only a feedback-horizon resource.

Primary outcomes remain:

- useful delivery;
- unsafe or out-of-scope reality-facing transitions;
- unresolved-result duration;
- replay / duplicate logical-request behavior;
- principal attention;
- third-party assurance labor;
- automatic assurance interventions;
- recovery quality;
- sensitivity to adaptive feedback and strategic proposal behavior.

The core falsifiable question is unchanged:

> Under common attention budget A and risk limit R, does BAA increase useful delivery or enlarge the delegable task set, and does that gain persist when the proposal policy actually encounters pressure toward unsafe or ambiguous actions?
