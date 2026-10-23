# Authorized Inventory, Export, and Erasure

This is a bounded application-data inventory, not an implementation or certification
of legal compliance or complete erasure. Before any export or deletion, verify the
requester's identity with the request-scoped user client's `auth.getUser()`, derive
the subject from that identity (not a posted user ID), and separately authorize
eligibility, retention/legal holds, shared ownership, and delivery. Admin-assisted
requests need their own reviewed authorization route; do not pass arbitrary IDs to
a service-role helper.

## Read-Only, Paginated Partial Inventory

The following example assumes approved application tables `profiles` and `documents`
with unique sortable `id`, `user_id`, and the selected columns; it does not discover
all personal data. The approved private bucket is `user-files`, with ownership
convention `users/<verified user UUID>/`. Its policies must enforce that boundary.
Use the request-scoped user client, never an admin client supplied by a caller.
The per-table/per-folder limits are application budgets, not Supabase quotas.

```typescript
import type { SupabaseClient } from '@supabase/supabase-js';

export async function inventoryOwnData(client: SupabaseClient) {
  const {
    data: { user },
    error: authError,
  } = await client.auth.getUser();
  if (authError || !user || !/^[0-9a-f-]{36}$/i.test(user.id)) {
    throw new Error('Verified subject required');
  }
  const receipt = {
    subjectId: user.id,
    scope: 'profiles, documents; user-files/users/<subject>; inventory only',
    enumerationFinished: false,
    completeErasure: false,
    authDeleted: false,
    rows: {} as Record<string, unknown[]>,
    objects: [] as string[],
    failures: [] as string[],
  };
  const pageSize = 100;
  try {
    for (const [table, columns] of [
      ['profiles', 'id, user_id, display_name'],
      ['documents', 'id, user_id, title'],
    ]) {
      receipt.rows[table] = [];
      let ended = false;
      for (let page = 0; page < 100; page++) {
        const { data, error } = await client
          .from(table)
          .select(columns)
          .eq('user_id', user.id)
          .order('id')
          .range(page * pageSize, (page + 1) * pageSize - 1);
        if (error || !Array.isArray(data)) throw new Error(`Table inventory failed: ${table}`);
        receipt.rows[table].push(...data);
        if (data.length < pageSize) {
          ended = true;
          break;
        }
      }
      if (!ended) throw new Error(`Table page budget exhausted: ${table}`);
    }
    const root = `users/${user.id}`;
    const folders = [root];
    const visited = new Set<string>();
    let calls = 0;
    while (folders.length) {
      const folder = folders.shift()!;
      if (visited.has(folder)) throw new Error('Repeated folder');
      visited.add(folder);
      let ended = false;
      for (let offset = 0; offset < 10_000; offset += pageSize) {
        if (++calls > 200) throw new Error('Storage call budget exhausted');
        const { data, error } = await client.storage.from('user-files').list(folder, {
          limit: pageSize,
          offset,
          sortBy: { column: 'name', order: 'asc' },
        });
        if (error || !Array.isArray(data)) throw new Error('Storage inventory failed');
        for (const item of data) {
          if (
            typeof item.name !== 'string' ||
            !item.name ||
            item.name === '.' ||
            item.name === '..' ||
            /[\\/\0]/.test(item.name)
          ) {
            throw new Error('Invalid storage entry');
          }
          const path = `${folder}/${item.name}`;
          if (item.id === null) {
            if (visited.size + folders.length >= 100) throw new Error('Folder budget exhausted');
            folders.push(path);
          } else if (typeof item.id === 'string') {
            receipt.objects.push(path);
          } else throw new Error('Invalid storage entry type');
        }
        if (data.length < pageSize) {
          ended = true;
          break;
        }
      }
      if (!ended) throw new Error('Storage page budget exhausted');
    }
    receipt.enumerationFinished = true;
  } catch (error) {
    receipt.failures.push(error instanceof Error ? error.message : 'Inventory failed');
  }
  return receipt;
}
```

A failure or exhausted budget returns `enumerationFinished: false` with only the
already-read subset. A successful enumeration is still not a consistent snapshot:
concurrent writes/deletes, RLS visibility, unlisted tables/buckets, external copies,
Auth records, object bytes, backups, and third-party systems remain outside scope.
Do not call it a complete DSAR export. For an approved export, establish a snapshot
or reconciliation cutoff, download every approved object with checked errors, and
verify counts/checksums in a protected delivery receipt. Never log or publicly serve
the returned rows/paths; authorized delivery needs a short-lived private channel.

## Separately Authorized Erasure Procedure

1. Record approved subject, actor, eligibility, retention exceptions, resource scope,
   and immutable operation ID in protected evidence. Quiesce relevant writes or
   design reconciliation; obtain the inventory before deleting while paginating.
2. Delete only approved table rows in reviewed foreign-key order. Check every
   returned error and record each resource's outcome. Do not treat missing tables,
   denied policies, timeouts, or zero visible rows as proof of erasure.
3. Remove enumerated objects in bounded batches through Storage `remove()`, checking
   all results; do not delete Storage metadata directly. Re-enumerate to detect
   concurrent additions and distinguish a budget stop from empty completion.
4. Stop or record explicit partial state on any failure. Do not automatically call
   `auth.admin.deleteUser()` after partial cleanup. Auth deletion is a separate
   server-only, freshly authorized finalization after eligibility and all approved
   dependencies are reconciled, including Storage ownership constraints.
5. Persist a checked, minimal receipt with unresolved systems/retention exceptions,
   not an unconditional `completedAt`/`success: true`. An audit-write failure also
   prevents a success receipt. Auth deletion is not proof of immediate invalidation
   of every issued JWT, nor of removal from backups or downstream systems.

No destructive helper or admin finalization is executed by this reference. Do not
replace the review requirements with a fabricated `getUserData()` / `deleteUser()`
SDK method. Determine legal retention and audit access with the accountable owner;
there is no universal seven-year or never-delete rule supplied here.

[Storage listing](https://supabase.com/docs/reference/javascript/storage-from-list)
[Storage removal](https://supabase.com/docs/reference/javascript/storage-from-remove)
[Admin user deletion](https://supabase.com/docs/reference/javascript/auth-admin-deleteuser)
[User management](https://supabase.com/docs/guides/auth/managing-user-data)
