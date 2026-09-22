---
name: cursor-team-setup
description: 'Set up Cursor for teams: plan selection, member management, shared rules,
  admin dashboard, and

  onboarding. Triggers on "cursor team", "cursor organization", "cursor business",
  "cursor enterprise setup",

  "cursor admin".

  '
allowed-tools: Read, Write, Edit, Bash(cmd:*)
version: 1.19.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- cursor
- cursor-team
compatibility: Designed for Claude Code
---
# Cursor Team Setup

## Overview

Onboard a Cursor team with approved identity, privacy, rules, repository access, and support ownership before broad AI-assisted development begins.

## Prerequisites

- A named tenant owner, identity source, approved plan, and data-use policy.
- Reviewed repository templates, ignore rules, and owner for onboarding/offboarding.

## Instructions

1. Pilot with a small group using SSO/SCIM or approved identity controls and least-privilege roles.
2. Publish reviewed shared rules and ignore files through source control, not untracked local instructions.
3. Train members on context boundaries, diff review, testing, escalation, and account recovery.
4. Review access, policy enforcement, and adoption evidence before expanding the rollout.

## Output

- A governed team rollout with ownership, onboarding evidence, and offboarding/access-review controls.

## Error Handling

| Condition | Safe response |
|---|---|
| A user receives excess access | Correct the identity/group mapping and record the access review. |
| Shared rules conflict with a repository | Use a reviewed scoped override; do not disable all team rules. |
| Privacy control cannot be verified | Hold expansion and escalate to the tenant/security owner. |

## Examples

Pilot one engineering group, verify SSO and Privacy Mode policy, open a template repository with reviewed rules, and collect a redacted onboarding receipt. Expand only after a new user and a departed user both pass the expected provisioning/deprovisioning checks.

Configure Cursor for teams and organizations. Covers plan selection, member management, shared configurations, Privacy Mode enforcement, and onboarding workflows.

## Plan Comparison

| Feature | Pro ($20/user/mo) | Business ($40/user/mo) | Enterprise (custom) |
|---------|-------------------|----------------------|---------------------|
| Fast requests | 500/mo | 500/mo/seat | Custom |
| Tab completion | Unlimited | Unlimited | Unlimited |
| Privacy Mode | Optional | Enforced by default | Enforced |
| SSO (SAML/OIDC) | No | Yes | Yes |
| SCIM provisioning | No | No | Yes |
| Admin dashboard | No | Yes | Yes |
| Usage analytics | No | Yes | Yes (advanced) |
| Priority support | No | No | Yes |
| Dedicated account mgr | No | No | Yes |
| SLA | No | No | Yes |
| SOC 2 report access | No | Request | Included |

## Team Setup Workflow

### Step 1: Create Organization

