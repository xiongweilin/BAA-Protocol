# Joint-Risk Binding Contract v1

> [English](joint-risk-binding-contract-v1.md) | 简体中文

## 状态

本文把 concrete exposure declaration 与冻结 structural-v1 joint-risk calculation 之间最后一层 semantic step 单独拆出来。

concrete exposure metric 与 bound 并不能自动决定 risk-factor identity。同样，仅仅复现 structural formula，也不能证明该 formula 代表真实 harm。

可执行 binding contract 位于 `baa_protocol/risk_bridge.py`；regression test 位于 `tests/test_joint_risk_binding.py`。

## 冻结 structural functional

本 contract 只识别一个 functional identity：

`pairwise-shared-factor-min-v1`

对 bound risk term `(b_i, f_i)` 与非负 interaction penalty `lambda`：

`risk = sum(b_i) + lambda * sum(min(b_i, b_j) for pairs with f_i == f_j)`

可执行函数复现 `FiniteBAAModel` 使用的同一计算。

这只建立 formula identity，不建立 calibration。

## Exact term binding

exposure declaration 能成为 joint-risk term 之前，必须另有 risk-factor declaration 绑定：

- 相同 proposal id；
- 相同 exposure metric id；
- 非空 risk-factor id；
- 被支持的 joint-risk functional id。

proposal identity rebound、metric identity rebound、空 risk factor、以及 functional substitution 都会 fail closed。

生成的 bound risk term 会保留 proposal id、exposure metric id、exposure bound、risk-factor id 与 functional id。

组合计算还会拒绝**重复 proposal id**和**混合 exposure metric id**。每个 term 单独完成精确绑定，并不等于可以直接相加不同计量单位（例如 subject count 与金额）。跨 metric 组合需要独立论证共同单位或显式换算，不属于 v1 保证。

## 当前 offboarding 结果：尚未 calibration

三个 reference offboarding proposal class 现在已有 concrete exposure declaration，但**没有** calibrated risk-factor declaration。

`OFFBOARDING_RISK_FACTOR_IDS_V1` 被有意保持为空。

因此：

- `employee.deactivate`；
- `identity.disable`；
- `sessions.revoke`

目前都不能通过该 bridge 投影到 structural joint-risk functional。

这是有意设计。把 HRIS 与 IAM effect 指定为相同或不同 risk factor，本身就是实质性的 dependence claim；仓库目前没有足够 evidence 支持该选择。

## Interaction penalty 仍是独立参数

即使未来声明了 risk-factor identity，interaction penalty 仍是独立 calibration parameter。

可执行测试显示，同样两个 unit exposure、同一 shared factor：

- penalty 0 -> risk 2；
- penalty 1 -> risk 3；
- penalty 2 -> risk 4。

本 contract 不为 concrete offboarding 选择其中任何一个值。

## 与前序 exposure layer 的关系

semantic chain 现在被拆成不同义务：

`proposal class -> exposure metric/bound -> reality-side measurement -> risk-factor identity -> joint-risk functional`

仓库已经为三个 offboarding operation 冻结第一步，并为后续 binding step 建立 exact contract。

已接受链条仍缺：

1. observable metric 的 accepted scope-complete reality-side measurement source；
2. calibrated offboarding risk-factor identity 与 interaction semantics。

## Claim 边界

本结果不建立：

- 哪些 offboarding operation 共享真实 risk factor；
- HRIS 与 IAM effect 是独立还是相关；
- concrete interaction penalty；
- pairwise-min functional 代表真实 harm；
- observable exposure metric 拥有正确 severity semantics；
- production risk probability 或 safety。

它只建立从“显式 exposure term + 显式 risk factor”到既有 structural formula 的 exact、fail-closed bridge。

## 下一项结构义务

剩余 semantic work 已经不是另一个 wiring layer，而是 empirical/domain-theoretic 问题：

1. 接受或拒绝冻结 exposure metric 的 scope-complete measurement source；
2. 为 concrete offboarding effect 定义有 evidence 支撑的 risk-factor identity；
3. 论证或证伪 pairwise interaction form 与 penalty。

在此之前，structural joint-risk guarantee 继续只在显式 Omega assumptions 下成立。
