# Supabase Error Code Reference

Use the exact service, locked version, returned error code, and documented response
contract. This is a selected diagnostic reference, not an exhaustive list or proof
that every failure has one cause. Database queries normally return `{ data, error }`;
Auth, Storage, Realtime callbacks and Python exceptions have different contracts.

## PostgREST Database API

Reviewed against the [official error reference](https://docs.postgrest.org/en/stable/references/errors.html)
on 2026-10-22. Prefer the server's actual version documentation if it differs.

| Code     | HTTP | Meaning and next check                                                                        |
| -------- | ---- | --------------------------------------------------------------------------------------------- |
| PGRST000 | 503  | Cannot connect: incorrect database URI or database not running; inspect service configuration |
| PGRST001 | 503  | Internal database-connection error; inspect availability and protected operational evidence   |
| PGRST002 | 503  | Database unavailable while building schema cache                                              |
| PGRST003 | 504  | Timed out waiting for a pool connection; inspect workload and pool capacity                   |
| PGRST100 | 400  | Query-string parsing error; inspect documented filter syntax                                  |
| PGRST116 | 406  | Singular response has zero or multiple rows; maybeSingle permits zero, not multiple           |
| PGRST200 | 400  | Embedded relationship missing or stale in schema cache; inspect foreign keys/embedding        |
| PGRST204 | 400  | Specified column absent; check schema and cache                                               |
| PGRST301 | 401  | JWT cannot be decoded or is invalid; check project/token/session configuration                |
| PGRST302 | 401  | Bearer authentication absent while anonymous role disabled                                    |
| PGRST303 | 401  | JWT claims validation or parsing failed                                                       |

Do not relabel PGRST301 as a connection error or blindly refresh/retry every 401.
A missing user session, invalid credential, and wrong project require different
remedies. Do not diagnose RLS by comparing a user's row count with a privileged one.

## PostgreSQL SQLSTATE

SQLSTATE is five characters, not always five digits. Codes can reach the Data API
from PostgreSQL; inspect the exact operation and policies before changing anything.

| Code  | Meaning                | Disposition                                                                                  |
| ----- | ---------------------- | -------------------------------------------------------------------------------------------- |
| 42501 | Insufficient privilege | Review grants, identity and RLS under the actual caller; not automatically an RLS-only issue |
| 23505 | Unique violation       | Reconcile conflict semantics; upsert may overwrite and needs explicit authorization          |
| 23503 | Foreign-key violation  | Verify intended ownership, parent row and dependency order                                   |
| 42P01 | Undefined table        | Check schema/migrations through the reviewed deployment workflow                             |
| 42703 | Undefined column       | Check schema, generated types and spelling                                                   |
| 57014 | Query cancelled        | Check deadline/load and indexes; do not automatically increase timeouts or replay writes     |

## Auth, Storage and Realtime

- Auth: inspect documented error codes and recovery flows. Do not disclose whether
  an account exists through a public diagnostic endpoint. Link/OTP expiry depends
  on the configured flow; no universal five-minute default is assumed here.
- Storage: verify bucket/path, operation-specific policies, and configured file
  limits. A resumable transport does not override the bucket's size limit. Upsert
  grants overwrite semantics, not a safe universal response to a conflict.
- Realtime: CHANNEL_ERROR and TIMED_OUT can have several causes. Check identity,
  channel authorization, connectivity, publication membership for Postgres Changes,
  and actual subscription status. Do not log changed rows or assume auto-reconnect
  guarantees recovery of missed events.

[Auth errors](https://supabase.com/docs/guides/auth/debugging/error-codes)
[Storage errors](https://supabase.com/docs/guides/storage/debugging/error-codes)
[PostgreSQL codes](https://www.postgresql.org/docs/current/errcodes-appendix.html)
[Realtime troubleshooting](https://supabase.com/docs/guides/realtime/troubleshooting)
