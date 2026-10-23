# Common Errors: Worked Examples

These application helpers assume an existing schema with the stated columns and
RLS/grants for the authenticated user. Pass a request-scoped user client; do not
share sessions across users or pass a service-role client to this request code.
Construction alone is not a database connection or authorization test.

## Optional Profile: Check Error Before Null

```typescript
import type { SupabaseClient } from '@supabase/supabase-js';

export async function ownProfile(client: SupabaseClient) {
  const {
    data: { user },
    error: authError,
  } = await client.auth.getUser();
  if (authError || !user) throw new Error('Verified user required');
  const { data, error } = await client
    .from('profiles')
    .select('id, display_name')
    .eq('user_id', user.id)
    .maybeSingle();
  if (error) throw error; // multiple rows and other failures remain errors
  return data; // null is a successful zero-row result, not permission to insert
}
```

`.single()` reports zero OR multiple rows through an error result; it does not
normally throw that result as an exception. `.maybeSingle()` permits zero rows only.

## Deliberate Upsert, Not a Universal Duplicate Fix

```typescript
export async function setOwnTheme(client: SupabaseClient, theme: 'dark' | 'light') {
  const {
    data: { user },
    error: authError,
  } = await client.auth.getUser();
  if (authError || !user) throw new Error('Verified user required');
  const { error } = await client
    .from('user_settings')
    .upsert({ user_id: user.id, theme }, { onConflict: 'user_id' });
  if (error) throw error;
}
```

This requires a unique `user_id` and reviewed insert/update policies. Upsert can
overwrite an existing value; never use it to suppress an unexplained uniqueness
violation or to merge data across identities. A timed-out write needs reconciliation
before a retry decision.

## Realtime Status and Cleanup

```typescript
export function watchTodos(client: SupabaseClient, onStatus: (status: string) => void) {
  const channel = client
    .channel('own-todos')
    .on('postgres_changes', { event: '*', schema: 'public', table: 'todos' }, () =>
      onStatus('change-notification'),
    )
    .subscribe((status) => onStatus(status));
  return () => client.removeChannel(channel);
}
```

Subscribe only under the correct user identity and database/publication policies.
The callback intentionally does not log changed rows. CHANNEL_ERROR does not prove
one specific configuration defect; investigate the actual service response. On
reconnect, reconcile data rather than assuming all missed events will be replayed.
Call the returned cleanup function when the view/request lifecycle ends.

## Data API Versus Direct SQL Pools

The HTTP SDK is not a direct Postgres client pool. A request-scoped SSR client does
not imply a new SQL connection for each invocation. PGRST000 concerns unavailable
or misconfigured database connectivity; PGRST003 is the pool acquisition timeout.
Inspect server workload and capacity before changing pool settings. Direct `pg`
clients and Supavisor session/transaction modes have separate connection contracts.
Do not fix a user-session problem by caching a mutable authenticated singleton.

## Bounded Escalation Evidence

Record the service, safe error code, approximate time, operation class, locked
version and protected request ID. Use the actual project URL and an approved table
for any separately authorized probe, not Management API availability as a proxy.
Never run `env | grep SUPABASE` in a shared report: it can expose credentials.

[Error reference](error-reference.md)
[Diagnostic walkthrough](implementation.md)
[Database connections](https://supabase.com/docs/guides/database/connecting-to-postgres)
