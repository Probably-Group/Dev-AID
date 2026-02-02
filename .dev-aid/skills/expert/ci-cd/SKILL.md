---
name: ci-cd
version: 2.0.0
description: "Desktop app CI/CD pipelines with code signing, notarization, artifact management, and release automation."
risk_level: HIGH
---

# CI/CD Pipeline Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-321: Signing Key Management**
- NEVER: Signing keys in repository or plaintext
- ALWAYS: HSM, secure key storage, separate signing environment

**CWE-494: Code Signing Bypass**
- NEVER: Ship unsigned binaries
- ALWAYS: Sign all artifacts, verify signatures before deployment

**CWE-829: Dependency Confusion**
- NEVER: Mix public and private package sources without scoping
- ALWAYS: Scoped registries, namespace prefixes, source pinning

### 0.3 Risk Level: HIGH

**Verification requirements for HIGH risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 Secret Management (CWE-798)

**Principle:** Never hardcode secrets. Use encrypted secrets, OIDC, or external vaults.

```yaml
# ❌ WRONG - Secret in workflow file
jobs:
  deploy:
    steps:
      - run: |
          curl -H "Authorization: Bearer sk-secret123" https://api.example.com

# ✅ CORRECT - GitHub encrypted secrets
jobs:
  deploy:
    steps:
      - run: |
          curl -H "Authorization: Bearer ${{ secrets.API_TOKEN }}" https://api.example.com
        env:
          # Explicit env prevents accidental logging
          API_TOKEN: ${{ secrets.API_TOKEN }}
```

### 1.2 Workflow Injection Prevention (CWE-94)

**Principle:** Never use untrusted input in `run:` commands directly.

```yaml
# ❌ WRONG - Command injection via PR title
jobs:
  greet:
    steps:
      - run: echo "PR: ${{ github.event.pull_request.title }}"

# ✅ CORRECT - Use environment variable
jobs:
  greet:
    steps:
      - run: echo "PR: $PR_TITLE"
        env:
          PR_TITLE: ${{ github.event.pull_request.title }}
```

### 1.3 Permissions Minimization (CWE-250)

**Principle:** Request minimum permissions. Never use `write-all`.

### 1.4 Dependency Pinning (CWE-829)

**Principle:** Pin all actions by SHA, not tag. Pin base images by digest.

### 1.5 Code Signing (CWE-494)

**Principle:** Sign all release artifacts. Verify signatures before deployment.

### 1.6 Supply Chain Security (CWE-1357)

**Principle:** Use SLSA provenance. Verify dependencies with checksums.

---

## 2. Version Requirements

**ALWAYS use these minimum versions:**

```yaml
# GitHub Actions
actions/checkout@v4  # Pin by SHA in production
actions/setup-node@v4
actions/cache@v4

# Runner images
ubuntu-24.04  # Latest LTS
macos-14      # Apple Silicon
windows-2022
```

---

## 3. Code Patterns

### 3.1 WHEN creating GitHub Actions workflow

```yaml
# ❌ WRONG - Overly permissive, unpinned actions
name: CI
on: [push, pull_request]
permissions: write-all  # Too permissive!
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4  # Not pinned!
      - run: npm install && npm test

# ✅ CORRECT - Secure workflow structure
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

# Minimal default permissions
permissions:
  contents: read

# Prevent concurrent runs
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

env:
  NODE_VERSION: '20'
  PNPM_VERSION: '8'

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-24.04
    permissions:
      contents: read
    steps:
      - name: Checkout
        uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1

      - name: Setup pnpm
        uses: pnpm/action-setup@a3252b78c470c02df07e9d59298aecedc3ccdd6d  # v3.0.0
        with:
          version: ${{ env.PNPM_VERSION }}

      - name: Setup Node.js
        uses: actions/setup-node@60edb5dd545a775178f52524783378180af0d1f8  # v4.0.2
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'pnpm'

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Lint
        run: pnpm lint

  test:
    name: Test
    runs-on: ubuntu-24.04
    permissions:
      contents: read
    needs: lint
    steps:
      - name: Checkout
        uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11

      - name: Setup pnpm
        uses: pnpm/action-setup@a3252b78c470c02df07e9d59298aecedc3ccdd6d
        with:
          version: ${{ env.PNPM_VERSION }}

      - name: Setup Node.js
        uses: actions/setup-node@60edb5dd545a775178f52524783378180af0d1f8
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'pnpm'

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Run tests
        run: pnpm test -- --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@54bcd8715eee62d40e33596ef5e8f0f48dbbccab  # v4.1.0
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          fail_ci_if_error: false
```

### 3.2 WHEN building desktop apps with code signing

