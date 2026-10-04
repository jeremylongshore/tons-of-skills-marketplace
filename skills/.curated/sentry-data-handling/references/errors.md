# Error Handling Reference

| Error | Cause | Solution |
|-------|-------|----------|
| `PII still appearing in events` | Scrubbing rules incomplete | Add patterns to `beforeSend` and server-side rules |
| `User deletion failed` | Invalid user ID | Verify user ID format matches Sentry records |
| `Data retention not applied` | Plan limitation | Check organization settings and plan features |
| `Consent tracking broken` | SDK initialized before consent | Use conditional DSN based on consent state |

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
