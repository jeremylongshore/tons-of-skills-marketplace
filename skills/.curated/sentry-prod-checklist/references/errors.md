# Error Handling Reference

| Error | Cause | Solution |
|-------|-------|----------|
| `Source maps not working in prod` | Build artifact mismatch | Verify source maps from same build |
| `Debug output in prod` | Debug mode not disabled | Set `debug: false` explicitly |
| `Events not appearing` | Staging DSN in production | Verify production DSN is configured |
| `Alert storms` | Missing threshold configuration | Set appropriate alert thresholds |

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
