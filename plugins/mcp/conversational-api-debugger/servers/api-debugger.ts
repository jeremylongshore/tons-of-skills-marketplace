#!/usr/bin/env node

/**
 * Conversational API Debugger MCP Server
 *
 * Helps debug REST API failures by analyzing OpenAPI specs and HTTP logs.
 * Provides tools to load API documentation, ingest logs, explain failures,
 * and generate reproducible test commands.
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool
} from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import { zodToJsonSchema } from 'zod-to-json-schema';
import { promises as fs } from 'fs';
import * as yaml from 'yaml';
import type { OpenAPIV3, OpenAPIV3_1 } from 'openapi-types';

// Type definitions
type OpenAPISpec = OpenAPIV3.Document | OpenAPIV3_1.Document;

interface HTTPLog {
  timestamp: string;
  method: string;
  url: string;
  statusCode: number;
  requestHeaders?: Record<string, string>;
  requestBody?: any;
  responseHeaders?: Record<string, string>;
  responseBody?: any;
  duration?: number;
  error?: string;
}

interface ParsedEndpoint {
  path: string;
  method: string;
  summary?: string;
  description?: string;
  parameters?: OpenAPIV3.ParameterObject[];
  requestBody?: OpenAPIV3.RequestBodyObject;
  responses?: OpenAPIV3.ResponsesObject;
  security?: OpenAPIV3.SecurityRequirementObject[];
}

interface FailureAnalysis {
  log: HTTPLog;
  possibleCauses: string[];
  suggestedFixes: string[];
  matchingEndpoint?: ParsedEndpoint;
  severity: 'critical' | 'high' | 'medium' | 'low';
}

// In-memory storage
const apiSpecs: Map<string, OpenAPISpec> = new Map();
const httpLogs: HTTPLog[] = [];

// ============================================================================
// Zod Schemas
// ============================================================================

const LoadOpenAPISchema = z.object({
  filePath: z.string().describe('Path to OpenAPI spec file (JSON or YAML)'),
  name: z.string().optional().describe('Name to reference this spec')
});

const IngestLogsSchema = z.object({
  filePath: z.string().optional().describe('Path to log file (HAR, JSON, text)'),
  logs: z.array(z.object({
    timestamp: z.string(),
    method: z.string(),
    url: z.string(),
    statusCode: z.number(),
    requestHeaders: z.record(z.string(), z.string()).optional(),
    requestBody: z.any().optional(),
    responseHeaders: z.record(z.string(), z.string()).optional(),
    responseBody: z.any().optional(),
    duration: z.number().optional(),
    error: z.string().optional()
  })).optional().describe('Array of log objects to ingest directly'),
  format: z.enum(['har', 'json', 'auto']).optional().default('auto')
});

const ExplainFailureSchema = z.object({
  logIndex: z.number().optional().describe('Index of log to analyze (from ingest_logs)'),
  log: z.object({
    timestamp: z.string(),
    method: z.string(),
    url: z.string(),
    statusCode: z.number(),
    requestHeaders: z.record(z.string(), z.string()).optional(),
    requestBody: z.any().optional(),
    responseHeaders: z.record(z.string(), z.string()).optional(),
    responseBody: z.any().optional(),
    error: z.string().optional()
  }).optional().describe('Log object to analyze directly'),
  specName: z.string().optional().describe('Name of OpenAPI spec to compare against')
});

const MakeReproSchema = z.object({
  logIndex: z.number().optional().describe('Index of log to convert to cURL'),
  log: z.object({
    method: z.string(),
    url: z.string(),
    requestHeaders: z.record(z.string(), z.string()).optional(),
    requestBody: z.any().optional()
  }).optional().describe('Log object to convert directly'),
  includeHeaders: z.boolean().optional().default(true),
  pretty: z.boolean().optional().default(true).describe('Format output for readability')
});

// ============================================================================
// OpenAPI Spec Loading
// ============================================================================

/**
 * Load and parse an OpenAPI specification file
 */
