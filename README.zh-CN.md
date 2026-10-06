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

- [domains/employee-offboarding.zh-CN.md](domains/employee-offboarding.zh-CN.md) —— 任务域边界、假设、不变量与实验。
- [spec/protocol.zh-CN.md](spec/protocol.zh-CN.md) —— 准入与执行协议。
- [spec/guarantees.zh-CN.md](spec/guarantees.zh-CN.md) —— 证明义务与声明语言。
- [spec/state-machine.zh-CN.md](spec/state-machine.zh-CN.md) —— 协议状态语义。
- [spec/vsar.zh-CN.md](spec/vsar.zh-CN.md) —— 版本化充分性保证记录（VSAR）。
- [experiments/design.zh-CN.md](experiments/design.zh-CN.md) —— 可证伪实验设计。
- [experiments/prospective-model-protocol.zh-CN.md](experiments/prospective-model-protocol.zh-CN.md) — 前瞻真实模型研究的预注册协议。
- [experiments/prospective-model-result.zh-CN.md](experiments/prospective-model-result.zh-CN.md) —— 第一轮接受的真实模型结果与零结果解释。
- [experiments/delegation-frontier-baseline.zh-CN.md](experiments/delegation-frontier-baseline.zh-CN.md) —— 第一版共同预算确定性委托前沿。
- [experiments/status.zh-CN.md](experiments/status.zh-CN.md) —— 当前证据层级与阶段边界。
- [baa_protocol/model.py](baa_protocol/model.py) —— 通用参考模型。
- [baa_protocol/offboarding.py](baa_protocol/offboarding.py) —— 员工离职内核。
- [baa_protocol/experiment.py](baa_protocol/experiment.py) —— 三制度 episode harness。
- [baa_protocol/aios_adapter.py](baa_protocol/aios_adapter.py) —— AIOS 到 BAA 的薄映射层。
- [integration/README.zh-CN.md](integration/README.zh-CN.md) —— 当前 AIOS 集成边界与剩余声明。
- [integration/test_aios_offboarding_contract.py](integration/test_aios_offboarding_contract.py) —— 固定 AIOS 兼容性检查。
- [integration/aios_gate.py](integration/aios_gate.py) —— 位于真实 AIOS EffectProvider 边界的 BAA gate。
- [integration/test_aios_runtime_gate.py](integration/test_aios_runtime_gate.py) —— 真实 AIOS 离职执行引擎 gate 测试。
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
- AIOS workflow run <code>37393917221</code>：接受的 <code>prospective-offboarding-v1</code> 预注册真实模型比较；self-check、post-hoc audit 与 BAA 在 C0/C1/C2 都是 6/7 delegable。这是保留的 delegation-frontier expansion 零结果，不是 BAA 优势证据。

这些结果**不**建立生产租户安全、生产凭证/基础设施隔离、一般无人值守自治安全、真实世界失败概率或 production delegation leverage。第一轮有限真实模型比较明确没有显示 delegation-frontier expansion。第二轮预注册研究未通过 model-evidence qualification，因此没有可接受的 frontier 结果。

详见 [experiments/status.zh-CN.md](experiments/status.zh-CN.md)。

## 项目规范

参见 [贡献指南](CONTRIBUTING.zh-CN.md)、[行为准则](CODE_OF_CONDUCT.zh-CN.md)、[安全策略](SECURITY.zh-CN.md) 与 [MIT License](LICENSE)。
