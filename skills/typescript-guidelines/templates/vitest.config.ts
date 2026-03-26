import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    // Native TypeScript support - no ts-jest needed
    // Note: When globals: true, add "vitest/globals" to tsconfig types array
    globals: true,

    // Environment: 'node' for backend, 'jsdom' for frontend
    environment: 'node',

    // Test file patterns
    include: ['**/*.{test,spec}.{ts,tsx}'],
    exclude: ['node_modules', 'dist', 'build', '.next'],

    // Coverage configuration
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        '**/*.d.ts',
        '**/*.test.ts',
        '**/*.spec.ts',
        '**/index.ts',
        '**/types.ts',
        'node_modules/**',
        'dist/**',
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },

    // Type checking during tests (optional, adds time)
    typecheck: {
      enabled: false, // Enable for stricter testing
      tsconfig: './tsconfig.json',
    },

    // Watch mode configuration
    watchExclude: ['node_modules', 'dist', 'build'],

    // Pool configuration for performance
    pool: 'threads',
    poolOptions: {
      threads: {
        singleThread: false,
      },
    },

    // Timeouts
    testTimeout: 10000,
    hookTimeout: 10000,

    // Reporter
    reporters: ['default'],

    // Setup files (run before each test file)
    // setupFiles: ['./tests/setup.ts'],
  },
});
