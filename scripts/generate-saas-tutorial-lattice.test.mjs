import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';

import {
  buildReport,
  main,
  renderMarkdown,
  tutorialFamily,
} from './generate-saas-tutorial-lattice.mjs';

function write(root, repositoryPath, value) {
  const absolute = path.join(root, repositoryPath);
  fs.mkdirSync(path.dirname(absolute), { recursive: true });
  fs.writeFileSync(absolute, value);
}

function skill(name, body = 'Operational guidance.') {
  return `---\nname: ${name}\ndescription: Fixture skill for deterministic audit testing.\n---\n\n# ${name}\n\n${body}\n`;
}

function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'saas-lattice-'));
  t.after(() => fs.rmSync(root, { force: true, recursive: true }));
  execFileSync('git', ['init', '-q'], { cwd: root });
  const plugins = [
    {
      name: 'alpha-pack',
      source: './plugins/saas-packs/alpha-pack',
      category: 'saas-packs',
      version: '1.0.0',
      components: { skills: 2 },
      verification: { grade: 'D', score: 60 },
    },
    {
      name: 'beta-pack',
      source: './plugins/saas-packs/beta-pack',
      category: 'saas-packs',
      version: '2.0.0',
      components: { skills: 1 },
      verification: { grade: 'A', score: 95 },
    },
    {
      name: 'quarantined-pack',
      source: './plugins/saas-packs/quarantined-pack',
      category: 'saas-packs',
      publication: 'quarantined',
      version: '9.9.9',
      components: { skills: 999 },
    },
  ];
  write(root, '.claude-plugin/marketplace.extended.json', `${JSON.stringify({ plugins })}\n`);
  for (const [name, version] of [
    ['alpha-pack', '1.0.0'],
    ['beta-pack', '2.0.0'],
  ]) {
    write(
      root,
      `plugins/saas-packs/${name}/.claude-plugin/plugin.json`,
      `${JSON.stringify({ name, version })}\n`,
    );
    write(
      root,
      `plugins/saas-packs/${name}/package.json`,
      `${JSON.stringify({ name: `@example/${name}`, version: '0.1.0', files: ['skills/'] })}\n`,
    );
  }
  write(
    root,
    'plugins/saas-packs/alpha-pack/skills/alpha-hello-world/SKILL.md',
    skill('alpha-hello-world'),
  );
  write(
    root,
    'plugins/saas-packs/alpha-pack/skills/alpha-real-operator/SKILL.md',
    skill('alpha-real-operator'),
  );
  write(
    root,
    'plugins/saas-packs/beta-pack/skills/beta-install-auth/SKILL.md',
    skill('beta-install-auth'),
  );
  write(
    root,
    'plugins/saas-packs/alpha-pack/skills/alpha-hello-world/references/implementation-guide.md',
    'alpha candidate reference\n',
  );
  write(
    root,
    'plugins/saas-packs/alpha-pack/skills/alpha-real-operator/references/operator-guide.md',
    'alpha noncandidate reference\n',
  );
  write(
    root,
    'plugins/saas-packs/beta-pack/skills/beta-install-auth/references/implementation-guide.md',
    'beta candidate reference\n',
  );
  write(root, 'skills/.curated/alpha-hello-world/SKILL.md', skill('alpha-hello-world'));
  write(
    root,
    'skills/.curated/MANIFEST.json',
    `${JSON.stringify({
      count: 1,
      skills: [
        {
          curated_name: 'alpha-hello-world',
          source_path: 'plugins/saas-packs/alpha-pack/skills/alpha-hello-world',
        },
      ],
    })}\n`,
  );
  execFileSync('git', ['add', '.'], { cwd: root });
  return root;
}

