---
name: nda-generator
description: >
  Draft a confidentiality agreement from identified parties, disclosure direction,
  purpose and explicit term choices, with a separate decision/provenance record.
  Use for mutual, one-way, employee-context or vendor-context NDA drafting.
  Trigger with "nda-generator" or "create an NDA".
allowed-tools: Read, Write, Glob, Grep
version: 1.2.0
author: Intent Solutions <jeremy@intentsolutions.io>
license: MIT
tags:
  - legal
  - nda
  - confidentiality
  - document-generation
compatibility: Designed for Claude Code
---

# NDA Drafting

## Overview

Draft confidentiality terms for the actual disclosure relationship and purpose.
Separate confirmed facts, proposed commercial choices, verified template material
and unresolved legal questions; an NDA request does not authorize unrelated rights transfers.

## Prerequisites

- Actual party identities/roles and selected notice contacts/addresses. Reuse
  approved details; do not default an unknown entity to an individual or infer
  incorporation, physical office or governing law from an address.
- Disclosure direction, purpose, information categories, intended recipients and
  supplied term/survival choices. Record material unknowns instead of inventing them.
- Any existing NDA/master agreement, selected template and requested draft/review
  paths, with current jurisdiction-specific questions identified for verification.

Use authorized inputs only. Do not disclose confidential material to outside
services, contact counterparties, sign, send or file an agreement while drafting it.

## Instructions

1. Use Glob in the selected location if discovery is needed, then Read supplied
   agreements and party/term records. Use Grep to locate relevant definitions,
   confidentiality and precedence provisions, then Read their context. Preserve
   originals and reuse existing decisions rather than repeating discovery.
2. Choose the disclosure structure: mutual, one-way or an expressly identified
   multiparty structure. Employee/vendor are relationship contexts, not automatic
   proof of one-way disclosure or permission to add unrelated obligations.
3. Define the permitted purpose, information scope, relevant exclusions, handling
   duties and actual recipient needs. Distinguish disclosure duration from how
   long particular obligations continue. Do not insert standard year ranges,
   indefinite duties or a default jurisdiction as if the user selected them.
4. Select [relevant candidate sections](references/nda-decisions-and-provenance.md).
   Keep obligations coherent with the chosen direction and information categories.
   Check actual retention/backups and required-record limitations before promising
   destruction of every copy. Do not guarantee court remedies or legal enforceability.
5. Do not automatically add invention assignment, non-compete, non-solicitation,
   audit rights or a new IP license because the relationship is employment or
   vendor-related. If explicitly requested, identify the separate choice, scope,
   interactions and applicable-law questions before drafting those terms.
6. Identify any protected-disclosure, statutory-notice or other jurisdiction-specific
   questions relevant to the actual relationship. Verify current applicable primary
   authority before asserting a rule or copying a notice. If unavailable, keep the
   issue unresolved rather than substituting a generic employee clause.
7. For a selected template, inspect actual text/version and license, preserve needed
   attribution, and record modifications. Do not claim benchmarking that was not
   performed or call changed wording an unchanged standard. Keep original proposed
   wording distinct from sourced template material.
8. Use Write for the requested NDA draft and a separate review/decision record at
   chosen paths. Suggested new names are `nda-{matter-slug}.md` and
   `nda-review-{matter-slug}.md`. Read existing destinations before replacing them.
   Keep explanatory notes outside operative copy unless an annotated draft was
   requested, and leave signature fields unexecuted.

## Output

A confidentiality draft with relevant sections, consistent roles/definitions,
actual supplied contacts/dates and explicit draft status where choices remain.
The separate review record lists source inputs, disclosure structure, provided
and proposed terms, template/version/license, modifications and unresolved facts
or legal questions, with clause-linked explanations when requested.

Do not invent party approval, effective date, signature or legal suitability.
Generating a draft does not execute the agreement, transfer rights, establish an
attorney-client relationship or authorize sending it for signature.

## Error Handling

| Situation                                                     | Recovery                                                                                                 |
| ------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Party identity or entity type is unknown                      | Preserve the uncertainty and ask for the material fact; do not default to individual.                    |
| Governing law or term is undecided                            | List the actual decision needed or explicitly proposed options, not a default state or year range.       |
| Employee/vendor context suggests extra obligations            | Keep confidentiality scope and identify separately requested IP/restriction/data-handling choices.       |
| Existing master terms conflict                                | Show definitions/precedence conflicts and resolve the intended relationship before claiming consistency. |
| Template or current legal source cannot be verified           | Mark the relevant source/rule unresolved; do not invent a version, notice or legal conclusion.           |
| Proposed return/deletion promise is operationally unsupported | Identify retained-copy/backup constraints and the decision required for truthful wording.                |

## Examples

**Mutual discussion:** Two identified companies exchange product and commercial
information for a stated evaluation. Draft matching reciprocal duties from the
provided scope and term choices; do not silently select Delaware or a two-year term.

**Employee-context NDA:** Draft requested confidentiality terms and identify any
applicable protected-disclosure/notice questions. Do not add invention assignment
or a non-compete merely because the reader is an employee.

**Vendor access:** Identify which information the vendor actually receives and
which representatives need access. Keep any processing agreement, audit program
or IP transfer as a distinct requested scope rather than pretending an NDA proves
all those obligations are satisfied.

## Resources

- [NDA sections, decisions and template provenance](references/nda-decisions-and-provenance.md)
- Supplied party records, purpose, commercial choices and existing agreements.
