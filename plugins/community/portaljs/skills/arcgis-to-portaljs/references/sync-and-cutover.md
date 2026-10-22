# ArcGIS Hub → PortalJS — Phase 3: Sync & Cutover

Phase 0 migrates a Hub **once**. This reference covers the transition tooling that keeps the
shadow portal faithful over time and retires the old site:

- **(a) Scheduled sync** — re-harvest changed layers on a cadence so the shadow tracks the live Hub.
- **(b) Parity dashboard** — track source-vs-derived parity across runs, not just the last one.
- **(c) Cutover playbook** — preserve old URLs (redirects where you own the domain; link-outs +
  sitemap + crosswalk where you don't, e.g. an `opendata.arcgis.com` subdomain).
- **(d) Post-cutover options** — keep AGOL upstream / go git-native / full Esri exit.

Mental model (unchanged from Phase 0): **AGOL stays the editing source of truth; PortalJS is a
read-only shadow** that re-harvests on a schedule. You are replacing the *portal*, not (yet) the
GIS editing environment. Cutover (c) and the exit paths (d) are how you change that later.

---

## (a) Scheduled sync

### Where it runs — CI cron, not a Worker

The conversion tier is **native binaries** (GDAL/`ogr2ogr`, `tippecanoe`, `duckdb`). A Cloudflare
Worker cannot run them, so a Worker Cron Trigger can only refresh *metadata*, never re-tile or
re-convert geometry. Run the sync where the toolchain installs:

- **GitHub Actions scheduled workflow** (recommended) — the portal is already a git repo with
  `data/**` on Git LFS → R2; a scheduled job re-runs the pipeline and commits back. Zero extra infra.
- Any equivalent CI with a cron (GitLab CI, a self-hosted runner, a cron box). Same steps.
- A Worker Cron Trigger is only viable as a **change *detector*** that opens an issue / dispatches
  the Actions workflow when it sees drift — useful if you want sub-daily detection without a daily
  full CI run, but the actual conversion still happens in CI.

### The sync ledger — `arcgis-sync-state.json`

Change detection needs to know what was true at the last harvest. Phase 0 already knows these
numbers (it gates the parity report on them); Phase 3 **persists them** to a small ledger committed
in the portal repo, keyed by `(namespace, slug)`:

```json
{
  "generatedAt": "2026-07-14T16:00:00Z",
  "site": "https://hub-lewisville.opendata.arcgis.com",
  "layers": {
    "geo/parcels-hosted": {
      "serviceUrl": "https://services2.arcgis.com/kXGqZY4GIOcEYxoF/arcgis/rest/services/Parcels_Hosted/FeatureServer/0",
      "recordCount": 30694,
      "dataLastEditDate": 1783741000000,
      "extent": [-97.05, 33.02, -96.94, 33.10],
      "migratedAt": "2026-07-11T09:12:00Z",
      "missCount": 0
    }
  }
}
```

Write it in Phase 0/§7 alongside `datasets.json` (one entry per migrated layer), and rewrite the
touched entries on every sync run.

### Change detection — per layer, cheap first

For each migrated layer, one cheap request decides whether to do expensive work. Prefer the
edit-timestamp; fall back to the count (services with editor tracking disabled return a null
`editingInfo`):

```bash
SVC="$serviceUrl"     # from the ledger
# 1) Edit timestamp (authoritative when present). epoch ms.
LIVE_EDIT=$(curl -sS -m30 "$SVC?f=json" | jq -r '.editingInfo.dataLastEditDate // .editingInfo.lastEditDate // empty')
# 2) Live count (always available; the fallback + a second guard against silent add/delete).
LIVE_COUNT=$(curl -sS -m30 "$SVC/query?where=1=1&returnCountOnly=true&f=json" | jq -r '.count')

CHANGED=false
if [ -n "$LIVE_EDIT" ] && [ "$LIVE_EDIT" -gt "$STORED_EDIT" ]; then CHANGED=true; fi
if [ "$LIVE_COUNT" != "$STORED_COUNT" ]; then CHANGED=true; fi
```

Why both: on Lewisville, Parcels `dataLastEditDate` (`1783914682041` = 2026-07-13) already exceeds
the deployed 2026-07-11 run **and** the count moved 30,694 → 30,696. Either signal alone catches
this; keeping both means a service that disables editor tracking (null `editingInfo`) still syncs on
the count delta, and a metadata-only edit (schema tweak, same count) still syncs on the timestamp.
Also compare DCAT `modified` at the dataset level as a coarse cross-check — it is derived from
`dataLastEditDate`, so it agrees, but it is the only signal for **non-FeatureServer tabular** items.

### Apply — re-run Phase 0 for changed layers only

For each `CHANGED` layer, re-run the existing §5→§7 pipeline **scoped to that one layer**: export →
convert to the six formats → **idempotent upsert** into `datasets.json` on `(namespace, slug)` →
LFS-push the new blobs → update the ledger entry (`recordCount`, `dataLastEditDate`, `extent`,
`migratedAt`). Unchanged layers are skipped entirely — no re-export, no LFS churn, no commit noise.

Safety rules (a shadow must never lie or self-destruct):
- **Never delete on a single miss.** If a layer 404s or times out, increment `missCount` and keep the
  last-good artifacts. Only surface a layer for removal after `missCount >= 3` consecutive runs, and
  even then flag it in the run summary for a human — don't silently drop citizen-facing data.
- **`migratedAt` bumps only for layers that actually changed** — so the showcase "Migrated" field
  stays honest per dataset.
- **Commit message is the audit trail:** list changed layers + count deltas, e.g.
  `sync(arcgis): parcels 30694→30696 (+2), trees unchanged; 1/8 layers refreshed`.
- Append one parity row per changed layer to the history ledger (see (b)).

### The scheduled workflow — `.github/workflows/arcgis-sync.yml`

Drop this in the **portal** repo (not the skills repo). It installs the native toolchain, runs the
sync, and commits back. `SITE_ROOT` and the Arc LFS token come from repo secrets.

```yaml
name: arcgis-sync
on:
  schedule:
    - cron: '17 7 * * *'   # nightly 07:17 UTC; tighten/loosen per how fast the Hub edits
  workflow_dispatch: {}     # manual "sync now"
concurrency:
  group: arcgis-sync        # never overlap two syncs
  cancel-in-progress: false
permissions:
  contents: write
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          lfs: false        # pull pointers only; we push new blobs, we don't need old ones
      - name: Install native toolchain
        run: |
          sudo apt-get update
          sudo apt-get install -y gdal-bin duckdb jq
          # tippecanoe: prebuilt release or build from source (cache this step in practice)
          sudo apt-get install -y build-essential libsqlite3-dev zlib1g-dev
          git clone --depth 1 https://github.com/felt/tippecanoe /tmp/tippecanoe
          make -C /tmp/tippecanoe -j2 && sudo make -C /tmp/tippecanoe install
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - name: Run scheduled sync
        env:
          SITE_ROOT:       ${{ secrets.ARCGIS_SITE_ROOT }}
          PORTALJS_TOKEN:  ${{ secrets.PORTALJS_TOKEN }}   # mints the scoped LFS token, per /portaljs-deploy
          PROJECT_SLUG:    ${{ secrets.ARC_PROJECT_SLUG }}
        run: bash scripts/arcgis-sync.sh    # the §(a) detect+apply loop over the ledger
      - name: Commit refreshed data
        run: |
          git config user.name  "arcgis-sync"
          git config user.email "sync@portaljs"
          git add datasets.json arcgis-sync-state.json arcgis-parity-history.jsonl data/
          git commit -m "sync(arcgis): $(cat /tmp/sync-summary.txt)" || echo "no changes"
          git push
```

`scripts/arcgis-sync.sh` is the detect-and-apply loop above, iterating the ledger's `layers`.
After the data commit, **redeploy** the static export (the workflow can `npm run build && npx
portaljs deploy`, or a separate deploy workflow triggers on push — see `/portaljs-deploy`).

### Cadence guidance

Nightly is the sane default; the change detector makes it effectively **per-layer** (only drifting
layers cost anything). If one layer edits hourly and the rest are static, either raise the cron and
rely on detection to skip the static ones, or split hot layers into their own workflow with a
tighter schedule. Don't run tighter than the Hub's own re-import cadence — Lewisville re-imports
nightly, so sub-daily syncs would mostly no-op.

---

## (b) Parity dashboard

Phase 0 writes `arcgis-parity-report.md` for the **latest** run. To see drift *over time* (and prove
the shadow stayed faithful), append a machine-readable row per layer per run to a history ledger,
then render a dashboard from it.

### History ledger — `arcgis-parity-history.jsonl`

One JSON object per line (append-only; never rewritten, so it survives as an audit log):

```
{"run":"2026-07-11T09:12:00Z","slug":"geo/parcels-hosted","source":30694,"derived":30694,"verdict":"PASS","edit":1783741000000}
{"run":"2026-07-14T07:17:00Z","slug":"geo/parcels-hosted","source":30696,"derived":30696,"verdict":"PASS","edit":1783914682041}
```

The sync loop appends to it right after each layer's parity check (§8). `source` = live
`returnCountOnly`; `derived` = `duckdb` count on the fresh parquet; `verdict` = the §8 PASS/WARN/FAIL.

### Render — `arcgis-parity-dashboard.md` (or a portal page)

A small script folds the JSONL into a per-layer table: current counts, drift since first migration,
last successful sync, and the pass/warn/fail streak. Copy-paste:

```bash
node -e '
const fs=require("fs");
const rows=fs.readFileSync("arcgis-parity-history.jsonl","utf8").trim().split("\n").map(JSON.parse);
const by={};for(const r of rows){(by[r.slug] ||= []).push(r);}
let out="# ArcGIS parity dashboard\n\nGenerated from arcgis-parity-history.jsonl.\n\n";
out+="| Layer | Latest source | Latest derived | Verdict | Runs | First→latest Δ | Last sync |\n";
out+="|---|--:|--:|---|--:|--:|---|\n";
for(const [slug,rs] of Object.entries(by)){
  const first=rs[0],last=rs[rs.length-1];
  const d=last.source-first.source;
  out+=`| ${slug} | ${last.source} | ${last.derived} | ${last.verdict} | ${rs.length} | ${d>=0?"+":""}${d} | ${last.run} |\n`;
}
fs.writeFileSync("arcgis-parity-dashboard.md",out);
console.log(out);
'
```

For a **citizen-visible** status page, commit the dashboard as a content page (e.g.
`pages/sync-status.tsx` rendering the markdown, or a `datasets.json` "System" entry) so "how current
is this portal?" is answerable from the site itself. Keep it out of the searchable dataset catalog —
it is operational metadata, not a dataset.

---

## (c) Cutover playbook — preserve old URLs

The migration's SEO/bookmark promise is that `…/datasets/<slug>` links keep working. How you honor
it depends on **who controls the old domain**.

### Slug preservation (do this regardless)

Old Hub dataset URLs carry a slug; the showcase URL is `/@<namespace>/<slug>`. To keep inbound links
meaningful, map the Hub slug → PortalJS slug at migration time instead of re-deriving from the
filename. The DCAT `identifier` (`…item.html?id=<itemId>&sublayer=<n>`) and the Hub `landingPage`
give you the old slug. Persist the old→new mapping in the ledger so (c) can generate any of the
artifacts below.

### Case 1 — you own the domain (custom Hub domain, or the Stream case)

Emit **301 redirects** old path → new showcase. Generate the map from the harvest:

```bash
# crosswalk.tsv: <old_hub_path>\t</@ns/slug>  — built from DCAT landingPage + the emitted datasets.json
jq -r '.dataset[] | [ (.landingPage // .identifier), .title ] | @tsv' dcat.json > /tmp/hub-paths.tsv
# ...join against datasets.json slugs to produce redirect rules:
```

Then wire them where the new portal is served:
- **Cloudflare** (Arc is on Cloudflare): a [Bulk Redirect list](https://developers.cloudflare.com/rules/url-forwarding/bulk-redirects/), or `_redirects` for Pages-style hosting.
- **Next.js self-host:** `redirects()` in `next.config.js` (301, `permanent: true`).

### Case 2 — you do NOT own the domain (Lewisville: `hub-lewisville.opendata.arcgis.com`)

Esri controls `opendata.arcgis.com`, so you **cannot** install redirects on the old URLs. Do the next
best thing — make the new portal discoverable and give humans/bots a map:

1. **`sitemap.xml`** of the new portal (every showcase URL) submitted to Google/Bing Search Console,
   so the new URLs index and gradually outrank the old Hub pages. PortalJS can emit this at build.
2. **Crosswalk page** — a public `crosswalk.md`/`/moved` page listing every old Hub item → its new
   showcase URL, so a citizen with a bookmark can find the new home. Generate it from the same
   old→new mapping used in Case 1.
3. **Link-outs / hand-off request** — ask the city (the AGOL org owner) to add a banner or item
   description link on the ArcGIS Hub pointing at the new portal, and to set the Hub items'
   description to "Moved to <url>". This is the only lever on a domain you don't control, and it is a
   process step, not code — put it in the cutover checklist.
4. **`<link rel="canonical">`** on each new showcase pointing to itself, and (if the city cooperates)
   canonicals on the Hub items pointing to the new portal, to consolidate SEO signal.

Ship a `cutover-checklist.md` in the portal repo tracking: sitemap submitted, crosswalk published,
city notified, canonical set, redirects live (Case 1) or link-out banner live (Case 2).

---

## (d) Post-cutover options

Three futures, in increasing order of Esri independence. Present all three; let the owner choose.

| Option | AGOL role | Editing happens in | Sync (a) | Cost / lock-in | Effort |
|---|---|---|---|---|---|
| **1. Keep AGOL upstream** (status quo Phase 3) | Source of truth | ArcGIS Online | Nightly re-harvest, still on | Still paying Esri; PortalJS is a free public read-shadow | None beyond (a) |
| **2. Git-native publishing** | Retired per-layer | QGIS/CSV → git PR, or a light editor | Off for migrated layers | Drops Esri for those layers; portal becomes source of truth | Per-layer migration + editor training |
| **3. Full Esri exit** | Decommissioned | Open stack (QGIS + GeoParquet/PMTiles, or PostGIS + export) | Replaced by the open pipeline | No Esri cost or lock-in | Highest — retrain, re-tool all layers, plan REST-consumer story |

Decision inputs to document for the owner:
- **Consumer compatibility.** Anything still hitting the old FeatureServer REST endpoints breaks on a
  full exit. If that matters, the **Koop FeatureServer-compat adapter (epic Phase 4)** can serve a
  FeatureServer facade over the GeoParquet, buying a migration window for REST consumers.
- **Editing volume & staff skills.** High-churn layers with GIS staff comfortable in ArcGIS argue for
  Option 1 longer; low-churn reference layers are the easy first candidates for Option 2.
- **Cost.** Option 1 keeps the AGOL bill; 2/3 trade it for staff time and open-tooling setup.

Recommended path for most Cities: **1 → 2 (layer by layer, low-churn first) → 3**, never a big-bang
exit. The shadow portal already de-risks this — the public site is already off Esri from day one of
Phase 1; (d) only decides where *editing* lives.
