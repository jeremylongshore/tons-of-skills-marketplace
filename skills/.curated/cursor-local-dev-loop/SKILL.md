---
name: cursor-local-dev-loop
description: 'Optimize daily development workflow with Cursor IDE using Chat, Composer,
  Tab, and Git integration.

  Triggers on "cursor workflow", "cursor development loop", "cursor productivity",
  "cursor daily workflow",

  "cursor dev flow".

  '
allowed-tools: Read, Write, Edit, Bash(cmd:*)
version: 1.19.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- cursor
- workflow
compatibility: Designed for Claude Code
---
# Cursor Local Dev Loop

## Overview

Use Cursor inside the normal local development loop: small scoped change, inspect diff, run focused checks, commit reviewed work, and retain a rollback path.

## Prerequisites

- A clean or recoverable branch, repository instructions, and required local test/format commands.
- Approved privacy settings and exclusion of secrets, production exports, and unrelated repositories.

## Instructions

1. Start with a narrow issue and affected-file list, then use Chat/Inline Edit/Composer only for that scope.
2. Inspect every proposed diff and run the narrowest relevant formatter, test, and static check.
3. Commit one reviewed change at a time and use normal pull-request/branch rules for integration.
4. Revert rather than patching around an AI-generated regression when a focused check fails.

## Output

- A small reviewed local change with validation evidence and an ordinary git rollback path.

## Error Handling

| Condition | Safe response |
|---|---|
| Generated change is broad | Reject/split it before applying. |
| Test fails | Diagnose and revert or fix within scope; do not disable the test. |
| Working tree is mixed | Stash or commit unrelated user work before continuing. |

## Examples

Ask Inline Edit to update one function, inspect the diff, run that function's focused test, and commit it separately. If the test fails or unrelated files change, reject/revert and restate the task with tighter constraints.

Establish a productive daily development workflow using Cursor's AI features at each stage of the code-write-test-commit cycle.

## The AI-Augmented Development Loop

```
┌─────────────────────────────────────────────────────────────┐
│  1. PLAN        →  Chat (Cmd+L) with @Codebase, @Docs      │
│  2. SCAFFOLD    →  Composer (Cmd+I) for new files           │
│  3. IMPLEMENT   →  Tab completion for line-by-line coding   │
│  4. REFINE      →  Inline Edit (Cmd+K) for targeted fixes  │
│  5. TEST        →  Chat to generate tests, terminal to run  │
│  6. COMMIT      →  AI-generated commit messages             │
│  7. REVIEW      →  @Git for branch diff review              │
└─────────────────────────────────────────────────────────────┘
```

## Stage 1: Plan (Chat)

Start each task by discussing architecture with Chat:

```
@Codebase @Docs Prisma

I need to add a "favorites" feature where users can bookmark products.
What's the best approach given our current data model and API structure?
Consider: database schema, API endpoints, and frontend hooks.
```

Chat excels at:

- Architecture decisions before writing code
- Evaluating trade-offs (SQL join table vs JSON array, REST vs GraphQL)
- Understanding existing patterns via `@Codebase`

## Stage 2: Scaffold (Composer)

Once the plan is clear, use Composer for multi-file generation:

```
@src/api/users/route.ts @prisma/schema.prisma

Create the favorites feature:
1. prisma/schema.prisma: Favorite model (userId, productId, createdAt)
2. src/api/favorites/route.ts: GET (list user favorites), POST (add), DELETE (remove)
3. src/services/favorite.service.ts: FavoriteService with Prisma operations
4. src/hooks/useFavorites.ts: React hook with optimistic updates
Follow existing patterns from the users API.
```

**Tip:** Reference existing files with `@` so Composer replicates your patterns instead of inventing new ones.

## Stage 3: Implement (Tab Completion)

With scaffolded files open, use Tab for implementation details:

```typescript
// Open favorite.service.ts and start typing:
async toggleFavorite(userId: string, productId: string

// Tab completes the full method:
async toggleFavorite(userId: string, productId: string): Promise<Favorite | null> {
  const existing = await this.prisma.favorite.findUnique({
    where: { userId_productId: { userId, productId } },
  });
  if (existing) {
    await this.prisma.favorite.delete({ where: { id: existing.id } });
    return null;
  }
  return this.prisma.favorite.create({ data: { userId, productId } });
}
```

