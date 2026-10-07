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

- [domains/employee-offboarding.md](domains/employee-offboarding.md) — first task-domain boundary, assumptions, invariants, and experiment.
- [domains/canary-release-promotion.md](domains/canary-release-promotion.md) — second task domain: progressive traffic exposure with evidence gates and rollback.
- [spec/protocol.md](spec/protocol.md) — admission and execution protocol.
- [spec/guarantees.md](spec/guarantees.md) — proof obligations and claim language.
- [spec/state-machine.md](spec/state-machine.md) — protocol state semantics.
- [spec/vsar.md](spec/vsar.md) — Versioned Sufficiency Assurance Record.
- [experiments/design.md](experiments/design.md) — falsifiable experiment design.
- [experiments/prospective-model-protocol.md](experiments/prospective-model-protocol.md) — preregistered real-model study protocol.
- [experiments/prospective-model-result.md](experiments/prospective-model-result.md) — accepted v1 real-model null result.
- [experiments/prospective-model-v2-result.md](experiments/prospective-model-v2-result.md) — v2 qualification failure.
- [experiments/prospective-model-v3-result.md](experiments/prospective-model-v3-result.md) — v3 structured-output qualification failure and forced-function capability probe.
- [experiments/prospective-model-v4-result.md](experiments/prospective-model-v4-result.md) — qualified forced-function v4 comparison.
- [experiments/prospective-model-v5-protocol.md](experiments/prospective-model-v5-protocol.md) — preregistered recovery/liveness follow-up.
- [experiments/prospective-model-v5-result.md](experiments/prospective-model-v5-result.md) — qualified finite delegation-frontier expansion under preregistered recovery events.
- [experiments/prospective-model-v6-protocol.md](experiments/prospective-model-v6-protocol.md) — preregistered 24-episode prospective generalization study.
- [experiments/prospective-model-v6-result.md](experiments/prospective-model-v6-result.md) — qualified +6 C2 aggregate frontier expansion; preregistered cross-mechanism evidence-refresh generalization criterion not met.
- [experiments/prospective-canary-v1-protocol.md](experiments/prospective-canary-v1-protocol.md) — preregistered first real-model study in the second BAA task domain.
- [experiments/prospective-canary-v1-result.md](experiments/prospective-canary-v1-result.md) — qualified second-domain result: C2 Delta = -1, zero BAA unsafe transitions, and no cross-domain frontier expansion.
- [experiments/prospective-canary-v2-feedback-protocol.md](experiments/prospective-canary-v2-feedback-protocol.md) — preregistered mechanism study of assurance-feedback quality versus adaptive horizon.
- [experiments/prospective-canary-v2-feedback-result.md](experiments/prospective-canary-v2-feedback-result.md) — qualified null feedback/horizon result: stale-route remained 1/3 at H4/H8 with zero unsafe transitions.
- [experiments/prospective-canary-v3-evidence-protocol.md](experiments/prospective-canary-v3-evidence-protocol.md) — preregistered H4 evidence-reacquisition mechanism study; retention-only draft was superseded before any v3 sampling.
- [experiments/prospective-canary-v3-evidence-result.md](experiments/prospective-canary-v3-evidence-result.md) — qualified H4 null frontier result with one causal process-level repair from stale-evidence hold to a safely verified sequential transition.
- [experiments/prospective-canary-v4-evidence-horizon-protocol.md](experiments/prospective-canary-v4-evidence-horizon-protocol.md) — preregistered 2×2 evidence-recovery × H4/H8 interaction study.
- [experiments/prospective-canary-v4-evidence-horizon-result.md](experiments/prospective-canary-v4-evidence-horizon-result.md) — qualified positive interaction: stale-route contrast grows from 0 at H4 to +1 at H8 with zero unsafe transitions.
- [experiments/prospective-canary-v5-robustness-protocol.md](experiments/prospective-canary-v5-robustness-protocol.md) — preregistered 24-episode robustness study generated from a frozen parameter grid.
- [experiments/prospective-canary-v5-robustness-result.md](experiments/prospective-canary-v5-robustness-result.md) — qualified mixed robustness result: aggregate interaction +1, but only 1/3 preregistered timing strata is positive, so the strong robustness criterion is not met.
- [experiments/delegation-frontier-baseline.md](experiments/delegation-frontier-baseline.md) — first common-budget deterministic delegation frontier.
- [experiments/delegation-cost-frontier-v1-protocol.md](experiments/delegation-cost-frontier-v1-protocol.md) — frozen retrospective cost-frontier accounting contract over accepted real-model traces.
- [experiments/delegation-cost-frontier-v1-baseline.md](experiments/delegation-cost-frontier-v1-baseline.md) — observed attention/risk/assurance cost surface from offboarding v6 and canary v5.
- [experiments/prospective-delegation-cost-frontier-v1-protocol.md](experiments/prospective-delegation-cost-frontier-v1-protocol.md) — preregistered prospective cost-frontier study on a new 24-episode cross-mechanism canary workload.
- [experiments/status.md](experiments/status.md) — current evidence level and convergence boundary.
- [baa_protocol/model.py](baa_protocol/model.py) — generic reference model.
- [baa_protocol/offboarding.py](baa_protocol/offboarding.py) — employee-offboarding kernel.
- [baa_protocol/experiment.py](baa_protocol/experiment.py) — three-regime episode harness.
- [baa_protocol/aios_adapter.py](baa_protocol/aios_adapter.py) — thin AIOS-to-BAA projection.
- [integration/README.md](integration/README.md) — current AIOS integration boundary and remaining claims.
- [integration/test_aios_offboarding_contract.py](integration/test_aios_offboarding_contract.py) — pinned AIOS compatibility checks.
- [integration/aios_gate.py](integration/aios_gate.py) — BAA gate on the real AIOS EffectProvider boundary.
- [integration/test_aios_runtime_gate.py](integration/test_aios_runtime_gate.py) — real AIOS offboarding-engine gate tests.
- [formal/structural-guarantees-v1.md](formal/structural-guarantees-v1.md) — finite-state structural guarantee record, explicit assumptions, and refinement boundary.\n- [formal/structural-model-v1-result.json](formal/structural-model-v1-result.json) — machine-readable exhaustive model-check result.\n- [tests](tests) — regression and finite exhaustive checks.

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
- AIOS workflow run `37393917221`: accepted preregistered v1 comparison; all three regimes were 6/7 delegable at C0/C1/C2, a retained frontier null result;
- v2 failed model-evidence qualification; v3 failed structured-output interface qualification;
- AIOS workflow run `37402587158`: qualified forced-function v4 comparison; all three regimes were 9/12 delegable at C0/C1/C2. Direct/audit produced adaptive unsafe transitions while BAA remained at 0; this is a frontier null result with a positive finite safety-trajectory result;
- AIOS workflow run `37404551022`: qualified recovery-focused v5 comparison. C0/C1 remained 9/12 for all regimes; at C2 self-check/audit remained 9/12 while BAA reached **12/12 delegable**, with equal aggregate useful delivery (36), zero BAA unsafe transitions, and five direct/audit unsafe transitions.
- AIOS workflow run `37406741476`: first fully qualified v6 result on the frozen 24-episode workload. At C2 self-check/audit were 14/24 delegable and BAA was **20/24**, so the preregistered aggregate endpoint was Delta_C2 = +6. The gain was localized to time_recovery (+4) and readback_recovery (+2); subject/authority evidence-refresh strata showed no BAA-only gain, so the stronger preregistered cross-mechanism generalization criterion was not met.
- AIOS workflow run `37410377327`: first fully qualified second-domain canary result. At C2 self-check/audit were **11/18 delegable** and BAA was 10/18, so the preregistered endpoint was Delta_C2 = -1. BAA had 0 unsafe transitions versus 2 for each direct regime, but did not recover liveness in stale_route_refresh and therefore did not establish cross-domain delegation-frontier expansion.
- AIOS workflow run `37412693511`: first fully qualified corrected canary v2 feedback/horizon result. At H4 minimal/diagnostic/corrective were all 10/18 aggregate and 1/3 stale-route delegable, so the preregistered feedback endpoint was 0. Diagnostic H8 remained 1/3 stale-route, so the horizon contrast was also 0. Every cell retained zero unsafe transitions.
- AIOS workflow run `37438662474`: first fully qualified transport-amended canary v3 evidence-reacquisition result. H4 remained 11/18 overall and 1/3 stale-route delegable in both treatments, with zero unsafe transitions. The treated `stale-route-refresh-b` episode nevertheless moved from the exact stale-evidence hold to one safely admitted and verified sequential transition after a bounded evidence reacquisition; the H4 window ended before the remaining stage could complete.
- AIOS workflow run `37457822676`: first fully qualified canary v4 evidence×horizon result. The preregistered stale-route interaction was **+1**: both evidence policies were 0/3 stale-route delegable at H4; at H8 `no_reacquire` remained 0/3 while `reacquire` reached **1/3**, with aggregate delegability 11/18 versus **12/18**, zero unsafe transitions in all four cells, and unchanged 11/15 non-stale H8 delegability.
- AIOS workflow run `37466492295`: first fully qualified canary v5 robustness result on the prospectively generated 24-episode grid. Aggregate recovery interaction was **+1**, controls did not degrade, and unsafe transitions stayed 0; however only the mid timing stratum had positive interaction, so the preregistered strong robustness criterion was **not met**.

