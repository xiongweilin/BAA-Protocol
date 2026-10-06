# BAA-Protocol

> English | [简体中文](README.zh-CN.md)

[![Tests](https://github.com/xiongweilin/BAA-Protocol/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/xiongweilin/BAA-Protocol/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/github/license/xiongweilin/BAA-Protocol)](LICENSE)

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
- [experiments/prospective-model-protocol.md](experiments/prospective-model-protocol.md) — preregistered real-model study protocol.
- [experiments/prospective-model-result.md](experiments/prospective-model-result.md) — accepted v1 real-model null result.\n- [experiments/prospective-model-v2-result.md](experiments/prospective-model-v2-result.md) — v2 qualification failure.\n- [experiments/prospective-model-v3-result.md](experiments/prospective-model-v3-result.md) — v3 structured-output qualification failure and forced-function capability probe.\n- [experiments/prospective-model-v4-result.md](experiments/prospective-model-v4-result.md) — qualified forced-function v4 comparison.
- [experiments/delegation-frontier-baseline.md](experiments/delegation-frontier-baseline.md) — first common-budget deterministic delegation frontier.
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

**Executable reference prototype with pinned AIOS compatibility, execution-engine gating, isolated network recovery, real-product connector acceptance, composed real-product E2E acceptance, and a completed preregistered real-model comparison.**

The evidence chain now includes:

- AIOS workflow run `37302243172`: isolated HTTP/process/Docker network acceptance on `aios-windows-docker-desktop`, including lost acknowledgement, read-back outage, and unauthorized Runtime bypass;
- AIOS workflow runs `37306648690` and `37307582025`: standalone real ephemeral Keycloak and Odoo connector acceptance with separated writer/verifier identities;
- AIOS workflow run `37315551794`: one composed BAA -> AIOS -> World Runtime -> real ephemeral Keycloak/Odoo episode, with normal completion, lost-ack recovery, read-back-outage recovery, and unauthorized Runtime bypass. The composed run records independent product read-back, persisted recovery transitions, stable logical request identity, and verified external completion;
- AIOS workflow run `37393917221`: accepted preregistered v1 comparison; all three regimes were 6/7 delegable at C0/C1/C2, a retained frontier null result;\n- v2 failed model-evidence qualification; v3 failed structured-output interface qualification;\n- AIOS workflow run `37402587158`: qualified forced-function v4 comparison; all three regimes were 9/12 delegable at C0/C1/C2. Direct/audit produced 3 unsafe transitions at C1 and 4 at C2, while BAA remained at 0 through 2 and 3 automatic interventions respectively. This is a frontier null result with a positive finite safety-trajectory result.

These results do **not** establish production-tenant safety, production credential/infrastructure isolation, general unattended-autonomy safety, real-world failure probabilities, or production delegation leverage. The accepted v1 and v4 finite comparisons did not show delegation-frontier expansion. v2 and v3 are retained qualification failures. v4 did show that BAA prevented adaptive unsafe reality-facing transitions in already non-delegable episodes.

See [experiments/status.md](experiments/status.md).

## Project policies

See [Contributing](CONTRIBUTING.md), [Code of Conduct](CODE_OF_CONDUCT.md), [Security Policy](SECURITY.md), and the [MIT License](LICENSE).
