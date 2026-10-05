# AIOS Integration Boundary

BAA-Protocol pins the first employee-offboarding integration to:

~~~text
xiongweilin/aios@600ada8075d4641f22293bf0ba97482c4e73a55c
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

AIOS workflow run `37302243172` completed successfully on `aios-windows-docker-desktop` at AIOS head `600ada8075d4641f22293bf0ba97482c4e73a55c`.

Its retained evidence reports:

- mandate probe: HTTP 200 / active;
- normal: `completed`, three unique writes;
- lost acknowledgement: `executing -> completed`, three final unique writes, `duplicate_writes = 0`;
- read-back outage: `executing -> completed`, three final unique writes, `duplicate_writes = 0`;
- unauthorized Runtime bypass: HTTP 403, provider writes `0 -> 0`.

The evidence qualification is intentionally narrow: production-like network acceptance with isolated synthetic effects; it is not real Odoo/Keycloak evidence.

It still does not establish:

- real Keycloak or Odoo behavior;
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

The pinned AIOS repository additionally provides the isolated network acceptance path described above. The next stronger empirical step is no longer another local abstraction layer; it is evidence from less synthetic effect/read-back services and eventually the real administrative systems under an explicit deployment threat model.
