# World Runtime Refinement v1

## 状态

本文记录 BAA structural v1 的第二层有限具体 refinement。

固定 AIOS revision：

`34b9f4274487f856ac4c23266d1dd726b24ae53c`

该层由现有 `aios-compatibility` CI 可执行验证。它不主张 whole-program proof，也不主张 deployed network complete mediation。

## Refinement 目标

第一层 AIOS refinement 已把具体 offboarding gate trace 映射到抽象 BAA phase relation。本层继续检查下一道边界：reality-changing request 进入固定 AIOS World Runtime 时，是否保持 formal v1 所需要的 scope 与 unknown-effect 约束。

对 BAA 覆盖的 offboarding capability：

| BAA/AIOS 条件 | World Runtime refinement 检查 |
| --- | --- |
| exact capability scope | request 中 capability 固定，并进入 durable effect identity |
| 显式 target/resource scope | strict effect rule 要求显式 resource boundary |
| evidence/version binding | strict effect rule 要求非空 subject version refs |
| release 前 authorization | strict effect rule 要求 authorization；缺失时在 provider-attempt reservation 前失败 |
| stable logical effect identity | effectful request 必须有 durable idempotency key，并绑定 semantic fingerprint |
| 不允许 scope rebound | 同一 idempotency key 若改变 capability、resource 或 subject-version refs 会被拒绝 |
| unknown effect 保持 unresolved | ambiguous domain effect 不允许 fresh start，也不允许 dispatch |
| independent verification | 覆盖 capability 的 writer/verifier 使用不同 credential domain |

可执行 helper 位于 `integration/world_runtime_refinement.py`。

## 已覆盖的具体证据

`integration/test_aios_world_runtime_surface.py` 检查固定 administrative production Runtime stack。

当前验证：

1. 每个 BAA-covered capability 都要求 `authorization_required`、`resource_required`、`version_required`；
2. writer 与 verifier credential domain 分离；
3. 在 resource/version 已满足时，缺失 authorization 会失败，且失败前不存在 durable provider attempt；
4. 缺失 resource、缺失 version binding 分别都会在 provider attempt 前失败；
5. capability、resource、subject-version scope 任一改变都会改变 Runtime semantic effect fingerprint；
6. 已绑定的 idempotency identity 会拒绝上述 scope rebound。

`integration/test_aios_canary_runtime_reconciliation.py` 通过真实 Runtime HTTP service 检查固定 domain-effect boundary。模拟 lost acknowledgement 后，durable effect 状态为 `ambiguous`，已有 dispatch generation，同时 `start_allowed=false`、`dispatch_allowed=false`；再次调用 provider 会被拒绝。

## 与 formal v1 的关系

本层不新增 abstract phase，而是细化 structural-v1 中 capability scope 与 unknown-effect replay 相关义务：

- Runtime legality check 是从已保留 authority 走向 reality-facing pending effect 的前置条件；
- durable semantic fingerprint 防止同一 logical effect identity 扩张成不同 capability/resource/version scope；
- ambiguous durable effect 对应 unresolved pending effect，不能授权 blind redispatch；
- 独立 verifier credential 支撑具体 trace refinement 所用的 independence 假设，但它本身不证明 read-back 的语义正确性。

## 重要边界

以下内容仍不属于本次 claim：

- 证明所有 deployed reality-changing network path 都被强制经过 `WorldRuntime.invoke()` 或 domain-effect boundary；
- 所有 ledger interleaving 的 concurrency/crash refinement；
- Runtime authorization semantics 与完整 BAA authority model 的形式等价；
- 从 Runtime provider call 到 Keycloak/Odoo 语义的 product-connector refinement；
- 证明 subject-version refs 完整或语义充分；
- 证明 credential 分离必然意味着 evidence 独立；
- structural-v1 风险预算不变量所需的 exposure/risk semantic bridge；
- production tenant 或 unattended autonomy safety。

因此，该结果是有限可执行 boundary refinement，不是 complete mediation 或端到端验证。

## 下一项结构义务

下一步不需要继续增加 phase mapping。更有价值的是：对固定 reality-changing HTTP/domain-provider surface 建立 complete-mediation coverage test，然后再把 refinement 延伸到具体 product connector。后续 claim 继续保持 revision-pinned，并以 counterexample 为主导。
