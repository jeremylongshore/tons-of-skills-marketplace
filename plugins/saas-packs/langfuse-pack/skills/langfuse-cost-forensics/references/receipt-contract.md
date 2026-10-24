# Recorded-cost and coverage receipts

`scripts/inspect-costs.py` reads supplied Observations API v2 pages. It performs
no provider call, credential lookup, price lookup, model routing, alert delivery,
score write, or deployment. It audits the retained observation set, rather than
estimating a provider invoice or treating a first page as total project spend.

## Input envelope

The owned envelope has integer `schema_version: 1`,
`receipt_kind: "observations-v2"`, `context`, and a nonempty `pages` array.

| Context field                                     | Meaning                                                                                                                    |
| ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `project_id`                                      | Expected project ID, obtained from the authorized source.                                                                  |
| `from_start_time`, `to_start_time`                | Absolute timezone-aware timestamps. The interval includes its start and excludes its end. Maximum span: 366 days.          |
| `collection_started_at`, `collection_finished_at` | Actual collection times, not the data-query window. A future query window cannot establish complete recorded cost.         |
| `collection_complete`                             | Boolean collection outcome or null when unknown. Set false on caps, errors, interruptions, or filtered/incomplete exports. |

Each page has `request` (the actual SDK `getMany` query arguments) and
`response` (the native parsed response). Preserve query parameters and cursors;
never include authorization headers, key values, or an SDK client object.

The supported query arguments are `fields`, `limit`, `cursor`, `fromStartTime`,
`toStartTime`, `type`, `environment`, `version`, `name`, `traceId`, `level`,
`userId`, `sessionId`, `parentObservationId`, `isRootObservation`, `filter`, and
`parseIoAsJson`. Other options need a reviewed adapter. Omit `parseIoAsJson`,
or set it to false; the native v2 API rejects true. Keep the same query on every
page apart from the cursor. Explicit timestamps must agree with the context.
Additional scalar filters are retained in the query digest. The analyzer checks
project and start-window binding against rows; it does not replay every other
provider filter predicate or certify that the provider applied it correctly.

Structured `filter` takes precedence over simple query filters in the API.
This analyzer does not interpret that filter language: a nonempty filter is
marked for scope review and withholds complete-set cost. Individual retained
rows must still belong to the declared project and time window. Query scope is
hashed in the result, never printed with potentially sensitive filter values.

## Native response mapping

`response.data` is an array of observation objects, and `response.meta` is an
object. In the pinned JS/TS client 6.0.2 contract, the next cursor is
`meta.cursor`; **it is omitted at the end**, not represented as a null cursor.
The first request has no cursor. Each later request must use the preceding
response's cursor. Missing final pages, repeated cursors, empty nonterminal
pages, changed queries, and restarted chains prevent a complete page-chain claim.

Use field groups such as `core,basic,model,usage`. Core identity and time fields
are always included. The default groups omit usage and cost fields; forgetting
the `usage` group is not evidence that an observation costs zero. Avoid fetching
`io` and `metadata` for this workflow when they are unnecessary. The analyzer
does not emit those values even if they appear in supplied pages.

The analyzer consumes:

- `id`, `traceId`, `projectId`, `startTime`, `endTime`, and `type` from core fields.
- `model` for a hashed group identifier when available.
- `totalCost` and `usageDetails` from the `usage` field group.

Only `GENERATION` and `EMBEDDING` observations are eligible for cost coverage.
Identity is the project-bound `(traceId, id)` pair. Repeated identities are held
rather than silently choosing a revision or double-counting its cost. Equal span
IDs under different traces remain distinct. Missing project/trace identity or
rows outside the declared interval are held.

Record `totalCost` as supplied. Null or absent values remain unavailable, even
when `costDetails` exists. The analyzer does not sum potentially overlapping
cost components or reconstruct prices. Explicit numeric zero is a known value.
Numbers and bounded numeric strings are accepted; booleans, nonfinite values,
negative adjustments, and extreme exponents are held for separate handling.
Decimal summation avoids introducing binary floating-point accumulation error;
it cannot recover precision already lost upstream.

Nonempty numeric `usageDetails` establishes that usage values were retained.
The analyzer does not sum arbitrary usage types: input, output, total, audio,
cached, and other units must not be added indiscriminately. Open observations,
unavailable usage, unknown collection completeness, and future windows require
investigation rather than a final-cost conclusion.

## Output and limits

Run `python3 scripts/inspect-costs.py pages.json` from the skill directory,
or pipe JSON to stdin. At most 2 MiB, 100 pages, 1,000 rows per page, and
10,000 rows overall are accepted. Native default page size is 50. Duplicate JSON
keys and invalid inputs produce a fixed hold code on stderr with exit 2.

- Exit 0: `reviewable-retrieved-set`, with a complete chain and no detected gaps.
- Exit 1: `needs-investigation`; inspect finding codes and counts.
- Exit 2: invalid/unreadable evidence; no report was produced.

`known_rows_recorded_cost_usd` is only the subtotal of eligible rows whose cost
was actually retained. It is null when none has known cost, rather than zero.
`retrieved_set_recorded_cost_usd` is withheld when any investigation condition
remains. Neither field claims total project spend or a billable amount.

The output reports the observed denominator, unavailable-cost count, explicit
zeros, and usage coverage. Model groups are hashed, sorted by hash, and limited
to the first 50 with an explicit truncation flag; this is not a top-cost ranking.
Findings are limited to the first 100 with the full count retained. The CLI binds
the report to the exact input-byte SHA-256. Raw IDs, cursors, models, prompts,
answers, credentials, and filter values are not echoed. Original receipts and
cost data still need controlled storage; this tool authorizes no external sharing.

Cursor exhaustion is not an atomic snapshot. Exporter sampling, ingestion
latency, dropped spans, mutable observations, and undisclosed source filtering
can leave unobserved calls. A supplied completeness declaration is not
authenticated. Recorded cost may have been ingested directly or inferred from
model definitions; that provenance and invoice reconciliation require separate
evidence. For project-wide aggregate queries, use Metrics API v2 instead of a
bounded observation scan and retain that query's scope and limits separately.

## Primary references

- [Public API and SDK resources](https://langfuse.com/docs/api-and-data-platform/features/public-api)
- [Observations API reference](https://api.reference.langfuse.com/)
- [Client 6.0.2 package metadata](https://registry.npmjs.org/@langfuse/client/6.0.2)
- [Token and cost tracking](https://langfuse.com/docs/observability/features/token-and-cost-tracking)
- [Metrics API v2](https://langfuse.com/docs/metrics/features/metrics-api)
