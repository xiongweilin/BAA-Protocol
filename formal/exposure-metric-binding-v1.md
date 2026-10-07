# Exposure Metric Binding v1

> English | [简体中文](exposure-metric-binding-v1.zh-CN.md)

## Status

This layer makes the next semantic dependency explicit without changing the frozen structural-v1 state machine.

Structural v1 carries an integer `exposure_bound`, but that integer has no concrete metric identity. A reality-side measurement cannot safely feed formal settlement merely because it is also an integer.

The executable binding contract is implemented in `baa_protocol/exposure_bridge.py` and tested in `tests/test_exposure_bridge.py`.

## Frozen observable metric

This binding version recognizes one concrete metric identifier:

`managed-subject-state-change-count-v1`

Its value is the number of managed subjects whose frozen, explicitly observed product-state projection changes across one logical operation.

The metric is intentionally narrower than universal "all real-world side effects." Hidden product fields, unrelated object types, unmanaged subjects, downstream systems, and harms not represented by the projection are outside this metric.

## Required declaration

Before a concrete measurement may be used as a realized exposure, the proposal side must explicitly bind:

- proposal identity;
- metric identity;
- declared subject identity;
- exposure bound.

A measurement must then match that declaration exactly and provide:

- the same proposal identity;
- the same metric identity;
- the same declared subject;
- a target read-back compatible with that subject;
- managed-subject counts before and after;
- the changed-subject set;
- a scope-complete attestation for the frozen metric.

This prevents an observation gathered under one metric from silently settling a bound declared under another.

## Fail-closed cases

The executable checker rejects:

- proposal identity rebound;
- metric identity rebound;
- subject identity rebound;
- unsupported metric identifiers;
- incomplete managed-subject scope;
- read-back whose subject differs from the declaration;
- changed subjects outside the declared target;
- realized metric exposure above the declared bound.

A collateral-subject fixture remains explicit: target `employee:1`, control `employee:2`, bound 1, changed set `{employee:1, employee:2}` gives realized exposure 2 and does not establish the bridge.

## Relation to Exposure Bridge Contract v1

[Exposure Bridge Contract v1](exposure-bridge-contract-v1.md) established that target-only read-back is insufficient to prove a broad subject-scope bound.

This layer does not reverse that result. Instead it implements the second option identified there: define a narrower observable metric and require an exact metric declaration before its measurement can be interpreted as exposure.

That still leaves a semantic question open:

> Is `managed-subject-state-change-count-v1` actually the exposure quantity intended by a given structural guarantee?

This contract prevents accidental metric substitution; it does not answer that calibration question.

## Current acceptance instrumentation

The AIOS real Odoo/Keycloak connector acceptance has a candidate implementation of this observable metric on an isolated ephemeral tenant, with explicit managed control subjects and before/after enumeration. Those candidate runs are not part of this BAA claim until the corresponding AIOS change is accepted on its own repository line.

The binding contract therefore stands independently of any one acceptance run.

## Claim boundary

This result does not establish:

- that the observable metric captures all product side effects;
- that the observable metric captures severity or probability of harm;
- that current production tenants can be enumerated completely;
- that the abstract structural-v1 `exposure_bound` was historically declared using this metric;
- that the joint-risk functional is calibrated to this metric;
- production safety.

It establishes exact metric/identity binding and fail-closed conversion from a complete observable measurement to an integer realized exposure.

## Next structural obligation

After an accepted reality-side measurement source exists, the remaining semantic obligation is to bind each concrete proposal class to an explicit exposure metric and justify why that metric is the quantity consumed by the declared joint-risk functional.
