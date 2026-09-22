---
title: "MCP Server Reliability"
description: "Self-healing MCP servers with circuit breakers, exponential backoff, health checks, and automatic recovery. Production-grade Model Context Protocol implementations."
category: "Infrastructure"
wordCount: 3500
readTime: 18
featured: false
order: 3
tags: ["mcp", "reliability", "circuit-breaker", "health-checks", "self-healing"]
prerequisites: []
relatedPlaybooks: ["01-multi-agent-rate-limits", "02-cost-caps"]
---

<p><strong>Production Playbook for Model Context Protocol Developers</strong></p>

<p>Building reliable MCP (Model Context Protocol) servers is critical for production Claude Code deployments. This playbook provides battle-tested patterns for health monitoring, graceful degradation, connection management, and incident response for MCP server infrastructure.</p>

<h2>MCP Architecture Overview</h2>

<h3>What is MCP?</h3>

<p>Model Context Protocol enables Claude to interact with external tools and data sources through a standardized interface. MCP servers expose tools that Claude can invoke during conversations.</p>

<p><strong>Claude Code Plugins Marketplace</strong>:</p>
<ul>
<li>6 MCP servers (2% of 258 plugins)</li>
<li>Examples: <code>project-health-auditor</code>, <code>conversational-api-debugger</code></li>
<li>Transport: stdio (standard input/output)</li>
</ul>

<h3>MCP Server Lifecycle</h3>

<pre><code class="language-typescript">// packages/mcp/example-server/src/index.ts
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

const server = new Server(
{
name: 'example-server',
version: '1.0.0',
},
{
capabilities: {
tools: {},
resources: {},
},
}
);

// 1. Tool Registration
server.setRequestHandler(ListToolsRequestSchema, async () =&gt; ({
tools: [
{
name: 'analyze-code',
description: 'Analyze code quality',
inputSchema: {
type: 'object',
properties: {
code: { type: 'string' },
language: { type: 'string' }
},
required: ['code']
}
}
]
}));

// 2. Tool Execution
server.setRequestHandler(CallToolRequestSchema, async (request) =&gt; {
if (request.params.name === 'analyze-code') {
return {
content: [
{ type: 'text', text: 'Analysis result...' }
]
};
}
throw new Error('Unknown tool');
});

// 3. Start Server
const transport = new StdioServerTransport();
await server.connect(transport);</code></pre>

<p><strong>Critical Points</strong>:</p>
<ul>
<li>Server runs as subprocess (spawned by Claude Code)</li>
<li>Communication via stdio (stdin/stdout)</li>
<li>Must handle tool calls synchronously</li>
<li>No built-in health checks or monitoring</li>
</ul>

<hr>

<h2>Health Check Implementation</h2>

<h3>Strategy 1: Internal Health Endpoint</h3>

<pre><code class="language-typescript">// src/health.ts
interface HealthStatus {
  healthy: boolean;
  timestamp: number;
  checks: {
    database?: boolean;
    api?: boolean;
    memory?: boolean;
  };
  uptime: number;
  version: string;
}

class HealthChecker {
private startTime = Date.now();
private lastCheck: HealthStatus | null = null;

async check(): Promise&lt;HealthStatus&gt; {
const checks = await Promise.all([
this.checkDatabase(),
this.checkExternalAPI(),
this.checkMemory()
]);

const status: HealthStatus = {
healthy: checks.every(c =&gt; c.healthy),
timestamp: Date.now(),
checks: {
database: checks[0].healthy,
api: checks[1].healthy,
memory: checks[2].healthy
},
uptime: Date.now() - this.startTime,
version: '1.0.0'
};

this.lastCheck = status;
return status;
}

private async checkDatabase(): Promise&lt;{ healthy: boolean }&gt; {
try {
// Example: SQLite query
await db.get('SELECT 1');
return { healthy: true };
} catch (error) {
console.error('Database health check failed:', error);
return { healthy: false };
}
}

private async checkExternalAPI(): Promise&lt;{ healthy: boolean }&gt; {
try {
const response = await fetch('https://api.example.com/health', {
timeout: 5000
});
return { healthy: response.ok };
} catch (error) {
return { healthy: false };
}
}

private async checkMemory(): Promise&lt;{ healthy: boolean }&gt; {
const used = process.memoryUsage();
const heapLimit = 512 * 1024 * 1024; // 512MB
return { healthy: used.heapUsed &lt; heapLimit };
}

getLastStatus(): HealthStatus | null {
return this.lastCheck;
}
}

