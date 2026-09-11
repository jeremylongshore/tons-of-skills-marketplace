---
name: mindtickle-core-workflow-b
description: 'Design and govern a Mindtickle readiness and coaching measurement cycle tied to business outcomes. Use when defining competencies, assessments, coaching, or Readiness Index reviews. Trigger with "measure Mindtickle readiness".'
argument-hint: "[role-profile] [review-period]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, mindtickle, readiness, coaching, measurement]
model: inherit
effort: medium
compatibility: Designed for Claude Code; competency models, employee assessments, coaching actions, and CRM correlation require HR, legal, and business-owner approval
---
# Mindtickle Readiness and Coaching Measurement Cycle

## Overview

Create an explainable measurement plan that connects competencies, learning, coaching, and field outcomes without turning a readiness score into an unsupported employment decision.

## Prerequisites

- A role owner, approved competency model, review population, and business outcome
- Defined lawful uses, access controls, retention, and employee communication
- Confirmed entitlements for Readiness Index, assessments, coaching, analytics, and any CRM integration

## Tool Discipline

Use `Read`, `Glob`, and `Grep` for profiles and metric definitions, `WebFetch` for current official contracts, and `Write` or `Edit` for a governed measurement specification and redacted review receipt.

## Current Contract

Mindtickle describes Ideal Rep Profiles, competency benchmarks, assessments, coaching, module-level insights, team and regional views, and correlation with CRM outcomes. The customer owns the validity, fairness, interpretation, and permitted decisions built on those measurements.

## Authentication

Restrict learner-level data to approved roles. Use aggregate or de-identified data where possible, and keep CRM, HR, assessment, and coaching access independently authorized.

## Instructions

1. Define the decision the measurement may inform and decisions it must never make automatically.
2. Version the role profile, competencies, weights, evidence sources, exclusions, and review cadence.
3. Establish baselines and minimum sample sizes before setting targets or claiming correlation.
4. Validate assessment accessibility, scoring reproducibility, manager calibration, and missing-data treatment.
5. Map learning and coaching interventions to named gaps; retain a human review and appeal route.
6. Present any tenant configuration change with population impact, effective date, and rollback.
7. After approval, run the cycle and reconcile source evidence, computed views, and authorized exports.
8. Report trends with uncertainty and confounders; do not infer causation from a dashboard correlation.

## Approval Boundaries

Do not change competency weights, assign remediation, export learner-level results, or feed scores into compensation or employment actions without explicit policy and owner approval.

## Output

Return the versioned model, purpose and prohibited uses, access matrix, validation evidence, approved interventions, aggregate results, limitations, and next review date.

## Error Handling

| Condition | Response |
|---|---|
| A metric cannot be reproduced | Quarantine it from decisions and reconcile its source and transformation. |
| Group size risks re-identification | Suppress or aggregate the result according to policy. |
| Outcome correlation is unstable | Report uncertainty and collect more evidence; do not tune weights to force a result. |

## Example

```text
profile=enterprise-ae-v3; population=approved; calibration=pass; learner-export=none; outcome-link=correlation-only; review=quarterly
```

## Resources

- [Mindtickle Readiness Index](https://www.mindtickle.com/platform/analyze-sales-team-performance-sales-readiness-index/)
- [Mindtickle sales coaching](https://www.mindtickle.com/platform/sales-coaching-software/)

## Next Steps

Review the model with affected stakeholders and compare interventions against the frozen baseline.
