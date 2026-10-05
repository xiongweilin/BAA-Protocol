# Guarantee Claims and Proof Obligations

## 1. Claim discipline

BAA-Protocol separates three kinds of support.

### Structural guarantee

A deterministic or probabilistic statement established under explicit assumptions.

A generic template is:

[
orall Minmathcal M_{mathrm{adaptive}}, orall Einmathcal E_{Omega}:
Pr[	au_{0:H}(M,K,E)
otin I_D]learepsilon.
]

The claim MUST state whether (arepsilon) is:

- exactly zero under a deterministic proof;
- a bound from a conditional probabilistic proof; or
- an empirical estimate.

The third case is not a structural proof.

### Empirical reliability

Observed behavior of a versioned deployment policy in a stated task and environment distribution.

It may include:

- useful delivery;
- failures;
- unknown / unresolved outcomes;
- coverage;
- denial / hold rates;
- assurance interventions;
- recovery events;
- calibration;
- attention cost;
- third-party human assurance cost.

Historical reliability does not automatically establish behavior under distribution shift, a new deployment version, or a broader task domain.

### Deployment acceptance

A normative and institutional decision that the residual uncertainty, risk, attention burden, authorization structure, and responsibility arrangement are acceptable for use.

Acceptance does not make a false empirical or structural claim true.

## 2. Required claim fields

Every material guarantee claim SHOULD identify:

```text
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
```

## 3. Deployment version

Empirical records refer to a deployment policy, not only a model.

A minimal version tuple is:

[
v=(v_{model},v_{contract},v_{kernel},v_{tools},v_{observation}).
]

Other components SHOULD be versioned when they can change admission, execution, evidence, or outcomes.

A model upgrade may preserve some structural interface guarantees while invalidating behavior-distribution estimates.

## 4. Enforcement obligation

The first proof obligation is that the implementation actually enforces the kernel property (I_K).

Examples include:

- complete mediation of covered reality-facing operations;
- capability authenticity and binding;
- quota and expiry enforcement;
- non-bypassability;
- tamper resistance;
- concurrency fencing;
- accounting integrity;
- protected observation paths.

The exact assurance technique can include proof, model checking, exhaustive finite-state exploration, typed construction, testing, or a justified combination. The resulting claim strength must match the evidence.

## 5. Semantic bridge obligation

Enforcing a proxy is not enough.

The second obligation is:

[
oxed{Omega_{mathrm{bridge}}land I_KRightarrow I_D^*}
]

where (I_D^*) is a precisely stated real-world property in task domain (D), not an unspecified notion of "what the principal really wants".

The bridge assumptions SHOULD state:

- which real-world effects are constrained;
- how those effects are observed or bounded;
- which action channels are covered;
- acceptable observation error and delay;
- relevant timing and composition assumptions;
- excluded effects;
- environmental assumptions required for the implication.

If the bridge cannot be justified, narrow the interface, task domain, or guarantee statement.

A policy implementation bug is not automatically a new instance of normative non-closure. Ordinary implementation errors remain ordinary implementation errors.

## 6. Partial observability

The kernel acts from an information state, not the true world state.

Let:

[
mathcal X_t={x: x	ext{ is compatible with }H_t	ext{ under }Omega}.
]

Claims involving safety under uncertainty SHOULD cover all states that remain compatible with the available evidence, rather than silently selecting the most convenient state estimate.

Unknown observations remain unknown.

## 7. Sustainable safety

Where future effects can become uncontrollable, the structural obligation SHOULD be stronger than immediate constraint satisfaction.

One admissible form is:

[
Post_Omega(q_t,T_t)subseteqmathcal W_Omega,
]

where (mathcal W_Omega) is a region from which an enforceable fallback policy can continue maintaining the claimed property.

This is a viability-style obligation. The repository does not assume that the maximal safe region is computable.

## 8. Composition obligation

A guarantee about a sequence or concurrent set of actions must justify its composition model.

The claim MUST NOT infer whole-system safety merely from per-action acceptance.

The deployment SHOULD state:

- shared state;
- shared resources;
- interaction factors;
- non-linear or threshold effects;
- unresolved pending effects;
- concurrency semantics;
- history dependence;
- the risk or constraint functional (ho).

