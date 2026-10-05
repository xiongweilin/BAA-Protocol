# State Machine

## 1. Scope

This document defines the minimal protocol states required to distinguish authorization, execution, external effect, observation, verification, and settlement.

It is an executable design target, not a claim that every deployment must use identical storage tables or process boundaries.

## 2. Proposal states

A proposal begins in:

~~~text
PROPOSED
~~~

Admission produces exactly one of:

~~~text
PROPOSED -> DENIED
PROPOSED -> HELD
PROPOSED -> ADMITTED
~~~

- DENIED is terminal for that proposal version.
- HELD grants no reality-facing authority. A later retry must be represented as a new evaluation event, preserving the prior hold.
- ADMITTED requires issuance of a narrow capability and reservation of the declared exposure relevant to the guarantee.

## 3. Execution states

An admitted proposal may progress:

~~~text
ADMITTED
  -> ATTEMPTED
  -> PENDING
  -> VERIFIED
  -> SETTLED
~~~

Alternative paths include:

~~~text
ADMITTED -> EXPIRED
ATTEMPTED -> VERIFIED_NO_EFFECT
ATTEMPTED -> PENDING
PENDING -> VERIFIED
PENDING -> CONSERVATIVE_SETTLEMENT
PENDING -> SAFE_TERMINATION
VERIFIED -> RECOVERY
RECOVERY -> VERIFIED_RECOVERY
~~~

These labels describe semantic positions. A deployment may combine storage operations while preserving the distinctions.

## 4. Capability lifecycle

A capability is valid only when all of the following hold:

- it was issued by the trusted kernel;
- its proposal remains admitted;
- object and operation match exactly;
- requested amount / quota is within the capability;
- current time is within its validity interval;
- required preconditions still hold;
- it has not been revoked, exhausted, or invalidated by a state-version change.

The executor must reject a request when any of these conditions fail.

Agent text cannot mutate the capability.

## 5. Exposure accounting states

For a resource or risk dimension covered by the deployment model, exposure is tracked in non-overlapping accounting categories.

### Reserved

Exposure committed by admission but not yet dispatched.

### Pending

Execution has been attempted and the real-world effect is not yet adequately verified.

### Settled

The deployment has a defined terminal accounting treatment for the effect.

Settlement does not necessarily mean "no future consequence". It means the guarantee contract has defined how the remaining consequence is represented for the stated horizon.

The accounting implementation must define transitions so that one exposure is not silently present in two categories unless the risk functional intentionally models both.

## 6. Unknown effect semantics

After an execution attempt, lack of confirmation does not imply lack of effect.

The possible state must preserve at least:

~~~text
effect definitely absent
effect definitely present
effect unresolved
~~~

When partial execution is possible, the deployment must add sufficient states to cover it.

Retry policy must depend on effect semantics, not only transport idempotency.

## 7. Hold semantics

HELD is a non-authorizing state used when safe or justified admission cannot yet be established.

Examples:

- an authoritative read-back is unavailable;
- state uncertainty crosses the allowed envelope;
- composition with existing reservations is not bounded;
- postcondition verification is unavailable;
- an assumption needed for the semantic bridge is stale;
- the fallback policy would no longer be timely;
- the proposal is waiting for a separately authorized state change.

Hold is not completion and is not a successful delivery.

## 8. Pending timeout

A deployment must define a deadline for unresolved pending effects when a finite guarantee horizon requires one.

At timeout, the protocol may:

1. move the declared upper bound into conservative settled exposure; or
2. enter a safe terminal / degraded state.

The choice is part of the deployment contract.

The protocol must not:

- release the reservation merely because confirmation was lost;
- treat timeout as evidence that no effect occurred;
- automatically replay an action whose real-world effect may already have happened.

## 9. Viability and fallback

Admission into ADMITTED may require more than checking the immediate state.

For structural safety claims, the post-admission information state must remain inside a conservative region W_Omega from which a fallback policy is still enforceable in time.

A fallback can include, when actually available:

- refuse subsequent capabilities;
- rate-limit;
- isolate a resource;
- switch to a trusted controller;
- stop a process;
- enter a bounded degraded mode;
- compensate or reconcile;
- preserve pending exposure until evidence arrives.

A notification to a human is not itself a fallback guarantee during a strictly unattended interval unless the claim assumes a bounded human response time.

## 10. Version and state identity

Each event SHOULD bind:

~~~text
deployment_version
contract_version
kernel_version
tool_or_executor_version
observation_version
proposal_id
capability_id
state_version
timestamp
~~~

A stale capability can therefore be rejected when the state, contract, or protected dependency changed after issuance.

## 11. Minimal transition invariants

Reference implementations SHOULD test at least:

1. no covered execution without a valid capability;
2. no capability issuance when projected joint-state constraints fail;
3. no automatic zeroing of unresolved effects;
4. no capability reuse beyond quota or expiry;
5. no silent retry after an effect-unknown state unless the effect semantics permit it;
6. no structural claim whose protected evidence can be modified through an admitted uncovered path;
7. terminal treatment of unresolved effects;
8. preserved distinction among safety success, delivery success, and completion.

## 12. Event record

A minimal append-only event representation can include:

~~~text
event_id
proposal_id
event_type
prior_state
next_state
deployment_version
evidence_refs
capability_ref
exposure_before
exposure_after
observation_status
verification_status
reason_code
timestamp
~~~

The VSAR can add richer research fields, but the state transition history should remain reconstructable without relying on a later agent narrative.
