---
name: cursor-known-pitfalls
description: 'Avoid common Cursor IDE pitfalls: AI feature mistakes, security gotchas,
  configuration errors, and

  team workflow issues. Triggers on "cursor pitfalls", "cursor mistakes", "cursor
  gotchas", "cursor issues",

  "cursor problems", "cursor tips".

  '
allowed-tools: Read, Write, Edit, Bash(cmd:*)
version: 1.19.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- cursor
- cursor-known
compatibility: Designed for Claude Code
---
# Cursor Known Pitfalls

## Overview

Use these pitfalls as preflight checks for AI-assisted work: context leakage, over-broad edits, stale rules, unsupported assumptions, and misplaced trust in generated output.

## Prerequisites

- Project rules, data classification, and a normal review/test path for the work.
- A non-sensitive reproduction or sample when evaluating a Cursor behavior.

## Instructions

1. Identify the relevant pitfall before accepting a suggestion or changing configuration.
2. Narrow context and task scope, then verify the resulting diff and tests.
3. Record recurring failures in reviewed rules or team guidance rather than relying on memory.

## Output

- A documented prevention or remediation action tied to a specific Cursor failure mode.

## Error Handling

| Condition | Safe response |
|---|---|
| AI output is plausible but unverified | Treat it as a proposal and run normal review/tests. |
| Context contains excluded material | Stop, remove it, and follow exposure policy. |
| Rule causes repeated wrong output | Revise it through review and test on a fixture. |

## Examples

Before accepting a multi-file refactor, check that it has an explicit file list, does not include secret/generated paths, and has tests. Reject broad changes and split the request when any of those checks fail.

Common Cursor IDE pitfalls and their solutions. Organized by category: AI behavior, security, configuration, performance, and team collaboration.

## AI Feature Pitfalls

### Pitfall 1: Blindly Applying Composer Changes

**Problem:** Clicking "Apply All" without reviewing diffs. Composer can generate code with wrong imports, hallucinated APIs, or logic errors.

**Solution:**

```
1. Click each file in the Changes panel to review its diff
2. Check imports: are they real packages in your project?
3. Check function calls: do the methods actually exist?
4. Run build after applying: npm run build
5. Run tests: npm test
6. Commit BEFORE running Composer (easy rollback with git checkout .)
```

### Pitfall 2: Context Window Overflow

**Problem:** Adding too many `@Files`, `@Folders`, and `@Codebase` references. The model silently drops information, leading to:

- Ignoring your instructions
- Repeating itself
- Generating generic instead of project-specific code

**Solution:**

```
- Use @Files (specific) over @Folders (broad) over @Codebase (broadest)
- Limit to 3-5 file references per prompt
- Start new chats for new topics
- Remove stale context pills by clicking X
```

### Pitfall 3: Continuing Stale Conversations

**Problem:** Reusing a 20+ turn conversation for a new task. The conversation history fills context, leaving no room for your new request.

**Solution:** `Cmd+N` to start a new chat for each distinct task.

### Pitfall 4: AI Generates Deprecated Patterns

**Problem:** AI uses old APIs (React class components, Express 4 syntax, CommonJS require).

**Solution:** Pin versions in project rules:

```yaml
# .cursor/rules/stack.mdc
---
description: "Tech stack versions"
globs: ""
alwaysApply: true
---
ALWAYS use these versions:
- React 19 with Server Components (NOT class components)
- Next.js 15 App Router (NOT Pages Router)
- TypeScript 5.7 strict (NOT any casts)
- ESM imports (NOT CommonJS require)
```

### Pitfall 5: Tab Completion Fighting Manual Input

**Problem:** Tab suggests text you do not want, and you accidentally accept it while pressing Tab for indentation.

**Solution:**

- Use `Esc` to dismiss before pressing Tab for indentation
- Remap Tab acceptance: `Cmd+K Cmd+S` > search `acceptCursorTabSuggestion` > assign different key
- Or temporarily disable Tab completion for specific tasks

## Security Pitfalls

### Pitfall 6: Pasting Secrets into Chat

**Problem:** Copying an error message that includes an API key, database URL, or token and pasting it into Chat.

**Solution:**

```
NEVER paste:
- .env file contents
- Error logs containing credentials
- Database connection strings
- API response headers with auth tokens

INSTEAD:
- Redact secrets before pasting: "API key sk-...XXXX returned 401"
- Describe the error without the sensitive values
- Use @Files to reference the code, not copy-paste
```

### Pitfall 7: No .cursorignore

