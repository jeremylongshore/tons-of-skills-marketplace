# API Development Plugins Collection

A comprehensive collection of 25 professional plugins for API development with Claude Code.

## Overview

This collection provides tools for building, testing, securing, and monitoring APIs across REST, GraphQL, gRPC, and WebSocket protocols. All plugins follow API best practices and industry standards.

## Plugin Categories

### API Generation & Architecture (5 plugins)

1. **rest-api-generator** - Generate RESTful APIs from schemas
   - `/generate-rest-api` (shortcut: `/gra`)
   - Express, FastAPI, Django, Flask, NestJS support
   - OpenAPI documentation, validation, authentication

2. **graphql-server-builder** - Build GraphQL servers
   - `/build-graphql-server` (shortcut: `/gql`)
   - Schema-first design, resolvers, subscriptions
   - DataLoader, Apollo Server integration

3. **api-gateway-builder** - Build API gateways
   - `/build-api-gateway` (shortcut: `/gateway`)
   - Routing, authentication, rate limiting, load balancing

4. **grpc-service-generator** - Generate gRPC services
   - `/generate-grpc-service` (shortcut: `/grpc`)
   - Protocol Buffers, streaming support

5. **websocket-server-builder** - Build WebSocket servers
   - `/build-websocket-server` (shortcut: `/ws`)
   - Socket.io, real-time bidirectional communication

### API Security & Authentication (3 plugins)

1. **api-security-scanner** - Scan for OWASP API Top 10
   - `/scan-api-security` (shortcut: `/apiscan`)
   - Vulnerability detection, security audits

2. **api-authentication-builder** - Build auth systems
   - `/build-auth-system` (shortcut: `/auth`)
   - JWT, OAuth2, API keys, RBAC

3. **webhook-handler-creator** - Create secure webhooks
   - `/create-webhook-handler` (shortcut: `/webhook`)
   - Signature verification, idempotency, retry logic

### API Performance & Reliability (4 plugins)

1. **api-rate-limiter** - Implement rate limiting
   - `/add-rate-limiting` (shortcut: `/ratelimit`)
   - Token bucket, sliding window, Redis

2. **api-throttling-manager** - Manage throttling & quotas
    - `/implement-throttling` (shortcut: `/throttle`)
    - Dynamic rate limits, tiered pricing

3. **api-cache-manager** - Implement caching strategies
    - `/implement-caching` (shortcut: `/cache`)
    - Redis, HTTP headers, CDN integration

4. **api-load-tester** - Load test APIs
    - `/run-load-test` (shortcut: `/loadtest`)
    - k6, Gatling, Artillery support

### API Documentation & Contracts (3 plugins)

1. **api-documentation-generator** - Generate API docs
    - `/generate-api-docs` (shortcut: `/apidoc`)
    - OpenAPI 3.0, Swagger UI, Redoc

2. **api-contract-generator** - Generate API contracts
    - `/generate-contract` (shortcut: `/contract`)
    - Consumer-driven contract testing with Pact

3. **api-sdk-generator** - Generate client SDKs
    - `/generate-sdk` (shortcut: `/sdk`)
    - Multi-language SDK generation from OpenAPI

### API Testing & Validation (3 plugins)

1. **api-response-validator** - Validate API responses
    - `/validate-api-responses` (shortcut: `/validate`)
    - JSON Schema, OpenAPI validation

2. **api-schema-validator** - Validate API schemas
    - `/validate-schemas` (shortcut: `/schema`)
    - JSON Schema, Joi, Yup, Zod support

3. **api-mock-server** - Create mock API servers
    - `/create-mock-server` (shortcut: `/mock`)
    - OpenAPI-based mocking with Faker.js

### API Versioning & Migration (2 plugins)

1. **api-versioning-manager** - Manage API versions
    - `/manage-api-versions` (shortcut: `/apiver`)
    - Version strategies, deprecation notices

2. **api-migration-tool** - Migrate API versions
    - `/migrate-api` (shortcut: `/migrate`)
    - Breaking change detection, compatibility layers

### API Observability & Monitoring (3 plugins)

1. **api-monitoring-dashboard** - Create monitoring dashboards
    - `/create-monitoring` (shortcut: `/monitor`)
    - Metrics, logs, traces, alerts

2. **api-request-logger** - Implement request logging
    - `/setup-logging` (shortcut: `/logs`)
    - Structured logging, correlation IDs

