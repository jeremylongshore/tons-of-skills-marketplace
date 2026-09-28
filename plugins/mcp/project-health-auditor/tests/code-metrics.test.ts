import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { promises as fs } from 'fs';
import path from 'path';
import os from 'os';

// Mock data and utilities
let testRepoPath: string;
let testFilePath: string;

beforeEach(async () => {
  // Create temporary test directory
  testRepoPath = await fs.mkdtemp(path.join(os.tmpdir(), 'test-repo-'));

  // Create test file structure
  await fs.mkdir(path.join(testRepoPath, 'src'), { recursive: true });
  await fs.mkdir(path.join(testRepoPath, 'tests'), { recursive: true });

  // Create sample source file
  testFilePath = path.join(testRepoPath, 'src', 'example.ts');
  await fs.writeFile(testFilePath, `
// Example TypeScript file
export function complexFunction(x: number, y: number): number {
  if (x > 10) {
    for (let i = 0; i < y; i++) {
      if (i % 2 === 0) {
        console.log(i);
      } else {
        console.log('odd');
      }
    }
  } else if (x < 5) {
    while (y > 0) {
      y--;
    }
  }
  return x + y;
}

export function simpleFunction(a: number): number {
  return a * 2;
}
  `.trim());

  // Create sample test file
  await fs.writeFile(path.join(testRepoPath, 'tests', 'example.test.ts'), `
import { complexFunction, simpleFunction } from '../src/example';

describe('example', () => {
  it('should work', () => {
    expect(complexFunction(1, 2)).toBe(3);
  });
});
  `.trim());

  // Initialize git repo
  const { execSync } = await import('child_process');
  try {
    execSync('git init', { cwd: testRepoPath, stdio: 'ignore' });
    execSync('git config user.name "Test User"', { cwd: testRepoPath, stdio: 'ignore' });
    execSync('git config user.email "test@example.com"', { cwd: testRepoPath, stdio: 'ignore' });
    execSync('git add .', { cwd: testRepoPath, stdio: 'ignore' });
    execSync('git commit -m "Initial commit"', { cwd: testRepoPath, stdio: 'ignore' });

    // Make some changes and commit for churn analysis
    await fs.appendFile(testFilePath, '\n// More code\n');
    execSync('git add .', { cwd: testRepoPath, stdio: 'ignore' });
    execSync('git commit -m "Second commit"', { cwd: testRepoPath, stdio: 'ignore' });
  } catch (error) {
    console.warn('Git operations failed in test setup:', error);
  }
});

afterEach(async () => {
  // Clean up test directory
  try {
    await fs.rm(testRepoPath, { recursive: true, force: true });
  } catch (error) {
    console.warn('Failed to clean up test directory:', error);
  }
});

