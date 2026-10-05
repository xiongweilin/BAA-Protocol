# 员工离职任务域

> [English](employee-offboarding.md) | 简体中文

## 1. 任务域

这是 BAA-Protocol 的第一个具体任务域。

[
D = \texttt{employee-offboarding}
]

该任务域来自 AIOS 的 Administrative offboarding path。AIOS 已经把 governed facts、policy evaluation、authority、approval、execution authorization、external effects、independent read-back、reconciliation、completion 与 responsibility discharge 分开表示。

本仓库不声称实现或认证 AIOS。AIOS 文档与代码仅作为本 BAA instance 的源任务域模型。

第一版实验固定源快照：

~~~text
xiongweilin/aios@87f24f32a01c67a9246fc3cb127517c80798e169
~~~

之后任何影响 authority、obligation、effect、observation、reconciliation 或 completion 语义的 AIOS 变化，都必须先经过显式 domain-version review，结果才可继续比较。

## 2. 覆盖的现实操作

初始 external effect set 刻意保持狭窄：

- HRIS employee deactivation；
- IAM identity disablement；
- IAM session revocation。

对应预期 reality-side postconditions：

~~~text
hris.employee.deactivate:
  active == false

iam.identity.disable:
  enabled == false

iam.sessions.revoke:
  active_sessions == 0
~~~

identity-binding expiry、role-assignment expiry、role transfer、delegation expiry、principal deactivation 等 Administrative-domain obligation 对完整完成仍然重要，但在第一版 BAA executable model 中不表示为 remote-provider effect。

## 3. 结构输入

外部离职 effect proposal 至少必须绑定：

~~~text
case_id
subject_ref
authority_epoch
governance_basis_id
obligation_id
target_system
operation
expected_postcondition
effective_at
capability_expiry
state_version
request_identity
~~~

只有满足以下条件才有资格进入准入：

- case kind 为 employee-offboarding；
- effect 属于当前 immutable obligation set；
- authority epoch 与 governance basis 当前有效；
- operation 精确等于 obligation 允许的 operation；
- target subject 与 obligation 一致；
- 已到 authoritative effective time；
- 相应 target system 的 verification path 可用，或 deployment contract 明确允许 hold；
- 当前 information state 仍处于声明的 viable region 内。

## 4. Hard kernel property（I_K）

对覆盖接口，第一版原型尝试机械执行：

1. authoritative effective time 前不得发出外部 offboarding effect；
2. stale authority epoch 或 stale state version 下不得执行；
3. subject、target system 或 operation 与 admitted obligation 不匹配时不得执行；
4. 没有 narrow capability 不得执行覆盖 effect；
5. proposal 进入 pending 或 settled 后 capability 不得复用；
6. 前一 effect 可能已发生但确认缺失时不得自动 replay；
7. unresolved effect 按 deployment contract 持续计入暴露，或迫使系统进入 safe termination；
8. admitted action 不能修改 protected kernel、capability authority、VSAR 或 independent observation source。

这些是 interface/protocol properties。它们本身不说明某员工是否应被解雇，也不说明底层 HR policy 在规范上正确。

## 5. 现实属性（I_D^*）

第一版 domain bridge 只针对以下有界声明。

### Effect-scope property

每个覆盖的现实离职 effect，都必须可归因到同一 case、subject、authority epoch、target system 与 operation 的当前 exact-scope obligation。

### Timing property

任何覆盖的 deactivation / disablement / session-revocation effect 都不得在 authoritative effective time 前被有意 dispatch。

### Verified-effect property

外部 obligation 不能仅因 execution 返回 success 就被视为 fulfilled。必须存在满足冻结 postcondition 的当前 independent observation。

### Unknown-result property

若 execution result 含糊或 verification 不可用，obligation 保持 unresolved；协议不能推断“没有 effect”，也不能因此获得隐式 replay permission。

### Completion property

在 BAA 实验中，只有所有覆盖范围内 external postconditions 都被 independent verification 后，case 才计为 externally complete。Administrative-domain obligations 与 responsibility discharge 仍是第一版 executable kernel 之外的额外完成条件。

## 6. Bridge assumptions（Omega_bridge）

从 I_K 推到上述现实声明依赖：

- HRIS subject identifier 确实指向目标员工；
- IAM subject identifier 正确绑定目标 principal；
- authoritative effective-time source 当前有效；
- obligation set 来自预期 policy 与 authority process；
- 对覆盖 provider operations，executor 是代理唯一可用路径；
- independent read-back credential/endpoint 不能通过 admitted agent capability 写入；
- HRIS read-back 字段 <code>active</code> 在覆盖 deployment 中确实表示 employment activation；
- IAM read-back 字段 <code>enabled</code> 确实表示 login identity enablement；
- IAM session read-back 覆盖 policy 相关 active sessions；
- provider-side request identity 防止 request 被含糊地重新绑定到另一个 subject 或 operation；
- clock 与 state-version comparison 满足声明 timing assumptions。

