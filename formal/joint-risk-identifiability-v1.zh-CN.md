# Joint-Risk Identifiability v1 —— 负结果与校准准入条件

> [English](joint-risk-identifiability-v1.md) | 简体中文

## 状态

**有限负结果：已接受的真实产品 exposure 观察不能识别 structural joint-risk 模型。** 这不是产品 acceptance 失败，也不是新增 BAA 协议层。

已有证据：AIOS [real-product E2E run 37638217335](https://github.com/xiongweilin/aios/actions/runs/37638217335) 及 [Real-Product Exposure Binding Acceptance v1](real-product-exposure-binding-v1.zh-CN.md)。在 normal、lost-ack、read-back-outage 场景中，三种 offboarding effect 各自都与准确的 admitted proposal 绑定，并在窄的 `managed-subject-state-change-count-v1` metric 下观察到 `realized_exposure=1`。但这本身不包含多个 effect 之间的损失交互观测。

可执行反例位于 `tests/test_joint_risk_identifiability.py`。其中数据是**合成的观测形状 fixture**，不是伪造的产品 artifact，也不是经验估计。

## 不可识别性

冻结的 joint-risk functional 是：

```text
joint_risk(b, f, lambda)
  = sum_i(b_i)
  + lambda * sum_{i<j, f_i == f_j} min(b_i, b_j)
```

固定三次 effect 的 exposure 观察为 `(1, 1, 1)`，与真实产品结果的数值形状相同。令 `lambda=1`，相同的观察仍容许至少三种不同的**模型声明**：

| 未观察到的 risk-factor 分组 | 公式输出 |
| --- | ---: |
| 三个不同 factor | 3 |
| IAM disable/revoke 共享 factor，HRIS 独立 | 4 |
| 三个 effect 全部共享 factor | 6 |

即使固定中间的分组，`lambda` 仍不能识别：penalty 为 `0, 1, 2` 时公式分别输出 `3, 4, 5`，但 per-effect exposure 观察完全相同。

这些数字是不同**声明模型的计算结果**，不是不同的真实损失测量值。现有观察既没有独立建立 factor assignment，也没有可用来选择交互参数的独立 joint-loss outcome。

## 三种聚合不能混同

同一组合下，下列三个量不同：

- **被影响的 effect–subject transition 数量**：三次 unit effect observation；
- **被触及的不同 product-qualified subject 数量**：HRIS employee 与 IAM user，共两个；
- **底层 principal 数量**：可能只有一个，但需要独立的跨系统身份映射才能证明。

不同合同可以选择不同单位；这些量不能自动作为同一风险单位互换。

类似地，状态 `A -> B -> A` 包含两次中间变化，但期末净变化为零。因此 before/after projection 并不自动等于观察间隔内的完整 exposure trace。

既有真实产品 acceptance 确实在其冻结投影中检查了枚举 managed subject 的 collateral change；这个负结果不否定该观察，而是限制了**跨操作组合**能从中推断什么。

## 下一项可接受的校准研究

未来若要宣称识别了非零 interaction term，必须在看到结果**之前**冻结研究协议，至少包括：

1. **独立 outcome**：定义委托人事先批准、单位和适用域明确的 joint-loss/severity 量 `Y`，以及独立测量来源。直接把现有 per-effect subject count 重新命名为 `Y`，不能独立校准损害 penalty。
2. **可区分的干预**：在隔离安全任务域内比较单 effect、同 subject 多 effect、不同 subject 多 effect 的匹配 episode，控制操作顺序与时间重叠；包含 no-effect、unchanged-control 与 verification-outage 对照。
3. **可识别的 factor 假说**：事先声明竞争性的 HRIS/IAM factor 分组，以及候选交互族或 penalty 区间。观察必须能区分这些假说，不能事后根据结果贴 factor 标签。
4. **联合状态与不确定性**：在同一枚举 subject universe 上观察状态，保留 unknown/pending 与中间结果，处理共享状态与组间干扰，不把重复 trace 当作独立样本。
5. **冻结的接受规则**：预注册 exposure/harm endpoint、估计与不确定性方法、样本外验证、零/负结果及失效条件。分别标明经验界与结构假设。

若不能安全、独立地观察 `Y`，则**停在“尚不可识别”**。部署时仍可选择保守 budget，但不能称其为已校准的真实风险保证。

## 冻结结论

当前 offboarding risk-factor registry 继续保持为空。即使三项单位 exposure 都可靠地绑定到已准入的产品行动，也不能据此证明共享 factor 或正交互 penalty。

下一步应在隔离任务域中选择并独立观察适当的 joint outcome；否则必须将 joint-risk calibration 明确保留为开放的 `Omega` 假设。在现有单 case 产品 fixture 能区分竞争模型之前，不应继续扩张该 fixture。
