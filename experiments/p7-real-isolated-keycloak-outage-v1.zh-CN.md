# P7：隔离 Keycloak 真实进程中断与保守只读取证恢复——v1

> [English](p7-real-isolated-keycloak-outage-v1.md) | 简体中文

## 证据等级

**一次经过资格检查的真实隔离服务进程、可逆故障及 GET 只读观测**。它不是生产故障、Agent 自主行动、长期 soak、SLO/MTTR 分布，也不是 BAA 委托增益的因果对照。

前一轮 [P7 只读维护诊断](p7-readonly-maintenance-triage-v1.zh-CN.md) 只模拟**本地观测响应**的错误。本轮通过固定 Docker Compose 服务，**实际暂停**一次性 Keycloak 进程；要求观察者检测中断，并在无条件尝试恢复容器后重新取得证据。

## 预先冻结的实验规则

[AIOS v2 预注册文件](https://github.com/xiongweilin/aios/blob/engineering/p7-real-isolated-keycloak-outage-recovery/tests/acceptance/baa_offboarding/P7-ISOLATED-REAL-OUTAGE.md) 在首个故障实验前已提交：

1. 首轮四类 GET 基线必须全部正常，包括 World Runtime 三项 covered capability 的强制授权标志。
2. CI 中的固定控制器仅暂停一次**隔离测试** Keycloak 容器。
3. 暂停时 Keycloak realm GET 必须标记为 `transport_unknown`；World Runtime 健康、capability 契约及 Odoo 根接口必须保持 `ok`。
4. 无论暂停和观测是否出错，都必须尝试解除暂停。
5. 最多八轮恢复观测，每轮相隔两秒；要求**连续两轮完整且正常**，既有 `assess_maintenance` 规则必须判断为 `verified_recovered_evidence`。否则实验资格失败。

全程没有员工主体、产品写入 API、策略修改、真实凭据轮换或生产服务。

## 首轮合格的真实产品中断

- AIOS [PR #43](https://github.com/xiongweilin/aios/pull/43)，首轮合格故障实验的源 HEAD `ab5f023844a73e13b9b04b6acfe4960c304f8f67`。
- [GitHub Actions 37720188025](https://github.com/xiongweilin/aios/actions/runs/37720188025)，attempt 1；证据 artifact **11526115290**，压缩包 SHA-256 `cd1fd2b0b3574feb623c48ae9e1aefde5c885388d6f00f24e89c511f35d2b900`。
- Artifact 的 `provenance.json` 记录 PR checkout SHA `a01d456e4c30f401360a7422aa61b2dc829e7cab`，与源 HEAD 不同。
- 故障过程：合格基线 → 实际暂停 Keycloak → 观察到 `transport_unknown` → 成功解除暂停 → 连续两轮完整取证。
- 中断实验共 **4 轮／16 次真实 GET**：Keycloak 一次非 OK；其余三类观测**零**次非 OK。
- `assess_maintenance` 输出 `verified_recovered_evidence`，`observation_unknown_encountered=true`，`terminal_unresolved=false`，`evidence_reacquisition_rounds=2`。
- Docker unpause 命令结束后，直到第二轮完整正常观测结束的**同一主机单调时钟**耗时为 **2.076049 秒**。它是**重新取证耗时**，并非 Keycloak 真正恢复的精确时刻，更不是代表性的平均恢复时间。
- 同一 run 的其他独立任务也通过：40 秒只读 shadow（9 轮／36 次 GET）及此前的三个确定性只读维护诊断。**不能与中断实验的分母混算**。

## 最终合并版本与第二次合格实验

- AIOS PR #43 最终源分支 HEAD：`d8439c17248b88e0fdd971477f3a28fb151c6e76`；合并后 main [`c3c54474727e`](https://github.com/xiongweilin/aios/commit/c3c54474727e82f9f5d30e3a504065ae9d660a63)。
- [最终 CI run 37720702388](https://github.com/xiongweilin/aios/actions/runs/37720702388)，artifact **11526016609**，归档 SHA-256 `dfafd340bd3a10f2c4768c578b908cad1756e6f1009e3c5b153d49046ec16b60`；`provenance.json` 的 PR checkout ref 为 `2288420643148fd8a2aa56de8ba6f9def0cbe1cd`，与源分支及 main SHA 不同。
- 本次 Odoo/Keycloak/World Runtime 隔离测试栈**一次启动成功**：`fixture-startup.json` 为 `attempted=1`、`failed=0`、`qualified=true`，最大次数 2。
- 第二轮实际故障再次满足未修改的规则：**4 轮／16 次 GET**，仅 `keycloak_realm` 一次非 OK，三个对照接口均无失败；Docker unpause 成功，连续两轮重新取证；结果 `verified_recovered_evidence`，没有终态未解决。
- 从 Docker unpause 命令完成至两轮完整恢复观测完成的本机耗时为 **2.074594 秒**。加上首轮 **2.076049 秒**，也只有两次有限观测，不构成 MTTR 分布或统计保证。
- AIOS PR #43 的七项检查——CI、Acceptance、Real Product Offboarding E2E、P3 探针、P7 shadow、BAA 网络预检查及 SonarCloud——全部通过后才合并；BAA 归档 CI 独立检查。

## 实现及基础设施资格失败

- 首轮真实中断的科学判据通过，但同一源 HEAD 的主 CI 存在一个未使用 import 的 `F401` 错误，随后只修复导入。
- [run 37720464278](https://github.com/xiongweilin/aios/actions/runs/37720464278) 在启动一次性 `odoo-init` 时以退出码 2 失败，**尚未进入基线或中断实验**；属于基础设施资格失败，不计入恢复实验的正负分母。
- 随后仅对启动环节增加**最多两次**全新一次性 Compose 初始化，`fixture-startup.json` 记录尝试与失败次数；两次都失败仍判 CI 失败。Odoo 初始化偶发失败的根因**尚未查明**。故障目标、三项对照、两轮恢复、八轮上限和科学判据全部保持不变。
- 最终版本已通过全部七项 CI 并合并；首轮合格实验仍按其独立源 HEAD 记录。

## 不能外推的保证

一次受控 Docker pause 证明该隔离故障可以被当前只读探针区分，且 unpause 后可以重新取得连续两轮完整 GET 证据。它**不能**证明全程状态正确、现实业务修复、自然发生事故的诊断、principal attention、assurance labor、Agent 有用交付、尾部恢复延迟、BAA 因果优势或生产长期可靠性。

P3 联合风险因子 registry 未校准，保持不变。真正的维护任务委托研究仍需另行批准范围受限的只读 staging 权限，并对相同任务采用预先冻结的风险、注意力、交付、horizon 和 assurance 预算及独立结果核验。
