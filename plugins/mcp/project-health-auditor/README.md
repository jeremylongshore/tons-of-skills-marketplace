# Project Health Auditor

**MCP Server Plugin for Claude Code**

Analyze local repositories for code health, complexity, test coverage gaps, and git churn patterns. Get multi-dimensional insights into your codebase health combining complexity metrics, change frequency, and test coverage.

---

## Features

### 4 Powerful MCP Tools

**1. `list_repo_files`** - File Discovery

- List all files in a repository with glob pattern matching
- Exclude patterns (node_modules, .git, dist, build)
- Returns file count and full file list

**2. `file_metrics`** - Code Health Analysis

- Cyclomatic complexity calculation
- Function/method counting
- Comment ratio analysis
- File size and line count
- Health score (0-100) based on multiple factors

**3. `git_churn`** - Change Frequency Analysis

- Identify files that change frequently
- Track authors per file
- Find hot spots in your codebase
- Analyze commit patterns over time

**4. `map_tests`** - Test Coverage Mapping

- Map source files to test files
- Identify files missing tests
- Calculate test coverage ratio
- Get actionable recommendations

---

## Installation

```bash
# Install the plugin
/plugin install project-health-auditor@claude-code-plugins-plus

# The MCP server will be automatically available
```

---

## Usage

### Quick Analysis

```
Analyze the health of /path/to/my-project
```

Claude will use the MCP tools to:

1. List all source files
2. Analyze complexity of key files
3. Check git churn patterns
4. Map test coverage

### Individual Tool Usage

**List Repository Files:**

```
Use list_repo_files on /path/to/repo with globs ["src/**/*.ts", "lib/**/*.js"]
```

**Analyze File Metrics:**

```
What's the complexity of src/services/auth.ts?
```

**Check Git Churn:**

```
Show me the most frequently changed files in the last 6 months
```

**Map Tests:**

```
Which files are missing tests in this project?
```

---

## ️ MCP Tools Reference

### list_repo_files

**Purpose:** Discover files in a repository

**Input:**

```typescript
{
  repoPath: string;           // Absolute path to repository
  globs?: string[];           // Patterns to match (default: ["**/*"])
  exclude?: string[];         // Patterns to exclude
  limit?: number;             // Integer 1..100; default 100
  offset?: number;            // Nonnegative integer; default 0
}
```

**Output:**

```json
{
  "repoPath": "/path/to/repo",
  "totalFiles": 245,
  "limit": 100,
  "offset": 0,
  "showing": 100,
  "hasMore": true,
  "files": ["src/index.ts", "src/utils/helper.ts", ...],
  "patterns": ["**/*"],
  "excluded": ["node_modules/**", ".git/**"]
}
```

---

For both inventory tools, advance `offset` by `showing` while `hasMore` is true,
keeping the same repository and filters. Pages are sorted and reflect current
files, so repository changes between calls can shift offsets. Invalid paging
values return an argument error. `totalFiles` covers all files matching the
active list filters; `map_tests.summary` covers its complete unpaginated source
and test scan. `files`, `sourceFiles`, `coverage`, and `missingTests` contain only
the current page. `map_tests` pages source files, including both matched and
unmatched files, so missing tests beyond the old 50-file preview are reachable.
Individual paths and matching-test arrays remain intact; item limits do not
bound serialized characters or analysis time. Test mapping uses filename
heuristics; its ratio is not measured line coverage or proof that tests passed.

### file_metrics

**Purpose:** Analyze a single file's health

**Input:**

```typescript
{
  filePath: string;  // Absolute path to file
}
```

**Output:**

```json
{
  "file": "src/services/auth.ts",
  "size": 12543,
  "lines": 342,
  "extension": ".ts",
  "complexity": {
    "cyclomatic": 28,
    "functions": 12,
    "averagePerFunction": 2
  },
  "comments": {
    "lines": 45,
    "ratio": 13.16
  },
  "healthScore": 75
}
```

**Health Score Factors:**

- **High complexity** (>10 per function): -30 points
- **Medium complexity** (5-10): -15 points
- **Low comments** (<5%): -10 points
- **Good comments** (>20%): +10 points
- **Very long files** (>500 lines): -20 points
- **Long files** (>300 lines): -10 points

---

### git_churn

**Purpose:** Find frequently changing files (hot spots)

**Input:**

```typescript
{
  repoPath: string;             // Absolute path to git repository
  since?: string;               // Time period (default: "6 months ago")
}
```

**Output:**

```json
{
  "repoPath": "/path/to/repo",
  "since": "6 months ago",
  "totalCommits": 342,
  "filesChanged": 156,
  "topChurnFiles": [
    {
      "file": "src/api/handler.ts",
      "commits": 45,
      "authors": ["Alice", "Bob"],
      "authorCount": 2
    }
  ],
  "summary": {
    "highChurn": 12,      // >10 commits
    "mediumChurn": 34,    // 5-10 commits
    "lowChurn": 110       // <5 commits
  }
}
```

