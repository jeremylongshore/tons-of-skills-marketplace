# Lumera Agent Memory

**Durable agent memory with Cascade object storage and local FTS index**

## Architecture

```
CASS Session → Redact PII/Secrets → Encrypt Client-Side → Upload to Cascade
                                                              ↓
                                                         Cascade URI
                                                              ↓
                                          Store in Local SQLite FTS Index
                                                              ↓
                                          Query Index → Retrieve via URI → Decrypt
```

### Design Principles

- **Object storage + metadata index pattern**
- **CASS** (Claude Agent Session Store) remains source of truth
- **Cascade** stores selected sessions as durable encrypted blobs
- **Local SQLite FTS** index returns Cascade URIs (NEVER queries Cascade directly)
- **Client-side encryption** with user-controlled keys (AES-256-GCM)
- **Fail-closed security** for critical patterns (private keys, auth headers)
- **Redact-and-continue** for non-critical PII (emails, phones, expired tokens)

## MCP Tools

Exactly 4 tools with exact names:

### 1. `store_session_to_cascade`

Extract session from CASS, redact secrets/PII, encrypt, upload to Cascade, index locally.

**Args:**

- `session_id` (required): CASS session ID to store
- `tags` (optional): List of tags
- `metadata` (optional): Custom metadata
- `mode` (optional): "mock" | "live" (default: "mock")

**Returns:**

```json
{
  "ok": true,
  "session_id": "test_session_001",
  "cascade_uri": "cascade://sha256:abc123...",
  "indexed": true,
  "redaction": {
    "rules_fired": [
      {"rule": "email", "count": 2},
      {"rule": "aws_access_key", "count": 1}
    ]
  },
  "crypto": {
    "enc": "AES-256-GCM",
    "key_id": "default",
    "plaintext_sha256": "...",
    "ciphertext_sha256": "...",
    "bytes": 4567
  },
  "memory_card": {
    "title": "Deploy API to production",
    "summary_bullets": ["..."],
    "decisions": ["..."],
    "todos": ["..."],
    "entities": ["AWS", "ECS", "Production"],
    "keywords": ["deploy", "production", "api"],
    "notable_quotes": ["..."]
  }
}
```

### 2. `query_memories`

Search local SQLite FTS index (NEVER queries Cascade directly).

**Args:**

- `query` (required): Search query text
- `tags` (optional): Tag filters
- `time_range` (optional): `{start: ISO8601, end: ISO8601}`
- `limit` (optional): Max results (default: 10)

**Returns:**

```json
{
  "ok": true,
  "hits": [
    {
      "cass_session_id": "test_session_001",
      "cascade_uri": "cascade://sha256:abc123...",
      "title": "Deploy API to production",
      "snippet": "Deploy API to production - User requested deployment...",
      "tags": ["deployment", "aws"],
      "created_at": "2025-01-15T10:30:00Z",
      "score": 2.456
    }
  ]
}
```

### 3. `retrieve_session_from_cascade`

Fetch encrypted blob from Cascade via URI, decrypt client-side, return session.

**Args:**

- `cascade_uri` (required): Cascade URI from index
- `mode` (optional): "mock" | "live" (default: "mock")

**Returns:**

```json
{
  "ok": true,
  "cascade_uri": "cascade://sha256:abc123...",
  "session": {
    "session_id": "test_session_001",
    "messages": [...],
    "metadata": {...}
  },
  "memory_card": {
    "title": "...",
    "summary_bullets": ["..."],
    ...
  },
  "crypto": {
    "verified": true,
    "plaintext_sha256": "...",
    "ciphertext_sha256": "...",
    "key_id": "default"
  }
}
```

### 4. `estimate_storage_cost`

Estimate Cascade storage costs for session data.

**Args:**

- `bytes` (required): Data size in bytes
- `redundancy` (optional): Replication factor (default: 3)
- `pricing_inputs` (optional): Custom pricing overrides

**Returns:**

```json
{
  "ok": true,
  "bytes": 4567,
  "gb": 0.000004,
  "monthly_storage_usd": 0.0002,
  "estimated_request_usd": 0.0001,
  "total_estimated_usd": 0.0003,
  "assumptions": {
    "redundancy": 3,
    "storage_per_gb_month_usd": 0.02,
    "request_per_1k_usd": 0.0004,
    "estimated_reads_per_month": 100
  }
}
```

## Security Behavior

### Critical Patterns (Fail-Closed)

- Private keys (`-----BEGIN PRIVATE KEY-----`)
- AWS secret access keys (`aws_secret_access_key=...`)
- Raw authorization headers (`Authorization: Bearer ...`)
- Database passwords in connection strings

**Action:** Reject storage immediately with clear error message.

### Non-Critical Patterns (Redact & Continue)

- Email addresses
- Phone numbers
- AWS access keys (AKIA...)
- IPv4 addresses
- Generic API tokens (long base64-like strings)

**Action:** Redact with `[REDACTED:PATTERN_NAME]` and continue.

## Memory Card (Wow Factor)

Every stored session gets a deterministic "memory card" generated from content:

```json
{
  "title": "First user message (truncated to 80 chars)",
  "summary_bullets": ["First 3 messages with role prefix"],
  "decisions": ["Messages containing decision keywords"],
  "todos": ["Messages with action items"],
  "entities": ["Capitalized words (proper nouns)"],
  "keywords": ["Top 10 frequent words (5+ chars)"],
  "notable_quotes": ["Messages with ? or !"]
}
```

This makes search results feel intelligent without any network calls or LLM usage.

## Installation

```bash
cd /absolute/path/to/lumera-agent-memory
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
source .venv/bin/activate
```

## Running Tests

```bash
# All tests
pytest tests/ -v

# Just smoke test (90 seconds)
pytest tests/smoke_test_90s.py -v -s

# Specific test suites
pytest tests/test_redaction.py -v
pytest tests/test_encryption.py -v
pytest tests/test_fts_search.py -v
```

## Running the MCP Server

Installing this plugin does not automatically register its MCP server. Complete
the dependency setup above, then register the interpreter from that environment.

From the plugin directory, direct execution uses:

```bash
.venv/bin/python src/mcp_server.py
```

For Claude Code, register the same interpreter and script with absolute paths:

```bash
claude mcp add --transport stdio --scope user lumera-agent-memory -- "/absolute/path/to/lumera-agent-memory/.venv/bin/python" "/absolute/path/to/lumera-agent-memory/src/mcp_server.py"
```

Use the directory of your installed or copied plugin in both paths. Registration
is a manual step; it does not install Python dependencies. For another MCP host,
use its documented configuration location with the same executable and script.
Do not put an MCP server declaration in Claude Code's `settings.json`.

## Storage Locations

- **Mock Cascade:** `~/.lumera/cascade/` (content-addressed blobs)
- **SQLite Index:** `~/.lumera/index.db` (FTS5 search)

## Live Cascade Mode

Set environment variables:

```bash
export LUMERA_CASCADE_ENDPOINT="https://cascade.example.com"
export LUMERA_CASCADE_API_KEY="your-api-key"
```

Then use `mode="live"` in tool calls.

## Example Payloads

See below for example JSON payloads to call each tool.