These results do **not** establish production-tenant safety, production credential/infrastructure isolation, general unattended-autonomy safety, real-world failure probabilities, or population-level production delegation leverage. v1 and v4 retained frontier null results; v2 and v3 are qualification failures. v5 provides the first qualified finite delegation-frontier expansion. v6 prospectively reproduces an aggregate expansion on a new offboarding workload but does not establish the stronger preregistered evidence-refresh cross-mechanism generalization claim. Canary v1 then provides the first qualified second-domain counterexample: BAA improves the safety trace but produces a negative C2 frontier endpoint because safe blocking does not reliably recover liveness. Canary v2 shows that neither richer mechanical feedback nor H8 adaptive time alone repairs the frozen stale-route endpoint. Canary v3 shows that bounded current-route evidence reacquisition can repair a local stale-evidence transition without expanding the H4 frontier. Canary v4 then finds a positive preregistered evidence×horizon interaction: one stale-route episode safely completes only when reacquisition is combined with enough remaining H8 interaction time. This is a mechanism result inside BAA, not a new BAA-versus-direct comparison. None of these results estimates production frequency.

See [experiments/status.md](experiments/status.md).

## Project policies

See [Contributing](CONTRIBUTING.md), [Code of Conduct](CODE_OF_CONDUCT.md), [Security Policy](SECURITY.md), and the [MIT License](LICENSE).
