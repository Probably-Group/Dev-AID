# CI/CD Anti-Patterns and Common Mistakes

This document covers common anti-patterns and mistakes in CI/CD pipelines, with explanations of why they're problematic and how to fix them.

---

## 1. Permission Anti-Patterns

### 1.1 Overly Permissive Tokens

**WRONG - Granting write-all permissions:**
```yaml
permissions: write-all  # DANGEROUS!

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm run build
```

**Why This Is Dangerous**:
- Grants unnecessary write access to repository
- Allows malicious code to modify anything
- Violates principle of least privilege
- Increases attack surface for supply chain attacks

**CORRECT - Minimal permissions:**
```yaml
permissions:
  contents: read  # Only what's needed

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read  # Explicit per-job permissions
    steps:
      - uses: actions/checkout@v4
      - run: npm run build
```

**Best Practice**:
- Always set default `permissions: contents: read`
- Grant additional permissions only to specific jobs that need them
- Document why elevated permissions are needed

### 1.2 Missing Explicit Permissions

**WRONG - Relying on defaults:**
```yaml
name: Build
on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    # No permissions set - inherits defaults (too permissive)
    steps: [...]
```

**Why This Is Dangerous**:
- Default permissions vary by repository settings
- Implicit permissions can change without notice
- Hard to audit what access workflows have

**CORRECT - Explicit permissions:**
```yaml
name: Build
on: [push]

permissions:
  contents: read  # Explicit default

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read  # Explicit per-job
    steps: [...]
```

---

## 2. Dependency Pinning Anti-Patterns

### 2.1 Unpinned Actions (Tags/Branches)

**WRONG - Using tags or branches:**
```yaml
# Tag can be moved to malicious code
- uses: actions/checkout@v4

# Branch can be updated with malicious commits
- uses: actions/checkout@main

# Latest is completely unpredictable
- uses: some-org/some-action@latest
```

**Why This Is Dangerous**:
- Tags and branches are mutable references
- Attacker can move tag to malicious code
- Supply chain attacks via compromised actions
- No guarantee of code integrity

**Attack Scenario**:
1. Popular action `foo/bar@v1` is trusted
2. Attacker compromises action repository
3. Attacker force-pushes malicious code to `v1` tag
4. All workflows using `@v1` now execute malicious code
5. Credentials stolen, artifacts poisoned

**CORRECT - Pin by immutable SHA:**
```yaml
# SHA is immutable - cannot be changed
- uses: actions/checkout@8ade135a41bc03ea155e62e844d188df1ea18608  # v4.1.0

# Include comment with version for readability
- uses: actions/setup-node@8f152de45cc393bb48ce5d89d36b731f54556e65  # v4.0.0
```

**Best Practice**:
- Always pin actions by full SHA (40 characters)
- Add comment with corresponding tag for readability
- Use Dependabot to keep SHAs updated:

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

### 2.2 Unpinned Docker Images

**WRONG - Using latest or tags:**
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    container:
      image: node:latest  # Mutable tag

steps:
  - run: docker run node:20  # Mutable tag
```

**Why This Is Dangerous**:
- Image contents can change
- Breaks reproducibility
- Security vulnerabilities can be introduced
- No way to audit what actually ran

**CORRECT - Pin by SHA digest:**
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    container:
      image: node@sha256:a1b2c3d4e5f6...  # Immutable digest

steps:
  - run: docker run node@sha256:a1b2c3d4e5f6...
```

---

## 3. Secret Handling Anti-Patterns

### 3.1 Secrets in Command Line Arguments

**WRONG - Secret exposed in command:**
```yaml
# Secret appears in logs as command line argument
- run: curl -u user:${{ secrets.TOKEN }} https://api.example.com

# Secret in URL query parameter (logged)
- run: wget https://api.example.com?token=${{ secrets.API_KEY }}

# Secret echoed (appears in logs)
- run: echo "API_KEY=${{ secrets.API_KEY }}"
```

**Why This Is Dangerous**:
- Command line arguments logged by default
- Secrets visible in process listings
- Exposed in debug logs and screenshots
- Can leak in error messages

**Attack Vector**:
- Developer shares workflow run screenshot
- Secret visible in command output
- Attacker uses leaked secret

