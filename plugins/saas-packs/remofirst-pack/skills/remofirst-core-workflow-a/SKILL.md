---
name: remofirst-core-workflow-a
description: >-
  Manage and control a RemoFirst Employer-of-Record employee onboarding with
  country, contract, compensation, leave, benefit, and document checkpoints.
  Use when hiring a full-time worker through RemoFirst. Trigger with "onboard
  RemoFirst employee", "RemoFirst EOR hire", or "global employee checklist".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<country> <target-start-date>"
version: 2.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, remofirst, eor, employee-onboarding, compliance]
model: inherit
effort: high
compatibility: Designed for Claude Code; live RemoFirst access requires an approved client account and explicit operator action
---
# RemoFirst EOR Employee Onboarding Control

## Overview

Turn an approved global hire into a reviewable onboarding packet before a human
uses RemoFirst's People > Add employee flow. Country options, employment type,
contract type, payment frequency, leave, benefits, and local documents vary;
never infer them from another country or treat this skill as legal advice.

## Prerequisites

- Approved hire, employing country/region, target start date, and budget owner.
- Named People operator and authorized signatory.
- RemoFirst/local-team confirmation for country-specific requirements.

## Current Contract

The documented flow captures team and location, personal/contact/address data,
visa needs, job details, employment and contract type, compensation and payment
frequency, additional compensation, leave policy, and optional RemoHealth,
RemoTech, or RemoCheck services. Submission starts RemoFirst review; it does not
make the worker active. The worker later supplies documents and signs an agreement.

## Instructions

1. Create a redacted control record with country/region, role, employment type,
   proposed contract type, target start date, manager, and accountable approver.
2. Separate worker-supplied personal data from client decisions. Minimize fields
   in the working packet and keep identity documents out of repository artifacts.
3. Confirm country-dependent options with RemoFirst before setting compensation,
   frequency, leave, benefits, visa, background-check, or equipment choices.
4. Reconcile salary, currency, frequency, allowances, bonus, leave, and optional
   services against the approved offer and budget. Record unresolved differences.
5. Run a two-person review of job description, location, dates, manager, and all
   money-bearing fields before a human selects Continue.
6. After approved submission, record only the RemoFirst status and next owner.
   Do not copy documents or sensitive screens into the repository.
7. Treat Active as dependent on required documents and agreement signatures;
   escalate rejected documents through the documented operator flow.

## Tool Discipline

Use Read, Glob, and Grep for approved offer, policy, and checklist artifacts. Use
Write/Edit only for redacted control records and templates. These tools do not
authorize entering or submitting worker data in RemoFirst.

## Approval Boundaries

Require explicit approval before entering personal data, selecting employment or
contract type, committing compensation/benefits, ordering checks/equipment, or
submitting the hire. Never manufacture local-law, tax, leave, or visa guidance.

## Output

Return the redacted hire key, country, target date, field-completeness matrix,
country confirmations, financial reconciliation, document/signature states,
approvers, current status, blockers, and next operator action.

## Error Handling

- Country option unavailable: stop and ask RemoFirst; do not choose a substitute.
- Offer and platform differ: block submission until the business owner resolves it.
- Rejected document: preserve the reason and request a corrected worker upload.
- Start date at risk: surface the dependency; never bypass review or signatures.

## Examples

- "Prepare a UK EOR hire for 1 October" yields a country-confirmation and
  two-person review packet, not an automatic employee creation.
- "Reuse the US PTO defaults for France" is rejected as unsupported inference.
- "Upload this passport from the repo" is rejected as an unsafe data path.

## Validation

- All money, date, location, contract, leave, and benefit fields have owners.
- Country-specific choices are provider-confirmed rather than inferred.
- No sensitive document or unsupported API instruction is present.

## Resources

See [references/official-docs.md](references/official-docs.md) for the reviewed
employee onboarding, activation, EOR, access, and support sources.
