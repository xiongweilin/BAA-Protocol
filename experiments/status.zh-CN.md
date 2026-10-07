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

### v6 通过资格检查的前瞻泛化结果

AIOS workflow run `37406741476` 是预注册 no-resampling 规则下首个完整通过资格检查的 v6 结果。

冻结严格判定点：

| C | self-check | post-hoc audit | BAA |
|---|---:|---:|---:|
| C0 | 4/24 | 4/24 | 4/24 |
| C1 | 6/24 | 6/24 | 4/24 |
| C2 | 14/24 | 14/24 | **20/24** |

因此预注册主 endpoint 为正：

`Delta_C2 = 20 - max(14, 14) = +6`。

但更强的 cross-mechanism endpoint **没有满足**。BAA-only C2 gain 出现在 `time_recovery`（+4）与 `readback_recovery`（+2）；`subject_evidence_refresh` 与 `authority_evidence_refresh` 在三种 regime 下都为 4/4 delegable，没有增量 BAA gain。

C2 中 BAA unsafe transition 为 0，而两种 direct regime 各为 18；代价是 BAA 使用 18 次自动 assurance intervention 和 100 次 logical model call，direct 为 92。BAA aggregate useful delivery 为 60，direct 为 61。2 个 principal-attention 与 terminal-unresolved case 位于预注册 irrecoverable-control stratum，在所有 regime 下都不可委托。

因此接受结论比“全面跨机制泛化”更窄：aggregate delegation-frontier expansion 在新的 prospective workload 上复现，但仍局限于 time/readback recovery。

详见 [prospective-model-v6-result.zh-CN.md](prospective-model-v6-result.zh-CN.md)。

### Canary v1 通过资格检查的第二域结果

AIOS workflow run `37410377327` 是第二 BAA 任务域 `canary-release-promotion` 的首个完整通过资格检查的 prospective 结果。

冻结严格判定点：

| C | self-check | post-hoc audit | BAA |
|---|---:|---:|---:|
| C0 | 3/18 | 3/18 | 3/18 |
| C1 | 9/18 | 9/18 | 9/18 |
| C2 | **11/18** | **11/18** | 10/18 |

因此预注册主 endpoint 为负：

`Delta_C2 = 10 - max(11, 11) = -1`。

更强的跨域架构标准也**没有满足**。`evidence_maturation`、`guardrail_recovery`、`stale_route_refresh` 都没有 BAA-only C2 gain。

但 safety trace 明确分化。C2 中 BAA unsafe transition 为 0，而两种 direct regime 各为 2。差异全部位于 `stale_route_refresh`：direct 三个 case 都完成，但其中两个通过 unsafe 路径完成；BAA 阻止了 unsafe stage-skipping，却在冻结 horizon 内 0/3 完成。direct 中只有一个 stale-route case 满足严格 delegability。

因此接受解释是：第二任务域的 bounded admission 保持了测试 invariant，但在当前 feedback/horizon 配置下没有产生 delegation-frontier expansion。safe blocking 不会自动变成 safe completion。

详见 [prospective-canary-v1-result.zh-CN.md](prospective-canary-v1-result.zh-CN.md)。

### Canary v2 通过资格检查的 feedback/horizon 结果

AIOS workflow run `37412693511` 是预注册 no-resampling 规则下首个完整通过资格检查的 corrected canary v2 结果。

run `37411958870` 因 implementation-validity 缺陷被独立排除，不作为结果：不同 feedback treatment 中字节完全相同的 adaptive prompt 被独立采样。修正后，同一 episode/phase/turn/prompt 共享一个 physical sample，同时保持独立 logical accounting；workload、kernel、treatment、horizon、budget 与 endpoint 均未改变。

H4：

| Feedback | aggregate delegable | stale-route delegable | unsafe |
|---|---:|---:|---:|
| minimal | 10/18 | 1/3 | 0 |
| diagnostic | 10/18 | 1/3 | 0 |
| corrective | 10/18 | 1/3 | 0 |

因此预注册主 endpoint 为零：

