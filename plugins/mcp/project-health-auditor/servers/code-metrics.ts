#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { glob } from 'glob';
import { simpleGit } from 'simple-git';
import { promises as fs } from 'fs';
import { z } from 'zod';
import path from 'path';

// Input schemas
const ListRepoFilesSchema = z.object({
  repoPath: z.string(),
  globs: z.array(z.string()).optional().default(['**/*']),
  exclude: z.array(z.string()).optional().default(['node_modules/**', '.git/**', 'dist/**', 'build/**'])
});

const FileMetricsSchema = z.object({
  filePath: z.string()
});

const GitChurnSchema = z.object({
  repoPath: z.string(),
  since: z.string().optional().default('6 months ago')
});

const MapTestsSchema = z.object({
  repoPath: z.string()
});

// Tool implementations
async function listRepoFiles(args: z.infer<typeof ListRepoFilesSchema>) {
  const { repoPath, globs: patterns, exclude } = args;

  const files: string[] = [];

  for (const pattern of patterns) {
    const matches = await glob(pattern, {
      cwd: repoPath,
      ignore: exclude,
      nodir: true,
      absolute: false
    });
    files.push(...matches);
  }

  // Remove duplicates and sort
  const uniqueFiles = [...new Set(files)].sort();

  return {
    repoPath,
    totalFiles: uniqueFiles.length,
    files: uniqueFiles,
    patterns,
    excluded: exclude
  };
}

