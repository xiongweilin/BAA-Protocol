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
