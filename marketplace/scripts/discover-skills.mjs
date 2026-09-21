#!/usr/bin/env node

/**
 * Skills Discovery Script
 *
 * Scans the plugins directory for all SKILL.md files, parses their frontmatter,
 * and generates a comprehensive skills catalog for the Astro marketplace.
 *
 * ── Three-surface skill-count funnel (per #660 item 2) ────────────────────
 *
 * Three different skill counts exist across surfaces; the difference is
 * intentional filtering at each stage. Documenting here so future
 * maintainers don't re-investigate.
 *
 *   1) Filesystem            (~3,060 SKILL.md files found by `find plugins`)
 *      Raw count of every SKILL.md on disk, including those in:
 *        - Excluded subtrees (skill-databases/windsurf is intentionally
 *          excluded by sync-marketplace.cjs as a "personal-prefix or known
 *          duplicate")
 *        - Nested per-skill manifest dirs (synced packs like tonone ship
 *          a per-skill .claude-plugin/plugin.json — those skills still
 *          live under the outer tonone plugin, not as separate plugins)
 *
 *   2) Freshie discovery      (~3,000, freshie/scripts/rebuild-inventory.py)
 *      Subset of (1) after frontmatter validation. Skills with missing or
 *      malformed YAML headers fall out — they can't be classified.
 *
 *   3) Marketplace catalog    (~2,750, this script's main output)
 *      Subset of (2) where the parent plugin has a catalog entry in
 *      .claude-plugin/marketplace.extended.json. Skills whose parent isn't
 *      in the catalog are reported as "orphaned" — they exist on disk and
 *      validate cleanly but are not surfaced to users because the parent
 *      plugin was never registered with the marketplace.
 *
 *      As of 2026-05-17, the orphan list is dominated by synced packs
 *      (tonone, claude-pack, windsurf, general-legal-assistant,
 *      cli-power-skills, claudebase, claude-workflow-skills) that exist
 *      in sources.yaml but have no top-level entry in
 *      marketplace.extended.json. Resolution path: add catalog entries
 *      for the synced packs that should be user-visible; leave intentional
 *      exclusions (windsurf nested under skill-databases) as orphans.
 *
 * Parent-plugin attribution: skills/<skill-name>/.claude-plugin/plugin.json
 * is NOT treated as the parent — the walk-up logic skips any plugin.json
 * found inside a `/skills/` subtree and continues to the outer plugin
 * manifest. Mirrors the `-maxdepth 4` filter in
 * .github/workflows/validate-plugins.yml's "Check plugin structure" step.
 */

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { createRequire } from 'node:module';
import * as nodePath from 'node:path';
import { join, dirname, relative } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'url';
import {
  assertGeneratedContentCurrent,
  readIndexedArtifact,
} from '../../scripts/check-generated-artifacts.mjs';
import { resolveCorpus } from '../../scripts/corpus-resolver.mjs';
import { parseSkillFrontmatter } from '../../scripts/skill-frontmatter.mjs';
import { mdToHtml } from './md-to-html.mjs';

const require = createRequire(import.meta.url);
const { publishedPlugins } = require('../../scripts/publication-policy.cjs');

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const ROOT_DIR = join(__dirname, '..', '..');
const PLUGINS_DIR = join(ROOT_DIR, 'plugins');
const OUTPUT_FILE = join(ROOT_DIR, 'marketplace', 'src', 'data', 'skills-catalog.json');
const INDEX_FILE = join(ROOT_DIR, 'marketplace', 'src', 'data', 'skills-index.json');
const MARKETPLACE_CATALOG = join(ROOT_DIR, '.claude-plugin', 'marketplace.extended.json');

// ── Progressive disclosure level ─────────────────────────────────────────
// L0 (metadata): name + description + parent + version + slug; no body HTML.
//   Emitted to skills-index.json — fast load for catalog browsing / trigger
//   matching. Whole index is ~3-10 KB gzipped at our scale.
// L1 (full): full catalog including body HTML. Emitted to skills-catalog.json.
//   Default mode for backward compat with marketplace UI build.
// L2 (file): runtime-only — single reference file read by client on demand.
//   Not a build-time concern; CLI errors with guidance.
const LEVELS = new Set(['metadata', 'full', 'file']);
let LEVEL = 'full';
const CHECK = process.argv.includes('--check');
for (const arg of process.argv.slice(2)) {
  const m = arg.match(/^--level=(.+)$/);
  if (m) LEVEL = m[1];
}

