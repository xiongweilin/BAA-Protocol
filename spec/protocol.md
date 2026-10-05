# Protocol

## 1. Purpose

The Bounded Action Admission Protocol (BAA) separates an adaptive agent's proposal process from the mechanism that grants reality-facing authority.

The protocol does **not** assume that an agent's local sufficiency judgment is correct. A proposal may carry (S(B,P,T)) or equivalent reasoning as evidence, but execution authority is issued only by an external admission and enforcement path.

## 2. Roles

A deployment may combine roles physically, but the following trust responsibilities must remain distinguishable:

- **Agent (M)** — proposes transitions and adapts to prior feedback.
- **Admission / assurance kernel (K)** — evaluates mechanically enforceable conditions and issues narrow capabilities.
- **Executor (X)** — accepts only capabilities issued by (K); the agent cannot bypass it for covered actions.
- **Observation / verification path (O)** — supplies reality-side evidence for frozen postconditions.
- **VSAR** — versioned record of proposals, decisions, attempts, observations, unknowns, interventions, and outcomes.

Trust-domain separation is about authority and evidence dependence. It does not require different companies or a human to inspect every transition.

## 3. Proposal

A proposal SHOULD bind at least:

```text
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
```

Free-form explanation may accompany the proposal, but hard admission properties SHOULD depend on canonical fields or external state that the agent cannot alter merely by rephrasing text.

## 4. Information state

The kernel does not receive reality itself.

Let:

- (x_t) be the actual world state;
- (H_t) be the evidence and protocol history available at time (t);
- (q_t) be the kernel's information state, including state uncertainty, reservations, pending effects, settled exposure, clocks, and history constraints;
- (mathcal X_t) be the set of world states compatible with (H_t) under assumptions (Omega).

Unknown effects remain in the compatible-state set until evidence excludes them. Missing confirmation MUST NOT be silently converted into "no effect".

## 5. Admission

The abstract decision is:

[
Admit(T_tmid H_t,q_t,K)ightarrow
{deny, hold, admit}.
]

- **deny** — the requested transition is not granted.
- **hold** — the transition is not executable yet; unresolved evidence, state, timing, composition, or verification conditions remain.
- **admit** — the kernel issues a narrow capability tied to the proposal.

Admission is history-dependent. Approval of (T_1) may change the admissibility and marginal exposure of (T_2).

## 6. Composition-aware exposure

The protocol does not assume that independently declared action exposures add linearly.

Let (F(q_t,T)) describe the information-state update associated with admitting a transition and let (ho) be the declared deployment risk functional or constraint evaluator.

Admission requires, when applicable:

[
ho(F(q_t,T))preceq R.
]

The deployment MUST state what (ho) covers and what it does not cover.

Examples of interactions that may require joint treatment include:

- shared counterparties, assets, identities, or resources;
- common failure domains;
- threshold and nonlinear effects;
- sequencing and timing interactions;
- concurrent writes;
- correlated or dependent external processes;
- semantic or legal effects created only by a combination of actions.

If the interaction needed for the claimed guarantee cannot be bounded, the corresponding exposure is **unknown**, not zero.

## 7. Sustainable safety obligation

Immediate non-violation is insufficient when an admitted action can create an uncontrollable future process.

For a claimed structural safety property, admission SHOULD establish a condition of the form:

[
Post_Omega(q_t,T_t)subseteqmathcal W_Omega,
]

where:

- (Post_Omega) includes relevant intermediate execution states, concurrency, external changes, and time advance allowed by (Omega);
- (mathcal W_Omega) is a conservative region from which the kernel still has an actually enforceable fallback policy that preserves the claimed invariant.

The protocol does not require computing a maximal viable region. A conservative provable subset is acceptable; rejected useful work is measured on the delivery side.

If indistinguishable states require incompatible safety actions, no distinguishing evidence can be obtained in time, and no common enforceable fallback exists, the kernel cannot claim guaranteed safe continuation.

## 8. Capability issuance

An admitted transition receives a capability such as:

[
c=(subject,object,operation,scope,quota,expiry,preconditions,proposal_id).
]

