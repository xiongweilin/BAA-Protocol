# 状态机

> [English](state-machine.md) | 简体中文

## 1. 范围

本文定义区分 authorization、execution、external effect、observation、verification 与 settlement 所需的最小 protocol state。

它是 executable design target，不声称每个 deployment 必须使用完全相同的 storage table 或 process boundary。

## 2. Proposal states

proposal 从：

~~~text
PROPOSED
~~~

开始。

admission 恰好产生一种：

~~~text
PROPOSED -> DENIED
PROPOSED -> HELD
PROPOSED -> ADMITTED
~~~

- DENIED 对该 proposal version 为 terminal。
- HELD 不授予 reality-facing authority。后续 retry 必须表示为新的 evaluation event，并保留前一 hold。
- ADMITTED 要求发放 narrow capability，并 reservation 与 guarantee 相关的 declared exposure。

## 3. Execution states

admitted proposal 可沿：

~~~text
ADMITTED
  -> ATTEMPTED
  -> PENDING
  -> VERIFIED
  -> SETTLED
~~~

演化。

其他路径：

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

这些 label 表示 semantic position。deployment 可合并 storage operation，但必须保留语义区别。

## 4. Capability lifecycle

capability 仅在以下全部成立时有效：

- 由 trusted kernel 发放；
- proposal 仍为 admitted；
- object/operation 精确匹配；
- requested amount/quota 在 capability 范围内；
- 当前时间处于 validity interval；
- required precondition 仍成立；
- 未被 revoke、exhaust，也未因 state-version change 失效。

任一条件失败，executor 必须拒绝 request。

agent text 不能修改 capability。

## 5. Exposure accounting states

对 deployment model 覆盖的 resource/risk dimension，exposure 使用互不重叠 accounting category。

### Reserved

admission 已承诺但尚未 dispatch 的 exposure。

### Pending

execution 已 attempt，但 real-world effect 尚未 adequate verification。

### Settled

deployment 已为 effect 定义 terminal accounting treatment。

settlement 不一定意味着“未来没有 consequence”；它表示 guarantee contract 已规定在声明 horizon 内如何表示剩余 consequence。

accounting implementation 必须定义 transition，避免同一 exposure 静默同时存在于两个 category，除非 risk functional 有意这样建模。

## 6. Unknown effect semantics

execution attempt 后缺少 confirmation，不等于没有 effect。

possible state 至少保留：

~~~text
effect definitely absent
effect definitely present
effect unresolved
~~~

若可能 partial execution，deployment 必须增加足够 state 覆盖。

retry policy 必须依赖 effect semantics，而不能只依赖 transport idempotency。

## 7. Hold semantics

HELD 是 non-authorizing state，用于当前无法建立 safe/justified admission 的情况。

例如：

- authoritative read-back unavailable；
- state uncertainty 超出 allowed envelope；
- 与现有 reservation 的 composition 无法 bound；
- postcondition verification unavailable；
- semantic bridge 所需 assumption stale；
- fallback policy 已不能 timely 执行；
- proposal 等待一个另行授权的 state change。

hold 不是 completion，也不是 successful delivery。

## 8. Pending timeout

如果 finite guarantee horizon 需要 deadline，deployment 必须为 unresolved pending effect 定义 deadline。

timeout 时可以：

1. 把 declared upper bound 转入 conservative settled exposure；
2. 或进入 safe terminal / degraded state。

选择属于 deployment contract。

protocol 不得：

- 因 confirmation 丢失就释放 reservation；
- 把 timeout 当成“没有 effect”的 evidence；
- 自动 replay 可能已经产生 real-world effect 的 action。

## 9. Viability 与 fallback

进入 ADMITTED 前可能需要检查的不只是 immediate state。

对于 structural safety claim，post-admission information state 必须保持在保守 W_Omega 中，使 fallback policy 仍能及时 enforce。

实际可用时，fallback 可包括：

- 拒绝后续 capability；
- rate-limit；
- isolate resource；
- 切换 trusted controller；
- stop process；
- 进入 bounded degraded mode；
- compensate/reconcile；
- 保留 pending exposure 直到 evidence 到达。

在 strictly unattended interval 中，“通知人类”本身不构成 fallback guarantee，除非 claim 假设 bounded human response time。

## 10. Version 与 state identity

每个 event SHOULD 绑定：

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

因此，当 state、contract 或 protected dependency 在 issuance 后变化时，可拒绝 stale capability。

## 11. 最小 transition invariants

reference implementation SHOULD 至少测试：

1. 无 valid capability 不得 covered execution；
2. projected joint-state constraint 失败时不得 issuance capability；
3. unresolved effect 不得自动归零；
4. capability 不得超 quota/expiry 复用；
5. effect-unknown 后不得 silent retry，除非 effect semantics 明确允许；
6. admitted uncovered path 能修改 protected evidence 时，不得声称 corresponding structural guarantee；
7. unresolved effect 有 terminal treatment；
8. 保持 safety success、delivery success 与 completion 三者区分。

## 12. Event record

最小 append-only event 可包含：

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

VSAR 可增加研究字段，但 state-transition history 应在不依赖后续 agent narrative 的情况下可重建。