async function fileMetrics(args: z.infer<typeof FileMetricsSchema>) {
  const { filePath } = args;

  try {
    // Stat and read via a single open file handle instead of two separate
    // path-based calls (fs.stat then fs.readFile): two path lookups leave a
    // TOCTOU window where the path can be deleted, replaced, or swapped for
    // a symlink between calls. A shared handle stats and reads the same
    // inode.
    const handle = await fs.open(filePath, 'r');
    let stats;
    let content: string;
    try {
      stats = await handle.stat();
      content = await handle.readFile('utf-8');
    } finally {
      await handle.close();
    }

    // Basic metrics
    const lines = content.split('\n').length;
    const size = stats.size;
    const ext = path.extname(filePath);

    // Simple complexity estimation based on control flow keywords
    const complexityKeywords = /\b(if|else|for|while|switch|case|catch|&&|\|\||\?)\b/g;
    const matches = content.match(complexityKeywords);
    const cyclomaticComplexity = matches ? matches.length + 1 : 1;

    // Count functions/methods (approximation)
    const functionPatterns = /\b(function|const\s+\w+\s*=\s*\(|class\s+\w+|def\s+\w+)/g;
    const functions = content.match(functionPatterns);
    const functionCount = functions ? functions.length : 0;

    // Comment ratio
    const commentLines = content.split('\n').filter(line => {
      const trimmed = line.trim();
      return trimmed.startsWith('//') || trimmed.startsWith('#') || trimmed.startsWith('/*');
    }).length;
    const commentRatio = lines > 0 ? (commentLines / lines) * 100 : 0;

    return {
      file: filePath,
      size,
      lines,
      extension: ext,
      complexity: {
        cyclomatic: cyclomaticComplexity,
        functions: functionCount,
        averagePerFunction: functionCount > 0 ? Math.round(cyclomaticComplexity / functionCount) : 0
      },
      comments: {
        lines: commentLines,
        ratio: Math.round(commentRatio * 100) / 100
      },
      healthScore: calculateHealthScore(cyclomaticComplexity, functionCount, commentRatio, lines)
    };
  } catch (error) {
    throw new Error(`Failed to analyze file: ${error instanceof Error ? error.message : String(error)}`);
  }
}

function calculateHealthScore(complexity: number, functions: number, commentRatio: number, lines: number): number {
  // Health score algorithm (0-100)
  let score = 100;

  // Penalize high complexity
  const avgComplexity = functions > 0 ? complexity / functions : complexity;
  if (avgComplexity > 10) score -= 30;
  else if (avgComplexity > 5) score -= 15;

  // Reward comments
  if (commentRatio < 5) score -= 10;
  else if (commentRatio > 20) score += 10;

  // Penalize very long files
  if (lines > 500) score -= 20;
  else if (lines > 300) score -= 10;

  return Math.max(0, Math.min(100, score));
}

async function gitChurn(args: z.infer<typeof GitChurnSchema>) {
  const { repoPath, since } = args;

  try {
    const git = simpleGit(repoPath);

    // Get commit history
    const log = await git.log({
      '--since': since,
      '--name-only': null,
      '--pretty': 'format:%H|%an|%ae|%ad'
    });

    // Count file changes
    const fileChurn: Record<string, { commits: number; authors: Set<string> }> = {};

    for (const commit of log.all) {
      const commitDetails = await git.show([
        commit.hash,
        '--name-only',
        '--pretty=format:'
      ]);

      const files = commitDetails.split('\n').filter(f => f.trim());

      for (const file of files) {
        if (!fileChurn[file]) {
          fileChurn[file] = { commits: 0, authors: new Set() };
        }
        fileChurn[file].commits++;
        fileChurn[file].authors.add(commit.author_name);
      }
    }

    // Convert to array and sort by churn
    const churnData = Object.entries(fileChurn)
      .map(([file, data]) => ({
        file,
        commits: data.commits,
        authors: Array.from(data.authors),
        authorCount: data.authors.size
      }))
      .sort((a, b) => b.commits - a.commits);

    return {
      repoPath,
      since,
      totalCommits: log.total,
      filesChanged: churnData.length,
      topChurnFiles: churnData.slice(0, 20),
      summary: {
        highChurn: churnData.filter(f => f.commits > 10).length,
        mediumChurn: churnData.filter(f => f.commits > 5 && f.commits <= 10).length,
        lowChurn: churnData.filter(f => f.commits <= 5).length
      }
    };
  } catch (error) {
    throw new Error(`Failed to analyze git churn: ${error instanceof Error ? error.message : String(error)}`);
  }
}

async function mapTests(args: z.infer<typeof MapTestsSchema>) {
  const { repoPath } = args;

  try {
    // Find test files
    const testFiles = await glob('**/*.{test,spec}.{ts,js,tsx,jsx,py}', {
      cwd: repoPath,
      ignore: ['node_modules/**', '.git/**', 'dist/**'],
      nodir: true
    });

    // Find source files
    const sourceFiles = await glob('**/*.{ts,js,tsx,jsx,py}', {
      cwd: repoPath,
      ignore: [
        'node_modules/**',
        '.git/**',
        'dist/**',
        'build/**',
        '**/*.test.*',
        '**/*.spec.*',
        '**/__tests__/**'
      ],
      nodir: true
    });

    // Map tests to source files
    const testCoverage: Record<string, string[]> = {};
    const missingTests: string[] = [];

    for (const sourceFile of sourceFiles) {
      const baseName = path.basename(sourceFile, path.extname(sourceFile));
      const sourceDir = path.dirname(sourceFile);

      // Look for corresponding test files
      const matchingTests = testFiles.filter(testFile => {
        const testBaseName = path.basename(testFile, path.extname(testFile));
        return testBaseName.includes(baseName) || baseName.includes(testBaseName.replace('.test', '').replace('.spec', ''));
      });

      if (matchingTests.length > 0) {
        testCoverage[sourceFile] = matchingTests;
      } else {
        missingTests.push(sourceFile);
      }
    }

    const coverageRatio = sourceFiles.length > 0
      ? ((sourceFiles.length - missingTests.length) / sourceFiles.length) * 100
      : 0;

    return {
      repoPath,
      summary: {
        totalSourceFiles: sourceFiles.length,
        totalTestFiles: testFiles.length,
        testedFiles: sourceFiles.length - missingTests.length,
        coverageRatio: Math.round(coverageRatio * 100) / 100
      },
      coverage: testCoverage,
      missingTests: missingTests.slice(0, 50), // Limit to 50 for readability
      recommendations: generateTestRecommendations(missingTests, coverageRatio)
    };
  } catch (error) {
    throw new Error(`Failed to map tests: ${error instanceof Error ? error.message : String(error)}`);
  }
}

function generateTestRecommendations(missingTests: string[], coverageRatio: number): string[] {
  const recommendations: string[] = [];

  if (coverageRatio < 50) {
    recommendations.push(' CRITICAL: Test coverage is below 50%. Prioritize adding tests for core functionality.');
  } else if (coverageRatio < 80) {
    recommendations.push('️  Test coverage is below 80%. Consider adding tests for remaining files.');
  } else {
    recommendations.push(' Good test coverage! Maintain this level.');
  }

  if (missingTests.length > 0) {
    const highPriorityFiles = missingTests.filter(f =>
      f.includes('/services/') || f.includes('/api/') || f.includes('/utils/')
    );

    if (highPriorityFiles.length > 0) {
      recommendations.push(` High priority: Add tests for ${highPriorityFiles.length} files in critical directories (services, api, utils)`);
    }
  }

  return recommendations;
}

// Create and start the server
const server = new Server(
  {
    name: 'code-metrics',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Register tool list handler
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'list_repo_files',
        description: 'List all files in a repository matching glob patterns',
        inputSchema: {
          type: 'object',
          properties: {
            repoPath: {
              type: 'string',
              description: 'Absolute path to the repository'
            },
            globs: {
              type: 'array',
              items: { type: 'string' },
              description: 'Glob patterns to match (default: ["**/*"])',
              default: ['**/*']
            },
            exclude: {
              type: 'array',
              items: { type: 'string' },
              description: 'Glob patterns to exclude',
              default: ['node_modules/**', '.git/**', 'dist/**', 'build/**']
            }
          },
          required: ['repoPath']
        }
      },
      {
        name: 'file_metrics',
        description: 'Analyze a single file for complexity, size, and health metrics',
        inputSchema: {
          type: 'object',
          properties: {
            filePath: {
              type: 'string',
              description: 'Absolute path to the file to analyze'
            }
          },
          required: ['filePath']
        }
      },
      {
        name: 'git_churn',
        description: 'Analyze git commit history to identify high-churn files (files that change frequently)',
        inputSchema: {
          type: 'object',
          properties: {
            repoPath: {
              type: 'string',
              description: 'Absolute path to the git repository'
            },
            since: {
              type: 'string',
              description: 'Time period to analyze (e.g., "6 months ago", "1 year ago")',
              default: '6 months ago'
            }
          },
          required: ['repoPath']
        }
      },
      {
        name: 'map_tests',
        description: 'Map source files to test files and identify files missing tests',
        inputSchema: {
          type: 'object',
          properties: {
            repoPath: {
              type: 'string',
              description: 'Absolute path to the repository'
            }
          },
          required: ['repoPath']
        }
      }
    ]
  };
});

// Register tool call handler
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    switch (request.params.name) {
      case 'list_repo_files': {
        const args = ListRepoFilesSchema.parse(request.params.arguments);
        const result = await listRepoFiles(args);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2)
            }
          ]
        };
      }

      case 'file_metrics': {
        const args = FileMetricsSchema.parse(request.params.arguments);
        const result = await fileMetrics(args);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2)
            }
          ]
        };
      }

      case 'git_churn': {
        const args = GitChurnSchema.parse(request.params.arguments);
        const result = await gitChurn(args);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2)
            }
          ]
        };
      }

      case 'map_tests': {
        const args = MapTestsSchema.parse(request.params.arguments);
        const result = await mapTests(args);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2)
            }
          ]
        };
      }

      default:
        throw new Error(`Unknown tool: ${request.params.name}`);
    }
  } catch (error) {
    if (error instanceof z.ZodError) {
      throw new Error(`Invalid arguments: ${error.issues.map((e: any) => `${e.path.join('.')}: ${e.message}`).join(', ')}`);
    }
    throw error;
  }
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Code Metrics MCP Server running on stdio');
}

main().catch((error) => {
  console.error('Fatal error in main():', error);
  process.exit(1);
});
