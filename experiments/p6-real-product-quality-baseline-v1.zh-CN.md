# P6 BAA/AIOS 真实产品质量——首轮描述性基线

> [English](p6-real-product-quality-baseline-v1.md) | 简体中文

**当前状态：** 隔离真实产品下的测量仪器已通过，样本非常少；**尚无 SLO 或长期运行可靠性结论**。

## 冻结的来源与适用范围

- AIOS [PR #40](https://github.com/xiongweilin/aios/pull/40)，合并提交 `deb0ed6a22424150ce62d5d9b7234a5be43e328c`；验收分支 HEAD `73e1e229a8e24cf0c3853057cbe8b7b5a71ad074`。
- 隔离真实产品四场景 [Actions run 37713555933](https://github.com/xiongweilin/aios/actions/runs/37713555933)：`normal`、`lost_ack`、`readback_outage`、`runtime_bypass`，**全部通过**。
- 真实产品 workflow 固定的 BAA 执行版为 `b3215d940cf7c9bd6b208ed5915eaa3c92ab10e3`；不能将其与后来归档证据的 BAA HEAD 混淆。
- 所有场景均在一次性 Keycloak/Odoo/World Runtime 环境内，不涉及生产身份。每组只有一个独立 case，不能据此估计生产故障概率。
- 每个场景 artifact 的 `evidence.json` 旁新增 `p6-quality.json`。

## 已实际测得的结果

| 隔离场景 | E2E 验收 | Engine drive | Gate execute | 独立 observe | 采集完整 |
|---|---|---:|---:|---:|---|
| normal | 通过 | 1 | 3 | 3 | 是 |
| lost_ack | 通过 | 2 | 5 | 3 | 是 |
| readback_outage | 通过 | 2 | 5 | 3 | 是 |
| runtime_bypass | 通过 | 0 | 0 | 0 | 是 |

bypass 场景检验的是**另一条直接 World Runtime 拒绝路径**；BAA gate 采样为零，不代表零延迟、没有越权尝试或风险为零。

本次运行的阶段耗时 **描述性中位数**：

| 阶段（并非独立的纯 admission） | normal | lost_ack | readback_outage |
|---|---:|---:|---:|
| `engine_drive` P50 毫秒 | 4618.072 | 2284.659 | 2244.206 |
| `gate_execute_including_admission_dispatch_readback` P50 毫秒 | 775.020 | 210.390 | 205.933 |
| `gate_observe_including_independent_readback` P50 毫秒 | 181.168 | 412.274 | 460.960 |

Gate execute 同时包含 admission、provider dispatch 和即时回读，**不是纯 admission latency**。在 lost-ack 和 outage 路径中，部分调用返回 `deferred` 或 `outcome_unknown`，因此中位数小于 normal **不能**解释为架构加速。

每段记录 `n`、P50/P95/P99、最小值、最大值、结果类别计数和单调时钟原始耗时。单段 `n=1..5`，P95/P99 只是极少样本的插值；尚不能证明生产尾延迟、吞吐、故障概率或不确定性区间。构建／启动时间、CPU/内存/DB、外部回读开销、自动 assurance labor、principal attention **尚未测量**。

## 归档 artifact

| 场景 | Artifact ID | 归档 SHA-256 |
|---|---|---|
| normal | `11522508523` | `6d0b5ac9f3e23687316175ab1714e84ba6c16fbd249efa3867338201055beddf` |
| lost_ack | `11522518523` | `468d79ac55b229929ed6ea9683bcece62831f348b187ae45d69bc75528e29b6c` |
| readback_outage | `11522743042` | `7b72473bd0e9e2a18855671d4c7eae01fdbf6216cecd4ef927e4b71a6ef0fe59` |
| runtime_bypass | `11522403758` | `94bad1dee51f8a91fb3dbb908989e9affce0134ee8195af365d209fe114a61a8` |

这是 GitHub Actions **压缩包摘要**，不能理解为独立安全审计。

## 下一道验收边界

P6 下一次试验必须事先冻结重复工作负载、并发/到达率、预热、故障安排、数据保留规则和 **SLO 阈值**。需要单独采集纯 admission、effect 到 verification 的耗时，以及 CPU/内存/数据库和每次回读成本，并用足够样本评估不确定性。本轮只证明在不改动既有产品效果和验收判据的前提下，能够取得这些阶段的部分耗时与结果类别。

该证据与 P3 联合现实损失识别、P7 长期委托试点分开。**基线通过不等于允许无人值守的生产写入。**
