---
name: cursor-install-auth
description: 'Install Cursor IDE and configure authentication across macOS, Linux,
  and Windows. Triggers on

  "install cursor", "setup cursor", "cursor authentication", "cursor login", "cursor
  license",

  "cursor download".

  '
allowed-tools: Read, Write, Edit, Bash(cmd:*)
version: 1.19.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- cursor
- authentication
compatibility: Designed for Claude Code
---
# Cursor Install & Auth

## Overview

Install Cursor, authenticate through the approved identity flow, and establish privacy settings before opening sensitive repositories. Do not treat local profiles or settings files as a secrets store.

## Instructions

1. Download the signed installer from the official site or approved software catalog.
2. Sign in through the organization-approved account or SSO flow and confirm the expected tenant.
3. Enable approved privacy/data controls before opening proprietary code, then import only reviewed settings and extensions.
4. Verify Tab and Chat with a non-sensitive sample project; escalate tenant mismatch to the administrator.

Install Cursor IDE and authenticate your account. Covers all platforms, plan activation, and VS Code migration.

## Installation

### macOS

```bash
# Option 1: Direct download
open https://cursor.com/download

# Option 2: Homebrew
brew install --cask cursor
```

After install, drag Cursor.app to Applications. First launch may require: System Settings > Privacy & Security > Allow.

### Linux

```bash
# Download AppImage
curl -fSL https://download.cursor.com/linux/appImage/x64 -o cursor.AppImage
chmod +x cursor.AppImage
./cursor.AppImage

# Or via .deb (Debian/Ubuntu)
curl -fSL https://download.cursor.com/linux/deb/x64 -o cursor.deb
sudo dpkg -i cursor.deb
```

Add to PATH for terminal launching:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias cursor='/path/to/cursor.AppImage'
```

### Windows

Download installer from [cursor.com/download](https://cursor.com/download). Run the `.exe` installer. Cursor installs per-user (no admin required by default).

## Authentication

### First Launch Sign-In

1. Launch Cursor
2. Click **Sign In** in the welcome screen
3. Choose auth method:
   - **GitHub** (recommended for developers)
   - **Google**
   - **Email + password**
4. Browser opens for OAuth flow
5. Approve the authorization
6. Return to Cursor -- it detects the auth automatically

### Plan Activation

After sign-in, your plan is automatically active:

| Plan | Price | Includes |
|------|-------|----------|
| **Free** | $0/mo | 50 slow premium requests/month, Tab completions (limited) |
| **Pro** | $20/mo | 500 fast premium requests/month, unlimited Tab, all models |
| **Business** | $40/user/mo | Pro features + Privacy Mode enforced, SSO, admin dashboard |
| **Enterprise** | Custom | Business + SCIM, SLA, dedicated support |

Upgrade at: [cursor.com/settings](https://cursor.com/settings)

## VS Code Migration

On first launch, Cursor detects existing VS Code installations and offers one-click import:

### What Migrates Automatically

- **Settings**: `settings.json` preferences
- **Keybindings**: Custom keyboard shortcuts
- **Extensions**: Re-installs compatible extensions from Open VSX Registry
- **Themes**: Color themes and icon packs
- **Snippets**: User-defined code snippets

### What Does NOT Migrate

- **Microsoft-exclusive extensions**: GitHub Copilot, Live Share, Remote-SSH (MS marketplace only)
- **Extension state**: Login states, extension-specific databases
- **Workspace trust**: Need to re-trust workspaces

### Manual Extension Installation

For extensions not in Open VSX, install via `.vsix`:

1. Download `.vsix` from VS Code Marketplace website
2. In Cursor: `Cmd+Shift+P` > `Extensions: Install from VSIX...`
3. Select the downloaded file

## Post-Install Configuration Checklist

```
[ ] Sign in and verify plan (cursor.com/settings)
[ ] Import VS Code settings (if applicable)
[ ] Set default shell: Cursor Settings > Terminal > Default Profile
[ ] Configure privacy mode: Cursor Settings > General > Privacy Mode
[ ] Set default AI model: Cursor Settings > Models
[ ] Verify Tab completions work: type code, see ghost text
[ ] Verify Chat works: Cmd+L, ask a question
[ ] Install missing extensions from Open VSX
```

## Settings File Locations

| Platform | Settings Path |
|----------|--------------|
| macOS | `~/Library/Application Support/Cursor/User/settings.json` |
| Linux | `~/.config/Cursor/User/settings.json` |
| Windows | `%APPDATA%\Cursor\User\settings.json` |

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Sign-in loop (browser redirects back) | Clear browser cookies for cursor.com, try incognito |
| "License not found" after payment | Sign out and sign back in; check email matches |
| Extensions missing after migration | Search Open VSX Registry; install via VSIX if needed |
| Cursor opens as blank window (Linux) | Try `--disable-gpu` flag: `cursor --disable-gpu` |
| Auto-update fails | Download latest installer from cursor.com/download |

## Output

- A verified Cursor installation tied to the intended individual or enterprise account.
- Privacy and workspace-trust settings appropriate to the project's data classification.

## Examples

Install and verify in a non-sensitive workspace: install from the approved source, sign in using the company SSO tile, confirm the organization name, enable the approved privacy setting, and test Tab with a harmless comment. If the tenant is wrong or SSO is bypassed unexpectedly, sign out and contact the administrator; do not use a personal account as a workaround.

## Enterprise Considerations

- **Domain verification**: Enterprise admins verify company domain before enabling team features
- **Managed deployment**: Distribute Cursor via MDM (macOS) or SCCM (Windows) with pre-configured settings
- **Offline install**: Download the installer package for distribution behind firewalls (auth still requires network)
- **SSO bypass**: First login can use email/password; SSO enforcement applied after team admin configures SAML

## Resources

- [Cursor Download](https://cursor.com/download)
- [VS Code Migration Guide](https://docs.cursor.com/configuration/migrations/vscode)
- [Pricing](https://cursor.com/pricing)
- [Account Settings](https://cursor.com/settings)
