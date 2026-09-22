---
name: cursor-extension-integration
description: 'Integrate VS Code extensions with Cursor IDE: compatibility, Open VSX
  registry, VSIX installation,

  conflict resolution, and essential extensions. Triggers on "cursor extensions",
  "cursor vscode extensions",

  "cursor plugins", "cursor marketplace", "open vsx", "vsix install".

  '
allowed-tools: Read, Write, Edit, Bash(cmd:*)
version: 1.19.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- cursor
- cursor-extension
compatibility: Designed for Claude Code
---
# Cursor Extension Integration

## Overview

Add extensions only when their publisher, permissions, data flow, compatibility, and maintenance risk are understood for the target repository.

## Prerequisites

- Approved extension source, publisher verification, and workspace/data classification.
- A disposable profile or test workspace and a rollback method for extension settings.

## Instructions

1. Review publisher, permissions, license, update history, and network/data behavior.
2. Test one extension in an isolated profile with a non-sensitive workspace.
3. Check conflicts with Cursor, rules, completion providers, and repository tooling.
4. Approve, document, and periodically review the extension; remove it on security or compatibility failure.

## Output

- A tested extension decision with owner, version, permission/data assessment, and rollback path.

## Error Handling

| Condition | Safe response |
|---|---|
| Extension conflicts or degrades editor behavior | Disable/remove it in the test profile and retain diagnostics. |
| Extension requests unapproved access | Do not install; seek security review or an approved alternative. |
| Update changes permissions | Hold update until the new permissions are reviewed. |

## Examples

Test a formatter extension in a disposable profile against a sample repository, verify it does not transmit code or conflict with existing formatting, and then document the approved version. Remove it rather than disabling security controls if it conflicts.

Integrate VS Code extensions with Cursor IDE. Covers the Open VSX Registry, VSIX installation for Microsoft-exclusive extensions, conflict resolution with AI features, and recommended extension stacks.

## Extension Marketplace: Key Difference from VS Code

Cursor uses the **Open VSX Registry** instead of Microsoft's VS Code Marketplace. This is because Microsoft's marketplace terms restrict access to VS Code products only.

**Impact:** Most popular extensions are on Open VSX. Some Microsoft-published extensions are not.

### Available on Open VSX (works directly)

| Extension | Category |
|-----------|----------|
| ESLint | Linting |
| Prettier | Formatting |
| GitLens | Git visualization |
| Docker | Container management |
| Python | Python language support |
| Pylance | Python analysis (community build) |
| Go | Go language support |
| Rust Analyzer | Rust language support |
| Tailwind CSS IntelliSense | CSS utilities |
| Auto Rename Tag | HTML/JSX editing |
| Error Lens | Inline error display |
| TODO Highlight | Comment highlighting |
| Thunder Client | API testing |

### NOT Available on Open VSX (need manual install)

| Extension | Reason | Workaround |
|-----------|--------|------------|
| GitHub Copilot | Microsoft exclusive | Use Cursor's built-in AI (better integration) |
| Live Share | Microsoft exclusive | Use other collaboration tools |
| Remote - SSH | Microsoft exclusive | Install via VSIX |
| C# Dev Kit | Microsoft exclusive | Install via VSIX |
| IntelliCode | Microsoft exclusive | Cursor's Tab replaces this |

## Installing Extensions

### From Open VSX (In-App)

```
Cmd+Shift+X → search extension name → Install
```

### From VSIX (Manual)

For extensions not on Open VSX:

