#!/usr/bin/env node
/**
 * auto-bump-changed-plugins.mjs
 *
 * Per-PR auto-bump of plugin patch versions.
 *
 * Runs in CI on every pull request. For each plugin whose source changed in
 * the PR (any file other than its own package.json), bump the plugin's
 * patch version. The CI workflow then commits the bump back to the PR
 * branch so `publish-changed-packages.yml` will republish that plugin
 * when the PR merges to main.
 *
 * Without this script the freeze regrows: a human edit to a plugin's
 * SKILL.md doesn't change the package.json version, so the publish
 * workflow no-ops, so `pnpm update` users never see the change. With
 * this script every code-touching PR ships.
 *
 * Plugin layout supported:
 *   plugins/<category>/<plugin>/                          (3-level)
 *   plugins/saas-packs/skill-databases/<plugin>/          (4-level nested)
 *   packages/<pkg>/                                       (root packages)
 *
 * Decisions per plugin:
 *   - Only its own package.json changed     →  no-op (bumper is idempotent)
 *   - Source files changed (not pkg.json)   →  bump patch
 *   - Source files + pkg.json changed       →  bump patch (use the new local
 *                                              version as the base, not what's
 *                                              on origin/main)
 *
 * Versions are bumped in JSON-text order so we don't reformat unrelated keys.
 *
 * Usage:
 *   node scripts/auto-bump-changed-plugins.mjs            # apply (default)
 *   node scripts/auto-bump-changed-plugins.mjs --dry-run  # preview
 *   BASE_REF=main node scripts/auto-bump-changed-plugins.mjs  # override base
 *
 * Exit codes:
 *   0 — success (any number of bumps including zero)
 *   1 — git diff failed or a package.json couldn't be parsed
 */

import { spawnSync } from 'node:child_process';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
// Circular import by design: reconstruct-versions.mjs imports parseVersion/
// compareVersion from this module. Both modules only export hoisted function
// declarations and neither runs main() on import, so the cycle is safe.
import {
  setCatalogEntryVersion,
  editSkillFrontmatter,
  findSkillFiles,
} from './reconstruct-versions.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const SCOPE = '@intentsolutionsio/';
const EXTENDED_CATALOG = join(ROOT, '.claude-plugin', 'marketplace.extended.json');
const CLI_CATALOG = join(ROOT, '.claude-plugin', 'marketplace.json');

export function parseVersion(v) {
  if (!v || typeof v !== 'string') return null;
  const m = /^(\d+)\.(\d+)\.(\d+)$/.exec(v.trim());
  if (!m) return null;
  return { major: +m[1], minor: +m[2], patch: +m[3] };
}

function fmtVersion(p) {
  return `${p.major}.${p.minor}.${p.patch}`;
}

function bumpPatch(v) {
  return { major: v.major, minor: v.minor, patch: v.patch + 1 };
}

// Display surfaces move by MINOR per update (the approved 2026-07-16 formula:
// a plugin's display minor ≈ its lifetime update count). npm keeps patch.
export function bumpMinor(v) {
  return { major: v.major, minor: v.minor + 1, patch: 0 };
}

// Compare two parsed versions. >0 if a>b, 0 if equal, <0 if a<b.
export function compareVersion(a, b) {
  return a.major - b.major || a.minor - b.minor || a.patch - b.patch;
}

// Idempotency decision (blocker 62ye.5). Given a plugin's declared (local)
// version and its version on the PR base (null when the plugin is absent on
// base), decide whether to bump. Returns { bump: true } or { skip: reason }.
// Pure — no git, no fs — so the loop-prevention logic is unit-testable.
export function bumpDecision(declared, base) {
  if (!base) {
    // New plugin (absent on base): initial version is author-set and
    // publish-changed-packages handles the first release. Bumping it would also
    // loop forever — base stays null on every re-run.
    return { skip: 'new plugin (absent on base) — initial version left as authored' };
  }
  if (compareVersion(declared, base) > 0) {
    // Already ahead of base → a prior auto-bump run on this PR bumped it (or the
    // author set a deliberate minor/major bump, which we must not walk further).
    return {
      skip: `already bumped in this PR (base ${fmtVersion(base)} → local ${fmtVersion(declared)})`,
    };
  }
  return { bump: true };
}

