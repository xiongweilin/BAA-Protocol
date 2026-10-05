# VSAR Record

The Versioned Sufficiency Assurance Record (VSAR) is the external evidence state used by BAA experiments and deployments.

It is not an agent narrative and it is not a guarantee by itself.

## Minimal episode identity

~~~text
episode_id
task_domain
deployment_version
contract_version
kernel_version
model_version
tool_version
observation_version
started_at
guarantee_horizon
~~~

## Proposal record

Every proposal remains in the population, including proposals that never execute.

~~~text
proposal_id
episode_id
history_ref
object_identity
operation
scope
declared_assumptions
requested_capability
expected_postcondition
state_version
authority_epoch
created_at
~~~

## Admission record

~~~text
proposal_id
decision: deny | hold | admit
reason_code
kernel_state_digest
joint_constraint_state
capability_ref
decided_at
~~~

A denied or held proposal is not removed from later coverage calculations.

## Execution record

~~~text
capability_ref
attempt_id
dispatch_state
request_identity
attempted_at
provider_result: succeeded | failed | outcome_unknown
provider_ref
~~~

Provider success is not verification.

## Observation / verification record

~~~text
attempt_id
observation_source
availability
freshness
observed_state
observed_at
verification_result
postcondition_version
~~~

Unavailable, stale, late, or incompatible observations remain explicit.

## Settlement record

~~~text
attempt_id
settlement: verified_effect | verified_no_effect | unresolved | conservative_charge | recovery
exposure_before
exposure_after
remaining_obligations
settled_at
~~~

The guarantee horizon does not erase unresolved effects.

## Episode outcome

Report safety and delivery separately.

~~~text
structural_violation_count
verified_harm_count
unknown_result_count
principal_attention
assurance_labor
useful_delivery
completed
safe_terminal
~~~

Safe termination may be a safety success and a delivery failure.

## Statistical discipline

Do not condition reliability only on:

- admitted proposals;
- successfully completed proposals;
- observed outcomes;
- cases whose declared assumptions later proved true.

At minimum retain rates for proposed, denied, held, admitted, attempted, unknown, verified, recovered, and completed states.

VSAR records support empirical calibration and diagnosis. They do not convert finite test survival into a worst-case structural guarantee.
