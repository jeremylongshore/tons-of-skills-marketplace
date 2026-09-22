---
name: cohere-core-workflow-a
description: >-
  Build a Cohere v2 RAG pipeline with asymmetric embeddings, retrieval, Rerank v4, grounded Chat, and citation validation. Use when implementing grounded question answering. Trigger with "Cohere RAG", "Cohere retrieval", or "Cohere citations".
argument-hint: "[repository-path] [retrieval-backend]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- cohere
- rag
model: inherit
effort: high
compatibility: Designed for Claude Code; live verification requires network access and an approved Cohere API key
---
# Cohere Retrieval-Augmented Generation

## Overview

Create a measurable retrieval pipeline that separates indexing, query embedding, candidate retrieval, reranking, generation, and citation checks.

## Prerequisites

- The target repository, runtime, environment, and accountable owner
- An approved Cohere team and key for any live verification
- Current quality, security, privacy, capacity, and change-control requirements

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect code, configuration, and evidence. Use `WebFetch` only for current Cohere primary documentation. Use `Write` or `Edit` only when the user requested implementation and the exact target files are known; never write credentials or customer content.

## Current Contract

- Embed indexed passages with `input_type=search_document` and user queries with `input_type=search_query`.
- Keep the embedding model, output type, dimensions, normalization, and document schema in index metadata.
- Use Rerank v4 on a bounded candidate set before generation and retain document IDs.
- Pass selected documents to Chat v2 and validate returned citations against those IDs.

## Authentication

Use an environment-specific key injected from an approved secret manager. Never print, persist, commit, or place `CO_API_KEY` in an example. Confirm access with the least costly bounded operation appropriate to the task, and treat key creation, rotation, revocation, role changes, and production-capacity requests as owner-approved actions.

## Instructions

1. Define document IDs, chunking rules, metadata filters, and an evaluation query set.
2. Resolve and pin a live Embed model, then index documents with the document input type.
3. Embed each query with the query input type and retrieve a bounded candidate set.
4. Rerank candidates with a live v4 model and record scores and selected IDs.
5. Generate from only the selected evidence with citation options appropriate to the use case.
6. Evaluate retrieval recall, rerank quality, answer faithfulness, citation validity, latency, and cost before release.

## Approval Boundaries

Do not expose or rotate keys, change Cohere Team roles, accept commercial terms, enable sensitive production data, increase spend or capacity, switch production models, send a support bundle, or execute model-proposed side effects without the accountable owner's approval. Keep diagnosis read-only unless implementation was requested.

## Output

Return the resolved API and model contract, files or settings inspected, evidence collected, validation result, remaining risk, owner, and rollback or next action. Redact keys, authorization headers, prompts, retrieved documents, embeddings, customer identifiers, and unrestricted environment output.

## Error Handling

| Condition | Response |
|---|---|
| Dimension mismatch | Stop and rebuild or select the index matching its recorded model contract. |
| No candidates | Return a grounded no-answer result instead of unconstrained generation. |
| Invalid citation | Reject or flag the answer and retain the evidence bundle. |
| Context overflow | Reduce or rechunk evidence; v2 does not provide legacy prompt truncation. |

## Examples

Use this compact handoff shape to keep the selected scope, validation evidence, and operational result reviewable.

Input:

```text
query=approved-fixture; retrieve=40; rerank=8; require-citations=true
```

Expected handoff:

```text
answer=grounded; citations=valid; selected-doc-ids=recorded; eval=pass
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Embed API](https://docs.cohere.com/reference/embed)
- [Rerank models](https://docs.cohere.com/docs/rerank)
