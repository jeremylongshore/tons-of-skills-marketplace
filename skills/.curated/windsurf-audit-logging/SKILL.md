---
name: windsurf-audit-logging
description: 'Configure AI interaction audit logging for compliance. Activate when
  users mention

  "audit logging", "compliance logging", "ai interaction logs", "security audit",

  or "activity tracking". Handles compliance and audit configuration. Use when analyzing
  or auditing windsurf audit logging. Trigger with phrases like "windsurf audit logging",
  "windsurf logging", "windsurf".

  '
allowed-tools: Read,Write,Edit,Bash(cmd:*)
version: 1.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- skill-databases
- security
- logging
- compliance
compatibility: Designed for Claude Code
---
# Windsurf Audit Logging

## Overview

This skill enables comprehensive audit logging for Windsurf Enterprise deployments. It covers AI interaction logging, file access tracking, authentication events, and configuration changes.

## Prerequisites

- Windsurf Enterprise subscription
- Organization administrator access
- Compliance requirements documented
- Log storage infrastructure
- SIEM integration (optional but recommended)

## Instructions

1. **Enable Audit Logging**
2. **Configure Event Types**
3. **Set Up Integrations**
4. **Create Reports**
5. **Monitor and Alert**

See [`references/implementation.md`](references/implementation.md) for detailed implementation guide.

## Output

- Configured audit log streams
- SIEM integration
- Automated reports
- Alert configurations

## Error Handling

See [`references/errors.md`](references/errors.md) for comprehensive error handling.

## Examples

See [`references/examples.md`](references/examples.md) for detailed examples.

## Resources

- [Windsurf Audit Logging Guide](https://docs.windsurf.ai/admin/audit)
- [SOC 2 Compliance Documentation](https://docs.windsurf.ai/compliance/soc2)
- [SIEM Integration Guide](https://docs.windsurf.ai/admin/siem)