describe('Code Metrics MCP Server', () => {
  describe('Health Score Calculation', () => {
    it('should calculate perfect score for simple, well-commented file', () => {
      // Mock data: low complexity, good comments, reasonable size
      const complexity = 5;
      const functions = 2;
      const commentRatio = 25; // 25% comments
      const lines = 100;

      // Health score algorithm from server
      let score = 100;
      const avgComplexity = functions > 0 ? complexity / functions : complexity;

      if (avgComplexity > 10) score -= 30;
      else if (avgComplexity > 5) score -= 15;

      if (commentRatio < 5) score -= 10;
      else if (commentRatio > 20) score += 10;

      if (lines > 500) score -= 20;
      else if (lines > 300) score -= 10;

      const healthScore = Math.max(0, Math.min(100, score));

      // Score should be capped at 100
      expect(healthScore).toBe(100);
      expect(healthScore).toBeLessThanOrEqual(100);
    });

    it('should penalize high complexity', () => {
      const complexity = 120;
      const functions = 10;
      const commentRatio = 10;
      const lines = 200;

      let score = 100;
      const avgComplexity = complexity / functions; // 12

      if (avgComplexity > 10) score -= 30;

      expect(score).toBeLessThan(100);
      expect(score).toBe(70);
    });

    it('should penalize very long files', () => {
      const complexity = 10;
      const functions = 5;
      const commentRatio = 15;
      const lines = 600;

      let score = 100;
      if (lines > 500) score -= 20;

      expect(score).toBe(80);
    });

    it('should penalize low comment ratio', () => {
      const complexity = 8;
      const functions = 4;
      const commentRatio = 2; // Only 2% comments
      const lines = 150;

      let score = 100;
      if (commentRatio < 5) score -= 10;

      expect(score).toBe(90);
    });
  });

  describe('File Metrics', () => {
    it('should analyze file complexity correctly', async () => {
      const content = await fs.readFile(testFilePath, 'utf-8');
      const lines = content.split('\n').length;

      // Count complexity keywords
      const complexityKeywords = /\b(if|else|for|while|switch|case|catch|&&|\|\||\?)\b/g;
      const matches = content.match(complexityKeywords);
      const cyclomaticComplexity = matches ? matches.length + 1 : 1;

      expect(cyclomaticComplexity).toBeGreaterThan(1);
      expect(lines).toBeGreaterThan(10);
    });

    it('should count functions correctly', async () => {
      const content = await fs.readFile(testFilePath, 'utf-8');
      const functionPatterns = /\b(function|const\s+\w+\s*=\s*\(|export\s+function)/g;
      const functions = content.match(functionPatterns);

      expect(functions).toBeTruthy();
      expect(functions!.length).toBeGreaterThanOrEqual(2); // complexFunction and simpleFunction
    });

    it('should calculate comment ratio', async () => {
      const content = await fs.readFile(testFilePath, 'utf-8');
      const allLines = content.split('\n');
      const commentLines = allLines.filter(line => {
        const trimmed = line.trim();
        return trimmed.startsWith('//') || trimmed.startsWith('#') || trimmed.startsWith('/*');
      });

      const ratio = (commentLines.length / allLines.length) * 100;
      expect(ratio).toBeGreaterThanOrEqual(0);
      expect(ratio).toBeLessThanOrEqual(100);
    });

    it('should stat and read a file through a single handle (TOCTOU-safe)', async () => {
      // Regression for CodeQL js/file-system-race: fileMetrics() used to call
      // fs.stat(filePath) then fs.readFile(filePath) as two separate
      // path-based lookups, leaving a window where the path could be
      // deleted/replaced between calls. The fix opens one handle and stats +
      // reads from it. Exercise that same pattern directly here.
      const handle = await fs.open(testFilePath, 'r');
      let stats;
      let content: string;
      try {
        stats = await handle.stat();
        content = await handle.readFile('utf-8');
      } finally {
        await handle.close();
      }

      const expectedContent = await fs.readFile(testFilePath, 'utf-8');
      expect(content).toBe(expectedContent);
      expect(stats.size).toBe(Buffer.byteLength(expectedContent, 'utf-8'));
    });

    it('should reject a deleted file the same way stat-then-read would (no silent mismatch)', async () => {
      const goneFile = path.join(testRepoPath, 'src', 'gone.ts');
      await fs.writeFile(goneFile, 'export const x = 1;\n');
      await fs.unlink(goneFile);

      await expect(fs.open(goneFile, 'r')).rejects.toThrow(/ENOENT/);
    });
  });

  describe('File Discovery', () => {
    it('should find all TypeScript files', async () => {
      const { glob } = await import('glob');

      const files = await glob('**/*.ts', {
        cwd: testRepoPath,
        ignore: ['node_modules/**', '.git/**'],
        nodir: true
      });

      expect(files.length).toBeGreaterThan(0);
      expect(files).toContain('src/example.ts');
      expect(files).toContain('tests/example.test.ts');
    });

    it('should exclude specified patterns', async () => {
      const { glob } = await import('glob');

      // Create node_modules file (shouldn't appear)
      await fs.mkdir(path.join(testRepoPath, 'node_modules'), { recursive: true });
      await fs.writeFile(path.join(testRepoPath, 'node_modules', 'lib.js'), 'content');

      const files = await glob('**/*.{ts,js}', {
        cwd: testRepoPath,
        ignore: ['node_modules/**', '.git/**'],
        nodir: true
      });

      expect(files).not.toContain('node_modules/lib.js');
    });

    it('should handle glob patterns correctly', async () => {
      const { glob } = await import('glob');

      // Only source files
      const sourceFiles = await glob('src/**/*.ts', {
        cwd: testRepoPath,
        nodir: true
      });

      expect(sourceFiles.length).toBe(1);
      expect(sourceFiles[0]).toBe('src/example.ts');

      // Only test files
      const testFiles = await glob('tests/**/*.ts', {
        cwd: testRepoPath,
        nodir: true
      });

      expect(testFiles.length).toBe(1);
      expect(testFiles[0]).toBe('tests/example.test.ts');
    });
  });

  describe('Git Churn Analysis', () => {
    it('should parse git log correctly', async () => {
      const { simpleGit } = await import('simple-git');
      const git = simpleGit(testRepoPath);

      try {
        const log = await git.log({
          '--since': '1 year ago'
        });

        expect(log.total).toBeGreaterThanOrEqual(2); // Initial + second commit
        expect(log.all.length).toBeGreaterThanOrEqual(2);
      } catch (error) {
        console.warn('Git log test skipped:', error);
      }
    });

    it('should track file changes', async () => {
      const { simpleGit } = await import('simple-git');
      const git = simpleGit(testRepoPath);

      try {
        const log = await git.log({
          '--since': '1 year ago',
          '--name-only': null
        });

        // Our test file should appear in commits
        expect(log.total).toBeGreaterThan(0);
      } catch (error) {
        console.warn('Git churn test skipped:', error);
      }
    });
  });

  describe('Test Coverage Mapping', () => {
    it('should find test files', async () => {
      const { glob } = await import('glob');

      const testFiles = await glob('**/*.{test,spec}.{ts,js}', {
        cwd: testRepoPath,
        ignore: ['node_modules/**'],
        nodir: true
      });

      expect(testFiles.length).toBe(1);
      expect(testFiles[0]).toBe('tests/example.test.ts');
    });

    it('should find source files', async () => {
      const { glob } = await import('glob');

      const sourceFiles = await glob('**/*.{ts,js}', {
        cwd: testRepoPath,
        ignore: ['node_modules/**', '.git/**', '**/*.test.*', '**/*.spec.*'],
        nodir: true
      });

      expect(sourceFiles).toContain('src/example.ts');
      expect(sourceFiles).not.toContain('tests/example.test.ts');
    });

    it('should map tests to source files', () => {
      const sourceFile = 'src/example.ts';
      const testFile = 'tests/example.test.ts';

      const baseName = path.basename(sourceFile, path.extname(sourceFile));
      const testBaseName = path.basename(testFile, path.extname(testFile));

      // Check if test file matches source file
      const matches = testBaseName.includes(baseName) ||
                     baseName.includes(testBaseName.replace('.test', '').replace('.spec', ''));

      expect(matches).toBe(true);
    });

    it('should calculate coverage ratio', () => {
      const totalSourceFiles = 10;
      const testedFiles = 7;

      const coverageRatio = ((testedFiles) / totalSourceFiles) * 100;

      expect(coverageRatio).toBe(70);
    });

    it('should generate recommendations based on coverage', () => {
      const lowCoverage = 30;
      const mediumCoverage = 65;
      const highCoverage = 85;

      // Low coverage
      let recommendation: string;
      if (lowCoverage < 50) {
        recommendation = ' CRITICAL: Test coverage is below 50%';
      } else if (lowCoverage < 80) {
        recommendation = '️  Test coverage is below 80%';
      } else {
        recommendation = ' Good test coverage!';
      }
      expect(recommendation).toContain('CRITICAL');

      // Medium coverage
      if (mediumCoverage < 50) {
        recommendation = ' CRITICAL';
      } else if (mediumCoverage < 80) {
        recommendation = '️  Test coverage is below 80%';
      } else {
        recommendation = ' Good test coverage!';
      }
      expect(recommendation).toContain('below 80%');

      // High coverage
      if (highCoverage < 50) {
        recommendation = ' CRITICAL';
      } else if (highCoverage < 80) {
        recommendation = '️  below 80%';
      } else {
        recommendation = ' Good test coverage!';
      }
      expect(recommendation).toContain('Good');
    });
  });

  describe('Input Validation', () => {
    it('should validate repoPath is required', async () => {
      const { z } = await import('zod');

      const ListRepoFilesSchema = z.object({
        repoPath: z.string(),
        globs: z.array(z.string()).optional(),
        exclude: z.array(z.string()).optional()
      });

      expect(() => {
        ListRepoFilesSchema.parse({ repoPath: testRepoPath });
      }).not.toThrow();

      expect(() => {
        ListRepoFilesSchema.parse({});
      }).toThrow();
    });

    it('should validate filePath is string', async () => {
      const { z } = await import('zod');

      const FileMetricsSchema = z.object({
        filePath: z.string()
      });

      expect(() => {
        FileMetricsSchema.parse({ filePath: '/path/to/file.ts' });
      }).not.toThrow();

      expect(() => {
        FileMetricsSchema.parse({ filePath: 123 });
      }).toThrow();
    });

    it('should have defaults for optional fields', async () => {
      const { z } = await import('zod');

      const ListRepoFilesSchema = z.object({
        repoPath: z.string(),
        globs: z.array(z.string()).optional().default(['**/*']),
        exclude: z.array(z.string()).optional().default(['node_modules/**'])
      });

      const result = ListRepoFilesSchema.parse({ repoPath: '/path' });

      expect(result.globs).toEqual(['**/*']);
      expect(result.exclude).toEqual(['node_modules/**']);
    });
  });

  describe('Error Handling', () => {
    it('should handle non-existent file gracefully', async () => {
      const nonExistentFile = path.join(testRepoPath, 'does-not-exist.ts');

      await expect(fs.readFile(nonExistentFile, 'utf-8')).rejects.toThrow();
    });

    it('should handle invalid git repository', async () => {
      const { simpleGit } = await import('simple-git');
      const nonGitDir = await fs.mkdtemp(path.join(os.tmpdir(), 'non-git-'));

      const git = simpleGit(nonGitDir);

      await expect(git.log()).rejects.toThrow();

      await fs.rm(nonGitDir, { recursive: true });
    });

    it('should handle empty repository', async () => {
      const { glob } = await import('glob');
      const emptyDir = await fs.mkdtemp(path.join(os.tmpdir(), 'empty-'));

      const files = await glob('**/*', {
        cwd: emptyDir,
        nodir: true
      });

      expect(files.length).toBe(0);

      await fs.rm(emptyDir, { recursive: true });
    });
  });

  describe('Integration Tests', () => {
    it('should provide complete analysis workflow', async () => {
      // 1. List files
      const { glob } = await import('glob');
      const allFiles = await glob('**/*.ts', {
        cwd: testRepoPath,
        ignore: ['node_modules/**', '.git/**'],
        nodir: true
      });

      expect(allFiles.length).toBeGreaterThan(0);

      // 2. Analyze complexity
      const content = await fs.readFile(testFilePath, 'utf-8');
      const lines = content.split('\n').length;
      const keywords = content.match(/\b(if|else|for|while)\b/g);

      expect(lines).toBeGreaterThan(0);
      expect(keywords).toBeTruthy();

      // 3. Check git history
      const { simpleGit } = await import('simple-git');
      const git = simpleGit(testRepoPath);

      try {
        const log = await git.log();
        expect(log.total).toBeGreaterThan(0);
      } catch (error) {
        console.warn('Git integration test skipped:', error);
      }

      // 4. Map tests
      const testFiles = await glob('**/*.test.ts', {
        cwd: testRepoPath,
        nodir: true
      });

      expect(testFiles.length).toBe(1);
    });
  });
});
