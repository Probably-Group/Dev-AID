---
name: aid-code-health
description: Codebase health assessment with quality metrics, test coverage, and maintainability analysis
category: quality
author: Dev-AID Team (adapted from Tresor)
version: 1.0.0
---

# Code Health - Codebase Quality Assessment

Assess overall codebase health with quality metrics, test coverage, and maintainability scoring.

## Overview

This command provides a comprehensive code health assessment:
- **Phase 1**: Codebase statistics
- **Phase 2**: Code quality metrics
- **Phase 3**: Test coverage analysis
- **Phase 4**: Documentation assessment
- **Phase 5**: Overall health scoring

## Dev-AID Integration

### Memory Bank Updates
This command updates:
- `.dev-aid/memory-bank/patterns.md` - Code patterns and anti-patterns discovered
- `.dev-aid/memory-bank/testing.md` - Test coverage and quality metrics

### Report Output
Reports are saved to:
- `.dev-aid/reports/quality/code-health-[timestamp]/`

### Multi-Provider Support
Works with all enabled providers (Claude, Gemini, OpenAI).

---

## Execution Steps

### Phase 1: Codebase Statistics

Gather basic codebase metrics:

```bash
echo "=== Codebase Statistics ==="
TIMESTAMP=$(date +%Y-%m-%d-%H%M%S)
REPORT_DIR=".dev-aid/reports/quality/code-health-${TIMESTAMP}"
mkdir -p "$REPORT_DIR"

# Count lines of code by type
echo "Analyzing codebase..."

# Total files and lines
TOTAL_FILES=$(find . -type f \
  -not -path "*/node_modules/*" \
  -not -path "*/.git/*" \
  -not -path "*/dist/*" \
  -not -path "*/build/*" \
  -not -path "*/target/*" \
  -not -path "*/.next/*" \
  -not -path "*/coverage/*" \
  | wc -l)

echo "Total files: $TOTAL_FILES"

# Code files by language
echo ""
echo "Code files by language:"
find . -type f -name "*.js" -not -path "*/node_modules/*" | wc -l | xargs echo "  JavaScript:"
find . -type f -name "*.ts" -not -path "*/node_modules/*" | wc -l | xargs echo "  TypeScript:"
find . -type f -name "*.jsx" -not -path "*/node_modules/*" | wc -l | xargs echo "  React JSX:"
find . -type f -name "*.tsx" -not -path "*/node_modules/*" | wc -l | xargs echo "  React TSX:"
find . -type f -name "*.py" -not -path "*/venv/*" | wc -l | xargs echo "  Python:"
find . -type f -name "*.go" | wc -l | xargs echo "  Go:"
find . -type f -name "*.rs" | wc -l | xargs echo "  Rust:"

# Lines of code
echo ""
echo "Lines of code:"

# Create detailed statistics file
cat > "$REPORT_DIR/codebase-stats.txt" <<EOF
Codebase Statistics - $(date)
==============================

Project: $(basename $(pwd))
Total Files: $TOTAL_FILES

Language Breakdown:
EOF

# Count lines by language
if command -v cloc &> /dev/null; then
  echo "Using cloc for detailed statistics..."
  cloc . --exclude-dir=node_modules,.git,dist,build,target,.next,coverage \
    --quiet --report-file="$REPORT_DIR/cloc-report.txt"
  cat "$REPORT_DIR/cloc-report.txt"
  cat "$REPORT_DIR/cloc-report.txt" >> "$REPORT_DIR/codebase-stats.txt"
else
  echo "Tip: Install 'cloc' for detailed code statistics"
  echo "  brew install cloc  # macOS"
  echo "  apt-get install cloc  # Ubuntu"

  # Fallback: Simple line count
  echo "JavaScript/TypeScript lines:" | tee -a "$REPORT_DIR/codebase-stats.txt"
  find . -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" \
    | xargs wc -l 2>/dev/null | tail -1 | tee -a "$REPORT_DIR/codebase-stats.txt"
fi
```

### Phase 2: Code Quality Metrics

Analyze code quality:

