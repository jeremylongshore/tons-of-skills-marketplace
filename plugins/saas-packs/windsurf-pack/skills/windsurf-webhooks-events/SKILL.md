---
name: windsurf-webhooks-events
description: 'Build Devin Desktop (formerly Windsurf) extensions and integrate with VS Code extension API events.

  Use when building custom Windsurf extensions, tracking editor events,

  or integrating Windsurf with external tools via extension development.

  Trigger with phrases like "windsurf extension", "windsurf events",

  "windsurf plugin", "build windsurf extension", "windsurf API".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(npx:*)
argument-hint: "[scope or requirements]"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- windsurf
- extensions
- vscode-api
- development
compatibility: Designed for Claude Code
---
# Windsurf Extension Development & Events

## Overview

Build compatible extensions on Devin Desktop's VS Code foundation to observe workspace events and integrate external tools. Keep telemetry, credential, network, and user-consent boundaries explicit instead of assuming every VS Code behavior is product-guaranteed.

## Prerequisites

- Node.js 18+ and npm
- VS Code Extension API familiarity
- `yo` and `generator-code` for scaffolding
- Windsurf IDE for testing

## Tool Use

- Use `Read` to inspect only the repository files and configuration needed for the request.
- Use `Write` only for a new artifact the user requested; never write credentials or unreviewed production configuration.
- Use `Edit` for bounded, reviewable changes and preserve unrelated user work.
- Use only the command-scoped `Bash` entries declared in frontmatter, with non-destructive checks before mutations.

## Instructions

### Step 1: Scaffold Extension

```bash
# Install scaffolding tools
npm install -g yo generator-code

# Generate extension
yo code
# Select: New Extension (TypeScript)
# Name: my-windsurf-extension
```

### Step 2: Track Workspace Events

```typescript
// src/extension.ts
import * as vscode from "vscode";

export function activate(context: vscode.ExtensionContext) {
  console.log("Extension active in Windsurf");

  // Track file saves
  const saveListener = vscode.workspace.onDidSaveTextDocument(
    async (document) => {
      const diagnostics = vscode.languages.getDiagnostics(document.uri);
      const errors = diagnostics.filter(
        (d) => d.severity === vscode.DiagnosticSeverity.Error
      );
      if (errors.length > 0) {
        vscode.window.showWarningMessage(
          `${document.fileName}: ${errors.length} error(s) after save`
        );
      }
    }
  );

  // Track active editor changes
  const editorListener = vscode.window.onDidChangeActiveTextEditor(
    (editor) => {
      if (editor) {
        const lang = editor.document.languageId;
        const lines = editor.document.lineCount;
        console.log(`Opened: ${editor.document.fileName} (${lang}, ${lines} lines)`);
      }
    }
  );

  // Track terminal output
  const terminalListener = vscode.window.onDidWriteTerminalData((event) => {
    // Can monitor for specific patterns (errors, warnings)
    if (event.data.includes("ERROR") || event.data.includes("FAIL")) {
      vscode.window.showWarningMessage("Error detected in terminal output");
    }
  });

  context.subscriptions.push(saveListener, editorListener, terminalListener);
}
```

### Step 3: Send Events to External System

```typescript
// src/webhook.ts
import * as vscode from "vscode";

interface WorkspaceEvent {
  event: string;
  file?: string;
  language?: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

async function sendEvent(event: WorkspaceEvent): Promise<void> {
  const webhookUrl = vscode.workspace
    .getConfiguration("windsurf-events")
    .get<string>("webhookUrl");

  if (!webhookUrl) return;

  try {
    await fetch(webhookUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(event),
    });
  } catch (err) {
    console.warn("Webhook delivery failed:", err);
  }
}

// Debounce frequent events
const debounceMap = new Map<string, NodeJS.Timeout>();

function debouncedSend(event: WorkspaceEvent, delayMs = 2000): void {
  const key = `${event.event}:${event.file}`;
  clearTimeout(debounceMap.get(key));
  debounceMap.set(
    key,
    setTimeout(() => {
      sendEvent(event);
      debounceMap.delete(key);
    }, delayMs)
  );
}
```

### Step 4: Extension package.json

```json
{
  "name": "windsurf-events",
  "displayName": "Windsurf Events",
  "version": "1.0.0",
  "engines": { "vscode": "^1.85.0" },
  "activationEvents": ["onStartupFinished"],
  "main": "./dist/extension.js",
  "contributes": {
    "configuration": {
      "title": "Windsurf Events",
      "properties": {
        "windsurf-events.webhookUrl": {
          "type": "string",
          "description": "URL to send workspace events to"
        },
        "windsurf-events.trackSaves": {
          "type": "boolean",
          "default": true,
          "description": "Track file save events"
        },
        "windsurf-events.trackErrors": {
          "type": "boolean",
          "default": true,
          "description": "Track terminal error events"
        }
      }
    },
    "commands": [
      {
        "command": "windsurf-events.showStatus",
        "title": "Windsurf Events: Show Status"
      }
    ]
  }
}
```

### Step 5: Build and Install

```bash
# Build
npm run compile
# or: npm run build

# Package as .vsix
npx vsce package

# Install in Windsurf
windsurf --install-extension windsurf-events-1.0.0.vsix

# Or publish to marketplace
npx vsce publish
```

### Step 6: Test in Windsurf

```
1. Open Extension Development Host: F5 in Windsurf
2. A new Windsurf window opens with extension loaded
3. Open a file, save it, trigger events
4. Check Output panel > "Windsurf Events" channel
5. Verify webhook delivery (use https://webhook.site for testing)
```

## Output

Produce a reviewed VS Code-compatible extension change with event subscriptions, disposal lifecycle, authentication and secret storage, payload schema, retry behavior, local test evidence, package metadata, and marketplace compatibility notes. Do not log raw credentials or proprietary source.

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| Extension not activating | Wrong `activationEvents` | Use `onStartupFinished` for always-on |
| Webhook fails | Network/URL issue | Queue locally, retry with backoff |
| High CPU usage | Too many listeners | Debounce frequent events (saves, edits) |
| API incompatibility | Windsurf vs VS Code version | Pin `engines.vscode` version |
| `vsce package` fails | Missing fields | Add publisher, repository, license |

## Examples

### Team Analytics Extension

```typescript
// Track AI acceptance rate per developer
vscode.languages.registerInlineCompletionItemProvider(
  { pattern: "**" },
  {
    provideInlineCompletionItems(document, position) {
      // Log completion requests (don't interfere with Supercomplete)
      console.log(`Completion at ${document.fileName}:${position.line}`);
      return []; // Return empty -- let Windsurf handle completions
    }
  }
);
```

### Quick Test Webhook

```bash
# Start a test webhook receiver
npx -y webhook-relay -p 3456
# Configure extension: windsurf-events.webhookUrl = "http://localhost:3456"
```

## Resources

- [Focused first-party references](references/official-docs.md)
- [VS Code Extension API](https://code.visualstudio.com/api)
- [VS Code Extension Publishing](https://code.visualstudio.com/api/working-with-extensions/publishing-extension)
- [Windsurf Marketplace](https://marketplace.windsurf.com)

## Related Skill

Continue with `windsurf-multi-env-setup` to package extension settings, event destinations, and environment-specific policies for repeatable team rollout.
