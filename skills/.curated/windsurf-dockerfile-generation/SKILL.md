---
name: windsurf-dockerfile-generation
description: 'Create optimized Dockerfiles with AI-driven best practices. Activate
  when users mention

  "create dockerfile", "container image", "docker optimization", "containerize application",

  or "docker best practices". Handles Docker configuration generation. Use when working
  with windsurf dockerfile generation functionality. Trigger with phrases like "windsurf
  dockerfile generation", "windsurf generation", "windsurf".

  '
allowed-tools: Read,Write,Edit,Bash(cmd:*)
version: 1.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- skill-databases
- docker
compatibility: Designed for Claude Code
---
# Windsurf Dockerfile Generation

## Overview

This skill enables AI-assisted Docker configuration within Windsurf. Cascade analyzes your application to generate optimized Dockerfiles with multi-stage builds, minimal base images, proper layer caching, and security best practices.

## Prerequisites

- Windsurf IDE with Cascade enabled
- Docker installed locally
- Application with defined dependencies
- Understanding of containerization concepts
- Target deployment environment defined

## Instructions

1. **Analyze Application**
2. **Select Base Image**
3. **Generate Dockerfile**
4. **Configure Security**
5. **Test and Validate**

See [`references/implementation.md`](references/implementation.md) for detailed implementation guide.

## Output

- Optimized production Dockerfile
- Development Dockerfile with dev tools
- docker-compose.yml for orchestration
- .dockerignore for build optimization

## Error Handling

See [`references/errors.md`](references/errors.md) for comprehensive error handling.

## Examples

See [`references/examples.md`](references/examples.md) for detailed examples.

## Resources

- [Windsurf Docker Guide](https://docs.windsurf.ai/features/docker)
- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Container Security Guide](https://docs.windsurf.ai/guides/container-security)