**Problem:** Without `.cursorignore`, sensitive files (.env, credentials, PII) may be included in AI context via `@Codebase` search or automatic context.

**Solution:** Create `.cursorignore` in every project:

```gitignore
.env*
**/secrets/
**/credentials/
**/*.pem
**/*.key
```

### Pitfall 8: Privacy Mode Off

**Problem:** Without Privacy Mode, code may be retained by model providers for training.

**Solution:**

- Individual: `Cursor Settings` > `General` > Privacy Mode > ON
- Team: Admin Dashboard > Privacy > Enforce for all members
- Verify at cursor.com/settings

### Pitfall 9: Trusting AI-Generated Security Code

**Problem:** AI generates authentication, encryption, or authorization code that looks correct but has subtle vulnerabilities (timing attacks, SQL injection via string concatenation, missing CSRF protection).

**Solution:**

```
- Security-critical code ALWAYS needs human expert review
- Run SAST tools (Semgrep, Snyk) on AI-generated code
- Never deploy AI-generated auth code without penetration testing
- Add security rules in .cursor/rules/security.mdc
```

## Configuration Pitfalls

### Pitfall 10: No Project Rules

**Problem:** Without `.cursor/rules/`, the AI generates code without knowing your conventions, stack, or patterns. Result: inconsistent code that does not match your project.

**Solution:** Create at minimum:

1. `project.mdc` (stack, conventions, alwaysApply: true)
2. `security.mdc` (security constraints, alwaysApply: true)
3. Language-specific rules with glob patterns

### Pitfall 11: Conflicting Rules

**Problem:** Multiple `.mdc` rules with contradictory instructions (one says "use classes", another says "use functions").

**Solution:**

- Review all rules together for consistency
- Use specific globs so rules apply only to relevant files
- Test with `@Cursor Rules` in Chat to see which rules are active for a given file

### Pitfall 12: Running Multiple AI Completion Extensions

**Problem:** GitHub Copilot + Cursor Tab both enabled. Double ghost text, conflicting suggestions, UI glitches.

**Solution:** Disable all other inline completion extensions:

- GitHub Copilot
- TabNine
- Codeium
- IntelliCode

Only one inline completion provider should be active.

## Performance Pitfalls

### Pitfall 13: Opening Entire Monorepo

**Problem:** Opening a monorepo root with 200K files. Indexing takes hours, `@Codebase` returns noise, editor is sluggish.

**Solution:** Open specific packages: `cursor packages/api/`

### Pitfall 14: No File Watcher Exclusions

**Problem:** Cursor watches every file for changes, including `node_modules/`, `dist/`, and `.git/objects/`. Causes high CPU and memory.

**Solution:**

```json
// settings.json
{
  "files.watcherExclude": {
    "**/node_modules/**": true,
    "**/.git/objects/**": true,
    "**/dist/**": true,
    "**/build/**": true
  }
}
```

### Pitfall 15: Never Clearing Chat History

**Problem:** Running Cursor for weeks with dozens of open chat tabs. Memory grows, editor slows.

**Solution:** Close old chat tabs. Start new conversations. Restart Cursor weekly during heavy use.

## Team Collaboration Pitfalls

### Pitfall 16: Rules Not in Version Control

**Problem:** `.cursor/rules/` not committed to git. Each developer has different (or no) AI behavior rules.

**Solution:** Commit `.cursor/rules/` and `.cursorignore` to git. PR-review rule changes like any other configuration.

### Pitfall 17: No Code Review for AI Output

**Problem:** Developers commit AI-generated code without review. Bugs, wrong patterns, and security issues reach main branch.

**Solution:**

- Pre-commit hooks: lint + test (catches many AI errors)
- PR reviews: all code (human or AI) needs review
- Team policy: "AI output is a first draft, not production code"

### Pitfall 18: Inconsistent Model Selection

**Problem:** Some developers use Opus for everything (consuming quota fast), others use cursor-small (poor quality).

**Solution:**

- Set team default model in admin dashboard
- Document model selection guidance in onboarding
- Use Auto mode as default (Cursor selects appropriate model)

## Enterprise Considerations

- **Risk register**: Add Cursor-specific risks (AI hallucinations, data exposure) to your enterprise risk register
- **Training**: Quarterly refresher on pitfalls, especially security-related ones
- **Incident response**: Have a plan for "AI-generated code caused production incident" scenario
- **Vendor risk**: Review Cursor's security page annually as their practices evolve

## Resources

- [Cursor Security](https://cursor.com/security)
- [Cursor Data Use Policy](https://cursor.com/data-use)
- [Cursor Community Forum](https://forum.cursor.com)
