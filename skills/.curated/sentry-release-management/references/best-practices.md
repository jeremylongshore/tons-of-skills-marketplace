# Best Practices

## Release Naming Conventions

```bash
# Good: Predictable, traceable, unique
release: "my-app@2.1.0"           # Semver — matches package.json
release: "my-app@a1b2c3d"         # Short SHA — ties to exact commit
release: "my-app@2.1.0+a1b2c3d"   # Combined — version + commit

# Bad: Ambiguous, not traceable
release: "latest"                  # Overwritten every deploy
release: "production"              # No version info
release: "v2"                      # Too vague
```

## Source Map Upload

- **Upload before deploy** — Sentry does not retroactively apply source maps to existing events
- **Use `--validate`** — catches malformed maps before they reach Sentry
- **Delete maps from production** — source maps expose original source; use `filesToDeleteAfterUpload` in build plugins
- **Match `--url-prefix`** — compare against actual script URLs in browser DevTools Network tab

```bash
# Validate before uploading
sentry-cli sourcemaps upload \
  --release="$VERSION" \
  --url-prefix="~/static/js" \
  --validate \
  --dry-run \
  ./dist
```

## Release Health Monitoring

- **Target > 99.5% crash-free rate** — investigate if it drops below this
- **Watch adoption** — if adoption is low, your deploy may not have rolled out fully
- **Enable session tracking** — release health requires `autoSessionTracking: true` in the SDK
- **Compare releases** — use the Sentry UI to compare crash-free rates between consecutive releases

## CI/CD Integration

```bash
#!/bin/bash
# scripts/sentry-release.sh — idempotent release script
set -euo pipefail

VERSION="${1:-my-app@$(node -p "require('./package.json').version")}"
ENVIRONMENT="${2:-production}"

sentry-cli releases new "$VERSION"
sentry-cli releases set-commits "$VERSION" --auto
sentry-cli sourcemaps upload \
  --release="$VERSION" \
  --url-prefix="~/static/js" \
  --validate \
  ./dist
sentry-cli releases finalize "$VERSION"
sentry-cli releases deploys "$VERSION" new --env "$ENVIRONMENT"

echo "Sentry release $VERSION → $ENVIRONMENT complete"
```

## Cleanup Strategy

```bash
# Delete source maps from old releases to free storage
sentry-cli releases files "my-app@1.9.0" delete --all

# Delete releases no longer needed (removes all artifacts and deploy records)
sentry-cli releases delete "my-app@1.9.0"

# Keep at least the last 5 releases for regression comparison
```

## Common Pitfalls

| Pitfall | Impact | Prevention |
|---------|--------|-----------|
| Not quoting `$VERSION` | Breaks on versions with special chars | Always use `"$VERSION"` |
| Shallow clone in CI | `--auto` commit detection fails | Use `fetch-depth: 0` |
| Different release string in SDK vs CLI | Events not linked to releases | Inject build-time env var |
| Uploading maps after deploy | First errors have minified traces | Run CLI before deploy step |
| Missing `org:read` scope on token | Commit association silently fails | Include both `project:releases` + `org:read` |
