import assert from 'node:assert/strict';
import fs from 'node:fs';
import { createRequire } from 'node:module';
import os from 'node:os';
import path from 'node:path';
import test, { after } from 'node:test';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

import { checkMirrorQuarantine } from './check-mirror-quarantine.mjs';
import { isWithinPluginsDir } from './build-cowork-zips.mjs';
import {
  assertCatalogPublicationParity,
  ensureCatalogEntry,
  sourceAllowsPublication,
} from './sync-external.mjs';

const require = createRequire(import.meta.url);
const { publishedPlugins } = require('./publication-policy.cjs');
const yaml = require('js-yaml');
const temporaryRoots = new Set();
after(() => {
  for (const root of temporaryRoots) fs.rmSync(root, { recursive: true, force: true });
});

function write(root, relativePath, value) {
  const target = path.join(root, relativePath);
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, value);
}

function fixture() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'mirror-quarantine-'));
  temporaryRoots.add(root);
  const skill = 'plugins/community/mirror/skills/example/SKILL.md';
  write(root, skill, '---\nname: example\n---\n# Example\n');
  write(
    root,
    'plugins/community/mirror/.source.json',
    JSON.stringify({ synced_from: { repo: 'owner/repo', path: 'skills' } }),
  );
  write(
    root,
    'freshie/grades.csv',
    'skill_path,grade,score\nplugins/community/mirror/skills/example,B,85\n',
  );
  write(
    root,
    'freshie/disposition-ledger.json',
    JSON.stringify({
      schema_version: 'disposition-ledger/v1',
      artifacts: [
        {
          path: skill,
          disposition: 'QUARANTINE',
          gate: 'G0',
          reason_codes: ['SHELL_SUBSTITUTION'],
        },
      ],
    }),
  );
  write(root, 'skills/.curated/MANIFEST.json', JSON.stringify({ count: 0, skills: [] }));
  write(
    root,
    'sources.yaml',
    `sources:\n  - name: mirror\n    target_path: plugins/community/mirror\n    publication_disposition:\n      status: quarantined\n      channels: []\n      artifacts:\n        - path: ${skill}\n          reason_codes: [SHELL_SUBSTITUTION]\n      rationale: Retain for provenance and upstream repair only.\n`,
  );
  write(
    root,
    '.claude-plugin/marketplace.extended.json',
    JSON.stringify({
      plugins: [{ name: 'mirror', publication: 'quarantined' }],
    }),
  );
  write(root, '.claude-plugin/marketplace.json', JSON.stringify({ plugins: [] }));
  write(root, 'marketplace/src/data/catalog.json', JSON.stringify({ plugins: [] }));
  write(root, 'marketplace/src/data/skills-catalog.json', JSON.stringify({ skills: [] }));
  write(root, 'marketplace/src/data/skills-index.json', JSON.stringify({ skills: [] }));
  write(root, 'marketplace/src/data/unified-search-index.json', JSON.stringify({ items: [] }));
  write(root, 'marketplace/src/data/readme-sections.json', JSON.stringify({}));
  write(root, 'marketplace/src/data/spotlights.json', JSON.stringify({ hallOfFame: [] }));
  write(root, 'marketplace/src/data/cowork-manifest.json', JSON.stringify({ plugins: [] }));
  write(root, 'README.md', '# Marketplace\n');
  return { root, skill };
}

test('G0 mirror findings require exact no-channel source dispositions', () => {
  const { root } = fixture();
  assert.deepEqual(checkMirrorQuarantine({ root }), {
    mirrors: 1,
    quarantined: 1,
    g0Quarantined: 1,
  });
});

