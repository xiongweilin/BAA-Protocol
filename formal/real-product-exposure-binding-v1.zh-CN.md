# Real-Product Exposure Binding Acceptance v1

> [English](real-product-exposure-binding-v1.md) | 简体中文

## 接受范围

这是 `managed-subject-state-change-count-v1` 可观察 metric 的有限真实产品 acceptance 结果，**不是**整体外部敞口或 structural joint-risk functional 的证明。

接受的 AIOS 实现已合并于 `b2cc1254a1908d00ded7c705f6e230c43f08f6f8`。对应 E2E 使用 BAA-Protocol `b3215d940cf7c9bd6b208ed5915eaa3c92ab10e3`。真实产品 E2E [run 37638217335](https://github.com/xiongweilin/aios/actions/runs/37638217335) 通过，运行时 PR implementation head 为 `e10c5f6c52e12ea08f603e9c8d01ca099e070df4`；变更已进入 AIOS main。

## 四个 acceptance 场景

| Scenario | Evidence artifact | 观察结果 |
| --- | --- | --- |
| Normal | `11491082646` | 三个获准 proposal 均与完整 managed-subject measurement 精确绑定；bound=1、realized=1 |
| Lost acknowledgement | `11489419994` | 三条相同 binding；通过稳定身份恢复，冻结投影内没有额外的产品敞口 |
| Read-back outage | `11489454782` | 三条相同 binding；延迟观察后完成，没有把 unknown effect 误当作未发生 |
| Unauthorized Runtime bypass | `11489744687` | 未授权请求得到 HTTP 403；所观察的产品前后状态未变化；本场景不应产生 admitted exposure binding |

前三份 artifact 对 Odoo employee deactivation、Keycloak identity disable、Keycloak session revoke 各记录三条 `assessment_established=true` 的 effect binding，`changed_subject_refs` 只有 declared target。临时租户中观察了 3 个 Odoo employee 和 2 个 Keycloak managed subject，并设置 control subject 使 collateral change 成为可证伪情况。

bypass artifact 测的是另一种性质：拒绝未授权 reality-changing invocation。它**不包含**三条获准 proposal binding，不应被统计成 exposure settlement 成功 episode。

## 真正建立的桥接

BAA-gated offboarding proposal 具有冻结的 metric declaration 和 bound。产品侧 snapshot 枚举冻结 observation projection 所覆盖的 managed subject，计算前后变化，再绑定回同一个 proposal、metric 与 subject。只有精确匹配的证据才能作为 realized metric value。

它强于只读取目标对象 postcondition 的证据，因为还观察 control subject；但不能扩展到隐藏的 product field、unmanaged entity、无关 object type、下游效果或未观察时间段。

`scope_complete=true` 仅表示**针对已枚举 managed-subject universe 中声明的 acceptance projection 完整**，不表示所有可能的产品或真实世界后果完整。

## 未关闭的义务

- 在并发变化、分页异常、进程崩溃和对抗扰动下检验 snapshot source 的完整性；
- 如需部署保证，单独建立 production tenant 的 metric-to-reality bridge；
- 为 joint-risk 提供有证据支持的 shared risk-factor identity、interaction semantics 和 penalty；否则显式保留条件性；
- 不把三次 unit exposure 的观察误认为联合真实损失不超过 3 的证明。

冻结 structural-v1 model 与经验 delegation-frontier 研究都没有改变。本结果只关闭一个有限的 measurement/identity link，没有完成整个 joint-risk 模型的语义论证。