test('matches only explicit pack-prefix and terminal-family pairs', () => {
  assert.equal(tutorialFamily('vendor-pack', 'vendor-core-workflow-a'), 'core-workflow-a');
  assert.equal(tutorialFamily('vendor-pack', 'vendor-hello-world'), 'hello-world');
  assert.equal(tutorialFamily('vendor-pack', 'vendor-not-security-basics'), null);
  assert.equal(tutorialFamily('vendor-pack', 'hello-world-vendor'), null);
  assert.equal(tutorialFamily('anthropic-pack', 'anth-install-auth'), 'install-auth');
  assert.equal(tutorialFamily('customerio-pack', 'customerio-deploy-pipeline'), null);
  assert.equal(
    tutorialFamily('vendor-pack', 'vendor-advanced-troubleshooting'),
    'advanced-troubleshooting',
  );
  assert.equal(tutorialFamily('langchain-py-pack', 'langchain-otel-observability'), null);
});

test('builds a catalog-scoped denominator and deterministic queue', (t) => {
  const root = fixture(t);
  const report = buildReport({ root });
  assert.deepEqual(report.summary, {
    active_saas_packs: 2,
    active_skills: 3,
    tutorial_lattice_skills: 2,
    affected_packs: 2,
    fully_lattice_packs: 1,
    at_least_80_percent_lattice_packs: 1,
    unaffected_packs: 0,
    prefix_mismatch_skills: 0,
    prefix_override_candidate_skills: 0,
  });
  assert.deepEqual(
    report.queue.map((entry) => entry.pack),
    ['beta-pack', 'alpha-pack'],
  );
  assert.equal(report.packs[0].candidate_curated_count, 1);
  assert.equal(report.packs[0].candidate_skills[0].disposition, 'REVIEW_REQUIRED');
  assert.equal(report.packs[0].candidate_skills[0].public_name, 'alpha-hello-world');
  assert.equal(report.queue[0].next_action, 'ENSURE_EXACTLY_ONE_PACK_DISPOSITION_CHILD');
  assert.equal(report.queue_policy.wip_limit, 1);
  assert.match(report.queue_policy.duplicate_prevention, /never create a second/i);
  assert.equal(report.queue[0].pack_inventory_sha256, report.packs[1].pack_inventory_sha256);
  assert.match(renderMarkdown(report), /matching skill name proves structural repetition only/);
});

test('refuses a filesystem skill absent from the canonical corpus', (t) => {
  const root = fixture(t);
  write(
    root,
    'plugins/saas-packs/alpha-pack/skills/alpha-debug-bundle/SKILL.md',
    skill('alpha-debug-bundle'),
  );
  assert.throws(
    () => buildReport({ root }),
    /filesystem differs from the marketplace-visible corpus.*untracked skills/,
  );
});

test('refuses catalog component counts that disagree with the canonical corpus', (t) => {
  const root = fixture(t);
  const catalogPath = path.join(root, '.claude-plugin/marketplace.extended.json');
  const catalog = JSON.parse(fs.readFileSync(catalogPath, 'utf8'));
  catalog.plugins[0].components.skills = 99;
  fs.writeFileSync(catalogPath, `${JSON.stringify(catalog)}\n`);
  assert.throws(() => buildReport({ root }), /alpha-pack declares 99 skills but resolves 2/);
});

test('pack and candidate hashes cover complete tracked subtrees without cross-pack drift', (t) => {
  const root = fixture(t);
  const before = buildReport({ root });
  write(
    root,
    'plugins/saas-packs/alpha-pack/skills/alpha-hello-world/references/implementation-guide.md',
    'Changed alpha candidate reference.\n',
  );
  const afterCandidate = buildReport({ root });
  const beforeAlpha = before.packs.find((pack) => pack.name === 'alpha-pack');
  const beforeBeta = before.packs.find((pack) => pack.name === 'beta-pack');
  const candidateAlpha = afterCandidate.packs.find((pack) => pack.name === 'alpha-pack');
  const candidateBeta = afterCandidate.packs.find((pack) => pack.name === 'beta-pack');
  assert.notEqual(beforeAlpha.pack_inventory_sha256, candidateAlpha.pack_inventory_sha256);
  assert.notEqual(beforeAlpha.candidate_set_sha256, candidateAlpha.candidate_set_sha256);
  assert.equal(beforeBeta.pack_inventory_sha256, candidateBeta.pack_inventory_sha256);
  assert.equal(beforeBeta.candidate_set_sha256, candidateBeta.candidate_set_sha256);

  write(
    root,
    'plugins/saas-packs/alpha-pack/skills/alpha-real-operator/references/operator-guide.md',
    'Changed alpha noncandidate reference.\n',
  );
  const afterNoncandidate = buildReport({ root });
  const noncandidateAlpha = afterNoncandidate.packs.find((pack) => pack.name === 'alpha-pack');
  assert.notEqual(candidateAlpha.pack_inventory_sha256, noncandidateAlpha.pack_inventory_sha256);
  assert.equal(candidateAlpha.candidate_set_sha256, noncandidateAlpha.candidate_set_sha256);
});

