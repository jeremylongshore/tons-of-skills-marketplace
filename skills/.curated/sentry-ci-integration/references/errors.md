# Error Handling Reference

| Error | Cause | Solution |
|-------|-------|----------|
| `Authentication failed` | Invalid or expired token | Regenerate auth token in Sentry settings |
| `Release not found` | Release not created first | Run `sentry-cli releases new` before upload |
| `Source map upload failed` | Invalid file paths | Check `--url-prefix` matches actual URLs |
| `Permission denied` | Token missing scopes | Ensure token has `project:releases` scope |

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