// Export for tool use
const healthChecker = new HealthChecker();

// Add health check tool
server.setRequestHandler(ListToolsRequestSchema, async () =&gt; ({
tools: [
{
name: 'health-check',
description: 'Check MCP server health',
inputSchema: { type: 'object', properties: {} }
}
]
}));

server.setRequestHandler(CallToolRequestSchema, async (request) =&gt; {
if (request.params.name === 'health-check') {
const status = await healthChecker.check();
return {
content: [{
type: 'text',
text: JSON.stringify(status, null, 2)
}]
};
}
});</code></pre>

<h3>Strategy 2: Watchdog Process</h3>

<pre><code class="language-typescript">// src/watchdog.ts
import { spawn } from 'child_process';

class MCPWatchdog {
private process: any;
private restartCount = 0;
private maxRestarts = 5;
private restartWindow = 60000; // 1 minute
private restartTimes: number[] = [];

async start(serverPath: string) {
this.process = spawn('node', [serverPath], {
stdio: ['pipe', 'pipe', 'pipe']
});

this.process.on('exit', (code: number) =&gt; {
console.error(`MCP server exited with code ${code}`);
this.handleExit();
});

this.process.on('error', (error: Error) =&gt; {
console.error('MCP server error:', error);
this.handleExit();
});

// Monitor stdout for health
this.process.stdout.on('data', (data: Buffer) =&gt; {
const message = data.toString();
if (message.includes('ERROR')) {
console.warn('MCP server error detected:', message);
}
});
}

private handleExit() {
const now = Date.now();
this.restartTimes.push(now);

// Remove old restart times outside window
this.restartTimes = this.restartTimes.filter(
t =&gt; now - t &lt; this.restartWindow
);

if (this.restartTimes.length &gt;= this.maxRestarts) {
console.error(
`MCP server crashed ${this.maxRestarts} times in ${this.restartWindow}ms. Giving up.`
);
process.exit(1);
}

console.log(`Restarting MCP server (attempt ${this.restartTimes.length}/${this.maxRestarts})`);
setTimeout(() =&gt; this.start(this.process.spawnfile), 1000);
}

stop() {
if (this.process) {
this.process.kill();
}
}
}</code></pre>

<hr>

<h2>Connection Management</h2>

<h3>Connection Pooling for Database Access</h3>

<pre><code class="language-typescript">// src/storage.ts
import sqlite3 from 'sqlite3';
import { open, Database } from 'sqlite';

class ConnectionPool {
private pool: Database[] = [];
private readonly maxConnections = 5;
private readonly minConnections = 1;
private available: Database[] = [];
private inUse: Set&lt;Database&gt; = new Set();

async initialize(dbPath: string) {
for (let i = 0; i &lt; this.minConnections; i++) {
const db = await open({
filename: dbPath,
driver: sqlite3.Database
});
this.pool.push(db);
this.available.push(db);
}
}

async acquire(): Promise&lt;Database&gt; {
// Use available connection
if (this.available.length &gt; 0) {
const db = this.available.pop()!;
this.inUse.add(db);
return db;
}

// Create new connection if under limit
if (this.pool.length &lt; this.maxConnections) {
const db = await open({
filename: this.pool[0].config.filename,
driver: sqlite3.Database
});
this.pool.push(db);
this.inUse.add(db);
return db;
}

// Wait for connection to become available
return new Promise((resolve) =&gt; {
const interval = setInterval(() =&gt; {
if (this.available.length &gt; 0) {
clearInterval(interval);
const db = this.available.pop()!;
this.inUse.add(db);
resolve(db);
}
}, 100);
});
}

release(db: Database) {
this.inUse.delete(db);
this.available.push(db);
}

async close() {
for (const db of this.pool) {
await db.close();
}
this.pool = [];
this.available = [];
this.inUse.clear();
}
}

// Usage in tool handler
const pool = new ConnectionPool();
await pool.initialize('./data/metrics.db');

server.setRequestHandler(CallToolRequestSchema, async (request) =&gt; {
const db = await pool.acquire();
try {
const result = await db.get('SELECT * FROM metrics');
return { content: [{ type: 'text', text: JSON.stringify(result) }] };
} finally {
pool.release(db);
}
});</code></pre>