**CORRECT - Secrets via environment variables:**
```yaml
# Secret passed via env (masked in logs)
- name: Call API
  env:
    TOKEN: ${{ secrets.TOKEN }}
  run: curl -u "user:$TOKEN" https://api.example.com

# Secret in file (deleted after use)
- name: Use secret file
  env:
    API_KEY: ${{ secrets.API_KEY }}
  run: |
    echo "$API_KEY" > /tmp/key
    curl -K /tmp/key https://api.example.com
    rm /tmp/key
```

**Best Practice**:
- Always pass secrets via `env:` variables
- Never use secrets directly in `run:` commands
- Verify logs don't contain `***` masked values
- Use secret scanning tools

### 3.2 Secrets in Pull Request Workflows

**WRONG - Exposing secrets to untrusted code:**
```yaml
on: pull_request  # Runs on untrusted PR code

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build
        env:
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}  # DANGEROUS!
        run: npm ci && npm run build
```

**Why This Is Dangerous**:
- PR can contain malicious code
- `npm run build` executes untrusted scripts
- Scripts can exfiltrate `NPM_TOKEN`
- Attacker gains access to private npm packages

**Attack Scenario**:
1. Attacker submits PR with malicious `package.json`
2. Workflow runs with `NPM_TOKEN` secret
3. Malicious script exfiltrates token
4. Attacker publishes malicious packages to npm

**CORRECT - Don't expose secrets to PR builds:**
```yaml
on: pull_request

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci --ignore-scripts  # Disable scripts
      - run: npm run build
    # NO SECRETS - PR builds don't need them
```

---

## 4. pull_request_target Anti-Pattern

### 4.1 Unsafe pull_request_target with Untrusted Checkout

**DANGEROUS - Common but critically flawed pattern:**
```yaml
on:
  pull_request_target:  # Runs with write access!

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      # DANGEROUS: Checking out untrusted PR code
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}  # Untrusted code!

      - name: Build
        env:
          DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}  # Exposed to untrusted code!
        run: npm ci && npm run build
```

**Why This Is Critical**:
- `pull_request_target` has write access to repository
- Checks out PR code (untrusted)
- Exposes secrets to untrusted code
- `npm ci` runs install scripts from PR
- Malicious scripts can steal `DEPLOY_TOKEN`

**Attack Scenario**:
1. Attacker submits PR with malicious `package.json`
2. Workflow runs with write access and secrets
3. Malicious install script:
   - Steals `DEPLOY_TOKEN`
   - Pushes malicious code to main branch
   - Modifies workflow files
4. Complete repository compromise

**CORRECT - Safe pull_request_target usage:**
```yaml
on:
  pull_request_target:

jobs:
  # Only use pull_request_target for commenting, labeling
  comment:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write  # Only what's needed
      contents: read
    steps:
      # Don't checkout PR code - use base branch
      - uses: actions/checkout@v4

      # Safe operation - no untrusted code execution
      - name: Add comment
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: 'Thanks for the PR!'
            })
```

**Best Practice**:
- **Never** checkout PR code with `pull_request_target`
- **Never** expose secrets with `pull_request_target`
- Use `pull_request_target` only for:
  - Commenting on PRs
  - Labeling PRs
  - Reading PR metadata
- For building/testing PRs, use `pull_request` (no secrets)

---

## 5. Trust Boundary Anti-Patterns

### 5.1 Running Untrusted Code with Secrets

**WRONG - Installing dependencies from untrusted source:**
```yaml
on: [pull_request]

jobs:
  build:
    steps:
      - uses: actions/checkout@v4
      - env:
          AWS_SECRET: ${{ secrets.AWS_SECRET }}
        run: |
          npm ci  # Runs install scripts from potentially malicious package.json
          npm run build
```

**Why This Is Dangerous**:
- `npm ci` executes `preinstall`/`postinstall` scripts
- PR can modify `package.json` to add malicious dependencies
- Scripts run with full access to `AWS_SECRET`

**CORRECT - Isolate untrusted code:**
```yaml
on: [pull_request]

jobs:
  build:
    steps:
      - uses: actions/checkout@v4
      # NO SECRETS in job that runs untrusted code
      - run: npm ci --ignore-scripts
      - run: npm run build

  deploy:
    needs: build
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    environment: production  # Requires approval
    steps:
      - uses: actions/checkout@v4
      - env:
          AWS_SECRET: ${{ secrets.AWS_SECRET }}
        run: npm run deploy  # Only on trusted main branch
```

