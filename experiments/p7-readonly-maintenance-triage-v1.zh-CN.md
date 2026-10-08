# P7 隔离只读维护诊断——v1 资格验证

> [English](p7-readonly-maintenance-triage-v1.md) | 简体中文

**证据等级：** 在三个真实、一次性隔离服务上完成确定性只读维护诊断**仪器资格验证**。并非 Agent 委托制度比较、真实生产故障实验、真实 provider 故障注入、长期可靠性证明或 BAA attention-risk 增益。

## 预先冻结的实验

[AIOS 预注册规则](https://github.com/xiongweilin/aios/blob/02360374af3a61e7e63aee911a69a6fb50007ca7/tests/acceptance/baa_offboarding/P7-MAINTENANCE-TRIAGE.md) 在首个合格产品运行之前冻结三个 case，复用同一套隔离 Keycloak/Odoo/World Runtime。每个 case 按序采集四轮、每轮四个 GET 观测：Runtime 健康、三类受覆盖 capability 的安全契约、Keycloak realm 和 Odoo 根入口。

所有场景均不修改产品或用户权限。两种非正常情形**仅在本地观测通道**模拟异常，而不真的让身份系统宕机或改变 Runtime 合约。

| 场景 | 观测端干预 | 预注册结算规则 | 实测 |
|---|---|---|---|
| `normal` | 无 | `verified_stable` | 通过 |
| `observer_transport_gap` | 第 1 轮跳过 Keycloak GET，记录 `transport_unknown` | 连续两轮完整重新取证后才可 `verified_recovered_evidence` | 通过 |
| `observer_contract_anomaly` | 第 1 轮在本地将 Runtime 契约判为 `schema_unknown` | 即使之后正常也必须保持 `escalate_contract_or_authority` | 通过 |

规则拒绝缺失、重复、乱序的证据；第一轮不合格不得伪装健康；区分**遇到过 UNKNOWN**与**终态未解决**；契约或授权异常不得因后续一次正常读数自动关闭。

## 固定版本与分母

- AIOS [PR #42](https://github.com/xiongweilin/aios/pull/42)：源分支 HEAD `427002b8ddb26b5f54b6309ff40c6e60697d982b`，合并后 main `02360374af3a61e7e63aee911a69a6fb50007ca7`。
- 合格 [Actions run 37718555268](https://github.com/xiongweilin/aios/actions/runs/37718555268)，attempt 1。artifact **11524233834**，含 `maintenance-triage.json`、`observations.json` 和 `provenance.json`，归档 `sha256:abb424b07aa953724029ef4bf18ed962afe54d2e42317b37f0106d3915a04134`。
- artifact 记录的 PR checkout merge ref 为 `6bd401579aa1a9e7716461c95404e23ff071fc2f`，区别于源 HEAD 和事后的 squash merge。
- 维护诊断共有 **3×4×4=48 个观测位置**，其中 **46 次真实在线 GET + 2 次明确标注的观测端模拟异常**；逐场景是 `16+0`、`15+1`、`15+1`。
- 三项诊断均按冻结规则通过。三个有限 fixture 没有终态未解决；其中一项曾遭遇 UNKNOWN 并经过两轮完整重新取证，另一项即使后续样本正常仍保持升级处理。
- 同一运行中的原有 40 秒只读健康 shadow **另有 9 轮／36 次 GET**，未观察到故障、capability fingerprint 数为 1 且未漂移。不得与维护诊断的 48 个位置合并统计。
- PR #42 的七项 CI 均通过才合并。

早期运行 [37718407816](https://github.com/xiongweilin/aios/actions/runs/37718407816) 在启动隔离 `odoo-init` 时退出代码 2，**尚未进入维护诊断**，因此是测试环境资格失败，而不是维护任务正、负结果；同期两处 import lint 问题随后修复，但未修改决策判据。历史失败不被重新计为成功。

## 保证与费用边界

此处只是**只读维护诊断**，没有实际故障修复。获得 `verified_recovered_evidence` 只表明后两轮**被采样**的完整 GET 证据正常，不能证明发生真实 Keycloak 故障后的恢复。`escalate` 仅代表分类结果，未实际测量 principal attention、assurance labor、人工处理或修复动作。

本轮没有模型 Agent，没有 self-check/audit/BAA 三制度随机比较，没有修改实际权限，也没有测量真实联合损失 `Y`、risk factor、生产 P95/P99 SLO 或部署授权。P3 risk-factor registry 仍保持为空，P7 长期委托仍未获得资格。

下一步需另行明确授权**范围受限的只读 staging 身份和资源清单**，并冻结真实维护工单、独立结果核验、相同任务的 Agent 制度随机化、注意力／风险／交付／assurance 预算、故障处理及退出条件。个人 Windows 自托管 CI runner 的存在本身**不构成**合格 staging 权限边界。