export function compareSkillNamesOrdinal(left, right) {
  return left < right ? -1 : left > right ? 1 : 0;
}

function preservedGeneratedAt(path, label) {
  let value;
  try {
    value = JSON.parse(
      readIndexedArtifact(relative(ROOT_DIR, path), { root: ROOT_DIR }).toString('utf8'),
    ).generatedAt;
  } catch (error) {
    throw new Error(`cannot preserve ${label} generatedAt from ${path}: ${error.message}`);
  }
  if (typeof value !== 'string' || !Number.isFinite(Date.parse(value))) {
    throw new Error(`cannot preserve invalid ${label} generatedAt in ${path}`);
  }
  return value;
}
if (!LEVELS.has(LEVEL)) {
  console.error(`❌ Unknown --level=${LEVEL}. Expected: metadata | full | file`);
  process.exit(2);
}
if (LEVEL === 'file') {
  console.error('❌ --level=file is a runtime concern (client-side reference-file read).');
  console.error('   Build step emits L0 (skills-index.json) + L1 (skills-catalog.json).');
  console.error('   For a single reference file, read it directly from the plugin path.');
  process.exit(2);
}

/**
 * Parse YAML frontmatter from markdown content
 */
export const parseFrontmatter = parseSkillFrontmatter;

function isPlainMapping(value) {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) return false;
  const prototype = Object.getPrototypeOf(value);
  return prototype === Object.prototype || prototype === null;
}

/**
 * Generate URL-safe slug from skill name
 */
function generateSlug(name) {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
}

/**
 * Extract category from plugin path
 */
export function normalizePortablePath(candidate, pathApi = nodePath) {
  return String(candidate).split(pathApi.sep).join('/');
}

export function repositoryRelativePath(root, candidate, pathApi = nodePath) {
  return normalizePortablePath(pathApi.relative(root, candidate), pathApi);
}

export function extractCategory(pluginPath, pathApi = nodePath) {
  const parts = normalizePortablePath(pluginPath, pathApi).split('/');
  const pluginsIndex = parts.indexOf('plugins');
  if (pluginsIndex >= 0 && parts.length > pluginsIndex + 1) {
    return parts[pluginsIndex + 1];
  }
  return 'unknown';
}

/**
 * Extract plugin name from path
 */
export function extractPluginName(pluginPath, pathApi = nodePath) {
  const parts = normalizePortablePath(pluginPath, pathApi).split('/');
  return parts[parts.length - 1] || 'unknown';
}

/**
 * Get plugin metadata from plugin.json
 */
function getPluginMetadata(pluginDir) {
  const pluginJsonPath = join(pluginDir, '.claude-plugin', 'plugin.json');

  if (existsSync(pluginJsonPath)) {
    try {
      const pluginJson = JSON.parse(readFileSync(pluginJsonPath, 'utf-8'));
      return {
        name: pluginJson.name || extractPluginName(pluginDir),
        version: pluginJson.version,
        description: pluginJson.description,
        author: pluginJson.author
      };
    } catch (error) {
      if (CHECK) throw new Error(`failed to parse plugin.json at ${pluginJsonPath}: ${error.message}`);
      console.warn(`Failed to parse plugin.json at ${pluginJsonPath}: ${error.message}`);
    }
  }

  return {
    name: extractPluginName(pluginDir),
    version: 'unknown',
    description: '',
    author: ''
  };
}

/**
 * Normalize a frontmatter list-of-strings field. Accepts three forms:
 *   1. Real array (from block-list `- item` syntax) — returned as-is.
 *   2. Inline-array string `[a, b, c]` — bracket-stripped + comma-split.
 *   3. CSV string `a, b, c` — comma-split.
 * Each item is trimmed; surrounding quotes are stripped. Empty entries dropped.
 * Returns [] for missing/empty values.
 */
