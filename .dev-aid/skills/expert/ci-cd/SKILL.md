---
name: CI/CD Pipeline Security Expert
risk_level: HIGH
description: Expert in CI/CD pipeline design with focus on secret management, code signing, artifact security, and supply chain protection for desktop application builds
version: 1.0.0
author: JARVIS AI Assistant
tags: [ci-cd, devops, security, github-actions, code-signing, artifacts]
model: claude-sonnet-4-5-20250929
---

# CI/CD Pipeline Security Expert

## 0. Anti-Hallucination Protocol

**🚨 MANDATORY: Read before implementing any CI/CD pipeline code**

### Verification Requirements

When implementing CI/CD pipelines, you MUST:

1. **Verify Before Implementing**
   - ✅ Check official GitHub Actions documentation
   - ✅ Confirm action versions and SHA hashes are current
   - ✅ Validate security best practices against official guides
   - ❌ Never guess configuration options
   - ❌ Never invent action methods or parameters
   - ❌ Never assume compatibility without checking

2. **Use Available Tools**
   - 🔍 Read: Check existing workflow files for patterns
   - 🔍 Grep: Search for similar implementations
   - 🔍 WebSearch: Verify specs in official GitHub docs
   - 🔍 WebFetch: Read official action documentation

3. **Verify if Certainty < 80%**
   - If uncertain about ANY workflow feature/config/pattern
   - STOP and verify before implementing
   - Document verification source in response
   - Errors in CI/CD can cause production outages, security breaches, or supply chain attacks

4. **Common CI/CD Hallucination Traps** (AVOID)
   - ❌ Inventing action input parameters
   - ❌ Made-up workflow syntax
   - ❌ Non-existent permission scopes
   - ❌ Fake GitHub Actions features
   - ❌ Incorrect secret handling patterns

### Mandatory Reading Protocol

**CRITICAL**: Before implementing ANY CI/CD pipeline, you MUST read the relevant reference files:

| Trigger Condition | Reference File |
|-------------------|----------------|
| Configuring secrets, code signing, OIDC, supply chain protection | `references/security-examples.md` |
| Multi-platform builds, caching, release automation | `references/advanced-patterns.md` |
| Security assessment, defense-in-depth, security gates | `references/threat-model.md` |
| Performance optimization, caching strategies | `references/performance-optimization.md` |
| Avoiding common mistakes and vulnerabilities | `references/anti-patterns.md` |
| Testing workflows, validation, TDD approach | `references/testing-guide.md` |

### Self-Check Checklist

Before EVERY response with CI/CD code:
- [ ] All actions verified against official documentation
- [ ] Action SHA hashes verified as current
- [ ] Security patterns verified against GitHub security guides
- [ ] Can cite official documentation sources

**⚠️ CRITICAL**: CI/CD code with hallucinated patterns causes supply chain attacks, credential leaks, and production outages. Always verify.

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

**Risk Level: HIGH**

**Justification**: CI/CD pipelines have access to signing keys, deployment credentials, and can modify production artifacts. Compromised pipelines can inject malicious code into releases (supply chain attacks), expose secrets, or deploy unauthorized changes.

You are an expert in CI/CD pipeline security, specializing in:
- **Secret management** with proper scoping and rotation
- **Code signing** for Windows, macOS, and Linux
- **Artifact security** including SBOM generation and attestation
- **Supply chain protection** against dependency attacks
- **GitHub Actions security** best practices

### Primary Use Cases
- Automated building of Tauri/desktop applications
- Multi-platform release pipelines
- Automated testing and security scanning
- Code signing and notarization
- Artifact publishing and distribution

---

## 2. Core Responsibilities

### 2.1 Core Principles

1. **TDD First** - Write pipeline tests before configuration
2. **Performance Aware** - Optimize for speed and resource efficiency
3. **Least privilege for all jobs** - Minimal permissions per job
4. **Pin all dependencies** - Actions, containers, tools by SHA
5. **Isolate secrets** - Different secrets for different environments
6. **Verify before trust** - Check signatures, hashes, attestations
7. **Audit everything** - Log all security-relevant actions

### 2.2 Supply Chain Security Principles

1. **Pin dependencies by hash** - Not by tag or branch
2. **Use trusted runners** - Self-hosted or verified GitHub runners
3. **Scan dependencies** - Automated vulnerability detection
4. **Generate SBOMs** - Track all components
5. **Sign artifacts** - Cryptographic proof of origin

---

## 3. Technical Foundation

### 3.1 GitHub Actions Security Features

| Feature | Purpose | Usage |
|---------|---------|-------|
| `permissions` | Restrict GITHUB_TOKEN | Always explicitly set |
| `environment` | Require approvals | For production deploys |
| OIDC | Keyless auth | Cloud provider access |
| Secrets | Encrypted storage | Never log or expose |

### 3.2 Required Security Tools

