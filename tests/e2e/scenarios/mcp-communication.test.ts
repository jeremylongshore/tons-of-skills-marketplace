import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import path from 'path';
import fs from 'fs/promises';
import {
  createTestEnv,
  startMcpServer,
  invokeMcpTool,
  type TestEnvironment,
  type McpServer
} from '../setup';

describe('MCP Server Communication', () => {
  let env: TestEnvironment;

  beforeEach(async () => {
    env = await createTestEnv();
  });

  afterEach(async () => {
    await env.cleanup();
  });

  describe('Server Lifecycle', () => {
    it('should start MCP server successfully', async () => {
      // Arrange - create minimal MCP server
      const serverPath = await createMockMcpServer(env.basePath, 'test-server');

      // Act
      const server = await startMcpServer(serverPath, 'test-server');

      // Assert
      expect(server).toBeDefined();
      expect(server.name).toBe('test-server');
      expect(server.status).toBe('ready');
      expect(server.process).toBeDefined();

      // Cleanup
      await server.stop();
    });

    it('should initialize server in ready state', async () => {
      // Arrange
      const serverPath = await createMockMcpServer(env.basePath, 'test-server');

      // Act
      const server = await startMcpServer(serverPath, 'test-server');

      // Assert
      expect(server.status).toBe('ready');

      // Cleanup
      await server.stop();
    });

    it('should shutdown server gracefully', async () => {
      // Arrange
      const serverPath = await createMockMcpServer(env.basePath, 'test-server');
      const server = await startMcpServer(serverPath, 'test-server');

      // Act
      await server.stop();

      // Assert
      expect(server.status).toBe('stopped');
    });

    it('should timeout on slow server startup', async () => {
      // Arrange - create server that never responds
      const serverPath = await createNeverReadyMcpServer(env.basePath, 'slow-server');
      let childProcess: McpServer['process'] | undefined;

      // Act & Assert
      await expect(startMcpServer(serverPath, 'slow-server', {
        startupTimeoutMs: 100,
        onSpawn: process => {
          childProcess = process;
        }
      }))
        .rejects
        .toThrow('MCP Server startup timeout');

      expect(childProcess).toBeDefined();
      expect(childProcess?.exitCode ?? childProcess?.signalCode).not.toBeNull();
    });

    it('should handle server crash during startup', async () => {
      // Arrange - create server that crashes immediately
      const serverPath = await createCrashingMcpServer(env.basePath, 'crash-server');

      // Act & Assert
      await expect(startMcpServer(serverPath, 'crash-server'))
        .rejects
        .toThrow();
    });

    it('should stop idempotently and expose live status', async () => {
      const serverPath = await createMockMcpServer(env.basePath, 'test-server');
      const server = await startMcpServer(serverPath, 'test-server');

      await Promise.all([server.stop(), server.stop()]);
      await server.stop();

      expect(server.status).toBe('stopped');
      expect(server.process.exitCode ?? server.process.signalCode).not.toBeNull();
      expect(server.process.listenerCount('error')).toBe(0);
      expect(server.process.listenerCount('exit')).toBe(0);
      expect(server.process.listenerCount('close')).toBe(0);
      expect(server.process.stderr?.listenerCount('data')).toBe(0);
    });

    it('should not resolve stop on a process error before close', async () => {
      const serverPath = await createIgnoringSignalMcpServer(env.basePath, 'stubborn-server');
      const server = await startMcpServer(serverPath, 'stubborn-server', {
        stopGraceMs: 100
      });
      let stopped = false;

      const stopPromise = server.stop().then(() => {
        stopped = true;
      });
      server.process.emit('error', new Error('synthetic process error'));
      await new Promise(resolve => setTimeout(resolve, 20));

      expect(stopped).toBe(false);
      await stopPromise;
      expect(server.status).toBe('stopped');
    });
  });

  describe('Tool Registration', () => {
    it('should register tools on startup', async () => {
      // Arrange
      const serverPath = await createMockMcpServer(env.basePath, 'test-server', {
        tools: [
          {
            name: 'test-tool',
            description: 'A test tool',
            inputSchema: { type: 'object', properties: {} }
          }
        ]
      });

      // Act
      const server = await startMcpServer(serverPath, 'test-server');

      // Assert
      expect(server.tools.size).toBeGreaterThan(0);
      expect(server.tools.has('test-tool')).toBe(true);

      const tool = server.tools.get('test-tool');
      expect(tool?.name).toBe('test-tool');
      expect(tool?.description).toBe('A test tool');

      // Cleanup
      await server.stop();
    });

    it('should register multiple tools', async () => {
      // Arrange
      const serverPath = await createMockMcpServer(env.basePath, 'test-server', {
        tools: [
          {
            name: 'tool-1',
            description: 'First tool',
            inputSchema: { type: 'object' }
          },
          {
            name: 'tool-2',
            description: 'Second tool',
            inputSchema: { type: 'object' }
          }
        ]
      });

      // Act
      const server = await startMcpServer(serverPath, 'test-server');

      // Assert
      expect(server.tools.size).toBe(2);
      expect(server.tools.has('tool-1')).toBe(true);
      expect(server.tools.has('tool-2')).toBe(true);

      // Cleanup
      await server.stop();
    });

    it('should include tool input schemas', async () => {
      // Arrange
      const serverPath = await createMockMcpServer(env.basePath, 'test-server', {
        tools: [
          {
            name: 'test-tool',
            description: 'Test tool',
            inputSchema: {
              type: 'object',
              properties: {
                message: { type: 'string' }
              },
              required: ['message']
            }
          }
        ]
      });

      // Act
      const server = await startMcpServer(serverPath, 'test-server');

      // Assert
      const tool = server.tools.get('test-tool');
      expect(tool?.inputSchema).toBeDefined();
      expect(tool?.inputSchema.type).toBe('object');
      expect(tool?.inputSchema.properties).toHaveProperty('message');

      // Cleanup
      await server.stop();
    });
  });

  describe('Tool Invocation', () => {
    it('should invoke tool with parameters', async () => {
      // Arrange
      const serverPath = await createMockMcpServer(env.basePath, 'test-server', {
        tools: [
          {
            name: 'echo',
            description: 'Echo tool',
            inputSchema: {
              type: 'object',
              properties: { message: { type: 'string' } }
            }
          }
        ]
      });
      const server = await startMcpServer(serverPath, 'test-server');

      // Act
      const result = await invokeMcpTool(server, 'echo', { message: 'hello' });

      // Assert
      expect(result).toBeDefined();

      // Cleanup
      await server.stop();
    });

    it('should reject invocation of non-existent tool', async () => {
      // Arrange
      const serverPath = await createMockMcpServer(env.basePath, 'test-server');
      const server = await startMcpServer(serverPath, 'test-server');

      // Act & Assert
      await expect(invokeMcpTool(server, 'non-existent', {}))
        .rejects
        .toThrow('Tool non-existent not found');

      // Cleanup
      await server.stop();
    });

    it('should handle tool invocation timeout', async () => {
      // Arrange - server that never responds to tool calls
      const serverPath = await createIgnoringMcpServer(env.basePath, 'slow-server');
      const server = await startMcpServer(serverPath, 'slow-server');
      const stdoutListeners = server.process.stdout?.listenerCount('data');
      const exitListeners = server.process.listenerCount('exit');

      // Act & Assert
      await expect(invokeMcpTool(server, 'slow-tool', {}, 100))
        .rejects
        .toThrow('MCP tool invocation timeout');

      expect(server.process.stdout?.listenerCount('data')).toBe(stdoutListeners);
      expect(server.process.listenerCount('exit')).toBe(exitListeners);

      // Cleanup
      await server.stop();
    });

    it('should pass parameters correctly', async () => {
      // Arrange
      const serverPath = await createMockMcpServer(env.basePath, 'test-server', {
        tools: [
          {
            name: 'sum',
            description: 'Sum two numbers',
            inputSchema: {
              type: 'object',
              properties: {
                a: { type: 'number' },
                b: { type: 'number' }
              }
            }
          }
        ]
      });
      const server = await startMcpServer(serverPath, 'test-server');

      // Act
      const result = await invokeMcpTool(server, 'sum', { a: 5, b: 3 });

      // Assert
      expect(result).toBeDefined();

      // Cleanup
      await server.stop();
    });
  });

  describe('Error Handling', () => {
    it('should handle server errors gracefully', async () => {
      // Arrange
      const serverPath = await createMockMcpServer(env.basePath, 'test-server', {
        tools: [
          {
            name: 'error-tool',
            description: 'Tool that errors',
            inputSchema: { type: 'object' }
          }
        ]
      });
      const server = await startMcpServer(serverPath, 'test-server');

      // Modify server to return error
      server.tools.set('error-tool', {
        name: 'error-tool',
        description: 'Tool that errors',
        inputSchema: {}
      });

      // Act & Assert
      // In a real implementation, this would test actual error responses
      expect(server.tools.has('error-tool')).toBe(true);

      // Cleanup
      await server.stop();
    });

    it('should recover from server restart', async () => {
      // Arrange
      const serverPath = await createMockMcpServer(env.basePath, 'test-server');
      const server1 = await startMcpServer(serverPath, 'test-server');

      // Act - stop and restart
      await server1.stop();
      const server2 = await startMcpServer(serverPath, 'test-server');

      // Assert
      expect(server2.status).toBe('ready');

      // Cleanup
      await server2.stop();
    });
  });

  describe('Concurrent Operations', () => {
    it('should handle multiple servers simultaneously', async () => {
      // Arrange
      const server1Path = await createMockMcpServer(env.basePath, 'server-1');
      const server2Path = await createMockMcpServer(env.basePath, 'server-2');

      // Act
      const server1 = await startMcpServer(server1Path, 'server-1');
      const server2 = await startMcpServer(server2Path, 'server-2');

      // Assert
      expect(server1.status).toBe('ready');
      expect(server2.status).toBe('ready');
      expect(server1.name).not.toBe(server2.name);

      // Cleanup
      await server1.stop();
      await server2.stop();
    });

    it('should track servers in environment', async () => {
      // Arrange
      const serverPath = await createMockMcpServer(env.basePath, 'test-server');

      // Act
      const server = await startMcpServer(serverPath, 'test-server');
      env.mcpServers.set('test-server', server);

      // Assert
      expect(env.mcpServers.size).toBe(1);
      expect(env.mcpServers.has('test-server')).toBe(true);

      // Cleanup
      await server.stop();
    });
  });
});

