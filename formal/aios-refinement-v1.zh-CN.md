# AIOS Refinement Mapping v1

> [English](aios-refinement-v1.md) | 简体中文

## 状态

本文记录第一版从固定 AIOS offboarding execution path 到 BAA 结构模型 phase 词汇的可执行**有限 trace refinement 检查**。

它比 [structural-guarantees-v1.zh-CN.md](structural-guarantees-v1.zh-CN.md) 更窄：

- structural v1 穷举检查抽象状态迁移系统本身；
- refinement v1 检查三个具体 AIOS/BAA integration trace 能否投影到允许的抽象 phase transition。

它不是 whole-program refinement proof。

## 具体边界

被检查的路径：

~~~text
AIOS OffboardingExecutionEngine
  -> BAAGatedAIOSProvider
  -> OffboardingKernel admission
  -> narrow capability execution
  -> EffectProvider
  -> independent/post-dispatch observation
  -> OffboardingKernel verification
~~~

测试复用 `integration/test_aios_runtime_gate.py` 已固定的 AIOS integration surface。

## 投影

refinement checker 直接复用 `baa_protocol.formal_model.Phase`。

| 具体事件 | 抽象 phase transition |
|---|---|
| BAA 准入 AIOS effect 并签发窄 capability | `PROPOSED -> RESERVED` |
| BAA 在 provider dispatch 前记录 execution | `RESERVED -> PENDING` |
| outcome 仍含糊且 observation 不可用 | `PENDING -> PENDING` |
| post-dispatch 或后续 independent read-back 验证结果 | `PENDING -> SETTLED` |

在 reality-facing capability 出现之前，未授权的 HOLD/DENY 作为抽象 stuttering，不要求出现在投影 trace 中。

每个 reality-facing projection event 同时携带：

- effect id；
- proposal id；
- obligation id；
- target system；
- operation；
- stable request identity。

checker 会拒绝不连续 phase sequence，以及缺少 scope identity 的 reality-facing event。

## 已检查具体 trace

### 正常完成

三个 offboarding 外部 effect 通过真实 AIOS engine fixture 执行。

每个 effect 的投影都是：

[
PROPOSED 	o RESERVED 	o PENDING 	o SETTLED
]

三个 effect 全部 settled，AIOS case 达到 completion。

### Lost acknowledgement + independent read-back

第一笔 provider write 已发生，但 acknowledgement 丢失。

trace 先进入 `PENDING`；随后 independent read-back 在释放后续 effect 之前将同一 effect settled。第一笔逻辑 effect 不会被二次 dispatch。

reconciliation 后其余 effect 继续执行，全部 projected effect 最终进入 `SETTLED`。

### Outcome unknown 且无可用 read-back

第一笔 provider attempt 返回 ambiguous outcome，同时没有可用 independent observation。

projected trace 进入 `PENDING`，并在重复 AIOS reconciliation 中持续保持该状态。

底层 provider invocation 数始终为 1；原 effect unresolved 时不会出现第二次 reality-facing dispatch。

## Refinement 主张

对于上述三个已检查 fixture：

[
pi(	au_{mathrm{AIOS+gate}})
in
operatorname{Trace}(K_{mathrm{formal-v1}})
]

这里仅针对被表示的 phase relation 与 scope identity。

这是有限具体 trace 的已测试关系，不是对所有 AIOS execution 的普遍量化。

## 显式假设

该 refinement 主张依赖：

1. 所有 covered offboarding provider call 都通过 `BAAGatedAIOSProvider`；
2. 被检查执行中的 AIOS effect identity、obligation identity、authority epoch、target、operation 与 request identity 稳定；
3. gate 的 independent observation 是解决 effect ambiguity 的 observation channel；
4. abstract effect pending 时，没有未被 instrument 的路径修改同一个外部 effect；
5. 测试固定的 AIOS 语义与所讨论部署接口一致。

任一条件失效时，本次 tested refinement relation 不能推出部署行为。

## v1 尚未覆盖

当前 refinement check 还没有证明：

- deployed World Runtime HTTP boundary 的 complete mediation；
- 所有 runtime authorization/resource/version binding 都 refinement 到 formal capability tuple；
- concurrency refinement；
- BAA/AIOS 独立持久化状态下的 crash/restart refinement；
- Keycloak/Odoo connector refinement；
- exposure/risk-budget refinement，因为当前 offboarding gate 使用 obligation-level unresolved bound，而不是 generic formal risk ledger；
- verified product state 到全部现实损害维度的 semantic bridge。

所以下一结构步骤应扩展到固定 World Runtime invocation/reconciliation record，而不是继续增加抽象 phase。
