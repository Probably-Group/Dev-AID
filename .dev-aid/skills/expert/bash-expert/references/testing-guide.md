# Bash Testing Guide

Comprehensive guide to testing Bash scripts including unit testing, integration testing, and validation strategies.

---

## 1. Static Analysis and Validation

### 1.1 ShellCheck - Syntax and Best Practices

**Purpose**: Catches common bugs and style issues before runtime.

```bash
# Basic syntax check
shellcheck script.sh

# Check all scripts in directory
find . -name "*.sh" -type f -exec shellcheck {} +

# Specific checks only
shellcheck --severity=error script.sh

# Exclude specific warnings
shellcheck --exclude=SC2086,SC2181 script.sh

# Output in different formats
shellcheck --format=json script.sh
shellcheck --format=gcc script.sh  # For CI/CD integration
```

**Common Issues Detected**:
- Unquoted variables
- Unused variables
- Missing error handling
- Incorrect test syntax
- Portability issues
- Security vulnerabilities

**Integration in CI/CD**:
```bash
#!/bin/bash
# .github/workflows/shellcheck.sh

set -euo pipefail

echo "Running shellcheck on all shell scripts..."

# Find all shell scripts
mapfile -t scripts < <(find . -name "*.sh" -type f)

failed=0
for script in "${scripts[@]}"; do
    if ! shellcheck "$script"; then
        echo "❌ Failed: $script" >&2
        ((failed++))
    else
        echo "✅ Passed: $script"
    fi
done

if [[ $failed -gt 0 ]]; then
    echo "❌ Shellcheck failed for $failed script(s)" >&2
    exit 1
fi

echo "✅ All scripts passed shellcheck"
```

---

### 1.2 Bash Syntax Validation

**Purpose**: Verify syntax without executing the script.

```bash
# Syntax check without execution
bash -n script.sh

# Check all scripts
for script in *.sh; do
    echo "Checking: $script"
    bash -n "$script" || echo "Syntax error in $script" >&2
done

# Strict syntax check with pipefail
bash -neuo pipefail script.sh
```

---

## 2. Unit Testing Frameworks

### 2.1 BATS (Bash Automated Testing System)

**Installation**:
```bash
# Clone BATS repository
git clone https://github.com/bats-core/bats-core.git
cd bats-core
./install.sh /usr/local

# Or via package manager
apt-get install bats  # Debian/Ubuntu
brew install bats-core  # macOS
```

**Basic Test Structure**:
```bash
#!/usr/bin/env bats

# test/script.bats

# Setup function (runs before each test)
setup() {
    # Load script functions
    source "${BATS_TEST_DIRNAME}/../script.sh"

    # Create temp directory
    TEST_TEMP_DIR="$(mktemp -d)"
}

# Teardown function (runs after each test)
teardown() {
    # Cleanup
    rm -rf "$TEST_TEMP_DIR"
}

@test "sanitize_filename removes spaces" {
    result=$(sanitize_filename "my file.txt")
    [ "$result" = "myfile.txt" ]
}

@test "sanitize_filename removes special chars" {
    result=$(sanitize_filename "file@#$.txt")
    [ "$result" = "file.txt" ]
}

@test "validate_email accepts valid email" {
    run validate_email "user@example.com"
    [ "$status" -eq 0 ]
}

@test "validate_email rejects invalid email" {
    run validate_email "not-an-email"
    [ "$status" -eq 1 ]
    [[ "$output" =~ "Invalid email" ]]
}

@test "process_file handles missing file" {
    run process_file "nonexistent.txt"
    [ "$status" -eq 1 ]
    [[ "$output" =~ "not found" ]]
}
```

**Advanced BATS Features**:
```bash
#!/usr/bin/env bats

# Helper functions
load test_helper

@test "function handles empty input" {
    run my_function ""
    [ "$status" -eq 1 ]
    [[ "${lines[0]}" =~ "Error: Missing input" ]]
}

@test "function processes multiple files" {
    # Setup test files
    echo "data1" > "$TEST_TEMP_DIR/file1.txt"
    echo "data2" > "$TEST_TEMP_DIR/file2.txt"

    run process_files "$TEST_TEMP_DIR"/*.txt
    [ "$status" -eq 0 ]
    [ "${#lines[@]}" -eq 2 ]
}

@test "script respects timeout" {
    # Test with timeout
    run timeout 5s long_running_function
    [ "$status" -eq 0 ]
}

@test "function is idempotent" {
    # Run twice, should produce same result
    run my_function "input"
    first_output="$output"

    run my_function "input"
    [ "$output" = "$first_output" ]
}
```

