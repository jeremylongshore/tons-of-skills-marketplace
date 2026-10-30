# Custom Metrics, Alerting, and Health Checks

## Custom Metrics via Edge Functions

Collect bounded observations only from a reviewed existing table and bucket. Keep the deployed function's JWT verification enabled and restrict its invocation to approved monitoring identities; this example also verifies the request's user. It grants no monitoring entitlement by itself. Do not expose admin data or credentials. Storage listing is a root-entry sample, not a recursive object count or quota measurement.

```typescript
import { createClient } from '@supabase/supabase-js';

Deno.serve(async (request) => {
  const reply = (status: number, body: object) => new Response(JSON.stringify(body), {
    status, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'private, no-store' },
  });
  try {
    const authorization = request.headers.get('authorization');
    if (!authorization?.startsWith('Bearer ')) return reply(401, { error: 'Authentication required' });
    const client = createClient(Deno.env.get('SUPABASE_URL')!, Deno.env.get('SUPABASE_PUBLISHABLE_KEY')!, {
      global: { headers: { Authorization: authorization } },
      auth: { persistSession: false, autoRefreshToken: false },
    });
    const { data: { user }, error: authError } = await client.auth.getUser();
    if (authError || !user) return reply(401, { error: 'User verification failed' });
    const table = Deno.env.get('APPROVED_METRICS_TABLE');
    const bucket = Deno.env.get('APPROVED_METRICS_BUCKET');
    if (!table || !bucket) return reply(503, { error: 'Approved probe configuration required' });
    const { count, error: queryError } = await client.from(table).select('id', { count: 'exact', head: true });
    if (queryError || typeof count !== 'number' || !Number.isSafeInteger(count) || count < 0)
      return reply(503, { error: 'Approved table query failed' });
    const { data: entries, error: storageError } = await client.storage.from(bucket).list('', { limit: 20, offset: 0 });
    if (storageError || !Array.isArray(entries) || entries.length > 20)
      return reply(503, { error: 'Storage sample failed' });
    return reply(200, { status: 'observed', visible_table_rows: count, root_entries_sampled: entries.length, sample_limit: 20 });
  } catch {
    return reply(503, { error: 'Probe failed' });
  }
});
```

These user-scoped observations are not total users, total stored objects, database size, plan capacity, or overall platform health. No metrics write or undefined RPC is required. Use approved Dashboard/database monitoring for separately authorized capacity measurements.

Schedule through the [official Edge Function scheduling workflow](https://supabase.com/docs/guides/functions/schedule-functions):

1. Deploy and authorize the collector, then enable the required `pg_cron` and `pg_net` extensions.
2. Provision its project URL and appropriate invocation credential in Vault through an approved secret-management path; never commit plaintext credentials.
3. Create a reviewed `cron.schedule` job that invokes `net.http_post`, reading connection values from Vault. Match the function's authentication mode to the documented scheduler flow rather than disabling verification to silence errors.
4. Verify a synthetic authorized invocation and rejection of unauthorized calls. Inspect cron execution and function logs; scheduling an HTTP request alone does not prove successful metrics collection.

There is no function-level TOML schedule setting in this workflow.

## Health Check Endpoint

Use the authenticated bounded collector above as a probe of those specific operations only, with the same private, no-store responses and approved monitoring access. Treat authentication, query, storage, configuration, and thrown errors as failed probes; never report success on a returned error. A successful probe does not establish global service health. Do not invent `version` or `get_database_size` RPCs: database functions must be explicitly deployed and authorized before use.

## Real-time Connection Monitoring

Track active Realtime connections:

```typescript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

// Monitor channel state changes
const channel = supabase.channel('monitoring');

channel
  .on('system', { event: '*' }, (payload) => {
    console.log(`[REALTIME] System event:`, payload);
  })
  .subscribe((status) => {
    console.log(`[REALTIME] Connection status: ${status}`);
    if (status === 'CHANNEL_ERROR') {
      console.error('[REALTIME] Connection lost — will auto-reconnect');
    }
  });
```
