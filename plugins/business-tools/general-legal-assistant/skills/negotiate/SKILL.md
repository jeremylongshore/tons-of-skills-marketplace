---
name: negotiate
description: "Use when preparing clause-linked contract counterproposals, fallback positions, or a negotiation email draft from supplied terms and commercial priorities. Trigger with /negotiate or generate counter-proposals for this contract."
allowed-tools: Read, Glob, Grep
version: 1.2.0
author: Intent Solutions <jeremy@intentsolutions.io>
license: MIT
tags:
- legal
- negotiation
- contracts
- counter-proposal
compatibility: Designed for Claude Code
---
# Contract Negotiation Strategy

## Overview

Turn a supplied agreement and the user's actual priorities into a traceable
negotiation plan with proposed replacement language, fallback options and an
optional email draft. Distinguish source facts, commercial preferences, legal
questions and decisions the user has actually approved.

## Prerequisites

Obtain the agreement/version, represented party, negotiation goal and known
constraints. Ask for material missing context such as approved deal-breakers,
budget, operational commitments and fallback limits; do not infer bargaining
leverage from company size. Review only readable supplied or authorized material.
No external source access or file-writing tool is declared by this skill.

## Instructions

1. **Identify the source.** Use Glob to locate the requested agreement and related
   schedules, Read for accessible text and Grep for definitions/cross-references.
   Record version, source locators, amendments and actual review coverage. If the
   file is unreadable, incomplete or an excerpt, request an accessible export and
   identify unreviewed material. Preserve originals; no automatic redlining.
2. **Establish the decision context.** Record actual party roles, objectives,
   constraints, approved priorities and open questions. Extract amounts, units,
   dates and obligations exactly. Separate stated terms from proposed changes;
   unknown rates, durations, caps, jurisdictions and concessions remain unknown.
3. **Review contextual issue lenses.** Examine liability/indemnity, termination,
   intellectual property, payment, confidentiality, restrictive covenants,
   liability exclusions, disputes/governing law, data/privacy and force majeure.
   These are prompts to evaluate relevance, not mandatory defects. Review triggers,
   exceptions, definitions and related provisions before describing something as
   absent, perpetual, unlimited or one-sided. An asymmetric term may reflect an
   actual role difference; explain its practical effect without assuming unfairness.
4. **Prioritize supported issues.** Use the user's approved must-change positions,
   important objectives and optional improvements. Where the user has not chosen
   those categories, propose a priority with reasons and mark it unconfirmed.
   Do not declare a deal-breaker, walk-away threshold, legal violation or signing
   verdict from a generic heuristic. Explain technical/commercial uncertainty
   separately from the importance the user assigns to it.
5. **Draft counterproposals.** For each issue quote only the necessary source text
   with a locator, explain the possible effect, state the requested objective and
   propose precise language with explicit assumptions. Preserve defined terms and
   cross-reference consistency. Offer a fallback and explain what it trades away;
   do not silently replace an approved position. Use actual supplied numbers or
   clearly marked unresolved parameters, never invented notice windows, fees,
   discounts, liability caps or restrictive-covenant durations.
6. **Use sources honestly.** Read [proposal-and-source-checks.md](references/proposal-and-source-checks.md)
   when comparing a template or preparing replacement language. A benchmark needs
   the actual inspected passage, source/version and applicable reuse terms.
   A CommonPaper, Bonterms or other template is an example of drafting, not proof
   of market prevalence or suitability. Without an accessible supplied source,
   label wording an original proposed draft and identify research still needed.
   Do not list sources that were not consulted or claim performed benchmarking.
7. **Prepare communication if requested.** Draft a concise unsent email referencing
   actual clause IDs, explaining the requested changes and their rationale. Call
   substantive changes substantive; do not disguise concessions or rights changes
   as mere clarifications. Use the user's actual tone and next-step preference,
   without inventing prior agreement, approval or a scheduled call. The draft
   does not authorize sending or contacting the other party.
8. **Deliver and reconcile.** Present the strategy in chat. The current tools do
   not save a file; suggest a filename without claiming it exists. On revision,
   retain issue IDs, show which positions changed and distinguish proposed,
   counterparty-reported and actually agreed terms. Incorporate new evidence
   without inventing a successful negotiation outcome.

## Output

Suggested filename: `NEGOTIATION-STRATEGY-{contract-name}.md`, using the actual
contract identity. Include scope/coverage, represented party, objectives and
unresolved context, followed by an issue register:

| Field | Required content |
| --- | --- |
| Issue | Stable ID, source clause/definition and minimal quote |
| Effect | Qualified explanation and supporting facts |
| Priority | User-approved or proposed, with rationale |
| Objective | Commercial result sought and relevant constraints |
| Proposal | Draft wording, explicit parameters and assumptions |
| Fallback | Alternative plus conceded benefit or remaining risk |
| Source | Actual template passage/version/license, or original draft |
| Review | Open legal/operational questions and approval status |

Include a truthful unsent email draft only when useful or requested. State missing
sources and legal research needed. No numerical acceptance probability, market
confidence badge, safety grade or claim that the proposals are enforceable.

## Error Handling

- **Multiple versions:** confirm the intended baseline or compare them explicitly;
  do not mix clauses from different drafts without disclosure.
- **Unknown party or goal:** ask for that material context; continue extraction
  while leaving side-dependent proposals unassigned.
- **Missing governing facts/current authority:** qualify the recommendation and
  flag the research question. This read-only skill cannot verify current law
  through a nonexistent network tool.
- **Specialized or unfamiliar language:** identify the affected clauses, preserve
  original wording and request suitable translation or specialist review rather
  than assuming every agreement follows English common-law conventions.
- **Unavailable benchmark:** label the source unavailable and draft from supplied
  objectives where possible; no invented citation or template comparison.

## Examples

**SaaS customer.** The supplied clause caps certain damages using fees in a stated
period. Quote the definition, period and exceptions, ask what cap the customer
would accept, and draft a parameterized option tied to that objective. Do not
select twelve months or a new arbitration clause merely because an example did.

**Freelancer.** The user wants payment for completed work after cancellation.
Identify existing payment/termination provisions, propose language consistent with
that goal and list the unresolved fee/timing choices. Do not invent a 25% kill fee,
change ownership rights or pick a noncompete duration without an actual decision.

## Resources

The [proposal and source checks](references/proposal-and-source-checks.md) describe
how to inspect replacement wording and record template provenance. Draft proposals
are decision support, not legal advice or an attorney-client relationship; their
suitability depends on the actual facts and qualified review.
