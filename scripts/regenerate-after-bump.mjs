#!/usr/bin/env node
// Keep release projections in dependency order. --stage is for a disposable CI
// checkout: it stages the entire tree between writers for index-based consumers.
// Without it, callers own index synchronization. This command never commits.
import { spawnSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = fileURLToPath(new URL('..', import.meta.url));
export const GENERATORS = [
  ['pnpm', ['run', 'sync-marketplace']],
  ['node', ['marketplace/scripts/discover-skills.mjs', '--level=full']],
  ['node', ['marketplace/scripts/sync-catalog.mjs']],
  ['node', ['marketplace/scripts/generate-unified-search.mjs']],
  ['python3', ['freshie/scripts/promote-to-curated.py']],
  ['node', ['scripts/generate-saas-tutorial-lattice.mjs']],
  ['node', ['scripts/generate-readme-toc.mjs']],
  ['pnpm', ['run', 'normalize:dead-domain-projections']],
];
export const CHECKS = [
  ['node', ['marketplace/scripts/discover-skills.mjs', '--level=full', '--check']],
  ['node', ['marketplace/scripts/sync-catalog.mjs', '--check']],
  ['node', ['marketplace/scripts/generate-unified-search.mjs', '--check']],
  ['python3', ['freshie/scripts/promote-to-curated.py', '--check']],
  ['node', ['scripts/generate-saas-tutorial-lattice.mjs', '--check']],
];

export function runPipeline({ check = false, stage = false, run = spawnSync, root = ROOT } = {}) {
  if (check && stage) throw new Error('--check is non-mutating; cannot combine with --stage');
  const execute = (command, args) =>
    run(command, args, { cwd: root, stdio: 'inherit', shell: false });
  const stageTree = () => {
    const result = execute('git', ['add', '-A']);
    if (result.error || result.status !== 0) throw new Error('Projection staging failed');
  };
  if (stage) stageTree();
  const failures = [];
  for (const [command, args] of check ? CHECKS : GENERATORS) {
    const result = execute(command, args);
    if (result.error || result.status !== 0) {
      failures.push(`${command} ${args.join(' ')}`);
      // Never generate downstream projections from a failed upstream output.
      // Checks are independent and non-mutating: report every drift in one run.
      if (!check) break;
    }
    if (stage) stageTree();
  }
  if (failures.length)
    throw new Error(
      `Projection ${check ? 'checks' : 'regeneration'} failed:\n${failures.join('\n')}`,
    );
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    const args = process.argv.slice(2);
    if (args.length > 1 || (args.length === 1 && !['--check', '--stage'].includes(args[0]))) {
      throw new Error('Usage: node scripts/regenerate-after-bump.mjs [--check | --stage]');
    }
    runPipeline({ check: args[0] === '--check', stage: args[0] === '--stage' });
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
