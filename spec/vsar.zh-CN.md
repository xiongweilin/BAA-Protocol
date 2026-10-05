# VSAR 记录

> [English](vsar.md) | 简体中文

Versioned Sufficiency Assurance Record（VSAR）是 BAA 实验与 deployment 使用的外部 evidence state。

它不是 agent narrative，也不自动构成 guarantee。

## 最小 episode identity

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

每个 proposal 都保留在 population 中，包括从未执行的 proposal。

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

denied/held proposal 不得从后续 coverage calculation 中删除。

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

provider success 不是 verification。

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

unavailable、stale、late 或 incompatible observation 必须显式保留。

## Settlement record

~~~text
attempt_id
settlement: verified_effect | verified_no_effect | unresolved | conservative_charge | recovery
exposure_before
exposure_after
remaining_obligations
settled_at
~~~

guarantee horizon 不会删除 unresolved effect。

## Episode outcome

safety 与 delivery 分开报告：

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

safe termination 可以是 safety success，同时是 delivery failure。

## 统计纪律

reliability 不得只 condition 在：

- admitted proposal；
- successfully completed proposal；
- observed outcome；
- 事后发现 declared assumption 成立的 case。

至少保留 proposed、denied、held、admitted、attempted、unknown、verified、recovered、completed 的 rate。

VSAR 支持 empirical calibration 与 diagnosis，但不能把有限测试存活自动转化为 worst-case structural guarantee。
