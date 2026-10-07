# Offboarding Exposure Declarations v1

> [English](offboarding-exposure-declarations-v1.md) | 简体中文

## 状态

本文把每个 BAA-covered employee-offboarding proposal class 绑定到 Exposure Metric Binding v1 引入的 concrete observable exposure metric。

本层只是 declaration layer。它不主张每个 proposal instance 都已经拥有被接受的 reality-side measurement source，也不论证 joint-risk functional。

可执行 declaration registry 位于 `baa_protocol/offboarding.py`；regression test 位于 `tests/test_offboarding_exposure_declarations.py`。

## 冻结 declaration

三个允许的 external offboarding operation 全部使用：

`managed-subject-state-change-count-v1`

并声明 exposure bound=1。

| Target system | Operation | Metric | Bound |
| --- | --- | --- | ---: |
| HRIS | `employee.deactivate` | `managed-subject-state-change-count-v1` | 1 |
| IAM | `identity.disable` | `managed-subject-state-change-count-v1` | 1 |
| IAM | `sessions.revoke` | `managed-subject-state-change-count-v1` | 1 |

该 declaration 的含义是：

> 对冻结 observable metric，一个 logical offboarding effect 在 admission 时声明：最多只有 declared subject 的 managed product-state projection 发生变化。

它不表示所有真实 harm 或所有隐藏 product-side effect 都被 1 这个数字限制。

## Exact identity binding

对 concrete proposal，生成的 exposure declaration 会绑定：

- exact proposal id；
- 冻结 metric id；
- exact proposal subject；
- bound 1。

属于其他 proposal、metric 或 subject 的 measurement 不能 settle 当前 declaration。

## Coverage invariant

测试要求 declaration registry 的 operation key 与 `OffboardingKernel.ALLOWED_EXTERNAL_OPERATIONS` 完全一致。

因此，如果未来新增允许的 offboarding operation，却没有显式 exposure semantics，测试会失败；系统不会让它静默继承空语义或默认 metric。

registry 之外的 operation 会直接失败，而不是推断 declaration。

## Falsification

该 declaration 有意保持可证伪。

对三类 operation 中任意一类，如果完整 managed-subject measurement 同时报告 declared subject 与一个 control subject 发生变化，则 realized exposure=2。面对冻结 bound=1，metric bridge 不成立。

不允许 clamp，也不允许事后把结果重新解释成 target-only exposure。

## 与候选 AIOS acceptance evidence 的关系

开放的 AIOS PR #35 包含同一 metric 的候选真实临时产品 instrumentation。其真实 Keycloak 与 Odoo acceptance run 在 managed-subject projection 上都只观察到 declared target 发生变化。

但 declaration 的存在不会自动把这些候选 measurement 升格为已接受 evidence。AIOS 变更仍受其自身 gate 约束；目前因为一个无关的通用 Autodev vulnerability-scan workflow 保持红灯，该 PR 尚未合并。

因此 declaration 与 measurement source 仍是两个独立 proof obligation。

## Claim 边界

本结果不建立：

- bound=1 是 offboarding harm 的普适上界；
- observable product-state projection 覆盖全部 side effect；
- 候选 AIOS acceptance evidence 已进入 BAA 已接受证据链；
- 每个 production product tenant 都存在完整 managed-subject universe；
- joint-risk functional 已校准到这些 unit bound；
- production safety。

它只冻结三个 reference offboarding proposal class 所携带的 concrete metric semantics。

## 下一项结构义务

当该 metric 的 scope-complete measurement source 被正式接受后，剩余 structural semantic question 是 risk functional：为什么、以及在什么假设下，unit managed-subject state-change exposure（包括 effect 之间的 interaction）应由当前 declared joint-risk function 进行组合。
