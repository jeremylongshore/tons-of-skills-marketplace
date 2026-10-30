---
name: brand-strategy
description: >
  Build or review a seven-part brand strategy covering identity, audience,
  positioning, messaging, visual principles, channels and measurement. Use when
  creating a brand brief, defining positioning or revising brand messaging.
  Trigger with "create brand strategy", "build brand brief" or "brand messaging".
version: 1.8.0
author: Rowan Brooks <rowanbrooks100@github.com>
license: MIT
allowed-tools: Read, Write, Edit
tags:
  - business
  - brand-strategy
compatibility: Designed for Claude Code
---

# Brand Strategy Framework

## Overview

Build a usable brand strategy from the creator's context and evidence. Support a
full strategy, one selected phase, or a review of an existing document.

## Prerequisites

- The brand or product, intended audience and requested decision or deliverable.
- Existing briefs, customer observations, positioning and constraints when available.
- A selected project directory and output path for saved work. No branding API,
  CLI installation or authentication is required for this document workflow.

Read the files the user selects. Reuse known answers and approvals; ask only for
missing decisions that affect the requested work. If file paths are unavailable,
work from supplied text and record that limitation. Do not search unrelated
private documents for customer data.

## Instructions

1. Confirm the mode: full strategy, selected phase, or review. A full strategy
   normally follows the seven phases in order; a focused task can use established
   upstream decisions without repeating discovery.
2. Read [the seven-phase framework](references/seven-phase-framework.md) for the
   relevant questions and outputs. Preserve useful existing decisions and identify
   material contradictions before drafting dependent messaging or channel plans.
3. Separate supplied facts, observed research, creator decisions and hypotheses.
   Attach source paths or supplied URLs to claims about audiences, competitors or
   performance. If current research is unavailable, label proposed positioning and
   audience archetypes as hypotheses; do not invent customer quotes, competitor
   capabilities, market demand or cultural trends.
4. Develop concrete choices with rationale and tradeoffs. Tie proof points to real
   evidence. Treat visual directions as principles, not completed design assets;
   distinguish a proposed channel experiment from a proven acquisition channel.
5. Review each requested phase against its purpose. Ask about material unresolved
   choices; preserve any approval already given. Record draft/proposed/approved
   accurately, and never treat a generated suggestion as stakeholder approval.
6. Write the requested document to the selected output path. For a new strategy,
   suggest `brand-strategy-{brand-slug}.md`; use an explicitly selected existing
   path for revisions. Check an existing file before replacing it. Use Edit for a
   scoped revision, preserving unrelated sections and the creator's chosen voice.
7. Report the saved path, sections completed, unresolved decisions and next useful
   action. A partial phase deliverable must identify deferred phases rather than
   implying that the whole strategy is complete.

## Output

A full strategy document contains an executive summary plus these seven sections:

| Phase                 | Useful artifact                                                          |
| --------------------- | ------------------------------------------------------------------------ |
| Brand Truth           | Reason for being, core belief and values with concrete implications      |
| Audience Architecture | Motivations, needs, exclusions and evidence status for audience segments |
| Cultural Context      | Positioning, alternatives and a qualified competitive landscape          |
| Messaging Framework   | Core claim, supported proof points, objections and language guidance     |
| Visual Language       | Visual principles and reference directions with rationale                |
| Channel Strategy      | Priorities, role, themes and feasible cadence for each selected channel  |
| Measurement Framework | Outcome, metric definition, data source, owner and review cadence        |

Include scope, source inputs, decision status and open questions. A review can
instead report findings by section, supporting evidence and proposed revisions.
For measurement, record the actual baseline and observation window when known;
otherwise write unknown. Label targets as proposed or owner-approved, and explain
what evidence would test them. Do not promise that a leading indicator predicts
revenue or that a strategy will deliver a specific growth rate.

## Error Handling

| Situation                              | Recovery                                                                                      |
| -------------------------------------- | --------------------------------------------------------------------------------------------- |
| Brand or audience is unclear           | Ask for the decision needed to scope the work; avoid a generic seven-section filler document. |
| Sources contradict a desired claim     | Show the conflict and revise the claim or flag missing evidence.                              |
| No customer or competitor research     | Draft testable hypotheses and a bounded research plan; label the limits.                      |
| Baseline or attribution is unavailable | Record unknown and specify how it could be measured.                                          |
| Output path belongs to another brand   | Select a separate path or obtain an explicit revision instruction.                            |
| Earlier phases are unfinished          | Complete the requested phase with assumptions listed and flag dependent decisions.            |

## Examples

**Full strategy:** "Build a strategy for our coffee subscription using this brief."
Read the brief, reuse supplied audience and pricing decisions, then develop the
seven phases. Save a draft with unsupported taste or demand assumptions labeled.

**Focused phase:** "Revise messaging in `brand-strategy-coffee.md` for office buyers."
Read that document and relevant audience evidence. Edit messaging and identify
any positioning or channel implications without silently rewriting the strategy.

**Review:** "Our deck says awareness doubled, but we have no baseline."
Flag the unsupported result, keep the metric unknown, and propose a measurement
window and data source instead of inventing a prior value.

## Resources

- [Seven-phase questions and deliverables](references/seven-phase-framework.md)
- The user's selected brief, approved decisions and supplied research artifacts.
