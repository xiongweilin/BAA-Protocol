# Canary v3 transport qualification amendment

> English | [简体中文](prospective-canary-v3-transport-amendment.zh-CN.md)

## Status

**Frozen before the next accepted canary v3 sample.**

This amendment changes only the client-side handling of a response that has not yet become a usable Responses object. It does not change the v3 workload, evidence treatments, H4 horizon, BAA kernel, prompts, admission rules, observer fixtures, model ID, proposal schema, risk budget, or endpoint.

The controlling v3 protocol remains `prospective-canary-v3-evidence-recovery` at BAA commit `c9681ec6c1c54313f7e21467c4942e412b52583d`, except for the transport qualification rule documented here.

## Why this amendment exists

Two pre-amendment runs are qualification evidence, not study results.

- AIOS run `37427961277` diagnosed genuine gateway/provider transport faults. The captured gateway logs included seven HTTP 502 Responses requests and upstream `ClientConnectorError` / `ClientPayloadError` failures.
- The local gateway was then pinned to `llm-gateway` commit `6fe86653da104bd0c00637a856e352303774fc01`, which adds a narrow replay-safe retry for non-streaming `POST /v1/responses` requests with `store=false`.
- AIOS run `37428925069` then completed the real-model workload, but failed qualification because two physical model calls were still classified as transport errors. That run is not an accepted v3 result.
- A post-run gateway diagnostic captured exactly 65 `POST /v1/responses` HTTP 200 responses and no 4xx/5xx response for those 65 study calls. The gateway therefore no longer exhibited the explicit 502 transport failure seen in the earlier diagnostic.

At the frozen BAA revision, `ModelResponseError` is separately classified as `model`, and proposal parsing failures are separately classified as `schema`. The remaining two run-9 failures therefore occurred before the client obtained a usable Responses object and were conservatively classified as transport failures.

The purpose of this amendment is to make that transport boundary explicit instead of repeatedly resampling until a clean run occurs.

## Frozen retry rule

Canary v3 uses a `ReplaySafeTransportClient` wrapper with `max_retries=1`.

One retry is allowed only when the first attempt fails before a usable Responses object exists, for example:

- local connection/read failure;
- incomplete HTTP body read;
- timeout before a usable response is obtained;
- JSON/framing decode failure;
- a Responses body that cannot be decoded into a usable response object.

The following are explicitly **not retryable**:

- an explicit HTTP status failure (`HTTPError`);
- `ModelResponseError`, including refusal or absence of the required `submit_canary_proposal` function call;
- a successfully extracted function call whose proposal fails the canary action schema;
- any BAA deny/hold/admit outcome;
- any observed real-world action result.

The retry repeats the identical model request. It does not change prompt content, treatment, history, runtime state, evidence, model ID, tool schema, or sampling policy.

## Accounting

The accepted result must report, in addition to the existing physical-sampling fields:

- `http_attempts`;
- `transport_failures_seen`;
- `transport_retries`;
- `recovered_transport_calls`.

`physical_sampling.calls` remains the number of logical physical model samples used by the study. A retry is an additional HTTP attempt for the same sample, not a new study sample.

Qualification still requires:

```text
calls_with_errors = 0
transport_errors = 0
schema_errors = 0
model_errors = 0
```

and additionally:

```text
http_attempts >= physical_sampling.calls
transport_retries >= recovered_transport_calls
transport_retries <= physical_sampling.calls
```

When unresolved transport errors are zero, every retry that was actually taken must either have recovered the call or be reflected as an unresolved error; therefore a fully qualified run should satisfy:

```text
transport_retries = recovered_transport_calls
```

The implementation is separately unit-tested to permit at most one retry per call.

## Acceptance rule

Runs `37427961277` and `37428925069` remain qualification-invalid and must not be used as the canary v3 endpoint result.

The first post-amendment run that passes all original v3 qualification rules plus the accounting rules above is accepted regardless of sign. No further resampling is permitted merely because the evidence-reacquisition endpoint is zero or negative.

## Non-claims

This amendment does not claim that arbitrary model calls are replay-safe. Its scope depends on the existing canary request contract: non-streaming Responses requests use `store=false`, no reality-changing tool is executed by the model endpoint itself, and BAA executes reality-changing proposals only after the model response has been returned and admitted.
