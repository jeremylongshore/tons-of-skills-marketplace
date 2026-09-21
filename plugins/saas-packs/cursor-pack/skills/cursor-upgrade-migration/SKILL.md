---
name: cursor-upgrade-migration
description: 'Upgrade Cursor versions, migrate from VS Code, and transfer settings
  between machines. Triggers on

  "upgrade cursor", "update cursor", "cursor migration", "cursor new version", "vs
  code to cursor",

  "cursor changelog".

  '
allowed-tools: Read, Write, Edit, Bash(cmd:*)
version: 1.19.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- cursor
- migration
compatibility: Designed for Claude Code
---
# Cursor Upgrade & Migration

## Overview

Upgrade Cursor or migrate settings through a staged, reversible rollout that preserves policy, extensions, rules, workspace trust, and user recovery.

## Prerequisites

- Current/target versions, release-note review, supported-platform confirmation, and a settings backup.
- Pilot users, a named migration owner, and an approved rollback or previous installer.

## Instructions

1. Inventory settings, extensions, rules, integrations, and identity/privacy requirements.
2. Test the target version with a pilot using non-sensitive workspaces and required workflows.
3. Document compatibility, performance, and policy results before broader rollout.
4. Roll back or pause on sign-in, privacy, extension, or workflow regression; retain evidence for follow-up.

## Output

- A staged upgrade/migration record with pilot evidence, owner, compatibility decision, and rollback instructions.

## Error Handling

| Condition | Safe response |
|---|---|
| Upgrade breaks policy or privacy behavior | Stop rollout, revert/pause, and escalate to the tenant owner. |
| Extension/settings migration fails | Restore the verified backup and remediate in the pilot. |
| Version is unsupported | Do not force installation; use the supported version or plan platform remediation. |

## Examples

Back up a pilot user's settings, install the target version in a test profile, verify SSO, privacy, rules, indexing, and a sample repository, then expand only after the pilot receipt passes. Keep the previous installer until the observation window closes.

Upgrade Cursor IDE versions, migrate from VS Code, and transfer configurations between machines.

## Version Upgrades

### Auto-Update (Recommended)

Cursor checks for updates automatically. When available:

1. A notification appears: "A new version is available"
2. Click "Restart to Update" or go to `Help` > `Check for Updates`
3. Cursor downloads, installs, and restarts

### Manual Update

If auto-update fails or is disabled:

```bash
# macOS (Homebrew)
brew upgrade --cask cursor

# macOS/Linux/Windows: Download latest from
# https://cursor.com/download

# Linux AppImage: replace the old file
curl -fSL https://download.cursor.com/linux/appImage/x64 -o cursor.AppImage
chmod +x cursor.AppImage
```

### Pre-Upgrade Checklist

```
[ ] Note current version: Help > About
[ ] Check release notes: changelog.cursor.sh
[ ] Backup settings:
    macOS: cp -r ~/Library/Application\ Support/Cursor/User ~/cursor-settings-backup
    Linux: cp -r ~/.config/Cursor/User ~/cursor-settings-backup
[ ] Export extension list:
    cursor --list-extensions > extensions-backup.txt
[ ] Commit any unsaved work to git
[ ] Note any custom keybindings (keybindings.json)
```

### Post-Upgrade Verification

```
[ ] Cursor launches without errors
[ ] Sign-in still active (check top-right user icon)
[ ] AI features work: try Cmd+L, type a question
[ ] Tab completion works: type code, see ghost text
[ ] Extensions loaded: Cmd+Shift+X, verify list
[ ] Custom keybindings preserved: test your shortcuts
[ ] Project rules still load: @Cursor Rules in chat
[ ] Indexing status: check status bar
```

## VS Code to Cursor Migration

### Automatic Import (First Launch)

On first launch, Cursor detects VS Code and offers one-click import:

```
What migrates:
  ✅ settings.json (editor preferences)
  ✅ keybindings.json (custom shortcuts)
  ✅ User snippets
  ✅ Color themes
  ✅ Compatible extensions (from Open VSX Registry)

What does NOT migrate:
  ❌ Microsoft-exclusive extensions (Copilot, Live Share, Remote-SSH)
  ❌ Extension login states / databases
  ❌ Workspace trust settings
  ❌ Task configurations (.vscode/tasks.json -- copies but may need adjustment)
```

### Manual Migration

If you skipped the auto-import:

