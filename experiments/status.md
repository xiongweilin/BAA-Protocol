# Prototype Status

## Current claim level

The repository has reached four evidence layers for one concrete domain: employee offboarding.

1. Executable BAA reference semantics and deterministic fault fixtures.
2. Pinned AIOS contract compatibility and execution-engine gating.
3. Isolated production-like network acceptance across HTTP/process/Docker boundaries.
4. High-fidelity connector acceptance against real ephemeral Keycloak and Odoo product instances.

The strongest current claim is:

> For the finite BAA model, the pinned AIOS offboarding contract at commit `f5afd2721e04ab4b9e14c4aecd0e6bc688828783`, the isolated network acceptance fixture, and the tested real-product connector surfaces, the protocol can constrain the modeled offboarding action path, preserve and recover explicit uncertainty without replaying committed effects, and execute the covered IAM/HRIS connector operations against real ephemeral Keycloak and Odoo instances with separate writer/verifier identities.

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
- real ephemeral Odoo connector acceptance.

## Pinned AIOS compatibility

BAA CI pins:

~~~text
xiongweilin/aios@f5afd2721e04ab4b9e14c4aecd0e6bc688828783
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

## What remains unproved

The repository does not establish:

- completeness of the threat model;
- correctness of HR policy or termination decisions;
- end-to-end execution of one BAA offboarding episode through World Runtime into both real product instances;
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

The evidence now supports three different statements that must remain separate:

- structural/reference: modeled forbidden transitions are mechanically excluded under stated assumptions;
- integration: the pinned AIOS runtime and bounded gate preserve the intended action-state distinctions and recovery behavior;
- product compatibility: the covered connector operations work against real ephemeral Keycloak/Odoo instances under explicit temporary test configuration.

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
17. documentation states what is and is not proved.

## Next phase boundary

Further connector-only expansion is not justified by the current evidence.

The next stronger experiment should compose the layers in one episode:

~~~text
BAA admission
  -> AIOS OffboardingExecutionEngine
  -> World Runtime authorization/capability boundary
  -> real ephemeral Keycloak writer
  -> real ephemeral Odoo writer
  -> independently credentialed Keycloak/Odoo read-back
  -> BAA settlement / recovery / completion
~~~

The experiment should include at least normal completion, one ambiguous transport outcome with successful independent read-back, one read-back outage, and one unauthorized bypass attempt. It should preserve the same episode-level evidence accounting and distinguish principal attention from assurance labor.

Until that experiment passes, the strongest supported level is:

> reference guarantees + pinned AIOS execution gating + isolated network recovery + real-product connector compatibility.
