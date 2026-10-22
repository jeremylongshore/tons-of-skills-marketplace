import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';

const ROOT = process.cwd();
const CLI = join(ROOT, 'packages/cli/dist/index.js');
const registry = JSON.parse(readFileSync(join(ROOT, 'config/harness-registry.json'), 'utf8'));

function projectDestination(root, harness) {
  return join(root, harness.projectPath, 'portable-fixture', 'SKILL.md');
}

test('every harness has an installation or refusal-path receipt', () => {
  const root = mkdtempSync(join(tmpdir(), 'tons-harness-matrix-'));
  const source = join(root, 'plugins/testing/fixture/skills/portable-fixture');
  try {
    writeFileSync(join(root, '.gitkeep'), 'fixture\n');
    writeFileSync(join(root, 'placeholder'), 'fixture\n');
    mkdirSync(source, { recursive: true });
    writeFileSync(
      join(source, 'SKILL.md'),
      '---\nname: portable-fixture\ndescription: Validate portable installation fixture behavior.\n---\n# Fixture\n',
    );

    const git = (...args) => execFileSync('git', args, { cwd: root, stdio: 'pipe' });
    git('init', '--quiet');
    git('config', 'user.name', 'Harness Matrix');
    git('config', 'user.email', 'harness@example.invalid');
    git('remote', 'add', 'origin', 'https://github.com/example/portable-fixture');
    git('add', '.');
    git('commit', '--quiet', '-m', 'test: canonical skill fixture');

    for (const harness of registry.harnesses) {
      let failure = null;
      try {
        execFileSync(
          process.execPath,
          [CLI, 'skills', 'install', source, '--harness', harness.id, '--scope', 'project'],
          { cwd: root, encoding: 'utf8', stdio: 'pipe' },
        );
      } catch (error) {
        failure = error;
      }
      if (harness.support === 'verified-native') {
        assert.equal(failure, null, `${harness.id} should install`);
        assert.equal(
          readFileSync(projectDestination(root, harness), 'utf8').includes('# Fixture'),
          true,
        );
        const receipt = JSON.parse(
          readFileSync(
            join(root, harness.projectPath, 'portable-fixture', '.ccpi-portable-install.json'),
            'utf8',
          ),
        );
        assert.equal(receipt.source.commit.digest, git('rev-parse', 'HEAD').toString().trim());
        assert.equal(receipt.installation.harness, harness.id);
      } else {
        assert.notEqual(
          failure,
          null,
          `${harness.id} must refuse before verified-native evidence exists`,
        );
        assert.match(
          String(failure.stderr),
          new RegExp(`${harness.support}; installation is available only for verified-native`),
        );
      }
    }
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});
