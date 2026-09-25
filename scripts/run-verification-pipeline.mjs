#!/usr/bin/env node

/**
 * Verification Pipeline
 *
 * Runs the 100-point scoring system against all plugin skills and writes
 * verification results into marketplace.extended.json.
 *
 * Steps:
 *   1. Run validate-skills-schema.py --json --skills-only to get per-skill scores
 *   2. Aggregate scores per plugin (average across all skills in a plugin)
 *   3. Map scores to badge tiers: Gold (90-100), Silver (75-89), Bronze (60-74), None (<60)
 *   4. Write verification field into marketplace.extended.json
 *   5. Run sync-marketplace.cjs to sync the CLI catalog
 *   6. Print summary
 *
 * Usage:
 *   node scripts/run-verification-pipeline.mjs
 *   node scripts/run-verification-pipeline.mjs --dry-run    # Preview without writing
 *   node scripts/run-verification-pipeline.mjs --plugin snowflake-pack
 */

import { execSync } from 'node:child_process';
import { readFileSync, writeFileSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const repoRoot = join(__dirname, '..');

const extendedPath = join(repoRoot, '.claude-plugin', 'marketplace.extended.json');
const syncScript = join(repoRoot, 'scripts', 'sync-marketplace.cjs');
const validatorScript = join(repoRoot, 'scripts', 'validate-skills-schema.py');

const dryRun = process.argv.includes('--dry-run');
const pluginFlagIndex = process.argv.indexOf('--plugin');
const targetPlugin = pluginFlagIndex >= 0 ? process.argv[pluginFlagIndex + 1] : null;

if (pluginFlagIndex >= 0 && (!targetPlugin || targetPlugin.startsWith('--'))) {
  console.error('--plugin requires a plugin name or ./plugins/category/name source path');
  process.exit(2);
}

// === Badge tier mapping ===

function scoreToBadge(score) {
  if (score >= 90) return 'gold';
  if (score >= 75) return 'silver';
  if (score >= 60) return 'bronze';
  return null;
}

function scoreToGrade(score) {
  if (score >= 90) return 'A';
  if (score >= 80) return 'B';
  if (score >= 70) return 'C';
  if (score >= 60) return 'D';
  return 'F';
}

// === Step 1: Run the validator and get JSON output ===

function runValidator() {
  console.log('Step 1: Running skills validator...');

  let stdout;
  try {
    stdout = execSync(`python3 "${validatorScript}" --json --skills-only`, {
      cwd: repoRoot,
      encoding: 'utf-8',
      maxBuffer: 50 * 1024 * 1024,
    });
  } catch (err) {
    // The validator may exit non-zero on errors, but still produce JSON on stdout
    if (err.stdout) {
      stdout = err.stdout;
    } else {
      console.error('Failed to run validator:', err.message);
      process.exit(1);
    }
  }

  // The JSON output is on the last non-empty line (validator may print other text before it)
  const lines = stdout.trim().split('\n');
  let jsonLine = null;
  for (let i = lines.length - 1; i >= 0; i--) {
    const line = lines[i].trim();
    if (line.startsWith('[')) {
      jsonLine = line;
      break;
    }
  }

  if (!jsonLine) {
    console.error('No JSON output found from validator.');
    console.error('Raw output:', stdout.slice(0, 500));
    process.exit(1);
  }

  try {
    return JSON.parse(jsonLine);
  } catch (err) {
    console.error('Failed to parse validator JSON:', err.message);
    console.error('Raw line:', jsonLine.slice(0, 500));
    process.exit(1);
  }
}

// === Step 2: Aggregate scores per plugin ===

function aggregateByPlugin(skillResults) {
  console.log('Step 2: Aggregating scores per plugin...');

  // Map from plugin source path -> list of scores
  // Skill path format: plugins/[category]/[plugin-name]/skills/[skill-name]/SKILL.md
  // Plugin source format: ./plugins/[category]/[plugin-name]
  const pluginScores = new Map();

  for (const result of skillResults) {
    if (result.fatal) continue;
    // Skip the trailing kernel_shadow advisory element (DR-049 shadow block).
    if (result.kernel_shadow || typeof result.path !== 'string') continue;

    const parts = result.path.split(/[\\/]+/);
    // Validator output may be repository-relative or absolute. Anchor on the
    // plugins directory instead of assuming it is the first path component.
    const pluginsIndex = parts.indexOf('plugins');
    if (pluginsIndex < 0 || parts.length < pluginsIndex + 4) continue;

    const pluginSource = `./plugins/${parts[pluginsIndex + 1]}/${parts[pluginsIndex + 2]}`;

    if (!pluginScores.has(pluginSource)) {
      pluginScores.set(pluginSource, []);
    }
    pluginScores.get(pluginSource).push({
      score: result.score,
      grade: result.grade,
    });
  }

  // Calculate per-plugin aggregates
  const pluginVerifications = new Map();
  for (const [source, scores] of pluginScores) {
    const avgScore = Math.round(scores.reduce((sum, s) => sum + s.score, 0) / scores.length);
    pluginVerifications.set(source, {
      score: avgScore,
      grade: scoreToGrade(avgScore),
      badge: scoreToBadge(avgScore),
      skillCount: scores.length,
    });
  }

  return pluginVerifications;
}

/**
 * Write each plugin's verification result into the catalog. `lastValidated` is
 * the date the recorded result was established: an entry whose score, grade,
 * and badge are unchanged keeps its existing block, date included. Re-running
 * the pipeline on an unchanged tree therefore changes nothing. Before this, every
 * run restamped all entries with the current date, so any two pull requests that
 * ran it conflicted across the whole catalog even when no result had changed.
 * Returns the number of entries whose result changed.
 */
function sameResult(current, next) {
  return (
    current !== null &&
    typeof current === 'object' &&
    current.score === next.score &&
    current.grade === next.grade &&
    current.badge === next.badge
  );
}

function applyVerifications(catalog, pluginVerifications, requestedPlugin, validatedAt) {
  let updated = 0;
  for (const plugin of catalog.plugins) {
    if (!plugin || !plugin.source) continue;
    if (requestedPlugin && plugin.name !== requestedPlugin && plugin.source !== requestedPlugin) {
      continue;
    }

    const verification = pluginVerifications.get(plugin.source);
    if (!verification) continue;

    const next = {
      score: verification.score,
      grade: verification.grade,
      badge: verification.badge,
    };
    if (sameResult(plugin.verification, next)) continue;

    plugin.verification = { ...next, lastValidated: validatedAt };
    updated++;
  }
  return updated;
}

// === Step 3: Update marketplace.extended.json ===

function updateCatalog(pluginVerifications) {
  console.log('Step 3: Updating marketplace.extended.json...');

  const raw = readFileSync(extendedPath, 'utf-8');
  let catalog;
  try {
    catalog = JSON.parse(raw);
  } catch (err) {
    console.error('Failed to parse marketplace.extended.json:', err.message);
    process.exit(1);
  }

  if (!Array.isArray(catalog.plugins)) {
    console.error('Invalid catalog format: expected "plugins" array.');
    process.exit(1);
  }

  const now = new Date().toISOString().replace(/T.*/, 'T00:00:00.000Z');
  const updated = applyVerifications(catalog, pluginVerifications, targetPlugin, now);

  if (!dryRun && updated === 0) {
    console.log('   No verification result changed; catalog left untouched.');
  } else if (!dryRun) {
    writeFileSync(extendedPath, JSON.stringify(catalog, null, 2) + '\n');
    console.log(`   Updated ${updated} plugin entries.`);
  } else {
    console.log(`   [DRY RUN] Would update ${updated} plugin entries.`);
  }

  return { updated, total: catalog.plugins.length };
}

// === Step 4: Sync CLI catalog ===

function syncCatalog() {
  if (dryRun) {
    console.log('Step 4: [DRY RUN] Skipping sync-marketplace.cjs');
    return;
  }

  console.log('Step 4: Syncing CLI catalog...');
  try {
    const output = execSync(`node "${syncScript}"`, {
      cwd: repoRoot,
      encoding: 'utf-8',
    });
    console.log(`   ${output.trim()}`);
  } catch (err) {
    console.error('Failed to sync marketplace:', err.message);
    process.exit(1);
  }
}

// === Step 5: Summary ===

function printSummary(pluginVerifications, catalogStats) {
  const sep = '='.repeat(60);
  console.log(`\n${sep}`);
  console.log('VERIFICATION PIPELINE SUMMARY');
  console.log(sep);

  console.log(`\nPlugins scored:    ${pluginVerifications.size}`);
  if (targetPlugin) console.log(`Target plugin:     ${targetPlugin}`);
  console.log(`Catalog updated:   ${catalogStats.updated} / ${catalogStats.total} plugins`);

  // Grade distribution
  const gradeDist = { A: 0, B: 0, C: 0, D: 0, F: 0 };
  for (const v of pluginVerifications.values()) {
    gradeDist[v.grade]++;
  }

  console.log('\nGrade Distribution:');
  for (const letter of ['A', 'B', 'C', 'D', 'F']) {
    const count = gradeDist[letter];
    const pct = pluginVerifications.size
      ? ((count / pluginVerifications.size) * 100).toFixed(1)
      : '0.0';
    const bar = '#'.repeat(Math.round((count / Math.max(pluginVerifications.size, 1)) * 30));
    console.log(`  ${letter}: ${String(count).padStart(4)} (${pct.padStart(5)}%)  ${bar}`);
  }

  // Badge distribution
  const badgeDist = { gold: 0, silver: 0, bronze: 0, none: 0 };
  for (const v of pluginVerifications.values()) {
    badgeDist[v.badge || 'none']++;
  }

  console.log('\nBadge Distribution:');
  console.log(`  Gold   (90-100): ${badgeDist.gold}`);
  console.log(`  Silver (75-89):  ${badgeDist.silver}`);
  console.log(`  Bronze (60-74):  ${badgeDist.bronze}`);
  console.log(`  None   (<60):    ${badgeDist.none}`);

  // Average score
  const scores = [...pluginVerifications.values()].map((v) => v.score);
  const avg = scores.length
    ? (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1)
    : '0.0';
  console.log(`\nAverage Score: ${avg}/100`);

  console.log(sep);

  if (dryRun) {
    console.log('\n[DRY RUN] No files were modified.');
  }
}

// === Main ===

function main() {
  console.log(sep('Verification Pipeline'));
  if (dryRun) {
    console.log('[DRY RUN MODE - no files will be modified]\n');
  }

  const skillResults = runValidator();
  console.log(`   Found ${skillResults.length} skill results.\n`);

  const pluginVerifications = aggregateByPlugin(skillResults);
  console.log(`   Aggregated to ${pluginVerifications.size} plugins.\n`);

  const catalogStats = updateCatalog(pluginVerifications);
  console.log('');

  syncCatalog();

  printSummary(pluginVerifications, catalogStats);
}

function sep(title) {
  const line = '='.repeat(60);
  return `${line}\n ${title}\n${line}`;
}

export { aggregateByPlugin, applyVerifications, scoreToBadge, scoreToGrade };

if (process.argv[1] && resolve(process.argv[1]) === __filename) {
  main();
}
