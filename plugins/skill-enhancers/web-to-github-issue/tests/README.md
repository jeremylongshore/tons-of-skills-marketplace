# Test Suite for web-to-github-issue Plugin

Comprehensive automated test suite with **96.08% statement and line coverage** across all source files.

## Test Statistics

- **Total Tests**: 118 tests
- **Test Files**: 3
- **Code Coverage**: 96.08% statements/lines, 93.2% branches, 100% functions
- **Test Framework**: Vitest 3.2.7
- **Mocking**: Vitest built-in mocking (@octokit/rest)

## Coverage Report

```
File              | % Stmts | % Branch | % Funcs | % Lines |
------------------|---------|----------|---------|---------|
All files         |   96.08 |    93.2  |     100 |   96.08 |
formatter.js      |     100 |     100  |     100 |     100 |
github-client.js  |   90.85 |    79.31 |     100 |   90.85 |
parser.js         |     100 |    98.14 |     100 |     100 |
```

The configured 80% thresholds apply to the suite-wide totals because
`perFile` is not enabled. Individual-file percentages are diagnostic and do
not represent separate gates.

## Running Tests

### Quick Start

```bash
# Run all tests once
pnpm test

# Run tests in watch mode (auto-rerun on changes)
pnpm run test:watch

# Run tests with interactive UI
pnpm run test:ui

# Generate coverage report
pnpm run test:coverage

# Generate coverage report with UI
pnpm run test:coverage:ui
```

### Coverage Output

Coverage reports are generated in the following formats:

- **Terminal**: Text output in console
- **HTML**: `coverage/index.html` (open in browser)
- **JSON**: `coverage/coverage-final.json`
- **LCOV**: `coverage/lcov.info` (for CI integration)

## Test Files Overview

### 1. github-client.test.js (23 tests)

Tests the GitHub API client wrapper that handles authentication and issue creation.

**Test Categories:**

- **Constructor (4 tests)**: Token validation
  - Missing token error
  - Empty string token error
  - Null token error
  - Valid token initialization

- **createIssue (11 tests)**: Issue creation with validation
  - Valid repo format parsing (owner/repo)
  - Invalid repo format errors (no slash, missing owner/repo)
  - API error handling (rate limits, network failures)
  - Authentication errors
  - Permission errors (resource not accessible)
  - Repo not found errors
  - Default labels/assignees handling
  - Special characters in repo names (hyphens, underscores)

- **verifyRepo (8 tests)**: Repository verification
  - Valid repo access
  - Non-existent repo handling
  - Repos without issues enabled
  - Authentication errors
  - Network errors
  - Private repo access denied
  - Repo name parsing (hyphens, underscores)

**Mocking Strategy:**

- Mocks `@octokit/rest` using Vitest's `vi.mock()`
- Simulates API responses and errors
- Verifies correct parameters passed to Octokit methods

**Edge Cases Covered:**

- Invalid repo formats
- Network failures
- API rate limiting
- Authentication issues
- Missing/null/empty parameters

### 2. parser.test.js (46 tests)

Tests the search results parser that extracts insights from web search data.

**Test Categories:**

- **Empty/Invalid Inputs (3 tests)**:
  - Null results
  - Undefined results
  - Empty array

- **Basic Parsing (7 tests)**:
  - Single result parsing
  - Max sources limiting (default 5, custom limits)
  - Missing score handling (defaults to 1.0)
  - Missing title ("Untitled" fallback)
  - Missing snippet handling
  - Description as snippet fallback

- **URL Domain Extraction (4 tests)**:
  - Standard HTTPS URLs
  - HTTP URLs
  - Invalid URL graceful handling ("unknown" domain)
  - Subdomain extraction

- **Key Point Extraction (8 tests)**:
  - Action keyword detection (should, must, recommend, etc.)
  - Key point extraction enable/disable
  - Deduplication of identical points
  - Limiting to 10 key points
  - Short sentence filtering (< 20 chars)
  - Specific keyword detection (recommend, best practice, avoid)

- **Priority Detection (7 tests)**:
  - Urgent priority for security keywords
  - CVE mention detection
  - Deprecated API warnings
  - Normal priority for regular content
  - Priority detection enable/disable
  - Specific urgent keywords (urgent, exploit)

- **Actionability Detection (5 tests)**:
  - "How to" content detection
  - Tutorial content detection
  - Setup guide detection
  - Non-actionable theoretical content
  - Detection disable when priority detection off

- **Topic Extraction (7 tests)**:
  - Topic extraction from content
  - Limiting to 5 topics
  - Stop word filtering
  - Short word filtering (≤ 4 chars)
  - Frequency-based sorting
  - Empty content handling
  - Case-insensitive extraction

- **Complex Scenarios (5 tests)**:
  - Mix of valid and malformed results
  - All options enabled together
  - Unicode character handling
  - Very long snippets
  - Whitespace-only content

**Edge Cases Covered:**

- Null/undefined/empty inputs
- Missing required fields (title, snippet, URL)
- Invalid URLs
- Unicode characters and emojis
- Very long content
- Whitespace-only content
- Special characters

### 3. formatter.test.js (49 tests)

Tests the markdown formatter that creates formatted GitHub issue bodies.

**Test Categories:**

- **Basic Formatting (5 tests)**:
  - Topic in header
  - Generation date display
  - Source count display
  - Plugin attribution
  - Research date at bottom

- **Priority Handling (4 tests)**:
  - Urgent priority display
  - High priority display
  - Normal priority (not displayed)
  - Missing priority handling

- **Key Findings Section (4 tests)**:
  - Display with sources
  - Multiple key points
  - Omit when no points
  - Missing array handling