**Running BATS Tests**:
```bash
# Run all tests
bats test/

# Run specific test file
bats test/validation.bats

# Verbose output
bats --verbose test/

# TAP output for CI/CD
bats --tap test/

# Parallel execution
bats --jobs 4 test/
```

---

### 2.2 Manual Unit Testing

**Simple Test Framework**:
```bash
#!/bin/bash
# test_runner.sh

set -euo pipefail

# Test counters
readonly -i TESTS_RUN=0
readonly -i TESTS_PASSED=0
readonly -i TESTS_FAILED=0

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[0;33m'
readonly NC='\033[0m' # No Color

# Assert functions
assert_equals() {
    local expected="$1"
    local actual="$2"
    local message="${3:-}"

    ((TESTS_RUN++))

    if [[ "$expected" = "$actual" ]]; then
        ((TESTS_PASSED++))
        echo -e "${GREEN}✓${NC} ${message:-Assertion passed}"
        return 0
    else
        ((TESTS_FAILED++))
        echo -e "${RED}✗${NC} ${message:-Assertion failed}"
        echo "  Expected: '$expected'"
        echo "  Actual:   '$actual'"
        return 1
    fi
}

assert_success() {
    local message="${1:-Command should succeed}"

    ((TESTS_RUN++))

    if "$@"; then
        ((TESTS_PASSED++))
        echo -e "${GREEN}✓${NC} $message"
        return 0
    else
        ((TESTS_FAILED++))
        echo -e "${RED}✗${NC} $message (exit code: $?)"
        return 1
    fi
}

assert_failure() {
    local message="${1:-Command should fail}"

    ((TESTS_RUN++))

    if ! "$@"; then
        ((TESTS_PASSED++))
        echo -e "${GREEN}✓${NC} $message"
        return 0
    else
        ((TESTS_FAILED++))
        echo -e "${RED}✗${NC} $message (should have failed)"
        return 1
    fi
}

assert_contains() {
    local haystack="$1"
    local needle="$2"
    local message="${3:-}"

    ((TESTS_RUN++))

    if [[ "$haystack" == *"$needle"* ]]; then
        ((TESTS_PASSED++))
        echo -e "${GREEN}✓${NC} ${message:-String contains expected value}"
        return 0
    else
        ((TESTS_FAILED++))
        echo -e "${RED}✗${NC} ${message:-String does not contain expected value}"
        echo "  Haystack: '$haystack'"
        echo "  Needle:   '$needle'"
        return 1
    fi
}

# Test suite example
test_sanitize_filename() {
    echo "Testing sanitize_filename..."

    result=$(sanitize_filename "my file.txt")
    assert_equals "myfile.txt" "$result" "Should remove spaces"

    result=$(sanitize_filename "file@#$.txt")
    assert_equals "file.txt" "$result" "Should remove special chars"

    result=$(sanitize_filename "../../etc/passwd")
    assert_equals "passwd" "$result" "Should remove path traversal"
}

test_validate_email() {
    echo "Testing validate_email..."

    assert_success validate_email "user@example.com"
    assert_failure validate_email "not-an-email"
    assert_failure validate_email "user@"
    assert_failure validate_email "@example.com"
}

# Run all tests
run_tests() {
    echo "Running test suite..."
    echo

    test_sanitize_filename
    test_validate_email
    # Add more test functions here

    echo
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Test Results:"
    echo "  Tests run:    $TESTS_RUN"
    echo -e "  ${GREEN}Tests passed: $TESTS_PASSED${NC}"
    echo -e "  ${RED}Tests failed: $TESTS_FAILED${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}All tests passed!${NC}"
        return 0
    else
        echo -e "${RED}Some tests failed!${NC}"
        return 1
    fi
}

# Source the script to test
source ./script.sh

# Run tests
run_tests
```

---

## 3. Integration Testing

### 3.1 End-to-End Testing

