---
name: anth-deploy-integration
description: 'Deploy Claude API integrations to production cloud environments.

  Use when deploying Claude-powered services to Docker, Cloud Run, ECS,

  or Kubernetes with proper secret management and health checks.

  Trigger with phrases like "deploy anthropic", "claude production deploy",

  "ship claude integration", "anthropic cloud deployment".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Grep
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- ai
- anthropic
compatibility: Designed for Claude Code
---
# Anthropic Deploy Integration

## Overview

Deploy Claude API integrations with proper secret management, health checks, and rollback procedures across Docker, GCP Cloud Run, and Kubernetes.

## Docker Deployment

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
ENV ANTHROPIC_API_KEY=""
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```python
# src/main.py
from fastapi import FastAPI, HTTPException
import anthropic

app = FastAPI()
client = anthropic.Anthropic()

@app.get("/health")
async def health():
    try:
        count = client.messages.count_tokens(
            model="claude-haiku-4-20250514",
            messages=[{"role": "user", "content": "ping"}]
        )
        return {"status": "healthy", "api": "connected"}
    except Exception as e:
        raise HTTPException(503, detail=str(e))
```

## GCP Cloud Run

```bash
echo -n "sk-ant-api03-..." | gcloud secrets create anthropic-key --data-file=-

gcloud run deploy claude-service \
  --image gcr.io/my-project/claude-service \
  --set-secrets ANTHROPIC_API_KEY=anthropic-key:latest \
  --min-instances 1 --max-instances 10 \
  --memory 512Mi --timeout 120s
```

## Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: claude-service }
spec:
  replicas: 3
  strategy: { type: RollingUpdate, rollingUpdate: { maxUnavailable: 1 } }
  template:
    spec:
      containers:
        - name: app
          env:
            - name: ANTHROPIC_API_KEY
              valueFrom:
                secretKeyRef: { name: anthropic-secrets, key: api-key }
          livenessProbe:
            httpGet: { path: /health, port: 8000 }
            periodSeconds: 30
```

## Rollback

```bash
# Cloud Run
gcloud run services update-traffic claude-service --to-revisions=PREVIOUS=100

# Kubernetes
kubectl rollout undo deployment/claude-service
```

## Error Handling

| Issue | Cause | Fix |
|-------|-------|-----|
| Container crash on start | Missing API key env var | Verify secret binding |
| Health check fails | Key invalid in prod | Test key with curl |
| 429 after scaling up | More replicas = more RPM | Shared rate limiter (Redis) |

## Prerequisites

- Have an approved artifact digest, environment/workspace mapping, secret-manager reference, health probe, deployment owner, canary plan, and tested rollback command.
- Use a least-privileged runtime identity and synthetic fixtures in staging; never embed API keys in images, manifests, command history, or deployment output.
- Define deployment SLOs for health, errors, latency, rate limits, cost, and data-policy checks, with explicit halt thresholds.

## Instructions

1. Build and scan the pinned artifact, bind the environment-specific secret at runtime, and verify that logs and probes cannot expose prompts, responses, or credentials.
2. Deploy to staging and run the token-count/health probe plus synthetic Messages API, error, timeout, rate-limit, and redaction tests. Confirm the workspace and model are approved.
3. Release to one sandbox or internal canary, monitor aggregate SLOs and `sensitive_content_logged=0`, and require owner approval before wider traffic.
4. Promote in bounded stages while preserving the prior revision and idempotent deployment record. Do not bypass failed health, authorization, or data-policy gates.
5. On failure, stop traffic, roll back to the prior revision, revoke temporary access, clean up staged artifacts under the retention policy, and issue a redacted deployment receipt.

## Output

Produce a deployment receipt containing artifact digest, environment/workspace class, model policy, probe/test results, canary scope, SLO outcomes, approval, rollout state, retention cleanup, and rollback reference. Exclude API keys, prompts, responses, customer identifiers, and raw stack traces.

## Examples

Deploy `artifact=sha256:fixture` to a staging workspace, run synthetic `fixture-request-001`, assert `workspace=staging; sensitive_content_logged=0`, then release a 1% internal canary. If the 5xx or latency gate fails, record `promotion=halted; rollback=previous-revision` and send no production traffic.

## Resources

- [API Getting Started](https://platform.claude.com/docs/en/api/overview)
- [API Status](https://status.anthropic.com)

## Next Steps

For event-driven patterns, see `anth-webhooks-events`.
