# ArcGIS Hub → PortalJS — Reference

Detailed reference for the `arcgis-to-portaljs` skill. The executable workflow lives in
[`.claude/commands/arcgis-to-portaljs.md`](https://github.com/datopian/portaljs/blob/main/.claude/commands/arcgis-to-portaljs.md).

## What it composes (do not reinvent)

| Step | Reused from | Added here |
| --- | --- | --- |
| Harvest `/data.json` → canonical | `portaljs-migrate` (DCAT-US map) | Hub item classification |
| Export FeatureService → GeoJSON | — | REST `query` paging loop (downloads features) |
| Convert → PMTiles + GeoParquet | `portaljs-add-geo` §5–§8 | per-layer loop |
| Publish (LFS → R2, datasets.json) | `portaljs-migrate` §5 + `portaljs-add-geo` §10 | dual-tier entries in bulk |
| Parity report | — | source-vs-derived comparison |

`portaljs-migrate`'s `arcgis` source only *links* the `query?...&f=geojson` URL; this skill
*downloads* the features so they can be served serverless (PMTiles + GeoParquet) instead of
depending on the live Esri service.

## Hub item classification

| Class | Detect on | Path |
| --- | --- | --- |
| vector | distribution URL matches `/FeatureServer/\d+` or `/MapServer/\d+`; or `format` ∈ {GeoService, GeoJSON, Shapefile, File Geodatabase, GeoPackage} | REST export → dual tier |
| table | only tabular distributions (CSV/Excel), no geometry | download → Parquet |
| non-data | `type` ∈ {Web Map, Web Scene, Dashboard, StoryMap, Image Service}, drone imagery, or an Esri basemap reference | skip; list in report |

## REST export

- Discover: `GET <layer>?f=json` → `maxRecordCount` (typically 1000–2000), `extent`, `fields[]`.
- Count: `GET <layer>/query?where=1=1&returnCountOnly=true&f=json` → `count` (parity baseline).
- Page: `GET <layer>/query?where=1=1&outFields=*&outSR=4326&f=geojson&resultOffset=<n>&resultRecordCount=<max>`
  until a short page returns. Concatenate `features[]` into one GeoJSON `FeatureCollection`.
- `exceededTransferLimit` / hard caps → keyset paging: `orderByFields=<oid>` + `where=<oid> > <last>`.
- `f=json` fallback (Esri JSON) → pipe through `ogr2ogr` if `f=geojson` is disabled.
- Very large layers → `--fgdb <slug>=<path.gdb>`: `ogr2ogr` reads the `.gdb` directly, skipping
  paging. Ask the data owner for the dump (seconds from ArcGIS Pro).

## Conversion (from portaljs-add-geo)

Normalize (idempotent even though `outSR=4326` already applied — fixes winding/precision):
```bash
ogr2ogr -f GeoJSON -t_srs EPSG:4326 -lco RFC7946=YES out.4326.geojson in.source.geojson
```
PMTiles render tier:
```bash
tippecanoe -zg --drop-densest-as-needed --extend-zooms-if-still-dropping --force \
  -o out.pmtiles out.4326.geojson
```
GeoParquet query tier (covering `bbox` + Hilbert):
```bash
duckdb -c "LOAD spatial;
  COPY (SELECT * EXCLUDE (geom),
    {'xmin':ST_XMin(geom),'ymin':ST_YMin(geom),'xmax':ST_XMax(geom),'ymax':ST_YMax(geom)} AS bbox,
    geom AS geometry
  FROM ST_Read('out.4326.geojson')
  ORDER BY ST_Hilbert(geom,{'min_x':-180,'min_y':-90,'max_x':180,'max_y':90}::BOX_2D))
  TO 'out.parquet' (FORMAT PARQUET, ROW_GROUP_SIZE 25000);"
```
Size escape hatch (measure normalized GeoJSON bytes): warn ≥ 500 MB; > 2 GB → GeoParquet-only,
skip PMTiles (documented, never silent).

## Parity report (`arcgis-parity-report.md`)

| Check | Source | Derived | Pass if |
| --- | --- | --- | --- |
| Record count | `returnCountOnly=true` | `duckdb count(*)` on parquet | equal |
| Extent (bbox) | layer `.extent` → 4326 | `duckdb` min/max of `bbox` | within tolerance |
| Attribute schema | layer `.fields[].name` | parquet columns | source ⊆ derived |
| Geometry validity | — | `count(*) WHERE NOT ST_IsValid(geometry)` | 0 invalid |

Emit per-dataset PASS/WARN plus inventory accounting (migrated / skipped / failed, with
reasons) and the full non-data list. Never suppress a mismatch — the report is a deliverable.

## Publish (from portaljs-migrate / portaljs-add-geo)

`git lfs track "data/**"` → one commit → claim slug + mint Arc JWT → `git config lfs.url` →
one push (bytes → Giftless/R2, no GitHub remote required) → `git lfs prune`. R2 URL =
`${R2_PUBLIC_BASE:-https://data.portaljs.com}/lfs/datopian/<slug>/<oid>`. OSS self-host signs
locally with `giftless/mint-token.py`. Dual-tier `datasets.json` entry shape: see
`portaljs-add-geo` §10 (`tiles` pmtiles + `geo` geoparquet + `source` original, with a
bbox-first `query` filled from the layer extent). Also emit the sync ledger
`arcgis-sync-state.json` (per-layer `serviceUrl`/`recordCount`/`dataLastEditDate`/`extent`) so the
Phase-3 scheduled sync can detect drift — see [`sync-and-cutover.md`](sync-and-cutover.md).

## Phasing (epic po-0qe §6)

| Phase | Scope | In this skill? |
| --- | --- | --- |
| 0 | Harvest + export + convert + publish + parity (the automatable core) | **Yes** |
| 1 | Lewisville shadow portal (single-publisher, geo-heavy) | Run the skill; own bead |
| 2 | Stream (multi-publisher orgs, content pages, triage workflow) | Own bead |
| 3 | Scheduled sync + cutover playbook (re-harvest, redirects, DNS) | **Yes** → [`references/sync-and-cutover.md`](sync-and-cutover.md) |
| 4 | Koop FeatureServer-compat adapter (keep old REST consumers) | Own bead (optional) |

3D scenes / StoryMaps / drone imagery have no serverless open equivalent — link-out or leave
on AGOL. Strip Esri basemap references (license-bound). AGOL stays the editing source of
truth; the PortalJS site is a shadow that re-harvests on a schedule (Phase 3).
