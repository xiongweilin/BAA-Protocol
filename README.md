# BAA-Protocol

> English | [简体中文](README.zh-CN.md)

[![Protocol tests](https://github.com/xiongweilin/BAA-Protocol/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/xiongweilin/BAA-Protocol/actions/workflows/tests.yml)

**Bounded Action Admission + experimental contingent safe policy synthesis.** A bounded executor should do useful work without trusting an adaptive agent's assertions about authorization, uncertainty or external effects.

## Architecture

    Goal + current evidence + explicit world/action model
                ↓
      finite contingent policy compiler   [EXPERIMENTAL]
                ↓
       independent policy verifier        [EXPERIMENTAL]
                ↓
     existing BAA live deny / hold / admit [MANDATORY]
                ↓
     narrow capability → mediated executor
                ↓
    independent readback → reconcile / settle / reopen

**What changes:** the original protocol checked an already-proposed next action. The new [contingent policy](spec/contingent-policy.md) can proactively plan an authorized safe sequence with branches on trusted observations, minimizing declared worst-case operation cost. It retains *all* modeled possible effects after uncertainty, does not blind-retry, and has an independent structural checker. Its proposed plan confers **no authority**; current-time capabilities and World Runtime mediation are unchanged.

## Fundamental boundaries

1. **Normative:** goals, rights, allowed actions and trade-offs do not materialize from a planning algorithm.
2. **Epistemic:** the belief-state model may omit hazards, and authoritative evidence can be stale or wrong.
3. **Control:** an abstract policy can be safe yet impossible to execute, recover or observe in deployment.

Structural properties hold only under declared model/environment assumptions. Finite model checking and simulated execution do not establish production risk, human labor or global optimality.

## Validated status versus research target

| Evidence | Observed result | What is not established |
| --- | --- | --- |
| [Finite structural model](formal/structural-guarantees-v1.md) | 584 abstract states, 35,040 transitions | Universal deployed-interface safety |
| [Prospective offboarding v6](experiments/prospective-model-v6-result.md) | C2 BAA delegable 20/24 versus 14/24 controls, but C0 tied and C1 worse | Uniform horizon advantage; cross-mechanism generalization |
| [Cost frontier](experiments/prospective-delegation-cost-frontier-v1-result.md) | **C0/C1/C2: 0/30** BAA-positive strictly safe cells at each level | Broad lower-attention delegation advantage |
| [Isolated real-product acceptance](formal/real-product-exposure-binding-v1.md) | Scoped Odoo/Keycloak effect/readback and bypass-denial tests | Production-tenant acceptance |
| **New contingent planner** | Finite compiler, independent verifier and regression tests on this branch | New real-model advantage over a strong conditional-planning baseline |

Earlier experiments are frozen and will **not** be reclassified after architecture changes. Full run IDs, negative results, human-cost gaps and evidence-grade distinctions are in the [claim/evidence index](experiments/claim-evidence-index.md); original ZIP checksums and local preservation in [source provenance](experiments/source-artifact-provenance-2026-10-10.md).

## Core implementation

- [Contingent policy synthesis and independent verifier](baa_protocol/contingent_policy.py), with [adversarial-belief tests](tests/test_contingent_policy.py).
- Existing [admission protocol](spec/protocol.md), [state machine](spec/state-machine.md) and [guarantee claims](spec/guarantees.md) remain authoritative for actual external effects.
- [AIOS integration boundary](https://github.com/xiongweilin/aios/blob/main/src/domains/administrative_orchestrator/contingent_execution.py) stages but does not automatically dispatch a conditional step.
- [guide theory revision](https://github.com/xiongweilin/guide/blob/main/minimal-derivation.md) makes safe action under uncertainty primary; [Lean RobustAction](https://github.com/xiongweilin/distinction-self-reference-lean/blob/main/DistinctionSelfReference/RobustAction.lean) proves a conditional common-action special case.

Test reference logic: `python -m unittest discover -s tests -p 'test_*.py' -v`. Cross-repository CI continues to test pinned and moving AIOS main versions; branch-specific AIOS integration must also be separately checked.

## Acceptance for a stronger claim

Preregister a new task distribution, equally equipped active-planning control, C0/C1/C2 horizons, independent safety oracle, observation budget, authorization/scope ceilings and full human/automatic cost ledger. Report all cases including holds, failed delivery and unknown effects. Only measured outperformance can support a frontier-expansion claim. **No C0/C1/C2 gain is assumed for this branch.**

Project policies: [Contributing](CONTRIBUTING.md), [Security](SECURITY.md), [License](LICENSE).
