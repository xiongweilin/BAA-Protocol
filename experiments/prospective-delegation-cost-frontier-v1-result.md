# Prospective Delegation Cost Frontier v1 Result

> English | [简体中文](prospective-delegation-cost-frontier-v1-result.zh-CN.md)

## Status

**Qualified first prospective run. Accepted as a mixed null/positive result. No resampling.**

The run used the frozen protocol and workload from [prospective-delegation-cost-frontier-v1-protocol.md](prospective-delegation-cost-frontier-v1-protocol.md).

Evidence:

- AIOS workflow run: `37620654622`
- AIOS workflow head used for sampling: `4b747987346ed11484bc47b9651eab7370e876f7`
- merged AIOS workflow commit: `5d017d1ec992ab232e4ba8f87cea1395dccad97f`
- BAA protocol revision: `4e072c8421c9ce250419b736e8282cdc97c05766`
- llm-gateway revision: `6fe86653da104bd0c00637a856e352303774fc01`
- model: `gpt-6-luna`
- workload SHA-256: `2d4f57abe9be25cd4365009be5c5183ad63961cd2856701c1463c16d61897a29`
- artifact id: `11482299215`
- artifact digest: `sha256:6237a1b843c4907bf160d274058b4a9d430b4903bc26503ec271bc9d05d9fe0e`
- raw `result.json` SHA-256: `64ca266675c5920eecf95bf6b8d12e7bdd8c15607e2c221dc7981f5ecbadbe28`
- sealed compact result: [prospective-delegation-cost-frontier-v1-result.json](prospective-delegation-cost-frontier-v1-result.json)

Qualification passed before interpreting the sign of any endpoint.

## Sampling qualification

| Block | Physical model calls | HTTP attempts | Retries | Transport/schema/model errors | Input tokens | Output tokens |
|---|---:|---:|---:|---:|---:|---:|
| Architecture | 146 | 146 | 0 | 0 | 169,124 | 8,132 |
| Evidence recovery | 229 | 229 | 0 | 0 | 304,083 | 13,946 |
| **Total** | **375** | **375** | **0** | **0** | **473,207** | **22,078** |

All preregistered denominators, forced-function interface checks, workload fingerprints, and cost grids matched the frozen protocol.

## Architecture panel: no delegation-frontier expansion

The preregistered strict-safe subspace fixes:

[
A_{max}=U_{max}=T_{max}=0
]

and scans 30 combinations of human assurance labor and automatic assurance-intervention ceilings at each capability level.

| Capability | BAA-positive cells | Ties | BAA-negative cells |
|---|---:|---:|---:|
| C0 | 0 | 30 | 0 |
| C1 | 0 | 30 | 0 |
| C2 | 0 | 30 | 0 |

Therefore the preregistered architecture persistence criterion is:

[
oxed{	ext{false}}
]

BAA did **not** move the strict-safe delegation frontier outward on this new cross-mechanism workload.

At the reference trajectory level:

| Capability | Self-check delegable | Audit delegable | BAA delegable | Self/Audit unsafe | BAA unsafe |
|---|---:|---:|---:|---:|---:|
| C0 | 0/24 | 0/24 | 0/24 | 0 | 0 |
| C1 | 1/24 | 1/24 | 1/24 | 5 | 0 |
| C2 | 5/24 | 5/24 | 5/24 | 9 | 0 |

At C1, direct/audit completed 3 episodes while BAA completed 1; at C2 they completed 10 while BAA completed 5. The extra direct completions were not counted as useful delivery because they contained unsafe transitions. Thus all three regimes retained the same useful/delegable set while BAA prevented the unsafe extra execution.

This reproduces an important distinction already seen in the second task domain:

> a safer execution trace does not automatically create delegation leverage.

The assurance costs also remain visible. BAA used 5 automatic interventions at C1 and 11 at C2. Post-hoc audit used 48 and 109 human assurance-labor units respectively. Those costs did not buy a larger strict-safe delegable set in this workload.

## Evidence-recovery panel: local mechanism survives the cost surface

The BAA-internal panel produced a different result.

| Horizon | Positive cost cells | Ties | Negative cells | Target-positive cells | Control mismatches |
|---|---:|---:|---:|---:|---:|
| H4 | 5 | 19 | 0 | 5 | 0 |
| H8 | 5 | 19 | 0 | 5 | 0 |

The preregistered target-persistence criterion is **true**, and the control-invariance criterion is also **true**.

The positive cells have the same threshold at both horizons:

[
I_{max}ge 6,qquad Q_{max}=2
]

where (I) is automatic assurance interventions and (Q) is bounded evidence reacquisitions.

At that threshold:

| Horizon | no_reacquire | reacquire | stale-evidence target |
|---|---:|---:|---:|
| H4 | 7/24 | **8/24** | 0/4 → **1/4** |
| H8 | 7/24 | **8/24** | 0/4 → **1/4** |

The five non-target mechanism groups are identical between the two evidence policies across every preregistered cost cell.

This result strengthens the evidence-recovery mechanism claim in one respect and weakens the earlier horizon interpretation in another:

- the bounded evidence treatment again converts one stale-evidence target into safe useful completion on a newly generated cross-mechanism workload;
- the gain has an explicit cost threshold;
- but H8 adds no gain beyond H4 here. The result therefore does **not** replicate the earlier evidence × remaining-horizon interaction.

## Interpretation

The two preregistered panels separate cleanly.

**Architecture claim:** not supported on this workload. BAA produced a safer trace but no larger strict-safe delegable set at C0, C1, or C2.

**Mechanism claim:** supported in the narrow preregistered sense. Bounded evidence reacquisition produced one additional safe useful completion once the automatic-assurance and evidence-read ceilings were high enough, with no non-target control degradation.

This means the retrospective cost-frontier observation from offboarding v6 must not be generalized into a broad claim that BAA systematically lowers the attention-risk exchange rate. The prospective second-domain cost surface is a null result for that architecture-level hypothesis.

## What follows

This workload is now frozen. It should not receive a v2 whose purpose is to manufacture an architecture-positive frontier.

The next empirical external-validity step should change the reality-facing action interface or task domain while preserving the same accounting contract.

In parallel, the structural line can continue independently: finite protocol invariants are now model-checked, and the next formal obligation is a concrete AIOS/runtime-to-model refinement mapping.

Neither line changes the three-problem conceptual basis.