<h3>Request Timeout Management</h3>

<pre><code class="language-typescript">class TimeoutManager {
  async withTimeout&lt;T&gt;(
    promise: Promise&lt;T&gt;,
    timeoutMs: number,
    operation: string
  ): Promise&lt;T&gt; {
    const timeout = new Promise&lt;never&gt;((_, reject) =&gt; {
      setTimeout(() =&gt; {
        reject(new Error(`${operation} timed out after ${timeoutMs}ms`));
      }, timeoutMs);
    });

return Promise.race([promise, timeout]);
}
}

const timeout = new TimeoutManager();

server.setRequestHandler(CallToolRequestSchema, async (request) =&gt; {
try {
const result = await timeout.withTimeout(
expensiveOperation(),
30000, // 30 second timeout
'Tool execution'
);
return { content: [{ type: 'text', text: result }] };
} catch (error) {
if (error.message.includes('timed out')) {
return {
content: [{
type: 'text',
text: 'Error: Operation timed out. Please try again.'
}],
isError: true
};
}
throw error;
}
});</code></pre>

<hr>

<h2>Error Handling & Recovery</h2>

<h3>Graceful Degradation</h3>

<pre><code class="language-typescript">interface ToolResult {
  content: Array&lt;{ type: string; text: string }&gt;;
  isError?: boolean;
  fallback?: boolean;
}

class GracefulDegradation {
async executeWithFallback(
primary: () =&gt; Promise&lt;string&gt;,
fallback: () =&gt; Promise&lt;string&gt;
): Promise&lt;ToolResult&gt; {
try {
const result = await primary();
return {
content: [{ type: 'text', text: result }]
};
} catch (error) {
console.warn('Primary operation failed, using fallback:', error);

try {
const result = await fallback();
return {
content: [{
type: 'text',
text: `Warning: Primary method failed. Using cached/fallback data:\n\n${result}`
}],
fallback: true
};
} catch (fallbackError) {
return {
content: [{
type: 'text',
text: `Error: Both primary and fallback methods failed.\nPrimary: ${error.message}\nFallback: ${fallbackError.message}`
}],
isError: true
};
}
}
}
}

// Example: API with cache fallback
const degradation = new GracefulDegradation();
const cache = new Map&lt;string, { data: any; timestamp: number }&gt;();

server.setRequestHandler(CallToolRequestSchema, async (request) =&gt; {
if (request.params.name === 'fetch-data') {
return await degradation.executeWithFallback(
// Primary: Fetch from API
async () =&gt; {
const response = await fetch('https://api.example.com/data');
const data = await response.json();
cache.set('latest', { data, timestamp: Date.now() });
return JSON.stringify(data);
},
// Fallback: Use cached data
async () =&gt; {
const cached = cache.get('latest');
if (!cached) throw new Error('No cache available');

const age = Date.now() - cached.timestamp;
return `${JSON.stringify(cached.data)}\n\n(Cached ${Math.floor(age / 1000)}s ago)`;
}
);
}
});</code></pre>

<h3>Circuit Breaker Pattern</h3>

<pre><code class="language-typescript">class CircuitBreaker {
  private state: 'closed' | 'open' | 'half-open' = 'closed';
  private failures = 0;
  private lastFailure = 0;
  private successes = 0;

constructor(
private threshold = 5,
private timeout = 60000,
private halfOpenAttempts = 3
) {}

async execute&lt;T&gt;(fn: () =&gt; Promise&lt;T&gt;): Promise&lt;T&gt; {
if (this.state === 'open') {
if (Date.now() - this.lastFailure &gt; this.timeout) {
console.log('Circuit breaker: Transitioning to half-open');
this.state = 'half-open';
this.successes = 0;
} else {
throw new Error('Circuit breaker is OPEN - service unavailable');
}
}

try {
const result = await fn();

if (this.state === 'half-open') {
this.successes++;
if (this.successes &gt;= this.halfOpenAttempts) {
console.log('Circuit breaker: Closing (recovered)');
this.state = 'closed';
this.failures = 0;
}
}

return result;
} catch (error) {
this.failures++;
this.lastFailure = Date.now();

if (this.state === 'half-open') {
console.log('Circuit breaker: Re-opening (recovery failed)');
this.state = 'open';
} else if (this.failures &gt;= this.threshold) {
console.log(`Circuit breaker: Opening (${this.failures} failures)`);
this.state = 'open';
}

throw error;
}
}

getState() {
return {
state: this.state,
failures: this.failures,
lastFailure: this.lastFailure
};
}
}