1. Go to the VS Code Marketplace website: [marketplace.visualstudio.com](https://marketplace.visualstudio.com)
2. Find the extension page
3. Click "Download Extension" (downloads `.vsix` file)
4. In Cursor: `Cmd+Shift+P` > `Extensions: Install from VSIX...`
5. Select the downloaded `.vsix` file

### From Command Line

```bash
# Install from Open VSX
cursor --install-extension dbaeumer.vscode-eslint

# Install from VSIX file
cursor --install-extension ~/Downloads/extension.vsix

# List installed extensions
cursor --list-extensions

# Uninstall
cursor --uninstall-extension dbaeumer.vscode-eslint
```

## Conflict Resolution with Cursor AI

### Extensions That Conflict with Cursor

| Extension | Conflict | Resolution |
|-----------|----------|------------|
| **GitHub Copilot** | Duplicate Tab/ghost text suggestions | Disable Copilot. Cursor's built-in AI is better integrated |
| **TabNine** | Duplicate inline completions | Disable TabNine |
| **Codeium** | Duplicate inline completions | Disable Codeium |
| **IntelliCode** | Duplicate completions | Disable IntelliCode |
| **Vim** | Ctrl+K/L/I keybinding conflicts | Remap AI shortcuts (see below) |

### Vim Extension Conflict Resolution

```json
// keybindings.json
[
  {
    "key": "ctrl+l",
    "command": "aichat.focus",
    "when": "!vim.active || vim.mode == 'Normal'"
  },
  {
    "key": "ctrl+k",
    "command": "cursor.edit",
    "when": "editorTextFocus && vim.mode == 'Normal'"
  },
  {
    "key": "ctrl+i",
    "command": "composer.open",
    "when": "!vim.active || vim.mode == 'Normal'"
  }
]
```

### General Keybinding Conflict Check

`Cmd+K Cmd+S` > search for the conflicting shortcut > see which commands are bound > reassign or disable.

## Recommended Extension Stacks

### JavaScript / TypeScript

```
Required:
  dbaeumer.vscode-eslint          # Linting
  esbenp.prettier-vscode          # Formatting
  bradlc.vscode-tailwindcss       # Tailwind CSS (if using)

Recommended:
  formulahendry.auto-rename-tag   # HTML/JSX tag renaming
  usernamehw.errorlens            # Inline error display
  wix.vscode-import-cost          # Import size display
  christian-kohler.path-intellisense  # Path autocomplete
```

### Python

```
Required:
  ms-python.python                # Python language support
  charliermarsh.ruff              # Fast Python linter

Recommended:
  ms-python.debugpy               # Python debugger
  njpwerner.autodocstring         # Docstring generator
  ms-toolsai.jupyter              # Jupyter notebook support
```

### Go / Rust

```
Go:
  golang.go                       # Official Go extension

Rust:
  rust-lang.rust-analyzer         # Rust language server
  tamasfe.even-better-toml        # TOML config files
```

### DevOps

```
  ms-azuretools.vscode-docker     # Docker support
  redhat.vscode-yaml              # YAML validation
  hashicorp.terraform             # Terraform HCL support
  ms-kubernetes-tools.vscode-kubernetes-tools  # Kubernetes
```

## Performance Impact

Extensions affect editor performance. Audit regularly:

### Measuring Extension Impact

1. `Cmd+Shift+P` > `Developer: Show Running Extensions`
2. Sort by activation time or profile time
3. Disable extensions with high activation times that you rarely use

### Common Performance Offenders

| Extension | Issue | Fix |
|-----------|-------|-----|
| GitLens | High CPU on large repos | Disable for repos > 100K commits |
| Prettier (on save) | Slow on large files | Configure file size limit |
| TypeScript | High memory on large projects | Increase `tsserver.maxTsServerMemory` |
| Spell checker | CPU on large files | Exclude generated files |

### Disabling Extensions Per Workspace

```json
// .vscode/settings.json (per project)
{
  "extensions.ignoreRecommendations": true
}
```

Or right-click an extension > `Disable (Workspace)` to disable only for the current project.

## Extension Settings Sync

Cursor does not sync extensions between machines automatically like VS Code Settings Sync. To transfer:

```bash
# Export extension list
cursor --list-extensions > cursor-extensions.txt

# On new machine, reinstall all
while read ext; do cursor --install-extension "$ext"; done < cursor-extensions.txt
```

## Enterprise Considerations

- **Extension allow/deny lists**: No built-in mechanism in Cursor. Enforce via documentation and team policy.
- **VSIX vetting**: Review VSIX files before distributing to team (check for telemetry, network calls)
- **Open VSX vs Marketplace**: Some extensions have different publishers on Open VSX. Verify publisher identity.
- **Extension updates**: Extensions auto-update from Open VSX. VSIX-installed extensions do NOT auto-update.

## Resources

- [Cursor Extensions Documentation](https://docs.cursor.com/configuration/extensions)
- [Open VSX Registry](https://open-vsx.org)
- [VS Code Marketplace](https://marketplace.visualstudio.com) (for VSIX downloads)
