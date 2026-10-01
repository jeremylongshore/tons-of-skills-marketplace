# Deploy — Reference

Detailed reference for the `portaljs-deploy` skill. The executable workflow lives in
[`.claude/commands/portaljs-deploy.md`](https://github.com/datopian/portaljs/blob/main/.claude/commands/portaljs-deploy.md).

## Static export config

Arc serves plain static files, so `next.config.js` must produce a full `out/` export:

```js
module.exports = {
  output: 'export',
  images: { unoptimized: true }, // no image-optimization server on static hosting
}
```

The skill adds these keys if missing, preserving the rest of the config. A
`getStaticPaths`-driven route (the CKAN/manifest showcase) must set `fallback: false` —
the shipped templates already do. If `npm run build` complains about a dynamic route,
that's the cause: no server exists at request time to render a fallback page.

## Auth and environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `PORTALJS_TOKEN` | — | Arc bearer token; takes precedence over the credentials file. Use in CI. |
| `~/.portaljs/credentials` | — | `{"token":"…"}`, mode `0600`, written by the device sign-in flow. |
| `PORTALJS_ARC_API` | `https://api.arc.portaljs.com` | Deploy/whoami API base; override for staging. |
| `PORTALJS_ARC_AUTH` | `https://arc.portaljs.com` | Device-authorization worker; override for staging. |

The device flow mirrors `gh auth login` / `wrangler login`: it requests a device code,
opens a browser, polls until approved, then writes the credentials file. It never prints
or asks for a token to be pasted in. If Node can't run the flow (offline, no Node), the
skill falls back to asking for `PORTALJS_TOKEN` or a hand-written credentials file.

## Export hygiene (R2 / Git LFS)

A deployed portal must ship **zero dataset bytes** — large data is fetched in the browser
straight from Cloudflare R2 via absolute URLs already present in `datasets.json`
(`resourceUrl()` passes an absolute URL through unchanged). The `check-export` gate fails
the deploy on either:

1. A Git LFS pointer stub exported instead of real content (someone forgot the R2 URL is
   the source of truth, not the working tree file).
2. A data file at or over the size budget that should live in R2 instead of `out/`.

Never run `git lfs pull` before building — that inlines large bytes into the export
instead of leaving lightweight pointers, bloating the upload. Framework chunks under
`_next/` (including duckdb-wasm) are exempt from the size budget. Raise the budget for a
legitimately large *app* asset with `MAX_FILE_MB=<n> npm run check-export`. Portals
scaffolded before this script shipped skip the gate rather than blocking deploy.

## Source snapshots (interim Artifacts workaround)

Cloudflare Artifacts — the intended versioned-source backing for Arc deploys — is closed-beta
and not yet enrolled on the Datopian account. Until it lands, each successful deploy also
persists an **immutable snapshot of the pre-build source tree** (everything the build ran
against, minus `node_modules`/`.git`/`out`/`.next`/`.env*`) to R2, linked to that deployment's
owner and slug:

- `POST /v1/deploy/<deployment_id>/source` — upload a snapshot for a deployment just created
  by step 5. One snapshot per deployment; a second upload for the same id 409s rather than
  overwriting the first.
- `GET /v1/repos/<slug>/sources` — list a slug's snapshot history (deployment id, size,
  timestamp), newest first.
- `GET /v1/repos/<slug>/sources/<deployment_id>` — download one snapshot's gzipped tar.

Both retrieval endpoints are gated to the slug's owner (the account whose token deployed it)
or Datopian staff. This is snapshot storage, not version control — no diffing/branching; if
Artifacts access is later granted, that becomes the upgrade path.

## Troubleshooting

- **`check-export` script not found** — older portal predates the script; the deploy
  skill skips the gate automatically rather than failing.
- **Repeated 401 after re-login** — the token was revoked server-side; sign in again at
  <https://arc.portaljs.com> and confirm the account owns the slug.
- **Upload times out** — the tarball is large; check `check-export` output for files that
  should be R2-hosted instead of bundled.
- **Slug already has content from a previous deploy** — expected; deploys are idempotent
  and replace the site at that slug in place.