async function loadOpenAPI(args: z.infer<typeof LoadOpenAPISchema>) {
  const { filePath, name } = args;

  try {
    const content = await fs.readFile(filePath, 'utf-8');
    const fileName = name || filePath.split('/').pop() || 'unnamed';

    let spec: OpenAPISpec;

    // Try parsing as JSON first
    try {
      spec = JSON.parse(content);
    } catch {
      // If JSON fails, try YAML
      spec = yaml.parse(content);
    }

    // Validate it's an OpenAPI spec
    if (!spec.openapi && !('swagger' in spec)) {
      throw new Error('File does not appear to be an OpenAPI specification');
    }

    // Store the spec
    apiSpecs.set(fileName, spec);

    // Extract endpoint information
    const endpoints: ParsedEndpoint[] = [];
    if (spec.paths) {
      for (const [path, pathItem] of Object.entries(spec.paths)) {
        if (!pathItem) continue;
        const methods = ['get', 'post', 'put', 'patch', 'delete', 'options', 'head'] as const;

        for (const method of methods) {
          const operation = pathItem[method];
          if (operation) {
            endpoints.push({
              path,
              method: method.toUpperCase(),
              summary: operation.summary,
              description: operation.description,
              parameters: operation.parameters as OpenAPIV3.ParameterObject[],
              requestBody: operation.requestBody as OpenAPIV3.RequestBodyObject,
              responses: operation.responses,
              security: operation.security
            });
          }
        }
      }
    }

    return {
      name: fileName,
      version: spec.openapi || ('swagger' in spec ? (spec as any).swagger : 'unknown'),
      title: spec.info?.title,
      description: spec.info?.description,
      baseUrl: getBaseUrl(spec),
      endpoints: endpoints.length,
      endpointsList: endpoints.map(e => `${e.method} ${e.path}`),
      servers: spec.servers?.map(s => s.url) || [],
      loaded: true
    };
  } catch (error) {
    throw new Error(`Failed to load OpenAPI spec: ${error instanceof Error ? error.message : String(error)}`);
  }
}

/**
 * Extract base URL from OpenAPI spec
 */
function getBaseUrl(spec: OpenAPISpec): string {
  if (spec.servers && spec.servers.length > 0) {
    return spec.servers[0].url;
  }
  return '';
}

// ============================================================================
// HTTP Log Ingestion
// ============================================================================

/**
 * Ingest HTTP logs from file or array
 */
async function ingestLogs(args: z.infer<typeof IngestLogsSchema>) {
  const { filePath, logs: directLogs, format } = args;

  try {
    let parsedLogs: HTTPLog[] = [];

    if (directLogs) {
      // Use logs provided directly
      parsedLogs = directLogs;
    } else if (filePath) {
      // Load from file
      const content = await fs.readFile(filePath, 'utf-8');

      if (format === 'har' || (format === 'auto' && filePath.endsWith('.har'))) {
        // Parse HAR format
        const har = JSON.parse(content);
        parsedLogs = parseHAR(har);
      } else {
        // Parse as JSON array
        const jsonLogs = JSON.parse(content);
        parsedLogs = Array.isArray(jsonLogs) ? jsonLogs : [jsonLogs];
      }
    } else {
      throw new Error('Either filePath or logs must be provided');
    }

    // Add to in-memory storage
    const startIndex = httpLogs.length;
    httpLogs.push(...parsedLogs);

    // Analyze log patterns
    const statusCodes = new Map<number, number>();
    const methods = new Map<string, number>();
    const errors = parsedLogs.filter(log => log.statusCode >= 400);

    parsedLogs.forEach(log => {
      statusCodes.set(log.statusCode, (statusCodes.get(log.statusCode) || 0) + 1);
      methods.set(log.method, (methods.get(log.method) || 0) + 1);
    });

    return {
      ingested: parsedLogs.length,
      startIndex,
      endIndex: httpLogs.length - 1,
      summary: {
        totalRequests: parsedLogs.length,
        successfulRequests: parsedLogs.filter(log => log.statusCode >= 200 && log.statusCode < 300).length,
        failedRequests: errors.length,
        statusCodeDistribution: Object.fromEntries(statusCodes),
        methodDistribution: Object.fromEntries(methods)
      },
      errors: errors.map((log, idx) => ({
        index: startIndex + parsedLogs.indexOf(log),
        method: log.method,
        url: log.url,
        statusCode: log.statusCode,
        error: log.error
      })).slice(0, 10) // Show first 10 errors
    };
  } catch (error) {
    throw new Error(`Failed to ingest logs: ${error instanceof Error ? error.message : String(error)}`);
  }
}

