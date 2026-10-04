# Error Handling Reference

| Error | Cause | Solution |
|-------|-------|----------|
| `Dev errors in prod dashboard` | Shared DSN | Use separate DSN per environment or disable in dev |
| `Environment filter not working` | Environment not set | Verify `environment` option in SDK init |
| `Staging alerts overwhelming` | Same alert rules as prod | Configure environment-specific alert conditions |
| `Sample rates inconsistent` | Hard-coded values | Use environment-based configuration object |

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