这些假设必须显式存在。任何假设无法成立时，相应现实保证必须弱化或撤回。

## 7. Information state（q_t）

offboarding kernel 至少维护：

- current case / authority epoch；
- current governance-basis qualification status；
- effective time 与 current clock interval；
- immutable obligation-set identity；
- 与 completion 有关的 transfer/internal obligation blocker；
- admitted capabilities；
- reserved effects；
- pending / outcome-unknown effects；
- verified outcomes；
- observation freshness / availability；
- protected-source status；
- terminal pending policy。

kernel 不假设能够直接访问真实 external state。

## 8. Compatible-state 处理

每个 attempted external effect 至少保留：

~~~text
definitely_not_effected
possibly_effected
verified_effected
~~~

outcome-unknown provider result 进入 <code>possibly_effected</code>。

observation unavailable / stale / unknown 不能把 <code>possibly_effected</code> 折叠成 <code>definitely_not_effected</code>。

## 9. Viable region（W_Omega）

第一版原型使用保守 viable region，而不是最大 viable region。

只有满足以下条件，state 才有资格再次 dispatch external offboarding effect：

- next operation 有当前 exact-scope obligation 与 capability；
- 该 obligation 不存在前一 unresolved effect；
- authority epoch 与 state version 仍当前有效；
- effective time 已到；
- protected observation path 未失效；
- deployment 仍可拒绝所有未来 covered effects，而不违反已声称的 hard safety property。

该区域通过停止后续 effect 支持安全，但**不**保证 eventual completion。

## 10. Exposure model（rho）

第一版原型不假装所有 offboarding harm 都能压成有意义的单一标量。

使用 constraint vector：

[
\rho(q)=(U,S,A,P)
]

其中：

- U：unresolved external-effect obligations；
- S：stale-authority execution count；
- A：out-of-scope action count；
- P：protected-source mutation count。

hard budget：

~~~text
S == 0
A == 0
P == 0
U <= U_max
~~~

<code>U_max</code> 是 deployment parameter，控制可同时存在多少 unresolved effect。默认实验使用 <code>U_max = 1</code>，强制 serial reconciliation。

这刻意不被称为完整 harm metric。

## 11. Capability

offboarding capability 绑定：

~~~text
case_id
authority_epoch
obligation_id
subject_ref
target_system
operation
state_version
not_before
expires_at
request_identity
~~~

它不授予任意 HRIS 或 IAM access。

## 12. Hold 条件

在以下情况下，BAA 返回 <code>hold</code>，而不是虚构确定性：

- effective time 未到；
- authoritative time 或 fact freshness 不可用；
- obligation / governance basis 无法重新验证；
- required effect 的 verification 不可用；
- 同一 obligation 已存在 unresolved effect；
- protected observation path 降级；
- 声称现实属性所需 bridge assumption 已不当前有效。

## 13. Terminal unresolved effects

若 unattended horizon 结束时，external effect 仍可能已经发生但未验证：

- VSAR 中保持 unresolved；
- 不产生 replay permission；
- 暴露继续计入；
- delivery 不完整；
- deployment 可进入 safe terminal state。

该 effect 不得从统计分母中移除。

## 14. 明确不保证的内容

第一版 domain instance 不结构性证明：

- termination 本身合法或公平；
- selected successor 在规范上正确；
- 全部组织知识转移已完成；
- 禁用这些接口消除了所有 access path；
- provider observation 在 Omega_bridge 之外语义完整；
- 员工不会通过 communication、reputation、payroll、physical access 或其他未覆盖渠道受损；
- external completion 自动意味着 responsibility discharge。

这些都在第一版 guarantee boundary 之外。

## 15. 第一版实验

比较相同 offboarding episode set 下三种制度：

1. agent self-check 后直接执行；
2. direct execution + external record / post-hoc audit；
3. BAA admission + exact-scope capability + serial unresolved-effect limit + independent read-back + conservative pending treatment。

fault scenario 包括：

- IAM disable 后 execution confirmation 丢失；
- outcome unknown 后 repeated request；
- stale authority epoch；
- capability 用于另一员工；
- capability 用于另一 operation；
- observation source unavailable；
- effective time 前 attempt；
- 试图修改 protected observation source；
- 保持 kernel 不变的 model replacement；
- adaptive decomposition / retry probing。

核心问题：

> 在相同 offboarding workload 下，BAA 能否降低 unsafe reality-facing transition 与 unresolved replay risk，同时不让 principal attention 或 incomplete delivery 占据主导？
