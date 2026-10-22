---
name: portaljs-migrate
description: Migrate (harvest) datasets between open-data platforms. Reads CKAN, a DCAT-US /data.json catalog (DKAN, ArcGIS Hub, data.gov), a DCAT / DCAT-AP RDF feed (JSON-LD, Turtle, or RDF/XML), Socrata, OpenDataSoft, or an ArcGIS FeatureServer, and writes them to a static PortalJS catalog or pushes them into a CKAN instance over its API. Use when moving datasets from an external open-data platform into a PortalJS portal, or bridging one CKAN instance to another.
allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(npx:*), Bash(node:*), Bash(curl:*), Bash(git:*), WebFetch
version: 1.0.0
author: Datopian <hello@datopian.com>
license: MIT
compatibility: Claude Code with PortalJS portals (Next.js 14, React 18, Node 18+). Runs from any project via the plugin, a personal ~/.claude/commands install, or a portaljs clone.
tags:
  - portaljs
  - data-portal
  - migration
  - harvest
  - dcat
  - ckan
---

# PortalJS — Migrate

## Overview

Harvest datasets from an external open-data platform into a PortalJS portal, or
push them into a CKAN instance. Every source reads into one canonical shape —
`{ slug, namespace, name, description, resources[] }` — then writes to the target
from that shape, so adding a source covers every target automatically.

Supported sources: CKAN, a DCAT-US `/data.json` catalog (DKAN, ArcGIS Hub,
data.gov), a DCAT / DCAT-AP RDF feed, Socrata, OpenDataSoft, or an ArcGIS
FeatureServer/MapServer. Supported targets: a static PortalJS catalog
(`datasets.json`, resources linked by URL or downloaded into Cloudflare R2) or a
CKAN instance over its write API.

This is the copy-into-the-portal path, the inverse of `/portaljs-connect-ckan`
(which reads the source live at build time): a one-time, re-runnable snapshot so
the portal stands alone and needs no backend.

## Prerequisites

- An existing PortalJS portal for the static target: `datasets.json`,
  `package.json`, and `pages/[owner]/[slug].tsx` must exist (the `portaljs-catalog`
  template).
- Node 18+ and npm, with portal dependencies installed (`npm install`).
- Network access to the source platform's API or feed URL.
- For a CKAN target: a write API key in `CKAN_API_KEY` — never hardcoded.
- For `download` copy mode: `git-lfs` and a PortalJS Arc account (or a
  self-hosted Giftless endpoint) to push resource files to R2.
- For `dcat-rdf` sources: `lib/metadata/dcat-harvest.ts` and `dcat-profiles.ts`
  (copy from `examples/portaljs-catalog/lib/metadata/` if missing), run via `npx tsx`.

## Instructions

Full step-by-step workflow:
[`.claude/commands/portaljs-migrate.md`](https://github.com/datopian/portaljs/blob/main/.claude/commands/portaljs-migrate.md).

1. Gather input — source type, source URL, target (`static`/`ckan`), portal
   directory, copy mode (`link`/`download`), filters. Interview instead of erroring.
2. Validate the target — confirm the static catalog files exist, or that the CKAN
   URL and API key authenticate.
3. Detect the source type from the URL (or `--source`) and verify reachability.
4. Read the source into canonical dataset entries, per the source's field table in
   the reference doc, applying the metadata hygiene rules (license sentinel — never
   fabricate CC-BY; description sanitizer + fallback chain; source dates preserved
   with `migratedAt` separate; `cleanTitle` display-name cleanup with slugs from the
   raw title; `category` from a meaningful theme).
5. For a static target, resolve resource paths by copy mode: `link` keeps source
   URLs; `download` copies files into the repo under Git LFS, pushed to R2.
6. Print a dry-run preview; stop if `--dry-run` was passed.
7. Write `datasets.json` (upsert or `--replace`), or push packages/resources into
   CKAN over its action API.
8. Verify — `npm run build` (static) or re-query `package_search` (CKAN).
9. Report datasets migrated, namespaces touched, and next steps.

## Output

Static target: an updated `datasets.json` (upserted on `(namespace, slug)`),
optionally with resource files in Git LFS served from Cloudflare R2, plus a
passing `npm run build`. CKAN target: created/updated packages and resources;
per-dataset failures are logged and skipped, not fatal.

## Error Handling

| Symptom | Cause | Fix |
| --- | --- | --- |
| "not a `portaljs-catalog` template" | `datasets.json` missing | Confirm the portal directory, or run `/portaljs-new-portal` |
| CKAN target rejects every write (403) | Key missing, expired, or lacks org permission | Set a valid `CKAN_API_KEY`; stop rather than partially migrating |
| Source URL matches no known format | Auto-detection failed | Pass `--source` explicitly (`ckan`, `dcat`, `dcat-rdf`, `socrata`, `ods`, `arcgis`) |
| DCAT-RDF fetch returns HTML, not a feed | URL is a portal page, not the feed | Follow its `<link rel="alternate">` href, or use the direct feed URL |
| Build fails after write | Malformed entry (missing `slug`/`namespace`/`name`) | Inspect `/tmp/portaljs-migrate-build.log`, fix, rebuild |
| `download` mode push fails | `git-lfs` missing, or no Arc/Giftless token | Install `git-lfs`; mint a token via the Arc API or self-hosted Giftless |
| Duplicate datasets after re-running | `--replace` used unintentionally, or slug collisions | Omit `--replace` to upsert; keep slugs unique per namespace |

## Examples

### Example 1 — CKAN to static catalog, link mode

```bash
/portaljs-migrate --source ckan --source-url https://demo.dev.datopian.com \
  --target static --portal-dir . --copy-mode link
```
Upserts all packages from the CKAN demo instance into `datasets.json`, referencing
source resource URLs directly.

### Example 2 — data.gov DCAT-US catalog, downloaded into R2

```bash
/portaljs-migrate --source dcat --source-url https://catalog.data.gov/data.json \
  --target static --copy-mode download --org-filter epa-gov
```
Harvests one publisher and copies every resource file into the repo under Git
LFS, served from Cloudflare R2.

### Example 3 — DCAT-AP RDF feed from a national portal

```bash
/portaljs-migrate --source dcat-rdf \
  --source-url https://data.europa.eu/api/hub/search/catalog.jsonld \
  --target static --dry-run
```
Fetches the JSON-LD feed through the RDF harvester and previews the canonical
datasets without writing anything.

### Example 4 — CKAN to CKAN (platform-to-platform)

```bash
/portaljs-migrate --source ckan --source-url https://old-portal.example.org \
  --target ckan --target-url https://new-portal.example.org --owner-org research
```
Pushes every package from the old CKAN instance into the new one, filed under
`research`.

## Resources

- Command source: [`.claude/commands/portaljs-migrate.md`](https://github.com/datopian/portaljs/blob/main/.claude/commands/portaljs-migrate.md)
- Field mappings and troubleshooting: [`references/reference.md`](references/reference.md)
- Related skills: `/portaljs-connect-ckan`, `/portaljs-add-dcat`,
  `/portaljs-check-data-quality`, `/portaljs-define-schema`
- CKAN Action API reference: https://docs.ckan.org/en/latest/api/
