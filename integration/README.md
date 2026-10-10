# AIOS Integration Boundary

> English | [简体中文](README.zh-CN.md)

BAA-Protocol pins the first employee-offboarding integration to:

~~~text
xiongweilin/aios@87f24f32a01c67a9246fc3cb127517c80798e169
~~~

This is the first offboarding integration snapshot and the version used by the recorded composed end-to-end acceptance. The current compatibility workflow separately checks out AIOS commit `0ba9c36bd8168ae1346770e6430474662b30e196`; it does not reproduce that historical end-to-end run.

## Level 1: contract compatibility

The current compatibility workflow imports AIOS at `0ba9c36bd8168ae1346770e6430474662b30e196` and checks:

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
  -> immediate reality read-back
  -> BAA settlement
  -> AIOS verification / completion
~~~

The integration tests establish three finite properties:

1. A normal authorized offboarding episode can pass through the gate and complete the three covered external obligations.
2. If an attempted effect has an ambiguous outcome and independent read-back cannot resolve it, BAA preserves the ambiguity, prevents later provider dispatch under `U_max = 1`, and does not re-execute the ambiguous effect.
3. If an effect is committed but its acknowledgement is lost, independent read-back can settle that effect, the same authority epoch can resume execution, and the remaining covered effects can complete without replaying the committed effect.

A BAA `HOLD` is represented across the AIOS provider boundary as a deferred/no-attempt result, not as an outcome-unknown external attempt. This keeps admission, execution attempt, and observed effect as distinct states.

This is the first test in the repository where BAA changes the actual execution path of the pinned AIOS engine.

## Network acceptance boundary

The compatibility tests in this repository still use an in-memory AIOS database and deterministic provider fixtures. The pinned AIOS commit now also contains an executable network acceptance path at `tests/acceptance/baa_offboarding`:

~~~text
AIOS OffboardingExecutionEngine
  -> BAA gate
  -> WorldRuntimeBridge over HTTP
  -> World Runtime process
  -> isolated network effect service

Independent read-back:
BAA gate -> network read-back endpoint -> external observed state
~~~

That acceptance path is designed to exercise normal completion, lost acknowledgement, read-back outage, and an unauthorized Runtime bypass attempt while preserving exact-once observed effects in the isolated fixture.

### Recorded network evidence

AIOS workflow run `37302243172` completed successfully on `aios-windows-docker-desktop` at AIOS head `600ada8075d4641f22293bf0ba97482c4e73a55c`.

Its retained evidence reports:

- mandate probe: HTTP 200 / active;
- normal: `completed`, three unique writes;
- lost acknowledgement: `executing -> completed`, three final unique writes, `duplicate_writes = 0`;
- read-back outage: `executing -> completed`, three final unique writes, `duplicate_writes = 0`;
- unauthorized Runtime bypass: HTTP 403, provider writes `0 -> 0`.

The evidence qualification is intentionally narrow: production-like network acceptance with isolated synthetic effects; it is not real Odoo/Keycloak evidence.

The isolated network evidence remains intentionally synthetic. It does not establish production credential and infrastructure isolation, real production latency/outage/concurrency distributions, or empirical delegation leverage.


## Real product connector evidence

The pinned AIOS commit also contains high-fidelity acceptance against ephemeral instances of the actual administrative products used by the offboarding connectors.

### Keycloak

AIOS workflow run `37306648690` passed against Keycloak `26.8.0`.

The test uses real Admin REST and OAuth client-credentials flows and verifies:

- separate writer and verifier service accounts;
- a real user session exists before offboarding;
- `identity.disable` succeeds and is independently read back;
- `sessions.revoke` reduces the real session count from one to zero;
- durable request metadata is reconciled through the connector;
- the verifier credential cannot mutate users (HTTP 403).

Evidence artifact: `real-keycloak-offboarding-37306648690` (artifact id `11344280550`).

### Odoo

AIOS workflow run `37307582025` passed against real Odoo `18.0-20260926` with PostgreSQL.

The test uses real JSON-RPC and verifies:

- separate writer and verifier Odoo users;
- exact `hr.employee` deactivation;
- a durable deactivate request marker;
- independent read-back of `active = false`;
- reconciliation after the employee becomes inactive;
- verifier write denial.

The real Odoo run exposed one production-relevant issue: normal Odoo searches hide inactive employees. The connector now performs durable identity lookup with `active_test = false`, and a regression test locks that behavior.

Evidence artifact: `real-odoo-offboarding-37307582025` (artifact id `11344206985`).

These runs establish standalone connector compatibility with real ephemeral product instances. They do not by themselves establish production-tenant safety or production credential isolation.

## Composed real-product end-to-end evidence

AIOS workflow run `37315551794` passed at PR head `b0bb3705d5180557e35a5e6b103c912c32169b70`; that tree was merged unchanged as AIOS commit `87f24f32a01c67a9246fc3cb127517c80798e169`.

The matrix composes the previously separate layers:

~~~text
BAA admission
  -> AIOS OffboardingExecutionEngine
  -> WorldRuntimeBridge over HTTP
  -> World Runtime authorization/capability boundary
  -> real ephemeral Keycloak/Odoo writers
  -> independently credentialed Keycloak/Odoo read-back
  -> AIOS semantic verification
  -> BAA settlement / recovery / external completion
~~~

Four scenarios passed:

- `normal`: the case reaches `completed`; Keycloak reports `enabled = false` and `active_sessions = 0`; Odoo reports `active = false`; all three external obligations are independently read back and reach BAA `verified_effected`;
- `lost_ack`: the real Keycloak disable effect exists after the first ambiguous attempt, recovery persists `case.reconciliation_started` and `case.reconciliation_resolved_for_execution`, and the durable logical request identity remains stable rather than being replaced by a new request;
- `readback_outage`: the effect remains unresolved while independent read-back is unavailable, then resumes through the same persisted reconciliation transition after read-back recovers;
- `runtime_bypass`: a direct effectful Runtime invocation without authorization returns HTTP 403, `provider_effect_observed = false`, and the before/after Keycloak and Odoo product state is unchanged.

The E2E harness also re-checks credential separation: Keycloak verifier mutation is denied and Odoo verifier mutation is denied.

The claim is narrower than physical exactly-once delivery: the experiment establishes stable logical request identity and no blind replay in the tested recovery path. It remains ephemeral acceptance evidence, not production-tenant safety, production infrastructure isolation, or a delegation-leverage result.

## Level 3: pinned World Runtime enforcement prerequisite

CI builds the pinned AIOS production World Runtime stack without contacting the configured external services and checks the covered offboarding capability surface.

For the three BAA-covered capabilities it verifies:

- `authorization_required == true`;
- `resource_required == true`;
- `version_required == true`;
- exactly one registered writer and one registered verification capability;
- writer and verifier use different credential domains;
- an invocation missing authorization is rejected by World Runtime before provider execution.

This establishes a local enforcement prerequisite for the pinned runtime version. The repository-local BAA gate test and World Runtime prerequisite test remain separate compatibility checks. The pinned AIOS network acceptance path is the executable place where those components are composed across an HTTP/process boundary.

## Converged local boundary

The repository can test, without external infrastructure:

~~~text
BAA reference semantics
  -> AIOS contract projection
  -> real AIOS offboarding execution engine
  -> pinned World Runtime enforcement prerequisites
~~~

The pinned AIOS repository additionally provides the isolated network acceptance, standalone real-product connector acceptance, and the composed real-product E2E matrix described above. The next research step is no longer connector composition; it is the comparative delegation experiment across self-check, post-hoc audit, and non-bypassable BAA regimes under common attention and risk constraints.
