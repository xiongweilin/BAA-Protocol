# Canary Release Promotion 任务域

> [English](canary-release-promotion.md) | 简体中文

## 范围

这是 BAA 的第二个具体任务域：canary-release-promotion。

固定 AIOS 源版本：xiongweilin/aios@34b9f4274487f856ac4c23266d1dd726b24ae53c。

源任务域是 AIOS Autonomous Development 的 progressive delivery。它把风险结构从“撤销权限”切换为“逐步扩大真实流量敞口，同时保持 rollback”。

第一版只覆盖 AIOS 已有的两个 traffic capability：

- development.traffic.apply
- development.traffic.restore

接口机械绑定 experiment、target、control release、candidate deployment、stage index、candidate traffic weight、operation identity 与 state version。

## Kernel 性质

参考 kernel 尝试强制：

1. 没有 exact-scope capability 就不能改变 traffic；
2. experiment、target、release、deployment、stage、weight 不能重绑定；
3. stale state-version 不能执行；
4. 不能跳过配置 stage；
5. 当前 stage evidence 不足时不能继续扩大；
6. deterministic guardrail 违反时不能扩大；
7. 所需 telemetry 不完整时不能扩大；
8. 前一个 route effect unresolved 时不能扩大；
9. unresolved route increase 不能 blind replay；
10. rollback 不可用时不能增加 exposure；
11. 即使前一个 increase unresolved，也可独立授权 restore-to-control 作为 compensating action；
12. 只有独立观察到 candidate weight 为 0 才算 restore 完成。

这些是接口/过程保证，不是 candidate software 正确性的证明。

## 现实桥接

有界现实主张是：

- candidate traffic 不被有意提高到 admitted stage 以上；
- stage increase 必须顺序进行；
- 扩大 exposure 前必须有充分、可归属 evidence 且 guardrail 通过；
- route change 结果含糊时保持 unknown，不自动产生 replay permission；
- 增加 exposure 前必须存在可执行 restore-to-control 路径。

这些主张依赖显式假设：traffic director 是 covered route-changing 路径；candidate_weight_percent 对应有效流量敞口；identifier 绑定正确 runtime object；route read-back 观察现实而非 command receipt；telemetry 可归属且不能被 admitted write 修改；guardrail 是实际部署契约；restore 在要求时限内仍可执行。

## 信息与 exposure 状态

最小信息状态包括 experiment identity、target/control/candidate identity、stage sequence、当前 verified stage 与 weight、state version、stage evidence、guardrail、route-effect knowledge、rollback availability 与 operation history。

主要机械 exposure 是 candidate traffic weight。参考 risk state 是结构化向量而非单一标量：

rho(q) = (candidate_weight, unresolved_route_effect, guardrail_violations, stale_or_skip_actions, out_of_scope_actions)

guardrail violation 与 identity error 是约束，不能拿来与更多流量互换。

## 可持续安全区域

只有在 rollback 仍可强制、当前 exposure 位于配置 stage 内、没有前序 unresolved increase、当前 evidence 允许下一 stage 时，才 admit 新 exposure increase。

guardrail 失败后不再扩大。机械 fallback 是 restore-to-control，而不是通知人等待救场。

## Evidence 语义

后续 stage increase 前，前一 stage 必须满足 minimum duration、total requests、candidate requests、必要 control requests/metrics、telemetry completeness 与 guardrail。

evidence 不足输出 hold。guardrail violation 阻止 exposure increase。

协议保持：

command accepted != route changed != route independently observed

ambiguous apply 保持 pending。pending 期间不能继续增加，也不能 blind replay；可以独立授权 restore 来降低 exposure。

## 明确不保证

本域不证明程序正确、metric 完整、所有 metric change 的因果归属、观察窗口后没有 delayed regression、open-ended product objective 正确、声明假设之外 rollback 一定可用，或 failure mode 的 production prevalence。

## 第一阶段验证边界

在第二域真实模型比较之前必须先满足：

1. BAA canary state machine regression test 通过；
2. AIOS CanaryStage 与 Experiment stage 语义精确映射；
3. covered case 中 BAA evidence/guardrail decision 与 AIOS evaluate_canary_stage 一致；
4. AIOS traffic change 实际通过 development.traffic.apply 与 development.traffic.restore；
5. unknown traffic effect 在 World Runtime boundary 保持 reconciliation-required。
