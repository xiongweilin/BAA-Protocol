# Contingent Safe Policy — experimental core

> English | [简体中文](contingent-policy.zh-CN.md)

## Why this is an architectural change

The original gate accepts, holds or denies a **proposed next action**. A held proposal is safe but may waste an entire feedback horizon. The new planner searches for a **bounded sequence of actions and information-gathering branches** whose every declared world path remains qualified. It sits strictly *upstream* of the original BAA admission kernel.

    possible worlds + protected goal + authorized effect interface
      -> worst-case-cost AND/OR policy synthesis
      -> separate policy consistency checker
      -> current-time capability admission on EVERY effect
      -> independent readback / reconciliation / domain closure

A compiled policy does **not** mint a capability. The currently pinned World Runtime must still mediate each real external effect. This makes conditional execution possible without silently weakening effect authority.

## Finite semantics

Given a nonempty belief B of compatible world states and hard safety set S, the planner may choose:

1. **Effect:** only a caller-declared authorized effect with a nonempty set of possible successors for every world in B, all successors inside S. Its possible outcomes are *unioned*, never inferred to be a single observed success. The same named effect is not reissued on that branch.
2. **Probe:** only a caller-qualified observation defined for **every** world in B. The policy must successfully cover **every** possible returned label. Observation partitions B; it does not change the physical state.
3. **Done:** only if every possible state lies in the declared goal set G. This is model-relative policy completion and **not** automatic externally verified task settlement.

The finite search minimizes worst-case total declared step cost across the policy tree, under a fixed maximum number of operations. No unsafe path is accepted to buy delivery. Unknown effects can enter explicit pending states and must not be silently treated as absent. The new independent checker walks any proposed policy and verifies structural conditions without trusting the synthesis algorithm.

## Safety and limits

- **Soundness depends on the external model:** B must include reality, effect outcome sets must conservatively cover possible provider behavior, every effect needs a currently valid authorization binding, and probes must genuinely be independent and qualified. Source code cannot prove these facts.
- **Live enforcement remains outside the planner:** each step must be reauthorized by AIOS at use time. The AIOS experimental staging cursor refuses stale bindings, unknown effects, missing branches and unqualified observations; it does not dispatch provider writes.
- **Completeness is bounded:** max depth, finite state enumeration, and single-issuance policies can reject otherwise possible solutions. The planner does not optimize open semantic objectives or infer calibrated joint risk.
- **Failure and baseline accounting:** do not reuse earlier v6 or prospective cost-frontier experiments as evidence that this planner improves C0, C1 or C2. Preserve their null results. A new preregistered strong-baseline study must grant equal observation, horizon, authorization and assurance resources to each architecture.

## Implementation and regression tests

- Compiler and checker: [contingent_policy.py](../baa_protocol/contingent_policy.py).
- Negative and positive model cases: [test_contingent_policy.py](../tests/test_contingent_policy.py).
- Existing BAA gate: [protocol](protocol.md) and [state machine](state-machine.md).
- Real effect mediation: [AIOS contingent execution branch](https://github.com/xiongweilin/aios/blob/research/contingent-safe-execution-v1/src/domains/administrative_orchestrator/contingent_execution.py).
