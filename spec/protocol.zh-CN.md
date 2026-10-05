# 协议

> [English](protocol.md) | 简体中文

## 1. 目的

Bounded Action Admission Protocol（BAA）把自适应代理的 proposal process，与授予 reality-facing authority 的机制分离。

协议**不**假设代理自身的 local sufficiency judgment 正确。proposal 可以携带 S(B,P,T) 或同类推理作为 evidence，但 execution authority 只由外部 admission/enforcement path 发放。

## 2. 角色

deployment 可以在物理实现上合并角色，但以下 trust responsibility 必须可区分：

- **Agent (M)**——提出 transition，并根据过去反馈自适应。
- **Admission / assurance kernel (K)**——评估可机械执行的条件，并发放 narrow capability。
- **Executor (X)**——仅接受 K 发放的 capability；对 covered action，agent 不能绕过。
- **Observation / verification path (O)**——为冻结 postcondition 提供 reality-side evidence。
- **VSAR**——版本化记录 proposal、decision、attempt、observation、unknown、intervention 与 outcome。

trust-domain separation 关注 authority 与 evidence dependency，不要求一定由不同公司实现，也不要求人类检查每个 transition。

## 3. Proposal

proposal 至少 SHOULD 绑定：

~~~text
proposal_id
task_domain
deployment_version
object_identity
operation
scope
declared_assumptions
requested_capability
declared_exposure
risk_factors
preconditions
postconditions
verification_method
expiry
reopen_conditions
~~~

可附 free-form explanation，但 hard admission property SHOULD 依赖 canonical field 或 agent 不能通过改写文本就改变的 external state。

## 4. Information state

kernel 获得的不是 reality 本身。

令：

- x_t：真实 world state；
- H_t：时刻 t 可用的 evidence 与 protocol history；
- q_t：kernel information state，包括 state uncertainty、reservation、pending effect、settled exposure、clock 与 history constraint；
- X_t：在 assumption Omega 下与 H_t 相容的 world-state set。

unknown effect 必须一直保留在 compatible-state set 中，直到证据排除。missing confirmation **不得**静默转换成 “no effect”。

## 5. Admission

抽象 decision：

[
Admit(T_t \mid H_t,q_t,K)\rightarrow\{deny,hold,admit\}
]

- **deny**——不授予 requested transition。
- **hold**——当前不能执行；evidence、state、timing、composition 或 verification 条件仍 unresolved。
- **admit**——kernel 发放绑定该 proposal 的 narrow capability。

admission 依赖 history。T_1 的批准可能改变 T_2 的 admissibility 与 marginal exposure。

## 6. Composition-aware exposure

协议不假设各 action 声明的 exposure 可独立线性相加。

令 F(q_t,T) 表示 admit transition 后 information-state update，rho 表示 deployment 声明的 risk functional 或 constraint evaluator。适用时，admission 要求：

[
\rho(F(q_t,T))\preceq R
]

deployment 必须说明 rho 覆盖什么、不覆盖什么。

可能需要 joint treatment 的交互包括：

- shared counterparty、asset、identity、resource；
- common failure domain；
- threshold / nonlinear effect；
- sequencing / timing interaction；
- concurrent write；
- correlated/dependent external process；
- 只有组合后才出现的 semantic/legal effect。

若声称保证所需 interaction 无法被 bounded，相应 exposure 是**unknown**，不是 zero。

## 7. Sustainable safety obligation

若 admitted action 可产生未来不可控过程，仅检查即时 non-violation 不够。

对声称的 structural safety property，admission SHOULD 建立类似：

[
Post_\Omega(q_t,T_t)\subseteq\mathcal W_\Omega
]

其中：

- Post_Omega 包括 assumption Omega 允许的 relevant intermediate execution state、concurrency、external change 与 time advance；
- W_Omega 是一个保守区域，从中 kernel 仍拥有实际上可执行、能维持声称 invariant 的 fallback policy。

协议不要求计算 maximal viable region。可证明的保守 subset 可以接受；因此拒绝的有用工作必须在 delivery side 计量。

若不可区分 state 需要互不兼容的安全 action，无法及时获取区分证据，且不存在共同 enforceable fallback，kernel 就不能声称 guaranteed safe continuation。

## 8. Capability issuance

admitted transition 获得 capability，例如：

