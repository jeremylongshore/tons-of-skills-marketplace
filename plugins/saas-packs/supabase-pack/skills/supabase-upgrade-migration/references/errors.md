# Upgrade error handling

| Observation | Required response |
| --- | --- |
| Package runtime constraints reject installation | Check the exact selected version's published metadata; choose a reviewed compatible runtime/version pair. Do not assume all SDK majors share a fixed API date or runtime floor. |
| Type generator exits nonzero after partial output | Preserve the existing types file, discard only the owned temporary candidate, retain the failure status and diagnose the actual error. |
| Type generator succeeds with empty output | Refuse replacement and keep the previous file; empty output is not successful schema discovery. |
| Generated types fail application typecheck | Review schema/SDK/application differences and restore the prior artifact if needed; successful generation alone does not prove compatibility. |
| Auth operation reports a missing session | Inspect the actual operation and client scope; handle the intended unauthenticated case without escalating to an administrative key. |
| Tests pass after SDK downgrade | This proves only the checks run; it does not roll back database migrations, policies, credentials or hosted configuration. |

Use the [main upgrade workflow](../SKILL.md) and the [reviewed rollback boundary](examples.md#rollback-is-a-reviewed-dependency-and-application-change).
No static SDK-major/API-date matrix is maintained here: use evidence for the exact
package versions under review.
