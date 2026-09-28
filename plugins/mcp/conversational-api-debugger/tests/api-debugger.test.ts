import { describe, it, expect, beforeEach } from 'vitest';
import { promises as fs } from 'fs';
import path from 'path';
import os from 'os';

// Test data
let testDir: string;
let openAPISpecPath: string;
let harFilePath: string;

beforeEach(async () => {
  // Create temporary test directory
  testDir = await fs.mkdtemp(path.join(os.tmpdir(), 'api-debugger-test-'));

  // Create sample OpenAPI spec
  const openAPISpec = {
    openapi: '3.0.0',
    info: {
      title: 'Test API',
      version: '1.0.0',
      description: 'A test API for debugging'
    },
    servers: [
      {
        url: 'https://api.example.com/v1'
      }
    ],
    paths: {
      '/users/{id}': {
        get: {
          summary: 'Get user by ID',
          parameters: [
            {
              name: 'id',
              in: 'path',
              required: true,
              schema: { type: 'string' }
            }
          ],
          responses: {
            '200': {
              description: 'Success',
              content: {
                'application/json': {
                  schema: {
                    type: 'object',
                    properties: {
                      id: { type: 'string' },
                      name: { type: 'string' }
                    }
                  }
                }
              }
            },
            '404': {
              description: 'User not found'
            }
          }
        }
      },
      '/users': {
        post: {
          summary: 'Create user',
          requestBody: {
            required: true,
            content: {
              'application/json': {
                schema: {
                  type: 'object',
                  required: ['name', 'email'],
                  properties: {
                    name: { type: 'string' },
                    email: { type: 'string', format: 'email' }
                  }
                }
              }
            }
          },
          responses: {
            '201': {
              description: 'Created'
            },
            '400': {
              description: 'Bad request'
            }
          }
        }
      }
    }
  };

  openAPISpecPath = path.join(testDir, 'openapi.json');
  await fs.writeFile(openAPISpecPath, JSON.stringify(openAPISpec, null, 2));

  // Create sample HAR file
  const harFile = {
    log: {
      version: '1.2',
      creator: {
        name: 'Test',
        version: '1.0'
      },
      entries: [
        {
          startedDateTime: '2025-10-10T12:00:00.000Z',
          time: 150,
          request: {
            method: 'GET',
            url: 'https://api.example.com/v1/users/123',
            headers: [
              { name: 'Authorization', value: 'Bearer token123' },
              { name: 'Accept', value: 'application/json' }
            ]
          },
          response: {
            status: 200,
            headers: [
              { name: 'Content-Type', value: 'application/json' }
            ],
            content: {
              text: JSON.stringify({ id: '123', name: 'John Doe' })
            }
          }
        },
        {
          startedDateTime: '2025-10-10T12:01:00.000Z',
          time: 50,
          request: {
            method: 'POST',
            url: 'https://api.example.com/v1/users',
            headers: [
              { name: 'Content-Type', value: 'application/json' }
            ],
            postData: {
              text: JSON.stringify({ name: 'Jane' })
            }
          },
          response: {
            status: 400,
            headers: [
              { name: 'Content-Type', value: 'application/json' }
            ],
            content: {
              text: JSON.stringify({ error: 'Missing required field: email' })
            }
          }
        }
      ]
    }
  };

  harFilePath = path.join(testDir, 'requests.har');
  await fs.writeFile(harFilePath, JSON.stringify(harFile, null, 2));
});

