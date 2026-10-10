# Total human labor study: protocol draft

> English | [简体中文](human-cost-study-v1.zh-CN.md)

**Status:** design draft; not preregistered; no human-cost observations have been collected.

## Question and scope

For a fixed task set and delivery standard, does bounded admission reduce total human labor while preserving separately measured safety and useful delivery, compared with the existing authorization, type-checking, recovery, and review workflow?

This study is distinct from principal-attention accounting and from the proposed human-assurance-capacity study. Lower principal attention is not a total-labor result. The protocol does not establish a general benefit or a causal effect until a suitable comparison is run.

## Measurement unit

Use task-attributed person-minutes as the primary human-labor unit: sum active human minutes across every participating role for the same task. If two people work at the same time, count both people's active time. Do not count unattended elapsed time as labor unless a person must actively monitor it.

Record separately, without adding them to person-minutes:

- event counts, such as reviews, escalations, repairs, and takeovers;
- model calls, token counts, and machine elapsed time;
- synthetic attention or cost scores;
- one-time setup and training effort.

Report ambiguous or unobserved labor as unknown, not zero. Define the role list, start/stop rules, source of time records, and treatment of shared work before collection. Do not convert one unit into another without a separately justified conversion.

## Workload and comparison

Before collecting outcomes:

1. Select a new task workload and define the task unit, target population, purpose, useful-delivery criterion, and observable safety properties. Record exact BAA and AIOS commits, protocol/catalog versions, model, and gateway; changed versions form separate evidence strata unless equivalence is established.
2. Group tasks that share a material influence domain; do not treat repeated rows from one shared episode as independent tasks.
3. Select the comparator used in the actual setting. It must retain its ordinary authorization, type checks, recovery, and review controls; do not compare BAA only with an artificially weakened workflow.
4. Freeze allocation, task horizon, time-recording method, exclusions, missingness rules, baseline, and analysis. If assignment is not randomized or supported by another defensible identification strategy, report the result as descriptive rather than causal.
5. Preserve failed, incomplete, held, and unknown outcomes. Report labor per assigned task and useful delivery separately; do not condition the primary comparison only on completed tasks.

## Labor included

Attribute task-specific active labor for the principal, independent reviewers, repairers, exception responders, and maintainers. Record review, correction, recovery, exception takeover, and maintenance even when those activities move away from the principal.

Measure setup and training separately. Include recurring maintenance only over a predeclared observation window. Any amortization of one-time effort must be specified before outcomes and shown separately from observed task labor.

## Interpretation and stopping

Report total person-minutes and each role's contribution separately, alongside useful delivery, safety observations, and unknown outcomes. Event counts and attention scores remain separate columns.

If principal attention falls while total person-minutes do not, the evidence supports burden transfer at most, not labor saving. If delivery declines or safety is unresolved, do not describe lower labor as an equivalent result. Set the smallest worthwhile difference from task costs before the main comparison; this draft assigns no numerical threshold.

The study is not executable until the workload, comparator, observable safety properties, role definitions, instrumentation, allocation, and analysis are frozen. No total-human-labor conclusion is currently available.
