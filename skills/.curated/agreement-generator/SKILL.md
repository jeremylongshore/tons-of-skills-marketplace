---
name: agreement-generator
description: >
  Draft a business agreement from the selected relationship type, confirmed
  party and commercial facts, and explicit proposed choices with provenance.
  Use when preparing a service, partnership, licensing or other business agreement.
  Trigger with "agreement-generator" or "create a freelancer agreement".
allowed-tools: Read, Write, Glob, Grep
version: 1.2.0
author: Intent Solutions <jeremy@intentsolutions.io>
license: MIT
tags:
  - legal
  - agreements
  - contracts
  - business
  - document-generation
compatibility: Designed for Claude Code
---

# Business Agreement Drafting

## Overview

Turn the actual relationship, objectives and agreed commercial choices into a
coherent draft. Separate confirmed facts, proposed terms, verified source material
and unresolved legal questions instead of filling gaps with standard-looking defaults.

## Prerequisites

- Agreement purpose/type, actual parties/roles and requested scope, including any
  existing master terms, SOWs, schedules or selected template.
- Approved entity/contact details and commercial decisions: obligations, dates,
  payment/consideration where relevant, rights, governance and exit choices.
- Known jurisdiction and legal questions needing current-source verification.
  Missing facts remain unresolved or explicitly proposed; do not infer them from names.

Use only authorized inputs. Do not contact counterparties, sign or file documents,
form an entity, transfer funds or deploy a signing workflow as part of drafting.

## Instructions

1. Use Glob within the selected location for discovery when needed, then Read the
   supplied records. Use Grep for definitions, incorporated terms and obligations,
   then Read their context. Preserve originals and reuse approved decisions.
2. Choose the relevant [relationship type](references/agreement-decisions.md).
   A hybrid or multiparty deal may need a tailored scope rather than pretending
   the closest template fits unchanged. Distinguish confidentiality-only drafting
   from a broader service, ownership or governance agreement.
3. Gather material missing choices with their actual units, parties and triggers:
   deliverables/acceptance, money/fees, IP/license scope, milestones, term/renewal,
   termination, responsibilities and any governance. Do not invent rates, timing,
   liability caps, commissions, ownership transfers or governing jurisdiction.
4. If the user requests proposed terms, label options and assumptions and explain
   tradeoffs against the stated objectives. Do not present unsupported market-rate
   ranges, customary durations or a template's defaults as settled user decisions.
5. Draft only relevant sections. Do not automatically add non-competes, non-solicits,
   broad indemnities, arbitration, an SLA, data-processing commitments or an entity
   formation step because a relationship type often uses them. Identify any
   separately requested material choice and applicable-context questions.
6. For jurisdiction-specific assertions, inspect current applicable primary sources
   and actual facts with available authorized tools. Do not insert an ABC test,
   trade-secret notice or international arbitration clause solely from a location
   label. If verification is unavailable, record the question instead of assuring
   proper legal structure or enforceability.
7. Inspect any selected template's actual text/version/license and preserve required
   attribution, recording modifications. Original proposed wording is not a
   verified template clause. Check roles, definitions, obligations, amounts/units,
   dates, cross-references, precedence and schedules for consistency.
8. Use Write for the requested draft and separate review record at selected paths.
   Suggested new names are `agreement-{matter-slug}.md` and
   `agreement-review-{matter-slug}.md`. Read existing destinations first. Keep
   explanatory annotations separate unless an annotated draft is requested, and
   leave execution fields unsigned with actual provided date decisions.

## Output

A draft with relevant type-specific sections, coherent obligations, supplied
identity/contact facts and explicit status. The review record contains the source
inputs, actual/proposed decisions, template provenance/modifications, assumptions,
missing schedules and questions for qualified review. Explain what remains
unresolved rather than inventing legal suitability or party approval.

Generating a draft does not execute the agreement, form a company, establish worker
status, transfer rights or create an attorney-client relationship. Report actual
saved paths and preserve the user's original documents and unrelated work.

## Error Handling

| Situation                                        | Recovery                                                                                                  |
| ------------------------------------------------ | --------------------------------------------------------------------------------------------------------- |
| Relationship is hybrid or unclear                | Identify the actual obligations and needed decision, rather than choosing a convenient template silently. |
| Payment, scope or dates are missing              | Ask for material choices or label requested proposals; do not fill them with unsupported market norms.    |
| Party/entity/contact is unknown                  | Preserve the missing fact; do not default to an individual or infer incorporation from an address.        |
| Master terms and SOW conflict                    | Show the provisions and intended precedence before presenting a coherent final draft.                     |
| International or regulated context is unresolved | Identify actual applicable-source questions; do not add generic frameworks or arbitration as a cure.      |
| Source template or law cannot be verified        | Keep that assertion unresolved, without fictional versions, benchmarking or compliance claims.            |

## Examples

**Freelancer project:** Use actual deliverables, acceptance, fee and IP choices.
Do not add a six-month non-compete, net-thirty payment or work-for-hire assignment
simply because a web developer is involved. Label any requested proposed terms.

**MSA/SOW:** Draft the supplied service framework and incorporation/change process.
An SLA or uptime promise needs actual requested commitments and operational facts;
it is not an automatic MSA section or proof a service can deliver them.

**Referral commission:** A user supplies ten percent. Confirm the calculation base,
qualifying event, attribution, payment trigger and exclusions, or show them as
explicit proposed choices. Do not silently turn that into first-year revenue,
ninety-day qualification and a twelve-month attribution window.

## Resources

- [Ten relationship types, decisions and provenance](references/agreement-decisions.md)
- Supplied party records, existing terms, schedules and actual commercial decisions.