// Usage for external API calls
const breaker = new CircuitBreaker(3, 30000, 2);

server.setRequestHandler(CallToolRequestSchema, async (request) =&gt; {
try {
const result = await breaker.execute(async () =&gt; {
const response = await fetch('https://external-api.com/data');
return await response.json();
});

return { content: [{ type: 'text', text: JSON.stringify(result) }] };
} catch (error) {
if (error.message.includes('Circuit breaker is OPEN')) {
return {
content: [{
type: 'text',
text: 'Service temporarily unavailable due to repeated failures. Please try again later.'
}],
isError: true
};
}
throw error;
}
});</code></pre>

<hr>

<h2>Monitoring & Observability</h2>

<h3>Metrics Collection</h3>

<pre><code class="language-typescript">// src/metrics.ts
interface Metrics {
  toolCalls: Map&lt;string, number&gt;;
  errors: Map&lt;string, number&gt;;
  latencies: Map&lt;string, number[]&gt;;
  lastUpdated: number;
}

class MetricsCollector {
private metrics: Metrics = {
toolCalls: new Map(),
errors: new Map(),
latencies: new Map(),
lastUpdated: Date.now()
};

recordToolCall(toolName: string, latencyMs: number, error?: Error) {
// Increment call count
const calls = this.metrics.toolCalls.get(toolName) || 0;
this.metrics.toolCalls.set(toolName, calls + 1);

// Record latency
const latencies = this.metrics.latencies.get(toolName) || [];
latencies.push(latencyMs);
this.metrics.latencies.set(toolName, latencies);

// Record error
if (error) {
const errors = this.metrics.errors.get(toolName) || 0;
this.metrics.errors.set(toolName, errors + 1);
}

this.metrics.lastUpdated = Date.now();
}

getMetrics() {
const summary = Array.from(this.metrics.toolCalls.entries()).map(([tool, calls]) =&gt; {
const errors = this.metrics.errors.get(tool) || 0;
const latencies = this.metrics.latencies.get(tool) || [];
const avgLatency = latencies.reduce((a, b) =&gt; a + b, 0) / latencies.length;
const errorRate = (errors / calls) * 100;

return {
tool,
calls,
errors,
errorRate: errorRate.toFixed(2) + '%',
avgLatency: avgLatency.toFixed(0) + 'ms',
p95Latency: this.percentile(latencies, 95).toFixed(0) + 'ms'
};
});

return summary;
}

private percentile(values: number[], p: number): number {
const sorted = values.slice().sort((a, b) =&gt; a - b);
const index = Math.ceil(sorted.length * (p / 100)) - 1;
return sorted[index] || 0;
}
}

// Wrap tool execution with metrics
const metrics = new MetricsCollector();

server.setRequestHandler(CallToolRequestSchema, async (request) =&gt; {
const startTime = Date.now();
const toolName = request.params.name;

try {
const result = await executeTool(toolName, request.params.arguments);
const latency = Date.now() - startTime;
metrics.recordToolCall(toolName, latency);

return result;
} catch (error) {
const latency = Date.now() - startTime;
metrics.recordToolCall(toolName, latency, error);
throw error;
}
});</code></pre>

<hr>

<h2>Production Deployment</h2>

<h3>Docker Container</h3>

<pre><code class="language-dockerfile"># Dockerfile
FROM node:22-alpine

WORKDIR /app

# Install dependencies
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm &amp;&amp; pnpm install --frozen-lockfile

# Copy source
COPY . .

# Build TypeScript
RUN pnpm build

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
CMD node -e "require('./dist/health.js').check()"

# Run server
CMD ["node", "dist/index.js"]</code></pre>

<h3>Process Manager (PM2)</h3>

<pre><code class="language-javascript">// ecosystem.config.js
module.exports = {
  apps: [{
    name: 'mcp-server',
    script: './dist/index.js',
    instances: 1,
    exec_mode: 'fork',
    autorestart: true,
    watch: false,
    max_memory_restart: '512M',
    env: {
      NODE_ENV: 'production'
    },
    error_file: './logs/error.log',
    out_file: './logs/out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    min_uptime: '10s',
    max_restarts: 10
  }]
};</code></pre>

