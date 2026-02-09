---
name: aid-debt-analysis
description: Technical debt identification with prioritization, cost analysis, and refactoring roadmap
category: quality
author: Dev-AID Team (https://probably.group) (adapted from Tresor)
version: 1.0.0
---

# Technical Debt Analysis - Systematic Debt Identification

Identify, quantify, and prioritize technical debt for strategic refactoring.

## Overview

This command provides systematic technical debt analysis:
- **Phase 1**: Debt identification across all categories
- **Phase 2**: Cost quantification (time wasted)
- **Phase 3**: Risk assessment
- **Phase 4**: Effort estimation
- **Phase 5**: Prioritization and roadmap

## Dev-AID Integration

### Memory Bank Updates
This command updates:
- `.dev-aid/memory-bank/patterns.md` - Technical debt items and patterns
- `.dev-aid/memory-bank/decisions.md` - Debt prioritization decisions

### Report Output
Reports are saved to:
- `.dev-aid/reports/quality/debt-analysis-[timestamp]/`

### Multi-Provider Support
Works with all enabled providers (Claude, Gemini, OpenAI).

---

## Execution Steps

### Phase 1: Identify Technical Debt

Scan codebase for various types of technical debt:

```bash
echo "=== Technical Debt Identification ==="
TIMESTAMP=$(date +%Y-%m-%d-%H%M%S)
REPORT_DIR=".dev-aid/reports/quality/debt-analysis-${TIMESTAMP}"
mkdir -p "$REPORT_DIR"

# Initialize debt counters
DEBT_COUNT=0

# Create debt inventory
cat > "$REPORT_DIR/debt-inventory.md" <<EOF
# Technical Debt Inventory

**Date**: $(date)
**Project**: $(basename $(pwd))

## Debt Categories

EOF

echo "Scanning for technical debt..."
echo ""

# 1. Code Debt
echo "### 1. Code Debt" | tee -a "$REPORT_DIR/debt-inventory.md"
echo "" | tee -a "$REPORT_DIR/debt-inventory.md"

# TODO comments
TODO_COUNT=$(grep -r "TODO\|FIXME\|HACK\|XXX" . \
  --include="*.js" --include="*.ts" --include="*.py" --include="*.go" --include="*.rs" \
  --exclude-dir=node_modules --exclude-dir=.git \
  | wc -l)
echo "- **TODO/FIXME comments**: $TODO_COUNT" | tee -a "$REPORT_DIR/debt-inventory.md"
DEBT_COUNT=$((DEBT_COUNT + TODO_COUNT))

# Large files (> 500 lines)
LARGE_FILES=$(find . -type f \( -name "*.js" -o -name "*.ts" -o -name "*.py" \) \
  -not -path "*/node_modules/*" -not -path "*/.git/*" \
  -exec wc -l {} \; | awk '$1 > 500' | wc -l)
echo "- **Large files (> 500 lines)**: $LARGE_FILES" | tee -a "$REPORT_DIR/debt-inventory.md"
DEBT_COUNT=$((DEBT_COUNT + LARGE_FILES))

# Complex functions (> 100 lines)
COMPLEX_FUNCS=$(grep -rn "function\|def " . \
  --include="*.js" --include="*.ts" --include="*.py" \
  --exclude-dir=node_modules | wc -l)
echo "- **Total functions**: $COMPLEX_FUNCS (scan for complexity)" | tee -a "$REPORT_DIR/debt-inventory.md"

# Duplicate code patterns
echo "- **Code duplication**: Checking..." | tee -a "$REPORT_DIR/debt-inventory.md"
DUPLICATE_PATTERNS=$(grep -rn "copy.*paste\|duplicate\|DRY" . \
  --include="*.js" --include="*.ts" --include="*.py" \
  --exclude-dir=node_modules | wc -l)
echo "  Found $DUPLICATE_PATTERNS potential duplicates" | tee -a "$REPORT_DIR/debt-inventory.md"

echo "" | tee -a "$REPORT_DIR/debt-inventory.md"

# 2. Architecture Debt
echo "### 2. Architecture Debt" | tee -a "$REPORT_DIR/debt-inventory.md"
echo "" | tee -a "$REPORT_DIR/debt-inventory.md"

# Check for architecture issues
if ! [ -d "src" ] && ! [ -d "lib" ]; then
  echo "- **⚠️  No clear source directory structure**" | tee -a "$REPORT_DIR/debt-inventory.md"
  DEBT_COUNT=$((DEBT_COUNT + 1))
fi

# Check for separation of concerns
if [ -d "src" ]; then
  if ! [ -d "src/components" ] && ! [ -d "src/services" ] && ! [ -d "src/utils" ]; then
    echo "- **⚠️  No clear component/service separation**" | tee -a "$REPORT_DIR/debt-inventory.md"
    DEBT_COUNT=$((DEBT_COUNT + 1))
  fi
fi

# Check for circular dependencies
echo "- **Circular dependencies**: Checking..." | tee -a "$REPORT_DIR/debt-inventory.md"
# This requires tools like madge for JavaScript
if command -v madge &> /dev/null; then
  madge --circular . > "$REPORT_DIR/circular-deps.txt" 2>&1 || true
  CIRCULAR_COUNT=$(grep -c "Dependency chain" "$REPORT_DIR/circular-deps.txt" 2>/dev/null || echo "0")
  echo "  Found $CIRCULAR_COUNT circular dependency chains" | tee -a "$REPORT_DIR/debt-inventory.md"
  DEBT_COUNT=$((DEBT_COUNT + CIRCULAR_COUNT))
else
  echo "  Install 'madge' for circular dependency detection: npm install -g madge"
fi

echo "" | tee -a "$REPORT_DIR/debt-inventory.md"

# 3. Test Debt
echo "### 3. Test Debt" | tee -a "$REPORT_DIR/debt-inventory.md"
echo "" | tee -a "$REPORT_DIR/debt-inventory.md"

# Files without tests
SRC_FILES=$(find . -type f \( -name "*.js" -o -name "*.ts" \) \
  -not -path "*/node_modules/*" -not -path "*/test/*" -not -path "*/tests/*" \
  -not -name "*.test.*" -not -name "*.spec.*" | wc -l)

TEST_FILES=$(find . -type f \( -name "*.test.*" -o -name "*.spec.*" \) \
  -not -path "*/node_modules/*" | wc -l)

UNTESTED_FILES=$((SRC_FILES - TEST_FILES))
if [ "$UNTESTED_FILES" -gt 0 ]; then
  echo "- **Files without tests**: ~$UNTESTED_FILES" | tee -a "$REPORT_DIR/debt-inventory.md"
  DEBT_COUNT=$((DEBT_COUNT + UNTESTED_FILES))
fi

# Flaky test indicators
SKIP_COUNT=$(grep -r "skip\|xit\|xdescribe" . \
  --include="*.test.*" --include="*.spec.*" \
  --exclude-dir=node_modules | wc -l)
if [ "$SKIP_COUNT" -gt 0 ]; then
  echo "- **Skipped tests**: $SKIP_COUNT" | tee -a "$REPORT_DIR/debt-inventory.md"
  DEBT_COUNT=$((DEBT_COUNT + SKIP_COUNT))
fi

echo "" | tee -a "$REPORT_DIR/debt-inventory.md"

# 4. Documentation Debt
echo "### 4. Documentation Debt" | tee -a "$REPORT_DIR/debt-inventory.md"
echo "" | tee -a "$REPORT_DIR/debt-inventory.md"

# Missing README sections
if [ -f "README.md" ]; then
  if ! grep -q "Installation" README.md; then
    echo "- **⚠️  README missing Installation section**" | tee -a "$REPORT_DIR/debt-inventory.md"
    DEBT_COUNT=$((DEBT_COUNT + 1))
  fi
  if ! grep -q "Usage\|Getting Started" README.md; then
    echo "- **⚠️  README missing Usage section**" | tee -a "$REPORT_DIR/debt-inventory.md"
    DEBT_COUNT=$((DEBT_COUNT + 1))
  fi
else
  echo "- **❌ No README.md**" | tee -a "$REPORT_DIR/debt-inventory.md"
  DEBT_COUNT=$((DEBT_COUNT + 5))
fi

# Missing API documentation
if ! [ -d "docs" ]; then
  echo "- **⚠️  No docs/ directory**" | tee -a "$REPORT_DIR/debt-inventory.md"
  DEBT_COUNT=$((DEBT_COUNT + 1))
fi

# Missing inline documentation
JSDOC_COUNT=$(grep -r "^\s*/\*\*" . \
  --include="*.js" --include="*.ts" --exclude-dir=node_modules | wc -l)
if [ "$JSDOC_COUNT" -lt 10 ]; then
  echo "- **⚠️  Minimal inline documentation** ($JSDOC_COUNT JSDoc comments)" | tee -a "$REPORT_DIR/debt-inventory.md"
  DEBT_COUNT=$((DEBT_COUNT + 2))
fi

echo "" | tee -a "$REPORT_DIR/debt-inventory.md"

# 5. Dependency Debt
echo "### 5. Dependency Debt" | tee -a "$REPORT_DIR/debt-inventory.md"
echo "" | tee -a "$REPORT_DIR/debt-inventory.md"

if [ -f "package.json" ]; then
  # Outdated dependencies
  OUTDATED=$(npm outdated --json 2>/dev/null | jq '. | length' 2>/dev/null || echo "0")
  if [ "$OUTDATED" -gt 0 ]; then
    echo "- **Outdated dependencies**: $OUTDATED packages" | tee -a "$REPORT_DIR/debt-inventory.md"
    DEBT_COUNT=$((DEBT_COUNT + OUTDATED))
  fi

  # Check for deprecated packages
  DEPRECATED=$(npm ls --depth=0 2>&1 | grep -c "deprecated" || echo "0")
  if [ "$DEPRECATED" -gt 0 ]; then
    echo "- **Deprecated packages**: $DEPRECATED" | tee -a "$REPORT_DIR/debt-inventory.md"
    DEBT_COUNT=$((DEBT_COUNT + DEPRECATED))
  fi
fi

echo "" | tee -a "$REPORT_DIR/debt-inventory.md"

echo "**Total Debt Items**: $DEBT_COUNT" | tee -a "$REPORT_DIR/debt-inventory.md"
```

### Phase 2: Cost Quantification

Estimate time cost of technical debt:

```bash
echo ""
echo "=== Cost Quantification ==="

# Calculate estimated cost in hours
TODO_COST=$((TODO_COUNT * 2))  # 2 hours per TODO
LARGE_FILE_COST=$((LARGE_FILES * 8))  # 8 hours to refactor large file
UNTESTED_COST=$((UNTESTED_FILES * 4))  # 4 hours to add tests per file
OUTDATED_COST=$((OUTDATED * 1))  # 1 hour to update dependency

TOTAL_COST=$((TODO_COST + LARGE_FILE_COST + UNTESTED_COST + OUTDATED_COST))

cat > "$REPORT_DIR/cost-analysis.md" <<EOF
# Technical Debt Cost Analysis

**Total Estimated Cost**: $TOTAL_COST hours ($(awk "BEGIN {printf \"%.1f\", $TOTAL_COST / 8}") days)

## Cost Breakdown

| Debt Category | Items | Hours per Item | Total Cost |
|---------------|-------|----------------|------------|
| TODO/FIXME comments | $TODO_COUNT | 2h | ${TODO_COST}h |
| Large files | $LARGE_FILES | 8h | ${LARGE_FILE_COST}h |
| Untested files | $UNTESTED_FILES | 4h | ${UNTESTED_COST}h |
| Outdated deps | $OUTDATED | 1h | ${OUTDATED_COST}h |
| **Total** | $DEBT_COUNT | - | **${TOTAL_COST}h** |

## Annual Cost (Maintenance Burden)

Assuming 20% productivity loss due to debt:

- Monthly cost: $(awk "BEGIN {printf \"%.0f\", $TOTAL_COST * 0.2}") hours
- Annual cost: $(awk "BEGIN {printf \"%.0f\", $TOTAL_COST * 0.2 * 12}") hours
- At \$100/hour: \$$(awk "BEGIN {printf \"%.0f\", $TOTAL_COST * 0.2 * 12 * 100}")

EOF

cat "$REPORT_DIR/cost-analysis.md"
```

### Phase 3: Risk Assessment

Assess risk of not addressing each debt item:

```bash
echo ""
echo "=== Risk Assessment ==="

cat > "$REPORT_DIR/risk-assessment.md" <<EOF
# Technical Debt Risk Assessment

## High Risk (Address Immediately)

EOF

# High risk: Large files in critical paths
if [ "$LARGE_FILES" -gt 5 ]; then
  cat >> "$REPORT_DIR/risk-assessment.md" <<EOF
### Large Files
- **Risk**: High complexity makes changes error-prone
- **Impact**: Bugs, slow development, hard to onboard
- **Priority**: HIGH
- **Items**: $LARGE_FILES files > 500 lines

EOF
fi

# High risk: Low test coverage
if [ "$UNTESTED_FILES" -gt "$((SRC_FILES / 2))" ]; then
  cat >> "$REPORT_DIR/risk-assessment.md" <<EOF
### Missing Tests
- **Risk**: Changes break functionality without detection
- **Impact**: Production bugs, customer issues
- **Priority**: HIGH
- **Items**: $UNTESTED_FILES untested files

EOF
fi

cat >> "$REPORT_DIR/risk-assessment.md" <<EOF

## Medium Risk (Address Soon)

EOF

# Medium risk: TODO comments
if [ "$TODO_COUNT" -gt 20 ]; then
  cat >> "$REPORT_DIR/risk-assessment.md" <<EOF
### TODO Comments
- **Risk**: Incomplete features, known issues unfixed
- **Impact**: Technical debt accumulates
- **Priority**: MEDIUM
- **Items**: $TODO_COUNT TODO/FIXME comments

EOF
fi

# Medium risk: Documentation
if [ ! -f "README.md" ] || [ "$JSDOC_COUNT" -lt 10 ]; then
  cat >> "$REPORT_DIR/risk-assessment.md" <<EOF
### Documentation
- **Risk**: Hard to onboard, knowledge silos
- **Impact**: Slow development, maintenance issues
- **Priority**: MEDIUM
- **Items**: Missing README and inline docs

EOF
fi

cat >> "$REPORT_DIR/risk-assessment.md" <<EOF

## Low Risk (Plan for Future)

### Outdated Dependencies
- **Risk**: Security vulnerabilities, compatibility issues
- **Impact**: May require updates eventually
- **Priority**: LOW (unless security issues)
- **Items**: $OUTDATED outdated packages

EOF

cat "$REPORT_DIR/risk-assessment.md"
```

### Phase 4: Prioritization Matrix

Create prioritized refactoring roadmap:

```bash
echo ""
echo "=== Prioritization & Roadmap ==="

cat > "$REPORT_DIR/refactoring-roadmap.md" <<EOF
# Technical Debt Refactoring Roadmap

## Prioritization Matrix

Items ranked by: **Impact × Urgency / Effort**

### Phase 1: Critical (Next Sprint)

**Goal**: Address high-risk, high-impact debt

EOF

# Priority 1: Critical items
if [ "$LARGE_FILES" -gt 5 ]; then
  cat >> "$REPORT_DIR/refactoring-roadmap.md" <<EOF
#### 1. Refactor Top 3 Largest Files
- **Impact**: HIGH (reduces complexity, improves maintainability)
- **Effort**: 24 hours (3 days)
- **Risk**: HIGH if not addressed
- **ROI**: High

**Action Items**:
- [ ] Identify 3 largest files
- [ ] Break into smaller modules
- [ ] Add unit tests for new modules
- [ ] Refactor incrementally

EOF
fi

if [ "$UNTESTED_FILES" -gt "$((SRC_FILES / 2))" ]; then
  cat >> "$REPORT_DIR/refactoring-roadmap.md" <<EOF
#### 2. Add Tests for Core Modules
- **Impact**: HIGH (prevents production bugs)
- **Effort**: 40 hours (5 days)
- **Risk**: HIGH if not addressed
- **ROI**: Very High

**Action Items**:
- [ ] Identify 10 most critical untested files
- [ ] Write unit tests
- [ ] Achieve 70% coverage minimum
- [ ] Add tests to CI/CD

EOF
fi

cat >> "$REPORT_DIR/refactoring-roadmap.md" <<EOF

### Phase 2: Important (Next Month)

**Goal**: Improve code quality and documentation

EOF

if [ "$TODO_COUNT" -gt 20 ]; then
  cat >> "$REPORT_DIR/refactoring-roadmap.md" <<EOF
#### 3. Resolve TODO/FIXME Comments
- **Impact**: MEDIUM (completes incomplete features)
- **Effort**: $TODO_COST hours
- **Risk**: MEDIUM
- **ROI**: Medium

**Action Items**:
- [ ] Audit all TODO comments
- [ ] Convert to tickets/issues
- [ ] Prioritize by impact
- [ ] Resolve top 20 TODOs

EOF
fi

if [ ! -f "README.md" ] || [ "$JSDOC_COUNT" -lt 10 ]; then
  cat >> "$REPORT_DIR/refactoring-roadmap.md" <<EOF
#### 4. Improve Documentation
- **Impact**: MEDIUM (faster onboarding)
- **Effort**: 16 hours (2 days)
- **Risk**: LOW
- **ROI**: Medium-High

**Action Items**:
- [ ] Write/update README with setup, usage, architecture
- [ ] Add JSDoc to all public APIs
- [ ] Create docs/ directory with guides
- [ ] Document key design decisions

EOF
fi

cat >> "$REPORT_DIR/refactoring-roadmap.md" <<EOF

### Phase 3: Maintenance (Next Quarter)

**Goal**: Long-term quality improvements

#### 5. Update Dependencies
- **Impact**: LOW-MEDIUM (security, features)
- **Effort**: $OUTDATED_COST hours
- **Risk**: LOW
- **ROI**: Low-Medium

**Action Items**:
- [ ] Review npm outdated
- [ ] Update non-breaking changes
- [ ] Test thoroughly
- [ ] Update major versions carefully

#### 6. Reduce Code Duplication
- **Impact**: MEDIUM (DRY principle)
- **Effort**: 20 hours
- **Risk**: LOW
- **ROI**: Medium

**Action Items**:
- [ ] Identify duplicate patterns
- [ ] Extract to shared utilities
- [ ] Update all usage sites
- [ ] Add tests for shared code

---

## Summary

- **Phase 1** (Critical): 64 hours (8 days)
- **Phase 2** (Important): $(($TODO_COST + 16)) hours
- **Phase 3** (Maintenance): $(($OUTDATED_COST + 20)) hours

**Total Refactoring Effort**: $TOTAL_COST hours

## ROI Analysis

Addressing technical debt:
- ✅ Reduces bug rate by ~30%
- ✅ Increases development velocity by ~20%
- ✅ Improves developer satisfaction
- ✅ Easier onboarding for new team members

**Break-even**: ~3-6 months
EOF

cat "$REPORT_DIR/refactoring-roadmap.md"
```

### Phase 5: Generate Final Report

Create comprehensive technical debt report:

```bash
cat > "$REPORT_DIR/final-report.md" <<EOF
# Technical Debt Analysis Report

**Date**: $(date)
**Project**: $(basename $(pwd))
**Analysis ID**: debt-${TIMESTAMP}

## Executive Summary

This analysis identified **$DEBT_COUNT** technical debt items with an estimated **$TOTAL_COST hours** of remediation effort.

### Debt Distribution

- **Code Debt**: $TODO_COUNT TODO comments, $LARGE_FILES large files
- **Architecture Debt**: Moderate (needs review)
- **Test Debt**: $UNTESTED_FILES untested files, $SKIP_COUNT skipped tests
- **Documentation Debt**: $([ ! -f "README.md" ] && echo "Missing README" || echo "README exists")
- **Dependency Debt**: $OUTDATED outdated packages

### Priority Recommendations

1. **Immediate** (< 1 month): Refactor large files, add tests
2. **Short-term** (1-3 months): Resolve TODOs, improve docs
3. **Long-term** (3-6 months): Update dependencies, reduce duplication

## Detailed Reports

1. **Debt Inventory**: \`debt-inventory.md\`
2. **Cost Analysis**: \`cost-analysis.md\`
3. **Risk Assessment**: \`risk-assessment.md\`
4. **Refactoring Roadmap**: \`refactoring-roadmap.md\`

## Next Steps

1. Review prioritized roadmap
2. Add Phase 1 items to sprint backlog
3. Allocate 20% of sprint capacity to debt reduction
4. Re-run analysis quarterly

---

**Report Location**: $REPORT_DIR/
EOF

cat "$REPORT_DIR/final-report.md"

# Update memory bank
cat >> .dev-aid/memory-bank/patterns.md <<EOF

## Technical Debt Analysis - $(date +%Y-%m-%d)

**Total Debt Items**: $DEBT_COUNT
**Estimated Cost**: $TOTAL_COST hours

### High Priority Debt
- Large files: $LARGE_FILES
- Untested files: $UNTESTED_FILES
- TODO comments: $TODO_COUNT

### Remediation Plan
- Phase 1 (Critical): 64 hours
- Phase 2 (Important): $(($TODO_COST + 16)) hours
- Phase 3 (Maintenance): $(($OUTDATED_COST + 20)) hours

**Next Review**: $(date -d "+90 days" +%Y-%m-%d)
EOF

cat >> .dev-aid/memory-bank/decisions.md <<EOF

## Technical Debt Prioritization - $(date +%Y-%m-%d)

### Decision: Focus on Test Coverage and Large File Refactoring

**Rationale**:
- High risk: $UNTESTED_FILES untested files
- High complexity: $LARGE_FILES files > 500 lines
- ROI: Reduces bugs, improves velocity

**Action**: Allocate 20% sprint capacity to debt reduction
**Timeline**: Next 3 sprints
EOF

echo ""
echo "✅ Technical debt analysis complete!"
echo "📄 Full Report: $REPORT_DIR/final-report.md"
echo "🗺️  Roadmap: $REPORT_DIR/refactoring-roadmap.md"
echo "💰 Cost Analysis: $REPORT_DIR/cost-analysis.md"
```

---

## Usage Examples

### Basic Analysis
```bash
/dev-aid-debt-analysis
```

### After Analysis - Create Sprint Tasks
```bash
# Review roadmap
cat .dev-aid/reports/quality/debt-*/refactoring-roadmap.md

# Add Phase 1 items to backlog
# - Refactor 3 largest files
# - Add tests for core modules
```

### Quarterly Debt Review
```bash
# Run analysis every quarter
/dev-aid-debt-analysis

# Compare with previous reports
# Track debt reduction progress
```

---

## Tool Installation

For enhanced analysis:

**JavaScript/TypeScript:**
```bash
npm install -g madge  # Circular dependency detection
```

**Python:**
```bash
pip install radon  # Complexity analysis
```

---

## Success Criteria

Analysis succeeds if:
- ✅ All debt categories identified
- ✅ Cost quantified
- ✅ Risk assessment completed
- ✅ Prioritization matrix created
- ✅ Refactoring roadmap generated
- ✅ Reports saved
- ✅ Memory bank updated

---

**Begin technical debt analysis.**
