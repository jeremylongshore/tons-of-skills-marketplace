# Error Handling Reference

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Missing SUPABASE_URL or SUPABASE_ANON_KEY` | Environment variables not set | Check `.env` file and ensure variables are loaded |
| `new row violates row-level security policy` | RLS blocks the operation | Check role grants, verified identity, and the trusted membership row |
| Empty tenant result | Membership or matching rows absent | Inspect trusted membership provisioning; do not manufacture a JWT claim |
| `relation "public.audit_log" does not exist` | Audit migration not applied | Run `supabase db push` or `supabase db reset` |
| `permission denied for function claim_next_job` | Missing execute grant | Run `grant execute on function claim_next_job to authenticated` |
| `Cross-project profile lookup failed` | Wrong service_role key for the target project | Verify `MAIN_SUPABASE_SERVICE_ROLE_KEY` matches the main project |
| `TypeError: Cannot read properties of null` | Client singleton not initialized | Ensure env vars are available before first `getSupabaseClient()` call |
| `cron.schedule: permission denied` | `pg_cron` extension not enabled | Enable via dashboard: Database > Extensions > pg_cron |

## RLS Debugging Checklist

1. Check RLS is enabled on tenants, tenant_members, and projects.
2. Confirm authenticated has SELECT only and anon and PUBLIC have no table grants in this read-only example; audit other policies and PUBLIC grants.
3. Verify identity with the request-scoped user client; user-editable metadata is not authorization.
4. Test two ordinary users with disjoint memberships, a nonmember, and unauthenticated requests. Confirm membership writes are denied and the self-membership policy does not recurse.
5. Run scoped project reads through the Data API as the user; owner/admin SQL sessions can bypass RLS and are not isolation evidence. Application writes need separately reviewed policies.

See [RLS authorization and helper semantics](https://supabase.com/docs/guides/database/postgres/row-level-security).

## Cross-Project Access Troubleshooting

- **401 Unauthorized**: The `service_role` key is wrong or belongs to a different project
- **Network timeout**: Cross-region calls add latency; consider caching or co-locating projects
- **Rate limited**: Supabase enforces per-project rate limits; distribute load across projects
- **Type mismatch**: Regenerate types for both projects after schema changes
