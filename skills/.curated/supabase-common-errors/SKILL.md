---
name: supabase-common-errors
description: 'Diagnose and fix Supabase errors across PostgREST, PostgreSQL, Auth,
  Storage, and Realtime.

  Use when encountering error codes like PGRST301, 42501, 23505, or auth failures.

  Use when debugging failed queries, RLS policy violations, or HTTP 4xx/5xx responses.

  Trigger with "supabase error", "fix supabase", "PGRST", "supabase 403", "RLS not
  working",

  "supabase auth error", "unique constraint", "foreign key violation".

  '
allowed-tools: Read, Grep, Bash(curl:*), Bash(supabase:*), Bash(npx:*)
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - supabase
  - debugging
  - errors
  - postgrest
  - rls
  - auth
compatibility: Designed for Claude Code
---

# Supabase Common Errors

## Overview

Diagnostic guide for Supabase errors across PostgREST (`PGRST*`), PostgreSQL (numeric codes), Auth, Storage, and Realtime. Identify the error layer, trace the root cause, and apply the correct fix — database queries return `{ data, error }`; other SDK services have their own result, callback, and exception contracts.

The workflow is three steps: capture the error object, classify it by layer and code, then apply and verify the fix. Full step-by-step code lives in [the diagnostic walkthrough](references/implementation.md); complete lookup tables are in [the error reference](references/error-reference.md).

## Prerequisites

- `@supabase/supabase-js` installed (`npm install @supabase/supabase-js`)
- `SUPABASE_URL` and a publishable/anon key configured; normal request clients use verified user identity and RLS
- Access to Supabase Dashboard (for log inspection and SQL Editor)
- Supabase CLI installed for local development (`npx supabase --version`)

## Instructions

### Step 1 — Capture the Error Object

Supabase database queries return a `{ data, error }` result. Never assume `data` exists — always destructure and check `error` first, because `data` is null whenever `error` is set.

```typescript
const { data, error } = await supabase.from('todos').select('*');
if (error) {
  console.error(`[${error.code}] ${error.message}`);
  return; // data is null here — do not touch it
}
console.log(`Found ${data.length} rows`);
```

Do not diagnose the installed SDK version solely from an undefined property.
Check which service/method produced the result, its documented shape, and the
locked dependency version. Realtime subscriptions and Python clients differ.

### Step 2 — Identify the Error Layer and Code

Match the code prefix to its subsystem, then look it up in the Error Handling tables below:

- **`PGRST*`** → PostgREST (API gateway: JWT, query parsing, schema)
- **5-character SQLSTATE** (e.g. `42501`, `23505`) → PostgreSQL engine (RLS, constraints, migrations)
- **`AuthApiError`** → Auth service (credentials, confirmation, token expiry)
- **`StorageApiError`** → Storage service (bucket, RLS on `storage.objects`, size limits)

A missing code needs service-specific inspection: 401 can reflect invalid user credentials or a missing bearer identity, and 500 has multiple possible causes. Status alone does not prove a wrong project key or failing SQL function. A paste-ready `diagnoseSupabaseError()` classifier is in [the walkthrough](references/implementation.md).

### Step 3 — Apply the Fix and Verify

Apply the fix from the matching Error Handling table, then re-run the original operation to confirm. Common recoveries:

- For `PGRST301`, verify the JWT/project/session configuration; it means the JWT cannot be decoded or is invalid. Use the Auth session recovery workflow only when appropriate, not an automatic retry loop.
- For `42501`, inspect verified user identity, grants, and RLS under that identity. It means insufficient privilege, not necessarily RLS. Do not bypass the user boundary with a service-role client in the request path.
- After a migration, reload the PostgREST schema cache (an authorized SQL session using `NOTIFY pgrst, 'reload schema'`).

Full before/after fix code for both cases is in [the walkthrough](references/implementation.md).

## Output

Deliverables after applying this skill:

- Error identified by code and layer (PostgREST, PostgreSQL, Auth, Storage, Realtime)
- Root cause isolated using the diagnostic helper or manual code inspection
- Fix applied from the Error Handling table and verified against the original failing operation
- Guard code in place (`if (error)` checks) preventing silent null-data bugs

## Error Handling

The two most-cited layers are inline below. Auth, Storage, and Realtime tables are in [the full error reference](references/error-reference.md).

### PostgREST API Errors (PGRST\*)

