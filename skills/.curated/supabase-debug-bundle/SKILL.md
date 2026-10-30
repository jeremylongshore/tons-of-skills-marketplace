---
name: supabase-debug-bundle
description: 'Collect Supabase diagnostic info for troubleshooting and support tickets.

  Use when debugging connection failures, auth issues, Realtime drops, Storage

  errors, RLS misconfigurations, or preparing a support escalation.

  Trigger: "supabase debug", "supabase diagnostics", "supabase support bundle",

  "collect supabase logs", "debug supabase connection".

  '
allowed-tools: Read, Bash(npx:*), Bash(node:*), Bash(curl:*), Bash(supabase:*), Bash(tar:*),
  Grep, Glob
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- supabase
- debugging
- support
- diagnostics
compatibility: Designed for Claude Code
---
# Supabase Debug Bundle

## Overview

Collect approved diagnostic observations into a local candidate bundle. Record query/authentication outcomes and inconclusive results without claiming complete service-health or RLS verification. Minimize and sanitize the evidence, then obtain owner review before any sharing with support.

## Manual Environment Diagnostics

These commands are shown for an operator to run after approval, not executed when the skill loads. Use the project's installed CLI; a missing dependency is not a successful check.

```text
node --version
npx supabase --version
npm list @supabase/supabase-js
```

## Prerequisites

- **Node.js 22+** with `@supabase/supabase-js` v2 installed in the project
- **Supabase CLI** installed (`npm install --save-dev supabase` or `npx supabase`)
- **Environment variables** set: `SUPABASE_URL` and `SUPABASE_ANON_KEY` (minimum); `SUPABASE_SERVICE_ROLE_KEY` for full diagnostics
- Project linked and target verified before approved CLI diagnostics
- An explicitly approved existing diagnostic table with an `id` column, selected through `SUPABASE_DIAGNOSTIC_TABLE`; no automatic table discovery or creation

## Instructions

### Step 1: Gather Environment and Connectivity

Collect SDK version, project URL, key type, and test basic connectivity against the REST and Auth endpoints.

```typescript
import { createClient } from '@supabase/supabase-js'

const url = process.env.SUPABASE_URL!
const anonKey = process.env.SUPABASE_ANON_KEY!
const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY

// Identify which key is in use
const keyType = serviceKey ? 'service_role' : 'anon'
const supabase = createClient(url, serviceKey ?? anonKey, {
  auth: { autoRefreshToken: false, persistSession: false }
})

const diagnostics: Record<string, unknown> = {}

// 1a — SDK + environment
diagnostics.environment = {
  supabase_js_version: require('@supabase/supabase-js/package.json').version,
  node_version: process.version,
  project_url: url.replace(/https:\/\/([^.]+)\..*/, 'https://$1.***'),
  key_type: keyType,
  timestamp: new Date().toISOString(),
}

// 1b — REST API connectivity
const restStart = Date.now()
const restRes = await fetch(`${url}/rest/v1/`, {
  headers: { apikey: anonKey, Authorization: `Bearer ${anonKey}` },
})
diagnostics.rest_api = {
  status: restRes.status,
  latency_ms: Date.now() - restStart,
  ok: restRes.ok,
}

// 1c — Local auth storage is not an Auth-server availability/identity check.
const { data: sessionData, error: sessionErr } = await supabase.auth.getSession()
diagnostics.auth_storage = {
  status: sessionErr ? 'local_storage_error' : 'local_storage_read',
  has_session: !!sessionData?.session,
  identity_verified: false,
}

// 1d — Query only an approved table; never turn a missing-table error into success.
const probeTable = process.env.SUPABASE_DIAGNOSTIC_TABLE
if (!probeTable) {
  diagnostics.database = { status: 'not_run', detail: 'No approved diagnostic table' }
} else {
  const dbStart = Date.now()
  const { error } = await supabase.from(probeTable).select('id', { head: true }).limit(1)
  diagnostics.database = {
    status: error ? 'query_failed' : 'query_accepted',
    error_code: error?.code ?? null,
    latency_ms: Date.now() - dbStart,
    scope: 'approved table only; not overall health or RLS verification',
  }
}

console.log(JSON.stringify(diagnostics, null, 2))
```

**What to check:** Record the actual REST status. Local session storage is not a verified identity or platform-health signal. A successful table probe establishes only that approved query; missing tables (`42P01` or `PGRST205`), authorization failures, and all other returned errors remain failures. Provision or review the diagnostic table separately; do not fabricate a health RPC.

### Step 2: Test Realtime, Storage, and RLS

Probe the three subsystems that cause the most support tickets.

