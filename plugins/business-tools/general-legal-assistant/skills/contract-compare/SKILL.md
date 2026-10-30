---
name: contract-compare
description: >
  Compare two contract versions with clause-level evidence, coverage limits and
  qualified analysis of possible effects for the identified parties. Use when
  reviewing a revised contract or redline. Trigger with "contract-compare" or
  "compare these two contracts".
allowed-tools: Read, Glob, Grep, Write
version: 1.2.0
author: Intent Solutions <jeremy@intentsolutions.io>
license: MIT
tags:
  - legal
  - contracts
  - comparison
  - redline
  - negotiation
  - diff
compatibility: Designed for Claude Code
---

# Contract Compare

## Overview

Compare the supplied baseline and revision, align their clauses and explain the
observed changes. Separate textual evidence from possible commercial effects and
questions requiring legal review. Report the material actually inspected rather
than promising every change in an unreadable or incomplete contract.

## Prerequisites

- Two versions supplied as selected files, labeled text or a combination.
- An explicit baseline/revision mapping. Reuse labels already supplied; otherwise
  ask before describing additions/removals directionally. Do not infer chronology
  from upload order or a filename alone.
- The party the user represents and the contract purpose when favorability or
  negotiation analysis is requested. A neutral comparison can proceed without it.
- Known schedules, exhibits, amendments and incorporated documents relevant to the
  requested comparison. Record unavailable material and any supplied jurisdiction.

Use only the selected documents and authorized tools. Do not upload contracts to
an external converter, research service or other provider as an implicit step.
Do not edit either original contract or send a negotiation message.

## Instructions

1. Use Glob only within the selected input location when file discovery is needed.
   Read both versions and record filenames/version labels, page or section coverage,
   visible redline mode and extraction limits. If Read cannot expose an image,
   table, attachment or full document, request usable text or mark that area
   unreviewed; do not claim it was compared.
2. Build a structural map of sections, definitions, schedules and cross-references.
   Match relocated/renumbered clauses by their text and responsibility rather than
   section number alone. Preserve the originals while normalizing presentation for
   comparison. Distinguish whitespace/pagination changes from wording changes.
3. Compare aligned clauses and classify observed additions, removals, modifications
   and moves. Use Grep for defined terms and cross-reference targets in readable
   supplied text, then Read the surrounding clauses. A search miss in incomplete
   extraction does not prove a provision was removed.
4. Give each finding a stable ID and baseline/revision locators. Include the minimal
   exact excerpts needed to demonstrate the change, preserving negations, defined
   terms, dates, currencies and units. Describe paraphrases as paraphrases; never
   present generated wording as a quotation from the contract.
5. Inspect dependencies for changes in liability caps, indemnities, intellectual
   property, termination, notice, assignment, governing law or dispute terms when
   present. Follow changed definitions and exceptions into the affected clauses.
   If an exhibit or incorporated policy is missing, identify that dependency.
6. Explain possible effects for the mapped parties with the assumptions and source
   clauses that support them. Use unclear or context-dependent when appropriate.
   Do not infer deceptive intent from a change, treat an omitted term as proof of
   a legal entitlement, or convert a fee-window ratio into actual liability loss.
7. Prioritize findings using the user's objectives and concrete rights/obligations
   affected. Keep cosmetic edits separate. Counts describe detected changes within
   the stated coverage; they are not a winning score or proof a version is safe.
   If a numeric rubric is requested, label its weights as a user-selected triage
   heuristic and preserve the material findings that a total can hide.
8. Produce [the comparison report](references/report-and-review.md). State evidence
   gaps and questions for counsel rather than assuming a law applies to every
   contract. When a saved report is requested, use Write at the selected path;
   suggest `contract-comparison-{matter-slug}-{date}.md` for new work and inspect
   any existing destination before replacing it. Report the actual saved path.

## Output

A comparison draft with document identities and baseline direction, inspected
coverage, a clause map, observed change findings and qualified possible effects.
Use stable finding IDs, both version locators, exact evidence excerpts, dependencies,
review priority and unresolved questions. Include detected-change counts only
when actually counted and label their scope.

Distinguish no observed change in reviewed material from a complete-document
identity claim. Legal effect and enforceability require the applicable facts,
contract context and current jurisdiction-specific authority; this document
comparison does not establish them or an attorney-client relationship.

## Error Handling

| Situation                                   | Recovery                                                                                   |
| ------------------------------------------- | ------------------------------------------------------------------------------------------ |
| Baseline direction is missing               | Ask which version is baseline; a neutral alignment can be prepared meanwhile.              |
| Documents appear unrelated                  | Confirm the intended pair before labeling differences as negotiation changes.              |
| Pages, exhibits or OCR are missing          | List the gaps, compare readable material and avoid an exhaustive verdict.                  |
| Tracked changes or comments are ambiguous   | Record the visible mode and request the intended clean/redline version.                    |
| Clauses are renumbered or moved             | Align by content and show the mapping rather than reporting false deletion/addition pairs. |
| Party or business objective is unclear      | Provide factual changes first and leave directional favorability unresolved.               |
| Legal effect depends on unavailable context | State the precise question for qualified review instead of asserting default law.          |

## Examples

**Liability language:** A baseline refers to twelve months of fees and a revision
refers to fees in the preceding three months. Quote both clauses and check their
fee definitions, exclusions, timing and other caps. Report the changed reference
window; do not assert a 75% reduction in actual liability or financial exposure.

**Definition change:** "Deliverables" gains a reference to pre-existing materials.
Identify the exact added phrase and follow readable assignment/license clauses
using that definition. Describe a possible scope change with its dependencies,
not the counterparty's motive or a definitive ownership conclusion.

**Incomplete comparison:** The revised PDF omits Schedule B. Mark that schedule
unreviewed and compare available sections. Do not call Schedule B removed unless
the complete intended revision or other supplied evidence establishes removal.

## Resources

- [Report structure, evidence checks and review limits](references/report-and-review.md)
- The supplied contract versions, schedules, amendments and explicit party objectives.