- **Topics Section (4 tests)**:
  - Code-formatted topics with bullet separator
  - Omit when no topics
  - Missing array handling
  - Bullet separator count validation

- **Sources Section (4 tests)**:
  - Titles and URLs display
  - Multiple sources
  - Sources without snippets
  - Horizontal rule separators

- **Next Steps Section (2 tests)**:
  - Include when actionable
  - Omit when not actionable

- **Markdown Validity (3 tests)**:
  - Valid markdown structure
  - Special character handling
  - URLs with query parameters

- **generateIssueTitle (7 tests)**:
  - "Implement:" prefix for actionable
  - "[URGENT]" prefix for urgent priority
  - Actionable priority over urgent
  - "Research:" prefix for normal
  - Empty topic handling
  - Long topic handling
  - Special characters in topic

- **determineLabels (11 tests)**:
  - priority-high for urgent
  - priority-high for high
  - No priority-high for normal
  - actionable label when actionable
  - No actionable when not actionable
  - Combined labels
  - Duplicate removal
  - Empty base labels
  - Original label preservation
  - Undefined/null priority handling
  - Input array immutability

- **Edge Cases (5 tests)**:
  - Empty insights
  - Very long topics (200+ chars)
  - Special date formats
  - Missing generatedAt

**Edge Cases Covered:**

- Empty/missing data structures
- Very long text (topics, snippets)
- Special characters and markdown escaping
- URL query parameters
- Unicode and emojis
- Missing timestamps
- Array immutability

## Test Configuration

### vitest.config.js

```json
{
  test: {
    globals: true,
    environment: 'node',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      include: ['src/**/*.js'],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80
      }
    }
  }
}
```

## Key Testing Patterns Used

### 1. Mocking External Dependencies

```javascript
vi.mock('@octokit/rest', () => {
  return {
    Octokit: vi.fn().mockImplementation(function () { return ({
      issues: { create: vi.fn() },
      repos: { get: vi.fn() }
    }); })
  };
});
```

### 2. Testing Error Handling

```javascript
it('should handle API errors gracefully', async () => {
  mockOctokit.issues.create.mockRejectedValue(
    new Error('API rate limit exceeded')
  );

  await expect(
    client.createIssue('owner/repo', data)
  ).rejects.toThrow('Failed to create issue: API rate limit exceeded');
});
```

### 3. Testing Edge Cases

```javascript
it('should handle empty array', () => {
  const result = parseSearchResults([]);
  expect(result).toEqual({
    sources: [],
    keyPoints: [],
    detectedPriority: 'normal',
    actionable: false,
    topics: []
  });
});
```

### 4. Testing Array Immutability

```javascript
it('should not mutate input arrays', () => {
  const baseLabels = ['research'];
  const originalLength = baseLabels.length;

  determineLabels(baseLabels, 'urgent', insights);

  expect(baseLabels.length).toBe(originalLength);
});
```

## Edge Cases Discovered

During test development, the following edge cases were identified and handled:

1. **github-client.js**:
   - Invalid repo format variations (/, owner/, /repo, empty string)
   - Null vs undefined vs empty string token validation
   - Repo names with hyphens and underscores
   - Various GitHub API error types

2. **parser.js**:
   - Null, undefined, and empty array inputs
   - Missing object properties (title, snippet, url)
   - Invalid URLs causing domain extraction failures
   - Unicode characters and emojis in content
   - Very long snippets and whitespace-only content
   - "how to" triggering both actionable detection

3. **formatter.js**:
   - Missing or empty data structures
   - Very long topics (200+ characters)
   - Special markdown characters in user content
   - URLs with query parameters
   - Missing timestamps (undefined generatedAt)
   - Array immutability in label determination

## Continuous Integration

To integrate with CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Run tests with coverage
  run: pnpm run test:coverage

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage/lcov.info
```

## Best Practices Applied

1. **Arrange-Act-Assert Pattern**: Clear test structure
2. **Descriptive Test Names**: What is being tested and expected outcome
3. **One Assertion Per Concept**: Tests focus on single behavior
4. **Comprehensive Mocking**: External dependencies properly mocked
5. **Edge Case Coverage**: Null, undefined, empty, invalid inputs
6. **Error Path Testing**: Both success and failure scenarios
7. **Immutability Testing**: Verify no side effects on inputs
8. **Deterministic Tests**: No flakiness, consistent results

## Future Enhancements

Potential areas for additional testing:

1. **Integration Tests**: Test actual GitHub API interaction (with test repo)
2. **Performance Tests**: Benchmark parser with large result sets
3. **Snapshot Tests**: Verify formatter output consistency
4. **End-to-End Tests**: Full workflow from search to issue creation
5. **Security Tests**: Input sanitization, XSS prevention in markdown

## Maintenance

When adding new features:

1. Add tests BEFORE implementing feature (TDD)
2. Maintain the configured 80%+ suite-wide coverage threshold
3. Test both happy path and error cases
4. Update this README with new test categories
5. Run `pnpm run test:coverage` before committing

## Troubleshooting

### Tests Failing

```bash
# Reproduce the locked standalone install
pnpm install --ignore-workspace --frozen-lockfile

# Run tests with verbose output
pnpm test -- --reporter=verbose
```

### Coverage Below Threshold

```bash
# Generate detailed coverage report
pnpm run test:coverage

# Open HTML report
open coverage/index.html

# Check uncovered lines in terminal output
```

---

**Last Verified**: September 2026
**Test Framework**: Vitest 3.2.7
**Coverage**: 96.08% statements/lines, 93.2% branches, 100% functions
**Total Tests**: 118 passing