test('catalog leakage and stale or missing coverage fail closed', () => {
  const catalogLeak = fixture();
  write(
    catalogLeak.root,
    '.claude-plugin/marketplace.json',
    JSON.stringify({ plugins: [{ name: 'mirror' }] }),
  );
  assert.throws(
    () => checkMirrorQuarantine({ root: catalogLeak.root }),
    /quarantine leaks through CLI install catalog/,
  );

  const missing = fixture();
  write(
    missing.root,
    'sources.yaml',
    'sources:\n  - name: mirror\n    target_path: plugins/community/mirror\n',
  );
  assert.throws(
    () => checkMirrorQuarantine({ root: missing.root }),
    /G0 mirror has no source publication disposition/,
  );

  const readmeLeak = fixture();
  write(
    readmeLeak.root,
    'marketplace/src/data/readme-sections.json',
    JSON.stringify({ mirror: { overview: 'unsafe recommendation' } }),
  );
  assert.throws(() => checkMirrorQuarantine({ root: readmeLeak.root }), /website README sections/);

  const editorialLeak = fixture();
  write(
    editorialLeak.root,
    'marketplace/src/data/spotlights.json',
    JSON.stringify({ hallOfFame: [{ pluginSlug: 'mirror', grade: 'A' }] }),
  );
  assert.throws(() => checkMirrorQuarantine({ root: editorialLeak.root }), /community spotlight/);
});

test('external sync publishes by default and refuses malformed or quarantined dispositions', () => {
  const { root } = fixture();
  const held = yaml.load(fs.readFileSync(path.join(root, 'sources.yaml'), 'utf8')).sources[0];
  assert.equal(sourceAllowsPublication({ name: 'clean' }), true);
  assert.equal(sourceAllowsPublication(held, { root }), false);
  assert.throws(
    () =>
      sourceAllowsPublication({
        ...held,
        publication_disposition: {
          ...held.publication_disposition,
          status: 'pending',
        },
      }),
    /must be `status: quarantined`/,
  );
  assert.throws(
    () =>
      sourceAllowsPublication({
        ...held,
        publication_disposition: {
          ...held.publication_disposition,
          channels: ['marketplace'],
        },
      }),
    /empty `channels` list/,
  );
  assert.equal(
    sourceAllowsPublication({
      name: 'copyleft',
      copyleft_disposition: {
        status: 'quarantined',
        channels: [],
        rationale: 'Await a reviewed copyleft redistribution decision.',
      },
    }),
    false,
  );
  assert.throws(
    () =>
      sourceAllowsPublication({
        name: 'contradictory',
        publication_disposition: { status: 'quarantined', channels: [] },
        copyleft_disposition: { status: 'quarantined', channels: [] },
      }),
    /multiple publication dispositions/,
  );
});

test('external sync refuses existing catalog rows that contradict source disposition', () => {
  const { root } = fixture();
  const held = yaml.load(fs.readFileSync(path.join(root, 'sources.yaml'), 'utf8')).sources[0];
  assert.equal(
    assertCatalogPublicationParity(held, {
      name: held.name,
      publication: 'quarantined',
    }),
    false,
  );
  assert.throws(
    () => assertCatalogPublicationParity(held, { name: held.name }),
    /source disposition and catalog publication state disagree/,
  );
  assert.throws(
    () =>
      assertCatalogPublicationParity(
        { name: 'public' },
        { name: 'public', publication: 'quarantined' },
      ),
    /source disposition and catalog publication state disagree/,
  );

  const catalogFile = path.join(root, 'marketplace.extended.json');
  write(root, 'marketplace.extended.json', JSON.stringify({ plugins: [{ name: held.name }] }));
  assert.throws(
    () => ensureCatalogEntry(held, { root, catalogFile, dryRun: false }),
    /source disposition and catalog publication state disagree/,
  );
  write(
    root,
    'marketplace.extended.json',
    JSON.stringify({
      plugins: [{ name: held.name, publication: 'quarantined' }],
    }),
  );
  assert.equal(ensureCatalogEntry(held, { root, catalogFile, dryRun: false }), false);
});