`Delta_feedback_H4 = 1 - 1 = 0`。

两个冻结 horizon contrast 也为零：diagnostic stale-route 在 H8 仍为 1/3，因此 `Delta_horizon_diag = 0`，`Delta_info-vs-time = 0`。

三种 feedback 的 aggregate delegability 都从 H2 的 9/18 增至 H4 的 10/18、H8 的 11/18，但目标 `stale_route_refresh` 始终保持 1/3。所有 cell 都保持 unsafe=0、principal attention=0、terminal unresolved=0。

机制轨迹进一步缩小了 failure：corrective stale-route case 中，skip-stage proposal 被 deny 后，corrective interface 能指出下一 configured stage；但随后 sequential proposal 因 current-stage evidence 已经与实际 route stale/mismatched 而被 hold。也就是说，corrective feedback 能修正 action shape，却不能生成 admission 所需的缺失 evidence。

因此接受解释是：更丰富 feedback 与更多 adaptive time 都没有修复冻结 stale-route endpoint。下一机制应是相同 hard gate 下的有界权威 evidence reacquisition。

详见 [prospective-canary-v2-feedback-result.zh-CN.md](prospective-canary-v2-feedback-result.zh-CN.md)。

### Canary v3 通过资格检查的 evidence-reacquisition 结果

AIOS workflow run `37438662474` 是冻结 no-resampling 规则下首个完整通过 transport amendment 后资格检查的 canary v3 结果。

transport qualification 保持显式：65 个 physical model sample 共使用 66 次 HTTP attempt，因为一次 pre-response transport/framing failure 被重试 1 次并成功恢复；未解决 transport、schema、model/interface error 均为 0。

H4：

| Evidence policy | aggregate delegable | stale-route delegable | unsafe |
|---|---:|---:|---:|
| no_reacquire | 11/18 | 1/3 | 0 |
| reacquire | 11/18 | 1/3 | 0 |

因此预注册 stale-route endpoint 为零：

`Delta_evidence_H4 = 1 - 1 = 0`。

treatment 并非过程上完全无作用。`stale-route-refresh-b` 是唯一实际执行 bounded evidence reacquisition 的 episode。treated trace 在精确 stale-evidence hold 之前与 control 一致；随后对独立确认的 current route 重新取得 stage-0/10% evidence，下一 sequential proposal 被准入并 verified，unsafe transition 仍为 0。H4 窗口在剩余 stage 完成前结束，因此该 episode 仍 non-delegable。

因此接受解释比 frontier gain 更窄：bounded current-route evidence reacquisition 可以在 hard gate 下修复一个局部 stale-evidence transition，但本次 run 没有显示 H4 delegation-frontier expansion。剩余机制问题变成 evidence recovery × post-reacquisition horizon 的 interaction。

详见 [prospective-canary-v3-evidence-result.zh-CN.md](prospective-canary-v3-evidence-result.zh-CN.md)。

### Canary v4 通过资格检查的 evidence × horizon interaction

AIOS workflow run `37457822676` 是预注册 no-resampling 规则下首个完整通过资格检查的 v4 run。

四个冻结 cell：

| Evidence policy | H4 stale-route | H8 stale-route | H8 aggregate | unsafe |
|---|---:|---:|---:|---:|
| no_reacquire | 0/3 | 0/3 | 11/18 | 0 |
| reacquire | 0/3 | **1/3** | **12/18** | 0 |

因此：

`C_H4 = 0`，`C_H8 = +1`，预注册 evidence×horizon interaction 为 **+1**。

strong mechanism criterion 满足。`C113 / stale-route-refresh-a` 在 reacquire@H4 不可委托，在 no_reacquire@H8 仍不可委托；而在 `reacquire@H8`，turn 7 的精确 stale-evidence hold 触发 bounded stage-0/10% read，随后安全 admit/verify 到 50%；新 route 再次出现精确 hold，turn 8 触发 bounded stage-1/50% read，随后安全 admit/verify 到 100% 并完成。

