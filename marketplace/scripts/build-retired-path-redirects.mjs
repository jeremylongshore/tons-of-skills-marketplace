// Deterministic redirect map for retired tonsofskills.com URLs that still return 404.
//
// Inputs (all tracked):
//   src/data/retired-paths.json          observed 404 paths (analytics window + live re-check)
//   src/data/retired-path-overrides.json reviewed manual decisions (renames, keep-404s)
//   src/data/skills-catalog.json         live skill slugs (generated, drift-gated)
//   ../.claude-plugin/marketplace{,.extended}.json   live plugin pages
//   src/pages/learn/*/index.astro, src/content/playbooks/*.md, src/pages/*.astro   live hubs
//
// Outputs:
//   src/data/retired-path-redirects.json  the reviewed map, one row per normalized path
//   ops/retired-path-redirects.caddy      the ingress projection (HTTP 301, query preserved)
//
// Usage: node scripts/build-retired-path-redirects.mjs [--check]
//   --check  regenerate in memory and fail if either tracked output differs (writes nothing)
//
// Policy: a path redirects only to a page that exists in the current catalog. Nothing ever
// redirects to the home page. A path with no close live counterpart stays a 404 (the site's
// 404 page) with a recorded reason, rather than being funnelled to an unrelated page.
import { createHash } from 'node:crypto';
import { existsSync, readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const MARKETPLACE = join(dirname(fileURLToPath(import.meta.url)), '..');
const REPO = join(MARKETPLACE, '..');
const MAP_PATH = join(MARKETPLACE, 'src/data/retired-path-redirects.json');
const CADDY_PATH = join(MARKETPLACE, 'ops/retired-path-redirects.caddy');

// Section hubs a retired catalog page may fall back to (prior precedent in the live redirect
// file: retired /plugins/* -> /plugins/, retired /learn/* -> /learn/). Never "/".
export const SECTION_INDEXES = ['/plugins/', '/learn/', '/playbooks/'];
// Home is never a target. The allowlist exists so a future exception is an explicit,
// reviewed edit rather than a silent rule change; it is deliberately empty.
export const HOME_ALLOWLIST = [];
// Path segments produced by relative links inside rendered SKILL.md bodies. They never were
// pages, so there is nothing "closest" to send them to.
const LINK_ARTIFACT_SEGMENTS = new Set([
  'reference',
  'references',
  'examples',
  'scripts',
  'assets',
  'templates',
]);
// Only plain URL-path characters are emitted into Caddy; anything else stays a 404.
const SAFE_PATH = /^\/[A-Za-z0-9._~/-]+$/;
const SIMILARITY_FLOOR = 0.6;
const SAME_VENDOR_FLOOR = 0.5;

function readJson(path) {
  return JSON.parse(readFileSync(path, 'utf8'));
}

export function loadLiveUniverse() {
  const skills = readJson(join(MARKETPLACE, 'src/data/skills-catalog.json')).skills;
  const extended = readJson(join(REPO, '.claude-plugin/marketplace.extended.json')).plugins;
  const installable = new Set(
    readJson(join(REPO, '.claude-plugin/marketplace.json')).plugins.map((p) => p.name),
  );
  const plugins = extended.map((p) => p.name).filter((name) => installable.has(name));
  const learnDir = join(MARKETPLACE, 'src/pages/learn');
  const learn = readdirSync(learnDir, { withFileTypes: true })
    .filter((d) => d.isDirectory() && existsSync(join(learnDir, d.name, 'index.astro')))
    .map((d) => d.name);
  const playbooks = readdirSync(join(MARKETPLACE, 'src/content/playbooks'))
    .filter((f) => f.endsWith('.md'))
    .map((f) => f.replace(/\.md$/, ''));
  // Top-level pages that render content (a page whose frontmatter only redirects is not one).
  const staticPages = readdirSync(join(MARKETPLACE, 'src/pages'))
    .filter((f) => f.endsWith('.astro') && f !== 'index.astro' && f !== '404.astro')
    .filter((f) => !readFileSync(join(MARKETPLACE, 'src/pages', f), 'utf8').includes('Astro.redirect'))
    .map((f) => f.replace(/\.astro$/, ''));
  const docsDir = join(MARKETPLACE, 'src/content/docs');
  const docs = readdirSync(docsDir, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .flatMap((d) =>
      readdirSync(join(docsDir, d.name))
        .filter((f) => /\.mdx?$/.test(f))
        .map((f) => `${d.name}/${f.replace(/\.mdx?$/, '')}`),
    );

  const skillParent = new Map(skills.map((s) => [s.slug, s.parentPlugin?.name ?? null]));
  const routes = new Set([
    ...SECTION_INDEXES,
    '/skills/',
    ...skills.map((s) => `/skills/${s.slug}/`),
    ...plugins.map((n) => `/plugins/${n}/`),
    ...learn.map((v) => `/learn/${v}/`),
    ...playbooks.map((p) => `/playbooks/${p}/`),
    ...staticPages.map((p) => `/${p}/`),
    ...docs.map((d) => `/docs/${d}/`),
  ]);
  return {
    skills: [...skillParent.keys()].sort(),
    skillParent,
    plugins: new Set(plugins),
    pluginList: [...plugins].sort(),
    learn: new Set(learn),
    playbooks: new Set(playbooks),
    routes,
  };
}

const tokens = (slug) => slug.split('-').filter(Boolean);

function jaccard(a, b) {
  const A = new Set(a);
  const B = new Set(b);
  let shared = 0;
  for (const t of A) if (B.has(t)) shared += 1;
  const union = A.size + B.size - shared;
  return { score: union === 0 ? 0 : shared / union, shared };
}

// Highest-scoring candidate; ties break lexicographically so the result is stable.
function bestMatch(slug, candidates, { floor, dropFirstToken = false }) {
  const mine = dropFirstToken ? tokens(slug).slice(1) : tokens(slug);
  let best = null;
  for (const candidate of candidates) {
    if (candidate === slug) continue;
    const theirs = dropFirstToken ? tokens(candidate).slice(1) : tokens(candidate);
    const { score, shared } = jaccard(mine, theirs);
    // A single shared token is only meaningful when the retired slug is itself one token.
    if (shared === 0 || (shared < 2 && mine.length > 1)) continue;
    if (score < floor) continue;
    if (!best || score > best.score || (score === best.score && candidate < best.slug)) {
      best = { slug: candidate, score };
    }
  }
  return best;
}

export function normalize(path) {
  const stripped = path.replace(/\/+$/, '');
  return stripped === '' ? '/' : stripped;
}

function matchSkill(segments, live) {
  const [slug, ...rest] = segments;
  if (LINK_ARTIFACT_SEGMENTS.has(slug)) return { status: 404, rule: 'relative-link-artifact' };
  if (live.skillParent.has(slug)) {
    return rest.length
      ? { status: 301, to: `/skills/${slug}/`, rule: 'live-parent-page' }
      : { status: 404, rule: 'already-live' };
  }
  const deduped = slug.replace(/-\d+$/, '');
  if (deduped !== slug && live.skillParent.has(deduped)) {
    return { status: 301, to: `/skills/${deduped}/`, rule: 'duplicate-suffix' };
  }
  const vendor = tokens(slug)[0];
  const sameVendor = live.skills.filter((s) => s.startsWith(`${vendor}-`));
  if (sameVendor.length && tokens(slug).length > 1) {
    const hit = bestMatch(slug, sameVendor, { floor: SAME_VENDOR_FLOOR, dropFirstToken: true });
    if (hit) return { status: 301, to: `/skills/${hit.slug}/`, rule: 'same-vendor-similar-skill' };
    // The vendor still ships a pack: its plugin page is the closest live page, but only when
    // every surviving vendor skill belongs to one plugin named for that vendor.
    const parents = new Set(sameVendor.map((s) => live.skillParent.get(s)));
    const [pack] = parents;
    if (parents.size === 1 && pack?.startsWith(`${vendor}-`) && live.plugins.has(pack)) {
      return { status: 301, to: `/plugins/${pack}/`, rule: 'vendor-pack-page' };
    }
  }
  // Renamed-by-extension: a live skill whose slug contains every token of the retired one
  // (e.g. `contagious` -> `contagious-marketing`). Cross-vendor template matches such as
  // `perplexity-core-workflow-a` -> `abridge-core-workflow-a` are exactly what this excludes.
  const mine = tokens(slug);
  const extension = live.skills.filter((s) => {
    const theirs = new Set(tokens(s));
    return theirs.size > 0 && tokens(s)[0] === mine[0] && mine.every((t) => theirs.has(t));
  });
  const global = bestMatch(slug, extension, { floor: SIMILARITY_FLOOR });
  if (global) return { status: 301, to: `/skills/${global.slug}/`, rule: 'renamed-skill' };
  if (live.plugins.has(slug)) return { status: 301, to: `/plugins/${slug}/`, rule: 'same-name-plugin' };
  return { status: 404, rule: 'no-close-match' };
}

function matchPlugin(segments, live) {
  const [name, ...rest] = segments;
  // `/plugins/references/x.md`, `/plugins/README.fr.md`: relative links out of a README.
  if (LINK_ARTIFACT_SEGMENTS.has(name) || name.includes('.')) {
    return { status: 404, rule: 'relative-link-artifact' };
  }
  if (live.plugins.has(name)) {
    return rest.length
      ? { status: 301, to: `/plugins/${name}/`, rule: 'live-parent-page' }
      : { status: 404, rule: 'already-live' };
  }
  // `/plugins/<category>/<name>`: the repository directory layout, not the site's route.
  if (rest.length && live.plugins.has(rest[0])) {
    return { status: 301, to: `/plugins/${rest[0]}/`, rule: 'category-path' };
  }
  const alt = name.endsWith('-pack') ? name.slice(0, -5) : `${name}-pack`;
  if (live.plugins.has(alt)) return { status: 301, to: `/plugins/${alt}/`, rule: 'pack-suffix-rename' };
  const hit = bestMatch(name, live.pluginList, { floor: SIMILARITY_FLOOR });
  if (hit) return { status: 301, to: `/plugins/${hit.slug}/`, rule: 'similar-plugin' };
  if (live.skillParent.has(name)) return { status: 301, to: `/skills/${name}/`, rule: 'same-name-skill' };
  return { status: 301, to: '/plugins/', rule: 'retired-plugin-section-index' };
}

function matchLearn(segments, live) {
  const [vendor] = segments;
  if (live.learn.has(vendor)) return { status: 301, to: `/learn/${vendor}/`, rule: 'live-parent-page' };
  if (live.plugins.has(`${vendor}-pack`)) {
    return { status: 301, to: `/plugins/${vendor}-pack/`, rule: 'vendor-pack-page' };
  }
  return { status: 301, to: '/learn/', rule: 'retired-learn-section-index' };
}

function matchPlaybook(segments, live) {
  const leaf = segments[segments.length - 1].replace(/\.md$/, '');
  if (live.playbooks.has(leaf)) return { status: 301, to: `/playbooks/${leaf}/`, rule: 'playbook-source-link' };
  return { status: 301, to: '/playbooks/', rule: 'retired-playbook-section-index' };
}

export function decide(path, live, overrides) {
  const key = normalize(path);
  if (Object.hasOwn(overrides, key)) {
    const o = overrides[key];
    return o.to
      ? { status: 301, to: o.to, rule: 'reviewed-override', note: o.reason }
      : { status: 404, rule: 'reviewed-keep-404', note: o.reason };
  }
  if (!SAFE_PATH.test(key)) return { status: 404, rule: 'malformed-path' };
  const [section, ...segments] = key.split('/').slice(1);
  if (section === 'skills' && segments.length) return matchSkill(segments, live);
  if (section === 'plugins' && segments.length) return matchPlugin(segments, live);
  if (section === 'learn' && segments.length === 1) return matchLearn(segments, live);
  if (section === 'playbooks' && segments.length) return matchPlaybook(segments, live);
  return { status: 404, rule: 'outside-catalog' };
}

export function buildMap() {
  const inventory = readJson(join(MARKETPLACE, 'src/data/retired-paths.json'));
  const overrides = readJson(join(MARKETPLACE, 'src/data/retired-path-overrides.json')).overrides;
  const live = loadLiveUniverse();

  const groups = new Map();
  for (const path of inventory.paths) {
    const key = normalize(path);
    if (!groups.has(key)) groups.set(key, new Set());
    groups.get(key).add(path);
  }
  const entries = [...groups.keys()].sort().map((key) => ({
    from: key,
    observed: [...groups.get(key)].sort(),
    ...decide(key, live, overrides),
  }));

  const redirected = entries.filter((e) => e.status === 301);
  const byRule = {};
  for (const e of entries) byRule[e.rule] = (byRule[e.rule] ?? 0) + 1;
  const observedRedirected = redirected.reduce((n, e) => n + e.observed.length, 0);
  return {
    schemaVersion: 1,
    generatedBy: 'marketplace/scripts/build-retired-path-redirects.mjs',
    stats: {
      observedPaths: inventory.paths.length,
      normalizedPaths: entries.length,
      redirected: redirected.length,
      observedPathsRedirected: observedRedirected,
      kept404: entries.length - redirected.length,
      observedPathsKept404: inventory.paths.length - observedRedirected,
      byRule: Object.fromEntries(Object.entries(byRule).sort()),
    },
    entries,
  };
}

// Caddy needs both slash forms per path. The `retired` matcher prefix keeps these distinct
// from the hand-installed `@redirNNN` block the installer checks for collisions. IDs are a
// hash of the path, so adding or removing one entry does not renumber every other line.
export const matcherId = (from) =>
  `@retired${createHash('sha256').update(from).digest('hex').slice(0, 12)}`;
export function renderCaddy(map) {
  const lines = [
    '# Retired tonsofskills.com URLs — generated by marketplace/scripts/build-retired-path-redirects.mjs',
    '# from src/data/retired-path-redirects.json. Do not hand-edit; regenerate.',
    '# Each matcher covers both slash forms; `permanent` emits HTTP 301 and {?query} keeps the query string.',
    '',
  ];
  map.entries
    .filter((e) => e.status === 301)
    .forEach((e) => {
      const id = matcherId(e.from);
      lines.push(`${id} path ${e.from} ${e.from}/`, `redir ${id} ${e.to}{?query} permanent`);
    });
  return `${lines.join('\n')}\n`;
}

const isMain = process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1];
if (isMain) {
  const map = buildMap();
  const json = `${JSON.stringify(map, null, 2)}\n`;
  const caddy = renderCaddy(map);
  if (process.argv.includes('--check')) {
    const stale = [];
    if (!existsSync(MAP_PATH) || readFileSync(MAP_PATH, 'utf8') !== json) stale.push(MAP_PATH);
    if (!existsSync(CADDY_PATH) || readFileSync(CADDY_PATH, 'utf8') !== caddy) stale.push(CADDY_PATH);
    if (stale.length) {
      console.error(`retired-path redirects are stale; regenerate:\n  ${stale.join('\n  ')}`);
      process.exit(1);
    }
    console.log('retired-path redirects are current');
  } else {
    writeFileSync(MAP_PATH, json);
    writeFileSync(CADDY_PATH, caddy);
  }
  console.log(JSON.stringify(map.stats));
}
