# Prototype Status

## Current claim level

The repository has reached five evidence layers for one concrete domain: employee offboarding.

1. Executable BAA reference semantics and deterministic fault fixtures.
2. Pinned AIOS contract compatibility and execution-engine gating.
3. Isolated production-like network acceptance across HTTP/process/Docker boundaries.
4. High-fidelity connector acceptance against real ephemeral Keycloak and Odoo product instances.
5. Single-episode real-product end-to-end acceptance composing BAA, AIOS, World Runtime, both products, independent read-back, and recovery.

The pinned AIOS baseline is:

~~~text
xiongweilin/aios@87f24f32a01c67a9246fc3cb127517c80798e169
~~~

The strongest current claim is:

> For the finite BAA model and the tested employee-offboarding deployment topology, one bounded offboarding episode can pass through BAA admission, the AIOS execution engine, the World Runtime authorization/capability boundary, real ephemeral Keycloak and Odoo writers, separately credentialed product read-back, semantic postcondition verification, and completion. The same topology can recover from a lost acknowledgement and an independent read-back outage while preserving stable logical request identity and persisted reconciliation transitions, and it rejects a direct Runtime invocation at the authorization boundary before real product state changes.

This remains falsification/integration evidence. It is not a production-tenant safety claim, a general unattended-autonomy theorem, or a certification result.

## What is executable

The prototype and pinned AIOS baseline now cover:

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
- self-check, post-hoc audit, and BAA reference experiment regimes;
- deterministic episode-level fault fixtures;
- finite exhaustive admission checks;
- projection from real AIOS Administrative obligations;
- pinned AIOS compatibility CI;
- isolated Windows/Docker network acceptance;
- real ephemeral Keycloak connector acceptance;
- real ephemeral Odoo connector acceptance;
- a real-product end-to-end fault matrix using both products in one episode topology.

## Pinned AIOS compatibility

BAA CI pins:

~~~text
xiongweilin/aios@87f24f32a01c67a9246fc3cb127517c80798e169
~~~

CI verifies the contract and local enforcement surface:

1. AIOS offboarding policy effects equal the BAA hard-domain effect set.
2. AIOS-derived external obligations project without losing case, subject, authority epoch, governance basis, target system, or operation.
3. Covered AIOS reality postconditions map to the BAA verification surface.
4. Every covered effect maps to an AIOS World Runtime capability.
5. The BAA kernel can admit, execute, verify, recover, and externally complete obligations derived by the pinned AIOS code.
6. The BAA provider gate changes the actual AIOS execution path while preserving deferred/no-attempt versus outcome-unknown semantics.
7. The pinned World Runtime surface requires authorization, resource binding, version binding, and separated writer/verifier credential domains.

The pinned AIOS version additionally fixes semantic verification so the IAM postconditions `enabled = false` and `active_sessions = 0` cannot be silently ignored.

## Isolated network evidence

AIOS workflow run `37302243172` passed on the repository-scoped Windows/Docker Desktop runner.

Observed evidence:

- normal episode: completed with exactly three unique external writes;
- lost acknowledgement: recovered to completion with three unique writes and zero duplicates;
- read-back outage: recovered to completion with three unique writes and zero duplicates;
- unauthorized Runtime bypass: HTTP 403 with zero provider writes.

This establishes recovery and authorization behavior across a real HTTP/process/Docker boundary using a synthetic effect service.

## Standalone real-product connector evidence

### Keycloak

AIOS workflow run `37306648690` passed against Keycloak `26.8.0`.

Observed evidence includes real OAuth/Admin REST, distinct writer/verifier service accounts, identity disable, real session count from one to zero, durable reconciliation metadata, independent read-back, and verifier mutation denial.

### Odoo

AIOS workflow run `37307582025` passed against Odoo `18.0-20260926` with PostgreSQL.

Observed evidence includes real JSON-RPC, distinct writer/verifier users, exact `hr.employee` deactivation, durable request identity, independent read-back, reconciliation after deactivation, and verifier write denial.

This run exposed the inactive-record lookup issue; durable Odoo lookup now uses `active_test = false`, with regression coverage.

## Single-episode real-product E2E evidence

AIOS workflow run `37315551794` passed all four scenarios against real ephemeral Keycloak and Odoo instances:

### Normal

The same subject identity, `odoo:hr.employee:<id>`, is carried across Odoo, Keycloak, AIOS obligations, and BAA.

The final independently observed product state is:

~~~text
Keycloak:
  enabled = false
  active_sessions = 0
  disable request marker present
  session-revoke request marker present