| Code       | HTTP | Meaning                                             | Root Cause                                     | Fix                                                                                      |
| ---------- | ---- | --------------------------------------------------- | ---------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `PGRST301` | 401  | JWT cannot be decoded or is invalid                 | Invalid token or mismatched configuration      | Verify token/project/session through the appropriate Auth workflow; do not retry blindly |
| `PGRST302` | 401  | Bearer request absent while anonymous role disabled | Request lacks required identity                | Verify authenticated bearer propagation and server configuration                         |
| `PGRST116` | 406  | Singular result has zero or multiple rows           | Result does not satisfy exactly-one contract   | Use `.maybeSingle()` for zero-or-one; correct multiple matches                           |
| `PGRST200` | 400  | Relationship/schema-cache mismatch                  | Embedded relationship absent or stale          | Check foreign keys and embedding; refresh cache if appropriate                           |
| `PGRST204` | 400  | Column not found                                    | Column name doesn't exist in the table or view | Verify column exists with `supabase gen types typescript`; check for typos               |
| `PGRST000` | 503  | Database connection unavailable                     | Invalid database URI or database not running   | Inspect service configuration and availability                                           |
| `PGRST003` | 504  | Pool acquisition timed out                          | No pool connection became available            | Inspect query load and pool capacity; apply bounded admission                            |

### PostgreSQL Database Errors (SQLSTATE)

| Code    | Meaning                             | Root Cause                                       | Fix                                                                                                            |
| ------- | ----------------------------------- | ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------- |
| `42501` | Insufficient privilege              | Grants or RLS deny this identity                 | Review grants and policies with the actual authorized user                                                     |
| `23505` | Unique constraint violation         | INSERT/UPDATE conflicts with an existing row     | Review conflict semantics; `.upsert(row, { onConflict: 'column' })` can overwrite data and needs authorization |
| `23503` | Foreign key violation               | Referenced row doesn't exist in the parent table | Insert the parent row first, or check the foreign key value                                                    |
| `42P01` | Table or relation doesn't exist     | Migration not applied, or wrong schema           | Run `supabase db push`; verify schema with `\dt` in SQL Editor                                                 |
| `42703` | Column doesn't exist                | Schema out of sync with code                     | Regenerate types: `supabase gen types typescript --local > types/supabase.ts`                                  |
| `57014` | Query cancelled (statement timeout) | Query took longer than `statement_timeout`       | Add indexes; simplify the query; increase timeout in `postgresql.conf`                                         |

## Examples

The most common failure — calling `.single()` on optional data — is inline below. Three more worked examples (upsert to dodge `23505`, Realtime subscription error handling, and serverless pool exhaustion) are in [the examples reference](references/examples.md).

### Handling `.single()` on optional data (PGRST116)

```typescript
const { data: profile, error } = await supabase
  .from('profiles')
  .select('id, display_name')
  .eq('user_id', userId)
  .maybeSingle();
if (error) throw error;
if (!profile) {
  // A successful zero-row read is not authorization to create an arbitrary profile.
  // Present the application's separately authorized create-profile workflow.
}
```

## Resources

- [Full diagnostic walkthrough](references/implementation.md) — every capture/classify/fix code block
- [Complete error reference](references/error-reference.md) — Auth, Storage, and Realtime tables
- [Worked examples](references/examples.md) — upsert, Realtime, serverless pooling
- [Supabase JavaScript SDK Reference](https://supabase.com/docs/reference/javascript/introduction)
- [PostgREST Error Codes](https://postgrest.org/en/stable/references/errors.html)
- [PostgreSQL Error Codes](https://www.postgresql.org/docs/current/errcodes-appendix.html)
- [RLS Debugging Guide](https://supabase.com/docs/guides/database/postgres/row-level-security)
- [Supabase Realtime Troubleshooting](https://supabase.com/docs/guides/realtime/troubleshooting)
- [Supabase Status Page](https://status.supabase.com)

## Next Steps

- Use `supabase-debug-bundle` to generate a full diagnostic snapshot when errors persist after applying these fixes.
- Use `supabase-security-basics` to audit your RLS policies and prevent `42501` errors proactively.
- Use `supabase-known-pitfalls` for edge cases and SDK behavior that can cause subtle bugs.
- Use `supabase-observability` to set up logging and alerting so you catch errors before users report them.