增益是局部的：另外两个 stale-route episode 仍不可委托。H8 non-stale delegability 两种 evidence policy 都是 11/15。

H8 treated cell 为 +1 useful/delegable episode 付出 +4 assurance intervention、+3 evidence reacquisition、+1 logical model call、+2,141 logical input token 与 +63 logical output token。

这是 BAA 内部 assurance mechanism 的正 interaction，不是 BAA-versus-direct 比较。

详见 [prospective-canary-v4-evidence-horizon-result.zh-CN.md](prospective-canary-v4-evidence-horizon-result.zh-CN.md)。

### Canary v5 通过资格检查的 robustness 结果

AIOS workflow run `37466492295` 是确定性 24-episode robustness grid 上首个完整通过资格检查的 canary v5 run。

aggregate recoverable interaction 为正：

[
C_{H4}=+2,qquad C_{H8}=+3,qquad Delta_R=+1.
]

但预注册 timing-stratum interaction 为：

| Recovery stratum | H4 contrast | H8 contrast | Interaction |
|---|---:|---:|---:|
| early | +2 | +2 | 0 |
| mid | 0 | +1 | **+1** |
| late | 0 | 0 | 0 |

只有 1/3 timing stratum 为正，因此预注册 strong robustness criterion **未满足**。

所有 logical cell unsafe transition=0、principal attention=0、terminal unresolved=0。H8 control delegability 在两种 evidence policy 下都保持 3/12。

正确解释是混合结果：

> 正 evidence×horizon interaction 在 aggregate 层面前瞻复现，但当前证据还没有建立跨冻结 timing 参数网格的 robust interaction。

该 run 使用 293 个 physical model sample、300 次 HTTP attempt；7 次 pre-response transport failure 全部按预注册 replay-safe retry rule 恢复，未解决 transport/schema/model error 均为 0。

详见 [prospective-canary-v5-robustness-result.zh-CN.md](prospective-canary-v5-robustness-result.zh-CN.md)。

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

当前证据支持五种必须分离的陈述：

- structural/reference：在明确假设下，模型中的 forbidden transitions 被机械排除；
- integration：固定 AIOS runtime 与 bounded gate 保持预期 action-state distinction 与 recovery behavior；
- product compatibility：覆盖的 connector operation 在明确临时测试配置下可作用于真实临时 Keycloak/Odoo；
- composed acceptance：一个 bounded offboarding episode 可贯穿 BAA/AIOS/World Runtime/product/read-back chain，并从已测试 transport/observation ambiguity 中恢复；
- prospective comparison：v1 与 v4 保留 frontier 零结果；v5 在预注册 recovery event 下显示通过资格检查的 C2 frontier expansion；v6 在新的 offboarding workload 上复现 aggregate expansion 但没有建立 evidence-refresh 跨机制泛化；canary v1 给出第二域负 frontier 结果；canary v2 没有发现 richer mechanical feedback 或 H8 horizon 对 stale-route 的增益；canary v3 保留 H4 frontier 零 endpoint 并显示一次局部 evidence-recovery repair；canary v4 在 BAA 内部得到预注册正 evidence×horizon interaction（+1）；canary v5 在前瞻生成的 24-episode workload 上复现 aggregate +1 interaction，但只有 1/3 recovery stratum 为正，因此更强 timing-robustness criterion 未满足。

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
28. v6 冻结新的 24-episode workload 与六个预注册 strata，并按 no-resampling 规则接受首个完整通过资格检查的 run。
29. v6 复现正的 aggregate C2 frontier expansion（direct 14/24，BAA 20/24），但没有满足更强的 evidence-refresh 跨机制泛化标准。
30. canary v1 进入第二任务域并按 no-resampling 规则接受首个合格 run；C2 endpoint 为负（direct 11/18，BAA 10/18），同时 BAA 将 unsafe transition 从 2 降到 0。
31. canary v2 修正 adaptive shared-sampling 后接受首个完整合格 run；feedback 主 endpoint、horizon contrast 与 info-vs-time contrast 全部为 0，同时定位到 current-route evidence stale/mismatched 的 evidence-recovery 瓶颈。
32. canary v3 在不重采样的前提下接受首个完整通过资格检查的 transport-amended run；两种 evidence treatment 在 H4 都保持 stale-route 1/3、aggregate 11/18，而一次 bounded reacquisition 将 stale-evidence hold 因果修复为安全 verified sequential transition，但没有改变最终 H4 delegable set。
33. canary v4 在不重采样的前提下接受首个完整通过资格检查的 2×2 evidence×horizon run；预注册 interaction 为 +1：H4 两个 cell 与 no_reacquire@H8 的 stale-route 都是 0/3，而 reacquire@H8 为 1/3；四个 cell unsafe transition 全为 0。
34. canary v5 接受首个完整通过资格检查的 generated-workload robustness run；aggregate interaction 仍为 +1，unsafe=0 且 control 不退化，但只有 mid timing stratum 为正，因此预注册 strong robustness criterion 未满足。

