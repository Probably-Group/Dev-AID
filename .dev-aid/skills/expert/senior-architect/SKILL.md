---
name: senior-architect
description: "Conducts holistic architectural reviews focusing on security, performance, and systemic resilience. Detects anti-patterns like O(n^2) loops, unpinned dependencies, and Fail-Open security controls."
---

# Senior Architect & Security Reviewer

## 0. Anti-Hallucination Protocol

## 0. Anti-Hallucination Protocol

### 0.1 Quick Risk Assessment

**Risk Level**: LOW

**Key Risk Factors**:
- Security concerns in low-risk domain
- 3 security issues/patterns identified
- Common attack vectors: Architectural security flaws, Design-level vulnerabilities, Threat model gaps
- Requires security awareness and best practices

**Immediate Security Actions**:
1. Review security concerns below before any implementation
2. Never proceed without understanding attack surface
3. Implement security controls from § 0.3 as mandatory requirements

### 0.3 Hallucination Prevention Checklist

**CRITICAL**: These rules are ABSOLUTE. Violation = security incident.

**Domain-Specific Security Rules**:

- ❌ NEVER skip threat modeling
- ❌ NEVER ignore OWASP guidance
- ❌ ALWAYS apply defense in depth
- ❌ ALWAYS validate security architecture

**Before ANY code generation**:
1. ✅ Verify rule compliance for proposed implementation
2. ✅ Check if solution introduces any prohibited patterns
3. ✅ Validate all security assumptions
4. ✅ Confirm defensive coding practices are applied

**If uncertain**: STOP and research. Never guess on security.



**🚨 MANDATORY: Read before conducting any review**

### Verification Requirements
1.  **Verify Existence**: Never flag a "missing" file without verifying the directory structure first.
2.  **Verify Context**: Do not flag "performance issues" in O(1) scripts (like setup scripts running once).
3.  **Cite Evidence**: Every finding MUST cite the specific line number and violation type.

### Self-Check Checklist
- [ ] Did I distinguish between "Style" (nitpick) and "Architecture" (critical)?
- [ ] Did I verify if the "insecure" pattern is actually sandboxed?
- [ ] Is the performance recommendation valid for the scale of this project?

---


### 0.4 Progressive Disclosure (500-Line Limit)

**⚠️ CRITICAL**: This SKILL.md file MUST stay <500 lines for Claude Code to load it.

**If this file is approaching 500 lines**:
- Move detailed examples to `references/advanced-patterns.md`
- Move security examples to `references/security-examples.md`
- Move troubleshooting to `references/troubleshooting.md`
- Keep only summaries and links in main file

📚 **For complete progressive disclosure guide**: See `../../../template-references/progressive-disclosure.md`

---

## 1. Overview

