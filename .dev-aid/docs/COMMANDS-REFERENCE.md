# Dev-AID Slash Commands Reference

Complete guide to all available slash commands in Dev-AID.

---

## 📋 Built-in Commands

### Setup & Analysis

#### `/dev-aid-analyze`
**Category:** Setup
**Purpose:** Analyze codebase and generate adaptation plan
**When to use:** After installation, when adding Dev-AID to existing project
**Output:**
- `.dev-aid/analysis/adaptation-plan.md`
- `.dev-aid/analysis/quick-start-checklist.md`

**Example:**
```
/dev-aid-analyze
```

#### `/dev-aid-status`
**Category:** Setup
**Purpose:** Show current Dev-AID configuration and setup status
**When to use:** After installation, troubleshooting, regular checkups
**Output:** Console display of configuration, providers, context files, memory bank status

**Example:**
```
/dev-aid-status
```

#### `/generate-ci` (Script)
**Category:** Automation
**Purpose:** Auto-generate production-ready CI/CD workflows
**When to use:** Setting up CI/CD, migrating projects, adding automation
**Output:** `.github/workflows/ci.yml`
**Supported:** Python, Node.js, Java, Go, Rust, C#, PHP, Ruby, C++

**Example:**
```bash
# Auto-detect and generate
./.dev-aid/scripts/generate-ci.sh

# Custom output location
./.dev-aid/scripts/generate-ci.sh -o .github/workflows/custom.yml
```

**Documentation:** See [CI-GENERATOR-GUIDE.md](./CI-GENERATOR-GUIDE.md)

---

## 🎓 Recommended Commands from Other Repos

These commands are available in claude-code-tresor and can be added to Dev-AID:

### Security Commands

#### `/audit`
**Purpose:** Comprehensive security audit
**Phases:** 3-4 phases with multiple agents
**Coverage:** Code, dependencies, configuration, secrets
**How to add:** Copy from `claude-code-tresor/commands/security/audit/`

#### `/vulnerability-scan`
**Purpose:** Scan for known vulnerabilities
**Checks:** Dependencies, code patterns, CVEs
**How to add:** Copy from `claude-code-tresor/commands/security/vulnerability-scan/`

#### `/compliance-check`
**Purpose:** Verify compliance (GDPR, SOC2, etc.)
**How to add:** Copy from `claude-code-tresor/commands/security/compliance-check/`

### Performance Commands

#### `/profile`
**Purpose:** Performance profiling
**Analyzes:** CPU, memory, I/O bottlenecks
**How to add:** Copy from `claude-code-tresor/commands/performance/profile/`

#### `/benchmark`
**Purpose:** Run benchmarking tests
**How to add:** Copy from `claude-code-tresor/commands/performance/benchmark/`

### Operations Commands

#### `/deploy-validate`
**Purpose:** Pre-deployment validation
**Checks:** Tests, linting, security, dependencies
**How to add:** Copy from `claude-code-tresor/commands/operations/deploy-validate/`

#### `/health-check`
**Purpose:** System health monitoring
**How to add:** Copy from `claude-code-tresor/commands/operations/health-check/`

#### `/incident-response`
**Purpose:** Incident management workflow
**How to add:** Copy from `claude-code-tresor/commands/operations/incident-response/`

### Quality Commands

#### `/code-health`
**Purpose:** Code quality assessment
**Metrics:** Complexity, duplication, coverage
**How to add:** Copy from `claude-code-tresor/commands/quality/code-health/`

#### `/debt-analysis`
**Purpose:** Technical debt analysis
**How to add:** Copy from `claude-code-tresor/commands/quality/debt-analysis/`

---

## 🛠️ Creating Custom Commands

### Template for New Command

Create: `.dev-aid/providers/claude/.claude/commands/[category]/[command-name].md`

```markdown
---
name: my-command
description: Brief description
category: category-name
author: Your Name
version: 1.0.0
---

# Command Name

Your command instructions here...

## Purpose
What this command does

## Usage
How to use it

## Output
What it produces
```

### Example: Custom Test Command

```markdown
---
name: run-tests
description: Run all tests with coverage
category: testing
author: Dev Team
version: 1.0.0
---

# Run Tests with Coverage

Run the full test suite with coverage reporting.

## Steps
1. Run unit tests
2. Run integration tests
3. Generate coverage report
4. Check coverage threshold (80%)

## Output
- Test results
- Coverage report in `.dev-aid/reports/coverage/`
```

