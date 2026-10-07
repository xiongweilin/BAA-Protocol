# Exposure Bridge Contract v1

> [English](exposure-bridge-contract-v1.md) | 简体中文

## 状态

本文把 structural v1 的一个剩余假设变成可执行、可证伪的 contract：

`用于 settlement 的 realized exposure <= admission 时声明的 exposure bound`。

本结果**不是**“固定 product path 已经建立该假设”。实际结果是：最低证据要求已经显式化，当前只针对目标对象的 product read-back 不足以满足该要求，而且反例会被保留而不是被 clamp 掉。

可执行 contract 位于 `baa_protocol/exposure_bridge.py`；regression 与 counterexample test 位于 `tests/test_exposure_bridge.py`。

## 具体 exposure metric

v1 只定义一个窄 metric：

> subject-scope exposure = 一个 logical effect 实际影响的不同 product subject 数量。

这个 metric 可用于检验 structural bound assumption，但不声称代表 severity、harm probability、monetary loss、privilege magnitude、session 数量或普适 risk。

当 declared bound=1 时，完整 evidence 最多只能建立 0 或 1 个被影响的 declared subject。出现第二个 subject 就直接证伪该 bound。

## Evidence contract

能够用于 settlement 的 evidence record 必须包含：

- declared subject identity；
- observed target postcondition；
- 显式 affected subject identity 集合；
- 对该 affected-subject 集合在当前 metric 下“完整”的 attestation。

只有 target postcondition read-back 并不满足后两项。

因此 bridge 有三种结果：

1. **established** —— scope-complete evidence 测得 exposure 未超过 declared bound；
2. **falsified** —— scope-complete evidence 测得 exposure 超过 bound，或影响超出 declared target；
3. **unestablished** —— evidence 只观察 target，无法建立 collateral-effect coverage。

只有第一种结果才能生成 formal settlement 使用的 realized exposure。

## 当前固定 product evidence

现有 Odoo/Keycloak verifier 都报告 declared target 的当前状态：

- Odoo employee deactivation 报告 declared subject 与当前 `active`；
- Keycloak identity disable 报告 declared subject 与当前 `enabled`；
- Keycloak session revoke 报告 declared subject 与当前 active-session count。

这些 observation 对 effect completion 与 product reconciliation 很重要，但它们不会枚举底层 operation 实际影响的所有 product subject。因此，对于本 exposure metric，它们仍然是 scope-incomplete。

这意味着当前 product refinement chain 可以建立 exact request identity、ambiguity 后不 blind replay、target postcondition verification，但 structural exposure-bound assumption 仍保持条件性。

## Counterexample

可执行测试保留两类证伪。

### Collateral subject

declared subject 为 `employee:1`、bound=1 时，如果完整 evidence 同时包含 `employee:1` 与 `employee:2`，realized exposure=2。

同一个值随后进入 structural-v1 transition model，verification step 会因为超出 declared bound 而拒绝 settlement。

### Target rebound

如果 declared subject 是 `employee:1`，但 product read-back 标识的是 `employee:2`，即使附带 affected-subject list，bridge 仍不能建立。

## 为什么这是负的结构结果

此前 refinement layer 已逐步连接：

`formal state -> AIOS gate -> World Runtime -> mediated provider surface -> product connector`。

但这些层没有提供 collateral subject effect 的完整 observation。若把 target verification 当成 exposure completeness，就会在没有证据的情况下偷偷加强 claim。

因此 v1 记录这个缺口，而不是事后重定义 exposure。

## Claim 边界

本 contract 不建立：

- 当前 Keycloak/Odoo API 能完整枚举 affected subject；
- subject-count metric 是 production decision 正确的 risk quantity；
- product endpoint 绝不存在隐藏 cross-subject side effect；
- structural joint-risk functional 已校准到真实 harm；
- production failure probability 或 severity；
- production tenant safety。

它只定义并测试：要让一个 exposure-bound assumption 变得可证伪，最低需要什么 evidence。

## 下一项结构义务

现在有两个不同选项，不能混为一谈：

1. 为 subject-count metric 增加 scope-complete reality-side evidence source；或
2. 定义并论证另一种在 product boundary 上能够完整观察的 exposure metric。

只有在 exposure measurement 建立之后，才进入剩余的 semantic task：论证 declared joint-risk functional 本身。
