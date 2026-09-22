/**
 * Skills Validator - Validates SKILL.md files comply with Claude Code Skills spec
 *
 * Based on:
 * - https://code.claude.com/docs/en/skills (Official Anthropic docs)
 * - Intent Solutions Enterprise Standards
 */

/**
 * Compatibility validator used by `ccpi validate`. The repository's universal
 * Python validator remains authoritative for marketplace grading.
 */

import { promises as fs } from 'node:fs';
import * as path from 'node:path';
import * as yaml from 'yaml';

// Valid tools per Claude Code spec
const VALID_TOOLS = new Set([
  'Read',
  'Write',
  'Edit',
  'Bash',
  'Glob',
  'Grep',
  'Agent',
  'Artifact',
  'CronCreate',
  'CronDelete',
  'CronList',
  'EndConversation',
  'EnterPlanMode',
  'EnterWorktree',
  'ExitPlanMode',
  'ExitWorktree',
  'LSP',
  'ListMcpResourcesTool',
  'Monitor',
  'PowerShell',
  'PushNotification',
  'ReadMcpResourceTool',
  'RemoteTrigger',
  'ReportFindings',
  'ScheduleWakeup',
  'SendMessage',
  'SendUserFile',
  'ShareOnboardingGuide',
  'TaskCreate',
  'TaskGet',
  'TaskList',
  'TaskOutput',
  'TaskStop',
  'TaskUpdate',
  'Task', // Legacy alias retained for compatibility; new skills should use Agent.
  'ToolSearch',
  'WaitForMcpServers',
  'Workflow',
  'WebFetch',
  'WebSearch',
  'TodoWrite',
  'NotebookEdit',
  'AskUserQuestion',
  'Skill',
]);

// Fields per Anthropic spec
const REQUIRED_FIELDS = new Set(['name', 'description']);

// Enterprise standard fields (Intent Solutions)
const ENTERPRISE_REQUIRED = new Set([
  'allowed-tools',
  'version',
  'author',
  'license',
  'compatibility',
  'tags',
]);

// Optional fields per Anthropic spec + AgentSkills.io
const OPTIONAL_FIELDS = new Set([
  'model',
  'effort',
  'background',
  'when_to_use',
  'arguments',
  'disallowed-tools',
  'disable-model-invocation',
  'tags',
  'metadata',
  'argument-hint',
  'context',
  'agent',
  'user-invocable',
  'hooks',
  'compatibility',
  'paths',
  'shell',
]);

const DEPRECATED_FIELDS = new Set(['mode', 'compatible-with']);
const VALID_EFFORT_LEVELS = new Set(['low', 'medium', 'high', 'xhigh', 'max']);

export interface SkillValidationResult {
  file: string;
  fatal?: string;
  errors: string[];
  warnings: string[];
  info: string[];
  wordCount?: number;
  hasAllowedTools?: boolean;
}

export interface SkillValidationSummary {
  total: number;
  compliant: number;
  withWarnings: number;
  withErrors: number;
  results: SkillValidationResult[];
}

/**
 * Parse YAML frontmatter from content
 */
function parseYamlFrontmatter(content: string): Record<string, unknown> | null {
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) {
    return null;
  }

  try {
    return yaml.parse(match[1]) || {};
  } catch (e) {
    return { _parse_error: String(e) };
  }
}

/**
 * Parse allowed-tools which can be string or list
 * Split on commas or whitespace outside a parenthesized tool scope.
 */
function parseAllowedTools(toolsValue: unknown): string[] {
  if (Array.isArray(toolsValue)) {
    return toolsValue.map(String);
  } else if (typeof toolsValue === 'string') {
    const tools: string[] = [];
    let current = '';
    let depth = 0;
    for (const character of toolsValue) {
      if (character === '(') depth += 1;
      if (character === ')') depth -= 1;
      if ((character === ',' || /\s/.test(character)) && depth === 0) {
        if (current.trim()) tools.push(current.trim());
        current = '';
      } else {
        current += character;
      }
    }
    if (current.trim()) tools.push(current.trim());
    return tools;
  }
  return [];
}

/**
 * Validate a single tool permission including wildcards like Bash(git:*)
 */
function validateToolPermission(tool: string): { valid: boolean; message: string } {
  // Extract base tool name (before parentheses)
  const baseTool = tool.split('(')[0].trim();

  if (!VALID_TOOLS.has(baseTool) && !baseTool.startsWith('mcp__')) {
    return { valid: false, message: `Unknown tool: ${baseTool}` };
  }

  // Validate wildcard syntax if present
  if (tool.includes('(')) {
    if (!tool.endsWith(')') || tool.indexOf('(') !== tool.lastIndexOf('(')) {
      return { valid: false, message: `Invalid wildcard syntax: ${tool}` };
    }
    const inner = tool.slice(tool.indexOf('(') + 1, -1);
    if (!inner.trim()) {
      return { valid: false, message: `Empty tool scope: ${tool}` };
    }
  }

  return { valid: true, message: '' };
}