**Test Complete Workflows**:
```bash
#!/bin/bash
# integration_test.sh

set -euo pipefail

# Setup test environment
setup_test_env() {
    export TEST_DIR="$(mktemp -d)"
    export TEST_DB="$TEST_DIR/test.db"
    export TEST_CONFIG="$TEST_DIR/config.ini"

    # Create test fixtures
    cat > "$TEST_CONFIG" <<EOF
[database]
path=$TEST_DB

[app]
debug=true
EOF

    # Initialize test database
    sqlite3 "$TEST_DB" <<EOF
CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);
INSERT INTO users VALUES (1, 'Alice');
INSERT INTO users VALUES (2, 'Bob');
EOF
}

# Cleanup test environment
cleanup_test_env() {
    rm -rf "$TEST_DIR"
}

# Ensure cleanup on exit
trap cleanup_test_env EXIT INT TERM

# Test scenarios
test_user_creation() {
    echo "Testing user creation workflow..."

    # Run the script
    ./app.sh create-user "Charlie" --config "$TEST_CONFIG"

    # Verify user was created
    result=$(sqlite3 "$TEST_DB" "SELECT name FROM users WHERE name='Charlie'")

    if [[ "$result" = "Charlie" ]]; then
        echo "✅ User creation test passed"
        return 0
    else
        echo "❌ User creation test failed" >&2
        return 1
    fi
}

test_user_deletion() {
    echo "Testing user deletion workflow..."

    ./app.sh delete-user "Alice" --config "$TEST_CONFIG"

    result=$(sqlite3 "$TEST_DB" "SELECT COUNT(*) FROM users WHERE name='Alice'")

    if [[ "$result" = "0" ]]; then
        echo "✅ User deletion test passed"
        return 0
    else
        echo "❌ User deletion test failed" >&2
        return 1
    fi
}

# Run integration tests
main() {
    setup_test_env

    local failed=0

    test_user_creation || ((failed++))
    test_user_deletion || ((failed++))

    if [[ $failed -eq 0 ]]; then
        echo "✅ All integration tests passed"
        return 0
    else
        echo "❌ $failed integration test(s) failed" >&2
        return 1
    fi
}

main
```

---

### 3.2 Mock External Dependencies

**Mocking External Commands**:
```bash
#!/bin/bash
# test_with_mocks.sh

# Mock curl for testing
curl() {
    # Redirect to mock implementation
    case "$*" in
        *"api.example.com/users"*)
            cat <<EOF
{"users": [{"id": 1, "name": "Alice"}]}
EOF
            return 0
            ;;
        *"api.example.com/error"*)
            echo "Error: API unavailable" >&2
            return 1
            ;;
        *)
            echo "Error: Unknown endpoint" >&2
            return 1
            ;;
    esac
}

# Export mock function
export -f curl

# Now test script that uses curl
source ./script.sh

test_api_call() {
    # This will use our mock curl
    result=$(fetch_users)
    echo "$result" | grep -q "Alice" && echo "✅ Test passed" || echo "❌ Test failed"
}

test_api_call
```

**Mocking with Temporary Scripts**:
```bash
#!/bin/bash
# Create mock commands in temp directory

setup_mocks() {
    MOCK_DIR="$(mktemp -d)"

    # Create mock git command
    cat > "$MOCK_DIR/git" <<'EOF'
#!/bin/bash
# Mock git command
case "$1" in
    "status")
        echo "On branch main"
        echo "nothing to commit, working tree clean"
        ;;
    "log")
        echo "commit abc123 Mock commit message"
        ;;
    *)
        echo "git $*" >&2
        exit 0
        ;;
esac
EOF

    chmod +x "$MOCK_DIR/git"

    # Add mock directory to PATH
    export PATH="$MOCK_DIR:$PATH"
}

cleanup_mocks() {
    rm -rf "$MOCK_DIR"
}

trap cleanup_mocks EXIT

setup_mocks

# Run tests with mocked commands
source ./script.sh
run_tests
```

---

## 4. Performance Testing

### 4.1 Benchmarking

**Simple Benchmark**:
```bash
#!/bin/bash
# benchmark.sh

benchmark() {
    local name="$1"
    shift
    local iterations="${1:-100}"
    shift

    echo "Benchmarking: $name ($iterations iterations)"

    local start
    start=$(date +%s.%N)

    for ((i=0; i<iterations; i++)); do
        "$@" > /dev/null 2>&1
    done

    local end
    end=$(date +%s.%N)

    local duration
    duration=$(echo "$end - $start" | bc)
    local avg
    avg=$(echo "scale=6; $duration / $iterations" | bc)

    echo "  Total time: ${duration}s"
    echo "  Average:    ${avg}s per iteration"
}

# Example usage
benchmark "grep pattern" 1000 grep -r "pattern" /path/to/files
benchmark "awk processing" 100 awk '{print $1}' largefile.txt
```

