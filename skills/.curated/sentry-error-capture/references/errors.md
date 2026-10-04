# Error Handling Reference

| Error | Cause | Solution |
|-------|-------|----------|
| `Missing event ID` | Capture failed silently | Enable `debug: true` to see SDK logs |
| `User context not appearing` | User set after capture | Call `setUser()` before `captureException()` |
| `Tags not filterable` | Invalid tag format | Use string values only, no nested objects |
| `Breadcrumbs missing` | Integration disabled | Verify Breadcrumbs integration is enabled |

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
