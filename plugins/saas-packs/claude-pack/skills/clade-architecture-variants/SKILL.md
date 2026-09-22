---
name: clade-architecture-variants
description: "Build different types of Claude-powered applications \u2014 chatbots,\
  \ RAG systems,\nUse when working with architecture-variants patterns.\nagents, content\
  \ pipelines, and code generation tools.\nTrigger with \"claude architecture\", \"\
  anthropic rag\", \"build with claude\",\n\"claude agent pattern\", \"anthropic app\
  \ design\".\n"
allowed-tools: Read, Write, Edit
version: 1.1.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- anthropic
- claude
- architecture
- rag
- agents
compatibility: Designed for Claude Code
---
# Claude Architecture Variants

## Overview

Five architecture patterns for Claude-powered applications: Chatbot (stateless API wrapper), RAG (retrieval-augmented generation with vector search), Agent (tool use loop), Content Pipeline (batch processing), and Evaluation (using Claude as a judge). Each includes complete code and a comparison table.

## 1. Chatbot (Stateless API Wrapper)

Simplest pattern — proxy Claude with a system prompt.

```typescript
// api/chat.ts
export async function POST(req: Request) {
  const { messages } = await req.json();
  const response = await client.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 2048,
    system: 'You are a helpful assistant for our SaaS product.',
    messages,
    stream: true,
  });
  return new Response(response.toReadableStream());
}
```

**Best for:** Customer support, Q&A, simple conversational interfaces.

## 2. RAG (Retrieval-Augmented Generation)

Fetch relevant context, inject into prompt, generate grounded answer.

```typescript
async function ragQuery(question: string) {
  // 1. Embed the question (use Voyage, OpenAI, or Cohere — not Anthropic)
  const embedding = await embeddingClient.embed(question);

  // 2. Search vector DB for relevant chunks
  const chunks = await vectorDb.query(embedding, { topK: 5 });

  // 3. Send to Claude with context
  const message = await client.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 2048,
    system: `Answer based on the provided context. If the context doesn't contain the answer, say so.`,
    messages: [{
      role: 'user',
      content: `Context:\n${chunks.map(c => c.text).join('\n---\n')}\n\nQuestion: ${question}`,
    }],
  });
  return message.content[0].text;
}
```

**Best for:** Documentation Q&A, knowledge bases, support with source citations.

## 3. Agent (Tool Use Loop)

Claude decides which tools to call, you execute them, loop until done.

```typescript
async function agentLoop(userInput: string, tools: Anthropic.Tool[]) {
  let messages: MessageParam[] = [{ role: 'user', content: userInput }];

  while (true) {
    const response = await client.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 4096,
      tools,
      messages,
    });
    messages.push({ role: 'assistant', content: response.content });

    if (response.stop_reason === 'end_turn') {
      return response.content.find(b => b.type === 'text')?.text;
    }

    // Execute tools
    const results = [];
    for (const block of response.content) {
      if (block.type === 'tool_use') {
        const result = await executeTool(block.name, block.input);
        results.push({ type: 'tool_result', tool_use_id: block.id, content: JSON.stringify(result) });
      }
    }
    messages.push({ role: 'user', content: results });
  }
}
```

**Best for:** Data analysis, code generation, multi-step workflows.

## 4. Content Pipeline (Batch Processing)

Process thousands of documents through Claude asynchronously.

```typescript
const batch = await client.messages.batches.create({
  requests: documents.map((doc, i) => ({
    custom_id: doc.id,
    params: {
      model: 'claude-haiku-4-5-20251001', // Cheap for bulk
      max_tokens: 512,
      messages: [{ role: 'user', content: `Extract entities: ${doc.text}` }],
    },
  })),
});
// 50% cheaper, processes within 24h
```

**Best for:** Summarization, classification, extraction at scale.

## 5. Evaluation / Grading

Use Claude to evaluate other AI outputs or human content.

```typescript
const evaluation = await client.messages.create({
  model: 'claude-opus-4-20250514', // Best judgment
  max_tokens: 1024,
  system: `You are an expert evaluator. Score the response 1-5 on accuracy, relevance, and completeness. Return JSON: { "accuracy": N, "relevance": N, "completeness": N, "reasoning": "..." }`,
  messages: [{
    role: 'user',
    content: `Question: ${question}\nResponse to evaluate: ${candidateResponse}`,
  }],
});
```

**Best for:** AI output quality, content moderation, automated grading.

## Choosing a Pattern

| Pattern | Latency | Cost | Complexity |
|---------|---------|------|------------|
| Chatbot | Low (streaming) | Low | Simple |
| RAG | Medium (embed + search + generate) | Medium | Medium |
| Agent | High (multi-turn) | High | Complex |
| Pipeline | High (async batch) | Low (50% off) | Simple |
| Evaluation | Medium | Varies | Simple |

## Output

- Architecture pattern selected based on requirements
- Implementation code for chosen pattern
- Cost and latency characteristics understood
- Scaling strategy identified (streaming for chatbots, batches for pipelines)

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| API Error | Check error type and status code | See `clade-common-errors` |

## Examples

See five numbered pattern sections with complete TypeScript code, and the Choosing a Pattern comparison table with latency, cost, and complexity ratings.

## Resources

- [Tool Use Guide](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [Prompt Engineering](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)

## Next Steps

See `clade-known-pitfalls` for common mistakes.

## Prerequisites

- Completed `clade-install-auth` and `clade-model-inference`
- Understanding of your use case requirements (latency, cost, complexity)
- For RAG: vector database and embedding model (Voyage, OpenAI, or Cohere)

## Instructions

### Step 1: Review the patterns below

Each section contains production-ready code examples. Copy and adapt them to your use case.

### Step 2: Apply to your codebase

Integrate the patterns that match your requirements. Test each change individually.

### Step 3: Verify

Run your test suite to confirm the integration works correctly.
