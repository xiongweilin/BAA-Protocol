# Prototype Status

## Current claim level

The repository has reached an executable reference baseline and an isolated production-like network acceptance baseline for one concrete domain: employee offboarding.

The strongest current claim is:

> For the finite BAA reference model, explicit fault fixtures, and the pinned AIOS administrative execution contract, the BAA regime mechanically constrains the modeled offboarding action path and preserves explicit uncertainty. In an isolated network acceptance run on the Windows self-hosted runner, the same bounded-action path completed normal execution, recovered from lost acknowledgement and read-back outage without duplicate reality writes, and rejected an unauthorized Runtime bypass before provider execution.

This is not a claim of real Odoo/Keycloak safety, general unattended-autonomy safety, or production certification.

## What is executable

The prototype now includes:

- generic bounded action admission;
- concrete employee-offboarding admission;
- exact-scope capabilities;
- authority-epoch and controlled state-version invalidation;
- effective-time and verification gating;
- explicit deferred/no-attempt semantics for admission HOLD;
- unresolved-effect preservation;
- retry suppression after ambiguous effect;
- recovery after independently resolved ambiguous effects;
- protected guarantee-source isolation;
- a conservative unresolved-effect concurrency limit;
- VSAR event capture;
- self-check, post-hoc audit, and BAA experiment regimes;
- episode-level deterministic fault fixtures;
- finite exhaustive admission checks;
- a projection from real AIOS Administrative obligations;
- CI against a pinned AIOS checkout.

## Pinned AIOS compatibility

BAA CI pins the merged AIOS recovery contract at:

~~~text
xiongweilin/aios@6f51a0f96d2b6c7a5077d3ab745f6da749930964
~~~

CI independently verifies:

1. AIOS offboarding policy effects equal the BAA hard-domain effect set.
2. AIOS-derived external obligations project without losing case, subject, authority epoch, governance basis, target system, or operation.
3. Covered AIOS reality postconditions map to the BAA verification surface.
4. Every covered effect maps to an actual AIOS World Runtime capability.
5. The BAA kernel can admit, execute, verify, recover, and externally complete obligations derived by the pinned AIOS code.

These checks detect contract drift. They do not prove that real HRIS / IAM observations are complete or independent.

## Real AIOS execution-engine gate

The integration suite wraps the AIOS `OffboardingExecutionEngine` with the BAA provider gate.

It verifies finite execution-path properties including:

- a normal authorized offboarding episode completes all three covered external obligations;
- an ambiguous effect with no independent read-back remains unresolved and is not replayed;
- a lost acknowledgement after a committed effect can be settled by independent read-back, after which the same authority epoch resumes the remaining bounded execution;
- BAA HOLD remains a deferred/no-attempt state rather than being mislabeled as an outcome-unknown external attempt.

The pinned production World Runtime surface is also exercised locally: all three covered capabilities require authorization, resource binding, and version binding; writer and verifier credential domains are distinct; and a request without authorization is rejected before provider execution.

## Windows network acceptance evidence

A production-like isolated network acceptance passed on the repository-scoped Windows self-hosted runner:

~~~text
workflow run: 37302243172
workflow head: 600ada8075d4641f22293bf0ba97482c4e73a55c
runner: aios-windows-docker-desktop
evidence artifact: baa-offboarding-network-37302243172-1
artifact id: 11343085097
~~~

The execution topology was:

~~~text
AIOS OffboardingExecutionEngine
  -> BAA gate
  -> WorldRuntimeBridge over HTTP
  -> World Runtime process
  -> isolated network effect service

Independent read-back:
BAA gate -> network read-back endpoint -> external observed state
~~~

Observed evidence:

- Runtime mandate probe: HTTP 200, active.
- Runtime covered effect-rule count: 3.
- Normal episode: completed, exactly 3 unique external writes.
- Lost acknowledgement:
  - first externally visible state: executing;
  - first sandbox state: exactly 1 committed write;
  - final state: completed;
  - final sandbox state: exactly 3 unique writes;
  - duplicate writes: 0.
- Read-back outage:
  - first externally visible state: executing;
  - first sandbox state: exactly 1 committed write;
  - final state: completed;
  - final sandbox state: exactly 3 unique writes;
  - duplicate writes: 0.
- Unauthorized Runtime bypass:
  - HTTP 403;
  - provider writes before: 0;
  - provider writes after: 0.

This establishes that the bounded-action path can cross a real HTTP/process/Docker boundary on the target Windows workstation while preserving the modeled no-replay and authorization properties for the synthetic effect service.

## What remains unproved

The repository does not establish:

- completeness of the threat model;
- correctness of HR policy or termination decisions;
- completeness or independence of real IAM / HRIS observations;
- real Keycloak or Odoo behavior;
- absence of uncovered side channels;
- production credential and infrastructure isolation;
- real-world failure probabilities;
- worst-case safety against arbitrary adaptive agents;
- production delegation leverage;
- episode-level principal attention savings;
- third-party assurance labor savings;
- the full semantic bridge from kernel properties to all relevant real-world harms.

## Experiment interpretation

The network acceptance is still a falsification harness, not a probability estimator.

A positive run means:

> Under the explicit modeled workload, network faults, authorization boundary, and isolated effect service, the enforced protocol changes which reality-facing transitions can occur and can recover to useful completion without replaying committed effects.

It does not estimate failure probability over an open environment.

The next empirical claim is stronger:

> Under the same useful offboarding workload and less synthetic execution/read-back interfaces, does BAA improve the feasible delivery frontier under common attention and risk constraints after assurance labor is counted?

## Convergence criterion for this phase

The current prototype/network-acceptance phase is converged because:

1. one task domain is pinned to a source version;
2. guarantee boundary and semantic-bridge assumptions are explicit;
3. the protocol is executable;
4. safety and delivery are measured separately;
5. ambiguous effects remain unresolved rather than silently retried;
6. independently resolved ambiguity can resume bounded execution;
7. adaptive retry is present in threat fixtures;
8. finite admission-state exploration is automated;
9. CI runs regression tests and deterministic comparison harnesses;
10. real source-domain contracts are checked for compatibility;
11. the action path crosses an actual HTTP/process/Docker boundary;
12. lost acknowledgement and read-back outage recover without duplicate external writes;
13. an unauthorized Runtime bypass is rejected before provider execution;
14. documentation states what is and is not proved.

## Next phase boundary

Further local conceptual or reference-model expansion is not justified by the current evidence.

The next stronger phase should replace one or more synthetic boundaries with faithful or real administrative systems while keeping the same evidence discipline:

- real or high-fidelity Odoo / HRIS execution and read-back;
- real or high-fidelity Keycloak / IAM execution and read-back;
- independently controlled writer and verifier credentials in deployment;
- measured latency, outage, concurrency, and recovery distributions;
- episode-level principal attention;
- third-party assurance labor;
- useful delivery under common attention and risk constraints.

Until then, the strongest supported level is:

> reference model + pinned AIOS contract compatibility + finite execution-engine gate + isolated production-like network acceptance on the target Windows runner.
