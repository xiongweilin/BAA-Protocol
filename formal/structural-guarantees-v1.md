# Structural Guarantees v1

> English | [简体中文](structural-guarantees-v1.zh-CN.md)

## Status

This document records the first finite-state structural model check for BAA-Protocol.

It is a proof obligation over a deliberately small abstract transition system. It is **not** a production certification and is not evidence that arbitrary real-world actions satisfy the same assumptions.

Machine-readable result:

- [structural-model-v1-result.json](structural-model-v1-result.json)

Executable checker:

- `baa_protocol/formal_model.py`
- `scripts/run_formal_model_check.py`
- `tests/test_formal_model.py`

## Claim form

The checked claim is:

[
Omega_{mathrm{formal-v1}}
Rightarrow
orall 	au in operatorname{Trace}(K_{mathrm{formal-v1}}),
quad
	au models I_{mathrm{formal-v1}}
]

where the quantification is only over the finite transition system encoded by `FiniteBAAModel`.

The current frozen state space contains:

- **584 reachable states**
- **35,040 explored transitions**

CI exhaustively evaluates every declared action from every reachable state.

## Finite universe

The v1 model contains five proposal slots:

1. a normal proposal with risk factor `shared`;
2. a second normal proposal with the same factor, so joint interaction matters;
3. a normal proposal with a different risk factor;
4. a proposal targeting a protected guarantee source;
5. a proposal with no verification path.

The frozen risk model uses:

[
R = 3
]

with pairwise same-factor interaction penalty (1).

The action alphabet includes:

- evaluation/admission;
- exact-scope execution;
- wrong-object execution;
- wrong-operation execution;
- over-quota execution;
- expired execution;
- stale-version execution;
- verification at zero exposure;
- verification at the declared bound;
- an out-of-(Omega) verification attempt above the declared bound;
- conservative timeout settlement;
- observation-unavailable self-transition.

Rejected requests are represented as non-authorizing self-transitions so they are included in the exhaustive check.

## Explicit assumptions (Omega_{mathrm{formal-v1}})

The result depends on all of the following:

1. the executor is the complete mediation path for represented actions;
2. proposal scope and exposure bounds are immutable after admission;
3. realized exposure used for settlement is non-negative and no greater than the declared bound;
4. protected guarantee sources are exactly the objects marked `protected_source`;
5. the declared joint-risk functional is the risk quantity being guaranteed;
6. no unmodelled external transition mutates the represented ledger.

These assumptions are part of the claim, not implementation notes.

## Checked invariants

The finite model satisfies all seven frozen invariants.

### 1. Capability scope non-expansion

Any accepted execute transition must match the issued object, operation, quota, expiry, and state version exactly.

Wrong-object, wrong-operation, over-quota, expired, stale-version, altered, or non-executable capabilities cannot produce a reality-facing state transition in the model.

### 2. Ledger category exclusivity

Each represented exposure occupies exactly one semantic accounting category:

- reserved;
- pending;
- settled;

or no exposure-bearing category.

A transition cannot silently double-count the same proposal in multiple categories.

### 3. Joint risk budget

For every reachable state:

[
ho(X_t) le R
]

under the frozen joint-risk function.

Admission uses the current joint state, including pairwise interaction, rather than checking only a proposal's marginal bound.

### 4. Pending exposure is not silently released

Once execution moves an exposure to `PENDING`, any non-terminal action preserves it as pending.

The only terminal transitions represented in v1 are:

- verification;
- conservative timeout settlement.

### 5. Unknown effect is not blindly replayed

An exact replay attempt while the proposal is pending is rejected.

The model therefore never converts “acknowledgement unknown” into permission to execute the same capability again.

### 6. Protected guarantee source is unreachable

A proposal whose target is a declared protected guarantee source cannot receive a capability.

No reachable state gives that proposal reserved, pending, or settled reality-facing authority.

### 7. Conservative timeout settlement

A pending timeout settles at the proposal's declared upper bound:

[
E_{mathrm{settled}} = E_{mathrm{declared bound}}
]

rather than releasing the exposure because confirmation is missing.

## Why the exposure-bound assumption is explicit

The reference kernel intentionally does not clamp an observed realized exposure to the declared bound.

A regression test demonstrates the consequence:

1. risk budget = 5;
2. a proposal declares exposure bound = 5 and is admitted;
3. execution becomes pending;
4. verification reports realized exposure = 6;
5. the recorded current risk becomes 6.

Therefore:

[
	ext{realized exposure} le 	ext{declared bound}
]

is a substantive semantic/risk-model assumption. If reality violates it, the structural budget guarantee is invalidated. Silently clamping the observation to 5 would hide the failure instead of preserving evidence that (Omega) was false.

## What is not proved

This model check does not establish:

- that AIOS or any production executor is a complete mediation path;
- that a real exposure bound is correct;
- that all relevant harm dimensions are represented by the toy risk functional;
- that outside actors cannot modify protected sources or ledger-relevant reality;
- that observations correctly identify real effects;
- that arbitrary concurrency, distributed failure, or timing behavior refines to this state machine;
- that a model or planner will complete useful work;
- that the finite five-proposal universe represents all possible action compositions.

Those are separate refinement, bridge, empirical, or deployment obligations.

## Subsequent refinement status

The next useful formal step is not to enlarge the abstract state count mechanically.

Since this v1 model check was frozen, the repository has added finite, revision-pinned executable refinement/coverage layers for the AIOS offboarding gate, the World Runtime scope/identity boundary, the public Runtime/adaptor mediation surface, and the three Odoo/Keycloak offboarding connectors.

That progress does not remove the conditional nature of this result. In particular, the third Omega assumption—realized exposure used for settlement is no greater than the declared bound—now has an explicit, falsifiable [Exposure Bridge Contract v1](exposure-bridge-contract-v1.md), but current target-only product read-back is deliberately classified as scope-incomplete and therefore cannot establish that assumption.

The highest-value structural obligations are now:

1. provide scope-complete reality-side evidence for the declared exposure metric, or define another exposure metric whose completeness is observable; and
2. once exposure measurement is established, justify that the declared joint-risk functional is the actual risk quantity intended by the guarantee.

Until those semantic-bridge obligations are closed, the joint-risk budget remains a structural guarantee under explicit Omega assumptions, not an unconditional deployed-system guarantee.