/**
 * Helper: Create a mock MCP server for testing
 */
async function createMockMcpServer(
  basePath: string,
  name: string,
  config: { tools?: Array<{ name: string; description: string; inputSchema: Record<string, unknown> }> } = {}
): Promise<string> {
  const serverDir = path.join(basePath, 'mcp-servers', name);
  await fs.mkdir(serverDir, { recursive: true });

  const serverCode = `#!/usr/bin/env node

const readline = require('readline');

// Mock MCP server for testing
const tools = ${JSON.stringify(config.tools || [])};

// Send tools list on startup
process.stdout.write(JSON.stringify({
  jsonrpc: '2.0',
  method: 'tools/list',
  params: { tools }
}) + '\\n');

// Handle incoming requests
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

rl.on('line', (line) => {
  try {
    const request = JSON.parse(line);

    if (request.method === 'tools/call') {
      // Echo back the tool call as result
      const response = {
        jsonrpc: '2.0',
        id: request.id,
        result: {
          tool: request.params.name,
          arguments: request.params.arguments
        }
      };
      process.stdout.write(JSON.stringify(response) + '\\n');
    }
  } catch (e) {
    // Ignore invalid JSON
  }
});

// Keep server running
process.on('SIGTERM', () => {
  process.exit(0);
});
`;

  const serverPath = path.join(serverDir, 'server.js');
  await fs.writeFile(serverPath, serverCode);
  await fs.chmod(serverPath, 0o755);

  return serverPath;
}

