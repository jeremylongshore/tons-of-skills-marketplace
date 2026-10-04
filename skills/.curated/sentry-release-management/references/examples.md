# Examples

## Semver Release with Full Lifecycle

**Request:** "Create a Sentry release for version 2.1.0 with source maps"

```bash
VERSION="my-app@2.1.0"
sentry-cli releases new "$VERSION"
sentry-cli releases set-commits "$VERSION" --auto
sentry-cli sourcemaps upload --release="$VERSION" --url-prefix="~/static/js" --validate ./dist
sentry-cli releases finalize "$VERSION"
sentry-cli releases deploys "$VERSION" new --env production
```

**Result:** Release `my-app@2.1.0` created with commits linked, source maps uploaded, finalized, and production deploy recorded.

## Git SHA Release for Continuous Deployment

**Request:** "Create a release tied to the current commit"

```bash
VERSION="my-app@$(git rev-parse --short HEAD)"
sentry-cli releases new "$VERSION"
sentry-cli releases set-commits "$VERSION" --auto
sentry-cli sourcemaps upload --release="$VERSION" --url-prefix="~/" ./dist
sentry-cli releases finalize "$VERSION"
sentry-cli releases deploys "$VERSION" new --env staging
```

**Result:** Release `my-app@a1b2c3d` created and deployed to staging.

## Monorepo Multi-Project Release

**Request:** "Release both API and frontend with separate Sentry projects"

```bash
SHA=$(git rev-parse --short HEAD)

# API backend
SENTRY_PROJECT=api-backend sentry-cli releases new "api@$SHA"
SENTRY_PROJECT=api-backend sentry-cli releases set-commits "api@$SHA" --auto
SENTRY_PROJECT=api-backend sentry-cli sourcemaps upload --release="api@$SHA" ./api/dist
SENTRY_PROJECT=api-backend sentry-cli releases finalize "api@$SHA"

# Web frontend
SENTRY_PROJECT=web-frontend sentry-cli releases new "web@$SHA"
SENTRY_PROJECT=web-frontend sentry-cli releases set-commits "web@$SHA" --auto
SENTRY_PROJECT=web-frontend sentry-cli sourcemaps upload --release="web@$SHA" --url-prefix="~/" ./web/dist
SENTRY_PROJECT=web-frontend sentry-cli releases finalize "web@$SHA"
```

## Cleanup Old Releases

**Request:** "Delete source maps from releases older than v2.0.0"

```bash
# List releases
sentry-cli releases list

# Delete artifacts for a specific release
sentry-cli releases files "my-app@1.9.0" delete --all

# Delete the release entirely
sentry-cli releases delete "my-app@1.9.0"
```

## Query Release Health via API

**Request:** "Check crash-free rate for the latest release"

```bash
curl -s -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/organizations/$SENTRY_ORG/releases/" \
  | jq '.[0] | {version, dateCreated, newGroups, commitCount}'
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