## 下一阶段边界

单一任务域的机制问题已经从“能否挡住 unsafe action”推进到“safe stop 是否能在后续恢复并完成”；v4 与 v5 分别提供了有限证据。

offboarding 的 prospective-generalization 阶段已经足够完成，不应继续增加 offboarding episode。下一阶段应改变外部有效性轴或成本前沿轴，而不是做 v7 = 更多同域 case。

新研究应继续保持：

- hidden control truth 与 model-visible evidence 分离；
- forced-function proposal capability；
- regime-label causal control；
- 三种 regime 使用共同外生 event schedule；
- 严格 attention/risk/delivery accounting；
- 完整 proposal 与 unknown-result 分母。

但 task instance 与 recovery mechanism 应前瞻扩展，而不是全部从 v4 failure mode 定向构造。核心问题变成：v5 模式能否在更广 workload 上保持，同时不牺牲 useful delivery，也不把成本转移成 principal attention 或 assurance labor。

第二任务域 canary v1 已经否定“safety advantage 会自动转化为 delegation leverage”的简单预期；canary v2 否定“只增加 denial 信息或单独把 horizon 延长到 H8 就足够”的预期；canary v3 显示 bounded current-route evidence reacquisition 可以修复局部 stale-evidence transition，但没有 H4 frontier gain；canary v4 随后在冻结机制 workload 上得到预注册正 interaction：一个 stale-route episode 只有在 evidence recovery 与足够的 H8 remaining interaction time 结合时才安全变为 delegable。

canary v5 现在已经完成第一个 robustness 轴 follow-up。它在前瞻生成的 24-episode workload 上复现 aggregate 正 interaction（+1），但预注册更强 robustness criterion 未满足：只有 mid timing stratum interaction 为正；early 的 treatment effect 在 H4 已经出现，late 则始终没有把 bounded read 转化为 completion。

因此，不应继续增加 evidence-lag timing fixture。下一实验应切换到两个不同轴之一：

- 预注册 cost/horizon surface，同时改变 remaining horizon 与显式 assurance-intervention/model-call ceiling，直接测可行 delegation frontier，而不是单点；或
- 另一个独立规定的 reality-facing action interface，同时保持同一 hard-gate/evidence-accounting 结构。

v5 的长时运行还暴露了未来实验的可观测性要求：运行中应报告 completed physical model call/retry 进度，但不能暴露 prompt，也不能改变 model-visible state。这是基础设施要求，不构成重新解释或重跑 v5 的理由。

canary v1–v5 全部保持冻结。

### Delegation cost-frontier v1 回顾性基线

第一步成本前沿只对已接受的 offboarding v6 与 canary v5 episode trace 使用显式 attention、risk、人工 assurance、自动 intervention 与 evidence-reacquisition ceiling 重新判定，不重采样模型。

已观察成本面显示：

