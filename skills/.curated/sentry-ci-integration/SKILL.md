---
name: sentry-ci-integration
description: 'Integrate Sentry into CI/CD pipelines for automated release creation,

  source map uploads, and deploy notifications.

  Use when setting up GitHub Actions, GitLab CI, or CircleCI to automate

  Sentry releases, upload source maps, or associate commits with deploys.

  Trigger with phrases like "sentry github actions", "sentry CI pipeline",

  "automate sentry releases", "sentry source map upload CI",

  "sentry gitlab ci", "sentry circleci".

  '
allowed-tools: Read, Write, Edit, Bash(gh:*), Bash(sentry-cli:*), Bash(npm:*), Bash(npx:*),
  Grep, Glob
version: 1.51.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- sentry
- ci-cd
- github-actions
- gitlab-ci
- source-maps
- deployment
compatibility: Designed for Claude Code
---
# Sentry CI Integration

## Overview

Sentry releases connect errors to the code that caused them. Automating release creation in CI/CD ensures every deploy has commit association (suspect commits), source maps for readable stack traces, and deployment tracking across environments. This skill covers `sentry-cli` commands, the official GitHub Action, build tool plugins (`@sentry/webpack-plugin`, `@sentry/vite-plugin`, `@sentry/esbuild-plugin`), and multi-platform CI configurations.

## Prerequisites

