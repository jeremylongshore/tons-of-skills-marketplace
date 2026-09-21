import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

import { compareSkillNamesOrdinal } from '../marketplace/scripts/discover-skills.mjs';

const ROOT = fileURLToPath(new URL('..', import.meta.url));
const WORKFLOW = readFileSync(`${ROOT}/.github/workflows/validate-plugins.yml`, 'utf8');
const STANDALONE_E2E_WORKFLOW = readFileSync(
  `${ROOT}/.github/workflows/standalone-e2e.yml`,
  'utf8',
);
const PACKAGE = JSON.parse(readFileSync(`${ROOT}/package.json`, 'utf8'));
const GENERATED_CONTENT_COMMAND = PACKAGE.scripts['validate:generated-content'];
const PARSER_SECURITY_SUITES = [
  'marketplace/scripts/discover-skills.test.mjs',
  'marketplace/scripts/md-to-html.test.mjs',
  'marketplace/scripts/truncate-html.test.mjs',
];
const RED_PROOF_CHILD = 'GENERATED_CONTENT_SECURITY_RED_PROOF_CHILD';
const RED_PROOF_TARGET = 'GENERATED_CONTENT_SECURITY_RED_PROOF_TARGET';
const DISCOVER_SKILLS = readFileSync(`${ROOT}/marketplace/scripts/discover-skills.mjs`, 'utf8');
const SKILL_FRONTMATTER = readFileSync(`${ROOT}/scripts/skill-frontmatter.mjs`, 'utf8');
const VENDORED_JS_YAML = `${ROOT}/scripts/vendor/js-yaml-4.1.1/js-yaml.mjs`;
const VENDORED_JS_YAML_SHA256 = 'efbc45850bf15f0c8ee3434983f512be656002d7507dc292c7ade4449b5d57fa';
const VENDORED_JS_YAML_PATH = 'scripts/vendor/js-yaml-4.1.1/js-yaml.mjs';

function countLiteral(text, value) {
  return text.split(value).length - 1;
}

function jobBlock(name) {
  const marker = `  ${name}:\n`;
  const start = WORKFLOW.indexOf(marker);
  assert.notEqual(start, -1, `missing workflow job ${name}`);
  const rest = WORKFLOW.slice(start + marker.length);
  const next = rest.search(/^ {2}[a-zA-Z0-9_-]+:\n/m);
  return rest.slice(0, next === -1 ? undefined : next);
}

function workflowRunScript(name) {
  const lines = jobBlock(name).split('\n');
  const runIndex = lines.indexOf('        run: |');
  assert.notEqual(runIndex, -1, `missing run script in workflow job ${name}`);

  const commands = [];
  for (const line of lines.slice(runIndex + 1)) {
    if (!line.startsWith('          ')) break;
    commands.push(line.slice(10));
  }
  assert.notEqual(commands.length, 0, `empty run script in workflow job ${name}`);
  return commands.join('\n');
}

function assertPlantedFailure(result, target, caller) {
  assert.equal(result.error, undefined, `${caller} could not execute: ${result.error?.message}`);
  assert.notEqual(result.status, 0, `${caller} admitted planted failure in ${target}`);
  assert.match(
    `${result.stdout}\n${result.stderr}`,
    new RegExp(`GENERATED_CONTENT_SECURITY_RED_PROOF:${target}`),
    `${caller} failed without executing the planted ${target} failure`,
  );
}

test('generated content drift job is unconditional, credential-free, and exact', () => {
  const block = jobBlock('generated-content-drift');
  assert.doesNotMatch(block, /^ {4}if:/m);
  assert.doesNotMatch(block, /\b(?:paths|paths-ignore):/);
  assert.doesNotMatch(block, /continue-on-error|\|\|\s*true|secrets\./);
  assert.match(block, /permissions:\n {6}contents: read/);
  assert.match(block, /fetch-depth: 1/);
  assert.match(block, /persist-credentials: false/);
  assert.match(block, /name: Fetch pinned README presentation source/);
  assert.match(block, /\[\[ "\$source_commit" =~ \^\[0-9a-f\]\{40\}\$ \]\]/);
  assert.match(block, /git fetch --no-tags --depth=1 origin "\$source_commit"/);
  assert.match(block, /timeout-minutes: 10/);
  assert.doesNotMatch(block, /(?:npm|pnpm)\s+(?:ci|install)/);
  assert.match(
    block,
    /node --test scripts\/generated-content-ci\.test\.mjs marketplace\/scripts\/discover-skills\.test\.mjs marketplace\/scripts\/md-to-html\.test\.mjs marketplace\/scripts\/truncate-html\.test\.mjs marketplace\/scripts\/sync-catalog\.test\.mjs marketplace\/scripts\/generate-unified-search\.test\.mjs/,
  );
  for (const suite of PARSER_SECURITY_SUITES) {
    assert.equal(
      countLiteral(block, suite),
      1,
      `${suite} must run exactly once in the workflow job`,
    );
  }
  assert.match(block, /node marketplace\/scripts\/discover-skills\.mjs --level=full --check/);
  assert.match(block, /node marketplace\/scripts\/sync-catalog\.mjs --check/);
  assert.match(block, /node marketplace\/scripts\/generate-unified-search\.mjs --check/);
  assert.doesNotMatch(block, /--level=metadata/);
  assert.doesNotMatch(block, /(?:npm|pnpm)\s+(?:publish|pack)|git\s+(?:tag|push)/);
});

