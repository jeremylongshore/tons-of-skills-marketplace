---
name: contract-review
description: "Use when reviewing a supplied contract for clause meaning, obligations, risks, missing protections, and regulatory questions. Produces an evidence-linked executive report with actual document coverage. Trigger with /contract-review or review this contract."
allowed-tools: Read, Glob, Grep, Task
version: 1.2.0
author: Intent Solutions <jeremy@intentsolutions.io>
license: MIT
tags:
- legal
- contracts
- review
- risk
- orchestration
- multi-agent
compatibility: Designed for Claude Code
---
# Contract Review

## Overview

Produce a practical review of a supplied agreement from the identified party's
perspective, with source-linked findings, unresolved questions and negotiation
options. Use multiple analysis lenses and optional permitted delegation without
turning agreement between reviewers into proof of legal correctness.

## Prerequisites

Obtain readable contract text or an accessible file, the user's role, review goal,
and relevant commercial priorities. Identify known jurisdiction and transaction
context without inferring them from a company name. Use the actual document tools
available; Read support for one format does not guarantee DOCX, scanned PDF or
encrypted-file extraction. Ask for an accessible export when necessary.

## Instructions

1. **Establish the document boundary.** Use Glob to locate the supplied document
   set, Read to inspect accessible content, and Grep to find defined terms and
   cross-references within that set. Record title, version/date, source path,
   party roles, schedules, incorporated documents and amendments available. Keep
   originals unchanged. Identify missing pages, tables, signatures and extraction
   uncertainty. Maintain a section/page coverage map for long contracts; process
   accessible sections in bounded passes and reconcile definitions/cross-references.
   Do not silently summarize unread portions or call an excerpt a full review.
2. **Build the clause inventory.** Extract actual parties, dates, duration,
   obligations, payment terms, termination, rights, liability and dispute provisions
   with locators. Mark unstated facts unknown, distinguish signature date from
   effective date, and follow amendment/precedence language. Classify the agreement
   provisionally (employment, contractor, NDA, services, software/SaaS, terms,
   privacy/data processing, partnership, lease, or other) without forcing a fit.
3. **Choose the execution mode.** Direct analysis is valid. Delegate only if the
   session permits it and the named agent/tool is actually available. The declared
   Task tool is a legacy delegation alias; use the supported equivalent only for
   that permitted delegation. Read
   [review-and-handoff.md](references/review-and-handoff.md) when using delegation
   or combining multiple reviewers. The bundled agents are `legal-clauses`,
   `legal-risks`, `legal-compliance`, `legal-obligations`, and
   `legal-recommendations`; they are not five interchangeable parallel reviewers.
   Inventory precedes dependent analysis, and recommendations consume the actual
   available findings. Do not spawn agents merely because this skill mentions them.
4. **Review through five lenses.** Explain material clauses in plain language;
   assess commercial risks; examine relevant missing/partial protections; identify
   regulatory questions; compare actual obligations and negotiating positions.
   Preserve actors, conditions, exceptions, units, definitions and negations.
   Reuse applicable bundled skill guidance where available, including risk-analysis,
   plain-english, missing-protections and compliance-audit. Candidate topics are
   not clauses every agreement must contain. A missing attachment can prevent a
   finding about whether a protection is absent.
5. **Separate evidence from conclusions.** For every finding retain the exact
   locator and minimal necessary quote, observed wording, qualified possible
   effect, dependencies and unresolved facts. Check calculations against actual
   amounts/time windows and label conditional scenarios. Do not invent loss
   probabilities, fairness percentages, reading levels or a Contract Safety Score.
   Optional user-defined prioritization is a decision aid with a stated rubric,
   not a signing recommendation or calibrated legal-risk measurement.
6. **Check authority and contradictions.** Regulatory applicability/enforceability
   need the relevant facts and current jurisdiction-specific authority. This
   skill's toolset has no web research tool: use supplied verified sources or
   identify research still needed. Reject unsupported findings even if multiple
   reviewers repeat them. Reconcile inconsistent locators, definitions, versions
   and recommendations; preserve unresolved disagreements explicitly.
7. **Synthesize a usable report.** Rank supported issues by the user's stated
   priorities and explain the basis. Present proposed changes, tradeoffs, questions
   for the other party and matters needing qualified counsel. Distinguish an
   observed issue, proposed wording and an accepted decision. Do not claim the
   agreement is safe to sign, legally compliant or equivalent to a law-firm review.
   Present the report in chat; the current toolset lacks Write, so a suggested
   filename is not evidence a report was saved.

## Output

Suggested filename: `CONTRACT-REVIEW-{title}-{review-date}.md`, with actual supplied
identity and review date. Include:

- Executive summary with the most material supported issues and open decisions.
- Document metadata, coverage, missing material and analysis mode actually used.
- Clause inventory and plain-language explanation of critical provisions.
- Findings register: stable ID, locator, wording, possible effect, assumptions,
  status, priority rationale and proposed next action.
- Relevant gaps and applicability questions, with evidence status.
- Obligations/rights comparison, amounts and timing with calculation assumptions.
- Negotiation options, unresolved disagreements and research/counsel questions.

No overall safety grade or automated accept/reject verdict. Describe partial work
as partial and identify any requested deliverable that could not be produced.

## Error Handling

- **Missing/unreadable document:** identify the source and extraction problem;
  request an accessible copy rather than pretending the full text was reviewed.
- **Missing context:** continue textual analysis and label context-dependent
  findings provisional. Ask only for facts that materially change the review.
- **Unavailable or failed agent:** report the actual failure. Perform a permitted
  direct pass where useful, otherwise leave that lens unassessed; no invented run.
- **Conflicting findings:** return to quoted text, definitions and authority;
  reviewer count does not resolve a legal or factual disagreement.
- **Sensitive contract:** include only necessary excerpts and approved destinations;
  delegation does not imply permission for external uploads or disclosure.

## Examples

**Services agreement.** The supplied Section 8 limits specified liability to fees
paid during a defined period, but an unavailable schedule may contain exceptions.
Quote Section 8, explain its scope and request the schedule. Do not label exposure
unlimited or compute a loss forecast without the actual exception and fee facts.

**Pasted NDA excerpt.** Review the disclosure and recipient obligations shown,
identify missing definitions/term provisions as not supplied, and explain how they
could change the analysis. Report excerpt coverage and practical questions; do
not assign an F grade because the pasted excerpt omits the rest of the agreement.

## Resources

Read [review-and-handoff.md](references/review-and-handoff.md) for the actual bundled
agent dependency map and evidence contract. Legal interpretation remains dependent
on facts, current authority and qualified review; no attorney-client relationship
or legal opinion is created by this workflow.