---

## 6. Caching Anti-Patterns

### 6.1 Overly Broad Cache Keys

**WRONG - Cache key that never invalidates:**
```yaml
- uses: actions/cache@v4
  with:
    path: node_modules
    key: ${{ runner.os }}-deps  # No hash - never invalidates!
```

**Why This Fails**:
- Cache never invalidates when dependencies change
- Builds use stale dependencies
- Security updates not applied
- Hard-to-debug version mismatches

**CORRECT - Include dependency hash:**
```yaml
- uses: actions/cache@v4
  with:
    path: node_modules
    key: ${{ runner.os }}-deps-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-deps-
```

### 6.2 Caching Secrets or Credentials

**WRONG - Caching sensitive files:**
```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.aws  # Contains credentials!
      ~/.docker  # Contains auth tokens!
      .env  # Contains secrets!
    key: ${{ runner.os }}-config
```

**Why This Is Dangerous**:
- Caches are accessible to all workflow runs
- Secrets persist beyond secret rotation
- Can be accessed from forked PRs
- Violates secret management best practices

**CORRECT - Never cache credentials:**
```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cargo/registry
      target/
    key: ${{ runner.os }}-cargo-${{ hashFiles('Cargo.lock') }}
  # Explicitly exclude credential directories
```

---

## 7. Workflow Trigger Anti-Patterns

### 7.1 Overly Broad Workflow Triggers

**WRONG - Trigger on every event:**
```yaml
on:
  - push
  - pull_request
  - schedule
  - workflow_dispatch
  # Runs on ALL branches, ALL paths, ALL events

jobs:
  expensive-e2e-tests:  # 30 minute job
    runs-on: ubuntu-latest
```

**Why This Wastes Resources**:
- E2E tests run on documentation changes
- Tests run on feature branches
- Massive CI minute usage
- Slow feedback for developers

**CORRECT - Targeted triggers:**
```yaml
on:
  push:
    branches: [main, develop]  # Only important branches
    paths:
      - 'src/**'
      - 'tests/**'
      - '!**/*.md'  # Exclude documentation
  pull_request:
    types: [opened, synchronize, reopened]
    paths:
      - 'src/**'
      - 'tests/**'

jobs:
  expensive-e2e-tests:
    runs-on: ubuntu-latest
```

---

## 8. Container Security Anti-Patterns

### 8.1 Running Containers as Root

**WRONG - Default root user:**
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    container:
      image: node:20
      # Runs as root by default - DANGEROUS
    steps:
      - run: npm install -g some-package  # Runs as root
```

**Why This Is Dangerous**:
- Malicious packages can modify system
- Escape container to runner
- Privilege escalation attacks

**CORRECT - Non-root user:**
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    container:
      image: node:20
      options: --user 1001:1001  # Non-root user
    steps:
      - run: npm install  # Runs as non-root
```

---

## 9. Artifact Anti-Patterns

### 9.1 Uploading Secrets in Artifacts

**WRONG - Artifacts containing secrets:**
```yaml
- name: Build
  run: npm run build  # Bundles .env file

- uses: actions/upload-artifact@v4
  with:
    name: build
    path: dist/  # Contains bundled .env with secrets!
```

**Why This Is Dangerous**:
- Artifacts accessible to all with repo access
- Secrets persist beyond rotation
- Can be downloaded by anyone with artifact link

**CORRECT - Exclude secrets from artifacts:**
```yaml
- name: Build
  run: npm run build

- name: Remove secrets before upload
  run: |
    find dist/ -name '.env*' -delete
    find dist/ -name '*credentials*' -delete

- uses: actions/upload-artifact@v4
  with:
    name: build
    path: dist/
```

---

## 10. Code Signing Anti-Patterns

### 10.1 Leaving Certificates in Repository

**WRONG - Certificate file committed:**
```yaml
# Certificate file committed to repository
- name: Import certificate
  run: |
    Import-PfxCertificate -FilePath ./certs/signing-cert.pfx  # In repo!
```

**Why This Is Dangerous**:
- Certificate and private key in version control
- Accessible to all with repo access
- Cannot be rotated without breaking history
- Violates secret management policies

