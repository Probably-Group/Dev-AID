# Language-Aware Verification Commands

Complete reference for per-language verification commands used by the verification-gate skill.

## Language Detection

### Detection Priority

Check files in this order to determine project type:

| Priority | File/Pattern | Project Type |
|----------|--------------|--------------|
| 1 | `package.json` | Node.js (npm/yarn/pnpm/bun) |
| 2 | `Cargo.toml` | Rust |
| 3 | `go.mod` | Go |
| 4 | `pyproject.toml` | Python (modern) |
| 5 | `setup.py` | Python (legacy) |
| 6 | `requirements.txt` | Python (minimal) |
| 7 | `pom.xml` | Java (Maven) |
| 8 | `build.gradle` | Java/Kotlin (Gradle) |
| 9 | `*.csproj` | C# (.NET) |
| 10 | `composer.json` | PHP |
| 11 | `Gemfile` | Ruby |

### Multi-Language Projects

When multiple indicators exist:
- Use the most specific (e.g., `pyproject.toml` over `requirements.txt`)
- If equal priority, prefer the one with more recent modification
- Allow explicit override via `--language` flag

---

## Python

### Package Manager Detection

| File | Manager | Test Command |
|------|---------|--------------|
| `pyproject.toml` + `poetry.lock` | Poetry | `poetry run pytest` |
| `pyproject.toml` + `uv.lock` | uv | `uv run pytest` |
| `pyproject.toml` (only) | pip | `pytest` |
| `requirements.txt` | pip | `pytest` |

### Verification Commands

```bash
# Tests
pytest -v                          # Standard
pytest -v --tb=short              # Shorter traceback
pytest -v -x                      # Stop on first failure
pytest -v --cov=src --cov-report=term-missing  # With coverage

# Build (syntax check)
python -m py_compile src/**/*.py  # Check syntax
python -m compileall src/         # Compile all

# Lint
flake8 . --max-line-length=120    # Style
mypy . --ignore-missing-imports   # Types
black --check .                   # Formatting
isort --check-only .              # Import sorting
bandit -r . -ll                   # Security

# Combined
flake8 . && mypy . && pytest -v   # Full validation
```

### Expected Output Patterns

```
# Passing tests
==================== 47 passed in 2.34s ====================
# Exit code: 0

# Failing tests
==================== 1 failed, 46 passed in 2.51s ====================
# Exit code: 1

# Type check pass
Success: no issues found in 156 source files
# Exit code: 0
```

---

## Node.js / TypeScript

### Package Manager Detection

| File | Manager | Test Command |
|------|---------|--------------|
| `pnpm-lock.yaml` | pnpm | `pnpm test` |
| `yarn.lock` | yarn | `yarn test` |
| `bun.lockb` | bun | `bun test` |
| `package-lock.json` | npm | `npm test` |

### Verification Commands

```bash
# Tests
npm test                          # Standard
npm run test:coverage             # With coverage (if configured)
npx jest --passWithNoTests        # Jest specific
npx vitest run                    # Vitest

# Build
npm run build                     # Standard
npx tsc --noEmit                  # Type check only
npx tsc                           # Full compile

# Lint
npm run lint                      # Standard (uses project config)
npx eslint . --ext .ts,.tsx       # ESLint direct
npx prettier --check .            # Formatting

# Combined
npm run lint && npm run build && npm test  # Full validation
```

### Expected Output Patterns

```
# Jest passing
Test Suites: 12 passed, 12 total
Tests:       47 passed, 47 total
Time:        3.245 s
# Exit code: 0

# TypeScript no errors
# (no output on success)
# Exit code: 0

# TypeScript with errors
src/auth.ts(15,23): error TS2345: Argument of type 'string' is not assignable...
Found 1 error in src/auth.ts:15
# Exit code: 1
```

---

## Rust

### Verification Commands

