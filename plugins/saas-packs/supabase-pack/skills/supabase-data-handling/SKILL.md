---
name: supabase-data-handling
description: |
  Implement GDPR/CCPA compliance with Supabase: RLS for data isolation, user
  deletion via auth.admin.deleteUser(), data export via SQL, PII column
  management, backup/restore workflows, and retention policies.
  Use when handling sensitive data, implementing right-to-deletion, configuring
  data retention, or auditing PII in Supabase database columns.
  Trigger with: "supabase GDPR", "supabase data handling", "supabase PII",
  "supabase compliance", "supabase data retention", "supabase delete user",
  "supabase data export".
allowed-tools: Read, Write, Edit, Bash(npx supabase:*), Bash(supabase:*), Bash(psql:*),
  Grep, Glob
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- supabase
- gdpr
- ccpa
- compliance
- data-handling
- privacy
compatibility: Designed for Claude Code
---
# Supabase Data Handling

## Overview

Plan data access, erasure, retention, and recovery with explicit authorization and partial-operation receipts. RLS, application cleanup, Storage ownership, Auth administration, and backups are separate boundaries. These examples do not establish legal compliance, complete discovery, atomic erasure, or immediate session revocation.

**When to use:** Implement GDPR right-to-deletion, respond to data subject access requests (DSARs), audit PII in the database, configure automated retention, set up tenant isolation with RLS, or plan backup/restore procedures.

## Prerequisites

- `@supabase/supabase-js` v2+ with service role key for admin operations
- Verify current `pg_cron` extension availability separately from the project’s backup/PITR plan or add-on entitlement; neither implies the other
- Understanding of GDPR Articles 15-17 (access, rectification, erasure)
- Database access via SQL Editor or `psql` for schema changes

## Instructions

### Step 1: RLS for Data Isolation and PII Column Management

Enable RLS on every table holding user data, then classify PII columns so later deletion and export steps know what to touch. The RLS skeleton is one `USING (auth.uid() = ...)` policy per access pattern:

```sql
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users_read_own_profile" ON public.profiles
  FOR SELECT USING (auth.uid() = id);
```

Pair the policies with a PII audit — an `information_schema.columns` scan by naming pattern, `COMMENT ON COLUMN` tags, a `pii_registry` view, and an SDK-side regex scanner for emails, phones, SSNs, and IPs.

See [RLS and PII reference](references/rls-and-pii.md) for the full multi-tenant policy set, the PII audit SQL, the `pii_registry` view, and the `scanTableForPII()` SDK scanner.

### Step 2: User Deletion and Data Export

Start with a read-only, user-scoped inventory. The caller supplies a request session, not a target user ID. A public-key client forwards that session and verifies it with Auth; RLS and reviewed table grants still determine access.

```typescript
import { createClient } from '@supabase/supabase-js';

async function inventoryOwnProfile(request: Request) {
  const authorization = request.headers.get('authorization');
  if (!authorization?.startsWith('Bearer ')) throw new Error('Authentication required');
  const client = createClient(url, publishableKey, {
    global: { headers: { Authorization: authorization } },
    auth: { persistSession: false, autoRefreshToken: false },
  });
  const { data: { user }, error: authError } = await client.auth.getUser();
  if (authError || !user) throw new Error('User verification failed');
  const { data, error } = await client.from('profiles')
    .select('id').eq('id', user.id).limit(1);
  if (error || !Array.isArray(data)) throw new Error('Profile inventory failed');
  return { status: 'partial_inventory', profile_rows: data.length,
    deletion_started: false, complete_export: false };
}
```

This observes only the reviewed profile projection, not every table, object, backup, or processor. Do not log row contents or credentials; expose results only to the authorized subject with private, no-store responses. A zero-row result does not authorize creating or deleting anything.

