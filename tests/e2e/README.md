# E2E Test Suite for Claude Code Plugins

Comprehensive end-to-end testing for real-world plugin installation, activation, and usage scenarios.

## Overview

This test suite validates the complete plugin lifecycle from installation to execution, including:

- Plugin installation and marketplace operations
- Skill activation and trigger phrase detection
- MCP server communication and tool invocation
- Cross-plugin interactions and dependency resolution
- Error handling and recovery scenarios

## Test Architecture

### Test Pyramid Strategy

```
    /\
   /  \    E2E Tests (Comprehensive Workflows)
  /    \
 /------\  Integration Tests (Component Interactions)
/        \
|--------|  Unit Tests (Individual Functions)
```

**Our focus:** E2E tests that validate real-world user scenarios

### Test Organization

```
tests/e2e/
├── README.md                  # This file
├── vitest.config.ts           # Vitest configuration
├── setup.ts                   # Global test setup and utilities
├── scenarios/                 # Test scenarios by functionality
│   ├── plugin-install.test.ts       # Installation lifecycle
│   ├── skill-activation.test.ts     # Skill triggers and context
│   └── mcp-communication.test.ts    # MCP server interactions
└── fixtures/                  # Test data and mock plugins
    └── test-plugin/           # Minimal test plugin
```

## Running Tests

### All E2E Tests
```bash
pnpm --dir tests/e2e test
```

### Specific Test Suite
```bash
pnpm --dir tests/e2e exec vitest run scenarios/plugin-install.test.ts
```

### Watch Mode (Development)
```bash
pnpm --dir tests/e2e run test:watch
```

### Coverage Report
```bash
pnpm --dir tests/e2e run test:coverage
```

### Validate the Marketplace Skill Fixture

```bash
python3 scripts/validate-skills-schema.py --marketplace \
  tests/e2e/fixtures/test-plugin/skills/test-skill/SKILL.md
```

## Test Scenarios

### 1. Plugin Installation (`plugin-install.test.ts`)

Tests the complete plugin installation lifecycle:

- **Marketplace Discovery:** Catalog parsing and plugin lookup
- **Installation:** File copying and validation
- **Plugin Loading:** Manifest parsing and metadata extraction
- **Uninstallation:** Complete cleanup of plugin files
- **Error Handling:** Invalid plugins, missing dependencies, corrupt manifests

**Key Test Cases:**
```typescript
describe('Plugin Installation', () => {
  it('should install plugin from catalog')
  it('should validate plugin.json schema')
  it('should copy all plugin files correctly')
  it('should handle duplicate installations')
  it('should uninstall plugin completely')
  it('should reject invalid plugin manifests')
})
```

### 2. Skill Activation (`skill-activation.test.ts`)

Tests skill discovery and activation mechanisms:

- **Trigger Detection:** Phrase matching and context awareness
- **Tool Permissions:** `allowed-tools` validation
- **Skill Loading:** SKILL.md parsing and instruction extraction
- **Multi-Skill Scenarios:** Multiple skills from same/different plugins
- **Priority Handling:** Skill selection when multiple match

**Key Test Cases:**
```typescript
describe('Skill Activation', () => {
  it('should detect trigger phrases in user input')
  it('should validate allowed-tools permissions')
  it('should load skill instructions from SKILL.md')
  it('should handle multiple active skills')
  it('should respect tool restrictions')
})
```

### 3. MCP Server Communication (`mcp-communication.test.ts`)

Tests MCP server lifecycle and tool invocation:

- **Server Startup:** Process spawning and initialization
- **Tool Registration:** Server tool discovery and schema validation
- **Tool Invocation:** Parameter passing and response handling
- **Error Recovery:** Server crashes, timeouts, invalid responses
- **Server Shutdown:** Graceful cleanup and resource release

**Key Test Cases:**
```typescript
describe('MCP Server Communication', () => {
  it('should start MCP server successfully')
  it('should register server tools')
  it('should invoke tools with parameters')
  it('should handle server errors gracefully')
  it('should shutdown server cleanly')
})
```

## Test Fixtures

### Test Plugin Structure

The `fixtures/test-plugin/` directory contains a minimal but complete plugin for testing:

```
test-plugin/
├── .claude-plugin/
│   └── plugin.json           # Valid manifest with all required fields
├── README.md                 # Basic documentation
├── skills/
│   └── test-skill/
│       └── SKILL.md          # Current marketplace skill with triggers
└── commands/
    └── test-command.md       # Simple slash command
```

**Plugin Manifest (`plugin.json`):**
```json
{
  "name": "test-plugin",
  "version": "1.0.0",
  "description": "Minimal test plugin for E2E validation",
  "author": {
    "name": "Test Author",
    "email": "test@example.com"
  },
  "license": "MIT"
}
```

**Skill Definition (`SKILL.md`):**
```yaml
---
name: test-skill
description: |
  Test skill for E2E validation. Use when testing skill activation and tool
  permissions. Trigger with "run test skill" or "execute test".
allowed-tools: Read, Write, Bash(pnpm:*)
version: 1.0.0
license: MIT
author: Test Author <test@example.com>
compatibility: Works with model-agnostic agents that support Agent Skills frontmatter.
tags: [testing, e2e]
---
```

## Test Utilities

### Setup Functions (`setup.ts`)

Common utilities for all E2E tests:

