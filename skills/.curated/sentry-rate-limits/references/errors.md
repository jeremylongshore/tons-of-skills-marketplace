# Error Handling Reference

| Error | Cause | Solution |
|-------|-------|----------|
| `429 Too Many Requests` | Rate limit exceeded | Implement client-side sampling |
| `Quota exhausted` | Event volume too high | Enable inbound filters and reduce sample rates |
| `Critical errors missed` | Over-aggressive filtering | Always capture fatal errors at 100% |
| `Billing spike` | Sudden traffic increase | Set up spend alerts and rate limits |

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
