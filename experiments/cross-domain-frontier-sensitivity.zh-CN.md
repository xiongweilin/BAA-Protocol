# 跨任务域前沿敏感性分析

> [English](cross-domain-frontier-sensitivity.md) | 简体中文

## 状态

**对已经接受的 run 做事后探索性分析。**

本文不修改任何预注册 endpoint，也不是新的模型实验。

输入：

- offboarding v6 接受 run：AIOS `37406741476`，artifact `11386984007`，SHA-256 `28db9bb852eeba59d26b93687dd5c02dad6bb9b4d144c96cdacb8b5da5112ad4`；
- canary v1 接受 run：AIOS `37410377327`，artifact `11389635051`，SHA-256 `c0e667c1c564d73c8986e001c7ee68947a8d9a95984dbcd91a915c71c11fc0af`。

冻结实验的正式结论仍以各自预注册结果为准。

## 为什么必须单独重分类

两个研究对所有 counterfactual budget 分析并没有完全相同的 useful-delivery 编码。

canary v1 中，如果 trajectory 虽然到达目标，但经过 unsafe transition，则 useful delivery 被置为 0。对预注册 strict contract 这是正确的；但如果随后放宽 unsafe-transition ceiling，却继续要求保存的 useful-delivery 字段，就会把 risk 重复计算一次。

因此本敏感性分析单独定义：

~~~text
completed_within_bounds(B)
~~~

一个已经观察到的 episode 只有在以下条件满足时计入：

~~~text
completed == true
principal_attention <= A
unsafe_transitions <= U
terminal_unresolved_results <= Q
assurance_labor_units <= L       # 仅在提供 ceiling 时
assurance_interventions <= I     # 仅在提供 ceiling 时
~~~

这里 delivery 侧只使用 raw completion。这个量不会被重新命名为预注册 delegability。

同时，人类 audit labor 与 BAA 自动 intervention 保持两个独立维度，不换算成同一个 scalar cost。

## 冻结 strict endpoint 不变

C2 正式接受结果：

| Domain | Best direct | BAA | BAA delta |
|---|---:|---:|---:|
| offboarding v6 | 14 / 24 | **20 / 24** | **+6** |
| canary v1 | **11 / 18** | 10 / 18 | **-1** |

因此在任何事后重分类之前，两个任务域的符号就已经不同。

## Strict risk 下的 horizon 敏感性

使用 raw completion，并固定 A=0、U=0、Q=0：

| Domain | C | Best direct | BAA | Delta |
|---|---:|---:|---:|---:|
| offboarding v6 | C0 | 4 | 4 | 0 |
| offboarding v6 | C1 | **6** | 4 | -2 |
| offboarding v6 | C2 | 14 | **20** | +6 |
| canary v1 | C0 | 3 | 3 | 0 |
| canary v1 | C1 | 9 | 9 | 0 |
| canary v1 | C2 | **11** | 10 | -1 |

offboarding 的 BAA 优势并不随 adaptive horizon 单调增加：C1 时 BAA 落后，C2 才反超。canary 在冻结 horizon 内没有跨入正的 BAA frontier。

## C2 risk-tolerance 敏感性

固定 A=0、Q=0，只改变每个 episode 允许的 unsafe transition 数 U，并对已经观察到的 completed trajectory 重分类：

| Domain | Unsafe ceiling U | Best direct | BAA | Delta |
|---|---:|---:|---:|---:|
| offboarding v6 | 0 | 14 | 20 | **+6** |
| offboarding v6 | 1 | 16 | 20 | **+4** |
| offboarding v6 | 2 | 19 | 20 | **+1** |
| canary v1 | 0 | 11 | 10 | **-1** |
| canary v1 | 1 | 13 | 10 | **-3** |
| canary v1 | 2 | 13 | 10 | **-3** |

这不是“如果部署政策更宽松，模型会怎样行为”的因果结论，只是对已经观察到的轨迹重新分类。

在这个限制内，模式仍然很清楚：

