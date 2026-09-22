---
name: anima-deploy-integration
description: 'Deploy Anima design-to-code service as a backend API endpoint.

  Use when building a design-to-code microservice, deploying Anima SDK

  as a serverless function, or creating an internal design tool API.

  Trigger with: "deploy anima", "anima service deploy", "anima serverless".

  '
allowed-tools: Read, Write, Edit, Bash(vercel:*), Bash(gcloud:*), Bash(docker:*)
version: 2.0.0
argument-hint: "[deployment-target]"
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- design
- figma
- anima
- deployment
compatibility: Requires Node.js 20+, approved Anima API access, current Anima SDK documentation, and authorized Figma or website source access
---
# Anima Deploy Integration

## Overview

Deploy the Anima SDK as a backend service. The SDK is server-side only, so deploy it behind an API endpoint that accepts Figma file/node references and returns generated code.

## Prerequisites

- A private or authenticated service boundary with an allowlisted design-file
  registry; do not expose arbitrary `fileKey` and `nodesId` generation to the
  public internet.
- Managed Anima and Figma secrets, separate staging/production credentials,
  request limits, and an audit trail that excludes token values and design
  content.
- An approved generated-output path, validation pipeline, and rollback target
  for every deployment revision.

## Instructions

### Step 1: Express API Wrapper

```typescript
// src/server.ts
import express from 'express';
import { Anima } from '@animaapp/anima-sdk';

const app = express();
app.use(express.json());

const anima = new Anima({ auth: { token: process.env.ANIMA_TOKEN! } });

app.post('/api/generate', async (req, res) => {
  const { fileKey, nodesId, settings } = req.body;

  if (!fileKey || !nodesId?.length) {
    return res.status(400).json({ error: 'fileKey and nodesId required' });
  }

  try {
    const { files } = await anima.generateCode({
      fileKey,
      figmaToken: process.env.FIGMA_TOKEN!,
      nodesId,
      settings: settings || { language: 'typescript', framework: 'react', styling: 'tailwind' },
    });
    res.json({ files, count: Object.keys(files).length });
  } catch (err: any) {
    res.status(502).json({ error: 'Generation failed', requestId: req.id });
  }
});

app.get('/health', (_req, res) => res.json({ status: 'ok' }));
app.listen(3000, () => console.log('Anima service on :3000'));
```

### Step 2: Vercel Serverless Function

```typescript
// api/generate.ts
import { Anima } from '@animaapp/anima-sdk';

const anima = new Anima({ auth: { token: process.env.ANIMA_TOKEN! } });

export default async function handler(req: any, res: any) {
  if (req.method !== 'POST') return res.status(405).end();

  const { fileKey, nodesId, settings } = req.body;
  const { files } = await anima.generateCode({
    fileKey, figmaToken: process.env.FIGMA_TOKEN!, nodesId,
    settings: settings || { language: 'typescript', framework: 'react', styling: 'tailwind' },
  });
  res.json({ files });
}
```

### Step 3: Deploy Commands

```bash
# Vercel
vercel secrets add anima_token "$ANIMA_TOKEN"
vercel secrets add figma_token "$FIGMA_TOKEN"
vercel --prod

# Cloud Run
gcloud run deploy anima-service \
  --source . \
  --set-secrets=ANIMA_TOKEN=anima-token:latest,FIGMA_TOKEN=figma-token:latest \
  --region us-central1 --no-allow-unauthenticated
```

## Tool Discipline

Use Read and Grep to inspect the existing integration and generated diff before changing anything. Use Write or Edit only inside the approved generated-code, test, or configuration paths. Use the declared Bash commands only for the explicit install, validation, or diagnostic steps in this workflow; never print tokens, source designs, generated source, or private website captures.

## Output

- Express API wrapping Anima SDK for internal design tooling
- Vercel serverless function for lightweight deployment
- Cloud Run deployment with Secret Manager

## Examples

Deploy the service to a staging environment behind the organization’s existing
identity proxy and invoke `/api/generate` with one allowlisted file/node pair.
Verify the request is authorized, output remains in the approved generated-code
location, logs contain only request metadata, and generated files pass the
downstream formatter and test gate before a human reviews them. If an unauthenticated
caller, unknown node, or secret-binding error reaches the service, reject the
request, alert the operator, and keep the prior revision active rather than
opening broad access or embedding credentials in the client.

## Error Handling

| Failure | Response |
|---------|----------|
| Caller is not authenticated or file/node is not allowlisted | Reject before contacting Anima or Figma. |
| Managed secret is unavailable | Fail closed and repair the deployment binding; never use a plaintext fallback. |
| Generation or validation fails | Return a sanitized failure, preserve the prior revision, and quarantine the output. |
| Rate limit or repeated bad requests occur | Apply bounded throttling and alert the owning service team. |

## Resources

- [Anima API](https://docs.animaapp.com/docs/anima-api)
- [Anima SDK Example Server](https://github.com/AnimaApp/anima-sdk)