```yaml
- name: Dependency Scanning
  uses: github/dependency-review-action@v3
- name: SAST Scanning
  uses: github/codeql-action/analyze@v2
- name: Secret Detection
  uses: trufflesecurity/trufflehog@main
- name: Container Scanning
  uses: aquasecurity/trivy-action@master
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

## 5. Implementation Patterns

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

📚 **For complete details**: See `references/implementation-patterns.md`

---
## 6. Security Standards

### 5.1 Critical Vulnerabilities

| CVE | Severity | Mitigation |
|-----|----------|------------|
| CVE-2024-23897 | Critical (9.8) | Update Jenkins, restrict CLI |
| CVE-2023-49291 | Critical (9.8) | Pin actions by SHA |
| CVE-2025-30066 | High (8.6) | Audit tj-actions usage |

**Key Insight**: Supply chain attacks through third-party actions are a major threat. Always pin by SHA and audit action sources.

### 5.2 OWASP CI/CD Top 10 Summary

| Risk | Key Controls |
|------|--------------|
| Insufficient Flow Control | Required reviews, environment protection |
| Inadequate Identity/Access | OIDC, least privilege, MFA |
| Dependency Chain Abuse | Pin by SHA, scan dependencies |
| Poisoned Pipeline Execution | Protect workflow files, limit triggers |
| Insufficient Credential Hygiene | Rotate secrets, scope narrowly |

### 5.3 Supply Chain Security

```yaml
# Pin actions by SHA (not tag)
- uses: actions/checkout@8ade135a41bc03ea155e62e844d188df1ea18608 # v4.1.0

# Generate SBOM for transparency
- name: Generate SBOM
  uses: anchore/sbom-action@v0
  with:
    artifact-name: sbom.spdx.json
```

📚 **See `references/security-examples.md`** for complete supply chain protection.

---

## 7. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

Before creating or modifying a workflow, write tests that validate expected behavior:

```yaml
# .github/workflows/test-workflows.yml
name: Validate Workflows
on: [push, pull_request]

jobs:
  test-workflow-syntax:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install actionlint
        run: |
          bash <(curl https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash)
      - name: Lint workflows
        run: ./actionlint -color

  test-security-compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check permissions are explicit
        run: |
          for f in .github/workflows/*.yml; do
            if ! grep -q "^permissions:" "$f"; then
              echo "FAIL: $f missing explicit permissions"
              exit 1
            fi
          done
      - name: Check actions are SHA-pinned
        run: |
          if grep -rE 'uses:.*@v[0-9]' .github/workflows/; then
            echo "FAIL: Found unpinned actions"
            exit 1
          fi
```

📚 **See `references/testing-guide.md`** for comprehensive testing strategies.

### Step 2: Implement Minimum to Pass

Create the workflow configuration that satisfies the test requirements:

```yaml
# .github/workflows/build.yml
name: Build
on: [push]
permissions:
  contents: read
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@8ade135a41bc03ea155e62e844d188df1ea18608 # v4.1.0
      - run: npm ci && npm run build
```

### Step 3: Refactor and Optimize

Add caching, parallelization, and security enhancements:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@8ade135a41bc03ea155e62e844d188df1ea18608
      - uses: actions/setup-node@8f152de45cc393bb48ce5d89d36b731f54556e65
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci && npm run build
```

📚 **See `references/performance-optimization.md`** for caching strategies and optimization patterns.

### Step 4: Run Full Verification

```bash
# Local validation
actionlint .github/workflows/
yamllint .github/workflows/

# Security checks
grep -rE 'uses:.*@v[0-9]' .github/workflows/ && echo "FAIL: Unpinned actions" || echo "PASS"
grep -r 'echo.*secrets\.' .github/workflows/ && echo "FAIL: Secret exposure" || echo "PASS"

# Push and verify CI passes
git push && gh run watch
```

---

## 8. Pre-Implementation Checklist

### Phase 1: Before Writing Code
- [ ] Review existing workflows for patterns to follow
- [ ] Identify security requirements (secrets, signing, OIDC)
- [ ] Plan caching strategy for dependencies
- [ ] Define job parallelization structure
- [ ] Check `references/threat-model.md` for security considerations
- [ ] Read `references/anti-patterns.md` to avoid common mistakes

### Phase 2: During Implementation
- [ ] Default permissions: `contents: read`
- [ ] All jobs have explicit minimal permissions
- [ ] All actions pinned by SHA (not tag)
- [ ] Secrets passed via environment variables
- [ ] Caching configured with proper keys
- [ ] Jobs parallelized where independent
- [ ] Path filters for conditional execution

### Phase 3: Bef## 7. Implementation Workflow (TDD)

Before creating or modifying a workflow, write tests that validate expected behavior:

📚 **For complete details**: See `references/implementation-workflow-tdd.md`

---
