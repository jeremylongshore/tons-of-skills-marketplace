# Data Handling Reference

## Classify Before Reading or Writing

Inventory the application's actual tables, buckets, Auth data, caches, queues,
backups, and external processors. Classify personal, credential, operational, and
public data; define purpose, authorized readers/writers, retention owner, and
deletion/export dependencies for each. Supabase has no generic `getUserData()` or
`deleteUser()` client method that discovers and processes this graph.

## Minimize Output Rather Than Logging Whole Responses

Use an explicit allowlist of operational fields. Regex PII detection is incomplete,
and replacing a few top-level keys does not sanitize nested objects, tokens, free
text, or arbitrary SDK error messages. Do not log request bodies or query results
under the label "redacted" merely because an email field was removed.

```typescript
export function operationSummary(operation: 'export' | 'inventory', count: number) {
  if (!Number.isSafeInteger(count) || count < 0) throw new Error('Invalid count');
  return { operation, count }; // no subject IDs, rows, keys, or paths
}
```

Read only approved columns under user-scoped RLS; `select('id, display_name')` is
column selection, not field-level authorization. Do not pass a service-role client
to ordinary request code or trust a caller-supplied subject ID.

## Retention Is an Application Decision

Document retention periods by data class and lawful purpose with the accountable
owner. "Audit logs seven years", "PII until a request", and "logs thirty days" are
not universal Supabase/GDPR/CCPA requirements. Apply legal holds, backup expiry,
processor obligations, and audit-access controls explicitly. Schedule cleanup only
after a reviewed inventory, dry-run counts, rollback limits, and authorization;
a cron expression alone does not establish safe retention enforcement.

## Export and Erasure Receipts

Use [the bounded inventory and erasure workflow](deletion-and-export.md). It checks
identity, paginates approved tables and nested Storage paths, stops on errors or
budgets, and explicitly reports partial scope. It does not delete Auth automatically
or certify complete erasure. An export must include approved object bytes and
reconcile concurrent changes before it can claim its declared scope is complete.

Keep receipt contents private. Record per-resource success/failure, remaining scope,
actor/operation authorization and retained exceptions; check the audit write itself.
Do not print personal data, swallowed error bodies, or export archives to stdout.

## Error Handling

| Situation                        | Required disposition                                                           |
| -------------------------------- | ------------------------------------------------------------------------------ |
| Read/delete denied or failed     | Explicit partial failure; do not finalize Auth deletion                        |
| Pagination budget exhausted      | Resume through a reviewed checkpoint or revise the budget; never call it empty |
| Concurrent changes               | Quiesce or reconcile against a defined cutoff                                  |
| External/backup copy not covered | Record remaining scope and retention owner                                     |
| Receipt persistence failed       | No success/compliance claim                                                    |

[Supabase data security](https://supabase.com/docs/guides/database/postgres/row-level-security)
[Storage access control](https://supabase.com/docs/guides/storage/security/access-control)
