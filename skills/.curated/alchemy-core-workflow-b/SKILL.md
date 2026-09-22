---
name: alchemy-core-workflow-b
description: >-
  Build an NFT discovery workflow with Alchemy NFT API v3 and isolate typed on-chain reads through viem. Use when creating collection explorers or ownership checks. Trigger with "Alchemy NFT API", "NFT collection explorer", or "read an NFT contract".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<owner-or-contract> <network> <query-purpose>"
version: 2.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, alchemy, nft, viem]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Alchemy access requires network access, an appropriate credential, account capacity, and explicit approval"
---
# Alchemy NFT Discovery and Contract Read Workflow

## Overview

Build an NFT discovery workflow with Alchemy NFT API v3 and isolate typed on-chain reads through viem. This workflow produces a reviewable artifact and negative-path evidence before any live side effect.

## Prerequisites

- Current first-party Alchemy documentation for the selected product, chain, feature, client, authentication method, limit, and lifecycle.
- Named product, application, security, data/privacy, budget, release, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures, a credential canary, explicit success criteria, and a tested rollback boundary.

## Current Contract

NFT API responses, metadata availability, spam classification, pagination, and supported networks are endpoint-specific. NFT indexing is not chain finality, and cached media is not proof of ownership. Contract state reads use the declared viem chain and ABI; ownership-sensitive decisions require an explicit block/finality policy.

## Authentication

Use a scoped application API key in the server boundary. Validate owner and contract addresses before lookup. Treat queried owner addresses, collections, and behavioral analytics under the product's privacy and retention policy.

## Instructions

1. Choose owner discovery, collection enumeration, metadata lookup, or contract-state verification and confirm the endpoint's current chain support.
2. Define the response schema, spam/filter policy, metadata and media fallbacks, page-key handling, maximum pages, and freshness label.
3. Fetch through a narrow NFT API v3 adapter, validate every page, and retain provenance for cached versus original media without executing remote media content.
4. For on-chain verification, create a viem public client on the same declared chain, use a reviewed minimal ABI, and record the block context.
5. Reconcile indexer output with contract reads only where the product requires it; represent disagreement and reorganization risk explicitly.
6. Test empty, paginated, malformed metadata, spam-filtered, unsupported-chain, and indexer-versus-chain disagreement before release.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, wallet addresses, customer data, plan changes, spend, key creation or rotation, webhook changes, deployment, replay, transaction construction, signing, broadcast, or deletion.

## Approval Boundaries

Product/privacy owners approve address use and analytics. Security approves remote-media handling and ABI/source provenance. Transactions, approvals, mints, or marketplace writes are outside this read-only workflow.

## Error Handling

- Do not infer ownership from an image URL or stale cached metadata.
- Do not silently exclude assets without recording the configured spam/filter policy.
- If the NFT index and contract read disagree, show an indeterminate state and reconcile at an approved block/finality point.

## Output

Return the query purpose, chain/endpoint proof, schema and pagination contract, filter policy, media safety rules, optional viem read evidence, disagreement behavior, tests, and rollback. Mark assumptions, observations, source dates, environment-specific behavior, owners, and unresolved gaps explicitly.

## Examples

- Page through a public test collection and retain the next-page token until exhaustion while labeling cached media provenance.
- Verify an ownership-sensitive result with a typed `ownerOf` read at a recorded block and surface disagreement instead of choosing one source silently.

## Validation

Exercise and record expected and observed results for:

- empty collection
- multi-page owner
- missing metadata
- unsafe media URL
- unsupported network
- indexer/contract disagreement

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Alchemy sources before execution.
- Treat observed account, application, network, indexer, chain, or provider behavior as environment-specific evidence, never a universal guarantee.
