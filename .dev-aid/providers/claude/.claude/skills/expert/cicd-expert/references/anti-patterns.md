# CI/CD Anti-Patterns and Common Mistakes

## Mistake 1: Overly Permissive Workflow Permissions

```yaml
# ❌ BAD: Default permissions too broad
name: CI
on: [push]
# Inherits write permissions to everything!

# ✅ GOOD: Explicit minimal permissions
permissions:
  contents: read
  pull-requests: write
```

**Why It's Bad**: Default permissions grant write access to repository contents, issues, PRs, and more. This violates the principle of least privilege and increases attack surface.

**Impact**: A compromised workflow could modify code, create malicious releases, or exfiltrate secrets.

---

## Mistake 2: Not Using Dependency Caching

```yaml
# ❌ BAD: Reinstalls dependencies every time
- run: npm install

# ✅ GOOD: Cache dependencies
- uses: actions/setup-node@v4
  with:
    cache: 'npm'
- run: npm ci
```

**Why It's Bad**: Reinstalling dependencies on every build wastes time and bandwidth, slowing down CI/CD pipelines significantly.

**Impact**: Slower build times compound across all developers and branches, reducing productivity.

---

## Mistake 3: Hardcoded Environment Values

```yaml
# ❌ BAD: Hardcoded values
- name: Deploy
  run: kubectl apply -f k8s/
  env:
    DATABASE_URL: postgresql://prod-db:5432/mydb

# ✅ GOOD: Use secrets and environment-specific configs
- name: Deploy
  run: kubectl apply -f k8s/overlays/${{ inputs.environment }}
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

**Why It's Bad**: Hardcoded values make environments less flexible, expose sensitive information in code, and make it difficult to change configurations.

**Impact**: Security vulnerabilities, inability to promote code between environments, configuration drift.

---

## Mistake 4: No Timeout Configuration

```yaml
# ❌ BAD: Job can run forever
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: npm run build

# ✅ GOOD: Set reasonable timeouts
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - run: npm run build
```

**Why It's Bad**: Jobs without timeouts can hang indefinitely, consuming runner resources and blocking other workflows.

**Impact**: Wasted compute resources, blocked pipelines, delayed feedback to developers.

---

## Mistake 5: Deploying Without Health Checks

```yaml
# ❌ BAD: Deploy and hope it works
- name: Deploy
  run: kubectl apply -f deployment.yml

# ✅ GOOD: Verify deployment health
- name: Deploy
  run: kubectl apply -f deployment.yml

- name: Wait for rollout
  run: kubectl rollout status deployment/myapp --timeout=5m

- name: Health check
  run: |
    for i in {1..30}; do
      if curl -f https://api.example.com/health; then
        echo "Health check passed"
        exit 0
      fi
      sleep 10
    done
    echo "Health check failed"
    exit 1
```

**Why It's Bad**: Without health checks, you won't know if the deployment actually succeeded or if the application is functioning correctly.

**Impact**: Broken deployments go unnoticed, leading to production incidents and user impact.

---

## Mistake 6: Not Using Artifact Attestation

```yaml
# ❌ BAD: No provenance tracking
- name: Build Docker image
  run: docker build -t myapp:latest .

# ✅ GOOD: Generate attestation
- name: Build and attest
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: myapp:latest
    provenance: true
    sbom: true
```

**Why It's Bad**: Without attestation, you can't verify the provenance of artifacts or detect tampering in the supply chain.

**Impact**: Supply chain security vulnerabilities, inability to audit artifact origins, compliance failures.

---

## Mistake 7: Exposing Secrets in Pull Request Builds

```yaml
# ❌ BAD: Secrets available to PRs from forks
on: pull_request
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: deploy.sh
        env:
          AWS_SECRET: ${{ secrets.AWS_SECRET }}  # Exposed to fork PRs!

# ✅ GOOD: Restrict secrets to specific events
on:
  pull_request:
  push:
    branches: [main]

