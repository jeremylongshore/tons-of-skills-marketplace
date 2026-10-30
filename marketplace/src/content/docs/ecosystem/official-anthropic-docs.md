---
title: 'Official Anthropic Documentation Links'
description: 'Organized directory of official Anthropic documentation for Claude Code. Find the right reference for skills, plugins, agents, hooks, MCP, CLI usage, and best practices.'
section: 'ecosystem'
order: 2
keywords:
  - "Anthropic documentation"
  - "Claude Code docs"
  - "official docs"
  - "Claude Code reference"
  - "skills documentation"
  - "plugins documentation"
  - "MCP documentation"
  - "Claude Code CLI"
officialLinks:
  - title: 'Claude Code Overview'
    url: 'https://code.claude.com/docs/en/overview'
  - title: 'Claude Code Skills'
    url: 'https://code.claude.com/docs/en/skills'
  - title: 'Claude Code Plugins'
    url: 'https://code.claude.com/docs/en/plugins'
  - title: 'Claude Code Agents'
    url: 'https://code.claude.com/docs/en/sub-agents'
  - title: 'Claude Code Hooks'
    url: 'https://code.claude.com/docs/en/hooks'
  - title: 'Claude Code MCP'
    url: 'https://code.claude.com/docs/en/mcp'
  - title: 'Claude Code CLI Reference'
    url: 'https://code.claude.com/docs/en/cli-reference'
  - title: 'Claude Code Best Practices'
    url: 'https://code.claude.com/docs/en/best-practices'
relatedDocs:
  - 'ecosystem/marketplace-overview'
  - 'ecosystem/community-resources'
  - 'ecosystem/faq'
---

## Overview

Use primary Claude Code documentation for platform behavior. This marketplace adds repository-specific metadata, validation, static grading, and contribution rules; it does not replace the platform specification or make every example a production certification.

The catalog and public search inventory change over time. Use the site's generated public counts rather than a hard-coded plugin or skill total in this directory.

## Primary reference directory

| Topic                       | Primary source                                                                                                | What it owns                                                     |
| --------------------------- | ------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| Claude Code                 | [Overview](https://code.claude.com/docs/en/overview)                                                          | Product setup and capabilities                                   |
| Plugins                     | [Plugin reference](https://code.claude.com/docs/en/plugins-reference)                                         | Native layout, manifest, component paths, and substitutions      |
| Installation and management | [Discover plugins](https://code.claude.com/docs/en/discover-plugins)                                          | Marketplace registration, scopes, install, update, and uninstall |
| Skills and legacy commands  | [Skills](https://code.claude.com/docs/en/skills)                                                              | Invocation, frontmatter, context, and command-file compatibility |
| Subagents                   | [Subagents](https://code.claude.com/docs/en/sub-agents)                                                       | Agent definitions, delegation, tools, and model settings         |
| Hooks                       | [Hooks](https://code.claude.com/docs/en/hooks)                                                                | Event schema, stdin payloads, decisions, and exit behavior       |
| MCP integration             | [Claude Code MCP](https://code.claude.com/docs/en/mcp)                                                        | Client configuration and supported connections                   |
| Native CLI                  | [CLI reference](https://code.claude.com/docs/en/cli-reference)                                                | Claude commands and flags                                        |
| Editor integrations         | [VS Code](https://code.claude.com/docs/en/vs-code) and [JetBrains](https://code.claude.com/docs/en/jetbrains) | Integration-specific setup and behavior                          |

The broad `/agents` page covers parallel work; the specific agent-definition authority is `/sub-agents`. Older slash-command links may resolve to skills documentation because command files and skills share that reference.

## Skills: native format versus marketplace requirements

The [Agent Skills specification](https://agentskills.io/specification) and Claude's native skill reference describe their own permissive formats. This repository independently requires all eight marketplace fields: `name`, `description`, `allowed-tools`, `version`, `author`, `license`, `compatibility`, and `tags`. Missing fields are errors at marketplace tier. Do not present those stricter requirements as optional polish or silently remove them to match the native floor.

`allowed-tools` preapproves tools for an invocation; it is not an exclusive sandbox. Manual invocation does not require `argument-hint`. `user-invocable: false` blocks direct user invocation; `disable-model-invocation` separately controls model invocation.

`effort` is supported for skills as well as agents. Its current five values are model-dependent. Check the primary page for runtime behavior and the unchanged local schema for marketplace acceptance.

## Agents and hooks

Agents support a `tools` allowlist and `disallowedTools` denylist. Do not infer native capability controls from fields named `capabilities`, `expertise_level`, or `activation_priority`; the local validator rejects them. Plugin agents and standalone definitions also have different local restrictions.

Hooks use named lifecycle events such as `PreToolUse`, `PostToolUse`, and `SessionStart`, not invented `pre-tool-call` keys. A command hook reads event JSON from stdin. Exit 2 is a documented blocking mechanism for applicable events; arbitrary nonzero statuses are not a universal blocking contract, and post-tool hooks cannot undo an executed action.

## MCP protocol and SDK sources

MCP is not the Anthropic Messages API. `@anthropic-ai/sdk` is not the MCP server SDK. Use the [MCP specification](https://modelcontextprotocol.io/specification/2025-11-25) and the appropriate official SDK, such as the [TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk), for server development.

Select a coherent pinned SDK generation. The maintained v1 `@modelcontextprotocol/sdk` API and v2 APIs differ; do not combine their examples. Standard transports include stdio and Streamable HTTP; legacy HTTP+SSE compatibility is a separate concern.

## This marketplace's role

Anthropic publishes official marketplaces. Tons of Skills is a complementary catalog with its own contribution workflow, source provenance, and stricter metadata and static gates. Search results, grades, and badges do not substitute for reviewing source or verifying a live integration.

The canonical repository is [jeremylongshore/tons-of-skills-marketplace](https://github.com/jeremylongshore/tons-of-skills-marketplace). Its `STANDARDS.md` authority index points to the canonical local standards. This directory links to owners; it does not adopt a new schema, security policy, or kernel version.