test('refuses public names that differ from their skill directory', (t) => {
  const root = fixture(t);
  write(
    root,
    'plugins/saas-packs/alpha-pack/skills/alpha-hello-world/SKILL.md',
    skill('renamed-public-skill'),
  );
  assert.throws(() => buildReport({ root }), /public name.*differs from directory/);
});

test('refuses a nested mirror boundary hidden below a first-party pack', (t) => {
  const root = fixture(t);
  write(
    root,
    'plugins/saas-packs/alpha-pack/skills/alpha-hello-world/.source.json',
    `${JSON.stringify({ synced_from: { repo: 'owner/upstream', path: 'skills/alpha' } })}\n`,
  );
  assert.throws(() => buildReport({ root }), /crosses a nested provenance boundary/);
});

test('refuses a tracked pack input replaced by a worktree symlink', (t) => {
  const root = fixture(t);
  const reference = path.join(
    root,
    'plugins/saas-packs/alpha-pack/skills/alpha-real-operator/references/operator-guide.md',
  );
  const target = path.join(root, 'replacement.md');
  fs.writeFileSync(target, 'replacement\n');
  fs.unlinkSync(reference);
  fs.symlinkSync(target, reference);
  assert.throws(() => buildReport({ root }), /tracked pack input crosses a symlink/);
});

test('refuses curated rows whose indexed mirror is missing from the worktree', (t) => {
  const root = fixture(t);
  fs.unlinkSync(path.join(root, 'skills/.curated/alpha-hello-world/SKILL.md'));
  assert.throws(() => buildReport({ root }), /mirror is unreadable/);
});

test('refuses a curated row whose canonical source is absent', (t) => {
  const root = fixture(t);
  const manifestPath = path.join(root, 'skills/.curated/MANIFEST.json');
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  manifest.skills[0].source_path = 'plugins/saas-packs/alpha-pack/skills/does-not-exist';
  fs.writeFileSync(manifestPath, `${JSON.stringify(manifest)}\n`);
  assert.throws(() => buildReport({ root }), /has no tracked canonical source/);
});

test('accepts the promoter collision-safe plugin__skill curated name', (t) => {
  const root = fixture(t);
  const manifestPath = path.join(root, 'skills/.curated/MANIFEST.json');
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  manifest.skills[0].curated_name = 'alpha-pack__alpha-hello-world';
  fs.renameSync(
    path.join(root, 'skills/.curated/alpha-hello-world'),
    path.join(root, 'skills/.curated/alpha-pack__alpha-hello-world'),
  );
  fs.writeFileSync(manifestPath, `${JSON.stringify(manifest)}\n`);
  execFileSync('git', ['add', '-A'], { cwd: root });

  assert.equal(buildReport({ root }).summary.tutorial_lattice_skills, 2);
});

