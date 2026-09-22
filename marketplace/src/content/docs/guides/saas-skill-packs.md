---
title: "SaaS Skill Packs: Platform Integrations"
description: "Learn how SaaS skill packs provide platform-specific Claude Code integrations. Covers available packs, anatomy, usage, and how to create custom SaaS packs for any platform API."
section: "guides"
order: 4
keywords:
  - "SaaS pack"
  - "skill pack"
  - "platform integration"
  - "API skills"
  - "Stripe"
  - "GitHub"
  - "Slack"
  - "Vercel"
  - "SaaS integration"
  - "Claude Code integrations"
officialLinks:
  - title: "Anthropic Claude Code Documentation"
    url: "https://code.claude.com/docs/en/"
  - title: "Tons of Skills Marketplace"
    url: "https://tonsofskills.com/explore"
relatedDocs:
  - "concepts/plugins"
  - "concepts/skills"
  - "ecosystem/marketplace-overview"
---

## What Are SaaS Skill Packs?

SaaS skill packs are collections of Claude Code skills designed for a specific platform or service. Instead of a general-purpose plugin that covers many topics, a SaaS pack focuses entirely on one platform -- its API, CLI, configuration, best practices, and common workflows.

Each pack bundles multiple skills that work together to provide comprehensive coverage of that platform. A Stripe pack, for example, might include skills for payment integration, webhook handling, subscription management, and Stripe CLI operations. A GitHub pack might cover Actions workflows, repository management, issue automation, and PR review patterns.

SaaS packs are pnpm workspace members that live in the `plugins/saas-packs/` directory. They follow the same plugin structure as regular plugins but are organized by platform and contain domain-specific knowledge that goes deeper than a generic plugin could.

## How SaaS Packs Differ from Regular Plugins

| Aspect | Regular Plugin | SaaS Pack |
|--------|---------------|-----------|
| **Scope** | A workflow or task type (testing, deployment) | A specific platform (Stripe, GitHub, Slack) |
| **Skills** | General-purpose instructions | Platform API-specific guidance |
| **Knowledge** | Broad best practices | Deep platform documentation |
| **Naming** | `my-plugin` | `platform-pack` (e.g., `stripe-pack`) |
| **Location** | `plugins/[category]/` | `plugins/saas-packs/` |
| **Dependencies** | Usually none | May reference platform SDKs or CLIs |

The key advantage of SaaS packs is depth. A regular plugin might tell Claude to "make an API call." A SaaS pack teaches Claude the specific API endpoints, authentication patterns, error codes, rate limits, and idiomatic usage for that platform.

## Available SaaS Packs

The Tons of Skills marketplace includes over 60 SaaS packs covering platforms across categories. Here is a representative sample:

### Developer Tools

| Pack | Platform | Skills |
|------|----------|--------|
| `anthropic-pack` | Anthropic API | Claude API integration, prompt engineering, model selection |
| `github-pack` | GitHub | Actions, repository management, PR automation, Issues |
| `vercel-pack` | Vercel | Deployment, serverless functions, edge config |
| `netlify-pack` | Netlify | Deploy, forms, functions, identity |
| `claude-pack` | Claude Code | Plugin development, skill writing, agent creation |

### Payments and Commerce

| Pack | Platform | Skills |
|------|----------|--------|
| `stripe-pack` | Stripe | Payments, subscriptions, webhooks, Stripe CLI |
| `shopify-pack` | Shopify | Storefront API, admin API, theme development |
| `square-pack` | Square | Payments, catalog, inventory |

### Communication

| Pack | Platform | Skills |
|------|----------|--------|
| `slack-pack` | Slack | Bot development, Bolt framework, Block Kit, webhooks |
| `twilio-pack` | Twilio | SMS, voice, WhatsApp, Verify |

### Data and Analytics

| Pack | Platform | Skills |
|------|----------|--------|
| `algolia-pack` | Algolia | Search implementation, indexing, analytics |
| `apollo-pack` | Apollo GraphQL | Client setup, schema design, caching |

### Infrastructure

| Pack | Platform | Skills |
|------|----------|--------|
| `castai-pack` | CAST AI | Kubernetes optimization, cost management |
| `brightdata-pack` | Bright Data | Web scraping, proxy management |

Browse all available packs on the [Explore](/explore) page by filtering for the "saas-packs" category.

## Anatomy of a SaaS Pack

A SaaS pack follows standard plugin structure with platform-specific content. Here is the structure of a typical pack:

