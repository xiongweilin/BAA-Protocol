# Prototype Status

## Current claim level

The repository has reached an executable reference baseline for one concrete domain: employee offboarding.

The strongest current claim is:

> For the finite BAA reference model and explicit fault fixtures in this repository, the BAA regime mechanically blocks the modeled out-of-scope, stale-authority, premature, protected-source, and ambiguous-replay transitions while preserving explicit unknown states. The BAA offboarding projection is also compatible with the pinned AIOS policy, obligation, postcondition, and World Runtime capability surface at commit `600ada8075d4641f22293bf0ba97482c4e73a55c`.

This is not a real-world safety or production-implementation claim.

## What is executable

The prototype now includes:

- generic bounded action admission;
- concrete employee-offboarding admission;
- exact-scope capabilities;
- authority-epoch and state-version invalidation;
- effective-time and verification gating;
- unresolved-effect preservation;
- retry suppression after ambiguous effect;
- protected guarantee-source isolation;
- a conservative unresolved-effect concurrency limit;
- VSAR event capture;
- self-check, post-hoc audit, and BAA experiment regimes;
- episode-level deterministic fault fixtures;
- finite exhaustive admission checks;
- a thin projection from real AIOS Administrative obligations;
- CI against a pinned AIOS checkout.

## Pinned AIOS compatibility

CI installs the pinned AIOS repository and independently verifies five boundaries:

1. AIOS offboarding policy effects equal the BAA hard-domain effect set.
2. AIOS-derived external obligations project without losing case, subject, authority epoch, governance basis, target system, or operation.
3. Covered AIOS reality postconditions map to the BAA verification surface.
4. Every covered effect maps to an actual pinned AIOS World Runtime capability.
5. The BAA kernel can admit, execute, verify, and externally complete obligations derived by the pinned AIOS code.

These checks detect contract drift. They do not show that production execution is non-bypassable or that real HRIS / IAM observations satisfy the semantic bridge.

## Real AIOS execution-engine gate now established

The integration suite now also wraps the pinned AIOS `OffboardingExecutionEngine` with an integration-only BAA provider gate.

It verifies three finite execution-path properties:

- a normal authorized offboarding episode completes through BAA and the real AIOS execution state machine;
- when an attempted effect remains genuinely unresolved, BAA prevents additional provider dispatch under the conservative unresolved-effect limit and does not replay that effect;
- when an effect is committed but its acknowledgement is lost, independent read-back resolves the ambiguity, execution resumes within the same authority epoch, and the remaining covered effects complete without replaying the committed effect.

This is stronger than contract projection because BAA now changes the execution path exercised by the pinned AIOS engine. It still uses an in-memory database and deterministic provider fixture.

The pinned production World Runtime surface is also exercised locally: all three covered capabilities require authorization, resource binding, and version binding; writer and verifier credential domains are distinct; and an invocation without authorization is rejected before provider execution.

A separate isolated network acceptance has now passed end to end on the repository's self-hosted Windows/Docker Desktop runner:

- AIOS workflow run: `37302243172`;
- runner: `aios-windows-docker-desktop`;
- AIOS head: `600ada8075d4641f22293bf0ba97482c4e73a55c`;
- normal episode: completed with exactly three unique external writes;
- lost-ack episode: recovered from one committed write to completion with three unique writes and zero duplicates;
- read-back outage: recovered from one committed write to completion with three unique writes and zero duplicates;
- unauthorized Runtime bypass: HTTP 403 with zero provider writes.

The evidence artifact explicitly qualifies the run as production-like network acceptance with isolated synthetic effects, not real Odoo/Keycloak evidence.

## What remains unproved

The repository does not establish:

- completeness of the threat model;
- correctness or non-bypassability of the AIOS production implementation;
- correctness of HR policy or termination decisions;
- completeness or independence of IAM / HRIS observations;
- absence of uncovered side channels;
- real-world failure probabilities;
- worst-case safety against arbitrary adaptive agents;
- production delegation leverage;
- the full semantic bridge from kernel properties to all relevant real-world harms.

## Experiment interpretation

The deterministic experiment is a falsification harness, not a probability estimator.

A positive fixture result means only:

> Under the explicit modeled histories, the enforced protocol changes which reality-facing transitions can occur.

The isolated network experiment now establishes that the protocol can cross a real HTTP/process boundary in the self-hosted Windows/Docker Desktop environment while preserving the modeled safety and recovery properties.

The next empirical claim is stronger:

> Under the same non-synthetic offboarding workload and real administrative effect/read-back interfaces, does BAA improve the feasible delivery frontier under common attention and risk constraints after assurance labor is counted?

## Convergence criterion for this phase

The reference-contract phase is converged when:

1. one task domain is pinned to a source version;
2. guarantee boundary and semantic-bridge assumptions are explicit;
3. the protocol is executable;
4. safety and delivery are measured separately;
5. ambiguous effects remain unresolved rather than silently retried;
6. adaptive retry is present in threat fixtures;
7. finite admission-state exploration is automated;
8. CI runs regression tests and the deterministic comparison harness;
9. real source-domain contracts are checked for compatibility;
10. documentation states what is and is not proved.

All ten conditions are now satisfied.

## Next phase boundary

Further local conceptual or synthetic network expansion is not justified by the current evidence.

The next stronger phase is a **less-synthetic administrative integration experiment** using real or faithful external systems and a controlled test population. It must add evidence for:

- real Keycloak / IAM and Odoo / HRIS effect behavior;
- independently credentialed external read-back;
- real outage, latency, concurrency, and reconciliation behavior;
- bypass attempts across the deployed process / credential boundary;
- episode-level principal attention;
- third-party assurance labor;
- useful delivery under the same workload across the three regimes.

Current claims therefore stop at: reference-model guarantees + pinned AIOS compatibility + finite execution-engine gating + successful isolated network acceptance on the self-hosted Windows/Docker Desktop environment.
