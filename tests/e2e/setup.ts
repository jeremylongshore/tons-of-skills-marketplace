import { vi, beforeEach, afterEach } from 'vitest';
import fs from 'fs/promises';
import path from 'path';
import { randomUUID } from 'crypto';
import { spawn, ChildProcess } from 'child_process';
import {
  parseSkillFrontmatter,
  type SkillFrontmatterValue
} from '../../scripts/skill-frontmatter.mjs';

const activeMcpServers = new Set<McpServer>();
// The harness projects the marketplace-required fields used by these scenarios.
// Full field semantics stay owned by the repository's validate-skills-schema.py gate.
const SKILL_REQUIRED_FIELDS = [
  'name',
  'description',
  'allowed-tools',
  'version',
  'author',
  'license',
  'compatibility',
  'tags'
] as const;

/**
 * Test environment for isolated E2E testing
 */
export interface TestEnvironment {
  /** Unique test environment ID */
  id: string;
  /** Base path for test environment */
  basePath: string;
  /** Path to test marketplace catalog */
  catalogPath: string;
  /** Path to installed plugins */
  pluginsPath: string;
  /** Installed plugins */
  installedPlugins: Map<string, PluginMetadata>;
  /** Active MCP servers */
  mcpServers: Map<string, McpServer>;
  /** Cleanup function */
  cleanup: () => Promise<void>;
}

export interface PluginMetadata {
  name: string;
  version: string;
  description: string;
  author: {
    name: string;
    email: string;
  };
  license: string;
  manifestPath: string;
  installPath: string;
}

export interface Skill {
  name: string;
  description: string;
  allowedTools: string[];
  version: string;
  author: string;
  license: string;
  compatibility: string;
  tags: string[];
  content: string;
  triggerPhrases: string[];
}

export interface McpServer {
  /** Server process */
  process: ChildProcess;
  /** Server name */
  name: string;
  /** Server port (if applicable) */
  port?: number;
  /** Registered tools */
  tools: Map<string, McpTool>;
  /** Server status */
  status: 'starting' | 'ready' | 'error' | 'stopped';
  /** Stop function */
  stop: () => Promise<void>;
}

export interface McpTool {
  name: string;
  description: string;
  inputSchema: Record<string, unknown>;
}

export interface McpServerOptions {
  startupTimeoutMs?: number;
  stopGraceMs?: number;
  onSpawn?: (serverProcess: ChildProcess) => void;
}

/**
 * Create an isolated test environment
 */
export async function createTestEnv(): Promise<TestEnvironment> {
  const id = randomUUID();
  const basePath = path.join('/tmp', `claude-e2e-test-${id}`);
  const catalogPath = path.join(basePath, 'marketplace.json');
  const pluginsPath = path.join(basePath, 'plugins');

  // Create directory structure
  await fs.mkdir(basePath, { recursive: true });
  await fs.mkdir(pluginsPath, { recursive: true });

  // Create empty catalog
  await fs.writeFile(
    catalogPath,
    JSON.stringify({
      name: 'test-marketplace',
      version: '1.0.0',
      plugins: []
    }, null, 2)
  );

  const installedPlugins = new Map<string, PluginMetadata>();
  const mcpServers = new Map<string, McpServer>();

  const cleanup = async () => {
    // Stop all MCP servers
    for (const server of mcpServers.values()) {
      await server.stop();
    }

    // Remove test directory unless E2E_KEEP_ARTIFACTS is set
    if (!process.env.E2E_KEEP_ARTIFACTS) {
      await fs.rm(basePath, { recursive: true, force: true });
    } else {
      console.log(`Test artifacts kept at: ${basePath}`);
    }
  };

  return {
    id,
    basePath,
    catalogPath,
    pluginsPath,
    installedPlugins,
    mcpServers,
    cleanup
  };
}

/**
 * Install a plugin into the test environment
 */
