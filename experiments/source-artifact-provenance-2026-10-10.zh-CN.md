# 冻结 CI 原始产物来源记录 — 2026-10-10

> [English](source-artifact-provenance-2026-10-10.md) | 简体中文

本表记录的是 GitHub Actions **原始 artifact ZIP 字节**，不是新增实验或重跑。SHA-256 针对 ZIP 本身而非内部 JSON。2026-10-10 已从表中对应运行下载六份原始档案，副本保存在 `D:\infrastructure\data\evidence\BAA-Protocol\github-actions\2026-10-10\original-zips\`；同目录 `manifest.json` 记录 artifact ID、run ID、字节数、摘要和允许用途。六个本地文件的字节数与 SHA-256 均匹配本表。此次保全下载没有解包或查看档案内容。**SHA-256 清单本身不保存 ZIP 字节；本地副本只证明该目录在本次校验时保存了这些字节。**

| 原始运行 | Actions run | Artifact ID | ZIP 字节数 | ZIP SHA-256 | GitHub UTC 到期 |
| --- | ---: | ---: | ---: | --- | --- |
| 离职任务前瞻 v6 | [37406741476](https://github.com/xiongweilin/aios/actions/runs/37406741476) | 11386984007 | 49151 | `28db9bb852eeba59d26b93687dd5c02dad6bb9b4d144c96cdacb8b5da5112ad4` | 2026-10-20 |
| 委托成本前沿 | [37620654622](https://github.com/xiongweilin/aios/actions/runs/37620654622) | 11482299215 | 68872 | `6237a1b843c4907bf160d274058b4a9d430b4903bc26503ec271bc9d05d9fe0e` | 2026-10-21 |
| 真实产品 E2E：正常 | [37713555933](https://github.com/xiongweilin/aios/actions/runs/37713555933) | 11522508523 | 14948 | `6d0b5ac9f3e23687316175ab1714e84ba6c16fbd249efa3867338201055beddf` | 2026-10-22 |
| E2E：应答丢失 | [37713555933](https://github.com/xiongweilin/aios/actions/runs/37713555933) | 11522518523 | 15191 | `468d79ac55b229929ed6ea9683bcece62831f348b187ae45d69bc75528e29b6c` | 2026-10-22 |
| E2E：回读中断 | [37713555933](https://github.com/xiongweilin/aios/actions/runs/37713555933) | 11522743042 | 15327 | `7b72473bd0e9e2a18855671d4c7eae01fdbf6216cecd4ef927e4b71a6ef0fe59` | 2026-10-22 |
| E2E：越过 Runtime | [37713555933](https://github.com/xiongweilin/aios/actions/runs/37713555933) | 11522403758 | 12926 | `94bad1dee51f8a91fb3dbb908989e9affce0134ee8195af365d209fe114a61a8` | 2026-10-22 |

## 限制和保全要求

- v6 ZIP 含 `summary.json`、逐案例 `result.json` 和 `gateway.json`；成本前沿 ZIP 还含 `workload.json`。E2E ZIP 含 `evidence.json`、`p6-quality.json`、服务日志与进程状态。
- 复制原始记录并复算汇总数只构成**一致性审计**，不能算作新的独立模型样本。v6 在特定 C2 工作负载的 +6 不推翻成本前沿 0/30 的严格安全成本零结果。
- **本地保全状态：**六个已核验 ZIP 副本保存在 `D:\infrastructure\data\evidence\BAA-Protocol\github-actions\2026-10-10\original-zips\`，位于 Git 仓库之外，并附有本地 `manifest.json`。这只是本地副本；没有核验独立备份或恢复能力。该目录的访问控制尚未通过资格核验，本次也没有审阅档案日志。未完成 secret/log 检查与适当脱敏前，不得公开原始 ZIP。
- 本次未提供人体实验结果、生产授权、四小时真实 P7 观测、长期运行可靠性或人力节省证据。

核对保留的原始文件：

```bash
sha256sum downloaded-original.zip
unzip -l downloaded-original.zip
```

字节数和摘要匹配只能证明文件副本一致，不证明实验结论适用于现实部署。