test('refuses duplicate and traversal-shaped curated names', (t) => {
  const root = fixture(t);
  const manifestPath = path.join(root, 'skills/.curated/MANIFEST.json');
  const duplicate = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  duplicate.count = 2;
  duplicate.skills.push({
    curated_name: 'alpha-hello-world',
    source_path: 'plugins/saas-packs/beta-pack/skills/beta-install-auth',
  });
  fs.writeFileSync(manifestPath, `${JSON.stringify(duplicate)}\n`);
  assert.throws(() => buildReport({ root }), /curated manifest membership|duplicate curated/);

  const unsafe = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  unsafe.count = 1;
  unsafe.skills = [
    {
      curated_name: '../alpha-hello-world',
      source_path: 'plugins/saas-packs/alpha-pack/skills/alpha-hello-world',
    },
  ];
  fs.writeFileSync(manifestPath, `${JSON.stringify(unsafe)}\n`);
  assert.throws(() => buildReport({ root }), /curated manifest membership|invalid or duplicate/);
});

test('confines output paths and refuses output symlinks', (t) => {
  const root = fixture(t);
  fs.mkdirSync(path.join(root, 'freshie'), { recursive: true });
  fs.mkdirSync(path.join(root, '000-docs'), { recursive: true });
  assert.throws(
    () => main(['--root', root, '--json', '../escape.json']),
    /json output must be a \.json file below freshie\//,
  );
  const target = path.join(root, 'target.json');
  fs.writeFileSync(target, '{}\n');
  fs.symlinkSync(target, path.join(root, 'freshie/linked.json'));
  assert.throws(
    () => main(['--root', root, '--json', 'freshie/linked.json']),
    /json output is not a regular file/,
  );
});

test('check mode rejects input and staged-output divergence', (t) => {
  const root = fixture(t);
  fs.mkdirSync(path.join(root, 'freshie'), { recursive: true });
  fs.mkdirSync(path.join(root, '000-docs'), { recursive: true });
  main(['--root', root]);
  execFileSync('git', ['add', '.'], { cwd: root });

  const catalogPath = path.join(root, '.claude-plugin/marketplace.extended.json');
  const catalog = JSON.parse(fs.readFileSync(catalogPath, 'utf8'));
  catalog.plugins[0].verification.score = 61;
  fs.writeFileSync(catalogPath, `${JSON.stringify(catalog)}\n`);
  assert.throws(() => main(['--root', root, '--check']), /inputs differ.*Git index/);

  execFileSync('git', ['add', '.claude-plugin/marketplace.extended.json'], { cwd: root });
  main(['--root', root]);
  assert.throws(() => main(['--root', root, '--check']), /generated content drift/);
});

test('check mode refuses an input mutation after its initial parity check', (t) => {
  const root = fixture(t);
  fs.mkdirSync(path.join(root, 'freshie'), { recursive: true });
  fs.mkdirSync(path.join(root, '000-docs'), { recursive: true });
  main(['--root', root]);
  execFileSync('git', ['add', '.'], { cwd: root });
  assert.throws(
    () =>
      main(['--root', root, '--check'], {
        afterInputParity() {
          write(
            root,
            'plugins/saas-packs/alpha-pack/skills/alpha-hello-world/SKILL.md',
            skill('alpha-hello-world', 'Mutated after the initial parity check.'),
          );
        },
      }),
    /inputs differ between the worktree and Git index/,
  );
});

test('package and workflow keep the lattice validation lane unconditional', () => {
  const packageJson = JSON.parse(fs.readFileSync(path.resolve('package.json'), 'utf8'));
  const workflow = fs.readFileSync('.github/workflows/validate-plugins.yml', 'utf8');
  assert.equal(
    packageJson.scripts['validate:saas-lattice'],
    'node --test scripts/generate-saas-tutorial-lattice.test.mjs && node scripts/generate-saas-tutorial-lattice.mjs --check',
  );
  const steps = workflow.match(
    /\n\s+- name: Verify the SaaS tutorial-lattice denominator\n[\s\S]*?(?=\n\s+- name:)/g,
  );
  assert.equal(steps?.length, 1);
  assert.match(steps[0], /run: pnpm run validate:saas-lattice/);
  assert.doesNotMatch(steps[0], /\n\s+if:/);
});
