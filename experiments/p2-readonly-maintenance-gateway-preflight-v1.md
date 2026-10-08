# P2 Read-Only Maintenance Real-Model Pilot — First Gateway Qualification Failure

> English | [简体中文](p2-readonly-maintenance-gateway-preflight-v1.zh-CN.md)

**Evidence status: infrastructure/interface qualification failure before model sampling. No model or delegation result.**

## Frozen source and observed execution

The existing [five-window P2 protocol](p2-readonly-maintenance-model-v1.md) and pinned P7 product evidence were **not modified** to respond to this failure.

- AIOS experiment [PR #44](https://github.com/xiongweilin/aios/pull/44), source head `0a1c14219ec62e17cd1f3b274053c61b29f5f92a`.
- Self-hosted Windows real-model [Actions run 37722950723](https://github.com/xiongweilin/aios/actions/runs/37722950723): **failure**.
- The workflow completed repository checkouts, Python setup, and offline frozen-workload/model-interface tests. At the subsequent existing-loopback-gateway qualification step, `Invoke-RestMethod` for `http://127.0.0.1:4101/v1/models` failed with **connection refused**. The model sampling step was never entered.
- **Physical model proposal calls from this run: 0**. No three-regime outcome table, usable model sampling, causal value estimate, external maintenance task delivery, new product effect, or model-output cost evidence was produced.
- A missing local gateway is not evidence that a particular model is absent from a working catalog, nor that the underlying BAA/P2 policy failed. The observed failure class is **gateway unavailable at the request boundary**; root cause not established by these logs.

The branch's original workflow would auto-trigger on a branch push; this was not merged. [AIOS PR #44](https://github.com/xiongweilin/aios/pull/44) was closed without merge to avoid a second model workflow and unintended repeated sampling. [AIOS PR #45](https://github.com/xiongweilin/aios/pull/45), merged as `0f5d05212b72ecba8258d1cfe0bf33d9d9eaabcd`, is the canonical integration and permits model calls **only after an explicit manual dispatch with affirmative finite-spend approval**.

The current main's model tool is pinned to BAA `82370d7991eea9c288126610594a208efff06baa`, requires the original P7 [run 37720702388](https://github.com/xiongweilin/aios/actions/runs/37720702388) artifact **11526016609** with its exact SHA-256 and all five model-visible source projections, and refuses to sample if that prerequisite fails.

## Continuation and claim boundary

The next **separate opt-in** is to make the existing authorized loopback model gateway operational and, when ready to accept bounded model cost, manually dispatch the AIOS workflow `BAA P2 Isolated Read-Only Maintenance Model Replay v1` with `approve_finite_model_sampling=yes`.

Do **not** rerun a branch-push job, invent a model response, change the preregistered workload, infer that principal attention is zero, claim a BAA frontier expansion, or seek production Keycloak/Odoo access to work around local-gateway unavailability.

A successful future interface qualification would at most support a small, correlated, archived-evidence **model replay**. It would still not qualify prospective randomized P2 delivery, real organizational attention, P3 loss factors, or P7 deployment authority.
