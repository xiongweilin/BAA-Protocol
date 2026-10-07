# Exposure Metric Binding v1

> [English](exposure-metric-binding-v1.md) | 简体中文

## 状态

本层在不修改冻结 structural-v1 state machine 的前提下，把下一项 semantic dependency 显式化。

structural v1 携带整数 `exposure_bound`，但该整数没有 concrete metric identity。现实侧 measurement 不能仅因为“也是一个整数”就直接进入 formal settlement。

可执行 binding contract 位于 `baa_protocol/exposure_bridge.py`，测试位于 `tests/test_exposure_bridge.py`。

## 冻结 observable metric

本 binding 版本只识别一个 concrete metric identifier：

`managed-subject-state-change-count-v1`

其值定义为：一个 logical operation 前后，在冻结且显式观察的 product-state projection 中发生变化的 managed subject 数量。

该 metric 有意比“所有真实世界 side effect”更窄。隐藏 product field、无关 object type、unmanaged subject、downstream system，以及 projection 没有表示的 harm 都不属于该 metric。

## 必须存在的 declaration

concrete measurement 可以作为 realized exposure 使用之前，proposal side 必须显式绑定：

- proposal identity；
- metric identity；
- declared subject identity；
- exposure bound。

measurement 随后必须精确匹配该 declaration，并提供：

- 相同 proposal identity；
- 相同 metric identity；
- 相同 declared subject；
- 与该 subject 一致的 target read-back；
- managed-subject before/after count；
- changed-subject set；
- 对冻结 metric 的 scope-complete attestation。

这样可以防止“按一个 metric 收集的 observation”被静默拿去 settle “按另一个 metric 声明的 bound”。

## Fail-closed 情况

可执行 checker 会拒绝：

- proposal identity rebound；
- metric identity rebound；
- subject identity rebound；
- 不支持的 metric identifier；
- managed-subject scope 不完整；
- read-back subject 与 declaration 不一致；
- changed subject 超出 declared target；
- realized metric exposure 超过 declared bound。

collateral-subject 反例继续保留：target=`employee:1`、control=`employee:2`、bound=1、changed set=`{employee:1, employee:2}` 时，realized exposure=2，bridge 不成立。

## 与 Exposure Bridge Contract v1 的关系

[Exposure Bridge Contract v1](exposure-bridge-contract-v1.zh-CN.md) 已经明确：仅有 target-only read-back 不足以证明广义 subject-scope bound。

本层不会推翻那个负结果。它实现的是该文档给出的第二条路径：定义一个更窄、可观察的 metric，并要求 measurement 在解释为 exposure 前与 proposal 的 metric declaration 精确绑定。

仍有一个 semantic 问题没有解决：

> 对某一项 structural guarantee 而言，`managed-subject-state-change-count-v1` 是否真的是它希望约束的 exposure quantity？

本 contract 防止 metric substitution，但不回答这个 calibration 问题。

## 当前 acceptance instrumentation

AIOS 的真实 Odoo/Keycloak connector acceptance 已有该 observable metric 的候选实现：在隔离临时 tenant 中加入显式 managed control subject，并做 before/after 全量枚举。对应 AIOS 变更在其自身仓库线被接受之前，这些候选运行不进入本 BAA claim。

因此，本 binding contract 独立于任何单次 acceptance run。

## Claim 边界

本结果不建立：

- observable metric 覆盖全部 product side effect；
- observable metric 能表示 harm severity 或 probability；
- 当前 production tenant 能被完整枚举；
- structural-v1 的历史 `exposure_bound` 本来就是按该 metric 声明；
- joint-risk functional 已校准到该 metric；
- production safety。

它建立的是 exact metric/identity binding，以及从完整 observable measurement 到整数 realized exposure 的 fail-closed 转换。

## 下一项结构义务

当一个 reality-side measurement source 被正式接受后，剩余 semantic obligation 是：为每类 concrete proposal 显式绑定 exposure metric，并论证为什么该 metric 正是 declared joint-risk functional 所消费的 quantity。
