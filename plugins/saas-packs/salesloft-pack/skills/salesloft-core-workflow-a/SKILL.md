---
name: salesloft-core-workflow-a
description: >-
  Analyze and resolve a Salesloft person, then enroll that person in an approved cadence with duplicate, visibility, and consent safeguards. Use when automating controlled prospect enrollment. Trigger with "Salesloft cadence enrollment", "add person to Salesloft cadence", or "Salesloft person workflow".
argument-hint: "[repository-path] [team-alias] [cadence-id]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- salesloft
- cadences
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Salesloft Controlled Cadence Enrollment

## Overview

This skill turns person resolution and cadence enrollment into one auditable workflow. It prevents demo writes, duplicate people, accidental owner changes, and enrollment into an unapproved cadence.

## Prerequisites

- Approved Salesloft team, cadence ID, acting user, and business purpose
- `people:read`, required person-write scope when creation is approved, and `cadences:read` or write scope as documented
- Consent and contact-restriction policy for the target person
- A durable application correlation key and rollback owner

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to find person resolution, cadence, and CRM ownership code. Use `WebFetch` only for current official endpoint documentation. Use `Write` or `Edit` after the mutation boundary is approved.

## Current Contract

- `POST /v2/people` requires either an email address or phone plus last name as a unique lookup basis.
- A person's `do_not_contact` and `contact_restrictions` affect permitted communication and cadence steps.
- `POST /v2/cadence_memberships` requires visible `person_id` and `cadence_id` values.
- Acting for a teammate is constrained by team-cadence ownership or Personal Cadence Admin permission.
- Cadence membership records are mutable and can represent later re-enrollment, not immutable event history.

## Authentication

Use a tenant-bound Bearer credential with only the scopes needed for the chosen read or write steps. Prove team and acting-user identity before mutation.

## Instructions

1. Confirm team, person lookup, approved cadence, acting user, consent state, and owned fields.
2. Search using only documented person filters and handle zero, one, or multiple candidates explicitly.
3. If no person exists, present the exact create payload and endpoint content type for approval.
4. Re-read the person and stop for `do_not_contact`, incompatible restrictions, or identity ambiguity.
5. Inspect current and historical cadence membership before adding a new membership.
6. Create one membership only after cadence visibility and acting-user permission are proven.
7. Read back the membership state and retain correlation, approval, and rollback evidence.

## Approval Boundaries

Creating or updating a person and enrolling in a cadence are live CRM mutations. Require explicit target and payload approval; never bypass consent, contact restrictions, teammate permissions, or an ambiguous match.

## Output

Return team, person resolution, consent checks, cadence and acting-user proof, proposed or executed mutation, read-after-write state, and rollback owner.

## Error Handling

| Condition | Response |
|---|---|
| Multiple person matches | Stop and request a stable external identifier. |
| 403 | Verify scope, visibility, cadence ownership, and acting-user permission. |
| 422 | Preserve field-keyed errors and correct only approved fields. |
| Pending/processing membership | Do not submit another enrollment; poll the existing record. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
team=staging; person=resolved; consent=pass; cadence=approved; action=awaiting-approval
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Create a person](https://developers.salesloft.com/docs/api/people-create/)
- [Create a cadence membership](https://developers.salesloft.com/docs/api/cadence-memberships-create/)
