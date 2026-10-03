# Bug clustering runtime contract

## Implemented stages

- `parseCandidate()` extracts symptoms, error strings, reproduction hints, URLs, surface, and feature
  with regular expressions. It selects one of 12 classifications through fixed phrase rules.
- `redactPii()` replaces matching email, token-like, phone, account-ID, and URL-token strings. Media is
  represented by keys and a boolean; there is no separate media-redaction detector.
- `scoreReporter()` uses fixed arithmetic over text length, extracted details, engagement, and reply
  shape. Historical accuracy is currently always `0.5`.
- `deduplicateCandidates()` performs pairwise text comparison and returns canonical IDs; it does not
  modify candidate rows.
- `clusterCandidates()` reads active suppression rules, groups only eligible families, and writes
  cluster plus cluster-post rows. New severity is always `low`.

## Not implemented as one command

There is no checked-in CLI that runs parse, deduplicate, candidate persistence, cluster persistence,
and audit logging as one transaction. The caller owns orchestration and rollback. `clusterCandidates()`
does not insert candidates or audit events and does not persist deduplication groups.

## Data boundaries

The SQLite schema stores redacted text, but pattern matching is not a complete data-loss-prevention
control. Treat source selection and operator review as separate security boundaries.
