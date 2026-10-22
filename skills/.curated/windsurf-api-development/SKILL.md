---
name: windsurf-api-development
description: 'Generate API clients and documentation with Cascade. Activate when users
  mention

  "generate api client", "api documentation", "openapi generation", "sdk generation",

  or "api integration". Handles API development workflows. Use when working with APIs
  or building integrations. Trigger with phrases like "windsurf api development",
  "windsurf development", "windsurf".

  '
allowed-tools: Read,Write,Edit,Bash(cmd:*),Grep
version: 1.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- skill-databases
- api
- workflow
compatibility: Designed for Claude Code
---
# Windsurf Api Development

## Overview

This skill enables AI-assisted API development workflows within Windsurf. Cascade can generate type-safe API clients from OpenAPI/Swagger specs, create comprehensive API documentation, design REST and GraphQL schemas, and produce SDKs for multiple languages.

## Prerequisites

- Windsurf IDE with Cascade enabled
- OpenAPI/Swagger specification or API endpoints
- Target language runtime (Node.js, Python, etc.)
- Understanding of API design patterns
- Documentation requirements defined

## Instructions

1. **Define API Specification**
2. **Generate Clients**
3. **Implement Endpoints**
4. **Create Documentation**
5. **Test and Validate**

See [`references/implementation.md`](references/implementation.md) for detailed implementation guide.

## Output

- Generated API clients (TypeScript, Python, etc.)
- Type definitions and schemas
- API reference documentation
- Quick start guides and examples

## Error Handling

See [`references/errors.md`](references/errors.md) for comprehensive error handling.

## Examples

See [`references/examples.md`](references/examples.md) for detailed examples.

## Resources

- [Windsurf API Development](https://docs.windsurf.ai/features/api-development)
- [OpenAPI Specification](https://swagger.io/specification/)
- [API Design Best Practices](https://docs.windsurf.ai/guides/api-design)
