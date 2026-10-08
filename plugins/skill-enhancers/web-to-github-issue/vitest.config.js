import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      include: ['src/**/*.js'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.test.js',
        '**/*.spec.js',
      ],
      // Vitest 4 removed coverage.all; coverage.include above sets the file scope.
      // Migrated from the Vitest 0.x flat format to nested thresholds.
      // `thresholds: {}`. Floor documented in tests/README.md.
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },
    include: ['tests/**/*.test.js'],
    exclude: ['node_modules/', 'dist/'],
  },
});
