# Product Connector Refinement v1

> [English](product-connector-refinement-v1.md) | 简体中文

## 状态

本文定义从 World Runtime provider request identity 到 BAA offboarding 路径所使用的三个具体 product connector 的有限、revision-pinned refinement。

固定 AIOS revision：

`34b9f4274487f856ac4c23266d1dd726b24ae53c`

覆盖的 effect：

| Runtime capability | Product writer | 独立 read-back |
| --- | --- | --- |
| `administrative.hris.employee.deactivate.v1` | Odoo employee deactivate connector | Odoo deactivate verifier |
| `administrative.iam.identity.disable.v1` | Keycloak identity disable connector | Keycloak disable verifier |
| `administrative.iam.sessions.revoke.v1` | Keycloak session revoke connector | Keycloak session verifier |

可执行 fixture 位于 `integration/test_aios_product_connector_refinement.py`。

## Refinement relation

production Runtime provider 会把稳定的 Runtime `CapabilityRequest.id` 作为 connector 的 `request_ref`。Runtime recovery 随后调用同一 provider 的 `reconcile(request_id)`，因此 dispatch 与 reconciliation 使用同一 identity。

对覆盖的 product operation，connector 必须保持以下关系：

1. product write 携带 operation-specific durable request marker；
2. 已存在但不同的 marker 是 hard identity failure，不能覆盖或复用 product object；
3. ambiguous/lost acknowledgement 保持 unknown；
4. reconciliation 根据 durable marker 查询并读取 product state，而不是重复原始 reality-changing write；
5. 只有观察到已完成的 product state 才得到 reconciled success；
6. 独立 verifier 报告当前 product state，而不是复制 expected postcondition。

## Odoo employee deactivation

writer 只接受精确的 `odoo:hr.employee:<id>` identity。

product write 在同一次 Odoo update 中写入 `active=false` 与 deactivate request marker。refinement fixture 在该 write 上注入 lost acknowledgement，随后提供“同一 request marker 且 employee 已 inactive”的产品状态。reconciliation 成功，并且不会发出第二次 product write。

如果 product 中已经记录不同的 deactivate request marker，则返回 `ConflictingExternalRequestIdentity`。

verifier 独立读取 employee，并报告实际观察到的 `active` 值。

## Keycloak identity disable

writer 读取精确 subject，保留无关 user attribute，并同时写入 `enabled=false` 与 disable request marker。

lost-ack fixture 让写请求之后得到 ambiguous server result。reconciliation 随后根据同一 marker 找到 user 并观察到 `enabled=false`；它成功结束且不再发送 PUT。

若已有不同 disable request marker，则拒绝 identity rebound。

verifier 读取当前 Keycloak user state，并报告实际 `enabled` 值。

## Keycloak session revocation

logout 前，writer 先把 session-revoke request marker 持久写入 user，然后读取 session；只有仍有 session 时才执行 logout。

lost-ack fixture 让 logout outcome 变为 ambiguous。reconciliation 通过 marker 找到该 effect 并读取 session list；当 session 已为空时，仅通过 GET 就成功完成，不会再次发送 logout POST。

若已有不同 session-revoke marker，则拒绝 identity rebound。

verifier 独立报告当前 active-session 数量。

## 与前序层的关系

当前有限 refinement chain 已明确为：

`formal-v1 -> AIOS gate trace -> World Runtime scope/identity -> Runtime mediation surface -> product connector request marker/read-back`

本层把 Runtime request identity 连接到产品侧 durable request identity 与 recovery 行为，不新增 abstract protocol phase。

仓库此前已经有独立的真实临时 Keycloak/Odoo connector acceptance 与组合 real-product E2E evidence。这些运行提高了 fidelity，但本 v1 refinement claim 仍只由固定 revision 的可执行 connector fixture 定义，不能因为已有真实产品 acceptance 而扩大声明。

## Claim 边界

该结果不建立：

- production tenant safety 或生产 credential isolation；
- Keycloak/Odoo 内部 HTTP call 或数据库 transaction 的形式化证明；
- product server implementation 的正确性；
- 全部 transport、crash、concurrency 或 partial-write interleaving；
- durable request marker 在 connector 检查之外全局唯一；
- 所有 expected postcondition 与产品现实的语义等价；
- verifier credential separation 必然意味着组织独立性；
- structural v1 所需的 exposure/risk semantic bridge。

因此，当前 claim 是三个固定 offboarding operation 的有限 product-connector identity/reconciliation/read-back refinement。

## 下一项结构义务

当前价值最高的剩余结构缺口是：把 admission 时声明的 exposure/risk bound 与 reality-side measured exposure 建立 semantic bridge。应使用显式、可证伪的 contract 与 counterexample 推进，而不是继续扩大当前 connector claim。
