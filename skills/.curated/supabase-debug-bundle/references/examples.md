# Diagnostic export review

A stack trace can embed a token-bearing URL; a database error can embed SQL values;
a bucket or object name can identify a customer. These are not automatically safe
just because they are diagnostic output. Credentials, personal data, project IDs
and internal topology must be minimized according to the intended recipient.

1. Inspect the private [collector](../SKILL.md) receipts and preserve failures.
2. Select the minimum observations needed to explain the issue.
3. Build a separate export with reviewed field replacements and no credentials.
4. Review the exact export, including archive members, then obtain sharing approval.

The private source directory and candidate archive remain local. Do not treat
`REVIEW-REQUIRED.txt`, successful archive creation or a regex search with no matches
as sanitization evidence. No support upload occurs as part of collection.

## Operator probe examples

Run these only for the approved project and identity. They make actual requests; they are not offline fixture checks.

**Quick connectivity check (no service key needed):**

```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(process.env.SUPABASE_URL!, process.env.SUPABASE_ANON_KEY!)

const table = process.env.SUPABASE_DIAGNOSTIC_TABLE
if (!table) throw new Error('An approved diagnostic table is required')
const start = Date.now()
const { error } = await supabase.from(table).select('id', { head: true }).limit(1)
console.log({
  query_accepted: !error,
  latency_ms: Date.now() - start,
  error_code: error?.code ?? null,
  scope: 'approved table only; not overall health or RLS verification',
})
```

**Verify the current user from an approved running app's user client:**

```typescript
const { data: { user }, error } = await supabase.auth.getUser()
if (error || !user) console.log('No server-verified authenticated user', error?.code ?? null)
else console.log('Current user verified by Auth server')
```

This is a fresh user lookup, not a complete Auth-platform health check. Do not use an admin client's absence of a user session to diagnose an outage, and never include session tokens in the bundle.
