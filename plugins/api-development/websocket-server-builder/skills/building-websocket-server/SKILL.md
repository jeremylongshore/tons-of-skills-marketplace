---
name: building-websocket-server
description: 'Build scalable WebSocket servers for real-time bidirectional communication.

  Use when enabling real-time bidirectional communication.

  Trigger with phrases like "build WebSocket server", "add real-time API", or "implement
  WebSocket".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(api:websocket-*)
version: 1.25.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- api
- scaling
- websocket-server
compatibility: Designed for Claude Code
---
# Building WebSocket Server

## Overview

Build scalable WebSocket servers for real-time bidirectional communication using the `ws` library, Socket.IO, or native framework WebSocket support. Handle connection lifecycle management, room/channel subscriptions, message broadcasting, heartbeat keepalive, and horizontal scaling with Redis pub/sub adapters.

## Prerequisites

- Node.js 18+ with `ws` or `socket.io`, or Python 3.10+ with `websockets` or FastAPI WebSocket, or Go with `gorilla/websocket`
- Redis for horizontal scaling with pub/sub adapter (Socket.IO Redis adapter, or manual pub/sub)
- Load balancer configured for WebSocket upgrade (sticky sessions or proper `Upgrade` header forwarding)
- JWT or session-based authentication for connection handshake
- Monitoring for active connection counts and message throughput

## Instructions

1. Examine existing HTTP server configuration using Read and Grep to determine the framework and identify where WebSocket upgrade handling integrates.
2. Create a WebSocket server instance attached to the existing HTTP server, configuring the upgrade path (e.g., `/ws`, `/socket.io`) and allowed origins.
3. Implement connection authentication by validating JWT tokens or session cookies during the WebSocket handshake `upgrade` event, rejecting unauthorized connections before protocol switch.
4. Build a connection registry that tracks active clients with metadata (user ID, subscribed channels, connection time) for targeted message delivery.
5. Define a message protocol using JSON envelopes with `type`, `channel`, `payload`, and `correlationId` fields for structured bidirectional communication.
6. Implement room/channel subscription logic allowing clients to join and leave named channels with server-side membership tracking.
7. Add heartbeat ping/pong mechanism with configurable interval (default 30s) and timeout detection to clean up stale connections.
8. Configure Redis pub/sub adapter for horizontal scaling so messages broadcast from any server instance reach all connected clients across the cluster.
9. Write connection lifecycle tests covering connect, authenticate, subscribe, message exchange, reconnect, and graceful disconnect scenarios.

See `${CLAUDE_SKILL_DIR}/references/implementation.md` for the full implementation guide.

## Output

- `${CLAUDE_SKILL_DIR}/src/ws/server.js` - WebSocket server setup and upgrade handling
- `${CLAUDE_SKILL_DIR}/src/ws/handlers/` - Per-message-type handler functions
- `${CLAUDE_SKILL_DIR}/src/ws/rooms.js` - Room/channel subscription management
- `${CLAUDE_SKILL_DIR}/src/ws/registry.js` - Active connection tracking registry
- `${CLAUDE_SKILL_DIR}/src/ws/heartbeat.js` - Ping/pong keepalive logic
- `${CLAUDE_SKILL_DIR}/src/ws/adapters/redis.js` - Redis pub/sub adapter for scaling
- `${CLAUDE_SKILL_DIR}/tests/ws/` - WebSocket connection and messaging tests

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| 401 during upgrade | JWT token missing or expired in handshake query/headers | Reject upgrade with HTTP 401 before WebSocket protocol switch completes |
| 1008 Policy Violation | Client sends malformed message or violates protocol | Send close frame with code 1008 and human-readable reason; log violation |
| 1006 Abnormal Closure | Network interruption without close handshake | Detect via heartbeat timeout; clean up connection registry; notify room members |
| Memory leak | Connection registry grows unbounded from stale entries | Implement heartbeat-based cleanup sweep every 60s; enforce max connections per server |
| Message storm | Single client flooding messages beyond acceptable rate | Apply per-connection message rate limiting; disconnect abusive clients with 1008 |

Refer to `${CLAUDE_SKILL_DIR}/references/errors.md` for comprehensive error patterns.

## Examples

**Chat application**: Multi-room chat server where clients join named rooms, receive member presence updates, and see real-time message delivery with typing indicators via separate message types.

**Live dashboard**: Server pushes metric updates to subscribed dashboard clients every second, with initial state snapshot on connection and incremental deltas thereafter.

**Collaborative editing**: Operational transformation relay server that receives edit operations from clients, transforms against concurrent operations, and broadcasts resolved changes to all document subscribers.

See `${CLAUDE_SKILL_DIR}/references/examples.md` for additional examples.

## Resources

- RFC 6455 The WebSocket Protocol
- Socket.IO documentation: https://socket.io/docs/v4/
- `ws` library: https://github.com/websockets/ws
- Redis pub/sub for WebSocket scaling patterns
