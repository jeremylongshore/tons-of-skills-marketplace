---
name: bug-clustering
description: |
    Normalize supplied X post objects, redact common sensitive strings, score
    heuristic signals, deduplicate similar text, and persist deterministic bug
    clusters with the repository's Bun libraries. Use when developing or testing
    the local clustering stage. Trigger with "cluster these supplied bug posts".
allowed-tools: "Read, Bash(bun:*)"
version: 0.2.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: "Designed for Claude Code with Bun and a local x-bug-triage-plugin checkout; operates on supplied post data and a caller-selected SQLite database."
tags: [triage, clustering, redaction, heuristics, sqlite]
argument-hint: "<fixture-or-input-file> [--db PATH]"
disable-model-invocation: true
model: inherit
effort: high
---

# Bug Clustering

Exercise the repository's real normalization and clustering libraries on data the operator supplies.
This skill does not fetch X posts, infer truth, or provide a packaged end-to-end runner.

## Overview

`parseCandidate()` performs regex-based extraction, classification, redaction, and scoring.
`deduplicateCandidates()` groups similar text with trigram and token-Jaccard similarity.
`clusterCandidates()` writes cluster and cluster-post rows to SQLite. Read
[the runtime contract](references/runtime-contract.md) before treating any score as evidence.

## Prerequisites

- Work from this repository with Bun installed and dependencies available.
- Supply X-shaped post objects; do not pass secrets or unredacted private exports.
- Select a disposable or explicitly approved SQLite database. Initialize it with `bun run db:migrate`.
- Back up any non-disposable database before a clustering run.

## Authentication

No external authentication is used. This skill reads supplied local data and may write only to the
operator-selected SQLite path through the local Bun libraries.

## Instructions

1. Inspect the input count and schema before execution. Refuse unknown binary or private-source files.
2. Parse each post with `parseCandidate(post, runId, approvedAccounts, sourceType?)` from
   `lib/parser.ts`.
3. Verify `raw_text_redacted` and `pii_flags`. The redactor covers configured patterns, not every
   possible sensitive value; stop if the sample still exposes private content.
4. Pass `{ post_id, text, public_metrics }` objects to `deduplicateCandidates()`. Its default threshold
   is `0.70`; record any override.
5. Insert the triage run and only the approved candidates into the selected database.
6. Call `clusterCandidates(db, candidates, runId, threshold?)`. It clusters only four eligible
   classification families and skips non-clustering classifications.
7. Report new, updated, skipped, and suppressed counts. Do not invent audit rows: this function writes
   clusters and links, but does not itself emit the audit events claimed by older documentation.
8. Run the relevant Bun tests after changing library behavior.

## Output

Return:

- input, parsed, forwarded, skipped, and suppressed counts;
- duplicate groups and the threshold used;
- new and updated cluster identifiers;
- the exact database path and whether it was disposable;
- warnings about residual sensitive content, weak classifications, or missing surface/feature data.

## Examples

```text
Input: tests/fixtures/x-api/mentions-response.json
Database: /tmp/x-bug-triage-demo.db
Threshold: 0.70
Result: 3 parsed; 3 forwarded; 2 new clusters; 1 skipped; 0 suppressed
Warning: scores are deterministic heuristics, not verified bug truth.
```

```text
No execution performed: the requested database was data/triage.db and no backup or mutation approval
was provided.
```

## Error Handling

| Situation                           | Response                                                               |
| ----------------------------------- | ---------------------------------------------------------------------- |
| Input is not X-shaped JSON          | Stop and report the missing fields.                                    |
| Redaction leaves sensitive text     | Do not persist that candidate.                                         |
| Database is not explicitly selected | Use a disposable path or request a path; never assume production data. |
| Candidate references a missing run  | Insert the run first or stop on the foreign-key error.                 |
| One library call throws             | Roll back the caller-managed batch and report the exact stage.         |

## Guardrails

- Never claim the classifier is an ML model; it is a fixed regex/keyword heuristic.
- Never treat reporter reliability as identity verification or factual truth.
- Never store original private text merely because configured patterns did not match it.
- Never run `bun run db:reset` without explicit approval; it deletes the configured database.

## Resources

- [Runtime contract](references/runtime-contract.md)
- [Repository source](https://github.com/jeremylongshore/x-bug-triage-plugin/tree/main/lib)
