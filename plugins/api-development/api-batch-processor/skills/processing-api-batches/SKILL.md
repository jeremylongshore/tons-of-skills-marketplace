---
name: processing-api-batches
description: 'Optimize bulk API requests with batching, throttling, and parallel execution.

  Use when processing bulk API operations efficiently.

  Trigger with phrases like "process bulk requests", "batch API calls", or "handle
  batch operations".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(api:batch-*)
version: 1.26.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- api
- processing-api
compatibility: Designed for Claude Code
---
# Processing API Batches

## Overview

Optimize bulk API operations with batch request endpoints, parallel execution with concurrency control, partial failure handling, and progress tracking. Implement batch processing patterns that accept arrays of operations in a single request, execute them efficiently with database bulk operations, and return per-item results with individual success/failure status.

## Prerequisites

- Web framework capable of handling large request bodies (configure body size limits: 10MB+ for batch payloads)
- Database with bulk operation support (bulk insert, bulk update, transactions)
- Queue system for async batch processing: Bull/BullMQ (Node.js), Celery (Python), or SQS
- Progress tracking store (Redis) for long-running batch status polling
- Rate limiting aware of batch operations (count individual operations, not just requests)

## Instructions

1. Examine existing API endpoints using Read and Grep to identify operations frequently called in loops by consumers, which are candidates for batch equivalents.
2. Design the batch request format: accept an array of operations in the request body, each with an optional client-provided `id` for result correlation, e.g., `POST /batch` with `{operations: [{method: "POST", path: "/users", body: {...}, id: "op1"}]}`.
3. Implement synchronous batch processing for small batches (< 100 items): validate all items, execute in a database transaction, and return per-item results with `{id, status, result|error}` for each operation.
4. Add asynchronous batch processing for large batches (> 100 items): accept the batch, return 202 Accepted with a `batchId` and status polling URL, process in a background worker, and update progress in Redis.
5. Implement concurrency control: process batch items in parallel with configurable concurrency limit (default: 10) using `p-limit` or `asyncio.Semaphore` to prevent database connection exhaustion.
6. Handle partial failures: do not abort the entire batch when individual items fail; collect per-item results with success/failure status, and return the batch result with summary counts (`succeeded`, `failed`, `total`).
7. Add progress tracking for async batches: expose `GET /batch/:batchId/status` returning `{total, completed, failed, progress: 0.75, status: "processing|completed|failed"}`.
8. Implement batch size limits and validation: maximum 1000 items per batch, reject oversized batches with 413, validate all items before processing any, and return all validation errors upfront.
9. Write tests covering: small sync batches, large async batches, partial failure handling, progress tracking, concurrency limits, and batch size validation.

See [`references/implementation.md`](references/implementation.md) for the full implementation guide.

## Output

- `${CLAUDE_SKILL_DIR}/src/routes/batch.js` - Batch request endpoint with sync/async routing
- `${CLAUDE_SKILL_DIR}/src/batch/processor.js` - Batch execution engine with concurrency control
- `${CLAUDE_SKILL_DIR}/src/batch/validator.js` - Batch request validation and size limit enforcement
- `${CLAUDE_SKILL_DIR}/src/batch/progress.js` - Redis-backed progress tracking for async batches
- `${CLAUDE_SKILL_DIR}/src/batch/workers/` - Background worker for async batch processing
- `${CLAUDE_SKILL_DIR}/src/batch/results.js` - Per-item result aggregation with summary statistics
- `${CLAUDE_SKILL_DIR}/tests/batch/` - Batch processing integration tests

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| 413 Payload Too Large | Batch exceeds maximum item count (1000) or body size limit | Return clear error with maximum allowed count; suggest splitting into multiple batch requests |
| 207 Multi-Status | Some batch items succeeded while others failed | Return per-item status array; include error details for failed items; provide summary counts |
| 408 Batch Timeout | Synchronous batch processing exceeded request timeout | Switch to async processing for large batches; return 202 with status polling URL |
| Partial transaction failure | Database transaction rolls back all items due to one failure | Use savepoints for per-item isolation; or process items individually outside a wrapping transaction |
| Progress tracking stale | Worker crashed mid-batch; progress stops updating | Implement heartbeat monitoring; mark batch as failed after heartbeat timeout; enable retry from last checkpoint |

Refer to [`references/errors.md`](references/errors.md) for comprehensive error patterns.

## Examples

**Bulk user import**: Accept a CSV-uploaded batch of 5000 user records via `POST /batch/users/import`, return 202 with `batchId`, process asynchronously with progress updates, and provide a downloadable results file when complete.

**Multi-resource batch**: Accept mixed operations in a single batch: `[{method:"POST",path:"/users",...}, {method:"PUT",path:"/orders/123",...}, {method:"DELETE",path:"/products/456"}]`, executing each against the appropriate handler.

**Idempotent batch retry**: Client includes `idempotencyKey` per batch item; on retry, already-completed items return their cached result without re-execution, while failed items are re-attempted.

See [`references/examples.md`](references/examples.md) for additional examples.

## Resources

- Google Cloud batch request format: https://cloud.google.com/storage/docs/json_api/v1/how-tos/batch
- Facebook Graph API batch requests pattern
- HTTP 207 Multi-Status (WebDAV) for partial success responses
- Bull queue documentation: https://docs.bullmq.io/