```yaml
name: Build Desktop App

on:
  push:
    tags:
      - 'v*'

permissions:
  contents: write  # For release creation

jobs:
  build-tauri:
    strategy:
      fail-fast: false
      matrix:
        include:
          - platform: macos-14
            target: aarch64-apple-darwin
          - platform: macos-14
            target: x86_64-apple-darwin
          - platform: ubuntu-24.04
            target: x86_64-unknown-linux-gnu
          - platform: windows-2022
            target: x86_64-pc-windows-msvc

    runs-on: ${{ matrix.platform }}

    steps:
      - name: Checkout
        uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11

      - name: Setup Rust
        uses: dtolnay/rust-toolchain@stable
        with:
          targets: ${{ matrix.target }}

      - name: Setup Node.js
        uses: actions/setup-node@60edb5dd545a775178f52524783378180af0d1f8
        with:
          node-version: '20'

      - name: Install dependencies (Ubuntu)
        if: matrix.platform == 'ubuntu-24.04'
        run: |
          sudo apt-get update
          sudo apt-get install -y libwebkit2gtk-4.1-dev libappindicator3-dev librsvg2-dev

      # macOS code signing
      - name: Import macOS certificates
        if: startsWith(matrix.platform, 'macos')
        env:
          APPLE_CERTIFICATE: ${{ secrets.APPLE_CERTIFICATE }}
          APPLE_CERTIFICATE_PASSWORD: ${{ secrets.APPLE_CERTIFICATE_PASSWORD }}
          KEYCHAIN_PASSWORD: ${{ secrets.KEYCHAIN_PASSWORD }}
        run: |
          # Create keychain
          security create-keychain -p "$KEYCHAIN_PASSWORD" build.keychain
          security default-keychain -s build.keychain
          security unlock-keychain -p "$KEYCHAIN_PASSWORD" build.keychain
          security set-keychain-settings -t 3600 -u build.keychain

          # Import certificate
          echo "$APPLE_CERTIFICATE" | base64 --decode > certificate.p12
          security import certificate.p12 -k build.keychain \
            -P "$APPLE_CERTIFICATE_PASSWORD" \
            -T /usr/bin/codesign \
            -T /usr/bin/security

          # Allow codesign access
          security set-key-partition-list -S apple-tool:,apple: \
            -s -k "$KEYCHAIN_PASSWORD" build.keychain

          # Clean up
          rm certificate.p12

      # Windows code signing
      - name: Setup Windows signing
        if: matrix.platform == 'windows-2022'
        env:
          WINDOWS_CERTIFICATE: ${{ secrets.WINDOWS_CERTIFICATE }}
          WINDOWS_CERTIFICATE_PASSWORD: ${{ secrets.WINDOWS_CERTIFICATE_PASSWORD }}
        run: |
          echo "$env:WINDOWS_CERTIFICATE" > certificate.b64
          certutil -decode certificate.b64 certificate.pfx
          Remove-Item certificate.b64

      - name: Build Tauri app
        uses: tauri-apps/tauri-action@v0
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          # macOS signing
          APPLE_SIGNING_IDENTITY: ${{ secrets.APPLE_SIGNING_IDENTITY }}
          APPLE_ID: ${{ secrets.APPLE_ID }}
          APPLE_PASSWORD: ${{ secrets.APPLE_PASSWORD }}
          APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
          # Windows signing
          TAURI_PRIVATE_KEY: ${{ secrets.TAURI_PRIVATE_KEY }}
          TAURI_KEY_PASSWORD: ${{ secrets.TAURI_KEY_PASSWORD }}
        with:
          tagName: ${{ github.ref_name }}
          releaseName: 'v__VERSION__'
          releaseBody: 'See the assets for downloadable binaries.'
          releaseDraft: true
          prerelease: false
          args: --target ${{ matrix.target }}

      - name: Clean up Windows certificate
        if: matrix.platform == 'windows-2022' && always()
        run: Remove-Item -Force certificate.pfx -ErrorAction SilentlyContinue
```

### 3.3 WHEN implementing release automation

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

permissions:
  contents: write
  id-token: write  # For OIDC
  attestations: write  # For SLSA