**Memory Usage**:
```bash
#!/bin/bash
# Check memory usage

check_memory_usage() {
    local script="$1"

    # Run with time and get memory info
    /usr/bin/time -v bash "$script" 2>&1 | grep "Maximum resident set size"
}

check_memory_usage "./script.sh"
```

---

## 5. Coverage Analysis

### 5.1 Function Coverage

**Track Function Calls**:
```bash
#!/bin/bash
# coverage.sh

declare -A FUNCTION_CALLS

# Wrap functions with coverage tracking
track_coverage() {
    local func_name="$1"
    FUNCTION_CALLS[$func_name]=$((${FUNCTION_CALLS[$func_name]:-0} + 1))
}

# Instrument functions
sanitize_filename() {
    track_coverage "sanitize_filename"
    # Original function body
}

validate_email() {
    track_coverage "validate_email"
    # Original function body
}

# Report coverage
report_coverage() {
    echo "Function Coverage Report:"
    for func in "${!FUNCTION_CALLS[@]}"; do
        echo "  $func: ${FUNCTION_CALLS[$func]} calls"
    done
}

trap report_coverage EXIT
```

---

## 6. Test Organization

### 6.1 Directory Structure

```
project/
├── script.sh              # Main script
├── lib/                   # Libraries
│   ├── validation.sh
│   └── helpers.sh
├── test/                  # Test directory
│   ├── test_helper.bash   # Shared test utilities
│   ├── unit/              # Unit tests
│   │   ├── validation.bats
│   │   └── helpers.bats
│   ├── integration/       # Integration tests
│   │   └── workflow.bats
│   ├── fixtures/          # Test data
│   │   ├── sample.txt
│   │   └── config.ini
│   └── mocks/             # Mock commands
│       └── git
└── Makefile               # Test automation
```

### 6.2 Test Automation with Makefile

```makefile
# Makefile

.PHONY: test test-unit test-integration test-all shellcheck lint

# Run all tests
test-all: shellcheck test

# Static analysis
shellcheck:
	@echo "Running shellcheck..."
	@find . -name "*.sh" -type f -exec shellcheck {} +

# Alias for shellcheck
lint: shellcheck

# Unit tests
test-unit:
	@echo "Running unit tests..."
	@bats test/unit/

# Integration tests
test-integration:
	@echo "Running integration tests..."
	@bats test/integration/

# All functional tests
test: test-unit test-integration

# Coverage report
coverage:
	@echo "Generating coverage report..."
	@./scripts/generate_coverage.sh

# Clean test artifacts
clean:
	@echo "Cleaning test artifacts..."
	@find test/ -name "*.log" -delete
	@rm -rf test/tmp/
```

---

## 7. Continuous Integration

### 7.1 GitHub Actions Example

```yaml
# .github/workflows/test.yml

name: Test Bash Scripts

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y shellcheck bats

      - name: Run shellcheck
        run: |
          find . -name "*.sh" -type f -exec shellcheck {} +

      - name: Run unit tests
        run: |
          bats test/unit/

      - name: Run integration tests
        run: |
          bats test/integration/

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: test/results/
```

---

## 8. Best Practices

### Testing Checklist

**Before Deployment**:
- [ ] All functions have unit tests
- [ ] Critical workflows have integration tests
- [ ] Shellcheck passes with no errors
- [ ] Syntax validation passes
- [ ] Tests run in CI/CD pipeline
- [ ] Code coverage > 80%
- [ ] Performance benchmarks acceptable
- [ ] Error cases tested
- [ ] Edge cases covered
- [ ] Mocks for external dependencies

**Test Quality**:
- [ ] Tests are independent (no order dependency)
- [ ] Tests clean up after themselves
- [ ] Tests are fast (< 5s for unit tests)
- [ ] Tests have clear names
- [ ] Assertions have descriptive messages
- [ ] Test data is realistic
- [ ] Flaky tests are fixed or removed

**Documentation**:
- [ ] Test purpose documented
- [ ] Setup requirements documented
- [ ] How to run tests documented
- [ ] Expected results documented
