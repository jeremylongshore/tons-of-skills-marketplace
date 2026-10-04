# Error Handling Reference

## Common Migration Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Error count mismatch (>10% delta) | Sampling rates differ between tools | Set both to `sampleRate: 1.0` during parallel run; restore tuned rate after cutover |
| Missing stack traces in Sentry | Source maps not uploaded for the release | Add `sentry-cli sourcemaps upload --release=$(npm pkg get version) dist/` to CI pipeline |
| `beforeSend` dropping events | Filter logic too aggressive during migration | Log dropped events to console during parallel run to verify filter correctness |
| Alert parity issues | Old tool uses count-based alerts, Sentry uses different thresholds | Map each alert individually; test with synthetic errors before going live |
| Sentry events missing user context | `setUser()` called after `captureException()` | Call `Sentry.setUser()` in authentication middleware, before any error capture |
| Breadcrumbs not appearing | Breadcrumb added after exception capture | Breadcrumbs must be added before the error occurs; they attach to the next captured event |
| Data export from old tool fails | API rate limiting on historical data export | Use pagination with 100-item batches and exponential backoff |
| Old SDK references in CI config | Only searched application code, not CI/CD files | Grep across `*.yml`, `*.yaml`, `Dockerfile`, and environment variable stores |
| Team cannot find issues in Sentry | Different UI navigation from old tool | Schedule a 30-minute walkthrough; share saved searches for common filters |
| Rollback needed mid-migration | Sentry capturing fewer errors than expected | Re-enable dual-reporter; old tool config preserved in `migration-backup/` directory |

## Validation Checklist

Run this checklist before removing the old tool:

- [ ] Error counts within 10% between old tool and Sentry (24h window)
- [ ] Stack traces resolve with correct file names and line numbers
- [ ] User context (id, email) appears on Sentry events
- [ ] Breadcrumbs appear in event detail timeline
- [ ] All alert rules fire correctly (tested with synthetic errors)
- [ ] Release tracking shows deploy markers in Sentry Releases view
- [ ] Performance traces appear (if `tracesSampleRate > 0`)
- [ ] Source maps uploaded in CI for every deploy
- [ ] Team has completed Sentry dashboard walkthrough

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
