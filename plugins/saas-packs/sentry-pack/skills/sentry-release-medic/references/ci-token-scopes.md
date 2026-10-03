# CI token scopes

Least privilege for a human running the release CLI:

- `project:releases`
- `org:read`

Check: `npx @sentry/cli info` or `sentry-cli info`.

Do not print the token. Do not commit `SENTRY_AUTH_TOKEN`. Plugins (`@sentry/webpack-plugin`, `@sentry/vite-plugin`, `@sentry/esbuild-plugin`) read `SENTRY_AUTH_TOKEN`, `SENTRY_ORG`, `SENTRY_PROJECT` from the environment.

This skill still does not upload. Scopes are what the human needs if they choose to run the command you recommended.

GitLab CI and CircleCI use the same CLI flags as GitHub Actions. The inject/upload/deploy order does not change because the YAML dialect changed. `fetch-depth: 0` is the Actions form of "do not use a shallow clone."