1. Go to [cursor.com/settings](https://cursor.com/settings)
2. Click "Create Team" or "Create Organization"
3. Enter organization name and billing details
4. Select plan (Business or Enterprise)

### Step 2: Configure Team Settings

**Admin Dashboard** (Business/Enterprise):

```
Dashboard Sections:
├── Members         → Invite, remove, assign roles
├── Usage           → Request counts, model usage, costs
├── Privacy         → Privacy Mode enforcement
├── Models          → Restrict available models
├── SSO             → SAML/OIDC configuration
└── Billing         → Plan, invoices, seat management
```

### Step 3: Invite Members

```
Methods:
1. Email invitation: Admin dashboard > Members > Invite by email
2. Domain auto-join: Allow anyone with @company.com to join
3. SSO provisioning: Users auto-join when they sign in via SSO
4. SCIM (Enterprise): Automatic sync from identity provider
```

**Roles:**

| Role | Permissions |
|------|------------|
| Owner | Full admin, billing, delete org |
| Admin | Manage members, settings, SSO |
| Member | Use Cursor with team settings |

### Step 4: Enforce Privacy Mode

For Business and Enterprise plans:

1. Admin Dashboard > Privacy
2. Enable "Enforce Privacy Mode for all members"
3. Team members cannot disable Privacy Mode locally
4. Verification: each client pings server every 5 minutes to check enforcement

Privacy Mode guarantees:

- Zero data retention at model providers (OpenAI, Anthropic)
- No code used for model training
- No plaintext code stored on Cursor servers

### Step 5: Configure Model Access

Admin Dashboard > Models:

```
Available models (toggle on/off per team):
  ✅ GPT-4o
  ✅ Claude Sonnet
  ✅ Auto mode
  ❌ Claude Opus (restricted to save costs)
  ❌ o1 (restricted to save costs)
  ✅ cursor-small
```

Restricting models helps control costs -- premium models consume fast requests faster.

## Shared Configuration (via Git)

Team settings that belong in the project repository:

### Project Rules

```
.cursor/rules/
├── project.mdc            # Stack, conventions (alwaysApply: true)
├── security.mdc           # Security constraints (alwaysApply: true)
├── code-style.mdc         # Naming, formatting (alwaysApply: true)
├── typescript.mdc         # TS patterns (glob: **/*.ts)
├── react.mdc              # React patterns (glob: **/*.tsx)
└── testing.mdc            # Test conventions (glob: **/*.test.ts)
```

Commit these to git. Every team member gets the same AI behavior.

### Ignore Files

```
.cursorignore              # Shared exclusions (commit to git)
.cursorindexingignore      # Shared indexing exclusions (commit to git)
```

### Machine-Local Settings

These are NOT shared via git:

- `settings.json` (editor preferences -- personal choice)
- `keybindings.json` (keyboard shortcuts -- personal choice)
- API keys (stored in Cursor's local settings database)

## Onboarding New Team Members

### Onboarding Checklist

```markdown
## New Team Member: Cursor Setup (20 minutes)

### Account
[ ] Download Cursor from cursor.com/download
[ ] Sign in with @company.com email
[ ] Verify Business plan active (cursor.com/settings)
[ ] Verify Privacy Mode is ON (Cursor Settings > General)

### Project Setup
[ ] Clone the repository
[ ] Open in Cursor: `cursor /path/to/project`
[ ] Wait for indexing to complete (bottom status bar)
[ ] Verify rules loaded: Cmd+L > type "@Cursor Rules"

### Learn the Basics (10 min)
[ ] Tab completion: type code, accept with Tab
[ ] Chat: Cmd+L > "@Codebase how is auth handled?"
[ ] Inline Edit: select code > Cmd+K > "add error handling"
[ ] Composer: Cmd+I > describe a multi-file task

### Team Conventions
[ ] Read .cursor/rules/ files (our AI guidelines)
[ ] Use Conventional Commits for commit messages
[ ] Start new chats for new tasks (don't reuse old conversations)
[ ] Review all AI-generated code before committing
```

### Buddy System

Pair new team members with experienced Cursor users for their first week. Focus areas:

- When to use Chat vs Composer vs Inline Edit
- How to write effective prompts with `@` context
- Common pitfalls (context overflow, blind apply)
- Team-specific rules and conventions

## Usage Monitoring

### Admin Dashboard Metrics

| Metric | Purpose |
|--------|---------|
| Requests per user | Identify power users and underutilizers |
| Model distribution | Which models are used most |
| Fast vs slow requests | Quota consumption rate |
| Cost per seat | ROI calculation |

### Adoption Indicators

```
High adoption:
  - 80%+ team members active weekly
  - Average 10+ requests/day per user
  - Rules files regularly updated in git

Low adoption (needs attention):
  - Team members not signing in
  - Rules files stale or absent
  - No AI commit messages in git history
```

## Enterprise Considerations

- **SCIM provisioning**: Sync users and groups from Okta/Azure AD automatically (Enterprise only)
- **Audit logging**: Enterprise plans include detailed usage audit logs for compliance
- **Cost allocation**: Track AI costs per team/project for internal chargeback
- **Vendor review**: Request Cursor's SOC 2 Type II report and security questionnaire for procurement

## Resources

- [Cursor Team Documentation](https://docs.cursor.com/plans/business)
- [Cursor Enterprise](https://cursor.com/enterprise)
- [Admin Dashboard](https://cursor.com/settings)
- [Privacy and Data Governance](https://docs.cursor.com/enterprise/privacy-and-data-governance)
