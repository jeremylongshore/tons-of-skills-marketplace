# Error Handling Reference

| Error | Cause | Solution |
|-------|-------|----------|
| `No transactions in dashboard` | `tracesSampleRate` is 0 | Set sample rate > 0 |
| `Spans not linked to transactions` | Missing scope configuration | Use `configureScope` to set current span |
| `Distributed trace broken` | Missing headers | Ensure `sentry-trace` and `baggage` headers propagate |
| `Performance tab empty` | Plan doesn't include performance | Upgrade Sentry plan or enable performance feature |

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
