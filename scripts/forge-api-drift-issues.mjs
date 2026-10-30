import { readFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';

const pluginPattern = /^plugins\/[a-z0-9-]{1,80}\/[a-z0-9-]{1,80}$/;
const toolPattern = /^[a-z][a-z0-9_]{0,63}$/;
const shaPattern = /^[a-f0-9]{40}$/;

export function buildNotices(report) {
  if (
    report?.schema_version !== 1 ||
    !Array.isArray(report.results) ||
    report.results.length > 40
  ) {
    throw new Error('Invalid drift report');
  }
  const rows =
    report.status === 'UNVERIFIED'
      ? [{ plugin: 'configuration', status: 'UNVERIFIED', reason: report.reason }]
      : report.results;
  if (rows.length === 0) throw new Error('Empty drift report');
  const seen = new Set();
  return rows.flatMap((row) => {
    if (
      typeof row.plugin !== 'string' ||
      row.plugin !== row.plugin.trim() ||
      (row.plugin !== 'configuration' && !pluginPattern.test(row.plugin)) ||
      seen.has(row.plugin)
    ) {
      throw new Error('Invalid or duplicate plugin');
    }
    seen.add(row.plugin);
    if (!['NO_NAME_DRIFT', 'NAME_DRIFT', 'UNVERIFIED'].includes(row.status)) {
      throw new Error('Unknown drift status');
    }
    if (row.status === 'NO_NAME_DRIFT') return [];
    const marker = `<!-- forge-api-drift:v1:${row.plugin} -->`;
    let detail;
    if (row.status === 'NAME_DRIFT') {
      if (
        typeof row.upstream_commit !== 'string' ||
        row.upstream_commit.length !== 40 ||
        !shaPattern.test(row.upstream_commit) ||
        !Array.isArray(row.missing_tools) ||
        !row.missing_tools.length ||
        row.missing_tools.length > 200 ||
        row.missing_tools.some(
          (name) => typeof name !== 'string' || name !== name.trim() || !toolPattern.test(name),
        ) ||
        new Set(row.missing_tools).size !== row.missing_tools.length
      ) {
        throw new Error('Invalid name-drift evidence');
      }
      detail = `Captured tool names absent from the registered upstream catalogue and its declared aliases:\n\n${row.missing_tools.map((name) => `- \`${name}\``).join('\n')}\n\nUpstream revision: [\`${row.upstream_commit}\`](https://github.com/makeplane/plane-mcp-server/tree/${row.upstream_commit}).`;
    } else {
      if (typeof row.reason !== 'string' || !/^[A-Z][A-Z0-9_]{0,79}$/.test(row.reason)) {
        throw new Error('Invalid unverified reason');
      }
      detail = `The probe is incomplete: \`${row.reason}\`. This is not a no-drift result.`;
    }
    const subject = row.plugin === 'configuration' ? 'configuration' : row.plugin.split('/').at(-1);
    const baseline =
      row.plugin === 'configuration'
        ? 'Review `scripts/forge-api-surfaces.json`.'
        : `Baseline: [forge research](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/main/${row.plugin}/.forge/research.md).`;
    return [
      {
        marker,
        title: `Forge API surface review: ${subject}`,
        body: `${marker}\n\n${detail}\n\n${baseline}\n\nThis compares public source tool names only. It does not execute the upstream server, call a workspace, prove an outage, or assess argument compatibility. Review the retained workflow report, installed server version and migration/alias semantics before deciding whether to run /skill-creator --reforge. Do not silently replace the historical baseline. A later no-drift result does not automatically close this issue.\n`,
      },
    ];
  });
}

export async function publishNotices(notices, api) {
  if (!notices.length) return { created: 0, updated: 0 };
  const open = [];
  for (let page = 1; page <= 20; page += 1) {
    const rows = await api('GET', `/issues?state=open&per_page=100&page=${page}`);
    if (!Array.isArray(rows) || rows.length > 100) throw new Error('Invalid issue listing');
    open.push(...rows);
    if (rows.length < 100) break;
    if (page === 20) throw new Error('Issue inventory exceeds bounded pagination');
  }
  const result = { created: 0, updated: 0 };
  for (const notice of notices) {
    const matching = open.filter(
      (issue) =>
        !issue.pull_request &&
        issue.user?.login === 'github-actions[bot]' &&
        typeof issue.body === 'string' &&
        issue.body.startsWith(`${notice.marker}\n`),
    );
    if (matching.length > 1) throw new Error('Duplicate bot-owned drift issues need review');
    const issue = matching[0];
    if (!issue) {
      await api('POST', '/issues', { title: notice.title, body: notice.body });
      result.created += 1;
    } else if (issue.title !== notice.title || issue.body !== notice.body) {
      if (!Number.isSafeInteger(issue.number) || issue.number < 1)
        throw new Error('Invalid issue number');
      await api('PATCH', `/issues/${issue.number}`, { title: notice.title, body: notice.body });
      result.updated += 1;
    }
  }
  return result;
}

async function main() {
  const repo = process.env.GITHUB_REPOSITORY;
  const token = process.env.GH_TOKEN;
  if (repo !== 'jeremylongshore/tons-of-skills-marketplace' || !token) {
    throw new Error('Expected repository and issue token required');
  }
  const data = await readFile(process.argv[2], 'utf8');
  if (Buffer.byteLength(data) > 2 * 1024 * 1024) throw new Error('Drift report too large');
  const notices = buildNotices(JSON.parse(data));
  const api = async (method, path, body) => {
    const response = await fetch(`https://api.github.com/repos/${repo}${path}`, {
      method,
      redirect: 'error',
      signal: globalThis.AbortSignal.timeout(30_000),
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: 'application/vnd.github+json',
        'Content-Type': 'application/json',
        'X-GitHub-Api-Version': '2022-11-28',
      },
      ...(body ? { body: JSON.stringify(body) } : {}),
    });
    if (!response.ok) throw new Error(`Issue API failed: HTTP ${response.status}`);
    return response.json();
  };
  console.log(JSON.stringify(await publishNotices(notices, api)));
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
  });
}
