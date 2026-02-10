---
name: cicd-expert
version: 2.0.0
description: "CI/CD pipeline design for GitHub Actions and GitLab CI with security gates, caching, artifact management, and deployment strategies. Use when creating workflows, optimizing build pipelines, adding security scanning steps, or configuring deployment environments. Do NOT use for ArgoCD GitOps delivery (use argo-expert) or desktop app code signing pipelines (use ci-cd)."
compatibility: "GitHub Actions or GitLab CI"
risk_level: MEDIUM
---

# Cicd Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-798: Hardcoded Secrets**
- NEVER: Secrets in pipeline files, environment in logs
- ALWAYS: Secret management (Vault, GitHub Secrets), mask in logs

**CWE-829: Untrusted Dependencies**
- NEVER: Pull dependencies without verification
- ALWAYS: Lock files, checksum verification, dependency scanning

**CWE-94: Code Injection in Pipelines**
- NEVER: `run: ${{ github.event.issue.title }}` - user input in commands
- ALWAYS: Sanitize inputs, use intermediate environment variables

**CWE-250: Excessive Pipeline Permissions**
- NEVER: Full repo/admin access for all jobs
- ALWAYS: Minimal permissions per job, OIDC for cloud auth

### 0.3 Risk Level: MEDIUM

**Verification requirements for MEDIUM risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 Data ≠ Code (CWE-94, CWE-78, CWE-89)

**Principle:** Never construct executable code/commands/queries from untrusted data via string operations.

```yaml
# ❌ WRONG - Secrets in plain text
apiVersion: v1
kind: Secret
data:
  password: plaintext-password

# ✅ CORRECT - Use sealed secrets or external secrets
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
spec:
  encryptedData:
    password: AgBy8hCi...
```

### 1.2 Input Validation (CWE-20)

**Principle:** Validate all input at trust boundaries. Allowlist > Denylist. Reject by default.

```yaml
# ❌ WRONG - No resource limits
containers:
  - name: app
    image: myapp

# ✅ CORRECT - Resource limits set
containers:
  - name: app
    image: myapp
    resources:
      limits:
        memory: "128Mi"
        cpu: "500m"
```

### 1.3 Secrets ≠ Code (CWE-798)

**Principle:** Never hardcode secrets. Use environment/vault. Never log secrets.

```yaml
# ❌ WRONG - Hardcoded secrets
env:
  - name: API_KEY
    value: "sk-1234567890"

# ✅ CORRECT - From secret reference
env:
  - name: API_KEY
    valueFrom:
      secretKeyRef:
        name: api-secrets
        key: api-key
```

### 1.4 Fail Secure (CWE-636)

**Principle:** Default deny. On error, deny access. Never fail open.

### 1.5 Least Privilege (CWE-250)

**Principle:** Minimum permissions needed. Drop privileges when possible.

### 1.6 Defense in Depth

**Principle:** Multiple security layers. Don't rely on single control.

---

## 2. Version Requirements

**ALWAYS use current stable versions. Check for security advisories before use.**

```
20
20
```

---

## 3. Code Patterns

### 3.1 WHEN creating GitHub Actions workflow

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read  # Least privilege

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci  # Use ci, not install

      - name: Security audit
        run: npm audit --audit-level=high

      - name: Lint
        run: npm run lint

      - name: Test
        run: npm test

      - name: Build
        run: npm run build

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy
        env:
          # Secrets from GitHub Secrets, never hardcoded
          API_KEY: ${{ secrets.API_KEY }}
        run: ./deploy.sh
```

### 3.2 WHEN handling secrets in pipelines

```yaml
# ❌ WRONG - Secret in workflow file
env:
  API_KEY: "sk-1234567890"

# ✅ CORRECT - From GitHub Secrets
env:
  API_KEY: ${{ secrets.API_KEY }}

# ✅ CORRECT - Mask secrets in logs
- name: Use secret
  run: |
    echo "::add-mask::${{ secrets.API_KEY }}"
    ./script.sh
```

### 3.3 WHEN running security scans

```yaml
security:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    # SAST
    - name: Run Semgrep
      uses: returntocorp/semgrep-action@v1
      with:
        config: auto

    # Dependency scanning
    - name: Run Trivy
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        severity: 'CRITICAL,HIGH'
        exit-code: '1'

    # Secret scanning
    - name: Run Gitleaks
      uses: gitleaks/gitleaks-action@v2
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## 4. Anti-Patterns

**NEVER:**
- Construct code from untrusted data
- Skip input validation
- Hardcode secrets
- Fail open on errors
- Use deprecated/vulnerable dependencies

---

## 5. Testing

**ALWAYS write security tests before implementation.**

Test coverage requirements:
- [ ] Input validation tests
- [ ] Authorization tests
- [ ] Error handling tests (no info leakage)
- [ ] Edge cases (null, empty, boundary)

---

## 6. Pre-Generation Checklist

**BEFORE generating any code:**

- [ ] Data ≠ Code: No string concatenation for queries/commands
- [ ] Input validation: All external input validated
- [ ] Secrets: From environment, never hardcoded
- [ ] Error handling: Fail secure, no sensitive data in errors
- [ ] Dependencies: Using secure versions

**Templates**: See `assets/` for reusable output templates.

---

**Performance**: Quality over speed. Verify all code examples compile. Never skip security checks. See `template-references/performance-notes.md` for full guidelines.