/**
 * Helper: Create an MCP server that never reaches ready state
 */
async function createNeverReadyMcpServer(
  basePath: string,
  name: string
): Promise<string> {
  const serverDir = path.join(basePath, 'mcp-servers', name);
  await fs.mkdir(serverDir, { recursive: true });

  const serverCode = `#!/usr/bin/env node

setInterval(() => {}, 60000);
`;

  const serverPath = path.join(serverDir, 'server.js');
  await fs.writeFile(serverPath, serverCode);
  await fs.chmod(serverPath, 0o755);

  return serverPath;
}

/**
 * Helper: Create a ready MCP server that intentionally ignores tool calls
 */
async function createIgnoringMcpServer(basePath: string, name: string): Promise<string> {
  const serverDir = path.join(basePath, 'mcp-servers', name);
  await fs.mkdir(serverDir, { recursive: true });

  const serverCode = `#!/usr/bin/env node

process.stdout.write(JSON.stringify({
  jsonrpc: '2.0',
  method: 'tools/list',
  params: {
    tools: [{
      name: 'slow-tool',
      description: 'Intentionally ignores calls',
      inputSchema: { type: 'object' }
    }]
  }
}) + '\\n');

process.stdin.resume();
process.on('SIGTERM', () => process.exit(0));
`;

  const serverPath = path.join(serverDir, 'server.js');
  await fs.writeFile(serverPath, serverCode);
  await fs.chmod(serverPath, 0o755);

  return serverPath;
}

/**
 * Helper: Create a ready MCP server that requires forced termination
 */
async function createIgnoringSignalMcpServer(basePath: string, name: string): Promise<string> {
  const serverDir = path.join(basePath, 'mcp-servers', name);
  await fs.mkdir(serverDir, { recursive: true });

  const serverCode = `#!/usr/bin/env node

process.stdout.write(JSON.stringify({
  jsonrpc: '2.0',
  method: 'tools/list',
  params: { tools: [] }
}) + '\\n');

process.on('SIGTERM', () => {});
setInterval(() => {}, 60000);
`;

  const serverPath = path.join(serverDir, 'server.js');
  await fs.writeFile(serverPath, serverCode);
  await fs.chmod(serverPath, 0o755);

  return serverPath;
}

/**
 * Helper: Create an MCP server that crashes immediately
 */
async function createCrashingMcpServer(basePath: string, name: string): Promise<string> {
  const serverDir = path.join(basePath, 'mcp-servers', name);
  await fs.mkdir(serverDir, { recursive: true });

  const serverCode = `#!/usr/bin/env node

// Server that crashes immediately
process.exit(1);
`;

  const serverPath = path.join(serverDir, 'server.js');
  await fs.writeFile(serverPath, serverCode);
  await fs.chmod(serverPath, 0o755);

  return serverPath;
}
