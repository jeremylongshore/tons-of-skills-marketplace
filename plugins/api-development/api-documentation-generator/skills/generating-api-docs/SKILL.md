---
name: generating-api-docs
description: 'Create comprehensive API documentation with examples, authentication
  guides, and SDKs.

  Use when creating comprehensive API documentation.

  Trigger with phrases like "generate API docs", "create API documentation", or "document
  the API".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(api:docs-*)
version: 1.28.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- api
- authentication
- api-docs
compatibility: Designed for Claude Code
---
# Generating API Documentation

## Overview

Create comprehensive, interactive API documentation from OpenAPI specifications with runnable code examples, authentication guides, error reference tables, and SDK quick-start tutorials. Generate documentation sites using Redoc, Stoplight Elements, or Swagger UI with custom branding, versioned navigation, and full-text search.

## Prerequisites

- OpenAPI 3.0+ specification with descriptions, examples, and complete schema definitions
- Documentation generator: Redoc, Stoplight Elements, Swagger UI, or Docusaurus with OpenAPI plugin
- Code example generator for multiple languages (curl, JavaScript, Python, Go)
- Static site hosting for documentation deployment (GitHub Pages, Netlify, Vercel)
- Custom branding assets (logo, color scheme) for white-labeled documentation

## Instructions

1. Read the OpenAPI specification using Read and audit documentation completeness: verify all operations have `summary`, `description`, parameter descriptions, and at least one example per request/response.
2. Enrich the specification with long-form descriptions using Markdown: add getting-started guides, authentication flow explanations, and rate limiting documentation in the `info.description` or `x-documentation` extensions.
3. Generate interactive documentation using Redoc or Stoplight Elements with "Try It" functionality that allows consumers to execute requests directly from the documentation page.
4. Create runnable code examples for every endpoint in curl, JavaScript (fetch/axios), Python (requests/httpx), and Go (net/http), with proper authentication header injection.
5. Build an authentication guide covering all supported auth schemes: API key setup, OAuth2 authorization code flow walkthrough, JWT token lifecycle, and credential rotation procedures.
6. Add an error reference section that documents every error code, its meaning, common causes, and resolution steps -- organized by HTTP status code with searchable error code index.
7. Configure documentation versioning so consumers can switch between API versions (v1, v2) with visual diff highlighting showing changes between versions.
8. Set up automated documentation deployment: on OpenAPI spec changes, regenerate the documentation site and deploy to hosting with cache invalidation.

See [`references/implementation.md`](references/implementation.md) for the full implementation guide.

## Output

- `${CLAUDE_SKILL_DIR}/docs/site/` - Generated documentation website (HTML/CSS/JS)
- `${CLAUDE_SKILL_DIR}/docs/guides/authentication.md` - Authentication flow guide with code examples
- `${CLAUDE_SKILL_DIR}/docs/guides/getting-started.md` - Quick-start tutorial for first API call
- `${CLAUDE_SKILL_DIR}/docs/reference/errors.md` - Complete error code reference with resolution steps
- `${CLAUDE_SKILL_DIR}/docs/examples/` - Per-endpoint code examples in multiple languages
- `${CLAUDE_SKILL_DIR}/docs/config/redoc.yaml` - Documentation generator configuration with branding

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Missing examples | OpenAPI spec lacks `example` or `examples` for request/response schemas | Generate examples from schema using Faker-based data; flag missing examples in spec linting |
| Stale documentation | Docs deployed from an older spec version than the running API | Tie doc deployment to API deployment pipeline; version docs alongside API releases |
| Broken Try-It requests | CORS not configured for documentation domain on the API server | Add documentation domain to CORS `Access-Control-Allow-Origin`; or use a proxy for Try-It requests |
| Code example errors | Generated code example uses deprecated SDK method or wrong import path | Auto-test code examples against a staging API; version examples alongside SDK releases |
| Search not working | Full-text search index not rebuilt after content update | Include search index regeneration in documentation build pipeline; verify Algolia/Lunr config |

Refer to [`references/errors.md`](references/errors.md) for comprehensive error patterns.

## Examples

**Stripe-style API docs**: Generate a three-column documentation layout with navigation on the left, description in the center, and code examples on the right, with language switcher for curl/Node/Python/Ruby.

**Versioned documentation site**: Host v1 and v2 documentation side-by-side with a version switcher dropdown, and a changelog page highlighting breaking changes and migration steps between versions.

**Developer portal**: Combine API reference docs with getting-started tutorials, use-case guides, webhooks documentation, and SDK installation instructions in a single searchable portal.

See [`references/examples.md`](references/examples.md) for additional examples.

## Resources

- Redoc documentation generator: https://redocly.com/redoc
- Stoplight Elements: https://stoplight.io/open-source/elements
- Swagger UI: https://swagger.io/tools/swagger-ui/
- Documentation best practices: Stripe, Twilio, and GitHub API docs as exemplars
