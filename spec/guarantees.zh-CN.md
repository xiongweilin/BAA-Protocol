# 保证声明与证明义务

> [English](guarantees.md) | 简体中文

## 1. 声明纪律

BAA-Protocol 区分三类支持。

### 结构保证

在显式假设下建立的确定性或概率性陈述。

通用形式：

[
\forall M\in\mathcal M_{\mathrm{adaptive}},\ \forall E\in\mathcal E_\Omega:
Pr[\tau_{0:H}(M,K,E)\notin I_D]\le\varepsilon
]

声明 MUST 说明 epsilon 是：

- 确定性证明下严格为 0；
- 条件概率证明给出的上界；
- 或经验估计。

第三种不属于 structural proof。

### 经验可靠性

版本化 deployment policy 在明确 task/environment distribution 中的观测行为。

可包括：

- useful delivery；
- failure；
- unknown/unresolved outcome；
- coverage；
- denial/hold rate；
- assurance intervention；
- recovery event；
- calibration；
- attention cost；
- third-party human assurance cost。

历史可靠性不会自动推广到 distribution shift、新 deployment version 或更宽 task domain。

### 部署接受

对 residual uncertainty、risk、attention burden、authorization structure 与 responsibility arrangement 是否可接受所作的规范/制度决定。

deployment acceptance 不会让错误的 empirical 或 structural claim 变真。

## 2. 必需声明字段

每个 material guarantee claim SHOULD 指明：

~~~text
claim_id
claim_class: structural_deterministic | structural_probabilistic | empirical | deployment_acceptance
task_domain D
guarantee_horizon H
real_world_property I_D
kernel_property I_K
deployment_version v
assumptions Omega
adaptive_agent_class M
environment_class E
covered_interfaces
excluded_effects
observation_sources
terminal_pending_policy
proof_or_evaluation_method
epsilon_or_empirical_uncertainty
falsification_conditions
~~~

## 3. Deployment version

经验记录针对 deployment policy，而不只是模型。

最小 version tuple：

[
v=(v_{model},v_{contract},v_{kernel},v_{tools},v_{observation})
]

其他会改变 admission、execution、evidence 或 outcome 的组件也 SHOULD versioned。

model upgrade 可能保持某些 structural interface guarantee，却使 behavior-distribution estimate 失效。

## 4. Enforcement obligation

第一项 proof obligation：implementation 确实执行 kernel property I_K。

例如：

- covered reality-facing operation 的 complete mediation；
- capability authenticity/binding；
- quota/expiry enforcement；
- non-bypassability；
- tamper resistance；
- concurrency fencing；
- accounting integrity；
- protected observation path。

assurance technique 可以是 proof、model checking、finite-state exhaustive exploration、typed construction、testing 或合理组合；最终 claim strength 必须与 evidence 匹配。

## 5. Semantic bridge obligation

执行 proxy 不够。

第二项义务：

[
\boxed{\Omega_{\mathrm{bridge}}\land I_K\Rightarrow I_D^*}
]

其中 I_D^* 必须是 task domain D 中精确定义的现实属性，而不是未定义的“委托人真正想要什么”。

bridge assumptions SHOULD 说明：

- 哪些 real-world effects 被约束；
- 如何观测或 bound；
- 哪些 action channel 被覆盖；
- 可接受 observation error/delay；
- 相关 timing/composition assumption；
- excluded effect；
- implication 成立所需 environment assumption。

若 bridge 无法论证，应收窄 interface、task domain 或 guarantee statement。

policy implementation bug 不会自动成为新的 normative non-closure；普通实现错误仍是普通实现错误。

## 6. Partial observability

kernel 从 information state 行动，而不是直接从 true world state 行动。

令：

[
\mathcal X_t=\{x:x\text{ 在 }\Omega\text{ 下与 }H_t\text{ 相容}\}
]

涉及 uncertainty safety 的 claim SHOULD 覆盖所有仍与 evidence 相容的 state，而不是静默选择最方便的 state estimate。

unknown observation 保持 unknown。

## 7. Sustainable safety

当未来 effect 可能变得不可控，structural obligation SHOULD 强于即时 constraint satisfaction。

一种形式：

[
Post_\Omega(q_t,T_t)\subseteq\mathcal W_\Omega
]

其中 W_Omega 是一个区域，从中 enforceable fallback policy 仍能继续维持声称属性。

这是 viability-style obligation。仓库不假设 maximal safe region 可计算。

## 8. Composition obligation

对 action sequence 或 concurrent set 的 guarantee 必须证明其 composition model。

不得仅从 per-action acceptance 推导 whole-system safety。

deployment SHOULD 说明：