```bash
echo ""
echo "=== Code Quality Analysis ==="

# Check for code complexity (if tools available)
if command -v eslint &> /dev/null && [ -f ".eslintrc.js" ] || [ -f ".eslintrc.json" ]; then
  echo "Running ESLint..."
  eslint . --format=compact > "$REPORT_DIR/eslint-report.txt" 2>&1 || true

  # Count issues by severity
  ERROR_COUNT=$(grep -c "error" "$REPORT_DIR/eslint-report.txt" 2>/dev/null || echo "0")
  WARNING_COUNT=$(grep -c "warning" "$REPORT_DIR/eslint-report.txt" 2>/dev/null || echo "0")

  echo "  Errors: $ERROR_COUNT"
  echo "  Warnings: $WARNING_COUNT"
fi

# Python linting
if command -v pylint &> /dev/null && [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
  echo "Running Pylint..."
  pylint **/*.py > "$REPORT_DIR/pylint-report.txt" 2>&1 || true
  tail -5 "$REPORT_DIR/pylint-report.txt"
fi

# Check for code duplication
echo ""
echo "Checking for code duplication..."

# Find duplicate code patterns
echo "Large files (> 500 lines):"
find . -type f \( -name "*.js" -o -name "*.ts" -o -name "*.py" \) \
  -not -path "*/node_modules/*" -exec wc -l {} \; \
  | awk '$1 > 500 {print $2 " - " $1 " lines"}' \
  | head -10

# Check for very long functions (potential complexity issues)
echo ""
echo "Checking function complexity..."
grep -rn "function\|def " . \
  --include="*.js" --include="*.ts" --include="*.py" \
  --exclude-dir=node_modules \
  | wc -l | xargs echo "Total functions:"
```

### Phase 3: Test Coverage Analysis

Analyze test coverage:

```bash
echo ""
echo "=== Test Coverage Analysis ==="

# Node.js test coverage
if [ -f "package.json" ]; then
  if grep -q "\"test:coverage\":" package.json; then
    echo "Running test coverage analysis..."
    npm run test:coverage > "$REPORT_DIR/coverage-report.txt" 2>&1 || true

    # Extract coverage percentage if available
    if [ -d "coverage" ]; then
      echo "Coverage report generated in: coverage/"

      # Try to extract coverage percentage
      if [ -f "coverage/coverage-summary.json" ]; then
        if command -v jq &> /dev/null; then
          COVERAGE=$(jq -r '.total.lines.pct' coverage/coverage-summary.json 2>/dev/null)
          echo "Overall coverage: ${COVERAGE}%"
        fi
      fi
    fi
  else
    echo "No test:coverage script found in package.json"
    echo "Add: \"test:coverage\": \"jest --coverage\" or similar"
  fi
fi

# Python test coverage
if command -v pytest &> /dev/null; then
  if [ -f "pytest.ini" ] || [ -f "setup.py" ]; then
    echo "Running Python test coverage..."
    pytest --cov=. --cov-report=term > "$REPORT_DIR/pytest-coverage.txt" 2>&1 || true
    tail -20 "$REPORT_DIR/pytest-coverage.txt"
  fi
fi

# Check for files without tests
echo ""
echo "Checking for untested files..."

# Find source files
SRC_FILES=$(find . -type f \( -name "*.js" -o -name "*.ts" \) \
  -not -path "*/node_modules/*" \
  -not -path "*/test/*" \
  -not -path "*/tests/*" \
  -not -name "*.test.*" \
  -not -name "*.spec.*" \
  | wc -l)

# Find test files
TEST_FILES=$(find . -type f \( -name "*.test.*" -o -name "*.spec.*" \) \
  -not -path "*/node_modules/*" \
  | wc -l)

echo "Source files: $SRC_FILES"
echo "Test files: $TEST_FILES"

if [ "$SRC_FILES" -gt 0 ]; then
  TEST_RATIO=$(awk "BEGIN {printf \"%.1f\", ($TEST_FILES / $SRC_FILES) * 100}")
  echo "Test file ratio: ${TEST_RATIO}%"
fi
```

### Phase 4: Documentation Assessment

Analyze documentation quality:

