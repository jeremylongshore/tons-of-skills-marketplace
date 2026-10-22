import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
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
      if (harness.support === 'verified-native') {
        const emptyProject = join(root, `empty-${harness.id}`);
        mkdirSync(emptyProject);
        const args = [
          CLI,
          'skills',
          'doctor',
          '--harness',
          harness.id,
          '--source-repo',
          root,
          '--json',
        ];
        const empty = JSON.parse(
          execFileSync(process.execPath, args, {
            cwd: emptyProject,
            encoding: 'utf8',
            stdio: 'pipe',
          }),
        );
        assert.equal(empty.exists, false);
        assert.deepEqual(empty.skills, []);
        const missing = JSON.parse(
          execFileSync(process.execPath, [...args, '--skill', 'missing-skill'], {
            cwd: emptyProject,
            encoding: 'utf8',
            stdio: 'pipe',
          }),
        );
        assert.equal(missing.skills[0].integrity, 'missing');
        assert.equal(existsSync(join(emptyProject, harness.projectPath)), false);
      }
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
        const doctorArgs = [
          CLI,
          'skills',
          'doctor',
          '--harness',
          harness.id,
          '--source-repo',
          root,
        ];
        const report = JSON.parse(
          execFileSync(process.execPath, [...doctorArgs, '--json'], {
            cwd: root,
            encoding: 'utf8',
            stdio: 'pipe',
          }),
        );
        assert.equal(report.verificationScope, 'source-and-installed-bytes');
        assert.equal(report.skills[0].integrity, 'verified');
        assert.equal(report.skills[0].quality, 'not-assessed');
        assert.deepEqual(report.skills[0].source, receipt.source);
        assert.equal(report.skills[0].installedDigest, receipt.tree.digest);
        const human = execFileSync(process.execPath, doctorArgs, {
          cwd: root,
          encoding: 'utf8',
          stdio: 'pipe',
        });
        assert.ok(human.includes('quality not assessed'));
        assert.ok(human.includes(receipt.source.commit.digest));
        assert.ok(human.includes(receipt.tree.digest));
        const missing = JSON.parse(
          execFileSync(process.execPath, [...doctorArgs, '--skill', 'missing-skill', '--json'], {
            cwd: root,
            encoding: 'utf8',
            stdio: 'pipe',
          }),
        );
        assert.equal(missing.skills[0].integrity, 'missing');
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