Expected values are linear without an independence assumption; some coherent risk measures are subadditive. The issue is whether the quantity being combined is a valid bound for the current joint process and whether unmodeled interaction effects remain.

## 9. Adaptive-agent assumption

(mathcal M_{mathrm{adaptive}}) must be explicit.

A strong structural target permits agents that know the public policy and adapt based on prior operational feedback.

Any claim that additionally depends on:

- limited query count;
- bounded computational resources;
- secret material;
- rate limits;
- restricted feedback;
- non-collusion;

must state these assumptions.

Such a claim may still be a structural deterministic or structural probabilistic guarantee if the bound is proved in the stated model. Conditionality does not make a result merely empirical.

## 10. Assurance-channel isolation

Protected guarantee sources and control points must be identified.

If an admitted action can alter:

- the kernel;
- policy configuration;
- capability-signing material;
- counters;
- trusted clocks;
- read-back sources;
- audit integrity;
- the operator or institution defining the contract;

then either:

1. that path is excluded by enforceable isolation; or
2. the guarantee explicitly models and constrains it.

"Independent source" is not a magic label. Independence is a property of actual failure and control dependencies.

## 11. Pending and terminal obligations

Guarantee horizon (H) does not erase effects that remain unresolved at (H).

A claim MUST specify terminal treatment of:

- unconfirmed attempts;
- possibly-realized effects;
- delayed observations;
- long-lived commitments;
- recovery obligations.

If an effect remains possible and cannot be verified, it remains represented in the terminal state or is conservatively charged according to the deployment contract.

## 12. Interface-bounded structural coverage

Structural guarantees are strongest for properties mechanically exposed by the execution interface.

The repository therefore distinguishes:

- **interface-discernible properties** — object, operation, amount, recipient, rate, expiry, quota, state-machine position;
- **semantic-dependent properties** — intent, social meaning, legal interpretation, hidden code behavior, sensitive-content meaning.

This is not an absolute metaphysical division. Interface redesign can move properties from the second category toward the first.

The structural claim must name the actual boundary.

## 13. Red-team evidence

Adaptive red teaming is primarily falsificatory.

For tested attack policies:

[
max_{piinPi_{mathrm{tested}}}Risk(K,pi)
le
sup_{piinPi_C}Risk(K,pi).
]

Therefore:

- a successful attack can refute the corresponding claim;
- failure to find an attack can increase empirical confidence;
- finite red-team search does not by itself establish a worst-case upper bound over (Pi_C).

Reports MUST state attack resources, feedback access, search budget, model versions, and stopping conditions.

## 14. VSAR evidence requirements

The Versioned Sufficiency Assurance Record SHOULD preserve the full proposal population, including:

```text
proposed
-> denied | held | admitted
-> attempted
-> effect unknown | observed
-> verified | failed verification
-> settled | unresolved | recovery
```

It should not report reliability only on:

- admitted successful cases;
- cases with conveniently observed outcomes;
- cases selected after discovering that their declared assumptions happened to hold.

At minimum report:

- conditional reliability;
- proposal coverage;
- denial / hold / admission rates;
- unknown-result proportion;
- intervention rate;
- assumption-failure rate;
- useful delivery;
- principal attention;
- third-party assurance labor.

## 15. Attention and delivery are separate from safety

A deployment can remain safe by refusing or holding everything.

Therefore safety claims are evaluated separately from delivery claims.

A deployment evaluation may use constraints such as:

[
Pr(A_H>A_{max})ledelta_A,
]

[
ho(mathbf L_H)preceqmathbf R,
]

and

[
Pr(W_Hge W_{min})ge1-delta_W.
]

These expressions do not create their own evidence. Each probability, risk measure, and threshold must be justified by the relevant proof, data, or deployment decision.

## 16. Assumption set (Omega)

At minimum, a material structural claim SHOULD consider:

- observation availability and error;
- observation latency;
- executor mediation;
- capability integrity;
- timing assumptions;
- concurrency semantics;
- composition model;
- pending-effect accounting;
- fallback controllability;
- adaptive-agent capability;
- guarantee-channel isolation;
- semantic bridge;
- environment change class;
- terminal treatment;
- cryptographic or secrecy assumptions, where applicable.

An omitted assumption is not thereby false, but it is outside the stated guarantee.
