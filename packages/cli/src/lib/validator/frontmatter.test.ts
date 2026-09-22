import { promises as fs } from 'node:fs';
import { tmpdir } from 'node:os';
import * as path from 'node:path';
import { describe, expect, it } from 'vitest';

import { validateFrontmatterFile } from './frontmatter.js';
import { validateSkillFile } from './skills.js';

async function withAgent(frontmatter: string, run: (file: string) => Promise<void>): Promise<void> {
  const root = await fs.mkdtemp(path.join(tmpdir(), 'ccpi-agent-frontmatter-'));
  const agentDir = path.join(root, 'agents');
  const file = path.join(agentDir, 'current-agent.md');
  await fs.mkdir(agentDir);
  await fs.writeFile(file, `---\n${frontmatter}---\n\nValidate the current contract.\n`);
  try {
    await run(file);
  } finally {
    await fs.rm(root, { recursive: true, force: true });
  }
}

async function withSkill(frontmatter: string, run: (file: string) => Promise<void>): Promise<void> {
  const root = await fs.mkdtemp(path.join(tmpdir(), 'ccpi-skill-frontmatter-'));
  const skillDir = path.join(root, 'current-skill');
  const file = path.join(skillDir, 'SKILL.md');
  await fs.mkdir(skillDir);
  await fs.writeFile(file, `---\n${frontmatter}---\n\nValidate the current contract.\n`);
  try {
    await run(file);
  } finally {
    await fs.rm(root, { recursive: true, force: true });
  }
}

describe('current subagent frontmatter', () => {
  it('accepts current aliases, full model IDs, MCP lists, and cache TTL', async () => {
    await withAgent(
      [
        'name: current-agent',
        'description: Use when validating a current Claude Code subagent definition.',
        'tools: [Read, Agent]',
        'disallowedTools: [Write]',
        'model: claude-opus-5',
        'permissionMode: manual',
        'maxTurns: 12',
        'skills: [validate-agent]',
        'mcpServers: [github]',
        'hooks: {}',
        'memory: project',
        'background: false',
        'effort: xhigh',
        'isolation: worktree',
        'color: cyan',
        'initialPrompt: Start validation.',
        'experimental:',
        '  cacheTtl: 1h',
        '',
      ].join('\n'),
      async (file) => {
        const result = await validateFrontmatterFile(file);
        expect(result.fileType).toBe('agent');
        expect(result.errors).toEqual([]);
      },
    );
  });

  it('rejects retired capabilities metadata', async () => {
    await withAgent(
      [
        'name: current-agent',
        'description: Use when validating a legacy Claude Code agent definition.',
        'capabilities: [review, testing]',
        '',
      ].join('\n'),
      async (file) => {
        const result = await validateFrontmatterFile(file);
        expect(result.errors).toContain('Invalid agent field: capabilities');
      },
    );
  });

  it('rejects unsupported cache TTL values', async () => {
    await withAgent(
      [
        'name: current-agent',
        'description: Use when validating experimental Claude Code agent settings.',
        'experimental:',
        '  cacheTtl: forever',
        '',
      ].join('\n'),
      async (file) => {
        const result = await validateFrontmatterFile(file);
        expect(result.errors).toContain("Field 'experimental.cacheTtl' must be one of: 5m, 1h");
      },
    );
  });
});

describe('current skill frontmatter', () => {
  it('accepts current invocation, fork, model, effort, and tool forms', async () => {
    await withSkill(
      [
        'name: current-skill',
        'description: Validate current Claude Code skill frontmatter. Use when checking drift.',
        'when_to_use: Trigger after changing a skill contract.',
        'allowed-tools: Read Agent Bash(git status *)',
        'disallowed-tools: [AskUserQuestion]',
        'version: 1.0.0',
        'author: Test Author <test@example.com>',
        'license: MIT',
        'compatibility: Requires Claude Code 2.1.248+.',
        'tags: [validation]',
        'model: claude-opus-5',
        'effort: xhigh',
        'context: fork',
        'background: false',
        'arguments: [file]',
        'paths: ["packages/**"]',
        'shell: bash',
        '',
      ].join('\n'),
      async (file) => {
        const result = await validateSkillFile(file);
        expect(result.errors).toEqual([]);
        expect(result.warnings).not.toContain('Deprecated field used: when_to_use');
        expect(result.info).not.toContain('Non-spec field: background');
      },
    );
  });
});
