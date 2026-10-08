# P6 Real-Product BAA/AIOS Quality — First Descriptive Baseline

> English | [简体中文](p6-real-product-quality-baseline-v1.zh-CN.md)

**Status: qualified instrumentation with a tiny isolated-product sample; no SLO or long-run reliability claim.**

## Frozen provenance and scope

- AIOS [PR #40](https://github.com/xiongweilin/aios/pull/40), merged as `deb0ed6a22424150ce62d5d9b7234a5be43e328c`; acceptance branch head `73e1e229a8e24cf0c3853057cbe8b7b5a71ad074`.
- Four-scenario isolated real-product [Actions run 37713555933](https://github.com/xiongweilin/aios/actions/runs/37713555933): `normal`, `lost_ack`, `readback_outage`, `runtime_bypass`; **all passed**.
- The underlying real-product workflow pins BAA `b3215d940cf7c9bd6b208ed5915eaa3c92ab10e3`; do not confuse that executable pin with the later BAA evidence-archive HEAD.
- Ephemeral Keycloak/Odoo/World Runtime, no production identities. Each arm provisions an independent test environment and contributes only one case, not an estimate of production reliability.
- Quality artifact files: `p6-quality.json` beside each `evidence.json` in the existing scenario artifact.

## Measured outcomes

| Isolated arm | E2E accepted | Engine drives | Gate executes | Gate independent observes | Instrument complete |
|---|---|---:|---:|---:|---|
| normal | yes | 1 | 3 | 3 | yes |
| lost_ack | yes | 2 | 5 | 3 | yes |
| readback_outage | yes | 2 | 5 | 3 | yes |
| runtime_bypass | yes | 0 | 0 | 0 | yes |

The bypass arm tests a **different, direct World Runtime rejection path**. Zero BAA-gate samples there do not mean zero latency, absence of attempted bypass, or zero risk.

Selected **descriptive** stage medians from this single run:

| Stage (not isolated pure admission) | normal | lost_ack | readback_outage |
|---|---:|---:|---:|
| `engine_drive` P50 ms | 4618.072 | 2284.659 | 2244.206 |
| `gate_execute_including_admission_dispatch_readback` P50 ms | 775.020 | 210.390 | 205.933 |
| `gate_observe_including_independent_readback` P50 ms | 181.168 | 412.274 | 460.960 |

The gate-execute stage contains admission, provider dispatch and immediate read-back. It is **not** pure admission latency. Some lost-ack and outage attempts return `deferred` or `outcome_unknown`, causing lower medians than the normal case. The numbers **cannot** be read as a causal speedup.

Every stage reports `n`, P50/P95/P99, minimum, maximum, status counts and individual monotonic elapsed time. At `n=1..5`, P95/P99 are just interpolations of a few measurements; no SLO tail, throughput, error probability or uncertainty interval can be inferred. Startup/build time, CPU/memory/DB costs, external read-back cost, automated assurance labor and principal attention are **not yet measured**.

## Archived artifacts

| Scenario | Artifact ID | Archive SHA-256 |
|---|---|---|
| normal | `11522508523` | `6d0b5ac9f3e23687316175ab1714e84ba6c16fbd249efa3867338201055beddf` |
| lost_ack | `11522518523` | `468d79ac55b229929ed6ea9683bcece62831f348b187ae45d69bc75528e29b6c` |
| readback_outage | `11522743042` | `7b72473bd0e9e2a18855671d4c7eae01fdbf6216cecd4ef927e4b71a6ef0fe59` |
| runtime_bypass | `11522403758` | `94bad1dee51f8a91fb3dbb908989e9affce0134ee8195af365d209fe114a61a8` |

These are GitHub Actions **archive digests**, not claims about secrecy or independent attestation.

## Next decision boundary

The next P6 test must freeze a repeatable workload, concurrency/rate profile, warmup, fault schedule, data retention and **SLO thresholds before looking at outcomes**. Measure true stage-specific admission and post-effect-to-verification latency, memory/CPU/DB and per-provider costs, with sufficient repetitions and uncertainty. This first artifact just proves that the agreed stage categories can be collected without changing the accepted real-product offboarding path.

Separate from P3 joint-loss identifiability and P7 sustained deployment. Passing this baseline is **not** permission to start unattended production writes.