---

## 📚 How-To Guides for Developers

### Quick Start: Using Slash Commands

**Step 1: Discover available commands**
```bash
# In Claude Code, type:
/
# This shows autocomplete of available commands
```

**Step 2: Run a command**
```bash
/dev-aid-analyze
```

**Step 3: Review output**
```bash
cat .dev-aid/analysis/adaptation-plan.md
```

### Adding Commands from Tresor

**Option 1: Copy Individual Command**
```bash
# Copy command file
cp claude-code-tresor/commands/security/audit/audit.md \
   dev-aid/.dev-aid/providers/claude/.claude/commands/security/

# Test it
/audit
```

**Option 2: Copy Entire Category**
```bash
# Copy all security commands
cp -r claude-code-tresor/commands/security/ \
   dev-aid/.dev-aid/providers/claude/.claude/commands/

# Now you have: /audit, /vulnerability-scan, /compliance-check
```

### Customizing Commands for Your Project

**Example: Customize /audit for your stack**

1. Copy the command:
```bash
cp claude-code-tresor/commands/security/audit/audit.md \
   dev-aid/.dev-aid/providers/claude/.claude/commands/security/
```

2. Edit for your needs:
```bash
vim dev-aid/.dev-aid/providers/claude/.claude/commands/security/audit.md
```

3. Add project-specific checks:
```markdown
## Custom Checks for Our Project
- Check Stripe API key rotation (every 90 days)
- Verify AWS IAM policies
- Scan for exposed Redis ports
```

---

## 🎯 Recommended Command Workflow

### For New Projects

**Week 1: Setup**
```bash
/dev-aid-analyze              # Understand codebase
/dev-aid-status               # Verify configuration
# Review adaptation plan
# Implement Phase 1 recommendations
```

**Week 2: Quality**
```bash
/code-health              # Assess code quality
/debt-analysis            # Identify tech debt
# Address critical issues
```

**Week 3: Security**
```bash
/audit                    # Security audit
/vulnerability-scan       # Check dependencies
# Fix security issues
```

**Week 4: Performance**
```bash
/profile                  # Find bottlenecks
/benchmark                # Baseline performance
# Optimize critical paths
```

### For Production Projects

**Before Deployment**
```bash
/deploy-validate          # Pre-deployment checks
# Fix any issues
# Deploy
```

**After Deployment**
```bash
/health-check             # Verify system health
# Monitor for 24 hours
```

**Monthly Maintenance**
```bash
/vulnerability-scan       # Security updates
/code-health              # Code quality
/debt-analysis            # Tech debt review
```

---

## 🔗 Command Chaining

You can chain commands for workflows:

**Example: Full Quality Check**
```bash
# Run multiple checks
/code-health
/debt-analysis
/audit
/vulnerability-scan

# Then review all reports
cat .dev-aid/reports/code-health.md
cat .dev-aid/reports/debt-analysis.md
cat .dev-aid/reports/audit.md
cat .dev-aid/reports/vulnerabilities.md
```

---

## 📊 Command Categories

| Category | Commands Available | Purpose |
|----------|-------------------|---------|
| **Setup** | `/dev-aid-analyze`, `/dev-aid-status` | Initial setup, analysis, configuration visibility |
| **Security** | `/audit`, `/vulnerability-scan`, `/compliance-check` | Security operations |
| **Performance** | `/profile`, `/benchmark` | Performance analysis |
| **Operations** | `/deploy-validate`, `/health-check`, `/incident-response` | DevOps workflows |
| **Quality** | `/code-health`, `/debt-analysis` | Code quality |
| **Testing** | (custom) | Test execution |
| **Documentation** | (custom) | Doc generation |

---

## 💡 Best Practices

### 1. Use Commands Consistently
- Run `/code-health` weekly
- Run `/audit` monthly
- Run `/deploy-validate` before every deploy

### 2. Automate with CI/CD
```yaml
# .github/workflows/quality.yml
jobs:
  quality-check:
    runs-on: ubuntu-latest
    steps:
      - name: Code health check
        run: claude run /code-health

      - name: Security audit
        run: claude run /audit
```

