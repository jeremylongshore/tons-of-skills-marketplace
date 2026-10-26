# Conversational API Debugger

**Debug REST API failures using OpenAPI specs and HTTP logs**

An MCP server that helps developers quickly identify and fix API issues by analyzing OpenAPI specifications, ingesting HTTP logs, explaining failures, and generating reproducible test commands.

## What It Does

This plugin transforms API debugging from guesswork into systematic analysis:

1. **Load OpenAPI Specs** - Parse API documentation (JSON/YAML)
2. **Ingest HTTP Logs** - Import request/response data (HAR, JSON)
3. **Explain Failures** - Analyze why API calls failed with root cause analysis
4. **Generate Repros** - Create cURL/HTTPie/fetch commands to reproduce issues

## Installation

```bash
/plugin install conversational-api-debugger@claude-code-plugins-plus
```

## Features

### 4 Powerful MCP Tools

#### 1. `load_openapi`

Load and parse OpenAPI 3.x specifications.

```json
{
  "filePath": "/path/to/openapi.yaml",
  "name": "my-api"
}
```

**Returns:**

- API title, version, description
- Base URL and servers
- Complete endpoint list
- Endpoint count and structure

#### 2. `ingest_logs`

Import HTTP request/response logs for analysis.

```json
{
  "filePath": "/path/to/requests.har",
  "format": "har"
}
```

Or provide logs directly:

```json
{
  "logs": [
    {
      "timestamp": "2025-10-10T12:00:00Z",
      "method": "POST",
      "url": "https://api.example.com/users",
      "statusCode": 400,
      "requestBody": { "name": "John" },
      "responseBody": { "error": "Missing required field: email" }
    }
  ]
}
```

**Returns:**

- Total requests ingested
- Success/failure breakdown
- Status code distribution
- Method distribution
- Top errors (first 10)

#### 3. `explain_failure`

Analyze why an API call failed.

```json
{
  "logIndex": 0,
  "specName": "my-api"
}
```

**Returns:**

- **Severity**: critical | high | medium | low
- **Possible Causes**: List of likely root causes
- **Suggested Fixes**: Actionable remediation steps
- **Matching Endpoint**: Comparison with OpenAPI spec
- **Details**: Request/response for inspection

#### 4. `make_repro`

Generate cURL command to reproduce API call.

```json
{
  "logIndex": 0,
  "includeHeaders": true,
  "pretty": true
}
```

**Returns:**

- **cURL Command**: Ready to copy-paste
- **HTTPie Alternative**: Shorter syntax
- **JavaScript fetch**: For automated tests
- **Metadata**: Method, URL, headers count

Generated cURL and HTTPie commands use POSIX-shell quoting. URL, method, headers,
and body values stay literal; JavaScript uses serialized string/object values.
Bodies use raw-data options, including JSON serialization for non-string values,
so a leading `@` is body text. `false`, `0`, empty strings, and `null` remain bodies.
`includeHeaders: false` suppresses headers in every generated alternative without
changing stored logs. When headers are included, their names must be HTTP
tokens; suppressed headers are not validated. Shell arguments containing NUL are
rejected because an argv argument cannot represent that byte.
HTTPie escapes a leading `@` in header values to avoid its file-import operator.
These snippets do not run automatically. Review the target and request before
running them; quoting does not redact credentials or make a request read-only.
The shell output targets POSIX shells, not PowerShell or cmd.exe.

## Quick Start

### Scenario 1: Debugging a 400 Bad Request

```bash
# 1. Load your OpenAPI spec
Use load_openapi with path to your spec file

# 2. Export HAR from browser DevTools
# Network tab → Right-click → Save as HAR with content

# 3. Ingest the logs
Use ingest_logs with HAR file path

# 4. Analyze the failure
Use explain_failure on the failed request

# 5. Get a working cURL command
Use make_repro to generate test command
```

**Example Output:**

```
 ANALYSIS
Status: 400 Bad Request
Severity: HIGH

 ROOT CAUSE
Missing required field: "email"

OpenAPI spec requires:
- name (string, required)
- email (string, format: email, required)

Your request only included "name".

 SUGGESTED FIXES
1. Add "email" field to request body
2. Ensure email format is valid ([email protected])

 TEST COMMAND
curl -X POST "https://api.example.com/users" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "[email protected]"
  }'
```

### Scenario 2: Understanding 401 Unauthorized

```bash
# 1. Ingest logs showing 401 errors
Use ingest_logs

# 2. Explain the failure
Use explain_failure

# Get specific guidance on:
# - Missing Authorization header
# - Invalid/expired token
# - Wrong authentication scheme
# - Missing scopes/permissions
```

## Slash Command

Use the `/debug-api` command for a guided debugging workflow:

```bash
/debug-api
```

This activates a systematic 4-step process:

1. Load API documentation (OpenAPI spec)
2. Ingest HTTP logs (HAR or JSON)
3. Analyze failures (explain errors)
4. Generate test commands (cURL repros)

## AI Agent

The `api-expert` agent specializes in API debugging:

- **Root cause analysis** of HTTP errors
- **OpenAPI spec interpretation**
- **Severity assessment** (critical → low)
- **Actionable fix suggestions**
- **Test command generation**

Activate by asking questions like:

- "Why is my API returning 400?"
- "Help me debug this authentication error"
- "Analyze these API logs"

## Supported Formats

### OpenAPI Specs

- OpenAPI 3.0.x
- OpenAPI 3.1.x
- JSON format
- YAML format
- ️ Swagger 2.0 (limited support)