test('generated content parser uses the pinned install-free YAML implementation', () => {
  assert.match(
    DISCOVER_SKILLS,
    /import \{ parseSkillFrontmatter \} from '\.\.\/\.\.\/scripts\/skill-frontmatter\.mjs';/,
  );
  assert.match(SKILL_FRONTMATTER, /import yaml from '\.\/vendor\/js-yaml-4\.1\.1\/js-yaml\.mjs';/);
  assert.doesNotMatch(DISCOVER_SKILLS, /(?:from|require\()\s*['"]js-yaml['"]/);
  assert.doesNotMatch(SKILL_FRONTMATTER, /(?:from|require\()\s*['"]js-yaml['"]/);
  assert.equal(
    createHash('sha256').update(readFileSync(VENDORED_JS_YAML)).digest('hex'),
    VENDORED_JS_YAML_SHA256,
    'vendored js-yaml bytes must match the reviewed 4.1.1 distribution',
  );
  assert.match(
    readFileSync(`${ROOT}/scripts/vendor/js-yaml-4.1.1/LICENSE`, 'utf8'),
    /Permission is hereby granted, free of charge/,
  );
  for (const ignoreFile of ['.prettierignore', 'eslint.config.mjs']) {
    const ignoreConfig = readFileSync(`${ROOT}/${ignoreFile}`, 'utf8');
    assert.equal(
      countLiteral(ignoreConfig, VENDORED_JS_YAML_PATH),
      1,
      `${ignoreFile} must preserve the pinned upstream bytes with one exact exclusion`,
    );
  }
});

test('standalone E2E owns vendored parser changes and uses immutable credential-free actions', () => {
  assert.equal(
    countLiteral(STANDALONE_E2E_WORKFLOW, "- 'scripts/vendor/js-yaml-4.1.1/**'"),
    2,
    'pull_request and push must both run standalone E2E for vendored parser changes',
  );
  assert.match(
    STANDALONE_E2E_WORKFLOW,
    /actions\/checkout@d23441a48e516b6c34aea4fa41551a30e30af803 # v6\n {8}with:\n {10}persist-credentials: false/,
  );
  assert.match(
    STANDALONE_E2E_WORKFLOW,
    /pnpm\/action-setup@b906affcce14559ad1aafd4ab0e942779e9f58b1 # v4/,
  );
  assert.match(
    STANDALONE_E2E_WORKFLOW,
    /actions\/setup-node@249970729cb0ef3589644e2896645e5dc5ba9c38 # v6/,
  );
  assert.doesNotMatch(STANDALONE_E2E_WORKFLOW, /uses: [^\n]+@v\d+/);
});

test('canonical generated content command executes parser security suites exactly once', () => {
  assert.equal(typeof GENERATED_CONTENT_COMMAND, 'string');
  assert.match(
    GENERATED_CONTENT_COMMAND,
    /node --test scripts\/generated-content-ci\.test\.mjs marketplace\/scripts\/discover-skills\.test\.mjs marketplace\/scripts\/md-to-html\.test\.mjs marketplace\/scripts\/truncate-html\.test\.mjs marketplace\/scripts\/sync-catalog\.test\.mjs/,
  );
  for (const suite of PARSER_SECURITY_SUITES) {
    assert.equal(
      countLiteral(GENERATED_CONTENT_COMMAND, suite),
      1,
      `${suite} must run exactly once in validate:generated-content`,
    );
  }
  assert.match(
    GENERATED_CONTENT_COMMAND,
    /node marketplace\/scripts\/discover-skills\.mjs --level=full --check/,
  );
  assert.match(GENERATED_CONTENT_COMMAND, /node marketplace\/scripts\/sync-catalog\.mjs --check/);
});

test(
  'planted parser-suite failures make the local command and required workflow job red',
  { skip: process.env[RED_PROOF_CHILD] === '1' },
  () => {
    const workflowCommand = workflowRunScript('generated-content-drift');

    for (const target of ['discover-skills', 'md-to-html', 'truncate-html']) {
      const env = {
        ...process.env,
        [RED_PROOF_CHILD]: '1',
        [RED_PROOF_TARGET]: target,
      };
      // Node marks test-runner workers with this variable. Do not leak it into
      // the nested CLI proof or `node --test` will treat the child as recursive
      // and skip the very suites this test is proving.
      delete env.NODE_TEST_CONTEXT;
      const local = spawnSync(
        'bash',
        ['--noprofile', '--norc', '-e', '-o', 'pipefail', '-c', GENERATED_CONTENT_COMMAND],
        {
          cwd: ROOT,
          encoding: 'utf8',
          env,
          timeout: 30_000,
        },
      );
      assertPlantedFailure(local, target, 'validate:generated-content package script');

      const workflow = spawnSync(
        'bash',
        ['--noprofile', '--norc', '-e', '-o', 'pipefail', '-c', workflowCommand],
        {
          cwd: ROOT,
          encoding: 'utf8',
          env,
          timeout: 30_000,
        },
      );
      assertPlantedFailure(workflow, target, 'generated-content-drift');
    }
  },
);

test('generated content drift is aggregated exactly once without a new context', () => {
  const aggregate = jobBlock('ci-required');
  assert.equal(
    [...aggregate.matchAll(/^ {6}- generated-content-drift$/gm)].length,
    1,
    'ci-required must depend on generated-content-drift exactly once',
  );
  assert.match(aggregate, /^ {4}name: ci-required$/m);
});

test('Validate Plugins remains an every-PR workflow with no path filter', () => {
  const trigger = WORKFLOW.slice(0, WORKFLOW.indexOf('\njobs:'));
  assert.match(trigger, /^ {2}pull_request:$/m);
  assert.doesNotMatch(trigger, /\b(?:paths|paths-ignore):/);
});

test('skill projection ordering is locale-independent for non-ASCII names', () => {
  const names = ['éclair', 'Zulu', 'ångström', 'alpha'];
  assert.deepEqual(names.sort(compareSkillNamesOrdinal), ['Zulu', 'alpha', 'ångström', 'éclair']);
});
