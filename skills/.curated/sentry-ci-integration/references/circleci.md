# Circleci

## CircleCI

```yaml
# .circleci/config.yml
version: 2.1

orbs:
  sentry: sentry-io/sentry-cli@0.1.0

jobs:
  build-and-release:
    docker:
      - image: cimg/node:20.0
    steps:
      - checkout
      - run: npm ci
      - run: npm run build
      - sentry/install_sentry_cli
      - run:
          name: Create Sentry Release
          command: |
            export SENTRY_RELEASE=$(git rev-parse --short HEAD)
            sentry-cli releases new $SENTRY_RELEASE
            sentry-cli releases files $SENTRY_RELEASE upload-sourcemaps ./dist
            sentry-cli releases finalize $SENTRY_RELEASE

workflows:
  deploy:
    jobs:
      - build-and-release:
          context: sentry
```
