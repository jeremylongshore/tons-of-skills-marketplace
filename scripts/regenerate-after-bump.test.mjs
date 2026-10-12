import assert from 'node:assert/strict';
import { execFileSync, spawnSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { GENERATORS, CHECKS, runPipeline } from './regenerate-after-bump.mjs';

test('regeneration invokes every canonical writer in dependency order without shell expansion', () => {
  const calls = [];
  runPipeline({
    root: '/fixture',
    run(command, args, options) {
      calls.push([command, args]);
      assert.equal(options.cwd, '/fixture');
      assert.equal(options.shell, false);
      return { status: 0 };
    },
  });
  assert.deepEqual(calls, GENERATORS);
  // The verification refresh writes the catalog, so it must precede every reader.
  assert.deepEqual(calls[0], ['node', ['scripts/run-verification-pipeline.mjs']]);
  assert.deepEqual(calls[1], ['pnpm', ['run', 'sync-marketplace']]);
  assert.deepEqual(
    calls.slice(2, 5).map(([, args]) => args[0]),
    [
      'marketplace/scripts/discover-skills.mjs',
      'marketplace/scripts/sync-catalog.mjs',
      'marketplace/scripts/generate-unified-search.mjs',
    ],
  );
  assert.ok(calls.some(([, args]) => args[0] === 'freshie/scripts/promote-to-curated.py'));
  assert.ok(calls.some(([, args]) => args[0] === 'scripts/generate-saas-tutorial-lattice.mjs'));
});

for (const failure of [
  { status: 1 },
  { status: null, signal: 'SIGTERM' },
  { error: new Error('ENOENT') },
]) {
  test(`regeneration stops on subprocess failure ${JSON.stringify(failure)}`, () => {
    let calls = 0;
    assert.throws(
      () =>
        runPipeline({
          run() {
            calls++;
            return failure;
          },
        }),
      /regeneration failed/,
    );
    assert.equal(calls, 1);
  });
}

test('check mode runs all checks and reports all drift, without invoking writers', () => {
  const calls = [];
  assert.throws(
    () =>
      runPipeline({
        check: true,
        run(command, args) {
          calls.push([command, args]);
          assert.ok(args.includes('--check'));
          return { status: 1 };
        },
      }),
    (error) =>
      CHECKS.every(([command, args]) => error.message.includes(`${command} ${args.join(' ')}`)),
  );
  assert.deepEqual(calls, CHECKS);
});

test('workflow regenerates and validates before pushing, retaining fork and event boundaries', () => {
  const workflow = readFileSync(
    new URL('../.github/workflows/auto-bump-on-pr.yml', import.meta.url),
    'utf8',
  );
  const regen = workflow.indexOf('run: node scripts/regenerate-after-bump.mjs --stage\n');
  const check = workflow.indexOf('node scripts/regenerate-after-bump.mjs --check');
  const push = workflow.indexOf('git push origin HEAD:');
  assert.ok(regen > 0 && regen < check && check < push);
  assert.match(workflow, /head.repo.full_name == github.repository/);
  assert.match(workflow, /^ {2}pull_request:/m);
  assert.doesNotMatch(workflow, /^ {2}pull_request_target:/m);
  assert.match(workflow, /pnpm install --frozen-lockfile.*--ignore-scripts/);
  assert.match(workflow, /git add -A\n.*node scripts\/regenerate-after-bump.mjs --check/);
  assert.doesNotMatch(workflow, /pnpm run measure:e1|node scripts\/measure-epic-1\.mjs/);
});

test('CI staging refreshes index before every downstream consumer, including membership changes', () => {
  let indexCurrent = false;
  let curatedWritten = false;
  let readmeAfterCurated = false;
  runPipeline({
    stage: true,
    run(command, args) {
      if (command === 'git') {
        assert.deepEqual(args, ['add', '-A']);
        indexCurrent = true;
        return { status: 0 };
      }
      assert.equal(indexCurrent, true, `stale index before ${args[0]}`);
      if (args[0] === 'freshie/scripts/promote-to-curated.py') curatedWritten = true;
      if (args[0] === 'scripts/generate-readme-toc.mjs') readmeAfterCurated = curatedWritten;
      indexCurrent = false;
      return { status: 0 };
    },
  });
  assert.equal(readmeAfterCurated, true);
  assert.equal(indexCurrent, true);
});

test('staging failure prevents generation, and check mode cannot stage', () => {
  let calls = 0;
  assert.throws(
    () =>
      runPipeline({
        stage: true,
        run() {
          calls++;
          return { status: 1 };
        },
      }),
    /staging failed/,
  );
  assert.equal(calls, 1);
  assert.throws(() => runPipeline({ stage: true, check: true }), /non-mutating/);
});

test('CI regeneration stages the scorecard measured from the final upstream outputs', (t) => {
  const root = mkdtempSync(join(tmpdir(), 'release-scorecard-'));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  const artifact = '000-docs/742-RA-DATA-epic-1-scorecard.json';
  mkdirSync(join(root, '000-docs'));
  writeFileSync(join(root, 'README.md'), 'old');
  writeFileSync(join(root, artifact), 'stale');
  execFileSync('git', ['init', '-q'], { cwd: root });
  execFileSync('git', ['add', '-A'], { cwd: root });

  runPipeline({
    root,
    stage: true,
    run(command, args, options) {
      if (command === 'git') return spawnSync(command, args, options);
      if (args[0] === 'scripts/generate-readme-toc.mjs') {
        writeFileSync(join(root, 'README.md'), 'generated');
      }
      if (args[1] === 'normalize:dead-domain-projections') {
        writeFileSync(join(root, 'README.md'), 'normalized');
      }
      if (args[0] === 'scripts/measure-epic-1.mjs') {
        // Model the measurement command's index-input / worktree-output contract.
        const indexedInput = execFileSync('git', ['show', ':README.md'], { cwd: root });
        writeFileSync(join(root, artifact), indexedInput);
      }
      return { status: 0 };
    },
  });

  assert.equal(
    execFileSync('git', ['show', `:${artifact}`], { cwd: root, encoding: 'utf8' }),
    'normalized',
  );
  assert.equal(readFileSync(join(root, artifact), 'utf8'), 'normalized');
  assert.equal(execFileSync('git', ['diff', '--name-only'], { cwd: root, encoding: 'utf8' }), '');
});

test('scorecard-only drift fails the shared check without staging or running writers', () => {
  assert.throws(
    () =>
      runPipeline({
        check: true,
        run(command, args) {
          assert.notEqual(command, 'git');
          assert.ok(args.includes('--check'));
          return { status: args[0] === 'scripts/measure-epic-1.mjs' ? 1 : 0 };
        },
      }),
    /Projection checks failed:\nnode scripts\/measure-epic-1\.mjs --check/,
  );
});

test('measurement failure cannot be reported as successful regeneration or staged', () => {
  const calls = [];
  assert.throws(
    () =>
      runPipeline({
        stage: true,
        run(command, args) {
          calls.push([command, args]);
          return { status: args[0] === 'scripts/measure-epic-1.mjs' ? 1 : 0 };
        },
      }),
    /Projection regeneration failed:\nnode scripts\/measure-epic-1\.mjs/,
  );
  assert.deepEqual(calls.at(-1), ['node', ['scripts/measure-epic-1.mjs']]);
});
