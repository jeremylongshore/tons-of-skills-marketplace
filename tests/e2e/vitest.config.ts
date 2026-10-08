import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    name: 'e2e',
    globals: true,
    environment: 'node',
    include: ['scenarios/**/*.test.ts'],
    exclude: [
      'node_modules/',
      'dist/',
      'fixtures/',
      '**/*.config.*',
      '**/*.d.ts'
    ],
    testTimeout: 30000, // E2E tests may take longer
    hookTimeout: 10000,
    teardownTimeout: 10000,
    // Run tests sequentially for E2E isolation
    pool: 'forks',
    // Vitest 4 removed poolOptions; one worker runs test files one at a time,
    // each still in its own isolated module graph (isolate defaults to true).
    maxWorkers: 1,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      reportsDirectory: './coverage',
      exclude: [
        'node_modules/',
        'dist/',
        'tests/',
        'fixtures/',
        '**/*.config.*',
        '**/*.d.ts',
        '**/types.ts'
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 75,
        statements: 80
      }
    },
    // Retry flaky tests once
    retry: 1,
    // Show verbose output for debugging
    reporters: process.env.E2E_DEBUG ? ['verbose'] : ['default'],
    // Setup file for global test utilities
    setupFiles: ['./setup.ts']
  },
  resolve: {
    alias: {
      '@fixtures': path.resolve(__dirname, './fixtures'),
      '@scenarios': path.resolve(__dirname, './scenarios'),
      '@': path.resolve(__dirname, '../../')
    }
  }
});
