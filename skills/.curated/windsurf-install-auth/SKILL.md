---
name: windsurf-install-auth
description: 'Install and authenticate Devin Desktop, the current name for Windsurf.
  Use when performing first-time setup, the Windsurf-to-Devin Desktop update, organization
  selection, or sign-in repair. Trigger with "install windsurf", "install Devin
  Desktop", "windsurf auth", "sign in", or "choose organization".'
argument-hint: "[operating system and account type]"
allowed-tools: Read
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- windsurf
- devin-desktop
- authentication
- ide-setup
compatibility: Designed for Claude Code
---

# Install and Authenticate Devin Desktop

## Overview

Devin Desktop is the new name for Windsurf. Existing Windsurf installations receive it as a standard over-the-air update, with plans, settings, extensions, workflows, and in-progress work carried forward.

## Prerequisites

- A supported desktop operating system shown on the current download page
- A Devin/Windsurf account or organization invitation
- Browser access for the interactive sign-in flow
- Organization approval before installing on a managed device

## Tool Use

- Use `Read` to inspect only the repository files and configuration needed for the request.

## Instructions

### Step 1: Choose update or fresh install

If Windsurf is already installed, use its normal update flow and preserve the existing profile. For a fresh install, download the signed installer from the official product page; do not use an unverified curl-to-shell command or third-party package.

### Step 2: Preserve the current profile

Before a major update, record the editor version and export any profile the product exposes. Commit repository Rules, `AGENTS.md`, Workflows, and Skills separately so team customizations do not depend on one workstation.

### Step 3: Sign in interactively

1. Launch Devin Desktop.
2. Select the visible sign-in option.
3. Complete the browser-based account or enterprise identity-provider flow.
4. Return to the editor and select the intended organization.
5. Confirm that the account identity and plan shown in the product are expected.

Do not ask users to paste session tokens, cookies, SAML assertions, recovery codes, or API keys into chat or repository files.

### Step 4: Apply enterprise controls

For managed organizations, verify repository access, identity-provider policy, seat assignment, MCP policy, system Rules, network allowlists, and data controls through the current admin documentation. Do not invent private server URLs or undocumented settings keys.

### Step 5: Verify non-destructively

Open a disposable or clean version-controlled project. Confirm:

- Cascade opens and identifies Code and Chat modes;
- a read-only codebase question returns relevant context;
- Supercomplete is available where the plan and policy permit it;
- no unexpected organization or repository is connected.

## Output

Report the installed Devin Desktop version, operating system, update or fresh-install path, sign-in method, selected organization, profile migration result, and successful non-destructive Cascade check. Redact all account identifiers not needed for verification.

## Error Handling

| Issue | Response |
|---|---|
| Installer is blocked or damaged | Stop and use the current OS-specific troubleshooting instructions |
| Browser sign-in does not return | Restart the interactive flow and check proxy or deep-link policy |
| Wrong organization selected | Sign out, preserve diagnostics, and choose the authorized organization |
| Features are unavailable | Verify plan, seat, organization policy, and quota state |
| Update changed behavior | Check release notes and use the preserved profile for rollback evidence |

## Examples

**Successful handoff:** "Devin Desktop installed on macOS through the official signed download; browser SSO completed; Engineering organization selected; Cascade Chat read-only smoke test passed; no secrets collected."

## Resources

- [Focused first-party references](references/official-docs.md)
- [Devin Desktop / Windsurf product page](https://windsurf.com/editor)
- [Official download](https://windsurf.com/download)
- [Common Devin Desktop issues](https://docs.devin.ai/desktop/troubleshooting/windsurf-common-issues)
- [Enterprise administration](https://docs.devin.ai/desktop/guide-for-admins)

## Related Skill

Continue with `windsurf-hello-world` to verify the installation through a disposable, guarded Code and Chat workflow before opening sensitive repositories.
