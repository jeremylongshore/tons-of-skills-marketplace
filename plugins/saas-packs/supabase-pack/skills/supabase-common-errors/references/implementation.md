# Common Errors: Diagnostic Walkthrough

## 1. Capture the Correct Contract Without Leaking Data

Database queries return `{ data, error }`; check the error before using data. Do
not infer the SDK version from one missing property, or assume subscription callbacks
and Python clients return the same shape. Use the locked version's documentation.
The example receives a client already scoped to the intended user/public operation.
The existing `todos` table needs appropriate grants/RLS; this is not an admin probe.

```typescript
import type { SupabaseClient } from '@supabase/supabase-js';

export async function probeTodos(client: SupabaseClient) {
  const { data, error } = await client.from('todos').select('id').limit(1);
  if (error) return { available: false, code: safeDatabaseCode(error) };
  return { available: true, visibleSampleRows: data.length };
}

export function safeDatabaseCode(error: unknown): string | null {
  if (!error || typeof error !== 'object') return null;
  const code = (error as { code?: unknown }).code;
  return typeof code === 'string' && /^(?:PGRST[0-9A-Z]{3}|[0-9A-Z]{5})$/.test(code) ? code : null;
}
```

No rows is a successful empty visible sample, not proof that the table is empty or
that its RLS is correct. Do not log raw error objects, hints, tokens, user rows or
environment values to stdout. Keep request IDs and bounded diagnostic summaries in
an access-controlled channel.

## 2. Use Service Context, Not Message Guessing

```typescript
export function classifyDatabaseFailure(error: unknown): string {
  const code = safeDatabaseCode(error);
  if (code?.startsWith('PGRST')) return 'postgrest';
  if (code) return 'postgresql';
  return 'unclassified';
}
```

This helper is only for an error already known to come from a database query. It
does not automatically identify Auth/Storage by searching error-message text. Their
service-specific contracts and Realtime callback statuses need separate handling.
HTTP status alone does not prove a wrong project key or a failing database function.

## 3. Correct the Actual Failure and Verify Under the Same Identity

- PGRST301 means an undecodable/invalid JWT, not a transient connection error or
  universal expiry signal. Check project and session configuration. Recover the
  session only through the appropriate Auth workflow; do not repeatedly refresh,
  sign users out, or retry writes based on this code alone.
- 42501 means insufficient privilege. Verify the caller using fresh `getUser()`,
  then inspect table grants and policies in a separately authorized catalog session.
  A service-role success does not establish which grant/policy failed. Never inject
  that privileged client into the user's request as a fix.
- For schema-cache issues, verify the actual migration/schema first. An authorized
  SQL session can issue `NOTIFY pgrst, 'reload schema';` when appropriate. Do not
  deploy migrations or change policies merely because a diagnostic helper ran.
- Re-run the original bounded operation under the original intended identity.
  Check every returned error. Do not print user identifiers/rows in the evidence.

[Selected error reference](error-reference.md)
[PostgREST errors](https://docs.postgrest.org/en/stable/references/errors.html)
[RLS](https://supabase.com/docs/guides/database/postgres/row-level-security)
