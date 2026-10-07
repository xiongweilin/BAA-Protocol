# Joint-Risk Binding Contract v1

> English | [简体中文](joint-risk-binding-contract-v1.zh-CN.md)

## Status

This record isolates the final semantic step between concrete exposure declarations and the frozen structural-v1 joint-risk calculation.

A concrete exposure metric and bound do not determine a risk-factor identity. Likewise, matching the structural formula does not justify that the formula represents real harm.

The executable binding contract is in `baa_protocol/risk_bridge.py`; regression tests are in `tests/test_joint_risk_binding.py`.

## Frozen structural functional

The contract recognizes one functional identity:

`pairwise-shared-factor-min-v1`

For bound risk terms `(b_i, f_i)` and non-negative interaction penalty `lambda`:

`risk = sum(b_i) + lambda * sum(min(b_i, b_j) for pairs with f_i == f_j)`

The executable function reproduces the same calculation used by `FiniteBAAModel`.

This establishes formula identity only. It does not establish calibration.

## Exact term binding

Before an exposure declaration may become a joint-risk term, a separate risk-factor declaration must bind:

- the same proposal id;
- the same exposure metric id;
- a non-empty risk-factor id;
- the supported joint-risk functional id.

Proposal identity rebound, metric identity rebound, empty risk factor, and functional substitution all fail closed.

The resulting bound risk term retains proposal id, exposure metric id, exposure bound, risk-factor id, and functional id.

At composition time, the evaluator also rejects **duplicate proposal ids** and **mixed exposure metric ids**. Exact binding of each term does not authorize adding heterogeneous units (such as subject counts and monetary losses). Cross-metric composition requires an independently justified common unit or explicit conversion and is outside v1.

## Current offboarding result: uncalibrated

The three reference offboarding proposal classes now have concrete exposure declarations, but they do **not** have calibrated risk-factor declarations.

`OFFBOARDING_RISK_FACTOR_IDS_V1` is intentionally empty.

Therefore:

- `employee.deactivate`;
- `identity.disable`;
- `sessions.revoke`

cannot currently be projected into the structural joint-risk functional through this bridge.

This is intentional. Assigning HRIS and IAM effects to the same or different risk factors would encode a substantive dependence claim. The repository does not currently have evidence that justifies that choice.

## Interaction penalty remains separate

Even after risk-factor identities are declared, the interaction penalty remains an independent calibration parameter.

The executable test demonstrates the same two unit exposures with one shared factor produce:

- penalty 0 -> risk 2;
- penalty 1 -> risk 3;
- penalty 2 -> risk 4.

No value is selected for concrete offboarding by this contract.

## Relation to prior exposure layers

The semantic chain is now separated into distinct obligations:

`proposal class -> exposure metric/bound -> reality-side measurement -> risk-factor identity -> joint-risk functional`

The repository has frozen the first step for the three offboarding operations and has an exact contract for the later binding steps.

The accepted chain still lacks:

1. an accepted scope-complete reality-side measurement source for the observable metric; and
2. calibrated offboarding risk-factor identities and interaction semantics.

## Claim boundary

This result does not establish:

- which offboarding operations share a real risk factor;
- whether HRIS and IAM effects are independent or dependent;
- a concrete interaction penalty;
- that the pairwise-min functional represents real harm;
- that the observable exposure metric has the right severity semantics;
- production risk probabilities or safety.

It establishes only an exact, fail-closed bridge from an explicitly declared exposure term plus an explicitly declared risk factor into the already frozen structural formula.

## Next structural obligation

The remaining semantic work is empirical/domain-theoretic rather than another wiring layer:

1. accept or reject a scope-complete measurement source for the frozen exposure metric;
2. define evidence-backed risk-factor identities for the concrete offboarding effects;
3. justify or falsify the pairwise interaction form and penalty.

Until then, the structural joint-risk guarantee remains conditional on explicit Omega assumptions.
