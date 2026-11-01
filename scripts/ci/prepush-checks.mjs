#!/usr/bin/env node
/** Focused read-only checks; preserve CI as the full trusted acceptance boundary. */
import { spawnSync } from 'node:child_process';
import { existsSync, readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

export function planChecks(
  paths,
  exists = existsSync,
  read = (path) => readFileSync(path, 'utf8'),
) {
  const plan = [],
    tests = new Set(),
    packages = new Set();
  const workflows = paths.filter(
    (path) => /^\.github\/workflows\/[^/]+\.ya?ml$/.test(path) && exists(path),
  );
  if (workflows.length) plan.push(['actionlint', ...workflows]);
  for (const path of paths) {
    if (/^scripts\/.*\.test\.mjs$/.test(path) && exists(path)) tests.add(path);
    if (/^scripts\/.*\.mjs$/.test(path)) {
      const test = path.replace(/\.mjs$/, '.test.mjs');
      if (exists(test)) tests.add(test);
    }
    if (/^(packages|plugins)\//.test(path) && /(?:\.(ts|tsx|js|mjs)|\/package\.json)$/.test(path)) {
      let dir = dirname(path);
      while (dir !== '.' && dir !== '/') {
        if (exists(`${dir}/.source.json`)) break; // Do not invent commands for upstream mirrors.
        if (exists(`${dir}/package.json`)) {
          const pkg = JSON.parse(read(`${dir}/package.json`));
          if (pkg.scripts?.typecheck) packages.add(dir);
          break;
        }
        dir = dirname(dir);
      }
    }
  }
  const python = new Set();
  for (const path of paths) {
    if (/^tests\/ci\/test_[a-z0-9_]+\.py$/.test(path) && exists(path))
      python.add(path.replace(/\.py$/, '').replaceAll('/', '.'));
    if (/^scripts\/ci\/[a-z0-9_]+\.py$/.test(path)) {
      const candidate = path.replace('scripts/ci/', 'tests/ci/test_');
      if (exists(candidate)) python.add(candidate.replace(/\.py$/, '').replaceAll('/', '.'));
      if (['scripts/ci/fastlane.py', 'scripts/ci/link_scope.py'].includes(path))
        python.add('tests.ci.test_ci_performance');
    }
  }
  if (python.size)
    plan.push([
      'python3',
      '-m',
      'pytest',
      ...[...python].sort().map((name) => name.replaceAll('.', '/') + '.py'),
      '-q',
    ]);
  if (tests.size) plan.push(['node', '--test', ...[...tests].sort()]);
  for (const dir of [...packages].sort()) plan.push(['pnpm', '--filter', `./${dir}`, 'typecheck']);
  return plan;
}
export function checkEnvironment(environment = process.env) {
  // Hooks export repository-local Git state. Nested fixture repositories must
  // discover their own Git directory and index, instead of mutating this one.
  return Object.fromEntries(Object.entries(environment).filter(([key]) => !key.startsWith('GIT_')));
}

export function main() {
  const env = checkEnvironment();
  const diff = spawnSync(
    'git',
    ['diff', '--name-only', '-z', '--diff-filter=ACMR', 'origin/main...HEAD'],
    { encoding: 'utf8', env },
  );
  if (diff.status !== 0) throw new Error('Cannot determine committed changes against origin/main');
  const paths = diff.stdout.split('\0').filter(Boolean);
  for (const [command, ...args] of planChecks(paths)) {
    console.error(`Pre-push: ${command} ${args.join(' ')}`);
    const result = spawnSync(command, args, { stdio: 'inherit', env });
    if (result.error || result.status !== 0)
      throw new Error(
        `Pre-push check failed: ${command}. ${result.error?.message || 'Fix the reported failure before pushing.'}`,
      );
  }
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    main();
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
