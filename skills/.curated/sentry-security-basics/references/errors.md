# Error Handling Reference

| Error | Cause | Solution |
|-------|-------|----------|
| `PII in events` | Scrubbing rules incomplete | Add patterns to beforeSend and server rules |
| `DSN exposed in repo` | Hardcoded value | Move to environment variable immediately |
| `Unauthorized API access` | Token too permissive | Create scoped tokens with minimal permissions |
| `Audit log gaps` | Events not being tracked | Enable audit logging in organization settings |

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