The executor MUST reject:

- missing or invalid capabilities;
- object or operation mismatch;
- expired capabilities;
- quota excess;
- capabilities revoked or invalidated by state changes;
- actions that bypass required sequencing or fencing.

The agent MUST NOT be able to widen, rebind, extend, or mint the capability itself.

## 9. Interface narrowing

Hard guarantees are strongest where the reality-facing interface exposes mechanically distinguishable properties.

Examples:

- amount;
- object identity;
- operation type;
- recipient set;
- rate;
- expiry;
- bounded resource quota.

Open semantic effects generally require empirical detection unless the interface is narrowed so that the relevant semantics become mechanically constrained.

For example, replacing unrestricted email generation with selection from approved templates and constrained fields may reduce delivery flexibility while expanding the structurally enforceable region.

This trade-off is explicit:

[
interface width
leftrightarrow
hard guarantee coverage
leftrightarrow
useful delivery.
]

## 10. Execution and effect

The protocol preserves:

```text
proposal
!= admission
!= authorization capability
!= execution attempt
!= external effect
!= observation
!= verification
!= outcome
!= completion
```

A transport success or provider receipt cannot by itself settle a real-world effect.

External systems generally cannot atomically commit with the local protocol ledger. The state machine must represent effects that are pending, partially observed, confirmed after delay, or unsafe to replay.

## 11. Pending exposure

Reserved, pending, and settled exposure MUST have mutually defined accounting semantics so the same exposure is not accidentally counted twice or silently dropped.

When a pending effect reaches its terminal verification deadline without adequate evidence, the deployment contract MUST predefine a conservative response, such as:

- charge the declared upper bound as consumed exposure for the remaining horizon; or
- enter a safe terminal / degraded mode.

An unresolved effect MUST NOT disappear from accounting merely because the authorization window ended.

## 12. Guarantee-channel isolation

For structural claims, admitted agent actions must not be able to modify the mechanism or evidence sources on which those same claims depend, unless that modification path is itself explicitly covered by the guarantee.

A useful deployment obligation is:

[
Reach(admitted actions)cap Sources(K)=arnothing
]

for the protected sources in scope.

The protected set can include:

- kernel policy and executable;
- capability-signing authority;
- audit / VSAR integrity;
- independent read-back sources;
- clocks and counters relevant to the guarantee;
- contract configuration;
- credentials and isolation boundaries.

If a deployment intentionally permits changes to these sources, the claim must describe the additional trust and transition protocol instead of assuming isolation.

## 13. Adaptive agents

Hard guarantees SHOULD be stated against agents that may:

- know the published admission policy;
- remember prior proposals;
- observe the minimal operational result of admission decisions;
- adapt wording, decomposition, ordering, and timing;
- search for policy boundaries.

Security through hiding the policy is not a substitute for correct enforcement.

Secrets, randomized mechanisms, or query bounds may still support conditional deterministic or probabilistic guarantees when their assumptions and proof model are explicit.

## 14. Agent-visible feedback

The agent need not receive the entire assurance record.

The external record may retain detailed rejection causes, risk-model state, red-team rules, calibration outcomes, and verification evidence, while the agent receives only the information required for continued operation.

Reduced disclosure is defense in depth. Structural safety claims should not depend on an adaptive agent simply failing to infer the guard.

## 15. Settlement and reopening

Verification compares external observations with frozen postconditions and declared scope.

A transition may result in:

- verified expected effect;
- verified unexpected effect;
- no effect;
- unresolved / unknown effect;
- recovery or compensation;
- contract or boundary reopening.

Settlement updates exposure and delivery records. New evidence, changed assumptions, expired observations, or bridge failure may invalidate future admissions even when earlier actions remain historically recorded.

## 16. Non-goals

The protocol does not, by itself:

- define correct values;
- prove that its risk model captures all harms;
- create missing real-world reversibility;
- make open semantic tasks structurally safe;
- guarantee task completion;
- remove the need for deployment acceptance or responsibility arrangements;
- turn red-team survival into a proof of worst-case safety.