jobs:
  deploy:
    if: github.event_name == 'push'  # Only on push to main
    runs-on: ubuntu-latest
    steps:
      - run: deploy.sh
        env:
          AWS_SECRET: ${{ secrets.AWS_SECRET }}
```

**Why It's Bad**: Pull requests from forks can access secrets, allowing malicious actors to exfiltrate credentials.

**Impact**: Credential theft, unauthorized access to cloud resources, security breaches.

---

## Mistake 8: Ignoring Failed Steps

```yaml
# ❌ BAD: Continue on error without handling
- name: Run tests
  run: npm test
  continue-on-error: true

# ✅ GOOD: Handle failures explicitly
- name: Run tests
  id: tests
  run: npm test
  continue-on-error: true

- name: Report test failure
  if: steps.tests.outcome == 'failure'
  run: |
    echo "Tests failed! Creating GitHub issue..."
    gh issue create --title "Tests failing in ${{ github.sha }}" --body "Check logs"
```

**Why It's Bad**: Silently continuing after failures masks problems and gives false confidence that everything is working.

**Impact**: Bugs reach production, quality degradation, loss of trust in CI/CD system.

---

## Mistake 9: Using Latest Tags for Actions

```yaml
# ❌ BAD: Using mutable tags
- uses: actions/checkout@main
- uses: some-org/some-action@latest

# ✅ GOOD: Pin to specific SHA
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
- uses: some-org/some-action@1234567890abcdef1234567890abcdef12345678  # v2.3.0
```

**Why It's Bad**: Tags like `@main` or `@latest` can change at any time, introducing breaking changes or malicious code.

**Impact**: Supply chain attacks, unexpected pipeline failures, non-reproducible builds.

---

## Mistake 10: No Branch Protection Rules

```yaml
# ❌ BAD: Anyone can push directly to main
# (No configuration)

# ✅ GOOD: Configure branch protection
# In GitHub Settings > Branches > Branch protection rules:
# - Require pull request reviews before merging
# - Require status checks to pass before merging
# - Require branches to be up to date before merging
# - Include administrators
```

**Why It's Bad**: Without branch protection, anyone with write access can push unreviewed code directly to production branches.

**Impact**: Unreviewed code reaches production, bypassing security scans and tests, quality issues.

---

## Mistake 11: Not Using Matrix Builds Strategically

```yaml
# ❌ BAD: Sequential jobs for each platform
jobs:
  test-ubuntu:
    runs-on: ubuntu-latest
  test-macos:
    runs-on: macos-latest
  test-windows:
    runs-on: windows-latest

# ✅ GOOD: Use matrix strategy
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    runs-on: ${{ matrix.os }}
```

**Why It's Bad**: Manual duplication is error-prone and harder to maintain. Changes must be replicated across multiple jobs.

**Impact**: Maintenance burden, inconsistencies between platforms, increased chance of errors.

---

## Mistake 12: Building on Pull Request from Forks

```yaml
# ❌ BAD: Allow untrusted code to run in secure context
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm install  # Could run malicious scripts!

# ✅ GOOD: Use pull_request_target with explicit checkout
on:
  pull_request_target:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}
      - name: Review code before running
        run: echo "Manual review required for fork PRs"
```

**Why It's Bad**: Fork PRs can contain malicious code that gets executed in your CI environment with access to secrets.

**Impact**: Code injection, secret exfiltration, compromised CI/CD infrastructure.

---

## Quick Reference: Anti-Pattern Checklist

Before merging CI/CD changes:
- [ ] Workflow permissions are minimal and explicit
- [ ] Dependencies and build artifacts are cached
- [ ] No hardcoded secrets or environment values
- [ ] Timeouts configured for all jobs
- [ ] Health checks verify deployments
- [ ] Artifacts signed and attested
- [ ] Secrets not exposed to fork PRs
- [ ] Failed steps are handled explicitly
- [ ] Actions pinned to specific SHAs
- [ ] Branch protection rules enabled
- [ ] Matrix builds used where appropriate
- [ ] Fork PR security considered