jobs:
  release:
    runs-on: ubuntu-24.04

    steps:
      - name: Checkout
        uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11
        with:
          fetch-depth: 0  # For changelog generation

      - name: Setup Node.js
        uses: actions/setup-node@60edb5dd545a775178f52524783378180af0d1f8
        with:
          node-version: '20'
          registry-url: 'https://registry.npmjs.org'

      - name: Build
        run: |
          npm ci
          npm run build

      - name: Generate SBOM
        uses: anchore/sbom-action@v0
        with:
          artifact-name: sbom.spdx.json

      - name: Generate changelog
        id: changelog
        uses: orhun/git-cliff-action@v3
        with:
          config: cliff.toml
          args: --latest --strip header

      - name: Create checksums
        run: |
          cd dist
          sha256sum * > checksums.sha256

      - name: Generate attestation
        uses: actions/attest-build-provenance@v1
        with:
          subject-path: 'dist/*'

      - name: Create release
        uses: softprops/action-gh-release@v2
        with:
          body: ${{ steps.changelog.outputs.content }}
          files: |
            dist/*
            sbom.spdx.json
          draft: false
          prerelease: ${{ contains(github.ref, '-') }}

      - name: Publish to npm
        run: npm publish --provenance
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

### 3.4 WHEN setting up matrix builds

```yaml
name: Cross-Platform Build

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  build:
    strategy:
      fail-fast: false
      matrix:
        include:
          # Linux
          - os: ubuntu-24.04
            target: x86_64-unknown-linux-gnu
            artifact: app-linux-x64
          - os: ubuntu-24.04
            target: aarch64-unknown-linux-gnu
            artifact: app-linux-arm64
            cross: true

          # macOS
          - os: macos-14
            target: aarch64-apple-darwin
            artifact: app-macos-arm64
          - os: macos-14
            target: x86_64-apple-darwin
            artifact: app-macos-x64

          # Windows
          - os: windows-2022
            target: x86_64-pc-windows-msvc
            artifact: app-windows-x64

    runs-on: ${{ matrix.os }}

    steps:
      - name: Checkout
        uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11

      - name: Setup Rust
        uses: dtolnay/rust-toolchain@stable
        with:
          targets: ${{ matrix.target }}

      - name: Setup cross-compilation
        if: matrix.cross
        uses: taiki-e/setup-cross-toolchain-action@v1
        with:
          target: ${{ matrix.target }}

      - name: Cache cargo
        uses: Swatinem/rust-cache@v2
        with:
          key: ${{ matrix.target }}

      - name: Build
        run: cargo build --release --target ${{ matrix.target }}

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: ${{ matrix.artifact }}
          path: |
            target/${{ matrix.target }}/release/app
            target/${{ matrix.target }}/release/app.exe
          if-no-files-found: error
          retention-days: 7
```

### 3.5 WHEN implementing security scanning

```yaml
name: Security

on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: '0 6 * * 1'  # Weekly Monday 6 AM

permissions:
  contents: read
  security-events: write

jobs:
  dependency-scan:
    runs-on: ubuntu-24.04
    steps:
      - name: Checkout
        uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload Trivy results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'

  sast:
    runs-on: ubuntu-24.04
    steps:
      - name: Checkout
        uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v3
        with:
          languages: javascript, typescript
          queries: security-extended

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v3
        with:
          category: '/language:javascript'

  secrets-scan:
    runs-on: ubuntu-24.04
    steps:
      - name: Checkout
        uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11
        with:
          fetch-depth: 0  # Full history for secret scanning

      - name: Detect secrets
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
          extra_args: --only-verified
```

### 3.6 WHEN implementing deployment pipelines

```yaml
name: Deploy

on:
  workflow_run:
    workflows: [CI]
    types: [completed]
    branches: [main]

permissions:
  contents: read
  id-token: write  # For OIDC

concurrency:
  group: deploy-production
  cancel-in-progress: false  # Never cancel deployments

jobs:
  deploy:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-24.04
    environment:
      name: production
      url: https://app.example.com

    steps:
      - name: Checkout
        uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11

      # Use OIDC instead of long-lived credentials
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789:role/github-actions-deploy
          aws-region: us-east-1

      - name: Download build artifacts
        uses: actions/download-artifact@v4
        with:
          name: build
          path: dist
          run-id: ${{ github.event.workflow_run.id }}

      - name: Deploy to S3
        run: |
          aws s3 sync dist/ s3://my-bucket/ \
            --delete \
            --cache-control "max-age=31536000,immutable" \
            --exclude "index.html" \
            --exclude "*.json"

          # index.html with no-cache
          aws s3 cp dist/index.html s3://my-bucket/ \
            --cache-control "no-cache,no-store,must-revalidate"

      - name: Invalidate CloudFront
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ vars.CLOUDFRONT_DISTRIBUTION_ID }} \
            --paths "/*"

      - name: Notify on failure
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          channel-id: 'deployments'
          slack-message: 'Deployment failed: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}'
        env:
          SLACK_BOT_TOKEN: ${{ secrets.SLACK_BOT_TOKEN }}
```

---

## 4. Anti-Patterns

**NEVER:**
- Use `permissions: write-all`
- Use unpinned actions (use SHA)
- Put secrets in workflow files
- Use untrusted input in `run:` directly
- Skip security scanning
- Use long-lived credentials (use OIDC)
- Cancel deployment jobs in progress
- Deploy without environment protection rules

---

## 5. Testing

**ALWAYS test workflows locally:**

```bash
# Install act for local testing
brew install act

# Run workflow locally
act push --secret-file .secrets

# Test specific job
act -j build --secret-file .secrets

# Validate workflow syntax
actionlint .github/workflows/*.yml
```

---

## 6. Pre-Generation Checklist

**BEFORE generating any CI/CD configuration:**

- [ ] Minimal permissions declared
- [ ] All actions pinned by SHA
- [ ] Secrets use GitHub encrypted secrets or OIDC
- [ ] No untrusted input in run commands
- [ ] Security scanning (SAST, dependencies, secrets)
- [ ] Code signing configured for releases
- [ ] SBOM and attestations for artifacts
- [ ] Concurrency controls prevent race conditions
- [ ] Environment protection rules for production
- [ ] Caching optimized for performance