```bash
# Copy settings (macOS example)
cp ~/Library/Application\ Support/Code/User/settings.json \
   ~/Library/Application\ Support/Cursor/User/settings.json

# Copy keybindings
cp ~/Library/Application\ Support/Code/User/keybindings.json \
   ~/Library/Application\ Support/Cursor/User/keybindings.json

# Copy snippets
cp -r ~/Library/Application\ Support/Code/User/snippets/ \
      ~/Library/Application\ Support/Cursor/User/snippets/

# Reinstall extensions (from backup list)
while read ext; do cursor --install-extension "$ext"; done < extensions-backup.txt
```

### Extension Marketplace Differences

Cursor uses **Open VSX Registry** instead of Microsoft's VS Code Marketplace:

| Extension | Status in Cursor |
|-----------|-----------------|
| ESLint | Available (Open VSX) |
| Prettier | Available (Open VSX) |
| GitLens | Available (Open VSX) |
| Docker | Available (Open VSX) |
| Python | Available (Open VSX) |
| GitHub Copilot | Not available (Microsoft exclusive, also conflicts with Cursor AI) |
| Live Share | Not available (Microsoft exclusive) |
| Remote - SSH | Not available (Microsoft exclusive) |
| C# Dev Kit | Not available (Microsoft exclusive) |

**For unavailable extensions**, download `.vsix` from the VS Code Marketplace website and install manually:
`Cmd+Shift+P` > `Extensions: Install from VSIX...`

### Running VS Code and Cursor Side-by-Side

Both can be installed simultaneously. They use separate:

- Settings directories
- Extension directories
- Configuration files

You can open the same project in both editors at once (though be careful with file save conflicts).

## Migration Between Machines

### Export Configuration

```bash
# List all extensions
cursor --list-extensions > cursor-extensions.txt

# Copy settings files
cp ~/Library/Application\ Support/Cursor/User/settings.json .
cp ~/Library/Application\ Support/Cursor/User/keybindings.json .

# Copy project rules (these are already in git if committed)
# .cursor/rules/*.mdc are project-level, not machine-level
```

### Import on New Machine

```bash
# Install Cursor
# Sign in (settings sync if available)

# Restore settings
cp settings.json ~/Library/Application\ Support/Cursor/User/
cp keybindings.json ~/Library/Application\ Support/Cursor/User/

# Install extensions
while read ext; do cursor --install-extension "$ext"; done < cursor-extensions.txt
```

### Settings to Review After Machine Transfer

```json
// settings.json -- platform-specific settings to check
{
  "terminal.integrated.defaultProfile.osx": "zsh",    // macOS
  "terminal.integrated.defaultProfile.linux": "bash",  // Linux
  "editor.fontFamily": "Fira Code",                    // Font must be installed
  "files.watcherExclude": { ... }                      // Paths may differ
}
```

## Handling Breaking Changes

### .cursorrules to .cursor/rules/ Migration

If upgrading from a Cursor version that used `.cursorrules`:

1. Create `.cursor/rules/` directory
2. Split `.cursorrules` content into scoped `.mdc` files:
   - Global rules → `project.mdc` with `alwaysApply: true`
   - Language rules → `typescript.mdc` with `globs: "**/*.ts"`
3. Test: open Chat, type `@Cursor Rules` to verify rules load
4. Delete `.cursorrules` after confirming

### Cursor 2.0 Changes

Cursor 2.0 introduced:

- Agent-first architecture (Composer defaults to Agent mode)
- New Composer model (faster generation)
- Parallel agents (up to 8 simultaneous)
- Bug fixes in Chat may appear as: settings key renames, deprecated fields

Check [changelog.cursor.sh](https://changelog.cursor.sh) for specific breaking changes.

## Enterprise Considerations

- **Managed deployment**: Use MDM (macOS) or SCCM (Windows) to distribute Cursor with pre-configured settings
- **Version pinning**: Enterprise admins can control which Cursor versions are deployed
- **Settings templates**: Create a starter `settings.json` for new team members
- **Rollback**: Keep the previous installer if an update causes issues; downgrade by reinstalling

## Resources

- [Cursor Changelog](https://changelog.cursor.sh)
- [Cursor Downloads](https://cursor.com/download)
- [VS Code Migration Guide](https://docs.cursor.com/configuration/migrations/vscode)
- [Extensions Documentation](https://docs.cursor.com/configuration/extensions)
