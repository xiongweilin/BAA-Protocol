# Contingent policy v1 — bounded research-code merge acceptance

Date: 2026-10-10. **Accept research compiler + standalone staging contract only, not validated production autonomy or measured C0/C1/C2 advantage.**

## Immutable candidates and test evidence

- Repository `xiongweilin/BAA-Protocol`, [PR #92](https://github.com/xiongweilin/BAA-Protocol/pull/92).
- Core examined BAA HEAD `91b3280c5703fe248849f170d6a99accaf9799b0`. Final cross-repo acceptance used BAA checkout incorporating pin-to-merged-AIOS commit `b5c3b09de9b6903bc7da6f185108f55b30237b21` (workflow tested with GitHub PR merge ref).
- **Immutable AIOS integration version:** `d68e77f4343ed798c6c0b8d29a007858dbcc908f`, [AIOS PR #53 merged](https://github.com/xiongweilin/aios/pull/53). The BAA experimental contract workflow checks out this **specific commit**, never a moving `research/*` branch.
- [BAA reference test run 38053957949](https://github.com/xiongweilin/BAA-Protocol/actions/runs/38053957949): **254 tests passed** on the pinned-integration candidate, including 300 seeded synthetic adversarial world-model comparisons against a separately implemented exhaustive AND/OR minimum-worst-cost oracle.
- [Pinned BAA→merged AIOS integration run 38053957940](https://github.com/xiongweilin/BAA-Protocol/actions/runs/38053957940): successful checkout of the exact merged AIOS SHA, **22 Python AIOS boundary tests** on the pair, followed by compiled policy execution-cursor contract with both qualified observation branches, unknown-effect readback/reconciliation, anti-blind-replay and renewed authorization.
- [BAA full protocol test run 38053955299](https://github.com/xiongweilin/BAA-Protocol/actions/runs/38053955299): reference model plus current-main and pinned AIOS compatibility all green; required `aios-compatibility` aggregator retained.

## Claims that passed the bounded gates

| Claim | Evidence | Disposition |
| --- | --- | --- |
| The finite planner constructs every-branch-qualified policies with no modeled unsafe successor | Model-relative independent checker and negative forged-policy tests | **Accepted conditional on full/correct model inputs** |
| Worst-case cost is minimum among enumerated finite safe candidate trees, with declared cost/horizon and no repeat of an effect on its branch | 300 deterministic oracle comparisons; tamper-proof cost checker test | **Accepted only for tested discrete model and stated algorithm constraints** |
| The AIOS staging cursor rejects stale/currently unauthorized effects, missing branches, mutating policy trees and replay | 22 paired adversarial tests against immutable merged AIOS commit | **Accepted as no-provider-write staging behavior** |
| Unknown effects can be read back and reconciled safely instead of blindly retried | Cross-repo positive/negative branch contract plus AIOS readback E2E | **Accepted on isolated fixtures; not an external truth oracle** |
| C0/C1/C2 have improved versus a matched strongest active-planning baseline | No frozen fresh strong-baseline trial exists | **NOT ACCEPTED** |
| The planner improves real labor cost, tenant safety or unattended delivery | No authorized production trial; interface still staged | **NOT ACCEPTED** |

## Failure boundaries / release blockers, explicitly out of scope of code merge

The enumerated possible-world set must overapproximate **all real relevant conditions**. Effects, authorized operations and probes are **external assumptions**; the planner does not mint capabilities, keep persistent durable effect state, calibrate production risks, or independently verify the outside world. The existing BAA admission and AIOS World Runtime remain mandatory for every actual write. The new cursor is not a production autonomous worker.

Historical frozen v6 and strict-safe cost-frontier null results remain preserved and unchanged; read them via [claim/evidence index](claim-evidence-index.md) and [source artifact provenance](source-artifact-provenance-2026-10-10.md). Locally preserved raw evidence archives are not silently replaced by these tests.

**Code merge gate:** final checks on the documentation-containing BAA tree must pass, the AIOS SHA pin must remain as written, and PR SHA must be checked at merge. Subsequent production activation and C0/C1/C2 performance claims are **separate closed-by-evidence gates**, not auto-approved here.