/**
 * Parse HAR (HTTP Archive) format
 */
function parseHAR(har: any): HTTPLog[] {
  const logs: HTTPLog[] = [];

  if (!har.log || !har.log.entries) {
    return logs;
  }

  for (const entry of har.log.entries) {
    const request = entry.request;
    const response = entry.response;

    logs.push({
      timestamp: entry.startedDateTime,
      method: request.method,
      url: request.url,
      statusCode: response.status,
      requestHeaders: headersToObject(request.headers),
      requestBody: request.postData?.text ? tryParseJSON(request.postData.text) : undefined,
      responseHeaders: headersToObject(response.headers),
      responseBody: response.content?.text ? tryParseJSON(response.content.text) : undefined,
      duration: entry.time
    });
  }

  return logs;
}

/**
 * Convert HAR headers array to object
 */
function headersToObject(headers: any[]): Record<string, string> {
  const obj: Record<string, string> = {};
  if (Array.isArray(headers)) {
    headers.forEach(header => {
      obj[header.name] = header.value;
    });
  }
  return obj;
}

/**
 * Try parsing JSON, return original on failure
 */
function tryParseJSON(text: string): any {
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

// ============================================================================
// Failure Analysis
// ============================================================================

/**
 * Explain why an API call failed
 */
async function explainFailure(args: z.infer<typeof ExplainFailureSchema>) {
  const { logIndex, log: directLog, specName } = args;

  try {
    // Get the log to analyze
    let log: HTTPLog;
    if (directLog) {
      log = directLog as HTTPLog;
    } else if (logIndex !== undefined) {
      if (logIndex < 0 || logIndex >= httpLogs.length) {
        throw new Error(`Invalid log index: ${logIndex}. Available logs: 0-${httpLogs.length - 1}`);
      }
      log = httpLogs[logIndex];
    } else {
      throw new Error('Either logIndex or log must be provided');
    }

    // Find matching endpoint in OpenAPI spec
    let matchingEndpoint: ParsedEndpoint | undefined;
    if (specName && apiSpecs.has(specName)) {
      matchingEndpoint = findMatchingEndpoint(log, apiSpecs.get(specName)!);
    }

    // Analyze the failure
    const analysis: FailureAnalysis = analyzeFailure(log, matchingEndpoint);

    return {
      log: {
        method: log.method,
        url: log.url,
        statusCode: log.statusCode,
        timestamp: log.timestamp
      },
      severity: analysis.severity,
      possibleCauses: analysis.possibleCauses,
      suggestedFixes: analysis.suggestedFixes,
      matchingEndpoint: matchingEndpoint ? {
        path: matchingEndpoint.path,
        method: matchingEndpoint.method,
        summary: matchingEndpoint.summary,
        expectedStatus: Object.keys(matchingEndpoint.responses || {})
      } : undefined,
      details: {
        requestBody: log.requestBody,
        responseBody: log.responseBody,
        error: log.error
      }
    };
  } catch (error) {
    throw new Error(`Failed to explain failure: ${error instanceof Error ? error.message : String(error)}`);
  }
}

/**
 * Find matching endpoint in OpenAPI spec
 */
function findMatchingEndpoint(log: HTTPLog, spec: OpenAPISpec): ParsedEndpoint | undefined {
  if (!spec.paths) return undefined;

  const url = new URL(log.url, 'http://example.com');
  const pathname = url.pathname;

  for (const [path, pathItem] of Object.entries(spec.paths)) {
    if (!pathItem) continue;

    // Simple path matching (could be improved with path parameter matching)
    const pathRegex = new RegExp('^' + path.replace(/\{[^}]+\}/g, '[^/]+') + '$');
    if (pathRegex.test(pathname)) {
      const method = log.method.toLowerCase() as keyof typeof pathItem;
      const operation = pathItem[method];

      if (operation && typeof operation === 'object' && 'responses' in operation) {
        return {
          path,
          method: log.method,
          summary: operation.summary,
          description: operation.description,
          parameters: operation.parameters as OpenAPIV3.ParameterObject[],
          requestBody: operation.requestBody as OpenAPIV3.RequestBodyObject,
          responses: operation.responses,
          security: operation.security
        };
      }
    }
  }

  return undefined;
}

