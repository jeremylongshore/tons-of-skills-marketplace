/**
 * Frontmatter Validator - Validates YAML frontmatter in markdown files
 *
 * Validates commands and agents markdown files for proper frontmatter formatting.
 */

/**
 * Compatibility validator used by `ccpi validate`. The repository's universal
 * Python validator remains authoritative for marketplace grading.
 */

import { promises as fs } from 'node:fs';
import * as path from 'node:path';
import * as yaml from 'yaml';

const VALID_CATEGORIES = [
  'git',
  'deployment',
  'security',
  'testing',
  'documentation',
  'database',
  'api',
  'frontend',
  'backend',
  'devops',
  'forecasting',
  'analytics',
  'migration',
  'monitoring',
  'other',
];

const VALID_DIFFICULTIES = ['beginner', 'intermediate', 'advanced', 'expert'];
const VALID_EFFORT_LEVELS = ['low', 'medium', 'high', 'xhigh', 'max'];
const VALID_MODELS = ['sonnet', 'opus', 'haiku', 'fable', 'inherit'];
const VALID_PERMISSION_MODES = [
  'default',
  'manual',
  'acceptEdits',
  'auto',
  'dontAsk',
  'bypassPermissions',
  'plan',
];
const VALID_MEMORY_SCOPES = ['user', 'project', 'local'];
const VALID_COLORS = ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink', 'cyan'];
const INVALID_AGENT_FIELDS = ['capabilities', 'expertise_level', 'activation_priority'];

/**
 * Type-safe check that an unknown value is a string contained in a string array.
 */