test('catalog publication policy omits quarantine and refuses unknown states', () => {
  assert.deepEqual(
    publishedPlugins([{ name: 'public' }, { name: 'held', publication: 'quarantined' }]).map(
      (plugin) => plugin.name,
    ),
    ['public'],
  );
  assert.throws(
    () => publishedPlugins([{ name: 'ambiguous', publication: 'pending' }]),
    /unknown publication state/,
  );
});

test('native CLI catalog excludes held mirrors without suppressing public controls', () => {
  const { root } = legalFixture();
  const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
  fs.mkdirSync(path.join(root, 'scripts'));
  for (const filename of ['sync-marketplace.cjs', 'publication-policy.cjs']) {
    fs.copyFileSync(path.join(scriptDirectory, filename), path.join(root, 'scripts', filename));
  }
  fs.symlinkSync(path.join(scriptDirectory, '..', 'node_modules'), path.join(root, 'node_modules'));
  const plugins = [
    { name: 'mirror', source: './plugins/community/mirror', publication: 'quarantined' },
    { name: 'public-control', source: './plugins/testing/public-control', version: '1.0.0' },
  ];
  write(root, '.claude-plugin/marketplace.extended.json', JSON.stringify({ plugins }));
  execFileSync(process.execPath, ['scripts/sync-marketplace.cjs'], { cwd: root, stdio: 'pipe' });
  const projected = JSON.parse(fs.readFileSync(path.join(root, '.claude-plugin/marketplace.json')));
  assert.deepEqual(
    projected.plugins.map((plugin) => plugin.name),
    ['public-control'],
  );
  assert.equal(projected.plugins[0].source, plugins[1].source);
});

test('Cowork containment accepts Windows descendants but rejects adjacent paths', () => {
  const pluginsDir = String.raw`C:\repo\plugins`;
  assert.equal(
    isWithinPluginsDir(String.raw`C:\repo\plugins\security\safe`, {
      pluginsDir,
      pathApi: path.win32,
    }),
    true,
  );
  assert.equal(
    isWithinPluginsDir(String.raw`C:\repo\plugins-archive\security\unsafe`, {
      pluginsDir,
      pathApi: path.win32,
    }),
    false,
  );
});

test('publication policy gap: a declared G1 legal hold is not a fabricated G0 finding', () => {
  const { root, skill } = fixture();
  const evidence = 'plugins/community/mirror/provenance.json';
  const reasons = ['INCOMPLETE_ORIGINAL_SOURCE_PROVENANCE'];
  write(root, evidence, JSON.stringify({ originalRevision: null }));
  write(
    root,
    'sources.yaml',
    `sources:\n  - name: mirror\n    target_path: plugins/community/mirror\n    publication_disposition:\n      status: quarantined\n      channels: []\n      artifacts:\n        - path: ${evidence}\n          gate: G1\n          reason_codes: [${reasons[0]}]\n      rationale: Original source revision is unknown; retain no publication channels.\n`,
  );
  write(
    root,
    'freshie/disposition-ledger.json',
    JSON.stringify({
      schema_version: 'disposition-ledger/v1',
      artifacts: [
        {
          path: skill,
          disposition: 'QUARANTINE',
          gate: 'G1',
          reason_codes: reasons,
          source_hold: {
            source: 'mirror',
            rationale: 'Original source revision is unknown; retain no publication channels.',
            artifacts: [{ path: evidence, reason_codes: reasons }],
          },
        },
      ],
    }),
  );
  assert.deepEqual(checkMirrorQuarantine({ root }), {
    mirrors: 1,
    quarantined: 1,
    g0Quarantined: 0,
  });
});