```bash
echo ""
echo "=== Documentation Assessment ==="

# Check README exists and is substantial
if [ -f "README.md" ]; then
  README_LINES=$(wc -l < README.md)
  echo "README.md: $README_LINES lines"

  if [ "$README_LINES" -lt 20 ]; then
    echo "  ⚠️  README is very short (< 20 lines)"
  else
    echo "  ✓ README has good content"
  fi
else
  echo "❌ No README.md found"
fi

# Check for inline documentation
echo ""
echo "Inline documentation:"

# JavaScript/TypeScript JSDoc
JSDOC_COUNT=$(grep -r "^\s*/\*\*" . \
  --include="*.js" --include="*.ts" \
  --exclude-dir=node_modules \
  | wc -l)
echo "  JSDoc comments: $JSDOC_COUNT"

# Python docstrings
DOCSTRING_COUNT=$(grep -r "^\s*\"\"\"" . \
  --include="*.py" \
  --exclude-dir=venv \
  | wc -l)
echo "  Python docstrings: $DOCSTRING_COUNT"

# Check for CONTRIBUTING guide
if [ -f "CONTRIBUTING.md" ]; then
  echo "  ✓ CONTRIBUTING.md exists"
else
  echo "  ⚠️  No CONTRIBUTING.md"
fi

# Check for API documentation
if [ -d "docs" ]; then
  DOC_FILES=$(find docs -name "*.md" | wc -l)
  echo "  ✓ Documentation directory with $DOC_FILES files"
else
  echo "  ⚠️  No docs/ directory"
fi
```

### Phase 5: Overall Health Score

Calculate overall code health score:

```bash
echo ""
echo "=== Overall Code Health Score ==="

# Calculate health score (0-10 scale)
HEALTH_SCORE=10.0

# Deduct points for issues
if [ "$ERROR_COUNT" -gt 50 ]; then
  HEALTH_SCORE=$(awk "BEGIN {print $HEALTH_SCORE - 1.0}")
fi

if [ "$TEST_RATIO" -lt 50 ]; then
  HEALTH_SCORE=$(awk "BEGIN {print $HEALTH_SCORE - 1.5}")
fi

if [ ! -f "README.md" ]; then
  HEALTH_SCORE=$(awk "BEGIN {print $HEALTH_SCORE - 0.5}")
fi

if [ "$JSDOC_COUNT" -eq 0 ] && [ "$DOCSTRING_COUNT" -eq 0 ]; then
  HEALTH_SCORE=$(awk "BEGIN {print $HEALTH_SCORE - 1.0}")
fi

# Determine status
if awk "BEGIN {exit !($HEALTH_SCORE >= 8.0)}"; then
  STATUS="🟢 EXCELLENT"
elif awk "BEGIN {exit !($HEALTH_SCORE >= 6.0)}"; then
  STATUS="🟡 GOOD"
elif awk "BEGIN {exit !($HEALTH_SCORE >= 4.0)}"; then
  STATUS="🟠 FAIR"
else
  STATUS="🔴 NEEDS IMPROVEMENT"
fi

# Generate final report
cat > "$REPORT_DIR/health-score.md" <<EOF
# Code Health Assessment

**Date**: $(date)
**Project**: $(basename $(pwd))

## Overall Health Score: $HEALTH_SCORE / 10.0
**Status**: $STATUS

---

## Health Breakdown

| Category | Score | Status |
|----------|-------|--------|
| Code Quality | $(awk "BEGIN {printf \"%.1f\", 10 - ($ERROR_COUNT / 10)}") / 10 | $([ "$ERROR_COUNT" -lt 50 ] && echo "✓" || echo "⚠️") |
| Test Coverage | $(awk "BEGIN {printf \"%.1f\", $TEST_RATIO / 10}") / 10 | $([ "$TEST_RATIO" -gt 50 ] && echo "✓" || echo "⚠️") |
| Documentation | $([ -f "README.md" ] && echo "7.0" || echo "3.0") / 10 | $([ -f "README.md" ] && echo "✓" || echo "⚠️") |
| Maintainability | 7.0 / 10 | ✓ |

---

## Metrics

### Codebase Size
- Total files: $TOTAL_FILES
- Source files: $SRC_FILES
- Test files: $TEST_FILES

### Code Quality
- Lint errors: $ERROR_COUNT
- Lint warnings: $WARNING_COUNT

### Test Coverage
- Test file ratio: ${TEST_RATIO}%
- Coverage: ${COVERAGE:-"Not measured"}%

### Documentation
- README: $([ -f "README.md" ] && echo "✓" || echo "✗")
- JSDoc comments: $JSDOC_COUNT
- Python docstrings: $DOCSTRING_COUNT
- Docs directory: $([ -d "docs" ] && echo "✓" || echo "✗")

---

## Top Issues to Address

EOF

# Add specific recommendations based on findings
if [ "$ERROR_COUNT" -gt 50 ]; then
  echo "1. **Fix linting errors** - $ERROR_COUNT errors found" >> "$REPORT_DIR/health-score.md"
  echo "   - Run: \`eslint . --fix\`" >> "$REPORT_DIR/health-score.md"
  echo "" >> "$REPORT_DIR/health-score.md"
fi

if awk "BEGIN {exit !($TEST_RATIO < 50)}"; then
  echo "2. **Improve test coverage** - Only ${TEST_RATIO}% of files have tests" >> "$REPORT_DIR/health-score.md"
  echo "   - Goal: 80% test file ratio" >> "$REPORT_DIR/health-score.md"
  echo "   - Add tests for critical business logic" >> "$REPORT_DIR/health-score.md"
  echo "" >> "$REPORT_DIR/health-score.md"
fi

if [ ! -f "README.md" ]; then
  echo "3. **Create README.md** - Project lacks documentation" >> "$REPORT_DIR/health-score.md"
  echo "   - Include: Setup, Usage, API docs" >> "$REPORT_DIR/health-score.md"
  echo "" >> "$REPORT_DIR/health-score.md"
fi

cat >> "$REPORT_DIR/health-score.md" <<EOF

## Recommendations

### Quick Wins (< 1 week)
- [ ] Fix critical linting errors
- [ ] Add README if missing
- [ ] Add tests for core modules

### Medium-term (1-4 weeks)
- [ ] Achieve 70% test coverage
- [ ] Document all public APIs
- [ ] Refactor large files (> 500 lines)

### Long-term (> 1 month)
- [ ] Achieve 90% test coverage
- [ ] Add comprehensive API documentation
- [ ] Implement automated code quality checks in CI/CD

---

## Reports Generated

- Health Score: health-score.md
- Codebase Stats: codebase-stats.txt
- Lint Report: eslint-report.txt (if applicable)
- Coverage Report: coverage/ (if generated)

**Report Location**: $REPORT_DIR/
EOF

# Display health score
cat "$REPORT_DIR/health-score.md"

# Update memory bank
cat >> .dev-aid/memory-bank/patterns.md <<EOF

## Code Health Assessment - $(date +%Y-%m-%d)

**Health Score**: $HEALTH_SCORE / 10.0 ($STATUS)

### Key Metrics
- Lint errors: $ERROR_COUNT
- Test file ratio: ${TEST_RATIO}%
- Documentation: $([ -f "README.md" ] && echo "Good" || echo "Needs work")

### Improvement Areas
- $([ "$ERROR_COUNT" -gt 50 ] && echo "Reduce linting errors" || echo "Code quality maintained")
- $(awk "BEGIN {exit !($TEST_RATIO < 50)}" && echo "Improve test coverage" || echo "Test coverage adequate")

EOF

cat >> .dev-aid/memory-bank/testing.md <<EOF

## Test Coverage - $(date +%Y-%m-%d)

**Test File Ratio**: ${TEST_RATIO}%
**Coverage**: ${COVERAGE:-"Not measured"}%

### Test Files
- Total: $TEST_FILES
- Source files: $SRC_FILES

EOF

echo ""
echo "✅ Code health assessment complete!"
echo "📄 Full Report: $REPORT_DIR/health-score.md"
```

---

## Usage Examples

### Basic Assessment
```bash
/aid-code-health
```

### After Assessment - Fix Issues
```bash
# Fix linting errors
eslint . --fix

# Run tests with coverage
npm run test:coverage

# Review large files for refactoring
find . -name "*.js" -o -name "*.ts" | xargs wc -l | sort -rn | head -10
```

### Schedule Regular Assessments
Add to weekly tasks:
```bash
# Weekly code health check
/aid-code-health

# Review health score trend over time
```

---

## Tool Installation

For best results, install code quality tools:

**JavaScript/TypeScript:**
```bash
npm install -D eslint @typescript-eslint/parser
npm install -D jest  # For test coverage
npm install -g cloc  # For code statistics
```

**Python:**
```bash
pip install pylint
pip install pytest pytest-cov
```

**General:**
```bash
# macOS
brew install cloc

# Ubuntu
apt-get install cloc
```

---

## Success Criteria

Assessment succeeds if:
- ✅ Codebase statistics collected
- ✅ Code quality metrics gathered
- ✅ Test coverage analyzed
- ✅ Documentation assessed
- ✅ Health score calculated
- ✅ Reports generated
- ✅ Memory bank updated

---

**Begin codebase health assessment.**