export async function installPlugin(
  env: TestEnvironment,
  pluginSourcePath: string
): Promise<PluginMetadata> {
  // Read plugin manifest
  const manifestPath = path.join(pluginSourcePath, '.claude-plugin', 'plugin.json');
  const manifestContent = await fs.readFile(manifestPath, 'utf-8');
  const manifest = JSON.parse(manifestContent);

  // Validate required fields
  if (!manifest.name || !manifest.version || !manifest.description) {
    throw new Error('Invalid plugin manifest: missing required fields');
  }

  // Check for duplicate installation
  if (env.installedPlugins.has(manifest.name)) {
    throw new Error(`Plugin ${manifest.name} is already installed`);
  }

  // Copy plugin files to test environment
  const installPath = path.join(env.pluginsPath, manifest.name);
  await copyDirectory(pluginSourcePath, installPath);

  const metadata: PluginMetadata = {
    name: manifest.name,
    version: manifest.version,
    description: manifest.description,
    author: manifest.author || { name: 'Unknown', email: '' },
    license: manifest.license || 'MIT',
    manifestPath: path.join(installPath, '.claude-plugin', 'plugin.json'),
    installPath
  };

  env.installedPlugins.set(manifest.name, metadata);

  return metadata;
}

/**
 * Uninstall a plugin from the test environment
 */
export async function uninstallPlugin(
  env: TestEnvironment,
  pluginName: string
): Promise<void> {
  const plugin = env.installedPlugins.get(pluginName);
  if (!plugin) {
    throw new Error(`Plugin ${pluginName} is not installed`);
  }

  // Remove plugin directory
  await fs.rm(plugin.installPath, { recursive: true, force: true });

  // Remove from installed plugins map
  env.installedPlugins.delete(pluginName);
}

/**
 * Load a skill from a plugin
 */
export async function loadSkill(
  env: TestEnvironment,
  pluginName: string,
  skillName: string
): Promise<Skill> {
  const plugin = env.installedPlugins.get(pluginName);
  if (!plugin) {
    throw new Error(`Plugin ${pluginName} is not installed`);
  }

  const skillPath = path.join(
    plugin.installPath,
    'skills',
    skillName,
    'SKILL.md'
  );

  // Read skill file
  const skillContent = await fs.readFile(skillPath, 'utf-8');

  const frontmatter = parseSkillFrontmatter(skillContent);
  if (!frontmatter) {
    throw new Error(`Invalid skill: missing frontmatter in ${skillPath}`);
  }

  const missingFields = SKILL_REQUIRED_FIELDS.filter(
    field => frontmatter[field] === undefined || frontmatter[field] === null
  );
  if (missingFields.length > 0) {
    throw new Error(`Invalid skill: missing required fields: ${missingFields.join(', ')}`);
  }

  const name = requireStringField(frontmatter, 'name');
  const description = requireStringField(frontmatter, 'description');
  const version = requireStringField(frontmatter, 'version');
  const author = requireStringField(frontmatter, 'author');
  const license = requireStringField(frontmatter, 'license');
  const compatibility = requireStringField(frontmatter, 'compatibility');
  const tags = parseStringList(frontmatter.tags, 'tags');
  const allowedTools = parseAllowedTools(frontmatter['allowed-tools']);

  // Extract trigger phrases from description
  const triggerPhrases = extractTriggerPhrases(description);

  return {
    name: name || skillName,
    description,
    allowedTools,
    version,
    author,
    license,
    compatibility,
    tags,
    content: skillContent,
    triggerPhrases
  };
}

/**
 * Simulate skill activation by trigger phrase
 */