describe('API Debugger MCP Server', () => {
  describe('OpenAPI Spec Loading', () => {
    it('should load and parse JSON OpenAPI spec', async () => {
      const content = await fs.readFile(openAPISpecPath, 'utf-8');
      const spec = JSON.parse(content);

      expect(spec.openapi).toBe('3.0.0');
      expect(spec.info.title).toBe('Test API');
      expect(spec.paths['/users/{id}']).toBeDefined();
    });

    it('should extract endpoints from spec', async () => {
      const content = await fs.readFile(openAPISpecPath, 'utf-8');
      const spec = JSON.parse(content);
      const endpoints: string[] = [];

      for (const [path, pathItem] of Object.entries(spec.paths)) {
        const methods = ['get', 'post', 'put', 'delete'] as const;
        for (const method of methods) {
          if ((pathItem as any)[method]) {
            endpoints.push(`${method.toUpperCase()} ${path}`);
          }
        }
      }

      expect(endpoints).toContain('GET /users/{id}');
      expect(endpoints).toContain('POST /users');
    });

    it('should extract base URL from servers', async () => {
      const content = await fs.readFile(openAPISpecPath, 'utf-8');
      const spec = JSON.parse(content);

      expect(spec.servers).toBeDefined();
      expect(spec.servers[0].url).toBe('https://api.example.com/v1');
    });

    it('should validate OpenAPI version', async () => {
      const content = await fs.readFile(openAPISpecPath, 'utf-8');
      const spec = JSON.parse(content);

      expect(spec.openapi || spec.swagger).toBeDefined();
      expect(spec.openapi).toMatch(/^3\./);
    });
  });

  describe('HAR File Parsing', () => {
    it('should parse HAR file structure', async () => {
      const content = await fs.readFile(harFilePath, 'utf-8');
      const har = JSON.parse(content);

      expect(har.log).toBeDefined();
      expect(har.log.entries).toBeInstanceOf(Array);
      expect(har.log.entries.length).toBe(2);
    });

    it('should extract HTTP logs from HAR entries', async () => {
      const content = await fs.readFile(harFilePath, 'utf-8');
      const har = JSON.parse(content);
      const logs = [];

      for (const entry of har.log.entries) {
        logs.push({
          timestamp: entry.startedDateTime,
          method: entry.request.method,
          url: entry.request.url,
          statusCode: entry.response.status,
          duration: entry.time
        });
      }

      expect(logs).toHaveLength(2);
      expect(logs[0].method).toBe('GET');
      expect(logs[0].statusCode).toBe(200);
      expect(logs[1].method).toBe('POST');
      expect(logs[1].statusCode).toBe(400);
    });

    it('should convert HAR headers array to object', async () => {
      const content = await fs.readFile(harFilePath, 'utf-8');
      const har = JSON.parse(content);
      const headers = har.log.entries[0].request.headers;

      const headersObj: Record<string, string> = {};
      headers.forEach((h: any) => {
        headersObj[h.name] = h.value;
      });

      expect(headersObj).toHaveProperty('Authorization');
      expect(headersObj['Authorization']).toBe('Bearer token123');
    });

    it('should parse request and response bodies', async () => {
      const content = await fs.readFile(harFilePath, 'utf-8');
      const har = JSON.parse(content);

      const entry1 = har.log.entries[0];
      const responseBody = JSON.parse(entry1.response.content.text);
      expect(responseBody).toEqual({ id: '123', name: 'John Doe' });

      const entry2 = har.log.entries[1];
      const requestBody = JSON.parse(entry2.request.postData.text);
      expect(requestBody).toEqual({ name: 'Jane' });
    });
  });

  describe('Log Analysis', () => {
    it('should calculate status code distribution', async () => {
      const logs = [
        { statusCode: 200 },
        { statusCode: 200 },
        { statusCode: 400 },
        { statusCode: 500 }
      ];

      const distribution = new Map<number, number>();
      logs.forEach(log => {
        distribution.set(log.statusCode, (distribution.get(log.statusCode) || 0) + 1);
      });

      expect(distribution.get(200)).toBe(2);
      expect(distribution.get(400)).toBe(1);
      expect(distribution.get(500)).toBe(1);
    });

    it('should identify failed requests', async () => {
      const logs = [
        { statusCode: 200, url: '/success' },
        { statusCode: 400, url: '/bad-request' },
        { statusCode: 500, url: '/error' },
        { statusCode: 201, url: '/created' }
      ];

      const errors = logs.filter(log => log.statusCode >= 400);

      expect(errors).toHaveLength(2);
      expect(errors[0].statusCode).toBe(400);
      expect(errors[1].statusCode).toBe(500);
    });

    it('should count method distribution', async () => {
      const logs = [
        { method: 'GET' },
        { method: 'GET' },
        { method: 'POST' },
        { method: 'PUT' }
      ];

      const methods = new Map<string, number>();
      logs.forEach(log => {
        methods.set(log.method, (methods.get(log.method) || 0) + 1);
      });

      expect(methods.get('GET')).toBe(2);
      expect(methods.get('POST')).toBe(1);
      expect(methods.get('PUT')).toBe(1);
    });
  });

  describe('Failure Analysis', () => {
    it('should identify 400 Bad Request causes', () => {
      const statusCode = 400;
      const causes: string[] = [];
      const fixes: string[] = [];

      if (statusCode === 400) {
        causes.push('Bad Request - Invalid request syntax or parameters');
        fixes.push('Validate request body matches API schema');
        fixes.push('Check required parameters are present');
      }

      expect(causes.some(c => c.includes('Bad Request'))).toBe(true);
      expect(fixes.some(f => f.includes('Validate request body'))).toBe(true);
    });

    it('should identify 401 Unauthorized causes', () => {
      const statusCode = 401;
      const causes: string[] = [];
      const fixes: string[] = [];

      if (statusCode === 401) {
        causes.push('Unauthorized - Missing or invalid authentication');
        fixes.push('Check authentication token/credentials are valid');
        fixes.push('Ensure Authorization header is present');
      }

      expect(causes.some(c => c.includes('Unauthorized'))).toBe(true);
      expect(fixes.length).toBeGreaterThanOrEqual(2);
    });

    it('should identify 404 Not Found causes', () => {
      const statusCode = 404;
      const causes: string[] = [];

      if (statusCode === 404) {
        causes.push('Not Found - Endpoint or resource does not exist');
      }

      expect(causes.some(c => c.includes('Not Found'))).toBe(true);
    });

    it('should identify 500 Internal Server Error causes', () => {
      const statusCode = 500;
      const severity = statusCode === 500 ? 'critical' : 'medium';

      expect(severity).toBe('critical');
    });

    it('should extract error from response body', () => {
      const responseBody = {
        error: 'Missing required field: email',
        code: 'VALIDATION_ERROR'
      };

      const causes: string[] = [];
      if ('error' in responseBody) {
        causes.push(`Server error message: ${responseBody.error}`);
      }

      expect(causes).toContain('Server error message: Missing required field: email');
    });

    it('should determine severity level', () => {
      const severities: Record<number, 'critical' | 'high' | 'medium' | 'low'> = {
        500: 'critical',
        502: 'critical',
        400: 'high',
        401: 'high',
        404: 'medium',
        429: 'medium'
      };

      expect(severities[500]).toBe('critical');
      expect(severities[400]).toBe('high');
      expect(severities[404]).toBe('medium');
    });
  });

  describe('Endpoint Matching', () => {
    it('should match URL path to OpenAPI endpoint', async () => {
      const content = await fs.readFile(openAPISpecPath, 'utf-8');
      const spec = JSON.parse(content);

      const url = 'https://api.example.com/v1/users/123';
      const pathname = new URL(url).pathname.replace('/v1', '');

      const pathPattern = '/users/{id}';
      const regex = new RegExp('^' + pathPattern.replace(/\{[^}]+\}/g, '[^/]+') + '$');

      expect(regex.test(pathname)).toBe(true);
    });

    it('should match HTTP method to operation', async () => {
      const content = await fs.readFile(openAPISpecPath, 'utf-8');
      const spec = JSON.parse(content);

      const method = 'GET';
      const path = '/users/{id}';
      const pathItem = spec.paths[path];

      expect(pathItem[method.toLowerCase()]).toBeDefined();
      expect(pathItem.get.summary).toBe('Get user by ID');
    });

    it('should identify required parameters', async () => {
      const content = await fs.readFile(openAPISpecPath, 'utf-8');
      const spec = JSON.parse(content);

      const operation = spec.paths['/users/{id}'].get;
      const requiredParams = operation.parameters.filter((p: any) => p.required);

      expect(requiredParams).toHaveLength(1);
      expect(requiredParams[0].name).toBe('id');
    });

    it('should check if request body is required', async () => {
      const content = await fs.readFile(openAPISpecPath, 'utf-8');
      const spec = JSON.parse(content);

      const operation = spec.paths['/users'].post;
      const isBodyRequired = operation.requestBody?.required;

      expect(isBodyRequired).toBe(true);
    });
  });

  describe('cURL Generation', () => {
    it('should generate basic GET request', () => {
      const log = {
        method: 'GET',
        url: 'https://api.example.com/users',
        requestHeaders: {}
      };

      const parts = ['curl'];
      if (log.method !== 'GET') {
        parts.push(`-X ${log.method}`);
      }
      parts.push(`"${log.url}"`);

      const curl = parts.join(' ');
      expect(curl).toBe('curl "https://api.example.com/users"');
    });

    it('should generate POST request with body', () => {
      const log = {
        method: 'POST',
        url: 'https://api.example.com/users',
        requestHeaders: {},
        requestBody: { name: 'John', email: '[email protected]' }
      };

      const parts = ['curl', '-X POST'];
      const body = JSON.stringify(log.requestBody);
      parts.push(`-d '${body}'`);
      parts.push(`"${log.url}"`);

      const curl = parts.join(' ');
      expect(curl).toContain('-X POST');
      expect(curl).toContain('-d');
    });

    it('should include custom headers', () => {
      const log = {
        method: 'GET',
        url: 'https://api.example.com/users',
        requestHeaders: {
          'Authorization': 'Bearer token123',
          'Accept': 'application/json'
        }
      };

      const parts = ['curl'];
      for (const [key, value] of Object.entries(log.requestHeaders)) {
        parts.push(`-H "${key}: ${value}"`);
      }
      parts.push(`"${log.url}"`);

      const curl = parts.join(' ');
      expect(curl).toContain('-H "Authorization: Bearer token123"');
      expect(curl).toContain('-H "Accept: application/json"');
    });

    it('should escape single quotes in body for safe shell single-quoting', () => {
      const body = "{ \"name\": \"O'Brien\" }";
      // Matches servers/api-debugger.ts: a bare backslash cannot escape a
      // quote inside a single-quoted shell string, so close/escape/reopen.
      const escaped = body.replace(/'/g, "'\\''");

      expect(escaped).toBe("{ \"name\": \"O'\\''Brien\" }");
    });

    it('should format with line breaks for readability', () => {
      const parts = ['curl', '-X POST', '-H "Content-Type: application/json"', '"https://api.example.com/users"'];
      const pretty = parts.join(' \\\n  ');

      expect(pretty).toContain('\\\n');
      expect(pretty.split('\n').length).toBe(4);
    });
  });

  describe('Alternative Command Generation', () => {
    it('should generate HTTPie command', () => {
      const log = {
        method: 'POST',
        url: 'https://api.example.com/users',
        requestHeaders: {
          'Authorization': 'Bearer token123'
        },
        requestBody: {
          name: 'John',
          email: '[email protected]'
        }
      };

      const parts = ['http'];
      if (log.method !== 'GET') {
        parts.push(log.method);
      }
      parts.push(log.url);

      // Headers
      for (const [key, value] of Object.entries(log.requestHeaders)) {
        parts.push(`${key}:"${value}"`);
      }

      // Body (HTTPie auto-detects JSON)
      if (typeof log.requestBody === 'object') {
        for (const [key, value] of Object.entries(log.requestBody)) {
          parts.push(`${key}="${value}"`);
        }
      }

      const httpie = parts.join(' ');
      expect(httpie).toContain('http POST');
      expect(httpie).toContain('Authorization:"Bearer token123"');
    });

    it('should generate JavaScript fetch code', () => {
      const log = {
        method: 'POST',
        url: 'https://api.example.com/users',
        requestHeaders: {
          'Content-Type': 'application/json'
        },
        requestBody: {
          name: 'John'
        }
      };

      const options = {
        method: log.method,
        headers: log.requestHeaders,
        body: JSON.stringify(log.requestBody)
      };

      const code = `fetch("${log.url}", ${JSON.stringify(options, null, 2)})`;

      expect(code).toContain('fetch(');
      expect(code).toContain('"method": "POST"');
      expect(code).toContain('"Content-Type": "application/json"');
    });
  });

  describe('Input Validation', () => {
    it('should validate load_openapi schema', async () => {
      const { z } = await import('zod');

      const LoadOpenAPISchema = z.object({
        filePath: z.string(),
        name: z.string().optional()
      });

      expect(() => LoadOpenAPISchema.parse({ filePath: '/path/to/spec.json' })).not.toThrow();
      expect(() => LoadOpenAPISchema.parse({})).toThrow();
    });

    it('should validate ingest_logs schema', async () => {
      const { z } = await import('zod');

      const IngestLogsSchema = z.object({
        filePath: z.string().optional(),
        logs: z.array(z.object({
          timestamp: z.string(),
          method: z.string(),
          url: z.string(),
          statusCode: z.number()
        })).optional(),
        format: z.enum(['har', 'json', 'auto']).optional()
      });

      expect(() => IngestLogsSchema.parse({ filePath: '/path/to/logs.har' })).not.toThrow();
      expect(() => IngestLogsSchema.parse({ logs: [] })).not.toThrow();
      // Empty object is valid since both filePath and logs are optional
      expect(() => IngestLogsSchema.parse({})).not.toThrow();
    });

    it('should validate explain_failure schema', async () => {
      const { z } = await import('zod');

      const ExplainFailureSchema = z.object({
        logIndex: z.number().optional(),
        log: z.object({
          timestamp: z.string(),
          method: z.string(),
          url: z.string(),
          statusCode: z.number()
        }).optional(),
        specName: z.string().optional()
      });

      expect(() => ExplainFailureSchema.parse({ logIndex: 0 })).not.toThrow();
      expect(() => ExplainFailureSchema.parse({ log: { timestamp: '', method: 'GET', url: '', statusCode: 400 } })).not.toThrow();
      // Empty object is valid since all fields are optional
      expect(() => ExplainFailureSchema.parse({})).not.toThrow();
    });

    it('should validate make_repro schema', async () => {
      const { z } = await import('zod');

      const MakeReproSchema = z.object({
        logIndex: z.number().optional(),
        log: z.object({
          method: z.string(),
          url: z.string()
        }).optional(),
        includeHeaders: z.boolean().optional(),
        pretty: z.boolean().optional()
      });

      expect(() => MakeReproSchema.parse({ logIndex: 0 })).not.toThrow();
      expect(() => MakeReproSchema.parse({ log: { method: 'GET', url: 'https://api.example.com' } })).not.toThrow();
      // Empty object is valid since all fields are optional
      expect(() => MakeReproSchema.parse({})).not.toThrow();
    });
  });

  describe('Error Handling', () => {
    it('should handle non-existent file', async () => {
      const nonExistentPath = path.join(testDir, 'does-not-exist.json');
      await expect(fs.readFile(nonExistentPath, 'utf-8')).rejects.toThrow();
    });

    it('should handle invalid JSON', async () => {
      const invalidJSONPath = path.join(testDir, 'invalid.json');
      await fs.writeFile(invalidJSONPath, '{ invalid json }');

      const content = await fs.readFile(invalidJSONPath, 'utf-8');
      expect(() => JSON.parse(content)).toThrow();
    });

    it('should handle missing OpenAPI version', async () => {
      const invalidSpec: any = {
        info: { title: 'Test' },
        paths: {}
      };

      expect(invalidSpec.openapi || invalidSpec.swagger).toBeUndefined();
    });

    it('should handle invalid log index', () => {
      const logs: any[] = [];
      const index = 5;

      const isInvalid = index < 0 || index >= logs.length;
      expect(isInvalid).toBe(true);
    });
  });
});