/**
 * Check for hardcoded paths that should use ${CLAUDE_SKILL_DIR}
 */
function checkHardcodedPaths(content: string): string[] {
  const issues: string[] = [];

  // Remove code blocks to avoid false positives
  let contentNoCode = content.replace(/```[\s\S]*?```/g, '');
  contentNoCode = contentNoCode.replace(/`[^`]+`/g, '');

  const pathPatterns: [RegExp, string][] = [
    [/\/home\/\w+\//, '/home/user/'],
    [/\/Users\/\w+\//, '/Users/user/'],
    [/C:\\Users\\/, 'C:\\Users\\'],
  ];

  for (const [pattern, desc] of pathPatterns) {
    if (pattern.test(contentNoCode)) {
      issues.push(`Hardcoded path detected (use \${CLAUDE_SKILL_DIR}): ${desc}`);
    }
  }

  return issues;
}

/**
 * Estimate word count for content length check
 */
function estimateWordCount(content: string): number {
  // Remove frontmatter
  const contentBody = content.replace(/^---\n[\s\S]*?\n---\n?/, '');
  return contentBody.split(/\s+/).filter((w) => w.length > 0).length;
}

/**
 * Validate a single SKILL.md file against Claude Code spec
 */
export async function validateSkillFile(filePath: string): Promise<SkillValidationResult> {
  const result: SkillValidationResult = {
    file: filePath,
    errors: [],
    warnings: [],
    info: [],
  };

  let content: string;
  try {
    content = await fs.readFile(filePath, 'utf-8');
  } catch (e) {
    result.fatal = `Cannot read file: ${e}`;
    return result;
  }

  const frontmatter = parseYamlFrontmatter(content);

  if (!frontmatter) {
    result.fatal = 'No YAML frontmatter found';
    return result;
  }

  if ('_parse_error' in frontmatter) {
    result.fatal = `YAML parse error: ${frontmatter._parse_error}`;
    return result;
  }

  // === REQUIRED FIELDS ===

  // name field
  if (!('name' in frontmatter)) {
    result.errors.push('Missing required field: name');
  } else {
    const name = String(frontmatter.name);
    const folderName = path.basename(path.dirname(filePath));

    if (name !== folderName) {
      result.info.push(
        `name '${name}' differs from folder '${folderName}' (best practice: match them)`,
      );
    }

    if (name.length > 1 && !/^[a-z][a-z0-9-]*[a-z0-9]$/.test(name)) {
      result.warnings.push(`name should be kebab-case: ${name}`);
    }

    if (name.length > 64) {
      result.errors.push('name exceeds 64 characters');
    }
  }

  // description field
  if (!('description' in frontmatter)) {
    result.errors.push('Missing required field: description');
  } else {
    const desc = String(frontmatter.description);
    if (desc.length < 20) {
      result.warnings.push('description too short (< 20 chars) - may not trigger well');
    }
    if (desc.length > 1024) {
      result.errors.push('description exceeds 1024 characters');
    }

    const imperativeStarts = [
      'analyze',
      'create',
      'generate',
      'build',
      'debug',
      'optimize',
      'validate',
      'test',
      'deploy',
      'monitor',
      'fix',
      'review',
      'extract',
      'convert',
      'implement',
      'this skill',
      'use this',
      'activates when',
    ];
    const descLower = desc.toLowerCase();
    const hasImperative = imperativeStarts.some(
      (v) => descLower.startsWith(v) || descLower.includes(v),
    );
    if (!hasImperative) {
      result.info.push('Consider using imperative language in description');
    }
  }

  // === ENTERPRISE REQUIRED FIELDS ===

  // allowed-tools
  if ('allowed-tools' in frontmatter) {
    const tools = parseAllowedTools(frontmatter['allowed-tools']);
    for (const tool of tools) {
      const { valid, message } = validateToolPermission(tool);
      if (!valid) {
        result.errors.push(message);
      }
    }

    if (tools.length > 6) {
      result.info.push(`Many tools permitted (${tools.length}) - consider limiting`);
    }
    result.hasAllowedTools = true;
  } else {
    result.warnings.push('Missing enterprise field: allowed-tools');
    result.hasAllowedTools = false;
  }

  // version
  if (!('version' in frontmatter)) {
    result.warnings.push('Missing enterprise field: version (use semver e.g., 1.0.0)');
  } else {
    const version = String(frontmatter.version);
    if (!/^\d+\.\d+\.\d+/.test(version)) {
      result.warnings.push(`version should be semver format: ${version}`);
    }
  }

  // author
  if (!('author' in frontmatter)) {
    result.warnings.push('Missing enterprise field: author');
  }

  // license
  if (!('license' in frontmatter)) {
    result.warnings.push('Missing enterprise field: license (use MIT)');
  }

  // === OPTIONAL FIELDS ===

  if ('model' in frontmatter) {
    const modelStr = String(frontmatter.model);
    if (
      !['inherit', 'sonnet', 'haiku', 'opus', 'fable'].includes(modelStr) &&
      !/^claude-[a-z0-9][a-z0-9.-]*$/.test(modelStr)
    ) {
      result.warnings.push(`Unknown model value: ${modelStr}`);
    }
  }

  if ('effort' in frontmatter && !VALID_EFFORT_LEVELS.has(String(frontmatter.effort))) {
    result.errors.push(`Invalid effort. Must be one of: ${[...VALID_EFFORT_LEVELS].join(', ')}`);
  }

  if ('background' in frontmatter && typeof frontmatter.background !== 'boolean') {
    result.errors.push("Field 'background' must be a boolean");
  }

  if ('shell' in frontmatter && !['bash', 'powershell'].includes(String(frontmatter.shell))) {
    result.errors.push("Field 'shell' must be 'bash' or 'powershell'");
  }

  if ('disallowed-tools' in frontmatter) {
    const tools = parseAllowedTools(frontmatter['disallowed-tools']);
    for (const tool of tools) {
      const { valid, message } = validateToolPermission(tool);
      if (!valid) result.errors.push(message);
    }
  }

  // === DEPRECATED FIELDS ===

  for (const field of DEPRECATED_FIELDS) {
    if (field in frontmatter) {
      result.warnings.push(`Deprecated field used: ${field}`);
    }
  }

  // === NON-SPEC FIELDS ===

  const knownFields = new Set([
    ...REQUIRED_FIELDS,
    ...ENTERPRISE_REQUIRED,
    ...OPTIONAL_FIELDS,
    ...DEPRECATED_FIELDS,
  ]);
  for (const field of Object.keys(frontmatter)) {
    if (!knownFields.has(field)) {
      result.info.push(`Non-spec field: ${field}`);
    }
  }

  // === CONTENT CHECKS ===

  const pathIssues = checkHardcodedPaths(content);
  result.errors.push(...pathIssues);

  const wordCount = estimateWordCount(content);
  result.wordCount = wordCount;

  if (wordCount > 5000) {
    result.warnings.push(`Content exceeds 5000 words (${wordCount}) - may overwhelm context`);
  } else if (wordCount > 3500) {
    result.info.push(`Content is lengthy (${wordCount} words) - consider using references/`);
  }

  // Check for second-person phrasing
  if (/\byou should\b|\byou can\b|\byou will\b/i.test(content)) {
    result.info.push('Consider imperative language instead of "you should/can/will"');
  }

  return result;
}

/**
 * Find all SKILL.md files in a directory
 */
export async function findSkillFiles(baseDir: string): Promise<string[]> {
  const skillFiles: string[] = [];

  async function walkDir(dir: string): Promise<void> {
    try {
      const entries = await fs.readdir(dir, { withFileTypes: true });
      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        if (entry.isDirectory()) {
          await walkDir(fullPath);
        } else if (entry.name === 'SKILL.md' && fullPath.includes('/skills/')) {
          skillFiles.push(fullPath);
        }
      }
    } catch {
      // Directory not accessible
    }
  }

  await walkDir(baseDir);
  return skillFiles;
}

/**
 * Validate all skills in a directory
 */
export async function validateAllSkills(baseDir: string): Promise<SkillValidationSummary> {
  const pluginsDir = path.join(baseDir, 'plugins');
  const skillFiles = await findSkillFiles(pluginsDir);

  const standaloneDir = path.join(baseDir, 'skills');
  const standaloneFiles = await findSkillFiles(standaloneDir);
  skillFiles.push(...standaloneFiles);

  const results: SkillValidationResult[] = [];
  let compliant = 0;
  let withWarnings = 0;
  let withErrors = 0;

  for (const skillFile of skillFiles) {
    const result = await validateSkillFile(skillFile);
    results.push(result);

    if (result.fatal || result.errors.length > 0) {
      withErrors++;
    } else if (result.warnings.length > 0) {
      withWarnings++;
    } else {
      compliant++;
    }
  }

  return {
    total: skillFiles.length,
    compliant,
    withWarnings,
    withErrors,
    results,
  };
}
