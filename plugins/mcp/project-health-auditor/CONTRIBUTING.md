# Contributing to project-health-auditor

Thank you for your interest in contributing! This MCP server helps developers identify technical debt and prioritize refactoring efforts.

## Development Setup

### Prerequisites

- Node.js 18+
- pnpm 8+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/jeremylongshore/claude-code-plugins.git
cd claude-code-plugins/plugins/mcp/project-health-auditor

# Install dependencies
pnpm install

# Run tests
pnpm test

# Build TypeScript
pnpm build
```

## Project Structure

```
project-health-auditor/
├── servers/
│   └── code-metrics.ts        # Main MCP server implementation
├── tests/
│   └── code-metrics.test.ts   # Comprehensive test suite
├── commands/
│   └── analyze.md             # /analyze slash command
├── agents/
│   └── reviewer.md            # Code health reviewer agent
├── examples/
│   ├── sample-repo/           # Example repository for testing
│   └── USAGE.md               # Usage examples
├── .mcp.json                  # MCP server configuration
└── package.json               # Dependencies and scripts
```

## MCP Server Architecture

The server implements 4 tools using the MCP SDK:

1. **list_repo_files** - File discovery with glob patterns
2. **file_metrics** - Complexity, health score, and comment analysis
3. **git_churn** - Change frequency and author analysis
4. **map_tests** - Test coverage mapping

### Adding a New Tool

```typescript
// 1. Define Zod schema for input validation
const NewToolSchema = z.object({
  param: z.string().describe("Parameter description")
});

// 2. Implement tool function
async function newTool(args: z.infer<typeof NewToolSchema>) {
  // Implementation
  return { /* results */ };
}

// 3. Register tool in server
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    // ... existing tools
    {
      name: "new_tool",
      description: "What this tool does",
      inputSchema: zodToJsonSchema(NewToolSchema)
    }
  ]
}));

// 4. Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "new_tool") {
    const args = NewToolSchema.parse(request.params.arguments);
    const result = await newTool(args);
    return {
      content: [{
        type: "text",
        text: JSON.stringify(result, null, 2)
      }]
    };
  }
  // ... handle other tools
});
```

### Testing Guidelines

We maintain **80%+ test coverage**. All PRs must include tests.

```typescript
// Example test structure
describe('New Tool', () => {
  it('should handle valid input', () => {
    // Arrange
    const input = { param: 'value' };

    // Act
    const result = newTool(input);

    // Assert
    expect(result).toBeDefined();
  });

  it('should handle edge cases', () => {
    // Test edge cases
  });

  it('should validate input', () => {
    // Test input validation
  });
});
```

### Health Score Algorithm

The health score (0-100) is calculated from multiple factors:

```typescript
function calculateHealthScore(
  complexity: number,
  functions: number,
  commentRatio: number,
  lines: number
): number {
  let score = 100;

  // Average complexity per function
  const avgComplexity = functions > 0 ? complexity / functions : complexity;
  if (avgComplexity > 10) score -= 30;      // Severe
  else if (avgComplexity > 5) score -= 15;  // Moderate

  // Comment ratio (% of lines that are comments)
  if (commentRatio < 5) score -= 10;        // Poor documentation
  else if (commentRatio > 20) score += 10;  // Well documented

  // File length
  if (lines > 500) score -= 20;             // Too long
  else if (lines > 300) score -= 10;        // Long

  return Math.max(0, Math.min(100, score));
}
```

**When modifying this algorithm:**

- Update the function in `servers/code-metrics.ts`
- Update corresponding tests in `tests/code-metrics.test.ts`
- Update documentation in `README.md` and `agents/reviewer.md`
- Ensure all tests still pass

## Code Style

- **TypeScript**: Strict mode, explicit types
- **Formatting**: Prettier with 2-space indentation
- **Linting**: ESLint with recommended rules
- **Comments**: JSDoc for public functions

```typescript
/**
 * Calculates file complexity metrics
 * @param filePath - Absolute path to file
 * @returns Complexity analysis including cyclomatic complexity and health score
 */
async function fileMetrics(args: z.infer<typeof FileMetricsSchema>) {
  // Implementation
}
```

## Testing Commands

```bash
# Run all tests
pnpm test

# Run tests in watch mode
pnpm test:watch

# Run tests with coverage
pnpm test:coverage

# Type check
pnpm build
```

## Submitting Changes

### Pull Request Process

1. **Fork the repository**
2. **Create a feature branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write code following style guidelines
   - Add/update tests
   - Update documentation

4. **Run tests**

   ```bash
   pnpm test
   pnpm build
   ```

5. **Commit with clear message**

   ```bash
   git commit -m "feat: add support for Python files"
   ```

6. **Push to your fork**

   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open Pull Request**
   - Use the PR template
   - Link related issues
   - Describe changes clearly

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions/changes
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `chore:` - Build/tooling changes

Examples:

```
feat: add Python file support to complexity analysis
fix: correct health score calculation for edge cases
docs: update usage examples with Python
test: add integration tests for git_churn tool
```

## Common Contribution Areas

### 1. Language Support

Add support for new programming languages:

- Update file patterns in `list_repo_files`
- Add language-specific complexity rules in `file_metrics`
- Add comment pattern detection
- Add tests with sample files

### 2. Metrics Improvements

Enhance existing metrics:

- Improve cyclomatic complexity calculation
- Add new health score factors
- Better test coverage detection
- More accurate churn analysis

### 3. Documentation

- Usage examples
- Best practices guides
- Video tutorials
- Integration guides

### 4. Testing

- More edge cases
- Integration tests
- Performance tests
- Error handling scenarios

## Questions?

- **GitHub Discussions**: https://github.com/jeremylongshore/claude-code-plugins/discussions
- **Issues**: https://github.com/jeremylongshore/claude-code-plugins/issues

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
