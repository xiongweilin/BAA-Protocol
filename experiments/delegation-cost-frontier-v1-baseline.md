# Delegation Cost Frontier v1 Baseline

> English | [简体中文](delegation-cost-frontier-v1-baseline.zh-CN.md)

## Status

**Retrospective accounting result over accepted frozen traces. No resampling.**

This result applies the [v1 cost-frontier protocol](delegation-cost-frontier-v1-protocol.md) to the accepted offboarding v6 and canary v5 artifacts.

It is descriptive evidence about the observed accounting surface, not a new prospective causal experiment.

## Architecture panel: strict risk and attention

Fix principal attention = 0, unsafe transitions = 0, terminal unresolved = 0, useful delivery minimum = 3, and audit labor ceiling = 5. Vary only the per-episode automatic assurance-intervention ceiling.

### C0

| Max automatic interventions | Self-check | Audit | BAA |
|---:|---:|---:|---:|
| 0 | 4/24 | 4/24 | 4/24 |
| 1 | 4/24 | 4/24 | 4/24 |
| 2 | 4/24 | 4/24 | 4/24 |
| 3 | 4/24 | 4/24 | 4/24 |

No architecture advantage appears at C0.

### C1

| Max automatic interventions | Self-check | Audit | BAA |
|---:|---:|---:|---:|
| 0 | 6/24 | 6/24 | 4/24 |
| 1 | 6/24 | 6/24 | 4/24 |
| 2 | 6/24 | 6/24 | 4/24 |
| 3 | 6/24 | 6/24 | 4/24 |

BAA remains behind at the shorter adaptive horizon. Increasing the assurance-intervention allowance does not repair missing post-event action opportunities.

### C2

| Max automatic interventions | Self-check | Audit | BAA |
|---:|---:|---:|---:|
| 0 | 14/24 | 14/24 | 13/24 |
| 1 | 14/24 | 14/24 | 16/24 |
| 2 | 14/24 | 14/24 | **20/24** |
| 3 | 14/24 | 14/24 | **20/24** |

The previously reported C2 frontier expansion therefore has a visible assurance-cost threshold.

With zero automatic-intervention budget, BAA is one episode behind self-check. At one intervention it is two episodes ahead; at two interventions the full observed +6 expansion appears.

## Human audit labor ceiling

At C2, with strict attention/risk, useful delivery minimum 3, and BAA automatic interventions allowed up to 3:

| Max human assurance labor per episode | Self-check | Audit | BAA |
|---:|---:|---:|---:|
| 0 | 14/24 | 0/24 | 20/24 |
| 1 | 14/24 | 0/24 | 20/24 |
| 2 | 14/24 | 0/24 | 20/24 |
| 3 | 14/24 | 14/24 | 20/24 |
| 4 | 14/24 | 14/24 | 20/24 |
| 5 | 14/24 | 14/24 | 20/24 |

In this frozen trace, every delegable audited completion consumes at least three audit-labor units.

## Risk-ceiling sensitivity

At C2, with attention = 0, terminal unresolved = 0, audit labor <= 5, and BAA interventions <= 3:

| Max unsafe transitions per episode | Self-check | Audit | BAA |
|---:|---:|---:|---:|
| 0 | 14/24 | 14/24 | **20/24** |
| 1 | 16/24 | 16/24 | **20/24** |
| 2 | 19/24 | 19/24 | **20/24** |
| 3 | 19/24 | 19/24 | **20/24** |

Relaxing the risk bound makes more direct episodes feasible by definition and shrinks the BAA advantage. It does not make those traces safer.

## Canary assurance-mechanism panel

Fix zero principal attention, zero unsafe transitions, zero terminal unresolved results, zero human assurance labor, and allow at most two evidence reacquisitions.

### H4

| Max automatic interventions | no_reacquire | reacquire |
|---:|---:|---:|
| 0 | 2/24 | 2/24 |
| 5 | 2/24 | **4/24** |
| 11 | 2/24 | **4/24** |
| 17 | 2/24 | **4/24** |

### H8

| Max automatic interventions | no_reacquire | reacquire |
|---:|---:|---:|
| 0 | 3/24 | 3/24 |
| 5 | 3/24 | **5/24** |
| 11 | 3/24 | **6/24** |
| 17 | 3/24 | **6/24** |

The recovery mechanism has a clear assurance-cost surface: the treated gain disappears when automatic intervention budget is forced to zero.

The full H8 gain also requires the two bounded evidence reacquisitions used by the recovered episodes. With a reacquisition ceiling of 0 or 1, both policies remain 3/24 at H8; with a ceiling of 2, `reacquire` reaches 6/24.

## What this baseline adds

The earlier studies answered whether a delegation advantage existed at selected budget points.

This baseline shows that the observed advantage is conditional on the available assurance budget:

- too little assurance work and BAA can be less delegable than direct execution;
- enough bounded assurance work and BAA can move the feasible frontier outward;
- relaxing the risk ceiling can make direct execution appear more delegable only by accepting traces previously classified as unsafe;
- post-hoc audit consumes a separate human labor budget even when it does not change the execution trace.

## Limits

The budget thresholds were read from already accepted traces, so this result is retrospective and cannot serve as a preregistered replication.

The next informative study should freeze a cost grid prospectively and then generate a new workload or new domain/interface trace set without changing the grid after outcomes are known.
