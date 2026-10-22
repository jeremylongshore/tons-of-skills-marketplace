---
name: arcgis-to-portaljs
description: Migrate a whole ArcGIS Hub site into a PortalJS Arc portal end-to-end. Harvests the Hub /data.json (DCAT-US) inventory, exports every FeatureService layer through the ArcGIS REST query API with resultOffset paging, converts each to the serverless dual tier (PMTiles render + GeoParquet query) with tabular items to Parquet, pushes everything to Cloudflare R2 via Git LFS, appends dual-tier datasets.json entries, and writes a source-vs-derived parity report. Use to move a City or sector ArcGIS Hub open-data portal onto PortalJS with no server-side compute.
allowed-tools: Read, Write, Edit, Bash(ogr2ogr:*), Bash(ogrinfo:*), Bash(tippecanoe:*), Bash(duckdb:*), Bash(git:*), Bash(curl:*), Bash(jq:*), Bash(npx:*), Bash(node:*), Bash(mkdir:*), Bash(cp:*), Bash(wc:*), Bash(command:*), WebFetch
version: 0.1.0
author: Datopian <hello@datopian.com>
license: MIT
compatibility: Claude Code with PortalJS portals (Next.js 14, React 18/19, Node 18+). Requires native GDAL, tippecanoe, duckdb, and jq on the operator's machine (macOS or Linux/WSL). Runs from any project via the plugin, a personal install, or a portaljs clone.
tags:
  - portaljs
  - data-portal
  - migration
  - arcgis
  - geospatial
  - pmtiles
---

# ArcGIS Hub → PortalJS

## Overview

Migrate an entire **ArcGIS Hub** open-data site into a **PortalJS Arc** portal in one pass.
Every Hub site is machine-readable — a DCAT-US catalog at `/data.json`, with every dataset
backed by an ArcGIS REST FeatureService — so migration is a **harvest → export → convert →
publish → verify** pipeline that runs almost fully automated on the operator's machine, no
server-side compute. The tooling is the reusable `arcgis-to-portaljs` migrator: input is one
Hub URL, output is a ready-to-deploy PortalJS catalog plus a parity report.

The skill is an orchestrator: it reuses the DCAT-US harvest from `portaljs-migrate`, the
`ogr2ogr`/`tippecanoe`/`duckdb` dual-tier conversion from `portaljs-add-geo`, and the bulk
Git-LFS → R2 push from `portaljs-migrate`. Its novel parts are the FeatureService REST export
loop (paged features, not just a link) and the source-vs-derived parity report.

## Prerequisites