```typescript
// 2a — Realtime subscription observation with checked channel cleanup
const channel = supabase.channel('debug-probe')
let timeout: ReturnType<typeof setTimeout> | undefined
let realtimeResult: Record<string, unknown>
try {
  realtimeResult = await new Promise<Record<string, unknown>>((resolve) => {
    timeout = setTimeout(() => {
      resolve({ status: 'timeout', detail: 'No SUBSCRIBED event within 5s' })
    }, 5000)
    channel.subscribe((status) => {
      if (status === 'SUBSCRIBED') {
        resolve({ status: 'ok', detail: 'Channel subscribed successfully' })
      } else if (status === 'CHANNEL_ERROR') {
        resolve({ status: 'error', detail: 'CHANNEL_ERROR on subscribe' })
      }
    })
  })
} finally {
  if (timeout !== undefined) clearTimeout(timeout)
  const cleanup = await supabase.removeChannel(channel)
  if (cleanup !== 'ok') throw new Error('Realtime probe cleanup failed')
}
diagnostics.realtime = realtimeResult

// 2b — Storage bucket listing
const { data: buckets, error: storageErr } = await supabase.storage.listBuckets()
diagnostics.storage = {
  status: storageErr ? `error: ${storageErr.message}` : 'ok',
  bucket_count: buckets?.length ?? 0,
  buckets: buckets?.map((b) => ({ name: b.name, public: b.public })) ?? [],
}

// 2c — Counts are observations, not an RLS verdict. Both probes require approval.
if (serviceKey && probeTable) {
  const anonClient = createClient(url, anonKey, {
    auth: { autoRefreshToken: false, persistSession: false },
  })
  const [anonResult, adminResult] = await Promise.all([
    anonClient.from(probeTable).select('id', { count: 'exact', head: true }),
    supabase.from(probeTable).select('id', { count: 'exact', head: true }),
  ])
  diagnostics.rls_comparison = {
    status: anonResult.error || adminResult.error ? 'query_failed' : 'inconclusive',
    anon_error_code: anonResult.error?.code ?? null,
    admin_error_code: adminResult.error?.code ?? null,
    anon_visible_rows: anonResult.count,
    admin_visible_rows: adminResult.count,
    scope: 'Counts alone cannot establish RLS status or correctness',
  }
} else {
  diagnostics.rls_comparison = { status: 'not_run', detail: 'Requires approved table and admin probe' }
}
```

**What to check:** Realtime should reach `SUBSCRIBED` within 5 seconds. Storage should list buckets without error. Equal or different counts are inconclusive: empty tables, grants, data, and policy scope can all affect results. Separately authorize SQL catalog inspection and seeded multi-user access tests; `information_schema` is not assumed to be exposed as a Data API table.

### Step 3: Collect Database Health and Package the Bundle

Collect only approved database statistics and platform-status evidence. The script below creates a local candidate archive; its example masking is incomplete and does not approve the result for export.

```bash
#!/bin/bash
set -euo pipefail

BUNDLE_DIR="supabase-debug-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BUNDLE_DIR"

# 3a — Supabase CLI status (local dev)
npx supabase status > "$BUNDLE_DIR/cli-status.txt" 2>&1 || echo "CLI status unavailable (not linked or no local dev)" > "$BUNDLE_DIR/cli-status.txt"

# 3b — Approved database inspections; preserve individual exit statuses.
# A captured output file can contain an error, not a successful observation.
STATUS_FILE="$BUNDLE_DIR/inspect-status.tsv"
printf 'inspection\texit_status\n' > "$STATUS_FILE"
for inspection in table-sizes index-usage cache-hit seq-scans long-running-queries bloat replication-slots; do
  if npx supabase inspect db "$inspection" > "$BUNDLE_DIR/$inspection.txt" 2>&1; then
    probe_status=0
  else
    probe_status=$?
  fi
  printf '%s\t%s\n' "$inspection" "$probe_status" >> "$STATUS_FILE"
done
# Fail if receipt creation fails; nonzero probe statuses remain explicit partial evidence.
cat "$STATUS_FILE"

# 3c — Platform status page
curl -sf https://status.supabase.com/api/v2/status.json \
  | python3 -m json.tool > "$BUNDLE_DIR/platform-status.json" 2>/dev/null \
  || echo '{"error": "Could not reach status.supabase.com"}' > "$BUNDLE_DIR/platform-status.json"

# 3d — Partial example masking only; inspect and sanitize the candidate manually
find "$BUNDLE_DIR" -type f -exec sed -i \
  -e 's/eyJ[A-Za-z0-9_-]\{20,\}\(\.[A-Za-z0-9_-]*\)*/[JWT_REDACTED]/g' \
  -e 's/sbp_[A-Za-z0-9]\{20,\}/[SBP_KEY_REDACTED]/g' \
  -e 's/[A-Za-z0-9._%+-]\+@[A-Za-z0-9.-]\+\.[A-Za-z]\{2,\}/[EMAIL_REDACTED]/g' {} +

# 3e — Local candidate only; owner-reviewed minimization/sanitization required before sharing
tar czf "${BUNDLE_DIR}.tar.gz" "$BUNDLE_DIR"
echo "Debug bundle created: ${BUNDLE_DIR}.tar.gz"
echo "Contents:"
ls -lh "$BUNDLE_DIR"/
```

