# World Runtime Refinement v1

## Status

This record defines the second finite concrete refinement layer for BAA structural v1.

Pinned AIOS revision:

`34b9f4274487f856ac4c23266d1dd726b24ae53c`

It is executable through the existing `aios-compatibility` CI job. It does not claim a whole-program proof or deployed-network complete mediation.

## Refinement target

The first AIOS refinement layer maps concrete offboarding gate traces into the abstract BAA phase relation. This layer checks the next boundary: a reality-changing request entering the pinned AIOS World Runtime.

For the BAA-covered offboarding capabilities:

| BAA/AIOS condition | World Runtime refinement check |
| --- | --- |
| exact capability scope | capability is fixed in the request and participates in durable effect identity |
| explicit target/resource scope | a strict effect rule requires an explicit resource boundary |
| evidence/version binding | a strict effect rule requires non-empty subject version refs |
| authorization before release | a strict effect rule requires authorization; missing authorization fails before provider-attempt reservation |
| stable logical effect identity | effectful requests require a durable idempotency key and bind a semantic fingerprint |
| no scope rebound | reusing the idempotency key with changed capability, resource, or subject-version refs is rejected |
| unknown effect stays unresolved | ambiguous domain effect has neither fresh-start nor dispatch permission |
| independent verification | covered writer and verifier providers use distinct credential domains |

The executable helpers are in `integration/world_runtime_refinement.py`.

## Covered concrete evidence

`integration/test_aios_world_runtime_surface.py` checks the pinned administrative production Runtime stack.

It verifies:

1. every BAA-covered capability has `authorization_required`, `resource_required`, and `version_required`;
2. writer and verifier credential domains are distinct;
3. missing authorization fails after resource/version requirements are satisfied, before a durable provider attempt exists;
4. missing resource and missing version bindings each fail before a provider attempt exists;
5. the Runtime semantic effect fingerprint changes when capability, resource, or subject-version scope changes;
6. a previously bound idempotency identity rejects those scope rebounds.

`integration/test_aios_canary_runtime_reconciliation.py` checks the pinned domain-effect boundary over the real Runtime HTTP service. After a simulated lost acknowledgement, the durable effect is `ambiguous`, has a recorded dispatch generation, and exposes neither `start_allowed` nor `dispatch_allowed`. A second provider call is rejected.

## Relation to formal v1

This layer does not introduce new abstract phases. It refines structural-v1 obligations around capability scope and unknown-effect replay:

- Runtime legality checks are preconditions for crossing from reserved authority toward a reality-facing pending effect.
- The durable semantic fingerprint prevents one logical effect identity from expanding to a different capability/resource/version scope.
- An ambiguous durable effect corresponds to an unresolved pending effect and cannot authorize blind redispatch.
- Separate verifier credentials support the independence assumption used by the concrete trace layer, but do not by themselves prove semantic correctness of a read-back.

## Important boundary

The following remain outside this claim:

- proof that every deployed reality-changing network path is forced through `WorldRuntime.invoke()` or the domain-effect boundary;
- concurrency/crash refinement for all ledger interleavings;
- formal equivalence between Runtime authorization semantics and the full BAA authority model;
- product-connector refinement from Runtime provider calls to Keycloak/Odoo semantics;
- proof that subject-version refs are complete or semantically sufficient;
- proof that independent verifier credentials imply independent evidence;
- the exposure/risk semantic bridge required by the structural-v1 budget invariant;
- production-tenant or unattended-autonomy safety.

Accordingly, this is a finite executable boundary refinement, not complete mediation or end-to-end verification.

## Next structural obligation

The next useful step is narrower than another phase mapping: test complete-mediation coverage for the pinned reality-changing HTTP/domain-provider surfaces, then extend refinement across concrete product connectors. Any such claim should remain revision-pinned and counterexample-driven.
