# Github Actions

## GitHub Actions

### Complete Workflow

```yaml
# .github/workflows/release.yml
name: Release with Sentry

on:
  push:
    branches: [main]

env:
  SENTRY_ORG: your-org
  SENTRY_PROJECT: your-project

jobs:
  build-and-release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build
        env:
          SENTRY_RELEASE: ${{ github.sha }}

      - name: Create Sentry Release
        uses: getsentry/action-release@v1
        env:
          SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
        with:
          environment: production
          version: ${{ github.sha }}
          sourcemaps: ./dist

      - name: Deploy
        run: npm run deploy
```

### Source Maps Only

```yaml
- name: Upload Source Maps
  run: |
    npm install -g @sentry/cli
    sentry-cli releases new ${{ github.sha }}
    sentry-cli releases files ${{ github.sha }} upload-sourcemaps ./dist
    sentry-cli releases finalize ${{ github.sha }}
  env:
    SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
    SENTRY_ORG: your-org
    SENTRY_PROJECT: your-project
```