/**
 * Analyze why the API call failed
 */
function analyzeFailure(log: HTTPLog, endpoint?: ParsedEndpoint): FailureAnalysis {
  const possibleCauses: string[] = [];
  const suggestedFixes: string[] = [];
  let severity: 'critical' | 'high' | 'medium' | 'low' = 'medium';

  const statusCode = log.statusCode;

  // Status code analysis
  if (statusCode === 400) {
    possibleCauses.push('Bad Request - Invalid request syntax or parameters');
    suggestedFixes.push('Validate request body matches API schema');
    suggestedFixes.push('Check required parameters are present');
    severity = 'high';
  } else if (statusCode === 401) {
    possibleCauses.push('Unauthorized - Missing or invalid authentication');
    suggestedFixes.push('Check authentication token/credentials are valid');
    suggestedFixes.push('Ensure Authorization header is present');
    severity = 'high';
  } else if (statusCode === 403) {
    possibleCauses.push('Forbidden - Insufficient permissions');
    suggestedFixes.push('Verify user has necessary permissions');
    suggestedFixes.push('Check API key/token scopes');
    severity = 'high';
  } else if (statusCode === 404) {
    possibleCauses.push('Not Found - Endpoint or resource does not exist');
    suggestedFixes.push('Verify the URL path is correct');
    suggestedFixes.push('Check resource ID is valid');
    severity = 'medium';
  } else if (statusCode === 405) {
    possibleCauses.push('Method Not Allowed - HTTP method not supported');
    suggestedFixes.push('Check HTTP method (GET, POST, etc.) matches API spec');
    severity = 'medium';
  } else if (statusCode === 408) {
    possibleCauses.push('Request Timeout - Server did not receive complete request in time');
    suggestedFixes.push('Check network connectivity');
    suggestedFixes.push('Increase client timeout settings');
    severity = 'low';
  } else if (statusCode === 409) {
    possibleCauses.push('Conflict - Request conflicts with current state');
    suggestedFixes.push('Check for duplicate resources');
    suggestedFixes.push('Verify resource state before operation');
    severity = 'medium';
  } else if (statusCode === 422) {
    possibleCauses.push('Unprocessable Entity - Validation errors');
    suggestedFixes.push('Review validation errors in response body');
    suggestedFixes.push('Ensure data types match schema');
    severity = 'high';
  } else if (statusCode === 429) {
    possibleCauses.push('Too Many Requests - Rate limit exceeded');
    suggestedFixes.push('Implement rate limiting/backoff');
    suggestedFixes.push('Check rate limit headers (X-RateLimit-*)');
    severity = 'medium';
  } else if (statusCode === 500) {
    possibleCauses.push('Internal Server Error - Server-side issue');
    suggestedFixes.push('Check server logs');
    suggestedFixes.push('Retry with exponential backoff');
    severity = 'critical';
  } else if (statusCode === 502) {
    possibleCauses.push('Bad Gateway - Upstream server error');
    suggestedFixes.push('Check if API server is running');
    suggestedFixes.push('Verify network connectivity to upstream');
    severity = 'critical';
  } else if (statusCode === 503) {
    possibleCauses.push('Service Unavailable - Server temporarily unavailable');
    suggestedFixes.push('Wait and retry later');
    suggestedFixes.push('Check Retry-After header');
    severity = 'high';
  } else if (statusCode === 504) {
    possibleCauses.push('Gateway Timeout - Upstream server timeout');
    suggestedFixes.push('Increase timeout settings');
    suggestedFixes.push('Optimize slow operations on server');
    severity = 'high';
  }

  // Response body analysis
  if (log.responseBody) {
    if (typeof log.responseBody === 'object') {
      if ('error' in log.responseBody) {
        possibleCauses.push(`Server error message: ${log.responseBody.error}`);
      }
      if ('message' in log.responseBody) {
        possibleCauses.push(`Server message: ${log.responseBody.message}`);
      }
      if ('errors' in log.responseBody && Array.isArray(log.responseBody.errors)) {
        possibleCauses.push(`Validation errors: ${log.responseBody.errors.join(', ')}`);
      }
    }
  }

  // OpenAPI spec comparison
  if (endpoint) {
    // Check if status code is expected
    const expectedStatuses = Object.keys(endpoint.responses || {});
    if (!expectedStatuses.includes(String(statusCode))) {
      possibleCauses.push(`Unexpected status code (expected: ${expectedStatuses.join(', ')})`);
    }

    // Check for missing required parameters
    const requiredParams = endpoint.parameters?.filter(p => p.required) || [];
    if (requiredParams.length > 0) {
      suggestedFixes.push(`Ensure required parameters are present: ${requiredParams.map(p => p.name).join(', ')}`);
    }

    // Check for missing request body
    if (endpoint.requestBody && 'required' in endpoint.requestBody && endpoint.requestBody.required) {
      if (!log.requestBody) {
        possibleCauses.push('Missing required request body');
        suggestedFixes.push('Add request body matching schema');
      }
    }
  }

  return {
    log,
    possibleCauses,
    suggestedFixes,
    matchingEndpoint: endpoint,
    severity
  };
}