function isStringIn(value: unknown, allowed: string[]): boolean {
  return typeof value === 'string' && allowed.includes(value);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function hasPathSegment(filePath: string, segment: string): boolean {
  return filePath.replaceAll('\\', '/').split('/').includes(segment);
}

function validateStringArray(value: unknown, field: string): string[] {
  if (!Array.isArray(value)) {
    return [`Field '${field}' must be an array`];
  }
  return value.flatMap((item, index) =>
    typeof item === 'string' ? [] : [`Field '${field}[${index}]' must be a string`],
  );
}

export interface FrontmatterValidationResult {
  file: string;
  fileType: 'command' | 'agent' | 'unknown';
  error?: string;
  errors: string[];
}

export interface FrontmatterValidationSummary {
  total: number;
  warnings: number;
  errors: number;
  results: FrontmatterValidationResult[];
}

/**
 * Extract YAML frontmatter from markdown file
 */
function extractFrontmatter(content: string): {
  frontmatter: Record<string, unknown> | null;
  error: string | null;
} {
  const match = content.match(/^---\s*\n([\s\S]*?)\n---\s*\n/);
  if (!match) {
    return { frontmatter: null, error: 'No frontmatter found' };
  }

  try {
    const frontmatter = yaml.parse(match[1]);
    return { frontmatter: frontmatter || {}, error: null };
  } catch (e) {
    return { frontmatter: null, error: `Invalid YAML: ${e}` };
  }
}

/**
 * Validate frontmatter for command files
 * Matches the Intent Solutions frontmatter validation standard
 */
function validateCommandFrontmatter(
  frontmatter: Record<string, unknown>,
  filePath: string,
): string[] {
  const errors: string[] = [];
  const fileName = path.basename(filePath, '.md');

  if (!('name' in frontmatter)) {
    errors.push('Missing required field: name');
  } else if (typeof frontmatter.name !== 'string') {
    errors.push("Field 'name' must be a string");
  } else {
    const name = frontmatter.name;
    if (!/^[a-z][a-z0-9-]*[a-z0-9]$/.test(name) && name.length > 1) {
      errors.push("Field 'name' must be kebab-case (lowercase + hyphens)");
    }
    if (name !== fileName) {
      errors.push(`Field 'name' '${name}' should match filename '${fileName}.md'`);
    }
  }

  if (!('description' in frontmatter)) {
    errors.push('Missing required field: description');
  } else if (typeof frontmatter.description !== 'string') {
    errors.push("Field 'description' must be a string");
  } else {
    if (frontmatter.description.length < 10) {
      errors.push("Field 'description' must be at least 10 characters");
    }
    if (frontmatter.description.length > 80) {
      errors.push("Field 'description' must be 80 characters or less");
    }
  }

  if ('shortcut' in frontmatter) {
    const shortcut = frontmatter.shortcut;
    if (typeof shortcut !== 'string') {
      errors.push("Field 'shortcut' must be a string");
    } else {
      if (shortcut.length < 1 || shortcut.length > 4) {
        errors.push("Field 'shortcut' must be 1-4 characters");
      }
      if (shortcut !== shortcut.toLowerCase()) {
        errors.push("Field 'shortcut' must be lowercase");
      }
      if (!/^[a-z]+$/.test(shortcut)) {
        errors.push("Field 'shortcut' must contain only letters");
      }
    }
  }

  if ('category' in frontmatter) {
    if (!isStringIn(frontmatter.category, VALID_CATEGORIES)) {
      errors.push(`Invalid category. Must be one of: ${VALID_CATEGORIES.join(', ')}`);
    }
  }

  if ('difficulty' in frontmatter) {
    if (!isStringIn(frontmatter.difficulty, VALID_DIFFICULTIES)) {
      errors.push(`Invalid difficulty. Must be one of: ${VALID_DIFFICULTIES.join(', ')}`);
    }
  }

  return errors;
}

/**
 * Validate frontmatter for agent files
 * Matches the Intent Solutions frontmatter validation standard
 */
function validateAgentFrontmatter(
  frontmatter: Record<string, unknown>,
  _filePath: string,
): string[] {
  const errors: string[] = [];

  if (!('name' in frontmatter)) {
    errors.push('Missing required field: name');
  } else if (typeof frontmatter.name !== 'string') {
    errors.push("Field 'name' must be a string");
  } else {
    const name = frontmatter.name;
    if (!/^[a-z][a-z0-9-]*[a-z0-9]$/.test(name) && name.length > 1) {
      errors.push("Field 'name' must be kebab-case (lowercase + hyphens)");
    }
  }

  // 20-1536 chars per the current Intent Solutions disclosure-marker cap.
  if (!('description' in frontmatter)) {
    errors.push('Missing required field: description');
  } else if (typeof frontmatter.description !== 'string') {
    errors.push("Field 'description' must be a string");
  } else {
    if (frontmatter.description.length < 20) {
      errors.push("Field 'description' must be at least 20 characters");
    }
    if (frontmatter.description.length > 1536) {
      errors.push("Field 'description' must be 1536 characters or less");
    }
  }

  for (const field of INVALID_AGENT_FIELDS) {
    if (field in frontmatter) {
      errors.push(`Invalid agent field: ${field}`);
    }
  }

  if ('tools' in frontmatter && typeof frontmatter.tools !== 'string') {
    errors.push(...validateStringArray(frontmatter.tools, 'tools'));
  }

  if ('disallowedTools' in frontmatter) {
    errors.push(...validateStringArray(frontmatter.disallowedTools, 'disallowedTools'));
  }

  if ('skills' in frontmatter) {
    errors.push(...validateStringArray(frontmatter.skills, 'skills'));
  }

  if ('model' in frontmatter) {
    const model = frontmatter.model;
    const isFullModelId = typeof model === 'string' && /^claude-[a-z0-9][a-z0-9.-]*$/.test(model);
    if (!isStringIn(model, VALID_MODELS) && !isFullModelId) {
      errors.push(
        `Invalid model. Must be one of: ${VALID_MODELS.join(', ')}, or a full Claude model ID`,
      );
    }
  }

  if ('effort' in frontmatter) {
    if (!isStringIn(frontmatter.effort, VALID_EFFORT_LEVELS)) {
      errors.push(`Invalid effort. Must be one of: ${VALID_EFFORT_LEVELS.join(', ')}`);
    }
  }

  if ('maxTurns' in frontmatter) {
    if (
      typeof frontmatter.maxTurns !== 'number' ||
      !Number.isInteger(frontmatter.maxTurns) ||
      frontmatter.maxTurns < 1
    ) {
      errors.push("Field 'maxTurns' must be a positive integer");
    }
  }

  if (
    'permissionMode' in frontmatter &&
    !isStringIn(frontmatter.permissionMode, VALID_PERMISSION_MODES)
  ) {
    errors.push(`Invalid permissionMode. Must be one of: ${VALID_PERMISSION_MODES.join(', ')}`);
  }

  if ('memory' in frontmatter && !isStringIn(frontmatter.memory, VALID_MEMORY_SCOPES)) {
    errors.push(`Invalid memory. Must be one of: ${VALID_MEMORY_SCOPES.join(', ')}`);
  }

  if ('background' in frontmatter && typeof frontmatter.background !== 'boolean') {
    errors.push("Field 'background' must be a boolean");
  }

  if ('hooks' in frontmatter && !isRecord(frontmatter.hooks)) {
    errors.push("Field 'hooks' must be an object");
  }

  if ('mcpServers' in frontmatter) {
    const servers = frontmatter.mcpServers;
    if (Array.isArray(servers)) {
      for (let index = 0; index < servers.length; index++) {
        const server = servers[index];
        if (typeof server !== 'string' && (!isRecord(server) || Object.keys(server).length !== 1)) {
          errors.push(
            `Field 'mcpServers[${index}]' must be a server-name string or one-key inline definition`,
          );
        }
      }
    } else if (!isRecord(servers)) {
      errors.push("Field 'mcpServers' must be an array or object");
    }
  }

  if ('isolation' in frontmatter && frontmatter.isolation !== 'worktree') {
    errors.push("Field 'isolation' must be 'worktree'");
  }

  if ('color' in frontmatter && !isStringIn(frontmatter.color, VALID_COLORS)) {
    errors.push(`Invalid color. Must be one of: ${VALID_COLORS.join(', ')}`);
  }

  if ('initialPrompt' in frontmatter && typeof frontmatter.initialPrompt !== 'string') {
    errors.push("Field 'initialPrompt' must be a string");
  }

  if ('experimental' in frontmatter) {
    const experimental = frontmatter.experimental;
    if (!isRecord(experimental)) {
      errors.push("Field 'experimental' must be an object");
    } else if (
      'cacheTtl' in experimental &&
      !['5m', '1h'].includes(String(experimental.cacheTtl))
    ) {
      errors.push("Field 'experimental.cacheTtl' must be one of: 5m, 1h");
    }
  }

  return errors;
}

/**
 * Validate a single markdown file's frontmatter
 */
export async function validateFrontmatterFile(
  filePath: string,
): Promise<FrontmatterValidationResult> {
  const result: FrontmatterValidationResult = {
    file: filePath,
    fileType: 'unknown',
    errors: [],
  };

  if (hasPathSegment(filePath, 'commands')) {
    result.fileType = 'command';
  } else if (hasPathSegment(filePath, 'agents')) {
    result.fileType = 'agent';
  }

  let content: string;
  try {
    content = await fs.readFile(filePath, 'utf-8');
  } catch (e) {
    result.error = `Cannot read file: ${e}`;
    return result;
  }

  const { frontmatter, error } = extractFrontmatter(content);

  if (error) {
    result.error = error;
    return result;
  }

  if (!frontmatter) {
    result.error = 'No frontmatter found';
    return result;
  }

  if (result.fileType === 'command') {
    result.errors = validateCommandFrontmatter(frontmatter, filePath);
  } else if (result.fileType === 'agent') {
    result.errors = validateAgentFrontmatter(frontmatter, filePath);
  }

  return result;
}

/**
 * Find all command and agent markdown files
 */
export async function findFrontmatterFiles(baseDir: string): Promise<string[]> {
  const files: string[] = [];

  async function walkDir(dir: string): Promise<void> {
    try {
      const entries = await fs.readdir(dir, { withFileTypes: true });
      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        if (entry.isDirectory()) {
          await walkDir(fullPath);
        } else if (entry.name.endsWith('.md')) {
          if (hasPathSegment(fullPath, 'commands') || hasPathSegment(fullPath, 'agents')) {
            files.push(fullPath);
          }
        }
      }
    } catch {
      // Directory not accessible
    }
  }

  await walkDir(path.join(baseDir, 'plugins'));
  return files;
}

/**
 * Validate all frontmatter in a directory
 */
export async function validateAllFrontmatter(
  baseDir: string,
  strict: boolean = false,
): Promise<FrontmatterValidationSummary> {
  const files = await findFrontmatterFiles(baseDir);
  const results: FrontmatterValidationResult[] = [];
  let warnings = 0;
  let errorCount = 0;

  for (const file of files) {
    const result = await validateFrontmatterFile(file);
    results.push(result);

    if (result.error) {
      if (strict) {
        errorCount++;
      } else {
        warnings++;
      }
    } else if (result.errors.length > 0) {
      errorCount++;
    }
  }

  return {
    total: files.length,
    warnings,
    errors: errorCount,
    results,
  };
}
