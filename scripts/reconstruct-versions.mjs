#!/usr/bin/env node
/**
 * reconstruct-versions.mjs
 *
 * One-shot reconstruction of real per-plugin versions from full git history,
 * written to the three DISPLAY surfaces that browse UIs actually read:
 *
 *   1. plugins/<...>/.claude-plugin/plugin.json  "version"   (tonsofskills.com plugin cards)
 *   2. .claude-plugin/marketplace.extended.json  per-entry   (→ marketplace.json → /plugin browser)
 *   3. plugins/<...>/**\/SKILL.md frontmatter    version     (tonsofskills.com skill cards)
 *
 * package.json is deliberately NOT touched — that surface drives npm publish
 * and already moves via auto-bump-changed-plugins.mjs.
 *
 * Why this exists: until 2026-07-12 nothing ever bumped ANY version surface,
 * and the auto-bumper added then only edits package.json — so the display
 * surfaces froze at ~1.0.0 while plugins were updated dozens of times.
 *
 * Version formula (approved 2026-07-16):
 *   updates(plugin)  = number of distinct first-parent commits on main that
 *                      touched the plugin dir with at least one file other
 *                      than its own package.json, MINUS the commit that
 *                      introduced the dir (creation is not an update).
 *                      Bulk sweeps are single commits, so they count as ONE
 *                      update by construction.
 *   derived          = { major: existing.major, minor: updates, patch: 0 }
 *   final            = semver-max(existing, derived)   // never downgrade
 *
 * Carve-outs:
 *   - external mirror plugins (dir contains .source.json): skipped entirely —
 *     upstream owns their versioning.
 *   - catalog entries whose source is not ./plugins/... : skipped, reported.
 *
 * Usage:
 *   node scripts/reconstruct-versions.mjs --dry-run             # plan + histogram
 *   node scripts/reconstruct-versions.mjs --execute             # write all surfaces
 *   node scripts/reconstruct-versions.mjs --check               # verify 3-surface agreement
 *   node scripts/reconstruct-versions.mjs --execute --report out.json
 *
 * Exit codes: 0 ok · 1 preflight/parse failure · 2 --check found disagreement
 */

