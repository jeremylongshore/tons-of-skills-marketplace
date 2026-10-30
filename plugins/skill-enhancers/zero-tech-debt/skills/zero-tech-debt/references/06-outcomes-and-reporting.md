# Preferred Outcomes + Reporting Back

This file describes what a successful zero-tech-debt refactor looks like, and how to summarize the result so reviewers and future readers can evaluate the _shape change_ rather than re-reading the diff.

## What success looks like

Possible signs of a useful simplification include:

- **Fewer files** — collapsed wrappers, deleted dead modules
- **Fewer modes** — `if (legacyMode)` branches removed, one path through the code
- **Fewer flags** — feature flags that became permanent are inlined
- **Fewer state transitions** — the state machine has fewer arrows on the diagram
- **Fewer routing paths** — aliases removed, one URL per resource
- **Fewer adapters** — pass-through layers flattened
- **Fewer abstractions** — single-implementation interfaces inlined
- **Fewer concepts developers must memorize** — fewer "you also need to know about X" caveats

Evaluate those changes against the requested end state and relevant evidence:

- **Clarity** — a new hire reads the code and understands the intent
- **Reliability** — fewer paths means fewer untested paths means fewer bugs
- **Maintainability** — the next change is cheaper because there's less to navigate around
- **Onboarding speed** — measured in "minutes to first useful PR," not "weeks to feel comfortable"
- **Operational confidence** — on-call can act on alerts without paging the original author
- **Implementation velocity** — features land faster because there's less scaffolding to route around

A correct redesign can add files, explicit states or a needed interface. Judge responsibilities and required behavior rather than a deletion quota. Claim reliability, onboarding or velocity improvements only to the extent measured; otherwise describe the structural change and its intended rationale.

## How to summarize the result

The diff lists every line. The summary exists to make the architectural delta legible to reviewers and future readers. A good summary fits in five sections:

### 1. Deleted

Use verified counts when useful, plus enough names or paths for the reviewer to locate the changed boundary. Omit counts that were not actually measured.

```
Deleted:
- 12 files
- 47 functions
- 3 feature flags (NEW_USER_FLOW, ENABLE_V2_PRICING, USE_OLD_AUTH)
- 5 route aliases (/api/v1/users → /api/users, etc.)
- 8 config keys (consolidated into `service.retry`)
```

### 2. Unified

Before/after shape, not before/after diff. One line per consolidated flow.

```
Unified:
- 3 user-lookup paths → 1 (UserService.findById is the single entry point)
- 2 retry implementations → 1 (utils/retry.ts; the http/retry.ts and queue/retry.ts variants are gone)
- 4 permission checks scattered across UI components → 1 (PolicyService.canUserAccess)
```

### 3. Renamed

Old name → new name, with the domain reason. The reason matters more than the names.

```
Renamed:
- MongoOrderStore → OrderRepository
  (we replaced Mongo with Postgres in 2024; the class name leaked the old infra)
- processOrder → fulfillOrder
  (function handles fulfillment, payment is now in PaymentService)
```

### 4. Intentionally Left Alone

Things the audit flagged but you chose not to touch, with the reason. This prevents the next refactor from re-noticing the same items.

```
Intentionally left alone:
- LegacyExportAdapter — still has 3 enterprise customers on the old schema; sunset is on the Q3 roadmap
- the `mode` parameter on Search — used by the analytics pipeline, removal would require a coordinated change with that team
```

### 5. Deferred

Use the project tracker for material follow-up work; reference actual issue IDs only after they exist. Do not invent a ticket merely to complete this report format.

```
Deferred (filed as separate tickets):
- #1234 — consolidate notification dispatch (3 paths, but each has independent retry/dedup logic)
- #1235 — remove DUAL_WRITE flag (still needed until the Postgres backfill completes Q1)
- #1236 — rename ProductCatalog (now handles services + bundles + products)
```

## Why this format

Reviewers reading a 2,000-line diff need to understand the _shape_ of the change in 60 seconds. The summary is that 60-second read. Scale the report to the change. Split work along meaningful review and ownership boundaries when that preserves a coherent end state.

Future readers (including future you) come back to figure out "why did we have X and now we have Y?" The summary is the answer. Make it good.

## The thing that does NOT belong in the summary

- Apologies for breaking changes ("sorry, this was unavoidable") — if it's unavoidable, just say what broke and how to migrate; no apology
- A diff narrative ("first I deleted X, then I noticed Y, so I refactored Z") — the diff has the history; the summary has the shape
- Marketing language ("dramatically improves," "industry-leading," "significantly cleaner") — the reviewer can evaluate; don't editorialize
- Speculation about future benefits ("this will make adding new features easier") — sometimes true, often not; prove it with the next feature, don't promise it in the summary

## Validation and recovery evidence

Report the actual commands, results and affected behavior. Distinguish unit or
fixture evidence from integration and production observations. State search scope,
unknown consumers, skipped checks and any untested migration/recovery paths. A
passing test suite does not by itself prove zero external breakage.
