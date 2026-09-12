---
name: onenote-core-workflow-a
description: >-
  Enumerate approved OneNote notebooks, sections, section groups, and page metadata with complete pagination evidence. Use when building an inventory or selecting a stable content target. Trigger with "inventory OneNote", "list OneNote pages", or "map OneNote hierarchy".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<user-group-or-site> <content-scope> <output-fields>"
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, onenote, inventory]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live OneNote actions require network access, delegated authentication, and explicit approval"
---
# OneNote Hierarchy Inventory

## Overview

Enumerate approved OneNote notebooks, sections, section groups, and page metadata with complete pagination evidence.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Microsoft Graph OneNote documentation and the selected integration's tested contract.
- Named identity, content, workload, security, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures with secrets and real notebook content removed.

## Current Contract

Production calls use the v1.0 user, group, or SharePoint-site OneNote root. Page lists are paged; broad all-pages reads can fail for users with many sections, so enumerate pages per approved section and follow every returned next link. Recheck the dated evidence map before relying on mutable permissions, limits, SDK behavior, supported resources, or cloud availability.

## Authentication

Use delegated Notes.Read unless writes are separately required. Confirm the signed-in user can access the selected user, group, or site content before retrieving metadata.

## Instructions

1. Resolve the exact user, group, or site location and approved notebook scope.
2. Request only needed fields and expand hierarchy relationships when that reduces safe round trips.
3. Enumerate notebooks, section groups, and sections while preserving stable IDs and parent links.
4. List pages section by section and follow every opaque next link until completion.
5. Record page counts, duplicate IDs, inaccessible containers, and the extraction watermark.
6. Reconcile the manifest against expected roots and label incomplete or denied areas explicitly.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, delegated credentials, tenant or notebook content, consent, file transfer, deployment, writes, spend, sharing changes, or deletion.

## Approval Boundaries

Require the content owner before traversing a new root or exporting metadata. The workflow is read-only and does not fetch page bodies unless separately approved.

## Error Handling

- Never infer completeness from the first page.
- Do not use titles as identities or reconstruct opaque next links.
- Stop if the resolved location differs from the approved user, group, or site.

## Output

Return the location contract, hierarchy manifest, page ledger, inaccessible scopes, reconciliation totals, watermark, and evidence gaps. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Inventory a group notebook without querying unrelated user notebooks.
- Resume a section page list from its exact saved next link.

## Validation

Exercise and record these paths with expected and observed results:

- empty notebook
- nested section groups
- multiple pages
- duplicate ID
- denied section
- resume

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal OneNote guarantee.
