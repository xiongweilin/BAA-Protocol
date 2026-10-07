# Runtime Mediation Surface v1

> English | [简体中文](runtime-mediation-surface-v1.zh-CN.md)

## Status

This record freezes a finite, revision-pinned inventory of the World Runtime HTTP surfaces that can initiate provider dispatch, prepare/advance a domain-owned effect, record its result, or enter provider reconciliation.

Pinned AIOS revision:

`34b9f4274487f856ac4c23266d1dd726b24ae53c`

This is the next structural step after World Runtime refinement v1. It is an executable surface-coverage claim, not a proof that no out-of-process or future bypass exists.

## Frozen reality-facing Runtime surface

The current inventory is:

| Method | Route | Boundary role |
| --- | --- | --- |
| POST | `/v1/invoke` | canonical Runtime capability invocation |
| POST | `/v1/domain-effects/prepare` | authorize and durably bind a domain-owned reality-changing effect |
| POST | `/v1/domain-effects/{idempotency_key}/start` | grant one fresh provider dispatch generation |
| POST | `/v1/domain-effects/{idempotency_key}/result` | persist provider outcome / ambiguity / reconciled result |
| POST | `/v1/reconcile/{idempotency_key}` | enter Runtime provider reconciliation for a durable attempt |

The executable test does not merely check that these routes exist. It discovers route endpoint functions that call the concrete Runtime provider-boundary methods and requires the discovered set to equal this frozen list. A new dispatch/recovery route therefore fails CI until it is explicitly reviewed and added.

## Required mediation checks

Every discovered route must construct authenticated request context and pass Runtime transition-authority checks before it crosses the provider-boundary state.

In addition:

- `/v1/invoke` must pass effect-authority checks before reality-changing capability invocation;
- `/v1/domain-effects/prepare` must pass effect-authority checks before it creates a dispatchable domain effect;
- the Administrative offboarding bridge must enter reality-changing execution through `/v1/invoke`;
- the autonomous-development bridge must prepare and start its domain effect before calling the concrete provider, and it must check `dispatch_allowed` before that provider call.

The last ordering condition is paired with the existing ambiguous-effect test, which demonstrates that a previously unknown outcome cannot receive a second dispatch grant.

## Relation to prior refinement layers

Structural v1 checks the abstract protocol state machine.

AIOS refinement v1 checks concrete offboarding gate traces against that abstract phase relation.

World Runtime refinement v1 checks capability/resource/version scope, authorization, durable effect identity, identity rebound rejection, writer/verifier separation, and ambiguous-effect fencing.

This mediation-surface layer checks that the pinned HTTP/adaptor entry points that can cross into provider-side execution are explicitly inventoried and guarded.

## Claim boundary

This result does not establish:

- a whole-repository proof that arbitrary Python code cannot directly call a provider object;
- operating-system, process, service-mesh, firewall, credential, or network-route complete mediation;
- absence of a bypass added outside the pinned revision;
- semantic correctness of authorization decisions;
- concurrency/crash refinement for all interleavings;
- product-connector refinement into Keycloak/Odoo state transitions;
- correctness or independence of product read-back;
- the exposure/risk semantic bridge.

Accordingly, the accepted claim is **pinned public Runtime/adaptor provider-boundary surface coverage**, not universal complete mediation.

## Next structural obligation

The next useful refinement target is the product boundary: connect the Runtime request identity and dispatch/reconciliation record to the pinned Keycloak/Odoo writer and verifier connectors, including lost-ack and read-back recovery, without inflating the current surface claim into production safety.
