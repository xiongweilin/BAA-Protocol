# Product Connector Refinement v1

> English | [简体中文](product-connector-refinement-v1.zh-CN.md)

## Status

This record defines a finite, revision-pinned refinement layer from World Runtime provider request identity into the three concrete product connectors used by the BAA offboarding path.

Pinned AIOS revision:

`34b9f4274487f856ac4c23266d1dd726b24ae53c`

Covered effects:

| Runtime capability | Product writer | Independent read-back |
| --- | --- | --- |
| `administrative.hris.employee.deactivate.v1` | Odoo employee deactivate connector | Odoo deactivate verifier |
| `administrative.iam.identity.disable.v1` | Keycloak identity disable connector | Keycloak disable verifier |
| `administrative.iam.sessions.revoke.v1` | Keycloak session revoke connector | Keycloak session verifier |

The executable fixtures are in `integration/test_aios_product_connector_refinement.py`.

## Refinement relation

The production Runtime provider passes the stable Runtime `CapabilityRequest.id` to each connector as `request_ref`. Runtime recovery later calls the same provider's `reconcile(request_id)`, so the same identity is used for dispatch and reconciliation.

For the covered product operations, the connector must then preserve the following relation:

1. the product write carries a durable operation-specific request marker;
2. a conflicting existing marker is a hard identity failure, not permission to overwrite or reuse the product object;
3. an ambiguous/lost acknowledgement remains unknown;
4. reconciliation searches the durable marker and reads product state instead of repeating the original reality-changing write;
5. only an observed completed product state yields reconciled success;
6. a separate verifier reports current product state rather than copying the expected postcondition.

## Odoo employee deactivation

The writer targets an exact `odoo:hr.employee:<id>` identity.

Its product write sets `active=false` and the deactivate request marker in the same Odoo update. The refinement fixture injects a lost acknowledgement on that write, then presents product state containing the same request marker with the employee inactive. Reconciliation succeeds without issuing a second product write.

A different pre-existing deactivate request marker is rejected as `ConflictingExternalRequestIdentity`.

The verifier independently reads the employee and reports the observed `active` value.

## Keycloak identity disable

The writer reads the exact subject, preserves unrelated user attributes, and writes both `enabled=false` and the disable request marker.

The lost-ack fixture returns an ambiguous server result after the write request. Reconciliation then locates the same marker and observes `enabled=false`; it succeeds without issuing another PUT.

A different existing disable request marker is rejected rather than rebound.

The verifier reads current Keycloak user state and reports the observed `enabled` value.

## Keycloak session revocation

Before logout, the writer first persists the session-revoke request marker on the user. It then observes sessions and performs logout only if sessions remain.

The lost-ack fixture makes the logout outcome ambiguous. Reconciliation searches the marker and reads the session list; when no sessions remain it succeeds after a GET only, without a second logout POST.

A different existing session-revoke marker is rejected rather than rebound.

The verifier independently reports the current active-session count.

## Relation to prior layers

The refinement chain is now finite but explicit:

`formal-v1 -> AIOS gate trace -> World Runtime scope/identity -> Runtime mediation surface -> product connector request marker/read-back`

This layer connects Runtime request identity to product-side durable request identity and recovery behavior. It does not add new abstract protocol phases.

The repository already has separate real ephemeral Keycloak/Odoo connector acceptance and composed real-product E2E evidence. Those runs increase fidelity, but this v1 refinement claim is defined by the pinned executable connector fixtures and must not be widened by those empirical acceptances.

## Claim boundary

This result does not establish:

- production-tenant safety or production credential isolation;
- a formal proof of the HTTP calls or database transactions inside Keycloak/Odoo;
- correctness of product server implementations;
- all transport, crash, concurrency, or partial-write interleavings;
- that a durable request marker is globally unique outside the connector checks;
- semantic equivalence between every expected postcondition and product reality;
- that verifier credential separation guarantees organizational independence;
- the exposure/risk semantic bridge required by structural v1.

Accordingly, the claim is a finite product-connector identity/reconciliation/read-back refinement for the three pinned offboarding operations.

## Next structural obligation

The highest-value remaining structural gap is the semantic bridge from declared admission exposure/risk bounds to measured reality-side exposure. That should be attacked with an explicit falsifiable contract and counterexamples rather than by extending the current connector claim.
