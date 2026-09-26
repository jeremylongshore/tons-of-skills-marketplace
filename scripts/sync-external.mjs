#!/usr/bin/env node
/**
 * External Plugin Sync Engine
 *
 * Syncs plugins from external repositories defined in sources.yaml.
 * Runs weekly via GitHub Actions to keep community plugins fresh.
 *
 * Usage:
 *   node scripts/sync-external.mjs [options]
 *
 * Options:
 *   --force        Force sync even if no changes detected (does NOT bypass the
 *                  sources.lock.json drift quarantine — only --relock does)
 *   --dry-run      Show what would be synced without making changes
 *   --source=NAME  Sync only the specified source
 *   --relock=NAME  Approve + re-baseline a DRIFTED source: mirror its current
 *                  upstream state and advance its sources.lock.json entry.
 *                  Repeatable. Only for use after a human reviewed the drift.
 *   --relock-all   Re-baseline every drifted source (post-review bulk approve)
 *   --verbose      Show detailed output
 *
 * 2026-06-02 rewrite (claude-5h8v):
 *   Switched from per-file GitHub Contents-API calls to `git clone
 *   --depth=1 --filter=blob:none --sparse`. The previous implementation
 *   burned ~5000 API calls per run (one per file × 48 sources × references/**
 *   glob expansion) and 403'd out partway through every time. Git protocol
 *   has higher rate limits AND naturally handles the path filter via
 *   sparse-checkout, so we get all of a source's files in one operation.
 *
 *   Also added auto-catalog-entry generation: after a sync writes new
 *   files, if marketplace.extended.json has no entry for the plugin name,
 *   we generate one from sources.yaml metadata + the synced plugin.json.
 *   This closes the "filesystem synced but plugin invisible" gap that
 *   stranded 16 plugins from the v1 sync (tracked in claude-x1el).
 */

import fs from 'fs';
import path from 'path';
import os from 'os';
import { fileURLToPath } from 'url';
import { execFileSync } from 'child_process';
import yaml from 'js-yaml';
import {
  computeFileDigest,
  loadLock,
  saveLock,
  buildLockEntry,
  diffSource,
  hasRootLicenseInclude,
  isRootLicenseFile,
  matchesPattern,
  unanchoredIncludes,
} from './sync-lockfile.mjs';
import { refuseFindingsForSource } from './scan-synced-content.mjs';
import {
  normalizeRelative,
  safeFileStatus,
  safeReadFile,
  safeReadFileIfExists,
  safeReadTree,
  safeRemoveFile,
  safeWriteFileAtomic,
  splitSafeRelative,
} from './safe-fs.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT_DIR = path.resolve(__dirname, '..');
const SOURCES_FILE = path.join(ROOT_DIR, 'sources.yaml');
const CATALOG_FILE = path.join(ROOT_DIR, '.claude-plugin', 'marketplace.extended.json');
// Content-pinning lockfile: per source, the resolved upstream sha + a sha256
// per mirrored file. A locked source whose upstream bytes moved is QUARANTINED
// (skipped) until a human approves the new state via --relock. See
// scripts/sync-lockfile.mjs for the threat model.
const LOCK_FILE = path.join(ROOT_DIR, 'sources.lock.json');

// Parse command line arguments
const args = process.argv.slice(2);
const options = {
  force: args.includes('--force'),
  dryRun: args.includes('--dry-run'),
  verbose: args.includes('--verbose'),
  // --strict: exit non-zero if ANY source errored / was quarantined / was
  // refused. NOTE: sync-external.yml does NOT pass --strict — the workflow's
  // human-routing lives in its "Flag partial sync" / "Flag quarantined drift" /
  // "Flag REFUSED sources" steps, which read the errors/quarantined/refused
  // counts from GITHUB_OUTPUT and exit 1 themselves (so the run goes visibly
  // red without walling the commit/PR of clean co-synced sources). Do NOT
  // remove those Flag steps on the assumption --strict covers them; without
  // --strict this process exits 0 on a partial/quarantined run. --strict is
  // for local/manual runs; promoting it into the workflow is a deliberate
  // soak decision, not a cleanup.
  strict: args.includes('--strict'),
  source: args.find((a) => a.startsWith('--source='))?.split('=')[1] || null,
  // --relock=NAME / --relock-all: the ONLY way to advance sources.lock.json
  // for a source whose upstream content drifted from the locked baseline.
  // Deliberately separate from --force (which the weekly workflow always
  // passes): forcing file writes must never double as approving new upstream
  // content sight-unseen.
  relockAll: args.includes('--relock-all'),
  relock: args
    .filter((a) => a.startsWith('--relock='))
    .map((a) => a.split('=')[1])
    .filter(Boolean),
};

// Colors for terminal output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  red: '\x1b[31m',
  cyan: '\x1b[36m',
};

function log(message, color = '') {
  console.log(`${color}${message}${colors.reset}`);
}

function logVerbose(message) {
  if (options.verbose) {
    console.log(`${colors.dim}  ${message}${colors.reset}`);
  }
}

/**
 * Sparse-clone a repo into a temp dir and return the local path.
 * The clone uses --depth=1 --filter=blob:none, then sparse-checkout
 * restricts blob materialization to the source_path subtree. Result:
 * ONE git fetch per source, zero REST API calls.
 *
 * Caller must clean up the returned tmpdir.
 */
