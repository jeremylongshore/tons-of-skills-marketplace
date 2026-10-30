---
name: compliance-audit
description: "Use when reviewing a website, application, or supplied evidence for potential gaps across GDPR, CCPA/CPRA, accessibility, PCI DSS, CAN-SPAM, COPPA, or SOC 2 readiness. Produces scoped findings, applicability questions, and an evidence-based remediation plan."
allowed-tools: Read, Glob, Grep, WebFetch
version: 1.2.0
author: Intent Solutions <jeremy@intentsolutions.io>
license: MIT
tags:
- legal
- compliance
- gdpr
- ccpa
- ada
- pci-dss
- audit
- regulatory
compatibility: Designed for Claude Code
---
# Compliance Evidence Review

## Overview

Review supplied assets across seven compliance lenses and produce a traceable gap
register and remediation plan. Establish applicability and evidence coverage before
judging a control. This is readiness analysis, not a legal opinion, certification,
attestation, or a substitute for an assessor's examination.

## Prerequisites

Obtain the requested URL or local paths, business activity, relevant jurisdictions,
service population, system boundary, and assessment purpose. Ask for missing facts
that determine applicability; continue useful evidence collection while labeling
those questions unresolved. Use only authorized accessible material. Do not submit
forms, purchase services, send email, upload personal data, or exercise live security
controls as a consequence of this review.

## Instructions

1. **Agree on scope.** Record assets, snapshot/commit or retrieval date, environments,
   relevant user journeys, available evidence, and exclusions. A single public page
   is a page sample, not a review of the whole organization. Select the relevant
   lenses from [framework-lenses.md](references/framework-lenses.md); read only the
   sections needed. Verify the applicable current authority/version and effective
   dates before making a requirement-specific finding. A feature is a signal to
   investigate applicability, not proof a law applies.
2. **Collect an evidence inventory.** Read supplied policies, contracts, operational
   records and code using Read, Glob and Grep. Use WebFetch for permitted public
   sources and the requested site. Record each source with a path/section or URL,
   date, and what it actually reveals. A fetched page may omit headers, cookies,
   JavaScript execution, authenticated flows and network requests. An HTTPS URL
   does not establish certificate configuration or encryption everywhere. Code
   presence does not prove deployed behavior or sustained control operation.
3. **Evaluate applicable criteria.** For each criterion record the authority and
   version, applicability rationale, expected evidence, inspected evidence and
   observation. Distinguish `observed`, `owner-asserted`, `not tested`, `not provided`,
   `contradictory`, and `not applicable with rationale`. Report a confirmed scoped
   gap only when the applicable requirement and actual evidence support it. Do
   not turn missing access or an unsuccessful search into a finding of absence.
4. **Explain practical effects.** Tie each finding to the affected data, actor,
   workflow or commitment. Separate technical observations from legal questions.
   A static code pattern may warrant a test; it does not establish a violation,
   enforceability, fine, lawsuit probability or organization-wide compliance.
5. **Prioritize remediation.** Give each issue a stable ID, supported impact,
   concrete next action, suggested owner, dependencies, evidence needed and a
   verification condition. Distinguish fixing a demonstrated defect from obtaining
   missing evidence. Use supplied milestones and genuine applicable deadlines;
   otherwise mark dates and estimates proposed or unknown. Do not invent hours,
   penalty exposure, deadlines or an obligation to remediate an inapplicable topic.
6. **Deliver the report.** Present Markdown in the conversation. The current toolset
   does not include file writing; offer a suggested filename without claiming a
   file was created. Do not modify source assets. Revisions should retain finding
   IDs and show which new evidence changed a conclusion.

## Output

Suggested filename: `COMPLIANCE-AUDIT-{company}-{review-date}.md`, using the actual
review date and a supplied company identifier. Include:

- Scope, assets, evidence dates, purpose and limitations.
- Applicability matrix: lens, authority/version, rationale and unresolved facts.
- Evidence inventory with locators and source status.
- Findings table: ID, criterion, evidence, observation, status, impact and question.
- Remediation plan: action, owner proposal, dependencies and verification evidence.
- Unassessed controls, missing evidence and matters for qualified review.

If requested, report transparent coverage counts such as “3 of 8 selected criteria
examined; 5 unassessed.” Name the denominator and exclusions. Do not convert counts
into compliance percentages, safety grades, aggregate compliance status, or claims
that unknown criteria passed. No SOC 2 report or regulatory approval is issued here.

## Error Handling

- **Unreachable site or unsupported document:** identify the failed source and ask
  for an accessible export or authorized evidence; preserve the unassessed status.
- **Only frontend evidence:** limit findings to the sampled representation and
  list backend, organizational and runtime evidence still needed.
- **Unclear applicability:** state the missing business/jurisdiction facts and seek
  a qualified determination; do not automatically mark the framework applicable.
- **Conflicting policy and implementation:** cite both, identify the version/date
  mismatch and request the authoritative deployed behavior; do not silently pick.
- **Current authority unavailable:** identify the unavailable source and withhold
  the dependent legal conclusion rather than inventing a requirement.

## Examples

**Public shop page.** A supplied page includes a payment-provider script and a
privacy link. Record those two observations and request the actual checkout/data
flow and merchant assessment evidence. Neither observation proves PCI DSS scope,
processor compliance, lawful processing, or the absence of a rights mechanism.

**Local application.** A repository contains an unsubscribe handler but no supplied
execution evidence. Cite the handler and mark operational suppression timing not
tested. Propose an authorized fixture-based check; do not send a real campaign or
claim requests are honored from code inspection alone.

## Resources

Use the linked [framework lenses](references/framework-lenses.md) for targeted
questions and primary sources. Record the authorities actually inspected in the
report; links alone do not mean their requirements were evaluated.
