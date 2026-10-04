# Gitlab Ci

## GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - build
  - release
  - deploy

variables:
  SENTRY_ORG: your-org
  SENTRY_PROJECT: your-project

build:
  stage: build
  script:
    - npm ci
    - npm run build
  artifacts:
    paths:
      - dist/

sentry-release:
  stage: release
  image: getsentry/sentry-cli
  script:
    - sentry-cli releases new $CI_COMMIT_SHA
    - sentry-cli releases files $CI_COMMIT_SHA upload-sourcemaps ./dist
    - sentry-cli releases set-commits $CI_COMMIT_SHA --auto
    - sentry-cli releases finalize $CI_COMMIT_SHA
    - sentry-cli releases deploys $CI_COMMIT_SHA new -e production
  only:
    - main
```
