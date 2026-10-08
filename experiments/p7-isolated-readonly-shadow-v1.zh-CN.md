# P7 隔离只读 Shadow——首轮基线

> [English](p7-isolated-readonly-shadow-v1.md) | 简体中文

## 当前证据等级

2026 年 10 月 8 日完成了一轮隔离 AIOS 环境中的短时只读观测。该结果属于系统监控仪器验证，不构成长期可靠性、委托价值或部署接受保证。

## 来源与版本

- AIOS [PR #41](https://github.com/xiongweilin/aios/pull/41) 合并提交：`964a8b78119bd9e9f005b041a11a6919fee3086f`。
- 通过验收的源分支版本：`94ee3bf740ca5eb2af7b748f2b57516dbc48ee6e`。
- [Actions 37714124440](https://github.com/xiongweilin/aios/actions/runs/37714124440)，artifact `11523113319`，SHA-256：`b8e16a2dca58e573f87519c0ba2324c28cdfdd7e7bd115461210bff30adb0167`。
- Artifact 记录的 PR checkout 版本：`bd32774b45dfbd1f0bc5c812108118aab81db0ea`。

## 实际观察

初始化隔离 Odoo、Keycloak、World Runtime 后，进行了 40 秒的 GET 只读检查。

| 项目 | 结果 |
|---|---|
| 完整轮次 | 9 |
| 总检查次数 | 36 |
| 四类目标的非 OK 次数 | 0 |
| Capability 契约 fingerprint 数 | 1 |
| 观察到的契约变化 | 0 |

检查对象包括 World Runtime 健康与三种离职 capability 的声明属性、Keycloak realm 和 Odoo HTTP 入口。三个受覆盖 capability 在检查时均要求授权、资源绑定和版本绑定。一次性环境没有执行实际离职操作。

## 不能推出的结论

观察窗口只有 40 秒，不能据此断言全天可用性、故障恢复分布、并发正确性、长期 Agent 行为或真实工作交付。健康检查也不等于所有授权路径都已不可绕过。本次没有测 principal attention、assurance labor 或模型成本。

工作流支持手动选择 1、5、15 分钟的隔离演练，没有设置自动周期任务。进一步扩大到现实维护任务前，仍需事先确定权限、任务边界、故障处理、人工接管、预算和验收规则。

因此，P7 目前只获得**短时只读仪器验证**，没有取得长期生产委托的验收资格。