// The plugin's version on the PR base ref, or null when the package.json is
// absent there (a brand-new plugin) or unparseable. Argv-form git (shell:false);
// baseRef is already validated by SAFE_REF_RE in detectBaseRef and dir comes
// from pluginDirFor (repo-relative), so nothing untrusted reaches a shell.
function baseVersion(baseRef, dir) {
  const res = spawnSync('git', ['show', `${baseRef}:${dir}/package.json`], {
    cwd: ROOT,
    encoding: 'utf-8',
    shell: false,
  });
  if (res.status !== 0) return null;
  try {
    return parseVersion(JSON.parse(res.stdout).version);
  } catch {
    return null;
  }
}

// Map a changed file to its plugin/package directory, or null if it's not
// inside one we manage. Returns the path *relative to ROOT* (no leading slash).
function pluginDirFor(relPath) {
  const parts = relPath.split('/');

  if (parts[0] === 'packages' && parts.length >= 2) {
    return parts.slice(0, 2).join('/');
  }

  if (parts[0] !== 'plugins' || parts.length < 3) return null;

  // Special-case: saas-packs/skill-databases hosts nested plugins one level
  // deeper. Same rule publish-changed-packages.yml uses.
  if (parts[1] === 'saas-packs' && parts[2] === 'skill-databases' && parts.length >= 4) {
    return parts.slice(0, 4).join('/');
  }

  return parts.slice(0, 3).join('/');
}

// git ref characters per `git check-ref-format` simplified to a safe subset:
// alphanumerics, `_`, `.`, `/`, `-`. No spaces, no shell metachars. Refuse
// anything else so a hostile env var can't influence the spawned argv.
const SAFE_REF_RE = /^[A-Za-z0-9._/-]+$/;

function detectBaseRef() {
  let candidate;
  if (process.env.BASE_REF) candidate = process.env.BASE_REF;
  else if (process.env.GITHUB_BASE_REF) candidate = `origin/${process.env.GITHUB_BASE_REF}`;
  else candidate = 'origin/main';
  if (!SAFE_REF_RE.test(candidate)) {
    throw new Error(
      `Refusing to use unsafe base ref "${candidate}". Allowed chars: A-Z a-z 0-9 . _ / -`,
    );
  }
  return candidate;
}

function gitDiff(args) {
  // Use spawnSync with argv-form (shell: false default) so untrusted ref
  // content can't be interpreted as shell. CodeQL js/indirect-command-line-
  // injection is satisfied because no input is concatenated into a string.
  return spawnSync('git', ['diff', '--name-only', ...args], {
    cwd: ROOT,
    encoding: 'utf-8',
    shell: false,
  });
}

function listChangedFiles(baseRef) {
  // Three-dot diff = "everything in HEAD that's not in baseRef" — exactly
  // the PR's footprint, ignoring main's own progress while the PR was open.
  let res = gitDiff([`${baseRef}...HEAD`]);
  if (res.status !== 0) {
    // Fall back to two-dot if the merge base isn't computable (shallow clone).
    res = gitDiff([baseRef, 'HEAD']);
  }
  if (res.status !== 0) {
    throw new Error(
      `git diff failed for base ref "${baseRef}": ${res.stderr || res.error?.message || 'non-zero exit'}. ` +
        `Set BASE_REF env var or ensure full fetch.`,
    );
  }
  return res.stdout
    .split('\n')
    .map((s) => s.trim())
    .filter(Boolean);
}

function loadPackageJson(absPath) {
  if (!existsSync(absPath)) return null;
  const raw = readFileSync(absPath, 'utf-8');
  try {
    const pkg = JSON.parse(raw);
    return { raw, pkg };
  } catch {
    throw new Error(`Cannot parse JSON: ${absPath}`);
  }
}

function applyPatchBump(absPath, raw, oldVersion, newVersion) {
  const oldLine = `"version": "${oldVersion}"`;
  const newLine = `"version": "${newVersion}"`;
  if (!raw.includes(oldLine)) {
    throw new Error(`Cannot find exact "${oldLine}" line in ${absPath}; refusing to edit`);
  }
  writeFileSync(absPath, raw.replace(oldLine, newLine));
}

