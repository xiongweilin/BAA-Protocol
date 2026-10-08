# P2 只读维护：原始证据归档资格校验修订 v1

> [English](p2-readonly-maintenance-source-qualification-v1.md) | 简体中文

## 状态

这是**已冻结五窗口 P2 真实模型回放在采样前的来源校验强化**。不修改原有工作负载、模型提示、工具 schema、自检／audit／BAA 三制度、C0/C1/C2 轮次预算、交付与注意力风险核算或预注册成功规则。[P2 原始协议](p2-readonly-maintenance-model-v1.zh-CN.md) 继续保持 canonical。

原先工作负载保存了 GitHub Actions artifact 和 SHA-256 等来源元数据，但模型采样程序**没有实际检查原始压缩包字节**。因此，人为修改工作负载中的产品读数而保留旧来源标签，仍可能进入模型调用。这是仪器资格问题，不代表原 P7 观测有误。

## 模型采样前必须执行的校验

模型程序现要求：

`--source-zip <原始-p7-actions-archive.zip>`

原始档案缺失或 SHA 不符时，**第一次模型调用之前**即拒绝。仅做来源资格验证可执行：

```bash
python scripts/run_p2_readonly_maintenance_model.py \
  --source-zip /path/to/original-actions-11526016609.zip \
  --qualify-source-only \
  --output /path/to/source-qualification.json
```

固定且验证的对象包括：

- [AIOS P7 run 37720702388](https://github.com/xiongweilin/aios/actions/runs/37720702388)，artifact **11526016609**，ZIP SHA-256 `dfafd340bd3a10f2c4768c578b908cad1756e6f1009e3c5b153d49046ec16b60`。
- 实验源 HEAD `d8439c17248b88e0fdd971477f3a28fb151c6e76`，独立的 PR checkout SHA `2288420643148fd8a2aa56de8ba6f9def0cbe1cd`，Actions run ID 和 attempt。
- 实际隔离 Keycloak 暂停和中断被观测到、成功 unpause、没有业务 effect，以及 `verified_recovered_evidence` 参考结果。
- 原始 16 条读数、每轮四个 source 的顺序、覆盖的 capability fingerprint（映射为固定的符号 ID），和合格的正常／观测端传输故障／观测端契约异常案例。
- 五个现有工作负载窗口的**逐项对应**：M01 两轮正常；M02–M04 来源于同一次真实服务中断的不同证据前缀及重新取证后缀；M05 来源于观测端模拟契约异常。

**重要反例：** 单纯的 Keycloak 观测端传输故障与真实隔离 Keycloak 暂停，在归一化 GET 状态序列上**不可区分**。只凭这些 readback 不能识别真实故障成因。该测试属于**负向语义可识别性检查**，不能写成架构泛化的正证据。

来源校验不访问真实产品，也不产生模型调用。新增 `--qualify-source-only` 只输出证据完整性结论；正式模型结果则新增 `source_qualification` 字段，不增加模型提案，也不重定义研究结果。

## 未能建立的保证

这只证明**冻结的 P2 证据投影与固定 Actions ZIP 一致**，不证明全部传感器的真实语义、不可见状态的独立见证、连续可用性、事故因果成因、Agent 有效工作或 BAA 委托增益。五个窗口相互关联，来源于短时一次性隔离环境。模型采样、真实注意力、assurance 成本和部署权限都必须另行取得证据。

如果 GitHub artifact 到期或缺失，**不能**重造 ZIP 或改写摘要以取得正结果；应如实封存来源资格失败，保持 P2 模型采样未合格。
