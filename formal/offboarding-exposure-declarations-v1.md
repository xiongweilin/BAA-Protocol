# Offboarding Exposure Declarations v1

> English | [简体中文](offboarding-exposure-declarations-v1.zh-CN.md)

## Status

This record binds each BAA-covered employee-offboarding proposal class to the concrete observable exposure metric introduced by Exposure Metric Binding v1.

It is a declaration layer only. It does not claim that a reality-side measurement source has been accepted for every proposal instance, and it does not justify the joint-risk functional.

The executable declaration registry is in `baa_protocol/offboarding.py`; regression tests are in `tests/test_offboarding_exposure_declarations.py`.

## Frozen declarations

All three allowed external offboarding operations use:

`managed-subject-state-change-count-v1`

with declared exposure bound 1.

| Target system | Operation | Metric | Bound |
| --- | --- | --- | ---: |
| HRIS | `employee.deactivate` | `managed-subject-state-change-count-v1` | 1 |
| IAM | `identity.disable` | `managed-subject-state-change-count-v1` | 1 |
| IAM | `sessions.revoke` | `managed-subject-state-change-count-v1` | 1 |

The declaration means:

> for the frozen observable metric, one logical offboarding effect is admitted under the claim that at most the declared subject's managed product-state projection changes.

It does not mean that all real-world harm or all hidden product-side effects are bounded by one.

## Exact identity binding

For a concrete proposal, the generated exposure declaration binds:

- the exact proposal id;
- the frozen metric id;
- the exact proposal subject;
- bound 1.

A measurement for another proposal, metric, or subject cannot settle this declaration.

## Coverage invariant

The declaration registry is tested to have exactly the same operation keys as `OffboardingKernel.ALLOWED_EXTERNAL_OPERATIONS`.

This prevents a newly allowed offboarding operation from silently inheriting no exposure semantics or an accidental default metric.

An operation outside the registry fails rather than receiving an inferred declaration.

## Falsification

The declaration is deliberately falsifiable.

For every one of the three operation classes, a complete managed-subject measurement that reports both the declared subject and a control subject as changed produces realized exposure 2. Against the frozen bound 1, the metric bridge is not established.

No clamping or target-only reinterpretation is permitted.

## Relation to candidate AIOS acceptance evidence

Open AIOS PR #35 contains candidate real ephemeral product instrumentation for the same metric. Its real Keycloak and Odoo acceptance runs observed only the declared target changing in the managed-subject projection.

Those candidate measurements do not become accepted evidence merely because this declaration exists. The AIOS change remains independently gated and currently unmerged because an unrelated generic Autodev vulnerability-scan workflow is red.

The declaration and the measurement source therefore remain separate proof obligations.

## Claim boundary

This result does not establish:

- that bound 1 is a universal bound on offboarding harm;
- that the observable product-state projection captures all side effects;
- that candidate AIOS acceptance evidence is accepted into the BAA chain;
- that every production product tenant has a complete managed-subject universe;
- that the joint-risk functional is calibrated to these unit bounds;
- production safety.

It only freezes the concrete metric semantics attached to the three reference offboarding proposal classes.

## Next structural obligation

Once a scope-complete measurement source for this metric is accepted, the remaining structural semantic question is the risk functional: why and under what assumptions should unit managed-subject state-change exposures, including interactions between effects, be composed by the declared joint-risk function.
