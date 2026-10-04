# Deployment Tracking

## Deployment Tracking

### Create Release and Deploy

```bash
#!/bin/bash
# deploy.sh

VERSION=$(git rev-parse --short HEAD)
ENVIRONMENT=${1:-production}

# Create release
sentry-cli releases new $VERSION

# Upload source maps
sentry-cli releases files $VERSION upload-sourcemaps ./dist

# Associate commits
sentry-cli releases set-commits $VERSION --auto

# Finalize release
sentry-cli releases finalize $VERSION

# Deploy application
npm run deploy:$ENVIRONMENT

# Notify Sentry of deployment
sentry-cli releases deploys $VERSION new \
  --env $ENVIRONMENT \
  --started $(date +%s) \
  --finished $(date +%s)

echo "Deployed $VERSION to $ENVIRONMENT"
```

### Application Configuration

```typescript
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  release: process.env.SENTRY_RELEASE || process.env.GIT_SHA,
});
```
