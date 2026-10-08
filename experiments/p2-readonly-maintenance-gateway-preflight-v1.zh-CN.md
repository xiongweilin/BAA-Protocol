# P2 只读维护真实模型先导——首次 Gateway 资格失败

> [English](p2-readonly-maintenance-gateway-preflight-v1.md) | 简体中文

**证据状态：模型采样前的基础设施／接口资格失败，没有模型结果，也没有委托价值结论。**

## 固定来源与实际过程

既有 [P2 五窗口预注册协议](p2-readonly-maintenance-model-v1.zh-CN.md) 和 P7 产品读数未因这次失败而更改。

- AIOS 实验 [PR #44](https://github.com/xiongweilin/aios/pull/44)，源 HEAD `0a1c14219ec62e17cd1f3b274053c61b29f5f92a`。
- 自托管 Windows 真实模型 [Actions run 37722950723](https://github.com/xiongweilin/aios/actions/runs/37722950723)：**失败**。
- Workflow 已完成代码 checkout、Python 准备、冻结工作负载和模型接口离线测试；接下来查询已有本机 gateway 的 `http://127.0.0.1:4101/v1/models` 时，`Invoke-RestMethod` 返回**连接被拒绝**。程序尚未进入模型采样步骤。
- 本轮**实际模型提案调用 0 次**。没有三制度结果、可用模型采样、因果委托价值估计、现实维护交付、新产品 effect 或模型输出费用证据。
- 本机 gateway 此时不可连接，并不证明具体模型缺席于一个正常工作的 catalog，也不能证明 BAA/P2 约束失效。能确认的失败类别仅为**请求边界上的 gateway 不可用**，日志不足以识别根因。

原 PR #44 的工作流在分支 push 时自动触发，未合并；为避免重复工作流及意外再次采样，[AIOS PR #44](https://github.com/xiongweilin/aios/pull/44) 已关闭。[AIOS PR #45](https://github.com/xiongweilin/aios/pull/45) 已以 `0f5d05212b72ecba8258d1cfe0bf33d9d9eaabcd` 合并，成为 canonical 接口：**只有手动触发并明确批准有限模型开销后才会调用模型**。

当前模型仪器固定 BAA `82370d7991eea9c288126610594a208efff06baa`；运行前必须提供 P7 [run 37720702388](https://github.com/xiongweilin/aios/actions/runs/37720702388) 的原始 artifact **11526016609**、正确 SHA-256 和五窗口证据投影，不合格则不得采样。

## 下一步及不能宣称的结论

下一次**单独 opt-in** 应先确保获准的本机模型 gateway 已运行；如果接受有限模型费用，再手动运行 AIOS `BAA P2 Isolated Read-Only Maintenance Model Replay v1` 并选择 `approve_finite_model_sampling=yes`。

不能靠 branch push 自动重新尝试、虚构模型输出、修改冻结 workload、将真实 principal attention 记为零、宣布 BAA frontier 扩张或为绕过 gateway 不可用而接入生产 Keycloak/Odoo。

即使以后接口资格通过，结果也仅属于来源相关的归档只读证据**模型重放**；无法自动升级为前瞻随机 P2、真实组织注意力、P3 联合损失因子或 P7 部署授权的证据。