Odoo:
  active = false
  deactivate request marker present
~~~

All three covered effects have AIOS effect records, realization assessments, confirmed outcomes, and BAA verified-effect state.

### Lost acknowledgement

The Keycloak identity disable is committed in the real product before the acknowledgement is converted to an unknown outcome.

The first run therefore observes a partially advanced reality: identity disabled, session still present, Odoo employee still active.

Recovery then converges to full completion. The durable disable request identity remains stable, and AIOS persists both:

~~~text
case.reconciliation_started
case.reconciliation_resolved_for_execution
~~~

The claim is stable logical request identity and successful reconciliation, not physical exactly-once transport.

### Read-back outage

A real product write succeeds while the independent verifier is made unavailable once.

The episode preserves uncertainty, persists the reconciliation transition, later resumes after independent read-back, and completes without changing the logical request identity.

### Runtime bypass

The test creates responsibility/work/run state but intentionally omits execution authorization, then directly invokes the effectful Runtime capability.

World Runtime returns HTTP 403 specifically at the authorization boundary. Real Keycloak and Odoo state before and after the attempt is identical.

The real-product matrix also rechecks writer/verifier separation and write denial for the verifier identities.

## Semantic evidence boundary

The real-product E2E does not copy the desired postcondition into the observed state.

Product read-back supplies reality-facing fields:

~~~text
Keycloak:
  enabled
  active_sessions
  durable request markers

Odoo:
  active
  durable request marker
~~~

Frozen execution context supplies fields such as employee reference, employment episode, termination status, and effective time.

AIOS then builds the semantic evidence view and compares the actual product fields with the frozen expected postcondition. This separation is part of the evidence claim.

## What remains unproved

The repository does not establish:

- correctness, legality, or fairness of the underlying HR termination decision;
- production tenant configuration correctness;
- production credential, network, and infrastructure isolation;
- completeness or independence of production IAM/HRIS observations;
- absence of uncovered side channels;
- real-world failure probabilities;
- worst-case safety against arbitrary adaptive agents;
- production delegation leverage;
- principal attention savings;
- third-party assurance labor savings;
- the full semantic bridge from kernel invariants to every relevant real-world harm.

## Experiment interpretation

The positive results must remain separated by evidence type:

- structural/reference: modeled forbidden transitions are mechanically excluded under stated assumptions;
- integration: the pinned AIOS runtime and BAA gate preserve action-state distinctions and recovery behavior;
- product compatibility: covered connectors work against real ephemeral Keycloak/Odoo under explicit temporary configuration;
- composed E2E: one bounded offboarding topology composes BAA, AIOS, Runtime authorization, real product effects, independent read-back, semantic verification, and recovery.

None implies production-tenant safety.

## Convergence criterion for this phase

The real-product integration phase is converged because:

1. the task domain and AIOS version are pinned;
2. the guarantee boundary and semantic-bridge assumptions are explicit;
3. BAA is on the actual execution path;
4. World Runtime enforces authorization/resource/version constraints;
5. real product writers and verifiers use separate identities;
6. one cross-system subject identity is used across the episode;
7. normal completion reaches verified product postconditions;
8. lost acknowledgement recovers without changing logical request identity;
9. read-back outage preserves uncertainty and later resumes;
10. recovery transitions are persisted in the AIOS audit history;
11. unauthorized Runtime invocation is rejected at the authorization boundary;
12. the semantic verifier checks `active`, `enabled`, and `active_sessions`;
13. current CI, Sonar, Acceptance, BAA preflight, and the real-product E2E matrix are green;
14. claim language remains below production-tenant safety.

## Next phase boundary

Further connector or single-episode mechanism expansion is not the main research bottleneck.

The next experiment should return to the original comparative research question and run three regimes under the same task distribution and explicit budgets:

~~~text
A. agent self-check
B. agent + post-hoc audit
C. BAA non-bypassable admission / execution / verification
~~~

Measure at least:

- useful delivery;
- structural/observed safety failures;
- principal attention;
- third-party assurance labor;
- unknown-state duration;
- recovery quality;
- duplicate/replay incidence.

Then increase adaptive attacker capability while holding the workload, attention budget, and exposure constraints comparable.

The next falsifiable claim is therefore not “the mechanism can work”; that has now been demonstrated for this bounded domain. It is:

> Under common attention and risk constraints, does BAA increase useful delegated work or enlarge the feasible delegated task set, and does that advantage persist as adaptive capability increases?