export async function activateSkill(
  env: TestEnvironment,
  userInput: string
): Promise<Skill | null> {
  // Search all installed plugins for matching skills
  for (const plugin of env.installedPlugins.values()) {
    const skillsPath = path.join(plugin.installPath, 'skills');

    try {
      const skillDirs = await fs.readdir(skillsPath);

      for (const skillDir of skillDirs) {
        const skillPath = path.join(skillsPath, skillDir, 'SKILL.md');

        try {
          const skill = await loadSkill(env, plugin.name, skillDir);

          // Check if user input matches any trigger phrase
          for (const trigger of skill.triggerPhrases) {
            if (userInput.toLowerCase().includes(trigger.toLowerCase())) {
              return skill;
            }
          }
        } catch (error) {
          // Skill file might not exist or be invalid, continue
          continue;
        }
      }
    } catch (error) {
      // Plugin might not have skills directory, continue
      continue;
    }
  }

  return null;
}

/**
 * Start an MCP server for testing
 */
export async function startMcpServer(
  serverPath: string,
  serverName: string,
  options: McpServerOptions = {}
): Promise<McpServer> {
  return new Promise((resolve, reject) => {
    // Spawn MCP server process
    const serverProcess = spawn('node', [serverPath], {
      stdio: ['pipe', 'pipe', 'pipe'],
      env: { ...process.env, NODE_ENV: 'test' }
    });
    options.onSpawn?.(serverProcess);

    const startupTimeoutMs = options.startupTimeoutMs ?? 5000;
    const stopGraceMs = options.stopGraceMs ?? 2000;

    const server: McpServer = {
      process: serverProcess,
      name: serverName,
      tools: new Map<string, McpTool>(),
      status: 'starting',
      stop: async () => {}
    };
    let startupSettled = false;
    let stopPromise: Promise<void> | undefined;
    let startupTimer: NodeJS.Timeout;
    let processClosed = false;

    const removeStartupListeners = () => {
      serverProcess.stdout?.off('data', handleStdout);
      serverProcess.off('error', handleStartupError);
      serverProcess.off('exit', handleStartupExit);
    };

    const finishStartup = (error?: Error) => {
      if (startupSettled) return;
      startupSettled = true;
      clearTimeout(startupTimer);
      removeStartupListeners();
      if (error) {
        reject(error);
      } else {
        activeMcpServers.add(server);
        resolve(server);
      }
    };

    const markStopped = () => {
      server.status = 'stopped';
      activeMcpServers.delete(server);
    };

    const handleLifecycleExit = () => markStopped();
    const handleLifecycleError = () => {
      if (server.status !== 'stopped') server.status = 'error';
    };
    const handleStderr = (data: Buffer) => {
      console.error(`MCP Server error: ${data.toString()}`);
    };
    const removeLifecycleListeners = () => {
      serverProcess.off('exit', handleLifecycleExit);
      serverProcess.off('error', handleLifecycleError);
      serverProcess.stderr?.off('data', handleStderr);
    };
    const handleLifecycleClose = () => {
      processClosed = true;
      markStopped();
      removeLifecycleListeners();
    };

    serverProcess.once('exit', handleLifecycleExit);
    serverProcess.on('error', handleLifecycleError);
    serverProcess.once('close', handleLifecycleClose);
    serverProcess.stderr?.on('data', handleStderr);

    server.stop = () => {
      if (stopPromise) return stopPromise;
      stopPromise = new Promise<void>(stopResolve => {
        clearTimeout(startupTimer);
        removeStartupListeners();

        if (processClosed) {
          markStopped();
          stopResolve();
          return;
        }

        let forceTimer: NodeJS.Timeout;
        const stopped = () => {
          clearTimeout(forceTimer);
          serverProcess.off('close', stopped);
          markStopped();
          stopResolve();
        };

        forceTimer = setTimeout(() => {
          if (!processClosed) {
            serverProcess.kill('SIGKILL');
          }
        }, stopGraceMs);
        serverProcess.once('close', stopped);
        if (serverProcess.exitCode === null && serverProcess.signalCode === null) {
          serverProcess.kill('SIGTERM');
        }
      });
      return stopPromise;
    };

    // Collect stdout for tool registration
    let stdoutBuffer = '';
    const handleStdout = (data: Buffer) => {
      stdoutBuffer += data.toString();

      const messages = stdoutBuffer.split('\n');
      stdoutBuffer = messages.pop() ?? '';
      for (const message of messages) {
        if (!message.trim()) continue;

        try {
          const parsed = JSON.parse(message);
          if (parsed.method === 'tools/list') {
            for (const tool of parsed.params?.tools || []) {
              server.tools.set(tool.name, {
                name: tool.name,
                description: tool.description,
                inputSchema: tool.inputSchema
              });
            }
            server.status = 'ready';
            finishStartup();
          }
        } catch {
          // Not JSON, ignore
        }
      }
    };
    serverProcess.stdout?.on('data', handleStdout);

    const handleStartupError = (error: Error) => {
      void server.stop().then(() => finishStartup(error));
    };
    const handleStartupExit = (code: number | null) => {
      void server.stop().then(() => {
        finishStartup(new Error(`MCP Server exited with code ${code}`));
      });
    };
    serverProcess.once('error', handleStartupError);
    serverProcess.once('exit', handleStartupExit);

    startupTimer = setTimeout(() => {
      void server.stop().then(() => {
        finishStartup(new Error('MCP Server startup timeout'));
      });
    }, startupTimeoutMs);
  });
}

