# P3 隔离受保护资源探针——资格验证记录 v1

> [English](p3-protected-access-qualification-v1.md) | 简体中文

## 证据状态

**通过资格验证的隔离真实产品单时点访问探针**，并非连续时序损失观测，也不是风险因子校准。

原始 [P3 时序损失协议](p3-offboarding-temporal-outcome-v1.zh-CN.md) 保持不变。本文件只记录访问能力观察通道的资格条件；不修改 endpoint、实验处理、过渡期、horizon、模型假设或负结果规则。

## 固定执行版本与合格观测

- 执行仓库：`xiongweilin/aios`，PR [#38](https://github.com/xiongweilin/aios/pull/38)，合并提交 [`eb8cc19c92ea`](https://github.com/xiongweilin/aios/commit/eb8cc19c92ea61e414fbd7f342f2583f8304a0be)。
- 首次通过点探针资格验证的执行 HEAD：`978367d0f52c166286403ab996ef610bafabbd60`。
- 固定 BAA 参考观测器：`3ebd6e7b392d30063cd77d5015a3f2e288dfdb38`。
- 通过验证的 GitHub Actions [run 37710849397](https://github.com/xiongweilin/aios/actions/runs/37710849397)，artifact **11521698006**，归档摘要 `sha256:9ba4d277a335c64653cdc4af2ddb24cf6b1b60468946fbf42ae3985505f84fc1`。
- 环境：GitHub-hosted Ubuntu 一次性运行环境、隔离 Odoo、Keycloak、World Runtime 与仅绑定 loopback 的受保护资源；一个待撤权测试主体及一个保持不变的对照主体。
- 受保护资源使用与签发测试 token **相同的 issuer origin** 做 Keycloak 在线 introspection；证据不包含原始 token 或 client secret。

### 实际证实的结果

| 观测 | 目标测试主体 | 未撤权对照 |
|---|---|---|
| Offboarding 前 | **ALLOW** | **ALLOW** |
| BAA→AIOS→World Runtime 三个 effect 独立核验后 | **DENY** | **ALLOW** |

探针网络不可达时明确标记为 **UNKNOWN**，并非 `DENY`。AIOS 以授权方式完成测试离职，三类产品 effect 均通过外部核验。

这些结果仅验证该隔离环境下的**单时点受保护资源访问区分能力**，不能外推所有部署的授权通道。

## 资格失败记录不能消失

下列是**仪器／环境资格失败**，不是已测真实损失，不应从来源链中删去：

| Run | Artifact | 观察到的缺口 |
|---|---|---|
| [37709634277](https://github.com/xiongweilin/aios/actions/runs/37709634277) | 11520849286 | 启用的基线账号仍被拒绝，访问探针尚不合格 |
| [37710011839](https://github.com/xiongweilin/aios/actions/runs/37710011839) | 11521342891 | 隔离 client 的 audience mapper 单独不足以修复基线 |
| [37710502830](https://github.com/xiongweilin/aios/actions/runs/37710502830) | 11521687493 | host-origin introspection 为 active、UserInfo 为 200，但容器 alias origin 校验失败 |
| [37710849397](https://github.com/xiongweilin/aios/actions/runs/37710849397) | 11521698006 | 匹配 token issuer origin 后，以相同判据通过探针资格检查 |

以上修复只针对**探针接口／隔离运行环境**，不能被解释为新的因果对照实验或事后成功校准。

## 时序与语义保证边界

冻结的 `SNAPSHOT_ONLY` 参考计算给出了示意性 `[0,6]` **主体秒**，同时 `exact_duration_identified=false`；但外部时钟误差**尚未经独立资格验证**。因此 **`[0,6]` 不是已验证的现实持续时间区间或已校准损失界**，只是局部示意时钟假设下的参考计算输出。

两次甚至多次有效的点探针不能证明中间全程状态。token 可能在两次请求间某个未知时刻失效，还可能存在短暂恢复和未观察到的可访问状态。既有 `managed-subject-state-change-count-v1` 的单位也不同于主体秒，不能直接作为时序损失 penalty。

**P3 当前地位：** 一种隔离部署的访问能力点探针已合格；**尚未建立**时序连续性、外部时钟资格、跨 effect 竞争模型的识别或现实 `Y` 校准。offboarding risk-factor registry 保持为空。

## 下一个可区分证据

1. 在 effect 执行期间以独立调度记录目标／对照受保护资源的请求时间区间，保留所有 UNKNOWN。
2. 资格验证外部时钟来源、允许观测误差、产品事件／迁移证据；否则仅报告未观测时间的保守区间。
3. 预注册真正可以区分风险因子分组的干预条件与独立留出样本，然后只在授权隔离环境执行；点探针成功或密集轮询均不能直接识别 interaction penalty。
