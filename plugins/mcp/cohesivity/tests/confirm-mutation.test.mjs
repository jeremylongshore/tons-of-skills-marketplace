// Behavioral tests for the confirmation boundary: the PreToolUse hook must hold every
// state-changing Cohesivity call for the user, and leave read-only tools alone.
// Run: node --test plugins/mcp/cohesivity/tests/*.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFile } from 'node:child_process';
import { readFile, stat } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { promisify } from 'node:util';

const pluginRoot = join(dirname(fileURLToPath(import.meta.url)), '..');
const run = promisify(execFile);
const readJson = async (path) => JSON.parse(await readFile(join(pluginRoot, path), 'utf8'));

const gate = async () => {
  const hooks = await readJson('hooks/hooks.json');
  assert.equal(hooks.hooks.PreToolUse.length, 1);
  return hooks.hooks.PreToolUse[0];
};

test('the hook matches every state-changing tool under both tool-name forms', async () => {
  const matcher = new RegExp((await gate()).matcher);
  for (const tool of ['create_tenant', 'provision_resource', 'claim_tenant']) {
    assert.ok(matcher.test(`mcp__cohesivity__${tool}`), tool);
    assert.ok(matcher.test(`mcp__plugin_cohesivity_cohesivity__${tool}`), tool);
  }
});

test('the hook leaves read-only tools and other servers alone', async () => {
  const matcher = new RegExp((await gate()).matcher);
  for (const tool of ['tenant_status', 'get_cohesivity_documentation', 'give_feedback']) {
    assert.equal(matcher.test(`mcp__cohesivity__${tool}`), false, tool);
    assert.equal(matcher.test(`mcp__plugin_cohesivity_cohesivity__${tool}`), false, tool);
  }
  assert.equal(matcher.test('mcp__other__create_tenant'), false);
  assert.equal(matcher.test('mcp__cohesivity__create_tenant_extra'), false);
});

test('the hook script is executable and asks the host for approval', async () => {
  const script = join(pluginRoot, 'scripts/confirm-mutation.sh');
  assert.notEqual((await stat(script)).mode & 0o111, 0);
  const handler = (await gate()).hooks[0];
  assert.equal(handler.command, '"${CLAUDE_PLUGIN_ROOT}/scripts/confirm-mutation.sh"');
  assert.equal(handler.enabled, true);
  assert.equal(handler.blocking, true);
  const { stdout } = await run(script, [], { env: {} });
  const output = JSON.parse(stdout).hookSpecificOutput;
  assert.equal(output.hookEventName, 'PreToolUse');
  assert.equal(output.permissionDecision, 'ask');
});

test('the plugin connects only to the hosted HTTPS server and runs nothing locally', async () => {
  const servers = (await readJson('.mcp.json')).mcpServers;
  assert.deepEqual(Object.keys(servers), ['cohesivity']);
  assert.deepEqual(servers.cohesivity, { type: 'http', url: 'https://cohesivity.ai/mcp' });
  assert.equal('command' in servers.cohesivity, false);
});

test('the skill pre-approves only read-only tools', async () => {
  const skill = await readFile(join(pluginRoot, 'skills/cohesivity/SKILL.md'), 'utf8');
  const allowed = skill.match(/^allowed-tools:\n((?: {2}- .+\n)+)/m)[1].match(/- (.+)/g).map((line) => line.slice(2));
  assert.deepEqual(allowed, ['Read', 'mcp__cohesivity__tenant_status', 'mcp__cohesivity__get_cohesivity_documentation']);
});