[
c=(subject,object,operation,scope,quota,expiry,preconditions,proposal_id)
]

executor MUST 拒绝：

- missing/invalid capability；
- object/operation mismatch；
- expired capability；
- quota excess；
- 被 state change revoke 或 invalidate 的 capability；
- 绕过所需 sequencing/fencing 的 action。

agent MUST NOT 能自行 widen、rebind、extend 或 mint capability。

## 9. Interface narrowing

hard guarantee 在 reality-facing interface 能暴露机械可区分属性时最强，例如：

- amount；
- object identity；
- operation type；
- recipient set；
- rate；
- expiry；
- bounded resource quota。

open semantic effect 通常需要 empirical detection；除非接口被收窄，使相关语义变成可机械约束属性。

例如，把 unrestricted email generation 替换成 approved template selection + constrained fields，可能降低 delivery flexibility，但扩大 structurally enforceable region。

该 trade-off 必须显式：

[
interface width
\leftrightarrow
hard guarantee coverage
\leftrightarrow
useful delivery
]

## 10. Execution 与 effect

协议保持以下区别：

~~~text
proposal
!= admission
!= authorization capability
!= execution attempt
!= external effect
!= observation
!= verification
!= outcome
!= completion
~~~

transport success 或 provider receipt 本身不能 settle 现实 effect。

external system 通常不能与 local protocol ledger atomic commit，因此 state machine 必须表示 pending、partial observation、delay-confirmed 或 unsafe-to-replay effect。

## 11. Pending exposure

reserved、pending、settled exposure 必须有互斥且明确的 accounting semantics，避免同一 exposure 被重复计数或静默丢失。

pending effect 达到 terminal verification deadline 仍缺少 adequate evidence 时，deployment contract MUST 预定义保守响应，例如：

- 在剩余 horizon 内把 declared upper bound 作为 consumed exposure；
- 或进入 safe terminal / degraded mode。

unresolved effect 不得仅因 authorization window 结束就从 accounting 中消失。

## 12. Guarantee-channel isolation

对 structural claim，admitted agent action 不能修改该 claim 所依赖的机制或 evidence source，除非该修改路径本身也被 guarantee 显式覆盖。

一个有用 deployment obligation 是：

[
Reach(admitted\ actions)\cap Sources(K)=\varnothing
]

对 scope 内 protected source 成立。

protected set 可包括：

- kernel policy/executable；
- capability-signing authority；
- audit / VSAR integrity；
- independent read-back source；
- guarantee 相关 clock/counter；
- contract configuration；
- credential 与 isolation boundary。

若 deployment 有意允许修改这些 source，claim 必须描述额外 trust 与 transition protocol，而不能默认 isolation。

## 13. Adaptive agents

hard guarantee SHOULD 面向可能：

- 知道公开 admission policy；
- 记住 prior proposal；
- 观察 admission decision 的最小 operational result；
- 调整 wording、decomposition、ordering、timing；
- 搜索 policy boundary；

的 agent。

隐藏 policy 不是正确 enforcement 的替代品。

secret、randomized mechanism 或 query bound 仍可支持 conditional deterministic/probabilistic guarantee，但必须显式说明 assumption 与 proof model。

## 14. Agent-visible feedback

agent 不需要看到完整 assurance record。

external record 可保留 detailed rejection cause、risk-model state、red-team rule、calibration outcome 与 verification evidence，而 agent 仅收到继续运行所需信息。

reduced disclosure 是 defense in depth。structural safety claim 不应依赖 adaptive agent 恰好没有推断出 guard。

## 15. Settlement 与 reopening

verification 把 external observation 与 frozen postcondition、declared scope 比较。

transition 可得到：

- verified expected effect；
- verified unexpected effect；
- no effect；
- unresolved / unknown effect；
- recovery / compensation；
- contract / boundary reopening。

settlement 更新 exposure 与 delivery record。即使早期 action 已历史记录，新 evidence、changed assumption、expired observation 或 bridge failure 都可能使 future admission 失效。

## 16. 非目标

协议本身不：

- 定义正确价值；
- 证明 risk model 捕获全部 harm；
- 创造现实中缺失的 reversibility；
- 让 open semantic task 自动变成 structurally safe；
- 保证 task completion；
- 消除 deployment acceptance 或 responsibility arrangement 的需要；
- 把 red-team survival 变成 worst-case safety proof。
