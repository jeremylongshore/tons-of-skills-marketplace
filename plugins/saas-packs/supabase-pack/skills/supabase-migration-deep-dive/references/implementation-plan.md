# Implementation Plan

## 1. Establish a Reviewed Migration Boundary

Install a reviewed compatible SDK version through the project's lockfile. The SDK
has no package-level `ping()` method. Validate configuration locally, then run a
separately authorized read against a known fixture table to test connectivity.
Never infer successful RLS or authentication from construction alone.

Record source/destination project identities, schema revision, approved fields,
retention rules, backup/restore evidence, and rollback ownership. Do not migrate
production data from an unreviewed shell one-liner.

## 2. Use Real Database Operations

This adapter assumes an existing `products(id, name)` schema with a unique `id` and
an explicitly authorized migration client. It accepts only the mapped fields and
checks the SDK's returned error. `create()` and `batchCreate()` are not generic
Supabase client methods.

```typescript
import type { SupabaseClient } from '@supabase/supabase-js';
type Product = { id: string; name: string };

export async function insertProducts(client: SupabaseClient, products: Product[]) {
  if (products.length === 0 || products.length > 100) throw new Error('Expected 1–100 rows');
  const rows = products.map(({ id, name }) => ({ id, name }));
  const { error } = await client.from('products').insert(rows);
  if (error) throw error;
  return { submitted: rows.length };
}
```

The receipt means the insert returned success, not that the whole migration is
complete. Do not blindly retry a timed-out insert. Reconcile immutable source IDs
against destination IDs before deciding whether to retry; choose upsert semantics
only after reviewing conflict keys and whether overwrites are authorized.

## 3. Batch, Reconcile, and Pause on Failure

Read the source with bounded stable pagination or a reviewed snapshot. Record each
batch's source IDs and checksum in protected migration evidence, not stdout. Stop
on any read/write/transform error; retain an explicit partial receipt rather than
silently skipping a failed batch. Compare counts, approved field checksums, RLS,
and representative reads before traffic shifts. Redact personal data from reports.

## 4. Shift Traffic Without Splitting an Identity's Writes

Use a persisted, deterministic tenant/user cohort assignment, not a fresh random
choice on every request. Define source of truth and write ownership per cohort,
reconciliation, a tested rollback boundary, and how already-written records are
handled. Restore schema/data only through a separately reviewed restore plan;
changing an application feature flag does not undo a data migration.

[Insert](https://supabase.com/docs/reference/javascript/insert)
[Upsert](https://supabase.com/docs/reference/javascript/upsert)