test('publication policy gap: unknown artifact gates cannot silently authorize a hold', () => {
  assert.throws(
    () =>
      sourceAllowsPublication({
        name: 'held',
        target_path: 'plugins/community/held',
        publication_disposition: {
          status: 'quarantined',
          channels: [],
          rationale: 'An unsupported gate must be rejected, not interpreted as G0 or G1.',
          artifacts: [
            {
              path: 'plugins/community/held/evidence.json',
              gate: 'G9',
              reason_codes: ['UNKNOWN_GATE'],
            },
          ],
        },
      }),
    /unknown.*gate/i,
  );
});

function legalFixture() {
  const { root, skill } = fixture();
  const source = yaml.load(fs.readFileSync(path.join(root, 'sources.yaml'), 'utf8')).sources[0];
  const evidence = `${source.target_path}/provenance.json`;
  write(root, evidence, JSON.stringify({ originalRevision: null }));
  source.publication_disposition = {
    status: 'quarantined',
    channels: [],
    rationale: 'The original source revision is unknown.',
    artifacts: [
      {
        path: evidence,
        gate: 'G1',
        reason_codes: ['INCOMPLETE_ORIGINAL_SOURCE_PROVENANCE'],
      },
    ],
  };
  const row = {
    path: skill,
    disposition: 'QUARANTINE',
    gate: 'G1',
    reason_codes: ['INCOMPLETE_ORIGINAL_SOURCE_PROVENANCE'],
    source_hold: {
      source: source.name,
      rationale: source.publication_disposition.rationale,
      artifacts: [
        {
          path: evidence,
          reason_codes: ['INCOMPLETE_ORIGINAL_SOURCE_PROVENANCE'],
        },
      ],
    },
  };
  write(root, 'sources.yaml', yaml.dump({ sources: [source] }));
  write(
    root,
    'freshie/disposition-ledger.json',
    JSON.stringify({
      schema_version: 'disposition-ledger/v1',
      artifacts: [row],
    }),
  );
  return { root, skill, source, evidence, row };
}

test('G1 evidence is fail-closed in sync, checker and native source policy', () => {
  const mutations = [
    ({ source }) => {
      source.publication_disposition.channels = ['npm'];
    },
    ({ source }) => {
      source.publication_disposition.rationale = ' ';
    },
    ({ source }) => {
      source.publication_disposition.artifacts[0].gate = null;
    },
    ({ source }) => {
      source.publication_disposition.artifacts[0].gate = 'G2';
    },
    ({ source }) => {
      source.publication_disposition.artifacts[0].path = '../outside.json';
    },
    ({ source }) => {
      source.publication_disposition.artifacts[0].path = 'plugins/other/source/evidence.json';
    },
    ({ source }) => {
      source.publication_disposition.artifacts[0].reason_codes = [];
    },
    ({ source }) => {
      source.publication_disposition.artifacts[0].reason_codes = [' '];
    },
    ({ root, evidence }) => {
      fs.unlinkSync(path.join(root, evidence));
    },
    ({ root, evidence }) => {
      fs.unlinkSync(path.join(root, evidence));
      fs.mkdirSync(path.join(root, evidence));
    },
    ({ root, evidence }) => {
      fs.unlinkSync(path.join(root, evidence));
      write(root, 'outside.json', '{}');
      fs.symlinkSync(path.join(root, 'outside.json'), path.join(root, evidence));
    },
  ];
  for (const mutate of mutations) {
    const context = legalFixture();
    mutate(context);
    write(context.root, 'sources.yaml', yaml.dump({ sources: [context.source] }));
    assert.throws(() => sourceAllowsPublication(context.source, { root: context.root }));
    assert.throws(() => checkMirrorQuarantine({ root: context.root }));
  }
});

