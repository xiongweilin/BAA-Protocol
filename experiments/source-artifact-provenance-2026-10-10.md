# Frozen CI artifact provenance snapshot — 2026-10-10

> English | [简体中文](source-artifact-provenance-2026-10-10.zh-CN.md)

This inventory records **original GitHub Actions artifact ZIP bytes**, not a new experiment or re-run. Each digest is SHA-256 over the ZIP itself, not the uncompressed JSON. On 2026-10-10 the six archives were downloaded from the cited successful runs. Their local copies are stored at `D:\infrastructure\data\evidence\BAA-Protocol\github-actions\2026-10-10\original-zips\`; the adjacent `manifest.json` records the artifact IDs, run IDs, byte counts, digests, and allowed use. All six local files match the listed byte counts and SHA-256 values. The preservation download did not extract or inspect archive contents. A hash list does **not** preserve artifact bytes; the local copies preserve them at the stated location as verified on this date.

| Original artifact / arm | Actions run | Artifact ID | ZIP bytes | ZIP SHA-256 | GitHub expiry (UTC) |
| --- | ---: | ---: | ---: | --- | --- |
| Offboarding prospective v6 | [37406741476](https://github.com/xiongweilin/aios/actions/runs/37406741476) | 11386984007 | 49151 | `28db9bb852eeba59d26b93687dd5c02dad6bb9b4d144c96cdacb8b5da5112ad4` | 2026-10-20 |
| Delegation cost frontier | [37620654622](https://github.com/xiongweilin/aios/actions/runs/37620654622) | 11482299215 | 68872 | `6237a1b843c4907bf160d274058b4a9d430b4903bc26503ec271bc9d05d9fe0e` | 2026-10-21 |
| Real product E2E — normal | [37713555933](https://github.com/xiongweilin/aios/actions/runs/37713555933) | 11522508523 | 14948 | `6d0b5ac9f3e23687316175ab1714e84ba6c16fbd249efa3867338201055beddf` | 2026-10-22 |
| Real product E2E — lost acknowledgment | [37713555933](https://github.com/xiongweilin/aios/actions/runs/37713555933) | 11522518523 | 15191 | `468d79ac55b229929ed6ea9683bcece62831f348b187ae45d69bc75528e29b6c` | 2026-10-22 |
| Real product E2E — readback outage | [37713555933](https://github.com/xiongweilin/aios/actions/runs/37713555933) | 11522743042 | 15327 | `7b72473bd0e9e2a18855671d4c7eae01fdbf6216cecd4ef927e4b71a6ef0fe59` | 2026-10-22 |
| Real product E2E — runtime bypass | [37713555933](https://github.com/xiongweilin/aios/actions/runs/37713555933) | 11522403758 | 12926 | `94bad1dee51f8a91fb3dbb908989e9affce0134ee8195af365d209fe114a61a8` | 2026-10-22 |

## Critical distinction

- The v6 ZIP contains `summary.json`, `result.json` with episode-level rows, and `gateway.json`; the cost-frontier ZIP contains the same kinds of files plus `workload.json`. E2E ZIPs contain `evidence.json`, `p6-quality.json`, process metadata, and service logs.
- The frozen reports and repository result summaries remain authoritative for qualified conclusions. Recomputed totals from copied records are **integrity cross-checks**, not additional independent real-model draws.
- The v6 observed +6 qualified C2 delegation episodes does not supersede the zero BAA-positive strict safe-cost cells in the subsequent frontier; the latter result explicitly narrows the efficiency claim.
- **Local preservation status:** the six checksum-verified ZIP copies are stored at `D:\infrastructure\data\evidence\BAA-Protocol\github-actions\2026-10-10\original-zips\`, outside Git, with a local `manifest.json`. This is a local copy; no independent backup or restore was verified. The directory's access-control status has not been qualified, and archive logs were not reviewed here. Do not publish the raw ZIPs without secret/log review and appropriate redaction.
- No participant data, production authorization, long-horizon reliability or realized human-hours benefit is supplied by this snapshot.

## Verify a retained original ZIP

```bash
sha256sum downloaded-original.zip
unzip -l downloaded-original.zip
```

Compare the byte count and ZIP digest above. Matching those values confirms only an identical archive, not the truth or generality of the experiment.
