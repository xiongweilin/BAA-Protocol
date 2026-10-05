# AIOS Integration Boundary

BAA-Protocol pins the employee-offboarding integration to:

~~~text
xiongweilin/aios@87f24f32a01c67a9246fc3cb127517c80798e169
~~~

## Level 1: contract compatibility

CI imports the pinned AIOS package and checks:

- offboarding policy effect set;
- derived external obligations;
- expected reality postconditions;
- World Runtime capability mapping;
- execution of AIOS-derived obligations by the BAA reference kernel.

This establishes compatibility with the pinned contract surface only.

## Level 2: real AIOS execution-engine gate

`BAAGatedAIOSProvider` is an integration-only provider wrapper placed on the actual AIOS `OffboardingExecutionEngine` effect boundary:

~~~text
AIOS OffboardingExecutionEngine
  -> AIOS EffectRecord
  -> BAA admission / narrow capability
  -> underlying EffectProvider
  -> independent reality read-back
  -> BAA settlement
  -> AIOS verification / completion
~~~

The repository-local integration tests establish that:

1. a normal authorized offboarding episode can pass through the gate;
2. an unresolved ambiguous effect blocks later dispatch under the conservative unresolved limit;
3. independent read-back can settle a committed effect whose acknowledgement was lost;
4. BAA HOLD remains distinct from an external attempt with unknown outcome.

## Level 3: isolated network boundary

AIOS workflow run `37302243172` composes the bounded path across real HTTP/process/Docker boundaries using an isolated synthetic effect service:

~~~text
AIOS OffboardingExecutionEngine
  -> BAA gate
  -> WorldRuntimeBridge over HTTP
  -> World Runtime
  -> network effect service
  -> independent network read-back
~~~

It passes:

- normal completion;
- lost acknowledgement recovery;
- read-back outage recovery;
- unauthorized Runtime bypass rejection.

This level proves network composition for the tested fixture, not real product behavior.

## Level 4: standalone real-product connector boundary

### Keycloak

AIOS workflow run `37306648690` exercises real ephemeral Keycloak `26.8.0` with separate writer/verifier clients, identity disable, session revoke, durable reconciliation metadata, independent read-back, and verifier write denial.

### Odoo

AIOS workflow run `37307582025` exercises real ephemeral Odoo `18.0-20260926` with PostgreSQL, separate writer/verifier users, employee deactivation, durable request identity, independent read-back, reconciliation after deactivation, and verifier write denial.

These runs establish high-fidelity connector compatibility separately.

## Level 5: single-episode real-product composition

AIOS workflow run `37315551794` passes a four-scenario matrix that composes the prior layers in one topology:

~~~text
BAA admission
  -> AIOS OffboardingExecutionEngine
  -> WorldRuntimeBridge
  -> World Runtime authorization/capability boundary
  -> real ephemeral Keycloak writer
  -> real ephemeral Odoo writer
  -> separately credentialed Keycloak/Odoo read-back
  -> semantic postcondition verification
  -> BAA settlement / AIOS reconciliation / completion
~~~

The same Odoo employee reference is also written into Keycloak as the administrative subject reference, giving one explicit cross-system subject identity.

### Normal

All three covered product postconditions are independently observed:

~~~text
Keycloak:
  enabled = false
  active_sessions = 0

Odoo:
  active = false
~~~

Durable request markers exist for identity disable, session revoke, and Odoo deactivation.

### Lost acknowledgement

A real Keycloak identity-disable mutation is committed, then its acknowledgement is converted to an unknown Runtime result.

The first execution therefore sees a genuinely advanced external state without a trusted acknowledgement. Independent read-back and reconciliation recover the episode to completion. The logical disable request identity remains stable.

AIOS audit history must include:

~~~text
case.reconciliation_started
case.reconciliation_resolved_for_execution
~~~

### Read-back outage

A real product write succeeds while the independent verifier returns unavailable once.

Uncertainty is retained, the reconciliation state is persisted, and execution resumes only after independent read-back becomes available.

### Runtime authorization bypass

The scenario creates responsibility/work/run state and then invokes an effectful Runtime capability without an execution authorization.

The expected result is HTTP 403 specifically at the authorization boundary, with no change in real Keycloak or Odoo state.

## Semantic bridge improvement in the pinned baseline

The pinned AIOS version closes a verifier gap discovered while constructing this E2E.

The generic Administrative semantic verifier now explicitly checks all covered product state fields:

~~~text
active
enabled
active_sessions
~~~

Therefore:

~~~text
expected enabled = false
observed enabled = true
=> mismatch

expected active_sessions = 0
observed active_sessions > 0
=> mismatch
~~~

Product observation remains separate from frozen execution context. `complete_readback_postcondition()` combines those sources into the semantic evidence view; it does not replace product observations with desired values.

## World Runtime enforcement prerequisite

The pinned Runtime surface requires, for the three covered effect capabilities:

- authorization;
- resource binding;
- version binding.

Writer and verifier trust domains remain distinct in the production-stack registration surface.

The E2E authorization-bypass scenario goes beyond the earlier static prerequisite check by driving a direct Runtime request to the missing-authorization boundary and verifying no real product mutation occurs.

## Current convergence boundary

Without production infrastructure, the repositories can now test:

~~~text
BAA reference semantics
  -> AIOS contract projection
  -> real AIOS execution engine
  -> World Runtime over HTTP
  -> real ephemeral Keycloak + Odoo
  -> independent read-back
  -> semantic verification
  -> ambiguous-result recovery
  -> completion
~~~

This does not establish production-tenant safety, production credential/network isolation, open-world failure probabilities, or delegation leverage.

The next research step is comparative rather than another integration layer: measure self-check, post-hoc audit, and BAA regimes under common workload, attention, exposure, and adaptive-attack conditions.