test('G1 machine association binds source, rationale, evidence and declared reasons', () => {
  const mutations = [
    ({ row }) => {
      row.source_hold.source = 'another-source';
    },
    ({ row }) => {
      row.source_hold.rationale = 'A different legal decision.';
    },
    ({ row }) => {
      row.source_hold.artifacts[0].path = 'plugins/community/mirror/other.json';
    },
    ({ row }) => {
      row.source_hold.artifacts[0].reason_codes = ['ANOTHER_REASON'];
    },
    ({ row }) => {
      row.reason_codes = [];
    },
    ({ row }) => {
      delete row.source_hold;
    },
    ({ row }) => {
      row.gate = 'G3';
    },
    ({ source }) => {
      delete source.publication_disposition;
    },
  ];
  for (const mutate of mutations) {
    const context = legalFixture();
    mutate(context);
    write(context.root, 'sources.yaml', yaml.dump({ sources: [context.source] }));
    write(
      context.root,
      'freshie/disposition-ledger.json',
      JSON.stringify({
        schema_version: 'disposition-ledger/v1',
        artifacts: [context.row],
      }),
    );
    assert.throws(() => checkMirrorQuarantine({ root: context.root }), /G1/);
  }
});

test('G0 remains exact and takes precedence over a mixed G1 source hold', () => {
  const { root, source, skill, row } = legalFixture();
  row.gate = 'G0';
  row.reason_codes = ['SHELL_SUBSTITUTION'];
  delete row.source_hold;
  write(
    root,
    'freshie/disposition-ledger.json',
    JSON.stringify({
      schema_version: 'disposition-ledger/v1',
      artifacts: [row],
    }),
  );
  assert.throws(() => checkMirrorQuarantine({ root }), /G0 mirror has no source/);
  source.publication_disposition.artifacts.push({
    path: skill,
    gate: 'G0',
    reason_codes: ['SHELL_SUBSTITUTION'],
  });
  write(root, 'sources.yaml', yaml.dump({ sources: [source] }));
  assert.equal(checkMirrorQuarantine({ root }).g0Quarantined, 1);
  row.reason_codes = ['DIFFERENT_SECURITY_REASON'];
  write(
    root,
    'freshie/disposition-ledger.json',
    JSON.stringify({
      schema_version: 'disposition-ledger/v1',
      artifacts: [row],
    }),
  );
  assert.throws(() => checkMirrorQuarantine({ root }), /G0 mirror disposition contradicts/);
  row.reason_codes = ['SHELL_SUBSTITUTION'];
  row.gate = 'G1';
  write(
    root,
    'freshie/disposition-ledger.json',
    JSON.stringify({
      schema_version: 'disposition-ledger/v1',
      artifacts: [row],
    }),
  );
  assert.throws(() => checkMirrorQuarantine({ root }), /no live G0 finding/);
});

test('G1 holds cannot leak through any existing public install or index surface', () => {
  const surfaces = [
    ['.claude-plugin/marketplace.json', { plugins: [{ name: 'mirror' }] }],
    ['marketplace/src/data/catalog.json', { plugins: [{ slug: 'mirror' }] }],
    [
      'marketplace/src/data/skills-catalog.json',
      { skills: [{ parentPlugin: { name: 'mirror' } }] },
    ],
    ['marketplace/src/data/skills-index.json', { skills: [{ parentPlugin: 'mirror' }] }],
    [
      'marketplace/src/data/unified-search-index.json',
      { items: [{ parentPlugin: { name: 'mirror' } }] },
    ],
    ['marketplace/src/data/readme-sections.json', { mirror: { overview: 'A held mirror.' } }],
    ['marketplace/src/data/cowork-manifest.json', { plugins: [{ name: 'mirror' }] }],
    ['marketplace/src/data/spotlights.json', { hallOfFame: [{ pluginSlug: 'mirror' }] }],
  ];
  for (const [surface, value] of surfaces) {
    const { root } = legalFixture();
    write(root, surface, JSON.stringify(value));
    assert.throws(() => checkMirrorQuarantine({ root }), /quarantine leaks/);
  }
  const { root } = legalFixture();
  write(root, 'README.md', '[mirror](https://example.com/held)\n');
  assert.throws(() => checkMirrorQuarantine({ root }), /root README recommendation/);
});
