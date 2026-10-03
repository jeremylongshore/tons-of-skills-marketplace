# action-release vs Debug IDs

Both of these were public on 2026-10-03. Do not delete one.

| Source | Claim |
|---|---|
| Help Center, verify Debug IDs | `getsentry/action-release@v3` with a `sourcemaps` path injects by default, with CLI ≥ 2.17.0 and bundler plugins ≥ 2.0.0. https://www.sentry.help/en/articles/13965232-javascript-how-do-i-verify-debug-ids-for-source-maps |
| Blog, "How to Fix Source Map Upload Errors" | The GitHub Action and the Netlify plugin cannot inject Debug IDs. https://blog.sentry.io/how-to-fix-source-map-upload-errors/ |
| GitHub Actions doc | Upload and release creation, after build, before deploy, `fetch-depth: 0`. It does not settle inject. https://docs.sentry.io/product/releases/setup/release-automation/github-actions/ |

Rule: grep the built JS for `debugId` (`scripts/grep_debug_id.py`). Absence means the bytes that will run were not injected. Run `sentry-cli sourcemaps inject` or a current bundler plugin before upload, then deploy those files. Pin the action major. Re-check the action source at build time.

A later editor must not "fix" this file by keeping only the Help Center or only the blog.
