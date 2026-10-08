# P3 Offboarding Temporal Outcome — Protocol v1

> English | [简体中文](p3-offboarding-temporal-outcome-v1.zh-CN.md)

## Status and claim boundary

**Instrument and identification-design preregistration, not an accepted empirical calibration.**

This protocol freezes the first independent candidate loss endpoint for P3 before running a product-based calibration. The current code and tests exercise synthetic, explicitly labelled instrumentation fixtures. No observations from those fixtures are presented as real harm or as evidence for a risk-factor assignment.

The prior negative result in [Joint-Risk Identifiability v1](../formal/joint-risk-identifiability-v1.md) remains in force. `OFFBOARDING_RISK_FACTOR_IDS_V1` stays empty.

## Domain and units

The unit of analysis is an explicitly enrolled, cross-system-mapped **principal/subject** over a frozen horizon `[0,H)`. Every subject has one preregistered effective revocation time `t_eff`, a nonnegative allowed grace `g`, and a domain-approved statement of pre-revocation access entitlement.

The primary candidate endpoint is:

```text
Y_joint = sum over enumerated subjects
          integral over the scored time window
          1{joint observed permission state violates frozen temporal policy} dt
```

Unit: **subject-seconds**. The transition-grace interval `[t_eff,t_eff+g)` is **excluded by contract**, not presumed safe or attributed zero observed harm. Grace and uncertain durations are reported separately.

For subjects with explicitly approved pre-revocation access, before `t_eff` the expected projection is:

```text
HRIS active = true; IAM enabled = true; access probe = ALLOW
```

If the pre-revocation access entitlement is explicitly false, the expected probe is `DENY` instead. No minimum active-session count is assumed before effective time.

After the deadline `t_eff+g`, the expected projection is:

```text
HRIS active = false; IAM enabled = false;
active IAM sessions = 0; independent access probe = DENY
```

The joint endpoint counts violation if **any** required property is known false. If none is known false but at least one is unknown, the interval is **not identified**.

Two secondary endpoints must be retained independently:

1. `Y_access`: post-deadline time during which a qualified real access probe still succeeds.
2. `Y_disruption`: before-effective time during which a qualified access probe is denied despite a frozen pre-effective entitlement.

A product field such as `enabled=false` cannot substitute for a real access probe.

## Observation and provenance obligations

The intended study environment is isolated, with test subjects only, independent read-only credentials for HRIS, IAM/session observation, and an actual authorization/access probe. Every observation binds the enrolled cross-system identity, source, event time, collector identity/version, and a monotonic or bounded-clock uncertainty.

**Sampling at two endpoints does not establish what occurred between them.** An interval may be scored as known only when a separately qualified instrument supplies an *interval-continuity attestation*. The current `INTERVAL_ATTESTED` value is only a declared assertion in reference data; the Python model does not cryptographically or empirically establish its truth.

`SNAPSHOT_ONLY`, unavailable observations, unobserved gaps, incomplete product projections, and clock-boundary uncertainty produce bounds rather than invented values.

For each endpoint `Y` report `[Y_lower,Y_upper]`. A single numeric outcome is acceptable only when the bounds coincide under the declared assumptions. For uncertain timing within `epsilon_clock` of either policy boundary, the reference instrument conservatively reports uncertainty, not exact duration.

### Important engineering prerequisite

Before a real study, verify that the observation collector can support the intended continuity claim. Possibilities include trustworthy state-transition journals **plus** periodic reconciliation and active probes, or an equivalent bounded-latency observer with an explicit mathematical interpolation error bound. If the proposed collector only polls, the study must report interval bounds; it cannot relabel polling samples as continuous truth.

An unresolved physical access probe may reflect reachability, expiry, credential state, or infrastructure failure. Define the access probe's authentication, network baseline, and failure-disambiguation rules before relying on it as authorization evidence.

## Contrast arms and design

The prospective study must use isolated test identities, randomized comparable episodes or cluster-level allocation when shared state causes interference. At minimum:

- unchanged control and single-effect arms;
- same-principal two-effect and three-effect compositions;
- disjoint-principal multi-effect compositions;
- order and overlap contrasts under the same effective time;
- lost acknowledgement, delayed read-back, partial failure, and unavailable evidence as **observation/execution factors**, never automatically as losses.

Each effect, including an intentionally induced bad state, must remain within an approved isolated test environment. No real employee deactivation or tenant-wide privileged change is in scope.

## Competing structural hypotheses

Freeze the following *candidate factor partitions* before observing treatment outcomes:

- `F_distinct`: HRIS deactivate, IAM disable, IAM sessions revoke all distinct;
- `F_IAM_shared`: IAM disable and session revoke share one factor, HRIS separate;
- `F_all_shared`: all three share one factor.

Also predeclare an interaction family with `lambda=0` as a baseline and a bounded nonnegative candidate range. **These are hypotheses, not calibrated assignments.**

A comparison of measured `Y_joint` with output of the existing `pairwise-shared-factor-min-v1` formula is *invalid* until a separately justified mapping places formula outputs and `Y_joint` in commensurate units. Merely changing the unit label is insufficient.

An estimable *outcome interaction* in a randomized factorial design, for example

```text
J_AB = E[Y | A+B] - E[Y | A] - E[Y | B] + E[Y | control]
```

does **not by itself** establish the existing risk-factor registry or the pairwise-min penalty. Such a claim additionally requires competing model predictions, identified parameters, appropriate uncertainty analysis and independent validation on held-out episodes.

## Frozen qualification and acceptance decision

A product-data run is **qualified for outcome analysis** only if:

1. subject universe, cross-system identity mappings, temporal policy and horizon were frozen before execution;
2. collector independence and reader versus writer permissions were tested;
3. clock-error bound, interval coverage, missingness and probe reachability were recorded;
4. at least one known injected policy violation was detected, one compliant control did not false-positive, and at least one observation outage widened rather than erased uncertainty;
5. no metric was retrofitted from an observed favorable result;
6. full episodes, failed runs, qualified and unqualified observations remain in the denominator;
7. accepted training and hold-out evidence are disjoint at the cluster/failure-domain level.

A calibration claim needs more: a preregistered discriminating contrast showing that the competing models imply empirically distinguishable outcomes under stated power/uncertainty, and a hold-out test of these predictions.

If observations are insufficient or all candidate predictions remain observationally equivalent, the accepted conclusion is **non-identification**. A null outcome is not a reason to modify the factor partition, grace period, endpoint, or candidate penalty after seeing it.

## Version and stopping rule

- Instrument: `baa_protocol/temporal_outcome.py`, v1.
- Read-only polling collector: `baa_protocol/temporal_collector.py`; it preserves errors and provenance but emits **SNAPSHOT_ONLY**, never verified continuity.
- Reference tests: `tests/test_temporal_outcome.py`, `tests/test_temporal_collector.py`.
- Current stage: synthetic qualification only; **no product calibration and no registry update**.
- First product study must pin BAA, AIOS, collector, Keycloak/Odoo versions, workload hash, policy and probe configuration.
- Stop at this stage until a qualified independent collector and explicit safe test-tenant authorization exist.

## Separation from other work

P5 executable refinement and P6 quality/cost instrumentation can proceed in parallel. Neither finite model checking nor throughput benchmarks may be substituted for this independent outcome-identification requirement.
