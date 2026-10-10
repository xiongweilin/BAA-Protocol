# AIOS 集成边界

> [English](README.md) | 简体中文

BAA-Protocol 的第一版 employee-offboarding integration 固定到：

~~~text
xiongweilin/aios@87f24f32a01c67a9246fc3cb127517c80798e169
~~~

这是第一版 offboarding 集成快照，也是已记录的组合端到端验收所用版本。当前兼容性 workflow 另行检出 AIOS commit `0ba9c36bd8168ae1346770e6430474662b30e196`；它不会复现该历史端到端运行。

## Level 1：contract compatibility

当前兼容性 workflow 导入 `0ba9c36bd8168ae1346770e6430474662b30e196` 版本的 AIOS，并检查：

- offboarding policy effect set；
- derived external obligations；
- expected reality postconditions；
- World Runtime capability mapping；
- BAA reference kernel 对 AIOS-derived obligations 的执行。

这只建立与固定 contract surface 的兼容性。

## Level 2：真实 AIOS execution-engine gate

<code>BAAGatedAIOSProvider</code> 是仅用于 integration 的 provider wrapper，位于真实 AIOS <code>OffboardingExecutionEngine</code> effect boundary：

~~~text
AIOS OffboardingExecutionEngine
  -> AIOS EffectRecord
  -> BAA admission / narrow capability
  -> underlying EffectProvider
  -> immediate reality read-back
  -> BAA settlement
  -> AIOS verification / completion
~~~

integration tests 建立三个有限属性：

1. 正常授权 offboarding episode 可通过 gate，并完成三个覆盖 external obligations。
2. 若 attempted effect outcome 含糊且 independent read-back 无法解决，BAA 保留 ambiguity，在 <code>U_max = 1</code> 下阻止后续 provider dispatch，并且不重新执行 ambiguous effect。
3. 若 effect 已 committed 但 acknowledgement 丢失，independent read-back 可结算该 effect；同一 authority epoch 可恢复 execution，并完成剩余 covered effects，而不 replay 已 committed effect。

BAA <code>HOLD</code> 穿过 AIOS provider boundary 时表示 deferred/no-attempt result，而不是 outcome-unknown external attempt。这样保持 admission、execution attempt 与 observed effect 三者分离。

这是仓库中第一类让 BAA 真正改变固定 AIOS engine execution path 的测试。

## Network acceptance 边界

仓库内 compatibility tests 仍使用 in-memory AIOS database 与 deterministic provider fixture。固定 AIOS commit 另包含 <code>tests/acceptance/baa_offboarding</code> 的可执行 network acceptance：

~~~text
AIOS OffboardingExecutionEngine
  -> BAA gate
  -> WorldRuntimeBridge over HTTP
  -> World Runtime process
  -> isolated network effect service

Independent read-back:
BAA gate -> network read-back endpoint -> external observed state
~~~

该 path 覆盖 normal completion、lost acknowledgement、read-back outage 与 unauthorized Runtime bypass，并在隔离 fixture 中保持 exact-once observed effects。

### 已记录 network evidence

AIOS workflow run <code>37302243172</code> 在 <code>aios-windows-docker-desktop</code> 上成功完成，当时 AIOS head 为 <code>600ada8075d4641f22293bf0ba97482c4e73a55c</code>。

保留证据显示：

- mandate probe：HTTP 200 / active；
- normal：<code>completed</code>，3 次 unique writes；
- lost acknowledgement：<code>executing -> completed</code>，最终 3 次 unique writes，<code>duplicate_writes = 0</code>；
- read-back outage：<code>executing -> completed</code>，最终 3 次 unique writes，<code>duplicate_writes = 0</code>；
- unauthorized Runtime bypass：HTTP 403，provider writes <code>0 -> 0</code>。

证据范围刻意狭窄：它是 isolated synthetic effect 上的 production-like network acceptance，不是真实 Odoo/Keycloak 证据。

它不建立 production credential/infrastructure isolation、真实 production latency/outage/concurrency distribution 或 non-synthetic workload 上的 empirical delegation leverage。

## 真实产品 connector evidence

固定 AIOS commit 还包含对实际 administrative products 临时实例的高保真 acceptance。

### Keycloak

AIOS workflow run <code>37306648690</code> 针对 Keycloak <code>26.8.0</code> 通过。

测试使用真实 Admin REST 与 OAuth client-credentials flow，并验证：

