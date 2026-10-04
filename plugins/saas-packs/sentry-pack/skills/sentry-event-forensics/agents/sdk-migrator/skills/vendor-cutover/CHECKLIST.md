# vendor-cutover

**Owner:** `sentry-event-forensics` → `sdk-migrator`
Only when the user asked to switch from Rollbar, Bugsnag, or a similar vendor.
The concept map is not the procedure.

## Sequence

1. **Parallel run.** Send to both SDKs from one process. Tag Sentry events with `vendor_cutover=parallel` (a tag, not a new project, unless `key-boundary-mapper` already said the quota blast radius requires one). Do not turn the old vendor off the same day you set `tracesSampleRate: 1`.
2. **Alert parity.** List the pages the old vendor fires (new error, spike, regression). For each, say whether a Sentry alert rule exists. Do not invent rule ids. Missing rule = not ready.
3. **Test capture.** One event id in Sentry that you can quote. Until that exists, cutover has not started.
4. **Cutover.** Remove the old SDK init. Keep the Sentry release string stable across the cut so the first Sentry-only deploy is comparable.
5. **Watch the quota script** on `sentry-quota-leak-hunter` the week after. A double-write week can look like a Sentry outage or a bill spike. That is expected during parallel run and should drop after cutover. Do not "fix" it with `sampleRate: 0`.

## Concept map (reference only)

| Old idea | Sentry |
|---|---|
| Rollbar item / Bugsnag error | Issue (grouping is prospective; it will not merge history from the other vendor) |
| Deploy / revision | Release string, shared with CI |
| Person | `user` — PII rules still apply; do not turn on `sendDefaultPii` to mimic the old vendor |
| Source map upload in the old product | Debug ID inject + upload, owned by release-medic |

## Do not

- Delete the old vendor account as part of this checklist.
- Claim parity because both tabs are open.
