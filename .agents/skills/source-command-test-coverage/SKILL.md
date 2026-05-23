---
name: "source-command-test-coverage"
description: "Run the migrated source command `test-coverage`."
---

# source-command-test-coverage

Use this skill when the user asks to run the migrated source command `test-coverage`.

## Command Template

# Test Coverage

Analyze test coverage and generate missing tests:

1. Run tests with coverage: npm test --coverage or pnpm test --coverage

2. Analyze coverage report (coverage/coverage-summary.json)

3. Identify files below 80% coverage threshold

4. For each under-covered file:
   - Analyze untested code paths
   - Generate unit tests for functions
   - Generate integration tests for APIs
   - Generate E2E tests for critical flows

5. Verify new tests pass

6. Show before/after coverage metrics

7. Ensure project reaches 80%+ overall coverage

Focus on:
- Happy path scenarios
- Error handling
- Edge cases (null, undefined, empty)
- Boundary conditions

## Migration Notes

Migrated from source command `test-coverage` into a Codex skill. Invoke it as `$source-command-test-coverage` or ask for coverage analysis in plain language. The original slash-command behavior is preserved as prose.
