# AIOS Integration Boundary

BAA-Protocol pins the first employee-offboarding integration to:

~~~text
xiongweilin/aios@e585cd5dd7e7a8dce75680992720b7a6941b6e0a
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

AIOS workflow run `37302243172` completed successfully on `aios-windows-docker-desktop` at AIOS head `e585cd5dd7e7a8dce75680992720b7a6941b6e0a`.

Its retained evidence reports:

- mandate probe: HTTP 200 / active;
- normal: `completed`, three unique writes;
- lost acknowledgement: `executing -> completed`, three final unique writes, `duplicate_writes = 0`;
- read-back outage: `executing -> completed`, three final unique writes, `duplicate_writes = 0`;
- unauthorized Runtime bypass: HTTP 403, provider writes `0 -> 0`.

The evidence qualification is intentionally narrow: production-like network acceptance with isolated synthetic effects.

### Real Keycloak connector acceptance

The pinned AIOS commit also contains a high-fidelity connector acceptance against an ephemeral real Keycloak 26.8.0 server. AIOS workflow run `37307098287` completed successfully on `main`; artifact `real-keycloak-offboarding-37307098287` (artifact id `11343404378`) records:

- a real user session existed before offboarding and was reduced from 1 active session to 0;
- the AIOS identity-disable connector succeeded and independent read-back observed `enabled = false`;
- disable reconciliation succeeded;
- the AIOS session-revoke connector succeeded and independent read-back observed `active_sessions = 0`;
- session-revoke reconciliation succeeded;
- writer and verifier used distinct service clients;
- a write attempted with the verifier identity was rejected with HTTP 403.

The Keycloak realm used explicit admin-only managed User Profile attributes for the durable BAA/AIOS identities and kept unmanaged attributes disabled. This is evidence about the real Keycloak product/API and AIOS connector behavior, but it is still an ephemeral test realm rather than a production tenant.

It still does not establish:

- real Odoo behavior;
- production Keycloak tenant configuration or credential administration;
- production credential and infrastructure isolation;
- real latency, outage, concurrency, or operator-attention distributions;
- empirical delegation leverage on a non-synthetic workload.


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

The pinned AIOS repository additionally provides both the isolated end-to-end network acceptance path and the real ephemeral Keycloak connector acceptance described above. The next stronger empirical step is real or high-fidelity Odoo/HRIS behavior, followed by composed Administrative execution against independently controlled external systems under an explicit deployment threat model.