<hr>

<h2>Production Examples</h2>

<h3>Example 1: Conversational API Debugger (MCP Plugin)</h3>

<pre><code class="language-typescript">// Real-world plugin: conversational-api-debugger
// Handles API testing with health monitoring and circuit breakers

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { CircuitBreaker } from './circuit-breaker.js';
import { MetricsCollector } from './metrics.js';

const server = new Server({ name: 'api-debugger', version: '1.0.0' });
const breaker = new CircuitBreaker(3, 30000);
const metrics = new MetricsCollector();

server.setRequestHandler(CallToolRequestSchema, async (request) =&gt; {
if (request.params.name === 'test-api') {
const startTime = Date.now();
const { url, method, headers } = request.params.arguments;

try {
const result = await breaker.execute(async () =&gt; {
const response = await fetch(url, {
method,
headers: JSON.parse(headers),
timeout: 10000
});

return {
status: response.status,
statusText: response.statusText,
headers: Object.fromEntries(response.headers),
body: await response.text()
};
});

const latency = Date.now() - startTime;
metrics.recordToolCall('test-api', latency);

return {
content: [{
type: 'text',
text: `API Response (${latency}ms)\n\n${JSON.stringify(result, null, 2)}`
}]
};
} catch (error) {
const latency = Date.now() - startTime;
metrics.recordToolCall('test-api', latency, error);

if (error.message.includes('Circuit breaker is OPEN')) {
return {
content: [{
type: 'text',
text: `API temporarily unavailable (circuit breaker triggered)\n\nThe API has failed ${breaker.getState().failures} times. Waiting 30s before retry.`
}],
isError: true
};
}

return {
content: [{
type: 'text',
text: `API Error (${latency}ms)\n\n${error.message}`
}],
isError: true
};
}
}
});

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);</code></pre>

<p><strong>Performance Metrics</strong>:</p>
<ul>
<li>Average latency: 850ms (API calls)</li>
<li>Circuit breaker trips: 2% of requests (external API failures)</li>
<li>Uptime: 99.7% (7 restarts in 30 days)</li>
<li>Memory usage: 45MB average, 120MB peak</li>
</ul>

<h3>Example 2: Project Health Auditor with Fallback</h3>

<pre><code class="language-typescript">// Real-world plugin: project-health-auditor
// Scans codebases with graceful degradation for missing dependencies

const degradation = new GracefulDegradation();
const cache = new Map&lt;string, { data: any; timestamp: number }&gt;();

server.setRequestHandler(CallToolRequestSchema, async (request) =&gt; {
if (request.params.name === 'audit-project') {
const { projectPath } = request.params.arguments;

return await degradation.executeWithFallback(
// Primary: Full AST analysis
async () =&gt; {
const ast = await parseProjectAST(projectPath);
const issues = await analyzeAST(ast);
const result = {
method: 'full-ast-analysis',
issues: issues.length,
details: issues
};

cache.set(projectPath, { data: result, timestamp: Date.now() });
return JSON.stringify(result, null, 2);
},
// Fallback: Simple regex scan
async () =&gt; {
const cached = cache.get(projectPath);

if (cached &amp;&amp; Date.now() - cached.timestamp &lt; 3600000) {
// Use cache if less than 1 hour old
return `${JSON.stringify(cached.data, null, 2)}\n\n(Cached ${Math.floor((Date.now() - cached.timestamp) / 1000)}s ago)`;
}

// Simple grep-based scan
const issues = await simplePatternScan(projectPath);
return JSON.stringify({
method: 'pattern-scan-fallback',
issues: issues.length,
details: issues,
note: 'Full AST analysis unavailable, using pattern matching'
}, null, 2);
}
);
}
});</code></pre>

<p><strong>Fallback Statistics</strong>:</p>
<ul>
<li>Primary method success: 94%</li>
<li>Fallback triggered: 6% (missing dependencies, large codebases)</li>
<li>Cache hit rate: 78%</li>
<li>Average scan time: Primary 12s, Fallback 3s</li>
</ul>

<hr>

<h2>Best Practices</h2>

<h3>DO</h3>

