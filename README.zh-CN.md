# BAA-Protocol

> [English](README.md) | 简体中文

**有界行动准入＋实验性条件安全策略合成。** 目标是在不信任模型对权限、外部效果和世界状态的自我声明的前提下，完成更多真正安全的工作。

## 新架构

    任务目标＋当前证据＋显式世界与操作模型
                ↓
      有界条件策略编译      [实验性]
                ↓
      独立策略结构检查      [实验性]
                ↓
      现有 BAA 实时准入     [强制]
                ↓
      精确权限凭证→受控执行
                ↓
      独立回读→对账／结算／重新打开

旧结构主要对模型已经提议的一个行动拒绝、保持或准入。新 [条件策略](spec/contingent-policy.zh-CN.md) 能在所有声明的可能世界里提前搜索安全行动和可信观测分支，在给定深度内优化最坏情形操作成本。未知外部效果仍包含所有可能后继，不盲目重发。预编译策略**不提供执行权限**；每一步仍需现有 World Runtime 实时授权和中介。

## 三条理论边界

1. **规范边界：**正确目标、权利、授权和取舍不会由规划器自动产生。
2. **认识边界：**模型可能遗漏危险状态，所谓权威来源可能延迟或错误。
3. **控制边界：**抽象安全策略不一定在真实部署中可执行、可观测或可恢复。

有限状态证明、模拟测试与隔离服务 E2E 都不等于生产保证。

## 实验已证实的结果和未证实的目标

| 证据 | 结果 | 尚未证实 |
| --- | --- | --- |
| [有限结构模型](formal/structural-guarantees-v1.zh-CN.md) | 584 状态、35,040 次抽象转移 | 全部实际执行接口安全 |
| [离职 v6](experiments/prospective-model-v6-result.zh-CN.md) | C2：20/24 对 14/24；但 C0 持平、C1 更差 | 各层统一优势与跨机制泛化 |
| [成本前沿](experiments/prospective-delegation-cost-frontier-v1-result.zh-CN.md) | C0/C1/C2 各 **0/30** 个严格安全成本单元正收益 | 广泛降低保障和注意力成本 |
| [隔离真实产品](formal/real-product-exposure-binding-v1.zh-CN.md) | 有限 Odoo/Keycloak 执行、回读及越权拒绝 | 生产租户验收 |
| **新条件规划器** | 分支算法、独立检查器和有限回归测试 | 相对于同等资源强基线的真实模型收益 |

历史实验保留冻结结论，不因新设计而事后修改。原始运行来源见 [证据索引](experiments/claim-evidence-index.zh-CN.md)，ZIP 原始证据与本地校验见 [来源记录](experiments/source-artifact-provenance-2026-10-10.zh-CN.md)。

## 代码和跨仓接口

- [条件策略合成／独立验证器](baa_protocol/contingent_policy.py)、[逆境世界测试](tests/test_contingent_policy.py)。
- 真实效果仍受 [原准入协议](spec/protocol.zh-CN.md)、[状态机](spec/state-machine.zh-CN.md)、[保证义务](spec/guarantees.zh-CN.md)约束。
- [AIOS 实验性执行边界](https://github.com/xiongweilin/aios/blob/main/src/domains/administrative_orchestrator/contingent_execution.py)只准备请求，不擅自执行外部写入。
- [guide 新理论主干](https://github.com/xiongweilin/guide/blob/main/minimal-derivation.zh-CN.md)、[Lean 条件性共同安全行动证明](https://github.com/xiongweilin/distinction-self-reference-lean/blob/main/DistinctionSelfReference/RobustAction.lean)。

原有跨仓 CI 保留当前主分支与固定版本的兼容性检查。新分支的 AIOS 配对集成还必须单独验证。

## 更强收益主张的准入条件

预先冻结新任务分布、同样具有主动规划／观察能力的强对照、C0/C1/C2 反馈窗口、独立安全判断、权限和成本预算，并完整记录失败、保持、未知结果以及人工／自动保障成本。只有实测结果才能表明新架构扩大了安全委托前沿。**本分支不预设 C0/C1/C2 全面领先。**

项目规范：[贡献](CONTRIBUTING.zh-CN.md)、[安全](SECURITY.zh-CN.md)、[许可](LICENSE)。