// ---------------------------------------------------------------------------
// Display surfaces (added 2026-07-16). package.json is the npm surface and
// moves by patch above — but nothing browsable reads it. The surfaces users
// actually see are plugin.json (tonsofskills plugin cards), the two catalog
// files (→ /plugin browser), and SKILL.md frontmatter (skill cards). Those
// froze at ~1.0.0 for nine months because only package.json ever moved.
// Every npm patch bump now also minor-bumps the plugin's display version
// (minor ≈ lifetime update count, per the reconstruction formula) and stamps
// the PR's changed SKILL.md files with it. Idempotency rides on the same
// bumpDecision guard as the patch bump.
// ---------------------------------------------------------------------------
function planDisplayBump(dir, changedFiles) {
  if (!dir.startsWith('plugins/')) return null; // packages/* have no display surfaces
  if (existsSync(join(ROOT, dir, '.source.json'))) return null; // external mirror — upstream owns versioning
  const source = `./${dir}`;

  const pjAbs = join(ROOT, dir, '.claude-plugin', 'plugin.json');
  let pjOld = null;
  if (existsSync(pjAbs)) {
    try {
      pjOld = JSON.parse(readFileSync(pjAbs, 'utf-8')).version || null;
    } catch {
      pjOld = null;
    }
  }
  let catOld = null;
  try {
    const cat = JSON.parse(readFileSync(EXTENDED_CATALOG, 'utf-8'));
    catOld = cat.plugins.find((p) => p.source === source)?.version || null;
  } catch {
    catOld = null;
  }
  const candidates = [pjOld, catOld].map(parseVersion).filter(Boolean);
  if (!candidates.length) return null;
  const base = candidates.reduce((a, b) => (compareVersion(a, b) >= 0 ? a : b));
  const to = fmtVersion(bumpMinor(base));
  return {
    dir,
    source,
    from: fmtVersion(base),
    to,
    pjAbs: pjOld ? pjAbs : null,
    pjOld,
    // Stamp ALL of the plugin's SKILL.md files on a display bump, not only the
    // ones in this PR's diff. Stamping only changed SKILL.md strands sibling
    // skills' frontmatter one minor behind the plugin/catalog cards every time
    // a non-SKILL file (command, agent, README) is edited — the exact
    // skill-card-vs-plugin-card drift this bump exists to prevent. changedFiles
    // is retained only for the sourceChanged gate upstream.
    skillFiles: findSkillFiles(dir),
  };
}

function applyDisplayBumps(plans) {
  let extendedRaw = readFileSync(EXTENDED_CATALOG, 'utf-8');
  // Read once; ENOENT means there is no CLI catalog to stamp. An existence
  // check followed by a read and a later write could act on a replaced file.
  let cliRaw;
  try {
    cliRaw = readFileSync(CLI_CATALOG, 'utf-8');
  } catch (error) {
    if (error.code !== 'ENOENT') throw error;
    cliRaw = null;
  }
  let extendedDirty = false;
  let cliDirty = false;
  for (const p of plans) {
    if (p.pjAbs) {
      const raw = readFileSync(p.pjAbs, 'utf-8');
      const oldLine = `"version": "${p.pjOld}"`;
      if (raw.includes(oldLine)) {
        writeFileSync(p.pjAbs, raw.replace(oldLine, `"version": "${p.to}"`));
      }
    }
    const ext = setCatalogEntryVersion(extendedRaw, p.source, p.to);
    if (ext) {
      extendedRaw = ext.out;
      extendedDirty = true;
    }
    if (cliRaw) {
      const cli = setCatalogEntryVersion(cliRaw, p.source, p.to);
      if (cli) {
        cliRaw = cli.out;
        cliDirty = true;
      }
    }
    for (const rel of p.skillFiles) {
      const abs = join(ROOT, rel);
      let current;
      try {
        current = readFileSync(abs, 'utf-8');
      } catch (error) {
        if (error.code === 'ENOENT') continue; // removed in this PR: nothing to stamp
        throw error;
      }
      const res = editSkillFrontmatter(current, p.to);
      if (res.out) writeFileSync(abs, res.out);
    }
  }
  if (extendedDirty) writeFileSync(EXTENDED_CATALOG, extendedRaw);
  if (cliDirty) writeFileSync(CLI_CATALOG, cliRaw);
}

