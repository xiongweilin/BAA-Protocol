# Exposure Bridge Contract v1

> English | [简体中文](exposure-bridge-contract-v1.zh-CN.md)

## Status

This record makes one remaining assumption of structural v1 executable and falsifiable:

`realized exposure used for settlement <= declared exposure bound`.

The result is deliberately **not** that the assumption has now been established for the pinned product path. The result is that the minimum evidence contract is explicit, current target-only product read-back is insufficient to satisfy it, and counterexamples are preserved rather than clamped.

The executable contract is in `baa_protocol/exposure_bridge.py`; regression and counterexample tests are in `tests/test_exposure_bridge.py`.

## Concrete exposure metric

v1 defines one narrow metric only:

> subject-scope exposure = number of distinct product subjects affected by one logical effect.

This metric is suitable for testing the structural bound assumption but does not claim to represent severity, probability of harm, monetary loss, privilege magnitude, session count, or a universal notion of risk.

For a declared bound of one, admissible complete evidence may establish zero or one affected declared subject. Any second subject falsifies the bound.

## Evidence contract

A settlement-capable evidence record must contain:

- the declared subject identity;
- the observed target postcondition;
- an explicit set of affected subject identities;
- an attestation that this affected-subject set is complete for the declared metric.

Target postcondition read-back alone does not satisfy the last two requirements.

The bridge therefore has three outcomes:

1. **established** — scope-complete evidence measures exposure within the declared bound;
2. **falsified** — scope-complete evidence measures exposure above the bound or outside the declared target;
3. **unestablished** — evidence is target-scoped but does not establish collateral-effect coverage.

Only the first outcome can produce a realized exposure value for formal settlement.

## Current pinned product evidence

The existing Odoo/Keycloak verifiers report the current state of the declared target:

- Odoo employee deactivation reports the declared subject and its current `active` value;
- Keycloak identity disable reports the declared subject and current `enabled` value;
- Keycloak session revoke reports the declared subject and current active-session count.

Those observations are valuable for effect completion and product reconciliation, but they do not enumerate all product subjects affected by the underlying operation. They therefore remain scope-incomplete for this exposure metric.

This means the product refinement chain can establish exact request identity, no blind replay after ambiguity, and target postcondition verification while the structural exposure-bound assumption remains conditional.

## Counterexamples

The executable tests preserve two classes of falsification.

### Collateral subject

For a declared subject `employee:1` and bound 1, complete evidence containing both `employee:1` and `employee:2` produces realized exposure 2.

The same value is then passed into the structural-v1 transition model, whose verification step rejects settlement because it lies outside the declared bound.

### Target rebound

If product read-back identifies `employee:2` while the declared subject is `employee:1`, the bridge is not established even if an affected-subject list is present.

## Why this is a negative structural result

Earlier refinement layers progressively connect:

`formal state -> AIOS gate -> World Runtime -> mediated provider surface -> product connector`.

They do not supply a complete observation of collateral subject effects. Treating target verification as if it proved exposure completeness would silently strengthen the evidence.

v1 therefore records the gap rather than redefining exposure after the fact.

## Claim boundary

This contract does not establish:

- that current Keycloak/Odoo APIs provide complete affected-subject enumeration;
- that the subject-count metric is the correct risk quantity for production decisions;
- that a product endpoint cannot have hidden cross-subject side effects;
- that the structural joint-risk functional is calibrated to real harms;
- production failure probabilities or severity;
- production-tenant safety.

It only defines and tests the evidence condition required to make one exposure-bound assumption falsifiable.

## Next structural obligation

There are now two distinct options, and they must not be conflated:

1. add a scope-complete reality-side evidence source for the subject-count metric; or
2. define and justify a different exposure metric whose completeness can actually be observed at the product boundary.

After exposure measurement is established, the remaining semantic task is to justify the declared joint-risk functional itself.