export function normalizeListField(value, fieldName) {
  if (value === undefined || value === null || value === '') return [];
  if (Array.isArray(value)) {
    return value
      .map((item, index) => {
        if (typeof item !== 'string') {
          throw new TypeError(`frontmatter ${fieldName}[${index}] must be a string`);
        }
        return item.trim().replace(/^['"]|['"]$/g, '');
      })
      .filter(Boolean);
  }
  if (typeof value === 'string') {
    let s = value.trim();
    if (s.startsWith('[') && s.endsWith(']')) s = s.slice(1, -1);
    return s.split(',').map(p => p.trim().replace(/^['"]|['"]$/g, '')).filter(Boolean);
  }
  throw new TypeError(`frontmatter ${fieldName} must be a string or a list of strings`);
}

function optionalStringField(metadata, fieldName, fallback) {
  const value = metadata[fieldName];
  if (value === undefined || value === null || value === '') return fallback;
  if (typeof value !== 'string') {
    throw new TypeError(`frontmatter ${fieldName} must be a string`);
  }
  return value;
}

export function normalizeDescription(value) {
  if (typeof value !== 'string') {
    throw new TypeError('frontmatter description must be a string');
  }

  // Descriptions are public card/search metadata, not Markdown bodies. YAML
  // block scalars may contain source-formatting newlines, but every consumer
  // expects one searchable line. Preserve the complete semantic value while
  // normalizing presentation whitespace at this projection boundary.
  return value.replace(/\s+/gu, ' ').trim();
}

export function resolveSkillVersion(metadata) {
  const nested = metadata.metadata;
  if (nested !== undefined && nested !== null && !isPlainMapping(nested)) {
    throw new TypeError('frontmatter metadata must be a mapping');
  }

  const directVersion = optionalStringField(metadata, 'version', '');
  const nestedVersion = nested ? optionalStringField(nested, 'version', '') : '';
  if (directVersion && nestedVersion && directVersion !== nestedVersion) {
    throw new TypeError('frontmatter version conflicts with metadata.version');
  }
  return directVersion || nestedVersion || '1.0.0';
}

function normalizeAuthor(value) {
  if (value === undefined || value === null || value === '') return '';
  if (typeof value === 'string') return value;
  if (!isPlainMapping(value) || typeof value.name !== 'string') {
    throw new TypeError('frontmatter author must be a string or a mapping with a string name');
  }
  if (value.email !== undefined && value.email !== null && typeof value.email !== 'string') {
    throw new TypeError('frontmatter author.email must be a string');
  }
  return value.email ? `${value.name} <${value.email}>` : value.name;
}

/**
 * Project a full skill record down to its L0 metadata view.
 * Fields chosen for trigger-match / catalog browse + client-side visibility
 * filtering — no body, no HTML.
 */
function projectL0(skill) {
  const v = skill.visibility || {};
  return {
    slug: skill.slug,
    name: skill.name,
    description: skill.description,
    version: skill.version,
    category: skill.parentPlugin.category,
    parentPlugin: skill.parentPlugin.name,
    // Visibility (schema 3.5.0). Empty arrays preserved so client code can
    // pattern-match without null-checking; absent fields default to [].
    requires_env: v.requires_env || [],
    requires_tools: v.requires_tools || [],
    fallback_for_env: v.fallback_for_env || [],
    fallback_for_tools: v.fallback_for_tools || [],
  };
}

/**
 * Process a single SKILL.md file
 *
 * @param {string} filePath
 * @param {{ metadataOnly?: boolean }} [opts]
 *   metadataOnly skips the mdToHtml body conversion — significant speedup
 *   on metadata-only builds.
 */
function processSkillFile(filePath, opts = {}) {
  const metadataOnly = opts.metadataOnly === true;
  try {
    const content = readFileSync(filePath, 'utf-8');
    const frontmatter = parseFrontmatter(content);

    if (!frontmatter) {
      console.warn(`No valid frontmatter found in ${filePath}`);
      return null;
    }

    // Extract markdown content (everything after frontmatter).
    // Skipped entirely in metadataOnly mode — mdToHtml is the slow step.
    const contentMatch = metadataOnly
      ? null
      : content.match(/^---\r?\n[\s\S]*?\r?\n---(?:\r?\n|$)([\s\S]*)$/);
    const markdownContent = contentMatch ? contentMatch[1].trim() : '';

    // Find parent plugin directory (go up until we find .claude-plugin).
    // CRITICAL: skip any .claude-plugin/plugin.json found INSIDE a /skills/
    // subtree. Some synced upstreams (notably tonone, claude-pack, windsurf)
    // ship a per-skill .claude-plugin/plugin.json so each skill can be
    // installed standalone. Treating those as the "parent plugin" leaves
    // 250+ skills mis-attributed to non-existent parents (each shows up as
    // an orphan because the per-skill manifest's `name` isn't in
    // marketplace.extended.json). Mirrors the `-maxdepth 4` filter already
    // applied in .github/workflows/validate-plugins.yml's "Check plugin
    // structure" step and in CLAUDE.md guidance. See #660 item 2.
    let currentDir = dirname(filePath);
    let pluginDir = null;

    for (let i = 0; i < 10; i++) { // Max 10 levels up
      if (existsSync(join(currentDir, '.claude-plugin', 'plugin.json'))) {
        // Only accept this plugin.json if it's NOT inside a /skills/ subtree.
        // The split-on-/skills/ test catches every form:
        //   .../plugin/skills/foo/...               → reject (inside skills/)
        //   .../plugin/skills/foo/sub/...           → reject
        //   .../plugin/                             → accept (no skills/ above)
        const relFromRoot = repositoryRelativePath(ROOT_DIR, currentDir);
        const skillsIdx = relFromRoot.split('/').indexOf('skills');
        // Reject if `skills` appears anywhere BEFORE the leaf — that means
        // we're inside the skills/ subtree of a higher-level plugin.
        const insideSkillsSubtree = skillsIdx >= 0 && skillsIdx < relFromRoot.split('/').length - 1;
        if (!insideSkillsSubtree) {
          pluginDir = currentDir;
          break;
        }
        // Otherwise keep walking up — we want the OUTER plugin manifest.
      }
      currentDir = dirname(currentDir);
    }

    // If no .claude-plugin found, use the directory structure to infer plugin dir
    // Skills are typically in plugins/category/plugin-name/skills/skill-name/SKILL.md
    if (!pluginDir) {
      const parts = normalizePortablePath(filePath).split('/');
      const skillsIndex = parts.findIndex(p => p === 'skills');
      if (skillsIndex >= 2) {
        // Go up to plugin-name level (2 levels before 'skills')
        pluginDir = parts.slice(0, skillsIndex).join('/');
      }
    }

    if (!pluginDir) {
      console.warn(`Could not find parent plugin directory for ${filePath}`);
      return null;
    }

    const category = extractCategory(pluginDir);
    const pluginMetadata = getPluginMetadata(pluginDir);
    const relativePath = repositoryRelativePath(ROOT_DIR, filePath);

    // Generate slug from name
    const name = optionalStringField(frontmatter, 'name', 'Unnamed Skill');
    const description = normalizeDescription(optionalStringField(frontmatter, 'description', ''));
    const version = resolveSkillVersion(frontmatter);
    const license = optionalStringField(frontmatter, 'license', 'MIT');
    const slug = generateSlug(name || 'unnamed-skill');

    // Ensure allowedTools is always an array
    const allowedTools = normalizeListField(frontmatter['allowed-tools'], 'allowed-tools');

    // Normalize author to string
    const authorStr = normalizeAuthor(frontmatter.author ?? pluginMetadata.author);

    // Parse compatible-with field
    const compatibleWith = normalizeListField(frontmatter['compatible-with'], 'compatible-with')
      .map(value => value.toLowerCase());

    // Visibility fields (schema 3.5.0) — normalized to JS arrays from any of
    // block-list / inline-array / CSV forms. All optional; default [].
    const visibility = {
      requires_env: normalizeListField(frontmatter.requires_env, 'requires_env'),
      requires_tools: normalizeListField(frontmatter.requires_tools, 'requires_tools'),
      fallback_for_env: normalizeListField(frontmatter.fallback_for_env, 'fallback_for_env'),
      fallback_for_tools: normalizeListField(frontmatter.fallback_for_tools, 'fallback_for_tools'),
    };

    return {
      slug,
      name,
      description,
      allowedTools,
      compatibleWith,
      visibility,
      version,
      author: authorStr,
      license,
      content: metadataOnly ? '' : mdToHtml(markdownContent),
      parentPlugin: {
        name: pluginMetadata.name,
        category: category,
        path: repositoryRelativePath(ROOT_DIR, pluginDir),
        version: pluginMetadata.version,
        description: pluginMetadata.description
      },
      filePath: relativePath
    };
  } catch (error) {
    console.error(`Error processing ${filePath}: ${error.message}`);
    return null;
  }
}

/**
 * Main execution
 */
function main() {
  const metadataOnly = LEVEL === 'metadata';
  console.log('🔍 Discovering skills across plugin marketplace...\n');
  console.log(`Plugins directory: ${PLUGINS_DIR}`);
  console.log(`Level:             ${LEVEL}${metadataOnly ? ' (L0 index only — no body HTML)' : ' (L0 index + L1 catalog)'}`);
  console.log(`Index output:      ${INDEX_FILE}`);
  if (!metadataOnly) console.log(`Catalog output:    ${OUTPUT_FILE}`);
  console.log('');

  // Load marketplace catalog to get valid plugin names
  let marketplacePluginNames = new Set();
  try {
    const marketplaceCatalog = JSON.parse(readFileSync(MARKETPLACE_CATALOG, 'utf-8'));
    marketplacePluginNames = new Set(
      publishedPlugins(marketplaceCatalog.plugins, 'extended catalog').map((p) => p.name),
    );
    console.log(`📦 Loaded marketplace catalog: ${marketplacePluginNames.size} plugins\n`);
  } catch (error) {
    if (CHECK) throw new Error(`cannot load marketplace catalog in check mode: ${error.message}`);
    console.warn(`⚠️  Could not load marketplace catalog: ${error.message}`);
    console.warn(`    Proceeding without marketplace filtering...\n`);
  }

  // Find all SKILL.md files
  const skillFiles = resolveCorpus('marketplace-visible', { root: ROOT_DIR }).map((entry) =>
    join(ROOT_DIR, entry),
  );
  console.log(`Found ${skillFiles.length} SKILL.md files\n`);

  // Process each skill file
  const skills = [];
  const orphanedSkills = [];
  let successCount = 0;
  let failCount = 0;

  for (const filePath of skillFiles) {
    const skill = processSkillFile(filePath, { metadataOnly });
    if (skill) {
      // Resolver membership is authoritative; keep this assertion as a
      // defensive check against catalog changes during a long generation run.
      if (marketplacePluginNames.size === 0 || marketplacePluginNames.has(skill.parentPlugin.name)) {
        skills.push(skill);
        successCount++;
      } else {
        orphanedSkills.push({
          skill: skill.name,
          parentPlugin: skill.parentPlugin.name,
          filePath: skill.filePath
        });
      }
    } else {
      failCount++;
    }
  }

  console.log(`✅ Successfully processed: ${successCount}`);
  console.log(`❌ Failed to process: ${failCount}`);
  if (orphanedSkills.length > 0) {
    console.log(`⚠️  Orphaned skills (parent not in marketplace): ${orphanedSkills.length}`);
    orphanedSkills.forEach(({ skill, parentPlugin, filePath }) => {
      console.log(`    • ${skill} (parent: ${parentPlugin})`);
      console.log(`      ${filePath}`);
    });
  }
  console.log('');

  if (failCount > 0) {
    throw new Error(`refusing to generate an incomplete skill projection: ${failCount} source file(s) failed`);
  }

  // Sort skills by name
  skills.sort((a, b) => compareSkillNamesOrdinal(a.name, b.name));

  // Check for duplicate slugs
  const slugCounts = {};
  for (const skill of skills) {
    slugCounts[skill.slug] = (slugCounts[skill.slug] || 0) + 1;
  }

  const duplicateSlugs = Object.entries(slugCounts)
    .filter(([_, count]) => count > 1)
    .map(([slug, _]) => slug);

  if (duplicateSlugs.length > 0) {
    console.warn(`⚠️  Found ${duplicateSlugs.length} duplicate slugs:`);
    duplicateSlugs.forEach(slug => {
      const dupes = skills.filter(s => s.slug === slug);
      console.warn(`  - ${slug} (${dupes.length} occurrences)`);
      // Add unique suffix to duplicates
      dupes.forEach((skill, index) => {
        if (index > 0) {
          skill.slug = `${skill.slug}-${index + 1}`;
        }
      });
    });
    console.log('');
  }

  const generatedAt = new Date().toISOString();
  const indexGeneratedAt = CHECK
    ? preservedGeneratedAt(INDEX_FILE, 'skills index')
    : generatedAt;
  const catalogGeneratedAt = CHECK && !metadataOnly
    ? preservedGeneratedAt(OUTPUT_FILE, 'skills catalog')
    : generatedAt;
  const categories = [...new Set(skills.map(s => s.parentPlugin.category))].sort();

  // L0 index — always emitted. ~150 bytes per skill, ~3-10 KB gzipped at our
  // scale. Schema v3.4.0 contract: clients load this first for trigger match
  // / catalog browse, then fetch L1 (skills-catalog.json) only on demand.
  const index = {
    schemaVersion: '3.6.0',
    level: 'metadata',
    skills: skills.map(projectL0),
    count: skills.length,
    generatedAt: indexGeneratedAt,
    categories,
  };
  const indexBytes = JSON.stringify(index, null, 2);
  if (!CHECK) writeFileSync(INDEX_FILE, indexBytes);
  console.log(
    `✅ L0 index ${CHECK ? 'rendered for check' : 'generated'}:   ${INDEX_FILE}  (${skills.length} skills)`,
  );

  // L1 catalog — only emitted at level=full. Heavy artifact with body HTML.
  let catalogBytes = null;
  if (!metadataOnly) {
    const catalog = {
      schemaVersion: '3.6.0',
      level: 'full',
      skills,
      count: skills.length,
      generatedAt: catalogGeneratedAt,
      categories,
      allowedToolsUsed: [...new Set(skills.flatMap(s => s.allowedTools))].sort()
    };
    catalogBytes = JSON.stringify(catalog, null, 2);
    if (!CHECK) writeFileSync(OUTPUT_FILE, catalogBytes);
    console.log(
      `✅ L1 catalog ${CHECK ? 'rendered for check' : 'generated'}: ${OUTPUT_FILE}  (${skills.length} skills with body HTML)`,
    );
  } else {
    console.log(`ℹ️  L1 catalog skipped (level=metadata — re-run without --level to emit it).`);
  }

  console.log('');
  console.log('📊 Skills Summary:');
  console.log(`   Total skills: ${skills.length}`);
  console.log(`   Categories: ${categories.length}`);
  if (!metadataOnly) {
    const allowedToolsUsed = [...new Set(skills.flatMap(s => s.allowedTools))];
    console.log(`   Unique tools: ${allowedToolsUsed.length}`);
  }

  // Show sample
  console.log('\n📝 First 3 skills:');
  skills.slice(0, 3).forEach((skill, i) => {
    console.log(`\n${i + 1}. ${skill.name}`);
    console.log(`   Slug: ${skill.slug}`);
    console.log(`   Category: ${skill.parentPlugin.category}`);
    console.log(`   Plugin: ${skill.parentPlugin.name}`);
    if (!metadataOnly) console.log(`   Tools: ${skill.allowedTools.join(', ')}`);
  });

  if (CHECK) {
    const candidates = [
      { path: 'marketplace/src/data/skills-index.json', contents: indexBytes },
      ...(metadataOnly
        ? []
        : [{ path: 'marketplace/src/data/skills-catalog.json', contents: catalogBytes }]),
    ];
    assertGeneratedContentCurrent(candidates, { root: ROOT_DIR });
    console.log(
      `\n✅ Generated skill projections match the Git index (${candidates.length} checked${metadataOnly ? '; skills-catalog pending' : ''})`,
    );
  }

  process.exit(0);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main();
