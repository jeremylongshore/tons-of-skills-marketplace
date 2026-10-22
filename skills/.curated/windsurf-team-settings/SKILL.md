---
name: windsurf-team-settings
description: 'Manage team-wide Windsurf settings and AI policies. Activate when users
  mention

  "team settings", "organization config", "team policies", "shared settings",

  or "team standardization". Handles team configuration management. Use when working
  with windsurf team settings functionality. Trigger with phrases like "windsurf team
  settings", "windsurf settings", "windsurf".

  '
allowed-tools: Read,Write,Edit
version: 1.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- skill-databases
- windsurf-team
compatibility: Designed for Claude Code
---
# Windsurf Team Settings

## Overview

This skill enables centralized management of Windsurf settings across teams and organizations. It covers editor preferences, AI behavior policies, tool approvals, and compliance requirements.

## Prerequisites

- Windsurf Enterprise subscription
- Organization administrator role
- Understanding of team structure and needs
- Compliance requirements documentation
- Team feedback on desired settings

## Instructions

1. **Define Organization Defaults**
2. **Create Team Overrides**
3. **Set Up Policies**
4. **Deploy Settings**
5. **Monitor and Iterate**

See [`references/implementation.md`](references/implementation.md) for detailed implementation guide.

## Output

- Organization-wide settings configuration
- Team-specific override files
- Policy documentation
- Compliance reports

## Error Handling

See [`references/errors.md`](references/errors.md) for comprehensive error handling.

## Examples

See [`references/examples.md`](references/examples.md) for detailed examples.

## Resources

- [Windsurf Team Administration](https://docs.windsurf.ai/admin/team-settings)
- [Policy Configuration Guide](https://docs.windsurf.ai/admin/policies)
- [Settings Sync Documentation](https://docs.windsurf.ai/features/settings-sync)
