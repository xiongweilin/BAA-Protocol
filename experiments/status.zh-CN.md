# 原型状态

> [English](status.md) | 简体中文

## 当前声明层级

仓库在一个具体任务域——员工离职——上已达到五层证据：

1. 可执行 BAA 参考语义与确定性故障 fixture。
2. 固定 AIOS contract compatibility 与 execution-engine gating。
3. 跨 HTTP/process/Docker 边界的隔离、类生产网络 acceptance。
4. 对真实临时 Keycloak 与 Odoo 实例的高保真 connector acceptance。
5. 单 episode 的组合 BAA -> AIOS -> World Runtime -> 真实 Keycloak/Odoo acceptance matrix，含独立产品 read-back 与故障恢复。

当前最强声明为：

> 对有限 BAA 模型和固定 AIOS 离职实现 <code>87f24f32a01c67a9246fc3cb127517c80798e169</code>，已测试路径能够约束覆盖范围内的离职行动流，在执行/回读含糊时保留显式不确定性，通过独立观测到的产品状态恢复，在 provider effect 前拒绝未授权 Runtime 绕过，并使用分离的 writer/verifier 身份在真实临时 Keycloak 与 Odoo 上完成覆盖的 IAM/HRIS 义务。

故障恢复声明指的是稳定逻辑 request identity 与已测试路径中的 no-blind-replay，不是对 physical exactly-once delivery 的证明。

这不是生产租户安全声明、一般无人值守自治定理或认证结果。

## 当前可执行内容

原型包括：

- 通用 bounded action admission；
- 具体 employee-offboarding admission；
- exact-scope capabilities；
- authority-epoch 与受控 state-version invalidation；
- effective-time 与 verification gating；
- admission HOLD 的显式 deferred/no-attempt 语义；
- unresolved-effect preservation；
- ambiguous effect 后 retry suppression；
- independent read-back 解决 ambiguity 后恢复；
- protected guarantee-source isolation；
- 保守 unresolved-effect concurrency limit；
- VSAR event capture；
- self-check、post-hoc audit 与 BAA 三制度实验；
- deterministic episode-level fault fixtures；
- finite exhaustive admission checks；
- 从真实 AIOS Administrative obligations 的映射；
- 针对固定 AIOS checkout 的 CI；
- 隔离 Windows/Docker 网络 acceptance；
- 真实临时 Keycloak connector acceptance；
- 真实临时 Odoo connector acceptance；
- normal、lost-ack、read-back-outage、unauthorized-bypass 四场景的组合真实产品 offboarding E2E；
- 共同预算 delegation frontier 与 adaptive capability sweep。

## 固定 AIOS 兼容性

BAA CI 固定：

~~~text
xiongweilin/aios@87f24f32a01c67a9246fc3cb127517c80798e169
~~~

CI 验证：

1. AIOS offboarding policy effects 等于 BAA hard-domain effect set。
2. AIOS-derived external obligations 映射时不丢失 case、subject、authority epoch、governance basis、target system 或 operation。
3. 覆盖的 AIOS reality postconditions 能映射到 BAA verification surface。
4. 每个覆盖 effect 都映射到 AIOS World Runtime capability。
5. BAA kernel 能对固定 AIOS 代码派生出的 obligation 执行 admit、execute、verify、recover 与 external complete。
6. BAA provider gate 实际改变 AIOS execution path，同时保持 deferred/no-attempt 与 outcome-unknown 的区别。
7. 固定 World Runtime surface 要求 authorization、resource binding、version binding，以及 writer/verifier credential-domain 分离。

这些检查用于发现 contract drift；它们不证明 production threat model 完整或 production credential isolation。

## 隔离网络证据

AIOS workflow run <code>37302243172</code> 在仓库专用 Windows/Docker Desktop runner 上通过。

- normal：完成，恰好三个 unique external writes；
- lost acknowledgement：恢复完成，最终三个 unique writes，<code>duplicate_writes = 0</code>；
- read-back outage：恢复完成，最终三个 unique writes，<code>duplicate_writes = 0</code>；
- unauthorized Runtime bypass：HTTP 403，provider writes <code>0 -> 0</code>。

这说明 bounded path 能跨越真实 HTTP/process/Docker 边界，并在 synthetic effect service 上保持模型中的 no-replay 与 authorization 属性。

## 真实 Keycloak 证据

AIOS workflow run <code>37306648690</code> 针对 Keycloak <code>26.8.0</code> 通过：

- 真实 OAuth client-credentials/Admin REST；
- writer 与 verifier service account 分离；
- offboarding 前存在真实 user session；
- <code>identity.disable</code> 成功并被独立回读；
- <code>sessions.revoke</code> 使真实 session count 从 1 降为 0；
- 通过持久 connector metadata reconciliation；
- verifier mutation attempt 返回 HTTP 403。

证据 artifact：<code>real-keycloak-offboarding-37306648690</code>，artifact id <code>11344280550</code>。

## 真实 Odoo 证据

AIOS workflow run <code>37307582025</code> 针对 Odoo <code>18.0-20260926</code> + PostgreSQL 通过：

- 真实 JSON-RPC；
- writer 与 verifier Odoo user 分离；
- 精确 <code>hr.employee</code> deactivation；
- 持久 deactivate request marker；
- independent read-back 观察到 <code>active = false</code>；
- deactivation 后 reconciliation 成功；
- verifier write 被拒绝。

