# Release Workflow

## Complete Release Lifecycle

Every Sentry release follows five stages: create, associate commits, upload artifacts, finalize, and deploy.

### 1. Create Release

```bash
# Semver naming (ties to package version)
VERSION="my-app@$(node -p "require('./package.json').version")"
sentry-cli releases new "$VERSION"

# SHA naming (ties to exact deployment)
VERSION="my-app@$(git rev-parse --short HEAD)"
sentry-cli releases new "$VERSION"

# Combined: my-app@2.1.0+a1b2c3d
VERSION="my-app@$(node -p "require('./package.json').version")+$(git rev-parse --short HEAD)"
sentry-cli releases new "$VERSION"

# Auto-propose version from git
VERSION=$(sentry-cli releases propose-version)
sentry-cli releases new "$VERSION"
```

### 2. Associate Commits

Commit association powers suspect commits — Sentry matches error stack frames against recently changed files.

```bash
# Auto-detect from git log (requires GitHub/GitLab integration)
sentry-cli releases set-commits "$VERSION" --auto

# Specify commit range manually
sentry-cli releases set-commits "$VERSION" \
  --commit "my-org/my-repo@from_sha..to_sha"

# Single commit reference
sentry-cli releases set-commits "$VERSION" \
  --commit "my-org/my-repo@abc1234"
```

### 3. Upload Source Maps

```bash
# Standard upload with validation
sentry-cli sourcemaps upload \
  --release="$VERSION" \
  --url-prefix="~/static/js" \
  --validate \
  ./dist

# Multiple directories (SSR apps)
sentry-cli sourcemaps upload \
  --release="$VERSION" \
  --url-prefix="~/" \
  ./dist/client ./dist/server

# Dry run to validate without uploading
sentry-cli sourcemaps upload \
  --release="$VERSION" \
  --url-prefix="~/static/js" \
  --validate \
  --dry-run \
  ./dist
```

### 4. Finalize Release

```bash
# Mark release as complete
sentry-cli releases finalize "$VERSION"

# Or create and finalize in one step (skips source map upload)
sentry-cli releases new "$VERSION" --finalize
```

### 5. Record Deploy

```bash
# Production deploy
sentry-cli releases deploys "$VERSION" new \
  --env production \
  --started $(date +%s) \
  --finished $(date +%s)

# Staging deploy
sentry-cli releases deploys "$VERSION" new --env staging
```

## Artifact Management

```bash
# List artifacts for a release
sentry-cli releases files "$VERSION" list

# Upload a single file
sentry-cli releases files "$VERSION" upload ./dist/app.js.map

# Delete all artifacts (free storage)
sentry-cli releases files "$VERSION" delete --all

# Delete the release entirely
sentry-cli releases delete "$VERSION"
```

## SDK Configuration

The SDK `release` value must match the CLI version exactly:

```typescript
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  release: process.env.SENTRY_RELEASE,
  environment: process.env.NODE_ENV,
  autoSessionTracking: true,
});
```
