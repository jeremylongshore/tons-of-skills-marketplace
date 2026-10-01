# Merge enablement

Review every open Hermes Tweet pull request before proposing another one.

## Find every pull request

Enumerate every open in-scope PR before discovery or outreach. A capped GitHub
CLI result is incomplete. Use paginated GraphQL or search API queries. Split
capped results by author, head owner, base repository, keyword, date, and state.

Write the enumeration and audit evidence to unique temporary files:

- `/tmp/hermes-tweet-open-prs-<timestamp>.json`
- `/tmp/hermes-tweet-pr-audit-<timestamp>.jsonl`

Missing pages, partial JSON, API errors, rate limits, or unclear caps leave the
audit incomplete. Retry or split the query. Validate each query against a known
open Hermes Tweet PR. If a query returns zero unexpectedly, record and rerun it
with explicit GitHub flags or GraphQL variables.

## Limit search shards

Start with exact Hermes Tweet and Hermes Agent queries. Include all tracked PRs.
Broad `xquik`, `tweet`, or `twitter` queries match unrelated work and consume
API quota.

Stop a query that expands to hundreds of endpoint reads. Save `complete: false`,
the reason, and the query. Rerun with exact terms or date windows. An aborted
query does not prove coverage. Keep capped URLs out of the final audit set.

## Audit each pull request

For each verified PR URL, read:

- mergeability and conflict status
- status checks and commit statuses
- review decisions and actionable review comments
- unresolved review threads where GitHub exposes them
- comments from maintainers and review bots
- head branch owner, fork owner, and branch drift

Repair controllable blockers only through verified `kriptoburak` branches.
Record maintainer-only checks, account failures, missing contexts, or unavailable
CI logs. Do not invent code changes for those blockers. When a dirty PR uses a
third-party fork or a head owner other than
`kriptoburak`, treat the conflict as non-controllable even when GitHub reports
`maintainerCanModify`. Record the head owner and conflict state, then continue
without pushing to that fork.

Verify aggregate `UNKNOWN` mergeability with a direct PR read. If it reports `DIRTY` or
`CONFLICTING` on a verified `kriptoburak` head branch, repair the branch before
discovery. If the head branch is not controlled, record the owner, the conflict
state, and the target-side evidence instead of attempting a repair.

## Review install commands

When a submission adds Hermes Tweet install instructions, verify every changed
snippet uses `hermes plugins install Xquik-dev/hermes-tweet --enable` or includes
an immediate `hermes plugins enable hermes-tweet` follow-up. Treat review
threads about missing enablement as controllable on verified `kriptoburak`
branches, because an installed but disabled plugin leaves the advertised
`hermes-tweet` tools unavailable.

## Submission gate

Open a new external PR only after every tracked PR is clean, repaired, or
blocked by the target. If no external route qualifies, improve first-party
discovery, validation, safety, or submission guidance instead. A prepared fork
branch is not outreach. If GitHub rejects PR creation, record the API error and
try another eligible route.

When a candidate's duplicate PR search is rate-limited or otherwise incomplete,
record the failed query and do not treat the target as eligible. Continue only
when the target already fails an independent fit check, such as
MCP-only registries, product-owned skill taps, or single-product plugin repos.