import { spawnSync } from 'node:child_process';
import { existsSync, readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { parseVersion, compareVersion } from './auto-bump-changed-plugins.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const CATALOG = join(ROOT, '.claude-plugin', 'marketplace.extended.json');
const CLI_CATALOG = join(ROOT, '.claude-plugin', 'marketplace.json');

function fmt(v) {
  return `${v.major}.${v.minor}.${v.patch}`;
}

// Same dir-mapping rule as auto-bump-changed-plugins.mjs / publish-changed-packages.yml.
export function pluginDirFor(relPath) {
  const parts = relPath.split('/');
  if (parts[0] !== 'plugins' || parts.length < 3) return null;
  if (parts[1] === 'saas-packs' && parts[2] === 'skill-databases' && parts.length >= 4) {
    return parts.slice(0, 4).join('/');
  }
  return parts.slice(0, 3).join('/');
}

// Agreement mode reads only the checked-out display surfaces. Reconstructing
// a version, by contrast, derives a count from complete first-parent history.
// Keep that distinction explicit so the blocking CI agreement check works in
// GitHub Actions' intentionally shallow checkout without weakening history
// reconstruction.
export function requiresFullHistory({ check }) {
  return !check;
}

// ---------------------------------------------------------------------------
// History pass: one `git log` over full first-parent main history.
// Returns Map<dir, { commits: [{sha, subject}] }> where each listed commit
// touched the dir with >=1 file that is not the dir's own package.json.
// Commits are ordered newest-first (git log order).
// ---------------------------------------------------------------------------
export function collectHistory() {
  const res = spawnSync(
    'git',
    ['log', '--first-parent', '--name-only', '--pretty=format:@@%H%x09%s'],
    { cwd: ROOT, encoding: 'utf-8', shell: false, maxBuffer: 512 * 1024 * 1024 },
  );
  if (res.status !== 0) {
    throw new Error(`git log failed: ${res.stderr || 'non-zero exit'}`);
  }
  const byDir = new Map();
  let sha = null;
  let subject = null;
  let touched = null; // Map<dir, meaningful:boolean> for the current commit
  const flush = () => {
    if (!sha || !touched) return;
    for (const [dir, meaningful] of touched) {
      if (!meaningful) continue;
      const rec = byDir.get(dir) || { commits: [] };
      rec.commits.push({ sha, subject });
      byDir.set(dir, rec);
    }
  };
  for (const line of res.stdout.split('\n')) {
    if (line.startsWith('@@')) {
      flush();
      const tab = line.indexOf('\t');
      sha = line.slice(2, tab === -1 ? undefined : tab);
      subject = tab === -1 ? '' : line.slice(tab + 1);
      touched = new Map();
      continue;
    }
    const file = line.trim();
    if (!file || !touched) continue;
    const dir = pluginDirFor(file);
    if (!dir) continue;
    const meaningful = file !== `${dir}/package.json`;
    touched.set(dir, touched.get(dir) || meaningful);
  }
  flush();
  return byDir;
}

// ---------------------------------------------------------------------------
// Surface writers — all string-level so unrelated formatting never changes.
// ---------------------------------------------------------------------------

// plugin.json: exact `"version": "X.Y.Z"` line replacement (applyPatchBump pattern).
function editPluginJson(dir, newVersion) {
  const abs = join(ROOT, dir, '.claude-plugin', 'plugin.json');
  // Read directly and treat ENOENT as absent, instead of an existence check
  // followed by a separate read of the same path.
  let raw;
  try {
    raw = readFileSync(abs, 'utf-8');
  } catch (error) {
    if (error.code === 'ENOENT') return { skipped: 'no plugin.json' };
    throw error;
  }
  let old;
  try {
    old = JSON.parse(raw).version;
  } catch {
    return { skipped: 'unparseable plugin.json' };
  }
  if (!old) return { skipped: 'no version field' };
  if (old === newVersion) return { old, unchanged: true };
  const oldLine = `"version": "${old}"`;
  if (!raw.includes(oldLine)) return { skipped: `exact version line not found (${old})` };
  writeFileSync(abs, raw.replace(oldLine, `"version": "${newVersion}"`));
  return { old };
}

// marketplace.extended.json: anchor each edit on the entry's unique
// `"source": "..."` line, then replace the FIRST `"version": "` after it —
// verified to (a) sit before the next `"source":` and (b) hold the value the
// parsed entry declares. Aborts loudly on any ambiguity.
export function editCatalogVersions(raw, edits) {
  // Dedupe by source — the catalog contains a few duplicate entries pointing
  // at the same dir; they must all agree, and each occurrence gets patched.
  const bySource = new Map();
  for (const e of edits) {
    if (e.oldVersion === e.newVersion) continue;
    const prev = bySource.get(e.source);
    if (prev && (prev.oldVersion !== e.oldVersion || prev.newVersion !== e.newVersion)) {
      throw new Error(`catalog: conflicting edits for duplicate source ${e.source}`);
    }
    bySource.set(e.source, e);
  }
  let out = raw;
  const applied = [];
  for (const { source, oldVersion, newVersion } of bySource.values()) {
    const srcNeedle = `"source": ${JSON.stringify(source)}`;
    const vNeedle = `"version": ${JSON.stringify(oldVersion)}`;
    let i = out.indexOf(srcNeedle);
    if (i === -1) throw new Error(`catalog: source anchor not found: ${source}`);
    while (i !== -1) {
      const j = out.indexOf(vNeedle, i);
      if (j === -1) throw new Error(`catalog: version "${oldVersion}" not found after ${source}`);
      const nextSrc = out.indexOf('"source": ', i + srcNeedle.length);
      if (nextSrc !== -1 && j > nextSrc) {
        throw new Error(`catalog: version for ${source} crosses into the next entry`);
      }
      out =
        out.slice(0, j) +
        `"version": ${JSON.stringify(newVersion)}` +
        out.slice(j + vNeedle.length);
      applied.push(source);
      i = out.indexOf(srcNeedle, j);
    }
  }
  return { out, applied };
}

// Single-entry variant used by auto-bump-changed-plugins.mjs at PR time:
// set one catalog entry's version (whatever it currently is) to newVersion,
// patching every occurrence of the source anchor (the catalog carries a few
// duplicate entries for the same dir). Returns { out, old } or null when the
// source isn't in this catalog file (e.g. packages/* dirs).
export function setCatalogEntryVersion(raw, source, newVersion) {
  const srcNeedle = `"source": ${JSON.stringify(source)}`;
  let i = raw.indexOf(srcNeedle);
  if (i === -1) return null;
  let out = raw;
  let old = null;
  while (i !== -1) {
    const j = out.indexOf('"version": "', i);
    if (j === -1) throw new Error(`catalog: no version field after ${source}`);
    const nextSrc = out.indexOf('"source": ', i + srcNeedle.length);
    if (nextSrc !== -1 && j > nextSrc) {
      throw new Error(`catalog: version for ${source} crosses into the next entry`);
    }
    const m = /^"version": "([^"]+)"/.exec(out.slice(j, j + 200));
    if (!m) throw new Error(`catalog: unparseable version line after ${source}`);
    old = m[1];
    const replacement = `"version": ${JSON.stringify(newVersion)}`;
    out = out.slice(0, j) + replacement + out.slice(j + m[0].length);
    i = out.indexOf(srcNeedle, j + replacement.length);
  }
  return { out, old };
}

