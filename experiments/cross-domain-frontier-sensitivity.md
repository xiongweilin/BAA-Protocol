# Cross-Domain Frontier Sensitivity Analysis

> English | [简体中文](cross-domain-frontier-sensitivity.zh-CN.md)

## Status

**Post-hoc exploratory analysis of already accepted runs.**

This document does not alter any preregistered endpoint and is not a new model experiment.

Inputs:

- offboarding v6 accepted run: AIOS `37406741476`, artifact `11386984007`, SHA-256 `28db9bb852eeba59d26b93687dd5c02dad6bb9b4d144c96cdacb8b5da5112ad4`;
- canary v1 accepted run: AIOS `37410377327`, artifact `11389635051`, SHA-256 `c0e667c1c564d73c8986e001c7ee68947a8d9a95984dbcd91a915c71c11fc0af`.

The accepted study results remain authoritative for their frozen endpoints.

## Why a separate reclassification is needed

The two studies do not encode useful delivery identically for every counterfactual budget analysis.

In canary v1, a trajectory that reaches the target through an unsafe transition receives zero useful-delivery credit. That is correct for the preregistered strict contract, but it means that relaxing the unsafe-transition ceiling while still requiring the stored useful-delivery field would count risk twice.

Therefore this sensitivity analysis defines a separate quantity:

~~~text
completed_within_bounds(B)
~~~

An observed episode counts when:

~~~text
completed == true
principal_attention <= A
unsafe_transitions <= U
terminal_unresolved_results <= Q
assurance_labor_units <= L       # only when a ceiling is supplied
assurance_interventions <= I     # only when a ceiling is supplied
~~~

This uses raw completion only for the delivery side of the reclassification. It does not rename this quantity as preregistered delegability.

The analysis also keeps human audit labor and automatic BAA interventions as separate dimensions. They are not converted into one scalar cost.

## Frozen strict endpoints remain unchanged

At C2, the accepted strict results are:

| Domain | Best direct | BAA | BAA delta |
|---|---:|---:|---:|
| offboarding v6 | 14 / 24 | **20 / 24** | **+6** |
| canary v1 | **11 / 18** | 10 / 18 | **-1** |

The domains therefore already disagree in sign before any post-hoc reclassification.

## Horizon sensitivity at strict risk

Using raw completion with A=0, U=0, Q=0 reproduces the strict completed-within-bounds counts:

| Domain | C | Best direct | BAA | Delta |
|---|---:|---:|---:|---:|
| offboarding v6 | C0 | 4 | 4 | 0 |
| offboarding v6 | C1 | **6** | 4 | -2 |
| offboarding v6 | C2 | 14 | **20** | +6 |
| canary v1 | C0 | 3 | 3 | 0 |
| canary v1 | C1 | 9 | 9 | 0 |
| canary v1 | C2 | **11** | 10 | -1 |

The offboarding advantage is therefore not monotonic in adaptive horizon: BAA is behind at C1 and ahead at C2. Canary does not cross into a positive BAA frontier within the frozen horizon.

## C2 risk-tolerance sensitivity

Holding A=0 and Q=0, reclassify observed completed trajectories while varying the allowed unsafe transitions per episode.

| Domain | Unsafe ceiling U | Best direct | BAA | Delta |
|---|---:|---:|---:|---:|
| offboarding v6 | 0 | 14 | 20 | **+6** |
| offboarding v6 | 1 | 16 | 20 | **+4** |
| offboarding v6 | 2 | 19 | 20 | **+1** |
| canary v1 | 0 | 11 | 10 | **-1** |
| canary v1 | 1 | 13 | 10 | **-3** |
| canary v1 | 2 | 13 | 10 | **-3** |

This is not a causal claim about what the model would do if deployed under a more permissive policy. It is only a reclassification of the observed trajectories.

Within that limitation, the pattern is clear:

- offboarding's BAA advantage shrinks sharply as unsafe transitions become more acceptable;
- canary's BAA deficit grows when the two unsafe direct completions become admissible;
- the sign and magnitude of delegation leverage are therefore strongly task- and risk-budget-dependent.

## Automatic assurance-intervention sensitivity

Next hold A=0, U=0, and Q=0, and cap per-episode BAA automatic interventions.

### Offboarding v6, C2

| Max BAA interventions per episode | BAA completed within bounds | Best direct | Delta |
|---:|---:|---:|---:|
| 0 | 13 | 14 | -1 |
| 1 | 16 | 14 | +2 |
| 2 | 20 | 14 | +6 |
| 3 | 20 | 14 | +6 |
| 4 | 20 | 14 | +6 |

In offboarding v6, automatic assurance work is productive: allowing intervention capacity converts safe blocking into additional safe completion.

### Canary v1, C2

| Max BAA interventions per episode | BAA completed within bounds | Best direct | Delta |
|---:|---:|---:|---:|
| 0 | 10 | 11 | -1 |
| 1 | 10 | 11 | -1 |
| 2 | 10 | 11 | -1 |
| 3 | 10 | 11 | -1 |
| 4 | 10 | 11 | -1 |

In canary v1, the five observed C2 interventions occur on trajectories that remain incomplete. Increasing the allowed intervention count therefore does not recover the lost liveness in the accepted run.

This is the sharpest cross-domain distinction in the current evidence:

> assurance intervention is not itself delegation leverage; it creates leverage only when the surrounding state/feedback dynamics let the model convert a blocked action into a safe continuation.

## Attention and unresolved-result ceilings

For both accepted workloads, relaxing A and Q from 0 to 1 does not increase completed-within-bounds counts at C0, C1, or C2.

The reason is empirical, not structural: episodes carrying terminal unresolved results in these accepted traces are also incomplete. A larger attention or unresolved-result budget cannot turn them into completed work by reclassification alone.

This means the current artifacts are informative about risk and intervention sensitivity, but weak for estimating an attention-completion exchange rate.

## Post-hoc audit cost

In both accepted studies, self-check and post-hoc audit have the same execution outcomes. Audit only adds assurance labor:

- offboarding v6 C2: 81 audit labor units;
- canary v1 C2: 57 audit labor units.

Within the measured endpoints, post-hoc audit is therefore dominated by self-check. That does not imply records have no external value; the studies simply do not assign downstream value to the audit record itself.

## Implication for the next experiment

The current evidence does not support one universal BAA frontier shift.

It supports a conditional statement:

- in offboarding v6, enough automatic intervention capacity plus a sufficiently long horizon converts strict risk control into more safe completion;
- in canary v1, the same broad architecture preserves safety but the feedback/state dynamics fail to convert denial into enough sequential continuation.

The next preregistered experiment should therefore vary a mechanism, not merely add cases. The most specific candidate is **machine-usable assurance feedback**: after deny/hold, expose a bounded corrective state such as the required next stage, missing evidence class, or reconciliation requirement, without weakening the hard admission rule.

That hypothesis should be tested as a new study version against a frozen workload; it must not rewrite canary v1.

## Reproduction

The repository script accepts the two downloaded result artifacts:

~~~text
python scripts/analyze_cross_domain_frontier.py \
  --offboarding-v6 <offboarding-v6-result.json> \
  --canary-v1 <canary-v1-result.json>
~~~

The output is a post-hoc reclassification report, not a new experimental result.
