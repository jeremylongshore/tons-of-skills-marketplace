# ci-sourcemap-upload

**Owner:** `sentry-release-medic` → `sourcemap-uploader`
**Canonical file.** Forensics holds a labeled copy for "release A on the event, release B on the maps."

Recommend the pipeline. Do not execute it. `--apply` on the grep script is refused.

## One release id

The SDK `release` and the CLI `--release` are the same string. Do not invent
`frontend@1.4.2-sourcemaps` beside `frontend@1.4.2`.

`sentry-cli sourcemaps upload --release` does **not** create the release. The
release appears when an event arrives with that name, or when someone creates
it in a separate call. Debug IDs do not require a release to unminify, and
that is why teams delete the release step and then lose suspect commits.
Keep the release if you want commits.

Set `dist` only when two files in the **same** project and release would share
a name. A `dist` the SDK does not send hides maps that Debug ID would have matched.

## Order

1. `actions/checkout` with `fetch-depth: 0` if commits must associate. Shallow checkout is why suspect commit is empty (RL05).
2. Build.
3. Inject Debug IDs into **those** artifacts (`sentry-cli sourcemaps inject`, or a bundler plugin ≥ 2.0.0: `@sentry/webpack-plugin`, `@sentry/vite-plugin`, `@sentry/esbuild-plugin`).
4. Upload those artifacts.
5. Deploy **those** files. A later job that uploads `dist/` from cache or a second build is RL01.

Token scopes a human needs to run this: `project:releases` and `org:read`.
Auth check: `npx @sentry/cli info` (or `sentry-cli info`). No token in this
skill's output. Advisory: pasted `sentry-cli releases list`. Do not guess the org slug.

Plugins read `SENTRY_AUTH_TOKEN`, `SENTRY_ORG`, `SENTRY_PROJECT` from the environment. Do not hardcode them into a workflow you print. Use secrets.

## debugId grep (RL04)

```bash
python3 scripts/grep_debug_id.py dist/
```

- `PRESENT`: `debugId` occurs in JS/HTML that will run. Exit 0.
- `ABSENT`: those bytes were not injected. Exit 2. Next step is inject, then upload, then deploy those files.
- A `.map` containing `debug_id` with no `debugId` in the JS is still `ABSENT` (`map_only_does_not_count`).

Cite both, every time, from the script's `citations` object:

- Help Center (verify Debug IDs): `getsentry/action-release@v3` with a `sourcemaps` path injects by default, CLI ≥ 2.17.0, bundler plugins ≥ 2.0.0. https://www.sentry.help/en/articles/13965232-javascript-how-do-i-verify-debug-ids-for-source-maps
- Blog "How to Fix Source Map Upload Errors": the GitHub Action and the Netlify plugin cannot inject Debug IDs. https://blog.sentry.io/how-to-fix-source-map-upload-errors/
- Actions doc describes upload and release creation (after build, before deploy, `fetch-depth: 0`) more than it spells inject. https://docs.sentry.io/product/releases/setup/release-automation/github-actions/

Do not delete a citation to settle the conflict. Pin the action major. Re-check the action source when you have it. The grep still wins.

## Monorepo (SC05)

One repo secret `SENTRY_PROJECT=web` uploading every package's maps is the bug.
One upload step per project, `dist` limited to that package. The DSN in each app must be the project you uploaded to. Preview deploys must not reuse the prod DSN if preview errors should stay out of prod crash-free rate.

## Not retroactive

Events already accepted stay as stored. Say that when the upload is late.

## JS only

Do not add ProGuard or dSYM steps to this checklist.