```typescript
// Create isolated test environment
export function createTestEnv(): TestEnvironment

// Install plugin in test environment
export function installPlugin(env: TestEnvironment, pluginPath: string): Promise<void>

// Simulate skill activation
export function activateSkill(env: TestEnvironment, triggerPhrase: string): Promise<Skill>

// Start MCP server for testing
export function startMcpServer(serverPath: string): Promise<McpServer>

// Clean up test environment
export function cleanupTestEnv(env: TestEnvironment): Promise<void>
```

## Test Environment

### Isolation Strategy

Each test runs in an isolated environment:

- **Temporary Directory:** `/tmp/claude-e2e-test-{uuid}`
- **Isolated Marketplace:** Local catalog copy
- **No Global State:** Tests don't interfere with each other
- **Automatic Cleanup:** Temp directories removed after tests

### Environment Variables

Tests use environment variables for configuration:

```bash
# Test timeout (default: 30s)
E2E_TEST_TIMEOUT=30000

# Verbose logging
E2E_DEBUG=true

# Keep test artifacts for debugging
E2E_KEEP_ARTIFACTS=true
```

## Best Practices

### Test Structure (Arrange-Act-Assert)

```typescript
it('should install plugin successfully', async () => {
  // Arrange: Set up test environment
  const env = await createTestEnv();
  const pluginPath = path.join(__dirname, 'fixtures/test-plugin');

  // Act: Perform the operation
  await installPlugin(env, pluginPath);

  // Assert: Verify expectations
  expect(env.hasPlugin('test-plugin')).toBe(true);
  expect(env.getPluginManifest('test-plugin')).toMatchObject({
    name: 'test-plugin',
    version: '1.0.0'
  });

  // Cleanup
  await cleanupTestEnv(env);
});
```

### Error Testing

Always test both success and failure paths:

```typescript
describe('Error Handling', () => {
  it('should succeed with valid plugin', async () => {
    // Test happy path
  });

  it('should fail with invalid manifest', async () => {
    // Test error path
    await expect(installPlugin(env, invalidPath))
      .rejects
      .toThrow('Invalid plugin manifest');
  });
});
```

### Deterministic Tests

Tests must be:
- **Idempotent:** Same result every time
- **Independent:** No test dependencies
- **Fast:** Complete in < 5 seconds each
- **Isolated:** No shared state between tests

## Coverage Goals

- **Line Coverage:** 80%+
- **Function Coverage:** 80%+
- **Branch Coverage:** 75%+
- **Statement Coverage:** 80%+

## Debugging

### Running Single Test

```bash
pnpm --dir tests/e2e exec vitest run scenarios/plugin-install.test.ts -t "should install plugin"
```

### Verbose Output

```bash
E2E_DEBUG=true pnpm --dir tests/e2e test
```

### Keep Test Artifacts

```bash
E2E_KEEP_ARTIFACTS=true pnpm --dir tests/e2e test
# Check /tmp/claude-e2e-test-* directories
```

### Inspect Test Environment

```typescript
it('should debug environment', async () => {
  const env = await createTestEnv();
  console.log('Test env:', env.basePath);
  console.log('Plugins:', env.listPlugins());

  // Add breakpoint or delay for inspection
  await new Promise(resolve => setTimeout(resolve, 60000));

  await cleanupTestEnv(env);
});
```

## CI/CD Integration

Tests run automatically in `.github/workflows/standalone-e2e.yml`:

```yaml
name: Standalone E2E Harness
on: [push, pull_request]
jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v6
        with:
          node-version: 22
      - run: pnpm install --ignore-workspace --frozen-lockfile --ignore-scripts
        working-directory: tests/e2e
      - run: pnpm test
        working-directory: tests/e2e
```

## Contributing

When adding new E2E tests:

1. **Choose the right scenario file:**
   - Plugin lifecycle → `plugin-install.test.ts`
   - Skill behavior → `skill-activation.test.ts`
   - MCP operations → `mcp-communication.test.ts`
   - Cross-cutting → Create new scenario file

2. **Follow naming conventions:**
   - Test files: `*.test.ts`
   - Test suites: `describe('Feature', () => {})`
   - Test cases: `it('should behave as expected', async () => {})`

3. **Maintain test isolation:**
   - Use `createTestEnv()` for each test
   - Clean up with `cleanupTestEnv()`
   - No global state modifications

4. **Document complex tests:**
   - Add comments for non-obvious logic
   - Explain test data choices
   - Link to related issues/docs

## Performance Benchmarks

Target execution times:

- **Single test:** < 5 seconds
- **Full suite:** < 60 seconds
- **With coverage:** < 90 seconds

## Known Limitations

1. **No Claude API testing:** Tests don't invoke actual Claude API
2. **Mocked MCP servers:** Real MCP server tests are limited
3. **File system dependent:** Tests assume POSIX-like filesystem
4. **Network isolation:** No external network calls in tests

## Future Improvements

- [ ] Add visual regression testing for CLI output
- [ ] Test concurrent plugin operations
- [ ] Add performance benchmarking tests
- [ ] Test plugin marketplace synchronization
- [ ] Add chaos engineering scenarios (random failures)
- [ ] Test plugin version migrations
- [ ] Add memory leak detection
- [ ] Test large plugin catalogs (1000+ plugins)

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [Testing Best Practices](https://github.com/goldbergyoni/javascript-testing-best-practices)
- [E2E Testing Patterns](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Claude Code Plugin Specification](../../CLAUDE.md)

## Support

For issues or questions:
- File an issue: https://github.com/jeremylongshore/claude-code-plugins/issues
- Email: jeremy@intentsolutions.io