/**
 * Invoke an MCP tool
 */
export async function invokeMcpTool(
  server: McpServer,
  toolName: string,
  params: Record<string, unknown>,
  timeoutMs = 10000
): Promise<unknown> {
  if (!server.tools.has(toolName)) {
    throw new Error(`Tool ${toolName} not found on server ${server.name}`);
  }

  return new Promise((resolve, reject) => {
    const requestId = randomUUID();
    const request = {
      jsonrpc: '2.0',
      id: requestId,
      method: 'tools/call',
      params: {
        name: toolName,
        arguments: params
      }
    };

    let responseBuffer = '';
    let settled = false;
    let timeout: NodeJS.Timeout;
    const finish = (error?: Error, result?: unknown) => {
      if (settled) return;
      settled = true;
      clearTimeout(timeout);
      server.process.stdout?.off('data', responseHandler);
      server.process.off('exit', exitHandler);
      server.process.off('error', errorHandler);
      if (error) reject(error);
      else resolve(result);
    };

    const responseHandler = (data: Buffer) => {
      responseBuffer += data.toString();
      const messages = responseBuffer.split('\n');
      responseBuffer = messages.pop() ?? '';
      for (const message of messages) {
        if (!message.trim()) continue;
        try {
          const parsed = JSON.parse(message);
          if (parsed.id === requestId) {
            if (parsed.error) finish(new Error(parsed.error.message));
            else finish(undefined, parsed.result);
            return;
          }
        } catch {
          // Not JSON or not our response, ignore
        }
      }
    };
    const exitHandler = () => finish(new Error('MCP Server exited during tool invocation'));
    const errorHandler = (error: Error) => finish(error);

    server.process.stdout?.on('data', responseHandler);
    server.process.once('exit', exitHandler);
    server.process.once('error', errorHandler);

    timeout = setTimeout(() => finish(new Error('MCP tool invocation timeout')), timeoutMs);

    if (!server.process.stdin || server.process.stdin.destroyed) {
      finish(new Error('MCP Server stdin is unavailable'));
      return;
    }
    server.process.stdin.write(JSON.stringify(request) + '\n', error => {
      if (error) finish(error);
    });
  });
}

/**
 * Helper: Copy directory recursively
 */
async function copyDirectory(src: string, dest: string): Promise<void> {
  await fs.mkdir(dest, { recursive: true });

  const entries = await fs.readdir(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (entry.isDirectory()) {
      await copyDirectory(srcPath, destPath);
    } else {
      await fs.copyFile(srcPath, destPath);
    }
  }
}