function sparseCheckout(repo, sourcePath, branch = 'main', licensePath = 'LICENSE') {
  const tmpdir = fs.mkdtempSync(path.join(os.tmpdir(), `sync-${repo.replace('/', '-')}-`));
  // Authenticated clone bumps rate limits when GITHUB_TOKEN is present.
  // Format: https://x-access-token:TOKEN@github.com/owner/repo.git
  const authUrl = process.env.GITHUB_TOKEN
    ? `https://x-access-token:${process.env.GITHUB_TOKEN}@github.com/${repo}.git`
    : `https://github.com/${repo}.git`;

  // Normalize source_path: '' or '.' means "whole repo root". Anything
  // else is treated as a path prefix. `--no-cone` mode treats patterns
  // as gitignore-style, so `/*` matches every entry at root recursively.
  const wholeRepo = !sourcePath || sourcePath === '.' || sourcePath === './';
  const sparsePatterns = wholeRepo ? ['/*'] : [sourcePath, `/${licensePath.replace(/^\/+/, '')}`];

  try {
    execFileSync(
      'git',
      [
        'clone',
        '--depth=1',
        '--filter=blob:none',
        '--sparse',
        '--branch',
        branch,
        '--quiet',
        authUrl,
        tmpdir,
      ],
      { stdio: ['ignore', 'pipe', 'pipe'] },
    );

    execFileSync('git', ['-C', tmpdir, 'sparse-checkout', 'set', '--no-cone', ...sparsePatterns], {
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    return tmpdir;
  } catch (err) {
    // Best-effort cleanup if the clone half-succeeded
    try {
      fs.rmSync(tmpdir, { recursive: true, force: true });
    } catch {
      // ignore
    }
    const stderr = err.stderr?.toString() || err.message;
    throw new Error(`git sparse-clone failed for ${repo}: ${stderr.trim().split('\n').pop()}`);
  }
}

/**
 * Read every regular file under `sourcePath` inside a fresh checkout.
 * Upstream content is hostile by assumption: links and junctions (anywhere,
 * including a parent of source_path), FIFOs and devices are never followed or
 * read. They are reported in `skipped` so the run log shows what was ignored.
 * Paths are relative to sourcePath; bytes are Buffers and modes are kept so
 * the executable bit survives the mirror.
 */
export function readUpstreamFiles(checkoutDir, sourcePath) {
  const wholeRepo = !sourcePath || sourcePath === '.' || sourcePath === './';
  const rel = wholeRepo ? '' : normalizeRelative(sourcePath);
  return safeReadTree(checkoutDir, rel, { exclude: ['.git'] });
}

/**
 * Validate a sources.yaml target_path and return it normalized. Mirrors may
 * only land under plugins/: a target such as `.github/workflows` would let
 * upstream bytes become CI configuration.
 */
export function mirrorTargetRel(targetPath) {
  const rel = normalizeRelative(targetPath);
  const segments = rel.split('/');
  if (segments[0] !== 'plugins' || segments.length < 2) {
    throw new Error(`target_path "${targetPath}" must be a directory under plugins/`);
  }
  return rel;
}

/**
 * Read the upstream license through the hardened reader. The license path is
 * a root-level LICENSE/COPYING name; a link, directory or special file there
 * is refused rather than followed.
 */
export function readUpstreamLicense(checkoutDir, licensePath) {
  const rel = normalizeRelative(licensePath);
  if (rel.includes('/') || !isRootLicenseFile(rel)) {
    throw new Error(
      `license_path "${licensePath}" must name a root LICENSE/COPYING file; refusing sync`,
    );
  }
  let found;
  try {
    found = safeReadFileIfExists(checkoutDir, rel);
  } catch (error) {
    throw new Error(
      `upstream license file "${licensePath}" is not a regular file (${error.message}); refusing sync`,
    );
  }
  if (!found) {
    throw new Error(
      `upstream license file "${licensePath}" is unavailable; refusing sync rather than distributing bytes without license text`,
    );
  }
  return { path: rel, content: found.content, mode: found.mode };
}

/**
 * Write mirrored files under root/targetRel. Every read, comparison and write
 * goes through safe-fs, so a planted link or special file in the mirror tree
 * refuses the whole source instead of redirecting a write. Returns changes.
 */
export function mirrorFiles({
  root,
  targetRel,
  files,
  dryRun = false,
  force = false,
  report = log,
}) {
  const changes = [];
  for (const file of files) {
    splitSafeRelative(file.path);
    const rel = `${targetRel}/${file.path}`;
    const wantMode = typeof file.mode === 'number' && file.mode & 0o111 ? 0o755 : 0o644;
    let reason = 'new';
    let needsUpdate = true;
    const existing = safeReadFileIfExists(root, rel);
    if (existing) {
      needsUpdate = false;
      // Buffer-to-Buffer compare: exact bytes, binaries included.
      if (!existing.content.equals(file.content)) {
        needsUpdate = true;
        reason = 'modified';
      } else if (typeof file.mode === 'number' && (existing.mode & 0o111) !== (file.mode & 0o111)) {
        // Same bytes, different executable bit: self-heal the stale mode.
        needsUpdate = true;
        reason = 'mode';
      }
    }
    if (!needsUpdate && !force) continue;
    if (dryRun) {
      report(`   📝 Would ${reason === 'new' ? 'create' : 'update'}: ${file.path}`, colors.yellow);
    } else {
      // Git's two canonical modes keyed on the upstream executable bit, set
      // through the descriptor so the result is umask-independent.
      safeWriteFileAtomic(root, rel, file.content, { mode: wantMode, createParents: true });
      report(`   ✅ ${reason === 'new' ? 'Created' : 'Updated'}: ${file.path}`, colors.green);
    }
    changes.push({ path: file.path, action: reason });
  }
  return changes;
}

/**
 * Delete files a PRIOR sync owned that upstream has since removed. The prior
 * manifest is committed, hand-editable data: each entry is validated on its
 * own, and a traversal, link or special file is refused and reported without
 * stopping the rest of the prune.
 */
export function pruneOrphans({ root, targetRel, priorFiles, ownedFiles, report = log }) {
  const changes = [];
  const refused = [];
  if (!Array.isArray(priorFiles)) return { changes, refused };
  const ownedSet = new Set(ownedFiles);
  for (const rel of priorFiles) {
    if (typeof rel !== 'string' || ownedSet.has(rel)) continue;
    try {
      splitSafeRelative(rel);
      if (safeRemoveFile(root, `${targetRel}/${rel}`)) {
        report(`   🗑️  Deleted (upstream removed): ${rel}`, colors.yellow);
        changes.push({ path: rel, action: 'deleted' });
      }
    } catch (error) {
      report(`   ⚠️  Refusing to prune ${JSON.stringify(rel)}: ${error.message}`, colors.red);
      refused.push({ path: rel, reason: error.message });
    }
  }
  return { changes, refused };
}

// matchesPattern lives in sync-lockfile.mjs (dependency-free) so the
// zero-install unit-corpus workflow can import it without resolving
// js-yaml; re-exported here because it is part of this module's API.
export { matchesPattern } from './sync-lockfile.mjs';

/**
 * Read marketplace.extended.json and return the unique plugin entry by name.
 * Malformed or duplicate catalog state fails closed instead of being treated
 * as a missing row that the sync may append around.
 */
function catalogLocation(catalogFile, root) {
  const rel = path.relative(root, catalogFile);
  if (!rel || path.isAbsolute(rel)) throw new Error(`catalog ${catalogFile} is outside ${root}`);
  splitSafeRelative(rel);
  return rel;
}

function catalogEntry(pluginName, catalogFile = CATALOG_FILE, root = ROOT_DIR) {
  const found = safeReadFileIfExists(root, catalogLocation(catalogFile, root));
  if (!found) return null;
  const data = JSON.parse(found.content.toString('utf8'));
  if (!Array.isArray(data?.plugins)) throw new Error('marketplace catalog has no plugins array');
  const matches = data.plugins.filter((plugin) => plugin?.name === pluginName);
  if (matches.length > 1) throw new Error(`${pluginName}: duplicate marketplace catalog entries`);
  return matches[0] ?? null;
}

/**
 * Return whether a mirrored source may be projected into publication catalogs.
 * A quarantine is deliberately retained in sources.yaml and on disk for
 * provenance/upstream repair, but it has no publication channel. Unknown or
 * malformed disposition shapes fail closed instead of silently publishing.
 */
export function sourceAllowsPublication(source) {
  const dispositions = [
    ['publication_disposition', source?.publication_disposition],
    ['copyleft_disposition', source?.copyleft_disposition],
  ].filter(([, value]) => value !== undefined);
  if (dispositions.length === 0) return true;
  if (dispositions.length > 1) {
    throw new Error(`${source?.name ?? '<unnamed source>'}: multiple publication dispositions`);
  }
  const [field, disposition] = dispositions[0];
  if (
    !disposition ||
    typeof disposition !== 'object' ||
    disposition.status !== 'quarantined' ||
    !Array.isArray(disposition.channels) ||
    disposition.channels.length !== 0
  ) {
    throw new Error(
      `${source?.name ?? '<unnamed source>'}: ${field} must be ` +
        '`status: quarantined` with an empty `channels` list',
    );
  }
  return false;
}

/** Require an existing catalog row to agree exactly with its source disposition. */
export function assertCatalogPublicationParity(source, plugin) {
  const publishable = sourceAllowsPublication(source);
  if (plugin === null || plugin === undefined) return publishable;
  if (!plugin || typeof plugin !== 'object' || Array.isArray(plugin)) {
    throw new Error(`${source?.name ?? '<unnamed source>'}: catalog entry must be an object`);
  }
  if (plugin.publication !== undefined && plugin.publication !== 'quarantined') {
    throw new Error(
      `${source?.name ?? '<unnamed source>'}: unknown catalog publication state ` +
        `${String(plugin.publication)}`,
    );
  }
  const catalogPublishable = plugin.publication === undefined;
  if (catalogPublishable !== publishable) {
    throw new Error(
      `${source?.name ?? '<unnamed source>'}: source disposition and catalog publication state disagree`,
    );
  }
  return publishable;
}

/**
 * Derive the plugin's catalog category from the target_path's filesystem
 * location, not from sources.yaml metadata. The catalog invariant check
 * (validate-catalog-invariants.py) requires category to match the parent
 * directory. e.g., target_path 'plugins/mcp/x-bug-triage' implies
 * category='mcp' regardless of what sources.yaml claims.
 *
 * Falls back to sources.yaml category if the path doesn't follow the
 * plugins/<category>/<name> convention.
 */
function categoryFromTargetPath(targetPath, fallback) {
  const match = /(?:^|\/)plugins\/([^/]+)\//.exec(targetPath);
  return match ? match[1] : fallback || 'community';
}

/**
 * Validate an upstream-supplied URL before it enters the catalog. The synced
 * plugin.json is UPSTREAM-CONTROLLED content, and homepage / repository /
 * author.url from it are rendered as the plugin's official links on
 * tonsofskills.com — so a rogue upstream must not be able to plant a
 * `javascript:` / `data:` / arbitrary-scheme link via its manifest. Accepts a
 * parseable http(s) URL only; anything else returns null (caller drops the
 * field and logs). Also unwraps the `{ type, url }` object form npm allows for
 * `repository`, normalizing it to the plain string the catalog uses.
 * Exported for direct unit verification.
 */
export function safeHttpUrl(value) {
  if (value && typeof value === 'object' && typeof value.url === 'string') {
    value = value.url;
  }
  if (typeof value !== 'string') return null;
  try {
    const u = new URL(value);
    return u.protocol === 'http:' || u.protocol === 'https:' ? value : null;
  } catch {
    return null;
  }
}

/**
 * Ensure a minimal .claude-plugin/plugin.json exists for the synced
 * plugin. Some sources.yaml entries only sync SKILL.md + references/
 * because their upstream repo has no plugin.json (skill-only repos like
 * skyvern, ejentum). Without a plugin.json the downstream
 * generate-plugin-package-jsons.mjs can't produce a package.json, which
 * trips validate-catalog-invariants.py.
 *
 * We synthesize a minimal plugin.json from sources.yaml metadata. The
 * file is created ONLY if absent; existing upstream plugin.json files
 * are not overwritten.
 *
 * Returns true if a plugin.json was created, false if one already existed
 * or dry-run mode.
 */
function ensurePluginJson(source, root = ROOT_DIR) {
  const pluginJsonRel = `${mirrorTargetRel(source.target_path)}/.claude-plugin/plugin.json`;

  // Throws for a planted link or special file: never read or write through it.
  const current = safeReadFileIfExists(root, pluginJsonRel);
  if (current) {
    // License metadata is a projection of the reviewed sources.yaml contract.
    // Preserve upstream fields, but never retain a contradictory license claim
    // after the source record has been corrected.
    let existing;
    try {
      existing = JSON.parse(current.content.toString('utf8'));
    } catch {
      // Existing malformed manifests are handled by the normal validators;
      // never rewrite an unreadable upstream-owned file during sync.
      return false;
    }
    if (!existing || typeof existing !== 'object' || Array.isArray(existing)) return false;
    if (source.license && existing.license !== source.license) {
      if (options.dryRun) {
        log(`   📋 Would reconcile plugin.json license: ${source.license}`, colors.yellow);
        return false;
      }
      existing.license = source.license;
      safeWriteFileAtomic(root, pluginJsonRel, JSON.stringify(existing, null, 2) + '\n');
      log(`   📋 Reconciled plugin.json license: ${source.license}`, colors.green);
      return true;
    }
    return false;
  }

  if (options.dryRun) {
    log(`   📋 Would synthesize .claude-plugin/plugin.json`, colors.yellow);
    return false;
  }

  const minimalPlugin = {
    name: source.name,
    version: '0.1.0',
    description: source.description || `${source.name} plugin`,
    author: source.author
      ? {
          name: source.author.name || 'External Contributor',
          ...(source.author.github ? { url: `https://github.com/${source.author.github}` } : {}),
          ...(source.author.email ? { email: source.author.email } : {}),
        }
      : { name: 'External Contributor' },
    ...(source.license ? { license: source.license } : {}),
    ...(source.repo ? { repository: `https://github.com/${source.repo}` } : {}),
  };

  safeWriteFileAtomic(root, pluginJsonRel, JSON.stringify(minimalPlugin, null, 2) + '\n', {
    createParents: true,
  });
  log(`   📋 Synthesized .claude-plugin/plugin.json (upstream had none)`, colors.green);
  return true;
}

/**
 * Ensure a README.md exists for the synced plugin. validate-plugins.yml
 * has a job that fails with "Missing README.md in <path>" otherwise.
 * Some upstream skill-only repos (ejentum/*) ship just SKILL.md and the
 * sources.yaml include pattern honestly reflects that.
 *
 * If README.md is missing, synthesize one from sources.yaml metadata.
 * If a SKILL.md exists at the plugin root, prefer that as the body
 * (rendered with a minimal header so reviewers see real content).
 *
 * Existing README.md files (from upstream sync) are never overwritten.
 *
 * Returns true if a README was created, false if one already existed
 * or dry-run mode.
 */
function ensureReadme(source, root = ROOT_DIR) {
  const targetRel = mirrorTargetRel(source.target_path);
  const readmeRel = `${targetRel}/README.md`;

  if (safeFileStatus(root, readmeRel)) {
    return false; // upstream provided one, or earlier sync wrote one
  }

  if (options.dryRun) {
    log(`   📋 Would synthesize README.md`, colors.yellow);
    return false;
  }

  // Try to use the upstream SKILL.md content as the README body if one
  // is present at the plugin root. Falls back to a minimal stub.
  const skill = safeReadFileIfExists(root, `${targetRel}/SKILL.md`);
  let body = '';
  if (skill) {
    body = skill.content.toString('utf8');
    // Strip the YAML frontmatter (lines between two `---` lines at start)
    body = body.replace(/^---\n[\s\S]*?\n---\n+/, '');
  } else {
    body = source.description || `${source.name} plugin`;
  }

  const author = source.author?.name || 'External Contributor';
  const repoLink = source.repo ? `https://github.com/${source.repo}` : null;

  const readme = `# ${source.name}

${source.description || ''}

${body}

---

**Author:** ${author}${repoLink ? `  \n**Upstream:** [${source.repo}](${repoLink})` : ''}
${source.license ? `  \n**License:** ${source.license}` : ''}
`;

  safeWriteFileAtomic(root, readmeRel, readme, { createParents: true });
  log(`   📋 Synthesized README.md (upstream had none)`, colors.green);
  return true;
}

/**
 * Auto-generate a marketplace.extended.json catalog entry for a freshly
 * synced source. Merges sources.yaml metadata with the synced
 * .claude-plugin/plugin.json (if present) to fill in version/keywords.
 *
 * Strategy: append the new entry to the plugins array. We write with
 * 2-space indent matching the catalog's canonical format, plus a final
 * newline. The check-catalog-format gate budgets +80±300 lines for one
 * added entry; a clean 20-25-line entry is well within that.
 *
 * Returns true if an entry was added, false if catalog already had one
 * or if dry-run mode.
 */
export function ensureCatalogEntry(
  source,
  { root = ROOT_DIR, catalogFile = CATALOG_FILE, dryRun = options.dryRun } = {},
) {
  const existing = catalogEntry(source.name, catalogFile, root);
  const publishable = assertCatalogPublicationParity(source, existing);
  if (existing) {
    return false; // already present, no action
  }

  // Pull version + license from the synced plugin.json if available.
  const pluginJsonFile = safeReadFileIfExists(
    root,
    `${mirrorTargetRel(source.target_path)}/.claude-plugin/plugin.json`,
  );
  let pluginJson = {};
  if (pluginJsonFile) {
    try {
      pluginJson = JSON.parse(pluginJsonFile.content.toString('utf8'));
    } catch {
      // ignore parse errors; fall back to sources.yaml metadata
    }
  }

  // Build the catalog entry. Order matches the canonical layout in
  // marketplace.extended.json so the diff stays tight and check-catalog-format
  // doesn't trip.
  // Name is normalized to lowercase: Astro emits routes at
  // /plugins/<lowercased-name>/ and check-routes.mjs verifies exact match,
  // so a catalog entry named 'Claudebase' would 404 at /plugins/Claudebase/.
  // Category MUST match the target_path's parent dir per
  // validate-catalog-invariants.py — derive from path, not sources.yaml.
  const entry = {
    name: source.name.toLowerCase(),
    source: source.target_path.startsWith('./') ? source.target_path : `./${source.target_path}`,
    description: source.description || pluginJson.description || `${source.name} plugin`,
    version: pluginJson.version || '0.1.0',
    category: categoryFromTargetPath(source.target_path, source.category),
  };
  if (!publishable) entry.publication = 'quarantined';

  // Keywords: prefer plugin.json, fall back to sources.yaml, else infer from category
  if (Array.isArray(pluginJson.keywords) && pluginJson.keywords.length > 0) {
    entry.keywords = pluginJson.keywords;
  } else if (Array.isArray(source.keywords) && source.keywords.length > 0) {
    entry.keywords = source.keywords;
  }

  // Author: prefer plugin.json author shape (object), fall back to sources.yaml.
  // author.url comes from UPSTREAM-controlled content → scheme-validated
  // (http/https only) before it can render as an official link.
  if (pluginJson.author && typeof pluginJson.author === 'object') {
    const authorUrl = safeHttpUrl(pluginJson.author.url);
    if (pluginJson.author.url && !authorUrl) {
      log(
        `   ⚠️  Dropped invalid upstream author.url: ${String(pluginJson.author.url).slice(0, 80)}`,
        colors.yellow,
      );
    }
    entry.author = {
      name: pluginJson.author.name || source.author?.name || 'External Contributor',
      ...(authorUrl ? { url: authorUrl } : {}),
      ...(pluginJson.author.email ? { email: pluginJson.author.email } : {}),
    };
  } else if (source.author) {
    entry.author = {
      name: source.author.name || 'External Contributor',
      ...(source.author.github ? { url: `https://github.com/${source.author.github}` } : {}),
      ...(source.author.email ? { email: source.author.email } : {}),
    };
  }

  // homepage / repository are likewise upstream-controlled: accept only a
  // parseable http(s) URL (repository's npm `{ type, url }` object form is
  // unwrapped to its string). A javascript:/data:/garbage value is dropped
  // loudly rather than published on the plugin's detail page.
  const homepage = safeHttpUrl(pluginJson.homepage);
  if (homepage) entry.homepage = homepage;
  else if (pluginJson.homepage) {
    log(
      `   ⚠️  Dropped invalid upstream homepage: ${String(pluginJson.homepage).slice(0, 80)}`,
      colors.yellow,
    );
  }
  const repository = safeHttpUrl(pluginJson.repository);
  if (repository) entry.repository = repository;
  else if (pluginJson.repository) {
    log(
      `   ⚠️  Dropped invalid upstream repository: ${JSON.stringify(pluginJson.repository).slice(0, 80)}`,
      colors.yellow,
    );
  }
  if (pluginJson.license || source.license) {
    entry.license = pluginJson.license || source.license;
  }

  if (dryRun) {
    log(`   📋 Would add catalog entry: ${source.name}`, colors.yellow);
    return false;
  }

  // Insert the entry. Append at the end of the plugins array, before the
  // closing brace. We avoid full JSON.stringify of the whole file because
  // that reformats every existing entry and trips check-catalog-format.
  const catalogRel = catalogLocation(catalogFile, root);
  const text = safeReadFile(root, catalogRel).content.toString('utf8');
  const entryJson = JSON.stringify(entry, null, 2)
    .split('\n')
    .map((line, i) => (i === 0 ? `    ${line}` : `    ${line}`))
    .join('\n');

  // Find the last `}` immediately before `]\n}` (the plugins-array close).
  // Replace `    }\n  ]\n}` with `    },\n    <new>\n  ]\n}`.
  const closeMatch = text.match(/(\s*}\s*)(\n\s*]\s*\n\s*}\s*)$/);
  if (!closeMatch) {
    log(`   ⚠️  Could not locate catalog insertion point — skipping entry`, colors.yellow);
    return false;
  }
  const before = text.slice(0, closeMatch.index);
  const lastEntryClose = closeMatch[1];
  const arrayClose = closeMatch[2];
  // Insert a newline between the prior entry's `},` and the new entry so the
  // seam is `},\n    {` (matching the file's canonical formatting) instead of
  // jamming them onto one line as `},    {`, which the catalog-format gate flags.
  const updated = `${before}${lastEntryClose.replace(/}(\s*)$/, '},')}\n${entryJson}${arrayClose}`;

  safeWriteFileAtomic(root, catalogRel, updated);
  log(`   📋 Added catalog entry: ${source.name}`, colors.green);
  return true;
}

