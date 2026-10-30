---
name: plain-english
description: >
  Explain supplied contract clauses in clear language while preserving conditions,
  exceptions and source locators. Use when a non-lawyer wants to understand an
  agreement. Trigger with "explain this contract", "plain-english" or "translate
  this contract to plain English".
allowed-tools: Read, Glob, Grep, Write
version: 1.2.0
author: Intent Solutions <jeremy@intentsolutions.io>
license: MIT
tags:
  - legal
  - contracts
  - plain-language
  - readability
  - translation
  - accessibility
compatibility: Designed for Claude Code
---

# Plain-English Contract Explanation

## Overview

Explain readable supplied clauses for the intended audience and preserve the
qualifications that affect meaning. Tie each explanation to the original text,
mark ambiguity and distinguish an explanatory draft from a legal conclusion.

## Prerequisites

- A selected contract file or pasted text, with relevant schedules when available.
- The audience and any party perspective the user has supplied. If the party is
  unknown, use neutral party labels instead of assuming what "you" must do.
- Requested coverage and output path. Record missing pages, unreadable images,
  table extraction, comments/redline mode and unavailable incorporated terms.

Use only supplied or authorized inputs. Do not upload contracts to external
conversion services, alter originals or infer that confidentiality is guaranteed
by the model or file format.

## Instructions

1. Use Glob within the selected location if discovery is needed, then Read the
   supplied material. State the pages/sections actually reviewed. If an attachment
   or image cannot be read, request usable text or leave that part unreviewed.
2. Map clauses and their definitions/cross-references. Use Grep to locate terms in
   readable supplied text and Read surrounding provisions. Do not automatically
   skip signatures, notices, order forms or headings when they contain party names,
   effective dates, exceptions or other operative details.
3. Explain clauses using short sentences and the audience's vocabulary. Preserve
   who must or may act, the action, trigger, deadline, amount/unit, conditions,
   exceptions, limits, negations and referenced definitions. Keep a specialized
   term alongside its explanation when a casual synonym would change its scope.
4. Follow [the explanation checks](references/clause-explanation-checks.md). Do
   not translate indemnity, damages exclusions or ownership language into a
   universal outcome. When wording supports several readings, show the ambiguity
   and the specific missing context instead of choosing one as established law.
5. Flag observed obligations, dependencies, exceptions, conflicting text or unclear
   meaning with a source locator. Dense wording alone is not proof of deception,
   deliberate concealment or a drafter's intent. Explain the concrete concern.
6. Build a quick-reference summary of the mapped parties' actions, restrictions,
   dates, payments, exit/renewal process and unresolved questions. Trace important
   summary statements back to clauses. Do not infer a right or remedy merely
   because one section does not mention it.
7. Review the explanation against the source. If readability metrics are requested
   and actually measured, report the method/tool, text sample and limits. Otherwise
   mark them unmeasured; do not invent a Flesch-Kincaid grade or promise a measured
   grade-eight result. A formula alone does not prove reader comprehension.
8. Return the requested report. When saving is requested, use Write at the chosen
   path; suggest `plain-english-{matter-slug}.md` for new work and inspect an
   existing destination before replacing it. Preserve the original contract.

## Output

An explanatory draft containing document identity, audience/party mapping,
reviewed coverage and gaps, a quick-reference summary and clause-by-clause notes.
For each note include a section/page locator, a minimal exact source excerpt,
plain explanation, dependencies and unresolved meaning. Label paraphrases and
examples clearly. Include measured readability results only when they exist.

The report does not amend the contract, establish enforceability or create an
attorney-client relationship. Identify decisions needing qualified legal review
without presenting the explanation as a replacement for that review.

## Error Handling

| Situation                                         | Recovery                                                                            |
| ------------------------------------------------- | ----------------------------------------------------------------------------------- |
| Party identity is missing                         | Use neutral labels; ask before assigning obligations to the user.                   |
| Clause relies on a missing schedule or definition | Explain the visible wording and mark the dependency unresolved.                     |
| Specialized term has no faithful short synonym    | Preserve the term and give a limited contextual explanation.                        |
| Multiple plausible readings remain                | Show the competing readings and question for qualified review.                      |
| Extraction or context is incomplete               | Label coverage and request the needed text rather than claiming a full translation. |
| No readability scorer is available                | Report unmeasured and review clarity directly; do not fabricate statistics.         |

## Examples

**Damages exclusion:** A clause lists several excluded damage types. Explain what
it purports to exclude and preserve its exceptions and relationship to any cap.
Do not turn that wording into "the company owes you nothing" or assume a refund
is the only remaining remedy.

**Definition dependency:** A definition of Services includes customer-created
integrations. Explain the expanded label, then inspect the supplied provisions
that use it. Ownership and licensing effects remain conditional on those clauses;
the definition alone does not establish who owns the integrations.

**Obligation summary:** A supplied clause requires written notice thirty days
before renewal, subject to an exception in a schedule. Preserve the notice form,
period, renewal reference and missing exception; do not replace it with "cancel
anytime" or invent a calendar deadline without the relevant dates.

## Resources

- [Clause explanation and readability checks](references/clause-explanation-checks.md)
- The supplied clauses, definitions, schedules and actual user questions.
