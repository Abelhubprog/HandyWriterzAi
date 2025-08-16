// Jest config for Next.js + TypeScript project
const nextJest = require('next/jest');

const createJestConfig = nextJest({
  dir: './',
});

const customJestConfig = {
  testEnvironment: 'jest-environment-jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  // Only run unit tests from src; exclude Playwright e2e specs
  testMatch: ['<rootDir>/src/**/__tests__/**/*.[jt]s?(x)', '<rootDir>/src/**/*.(spec|test).[tj]s?(x)'],
  testPathIgnorePatterns: ['<rootDir>/tests/e2e/'],
};

module.exports = createJestConfig(customJestConfig);