/**
 * Helper: Require a non-empty string frontmatter field
 */
function requireStringField(
  frontmatter: Record<string, SkillFrontmatterValue>,
  fieldName: string
): string {
  const value = frontmatter[fieldName];
  if (typeof value !== 'string' || value.trim().length === 0) {
    throw new TypeError(`Invalid skill: ${fieldName} must be a non-empty string`);
  }
  return value.trim();
}

/**
 * Helper: Parse string-or-list metadata
 */
function parseStringList(value: SkillFrontmatterValue, fieldName: string): string[] {
  if (!Array.isArray(value)) {
    throw new TypeError(`Invalid skill: ${fieldName} must be a YAML list`);
  }
  const result = value.map((item, index) => {
    if (typeof item !== 'string' || item.trim().length === 0) {
      throw new TypeError(`Invalid skill: ${fieldName}[${index}] must be a non-empty string`);
    }
    return item.trim();
  });
  if (result.length === 0) {
    throw new TypeError(`Invalid skill: ${fieldName} must not be empty`);
  }
  return result;
}

function parseAllowedTools(value: SkillFrontmatterValue): string[] {
  if (Array.isArray(value)) return parseStringList(value, 'allowed-tools');
  if (typeof value !== 'string') {
    throw new TypeError('Invalid skill: allowed-tools must be a string or YAML list');
  }

  const tools: string[] = [];
  let token = '';
  let depth = 0;
  for (const character of value.trim()) {
    if (character === '(') depth += 1;
    if (character === ')') {
      depth -= 1;
      if (depth < 0) throw new TypeError('Invalid skill: unbalanced allowed-tools scope');
    }
    if ((character === ',' || /\s/u.test(character)) && depth === 0) {
      if (token.trim()) tools.push(token.trim());
      token = '';
    } else {
      token += character;
    }
  }
  if (depth !== 0) throw new TypeError('Invalid skill: unbalanced allowed-tools scope');
  if (token.trim()) tools.push(token.trim());
  if (tools.length === 0) throw new TypeError('Invalid skill: allowed-tools must not be empty');
  return tools;
}

/**
 * Helper: Extract trigger phrases from description
 */
function extractTriggerPhrases(description: string): string[] {
  const triggers: string[] = [];

  // Look for quoted phrases
  const quotedMatches = description.match(/"([^"]+)"/g);
  if (quotedMatches) {
    triggers.push(...quotedMatches.map(m => m.replace(/"/g, '')));
  }

  // Look for common trigger patterns
  const patterns = [
    /trigger with ([\w\s]+)/gi,
    /use when ([\w\s]+)/gi,
    /activate on ([\w\s]+)/gi
  ];

  for (const pattern of patterns) {
    const matches = description.matchAll(pattern);
    for (const match of matches) {
      triggers.push(match[1].trim());
    }
  }

  return triggers;
}

/**
 * Global setup: Clean up any leftover test environments
 */
beforeEach(async () => {
  // Cleanup old test directories (older than 1 hour)
  try {
    const tmpDir = '/tmp';
    const entries = await fs.readdir(tmpDir, { withFileTypes: true });
    const oneHourAgo = Date.now() - 3600000;

    for (const entry of entries) {
      if (entry.isDirectory() && entry.name.startsWith('claude-e2e-test-')) {
        const dirPath = path.join(tmpDir, entry.name);
        const stats = await fs.stat(dirPath);

        if (stats.mtimeMs < oneHourAgo) {
          await fs.rm(dirPath, { recursive: true, force: true });
        }
      }
    }
  } catch (error) {
    // Ignore cleanup errors
  }
});

/**
 * Global teardown: Log test environment info
 */
afterEach(() => {
  const cleanup = [...activeMcpServers].map(server => server.stop());
  if (process.env.E2E_DEBUG) {
    console.log('Test completed');
  }
  return Promise.all(cleanup);
});