- Sentry account with a project at [sentry.io](https://sentry.io)
- `SENTRY_AUTH_TOKEN` — generate at sentry.io/settings/auth-tokens/ with scopes `project:releases` and `org:read`
- `SENTRY_ORG` and `SENTRY_PROJECT` environment variables matching your organization and project slugs
- Source maps generated during your build step (`devtool: 'source-map'` in webpack, `build.sourcemap: true` in Vite)
- Git integration installed in Sentry (sentry.io/settings/integrations/ — GitHub, GitLab, or Bitbucket) for commit association
- `sentry-cli` available via `npm install -g @sentry/cli`, `npx @sentry/cli`, or the `getsentry/sentry-cli` Docker image

## Instructions

### Step 1 — Configure Environment Variables and Auth Token

Set up the three required environment variables in your CI platform. Every `sentry-cli` command reads these automatically.

```bash
# GitHub Actions — add as repository secrets:
#   Settings > Secrets and variables > Actions > New repository secret
SENTRY_AUTH_TOKEN=sntrys_eyJ...     # Internal integration token from sentry.io/settings/auth-tokens/
SENTRY_ORG=my-org                    # Organization slug (visible in sentry.io URL)
SENTRY_PROJECT=my-project            # Project slug (Settings > Projects > project name)

# Required token scopes:
#   project:releases   — create releases, upload source maps, record deploys
#   org:read           — read organization data for --auto commit association

# GitLab CI — add under Settings > CI/CD > Variables (masked + protected)
# CircleCI — add under Project Settings > Environment Variables
```

For build tool plugins (`@sentry/webpack-plugin`, `@sentry/vite-plugin`, `@sentry/esbuild-plugin`), the same three environment variables are read automatically. No additional configuration needed.

Verify your token works locally before committing CI configuration:

```bash
export SENTRY_AUTH_TOKEN=sntrys_eyJ...
export SENTRY_ORG=my-org
export SENTRY_PROJECT=my-project
npx @sentry/cli info
# Should print organization name, project, and CLI version
```

### Step 2 — Create the CI Release Pipeline

The release pipeline follows five commands in sequence: create release, associate commits, upload source maps, finalize release, and record deployment.

```bash
# The five sentry-cli commands that form a complete release pipeline:
VERSION=$(git rev-parse HEAD)

# 1. Create a new release (idempotent — safe to re-run)
sentry-cli releases new "$VERSION"

# 2. Associate commits for suspect commit detection (requires Git integration)
sentry-cli releases set-commits "$VERSION" --auto

# 3. Upload source maps with validation
sentry-cli releases files "$VERSION" upload-sourcemaps ./dist \
  --url-prefix '~/' \
  --validate

# 4. Mark the release as complete
sentry-cli releases finalize "$VERSION"

# 5. Record the deployment environment
sentry-cli releases deploys "$VERSION" new -e production
```

The `--validate` flag on source map upload checks that each `.map` file references a valid source file and that `sourceMappingURL` comments point to uploaded artifacts. Always use it in CI to catch mismatches early.

The `--url-prefix` must match the URL path where your JavaScript files are served. For example, if your app serves `https://example.com/assets/app.js`, use `--url-prefix '~/assets/'`. The `~/` prefix is shorthand for your domain root.

### Step 3 — Integrate Build Tool Plugins (Alternative to sentry-cli)

Build tool plugins handle source map upload during the build step itself, eliminating the need for separate `sentry-cli` commands. They automatically create releases, upload maps, and optionally delete `.map` files from the output so they are never served to clients.

**Vite** (`@sentry/vite-plugin`):

```javascript
// vite.config.js
import { sentryVitePlugin } from '@sentry/vite-plugin';

export default {
  build: {
    sourcemap: true, // Required — plugin needs source maps to upload
  },
  plugins: [
    sentryVitePlugin({
      org: process.env.SENTRY_ORG,
      project: process.env.SENTRY_PROJECT,
      authToken: process.env.SENTRY_AUTH_TOKEN,
      release: {
        name: process.env.GITHUB_SHA || process.env.CI_COMMIT_SHA,
        setCommits: { auto: true },
        deploy: { env: process.env.NODE_ENV || 'production' },
      },
      sourcemaps: {
        filesToDeleteAfterUpload: ['./dist/**/*.map'],
      },
    }),
  ],
};
```

**Webpack** (`@sentry/webpack-plugin`):

```javascript
// webpack.config.js
const { sentryWebpackPlugin } = require('@sentry/webpack-plugin');

module.exports = {
  devtool: 'source-map',
  plugins: [
    sentryWebpackPlugin({
      org: process.env.SENTRY_ORG,
      project: process.env.SENTRY_PROJECT,
      authToken: process.env.SENTRY_AUTH_TOKEN,
      release: {
        name: process.env.GITHUB_SHA || process.env.CI_COMMIT_SHA,
        setCommits: { auto: true },
        deploy: { env: 'production' },
      },
      sourcemaps: {
        assets: ['./dist/**'],
        filesToDeleteAfterUpload: ['./dist/**/*.map'],
      },
    }),
  ],
};
```

**esbuild** (`@sentry/esbuild-plugin`):

```javascript
// build.mjs
import { sentryEsbuildPlugin } from '@sentry/esbuild-plugin';
import esbuild from 'esbuild';

await esbuild.build({
  entryPoints: ['./src/index.ts'],
  bundle: true,
  sourcemap: true,
  outdir: './dist',
  plugins: [
    sentryEsbuildPlugin({
      org: process.env.SENTRY_ORG,
      project: process.env.SENTRY_PROJECT,
      authToken: process.env.SENTRY_AUTH_TOKEN,
      release: {
        name: process.env.GITHUB_SHA,
      },
    }),
  ],
});
```

Install the plugin for your build tool:

```bash
# Pick one based on your build tool:
npm install --save-dev @sentry/vite-plugin
npm install --save-dev @sentry/webpack-plugin
npm install --save-dev @sentry/esbuild-plugin
```

## Output

After completing CI integration, every deploy produces:

- A Sentry release named by commit SHA, visible at sentry.io under Releases
- Source maps uploaded and validated, enabling readable JavaScript stack traces
- Commits associated with the release, powering suspect commit detection in issue details
- A deployment record in Sentry with the target environment (production, staging, etc.)
- Source map files optionally deleted from build output when using build tool plugins

Verify the release was created:

```bash
sentry-cli releases list --org my-org --project my-project
# Shows recent releases with commit counts and deploy environments
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `error: API request failed: 401 Unauthorized` | Auth token invalid, expired, or missing | Regenerate at sentry.io/settings/auth-tokens/ and update CI secret |
| `error: could not determine any commits to associate` | Git integration not installed or shallow clone | Install GitHub/GitLab integration at sentry.io/settings/integrations/ and set `fetch-depth: 0` in checkout |
| `error: could not find referenced source map` | `sourceMappingURL` comment missing from JS files | Verify `devtool: 'source-map'` (webpack) or `build.sourcemap: true` (Vite) is set |
| Source maps uploaded but stack traces still minified | `--url-prefix` does not match served URL paths | Open browser DevTools Network tab, check the URL path of your JS files, and set `--url-prefix` to match |
| `error: release already exists` | Re-running pipeline for same commit | Safe to ignore — `sentry-cli releases new` is idempotent; subsequent commands update the existing release |
| `error: org not found` | `SENTRY_ORG` does not match organization slug | Check your org slug at sentry.io/settings/ (it appears in the URL) |
| `413 Request Entity Too Large` | Source map bundle exceeds 40 MB upload limit | Split source maps per entry point or exclude vendor maps with `--ignore` flag |
| Build tool plugin silently skips upload | `SENTRY_AUTH_TOKEN` not set in CI environment | The plugins no-op when auth token is missing; ensure the secret is available to the build step |

## Examples

### Example A — GitHub Actions Full Release Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy with Sentry Release

on:
  push:
    branches: [main]

env:
  SENTRY_ORG: ${{ secrets.SENTRY_ORG }}
  SENTRY_PROJECT: ${{ secrets.SENTRY_PROJECT }}
  SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full git history for commit association

      - uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Install dependencies
        run: npm ci

      - name: Build with source maps
        run: npm run build

      - name: Create Sentry release and upload source maps
        run: |
          VERSION="${{ github.sha }}"
          npx @sentry/cli releases new "$VERSION"
          npx @sentry/cli releases set-commits "$VERSION" --auto
          npx @sentry/cli releases files "$VERSION" upload-sourcemaps ./dist \
            --url-prefix '~/' \
            --validate
          npx @sentry/cli releases finalize "$VERSION"
          npx @sentry/cli releases deploys "$VERSION" new -e production

      - name: Deploy application
        run: npm run deploy
```

Using the official GitHub Action as a simpler alternative:

```yaml
      - name: Create Sentry release
        uses: getsentry/action-release@v1
        env:
          SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
          SENTRY_ORG: ${{ secrets.SENTRY_ORG }}
          SENTRY_PROJECT: ${{ secrets.SENTRY_PROJECT }}
        with:
          environment: production
          version: ${{ github.sha }}
          sourcemaps: ./dist
          url_prefix: '~/'
          set_commits: auto
```

### Example B — Vite Plugin with GitHub Actions

When using `@sentry/vite-plugin`, the build step handles source maps automatically. No separate `sentry-cli` step needed.

```yaml
# .github/workflows/deploy.yml
name: Deploy (Vite + Sentry Plugin)

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Install dependencies
        run: npm ci

      - name: Build (Vite plugin uploads source maps automatically)
        run: npm run build
        env:
          SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
          SENTRY_ORG: ${{ secrets.SENTRY_ORG }}
          SENTRY_PROJECT: ${{ secrets.SENTRY_PROJECT }}
          GITHUB_SHA: ${{ github.sha }}

      - name: Deploy application
        run: npm run deploy
```

```javascript
// vite.config.js — referenced by the workflow above
import { sentryVitePlugin } from '@sentry/vite-plugin';

export default {
  build: { sourcemap: true },
  plugins: [
    sentryVitePlugin({
      org: process.env.SENTRY_ORG,
      project: process.env.SENTRY_PROJECT,
      authToken: process.env.SENTRY_AUTH_TOKEN,
      release: {
        name: process.env.GITHUB_SHA,
        setCommits: { auto: true },
        deploy: { env: 'production' },
      },
      sourcemaps: {
        filesToDeleteAfterUpload: ['./dist/**/*.map'],
      },
    }),
  ],
};
```

### Example C — GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - build
  - deploy
  - sentry

build:
  stage: build
  image: node:20
  script:
    - npm ci
    - npm run build
  artifacts:
    paths:
      - dist/

sentry-release:
  stage: sentry
  image: getsentry/sentry-cli:latest
  variables:
    SENTRY_AUTH_TOKEN: $SENTRY_AUTH_TOKEN
    SENTRY_ORG: $SENTRY_ORG
    SENTRY_PROJECT: $SENTRY_PROJECT
  script:
    - VERSION="$CI_COMMIT_SHA"
    - sentry-cli releases new "$VERSION"
    - sentry-cli releases set-commits "$VERSION" --auto
    - sentry-cli releases files "$VERSION" upload-sourcemaps ./dist
        --url-prefix '~/'
        --validate
    - sentry-cli releases finalize "$VERSION"
    - sentry-cli releases deploys "$VERSION" new -e production
  only:
    - main
```

### Example D — CircleCI

```yaml
# .circleci/config.yml
version: 2.1

jobs:
  deploy:
    docker:
      - image: cimg/node:20.0
    steps:
      - checkout
      - run: npm ci
      - run: npm run build
      - run:
          name: Create Sentry release
          command: |
            npm install -g @sentry/cli
            VERSION="$CIRCLE_SHA1"
            sentry-cli releases new "$VERSION"
            sentry-cli releases set-commits "$VERSION" --auto
            sentry-cli releases files "$VERSION" upload-sourcemaps ./dist \
              --url-prefix '~/' \
              --validate
            sentry-cli releases finalize "$VERSION"
            sentry-cli releases deploys "$VERSION" new -e production

workflows:
  deploy:
    jobs:
      - deploy:
          filters:
            branches:
              only: main
```

### Example E — Monorepo with Multiple Sentry Projects

```yaml
# .github/workflows/deploy.yml — monorepo with separate Sentry projects
jobs:
  deploy-api:
    runs-on: ubuntu-latest
    env:
      SENTRY_ORG: ${{ secrets.SENTRY_ORG }}
      SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - run: npm ci --workspace=api && npm run build --workspace=api
      - name: Sentry release for API
        run: |
          VERSION="api@${{ github.sha }}"
          npx @sentry/cli releases new "$VERSION" --project api-backend
          npx @sentry/cli releases set-commits "$VERSION" --auto
          npx @sentry/cli releases files "$VERSION" upload-sourcemaps ./api/dist \
            --project api-backend --validate
          npx @sentry/cli releases finalize "$VERSION"
          npx @sentry/cli releases deploys "$VERSION" new -e production

  deploy-web:
    runs-on: ubuntu-latest
    env:
      SENTRY_ORG: ${{ secrets.SENTRY_ORG }}
      SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - run: npm ci --workspace=web && npm run build --workspace=web
      - name: Sentry release for Web
        run: |
          VERSION="web@${{ github.sha }}"
          npx @sentry/cli releases new "$VERSION" --project web-frontend
          npx @sentry/cli releases set-commits "$VERSION" --auto
          npx @sentry/cli releases files "$VERSION" upload-sourcemaps ./web/dist \
            --project web-frontend --url-prefix '~/' --validate
          npx @sentry/cli releases finalize "$VERSION"
          npx @sentry/cli releases deploys "$VERSION" new -e production
```

## Resources

- [Sentry Release Automation](https://docs.sentry.io/product/releases/setup/release-automation/) — official guide for CI/CD integration
- [sentry-cli Releases](https://docs.sentry.io/cli/releases/) — full CLI reference for release management
- [Source Maps Upload](https://docs.sentry.io/platforms/javascript/sourcemaps/uploading/) — troubleshooting source map issues
- [@sentry/vite-plugin](https://www.npmjs.com/package/@sentry/vite-plugin) — Vite build integration
- [@sentry/webpack-plugin](https://www.npmjs.com/package/@sentry/webpack-plugin) — Webpack build integration
- [@sentry/esbuild-plugin](https://www.npmjs.com/package/@sentry/esbuild-plugin) — esbuild build integration
- [getsentry/action-release](https://github.com/getsentry/action-release) — official GitHub Action
- [Auth Token Scopes](https://docs.sentry.io/api/auth/) — token permission reference

## Next Steps

- **sentry-deploy-integration** — connect deploy notifications from Vercel, Netlify, or AWS to Sentry releases
- **sentry-release-management** — version naming strategies, release health monitoring, and regression detection
- **sentry-debug-bundle** — upload debug information files (dSYMs, ProGuard mappings) for native crash symbolication
- **sentry-performance-tracing** — add distributed tracing to correlate releases with performance regressions