**Workflow tips for Tab:**

- Open related files in tabs (service, types, API route) -- Tab reads open tabs for context
- Write type signatures first -- Tab generates better bodies when types are explicit
- Accept partially with `Cmd+→` when the suggestion is 80% right

## Stage 4: Refine (Inline Edit)

For targeted improvements, select code and use `Cmd+K`:

```
Select the toggleFavorite method → Cmd+K:
"Add input validation: userId and productId must be non-empty strings.
 Add error handling for database connection failures.
 Return a Result type instead of throwing."
```

Other common Cmd+K workflows:

- `"Add JSDoc comments"` on a function
- `"Convert to async/await"` on a Promise chain
- `"Add null checks"` on a code block
- `"Optimize this query"` on a database call

## Stage 5: Test (Chat + Terminal)

Generate tests via Chat:

```
@src/services/favorite.service.ts @tests/services/user.service.test.ts

Generate vitest tests for FavoriteService following the same patterns as
user.service.test.ts. Cover: addFavorite, removeFavorite, toggleFavorite,
getFavorites with pagination. Mock Prisma client.
```

Run tests in the integrated terminal:

```bash
# Cmd+` to open terminal
npm test -- --watch src/services/favorite.service.test.ts
```

If tests fail, paste the error into Chat:

```
@src/services/favorite.service.ts
This test is failing with: "Expected null but received undefined"
[paste test output]
What's wrong?
```

## Stage 6: Commit (AI Messages)

Use Cursor's Source Control panel (`Cmd+Shift+G`):

1. Stage changed files
2. Click the sparkle icon (AI) next to the commit message input
3. Cursor generates a commit message from the diff:

```
feat: add favorites feature with toggle, pagination, and optimistic updates

- Add Favorite model to Prisma schema with userId/productId unique constraint
- Create REST API endpoints (GET, POST, DELETE) for /api/favorites
- Implement FavoriteService with toggleFavorite and paginated listing
- Add useFavorites React hook with optimistic UI updates
```

## Stage 7: Review (@Git)

Before pushing, review your full branch diff:

```
@Git

Review all changes in this branch compared to main.
Check for:
- Missing error handling
- Type safety issues
- Potential N+1 query problems
- Any hardcoded values that should be environment variables
```

`@Git` includes the branch diff in context, giving the AI a complete view of all your changes.

## Daily Efficiency Tips

### Session Management

```
Morning startup:
1. cursor .                          # Open project
2. Wait for "Indexed" in status bar  # Indexing complete
3. Cmd+Shift+G → git pull           # Sync with team
4. Cmd+L → "What changed yesterday? @Git"

Task switching:
- Start a new Chat (Cmd+N) for each task
- Do NOT continue a 20-turn conversation on a new topic
```

### Keyboard-Driven Flow

Minimize mouse usage:

```
Cmd+P          →  Open any file by name
Cmd+Shift+P    →  Run any command
Cmd+L          →  Ask AI anything
Cmd+K          →  Edit selected code
Cmd+I          →  Multi-file changes
Cmd+`          →  Toggle terminal
Cmd+B          →  Toggle sidebar
Cmd+Shift+G    →  Git panel
```

### Project Rules for Consistency

Create `.cursor/rules/dev-standards.mdc`:

```yaml
---
description: "Development standards for all code"
globs: ""
alwaysApply: true
---
- Run `npm test` before committing
- All new functions need JSDoc comments
- Use Conventional Commits format
- No console.log in committed code (use proper logger)
```

## Enterprise Considerations

- **Reproducible workflows**: Document the AI-augmented workflow in team runbooks
- **Code review**: AI-generated code still needs human review -- Composer output is a first draft
- **Onboarding**: New team members can use Chat with `@Codebase` to explore unfamiliar code
- **Metrics**: Track time-to-feature before and after Cursor adoption to quantify ROI

## Resources

- [Cursor Feature Overview](https://cursor.com/features)
- [Keyboard Shortcuts](https://docs.cursor.com/kbd)
- [Context Management](https://docs.cursor.com/context/@-symbols/overview)