function main() {
  const args = process.argv.slice(2);
  const dryRun = args.includes('--dry-run');
  const baseRef = detectBaseRef();

  const changed = listChangedFiles(baseRef);
  if (!changed.length) {
    console.log(`No files changed vs ${baseRef}; nothing to bump.`);
    return;
  }

  const groups = new Map();
  for (const file of changed) {
    const dir = pluginDirFor(file);
    if (!dir) continue;
    const isPkgJson = file === `${dir}/package.json`;
    const g = groups.get(dir) || {
      changedFiles: [],
      pkgJsonChanged: false,
      sourceChanged: false,
    };
    g.changedFiles.push(file);
    if (isPkgJson) g.pkgJsonChanged = true;
    else g.sourceChanged = true;
    groups.set(dir, g);
  }

  const bumps = [];
  const skips = [];
  for (const [dir, g] of groups) {
    const absPkg = join(ROOT, dir, 'package.json');
    const loaded = loadPackageJson(absPkg);
    if (!loaded) {
      skips.push({ dir, reason: 'no package.json' });
      continue;
    }
    const { raw, pkg } = loaded;
    if (!pkg.name || !pkg.name.startsWith(SCOPE) || pkg.private) {
      skips.push({ dir, reason: `not @intentsolutionsio/* or private: ${pkg.name}` });
      continue;
    }
    if (!g.sourceChanged) {
      // Only the package.json itself changed. Don't double-bump.
      skips.push({ dir, reason: 'only package.json changed' });
      continue;
    }
    const declared = parseVersion(pkg.version);
    if (!declared) {
      skips.push({
        dir,
        reason: `local version "${pkg.version}" is not strict X.Y.Z`,
      });
      continue;
    }
    // Idempotency across re-runs (blocker 62ye.5). Every `synchronize` event
    // re-runs this workflow, and the triggering source file is still in the
    // PR's diff, so without a base-version check the plugin gets re-bumped each
    // time — 0.2.1 → 0.2.2 → 0.2.3 … — and each bump pushes a GITHUB_TOKEN head
    // that fires no checks, leaving the PR BLOCKED on unreported required
    // contexts. Decision is keyed on the plugin's version at the PR base.
    const decision = bumpDecision(declared, baseVersion(baseRef, dir));
    if (decision.skip) {
      skips.push({ dir, reason: decision.skip });
      continue;
    }
    const next = bumpPatch(declared);
    bumps.push({
      dir,
      absPkg,
      raw,
      name: pkg.name,
      from: fmtVersion(declared),
      to: fmtVersion(next),
    });
  }

  if (!bumps.length) {
    console.log(`No plugin source changes vs ${baseRef}; nothing to bump.`);
    if (skips.length) {
      console.log(`Skipped ${skips.length} dir(s):`);
      for (const s of skips) console.log(`  ${s.dir}: ${s.reason}`);
    }
    return;
  }

  const displayPlans = bumps
    .map((b) => planDisplayBump(b.dir, groups.get(b.dir).changedFiles))
    .filter(Boolean);

  console.log(`Plan (vs ${baseRef}):`);
  for (const b of bumps) {
    console.log(`  ${b.name.padEnd(50)}  ${b.from} → ${b.to}  (${b.dir})`);
  }
  if (displayPlans.length) {
    console.log('Display surfaces (plugin.json + catalogs + changed SKILL.md):');
    for (const p of displayPlans) {
      console.log(
        `  ${p.dir.padEnd(50)}  ${p.from} → ${p.to}  (${p.skillFiles.length} skill file(s))`,
      );
    }
  }
  if (skips.length) {
    console.log('Skipped:');
    for (const s of skips) console.log(`  ${s.dir}: ${s.reason}`);
  }

  if (dryRun) {
    console.log('\n(--dry-run; no files written)');
    return;
  }

  for (const b of bumps) {
    applyPatchBump(b.absPkg, b.raw, b.from, b.to);
  }
  applyDisplayBumps(displayPlans);

  console.log('');
  console.log(`bumped: ${bumps.length}`);
  console.log(`no-op:  ${skips.length}`);
}

// Run only when invoked directly (`node scripts/auto-bump-changed-plugins.mjs`),
// not when imported by the test suite — importing must have no side effects.
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    main();
  } catch (err) {
    console.error(err.message || err);
    process.exit(1);
  }
}