/**
 * Sync a single source via sparse git clone.
 *
 * `lock` is the loaded sources.lock.json object (shared across sources,
 * mutated in-memory here; main() persists it once after the loop).
 */
async function syncSource(source, config, lock) {
  log(`\n📦 Syncing: ${source.name}`, colors.cyan);
  log(`   From: ${source.repo}/${source.source_path}`, colors.dim);
  log(`   To:   ${source.target_path}`, colors.dim);

  // Curated freeze — mirror-by-default · never clobber (see 000-docs AT-DECR,
  // "mirror-by-default external-plugin sync model"). A source we have locally
  // hardened past its upstream (e.g. tonone / hyperflow, whose agents we A-graded
  // to marketplace frontmatter) must NEVER be force-reverted to upstream stubs
  // behind our back. When `curated: true` in sources.yaml we freeze the mirror
  // write entirely — no clone, no overwrite, no orphan prune — and only keep the
  // catalog entry current. The standing model is to push our improvement UPSTREAM
  // (a friendly issue → a PR the contributor owns and merges); once it lands at
  // the source the plugin is A-grade upstream and `curated:` can be removed to
  // resume normal mirroring. To deliberately re-baseline a curated plugin, drop
  // `curated:` first — the freeze is intentional and applies even to an explicit
  // `--source=<name>` run.
  if (source.curated === true) {
    log(
      `   🔒 Curated — mirror frozen; --force will NOT revert local edits. Upstream improvements instead.`,
      colors.yellow,
    );
    const catalogAdded = ensureCatalogEntry(source);
    return {
      source: source.name,
      changes: catalogAdded
        ? [{ path: '.claude-plugin/marketplace.extended.json', action: 'catalog' }]
        : [],
      error: null,
      curated: true,
    };
  }

  const changes = [];
  const branch = source.branch || config?.default_branch || 'main';
  let tmpdir = null;

  try {
    const licensePath = source.license_path || 'LICENSE';
    // Validate the destination before any network or disk work.
    const targetRel = mirrorTargetRel(source.target_path);
    tmpdir = sparseCheckout(source.repo, source.source_path, branch, licensePath);
    logVerbose(`Sparse-cloned ${source.repo}@${branch} → ${tmpdir}`);

    // Walk the sourcePath subtree (or repo root when source_path is '.' / '')
    // through the hardened reader: upstream links and special files are
    // reported and never followed.
    const { files, skipped } = readUpstreamFiles(tmpdir, source.source_path);
    for (const skip of skipped) {
      log(`   ⚠️  Not mirrored (${skip.reason}): ${skip.path}`, colors.yellow);
    }

    if (files.length === 0) {
      log(`   ⚠️  No files found at source path`, colors.yellow);
      return { source: source.name, changes: [], error: 'No files found at source path' };
    }
    logVerbose(`Discovered ${files.length} files in source`);

    // Warn loudly on unsupported glob syntax: matchesPattern does NOT implement
    // bash extglob ( !( ?( +( @( ) or brace expansion, so such a pattern
    // silently matches nothing — a dead include/exclude rule. Flag it rather
    // than let it no-op invisibly.
    for (const pat of [...(source.include || []), ...(source.exclude || [])]) {
      if (/[!?+@]\(|\{[^}]*,[^}]*\}/.test(pat)) {
        log(
          `   ⚠️  Unsupported glob (extglob/brace) — rule is a silent no-op: "${pat}"`,
          colors.red,
        );
      }
    }

    // Anchoring lint (blocker 62ye.6): an include that starts with neither `/`
    // nor `**` is silently auto-prefixed `**/` and matches at ANY depth, not the
    // root the vetter likely intended. Warn so intent is explicit — the fix is a
    // one-char edit in sources.yaml (`/README.md` root-only, or `**/README.md`
    // to keep it recursive on purpose). Advisory only; the matcher is unchanged.
    for (const pat of unanchoredIncludes(source.include)) {
      log(
        `   ⚠️  Unanchored include "${pat}" is auto-prefixed **/ (matches at any depth) — ` +
          `anchor as "/${pat}" for root-only, or write "**/${pat}" to make the recursion explicit`,
        colors.yellow,
      );
    }
    const filteredFiles = files.filter((file) => {
      const included = matchesPattern(file.path, source.include);
      const excluded = matchesPattern(file.path, source.exclude);
      return included && !excluded;
    });

    // License text must travel with every mirror. A source may mirror a nested
    // upstream subtree, but its license normally lives at repository root; the
    // dedicated license_path lets the sparse checkout carry it without widening
    // the mirrored content. Do not synthesize a license from a metadata claim:
    // the bytes must come from the upstream source selected by the include list.
    if (!hasRootLicenseInclude(source.include)) {
      throw new Error(
        'missing explicit root LICENSE/COPYING entry in sources.yaml include[]; refusing sync',
      );
    }
    // Read through the hardened reader: an upstream LICENSE that is a link
    // (for example to a runner file) is refused, never followed.
    const license = readUpstreamLicense(tmpdir, licensePath);
    if (!filteredFiles.some((file) => isRootLicenseFile(file.path))) {
      filteredFiles.push(license);
    }
    if (!filteredFiles.some((file) => isRootLicenseFile(file.path))) {
      throw new Error('no root LICENSE/COPYING file selected for mirror; refusing sync');
    }
    logVerbose(`${filteredFiles.length} files after filtering`);

    // ── Lockfile pinning gate (sources.lock.json) ────────────────────────
    // Compare the freshly-cloned upstream bytes against the committed lock
    // BEFORE any file is written. Three outcomes:
    //   new-source → first sync of a human-listed source: mirror + baseline.
    //   unchanged  → mirror as today (no-op diffs).
    //   drifted    → QUARANTINE: skip this source entirely this run; a human
    //                reviews the upstream diff and approves via --relock.
    // NOTE: --force does NOT bypass this gate (the weekly workflow always
    // passes --force); only an explicit --relock advances a drifted lock.
    let resolvedRef = null;
    try {
      resolvedRef = execFileSync('git', ['-C', tmpdir, 'rev-parse', 'HEAD'], {
        stdio: ['ignore', 'pipe', 'ignore'],
      })
        .toString()
        .trim();
    } catch {
      // Ref capture is best-effort metadata; the content digests below are
      // the actual gate.
    }

    const currentDigests = filteredFiles.map((file) => ({
      path: file.path,
      sha256: computeFileDigest(file.content),
    }));
    const lockDiff = diffSource(lock, source.name, currentDigests);
    const relockRequested = options.relockAll || options.relock.includes(source.name);
    let lockStatus = lockDiff.status;

    if (lockDiff.status === 'drifted' && !relockRequested) {
      log(
        `   🔒 QUARANTINED — upstream drifted from sources.lock.json baseline; nothing mirrored this run`,
        colors.red,
      );
      log(
        `      +${lockDiff.added.length} added  ~${lockDiff.changed.length} changed  -${lockDiff.removed.length} removed (upstream @ ${resolvedRef ? resolvedRef.slice(0, 12) : 'unknown'})`,
        colors.red,
      );
      // Full changed-file list prints UNCONDITIONALLY (not logVerbose): this
      // list is the drift-review surface — an operator deciding --relock from
      // the run log must see exactly which upstream paths moved, or a bulk
      // approve rubber-stamps content nobody enumerated.
      for (const p of lockDiff.added) log(`      drift added:   ${p}`, colors.red);
      for (const p of lockDiff.changed) log(`      drift changed: ${p}`, colors.red);
      for (const p of lockDiff.removed) log(`      drift removed: ${p}`, colors.red);
      log(
        `      Review the upstream diff, then approve with: node scripts/sync-external.mjs --source=${source.name} --relock=${source.name}`,
        colors.yellow,
      );
      return {
        source: source.name,
        changes: [],
        error: null,
        lockStatus: 'quarantined',
        quarantined: {
          added: lockDiff.added,
          removed: lockDiff.removed,
          changed: lockDiff.changed,
          resolved_ref: resolvedRef,
        },
      };
    }

    if (lockDiff.status === 'new-source') {
      log(
        `   🔏 New source — ${options.dryRun ? 'would record' : 'recording'} lock baseline (${currentDigests.length} files @ ${resolvedRef ? resolvedRef.slice(0, 12) : 'unknown'})`,
        colors.green,
      );
    } else if (lockDiff.status === 'drifted' && relockRequested) {
      lockStatus = 'relocked';
      log(
        `   🔏 Re-baselining via --relock: +${lockDiff.added.length} added  ~${lockDiff.changed.length} changed  -${lockDiff.removed.length} removed`,
        colors.yellow,
      );
      // The exact per-file approval surface, printed UNCONDITIONALLY: this is
      // what the --relock (or relock-all workflow input) is signing off on. A
      // reviewer reading the run log must be able to enumerate every path the
      // re-baseline admits — counts alone let a bulk approve hide a payload.
      for (const p of lockDiff.added) log(`      relock admits (added):   ${p}`, colors.yellow);
      for (const p of lockDiff.changed) log(`      relock admits (changed): ${p}`, colors.yellow);
      for (const p of lockDiff.removed) log(`      relock drops (removed):  ${p}`, colors.yellow);
    }

    // Supply-chain REFUSE quarantine (blocker 62ye.2). Scan this source's files
    // BEFORE writing any of them. A REFUSE quarantines ONLY this source: nothing
    // is mirrored, nothing malicious touches disk (no revert), and co-synced
    // clean sources still sync — instead of the whole run walling when the
    // repo-wide post-sync scan hit a single poisoned source.
    const refuseFindings = refuseFindingsForSource(filteredFiles, source.target_path);
    if (refuseFindings.length) {
      log(
        `   ⛔ REFUSED — ${refuseFindings.length} high-confidence malicious finding(s); nothing mirrored this run`,
        colors.red,
      );
      for (const f of refuseFindings.slice(0, 10)) {
        log(`      ${f.file}: ${f.id}${f.label ? ` — ${f.label}` : ''}`, colors.red);
      }
      return {
        source: source.name,
        changes: [],
        error: null,
        lockStatus: 'refused',
        refused: { findings: refuseFindings },
      };
    }

    changes.push(
      ...mirrorFiles({
        root: ROOT_DIR,
        targetRel,
        files: filteredFiles,
        dryRun: options.dryRun,
        force: options.force,
      }),
    );

    // Owned-file manifest: the exact set of upstream-matched files this sync
    // owns under target_path (NOT the synthesized README/plugin.json, which the
    // engine generates separately). Drives the orphan prune on the next run.
    const ownedFiles = filteredFiles.map((file) => file.path).sort();
    const sourceJsonRel = `${targetRel}/.source.json`;
    // Throws for a planted link or special file, failing this source closed.
    const priorSourceFile = options.dryRun ? null : safeReadFileIfExists(ROOT_DIR, sourceJsonRel);
    let priorSource = null;
    if (priorSourceFile) {
      try {
        priorSource = JSON.parse(priorSourceFile.content.toString('utf8'));
      } catch {
        // Unreadable prior manifest: skip the prune rather than guess.
      }
    }

    // Orphan prune: delete files a PRIOR sync owned but upstream has since
    // removed/renamed. Driven off the persisted manifest so the engine only
    // ever deletes files IT previously authored — immune to derived-file or
    // hand-added collisions. Skipped on the first run after this change, when
    // the prior .source.json has no files[] manifest.
    if (!options.dryRun && priorSource && typeof priorSource === 'object') {
      changes.push(
        ...pruneOrphans({
          root: ROOT_DIR,
          targetRel,
          priorFiles: priorSource.files,
          ownedFiles,
        }).changes,
      );
    }

    // Synthesize plugin.json + README.md if the upstream sync didn't
    // include them (skill-only repos like skyvern / ejentum). Required so
    // the downstream validators (generate-plugin-package-jsons.mjs,
    // validate-catalog-invariants.py, the README-check job) all pass.
    if (!options.dryRun) {
      const pluginJsonAdded = ensurePluginJson(source);
      if (pluginJsonAdded) {
        changes.push({ path: '.claude-plugin/plugin.json', action: 'plugin-json' });
      }
      const readmeAdded = ensureReadme(source);
      if (readmeAdded) {
        changes.push({ path: 'README.md', action: 'readme' });
      }
    }

    // Auto-register in the catalog if absent. This is the second half of
    // the sync — without it, files land on disk but the plugin stays
    // invisible to tonsofskills.com / ccpi CLI / search. The 16 stranded
    // entries documented in claude-x1el all stuck here.
    const catalogAdded = ensureCatalogEntry(source);
    if (catalogAdded) {
      changes.push({ path: '.claude-plugin/marketplace.extended.json', action: 'catalog' });
    }

    // `.source.json` is the provenance authority for a mirrored artifact. A
    // reviewed source-record correction (for example MIT → AGPL-3.0 after an
    // upstream license check) must update it even when upstream file bytes are
    // unchanged.
    // A malformed prior manifest is left for the validators: the final write
    // below repairs it only when this sync already has changes.
    if (
      !options.dryRun &&
      priorSource &&
      typeof priorSource === 'object' &&
      priorSource.license !== source.license
    ) {
      changes.push({ path: '.source.json', action: 'provenance' });
    }

    // Write provenance only after every generated projection has settled. This
    // keeps `.source.json` aligned when a source metadata correction changes a
    // synthesized plugin manifest without changing any upstream file bytes.
    if (changes.length > 0 && !options.dryRun) {
      const sourceJson = {
        synced_from: {
          repo: source.repo,
          path: source.source_path,
          branch,
        },
        last_sync: new Date().toISOString(),
        author: source.author,
        license: source.license,
        files_synced: ownedFiles.length,
        files: ownedFiles,
      };
      safeWriteFileAtomic(ROOT_DIR, sourceJsonRel, JSON.stringify(sourceJson, null, 2));
      logVerbose(`Written .source.json`);

      // Loud warning if any synced file is git-ignored: the workflow's
      // `git add -A` would silently drop it, producing an incomplete mirror.
      try {
        const targets = ownedFiles.map((file) => `${targetRel}/${file}`);
        const ignored = execFileSync('git', ['-C', ROOT_DIR, 'check-ignore', ...targets], {
          stdio: ['ignore', 'pipe', 'ignore'],
        })
          .toString()
          .trim();
        if (ignored) {
          log(
            `   ⚠️  GIT-IGNORED — will NOT be committed: ${ignored.split('\n').join(', ')}`,
            colors.red,
          );
        }
      } catch {
        // git check-ignore exits 1 when nothing matches — the normal, good path.
      }
    }

    if (changes.length === 0) {
      log(`   ✓ No changes detected`, colors.dim);
    }

    // Advance the in-memory lock (persisted once by main()) only AFTER the
    // mirror writes above succeeded — a throw mid-mirror must never leave an
    // approved baseline for content that never landed on disk:
    //   new-source / relocked → full fresh baseline entry.
    //   unchanged             → refresh nothing, EXCEPT backfilling a null
    //                           resolved_ref (bootstrap entries were built
    //                           from in-tree files without a clone). Never
    //                           bump an existing ref on unchanged content —
    //                           the recorded ref stays the one whose content
    //                           a human approved, and the lock diff stays
    //                           quiet when nothing actually changed.
    if (!options.dryRun) {
      if (lockStatus === 'new-source' || lockStatus === 'relocked') {
        lock.sources[source.name] = buildLockEntry(
          source,
          resolvedRef,
          currentDigests,
          new Date().toISOString(),
        );
      } else if (lockStatus === 'unchanged' && lock.sources[source.name].resolved_ref == null) {
        lock.sources[source.name].resolved_ref = resolvedRef;
      }
    }

    return { source: source.name, changes, error: null, lockStatus };
  } catch (error) {
    log(`   ❌ Error: ${error.message}`, colors.red);
    return { source: source.name, changes: [], error: error.message };
  } finally {
    if (tmpdir) {
      try {
        fs.rmSync(tmpdir, { recursive: true, force: true });
      } catch {
        // tmpdir cleanup is best-effort
      }
    }
  }
}

