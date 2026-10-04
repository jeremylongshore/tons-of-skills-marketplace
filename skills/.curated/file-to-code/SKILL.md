---
name: file-to-code
description: 'Generates production-ready code from file specifications such as CSV
  files,

  JSON schemas, SQL DDL, protobuf definitions, or requirements documents. Use

  when the user wants to convert a data file or specification into working code.

  Trigger with phrases like "generate code from this CSV", "create an API from

  this schema", "build a parser for this file", or "turn this spec into code".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(pip:*), Bash(node:*), Bash(python3:*),
  Glob, Grep
version: 0.17.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- code-generation
- requirements
- automation
- api-design
compatibility: Designed for Claude Code
---
# File to Code

Generate production-ready code from file specifications, data schemas, and requirements documents.

## Overview

This skill reads structured input files -- CSV data, JSON schemas, SQL DDL statements, protobuf definitions, OpenAPI specs, or plain-text requirements -- and generates complete, production-ready code to process, serve, or transform that data. Instead of manually writing boilerplate models, validation logic, and CRUD endpoints, this skill analyzes the input structure and produces well-typed code with proper error handling, input validation, and test coverage.

The skill supports multiple output languages and frameworks. It infers types from data samples, respects constraints defined in schemas, and follows best practices for the target framework. When generating API endpoints, it includes request validation, error responses, and OpenAPI documentation. When generating data processing pipelines, it includes type coercion, null handling, and logging.

## Instructions

1. **Point to the input file** or paste its contents:
   - "Read `data/users.csv` and generate a REST API for it"
   - "Here's my JSON schema: `{ ... }` -- generate TypeScript types and a validator"
   - "Create a data pipeline from `schema.sql`"

2. **Specify the target language and framework** (optional -- the skill will infer reasonable defaults):
   - Language: TypeScript, Python, Go, Rust, Java
   - Framework: Express, FastAPI, Gin, Actix, Spring Boot
   - If unspecified, defaults to TypeScript with Express for APIs, or Python for data processing

3. **Indicate the scope** of what you want generated:
   - "Just the types" -- generates type definitions and interfaces only
   - "Full CRUD API" -- generates routes, controllers, models, validation, and tests
   - "Parser only" -- generates a file reader/parser with error handling
   - "Everything" -- generates the full stack: types, API, tests, and documentation

4. **Review the generated code.** The skill creates files in your project directory following standard conventions (e.g., `src/models/`, `src/routes/`, `tests/`). Inspect the output and request adjustments if needed.

## Output

Depending on the input and requested scope, the skill generates:

- **Type Definitions**: Interfaces, types, or structs matching the input schema with proper nullability and constraints.
- **Validation Logic**: Input validation using libraries appropriate to the target framework (Zod for TypeScript, Pydantic for Python, etc.).
- **API Endpoints**: RESTful routes with CRUD operations, request/response typing, error handling, and pagination support.
- **Data Processors**: File readers, parsers, and transformation pipelines with type coercion and error recovery.
- **Test Suites**: Unit tests covering happy paths, edge cases, and error conditions using the project's test framework.
- **OpenAPI Spec**: Auto-generated API documentation in OpenAPI 3.0 format when generating API endpoints.

## Examples

### Example 1: CSV to REST API

**User:** "Read `data/products.csv` and generate a FastAPI app to serve this data."

The skill will:

1. Read the CSV file and analyze column names, data types, and sample values.
2. Generate a Pydantic model (`Product`) with fields inferred from the CSV headers.
3. Create FastAPI routes: `GET /products`, `GET /products/{id}`, `POST /products`, `PUT /products/{id}`, `DELETE /products/{id}`.
4. Add CSV ingestion logic to seed an SQLite database on startup.
5. Generate pytest tests for each endpoint.

### Example 2: JSON Schema to TypeScript

**User:** "Here's my API response schema. Generate TypeScript types and a Zod validator."

The skill will:

1. Parse the JSON Schema, resolving `$ref` references and nested objects.
2. Generate TypeScript interfaces for each schema definition.
3. Create corresponding Zod schemas that enforce the same constraints (required fields, string patterns, numeric ranges).
4. Export a `validate` function that returns typed, validated data or a structured error.

### Example 3: SQL DDL to Go Models

**User:** "Read `migrations/001_create_tables.sql` and generate Go structs with sqlc-compatible annotations."

The skill will:

1. Parse CREATE TABLE statements to extract table names, columns, types, and constraints.
2. Map SQL types to Go types (e.g., `VARCHAR` to `string`, `TIMESTAMP` to `time.Time`, `BOOLEAN` to `bool`).
3. Generate Go struct definitions with `db` and `json` tags.
4. Create a `queries.sql` file with standard CRUD queries for sqlc to process.

## Error Handling

- **Unrecognized file format:** Prompts the user to specify the format or provide a sample of the expected structure.
- **Ambiguous types:** When column types cannot be inferred from data alone, asks the user to clarify (e.g., "Is `status` an enum or a free-text string?").
- **Missing dependencies:** Lists required packages (e.g., `pip install fastapi uvicorn`) and offers to generate a `requirements.txt` or `package.json`.
- **Large files:** For files with many columns or tables, generates code incrementally and confirms scope before proceeding.

## Prerequisites

- Input file accessible on disk (CSV, JSON Schema, SQL DDL, protobuf, or OpenAPI spec)
- Target language runtime installed (Node.js, Python, Go, etc.)
- Package manager available (`npm` or `pip`) for installing generated dependencies

## Resources

- [JSON Schema specification](https://json-schema.org/) — schema definition reference
- [OpenAPI 3.0 specification](https://spec.openapis.org/oas/v3.0.3) — API description format
- [Zod documentation](https://zod.dev/) — TypeScript-first schema validation