3. **api-error-handler** - Standardized error handling
    - `/implement-error-handling` (shortcut: `/errors`)
    - Custom error classes, HTTP status codes

### Advanced API Patterns (2 plugins)

1. **api-event-emitter** - Event-driven APIs
    - `/implement-events` (shortcut: `/events`)
    - Message queues, Kafka, RabbitMQ

2. **api-batch-processor** - Batch API operations
    - `/implement-batch-processing` (shortcut: `/batch`)
    - Bulk operations, job queues, progress tracking

## Installation

### Install Individual Plugins

```bash
# REST API generator
/plugin install rest-api-generator@claude-code-plugins-plus

# GraphQL server builder
/plugin install graphql-server-builder@claude-code-plugins-plus

# API security scanner
/plugin install api-security-scanner@claude-code-plugins-plus
```

### Install All API Development Plugins

```bash
# Install the entire collection (25 plugins)
for plugin in rest-api-generator graphql-server-builder api-documentation-generator \
  api-versioning-manager webhook-handler-creator api-rate-limiter api-gateway-builder \
  grpc-service-generator api-mock-server api-security-scanner websocket-server-builder \
  api-response-validator api-error-handler api-cache-manager api-migration-tool \
  api-contract-generator api-monitoring-dashboard api-load-tester api-authentication-builder \
  api-request-logger api-throttling-manager api-sdk-generator api-schema-validator \
  api-event-emitter api-batch-processor; do
  /plugin install $plugin@claude-code-plugins-plus
done
```

## Quick Start Examples

### Build a REST API

```bash
/generate-rest-api

# Claude will ask:
# - What resources? (users, posts, products)
# - What framework? (Express, FastAPI, Django)
# - What database? (PostgreSQL, MongoDB)
# - Authentication? (JWT, OAuth, API keys)
```

### Secure Your API

```bash
# Scan for vulnerabilities
/scan-api-security

# Add authentication
/build-auth-system

# Implement rate limiting
/add-rate-limiting
```

### Document Your API

```bash
# Generate OpenAPI docs
/generate-api-docs

# Create client SDKs
/generate-sdk
```

### Monitor & Test

```bash
# Set up monitoring
/create-monitoring

# Load test
/run-load-test

# Validate responses
/validate-api-responses
```

## Best Practices Covered

### REST API Design

- Resource-based URLs
- Proper HTTP methods and status codes
- Pagination, filtering, sorting
- HATEOAS principles
- API versioning

### GraphQL Best Practices

- Schema-first design
- DataLoader for N+1 prevention
- Query complexity limiting
- Relay-style pagination

### API Security

- OWASP API Security Top 10
- JWT token management
- Rate limiting and throttling
- Input validation
- HTTPS/TLS enforcement

### Performance

- Caching strategies (Redis, CDN)
- Database query optimization
- Connection pooling
- Asynchronous processing

### Observability

- Structured logging
- Distributed tracing
- Metrics and alerting
- Error tracking

## Supported Frameworks

### Node.js

- Express
- NestJS
- Fastify
- Koa

### Python

- FastAPI
- Django REST Framework
- Flask
- Sanic

### Other Languages

- Go (Gin, Echo)
- Ruby (Rails API, Sinatra)
- Java (Spring Boot)
- C# (ASP.NET Core)

## Featured Plugins

The following plugins are marked as "featured" in the marketplace:

1. **rest-api-generator** - Most comprehensive REST API generator
2. **graphql-server-builder** - Production-ready GraphQL servers

## Requirements

- Claude Code CLI
- Node.js 18+ or Python 3.9+ (depending on framework)
- Database (PostgreSQL, MongoDB, MySQL - optional)
- Redis (for rate limiting and caching - optional)

## Contributing

These plugins are part of the Claude Code Plugins marketplace. To contribute improvements:

1. Fork the repository
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

MIT License - See individual plugin directories for details.

## Support

- Documentation: https://docs.claude.com/en/docs/claude-code/plugins
- Discussions: https://github.com/jeremylongshore/claude-code-plugins/discussions
- Issues: https://github.com/jeremylongshore/claude-code-plugins/issues

---

**Collection Version:** 1.0.0  
**Last Updated:** October 2025  
**Total Plugins:** 25  
**Category:** api-development
