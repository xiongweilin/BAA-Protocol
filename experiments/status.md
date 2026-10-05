# Prototype Status

## Current claim level

The repository has reached a first executable research baseline for one concrete domain: employee offboarding.

The current implementation supports only the following claim:

> For the finite reference model and explicit fault fixtures in this repository, the BAA regime mechanically blocks the modeled out-of-scope, stale-authority, premature, protected-source, and ambiguous-replay transitions while preserving explicit unknown states.

This is a regression claim about the reference model. It is not a real-world safety claim about AIOS or production HR / IAM systems.

## What is now executable

The prototype contains:

- a generic bounded action admission model;
- a concrete employee-offboarding instance;
- exact-scope capabilities;
- authority-epoch and state-version invalidation;
- effective-time gating;
- independent-verification gating;
- unresolved-effect preservation;
- retry suppression after ambiguous effect;
- protected guarantee-source isolation;
- a conservative unresolved-effect concurrency limit;
- VSAR event capture;
- three experiment regimes:
  - agent self-check;
  - external record / post-hoc audit;
  - bounded action protocol;
- episode-level deterministic fault fixtures;
- finite exhaustive admission checks over the current boolean fault dimensions.

## What the tests establish

The tests are allowed to establish only properties of the reference model.

They check that:

- a valid normal episode can complete its three external obligations;
- direct execution and post-hoc audit do not mechanically prevent modeled bad transitions;
- BAA rejects or holds modeled scope, timing, authority, verification, and protected-source faults;
- an ambiguous prior effect does not create replay permission;
- unknown observations remain explicit;
- structural safety and useful delivery remain separate metrics;
- finite combinations of the current admission fault flags fail closed.

## What the tests do not establish

They do not establish:

- completeness of the threat model;
- correctness of the AIOS production implementation;
- correctness of HR policy or termination decisions;
- completeness of IAM / HRIS observations;
- absence of side channels outside the covered interfaces;
- real-world failure probabilities;
- worst-case safety against arbitrary adaptive agents;
- delegation leverage in production;
- a proof of the semantic bridge from kernel properties to all real-world harms.

## Current experiment interpretation

The deterministic experiment is a falsification harness, not an estimator.

A positive result means only:

> Under these explicit fixtures, the enforced protocol changes which reality-facing transitions can occur.

The next empirical threshold is stronger:

> Under the same offboarding workload and real interfaces, does BAA increase the feasible delivery frontier under common attention and risk constraints after assurance labor is counted?

That claim requires integration with an executable external environment or AIOS test stack and prospective episode data.

## Convergence criterion for this phase

The conceptual / reference-model phase is considered converged when all of the following hold:

1. one task domain is pinned to a source version;
2. the guarantee boundary and bridge assumptions are explicit;
3. the protocol is executable;
4. safety and delivery are separately measured;
5. ambiguous effects remain unresolved rather than silently retried;
6. adaptive retry is present in the threat fixtures;
7. finite admission-state exploration is automated;
8. CI runs both regression tests and the deterministic comparison harness;
9. documentation states what is not proved.

Those conditions are now represented in the repository.

## Next phase boundary

Further progress should not add another conceptual layer.

The next phase is an integration experiment against the pinned AIOS offboarding stack (or a faithful executable environment) that supplies:

- real Administrative cases and obligations;
- World Runtime capability enforcement;
- provider execution outcomes;
- independent HRIS / IAM read-back;
- reconciliation after ambiguous effects;
- episode-level attention and assurance-labor measurements.

Until that integration exists, claims should remain at the reference-model level.
