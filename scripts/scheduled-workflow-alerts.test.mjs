import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, readFileSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import yaml from 'js-yaml';

const names = ['check-links', 'check-issue-body-links', 'update-npm-stats'];
const workflows = Object.fromEntries(
  names.map((name) => [
    name,
    yaml.load(readFileSync(new URL(`../.github/workflows/${name}.yml`, import.meta.url), 'utf8')),
  ]),
);
const alert = (workflow) =>
  Object.values(workflow.jobs)
    .flatMap((job) => job.steps)
    .find((step) => step.name?.startsWith('Alert Slack'));

test('all three scheduled workflows retain failure handlers and distinguish advisory findings', () => {
  for (const workflow of Object.values(workflows)) {
    assert.ok(workflow.on.schedule.length);
    assert.match(alert(workflow).if, /failure\(\)/);
    assert.match(alert(workflow).env.WEBHOOK, /secrets\.SLACK_OPERATION_HIRED_WEBHOOK_URL/);
  }
  const links = alert(workflows['check-links']).if;
  assert.match(links, /github.event_name != 'pull_request'/);
  assert.match(links, /steps.lychee_repo.outputs.exit_code != '0'/);
  assert.match(links, /steps.lychee_marketplace.outputs.exit_code != '0'/);
  assert.match(links, /always\(\)/);
  assert.match(
    alert(workflows['check-issue-body-links']).if,
    /steps.audit.outputs.audit_exit != '0'/,
  );
  const kernel = yaml.load(
    readFileSync(new URL('../.github/workflows/kernel-vendor-hash.yml', import.meta.url), 'utf8'),
  );
  assert.match(alert(kernel).if, /outputs.violation == 'true'/);
});

for (const name of names) {
  test(`${name}: executes actual alert shell, safely quotes text, and refuses missing credentials or delivery failure`, () => {
    const dir = mkdtempSync(join(tmpdir(), 'workflow-alert-test-'));
    try {
      // No network: the subprocess records the payload and models curl status.
      writeFileSync(
        join(dir, 'curl'),
        '#!/bin/sh\nwhile [ "$#" -gt 0 ]; do\nif [ "$1" = "--data" ]; then shift; printf "%s" "$1" > "$ALERT_CAPTURE"; fi\nshift\ndone\nexit "${MOCK_CURL_EXIT:-0}"\n',
        { mode: 0o700 },
      );
      const step = alert(workflows[name]);
      const env = {
        ...process.env,
        PATH: `${dir}:${process.env.PATH}`,
        WEBHOOK: 'https://example.invalid/test',
        RUN_URL: 'https://example.invalid/run/1',
        ALERT_TEXT: 'quoted "text"\n$(not-a-command)',
        ALERT_CAPTURE: join(dir, 'payload.json'),
      };
      const run = (overrides) =>
        spawnSync('bash', ['-e', '-c', step.run], {
          env: { ...env, ...overrides },
          encoding: 'utf8',
        });
      const success = run({});
      assert.equal(success.status, 0, success.stderr);
      assert.deepEqual(JSON.parse(readFileSync(env.ALERT_CAPTURE, 'utf8')), {
        text: `${env.ALERT_TEXT} <${env.RUN_URL}|View run>`,
      });
      for (const overrides of [{ WEBHOOK: '' }, { MOCK_CURL_EXIT: '22' }]) {
        const result = run(overrides);
        assert.notEqual(result.status, 0);
        assert.doesNotMatch(result.stdout, /alert delivered/);
        assert.doesNotMatch(result.stdout + result.stderr, /https:\/\/example.invalid\/test/);
      }
      assert.match(step.run, /--fail --connect-timeout 10 --max-time 30/);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
}
