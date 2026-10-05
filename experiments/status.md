# Prototype Status

## Current claim level

The repository has reached an executable reference baseline for one concrete domain: employee offboarding.

The strongest current claim is:

> For the finite BAA reference model and explicit fault fixtures in this repository, the BAA regime mechanically blocks the modeled out-of-scope, stale-authority, premature, protected-source, and ambiguous-replay transitions while preserving explicit unknown states. The BAA offboarding projection is also compatible with the pinned AIOS policy, obligation, postcondition, and World Runtime capability surface at commit `d2ca4e9e874bec1f5c28911e8175ff84e5f45055`.

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

The next empirical claim is stronger:

> Under the same offboarding workload and real execution interfaces, does BAA improve the feasible delivery frontier under common attention and risk constraints after assurance labor is counted?

That requires exercising the actual execution and observation boundary.

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

Further conceptual expansion is not justified by the current evidence.

The next phase is a **runtime integration experiment** against the pinned AIOS offboarding stack or an equivalent faithful executable environment. It must exercise:

- real World Runtime capability enforcement;
- provider execution outcomes;
- independent HRIS / IAM read-back;
- reconciliation after ambiguous effects;
- bypass attempts against the covered reality boundary;
- episode-level principal attention;
- third-party assurance labor;
- useful delivery under the same workload across the three regimes.

Until that runtime experiment exists, claims remain at the reference-model + pinned-contract-compatibility level.