- shared state；
- shared resource；
- interaction factor；
- nonlinear/threshold effect；
- unresolved pending effect；
- concurrency semantics；
- history dependence；
- risk/constraint functional rho。

expected value 的线性不需要 independence assumption；某些 coherent risk measure 是 subadditive。关键问题是：被组合的 quantity 是否真的是当前 joint process 的有效 bound，以及是否仍存在 unmodeled interaction effect。

## 9. Adaptive-agent assumption

必须显式定义 \mathcal M_adaptive。

强 structural target 应允许 agent 知道 public policy，并基于 prior operational feedback 自适应。

任何额外依赖以下条件的 claim：

- limited query count；
- bounded computation；
- secret material；
- rate limit；
- restricted feedback；
- non-collusion；

都必须写明。

若在声明模型中得到了证明，这类有条件 claim 仍可属于 structural deterministic/probabilistic guarantee；“有条件”不等于“只是经验性”。

## 10. Assurance-channel isolation

必须识别 protected guarantee source 与 control point。

如果 admitted action 可以修改：

- kernel；
- policy configuration；
- capability-signing material；
- counter；
- trusted clock；
- read-back source；
- audit integrity；
- 定义 contract 的 operator/institution；

则必须二选一：

1. 通过 enforceable isolation 排除该路径；
2. guarantee 显式建模并约束该路径。

“independent source”不是魔法标签；independence 是实际 failure/control dependency 的属性。

## 11. Pending 与 terminal obligation

guarantee horizon H 不会删除 H 时仍 unresolved 的 effect。

claim MUST 规定以下对象的 terminal treatment：

- unconfirmed attempt；
- possibly-realized effect；
- delayed observation；
- long-lived commitment；
- recovery obligation。

如果 effect 仍可能存在且不可验证，它必须继续表示在 terminal state 中，或按 deployment contract 做 conservative charge。

## 12. Interface-bounded structural coverage

structural guarantee 对 execution interface 能机械暴露的属性最强。

仓库区分：

- **interface-discernible properties**——object、operation、amount、recipient、rate、expiry、quota、state-machine position；
- **semantic-dependent properties**——intent、social meaning、legal interpretation、hidden code behavior、sensitive-content meaning。

这不是绝对形而上划分。interface redesign 可以把属性从第二类推向第一类。

structural claim 必须明确真实边界。

## 13. Red-team evidence

adaptive red teaming 首先是 falsificatory。

对已测试 attack policy：

[
\max_{\pi\in\Pi_{\mathrm{tested}}}Risk(K,\pi)
\le
\sup_{\pi\in\Pi_C}Risk(K,\pi)
]

因此：

- successful attack 可反驳相应 claim；
- 未找到 attack 可增加 empirical confidence；
- finite red-team search 本身不能建立对 Pi_C 的 worst-case upper bound。

报告 MUST 说明 attack resource、feedback access、search budget、model version 与 stopping condition。

## 14. VSAR 证据要求

VSAR SHOULD 保留完整 proposal population：

~~~text
proposed
-> denied | held | admitted
-> attempted
-> effect unknown | observed
-> verified | failed verification
-> settled | unresolved | recovery
~~~

不能只对以下 subset 报告 reliability：

- admitted successful cases；
- 方便观测到 outcome 的 case；
- 事后才发现 declared assumption 成立的 case。

至少报告：

- conditional reliability；
- proposal coverage；
- deny/hold/admit rate；
- unknown-result proportion；
- intervention rate；
- assumption-failure rate；
- useful delivery；
- principal attention；
- third-party assurance labor。

## 15. Attention 与 delivery 必须与 safety 分离

deployment 可以通过拒绝或 hold 一切来保持安全。

因此 safety claim 与 delivery claim 分开评价。

可以使用类似约束：

[
Pr(A_H>A_{max})\le\delta_A
]

[
\rho(\mathbf L_H)\preceq\mathbf R
]

[
Pr(W_H\ge W_{min})\ge 1-\delta_W
]

这些表达式本身不会创造 evidence。每个 probability、risk measure 与 threshold 都必须由相应 proof、data 或 deployment decision 支持。

## 16. Assumption set（Omega）

material structural claim 至少 SHOULD 考虑：

- observation availability/error；
- observation latency；
- executor mediation；
- capability integrity；
- timing assumption；
- concurrency semantics；
- composition model；
- pending-effect accounting；
- fallback controllability；
- adaptive-agent capability；
- guarantee-channel isolation；
- semantic bridge；
- environment change class；
- terminal treatment；
- cryptographic/secrecy assumption（适用时）。

遗漏 assumption 不代表它是 false，但它位于声明 guarantee 之外。