**High churn files are candidates for refactoring or stabilization.**

---

### map_tests

**Purpose:** Identify test coverage gaps

**Input:**

```typescript
{
  repoPath: string;  // Absolute path to repository
  limit?: number;   // Integer 1..100; default 100
  offset?: number;  // Nonnegative integer; default 0
}
```

**Output:**

```json
{
  "repoPath": "/path/to/repo",
  "limit": 100,
  "offset": 0,
  "showing": 100,
  "hasMore": true,
  "sourceFiles": ["src/services/auth.ts", "src/utils/helper.ts", "..."],
  "summary": {
    "totalSourceFiles": 156,
    "totalTestFiles": 98,
    "testedFiles": 102,
    "coverageRatio": 65.38
  },
  "coverage": {
    "src/services/auth.ts": ["src/services/auth.test.ts"],
    "src/utils/helper.ts": ["src/utils/helper.spec.ts"]
  },
  "missingTests": [
    "src/api/legacy.ts",
    "src/utils/old-helper.ts"
  ],
  "recommendations": [
    "️  Test coverage is below 80%. Consider adding tests for remaining files.",
    " High priority: Add tests for 23 files in critical directories"
  ]
}
```

---

## Use Cases

### 1. Pre-Refactoring Analysis

Before refactoring, identify:

- High complexity files (complexity > 10)
- High churn files (commits > 10)
- Files missing tests

**Strategy:** Refactor high-complexity, high-churn files first.

### 2. Code Review Preparation

Analyze changed files:

```
What's the complexity of the files I changed in the last commit?
```

### 3. Test Coverage Improvement

Find critical files without tests:

```
Which files in src/services/ are missing tests?
```

### 4. Technical Debt Identification

Combine metrics to find problematic files:

- High complexity + High churn + Missing tests = **Technical debt hot spot**

### 5. Onboarding New Developers

Show new team members:

- Most frequently changed files
- Core files with good health scores
- Areas needing test coverage

---

## Health Score Interpretation

| Score | Health | Action |
|-------|--------|--------|
| 90-100 | Excellent | Maintain current quality |
| 70-89 | Good | Minor improvements recommended |
| 50-69 | Fair | Consider refactoring |
| 30-49 | Poor | Refactoring needed |
| 0-29 | Critical | Immediate attention required |

---

## ️ Architecture

### Technology Stack

- **TypeScript** - Type-safe implementation
- **@modelcontextprotocol/sdk** - MCP server framework
- **glob** - File pattern matching
- **simple-git** - Git operations
- **zod** - Runtime type validation

### Project Structure

```
project-health-auditor/
├── servers/
│   └── code-metrics.ts        # MCP server with 4 tools
├── tests/
│   └── code-metrics.test.ts   # Comprehensive tests
├── .claude-plugin/
│   └── plugin.json            # Plugin metadata
├── .mcp.json                  # MCP server configuration
├── package.json               # Dependencies
├── tsconfig.json              # TypeScript config
└── README.md                  # This file
```

---

## Development

### Build

```bash
npm run build
```

### Test

```bash
npm test              # Run tests
npm run test:ci       # CI mode (no watch)
```

### Type Check

```bash
npm run typecheck
```

### Run Locally

```bash
npm run dev
```

---

## Metrics Explained

### Cyclomatic Complexity

Measures the number of independent paths through code:

- **1-10:** Simple, low risk
- **11-20:** Moderate complexity
- **21-50:** High complexity, hard to test
- **50+:** Very high risk, needs refactoring

**Calculation:** Count of control flow keywords (if, for, while, switch, &&, ||, ?) + 1

### Git Churn

Frequency of file changes:

- **High churn** (>10 commits): Hot spot, may need stabilization
- **Medium churn** (5-10): Normal development activity
- **Low churn** (<5): Stable or new file

**Why it matters:** High churn + High complexity = Technical debt

### Test Coverage Ratio

Percentage of source files with corresponding tests:

- **80-100%:** Excellent
- **60-79%:** Good
- **40-59%:** Fair
- **<40%:** Poor

---

## Contributing

This plugin is part of the Claude Code Plugins marketplace.

### Report Issues

https://github.com/jeremylongshore/claude-code-plugins/issues

### Suggest Features

Open an issue with the `enhancement` label.

---

## License

MIT License - see LICENSE file

---

## Credits

**Built by:** Intent Solutions IO
**Website:** https://intentsolutions.io
**Email:** [email protected]

**Part of the Claude Code Plugins Marketplace**

---

## Related Plugins

- **conversational-api-debugger** - API debugging with OpenAPI specs
- **test-coverage-booster** - AI-powered test generation
- **performance-profiler** - Full-stack performance analysis

---

**Generated with Claude Code**
**Co-Authored-By:** Claude <noreply@anthropic.com>
