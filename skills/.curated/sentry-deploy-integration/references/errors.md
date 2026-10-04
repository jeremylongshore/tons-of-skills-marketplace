# Error Handling Reference

| Error | Cause | Solution |
|-------|-------|----------|
| `Release not found` | Mismatched release names | Ensure SDK release matches CLI release |
| `Deploy notification failed` | Missing auth token | Verify SENTRY_AUTH_TOKEN is set |
| `Health metrics empty` | Session tracking disabled | Enable `autoSessionTracking: true` |
| `Rollback not reflected` | Old release not redeployed | Create new deploy notification for old version |

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
