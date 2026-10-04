# Error Handling Reference

| Error | Cause | Solution |
|-------|-------|----------|
| Event not appearing | DSN misconfigured | Verify DSN in project settings |
| Delayed events | Network latency | Wait 30-60 seconds, check again |
| Missing stack trace | Source maps not uploaded | Configure source map uploads |
| No user context | setUser not called | Add Sentry.setUser() before capture |

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
