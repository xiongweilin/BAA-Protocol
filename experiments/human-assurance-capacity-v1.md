# Human assurance capacity: longitudinal protocol draft

> English | [简体中文](human-assurance-capacity-v1.zh-CN.md)

**Status:** design draft; not preregistered; no reviewer-capacity or skill-retention observations have been collected.

## Question and scope

Does independently qualified review capacity change over time under a specified delegation and training arrangement, for a named task domain and review-demand scenario?

This protocol develops the proposed HRCC measurement in [experimental design §15](design.md#15-long-horizon-human-assurance-capacity-proposed-measurement-not-evidence). It does not alter the HRCC definition, claim that reviewer skill has declined, or treat headcount as review capacity.

## Measure

Use the same task domain, task mix, time horizon, and stress scenario in numerator and denominator:

~~~text
HRCC =
  independently qualified human review cases available within the horizon
  / required human review cases within that horizon and scenario
~~~

The numerator counts unseen blind review cases that available reviewers independently complete correctly within the declared response deadline. Define correctness, qualification, and deadline before testing; report accuracy and capacity separately. The denominator counts required review cases under a frozen scenario of escalations, semantic-bridge failures, assumption invalidations, emergency takeovers, and audits.

When required workload is zero, HRCC is undefined. HRCC below 1 indicates that demand exceeds qualified capacity in that specified scenario by definition. It is not a universal safety threshold. HRCC above 1 does not certify deployment safety or correct handling outside the measured cases.

## Longitudinal design requirements

Before any recruitment or measurement, freeze:

- task domain, task mix, scenario, review horizon, and response deadlines;
- role-specific qualification rubric, blind case bank, scoring and independent adjudication;
- cohort definitions for new, experienced, and exiting reviewers;
- training exposure and model-assistance rules;
- exact BAA and AIOS commits and protocol/catalog versions at each measurement point;
- comparator and a design capable of distinguishing delegation exposure from aging, selection, workload change, and training;
- observation schedule, missingness, attrition reporting, analysis, and reopening rules.

Use new unseen cases at each measurement point. Track reviewer skill, available capacity, demand, training effort, and review labor separately. Do not infer that automation caused a change merely because cohort scores or staffing changed over time.

## Decision use and limits

Interpret any capacity shortfall only against the predeclared scenario and required review deadline. If a deployment assumption depends on human takeover within that horizon and qualified capacity is unavailable, that assumption is not met for the scenario; this does not refute a finite formal guarantee.

This remains a protocol draft until the domain, rubric, workload scenarios, comparator, schedule, and analysis are fixed. No longitudinal effect or human-capacity claim is supported now.
