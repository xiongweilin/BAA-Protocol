# BAA-Protocol

> [English](README.md) | 简体中文

[![Tests](https://github.com/xiongweilin/BAA-Protocol/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/xiongweilin/BAA-Protocol/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/github/license/xiongweilin/BAA-Protocol)](LICENSE)

**有界行动准入协议（Bounded Action Admission Protocol）**

BAA-Protocol 研究：在注意力与风险约束固定的条件下，一个不可绕过的准入与执行协议，能否增加可用的委托工作量。

它不是一般性的安全声明。仓库明确提出、实现并尝试证伪一组有条件保证。

## 研究问题

在模型、任务分布和面向现实的接口相同的前提下，有界行动准入是否能扩大在固定委托人注意力预算与风险上限内可完成的任务集合？

这里把无人值守运行视为一种**委托结构属性**，而不是代理人自身的内在属性。

## 基本问题维度

1. **规范不闭包**——允许的结果、权衡与剩余裁量并不总是被完全决定。
2. **证据不闭包**——相关现实状态、效果与保证假设并不总能被可靠辨认。
3. **控制不闭包**——所需状态转移与约束并不总能被实现或持续维持。

自适应优化是一个会主动搜索既有缺口的**放大器**，而不是第四个基本类别。

## 协议

~~~text
Agent proposal
  -> admission: deny | hold | admit
  -> narrow capability
  -> constrained execution
  -> external observation / verification
  -> settlement, contraction, recovery, or reopen
~~~

准入依赖历史与联合状态：

~~~text
Admit(T_t | H_t, q_t, K) -> {deny, hold, admit}
~~~

协议显式处理组合效应、待定外部效果、时间、共享资源、部分可观测性和自适应代理。

## 保证类别

- **结构保证**——在显式假设下推导出的确定性或概率性声明。
- **经验可靠性**——针对版本化部署策略，观测到的交付、失败、未知结果、干预与校准分布。
- **部署接受**——对剩余风险、注意力成本、授权与责任安排作出的规范性决定。

内核属性得到执行，并不自动证明预期的现实属性；还必须单独满足语义桥接义务。

任何实质性声明都应指明任务域、保证时域、精确轨迹属性、假设集合、自适应代理类别、环境类别，以及概率界是证明得到还是经验估计。

## 主实验

在 episode 或共享影响域层面比较：

1. 代理自检；
2. 代理 + 外部记录 / 事后审计；
3. 代理 + 不可绕过的准入、窄能力、受约束执行、验证与暴露控制。

核心问题：

> 在共同的注意力预算 A 与风险上限 R 下，BAA 是否提高有用交付或扩大可委托任务集合？当自适应攻击能力提高时，这种增益是否仍然存在？

安全与交付必须分开报告。

## 第一个具体任务域

第一个任务域是**员工离职（employee offboarding）**，来自以下固定 AIOS 快照：

~~~text
xiongweilin/aios@87f24f32a01c67a9246fc3cb127517c80798e169
~~~

兼容性 CI 检查：

- AIOS 离职策略的效果集合；
- 从 AIOS 推导出的外部义务；
- 现实侧后置条件；
- World Runtime capability 名称；
- BAA 对映射后的 AIOS 义务的执行。

兼容性通过仅表示 BAA 映射与这个固定 AIOS contract surface 相匹配。它**不**认证生产 AIOS、HRIS、IAM 或语义桥。

## 仓库结构

- [domains/employee-offboarding.zh-CN.md](domains/employee-offboarding.zh-CN.md) —— 第一任务域边界、假设、不变量与实验。
- [domains/canary-release-promotion.zh-CN.md](domains/canary-release-promotion.zh-CN.md) —— 第二任务域：带 evidence gate 与 rollback 的渐进式流量敞口。
- [spec/protocol.zh-CN.md](spec/protocol.zh-CN.md) —— 准入与执行协议。
- [spec/guarantees.zh-CN.md](spec/guarantees.zh-CN.md) —— 证明义务与声明语言。
- [spec/state-machine.zh-CN.md](spec/state-machine.zh-CN.md) —— 协议状态语义。
- [spec/vsar.zh-CN.md](spec/vsar.zh-CN.md) —— 版本化充分性保证记录（VSAR）。
- [experiments/design.zh-CN.md](experiments/design.zh-CN.md) —— 可证伪实验设计。
- [experiments/prospective-model-protocol.zh-CN.md](experiments/prospective-model-protocol.zh-CN.md) — 前瞻真实模型研究的预注册协议。
- [experiments/prospective-model-result.zh-CN.md](experiments/prospective-model-result.zh-CN.md) —— v1 接受的真实模型零结果。
- [experiments/prospective-model-v2-result.zh-CN.md](experiments/prospective-model-v2-result.zh-CN.md) —— v2 qualification failure。
- [experiments/prospective-model-v3-result.zh-CN.md](experiments/prospective-model-v3-result.zh-CN.md) —— v3 structured-output qualification failure 与 forced-function capability probe。
- [experiments/prospective-model-v4-result.zh-CN.md](experiments/prospective-model-v4-result.zh-CN.md) —— 通过资格检查的 forced-function v4 比较。
- [experiments/prospective-model-v5-protocol.zh-CN.md](experiments/prospective-model-v5-protocol.zh-CN.md) —— 预注册的 recovery/liveness follow-up。
- [experiments/prospective-model-v5-result.zh-CN.md](experiments/prospective-model-v5-result.zh-CN.md) —— 在预注册 recovery event 下通过资格检查的有限 delegation-frontier expansion。
- [experiments/prospective-model-v6-protocol.zh-CN.md](experiments/prospective-model-v6-protocol.zh-CN.md) —— 预注册的 24-episode 前瞻泛化研究。
- [experiments/prospective-model-v6-result.zh-CN.md](experiments/prospective-model-v6-result.zh-CN.md) —— 通过资格检查的 C2 aggregate frontier +6；预注册 evidence-refresh 跨机制泛化标准未满足。
- [experiments/prospective-canary-v1-protocol.zh-CN.md](experiments/prospective-canary-v1-protocol.zh-CN.md) —— 第二 BAA 任务域的首个真实模型研究预注册。
- [experiments/prospective-canary-v1-result.zh-CN.md](experiments/prospective-canary-v1-result.zh-CN.md) —— 通过资格检查的第二域结果：C2 Delta = -1，BAA unsafe=0，未出现跨域 frontier expansion。
- [experiments/prospective-canary-v2-feedback-protocol.zh-CN.md](experiments/prospective-canary-v2-feedback-protocol.zh-CN.md) —— 预注册 assurance-feedback 质量 × adaptive horizon 的机制研究。
- [experiments/prospective-canary-v2-feedback-result.zh-CN.md](experiments/prospective-canary-v2-feedback-result.zh-CN.md) —— 通过资格检查的零 feedback/horizon 结果：H4/H8 stale-route 均保持 1/3，unsafe=0。
- [experiments/prospective-canary-v3-evidence-protocol.zh-CN.md](experiments/prospective-canary-v3-evidence-protocol.zh-CN.md) —— 预注册 H4 evidence-reacquisition 机制研究；retention-only 草案在任何 v3 采样前已被取代。
- [experiments/prospective-canary-v3-evidence-result.zh-CN.md](experiments/prospective-canary-v3-evidence-result.zh-CN.md) —— 通过资格检查的 H4 frontier 零结果；同时有一个 stale-evidence hold 到安全 verified sequential transition 的因果过程级修复。
- [experiments/prospective-canary-v4-evidence-horizon-protocol.zh-CN.md](experiments/prospective-canary-v4-evidence-horizon-protocol.zh-CN.md) —— 预注册 2×2 evidence-recovery × H4/H8 interaction study。
- [experiments/prospective-canary-v4-evidence-horizon-result.zh-CN.md](experiments/prospective-canary-v4-evidence-horizon-result.zh-CN.md) —— 通过资格检查的正 interaction：stale-route contrast 从 H4 的 0 增至 H8 的 +1，四个 cell unsafe 均为 0。
- [experiments/prospective-canary-v5-robustness-protocol.zh-CN.md](experiments/prospective-canary-v5-robustness-protocol.zh-CN.md) —— 预注册 24-episode robustness study，workload 由冻结参数网格生成。
- [experiments/prospective-canary-v5-robustness-result.zh-CN.md](experiments/prospective-canary-v5-robustness-result.zh-CN.md) —— 通过资格检查的混合 robustness 结果：aggregate interaction=+1，但仅 1/3 预注册 timing stratum 为正，因此 strong robustness criterion 未满足。
- [experiments/delegation-frontier-baseline.zh-CN.md](experiments/delegation-frontier-baseline.zh-CN.md) —— 第一版共同预算确定性委托前沿。
- [experiments/delegation-cost-frontier-v1-protocol.zh-CN.md](experiments/delegation-cost-frontier-v1-protocol.zh-CN.md) —— 基于已接受真实模型 trace 的冻结回顾性成本前沿 accounting contract。
- [experiments/delegation-cost-frontier-v1-baseline.zh-CN.md](experiments/delegation-cost-frontier-v1-baseline.zh-CN.md) —— 从 offboarding v6 与 canary v5 得到的 attention/risk/assurance 成本面。
- [experiments/prospective-delegation-cost-frontier-v1-protocol.zh-CN.md](experiments/prospective-delegation-cost-frontier-v1-protocol.zh-CN.md) —— 在新的 24-episode 跨机制 canary workload 上预注册的前瞻 cost-frontier 研究。
- [experiments/prospective-delegation-cost-frontier-v1-result.zh-CN.md](experiments/prospective-delegation-cost-frontier-v1-result.zh-CN.md) —— 通过 qualification 的“架构零结果 / evidence-recovery 正结果”前瞻成本前沿。
- [experiments/prospective-delegation-cost-frontier-v1-result.json](experiments/prospective-delegation-cost-frontier-v1-result.json) —— 封存的机器可读 endpoint 与 provenance。
- [experiments/p7-readonly-maintenance-triage-v1.zh-CN.md](experiments/p7-readonly-maintenance-triage-v1.zh-CN.md) —— 隔离真实产品只读维护诊断及证据恢复／升级机制；不宣称 Agent 委托增益。
- [experiments/p7-isolated-readonly-shadow-v1.zh-CN.md](experiments/p7-isolated-readonly-shadow-v1.zh-CN.md) —— 隔离只读运行观测基线。
- [experiments/p6-real-product-quality-baseline-v1.zh-CN.md](experiments/p6-real-product-quality-baseline-v1.zh-CN.md) —— P6 隔离真实产品四场景分阶段质量测量；仅描述性，不构成 SLO 验收。
- [experiments/p3-protected-access-timeline-v1.zh-CN.md](experiments/p3-protected-access-timeline-v1.zh-CN.md) —— 隔离受保护资源的 33 轮时间序列及有条件 0.205 秒请求包络；未识别连续损失。
- [experiments/p3-protected-access-qualification-v1.zh-CN.md](experiments/p3-protected-access-qualification-v1.zh-CN.md) —— Keycloak 隔离受保护资源点探针资格结果，保留三次仪器失败；不构成连续损失证据。
- [experiments/p3-offboarding-temporal-outcome-v1.zh-CN.md](experiments/p3-offboarding-temporal-outcome-v1.zh-CN.md) —— P3 主体秒损失观测及可识别性预注册门槛（仅仪器测试，未进行产品校准）。
- [baa_protocol/temporal_outcome.py](baa_protocol/temporal_outcome.py) —— 部分可观测、时钟不确定条件下的区间损失上下界。
- [baa_protocol/temporal_collector.py](baa_protocol/temporal_collector.py) —— 独立只读快照采集接口、访问探针及单时点资格检测。
- [experiments/claim-evidence-index.zh-CN.md](experiments/claim-evidence-index.zh-CN.md) —— 证据等级索引、封存研究导航及 P3 当前准入依赖。
- [experiments/status.zh-CN.md](experiments/status.zh-CN.md) —— 当前证据层级与阶段边界。
- [baa_protocol/model.py](baa_protocol/model.py) —— 通用参考模型。
- [baa_protocol/offboarding.py](baa_protocol/offboarding.py) —— 员工离职内核。
- [baa_protocol/experiment.py](baa_protocol/experiment.py) —— 三制度 episode harness。
- [baa_protocol/aios_adapter.py](baa_protocol/aios_adapter.py) —— AIOS 到 BAA 的薄映射层。
- [integration/README.zh-CN.md](integration/README.zh-CN.md) —— 当前 AIOS 集成边界与剩余声明。
- [integration/test_aios_offboarding_contract.py](integration/test_aios_offboarding_contract.py) —— 固定 AIOS 兼容性检查。
- [integration/aios_gate.py](integration/aios_gate.py) —— 位于真实 AIOS EffectProvider 边界的 BAA gate。
- [integration/test_aios_runtime_gate.py](integration/test_aios_runtime_gate.py) —— 真实 AIOS 离职执行引擎 gate 测试。
- [formal/structural-guarantees-v1.zh-CN.md](formal/structural-guarantees-v1.zh-CN.md) —— 有限状态结构保证记录、显式假设与 refinement 边界。
- [formal/structural-model-v1-result.json](formal/structural-model-v1-result.json) —— 机器可读的穷举模型检查结果。
- [formal/aios-refinement-v1.zh-CN.md](formal/aios-refinement-v1.zh-CN.md) —— 从固定 AIOS offboarding gate 到 formal-v1 phase relation 的有限具体 trace refinement 检查。
- [formal/world-runtime-refinement-v1.zh-CN.md](formal/world-runtime-refinement-v1.zh-CN.md) —— 对固定 World Runtime 的 authorization/resource/version scope、durable effect identity、ambiguous-effect fencing 与 writer/verifier separation 的有限 refinement 检查。
- [formal/runtime-mediation-surface-v1.zh-CN.md](formal/runtime-mediation-surface-v1.zh-CN.md) —— 固定 public Runtime/adaptor provider-boundary 的五个 dispatch/reconciliation route inventory 与 authority guard 覆盖。
- [formal/product-connector-refinement-v1.zh-CN.md](formal/product-connector-refinement-v1.zh-CN.md) —— 三种 offboarding effect 从 Runtime request identity 到 Odoo/Keycloak durable request marker、reconciliation 与 product read-back 的有限 refinement。
- [formal/exposure-bridge-contract-v1.zh-CN.md](formal/exposure-bridge-contract-v1.zh-CN.md) —— 可证伪的 subject-scope exposure contract；当前 target-only product read-back 被明确判定为不足以建立 structural exposure-bound assumption。
- [formal/exposure-metric-binding-v1.zh-CN.md](formal/exposure-metric-binding-v1.zh-CN.md) —— 在任何 realized exposure 进入 settlement 前，对 observable `managed-subject-state-change-count-v1` metric 执行精确 proposal/metric/subject binding。
- [formal/real-product-exposure-binding-v1.zh-CN.md](formal/real-product-exposure-binding-v1.zh-CN.md) —— 临时 Keycloak/Odoo 上有限 E2E 证据：正常、恢复、未授权绕过场景下，admitted proposal 与 managed-subject measurement 的精确关联。
- [formal/joint-risk-binding-contract-v1.zh-CN.md](formal/joint-risk-binding-contract-v1.zh-CN.md) —— 精确 joint-risk term 绑定、统一计量单位和唯一 proposal 约束；offboarding risk factor 仍明确为未校准。
- [formal/joint-risk-identifiability-v1.zh-CN.md](formal/joint-risk-identifiability-v1.zh-CN.md) —— 可执行的负识别结果：三次单位产品敞口无法识别共享 risk factor 与交互 penalty；列出未来可区分校准实验的准入条件。
- [formal/offboarding-exposure-declarations-v1.zh-CN.md](formal/offboarding-exposure-declarations-v1.zh-CN.md) —— 将三类 BAA offboarding proposal 全部冻结到该 observable metric，unit exposure bound=1；measurement acceptance 与 risk calibration 仍保持为独立义务。
- [tests](tests) —— 回归测试与有限穷举检查。

## 与 guide、AIOS 的关系

[guide](https://github.com/xiongweilin/guide) 提供局部充分性、行动语义分离、修订与 reopen 等概念输入。

[AIOS](https://github.com/xiongweilin/aios) 提供第一个具体任务域的 contract surface。

BAA 不把充分性声明当作执行权限，也不重新定义 AIOS 语义。

## 状态

**当前是可执行参考原型：具备固定 AIOS 兼容性、执行引擎 gate、隔离网络恢复、真实产品 connector acceptance、组合真实产品 E2E acceptance，以及已完成的预注册真实模型比较。**

现有证据链包括：

- AIOS workflow run <code>37302243172</code>：隔离 HTTP/process/Docker 网络 acceptance，包括确认丢失、read-back outage 与未授权 Runtime 绕过；
- AIOS workflow runs <code>37306648690</code>、<code>37307582025</code>：对真实临时 Keycloak 与 Odoo 实例分别完成 connector acceptance，并分离 writer/verifier 身份；
- AIOS workflow run <code>37315551794</code>：完成一个 BAA -> AIOS -> World Runtime -> 真实临时 Keycloak/Odoo 的组合 episode，覆盖正常完成、lost-ack 恢复、read-back-outage 恢复与未授权 Runtime 绕过，并记录独立产品 read-back、持久化恢复状态转移、稳定逻辑 request identity 与经验证的外部完成；
- AIOS workflow run <code>37393917221</code>：接受的 v1 比较；三种 regime 在 C0/C1/C2 都是 6/7 delegable，保留为 frontier 零结果；
- v2 未通过 model-evidence qualification；v3 未通过 structured-output interface qualification；
- AIOS workflow run <code>37402587158</code>：通过资格检查的 forced-function v4 比较；三种 regime 在 C0/C1/C2 都是 9/12 delegable。direct/audit 出现 adaptive unsafe transition，而 BAA 保持 0 unsafe；这是 frontier 零结果，同时包含有限 safety-trajectory 正结果；
- AIOS workflow run <code>37404551022</code>：通过资格检查的 recovery-focused v5 比较。C0/C1 三种 regime 都是 9/12；C2 self-check/audit 仍为 9/12，而 BAA 达到 **12/12 delegable**，三者 aggregate useful delivery 都为 36，BAA unsafe transition 为 0，direct/audit 为 5。
- AIOS workflow run <code>37406741476</code>：首个完整通过资格检查的 v6 结果。冻结 24-episode workload 的 C2 中 self-check/audit 为 14/24，BAA 为 **20/24 delegable**，预注册 aggregate endpoint 为 Delta_C2 = +6。增益局限于 time_recovery（+4）与 readback_recovery（+2）；subject/authority evidence-refresh strata 没有 BAA-only gain，因此更强的预注册 cross-mechanism 泛化标准未满足。
- AIOS workflow run <code>37410377327</code>：首个完整通过资格检查的第二任务域 canary 结果。C2 self-check/audit 为 **11/18 delegable**，BAA 为 10/18，预注册 endpoint 为 Delta_C2 = -1。BAA unsafe transition 为 0，而两种 direct regime 各为 2；但 BAA 在 stale_route_refresh 中没有恢复足够 liveness，因此没有建立跨域 delegation-frontier expansion。
- AIOS workflow run <code>37412693511</code>：首个完整通过资格检查的 corrected canary v2 feedback/horizon 结果。H4 minimal/diagnostic/corrective aggregate 都为 10/18、stale-route 都为 1/3，因此预注册 feedback endpoint=0；diagnostic H8 stale-route 仍为 1/3，因此 horizon contrast 也为 0。所有 cell unsafe transition=0。
- AIOS workflow run <code>37438662474</code>：首个完整通过资格检查的 transport-amended canary v3 evidence-reacquisition 结果。两种 treatment 在 H4 都是 overall 11/18、stale-route 1/3 delegable，unsafe transition 均为 0；但 treated `stale-route-refresh-b` 在一次有界 evidence reacquisition 后，从精确 stale-evidence hold 推进到一个安全准入并 verified 的 sequential transition，随后因 H4 窗口结束而来不及完成剩余 stage。
- AIOS workflow run <code>37457822676</code>：首个完整通过资格检查的 canary v4 evidence×horizon 结果。预注册 stale-route interaction 为 **+1**：H4 两种 evidence policy 都是 0/3；H8 `no_reacquire` 仍为 0/3，而 `reacquire` 达到 **1/3**，aggregate 为 11/18 对 **12/18**；四个 cell unsafe transition 全为 0，H8 non-stale delegability 都为 11/15。
- AIOS workflow run <code>37466492295</code>：首个完整通过资格检查的 canary v5 robustness 结果，使用前瞻生成的 24-episode grid。aggregate recovery interaction 为 **+1**，control 未退化且 unsafe transition=0；但只有 mid timing stratum interaction 为正，因此预注册 strong robustness criterion **未满足**。
- AIOS workflow run <code>37620654622</code>：首个完整通过 qualification 的 prospective delegation cost-frontier 结果。C0/C1/C2 的 30 个 strict-safe assurance-cost cell 中，BAA positive cell 都是 0，全部与最佳 non-BAA regime 打平，因此 architecture persistence 为 **false**；但 BAA 将 C1/C2 unsafe transition 从 5→0、9→0。内部 evidence-recovery panel 在 H4/H8 都有 5/24 个正 cost cell，非目标 control mismatch 为 0；最小正阈值是 automatic-intervention ceiling=6 且 evidence-reacquisition ceiling=2。

这些结果**不**建立生产租户安全、生产凭证/基础设施隔离、一般无人值守自治安全、真实世界失败概率或总体层面的 production delegation leverage。v1 与 v4 保留 frontier 零结果；v2 与 v3 是 qualification failure。v5 首次给出通过资格检查的有限 delegation-frontier expansion。v6 在新的 offboarding prospective workload 上复现 aggregate expansion，但没有建立更强的 evidence-refresh 跨机制泛化声明。canary v1 随后给出首个通过资格检查的第二域反例：BAA 改善 safety trace，但由于 safe blocking 没有稳定恢复 liveness，C2 frontier endpoint 为负。canary v2 进一步显示：更丰富的机械 feedback 或单独增加到 H8 的 adaptive time 都没有修复冻结 stale-route endpoint。canary v3 显示 bounded current-route evidence reacquisition 可以在不削弱 gate 的情况下修复局部 stale-evidence transition，但没有扩大 H4 frontier。canary v4 随后得到预注册正 evidence×horizon interaction：一个 stale-route episode 只有在 reacquisition 与足够的 H8 remaining interaction time 结合时才安全完成。这是 BAA 内部 assurance mechanism 的结果，不是新的 BAA-versus-direct 比较。这些结果都不能用于估计 production frequency。

详见 [experiments/status.zh-CN.md](experiments/status.zh-CN.md)。

## 项目规范

参见 [贡献指南](CONTRIBUTING.zh-CN.md)、[行为准则](CODE_OF_CONDUCT.zh-CN.md)、[安全策略](SECURITY.zh-CN.md) 与 [MIT License](LICENSE)。