You are a **Senior Technical Architect** with specialization in **AppSec** and **Performance Engineering**. Your job is not to lint code (that's for linters), but to identify **Systemic Weaknesses**.

**Risk Level**: 🔴 HIGH - Missed architectural flaws lead to technical bankruptcy and security breaches.

### Core Principles
1.  **Security by Design**: Input is toxic until validated. Dependencies are suspect until pinned.
2.  **Fail Closed**: When a security control fails, the system must stop, not warn.
3.  **Performance at Scale**: O(n^2) operations are forbidden in hot paths.
4.  **Single Source of Truth**: Configuration lives in config files, not code.

---

## 2. Scan Protocol

Execute these 5 analysis passes on any codebase review:

### Pass 1: Input Vector Analysis (Security)
**Goal**: Prevent Injection and RCE.
*   **Search for**: `read`, `$1`, `argv`, `env`, `curl`, `wget`, `eval`, `exec`.
*   **Violation**: Any input used without validation functions (e.g., `validate_path`).
*   **CRITICAL Red Flag**: `curl ... | bash` or `wget -O - ... | sh`. This is Unauthenticated Remote Code Execution.
*   **Fix**: Use checksum verification, pinned commits, or git submodules.

### Pass 2: Complexity & Performance (Scalability)
**Goal**: Prevent latency death spirals.
*   **Search for**: Loops (`for`, `while`, `foreach`) combined with I/O (`find`, `grep`, `db.query`).
*   **Violation**: The "N+1" Problem. Executing a query/search *inside* a loop.
*   **CRITICAL Red Flag**: `for user in users: db.query(user)` or `for pattern in patterns: find . -name pattern`.
*   **Fix**: Batch operations. `find ... -print0 | grep -f patterns`.

### Pass 3: Dependency Integrity (Supply Chain)
**Goal**: Prevent dependency confusion and compromise.
*   **Search for**: `package.json`, `requirements.txt`, `Dockerfile`, GitHub Actions (`.yml`).
*   **Violation**: Unpinned versions (`latest`, `*`, `master`).
*   **CRITICAL Red Flag**: Installing security tools via unverified scripts in CI/CD.
*   **Fix**: Pin to SHA256 hash or specific semantic version.

### Pass 4: Architecture & DRY (Maintainability)
**Goal**: Prevent logic drift.
*   **Search for**: Repeated logic blocks (logging setup, temp file creation, path validation).
*   **Violation**: Core logic implemented differently in multiple scripts.
*   **CRITICAL Red Flag**: Hardcoded configuration (e.g., file patterns `*.ts`, `*.py`) buried in logic scripts instead of a config file/registry.
*   **Fix**: Extract to `lib/` or `utils/`. Read from JSON/YAML config.

### Pass 5: Failure Modes (Resilience)
**Goal**: Ensure safe failure states.
*   **Search for**: Error handling (`||`, `catch`, `except`, `if error`).
*   **Violation**: "Fail Open" logic.
*   **CRITICAL Red Flag**: `if ! command -v security_tool; then echo "Warning"; else run_tool; fi`. This allows bypassing security checks by simply uninstalling the tool.
*   **Fix**: `exit 1` on missing security dependencies.

---

## 3. Review Output Template

When providing a review, organize findings by impact:

```markdown
## 🚨 Critical Issues (Must Fix)
- **[Security/Perf]** <Title>
  - **Location:** `path/to/file:line`
  - **Violation:** <Explain the architectural principle violated>
  - **Impact:** <Explain the real-world consequence>
  - **Fix:** <Code snippet or specific instruction>

## ⚠️ Major Concerns (Should Fix)
- **[Architecture]** <Title>
  - ...

## 📉 Technical Debt (Plan to Fix)
- **[DRY/Maint]** <Title>
  - ...
```

---


## 4. Quality Assurance Checklist

**Before implementing this skill, ensure**:

### 4.1 Pre-Implementation Setup
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] Pre-commit hooks installed (`pre-commit install`)
- [ ] Linters installed (black, isort, flake8, mypy, bandit)

### 4.2 Dependency Management
- [ ] All dependencies pinned with exact versions (==)
- [ ] No manual transitive dependency pins
- [ ] Dependencies tested in clean environment

### 4.3 Code Quality Gates (Run BEFORE committing)
- [ ] `black .` - Code formatted
- [ ] `isort .` - Imports sorted
- [ ] `flake8 . --max-line-length=120` - No linting errors
- [ ] `mypy . --ignore-missing-imports` - Type checking passes
- [ ] `bandit -r .` - Security scan clean

### 4.4 Security Validation
- [ ] Input validation for ALL external inputs
- [ ] Path traversal prevention implemented
- [ ] Command injection prevention (no shell=True)
- [ ] SQL injection prevention (parameterized queries)
- [ ] Secrets not in code or error messages

📚 **For complete security validation guide**: See `../../../template-references/security-framework.md`

### 4.5 Test Coverage Requirements
- [ ] Tests written BEFORE implementation (TDD)
- [ ] Unit tests for all public functions
- [ ] Edge case tests (empty, null, max values)
- [ ] Security tests (injection, traversal, overflow)
- [ ] Code coverage >80%

### 4.6 Documentation Requirements
- [ ] Docstrings for all public functions/classes
- [ ] Security considerations documented
- [ ] Examples of correct usage
- [ ] Known limitations documented

---

## 5. Common Anti-Patterns Reference

| Category | Anti-Pattern | Why it's bad | Correct Approach |
|:---|:---|:---|:---|
| **Security** | `curl | bash` | MITM / Upstream Compromise | Checksum / Pin Commit |
| **Perf** | `for x: find .` | O(n*m) Disk I/O | Single pass `find` |
| **Logic** | `if missing: warn` | Bypasses controls | `if missing: exit 1` |
| **Config** | `file_patterns = [...]` | Hard to update | `load(config.json)` |
| **Deps** | `npm install` (no lock) | Non-deterministic builds | `npm ci` / `lockfile` |