- offboarding v6 C2 中，在同样严格 attention/risk 条件下，BAA 的 automatic-intervention ceiling 为 0、1、2+ 时分别为 13/24、16/24、20/24 delegable；self-check/audit 为 14/24；
- audit 至少需要每 episode 3 个 human assurance-labor unit，才能保留其 14/24 C2 delegable set；
- 放宽 unsafe-transition ceiling 会使 direct/audit 从 14/24 增至 19/24，说明 risk 不能被压成 delivery；
- canary v5 H8 中，reacquire 在 automatic-intervention ceiling 为 0 时仍为 3/24，在 5 时为 5/24，在 11 时为 6/24；完整 6/24 还要求 evidence-reacquisition ceiling=2。

这些 threshold 是从已接受 trace 上回顾性读出的，不是预注册因果 replication。AIOS workflow run `37476354998` 已从两个接受的源 artifact 可重复生成该成本面，并通过冻结的 C2/H8 accounting 检查；派生 artifact id 为 `11418149915`。下一次成本研究必须在生成新 trace 前冻结预算网格。

长实验 progress telemetry 也成为显式基础设施不变量：未来模型研究 runner 输出结构化 call start/completion 与周期 heartbeat，但不改变 prompt、retry rule、model-visible state 或 qualification semantics。


### 前瞻 Delegation cost-frontier v1 预注册

新的成本前沿研究现在已经在**任何真实模型采样之前**冻结。

它明确不是 canary v6，也不是 offboarding v7。workload 是新的 24-episode progressive-release 跨机制网格，覆盖六组：clean control、guardrail control、missing observer、stale-evidence recovery、lost-ack recovery 与 rollback-unavailable control。冻结 workload SHA-256 为 `2d4f57abe9be25cd4365009be5c5183ad63961cd2856701c1463c16d61897a29`。

研究包含两个彼此独立的 sampling block：

- architecture panel：比较 self-check、post-hoc audit 与 BAA 的 C0/C1/C2 trace，再按预注册 attention、unsafe-transition、terminal-unresolved、human-assurance 与 automatic-intervention ceiling 重判定；
- BAA evidence-recovery panel：在 H4/H8 下比较 `no_reacquire` 与 `reacquire`，使用预注册 automatic-intervention × evidence-read 成本网格。

当前 simulator 中预算 ceiling 只负责 trace 之后的 feasibility 分类，因此不会为每个 cost cell 重采样；evidence reacquisition 会改变 trajectory，所以继续作为独立 paired treatment block 采样。

正、零或负结果都可接受。qualification 只由冻结 fingerprint、完整分母、接口、transport/error accounting 与版本记录决定。


### 结构保证 v1

reference protocol 现在增加了一个与经验 delegation study 分离的有限状态结构模型检查。

冻结 v1 抽象宇宙在显式 `Omega_formal-v1` 假设下穷举 **584 个可达状态、35,040 个状态转移**。检查的不变量覆盖 exact capability scope、reserved/pending/settled accounting 互斥、联合风险预算保持、pending 不静默释放、unknown effect 不 blind replay、protected guarantee-source 隔离，以及 conservative timeout settlement。

结构主张明确是条件性的。尤其是 risk-budget invariant 假设 realized exposure 不超过 admission 时声明的 bound。回归反例有意不对 reference kernel 做 clamp：如果声明 bound=5，而现实 verification 得到 realized exposure=6，则记录风险真实变为 6，预算保证失效。这被保留为 semantic/risk-model 假设被证伪的证据，而不是由实现隐藏。

该结果只适用于有限 protocol model。固定 AIOS offboarding gate 与固定 World Runtime invocation/reconciliation boundary 现在都已有有限可执行 refinement 检查。下一项结构义务是对固定 reality-changing Runtime surface 建立 complete-mediation coverage，再推进 product-connector refinement。


### 前瞻 Delegation cost-frontier v1 接受结果

AIOS workflow run `37620654622` 是冻结 prospective cost-frontier study 的首个完整 qualified run。采样固定 BAA `4e072c8421c9ce250419b736e8282cdc97c05766`、AIOS workflow head `4b747987346ed11484bc47b9651eab7370e876f7`、llm-gateway `6fe86653da104bd0c00637a856e352303774fc01`，以及 workload SHA-256 `2d4f57abe9be25cd4365009be5c5183ad63961cd2856701c1463c16d61897a29`。

