# P3 隔离受保护资源访问时间序列——资格验证记录 v1

> [English](p3-protected-access-timeline-v1.md) | 简体中文

## 当前状态

**一条通过资格检查的隔离真实产品独立调度访问点探针时间序列**。这不等于 HRIS/IAM/访问联合状态的连续观测，不等于真实主体秒损失的校准，也不能推出一般因果效应或联合风险参数。

本记录继承冻结的 [P3 时序损失协议](p3-offboarding-temporal-outcome-v1.zh-CN.md) 和 [受保护资源点探针资格记录](p3-protected-access-qualification-v1.zh-CN.md)。访问判据、目标／对照角色及原有研究协议均未改变。

## 可复核来源

- AIOS [PR #39](https://github.com/xiongweilin/aios/pull/39)，合并提交 [`09a2b40241b2`](https://github.com/xiongweilin/aios/commit/09a2b40241b234e5d96c922226a4dc41c12e08f9)。
- 合格运行的源分支 HEAD：`1f5b6af1c6f79792a089ef06eae42a2eeb4b658d`。
- `provenance.json` 记录的 GitHub Actions PR checkout merge ref：`90ceacfa9a716b237f3c2e9aeed924977772b0ff`；它既不是源分支 HEAD，也不是后来 squash merge 的 main 提交。
- 固定的 BAA 仪器：`3ebd6e7b392d30063cd77d5015a3f2e288dfdb38`。
- 合格隔离实验：[run 37712215991](https://github.com/xiongweilin/aios/actions/runs/37712215991)，attempt 1；artifact **11522760649**，归档 `sha256:81c19f0574599f54df5836d4bc07fb921b1e34299e668f445ebee5850dbebcb0`。
- 环境为单次使用的 Keycloak/Odoo/World Runtime 测试实例和仅绑定 loopback 的实际受保护资源，不包含生产主体、租户或凭据。
- 全程复用目标账号原始 bearer token；未撤权账号作为对照。探针相对真实 AIOS engine 独立调度，但仍共享 Python runner 主机，不代表具有完全独立的物理或管理故障域。

## 实际资格结果

| 观测项目 | 结果 |
|---|---|
| AIOS 最终状态 | `completed` |
| BAA 覆盖、独立核验的真实产品 effect | 3 |
| 观测轮数 | 33 |
| 在线受保护资源访问观测总数 | 66 |
| 目标账号 ALLOW / DENY / UNKNOWN | 3 / 30 / 0 |
| 未撤权对照 ALLOW / DENY / UNKNOWN | 33 / 0 / 0 |
| 观察到的 DENY→ALLOW 逆转 | 0 |
| 采样容量耗尽 | 否 |
| 目标账号**有条件单次状态切换候选窗口宽度** | 0.204721406 秒 |
| 连续损失已识别 | **否** |

每次探针都保留本机**单调时钟**下的请求起止包络及用于描述的 wall-clock 时间戳。候选窗口从最后一次 `ALLOW` 请求开始到第一次 `DENY` 请求结束，不是现实权限状态变化的精确时间。

一次未观察到逆转的序列**不能证明**权限仅变化一次且不可逆。轮询之间的短暂重新授权、产品时钟误差和不可见状态仍然存在。冻结的 `SNAPSHOT_ONLY` 参考计算得到的示意性主体秒区间为 `[0,7]`，并且 `exact_duration_identified=false`，**外部时钟误差尚未合格验证**。不能将其作为真实世界已校准的损失区间。

## 仪器与 CI 过程

较早的 [run 37711849889](https://github.com/xiongweilin/aios/actions/runs/37711849889)，artifact **11522022515**，已观察到 32 轮合格目标／对照探针，条件性候选窗口为 0.17295116 秒；相关 CI 因 import lint 问题未获最终接受。随后仅修复离线测试 BAA 模块导入、Ruff import 规范，以及前后台采样轮次的串行化。PR #39 最终**六项**检查均通过。较早的 CI 与资格历史不能被重新归类为最终合格证据。

## 下一个科学准入条件

1. 获得合格的独立产品状态迁移日志和有界时钟误差模型；否则只能报告单时点序列和保守未知时段。
2. 建立跨系统联合状态的准确主体绑定与区间连续性证据；仅访问能力轮询无法识别预注册的联合时序违规积分。
3. 在真实实验前冻结能区分候选风险因子划分的干预设计与独立留出验证。如果没有充分证明从现有计数 exposure 到主体秒 `Y` 的单位映射，就**不能**估计 pairwise-min penalty 或填充 `OFFBOARDING_RISK_FACTOR_IDS_V1`。

这是**观测分辨率与执行可观测性的提升**，不是 BAA 委托前沿已扩张或现实联合损失已校准的证据。
