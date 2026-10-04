---
name: span-fingerprint
description: |
  Performance-issue span evidence and detector thresholds (OP08).
  Not transaction-name cardinality. Not a marketplace skill.
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [sentry, nested, saas, checklist]
---

# span-fingerprint

**Owner:** `sentry-issue-triage` → `perf-span-auditor`
**Spawn only when** the issue type is a performance issue (N+1 DB, N+1 API, or another span-evidence issue). An error issue does not load this file.

Transaction grouping "isn't currently customizable or extendable." Error fingerprint rules and stack-trace rules do nothing here. `transaction-cardinality` (raw URL transaction names, owned by quota) is a different job.

## N+1 DB (do not improvise)

Cite these thresholds from the performance-issue docs; do not round them:

- Repeating database spans, usually at least 5, sequential.
- Total time of the repeating spans greater than 50ms.
- Full query text, not an ellipsized description.
- A preceding source span.
- Fingerprint inputs: parent span, source span, repeating span.
- Unparameterized SQL changes the fingerprint. Sentry's parameterizer misses cases. Recommend parameterizing in the SDK. Do not promise a server rule will merge `WHERE id = 1` with `WHERE id = 2`.

## N+1 API

- At least 10 simultaneous GETs.
- Greater than 300ms.
- Within 5ms of each other.
- Not GraphQL, not `_next/data`, not static assets.
- URLs are parameterized only for integers, UUIDs, SHA1, and MD5.
- Other ids: rewrite the span description in `beforeSendTransaction` (or span hooks). `beforeSend` on errors does not see these spans.

## Output

Which detector, which threshold the payload meets or misses, and the SDK change (parameterize SQL or rewrite the span description). State that the change is prospective. `writes: none`.

## Fail

Offering a project fingerprint rule as the fix. Treating this as cardinality. Inventing a threshold. Spawning this agent for an ordinary error.
