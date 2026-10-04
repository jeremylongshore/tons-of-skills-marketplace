# Error Handling Reference

| Error | Cause | Solution |
|-------|-------|----------|
| `High SDK overhead` | Too many integrations | Remove unused integrations |
| `Too many transactions` | Sampling rate too high | Use dynamic sampling based on endpoint |
| `Orphan spans` | Missing transaction context | Always create spans within transaction scope |
| `Memory leaks` | Unfinished transactions | Use try/finally to ensure finish() called |

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
