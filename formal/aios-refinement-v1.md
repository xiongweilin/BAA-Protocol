# AIOS Refinement Mapping v1

> English | [简体中文](aios-refinement-v1.zh-CN.md)

## Status

This document records the first executable **finite trace refinement check** from the pinned AIOS offboarding execution path into the phase vocabulary of the BAA structural model.

It is narrower than the finite-state model check in [structural-guarantees-v1.md](structural-guarantees-v1.md):

- structural v1 exhaustively checks the abstract transition system itself;
- refinement v1 checks that three concrete AIOS/BAA integration traces project into allowed abstract phase transitions.

It is not a whole-program refinement proof.

## Concrete boundary

The checked concrete path is:

~~~text
AIOS OffboardingExecutionEngine
  -> BAAGatedAIOSProvider
  -> OffboardingKernel admission
  -> narrow capability execution
  -> EffectProvider
  -> independent/post-dispatch observation
  -> OffboardingKernel verification
~~~

The test uses the pinned AIOS integration surface already exercised by `integration/test_aios_runtime_gate.py`.

## Projection

The refinement checker directly reuses `baa_protocol.formal_model.Phase`.

| Concrete event | Abstract phase transition |
|---|---|
| BAA admits the AIOS effect and issues the narrow capability | `PROPOSED -> RESERVED` |
| BAA records execution before provider dispatch | `RESERVED -> PENDING` |
| observation is unavailable while outcome remains ambiguous | `PENDING -> PENDING` |
| post-dispatch or later independent read-back verifies the outcome | `PENDING -> SETTLED` |

Non-authorizing HOLD/DENY behavior is treated as abstract stuttering before a reality-facing capability exists and is not required to appear in the projected trace.

Every reality-facing projection event also carries:

- effect id;
- proposal id;
- obligation id;
- target system;
- operation;
- stable request identity.

The checker rejects non-contiguous phase sequences and scope-less reality-facing events.

## Checked concrete traces

### Normal completion

Three offboarding external effects execute through the real AIOS engine fixture.

For each effect the projected path is:

[
PROPOSED 	o RESERVED 	o PENDING 	o SETTLED
]

All three effects settle and the AIOS case reaches completion.

### Lost acknowledgement with independent read-back

The first provider write occurs but its acknowledgement is lost.

The trace first reaches `PENDING`. Independent read-back then settles that same effect before later effects are released. The first logical effect is not dispatched twice.

After reconciliation, the remaining effects execute and all projected effects end in `SETTLED`.

### Outcome unknown without usable read-back

The first provider attempt returns an ambiguous outcome and no independent observation is available.

The projected trace reaches `PENDING` and remains there across repeated AIOS reconciliation attempts.

The underlying provider invocation count remains one. No second reality-facing dispatch occurs while the original effect remains unresolved.

## Refinement claim

For the three checked fixtures:

[
pi(	au_{mathrm{AIOS+gate}})
in
operatorname{Trace}(K_{mathrm{formal-v1}})
]

with respect to the represented phase relation and scope identity.

This is a tested trace relation, not a universal quantification over every AIOS execution.

## Explicit assumptions

The refinement claim assumes:

1. every covered offboarding provider call passes through `BAAGatedAIOSProvider`;
2. AIOS effect identity, obligation identity, authority epoch, target, operation, and request identity are stable for the checked execution;
3. the gate's independent observation is the observation channel used to resolve effect ambiguity;
4. no uninstrumented path mutates the same external effect while the abstract effect is pending;
5. the pinned AIOS semantics used by the tests match the deployed interface being discussed.

If any of these fail, the tested refinement relation does not establish the deployed behavior.

## What remains outside v1

This refinement check does not yet prove:

- complete mediation across the deployed World Runtime HTTP boundary;
- that runtime authorization/resource/version bindings refine the formal capability tuple for all calls;
- concurrency refinement;
- crash/restart refinement across independently persisted BAA and AIOS state;
- Keycloak/Odoo connector refinement;
- exposure/risk-budget refinement, because the offboarding gate currently uses obligation-level unresolved bounds rather than the generic formal risk ledger;
- the semantic bridge from verified product state to every real-world harm dimension.

The next structural step should therefore extend the mapping to the pinned World Runtime invocation and reconciliation records, rather than add more abstract phases.