- writer/verifier service account 分离；
- offboarding 前存在真实 user session；
- <code>identity.disable</code> 成功并被独立回读；
- <code>sessions.revoke</code> 把真实 session count 从 1 降到 0；
- durable request metadata 可通过 connector reconciliation；
- verifier credential 无权修改 user（HTTP 403）。

Evidence artifact：<code>real-keycloak-offboarding-37306648690</code>，id <code>11344280550</code>。

### Odoo

AIOS workflow run <code>37307582025</code> 针对真实 Odoo <code>18.0-20260926</code> + PostgreSQL 通过。

测试使用真实 JSON-RPC，并验证：

- writer/verifier Odoo user 分离；
- 精确 <code>hr.employee</code> deactivation；
- durable deactivate request marker；
- independent read-back 得到 <code>active = false</code>；
- employee inactive 后 reconciliation；
- verifier write denial。

真实 Odoo run 暴露了一个 production-relevant issue：默认 Odoo search 会隐藏 inactive employee。connector 现在使用 <code>active_test = false</code> 做 durable identity lookup，并由 regression test 锁定。

Evidence artifact：<code>real-odoo-offboarding-37307582025</code>，id <code>11344206985</code>。

这些 run 建立真实临时产品上的 standalone connector compatibility，但本身不建立 production-tenant safety 或 production credential isolation。

## 组合真实产品 end-to-end evidence

AIOS workflow run <code>37315551794</code> 在 PR head <code>b0bb3705d5180557e35a5e6b103c912c32169b70</code> 上通过；该 tree 未改变地合并为 AIOS commit <code>87f24f32a01c67a9246fc3cb127517c80798e169</code>。

组合路径：

~~~text
BAA admission
  -> AIOS OffboardingExecutionEngine
  -> WorldRuntimeBridge over HTTP
  -> World Runtime authorization/capability boundary
  -> real ephemeral Keycloak/Odoo writers
  -> independently credentialed Keycloak/Odoo read-back
  -> AIOS semantic verification
  -> BAA settlement / recovery / external completion
~~~

四个场景通过：

- <code>normal</code>：case 到达 <code>completed</code>；Keycloak <code>enabled = false</code>、<code>active_sessions = 0</code>；Odoo <code>active = false</code>；三个 external obligation 均 independent read-back 并到达 BAA <code>verified_effected</code>；
- <code>lost_ack</code>：第一次 ambiguous attempt 后真实 Keycloak disable effect 已存在；recovery 持久记录 <code>case.reconciliation_started</code> 与 <code>case.reconciliation_resolved_for_execution</code>；durable logical request identity 保持稳定；
- <code>readback_outage</code>：independent read-back 不可用时 effect 保持 unresolved，恢复后通过相同 persisted reconciliation transition 继续；
- <code>runtime_bypass</code>：未授权的直接 effectful Runtime invocation 返回 HTTP 403，<code>provider_effect_observed = false</code>，Keycloak/Odoo before/after state 不变。

E2E harness 也重新验证 credential separation：Keycloak 与 Odoo verifier mutation 都被拒绝。

该声明比 physical exactly-once delivery 更窄：实验支持的是 stable logical request identity 与测试路径中的 no-blind-replay。它仍是 ephemeral acceptance evidence，不是 production-tenant safety、production infrastructure isolation 或 delegation-leverage result。

## Level 3：固定 World Runtime enforcement prerequisite

CI 在不联系已配置 external service 的情况下构建固定 AIOS production World Runtime stack，并检查三个 BAA-covered capability：

- <code>authorization_required == true</code>；
- <code>resource_required == true</code>；
- <code>version_required == true</code>；
- 恰好一个 registered writer 与一个 registered verification capability；
- writer/verifier 使用不同 credential domain；
- 缺少 authorization 的 invocation 在 provider execution 前被 World Runtime 拒绝。

这建立固定 runtime version 的 local enforcement prerequisite。仓库内 BAA gate test 与 World Runtime prerequisite test 仍是独立 compatibility check；固定 AIOS network acceptance path 则在 HTTP/process boundary 上真正组合这些组件。

## 已收敛本地边界

仓库无需外部基础设施即可测试：

~~~text
BAA reference semantics
  -> AIOS contract projection
  -> real AIOS offboarding execution engine
  -> pinned World Runtime enforcement prerequisites
~~~

固定 AIOS 仓库另提供 isolated network acceptance、standalone real-product connector acceptance 与上述 composed real-product E2E matrix。

下一研究步骤不再是继续 connector composition，而是用共同 attention/risk constraint 比较 self-check、post-hoc audit 与 non-bypassable BAA 的 delegation frontier。
