# Canary v3 Transport Qualification 修订

> [English](prospective-canary-v3-transport-amendment.md) | 简体中文

## 状态

**在下一个可接受的 canary v3 样本之前冻结。**

本修订只改变 client-side 对“尚未形成可用 Responses object”的失败处理，不改变 v3 workload、evidence treatment、H4 horizon、BAA kernel、prompt、admission rule、observer fixture、model ID、proposal schema、risk budget 或 endpoint。

控制性 v3 protocol 仍是 BAA commit `c9681ec6c1c54313f7e21467c4942e412b52583d` 中的 `prospective-canary-v3-evidence-recovery`；唯一新增内容是本文规定的 transport qualification 规则。

## 为什么需要这次修订

两个修订前 run 只能作为 qualification evidence，不能作为研究结果。

- AIOS run `37427961277` 诊断到真实 gateway/provider transport fault。保存的 gateway 日志中包含 7 次 HTTP 502 Responses 请求，以及 upstream `ClientConnectorError` / `ClientPayloadError`。
- 随后 local gateway 被固定到 `llm-gateway` commit `6fe86653da104bd0c00637a856e352303774fc01`；该版本只对 non-streaming、`store=false` 的 `POST /v1/responses` 增加狭窄的 replay-safe retry。
- AIOS run `37428925069` 此后完整执行了真实模型 workload，但因为仍有 2 个 physical model call 被归类为 transport error 而 qualification 失败。该 run 不是被接受的 v3 结果。
- run 后 gateway diagnostic 对这 65 个 study call 精确观察到 65 次 `POST /v1/responses` HTTP 200，且没有 4xx/5xx。也就是说，之前明确出现的 gateway 502 transport failure 已经被消除。

在冻结 BAA revision 中，`ModelResponseError` 会单独记为 `model`，proposal parsing failure 会单独记为 `schema`。因此 run 9 剩下的两个失败发生在 client 获得可用 Responses object 之前，并被保守地归类为 transport failure。

本修订的目的，是显式规定这个 transport 边界，而不是反复重采样直到出现一次“干净”run。

## 冻结 retry 规则

Canary v3 使用 `ReplaySafeTransportClient` wrapper，`max_retries=1`。

只有第一次 attempt 在尚未得到可用 Responses object 时失败，才允许一次 retry，例如：

- local connection/read failure；
- HTTP body incomplete read；
- 在得到可用 response 之前 timeout；
- JSON/framing decode failure；
- Responses body 无法解码为可用 response object。

以下情况明确**不得 retry**：

- 明确 HTTP status failure（`HTTPError`）；
- `ModelResponseError`，包括 refusal 或缺少要求的 `submit_canary_proposal` function call；
- function call 已成功提取，但 proposal 不符合 canary action schema；
- 任意 BAA deny/hold/admit 结果；
- 任意已经观察到的现实行动结果。

retry 重复完全相同的 model request，不改变 prompt content、treatment、history、runtime state、evidence、model ID、tool schema 或 sampling policy。

## Accounting

被接受的结果除原有 physical-sampling 字段外，还必须报告：

- `http_attempts`；
- `transport_failures_seen`；
- `transport_retries`；
- `recovered_transport_calls`。

`physical_sampling.calls` 仍表示研究中使用的 logical physical model sample 数量。retry 是同一样本的额外 HTTP attempt，不是新的 study sample。

Qualification 仍要求：

```text
calls_with_errors = 0
transport_errors = 0
schema_errors = 0
model_errors = 0
```

并额外要求：

```text
http_attempts >= physical_sampling.calls
transport_retries >= recovered_transport_calls
transport_retries <= physical_sampling.calls
```

当 unresolved transport error 为零时，实际执行过的每个 retry 必须要么恢复该 call，要么留下 unresolved error；因此 fully qualified run 应满足：

```text
transport_retries = recovered_transport_calls
```

实现层另有单元测试保证每个 call 最多 retry 一次。

## 接受规则

run `37427961277` 与 `37428925069` 保持 qualification-invalid，不得作为 canary v3 endpoint 结果使用。

本修订后第一个同时通过原始 v3 qualification 与上述 accounting 规则的 run，无论结果正负都接受。不得因为 evidence-reacquisition endpoint 为零或负而继续重采样。

## 不主张

本修订不主张任意 model call 都可安全 replay。其适用范围依赖现有 canary request contract：Responses 请求为 non-streaming、`store=false`；model endpoint 本身不执行现实改变工具；现实改变 proposal 只有在 model response 返回后，经过 BAA admission 才可能执行。