```
plugins/saas-packs/stripe-pack/
├── .claude-plugin/
│   └── plugin.json
├── README.md
├── LICENSE
├── package.json                      # pnpm workspace member
├── skills/
│   ├── stripe-payments/
│   │   ├── SKILL.md                  # Payment integration skill
│   │   ├── reference.md              # API reference
│   │   └── examples/
│   │       └── checkout-session.ts
│   ├── stripe-webhooks/
│   │   ├── SKILL.md                  # Webhook handling skill
│   │   └── reference.md
│   ├── stripe-subscriptions/
│   │   ├── SKILL.md                  # Subscription management
│   │   └── reference.md
│   └── stripe-cli/
│       └── SKILL.md                  # Stripe CLI operations
├── commands/
│   └── stripe-setup.md              # Initial Stripe configuration
└── agents/
    └── stripe-debugger.md           # Autonomous payment debugging
```

### The plugin.json

```json
{
  "name": "stripe-pack",
  "version": "1.0.0",
  "description": "Comprehensive Stripe integration skills: payments, subscriptions, webhooks, CLI, and Connect platform",
  "author": "Your Name <you@example.com>",
  "repository": "https://github.com/username/claude-code-plugins",
  "license": "MIT",
  "keywords": ["stripe", "payments", "subscriptions", "webhooks", "fintech", "saas-pack"]
}
```

### The package.json

SaaS packs are pnpm workspace members. The `package.json` is minimal:

```json
{
  "name": "@plugins/stripe-pack",
  "version": "1.0.0",
  "private": true,
  "description": "Stripe integration skills for Claude Code"
}
```

### A Typical Pack Skill

Each skill in a SaaS pack provides deep, platform-specific instructions. Here is what a Stripe payments skill looks like:

```yaml
---
name: stripe-payments
description: |
  Implement Stripe payment processing in web applications. Covers
  Checkout Sessions, Payment Intents, payment methods, error handling,
  and PCI compliance. Trigger phrases: "add Stripe payments", "integrate
  Stripe checkout", "set up payment processing", "handle Stripe errors".
allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(npx:*), Glob, Grep
version: 1.0.0
author: Your Name <you@example.com>
license: MIT
compatibility: "Node.js >= 18"
compatible-with: claude-code
tags: [stripe, payments, checkout, fintech, saas-pack]
---

# Stripe Payments

Implement Stripe payment processing with Checkout Sessions and
Payment Intents.

## Overview

This skill helps integrate Stripe payments into web applications
using the official Stripe Node.js SDK. It covers the full payment
flow from client-side setup through server-side processing and
webhook verification.

## Prerequisites

- Stripe account with API keys
- Node.js 18+ project
- `stripe` npm package installed

## Current Project State

!`cat package.json | jq '.dependencies.stripe // "not installed"' 2>/dev/null`
!`ls .env* 2>/dev/null | head -3 || echo "no .env files found"`

## Instructions

1. Check if the Stripe SDK is installed:
   - If not: `npm install stripe`
   - Verify version is 14.0.0+

2. Set up server-side Stripe initialization:
   ```typescript
   import Stripe from 'stripe';

   const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
     apiVersion: '2024-12-18.acacia',
   });
   ```

1. Implement the Checkout Session flow:
   - Create a POST endpoint for session creation
   - Configure line items, mode (payment/subscription)
   - Set success and cancel URLs
   - Handle the response on the client

2. Add webhook endpoint for payment confirmation:
   - Verify webhook signature with `stripe.webhooks.constructEvent()`
   - Handle `checkout.session.completed` event
   - Handle `payment_intent.succeeded` event

3. Implement error handling:
   - `StripeCardError` for declined cards
   - `StripeInvalidRequestError` for bad parameters
   - `StripeAPIError` for Stripe-side failures

## Error Handling

- If STRIPE_SECRET_KEY is not set, warn the user and provide setup instructions
- If the Stripe SDK version is below 14.0, recommend upgrading
- If webhook signature verification fails, check the endpoint secret

## Security Notes

- Never expose the secret key in client-side code
- Always verify webhook signatures
- Use Stripe.js or Stripe Elements for PCI compliance
- Store only Stripe customer/subscription IDs, not card details

```

## Using SaaS Packs in Your Workflow

### Installation

Install a SaaS pack the same way as any plugin:

```bash
claude /plugin add jeremylongshore/claude-code-plugins --path plugins/saas-packs/stripe-pack
```

Or install the entire Tons of Skills collection to get all packs at once:

