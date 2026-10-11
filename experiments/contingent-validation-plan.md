# Conditional-policy validation: two distinct evidence gates

> English | [简体中文](contingent-validation-plan.zh-CN.md)

Status: **research branch, no new real-model or human observations.** The two
below are different tests; neither replaces the frozen v6 and cost-frontier
results.

## 1. Synthetic model-bridge perturbations (executable)

Run `PYTHONPATH=. python scripts/run_contingent_model_stress.py` and
`python -m unittest tests/test_contingent_model_stress.py`.

Five fixed adversarial perturbations examine whether a policy that is valid
under one *declared* model is rejected after a materially relevant assumption
is changed:

- an omitted initial possible world;
- an unreported unsafe provider successor;
- revoked current authorization;
- a newly admitted pending/unknown outcome;
- a probe whose qualification has been withdrawn.

**Expected diagnostic:** the old policy fails independent requalification for
each changed model. Passing these checks does not prove the original model
covers reality, that authorization cannot change, or that the effect has been
observed outside the test fixture. Do not count these cases as empirical draws.

## 2. Paired strong-contingent-planner study (instrument only)

Before any outcomes, freeze an independent task source, workload SHA-256,
task-unit and clustering rules, versions, sampling/allocation, strong active
contingent-planning comparator, authorization/observation resources, effect
limits, adaptive horizon, failure/unknown handling, human time instrument,
effect readback and outcome oracle. The comparator must be allowed to
conditionally plan, reacquire qualified evidence and recover from ambiguity
under the **same** rights and budgets. Do not use an intentionally weak
self-check or after-the-fact audit as the only control.

Input to `python scripts/analyze_contingent_strong_baseline.py frozen.csv` has
one `baa` and one `strong_control` row per assigned case. Required columns
are defined in `REQUIRED` in that script. It checks equality of the frozen
task SHA, information cutoff, model ID, authorization-policy fingerprint,
probe/effect budgets, horizon and review budget. It retains every assigned
case, including unsafe, incomplete, and unknown outcomes. Per-task human work
is principal + independent assurance + operations person-seconds, with missing
components left unknown, **not zero**. Strict safe useful delivery requires
known-safe execution, useful delivery, and no terminal unknown effects.
Unresolved terminal effects with otherwise safe/useful recorded status remain
**unknown**, not a known failure. Witnessed unsafe execution or known-incomplete
delivery is a known negative. Discrete operation/effect/call counts must be
nonnegative integers; fractional or nonfinite counts fail validation.

This analyzer cannot authenticate the rows, prove independently measured
real-world safety, verify comparator competence, validate model calls or
establish randomization and blinding. Human time must be measured separately
from token/call counts, and a proposed minimum meaningful effect must be
chosen from task costs *before* the study.

**Current claim:** tools and synthetic regression fixtures exist. No
BAA-versus-strong-control real task benefit has been demonstrated here.
