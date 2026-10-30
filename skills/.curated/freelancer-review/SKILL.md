---
name: freelancer-review
description: >
  Review a freelancer's supplied agreement across fourteen commercial lenses,
  with clause evidence, actual-work questions and scoped classification limits.
  Use when assessing a client or independent-contractor agreement. Trigger with
  "freelancer-review" or "review this contract as a freelancer".
allowed-tools: Read, Glob, Grep, Write
version: 1.2.0
author: Intent Solutions <jeremy@intentsolutions.io>
license: MIT
tags:
  - legal
  - contracts
  - freelancer
  - contractor
  - misclassification
  - gig-economy
compatibility: Designed for Claude Code
---

# Freelancer Agreement Review

## Overview

Review supplied terms from the identified freelancer's perspective and identify
commercial concerns, missing facts and questions for qualified review. Keep
contract wording separate from actual working arrangements and legal classification.

## Prerequisites

- The selected agreement, available SOWs/schedules and requested review scope.
- The user's role, objectives, work location/jurisdiction when known, rate/scope
  context and any actual working-practice facts they provide. Reuse explicit
  context; do not guess the represented party or claim rates are market-standard.
- Document coverage and extraction limits. Missing payment schedules or exhibits
  are unreviewed dependencies, not proof a duty or entitlement is absent.

Use only authorized inputs. Do not upload contracts, contact the client, submit a
worker-status filing, amend an agreement or invoke agents as part of this review.

## Instructions

1. Use Glob within the selected location if discovery is needed, then Read the
   supplied material. Record contract versions, pages/sections, missing attachments
   and any unreadable material. Preserve original files.
2. Map the [fourteen review lenses](references/freelancer-review-lenses.md) to the
   supplied terms. Use Grep for defined terms and cross-references, then Read the
   relevant context. Quote minimal supporting text with clause/page locators.
3. For each relevant lens, explain the observed term, possible practical effect,
   dependencies and the user's unresolved decision. Evaluate payment, scope,
   cancellation, IP and portfolio terms against actual objectives rather than a
   universal freelancer bill of rights or an invented fairness grade.
4. If worker status is relevant, identify which jurisdiction and legal/tax scheme
   is being considered. Separate contract statements from user-supplied facts about
   control, finances and the relationship. The IRS common-law framework concerns
   US federal employment tax; it is not a universal classification test.
5. Do not count indicators into low/moderate/high/near-certain classifications.
   The IRS does not prescribe a fixed factor count that decides status. A contract
   label, provided equipment, hourly pay or one clause alone does not establish the
   whole relationship. Identify missing facts and the scope of qualified review.
6. Prioritize concerns by the user's objectives, concrete obligations and timing.
   Offer clarification or negotiation options with their assumptions. Do not impose
   a payment period, kill-fee percentage, interest rate, IP outcome or walk-away
   rule as a universal entitlement or industry standard.
7. If a numeric preference rubric or replacement wording is explicitly requested,
   label proposed commercial choices and separate them from law and verified
   template text. Do not manufacture source versions, section numbers, market
   comparisons or classification probabilities.
8. Produce the review and next questions. If saving is requested, use Write at the
   chosen path, suggesting `freelancer-review-{matter-slug}.md` for new work. Read
   an existing destination before replacing it and report the actual saved path.

## Output

A review draft with party/objective, input identities and coverage, a lens register,
source-linked findings, classification-related facts/questions where relevant,
priorities and negotiation options. For each finding, include a clause/page,
minimal exact excerpt, possible effect, dependencies and unresolved facts.

Distinguish a requested commercial preference from a legal right, an observed
working fact from a contract promise, and a classification question from a ruling.
This report does not create an attorney-client relationship, establish worker
status, provide a tax determination or approve the agreement for signing.

## Error Handling

| Situation                                                  | Recovery                                                                                          |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Role or objectives are missing                             | Reuse available context and ask only for the missing decision before directional advice.          |
| Payment or SOW terms are in a missing attachment           | Mark the dependency unreviewed; do not infer zero compensation or unlimited scope.                |
| Contract and actual work differ                            | Record both evidence sources and the mismatch without selecting a legal classification.           |
| Jurisdiction or applicable worker-status regime is unknown | Keep classification unresolved; do not export IRS thresholds to another legal scheme.             |
| Market rate or desired protection is unspecified           | State the missing preference or benchmark rather than inventing fairness.                         |
| Draft language or a filing is requested                    | Identify the separate drafting/filing scope and required facts; do not send or submit implicitly. |

## Examples

**Fixed hours and location:** Quote a clause requiring office attendance and
record the user's actual-work facts separately. Ask how work is directed and
which classification question matters. Do not call thirteen checked boxes proof
of employment or assume remote work establishes independent-contractor status.

**Cancellation clause:** If the client may cancel on five days' notice, inspect
payment/SOW and termination provisions for completed work and expenses. Where
those materials are missing, report the gap instead of asserting the freelancer
will receive nothing. A proposed cancellation fee is a negotiable term, not a
universal right.

**Portfolio concern:** Identify any publication, confidentiality and license
provisions affecting the user's portfolio goal. Suggest a scoped clarification
or request without assuming a legal entitlement to disclose the client's work.

## Resources

- [Fourteen lenses and classification evidence](references/freelancer-review-lenses.md)
- Supplied agreement, SOWs and actual working-practice facts.
