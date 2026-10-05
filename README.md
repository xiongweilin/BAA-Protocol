# BAA-Protocol

**Bounded Action Admission Protocol**

BAA-Protocol studies whether an external, non-bypassable admission and execution protocol can increase useful delegated work under fixed attention and risk constraints.

It is not a claim that autonomous systems are generally safe. It is a repository for stating, implementing, and attempting to falsify conditional guarantees.

## Research question

Given the same model, task distribution, and reality-facing interfaces, does replacing direct agent execution with a bounded action protocol enlarge the set of tasks that can be completed under fixed principal-attention and risk limits?

The protocol treats unattended operation as a property of a **delegation structure**, not as an intrinsic property of an agent.

## Basic problem dimensions

The design assumes three persistent sources of incompleteness:

1. **Normative non-closure** — what outcomes, trade-offs, and residual discretion are allowed is not always fully determined.
2. **Evidential non-closure** — relevant states, effects, and guarantee assumptions cannot always be reliably distinguished.
3. **Control non-closure** — required transitions and constraints cannot always be implemented or continuously maintained.

Adaptive optimization is treated as an **amplifier**: it can actively search for existing gaps, but it is not introduced as a fourth basic category.

## Protocol shape

For history (H_t), information state (q_t), assurance kernel (K), and proposed transition (T_t):

```text
Agent proposal
  -> admission: deny | hold | admit
  -> narrow capability
  -> constrained execution
  -> external observation / verification
  -> settlement, contraction, recovery, or reopen
```

An admission decision is history- and joint-state-dependent:

```text
Admit(T_t | H_t, q_t, K) -> {deny, hold, admit}
```

The protocol must account for composition, pending effects, time, shared resources, and adaptive agents. Per-action compliance is not assumed to compose automatically.

## Guarantee classes

The repository keeps three kinds of claims separate:

- **Structural guarantees**: deterministic or probabilistic claims derived under explicit assumptions.
- **Empirical reliability**: observed delivery, failure, unknown-result, intervention, and calibration distributions for a versioned deployment policy.
- **Deployment acceptance**: normative decisions about residual risk, attention cost, authorization, and responsibility.

A proof about the enforcement mechanism does not by itself establish that the enforced proxy implies the intended real-world property. A separate bridge obligation is required.

## Core conditional claim template

A deployment claim should make explicit:

[
orall Minmathcal M_{adaptive}, orall Einmathcal E_{Omega}:
Pr[	au_{0:H}(M,K,E)
otin I_D]learepsilon
]

with:

- (D): permitted task domain and reality-facing interfaces;
- (H): guarantee horizon and terminal treatment of unresolved effects;
- (I_D): the exact real-world trace property being claimed;
- (Omega): observation, execution, timing, isolation, composition, and semantic-bridge assumptions;
- (mathcal M_{adaptive}): agents allowed to know the policy and adapt to prior feedback;
- (mathcal E_{Omega}): environment behaviors allowed by the assumptions;
- (arepsilon): whether the bound is proved or empirically estimated.

## Main experiment

Compare, at the episode or shared-influence-domain level:

1. agent self-check only;
2. agent + external record / post-hoc audit;
3. agent + non-bypassable bounded admission, capability issuance, execution, verification, and exposure control.

Primary outcome:

> Under common attention budget (A) and risk limit (R), does the bounded protocol increase useful delivery or enlarge the set of delegable tasks, and does that gain persist as adaptive attack capability increases?

Safety and delivery are reported separately. Safe termination can be a safety success and a delivery failure.

## Repository map

- [domains/employee-offboarding.md](domains/employee-offboarding.md) — first concrete task-domain instance derived from AIOS Administrative offboarding.\n- [spec/protocol.md](spec/protocol.md) — protocol responsibilities and transitions.
- [spec/guarantees.md](spec/guarantees.md) — claim language, proof obligations, and assumption set.
- [spec/state-machine.md](spec/state-machine.md) — executable state semantics.
- [experiments/design.md](experiments/design.md) — falsifiable evaluation design.
- [baa_protocol/model.py](baa_protocol/model.py) — minimal generic reference state machine.\n- [baa_protocol/offboarding.py](baa_protocol/offboarding.py) — concrete employee-offboarding admission model.
- [tests/test_protocol_model.py](tests/test_protocol_model.py) — mechanical regression tests.

## Relationship to guide

[guide](https://github.com/xiongweilin/guide) supplies the conceptual inputs: local sufficiency (S(B,P,T)), action-semantic separation, revision, and reopening.

BAA-Protocol does not treat a sufficiency declaration as execution authority. It maps proposals into externally constrained, narrow reality-facing capabilities.

The engineering action-chain reference in [AIOS](https://github.com/xiongweilin/aios) is treated as a design reference, not as evidence that the properties in this repository are already implemented.

## Status

**Initial research prototype.**

Nothing in this repository should be read as a general proof of unattended autonomy, a complete safety framework, or an implementation certification. Each guarantee must state its assumptions, covered interfaces, excluded effects, evidence type, and falsification conditions.
