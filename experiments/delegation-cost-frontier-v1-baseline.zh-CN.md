# 委托成本前沿 v1 基线

> [English](delegation-cost-frontier-v1-baseline.md) | 简体中文

## 状态

**对已接受冻结 trace 的回顾性 accounting 结果，不重采样。**

本结果把 [v1 cost-frontier protocol](delegation-cost-frontier-v1-protocol.zh-CN.md) 应用于已接受的 offboarding v6 和 canary v5 artifact。

它描述已观察 accounting surface，不构成新的前瞻因果实验。

## 架构面板：严格 risk 与 attention

固定 principal attention=0、unsafe transition=0、terminal unresolved=0、useful delivery minimum=3、audit labor ceiling=5。只改变每个 episode 的 automatic assurance-intervention ceiling。

### C0

| 最大自动 intervention | Self-check | Audit | BAA |
|---:|---:|---:|---:|
| 0 | 4/24 | 4/24 | 4/24 |
| 1 | 4/24 | 4/24 | 4/24 |
| 2 | 4/24 | 4/24 | 4/24 |
| 3 | 4/24 | 4/24 | 4/24 |

C0 不存在架构优势。

### C1

| 最大自动 intervention | Self-check | Audit | BAA |
|---:|---:|---:|---:|
| 0 | 6/24 | 6/24 | 4/24 |
| 1 | 6/24 | 6/24 | 4/24 |
| 2 | 6/24 | 6/24 | 4/24 |
| 3 | 6/24 | 6/24 | 4/24 |

较短 adaptive horizon 下 BAA 仍落后；增加 intervention 额度不能代替缺失的 post-event action opportunity。

### C2

| 最大自动 intervention | Self-check | Audit | BAA |
|---:|---:|---:|---:|
| 0 | 14/24 | 14/24 | 13/24 |
| 1 | 14/24 | 14/24 | 16/24 |
| 2 | 14/24 | 14/24 | **20/24** |
| 3 | 14/24 | 14/24 | **20/24** |

因此此前 C2 frontier expansion 存在明确 assurance-cost threshold：0 次 intervention 时 BAA 少 1 个；1 次时多 2 个；2 次时才出现完整 +6 expansion。

## 人工 audit labor ceiling

在 C2、严格 attention/risk、useful delivery minimum=3、BAA intervention ceiling=3 时：

| 每 episode 最大人工 assurance labor | Self-check | Audit | BAA |
|---:|---:|---:|---:|
| 0 | 14/24 | 0/24 | 20/24 |
| 1 | 14/24 | 0/24 | 20/24 |
| 2 | 14/24 | 0/24 | 20/24 |
| 3 | 14/24 | 14/24 | 20/24 |
| 4 | 14/24 | 14/24 | 20/24 |
| 5 | 14/24 | 14/24 | 20/24 |

这组冻结 trace 中，每个 delegable audit completion 至少消耗 3 个 audit-labor unit。

## Risk ceiling 敏感性

在 C2、attention=0、terminal unresolved=0、audit labor<=5、BAA intervention<=3 时：

| 每 episode 最大 unsafe transition | Self-check | Audit | BAA |
|---:|---:|---:|---:|
| 0 | 14/24 | 14/24 | **20/24** |
| 1 | 16/24 | 16/24 | **20/24** |
| 2 | 19/24 | 19/24 | **20/24** |
| 3 | 19/24 | 19/24 | **20/24** |

放宽 risk bound 会按定义让更多 direct episode 变成 feasible，从而缩小 BAA 优势；这并不使这些 trace 更安全。

## Canary assurance-mechanism 面板

固定 principal attention=0、unsafe transition=0、terminal unresolved=0、人工 assurance labor=0，并允许最多 2 次 evidence reacquisition。

### H4

| 最大自动 intervention | no_reacquire | reacquire |
|---:|---:|---:|
| 0 | 2/24 | 2/24 |
| 5 | 2/24 | **4/24** |
| 11 | 2/24 | **4/24** |
| 17 | 2/24 | **4/24** |

### H8

| 最大自动 intervention | no_reacquire | reacquire |
|---:|---:|---:|
| 0 | 3/24 | 3/24 |
| 5 | 3/24 | **5/24** |
| 11 | 3/24 | **6/24** |
| 17 | 3/24 | **6/24** |

recovery mechanism 呈现明确 assurance-cost surface：自动 intervention 预算为 0 时 treatment gain 消失。

完整 H8 gain 还要求 2 次 bounded evidence reacquisition。reacquisition ceiling 为 0 或 1 时两种 policy 均为 3/24；ceiling=2 时 `reacquire` 才达到 6/24。

## 本 baseline 新增了什么

已观察优势取决于可用 assurance budget：

- assurance 工作太少时，BAA 甚至可能比 direct execution 更不易委托；
- 足够的 bounded assurance 工作可以把 feasible frontier 推向外侧；
- 放宽 risk ceiling 会让 direct execution 看起来更可委托，但只是接受更多 unsafe trace；
- post-hoc audit 即使不改变执行 trace，也消耗独立人工 labor budget。

## 限制

这些 threshold 是从已经接受的 trace 上回顾性读出的，因此不能当作预注册 replication。

下一步应先冻结 prospective cost grid，再生成新的 workload 或新的任务域/接口 trace；看到结果后不能修改网格。