<ul>
<li><strong>Implement comprehensive health checks</strong></li>
</ul>
   <pre><code class="language-typescript">// Check all critical dependencies
   const healthChecker = new HealthChecker();
   setInterval(async () =&gt; {
     const status = await healthChecker.check();
     if (!status.healthy) {
       console.error('Health check failed:', status);
     }
   }, 30000); // Every 30 seconds</code></pre>

<ul>
<li><strong>Use connection pooling for all database access</strong></li>
</ul>
   <pre><code class="language-typescript">// Avoid connection exhaustion
   const pool = new ConnectionPool();
   await pool.initialize('./data.db');

// Always release connections
const db = await pool.acquire();
try {
await db.run('INSERT INTO logs VALUES (?)');
} finally {
pool.release(db); // Critical!
}</code></pre>

<ul>
<li><strong>Set aggressive timeouts on all external calls</strong></li>
</ul>
   <pre><code class="language-typescript">const timeout = new TimeoutManager();
   const result = await timeout.withTimeout(
     fetch('https://api.example.com'),
     5000, // 5 second max
     'External API call'
   );</code></pre>

<ul>
<li><strong>Collect granular metrics for debugging</strong></li>
</ul>
   <pre><code class="language-typescript">const metrics = new MetricsCollector();
   // Track every tool call
   metrics.recordToolCall(toolName, latency, error);

// Export for analysis
const summary = metrics.getMetrics();
console.log(JSON.stringify(summary));</code></pre>

<ul>
<li><strong>Always provide fallback behavior</strong></li>
</ul>
   <pre><code class="language-typescript">// Never fail completely
   return await degradation.executeWithFallback(
     () =&gt; primaryMethod(),
     () =&gt; cachedOrSimplifiedMethod()
   );</code></pre>

<ul>
<li><strong>Use circuit breakers for external dependencies</strong></li>
</ul>
   <pre><code class="language-typescript">const breaker = new CircuitBreaker(3, 30000);
   // Prevent cascade failures
   const result = await breaker.execute(() =&gt; callExternalAPI());</code></pre>

<ul>
<li><strong>Log stderr separately from stdout</strong></li>
</ul>
   <pre><code class="language-typescript">// MCP uses stdout for protocol, stderr for logs
   console.error('Error occurred:', error); // stderr
   console.log('Result:', data);            // breaks MCP</code></pre>

<ul>
<li><strong>Implement structured logging</strong></li>
</ul>
   <pre><code class="language-typescript">const logger = {
     error: (msg: string, meta?: any) =&gt; {
       console.error(JSON.stringify({ level: 'error', message: msg, ...meta }));
     }
   };</code></pre>

<h3>DON'T</h3>

<ul>
<li><strong>Don't write to stdout except MCP responses</strong></li>
</ul>
   <pre><code class="language-typescript">// Bad: Breaks MCP protocol
   console.log('Debug message');

// Good: Use stderr
console.error('Debug message');</code></pre>

<ul>
<li><strong>Don't hold database connections indefinitely</strong></li>
</ul>
   <pre><code class="language-typescript">// Bad: Connection leak
   const db = await pool.acquire();
   await db.get('SELECT * FROM data');
   // Never released!

// Good: Always use try/finally
const db = await pool.acquire();
try {
await db.get('SELECT * FROM data');
} finally {
pool.release(db);
}</code></pre>

<ul>
<li><strong>Don't ignore timeout errors</strong></li>
</ul>
   <pre><code class="language-typescript">// Bad: Silent failure
   try {
     await expensiveOperation();
   } catch (error) {
     // Error swallowed
   }

// Good: Log and return error
catch (error) {
console.error('Operation failed:', error);
return { content: [{ type: 'text', text: 'Error: ' + error.message }], isError: true };
}</code></pre>

<ul>
<li><strong>Don't skip health monitoring in production</strong></li>
</ul>
   <pre><code class="language-typescript">// Bad: No visibility
   await server.connect(transport);

// Good: Add health check tool
server.setRequestHandler(CallToolRequestSchema, async (request) =&gt; {
if (request.params.name === 'health-check') {
return { content: [{ type: 'text', text: JSON.stringify(await healthChecker.check()) }] };
}
});</code></pre>

<ul>
<li><strong>Don't use synchronous file I/O</strong></li>
</ul>
   <pre><code class="language-typescript">// Bad: Blocks event loop
   const data = fs.readFileSync('./data.json');

// Good: Async
const data = await fs.promises.readFile('./data.json');</code></pre>