```bash
# Tests
cargo test                        # Standard
cargo test -- --nocapture         # Show println! output
cargo test --release              # Release mode tests

# Build
cargo build                       # Debug build
cargo build --release             # Release build
cargo check                       # Fast type check (no codegen)

# Lint
cargo clippy                      # Lints
cargo clippy -- -D warnings       # Treat warnings as errors
cargo fmt -- --check              # Formatting check

# Combined
cargo fmt -- --check && cargo clippy && cargo test  # Full validation
```

### Expected Output Patterns

```
# Passing tests
running 47 tests
test result: ok. 47 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
# Exit code: 0

# Failing tests
running 47 tests
test result: FAILED. 46 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out
# Exit code: 101

# Build success
   Compiling myproject v0.1.0
    Finished dev [unoptimized + debuginfo] target(s) in 2.34s
# Exit code: 0
```

---

## Go

### Verification Commands

```bash
# Tests
go test ./...                     # All packages
go test -v ./...                  # Verbose
go test -race ./...               # Race detector
go test -cover ./...              # With coverage

# Build
go build ./...                    # Build all
go install ./...                  # Install binaries

# Lint
go vet ./...                      # Built-in checks
golangci-lint run                 # Comprehensive lint (if installed)
gofmt -l .                        # Format check (lists files)

# Combined
go vet ./... && golangci-lint run && go test -race ./...  # Full validation
```

### Expected Output Patterns

```
# Passing tests
ok      myproject/pkg        0.234s
ok      myproject/cmd        0.156s
# Exit code: 0

# Failing tests
--- FAIL: TestAuth (0.00s)
    auth_test.go:45: expected true, got false
FAIL    myproject/pkg        0.234s
# Exit code: 1

# go vet success
# (no output on success)
# Exit code: 0
```

---

## Java (Maven)

### Verification Commands

```bash
# Tests
mvn test                          # Standard
mvn test -Dtest=ClassName         # Specific class

# Build
mvn compile                       # Compile only
mvn package                       # Full build

# Lint
mvn checkstyle:check              # Style
mvn spotbugs:check                # Bug detection
```

---

## Java (Gradle)

### Verification Commands

```bash
# Tests
./gradlew test                    # Standard
./gradlew test --info             # Verbose

# Build
./gradlew build                   # Full build
./gradlew compileJava             # Compile only

# Lint
./gradlew check                   # All checks
```

---

## C# (.NET)

### Verification Commands

```bash
# Tests
dotnet test                       # Standard
dotnet test --verbosity normal    # Verbose

# Build
dotnet build                      # Build
dotnet build --no-restore         # Without restore

# Lint
dotnet format --verify-no-changes # Format check
```

---

## Evidence Interpretation

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - all checks passed |
| 1 | Failure - tests failed or errors found |
| 2+ | Tool-specific error (check documentation) |

### Partial Success Handling

**NEVER claim success for partial results:**

```
❌ "45 of 47 tests pass" → NOT success
❌ "Build succeeded with 3 warnings" → NOT clean success
❌ "0 errors, 12 warnings" → Requires decision on warnings
```

**Correct handling:**

```
✅ "46 tests pass, 1 test fails (test_auth_token in test_auth.py:45)"
✅ "Build succeeded with 3 warnings (list them if relevant)"
✅ "Lint reports 0 errors, 12 warnings - need decision on warning policy"
```

### Output Parsing Rules

1. Always check exit code first
2. Parse output for pass/fail counts
3. Extract specific failure locations
4. Note any warnings
5. Report complete picture

---

## Integration with Dev-AID

### Automatic Language Detection

The verification-gate skill reads `process-skills.json` for language detection configuration:

```json
{
  "languageDetection": {
    "priority": [
      { "file": "package.json", "type": "nodejs" },
      { "file": "Cargo.toml", "type": "rust" },
      ...
    ],
    "commands": {
      "nodejs": { "test": "npm test", ... },
      "python": { "test": "pytest -v", ... },
      ...
    }
  }
}
```

### Custom Commands

Projects can override default commands in `process-skills.json`:

```json
{
  "customCommands": {
    "test": "make test",
    "lint": "make lint",
    "build": "make build"
  }
}
```