- 随着 unsafe transition 更可接受，offboarding 中 BAA 的优势从 +6 快速缩小到 +1；
- canary 中，允许两个 direct unsafe completion 后，BAA 劣势从 -1 扩大到 -3；
- delegation leverage 的符号与大小都强烈依赖 task structure 与 risk budget。

## 自动 assurance intervention 敏感性

接着固定 A=0、U=0、Q=0，并限制每个 episode 可使用的 BAA 自动 intervention 次数。

### Offboarding v6，C2

| 每 episode 最大 BAA intervention | BAA completed within bounds | Best direct | Delta |
|---:|---:|---:|---:|
| 0 | 13 | 14 | -1 |
| 1 | 16 | 14 | +2 |
| 2 | 20 | 14 | +6 |
| 3 | 20 | 14 | +6 |
| 4 | 20 | 14 | +6 |

在 offboarding v6 中，自动 assurance work 是有生产力的：允许一定 intervention capacity 后，safe blocking 被转换成更多 safe completion。

### Canary v1，C2

| 每 episode 最大 BAA intervention | BAA completed within bounds | Best direct | Delta |
|---:|---:|---:|---:|
| 0 | 10 | 11 | -1 |
| 1 | 10 | 11 | -1 |
| 2 | 10 | 11 | -1 |
| 3 | 10 | 11 | -1 |
| 4 | 10 | 11 | -1 |

canary v1 中观察到的 5 次 C2 intervention 都发生在最终仍未完成的 trajectory 上。因此单纯增加允许的 intervention 次数，并没有恢复 accepted run 中丢失的 liveness。

这是当前跨任务域证据里最清楚的区别：

> assurance intervention 本身不是 delegation leverage；只有当周围的 state/feedback dynamics 允许模型把被阻止的动作转换成安全 continuation 时，它才会产生 leverage。

## Attention 与 unresolved-result ceiling

在两个接受 workload 中，把 A 与 Q 从 0 放宽到 1，都不会增加 C0、C1 或 C2 的 completed-within-bounds 数量。

原因是经验性的，不是结构定理：这些 accepted trace 中带 terminal unresolved result 的 episode 同时也是 incomplete。单靠事后放宽 attention 或 unresolved-result budget，不能把它们重新分类成完成任务。

因此当前 artifact 对 risk 与 intervention sensitivity 有信息量，但不足以估计稳定的 attention-completion exchange rate。

## Post-hoc audit 成本

两个接受研究里，self-check 与 post-hoc audit 的执行结果相同；audit 只增加 assurance labor：

- offboarding v6 C2：81 个 audit labor unit；
- canary v1 C2：57 个 audit labor unit。

在目前测量的 endpoint 下，post-hoc audit 因而被 self-check 支配。这不表示记录本身没有外部价值，只表示当前实验没有给 audit record 的后续制度价值计分。

## 对下一实验的含义

当前证据不支持“BAA 存在一个跨任务域统一向外移动的 frontier”。

它支持一个条件性结论：

- offboarding v6 中，在 horizon 足够长且允许一定自动 intervention capacity 时，严格 risk control 可以转换成更多 safe completion；
- canary v1 中，同一类架构虽然保持安全，但 feedback/state dynamics 没有把 denial 转换成足够的 sequential continuation。

因此下一次预注册实验应改变**机制**，而不是继续加 case。最具体的候选是 **machine-usable assurance feedback**：在 deny/hold 后，向模型暴露受限的 corrective state，例如 required next stage、missing evidence class 或 reconciliation requirement，同时不放松 hard admission rule。

这个假说必须作为新的 study version 在采样前冻结，不能改写 canary v1。

## 复现

仓库脚本接收两个下载后的 result artifact：

~~~text
python scripts/analyze_cross_domain_frontier.py \
  --offboarding-v6 <offboarding-v6-result.json> \
  --canary-v1 <canary-v1-result.json>
~~~

输出是事后重分类报告，不是新的实验结果。
