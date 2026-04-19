import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'happy-dom',
    globals: true,
    setupFiles: ['./__tests__/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      // Thresholds adjusted for happy-dom environment which doesn't fully
      // support focus APIs needed by useFocusTrap. Branch coverage is
      // particularly affected by focus-related code paths.
      thresholds: {
        statements: 85,
        branches: 65,
        functions: 90,
        lines: 85
      },
      exclude: [
        'node_modules/',
        '__tests__/',
        'src/app/',
        'src/components/',
        '**/*.d.ts',
      ]
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
})
