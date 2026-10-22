---
name: windsurf-extension-pack
description: 'Install and configure essential Windsurf extensions for productivity.
  Activate when users mention

  "install extensions", "setup windsurf plugins", "configure extensions", "extension
  recommendations",

  or "productivity extensions". Handles extension installation and configuration.
  Use when working with windsurf extension pack functionality. Trigger with phrases
  like "windsurf extension pack", "windsurf pack", "windsurf".

  '
allowed-tools: Read,Write,Bash(cmd:*)
version: 1.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- skill-databases
- windsurf-extension
compatibility: Designed for Claude Code
---
# Windsurf Extension Pack

## Overview

This skill enables rapid setup of Windsurf with essential extensions for productive development. It covers language support, linting, formatting, Git integration, and productivity tools.

## Prerequisites

- Windsurf IDE installed
- Internet connection for extension downloads
- Admin rights for system-wide extensions (optional)
- Understanding of team development requirements
- List of required language support needs

## Instructions

1. **Assess Requirements**
2. **Install Core Extensions**
3. **Configure Extension Settings**
4. **Create Team Configuration**
5. **Document and Share**

See [`references/implementation.md`](references/implementation.md) for detailed implementation guide.

## Output

- Fully configured Windsurf environment
- extensions.json with team recommendations
- settings.json with extension configurations
- Documentation for extension usage

## Error Handling

See [`references/errors.md`](references/errors.md) for comprehensive error handling.

## Examples

See [`references/examples.md`](references/examples.md) for detailed examples.

## Resources

- [Windsurf Extension Marketplace](https://marketplace.windsurf.ai)
- [Extension Development Guide](https://docs.windsurf.ai/extensions/development)
- [Team Extension Management](https://docs.windsurf.ai/admin/extensions)
