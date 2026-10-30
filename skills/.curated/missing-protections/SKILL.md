---
name: missing-protections
description: >
  Review supplied contract terms for relevant protection gaps, with applicability,
  coverage limits, source evidence and scoped drafting options when requested.
  Use when checking what protections a contract may be missing. Trigger with
  "missing-protections" or "what protections is this contract missing".
allowed-tools: Read, Glob, Grep, Write
version: 1.2.0
author: Intent Solutions <jeremy@intentsolutions.io>
license: MIT
tags:
  - legal
  - contracts
  - gap-analysis
  - protections
  - compliance
  - checklist
compatibility: Designed for Claude Code
---

# Contract Protection Gap Review

## Overview

Inspect relevant clause topics against the supplied contract, represented party
and business objectives. Distinguish an actual gap, partial/conflicting coverage,
missing evidence and a topic that is not relevant; no checklist fits every agreement.

## Prerequisites

- The selected contract, available schedules/amendments and requested scope.
- Contract type, represented party and objectives when supplied. Do not assume the
  user is the non-drafting or weaker party.
- Coverage/extraction limits, known jurisdiction and any user-selected template or
  policy benchmark. A template is not itself proof of applicable law or market practice.

Use authorized inputs only. Do not upload originals, amend the contract, send
negotiation messages or generate legal filings as an implicit part of gap review.

## Instructions

1. Use Glob for discovery within the chosen input location if needed, then Read
   the supplied material. Record version identities, readable pages/sections,
   missing exhibits and incorporated terms. Preserve the originals.
2. Select relevant items from [the candidate topic checklist](references/protection-topics.md)
   and any type-specific questions. Explain applicability. A confidentiality, data,
   termination or liability clause is not automatically required in every agreement.
3. Use Grep for relevant terms, definitions and cross-references, then Read their
   context. Check schedules, exceptions and precedence when available. A search
   miss in incomplete text is not proof a protection is absent.
4. Assign an evidence status: addressed, partial, conflicting, not found in reviewed
   material, unreviewed, or not relevant with a reason. Include clause/page locators
   and minimal exact excerpts, and identify the missing fact or document needed.
5. Explain possible commercial consequences and priorities against the user's
   objectives. Do not state that silence always favors one party, automatically
   creates unlimited exposure, or means a term must be added before signing.
   Separate a requested business preference from a verified legal requirement.
6. For a law-based assertion, identify applicability, party role, jurisdiction,
   recipient, trigger and current primary authority. Do not assign the same breach
   deadline to controller-to-authority and processor-to-controller notification or
   attribute an unrelated rule to CCPA without checking the actual provision.
   If verification is unavailable, flag the question instead of asserting the rule.
7. If drafting is requested, provide proposed language with explicit parameters,
   assumptions, placement/dependency checks and qualified-review questions. Verify
   any template source/version/license and actual passage before copying or
   attributing it. Do not invent template sections, standard rates, cancellation
   percentages, notice periods or universal NDA durations.
8. Produce a source-linked gap register and next questions. Count coverage only
   over an explicit relevant, reviewed denominator; keep unknowns separate and
   do not call a percentage a safety/compliance score. If saving is requested,
   use Write at the selected path, suggesting `protection-gaps-{matter-slug}.md`
   for new work and inspecting an existing destination before replacing it.

## Output

A review draft with contract/party/objectives, input versions, actual coverage and
benchmark applicability. For each relevant topic include status, source locator,
observed wording or search/coverage limit, possible effect, dependencies, priority
rationale and a specific next question. Include proposed clauses only within a
requested drafting scope, clearly separated from source quotations and verified law.

This register does not establish enforceability, compliance, signing approval or
an attorney-client relationship. Identify where current legal context, additional
facts or qualified review is still needed rather than filling gaps with certainty.

## Error Handling

| Situation                                             | Recovery                                                                                              |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Party or contract type is unclear                     | Use tentative mapping and ask for the missing context before directional recommendations.             |
| Schedule or extraction is incomplete                  | Mark dependent topics unreviewed; do not count them as missing or passed.                             |
| Clauses partly address or conflict on a topic         | Show the exact provisions and dependencies rather than a binary verdict.                              |
| A topic does not fit the transaction                  | Mark not relevant with rationale; do not add boilerplate merely for checklist coverage.               |
| Legal rule or template attribution cannot be verified | Leave the claim unresolved or label original proposed language; never fabricate a citation.           |
| Draft language depends on unknown commercial terms    | Ask for the material choice or list it as a proposed parameter; do not assert a default is mandatory. |

## Examples

**Cancellation concern:** A freelance agreement lacks a visible cancellation-fee
clause, but its payment schedule was not supplied. Mark payment consequences
unreviewed and ask for that schedule. If the user wants a cancellation-fee proposal,
obtain or label its commercial parameters instead of inserting a universal 25% fee.

**Breach notice:** A processing agreement says notice is prompt. Identify the
actual roles, recipient, trigger and applicable regime before proposing a contract
term. GDPR Article 33 distinguishes controller-to-authority and processor-to-controller
duties; do not treat seventy-two hours as the processor's universal deadline.

**Confidentiality topic:** For a transaction where no confidential information is
expected, ask whether the topic is relevant rather than automatically labeling the
absence of an NDA a critical defect. Preserve the user's actual objectives.

## Resources

- [Candidate topics, statuses and role-specific source checks](references/protection-topics.md)
- Supplied clauses, schedules, objectives and explicitly selected benchmarks.
