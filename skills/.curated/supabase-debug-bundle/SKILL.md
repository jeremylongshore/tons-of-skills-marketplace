---
name: supabase-debug-bundle
description: 'Collect Supabase diagnostic info for troubleshooting and support tickets.

  Use when debugging connection failures, auth issues, Realtime drops, Storage

  errors, RLS misconfigurations, or preparing a support escalation.

  Trigger with "supabase debug", "supabase diagnostics", "supabase support bundle",

  "collect supabase logs", "debug supabase connection".

  '
allowed-tools: Read, Grep, Glob, Bash(node --version:*), Bash(npm list:*)
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
./node_modules/.bin/supabase --version
npm list @supabase/supabase-js
```

## Prerequisites

- **Node.js 22+** with `@supabase/supabase-js` v2 installed in the project
- **Supabase CLI** already installed at the project's reviewed version; do not download a CLI as part of evidence collection
- **Environment variables** set: `SUPABASE_URL` and the intended legacy `SUPABASE_ANON_KEY` for these examples. An admin key is optional and only used for a separately approved comparison; ordinary probes must not inherit it
- Project linked and target verified before approved CLI diagnostics
- An explicitly approved existing diagnostic table with an `id` column, selected through `SUPABASE_DIAGNOSTIC_TABLE`; no automatic table discovery or creation

## Instructions

Use Glob to locate only approved evidence files, Read to inspect their contents, and Grep to check for sensitive fields before including them. Exclude credential files, shell history and unrelated logs. CLI, network and archive commands follow the session's normal permission flow; the default shell grants cover version inventory only.

### Step 1: Gather Environment and Connectivity

Collect SDK version, project URL, key type, and test basic connectivity against the REST and Auth endpoints.

```typescript
import { createClient } from '@supabase/supabase-js'

const url = process.env.SUPABASE_URL!
const anonKey = process.env.SUPABASE_ANON_KEY!
const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY

// Ordinary probes never escalate merely because an admin key is present.
const keyType = 'anon'
const supabase = createClient(url, anonKey, {
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
// Set the approval flag only after explicit approval for this admin comparison.
if (process.env.SUPABASE_DIAGNOSTIC_ADMIN_APPROVED === '1' && serviceKey && probeTable) {
  const adminClient = createClient(url, serviceKey, {
    auth: { autoRefreshToken: false, persistSession: false },
  })
  const anonClient = createClient(url, anonKey, {
    auth: { autoRefreshToken: false, persistSession: false },
  })
  const [anonResult, adminResult] = await Promise.all([
    anonClient.from(probeTable).select('id', { count: 'exact', head: true }),
    adminClient.from(probeTable).select('id', { count: 'exact', head: true }),
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
  diagnostics.rls_comparison = { status: 'not_run', detail: 'Requires approved table and separately approved admin comparison' }
}
```

**What to check:** Realtime should reach `SUBSCRIBED` within 5 seconds. Storage should list buckets without error. Equal or different counts are inconclusive: empty tables, grants, data, and policy scope can all affect results. Separately authorize SQL catalog inspection and seeded multi-user access tests; `information_schema` is not assumed to be exposed as a Data API table.

### Step 3: Collect Database Health and Package the Bundle

Collect only approved database statistics and platform-status evidence. The Bash script below creates a private local candidate archive on a POSIX filesystem. It does not sanitize arbitrary output or approve export. Confirm the target and installed CLI commands before running it; never include `.env`, raw CLI status, session tokens or home-directory log globs.

```bash
#!/bin/bash
set -euo pipefail
umask 077

# Unique owner-only directory, even if the caller has a permissive umask.
BUNDLE_DIR=$(mktemp -d "${TMPDIR:-/tmp}/supabase-debug.XXXXXX")

# 3a — Record CLI version only; raw status can disclose credentials.
if ./node_modules/.bin/supabase --version > "$BUNDLE_DIR/cli-version.txt" 2>&1; then
  version_status=0
else
  version_status=$?
fi
printf 'cli-version\t%s\n' "$version_status" > "$BUNDLE_DIR/version-status.tsv"

# 3b — Approved database inspections; preserve individual exit statuses.
# A captured output file can contain an error, not a successful observation.
STATUS_FILE="$BUNDLE_DIR/inspect-status.tsv"
printf 'inspection\texit_status\n' > "$STATUS_FILE"
for inspection in table-sizes index-usage cache-hit seq-scans long-running-queries bloat replication-slots; do
  if ./node_modules/.bin/supabase inspect db "$inspection" > "$BUNDLE_DIR/$inspection.txt" 2>&1; then
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

# 3d — Unreviewed candidate: raw output may still contain sensitive data.
printf '%s\n' 'UNREVIEWED: minimize and sanitize every file before sharing.' > "$BUNDLE_DIR/REVIEW-REQUIRED.txt"
tar -czf "${BUNDLE_DIR}.tar.gz" -C "$BUNDLE_DIR" .
printf 'Private candidate archive: %s\n' "${BUNDLE_DIR}.tar.gz"
printf 'Private evidence directory: %s\n' "$BUNDLE_DIR"
```

**What to check:** Inspect `inspect-status.tsv` first: a nonzero exit status means that inspection failed, even when an output file was archived. Treat the bundle as partial evidence. Cache ratios, estimated bloat, and sequential scans depend on workload, table size, measurement interval, and query plans; they do not by themselves establish memory pressure, a missing index, or a need for `VACUUM` or larger compute. Review approved baselines and execution plans before proposing separately authorized remediation.

## Output

The skill produces a uniquely named `supabase-debug.XXXXXX.tar.gz` candidate beside an owner-only evidence directory under the selected temporary directory. On a POSIX filesystem, new files/archive are mode 0600 and the directory is 0700. Verify permissions and storage policy on the actual host; shared identities or filesystem ACLs require separate review. The candidate contains:

| File | Contents |
|------|----------|
| `cli-version.txt` | Captured CLI version output or error; check the version receipt |
| `version-status.tsv` | Version-command exit status |
| `REVIEW-REQUIRED.txt` | Explicit unreviewed-artifact marker |
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

No regex pass can certify arbitrary diagnostic output as safe. Error messages, SQL text, object names, URLs and stack traces may contain credentials or personal data. Build a separate minimized, sanitized export from the private candidate and obtain owner review of its exact contents before sharing. Never archive `.env` or infer that replacing text after `=` handles multiline secrets. Keep the private source and candidate local under the approved retention policy; do not upload them automatically. See the [collection boundary](references/implementation.md), [review examples](references/examples.md) and [failure handling](references/errors.md).

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

See the [approved-scope probe examples](references/examples.md) for a bounded table query and server-verified user lookup. A successful request establishes only that observation; failures and missing sessions remain explicit. Review the [collection boundary](references/implementation.md) before building an export.

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
