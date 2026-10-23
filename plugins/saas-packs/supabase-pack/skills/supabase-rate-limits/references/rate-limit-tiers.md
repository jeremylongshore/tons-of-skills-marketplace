# Rate Limits and Quotas by Surface

Reviewed 2026-10-22 against the linked hosted-platform documentation. Limits are
surface-specific, mutable, and may depend on project settings or contract. There
is no supported universal Free/Pro Data API RPM/RPD table here, and Enterprise is
not an unconditional promise of unlimited requests.

| Surface                   | Check before sizing                                                                               |
| ------------------------- | ------------------------------------------------------------------------------------------------- |
| Auth                      | Endpoint-specific limits, IP/user/project basis, email-provider limits, and project Auth settings |
| Database API              | Query cost, timeouts, connection/compute capacity, and application admission limits               |
| Storage                   | Bucket upload limit, plan storage/egress allowances, and upload transport                         |
| Realtime                  | Project connection/message/join limits and configured allowances                                  |
| Edge Functions            | CPU, worker duration, request timeout, memory, and invocation allowances separately               |
| Direct Postgres/Supavisor | Compute-specific connection and pool limits, mode, and application pool budget                    |

The current [hosted Edge Functions limits](https://supabase.com/docs/guides/functions/limits)
list 2 seconds of CPU per request and worker wall-clock duration of 150 seconds
on Free or 400 seconds on paid plans. Waiting on I/O is not CPU time; a worker's
lifetime is not an individual request's guaranteed completion budget. The request
idle timeout is separately documented. Recheck before deployment, and set a lower
application deadline appropriate to the operation.

Use measured load and an explicit application budget; do not derive a global API
rate from plan included billing quantities. Handle an actual 429 according to the
surface's documented response, with bounded backoff and a deadline. Do not retry
non-idempotent mutations merely because a response was throttled or lost.

[Auth limits](https://supabase.com/docs/guides/auth/rate-limits)
[Realtime limits](https://supabase.com/docs/guides/realtime/limits)
[Storage upload limits](https://supabase.com/docs/guides/storage/uploads/file-limits)
[Database connections](https://supabase.com/docs/guides/database/connecting-to-postgres)
[Pricing](https://supabase.com/pricing)