Before any erasure, separately review application-owned eligibility, verified subject binding, retention/legal holds, schema cascades, Storage ownership, and ordered cleanup. Persist minimized per-step receipts and retry/idempotency state. Auth finalization is a separate privileged operation only after required cleanup is verified; partial failure remains partial, and existing JWTs may survive until expiry. Export similarly needs an approved table/object inventory, authorization, minimization, and protected delivery rather than a blanket completeness claim.

See [deletion and export reference](references/deletion-and-export.md) for the bounded plan and partial-receipt limitations. No destructive endpoint is supplied here.

### Step 3: Retention Policies and Backup/Restore

See [retention policies and backup/restore](references/retention-and-backup.md) for `pg_cron` automated retention schedules (30/90/730-day tiers), SDK-based retention monitoring, `pg_dump`/`pg_restore` commands, and point-in-time recovery configuration.

## Output

The reviewed output is an access-policy and PII inventory, a partial user-scoped observation, and an explicit erasure/export/retention/recovery plan. Pattern scans can miss sensitive values. Record which tables, objects, identities, operations, and failure paths were actually covered; do not label a partial result compliant, complete, immutable, or successfully erased without independent evidence.

## Error Handling

| Error | Cause | Solution |
| ------- | ------- | ---------- |
| `auth.admin.deleteUser()` returns 404 | User already deleted or wrong ID | Check `auth.users` table; may have been deleted by another process |
| `violates foreign key constraint` during deletion | Child rows reference user | Delete in cascade order (comments → orders → profiles) or use `ON DELETE CASCADE` |
| `permission denied for function cron.schedule` | Extension or caller privilege mismatch | Verify current extension availability and approved scheduling role separately from PITR entitlement |
| `pg_dump: connection refused` | Using wrong port or pooler URL | Use direct connection (port 5432), not pooler (port 6543) for `pg_dump` |
| Approved operation denied | Grants, identity, policy, or eligibility mismatch | Inspect the actual boundary; do not switch to a service-role client to silence the denial |
| Audit receipt missing | Write failed or logging design incomplete | Preserve partial status and investigate approved receipt authorization; do not broaden privileges blindly |
| Retention job not running | `pg_cron` job disabled or errored | Check `cron.job_run_details` for error messages |

## Examples

**Example 1 — Review an erasure request:**

Run the authenticated read-only inventory above, then record the requested scope and review eligibility, required cleanup, partial-failure recovery, and protected evidence delivery before approving any mutation. Applicable legal obligations and deadlines require the organization’s qualified review; this skill does not determine them.

**Example 2 — Quick PII audit:**

```sql
-- Count rows with email-like patterns in unexpected columns
SELECT 'profiles' AS table_name, 'bio' AS column_name, count(*) AS rows_with_email
FROM public.profiles
WHERE bio ~ '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}';
```

**Example 3 — Verify retention job execution:**

```sql
-- Separately approved operator metadata observation; inspect only reviewed jobs.
-- Run only if pg_cron is installed and the operator is authorized to read it.
SELECT jobid, status, start_time, end_time
FROM cron.job_run_details
ORDER BY start_time DESC
LIMIT 20;
```

A scheduler receipt alone does not establish successful cleanup or policy compliance. Inspect approved operation receipts and errors separately.

## Resources

- [Row Level Security — Supabase Docs](https://supabase.com/docs/guides/database/postgres/row-level-security)
- [Auth Admin deleteUser — Supabase Docs](https://supabase.com/docs/reference/javascript/auth-admin-deleteuser)
- [Database Backups — Supabase Docs](https://supabase.com/docs/guides/platform/backups)
- [pg_cron Extension — Supabase Docs](https://supabase.com/docs/guides/database/extensions/pg_cron)
- [CCPA Compliance Guide](https://oag.ca.gov/privacy/ccpa)

## Next Steps

- For enterprise role-based access control, see `supabase-enterprise-rbac`
- For security hardening and API key scoping, see `supabase-security-basics`
- For observability and audit trail monitoring, see `supabase-observability`
