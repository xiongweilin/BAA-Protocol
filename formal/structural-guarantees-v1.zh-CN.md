# 结构保证 v1

> [English](structural-guarantees-v1.md) | 简体中文

## 状态

本文记录 BAA-Protocol 第一版有限状态结构模型检查。

它针对一个有意缩小的抽象状态迁移系统完成证明义务，**不是**生产认证，也不能说明任意现实行动天然满足相同假设。

机器可读结果：

- [structural-model-v1-result.json](structural-model-v1-result.json)

可执行 checker：

- `baa_protocol/formal_model.py`
- `scripts/run_formal_model_check.py`
- `tests/test_formal_model.py`

## 主张形式

当前检查的主张是：

[
Omega_{mathrm{formal-v1}}
Rightarrow
orall 	au in operatorname{Trace}(K_{mathrm{formal-v1}}),
quad
	au models I_{mathrm{formal-v1}}
]

其中量化范围只覆盖 `FiniteBAAModel` 编码的有限状态系统。

当前冻结状态空间包含：

- **584 个可达状态**
- **35,040 个被枚举的状态转移**

CI 对每个可达状态枚举全部声明动作。

## 有限抽象宇宙

v1 模型包含五个 proposal slot：

1. 一个 risk factor 为 `shared` 的普通 proposal；
2. 第二个相同 risk factor 的 proposal，用于使组合交互真正影响准入；
3. 一个不同 risk factor 的普通 proposal；
4. 一个以受保护保证源为目标的 proposal；
5. 一个没有 verification path 的 proposal。

冻结风险模型使用：

[
R = 3
]

同 risk factor 的成对 interaction penalty 为 (1)。

动作字母表包括：

- evaluation/admission；
- exact-scope execution；
- wrong-object execution；
- wrong-operation execution；
- over-quota execution；
- expired execution；
- stale-version execution；
- zero-exposure verification；
- declared-bound verification；
- 一个超过 declared bound 的 out-of-(Omega) verification attempt；
- conservative timeout settlement；
- observation-unavailable self-transition。

被拒绝的请求保留为不授权的 self-transition，因此同样进入穷举检查。

## 显式假设 (Omega_{mathrm{formal-v1}})

结果依赖以下全部条件：

1. executor 是所表示行动的完整介入路径；
2. proposal scope 与 exposure bound 在 admission 后不可修改；
3. settlement 使用的 realized exposure 非负且不超过 declared bound；
4. protected guarantee source 恰好是标记为 `protected_source` 的对象；
5. 声明的 joint-risk functional 就是本保证所约束的风险量；
6. 不存在未建模的外部 transition 修改所表示的 ledger。

这些是保证主张的一部分，不是实现备注。

## 已检查不变量

有限模型满足全部七项冻结不变量。

### 1. Capability 不可扩大

任何成功 execute 都必须精确匹配已签发 capability 的 object、operation、quota、expiry 与 state version。

wrong-object、wrong-operation、over-quota、expired、stale-version、被修改或不可执行的 capability 都不能在模型中产生现实作用状态转移。

### 2. Ledger 类别互斥

每个被表示的 exposure 只处于一个语义 accounting 类别：

- reserved；
- pending；
- settled；

或不处于 exposure-bearing 类别。

同一个 proposal 不能被一次 transition 静默重复计入多个类别。

### 3. 联合风险预算

所有可达状态均满足：

[
ho(X_t) le R
]

这里使用冻结的 joint-risk function。

admission 查询当前联合状态及 pairwise interaction，而不是只检查 proposal 的边际 bound。

### 4. Pending exposure 不会被静默释放

execution 一旦把 exposure 移入 `PENDING`，任何非终端动作都必须保持 pending。

v1 表示的终端路径只有：

- verification；
- conservative timeout settlement。

### 5. Unknown effect 不会 blind replay

proposal 处于 pending 时，即使使用完全相同的 execute 请求也会被拒绝。

因此模型不会把“acknowledgement unknown”解释成再次执行同一 capability 的许可。

### 6. 保证源不可达

目标为声明 protected guarantee source 的 proposal 不会获得 capability。

不存在可达状态使该 proposal 获得 reserved、pending 或 settled 的 reality-facing authority。

### 7. Timeout 保守结算

pending timeout 按声明上界结算：

[
E_{mathrm{settled}} = E_{mathrm{declared bound}}
]

不会因为 confirmation 丢失而释放 exposure。

## 为什么 exposure-bound 假设必须显式存在

reference kernel 有意不会把观测到的 realized exposure 强行截断到 declared bound。

回归测试给出直接反例：

1. risk budget = 5；
2. proposal 声明 exposure bound = 5，并被准入；
3. execution 进入 pending；
4. verification 报告 realized exposure = 6；
5. 当前记录风险变成 6。

因此：

[
	ext{realized exposure} le 	ext{declared bound}
]

是实质性的 semantic/risk-model 假设。现实一旦违反它，结构预算保证就失效。若实现把观测值静默 clamp 为 5，反而会隐藏 (Omega) 已被证伪这一事实。

## 没有证明什么

当前模型检查没有建立：

- AIOS 或任意生产 executor 确实是完整介入路径；
- 现实 exposure bound 一定正确；
- toy risk functional 覆盖所有相关损害维度；
- 外部主体无法修改 protected source 或 ledger-relevant reality；
- observation 一定正确辨认现实 effect；
- 任意 concurrency、distributed failure 或 timing 行为都能 refinement 到该状态机；
- model/planner 一定完成有效工作；
- 五 proposal 的有限宇宙覆盖所有组合。

这些分别属于 refinement、semantic bridge、经验或部署义务。

## 下一项结构义务

下一步不应机械扩大抽象状态数。

真正有价值的是为一个具体 runtime boundary 建立到本模型的 **refinement mapping**：

[
Omega_{mathrm{bridge}}
land
operatorname{Trace}(	ext{implementation})
preceq
operatorname{Trace}(K_{mathrm{formal-v1}})
]

例如固定 AIOS World Runtime capability path。

在该 mapping 建立之前，本结果只属于 protocol model，而不是 deployed system。
