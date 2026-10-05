# BAA-Protocol

**Bounded Action Admission Protocol**

BAA-Protocol studies whether a non-bypassable admission and execution protocol can increase useful delegated work under fixed attention and risk constraints.

It is not a general safety claim. The repository states, implements, and attempts to falsify conditional guarantees.

## Research question

Given the same model, task distribution, and reality-facing interfaces, does bounded action admission enlarge the set of tasks that can be completed under fixed principal-attention and risk limits?

Unattended operation is treated as a property of a **delegation structure**, not as an intrinsic property of an agent.

## Basic problem dimensions

1. **Normative non-closure** — allowed outcomes, trade-offs, and residual discretion are not always fully determined.
2. **Evidential non-closure** — relevant states, effects, and guarantee assumptions cannot always be reliably distinguished.
3. **Control non-closure** — required transitions and constraints cannot always be implemented or continuously maintained.

Adaptive optimization is an **amplifier** that can actively search existing gaps; it is not introduced as a fourth basic category.

## Protocol

~~~text
Agent proposal
  -> admission: deny | hold | admit
  -> narrow capability
  -> constrained execution
  -> external observation / verification
  -> settlement, contraction, recovery, or reopen
~~~

Admission is history- and joint-state-dependent:

~~~text
Admit(T_t | H_t, q_t, K) -> {deny, hold, admit}
~~~

The protocol explicitly handles composition, pending effects, time, shared resources, partial observability, and adaptive agents.

## Guarantee classes

- **Structural guarantee** — deterministic or probabilistic claim derived under explicit assumptions.
- **Empirical reliability** — observed delivery, failure, unknown-result, intervention, and calibration distribution for a versioned deployment policy.
- **Deployment acceptance** — normative decision about residual risk, attention cost, authorization, and responsibility.

Enforcement of a kernel property does not by itself prove the intended real-world property; a separate semantic-bridge obligation is required.

A material claim must identify the task domain, guarantee horizon, exact trace property, assumption set, adaptive-agent class, environment class, and whether any probability bound is proved or empirically estimated.

## Main experiment

Compare at the episode or shared-influence-domain level:

1. agent self-check;
2. agent + external record / post-hoc audit;
3. agent + non-bypassable admission, narrow capability, constrained execution, verification, and exposure control.

Primary question:

> Under common attention budget A and risk limit R, does BAA increase useful delivery or enlarge the delegable task set, and does that gain persist as adaptive attack capability increases?

Safety and delivery are reported separately.

## First concrete domain

The first domain is **employee offboarding**, derived from this pinned AIOS snapshot:

~~~text
xiongweilin/aios@87f24f32a01c67a9246fc3cb127517c80798e169
~~~

Compatibility CI checks:

- the AIOS offboarding policy effect set;
- AIOS-derived external obligations;
- reality postconditions;
- World Runtime capability names;
- BAA execution over projected AIOS obligations.

Passing compatibility means that the BAA projection matches this pinned AIOS contract surface. It does **not** certify production AIOS, HRIS, IAM, or the semantic bridge.

## Repository map

- [domains/employee-offboarding.md](domains/employee-offboarding.md) — task-domain boundary, assumptions, invariants, and experiment.
- [spec/protocol.md](spec/protocol.md) — admission and execution protocol.
- [spec/guarantees.md](spec/guarantees.md) — proof obligations and claim language.
- [spec/state-machine.md](spec/state-machine.md) — protocol state semantics.
- [spec/vsar.md](spec/vsar.md) — Versioned Sufficiency Assurance Record.
- [experiments/design.md](experiments/design.md) — falsifiable experiment design.
- [experiments/status.md](experiments/status.md) — current evidence level and convergence boundary.
- [baa_protocol/model.py](baa_protocol/model.py) — generic reference model.
- [baa_protocol/offboarding.py](baa_protocol/offboarding.py) — employee-offboarding kernel.
- [baa_protocol/experiment.py](baa_protocol/experiment.py) — three-regime episode harness.
- [baa_protocol/aios_adapter.py](baa_protocol/aios_adapter.py) — thin AIOS-to-BAA projection.
- [integration/README.md](integration/README.md) — current AIOS integration boundary and remaining claims.
- [integration/test_aios_offboarding_contract.py](integration/test_aios_offboarding_contract.py) — pinned AIOS compatibility checks.
- [integration/aios_gate.py](integration/aios_gate.py) — BAA gate on the real AIOS EffectProvider boundary.
- [integration/test_aios_runtime_gate.py](integration/test_aios_runtime_gate.py) — real AIOS offboarding-engine gate tests.
- [tests](tests) — regression and finite exhaustive checks.

## Relationship to guide and AIOS

[guide](https://github.com/xiongweilin/guide) supplies conceptual inputs such as local sufficiency, action-semantic separation, revision, and reopening.

[AIOS](https://github.com/xiongweilin/aios) supplies the first concrete domain contract surface.

BAA does not treat a sufficiency declaration as execution authority and does not redefine AIOS semantics.

## Status

**Executable reference prototype with pinned AIOS compatibility, execution-engine gating, isolated network recovery, and single-episode real-product end-to-end acceptance.**

Current evidence includes isolated network run `37302243172`, standalone real Keycloak/Odoo connector runs `37306648690` and `37307582025`, and real-product end-to-end matrix run `37315551794`. The E2E matrix composes BAA, the AIOS offboarding engine, World Runtime, real ephemeral Keycloak and Odoo, independent verifier credentials, semantic postcondition checking, durable request identities, recovery after lost acknowledgement/read-back outage, and an authorization-boundary bypass rejection. It does not establish production-tenant safety, production delegation leverage, real-world failure probabilities, or a general unattended-autonomy theorem.

See [experiments/status.md](experiments/status.md).
