# 主张与证据索引——2026-10-08

> [English](claim-evidence-index.md) | 简体中文

本文件只提供证据等级与导航，**不重新计算、不取代**已封存的实验。每项主张仍以原始文件中的版本、资格检查、证据来源和失败条件为准。

| 问题／主张 | 主要证据 | 当前证据地位 | 尚未建立 |
|---|---|---|---|
| 基本不闭包与局部充分性 | [guide](https://github.com/xiongweilin/guide)、[BAA 保证声明](../spec/guarantees.zh-CN.md) | 概念框架 | 普遍充分条件定理 |
| 有界行动的结构性约束 | [有限状态检查](../formal/structural-guarantees-v1.zh-CN.md)、[AIOS refinement](../formal/aios-refinement-v1.zh-CN.md) | 584 状态、35,040 抽象迁移；有限实现轨迹 refinement | 全部部署作用通道的完整 mediation |
| 产品执行授权／回读／恢复 | [真实产品验收](../formal/real-product-exposure-binding-v1.zh-CN.md)、[连接器 refinement](../formal/product-connector-refinement-v1.zh-CN.md) | 隔离 Odoo/Keycloak 现实效果边界证据 | 生产租户安全、全部效果 |
| Offboarding 真实模型委托价值 | [v6 结果](prospective-model-v6-result.zh-CN.md) | 冻结工作负载下 C2 aggregate +6 | 跨机制全面泛化 |
| Canary 证据恢复 × horizon | [v5 robustness](prospective-canary-v5-robustness-result.zh-CN.md) | aggregate interaction +1；仅 1/3 timing strata 为正 | 对 timing 稳健的 interaction |
| 前瞻委托成本前沿 | [成本前沿结果](prospective-delegation-cost-frontier-v1-result.zh-CN.md) | C0/C1/C2 的 strict-safe BAA-positive 均为 0/30；证据恢复有局部增益 | 普遍改善 attention-risk exchange rate |
| P2 真实模型维护先导 | [预注册回放协议](p2-readonly-maintenance-model-v1.zh-CN.md)、[冻结五窗口工作负载](p2_readonly_maintenance_v1.json) | **目前仅有协议与真实产品历史证据；真实模型采样尚未验收**；各制度共享初始采样和不可写沙箱 | 真实在线委托、独立 episode 随机化、实际 attention/assurance 成本与 BAA 因果增益 |
| P7 真实隔离进程中断 | [Keycloak 暂停／恢复预注册资格记录](p7-real-isolated-keycloak-outage-v1.zh-CN.md) | 两轮合格的可逆真实隔离服务中断，每轮 4 轮／16 次 GET，仅 Keycloak 不可达，解除暂停后两轮重新取证 | 自然故障恢复、MTTR 分布、Agent 自主价值或生产可靠性 |
| P7 只读维护诊断 | [冻结的三场景真实产品诊断资格验证](p7-readonly-maintenance-triage-v1.zh-CN.md) | 48 个位置、46 次真实 GET、2 次观测端模拟异常；正常／重新取证／升级处理均符合规则 | 真实 provider 故障恢复、Agent 交付、注意力风险增益或生产可靠性 |
| P7 隔离只读观测 | [40 秒基线](p7-isolated-readonly-shadow-v1.zh-CN.md) | 9 轮、36 次 GET 检查，未观察到服务中断或 capability 契约漂移 | 长期可靠性、实际恢复、部署接受 |
| P6 真实产品质量 | [四场景隔离基线](p6-real-product-quality-baseline-v1.zh-CN.md) | 四组通过验收的一次性 E2E 分段耗时及状态计数，每组仅一个 case；无采样溢出 | 生产 P95/P99 SLO、持续吞吐、assurance 成本与 principal attention |
| 冻结产品投影中的 exposure | [指标绑定](../formal/exposure-metric-binding-v1.zh-CN.md)、[产品验收](../formal/real-product-exposure-binding-v1.zh-CN.md) | 三类 effect 的单位指标，精确绑定枚举受管主体投影 | 全部现实损失与中间时序损害 |
| 联合风险因子与 interaction | [不可识别性负结果](../formal/joint-risk-identifiability-v1.zh-CN.md)、[绑定契约](../formal/joint-risk-binding-contract-v1.zh-CN.md) | **尚未识别**；offboarding registry 有意留空 | 已校准因子划分或 penalty |
| P3 受保护资源时序观测 | [点探针资格记录](p3-protected-access-qualification-v1.zh-CN.md)、[独立时间序列记录](p3-protected-access-timeline-v1.zh-CN.md)、[P3 协议](p3-offboarding-temporal-outcome-v1.zh-CN.md) | **隔离真实产品点／序列仪器已合格**：33 轮／66 次实际探针，目标 ALLOW→DENY、对照保持 ALLOW；有条件请求包络仅供描述 | HRIS/IAM/访问联合连续状态、已校准主体秒 `Y`、风险映射 |

## 主张等级不能互相替代

1. **有限结构保证**：仅在显式 `Omega` 及对应模型范围内成立。
2. **隔离真实产品集成**：仅支持明确版本和测试租户的效果／回读观察。
3. **通过资格检查的前瞻经验结论**：只适用于预注册工作负载与对应样本。
4. **仪器层验证**：接口、测试已存在，但尚无合格的独立现实损失测量。
5. **部署接受**：不能由以上证据自动推出。

CI 变绿只能说明代码与测试契约一致，不能升级现实保证。产品投影 exposure 与 P3 主体秒指标单位不同，绝不能在 `rho` 中直接替换。

## 最近的实验准入依赖

P3 已在**一个授权隔离 Keycloak/Odoo 环境**通过实际受保护资源单时点访问探针资格验证，包含未撤权对照和 UNKNOWN 网络失效测试，详见[资格验证记录](p3-protected-access-qualification-v1.zh-CN.md)。但两次相同轮询快照仍不足以精确计算主体秒。首次产品实验前，必须冻结环境版本、主体映射、事件／时钟来源及误差界、干预条件、共享影响域随机分配和负结果规则。

在获得独立联合损失观测及可区分竞争模型的预测之前，现有不可识别性负结果继续有效，不能填充 risk-factor registry。

## 来源与可追溯性

本索引仅指向已封存的原始记录，不替代其中的 run id、SHA-256、artifact id、资格说明或 CI 记录。
