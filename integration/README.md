# AIOS Integration Boundary

BAA-Protocol pins the first employee-offboarding integration to:

~~~text
xiongweilin/aios@d2ca4e9e874bec1f5c28911e8175ff84e5f45055
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

The integration tests establish two finite properties:

1. A normal authorized offboarding episode can pass through the gate and complete the three covered external obligations.
2. If the first provider execution has an ambiguous outcome, BAA preserves it as unresolved, prevents later provider dispatch under `U_max = 1`, and repeated AIOS reconciliation does not re-execute the ambiguous effect.

This is the first test in the repository where BAA changes the actual execution path of the pinned AIOS engine.

## Remaining boundary

The current integration still uses an in-memory AIOS database and a deterministic provider fixture.

It does not yet establish:

- World Runtime HTTP cutover behavior through the BAA gate;
- non-bypassability across a deployed process / network boundary;
- real Keycloak or Odoo behavior;
- independence of writer and verifier credentials in deployment;
- real latency, outage, concurrency, or operator-attention distributions;
- empirical delegation leverage.

Those require a production-like runtime experiment rather than more reference-model structure.


## Level 3: pinned World Runtime enforcement prerequisite

CI builds the pinned AIOS production World Runtime stack without contacting the configured external services and checks the covered offboarding capability surface.

For the three BAA-covered capabilities it verifies:

- `authorization_required == true`;
- `resource_required == true`;
- `version_required == true`;
- exactly one registered writer and one registered verification capability;
- writer and verifier use different credential domains;
- an invocation missing authorization is rejected by World Runtime before provider execution.

This establishes a local enforcement prerequisite for the pinned runtime version. The current BAA gate test and the World Runtime test are still separate paths; BAA has not yet been deployed through the actual World Runtime HTTP cutover boundary.

## Converged local boundary

The repository can now test, without external infrastructure:

~~~text
BAA reference semantics
  -> AIOS contract projection
  -> real AIOS offboarding execution engine
  -> pinned World Runtime enforcement prerequisites
~~~

The next non-synthetic step requires an executable network boundary and external effect/read-back services. Further local abstraction would not strengthen the same empirical claim.
