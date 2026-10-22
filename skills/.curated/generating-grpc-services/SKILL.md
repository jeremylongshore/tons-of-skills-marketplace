---
name: generating-grpc-services
description: 'Generate gRPC service definitions, stubs, and implementations from Protocol
  Buffers.

  Use when creating high-performance gRPC services.

  Trigger with phrases like "generate gRPC service", "create gRPC API", or "build
  gRPC server".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(api:grpc-*)
version: 1.24.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- api
- performance
- grpc-services
compatibility: Designed for Claude Code
---
# Generating gRPC Services

## Overview

Generate gRPC service definitions, client/server stubs, and implementations from Protocol Buffer (protobuf) `.proto` files. Scaffold unary, server-streaming, client-streaming, and bidirectional-streaming RPC methods with proper error status codes, interceptors for auth/logging, and health check service registration.

## Prerequisites

- Protocol Buffers compiler (`protoc`) v3.21+ installed
- Language-specific gRPC plugin: `grpc_tools_node_protoc_plugin` (Node.js), `grpcio-tools` (Python), or Go gRPC plugin
- `buf` CLI for proto linting and breaking change detection (recommended)
- gRPC testing tool: `grpcurl`, `evans`, or BloomRPC
- TLS certificates for production transport security (mTLS recommended for service-to-service)

## Instructions

1. Read existing `.proto` files using Glob and Read, or design new service definitions with message types, RPC methods, and streaming patterns per service requirements.
2. Define proto3 message types with appropriate field types, using `google.protobuf.Timestamp` for dates, `google.protobuf.Struct` for dynamic fields, and `oneof` for polymorphic messages.
3. Compile `.proto` files with `protoc` to generate language-specific stubs, server interfaces, and client libraries using the appropriate gRPC plugin.
4. Implement server-side RPC handlers for each method, returning proper gRPC status codes (`OK`, `NOT_FOUND`, `INVALID_ARGUMENT`, `PERMISSION_DENIED`) instead of generic errors.
5. Add server interceptors for authentication (extracting JWT from metadata), request logging with correlation IDs, and deadline propagation across service calls.
6. Implement health check service (`grpc.health.v1.Health`) and reflection service for runtime introspection by tools like `grpcurl`.
7. Configure TLS transport security, preferring mutual TLS (mTLS) for service-to-service communication with certificate rotation support.
8. Write integration tests using an in-process test server, validating all RPC methods including streaming scenarios with multiple messages and error conditions.
9. Generate a REST-to-gRPC gateway using `grpc-gateway` annotations for HTTP/JSON clients that need to access gRPC services.

See [`references/implementation.md`](references/implementation.md) for the full implementation guide.

## Output

- `${CLAUDE_SKILL_DIR}/proto/` - Protocol Buffer service and message definitions
- `${CLAUDE_SKILL_DIR}/generated/` - Auto-generated stubs and client/server code
- `${CLAUDE_SKILL_DIR}/src/services/` - RPC method handler implementations
- `${CLAUDE_SKILL_DIR}/src/interceptors/` - Auth, logging, and metrics interceptors
- `${CLAUDE_SKILL_DIR}/src/health/` - Health check service implementation
- `${CLAUDE_SKILL_DIR}/gateway/` - REST-to-gRPC gateway configuration (optional)
- `${CLAUDE_SKILL_DIR}/tests/` - Integration tests with in-process test server

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| INVALID_ARGUMENT (3) | Request message fails field validation constraints | Return detailed `BadRequest` error details with field-level violation descriptions |
| NOT_FOUND (5) | Requested resource does not exist | Include resource type and ID in error message metadata for client debugging |
| PERMISSION_DENIED (7) | Caller lacks required role or scope in JWT metadata | Return required permission in error details; log denied access attempt |
| DEADLINE_EXCEEDED (4) | RPC took longer than client-specified deadline | Propagate deadlines to downstream calls; implement cascading timeout budgets |
| UNAVAILABLE (14) | Server overloaded or downstream dependency unreachable | Client should retry with exponential backoff; server should implement backpressure |

Refer to [`references/errors.md`](references/errors.md) for comprehensive error patterns.

## Examples

**User management service**: Define `UserService` with `CreateUser`, `GetUser`, `ListUsers` (server-streaming for large result sets), and `UpdateUser` RPCs with field mask support for partial updates.

**Real-time event stream**: Bidirectional streaming RPC where clients subscribe to event topics and the server pushes filtered events, with flow control via client-side backpressure signals.

**gRPC-Web frontend**: Generate gRPC-Web compatible stubs for browser clients using Envoy proxy for HTTP/2 to gRPC translation, enabling direct proto-based communication from React/Vue applications.

See [`references/examples.md`](references/examples.md) for additional examples.

## Resources

- gRPC documentation: https://grpc.io/docs/
- Protocol Buffers Language Guide: https://protobuf.dev/programming-guides/proto3/
- Buf CLI for proto management: https://buf.build/
- gRPC-Gateway: https://grpc-ecosystem.github.io/grpc-gateway/
