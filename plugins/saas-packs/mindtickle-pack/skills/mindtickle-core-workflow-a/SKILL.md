---
name: mindtickle-core-workflow-a
description: 'Plan, approve, launch, and verify a governed Mindtickle learning program for a defined audience. Use when rolling out courses, assessments, certifications, or reinforcement. Trigger with "launch a Mindtickle program".'
argument-hint: "[program-brief] [audience]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, mindtickle, learning, program-launch, governance]
model: inherit
effort: medium
compatibility: Designed for Claude Code; publishing content, assigning learners, and sending notifications require program-owner and tenant-admin approval
---
# Governed Mindtickle Learning Program Launch

## Overview

Convert an approved enablement brief into a controlled program release with audience, content, measurement, communications, and rollback evidence.

## Prerequisites

- A program owner, business outcome, audience source, due dates, and completion definition
- Confirmed tenant entitlements for the selected module types
- Approved content, accessibility review, privacy classification, and support owner

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect briefs and rosters, `WebFetch` for current product and tenant contracts, and `Write` or `Edit` for plans, validation fixtures, and redacted receipts.

## Current Contract

Mindtickle publicly describes courses, quick updates, checklists, certifications, instructor-led training, assessments, reinforcement, role-plays, coaching, and analytics. Exact creation, assignment, reminder, and reporting behavior depends on the subscribed package and current tenant configuration.

## Authentication

Use an authorized program administrator or a documented tenant API principal with only the required capabilities. Separate authoring, assignment, and reporting permissions and never embed credentials in content packages.

## Instructions

1. Freeze the brief: outcome, audience, exclusions, modules, passing rules, dates, locales, accessibility, and retention.
2. Confirm every module type and reporting field against the tenant entitlement and current documentation.
3. Validate content ownership, links, media, assessment answers, completion criteria, and representative mobile behavior.
4. Reconcile the audience to its system of record; quantify additions, removals, duplicates, disabled users, and managers.
5. Run a pilot with synthetic or approved users and verify assignment, navigation, completion, reporting, and support paths.
6. Present a launch preview with exact counts, schedule, notifications, risks, owner, and rollback.
7. After approval, publish and assign through the supported tenant path, then reconcile expected versus actual state.
8. Retain a redacted launch receipt and schedule outcome reviews rather than measuring completion alone.

## Approval Boundaries

Do not publish, assign users, alter passing rules, send communications, or replace live content without the program and data owners.

## Output

Return the frozen brief, entitlement check, content and audience validation, pilot evidence, mutation preview, launch receipt, reconciliation, and review schedule.

## Error Handling

| Condition | Response |
|---|---|
| Audience reconciliation is incomplete | Block assignment until the system-of-record owner resolves it. |
| Pilot reporting does not match completion | Preserve both observations and escalate the tenant contract; do not edit scores. |
| Launch is partially applied | Stop notifications, reconcile actual assignments, and execute the approved rollback. |

## Example

```text
program=q4-certification; audience=142; excluded=3; pilot=pass; approved=program-owner; assigned=142; reconciliation=exact
```

## Resources

- [Subscription services](https://www.mindtickle.com/legal/description-of-subscription-services/)
- [Mindtickle sales training](https://www.mindtickle.com/platform/pre-built-sales-training/)

## Next Steps

Use outcome evidence in the readiness workflow without redefining scores after launch.
