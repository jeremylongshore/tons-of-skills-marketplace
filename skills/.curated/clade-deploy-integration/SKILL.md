---
name: clade-deploy-integration
description: 'Deploy Claude-powered applications to Vercel, Fly.io, and Cloud Run

  Use when working with deploy-integration patterns.

  with proper secrets management and streaming support.

  Trigger with "deploy anthropic", "claude production deploy",

  "anthropic vercel", "deploy claude app".

  '
allowed-tools: Read, Write, Edit, Bash(vercel:*), Bash(fly:*), Bash(gcloud:*)
version: 1.1.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- anthropic
- claude
- deploy
- production
compatibility: Designed for Claude Code
---
# Deploy Anthropic Integration

## Overview

Claude integrations are stateless API wrappers — a serverless function receives a user request, streams from the Messages API, and returns the response. No database, no connection pool, no persistent state.

## Vercel Edge Function (Recommended)

```typescript
// app/api/chat/route.ts (Next.js App Router)
import Anthropic from '@claude-ai/sdk';

export const runtime = 'edge';

export async function POST(req: Request) {
  const client = new Anthropic();
  const { messages, system } = await req.json();

  const stream = await client.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 4096,
    system: system || 'You are a helpful assistant.',
    messages,
    stream: true,
  });

  // Convert Anthropic stream to ReadableStream for SSE
  const encoder = new TextEncoder();
  const readable = new ReadableStream({
    async start(controller) {
      for await (const event of stream) {
        if (event.type === 'content_block_delta' && event.delta.type === 'text_delta') {
          controller.enqueue(encoder.encode(`data: ${JSON.stringify(event.delta)}\n\n`));
        }
      }
      controller.enqueue(encoder.encode('data: [DONE]\n\n'));
      controller.close();
    },
  });

  return new Response(readable, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
    },
  });
}
```

## Instructions

### Step 1: Deploy to Vercel

```bash
# Add secret
vercel env add ANTHROPIC_API_KEY

# Deploy
vercel --prod
```

## Fly.io (Long-Running / WebSocket)

```dockerfile
FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
```

```bash
fly launch --name my-claude-app
fly secrets set ANTHROPIC_API_KEY=sk-ant-api03-...
fly deploy
```

## Google Cloud Run

```bash
gcloud run deploy claude-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-secrets=ANTHROPIC_API_KEY=claude-key:latest \
  --timeout=300 \
  --concurrency=80
```

## Health Check

```typescript
// api/health.ts
import Anthropic from '@claude-ai/sdk';

export async function GET() {
  try {
    const client = new Anthropic();
    const msg = await client.messages.create({
      model: 'claude-haiku-4-5-20251001',
      max_tokens: 5,
      messages: [{ role: 'user', content: 'ping' }],
    });
    return Response.json({ status: 'healthy', model: msg.model });
  } catch (err) {
    return Response.json({ status: 'unhealthy', error: err.message }, { status: 503 });
  }
}
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | API key from console.anthropic.com |
| `ANTHROPIC_MODEL` | No | Default model ID (override per request) |
| `ANTHROPIC_MAX_TOKENS` | No | Default max tokens |

## Output

- Application deployed to chosen platform with streaming support
- `ANTHROPIC_API_KEY` stored in platform secrets manager
- Health check endpoint returning Claude connectivity status
- Environment-specific configuration (model, max_tokens) in place

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| `FUNCTION_INVOCATION_TIMEOUT` | Claude response > function timeout | Set timeout to 300s. Use streaming. |
| Secret not found | Missing env var | Add via platform CLI |
| 529 in production | API overloaded | SDK retries automatically. Add fallback model. |
| CORS errors | Missing headers | Add CORS headers to API route |

## Examples

See Vercel Edge Function (with SSE streaming), Fly.io Dockerfile, Cloud Run deploy script, and Health Check endpoint above.

## Resources

- [Anthropic API Docs](https://platform.claude.com/docs/en/api/overview)
- [Vercel AI SDK](https://sdk.vercel.ai/docs) (optional higher-level wrapper)

## Next Steps

See `clade-observability` for monitoring your Claude calls in production.

## Prerequisites

- Completed `clade-install-auth` and `clade-prod-checklist`
- Production Anthropic API key (separate from dev key)
- Platform CLI installed: `vercel`, `fly`, or `gcloud`
- Application code tested locally