```bash
claude /plugin add jeremylongshore/claude-code-plugins
```

### Activation

SaaS pack skills auto-activate based on context. When you say "add Stripe payments to my app" or "set up Slack notifications", Claude Code matches the request against skill descriptions and loads the relevant pack skills.

You can also invoke pack commands explicitly:

```
/stripe-setup
```

### Combining Packs

SaaS packs compose naturally. You might use the Stripe pack for payment processing, the Slack pack for sending payment notifications, and the Vercel pack for deploying the application. Each pack's skills activate independently when their domain is relevant.

## Creating a Custom SaaS Pack

### Step 1: Scaffold the Pack

```bash
mkdir -p plugins/saas-packs/myplatform-pack/.claude-plugin
mkdir -p plugins/saas-packs/myplatform-pack/skills
mkdir -p plugins/saas-packs/myplatform-pack/commands
mkdir -p plugins/saas-packs/myplatform-pack/agents
```

### Step 2: Identify Core Skills

Map the platform's API surface to individual skills. Each skill should cover one coherent area:

| API Area | Skill Name | Purpose |
|----------|-----------|---------|
| Authentication | `myplatform-auth` | OAuth, API keys, token management |
| Core resource | `myplatform-items` | CRUD operations on the primary resource |
| Webhooks | `myplatform-webhooks` | Event handling and webhook setup |
| CLI | `myplatform-cli` | Platform CLI tool operations |

Aim for 3-8 skills per pack. Fewer than 3 suggests the pack is too narrow. More than 8 suggests it should be split.

### Step 3: Write Platform-Specific Skills

Each skill should encode deep platform knowledge:

- **API patterns:** Exact endpoint URLs, request/response shapes, pagination styles
- **Authentication:** How to initialize the SDK, manage tokens, handle refresh
- **Error codes:** Platform-specific error codes and their meaning
- **Rate limits:** Known limits and how to handle 429 responses
- **Best practices:** Official recommendations from the platform's documentation
- **Common pitfalls:** Known gotchas and how to avoid them

### Step 4: Add Supporting References

Create `reference.md` files alongside each SKILL.md with detailed API documentation. Claude Code reads these on demand when it needs deeper information:

```markdown
# Stripe Payments API Reference

## Checkout Sessions

### Create a Session

POST /v1/checkout/sessions

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `line_items` | array | Yes | Items the customer is purchasing |
| `mode` | string | Yes | `payment`, `subscription`, or `setup` |
| `success_url` | string | Yes | Redirect URL after success |
| `cancel_url` | string | Yes | Redirect URL after cancellation |

### Response

```json
{
  "id": "cs_test_...",
  "url": "https://checkout.stripe.com/...",
  "status": "open",
  "payment_status": "unpaid"
}
```

```

### Step 5: Add a package.json

```json
{
  "name": "@plugins/myplatform-pack",
  "version": "1.0.0",
  "private": true,
  "description": "MyPlatform integration skills for Claude Code"
}
```

### Step 6: Validate and Test

```bash
# Validate the pack structure
python3 scripts/validate-skills-schema.py --enterprise --verbose \
  plugins/saas-packs/myplatform-pack/

# Run quick test
pnpm run sync-marketplace && ./scripts/quick-test.sh
```

## Pack Quality Standards

SaaS packs in the Tons of Skills marketplace are held to enterprise quality standards:

| Criterion | Requirement |
|-----------|-------------|
| Frontmatter completeness | All required fields present, description > 100 chars |
| Body depth | 500+ words per skill with structured sections |
| Code examples | At least one working code example per skill |
| Error handling | Documented error scenarios and recovery steps |
| Supporting docs | Reference files for API details |
| Validation score | B grade (70+) on the 100-point rubric |

### Upgrading Pack Quality

The Tons of Skills repository includes batch remediation tools for upgrading skill quality:

```bash
# Preview compliance fixes
python3 freshie/scripts/batch-remediate.py --dry-run

# Apply all auto-fixes
python3 freshie/scripts/batch-remediate.py --all --execute
```

Auto-fixes cover common issues like missing `compatible-with` fields, incorrect tag formats, and missing `version` fields.

## Next Steps

- Browse available packs on the [Skills](/skills) page
- [Build a plugin](/docs/guides/build-a-plugin) to understand the full plugin structure
- [Publish your pack](/docs/guides/publish-to-marketplace) to the Tons of Skills marketplace
- Check the [Explore](/explore) page for packs in your platform's category