**CORRECT - Certificate from secrets:**
```yaml
- name: Import certificate
  env:
    CERTIFICATE_BASE64: ${{ secrets.WINDOWS_CERTIFICATE }}
    CERTIFICATE_PASSWORD: ${{ secrets.WINDOWS_CERTIFICATE_PASSWORD }}
  run: |
    $certBytes = [Convert]::FromBase64String($env:CERTIFICATE_BASE64)
    $certPath = Join-Path $env:RUNNER_TEMP "certificate.pfx"
    [IO.File]::WriteAllBytes($certPath, $certBytes)
    Import-PfxCertificate -FilePath $certPath -CertStoreLocation Cert:\CurrentUser\My
    Remove-Item $certPath  # Clean up immediately
```

### 10.2 Not Cleaning Up Imported Certificates

**WRONG - Certificate remains in keychain:**
```yaml
- name: Import Apple certificate
  run: |
    security import certificate.p12 -k build.keychain
    # Keychain remains for subsequent jobs!
```

**Why This Is Dangerous**:
- Certificate accessible to later jobs
- Persists on self-hosted runners
- Can be extracted by malicious code

**CORRECT - Clean up after use:**
```yaml
- name: Import certificate
  run: |
    security create-keychain -p "$KEYCHAIN_PASSWORD" build.keychain
    security import certificate.p12 -k build.keychain

- name: Sign app
  run: codesign --sign "Developer ID" app.dmg

- name: Clean up
  if: always()
  run: |
    security delete-keychain build.keychain
    rm certificate.p12
```

---

## 11. Self-Hosted Runner Anti-Patterns

### 11.1 Using Self-Hosted Runners for Public Repos

**WRONG - Self-hosted runner on public repository:**
```yaml
jobs:
  build:
    runs-on: self-hosted  # On public repo - CRITICAL RISK!
```

**Why This Is Critically Dangerous**:
- Anyone can submit PR to public repo
- PR code runs on your infrastructure
- Can access internal network
- Steal credentials from runner
- Install backdoors
- Cryptomining

**Attack Scenario**:
1. Attacker submits PR to public repo
2. Workflow runs on self-hosted runner
3. Malicious code scans internal network
4. Exfiltrates cloud credentials from runner
5. Compromises production infrastructure

**CORRECT - Only use GitHub-hosted runners for public repos:**
```yaml
jobs:
  build:
    runs-on: ubuntu-latest  # GitHub-hosted, isolated
```

**Exception**: Self-hosted runners OK for private repos with required approvals

---

## 12. Anti-Pattern Checklist

Before merging CI/CD changes, verify:

- [ ] No `permissions: write-all` or missing permissions
- [ ] All actions pinned by SHA (not tag/branch)
- [ ] No secrets in command line arguments
- [ ] No secrets exposed to `pull_request` events
- [ ] No `pull_request_target` with PR code checkout
- [ ] Cache keys include dependency hashes
- [ ] No credentials cached
- [ ] Workflow triggers are appropriately scoped
- [ ] Containers run as non-root user
- [ ] Artifacts don't contain secrets
- [ ] Certificates from secrets, not repository
- [ ] Certificate cleanup in `if: always()` block
- [ ] Self-hosted runners only for private repos

---

## Common Vulnerability Examples

### CVE-2024-23897 - Jenkins CLI Arbitrary File Read
**Severity**: Critical (9.8)
**Impact**: Remote attackers can read arbitrary files
**Mitigation**: Update Jenkins to patched version, restrict CLI access

### CVE-2023-49291 - GitHub Actions Supply Chain Attack
**Severity**: Critical (9.8)
**Impact**: Tag/branch pinning allows action hijacking
**Mitigation**: Always pin actions by SHA

### CVE-2025-30066 - tj-actions Path Traversal
**Severity**: High (8.6)
**Impact**: Arbitrary file write via path traversal
**Mitigation**: Audit all tj-actions usage, update to patched versions

---

## References

- [OWASP CI/CD Security Top 10](https://owasp.org/www-project-top-10-ci-cd-security-risks/)
- [GitHub Actions Security Hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [Preventing pwn requests](https://securitylab.github.com/research/github-actions-preventing-pwn-requests/)