// ============================================================================
// cURL Generation
// ============================================================================

/**
 * Generate cURL command to reproduce API call
 */
async function makeRepro(args: z.infer<typeof MakeReproSchema>) {
  const { logIndex, log: directLog, includeHeaders, pretty } = args;

  try {
    // Get the log to convert
    let log: Partial<HTTPLog>;
    if (directLog) {
      log = directLog;
    } else if (logIndex !== undefined) {
      if (logIndex < 0 || logIndex >= httpLogs.length) {
        throw new Error(`Invalid log index: ${logIndex}. Available logs: 0-${httpLogs.length - 1}`);
      }
      log = httpLogs[logIndex];
    } else {
      throw new Error('Either logIndex or log must be provided');
    }

    // Build cURL command
    const parts: string[] = ['curl'];

    // Add method
    if (log.method && log.method !== 'GET') {
      parts.push(`-X ${log.method}`);
    }

    // Add headers
    if (includeHeaders && log.requestHeaders) {
      for (const [key, value] of Object.entries(log.requestHeaders)) {
        // Skip some headers that curl adds automatically
        if (!['host', 'content-length', 'connection'].includes(key.toLowerCase())) {
          parts.push(`-H "${key}: ${value}"`);
        }
      }
    }

    // Add body
    if (log.requestBody) {
      const body = typeof log.requestBody === 'string'
        ? log.requestBody
        : JSON.stringify(log.requestBody);
      // POSIX single-quoted strings have no escape character, so a bare
      // backslash before a quote does not escape it -- it terminates the
      // quoted string early and lets whatever follows be interpreted as
      // shell syntax. Close the quote, emit a literal quote, then reopen:
      // ' -> '\''
      parts.push(`-d '${body.replace(/'/g, "'\\''")}'`);
    }

    // Add URL (must be last)
    parts.push(`"${log.url}"`);

    // Format output
    const curl = pretty
      ? parts.join(' \\\n  ')
      : parts.join(' ');

    return {
      curl,
      method: log.method,
      url: log.url,
      hasBody: !!log.requestBody,
      headerCount: Object.keys(log.requestHeaders || {}).length,
      alternative: {
        httpie: generateHTTPie(log),
        javascript: generateJavaScript(log)
      }
    };
  } catch (error) {
    throw new Error(`Failed to generate cURL: ${error instanceof Error ? error.message : String(error)}`);
  }
}

