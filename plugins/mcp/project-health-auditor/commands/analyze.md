---
name: analyze
description: Trigger full repository health analysis
---
# Repository Health Analysis

Analyze the code health of a repository using multi-dimensional metrics.

## Instructions

When the user requests a repository health analysis, follow this systematic approach:

1. **List Files**: Use `list_repo_files` to discover all source files
2. **Analyze Complexity**: Use `file_metrics` on key files to assess complexity
3. **Check Git Churn**: Use `git_churn` to identify frequently changing files
4. **Map Test Coverage**: Use `map_tests` to find files missing tests
5. **Generate Report**: Combine all metrics into actionable recommendations

For `list_repo_files` and `map_tests`, collect every page: keep repository and
filters fixed, advance `offset` by `showing`, and continue while `hasMore` is true.
The default and maximum page size is 100. Inventory arrays/maps contain only the
current page; summaries describe the complete unpaginated scan under the tool
discovery rules and active filters. Test mapping is based on
filenames, so report its ratio separately from measured coverage and test results.

## Analysis Workflow

### Step 1: File Discovery

```
Use list_repo_files with appropriate globs for the language:
- TypeScript/JavaScript: ["**/*.{ts,tsx,js,jsx}"]
- Python: ["**/*.py"]
- Go: ["**/*.go"]
- Multi-language: Combine patterns

Exclude: ["node_modules/**", ".git/**", "dist/**", "build/**"]
```

### Step 2: Complexity Analysis

Focus on:

- Files > 300 lines
- Core business logic files (services, controllers, models)
- Recently changed files

For each file, report:

- Cyclomatic complexity
- Function count
- Health score
- Comment ratio

### Step 3: Git Churn Analysis

Identify hot spots:

- Files with >10 commits (high churn)
- Files changed by multiple authors
- Recent change patterns

### Step 4: Test Coverage Mapping

Find gaps:

- Files in critical directories missing tests
- High-complexity files without tests
- High-churn files without tests

### Step 5: Prioritized Recommendations

Combine metrics to find:

- **Technical Debt Hot Spots**: High complexity + High churn + No tests
- **Refactoring Candidates**: Complexity >10 + Health score <50
- **Testing Priorities**: Critical files missing tests

## Output Format

Present findings in this structure:

### Repository Overview

- Total files: X
- Average health score: Y
- Test coverage: Z%

### Critical Issues

1. High complexity + High churn + No tests
2. Health score <30 (critical)

### ️  Warnings

1. Health score 30-70 (needs attention)
2. Test coverage <60%

### Good Practices

1. Well-tested files (high complexity + has tests)
2. Stable code (low churn + good health)

### Recommendations

Prioritized list of actions:

1. Add tests for critical files
2. Refactor high-complexity hot spots
3. Monitor high-churn files

## Example Usage

User: "Analyze the health of /home/user/my-project"

Response:

```
I'll analyze the code health of your project using multiple dimensions...

[Use list_repo_files on /home/user/my-project]
Found 245 source files (TypeScript/JavaScript)

[Use file_metrics on top files]
Critical complexity issues:
- src/services/auth.ts: Complexity 45, Health 30 
- src/api/handler.ts: Complexity 28, Health 65 ️

[Use git_churn on /home/user/my-project since "6 months ago"]
High churn files:
- src/api/handler.ts: 32 commits, 4 authors
- src/services/auth.ts: 18 commits, 2 authors

[Use map_tests on /home/user/my-project]
Test coverage: 62% (97 of 156 files tested)
Missing tests: 59 files

Critical files without tests:
- src/services/auth.ts (high complexity + high churn) 
- src/api/legacy.ts (high complexity)

## Recommendations:
1.  URGENT: Add tests for src/services/auth.ts (high complexity, high churn, no tests)
2. ️  Refactor src/api/handler.ts (complexity 28, reduce to <10)
3.  Improve test coverage to 80%+ (currently 62%)
```

## Notes

- Always use absolute paths
- Adjust time period for git_churn based on project age
- For large repos (>500 files), focus on changed files in last 3 months
- Combine metrics for maximum insight
