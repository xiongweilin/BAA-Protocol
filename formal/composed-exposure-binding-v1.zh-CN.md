# Composed Exposure Binding v1

> [English](composed-exposure-binding-v1.md) | 简体中文

## 状态

本结果关闭了 offboarding prototype 的一项有限 refinement 义务：现实侧 exposure measurement 现在已经绑定到真实 product effect 之前实际被 BAA 准入的那个 proposal。

accepted implementation 是 AIOS `b2cc1254a1908d00ded7c705f6e230c43f08f6f8`。合格 real-product E2E 运行在 PR head `e10c5f6c52e12ea08f603e9c8d01ca099e070df4`。两个 commit 的 Git tree 完全相同，都是 `0b24ed3f205ad8bbeffd6b238738baa1a34564a0`，因此被测试的代码内容与进入 AIOS main 的代码内容完全一致。

该 E2E 固定使用 BAA `b3215d940cf7c9bd6b208ed5915eaa3c92ab10e3`。

机器可读记录见 [composed-exposure-binding-v1-result.json](composed-exposure-binding-v1-result.json)。

## 现在已经接通的链条

对三个被覆盖的真实 product effect，流程都是：

1. AIOS 生成具有稳定 `effect_id` 的 effect。
2. BAA gate 用 `effect:{effect_id}` 构造真实 proposal id。
3. gate 在 dispatch 之前为该 proposal 产生 `admit` refinement event。
4. acceptance controller 对冻结的 managed-subject state projection 保存 before/after census。
5. 现实侧 evidence 输出同一个 proposal id、subject、metric id、changed-subject set 与 realized exposure。
6. E2E 通过真实 gate 重建 proposal，调用 `exposure_declaration_for_proposal()` 得到 declaration，再调用 `assess_metric_bound()`。
7. 只有 established assessment 才能通过 `realized_exposure_for_settlement()` 转成 settlement value。

冻结 metric 为 `managed-subject-state-change-count-v1`；三个 offboarding proposal class 都声明 bound=1。

## 合格运行

AIOS workflow run `37638217335` 的四个 scenario 全部通过。

对 `normal`、`lost_ack`、`readback_outage`：

- `identity.disable`：declared bound=1，realized exposure=1；
- `sessions.revoke`：declared bound=1，realized exposure=1；
- `employee.deactivate`：declared bound=1，realized exposure=1；
- 每个 assessment 都为 established；
- 每个被 measurement 引用的 proposal 都实际出现在 gate 的 `admit` trace 中；
- Keycloak measurement 枚举 2 个 managed subject，只有 declared target 发生变化；
- Odoo measurement 枚举 3 个 employee subject，只有 declared target 发生变化。

两个 recovery scenario 都通过 `executing -> completed` 收敛，所以 lost acknowledgement 与临时 read-back loss 没有破坏 proposal identity 或 exposure accounting。

`runtime_bypass` scenario 在 authorization boundary 返回 HTTP 403，没有观察到 provider effect，target product state 前后不变。

Artifacts：

- normal：`11491082646`，digest `sha256:f9f307627a55b01c38c78dc3603019ed6526e71b11f6af0ba02067c3a173e5b5`；
- lost_ack：`11489419994`，digest `sha256:7252a32f9ab63f63a3c481be247a83574be84c0c67a505add493b290d1925325`；
- readback_outage：`11489454782`，digest `sha256:e44102ff8443f0f7c8ee76b1c2e1e631d55ba09461284ab7ce9c3a65b26c343a`；
- runtime_bypass：`11489744687`，digest `sha256:a83371e4d8138a2f7eb1abf70861a9a79dafbcc8c88826caa6f0f4b4197e84cb`。

## 两种 evidence role

这里仍然刻意区分两种证据角色。

普通 target postcondition read-back 继续使用独立的只读 verifier credential。managed-subject scope census 则是由隔离临时 product 的 acceptance controller 执行，因为它的职责是建立冻结测试 projection 的完整性。

这足以支持有限 acceptance claim，但不是 deployed guarantee-channel 的设计证明。

## 本结果建立了什么

在冻结的 offboarding domain、acceptance product、metric、state projection 与测试 scenario 内，下列链条已经可执行并全部通过：

`admitted proposal -> declared metric/bound -> real effect -> scope-complete measurement -> bound assessment`

因此，之前“measurement 没有 admitted proposal identity”的缺口，在这个有限 composed path 上已经关闭。

## 仍未建立什么

本结果不建立：

- hidden product field 没有变化；
- unrelated object type、unmanaged subject、外部服务或 downstream system 没有受到影响；
- production tenant 中该 census mechanism 仍然完整；
- “一个 changed subject”已经对应某个经过校准的 harm quantity；
- 多个 unit exposure 的交互确实服从当前 structural joint-risk function；
- production safety。

因此，当前最高价值的剩余 semantic obligation 已经收缩到最后两项：论证冻结 exposure metric 如何映射到真正关心的 loss/risk quantity，尤其是多个 admitted effect 的组合方式。

这不能通过继续增加成功 connector fixture 来解决；需要显式 loss model，或者主动收窄 guarantee claim。
