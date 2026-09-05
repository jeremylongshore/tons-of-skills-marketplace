#!/usr/bin/env node
/**
 * generate-plugin-package-jsons.mjs
 *
 * For every plugin in `plugins/**` that has a `.claude-plugin/plugin.json` but
 * no sibling `package.json`, generate one following the @intentsolutionsio
 * scope + <slug> naming convention.
 *
 * npm packages are a TRACKING/PROOF layer only (D1=B). Installation remains
 * via the marketplace (`ccpi install <slug>` or `/plugin install <slug>`).
 *
 * Usage:
 *   node scripts/generate-plugin-package-jsons.mjs            # write files
 *   node scripts/generate-plugin-package-jsons.mjs --dry-run  # show plan only
 *   node scripts/generate-plugin-package-jsons.mjs --probe    # dry-run + npm registry collision check
 */

import { existsSync, readFileSync, readdirSync, statSync, writeFileSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

// `URL.pathname` is platform-independent and keeps a leading slash before a
// Windows drive letter, so `/C:/repo/scripts/x.mjs` makes `resolve()` read the
// path as drive-relative and prepend the current drive -- ROOT becomes
// `C:\C:\repo`. `fileURLToPath` answers correctly on every platform.
// See issue #1436.
const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const PLUGINS_DIR = join(ROOT, 'plugins');
// Must be the canonical repo slug (not the legacy `/claude-code-plugins`
// redirect). npm provenance rejects the publish if this doesn't match the
// actual repository GitHub Actions is running in.
const REPO_URL = 'https://github.com/jeremylongshore/tons-of-skills-marketplace';
const SCOPE = '@intentsolutionsio';
const LEGACY_REPO_URLS = [
  'https://github.com/jeremylongshore/claude-code-plugins-plus-skills',
  'https://github.com/jeremylongshore/claude-code-plugins',
];

// FS-only / personal-prefix dirs and known duplicates — skip entirely.
const EXCLUDE_PREFIXES = [
  join(PLUGINS_DIR, 'jeremy-google-adk'),
  join(PLUGINS_DIR, 'jeremy-vertex-ai'),
  join(PLUGINS_DIR, 'saas-packs', 'skill-databases'),
];

function isExcluded(pluginDir) {
  return EXCLUDE_PREFIXES.some((p) => pluginDir === p || pluginDir.startsWith(p + '/'));
}

function walkPluginDirs(root) {
  // Plugin root = any directory containing plugin.json (either at the
  // canonical .claude-plugin/plugin.json location or at the plugin root —
  // some 3rd-party contributions use the old root layout).
  const found = [];
  function walk(dir) {
    let entries;
    try {
      entries = readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    const hasPluginJson =
      existsSync(join(dir, '.claude-plugin', 'plugin.json')) ||
      existsSync(join(dir, 'plugin.json'));
    if (hasPluginJson) {
      found.push(dir);
      // A synced plugin (.source.json marker) is a vendored upstream tree:
      // generate exactly ONE top-level package.json for it and do NOT descend
      // into nested upstream plugin.json files (e.g. tonone/bundle/*), which
      // the CI structure check (find -maxdepth 4) would otherwise scaffold
      // spurious package.jsons for.
      if (existsSync(join(dir, '.source.json'))) return;
      // Otherwise still descend — rare nested first-party plugins exist (e.g.
      // the historical saas-packs/skill-databases/windsurf duplicate); the
      // exclusion list handles them.
    }
    for (const ent of entries) {
      if (!ent.isDirectory()) continue;
      // Skip internals that can't themselves be plugin roots.
      if (ent.name === 'node_modules' || ent.name === '.git' || ent.name === 'dist') continue;
      if (ent.name === '.claude-plugin') continue;
      if (ent.name === 'skills' || ent.name === 'commands' || ent.name === 'agents') continue;
      if (ent.name === 'hooks' || ent.name === 'scripts' || ent.name === 'references') continue;
      walk(join(dir, ent.name));
    }
  }
  walk(root);
  return found;
}

function readPluginJson(pluginDir) {
  const canonical = join(pluginDir, '.claude-plugin', 'plugin.json');
  const fallback = join(pluginDir, 'plugin.json');
  if (existsSync(canonical)) return readJson(canonical);
  if (existsSync(fallback)) return readJson(fallback);
  throw new Error(`no plugin.json at ${pluginDir}`);
}

function readJson(path) {
  return JSON.parse(readFileSync(path, 'utf-8'));
}

function slugFromPath(pluginDir) {
  return pluginDir.split('/').pop();
}

function scopedName(slug) {
  return `${SCOPE}/${slug}`;
}

// npm package names: lowercase, URL-safe, no spaces, max 214 chars. Our slugs
// are already kebab-case from plugin directory names, so pass-through.
function isValidNpmName(name) {
  if (name.length > 214) return false;
  const body = name.startsWith('@') ? name.slice(name.indexOf('/') + 1) : name;
  return /^[a-z0-9][a-z0-9._-]*$/.test(body);
}

function buildPackageJson(pluginDir, pluginJson) {
  const slug = slugFromPath(pluginDir);
  const relDir = relative(ROOT, pluginDir);
  const name = scopedName(slug);
  const description = (pluginJson.description || `Claude Code plugin: ${slug}`)
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 200);

  // Pull keywords from plugin.json, normalize, add standard tags.
  const baseKeywords = Array.isArray(pluginJson.keywords) ? pluginJson.keywords : [];
  const keywords = Array.from(
    new Set(
      [...baseKeywords, 'claude-code', 'claude-plugin', 'tonsofskills'].map((k) =>
        String(k).toLowerCase().trim(),
      ),
    ),
  ).slice(0, 20); // npm soft-limits keywords; keep it reasonable

  // Only include files that actually exist in the plugin directory.
  const candidateFiles = [
    'README.md',
    '.claude-plugin',
    'skills',
    'commands',
    'agents',
    'hooks',
    'scripts',
  ];
  const files = candidateFiles.filter((f) => existsSync(join(pluginDir, f)));
  // Always ship README if present; if not, fall back to whatever exists.
  if (!files.includes('README.md') && existsSync(join(pluginDir, 'README.md'))) {
    files.unshift('README.md');
  }

  const pkg = {
    name,
    version:
      pluginJson.version && /^\d+\.\d+\.\d+/.test(pluginJson.version)
        ? pluginJson.version
        : '1.0.0',
    description,
    keywords,
    repository: {
      type: 'git',
      url: `git+${REPO_URL}.git`,
      directory: relDir,
    },
    homepage: `https://tonsofskills.com/plugins/${slug}`,
    bugs: `${REPO_URL}/issues`,
    license: pluginJson.license || 'MIT',
    author: pluginJson.author || {
      name: 'Jeremy Longshore',
      email: 'jeremy@intentsolutions.io',
      url: 'https://github.com/jeremylongshore',
    },
    publishConfig: { access: 'public' },
    files,
    scripts: {
      postinstall:
        'node -e "console.log(\\"\\\\n→ This npm package is a tracking/proof artifact. Install the plugin via:\\\\n  ccpi install ' +
        slug +
        '\\\\n  or /plugin install ' +
        slug +
        '@claude-code-plugins-plus in Claude Code\\\\n\\")"',
    },
  };

  return pkg;
}

export function reconcileGeneratedPackageMetadata(pkg, relDir, { sourceOwned = false } = {}) {
  if (sourceOwned) return { changed: false, pkg };
  const repositoryUrl = typeof pkg?.repository === 'object' ? pkg.repository?.url : null;
  const managedByRepositoryPolicy =
    pkg?.name?.startsWith(`${SCOPE}/`) ||
    (pkg?.repository?.directory === relDir &&
      /^git\+https:\/\/github\.com\/jeremylongshore\/(?:claude-code-plugins(?:-plus-skills)?|tons-of-skills-marketplace)\.git$/.test(
        repositoryUrl ?? '',
      ));
  if (!managedByRepositoryPolicy) return { changed: false, pkg };
  const rewritten = rewriteLegacyRepositoryUrls(JSON.stringify(pkg));
  if (rewritten === JSON.stringify(pkg)) return { changed: false, pkg };
  return {
    changed: true,
    pkg: JSON.parse(rewritten),
  };
}

export function rewriteLegacyRepositoryUrls(source) {
  return LEGACY_REPO_URLS.reduce(
    (current, legacyUrl) => current.replaceAll(legacyUrl, REPO_URL),
    source,
  );
}

async function probeNpmRegistry(name) {
  try {
    const res = await fetch(`https://registry.npmjs.org/${encodeURIComponent(name)}`, {
      method: 'HEAD',
    });
    // 200 = exists (could be ours or a collision)
    // 404 = free
    return res.status;
  } catch {
    return -1;
  }
}

async function collisionCheck(names, { concurrency = 10 } = {}) {
  const hits = new Map(); // name -> status
  let i = 0;
  async function worker() {
    while (i < names.length) {
      const idx = i++;
      const name = names[idx];
      const status = await probeNpmRegistry(name);
      hits.set(name, status);
    }
  }
  const workers = Array.from({ length: concurrency }, () => worker());
  await Promise.all(workers);
  return hits;
}

/**
 * Refuse to report success on an empty discovery.
 *
 * This script's failure mode is silence: `walkPluginDirs` swallows a
 * `readdirSync` error and returns `[]`, so a ROOT pointing at nothing globs
 * nothing, prints `Wrote 0 package.json files.` and exits 0. That is what made
 * issue #1436's first half invisible -- the doubled-drive-letter ROOT produced
 * `Plugins with package.json already: 0` on a tree holding 440, and only the
 * TOC generator further down the `sync-marketplace` chain failed loudly.
 *
 * A run that discovers no plugins in this repository has not done its job, so
 * it exits non-zero rather than letting a green step stand for a completed one.
 * The message names the resolved ROOT, because when this fires the resolved
 * path is the whole diagnosis.
 */
function assertDiscoveryNonEmpty(pluginDirs) {
  if (!existsSync(PLUGINS_DIR)) {
    console.error(
      `No plugins directory at ${PLUGINS_DIR}.
` +
        `Resolved ROOT: ${ROOT}
` +
        'A doubled drive letter here means ROOT was derived from URL.pathname; ' +
        'see issue #1436.',
    );
    process.exit(1);
  }
  if (pluginDirs.length === 0) {
    console.error(
      `Discovered 0 plugins under ${PLUGINS_DIR}.
` +
        `Resolved ROOT: ${ROOT}
` +
        'Refusing to report success on an empty discovery: this repository has ' +
        'plugins, so zero means the walk looked in the wrong place or could not ' +
        'read it.',
    );
    process.exit(1);
  }
}

async function main() {
  const args = process.argv.slice(2);
  const dryRun = args.includes('--dry-run') || args.includes('--probe');
  const probe = args.includes('--probe');

  const pluginDirs = walkPluginDirs(PLUGINS_DIR);
  assertDiscoveryNonEmpty(pluginDirs);
  const needsScaffold = [];
  const skipped = [];
  const existing = [];
  const metadataUpdates = [];

  for (const pluginDir of pluginDirs) {
    if (isExcluded(pluginDir)) {
      skipped.push({ pluginDir, reason: 'excluded (personal-prefix or known duplicate)' });
      continue;
    }
    if (existsSync(join(pluginDir, 'package.json'))) {
      const packagePath = join(pluginDir, 'package.json');
      const source = readFileSync(packagePath, 'utf-8');
      const pkg = JSON.parse(source);
      const reconciled = reconcileGeneratedPackageMetadata(pkg, relative(ROOT, pluginDir), {
        sourceOwned: existsSync(join(pluginDir, '.source.json')),
      });
      existing.push(pluginDir);
      if (reconciled.changed) {
        metadataUpdates.push({ packagePath, source: rewriteLegacyRepositoryUrls(source) });
      }
      continue;
    }
    const pluginJson = readPluginJson(pluginDir);
    const slug = slugFromPath(pluginDir);
    const candidateName = scopedName(slug);
    if (!isValidNpmName(candidateName)) {
      skipped.push({ pluginDir, reason: `invalid npm name: ${candidateName}` });
      continue;
    }
    needsScaffold.push({ pluginDir, slug, candidateName, pluginJson });
  }

  console.log(`Plugins with package.json already: ${existing.length}`);
  console.log(`Generated metadata to reconcile:   ${metadataUpdates.length}`);
  console.log(`Plugins to scaffold:                ${needsScaffold.length}`);
  console.log(`Skipped (excluded/invalid):         ${skipped.length}`);
  if (skipped.length) {
    for (const s of skipped) {
      console.log(`  - ${relative(ROOT, s.pluginDir)}: ${s.reason}`);
    }
  }

  if (probe) {
    console.log(`\nProbing npm registry for ${needsScaffold.length} candidate names...`);
    const names = needsScaffold.map((n) => n.candidateName);
    const statuses = await collisionCheck(names);
    const collisions = [];
    const free = [];
    const errors = [];
    for (const [name, status] of statuses) {
      if (status === 404) free.push(name);
      else if (status === 200) collisions.push(name);
      else errors.push(`${name} (HTTP ${status})`);
    }
    console.log(`  free (404):        ${free.length}`);
    console.log(`  already on npm:    ${collisions.length}`);
    console.log(`  unresolved:        ${errors.length}`);
    if (collisions.length) {
      console.log('\n  ⚠ Collisions — these names already exist on npm:');
      for (const c of collisions.slice(0, 30)) console.log(`    - ${c}`);
      if (collisions.length > 30) console.log(`    ... and ${collisions.length - 30} more`);
    }
    if (errors.length) {
      console.log('\n  ⚠ Unresolved (transient registry errors):');
      for (const e of errors.slice(0, 10)) console.log(`    - ${e}`);
    }
  }

  if (dryRun) {
    console.log('\nDry-run mode. No files written.');
    return;
  }

  let written = 0;
  for (const { pluginDir, pluginJson } of needsScaffold) {
    const pkg = buildPackageJson(pluginDir, pluginJson);
    const out = JSON.stringify(pkg, null, 2) + '\n';
    writeFileSync(join(pluginDir, 'package.json'), out);
    written++;
  }
  for (const { packagePath, source } of metadataUpdates) {
    writeFileSync(packagePath, source);
  }
  console.log(`\nWrote ${written} package.json files.`);
  console.log(`Reconciled ${metadataUpdates.length} generated package.json files.`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  main().catch((err) => {
    console.error(err);
    process.exit(1);
  });
}
