# Runtime Mediation Surface v1

> [English](runtime-mediation-surface-v1.md) | 简体中文

## 状态

本文冻结一组有限、revision-pinned 的 World Runtime HTTP surface：这些入口能够启动 provider dispatch、准备/推进 domain-owned reality-changing effect、记录 provider result，或进入 provider reconciliation。

固定 AIOS revision：

`34b9f4274487f856ac4c23266d1dd726b24ae53c`

这是 World Runtime refinement v1 之后的下一项结构工作。它是可执行的 surface-coverage claim，不是“系统中绝不存在任何绕过路径”的证明。

## 冻结的 reality-facing Runtime surface

当前 inventory：

| Method | Route | Boundary role |
| --- | --- | --- |
| POST | `/v1/invoke` | canonical Runtime capability invocation |
| POST | `/v1/domain-effects/prepare` | 授权并持久绑定 domain-owned reality-changing effect |
| POST | `/v1/domain-effects/{idempotency_key}/start` | 授予一次 fresh provider dispatch generation |
| POST | `/v1/domain-effects/{idempotency_key}/result` | 持久记录 provider outcome / ambiguity / reconciled result |
| POST | `/v1/reconcile/{idempotency_key}` | 对 durable provider attempt 进入 Runtime reconciliation |

可执行测试不仅检查这些 route 是否存在。它会发现实际调用 Runtime provider-boundary 方法的 route endpoint，并要求发现结果与冻结清单完全一致。因此，如果 pinned Runtime 新增 dispatch/recovery route，CI 会失败，直到该入口被显式审查并加入 inventory。

## 必须满足的 mediation 检查

每个被发现的 route 在跨越 provider-boundary state 前都必须构造 authenticated request context，并执行 Runtime transition-authority check。

另外：

- `/v1/invoke` 在 reality-changing capability invocation 前必须执行 effect-authority check；
- `/v1/domain-effects/prepare` 在创建可 dispatch domain effect 前必须执行 effect-authority check；
- Administrative offboarding bridge 的 reality-changing execution 必须通过 `/v1/invoke` 进入；
- autonomous-development bridge 必须先 prepare/start domain effect，再调用具体 provider，并且 provider call 之前必须检查 `dispatch_allowed`。

最后一条与现有 ambiguous-effect 测试配套：已有 unknown outcome 的 effect 不会得到第二次 dispatch grant。

## 与前序 refinement 的关系

structural v1 检查抽象 protocol state machine。

AIOS refinement v1 检查具体 offboarding gate trace 是否符合抽象 phase relation。

World Runtime refinement v1 检查 capability/resource/version scope、authorization、durable effect identity、identity rebound 拒绝、writer/verifier separation 与 ambiguous-effect fencing。

本 mediation-surface 层检查 pinned HTTP/adaptor 中能够跨入 provider-side execution 的入口是否被显式 inventory，并且是否经过相应 guard。

## Claim 边界

该结果不建立：

- whole-repository 级证明，即任意 Python 代码绝不能直接调用 provider object；
- operating system、process、service mesh、firewall、credential 或 network route 层的 complete mediation；
- pinned revision 之外未来新增绕过路径不存在；
- authorization decision 的语义正确性；
- 全部 concurrency/crash interleaving 的 refinement；
- 到 Keycloak/Odoo 状态迁移的 product-connector refinement；
- product read-back 的正确性或独立性；
- exposure/risk semantic bridge。

因此，当前接受的 claim 是**固定 public Runtime/adaptor provider-boundary surface coverage**，而不是 universal complete mediation。

## 下一项结构义务

下一项有价值的 refinement target 是 product boundary：把 Runtime request identity 与 dispatch/reconciliation record 连接到固定 Keycloak/Odoo writer/verifier connector，包括 lost-ack 与 read-back recovery，同时不把该 surface claim 扩张成 production safety。