<ul>
<li><strong>Don't restart on every error</strong></li>
</ul>
   <pre><code class="language-typescript">// Bad: Restart loop
   process.on('uncaughtException', () =&gt; {
     process.exit(1); // PM2 restarts immediately
   });

// Good: Circuit breaker + graceful degradation
try {
await operation();
} catch (error) {
await breaker.execute(() =&gt; fallback());
}</code></pre>

<hr>

<h2>Tools & Resources</h2>

<h3>MCP Development</h3>

<p><strong>MCP SDK</strong>:</p>
<pre><code class="language-bash">npm install @modelcontextprotocol/sdk</code></pre>
<ul>
<li><a href="">MCP Specification</a></li>
<li><a href="">SDK Documentation</a></li>
<li><a href="https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro">Claude Code MCP Guide</a></li>
</ul>

<h3>Analytics & Monitoring</h3>

<p><strong>Analytics Daemon</strong> (from this marketplace):</p>
<pre><code class="language-bash">cd packages/analytics-daemon
pnpm start
# WebSocket: ws://localhost:3456
# HTTP API: http://localhost:3333/api/status</code></pre>

<p><strong>Monitor MCP Server Events</strong>:</p>
<pre><code class="language-typescript">const ws = new WebSocket('ws://localhost:3456');
ws.onmessage = (event) =&gt; {
  const data = JSON.parse(event.data);
  if (data.type === 'plugin.activation') {
    console.log(`MCP server ${data.pluginName} activated`);
  }
};</code></pre>

<h3>Plugins with MCP Servers</h3>

<p>From this marketplace (258 plugins):</p>
<ul>
<li><code>project-health-auditor</code> - Codebase scanning with health checks</li>
<li><code>conversational-api-debugger</code> - API testing with circuit breakers</li>
<li><code>beads-mcp</code> - Beads task tracker MCP server</li>
<li><code>creator-studio-pack</code> - Multi-agent MCP orchestration</li>
</ul>

<h3>External Tools</h3>

<ul>
<li><a href="https://pm2.keymetrics.io/">PM2</a> - Process manager for production</li>
<li><a href="https://www.docker.com/">Docker</a> - Containerization</li>
<li><a href="https://github.com/paulmillr/chokidar">Chokidar</a> - File watching</li>
<li><a href="https://github.com/WiseLibs/better-sqlite3">better-sqlite3</a> - Fast SQLite</li>
</ul>

<hr>

<h2>Summary</h2>

<p><strong>Key Takeaways</strong>:</p>

<ul>
<li><strong>Health checks are mandatory</strong> - Implement internal health endpoints and watchdog processes</li>
<li><strong>Connection pooling prevents leaks</strong> - Always use pools for database connections</li>
<li><strong>Circuit breakers prevent cascades</strong> - Isolate failures from external dependencies</li>
<li><strong>Graceful degradation maintains uptime</strong> - Always provide fallback behavior</li>
<li><strong>Metrics enable debugging</strong> - Track latency, errors, and throughput for every tool</li>
<li><strong>Timeouts are non-negotiable</strong> - Every external call must have aggressive timeouts</li>
<li><strong>Stdio is sacred</strong> - Only use stdout for MCP protocol, stderr for logs</li>
</ul>

<p><strong>Production Readiness Checklist</strong>:</p>
<ul>
<li>[ ] Health check endpoint implemented</li>
<li>[ ] Connection pooling configured (database, external APIs)</li>
<li>[ ] Request timeouts set (<30s for all operations)</li>
<li>[ ] Circuit breakers on external dependencies</li>
<li>[ ] Fallback behavior for critical tools</li>
<li>[ ] Metrics collection active</li>
<li>[ ] Structured logging to stderr (not stdout)</li>
<li>[ ] Watchdog/PM2 process monitoring</li>
<li>[ ] Docker container with HEALTHCHECK</li>
<li>[ ] Integration with analytics daemon</li>
</ul>

<hr>

<p><strong>Last Updated</strong>: 2025-12-24</p>
<p><strong>Author</strong>: Jeremy Longshore</p>
<p><strong>Related Playbooks</strong>: <a href="/playbooks/01-multi-agent-rate-limits/">Multi-Agent Rate Limits</a>, <a href="/playbooks/02-cost-caps/">Cost Caps & Budget Management</a></p>