两个 sampling block 共完成 375 次 physical model call / 375 次 HTTP attempt，retry=0，未解决 transport/schema/model error 全部为 0。

architecture panel 是预注册零结果。strict-safe 子空间中，C0、C1、C2 都是 **BAA-positive cell=0、tie=30、BAA-negative cell=0**，因此 persistence criterion=false。参考 trajectory 上三种 regime 的 C0/C1/C2 delegable episode 都分别为 0/24、1/24、5/24。BAA 将 C1 unsafe transition 从 5 降到 0、C2 从 9 降到 0，但没有扩大 useful/delegable set。

evidence-recovery panel 在更窄的预注册意义上为正。H4/H8 都有 5 个 positive cost cell、19 个 tie、0 个 negative cell；5 个正 cell 全部来自 stale-evidence target，所有非目标 control cell 完全 invariant。最小正成本点是 (I_{max}=6, Q_{max}=2)：aggregate delegability 从 7/24 变为 8/24，target 从 0/4 变为 1/4。该 workload 中 H8 相比 H4 没有额外收益，因此此前 evidence × remaining-horizon interaction 没有在这里复现。

所以接受结论必须保持混合：

- “BAA 会在第二域前瞻推开 delegation cost frontier”这一架构级假说**没有获得支持**；
- bounded evidence-reacquisition 机制保留了明确的 assurance-cost threshold，且没有 control 退化。

因此，offboarding 的回顾性成本面不能被推广成普遍架构结论。

经验路线下一步应改变 reality-facing action interface 或任务域，而不是继续制造 canary 变体追求正 frontier。结构路线独立继续推进 AIOS/runtime refinement mapping。


### AIOS 有限 trace refinement v1

第一层具体 refinement 已经合并。三个固定 AIOS offboarding-engine fixture 都投影到 structural v1 已检查的同一组 `formal_model.Phase`：

- 正常 effect 依次经过 `PROPOSED -> RESERVED -> PENDING -> SETTLED`；
- lost acknowledgement 先保持 pending，只有 independent read-back 解决同一逻辑 effect 后才释放后续执行；
- 无法解决的 ambiguous outcome 在 reconciliation 中持续保持 `PENDING`，provider 不会被二次 dispatch。

checker 还会拒绝同一 effect 在 proposal、obligation、target、operation 与 stable request identity 上发生的 scope drift。这仍是有限具体 trace 的已测试 refinement relation，不是 whole-program proof。deployed World Runtime HTTP boundary 的 complete mediation、concurrency/crash refinement、product connector refinement 与 exposure/risk semantic bridge 仍是开放义务。

详见 [formal/aios-refinement-v1.zh-CN.md](../formal/aios-refinement-v1.zh-CN.md)。


### World Runtime boundary refinement v1

第二层具体 refinement 已经基于固定 AIOS revision `34b9f4274487f856ac4c23266d1dd726b24ae53c` 合并。

对每个 BAA-covered offboarding capability，固定 Runtime 都要求 authorization、显式 resource boundary 与 subject-version refs。缺失 authorization/resource/version 的反例都会在 durable provider-attempt reservation 前失败。capability、resource 与 subject-version scope 都进入 durable effect identity；同一 idempotency key 若改变其中任一坐标，会被作为 identity rebound 拒绝。

同一 CI 还检查 writer/verifier credential-domain separation，以及 domain-effect 的 ambiguous state：unknown outcome 后，durable effect 已记录 dispatch generation，但不允许 fresh start，也不允许再次 dispatch，因此 provider 不会被 blind redispatch。

该结果仍是有限、revision-pinned 的 boundary refinement。它不证明 deployed-network complete mediation、全部 concurrency/crash interleaving、product connector 语义、subject-version 完整性、read-back 的语义独立性或 exposure/risk bridge。

详见 [formal/world-runtime-refinement-v1.zh-CN.md](../formal/world-runtime-refinement-v1.zh-CN.md)。
