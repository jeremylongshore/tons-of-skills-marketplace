---
name: risk-analysis
description: >
  Analyze supplied contract clauses and prepare an evidence-linked issue register
  with triggers, possible impacts and questions for review. Use when assessing
  contract risks from an identified party's perspective. Trigger with
  "risk-analysis" or "what are the risks in this contract".
allowed-tools: Read, Glob, Grep, Write
version: 1.2.0
author: Intent Solutions <jeremy@intentsolutions.io>
license: MIT
tags:
  - legal
  - contracts
  - risk
  - analysis
  - due-diligence
  - compliance
compatibility: Designed for Claude Code
---

# Contract Risk Analysis

## Overview

Inspect supplied clauses across ten issue categories and produce a prioritized
review register. Separate observed terms, conditional scenarios, unknowns and
questions requiring legal judgment; do not invent probabilities or loss estimates.

## Prerequisites

- A selected contract or pasted text and available schedules/amendments.
- The represented party, business objectives and decision being considered. Reuse
  supplied context; do not default to the party assumed not to have drafted it.
- Coverage limits, relevant dates, stated fees/caps and any user-provided impact or
  risk rubric. Record unavailable facts instead of silently filling them in.

Use only authorized inputs and tools. Do not upload contracts, modify originals,
send counterproposals or run legal agents as an implicit part of this analysis.

## Instructions

1. Use Glob for discovery within the selected location when needed, then Read the
   supplied material. Record document versions, readable pages/sections, missing
   exhibits, extraction limits and relevant incorporated terms. A missing section
   is unreviewed, not evidence of low risk or unlimited exposure.
2. Map the party's rights and obligations with clause/page locators and minimal
   exact excerpts. Use Grep for definitions and cross-references in readable
   supplied text, then Read related provisions before interpreting a clause alone.
3. Review the [ten categories](references/risk-register.md). For each relevant
   issue, record the observed term, trigger, affected party, dependencies, possible
   commercial consequence and evidence gap. A category checklist does not prove
   that every clause was reviewed or that applicable law was satisfied.
4. Inspect broad definitions, survival, renewal/notice, unilateral amendments,
   assignment and incorporated fees in context. Show what the text says and which
   dependencies were checked. Do not label an ambiguity intentional or infer
   concealed motives from placement or wording alone.
5. Prioritize by the user's objectives, the obligation at stake, timing and
   evidence. Explain qualitative priorities. If numerical weights are requested,
   identify the explicit rubric and assumptions; do not treat a severity label as
   a measured probability or multiply it by an invented likelihood.
6. Quantify only what explicit inputs support. Distinguish a stated fee/cap, a
   conditional arithmetic scenario and a prediction of actual liability. Show the
   formula, currency, units, inputs and source clauses. Leave expected loss,
   enforcement costs, IP value and maximum exposure unknown when evidence is
   missing. A clause without a visible cap is not proof of legally infinite loss.
7. Offer specific clarification or negotiation options tied to findings. Separate
   user business preferences from legal questions. Do not select a walk-away
   threshold, declare enforceability or conclude all personal inventions are
   assigned based on one excerpt. Refer unresolved law/context questions for
   qualified review rather than inventing citations.
8. Produce the register and executive decision summary with actual coverage and
   uncertainty. When saving is requested, use Write at the selected path; suggest
   `contract-risk-{matter-slug}.md` for new work and inspect an existing destination
   before replacing it. Preserve original contracts and unrelated reports.

## Output

A review draft identifying the contract, party, business objective, source inputs
and coverage. Each finding has an ID, clause/page locator, exact supporting text,
category, trigger, possible effect, priority rationale, dependencies and next
question. Include a separate table for source-backed amounts or explicitly
conditional scenarios; unknown quantities remain unknown.

A summary may identify the most decision-relevant findings without forcing a top
five or an overall safety verdict. This analysis does not establish legal effect,
compliance, expected loss or an attorney-client relationship. State where current
jurisdiction-specific review and additional facts are needed.

## Error Handling

| Situation                                        | Recovery                                                                                                       |
| ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------- |
| Party perspective is missing                     | Ask before directional recommendations; factual clause mapping can proceed.                                    |
| Schedule or amendment is unavailable             | Mark the affected dependency unreviewed and explain the decision it prevents.                                  |
| Clause is ambiguous or conflicts with another    | Quote both readings/provisions and frame the unresolved question; do not increase a score for presumed intent. |
| Amount, frequency or probability is unknown      | Leave it unknown; calculate only a clearly stated conditional scenario when inputs exist.                      |
| Several jurisdictions or precedence terms appear | Record the exact provisions and seek applicable-context review rather than selecting one silently.             |
| Reader asks if the contract is safe to sign      | Explain the unresolved findings and business/legal decisions; do not convert a score into approval.            |

## Examples

**Stated fee scenario:** In a fictional example, a supplied clause sets a termination
fee at two monthly fees and the supplied rate is USD 5,000 per month. The conditional
arithmetic is 2 x USD 5,000 = USD 10,000 if that clause applies. Show those inputs;
this is not a prediction of collectible damages or a complete exit cost.

**Broad data license:** Quote the granted uses, duration and any deletion or
termination exceptions. Identify operational concerns for the user's stated data
constraints and questions about related clauses; do not automatically declare the
license unlawful or cured by the word anonymized.

**Invention assignment:** Review the definition, assignment, exclusions and supplied
employment context together. Identify a possible scope question without claiming
all personal side projects belong to the employer or giving a jurisdiction-free
conclusion about enforceability.

## Resources

- [Ten-category review and risk-register evidence](references/risk-register.md)
- Supplied clauses, schedules, fee data and the user's actual objectives/rubric.
