# Real-Product Exposure Binding Acceptance v1

> English | [简体中文](real-product-exposure-binding-v1.zh-CN.md)

## Accepted scope

This is a finite real-product acceptance result for the observable metric `managed-subject-state-change-count-v1`, **not** a proof of total external exposure or the structural joint-risk functional.

The accepted AIOS implementation is merged at `b2cc1254a1908d00ded7c705f6e230c43f08f6f8`. Its preregistered structural dependencies were exercised against BAA-Protocol `b3215d940cf7c9bd6b208ed5915eaa3c92ab10e3`. The successful real-product E2E workflow is [run 37638217335](https://github.com/xiongweilin/aios/actions/runs/37638217335), triggered on the PR implementation head `e10c5f6c52e12ea08f603e9c8d01ca099e070df4`. The corresponding AIOS main merge includes these changes.

## Four acceptance cases

| Scenario | Evidence artifact | Observed result |
| --- | --- | --- |
| Normal | `11491082646` | Three admitted proposal identities each matched a scope-complete managed-subject measurement, bound 1 and realized value 1 |
| Lost acknowledgement | `11489419994` | Three such bindings; externally complete with recovered identity and no extra product exposure in the observed projection |
| Read-back outage | `11489454782` | Three such bindings; delayed observation still completed without reinterpreting an unknown effect as no effect |
| Unauthorized Runtime bypass | `11489744687` | Unauthorized request rejected with HTTP 403; the observed product before/after state was unchanged; no admitted exposure bindings were expected |

The first three artifacts each record `assessment_established=true` for all three offboarding effects: Odoo employee deactivation, Keycloak identity disable, and Keycloak session revocation. Their `changed_subject_refs` sets contain only the declared target. The tracked managed-subject populations are 3 Odoo employees and 2 Keycloak subjects in these ephemeral acceptance tenants. A separately provisioned control subject provides a concrete collateral-change falsification opportunity.

The bypass artifact measures a different property: denying a non-authorized reality-changing invocation. It does **not** contain three admitted proposal bindings and must not be counted as a successful exposure-settlement episode.

## What this actually bridges

A proposal from the BAA-gated offboarding engine carries a frozen metric declaration and bound. Product-side snapshots enumerate the managed subjects represented by the frozen observation projection; their before/after changes are bound back to the exact proposal, metric, and declared subject. Only matching evidence is interpreted as a realized metric value.

This is stronger than independent *target-only* postcondition read-back: control-subject state was also checked. It does not extend the structural guarantee to hidden product fields, unmanaged entities, unrelated object types, downstream effects, or unobserved intervals.

`scope_complete=true` means complete for the **declared acceptance projection over the enumerated managed-subject universe**, not complete for every possible product or real-world effect.

## Unclosed obligations

- Demonstrate that the snapshot source remains complete under concurrent changes, pagination anomalies, process crashes, and adversarial perturbations.
- Establish the metric-to-reality bridge for production tenants, if any such claim is desired.
- Assign evidence-backed shared-risk-factor identities, interaction semantics, and an interaction penalty—or explicitly leave the joint-risk guarantee conditional.
- Avoid treating three unit exposure observations as a proof that their combined real-world loss is three or less.

The frozen structural-v1 model and empirical delegation-frontier studies remain unchanged. This acceptance result closes one finite measurement/identity link, not the semantic justification of the full joint-risk model.
