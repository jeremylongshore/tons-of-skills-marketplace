# Error Handling Reference

| Error | Cause | Solution |
|-------|-------|----------|
| `Events not appearing` | Multiple possible causes | Run diagnostic script, check DSN, verify network |
| `Source maps not resolving` | URL prefix mismatch | Use `sentry-cli sourcemaps explain` |
| `SDK version conflicts` | Mixed package versions | Ensure all @sentry packages match |
| `Memory leaks` | Unfinished transactions | Always use try/finally for transaction.finish() |

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