### 3. Review and Act on Reports
- Don't just run commands - review outputs
- Track metrics over time
- Set quality gates

### 4. Customize for Your Needs
- Adapt commands to your tech stack
- Add project-specific checks
- Remove irrelevant checks

---

## 🛠️ Utility Scripts

Dev-AID provides standalone utility scripts for common development tasks:

### CI/CD Automation

#### `generate-ci.sh`
**Purpose:** Auto-generate GitHub Actions workflows
**Location:** `.dev-aid/scripts/generate-ci.sh`
**Detects:** Node.js, Python, Rust, Go projects
**Features:**
- Auto-detects package managers (npm/yarn/pnpm/bun, pip/poetry/uv, cargo)
- Security by default (Gitleaks + Trivy included)
- Docker support with image scanning
**Usage:**
```bash
.dev-aid/scripts/generate-ci.sh
.dev-aid/scripts/generate-ci.sh -o custom-workflow.yml
```

### Architecture & Visualization

#### `map-architecture.sh`
**Purpose:** Generate Mermaid.js architecture diagrams
**Location:** `.dev-aid/scripts/map-architecture.sh`
**Generates:**
- Class diagrams (OOP structure)
- Module dependency graphs
- C4 component diagrams
**Usage:**
```bash
.dev-aid/scripts/map-architecture.sh
.dev-aid/scripts/map-architecture.sh src/ -t class
.dev-aid/scripts/map-architecture.sh -o docs/my-diagram.md
```

### Testing & Data

#### `fabricate-data.sh`
**Purpose:** Generate realistic mock test data
**Location:** `.dev-aid/scripts/fabricate-data.sh`
**Supports:** JSON Schema, Pydantic, TypeScript interfaces
**Formats:** JSON, CSV, SQL
**Usage:**
```bash
.dev-aid/scripts/fabricate-data.sh schema.json
.dev-aid/scripts/fabricate-data.sh model.py -c 100 -f csv
.dev-aid/scripts/fabricate-data.sh schema.json -f sql -o data.sql
```

### Documentation

#### `sync-docs.sh`
**Purpose:** Detect documentation drift
**Location:** `.dev-aid/scripts/sync-docs.sh`
**Checks:** Package managers, scripts, Docker ports
**Usage:**
```bash
.dev-aid/scripts/sync-docs.sh
.dev-aid/scripts/sync-docs.sh --readme CONTRIBUTING.md
```

### Productivity

#### `dev-aid-guide.sh`
**Purpose:** Interactive feature discovery
**Location:** `.dev-aid/scripts/dev-aid-guide.sh`
**Features:** Menu-driven, best practices, command catalog
**Usage:**
```bash
.dev-aid/scripts/dev-aid-guide.sh
```

#### `draft-pr.sh`
**Purpose:** Generate PR descriptions from git diff
**Location:** `.dev-aid/scripts/draft-pr.sh`
**Usage:**
```bash
.dev-aid/scripts/draft-pr.sh > pr-description.md
```

#### `onboard.sh`
**Purpose:** Onboard new developers
**Location:** `.dev-aid/scripts/onboard.sh`
**Features:** Environment checks, project detection, setup guide
**Usage:**
```bash
.dev-aid/scripts/onboard.sh
```

---

## 🚀 Next Steps

1. **Try the built-in commands:**
   ```bash
   /dev-aid-analyze    # Analyze codebase
   /dev-aid-status     # Check configuration
   ```

2. **Add recommended commands from Tresor:**
   ```bash
   # Add security commands
   cp -r claude-code-tresor/commands/security/ \
      dev-aid/.dev-aid/providers/claude/.claude/commands/
   ```

3. **Create your first custom command:**
   ```bash
   vim dev-aid/.dev-aid/providers/claude/.claude/commands/testing/run-all-tests.md
   ```

4. **Set up CI/CD integration:**
   - Add commands to your GitHub Actions
   - Set quality gates
   - Automate reports

---

## 📖 Additional Resources

- [Dev-AID Style Guide](./DEV-AID-STYLE-GUIDE.md)
- [Claude Code Tresor Commands](../../../../../../claude-code-tresor/commands/)
- [Creating Custom Commands Guide](./CUSTOM-COMMANDS.md)

---

**Last Updated:** 2025-12-06
**Version:** 1.2.0