该 run 暴露了一个具有生产意义的边界：Odoo 默认搜索会隐藏 inactive employee。connector 现使用 <code>active_test = false</code> 做持久身份查找，并由回归测试锁定。

证据 artifact：<code>real-odoo-offboarding-37307582025</code>，artifact id <code>11344206985</code>。

## 组合真实产品 E2E 证据

AIOS workflow run <code>37315551794</code> 在 PR head <code>b0bb3705...</code> 上通过；该 tree 未改变地合并为 AIOS commit <code>87f24f32...</code>。

### Normal

- AIOS case 到达 <code>completed</code>；
- Keycloak：<code>enabled = false</code>、<code>active_sessions = 0</code>；
- Odoo：<code>active = false</code>；
- 三个 effect 均有 realization 与 confirmed outcome；
- independent read-back 在 frozen execution context 加入 semantic view 前直接观察真实产品字段；
- 三个 BAA obligation 均到达 <code>verified_effected</code>；
- Keycloak 与 Odoo verifier credential 均无 mutation authority。

### Lost acknowledgement

- 首个真实 Keycloak disable effect 已存在，但 acknowledgement 含糊；
- execution 进入持久 reconciliation；
- 记录 <code>case.reconciliation_started</code> 与 <code>case.reconciliation_resolved_for_execution</code>；
- disable 的 durable request identity 在恢复中保持稳定；
- episode 恢复并完成三个 obligation。

它支持“稳定逻辑 request identity + 已测试 no-blind-replay”，但不证明底层产品只发生了一次物理 write。

### Read-back outage

- independent read-back 不可用时，不把 effect 当作 absent；
- execution 进入持久 reconciliation；
- read-back 恢复后继续；
- 记录相同恢复状态转移；
- outage 期间不虚构 successful observation。

### Unauthorized Runtime bypass

- 未带 authorization 的直接 effectful Runtime 调用返回 HTTP 403；
- <code>provider_effect_observed = false</code>；
- Keycloak/Odoo before/after 产品状态不变。

该组合 E2E 仍是临时测试环境证据，不建立生产网络隔离、生产凭证保管或生产运行分布。

## 尚未证明

仓库不建立：

- threat model 完整性；
- HR policy 或 termination decision 的正确性；
- production tenant configuration 正确性；
- production credential/network/infrastructure isolation；
- production IAM/HRIS observation 的完整性或独立性；
- 不存在未覆盖 side channel；
- 真实世界 failure probability；
- 对任意 adaptive agent 的 worst-case safety；
- production delegation leverage；
- principal attention savings；
- third-party assurance labor savings；
- kernel invariant 到所有相关现实伤害的完整 semantic bridge；
- external product 的 physical exactly-once execution。

## 实验解释

所有正结果仍是 falsification evidence，而不是 open-world probability estimate。

当前证据支持四种必须分离的陈述：

- structural/reference：在明确假设下，模型中的 forbidden transitions 被机械排除；
- integration：固定 AIOS runtime 与 bounded gate 保持预期 action-state distinction 与 recovery behavior；
- product compatibility：覆盖的 connector operation 在明确临时测试配置下可作用于真实临时 Keycloak/Odoo；
- composed acceptance：一个 bounded offboarding episode 可贯穿 BAA/AIOS/World Runtime/product/read-back chain，并从已测试 transport/observation ambiguity 中恢复。

任何一项都不意味着生产租户安全。

## 本阶段收敛标准

reference/network/product-composition 阶段已经收敛，因为：

1. 一个 task domain 固定到 source version；
2. guarantee boundary 与 semantic-bridge assumption 明确；
3. protocol 可执行；
4. safety 与 delivery 分开测量；
5. ambiguous effect 保持 unresolved，而非静默 retry；
6. independent resolution 后可恢复 bounded execution；
7. threat fixture 中有 adaptive retry；
8. finite admission-state exploration 自动化；
9. CI 执行 regression tests 与 deterministic comparison harness；
10. source-domain contract 固定并检查；
11. action path 跨越真实 HTTP/process/Docker boundary；
12. 隔离 lost acknowledgement 与 read-back outage 可恢复且 fixture writes 无重复；
13. unauthorized Runtime bypass 在 provider execution 前被拒绝；
14. 真实 Keycloak disable/session-revoke 被执行；
15. 真实 Odoo deactivation/reconciliation 被执行；
16. 两产品 writer/verifier separation 被测试；
17. 一个组合 real-product episode 达到 externally verified completion；
18. real-product lost-ack 与 read-back-outage 持久记录并恢复 reconciliation state；
19. Runtime bypass test 保持真实临时产品状态不变；
20. 文档明确区分已证明与未证明内容。

## 下一阶段边界

继续扩展 connector 或单纯扩展 composition 已不再合理。

下一研究阶段是：

~~~text
A. agent self-check

B. agent + external record / post-hoc audit

C. BAA non-bypassable admission
   -> narrow capability
   -> constrained execution
   -> independent verification
   -> exposure / unresolved-effect control
~~~

三制度应在相同 episode 或 shared-influence-domain workload 上，以共同 principal-attention 与 risk constraint 比较。

主要 outcome 至少包括 useful delivery、unsafe/out-of-scope transition、unresolved-result duration、replay/duplicate logical-request behavior、principal attention、third-party assurance labor、recovery quality，以及对 adaptive attack capability 的敏感性。

核心可证伪问题仍是：

> 在共同注意力预算 A 与风险上限 R 下，BAA 是否提高有用交付或扩大可委托任务集合？该增益在 adaptive attack capability 增强时是否仍存在？
