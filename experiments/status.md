# Prototype Status

## Current claim level

The repository has reached five evidence layers for one concrete domain: employee offboarding.

1. Executable BAA reference semantics and deterministic fault fixtures.
2. Pinned AIOS contract compatibility and execution-engine gating.
3. Isolated production-like network acceptance across HTTP/process/Docker boundaries.
4. High-fidelity connector acceptance against real ephemeral Keycloak and Odoo product instances.
5. Single-episode composition through BAA, the real AIOS offboarding engine, World Runtime, both ephemeral products, and independently credentialed product read-back.

The strongest current claim is:

> For the finite BAA model and the pinned AIOS offboarding implementation at commit `87f24f32a01c67a9246fc3cb127517c80798e169`, the tested protocol can constrain one composed offboarding episode through AIOS and World Runtime into real ephemeral Keycloak and Odoo instances, independently read back the covered product state, recover the tested lost-acknowledgement and read-back-outage cases while preserving logical request identity, and reject the tested unauthorized Runtime bypass before product mutation.

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
- single-episode real-product composition through BAA, AIOS, World Runtime, Keycloak, Odoo, and independent read-back.

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

## Real-product end-to-end evidence

AIOS workflow run `37315551794` passed at PR head `b0bb3705d5180557e35a5e6b103c912c32169b70`, whose tree was merged to AIOS main as `87f24f32a01c67a9246fc3cb127517c80798e169`.

The matrix executed four isolated ephemeral-product scenarios:

- **normal** — one offboarding case completed with three effects, three realizations, three confirmed outcomes, and BAA knowledge `verified_effected` for all covered obligations;
- **lost acknowledgement** — Keycloak identity disable committed before acknowledgement was discarded; the case persisted reconciliation transitions, retained a stable disable request identity, independently read back the product state, resumed execution, and completed;
- **read-back outage** — the independent verifier first returned unavailable for identity disable; the case persisted reconciliation transitions, later resolved the real product state, and completed without changing the logical request identity;
- **unauthorized Runtime bypass** — direct effectful invocation without authorization returned HTTP 403, `provider_effect_observed = false`, and Keycloak/Odoo product state was unchanged.

The normal and recovery scenarios independently observed `enabled = false`, `active_sessions = 0`, and `active = false`. Writer and verifier credentials remained distinct, and verifier mutation attempts were denied for both products.

The recovery claim is deliberately about stable logical request identity plus independent reconciliation; it is not a proof of physical exactly-once delivery.

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
- the full semantic bridge from kernel invariants to all relevant real-world harms.

## Experiment interpretation

All current positive results remain falsification evidence, not open-world probability estimates.

The evidence now supports four different statements that must remain separate:

- structural/reference: modeled forbidden transitions are mechanically excluded under stated assumptions;
- integration: the pinned AIOS runtime and bounded gate preserve the intended action-state distinctions and recovery behavior;
- product compatibility: the covered connector operations work against real ephemeral Keycloak/Odoo instances under explicit temporary test configuration;
- composed acceptance: one tested offboarding episode can cross BAA, AIOS, World Runtime, both products, and independent read-back under the four tested acceptance scenarios.

None implies that a production tenant is safe.

## Convergence criterion for this phase

The reference/network/product-connector phase is converged because:

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
12. lost acknowledgement and read-back outage recover without duplicate writes;
13. unauthorized Runtime bypass is rejected before provider execution;
14. real Keycloak disable/session-revoke behavior is exercised;
15. real Odoo deactivation/reconciliation behavior is exercised;
16. writer/verifier separation is tested on both products;
17. a single episode composes BAA, AIOS, World Runtime, real ephemeral Keycloak/Odoo, and independent product read-back;
18. lost acknowledgement and read-back outage persist explicit reconciliation transitions and recover with stable logical request identity;
19. unauthorized Runtime bypass leaves the real ephemeral product state unchanged;
20. documentation states what is and is not proved.

## Next phase boundary

The composition phase is converged for the current ephemeral employee-offboarding domain. Further connector-only or acceptance-topology expansion is not the next research question.

The next experiment should test **delegation leverage** by comparing, at the episode or shared-influence-domain level:

1. agent self-check;
2. agent plus external record / post-hoc audit;
3. BAA non-bypassable admission, constrained execution, verification, and exposure control.

Under common principal-attention budget and risk limit, it should measure useful delivery, principal attention, third-party assurance labor, recovery quality, unknown duration, and duplicate/replay behavior while increasing adaptive attacker capability.

Until such comparative evidence exists, the strongest supported level is:

> reference guarantees + pinned AIOS execution gating + isolated network recovery + real-product connector compatibility + single-episode real-product end-to-end acceptance.

This still does not establish production-tenant safety or production delegation leverage.