**What to check:** Inspect `inspect-status.tsv` first: a nonzero exit status means that inspection failed, even when an output file was archived. Treat the bundle as partial evidence. Cache ratios, estimated bloat, and sequential scans depend on workload, table size, measurement interval, and query plans; they do not by themselves establish memory pressure, a missing index, or a need for `VACUUM` or larger compute. Review approved baselines and execution plans before proposing separately authorized remediation.

## Output

The skill produces `supabase-debug-YYYYMMDD-HHMMSS.tar.gz` containing:

| File | Contents |
|------|----------|
| `cli-status.txt` | Local Supabase stack status (services, ports, URLs) |
| `table-sizes.txt` | All tables with row counts and disk usage |
| `index-usage.txt` | Index scan frequency — unused indexes are candidates for removal |
| `cache-hit.txt` | Buffer cache and index cache hit ratios |
| `seq-scans.txt` | Sequential-scan observations; not proof of missing indexes |
| `long-running-queries.txt` | Captured long-running-query inspection output; check its exit status |
| `bloat.txt` | Table and index bloat percentages |
| `replication-slots.txt` | Captured replication-slot inspection output; check its exit status |
| `inspect-status.tsv` | Per-inspection exit statuses; failures remain failed observations |
| `platform-status.json` | Published platform-status observation or explicit fetch error |

Plus the TypeScript diagnostics output (connectivity, auth, Realtime, Storage, RLS) printed to stdout.

The example masks only text matching its `eyJ...` token, `sbp_...`, and email patterns. It does not guarantee removal of `sb_secret_...` keys, other opaque credentials, SQL/query contents, personal data, or secrets embedded in arbitrary output. Review and minimize every included file, apply the required sanitization, and obtain owner approval for the resulting artifact before sharing. A generated archive is not a safe-to-share certification.

## Error Handling

| Symptom | Cause | Fix |
|---------|-------|-----|
| REST API returns `401` | Request identity or credential rejected; cause not established by status alone | Check the actual request, key type, and approved Auth evidence; rotate credentials only through a reviewed cutover |
| REST fetch throws or request times out | Transport, URL, availability, or intermediary failure | Record the exception/status actually observed (`fetch` has no HTTP `000` response); inspect approved network and project evidence |
| Realtime returns `CHANNEL_ERROR` | Channel subscription failed; cause unproven | Review approved identity, channel, network and service evidence; retain the failed observation and checked cleanup outcome |
| Realtime times out (5s) | No subscribed event within the probe window | Check cleanup and approved subscription/network/service evidence; timeout alone does not justify enabling replication or changing quotas |
| Storage `listBuckets` returns `403` | Requested operation denied; identity, grants, or Storage policy may differ | Check the actual credential and intended operation under approved access; do not switch to a privileged key or broaden policy to silence the denial |
| `supabase inspect db` fails | Target, credentials, connectivity, command support, or database permission may differ | Preserve the exact nonzero command receipt; verify the intended target and approved access before any linking or privilege change |
| Low observed cache-hit ratio | Workload, working set, measurement window, or query-plan effects | Compare approved workload baselines and plans; do not infer undersized compute or apply automatic remediation |
| RLS comparison counts match or differ | Inconclusive by itself | Review approved catalog evidence and multi-user fixture results before deciding whether policies are correct |
| `pg_stat_statements` unavailable | Extension availability, grants, schema, or query context may differ | Inspect approved catalog evidence; extension or privilege changes require separate review |

## Examples

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

**API endpoint test with curl:**

```bash
curl -s -o /dev/null -w "HTTP %{http_code} in %{time_total}s\n" \
  "https://<project-ref>.supabase.co/rest/v1/" \
  -H "apikey: $SUPABASE_ANON_KEY"
```

**Verify the current user from an approved running app's user client:**

```typescript
const { data: { user }, error } = await supabase.auth.getUser()
if (error || !user) console.log('No server-verified authenticated user', error?.code ?? null)
else console.log('Current user verified by Auth server')
```

This is a fresh user lookup, not a complete Auth-platform health check. Do not use an admin client's absence of a user session to diagnose an outage, and never include session tokens in the bundle.

## Resources

- [Supabase Troubleshooting Guide](https://supabase.com/docs/guides/platform/troubleshooting) — official first-stop for common issues
- [Database Inspect (CLI)](https://supabase.com/docs/guides/database/inspect) — `supabase inspect db` command reference
- [Supabase Status Page](https://status.supabase.com) — live platform health
- [Supabase Support](https://supabase.com/support) — file a ticket with your debug bundle attached
- [RLS Guide](https://supabase.com/docs/guides/database/postgres/row-level-security) — row-level security policy authoring
- [Realtime Quotas](https://supabase.com/docs/guides/realtime/quotas) — connection and message limits

## Next Steps

- Run `supabase-common-errors` to match diagnostic output against known issue patterns
- Run `supabase-rate-limits` if the bundle reveals 429 responses or throttled connections
- Run `supabase-performance-tuning` if cache hit ratios are below 99% or sequential scans are high
- Run `supabase-observability` to set up ongoing monitoring so issues surface before they become tickets
