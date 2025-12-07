## 5. Safety-First Refactoring Workflow

### Mandatory Pre-Refactoring Checklist

```bash
# 1. Create feature branch
git checkout -b refactor/descriptive-name

# 2. Run all existing tests (MUST PASS)
./run-tests.sh  # Or npm test, pytest, cargo test, etc.

# 3. If tests fail or missing, STOP
# Fix tests first, or create characterization tests

# 4. Optional: Enable test coverage reporting
pytest --cov=module_name
npm test -- --coverage

# 5. Only proceed if tests pass and coverage adequate
```

### During Refactoring

```bash
# 1. Make ONE small change at a time
# 2. Run tests after each change
# 3. Commit immediately if tests pass
git add -p  # Review changes carefully
git commit -m "refactor: extract getUserData method"

# 4. Repeat for next small change
# 5. Push frequently to backup work
```

### Post-Refactoring Validation

```bash
# 1. Run full test suite
./run-all-tests.sh

# 2. Run linting and static analysis
./lint.sh

# 3. Performance benchmarks (if applicable)
./run-benchmarks.sh

# 4. Manual smoke testing of critical paths

# 5. Create PR with detailed description
gh pr create --title "Refactor: User authentication flow" \
  --body "$(cat <<EOF
## Summary
Refactored user authentication to use strategy pattern for better extensibility.

## Changes
- Extracted AuthStrategy interface
- Implemented LocalAuthStrategy, OAuthStrategy
- Removed duplicate code in login/signup flows
- Added tests for new auth strategies

## Testing
- All existing tests pass (242/242)
- Added 18 new unit tests for strategies
- Manual testing: login/signup/logout flows verified
- No breaking changes to API

## Migration Guide
No action needed - internal refactoring only.
EOF
)"
```

---

