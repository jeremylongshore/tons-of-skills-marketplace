# Error Handling Reference

## Authentication Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `error: API request failed: 401` | Auth token invalid or expired | Regenerate at sentry.io/settings/auth-tokens/ with `project:releases` + `org:read` scopes |
| `error: API request failed: 403` | Token lacks required scope | Ensure token has `project:releases` scope; add `org:read` for commit association |
| `SENTRY_AUTH_TOKEN not set` | Environment variable missing | Export `SENTRY_AUTH_TOKEN` or pass `--auth-token` flag |

## Commit Association Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `No commits found` with `--auto` | GitHub/GitLab integration not installed | Install at Settings > Integrations > GitHub, grant repo access |
| `Repository not found` | Repo slug mismatch between Sentry and VCS | Check `sentry-cli repos list` output matches your org/repo slug |
| `Failed to set commits` | Shallow clone in CI (`fetch-depth: 1`) | Use `fetch-depth: 0` in checkout to get full git history |
| `Could not determine any commits` | No previous release exists for baseline | First release has no commits — this is normal, subsequent releases will show diffs |

## Source Map Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Stack traces show minified code | Source maps uploaded after errors occurred | Upload source maps **before** deploying — Sentry does not retroactively apply them |
| `Could not find source map` | `--url-prefix` does not match script URL | Compare with browser DevTools Network tab; `~/` is a wildcard for scheme+host |
| `Source map validation failed` | Map file references wrong source file | Check `sources` array in `.map` file; rebuild with correct `sourceRoot` |
| `Upload failed: 413` | Source map file too large (>40MB) | Split bundles or use code splitting to reduce individual map file sizes |
| `No files to upload` | Wrong path or glob pattern | Verify `./dist` contains `.js.map` files; check `--ext` flag if using non-standard extensions |

## Release Lifecycle Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Release already exists` | Re-creating existing release | Non-fatal warning; update with `set-commits` and `sourcemaps upload` instead |
| `Release not found` in SDK events | `Sentry.init({ release })` mismatch | Print both values; they must be identical (case-sensitive, including prefix like `my-app@`) |
| Release health not appearing | `autoSessionTracking` disabled | Set `autoSessionTracking: true` in SDK init; verify in browser SDK it defaults to `true` |
| `Cannot delete release with active deploys` | Trying to delete deployed release | Remove deploy records first, or archive instead of deleting |

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