### HTTP Logs

- HAR (HTTP Archive) - browser DevTools export
- JSON array of request/response objects
- Direct log objects (manual entry)

## Status Code Knowledge Base

The plugin has built-in expertise for all common HTTP status codes:

### 4xx Client Errors

- **400** Bad Request → Validation/syntax errors
- **401** Unauthorized → Authentication issues
- **403** Forbidden → Permission problems
- **404** Not Found → Endpoint/resource missing
- **405** Method Not Allowed → Wrong HTTP method
- **408** Request Timeout → Network/performance
- **409** Conflict → Resource state conflict
- **422** Unprocessable Entity → Semantic validation
- **429** Too Many Requests → Rate limiting

### 5xx Server Errors

- **500** Internal Server Error → Server bug (CRITICAL)
- **502** Bad Gateway → Upstream error (CRITICAL)
- **503** Service Unavailable → Temporary issue (HIGH)
- **504** Gateway Timeout → Upstream timeout (HIGH)

## How It Works

### Under the Hood

1. **OpenAPI Parsing**: Uses `openapi-types` and `yaml` to parse specs
2. **HAR Processing**: Extracts requests/responses from browser exports
3. **Pattern Matching**: Matches URLs to OpenAPI endpoints with regex
4. **Failure Analysis**: Compares actual vs expected behavior
5. **Command Generation**: Creates executable test commands

### In-Memory Storage

The plugin maintains:

- **API Specs**: Map of loaded OpenAPI documents
- **HTTP Logs**: Array of ingested requests/responses
- **Log Indexing**: Fast lookup by index for analysis

Data persists during the session but clears on restart (no disk storage).

## Examples

### Export HAR from Browser

**Chrome/Edge:**

1. Open DevTools (F12)
2. Go to Network tab
3. Perform API calls
4. Right-click network log
5. "Save all as HAR with content"

**Firefox:**

1. Open DevTools (F12)
2. Go to Network tab
3. Perform API calls
4. Click gear icon → "Save All As HAR"

### Manual Log Entry

```javascript
// If you have logs in code, convert to this format:
const logs = [
  {
    timestamp: new Date().toISOString(),
    method: 'POST',
    url: 'https://api.example.com/users',
    statusCode: 400,
    requestHeaders: {
      'Content-Type': 'application/json'
    },
    requestBody: {
      name: 'John'
    },
    responseBody: {
      error: 'Missing required field: email'
    }
  }
];

// Then use ingest_logs with logs array directly
```

## ️ Architecture

```
conversational-api-debugger/
├── servers/
│   └── api-debugger.ts        # MCP server (730+ lines)
├── tests/
│   └── api-debugger.test.ts   # Comprehensive tests (36 tests)
├── commands/
│   └── debug-api.md           # /debug-api workflow
├── agents/
│   └── api-expert.md          # API debugging agent
└── .claude-plugin/
    └── plugin.json            # Plugin metadata
```

## Testing

```bash
# Run test suite
pnpm test

# Run with coverage
pnpm test:coverage

# Build TypeScript
pnpm build
```

**Test Coverage:**

- OpenAPI spec loading (JSON/YAML)
- HAR file parsing
- Log analysis (status codes, methods)
- Failure analysis (all HTTP status codes)
- Endpoint matching (path parameters)
- cURL generation (headers, bodies)
- Input validation (Zod schemas)
- Error handling

## Contributing

See [CONTRIBUTING.md](../../../000-docs/007-DR-GUID-contributing.md) for development guidelines.

## License

MIT License - see [LICENSE](../../../000-docs/001-BL-LICN-license.txt)

## Related Tools

- **project-health-auditor** - Code quality and technical debt analysis
- **domain-memory-agent** - Knowledge base with semantic search
- **design-to-code** - Figma/screenshot to component generation
- **workflow-orchestrator** - DAG-based task automation

## Use Cases

1. **Debugging Production Issues** - Analyze production API failures quickly
2. **API Integration** - Understand third-party API errors
3. **Documentation** - Generate examples for API docs
4. **Testing** - Create reproducible test cases
5. **Bug Reports** - Include working repro commands
6. **Onboarding** - Help new developers understand APIs

## Best Practices

1. **Always load OpenAPI spec first** - Provides context for analysis
2. **Use HAR files when possible** - Most complete log format
3. **Include request/response bodies** - Critical for validation errors
4. **Generate repro commands** - Makes debugging tangible
5. **Test fixes immediately** - Use generated cURL to verify
6. **Keep specs up-to-date** - Ensure accurate comparisons

## Performance

- **OpenAPI Loading**: < 100ms for typical specs
- **HAR Parsing**: < 500ms for 100 requests
- **Failure Analysis**: < 50ms per request
- **cURL Generation**: < 10ms per command

## Troubleshooting

**Q: OpenAPI spec fails to load**
A: Ensure it's valid OpenAPI 3.x (check `openapi: "3.0.0"` field)

**Q: HAR file won't parse**
A: Verify it's exported with "content" option enabled

**Q: Can't find matching endpoint**
A: Check URL path matches OpenAPI spec (including base path)

**Q: Generated cURL doesn't work**
A: Verify all required headers are in original request

## Features Coming Soon

- [ ] Support for GraphQL APIs
- [ ] Batch failure analysis
- [ ] Custom validation rules
- [ ] Postman collection export
- [ ] Response schema validation
- [ ] Performance profiling

---

**Made with ️ by [Intent Solutions](https://intentsolutions.io)**

Part of the Claude Code Plugin Marketplace