// SKILL.md frontmatter: handles top-level `version:` and nested
// `metadata:` → `  version:` forms. Only replaces an existing field.
export function editSkillFrontmatter(raw, newVersion) {
  if (!raw.startsWith('---\n')) return { skipped: 'no frontmatter' };
  const end = raw.indexOf('\n---', 3);
  if (end === -1) return { skipped: 'unterminated frontmatter' };
  const fm = raw.slice(4, end);
  const lines = fm.split('\n');

  // Pass 1: top-level version.
  let idx = lines.findIndex((l) => /^version:\s*\S/.test(l));
  // Pass 2: metadata.version (first indented `version:` inside a metadata: block).
  if (idx === -1) {
    let inMeta = false;
    for (let k = 0; k < lines.length; k++) {
      if (/^metadata:\s*$/.test(lines[k])) {
        inMeta = true;
        continue;
      }
      if (inMeta && /^\S/.test(lines[k])) inMeta = false;
      if (inMeta && /^\s+version:\s*\S/.test(lines[k])) {
        idx = k;
        break;
      }
    }
  }
  if (idx === -1) return { skipped: 'no version field' };

  const m = /^(\s*version:\s*)(['"]?)([^'"\s#]+)\2(\s*(#.*)?)$/.exec(lines[idx]);
  if (!m) return { skipped: `unparseable version line: ${lines[idx].trim()}` };
  const old = m[3];
  if (old === newVersion) return { old, unchanged: true };
  lines[idx] = `${m[1]}${m[2]}${newVersion}${m[2]}${m[4] || ''}`;
  return { old, out: raw.slice(0, 4) + lines.join('\n') + raw.slice(end) };
}

export function findSkillFiles(dir) {
  const out = [];
  const walk = (d) => {
    for (const ent of readdirSync(join(ROOT, d), { withFileTypes: true })) {
      if (ent.name === 'node_modules' || ent.name.startsWith('.')) continue;
      const rel = `${d}/${ent.name}`;
      if (ent.isDirectory()) walk(rel);
      else if (ent.name === 'SKILL.md') out.push(rel);
    }
  };
  walk(dir);
  return out;
}

// ---------------------------------------------------------------------------
// main
// ---------------------------------------------------------------------------
function main() {
  const args = process.argv.slice(2);
  const dryRun = args.includes('--dry-run');
  const execute = args.includes('--execute');
  const check = args.includes('--check');
  const reportIdx = args.indexOf('--report');
  const reportPath = reportIdx !== -1 ? args[reportIdx + 1] : null;
  if (!dryRun && !execute && !check) {
    console.error('Pass one of --dry-run | --execute | --check');
    process.exit(1);
  }

  const catalogRaw = readFileSync(CATALOG, 'utf-8');
  const catalog = JSON.parse(catalogRaw);

  const plugins = [];
  const skippedEntries = [];
  for (const entry of catalog.plugins) {
    if (typeof entry.source !== 'string' || !entry.source.startsWith('./plugins/')) {
      skippedEntries.push({ name: entry.name, reason: `non-local source: ${entry.source}` });
      continue;
    }
    const dir = entry.source.slice(2);
    if (existsSync(join(ROOT, dir, '.source.json'))) {
      skippedEntries.push({ name: entry.name, reason: 'external mirror (.source.json)' });
      continue;
    }
    if (!existsSync(join(ROOT, dir))) {
      skippedEntries.push({ name: entry.name, reason: 'dir missing on disk' });
      continue;
    }
    plugins.push({ name: entry.name, source: entry.source, dir, catalogVersion: entry.version });
  }

  // -------------------------------------------------------------- check mode
  if (check) {
    // Compare ALL FOUR display surfaces to the extended-catalog version (the
    // authority reconstruction writes): plugin.json, the generated CLI catalog
    // (marketplace.json), and EVERY SKILL.md frontmatter under the plugin dir.
    // The pre-2026-07 check read only plugin.json vs catalog, so it printed
    // "All surfaces agree" while SKILL.md frontmatter drifted — a false pass.
    let cliBySource = new Map();
    try {
      const cli = JSON.parse(readFileSync(CLI_CATALOG, 'utf-8'));
      for (const e of cli.plugins || []) {
        if (typeof e.source === 'string') cliBySource.set(e.source, e.version);
      }
    } catch {
      /* CLI catalog unreadable — skip that surface rather than crash */
    }
    let bad = 0;
    const noPluginJson = [];
    for (const p of plugins) {
      const want = p.catalogVersion;
      if (!want) continue;
      const mismatches = [];

      const pj = join(ROOT, p.dir, '.claude-plugin', 'plugin.json');
      if (existsSync(pj)) {
        try {
          const v = JSON.parse(readFileSync(pj, 'utf-8')).version;
          if (v && v !== want) mismatches.push(`plugin.json=${v}`);
        } catch {
          mismatches.push('plugin.json=UNPARSEABLE');
        }
      } else {
        // A catalog entry whose dir has no plugin.json (e.g. the vendored axiom
        // sub-marketplace). Surface it instead of silently skipping.
        noPluginJson.push(p.dir);
      }

      const cliV = cliBySource.get(p.source);
      if (cliV && cliV !== want) mismatches.push(`marketplace.json=${cliV}`);

      for (const rel of findSkillFiles(p.dir)) {
        const res = editSkillFrontmatter(readFileSync(join(ROOT, rel), 'utf-8'), want);
        if (res.old && res.old !== want) mismatches.push(`${rel}=${res.old}`);
      }

      if (mismatches.length) {
        bad++;
        console.log(`DISAGREE ${p.dir}: catalog=${want} · ${mismatches.join(' · ')}`);
      }
    }
    if (noPluginJson.length) {
      console.log(
        `\nNOTE: ${noPluginJson.length} catalog dir(s) have no plugin.json (vendored sub-marketplace?) ` +
          `and were not version-checked: ${noPluginJson.join(', ')}`,
      );
    }
    console.log(
      bad
        ? `\n${bad} plugin(s) disagree across surfaces (plugin.json / marketplace.json / SKILL.md vs catalog).`
        : 'All surfaces agree (plugin.json + marketplace.json + SKILL.md frontmatter vs catalog).',
    );
    process.exit(bad ? 2 : 0);
  }

  if (requiresFullHistory({ check }) && existsSync(join(ROOT, '.git', 'shallow'))) {
    console.error(
      'Repo is a SHALLOW clone — run `git fetch --unshallow` first; counts would be wrong.',
    );
    process.exit(1);
  }

  const history = collectHistory();

  const rows = [];
  for (const p of plugins) {
    const commits = history.get(p.dir)?.commits ?? [];
    // Oldest commit = the one that introduced the dir → creation, not an update.
    const updates = Math.max(0, commits.length - 1);
    // Floor = the HIGHEST of catalog + plugin.json. The plugin.json can lead
    // the catalog (e.g. a hand-bump that never reached the catalog); flooring on
    // the catalog alone silently DOWNGRADED such plugins — the 2026-07
    // reconstruction bug (claude-never-forgets 1.0.0→0.21.0 etc.). Taking the
    // higher of the two, and its major, keeps a leading plugin.json's major.
    const catV = parseVersion(p.catalogVersion) || { major: 1, minor: 0, patch: 0 };
    let pjV = null;
    try {
      const pjRaw = readFileSync(join(ROOT, p.dir, '.claude-plugin', 'plugin.json'), 'utf-8');
      pjV = parseVersion(JSON.parse(pjRaw).version);
    } catch {
      /* no plugin.json (vendored sub-marketplace) — the catalog is the floor */
    }
    const existing = pjV && compareVersion(pjV, catV) > 0 ? pjV : catV;
    const derived = { major: existing.major, minor: updates, patch: 0 };
    const finalV = compareVersion(derived, existing) > 0 ? derived : existing;
    rows.push({
      ...p,
      updates,
      evidence: commits.slice(0, 10).map((c) => `${c.sha.slice(0, 9)} ${c.subject}`),
      totalCommits: commits.length,
      oldVersion: p.catalogVersion,
      newVersion: fmt(finalV),
    });
  }

  // ----------------------------------------------------------------- summary
  const changing = rows.filter((r) => r.oldVersion !== r.newVersion);
  const hist = new Map();
  for (const r of rows) hist.set(r.newVersion, (hist.get(r.newVersion) || 0) + 1);
  console.log(
    `In-scope plugins: ${plugins.length}  (skipped ${skippedEntries.length}: mirrors/non-local/missing)`,
  );
  console.log(`Changing:         ${changing.length}`);
  console.log('Top target versions:');
  [...hist.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 12)
    .forEach(([v, n]) => console.log(`  ${String(n).padStart(4)}  ${v}`));
  const downgrades = rows.filter((r) => {
    const o = parseVersion(r.oldVersion);
    const n = parseVersion(r.newVersion);
    return o && n && compareVersion(n, o) < 0;
  });
  console.log(`Downgrades: ${downgrades.length} (must be 0)`);
  if (downgrades.length) {
    downgrades.forEach((d) => console.log(`  ${d.dir}`));
    process.exit(1);
  }

  if (dryRun) {
    console.log('\nSample (10 biggest movers):');
    [...changing]
      .sort((a, b) => b.updates - a.updates)
      .slice(0, 10)
      .forEach((r) =>
        console.log(`  ${r.dir}  ${r.oldVersion} → ${r.newVersion}  (${r.updates} updates)`),
      );
  }

  // ----------------------------------------------------------------- execute
  const report = {
    generatedAt: new Date().toISOString(),
    formula:
      'minor = first-parent update commits after creation; final = max(existing, derived); patch = 0',
    skippedEntries,
    plugins: [],
  };
  if (execute) {
    // 1. catalog (single pass, anchored)
    const { out } = editCatalogVersions(
      catalogRaw,
      changing.map((r) => ({
        source: r.source,
        oldVersion: r.oldVersion,
        newVersion: r.newVersion,
      })),
    );
    writeFileSync(CATALOG, out);

    // 2 + 3. plugin.json + SKILL.md per plugin
    for (const r of rows) {
      const rec = {
        name: r.name,
        dir: r.dir,
        updates: r.updates,
        evidence: r.evidence,
        catalog: { old: r.oldVersion, new: r.newVersion },
        pluginJson: null,
        skills: [],
      };
      if (r.oldVersion !== r.newVersion) {
        rec.pluginJson = editPluginJson(r.dir, r.newVersion);
        for (const sf of findSkillFiles(r.dir)) {
          const raw = readFileSync(join(ROOT, sf), 'utf-8');
          const res = editSkillFrontmatter(raw, r.newVersion);
          if (res.out) writeFileSync(join(ROOT, sf), res.out);
          rec.skills.push({ file: sf, old: res.old ?? null, skipped: res.skipped ?? null });
        }
      }
      report.plugins.push(rec);
    }
    if (reportPath) writeFileSync(resolve(reportPath), JSON.stringify(report, null, 2) + '\n');
    console.log(
      `\nWrote catalog + ${changing.length} plugin dirs.${reportPath ? ` Report: ${reportPath}` : ''}`,
    );
    console.log(
      'Now run: pnpm run sync-marketplace  &&  python3 freshie/scripts/promote-to-curated.py',
    );
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    main();
  } catch (err) {
    console.error(err.message || err);
    process.exit(1);
  }
}
