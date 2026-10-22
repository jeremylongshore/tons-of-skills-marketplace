---
name: windsurf-license-management
description: 'Manage Windsurf licenses and seat allocation. Activate when users mention

  "license management", "seat allocation", "billing optimization", "user licenses",

  or "subscription management". Handles license administration. Use when working with
  windsurf license management functionality. Trigger with phrases like "windsurf license
  management", "windsurf management", "windsurf".

  '
allowed-tools: Read,Write,Edit
version: 1.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- skill-databases
- windsurf-license
compatibility: Designed for Claude Code
---
# Windsurf License Management

## Overview

This skill enables enterprise license management for Windsurf deployments. It covers seat allocation, usage tracking, cost optimization, and compliance reporting.

## Prerequisites

- Windsurf Enterprise subscription with admin access
- Organization administrator role
- Access to billing portal
- User directory integration (optional: SCIM, Azure AD, Okta)
- Understanding of organization structure and teams

## Instructions

1. **Inventory Current Licenses**
2. **Set Allocation Policies**
3. **Configure Usage Tracking**
4. **Optimize Subscription**
5. **Monitor and Report**

See [`references/implementation.md`](references/implementation.md) for detailed implementation guide.

## Output

- License inventory with current allocations
- Utilization reports with recommendations
- Cost analysis with optimization opportunities
- Compliance reports for audits

## Error Handling

See [`references/errors.md`](references/errors.md) for comprehensive error handling.

## Examples

See [`references/examples.md`](references/examples.md) for detailed examples.

## Resources

- [Windsurf License Administration](https://docs.windsurf.ai/admin/licensing)
- [SCIM Integration Guide](https://docs.windsurf.ai/admin/scim)
- [Cost Optimization Best Practices](https://docs.windsurf.ai/admin/cost-optimization)
