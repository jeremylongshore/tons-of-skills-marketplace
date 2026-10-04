# Examples

**Example 1: Prepare Support Ticket (TypeScript)**
Request: "Create debug bundle for Sentry support ticket"
Result: Runs `sentry-diagnostics.ts` collecting SDK version, configuration (DSN redacted), integration list, test event ID with flush confirmation, and network connectivity status. Outputs `sentry-debug-YYYYMMDD-HHMMSS.md` ready to attach to support request.

**Example 2: Diagnose Missing Events (Python)**
Request: "Why are my Sentry errors not showing up?"
Result: Runs `sentry_diagnostics.py` to check client initialization, inspect `before_send` hook for dropped events, verify DSN connectivity, confirm sample rate is non-zero, and test event delivery with explicit flush.

**Example 3: Debug Source Map Resolution**
Request: "Source maps not working in Sentry"
Result: Runs `sentry-cli sourcemaps explain --org ORG --project PROJ EVENT_ID` to diagnose URL prefix mismatches, lists uploaded release artifacts, and validates local source maps with `--dry-run`.

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
