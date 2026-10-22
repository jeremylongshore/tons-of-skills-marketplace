---
name: building-graphql-server
description: 'Build production-ready GraphQL servers with schema design, resolvers,
  and subscriptions.

  Use when building GraphQL APIs with schemas and resolvers.

  Trigger with phrases like "build GraphQL API", "create GraphQL server", or "setup
  GraphQL".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(api:graphql-*)
version: 1.23.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- api
- graphql
- graphql-server
compatibility: Designed for Claude Code
---
# Building GraphQL Server

## Overview

Build production-ready GraphQL servers with SDL-first or code-first schema design, efficient resolver implementations with DataLoader batching, real-time subscriptions via WebSocket, and field-level authorization. Support Apollo Server, Yoga, Mercurius, and Strawberry across Node.js and Python runtimes.

## Prerequisites

- Node.js 18+ with Apollo Server/Yoga/Mercurius, or Python 3.10+ with Strawberry/Ariadne
- Database with ORM (Prisma, TypeORM, SQLAlchemy) for resolver data sources
- Redis for subscription pub/sub and DataLoader caching (production deployments)
- GraphQL client for testing: GraphiQL, Apollo Studio, or Insomnia
- `graphql-codegen` for TypeScript type generation from schema (recommended)

## Instructions

1. Examine existing data models, database schemas, and business requirements using Read and Glob to determine the entity graph and relationship structure.
2. Design the GraphQL schema with type definitions, including `Query`, `Mutation`, and `Subscription` root types, input types for mutations, and connection types for paginated lists.
3. Implement resolvers for each field, using DataLoader to batch and deduplicate database queries for nested relationships (N+1 query prevention).
4. Add input validation on mutation arguments using custom scalars (DateTime, Email, URL) and directive-based validation (`@constraint(minLength: 1, maxLength: 255)`).
5. Implement field-level authorization using schema directives (`@auth(requires: ADMIN)`) or resolver middleware that checks user roles from the GraphQL context.
6. Configure query complexity analysis and depth limiting to prevent abusive queries (maximum depth of 7, maximum complexity score of 1000).
7. Set up real-time subscriptions using `graphql-ws` protocol over WebSocket with Redis pub/sub for multi-instance message distribution.
8. Generate TypeScript types from the schema using `graphql-codegen` to ensure type safety between schema definitions and resolver implementations.
9. Write integration tests using `executeOperation` for query/mutation testing and WebSocket client tests for subscription verification.

See [`references/implementation.md`](references/implementation.md) for the full implementation guide.

## Output

- `${CLAUDE_SKILL_DIR}/src/schema/` - GraphQL SDL type definitions organized by domain
- `${CLAUDE_SKILL_DIR}/src/resolvers/` - Resolver implementations per type with DataLoader integration
- `${CLAUDE_SKILL_DIR}/src/dataloaders/` - DataLoader factories for batched database queries
- `${CLAUDE_SKILL_DIR}/src/directives/` - Custom schema directives (auth, validation, caching)
- `${CLAUDE_SKILL_DIR}/src/scalars/` - Custom scalar type definitions (DateTime, JSON, Email)
- `${CLAUDE_SKILL_DIR}/src/subscriptions/` - Subscription resolvers with pub/sub configuration
- `${CLAUDE_SKILL_DIR}/generated/types.ts` - Auto-generated TypeScript types from schema

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| N+1 query detected | Resolver fetches related records individually inside list resolver | Wrap data access in DataLoader; batch by parent ID array; cache within request scope |
| Query complexity exceeded | Client sends deeply nested query exceeding complexity budget | Return error with current complexity score and maximum allowed; suggest query simplification |
| Subscription connection dropped | WebSocket heartbeat timeout or network interruption | Implement automatic reconnection in client; use `graphql-ws` `connectionInitWaitTimeout` |
| Partial resolver failure | One field resolver throws while others succeed | Return partial data with `errors` array per GraphQL spec; log failed resolver with context |
| Schema stitching conflict | Duplicate type names when merging multiple schema modules | Use schema namespacing or federation with `@key` directives to resolve type ownership |

Refer to [`references/errors.md`](references/errors.md) for comprehensive error patterns.

## Examples

**E-commerce product catalog**: Schema with `Product`, `Category`, `Review` types, DataLoader-backed resolvers for nested queries like `products { reviews { author } }`, and a `productUpdated` subscription for inventory changes.

**Multi-tenant SaaS dashboard**: Code-first schema using TypeGraphQL decorators, tenant-scoped resolvers extracting `tenantId` from JWT context, and field-level visibility based on subscription plan tier.

**Federated microservice graph**: Apollo Federation with `@key` and `@external` directives across User, Order, and Product subgraphs, composed into a unified supergraph with a gateway router.

See [`references/examples.md`](references/examples.md) for additional examples.

## Resources

- GraphQL Specification: https://spec.graphql.org/
- Apollo Server documentation: https://www.apollographql.com/docs/apollo-server/
- DataLoader pattern: https://github.com/graphql/dataloader
- `graphql-ws` protocol: https://github.com/enisdenjo/graphql-ws
