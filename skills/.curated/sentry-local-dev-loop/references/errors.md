# Error Handling Reference

| Error | Cause | Solution |
|-------|-------|----------|
| `Debug output not showing` | Debug mode not enabled | Set `debug: true` in init options |
| `Events sent to production` | Wrong DSN configured | Check environment-specific DSN is loaded |
| `Too many events in dev` | High sample rate | Set `enabled: false` for development |
| `Test events in prod dashboard` | Shared DSN across envs | Use separate Sentry projects per environment |

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
