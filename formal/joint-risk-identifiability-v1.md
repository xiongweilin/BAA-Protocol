# Joint-Risk Identifiability v1 — Negative Result and Calibration Gate

> English | [简体中文](joint-risk-identifiability-v1.zh-CN.md)

## Status

**Finite negative result: the accepted real-product exposure observations do not identify the structural joint-risk model.** This is not a failure of the product acceptance and is not a new BAA protocol layer.

Evidence already accepted: AIOS [real-product E2E run 37638217335](https://github.com/xiongweilin/aios/actions/runs/37638217335) and [Real-Product Exposure Binding Acceptance v1](real-product-exposure-binding-v1.md). In normal, lost-ack, and read-back-outage scenarios, three offboarding effects each have one exact admitted-proposal-to-measurement binding with `realized_exposure=1` under the narrow `managed-subject-state-change-count-v1` metric. This says nothing by itself about a loss interaction among effects.

Executable counterexamples: `tests/test_joint_risk_identifiability.py`. The test data are **synthetic observational-shape fixtures**, not fabricated copies of product artifacts or empirical estimates.

## The identification obstruction

The frozen joint-risk functional is:

```text
joint_risk(b, f, lambda)
  = sum_i(b_i)
  + lambda * sum_{i<j, f_i == f_j} min(b_i, b_j)
```

Fix all three per-effect exposure measurements at `(1, 1, 1)`, as in the shape of the real-product results. With `lambda=1`, the same observations admit at least these distinct model specifications:

| Unobserved factor partition | Formula output |
| --- | ---: |
| Three distinct risk factors | 3 |
| IAM disable/revoke share one factor; HRIS separate | 4 |
| All three share one factor | 6 |

Fixing the middle partition does not identify `lambda` either: penalties `0, 1, 2` produce `3, 4, 5` respectively, without any change in the observed per-effect exposure counts.

These are alternative **declared model outputs**, not competing measured levels of real-world harm. The observations contain neither an independently established factor assignment nor a separately observed joint-loss outcome by which to select among the alternatives.

## Three aggregations must not be conflated

A synthetic three-effect shape also illustrates that the following are different:

- the **number of affected effect–subject transitions** (three unit effect observations);
- the **number of distinct product-qualified subjects touched** (an HRIS employee and an IAM user: two);
- the **number of underlying principals** (potentially one, but only if a cross-system identity mapping is independently established).

These quantities may be useful for different contractual purposes; they are not interchangeable risk units.

Similarly, a state that changes `A -> B -> A` has two intermediate transitions but zero terminal net change. A before/after projection is not automatically a complete exposure trace across an unobserved interval.

The existing product acceptance *does* test collateral changes to enumerated managed subjects in its frozen projection. This negative result does not undermine that observation. It limits what may be inferred **across operations** from those observations.

## Next admissible calibration study

A future study can claim to identify a nonzero interaction term only if its protocol is frozen **before** observing outcomes and includes:

1. **Independent outcome:** define a concrete, principal-approved joint-loss or severity quantity `Y`, with units, scope, attribution rules, and an independent measurement source. Reusing the current per-effect subject count as `Y` cannot independently calibrate a harm penalty.
2. **Contrasting interventions:** compare matched safe episodes containing individual effects, same-subject multi-effect compositions, and disjoint-subject compositions, with explicitly controlled order and overlap timing. Include no-effect, unchanged-control, and verification-outage cases.
3. **Identifiable factor hypotheses:** predeclare competing HRIS/IAM factor partitions and the candidate interaction family or bounded penalty interval. Observed differences must discriminate these hypotheses rather than simply match a factor label assigned after inspection.
4. **Joint-state and uncertainty accounting:** measure the same state projection over an enumerated subject universe, retain unknown/pending and interim outcomes, account for shared state and interference, and do not count repeated traces as independent samples.
5. **Frozen acceptance rule:** preregister exposure/harm outcomes, model-fitting and uncertainty method, out-of-sample validation, negative/null outcomes and failure modes. Report what is bounded empirically versus assumed structurally.

If the outcome `Y` cannot be safely and independently observed, **stop at non-identification**. An arbitrarily conservative budget can still be a deployment policy, but must not be described as a calibrated real-world risk guarantee.

## Frozen conclusion

The current offboarding risk-factor registry remains empty. Neither a shared factor nor a positive interaction penalty is justified by three observed unit exposures, even when those exposures are reliably tied to admitted product actions.

The next research operation is to choose and independently observe an appropriate joint outcome in an isolated task domain, or formally retain joint-risk calibration as an open `Omega` assumption. Do not extend the existing single-case product fixture until it is capable of distinguishing competing models.
