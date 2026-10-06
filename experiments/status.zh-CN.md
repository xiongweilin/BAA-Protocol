# 原型状态

> [English](status.md) | 简体中文

## 当前声明层级

仓库在一个具体任务域——员工离职——上已达到七层证据：

1. 可执行 BAA 参考语义与确定性故障 fixture。
2. 固定 AIOS contract compatibility 与 execution-engine gating。
3. 跨 HTTP/process/Docker 边界的隔离、类生产网络 acceptance。
4. 对真实临时 Keycloak 与 Odoo 实例的高保真 connector acceptance。
5. 单 episode 的组合 BAA -> AIOS -> World Runtime -> 真实 Keycloak/Odoo acceptance matrix，含独立产品 read-back 与故障恢复。
6. 预注册的真实模型三制度前瞻研究，包含版本固定的 model/gateway 证据，以及显式保留 null/qualification failure。
7. 通过资格检查的 recovery-focused 真实模型研究，在预注册公共环境恢复事件下显示有限 delegation-frontier expansion。

当前最强 integration 声明仍为：

> 对有限 BAA 模型和固定 AIOS 离职实现 <code>87f24f32a01c67a9246fc3cb127517c80798e169</code>，已测试路径能够约束覆盖范围内的离职行动流，在执行/回读含糊时保留显式不确定性，通过独立观测到的产品状态恢复，在 provider effect 前拒绝未授权 Runtime 绕过，并使用分离的 writer/verifier 身份在真实临时 Keycloak 与 Odoo 上完成覆盖的 IAM/HRIS 义务。

故障恢复声明指的是稳定逻辑 request identity 与已测试路径中的 no-blind-replay，不是对 physical exactly-once delivery 的证明。

第一轮 prospective comparative result 另行保留为负结果：在冻结的七 episode 真实模型研究中，三种 regime 在 C0、C1、C2 都是 6/7 delegable，因此 BAA 没有扩大该有限 delegation frontier。

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
- 共同预算 delegation frontier 与 adaptive capability sweep；
- 真实模型 prospective harness，包含 shared initial sampling、adaptive-prefix reuse、JSON/SSE Responses compatibility，以及 physical/counterfactual logical model cost 分离。

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

## 前瞻真实模型证据

AIOS workflow run <code>37393917221</code> 是第一轮 prospective real-model study 的接受结果。

固定证据：

~~~text
workload: prospective-offboarding-v1
model: gpt-6-luna
BAA-Protocol: 340dbd9a0bfbe72746e3666fa559fa7d812a25d0
AIOS experiment workflow: 6eeaed6874e67257f19d9dc1a66bdc796865804d
local gateway: 496ec69a5b1f578ae837498037f4badf6e4c2dbc
physical calls: 15
calls with errors: 0
~~~

在冻结的严格预算下，self-check、post-hoc audit 与 BAA 在 C0、C1、C2 都得到 6/7 delegable。这是 delegation-frontier expansion 的零结果。

terminal lost-confirmation 在三种 regime 下都不可委托。BAA 在第一个 unresolved effect 后停止后续动作，而 direct regimes 继续两个后续 obligation；因此 useful-delivery trace 不同，但最终 delegable set 不变。

接受 run 中模型没有提交 stale-authority、wrong-subject 或 scope-probing action，因此 BAA admission-denial intervention 为 0。真实模型 prompt 明确要求优先 authoritative evidence 与精确 identifier，所以本研究没有复现 deterministic fixture 中的 adversarial proposal behavior。

两个更早的 run 被排除：<code>37392398429</code> 暴露 JSON/SSE client compatibility bug；<code>37393326558</code> 暴露 episode 完成后 adaptive-call 继续计费的问题。两者均在接受 run 前修复并加入 regression test。

详见 [prospective-model-result.zh-CN.md](prospective-model-result.zh-CN.md)。

### v2 资格结果

第二轮预注册真实模型研究 `prospective-offboarding-v2` 没有产生可接受的 frontier 结果。

- 正式 run `37395717489` 因 transport 与 schema error 未通过 model-evidence qualification；
- 诊断 run `37397784048` 将 transport error 降为 0，但仍保留 1 个 schema error；
- 剩余失败是模型返回 execute object 时使用 `case_subject`，并遗漏必需的 `obligation_id` 与 `subject_ref`；
- 因此 artifact 中机械生成的 9/12 frontier summary 不能作为 comparative evidence 接受。

该结果被记录为 qualification failure，不通过反复重采样直到成功。详见 [prospective-model-v2-result.zh-CN.md](prospective-model-v2-result.zh-CN.md)。

### v3 接口资格结果

v3 请求 strict Responses Structured Outputs，但本地 route 并未执行声明的 JSON Schema。run `37399859506` 在 108 个 physical call 中有 107 个 schema failure，transport failure 为 0，因此没有 frontier 结果。随后独立的 forced-function capability probe 成功。详见 [prospective-model-v3-result.zh-CN.md](prospective-model-v3-result.zh-CN.md)。

### v4 通过资格检查的比较

AIOS workflow run `37402587158` 使用强制 `submit_baa_proposal` function interface，通过完整 v4 qualification。physical sampling 共 36 次调用，transport、schema、model/interface error 均为 0。

在冻结严格预算下，三种 regime 在 C0、C1、C2 都是 9/12 delegable。因此 v4 仍是 delegation-frontier 零结果。