/**
 * Generate HTTPie command as alternative
 */
function generateHTTPie(log: Partial<HTTPLog>): string {
  const parts: string[] = ['http'];

  // Method and URL
  if (log.method && log.method !== 'GET') {
    parts.push(log.method);
  }
  parts.push(log.url || '');

  // Headers
  if (log.requestHeaders) {
    for (const [key, value] of Object.entries(log.requestHeaders)) {
      parts.push(`${key}:"${value}"`);
    }
  }

  // Body (HTTPie auto-detects JSON)
  if (log.requestBody && typeof log.requestBody === 'object') {
    for (const [key, value] of Object.entries(log.requestBody)) {
      parts.push(`${key}="${value}"`);
    }
  }

  return parts.join(' ');
}

/**
 * Generate JavaScript fetch code
 */
function generateJavaScript(log: Partial<HTTPLog>): string {
  const options: any = {
    method: log.method || 'GET',
  };

  if (log.requestHeaders) {
    options.headers = log.requestHeaders;
  }

  if (log.requestBody) {
    options.body = typeof log.requestBody === 'string'
      ? log.requestBody
      : JSON.stringify(log.requestBody);
  }

  return `fetch("${log.url}", ${JSON.stringify(options, null, 2)})
  .then(res => res.json())
  .then(data => console.log(data))
  .catch(err => console.error(err));`;
}

// ============================================================================
// MCP Server Setup
// ============================================================================

const server = new Server(
  {
    name: 'api-debugger',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Define available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  const tools: Tool[] = [
    {
      name: 'load_openapi',
      description: 'Load and parse an OpenAPI specification file (JSON or YAML). Extracts endpoint definitions, parameters, and expected responses for comparison with actual API behavior.',
      inputSchema: zodToJsonSchema(LoadOpenAPISchema as any) as Tool['inputSchema']
    },
    {
      name: 'ingest_logs',
      description: 'Ingest HTTP request/response logs from file (HAR format) or direct array. Analyzes patterns, identifies errors, and prepares logs for failure analysis.',
      inputSchema: zodToJsonSchema(IngestLogsSchema as any) as Tool['inputSchema']
    },
    {
      name: 'explain_failure',
      description: 'Analyze why an API call failed. Compares actual behavior with OpenAPI spec (if loaded), identifies root causes, and suggests fixes. Provides severity assessment.',
      inputSchema: zodToJsonSchema(ExplainFailureSchema as any) as Tool['inputSchema']
    },
    {
      name: 'make_repro',
      description: 'Generate cURL command (and alternatives: HTTPie, JavaScript fetch) to reproduce an API call. Useful for debugging, documentation, and sharing reproducible test cases.',
      inputSchema: zodToJsonSchema(MakeReproSchema as any) as Tool['inputSchema']
    }
  ];

  return { tools };
});

// Handle tool execution
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    if (name === 'load_openapi') {
      const validatedArgs = LoadOpenAPISchema.parse(args);
      const result = await loadOpenAPI(validatedArgs);
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }]
      };
    }

    if (name === 'ingest_logs') {
      const validatedArgs = IngestLogsSchema.parse(args);
      const result = await ingestLogs(validatedArgs);
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }]
      };
    }

    if (name === 'explain_failure') {
      const validatedArgs = ExplainFailureSchema.parse(args);
      const result = await explainFailure(validatedArgs);
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }]
      };
    }

    if (name === 'make_repro') {
      const validatedArgs = MakeReproSchema.parse(args);
      const result = await makeRepro(validatedArgs);
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }]
      };
    }

    throw new Error(`Unknown tool: ${name}`);
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({ error: errorMessage }, null, 2)
      }],
      isError: true
    };
  }
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('API Debugger MCP server running on stdio');
}

main().catch((error) => {
  console.error('Fatal error in main():', error);
  process.exit(1);
});