- A scaffolded PortalJS portal whose template ships `components/MapPreview.tsx` and
  `components/GeoQuery.tsx` (PR #1647 or later). Run `portaljs-new-portal` first if none.
- Native CLIs: **GDAL** (`ogr2ogr`, `ogrinfo`), **tippecanoe**, **duckdb** (with `spatial`),
  and **jq**. macOS: `brew install gdal tippecanoe duckdb jq`; Debian/Ubuntu:
  `apt-get install gdal-bin duckdb jq` plus tippecanoe (apt or build from source); Windows via
  WSL. The skill hard-stops with the install hint if any is missing.
- Arc credentials for the Git-LFS → R2 push (the token `portaljs-deploy` resolves), or an OSS
  self-hosted Giftless.

## Instructions

The canonical, full step-by-step workflow is
[`.claude/commands/arcgis-to-portaljs.md`](https://github.com/datopian/portaljs/blob/main/.claude/commands/arcgis-to-portaljs.md)
— the single source of truth. Read and follow it when executing. Summary:

1. Gather input — Hub URL, portal directory, project slug, optional flags (`--limit`,
   `--only`, `--dry-run`, `--namespace-mode`). Interview if missing; never dead-end.
2. Check native tools (`ogr2ogr`, `tippecanoe`, `duckdb` + `spatial`, `jq`). Any missing →
   print the per-OS install and stop.
3. Validate the portal directory and confirm the geo showcase components exist.
4. Harvest the Hub `/data.json` (reuse the `portaljs-migrate` DCAT-US map) and classify each
   item: vector (FeatureService), table, or non-data (web map / 3D / imagery → skipped).
   Under `--namespace-mode owner`, resolve namespaces through a publisher-normalization
   table with title-prefix fallback for broken `{{source}}` publishers (multi-publisher
   Hubs ship dirty publisher labels). Dedup near-duplicate hosted-`view` layers — but only
   after a mandatory live record-count check on BOTH twins: equal ⇒ dedup (keep the source
   layer, log the pair); different ⇒ keep both as distinct datasets. Consolidate per-year
   dataset series into one year-partitioned Parquet with legacy per-year view entries. Enrich
   from the AGOL item: sanitized metadata (license/description/dates), cleaned display title
   (`cleanTitle` — raw title still drives the slug), `category` (item categories → meaningful
   theme → keyword mapping), and a `thumbnail` snapshot into `public/thumbnails/`.
5. Export each vector layer through the ArcGIS REST `query` API with `resultOffset` paging
   (`f=geojson`, `outSR=4326`); fall back to keyset paging on transfer limits; accept a
   customer File Geodatabase dump for very large layers.
6. Convert each layer to the dual tier via the `portaljs-add-geo` recipe (PMTiles +
   GeoParquet); tabular items to Parquet. Preserve the native-CRS original.
7. Publish — bulk Git-LFS track + one push to R2 through Giftless, then append dual-tier
   `datasets.json` entries (upsert on `(namespace, slug)`).
8. Write `arcgis-parity-report.md` — record count, extent, attribute schema, and geometry
   validity, source vs derived, per dataset, plus the migrated/skipped/failed accounting.
9. Report the inventory, migrated datasets, R2 push, and parity summary.

## Output

- **Created:** `data/<namespace>/<slug>.pmtiles`, `.parquet`, and the original per vector
  dataset (all LFS-tracked → R2); Parquet + original per table; `arcgis-parity-report.md`.
- **Modified:** `datasets.json` (one dual-tier entry per vector dataset, one resource entry
  per table); `.gitattributes` (LFS tracking).
- **Verified:** the parity report compares each derived artifact to the live FeatureService.
- **Result:** `/@<namespace>/<slug>` renders `<MapPreview>` + `<GeoQuery>` for each vector
  dataset with no page edits; the catalog lists everything migrated.

## Error Handling

| Symptom | Cause | Fix |
| --- | --- | --- |
| `MISSING_INPUT` | No Hub URL provided | Pass the site root (e.g. `https://hub-lewisville.opendata.arcgis.com`) and retry. |
| `MISSING_TOOLS` | `ogr2ogr`/`tippecanoe`/`duckdb`/`jq` (or duckdb `spatial`) absent | Print the per-OS install line and stop; re-run after installing. |
| `NOT_A_PORTAL` | Target dir has no `datasets.json` / geo components | Run `portaljs-new-portal` first, then re-run. |
| `HARVEST_FAILED` | `/data.json` unreachable or not DCAT-US | Confirm the site is an ArcGIS Hub and the feed loads in a browser. |
| `EXPORT_FAILED` | One FeatureService layer errored or hit a hard transfer cap | Logged and skipped; try keyset paging or a customer FGDB dump for that layer. |
| `LFS_PUSH_FAILED` | Missing/expired Arc token or unset `lfs.url` | Re-mint the JWT (see `portaljs-deploy`); confirm `git config lfs.url`. |

## Examples

### Example 1 — Migrate a City Hub (Lewisville)

```
/arcgis-to-portaljs https://hub-lewisville.opendata.arcgis.com slug=lewisville
```

### Example 2 — Dry-run inventory + plan only (no writes)

```
/arcgis-to-portaljs https://streamwaterdata.co.uk --dry-run
```

### Example 3 — Migrate a subset, one namespace per publisher

```
/arcgis-to-portaljs https://streamwaterdata.co.uk --only sewer-catchments,water-boundaries --namespace-mode owner
```

## Resources

- Full workflow: [`.claude/commands/arcgis-to-portaljs.md`](https://github.com/datopian/portaljs/blob/main/.claude/commands/arcgis-to-portaljs.md)
- REST export, classification, parity, and phasing details: [`references/reference.md`](references/reference.md)
- Ongoing sync, parity dashboard, and cutover (Phase 3): [`references/sync-and-cutover.md`](references/sync-and-cutover.md)
- Related skills: `portaljs-migrate`, `portaljs-add-geo`, `portaljs-add-dataset`, `portaljs-deploy`
- ArcGIS REST query API: <https://developers.arcgis.com/rest/services-reference/enterprise/query-feature-service-layer/> · tippecanoe: <https://github.com/felt/tippecanoe> · DuckDB spatial: <https://duckdb.org/docs/extensions/spatial>