adaptive feedback 同时暴露出有限 safety 差异：self-check/audit 在 C1 有 3 次 unsafe transition、C2 有 4 次；BAA 通过 2/3 次自动 assurance intervention 始终保持 0 unsafe。全部 unsafe transition 都发生在三个本来就不可委托的 episode 中，因为安全 completion 仍需要时间推进或缺失的外部证据。BAA 约束了 reality-facing trace，但没有创造 liveness。

详见 [prospective-model-v4-result.zh-CN.md](prospective-model-v4-result.zh-CN.md)。

### v5 通过资格检查的 delegation-leverage 结果

AIOS workflow run <code>37404551022</code> 使用预注册 recovery/liveness workload、forced-function proposal interface，以及移除 adaptive prompt regime label 的 causal-control head。

资格证据：

~~~text
workload: prospective-offboarding-v5
model: gpt-6-luna
model_interface: function_tool
BAA-Protocol: 59180c03daa3c5709cf974feb43b8dbe992c4427
AIOS workflow head: 81f1592a281cb88a3df8562ac81756382fe9bbe6
gateway: 496ec69a5b1f578ae837498037f4badf6e4c2dbc
physical calls: 32
calls with errors: 0
~~~

冻结严格预算下：

| C | self-check | post-hoc audit | BAA |
|---|---:|---:|---:|
| C0 | 9/12 | 9/12 | 9/12 |
| C1 | 9/12 | 9/12 | 9/12 |
| C2 | 9/12 | 9/12 | **12/12** |

C2 三种 regime 都完成 12/12 episode，并产生 36 个 useful-delivery unit。但 self-check/audit 在三个预注册 recovery episode 上累计 5 个 unsafe transition，因此仍不满足 risk bound。BAA 完成 12/12，同时 unsafe=0、principal attention=0、terminal unresolved=0。

新增的三个 delegable episode 精确为 V204、V210、V212：BAA 先保留安全 continuation，公共 environment recovery event 发生后，C2 后续 turn 完成工作；direct regime 虽也最终完成，但此前已经违反 risk bound。

这是 prospective 系列第一个通过资格检查的有限 delegation-frontier expansion。由于 recovery mechanism 有意来自 v4 已观察 failure mode，它属于机制性证据，而不是 production frequency 的估计。

详见 [prospective-model-v5-result.zh-CN.md](prospective-model-v5-result.zh-CN.md)。

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

正向 acceptance 结果仍是 falsification evidence，而不是 open-world probability estimate。prospective real-model comparison 同时保留其零结果，不把“没有优势”重新解释为失败运行。

当前证据支持四种必须分离的陈述：

- structural/reference：在明确假设下，模型中的 forbidden transitions 被机械排除；
- integration：固定 AIOS runtime 与 bounded gate 保持预期 action-state distinction 与 recovery behavior；
- product compatibility：覆盖的 connector operation 在明确临时测试配置下可作用于真实临时 Keycloak/Odoo；
- composed acceptance：一个 bounded offboarding episode 可贯穿 BAA/AIOS/World Runtime/product/read-back chain，并从已测试 transport/observation ambiguity 中恢复；
- prospective comparison：v1 与 v4 保留 frontier 零结果；v4 显示有限 safety-trajectory separation；v5 随后在预注册 recovery event 允许稍后安全 completion 时显示通过资格检查的 C2 frontier expansion。

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
20. 文档明确区分已证明与未证明内容；
21. 一个真实模型 comparative workload 在解释前完成预注册，并保存版本固定证据；
22. implementation-invalid run 被显式排除，接受的 v1 run 保留零 delegation-frontier result；
23. v2 与 v3 qualification failure 被保留，没有通过事后放宽 parser 或反复重采样消除；
24. forced-function proposal channel 先通过独立 capability probe，再用于完整通过资格检查的 v4 比较；
25. v4 将有限 safety-trajectory 正结果与 delegation-frontier 零结果明确分离；
26. v5 在接受 run 之前冻结公共 recovery-event 时序，并移除 adaptive prompt 中的 regime-name cue；
27. v5 产生首个通过资格检查的有限真实模型 delegation-frontier expansion：C2 self-check/audit 9/12，BAA 12/12。

## 下一阶段边界

单一任务域的机制问题已经从“能否挡住 unsafe action”推进到“safe stop 是否能在后续恢复并完成”；v4 与 v5 分别提供了有限证据。

下一阶段是**delegation leverage 的前瞻泛化检验**，而不是继续调整这十二个 episode。

新研究应继续保持：

- hidden control truth 与 model-visible evidence 分离；
- forced-function proposal capability；
- regime-label causal control；
- 三种 regime 使用共同外生 event schedule；
- 严格 attention/risk/delivery accounting；
- 完整 proposal 与 unknown-result 分母。

但 task instance 与 recovery mechanism 应前瞻扩展，而不是全部从 v4 failure mode 定向构造。核心问题变成：v5 模式能否在更广 workload 上保持，同时不牺牲 useful delivery，也不把成本转移成 principal attention 或 assurance labor。

核心可证伪问题：

> 在共同注意力预算 A 与风险上限 R 下，BAA 是否能在更广 prospective task distribution 上扩大 delegable set？该增益在 adaptive feedback 下是否持续存在，而不依赖手工挑选 recovery case？