/**
 * Main sync function
 */
async function main() {
  log('\n🔄 External Plugin Sync', colors.bright + colors.blue);
  log('='.repeat(50), colors.blue);

  if (options.dryRun) {
    log('DRY RUN MODE - No changes will be made\n', colors.yellow);
  }

  const sourcesFile = safeReadFileIfExists(ROOT_DIR, path.basename(SOURCES_FILE));
  if (!sourcesFile) {
    log(`❌ sources.yaml not found at ${SOURCES_FILE}`, colors.red);
    process.exit(1);
  }

  const sourcesContent = sourcesFile.content.toString('utf8');
  const { sources, config } = yaml.load(sourcesContent);

  if (!sources || sources.length === 0) {
    log('❌ No sources defined in sources.yaml', colors.red);
    process.exit(1);
  }

  log(`Found ${sources.length} source(s) to sync`, colors.dim);

  const sourcesToSync = options.source ? sources.filter((s) => s.name === options.source) : sources;

  if (options.source && sourcesToSync.length === 0) {
    log(`❌ Source "${options.source}" not found in sources.yaml`, colors.red);
    process.exit(1);
  }

  // Fail closed on an unreadable lock: a corrupt sources.lock.json must never
  // degrade into "nothing is pinned" (which would classify every source as
  // new-source and re-baseline drifted content sight-unseen).
  let lock;
  try {
    lock = loadLock(LOCK_FILE);
  } catch (error) {
    log(`❌ ${error.message}`, colors.red);
    process.exit(1);
  }

  const results = [];
  for (const source of sourcesToSync) {
    const result = await syncSource(source, config, lock);
    results.push(result);
  }

  // Persist the lock advanced by new-source / --relock entries. Written even
  // when quarantines exist: quarantined entries were NOT advanced, so the
  // committed lock keeps demanding review for them on every subsequent run.
  if (!options.dryRun) {
    if (saveLock(LOCK_FILE, lock)) {
      logVerbose(`Updated ${path.basename(LOCK_FILE)}`);
    }
  }

  log('\n' + '='.repeat(50), colors.blue);
  log('📊 Sync Summary', colors.bright + colors.blue);

  const totalChanges = results.reduce((acc, r) => acc + r.changes.length, 0);
  const catalogAdds = results.reduce(
    (acc, r) => acc + r.changes.filter((c) => c.action === 'catalog').length,
    0,
  );
  const errors = results.filter((r) => r.error);
  const quarantined = results.filter((r) => r.lockStatus === 'quarantined');
  const refused = results.filter((r) => r.lockStatus === 'refused');
  const lockUnchanged = results.filter((r) => r.lockStatus === 'unchanged').length;
  const lockNew = results.filter((r) => r.lockStatus === 'new-source').length;
  const lockRelocked = results.filter((r) => r.lockStatus === 'relocked').length;

  if (totalChanges > 0) {
    log(`✅ ${totalChanges} file(s) ${options.dryRun ? 'would be ' : ''}synced`, colors.green);
    if (catalogAdds > 0) {
      log(
        `📋 ${catalogAdds} catalog entr${catalogAdds === 1 ? 'y' : 'ies'} auto-added`,
        colors.green,
      );
    }
  } else {
    log('✓ All sources up to date', colors.dim);
  }

  // Lock accounting — mirrors the existing summary block. Quarantined sources
  // are the drift-review queue: nothing of theirs was mirrored this run.
  log(
    `🔒 Lock: ${lockUnchanged} unchanged, ${lockNew} new (locked), ${lockRelocked} re-baselined, ${quarantined.length} quarantined (need --relock after review)`,
    quarantined.length > 0 ? colors.yellow : colors.dim,
  );
  quarantined.forEach((q) =>
    log(
      `   - ${q.source}: +${q.quarantined.added.length} added ~${q.quarantined.changed.length} changed -${q.quarantined.removed.length} removed vs locked baseline`,
      colors.red,
    ),
  );

  if (refused.length > 0) {
    log(
      `⛔ ${refused.length} source(s) REFUSED — malicious content quarantined; nothing of theirs was mirrored`,
      colors.red,
    );
    refused.forEach((r) =>
      log(`   - ${r.source}: ${r.refused.findings.length} REFUSE finding(s)`, colors.red),
    );
  }

  if (errors.length > 0) {
    log(`⚠️  ${errors.length} source(s) had errors`, colors.yellow);
    errors.forEach((e) => log(`   - ${e.source}: ${e.error}`, colors.red));
  }

  if (process.env.GITHUB_OUTPUT) {
    const outputFile = process.env.GITHUB_OUTPUT;
    fs.appendFileSync(outputFile, `changes=${totalChanges}\n`);
    fs.appendFileSync(outputFile, `catalog_adds=${catalogAdds}\n`);
    fs.appendFileSync(outputFile, `sources=${results.map((r) => r.source).join(',')}\n`);
    fs.appendFileSync(outputFile, `has_changes=${totalChanges > 0}\n`);
    // Surface partial-failure signal so the workflow can route a partial sync to
    // a human instead of auto-PR'ing it as a clean full sync.
    fs.appendFileSync(outputFile, `errors=${errors.length}\n`);
    fs.appendFileSync(outputFile, `failed_sources=${errors.map((e) => e.source).join(',')}\n`);
    // Drift-quarantine signal: the workflow treats a quarantined run like the
    // existing partial-sync path (no commit / no auto-PR; visibly red), so a
    // routine sync PR never silently carries drifted upstream content.
    fs.appendFileSync(outputFile, `quarantined=${quarantined.length}\n`);
    fs.appendFileSync(
      outputFile,
      `quarantined_sources=${quarantined.map((q) => q.source).join(',')}\n`,
    );
    // REFUSE-quarantine signal (blocker 62ye.2): a poisoned source is EXCLUDED
    // from the mirror, not walling the run — clean sources still commit + PR
    // (these outputs do NOT gate the commit/PR steps), and the workflow opens a
    // security-review issue per refused source from this signal.
    fs.appendFileSync(outputFile, `refused=${refused.length}\n`);
    fs.appendFileSync(outputFile, `refused_sources=${refused.map((r) => r.source).join(',')}\n`);
  }

  log('\n');
  // Exit non-zero on TOTAL failure (no source succeeded) always; and on ANY
  // partial failure OR drift quarantine when --strict is set, so a partial or
  // drift-tainted sync is never committed and auto-PR'd as a clean full sync.
  const totalFailures = errors.length === sourcesToSync.length;
  process.exit(
    totalFailures ||
      (options.strict && (errors.length > 0 || quarantined.length > 0 || refused.length > 0))
      ? 1
      : 0,
  );
}

// Only run when executed directly (node scripts/sync-external.mjs …) —
// the unit corpus imports matchesPattern from this module and must not
// trigger a live sync on import.
const invokedDirectly =
  process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (invokedDirectly) {
  main().catch((error) => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}
