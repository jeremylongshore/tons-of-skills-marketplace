---
name: abridge-debug-bundle
description: "Produce a PHI-minimized Abridge support bundle with provenance, redaction, and protected escalation boundaries. Use when support needs reproducible evidence for an Abridge issue. Trigger with \"build an Abridge debug bundle\"."
argument-hint: "[incident-id] [time-window]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- abridge
- diagnostics
- privacy
- support-bundle
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Abridge tenant, approved test data, and health-system change authority
---
# Abridge Minimum-Necessary Support Bundle

## Overview

Collect configuration presence, component versions, coarse timestamps, correlation references, and observed outcomes without copying recordings, transcripts, generated notes, patient identifiers, tokens, or unrestricted logs.

## Prerequisites

- The authorized Abridge environment, clinical owner, and health-system policy set
- Current tenant-specific implementation evidence for every private interface in scope
- Synthetic data or the organization's formally approved test-record procedure

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository configuration, adapters, tests, policies, and existing evidence. Use `WebFetch` only for current official Abridge, HHS, or named EHR documentation. Use `Write` or `Edit` only after confirming scope, environment, owners, patient-data boundary, and approval state. These tools do not confer access to Abridge, an EHR, or a clinical record; return exact operator steps or an approval-gated handoff for live actions.

## Current Contract

- Abridge describes secure data handling and provides a protected support route, but public support content does not authorize exporting clinical content into ordinary tickets.
- HIPAA's minimum-necessary principle should shape diagnostic collection and access.
- A redacted value can still be identifying when combined with exact timestamps, user IDs, or rare workflow details.

## Authentication

Use only the health system's provisioned Abridge application access, SSO, administrative role, or tenant-specific partner authentication documented for the approved environment. Do not infer public API credentials, reuse production secrets in tests, or expose tokens and session material. Verify identity owner, least privilege, environment binding, storage, rotation, and revocation before any authenticated action.

## Instructions

1. Define the incident, recipient, protected channel, retention period, and exact evidence questions before collection.
2. Use `Read`, `Glob`, and `Grep` to locate approved logs and configuration names; do not recursively collect an application directory.
3. Allowlist fields such as component version, environment label, coarse time bucket, outcome class, and opaque support correlation reference.
4. Reject audio, transcript, note text, patient or clinician identifiers, URLs with query data, secrets, cookies, and authorization headers.
5. Use `Write` or `Edit` to create the bounded bundle and a manifest; have a second reviewer attest to the redaction.
6. Use `WebFetch` only to confirm current official Abridge security and support guidance before transfer.

## Approval Boundaries

Do not attach a bundle to email, chat, or a public issue unless the privacy and security owners approve that channel and the bundle passes review.

## Output

Return manifest, source classes, allowlisted fields, redaction counts, reviewer, destination, expiry, and excluded evidence classes. Separate verified facts, tenant-specific evidence, assumptions, and actions still awaiting approval.

## Error Handling

| Condition | Response |
|---|---|
| Sensitive value cannot be classified | Exclude it by default. |
| Recipient requests raw logs | Move to the approved protected disclosure process. |
| Bundle cannot reproduce the symptom | Document the limitation; do not broaden collection silently. |

## Example

The example is a redacted operational receipt, not patient data or proof of vendor certification.

```text
incident=INC-2041; window=15m-rounded; files=3; rejected-fields=17; phi=none-observed; reviewer=privacy-oncall; expiry=7d
```

## Resources

- [Official documentation map](references/official-docs.md) — dated public evidence and the limits of what those sources establish.

Read the source map before changing a workflow. Recheck tenant-specific implementation evidence for every interface or capability that public documentation does not define.

## Next Steps

Revalidate the evidence date and tenant-specific authority before repeating this workflow in another environment, cohort, care setting, or integration mode.
