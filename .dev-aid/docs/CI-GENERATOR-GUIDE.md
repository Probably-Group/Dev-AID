# CI/CD Workflow Generator Guide

**Automatically generate production-ready CI/CD workflows for your project**

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Supported Languages](#supported-languages)
4. [Features](#features)
5. [Usage](#usage)
6. [Language-Specific Examples](#language-specific-examples)
7. [Template Customization](#template-customization)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Configuration](#advanced-configuration)

---

## Overview

The **CI/CD Workflow Generator** is an intelligent automation tool that analyzes your project and generates optimized GitHub Actions workflows tailored to your technology stack.

### The Problem

Setting up CI/CD pipelines requires:
- ❌ Understanding GitHub Actions syntax
- ❌ Configuring security scans
- ❌ Setting up multi-version testing
- ❌ Integrating linters and formatters
- ❌ Maintaining workflows across projects

### The Solution

**One Command. Production-Ready CI/CD.**

```bash
./.dev-aid/scripts/generate-ci.sh
```

The generator:
- ✅ **Auto-detects** your language and package manager
- ✅ **Generates** optimized workflows with comprehensive security scanning
- ✅ **Configures** multi-version testing matrices
- ✅ **Includes** linting, testing, and coverage
- ✅ **Supports** Docker build and scan (optional)
- 🔒 **Fails on critical issues** (no continue-on-error bypasses)

---

## Quick Start

### 1. Generate CI Workflow

```bash
# Navigate to your project
cd your-project

# Run the generator
./.dev-aid/scripts/generate-ci.sh
```

### 2. Verify Generated Workflow

```bash
# Check the generated file
cat .github/workflows/ci.yml
```

### 3. Commit and Push

```bash
git add .github/workflows/ci.yml
git commit -m "ci: Add automated CI/CD workflow"
git push
```

### 4. Watch It Run

GitHub Actions will automatically run on your next push or pull request!

---

## Supported Languages

The generator supports **9 major languages** covering ~85% of GitHub projects:

| Language | Package Managers | Test Frameworks | Versions Tested |
|----------|-----------------|-----------------|-----------------|
| **Python** | pip, Poetry, uv | pytest | 3.9, 3.10, 3.11, 3.12 |
| **JavaScript/TypeScript** | npm, pnpm, yarn, bun | Jest, Vitest | Node 18, 20, 21 |
| **Java** | Maven, Gradle | JUnit | Java 11, 17, 21 |
| **Go** | go modules | go test | 1.20, 1.21, 1.22 |
| **Rust** | Cargo | cargo test | stable, beta |
| **C#/.NET** | dotnet | xUnit, NUnit | .NET 6, 7, 8 |
| **PHP** | Composer | PHPUnit | PHP 8.1, 8.2, 8.3 |
| **Ruby** | Bundler | RSpec | Ruby 3.0, 3.1, 3.2, 3.3 |
| **C++** | CMake | CTest | GCC, Clang |

### Detection Files

The generator detects your project by looking for:

```
Python:        pyproject.toml, requirements.txt, setup.py
Node.js:       package.json
Java:          pom.xml, build.gradle, build.gradle.kts
Go:            go.mod
Rust:          Cargo.toml
C#/.NET:       *.csproj, *.sln
PHP:           composer.json
Ruby:          Gemfile
C++:           CMakeLists.txt
Docker:        Dockerfile (adds container scanning)
```

---

## Features

### 🔒 **Security Scanning (Built-in) - 3 Tools**

Every generated workflow includes comprehensive security scanning with **auto-updating databases**:

| Tool | Scan Types | Coverage |
|------|------------|----------|
| **Gitleaks** | Secrets | Git history + current files (160+ patterns) |
| **Trivy** | CVE + Misconfig + Secrets | Dependencies, Dockerfiles, Terraform, K8s, GitHub Actions |
| **Opengrep** | SAST (340+ rules) | OWASP Top 10, CWE Top 25, CI/CD security |

**Auto-updates:**
- 🔄 Gitleaks: Auto-updates rules with `GITLEAKS_VERSION: "latest"`
- 🔄 Trivy: Auto-updates vulnerability database every 6 hours
- 🔄 Opengrep: Auto-fetches latest rulesets from registry on each run

**⚠️ Critical Findings Fail the Workflow:**
- Gitleaks: ANY secrets found → ❌ FAIL
- Trivy: CRITICAL vulnerabilities/misconfigs → ❌ FAIL
- Opengrep: ERROR severity → ❌ FAIL

Lower severities (info, style) are reported but don't block merges.

**📊 What Gets Scanned:**
```yaml
Trivy Comprehensive Scan:
  ✓ CVE vulnerabilities (dependencies, OS packages)
  ✓ Misconfigurations (Dockerfiles, IaC, K8s, GitHub Actions)
  ✓ Embedded secrets (hardcoded in dependencies)
  ✓ License compliance issues

Opengrep SAST (340+ rules):
  ✓ OWASP Top 10 vulnerabilities
  ✓ CWE Top 25 vulnerabilities
  ✓ CI/CD security issues
  ✓ Language-specific security patterns
```

### 🧪 **Multi-Version Testing**

Automatically tests across multiple versions:

```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11', '3.12']
```

### 📊 **Code Quality Checks**

- **Linting** - Auto-detected (ruff, eslint, rubocop, etc.)
- **Type Checking** - Language-specific (mypy, tsc, etc.)
- **Code Coverage** - Integrated with Codecov
- **Test Reports** - Uploaded as artifacts

### 🐳 **Docker Support**

If `Dockerfile` exists, adds:
- Multi-arch builds (amd64, arm64)
- Container scanning with Trivy
- Automatic push to GitHub Container Registry
- Cache optimization

### ⚡ **Performance Optimizations**

- Dependency caching (npm, pip, cargo, etc.)
- Incremental builds
- Parallel test execution
- GitHub Actions cache reuse

---

## Usage

### Basic Usage

```bash
# Generate workflow in default location (.github/workflows/ci.yml)
./.dev-aid/scripts/generate-ci.sh
```

### Custom Output Location

```bash
# Specify output file
./.dev-aid/scripts/generate-ci.sh -o .github/workflows/custom.yml
```

### Specific Directory

```bash
# Generate for a different project
./.dev-aid/scripts/generate-ci.sh /path/to/project
```

### What You'll See

```
🔍 Detecting project context...
✅ Detected: python
   Package Manager: poetry
   Docker: Yes

🛠️  Generating CI workflow...
✅ Generated: .github/workflows/ci.yml
   Lines: 142

📋 Commands configured:
   install: poetry install
   test: poetry run pytest
   lint: ruff check .
   type_check: mypy .

✅ Done! Workflow includes:
   - Security scanning (Gitleaks + Trivy)
   - Linting and type checking
   - Testing across multiple versions
   - Docker build and scan
```

---

## Language-Specific Examples

### Python (Poetry)

**Detected from:** `pyproject.toml` with `[tool.poetry]`

```yaml
- name: Setup Python
  uses: actions/setup-python@v5
  with:
    python-version: ${{ matrix.python-version }}
    cache: 'poetry'

- name: Install dependencies
  run: poetry install

- name: Test
  run: poetry run pytest
```

**Commands:**
- Install: `poetry install`
- Test: `poetry run pytest`
- Lint: `ruff check .`
- Type Check: `mypy .`

### Node.js (pnpm)

**Detected from:** `pnpm-lock.yaml`

```yaml
- name: Setup Node
  uses: actions/setup-node@v4
  with:
    node-version: ${{ matrix.node-version }}
    cache: 'pnpm'

- name: Install dependencies
  run: pnpm install

- name: Test
  run: pnpm test
```

**Commands:**
- Install: `pnpm install`
- Build: `pnpm build`
- Test: `pnpm test`
- Lint: `pnpm lint`

### Java (Gradle)

**Detected from:** `build.gradle` or `build.gradle.kts`

```yaml
- name: Setup Java
  uses: actions/setup-java@v4
  with:
    java-version: ${{ matrix.java-version }}
    distribution: 'temurin'
    cache: 'gradle'

- name: Build
  run: ./gradlew assemble

- name: Test
  run: ./gradlew test
```

**Commands:**
- Install: `./gradlew build --no-daemon`
- Build: `./gradlew assemble`
- Test: `./gradlew test`
- Lint: `./gradlew checkstyleMain`

### Go

**Detected from:** `go.mod`

```yaml
- name: Setup Go
  uses: actions/setup-go@v5
  with:
    go-version: ${{ matrix.go-version }}

- name: Install dependencies
  run: go mod download

- name: Test
  run: go test ./...
```

**Commands:**
- Install: `go mod download`
- Build: `go build ./...`
- Test: `go test ./...`
- Lint: `go vet ./...`

### Rust

**Detected from:** `Cargo.toml`

```yaml
- name: Setup Rust
  uses: actions-rs/toolchain@v1
  with:
    toolchain: ${{ matrix.rust }}
    override: true

- name: Test
  run: cargo test
```

**Commands:**
- Install: `cargo fetch`
- Build: `cargo build`
- Test: `cargo test`
- Lint: `cargo clippy`

### C#/.NET

**Detected from:** `*.csproj` or `*.sln`

```yaml
- name: Setup .NET
  uses: actions/setup-dotnet@v4
  with:
    dotnet-version: ${{ matrix.dotnet-version }}

- name: Restore
  run: dotnet restore

- name: Test
  run: dotnet test --configuration Release
```

**Commands:**
- Install: `dotnet restore`
- Build: `dotnet build --configuration Release`
- Test: `dotnet test --configuration Release`
- Lint: `dotnet format --verify-no-changes`

### PHP (Composer)

**Detected from:** `composer.json`

```yaml
- name: Setup PHP
  uses: shivammathur/setup-php@v2
  with:
    php-version: ${{ matrix.php-version }}
    extensions: mbstring, xml, ctype, iconv

- name: Install dependencies
  run: composer install --prefer-dist --no-progress
```

**Commands:**
- Install: `composer install --prefer-dist --no-progress`
- Test: `vendor/bin/phpunit`
- Lint: `vendor/bin/phpcs`

### Ruby (Bundler)

**Detected from:** `Gemfile`

```yaml
- name: Setup Ruby
  uses: ruby/setup-ruby@v1
  with:
    ruby-version: ${{ matrix.ruby-version }}
    bundler-cache: true

- name: Install dependencies
  run: bundle install
```

**Commands:**
- Install: `bundle install`
- Test: `bundle exec rspec`
- Lint: `bundle exec rubocop`

### C++ (CMake)

**Detected from:** `CMakeLists.txt`

```yaml
- name: Install CMake
  uses: lukka/get-cmake@latest

- name: Configure
  run: cmake -B build -DCMAKE_BUILD_TYPE=Release

- name: Build
  run: cmake --build build --config Release
```

**Commands:**
- Build: `cmake -B build -DCMAKE_BUILD_TYPE=Release`
- Test: `ctest --output-on-failure`
- Lint: `clang-tidy src/*.cpp`

---

## Template Customization

### Modify Commands

Templates use placeholders that are replaced during generation:

```yaml
- name: Install dependencies
  run: {{INSTALL_COMMAND}}

- name: Build
  run: {{BUILD_COMMAND}}

- name: Test
  run: {{TEST_COMMAND}}

- name: Lint
  run: {{LINT_COMMAND}}

- name: Type check
  run: {{TYPE_CHECK_COMMAND}}
```

### Add Custom Steps

After generation, you can add custom steps:

```yaml
- name: Custom validation
  run: ./scripts/validate.sh

- name: Deploy to staging
  if: github.ref == 'refs/heads/develop'
  run: ./scripts/deploy-staging.sh
```

### Environment Variables

Add secrets and environment variables:

```yaml
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  API_KEY: ${{ secrets.API_KEY }}
```

### Conditional Docker Build

Docker builds are only included if `Dockerfile` exists:

```yaml
{{#DOCKER}}
docker:
  name: Docker Build
  runs-on: ubuntu-latest
  steps:
    - name: Build and push
      uses: docker/build-push-action@v5
{{/DOCKER}}
```

---

## Troubleshooting

### "Could not detect project language"

**Cause:** No recognized project files found.

**Solution:** Ensure you have one of the detection files:
```bash
# Python
touch pyproject.toml  # or requirements.txt

# Node.js
touch package.json

# Java
touch pom.xml  # or build.gradle

# Go
touch go.mod

# etc.
```

### "Template not found"

**Cause:** Missing template file in `.dev-aid/templates/ci/`

**Solution:** Ensure templates exist:
```bash
ls -la .dev-aid/templates/ci/
# Should show: python.yml, nodejs.yml, java.yml, etc.
```

### Wrong Package Manager Detected

**Cause:** Multiple lock files present

**Solution:** Remove unused lock files:
```bash
# Keep only one
rm yarn.lock  # if using npm
rm package-lock.json  # if using yarn
```

### Tests Failing in CI

**Common causes:**

1. **Missing dependencies:**
   ```yaml
   # Add system dependencies
   - name: Install system deps
     run: sudo apt-get install -y libpq-dev
   ```

2. **Environment variables:**
   ```yaml
   # Set test environment
   env:
     NODE_ENV: test
     CI: true
   ```

3. **Database setup:**
   ```yaml
   # Add service container
   services:
     postgres:
       image: postgres:15
       env:
         POSTGRES_PASSWORD: postgres
   ```

---

## Advanced Configuration

### Multi-Platform Testing

For cross-platform projects (C#, C++):

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    dotnet-version: ['6.0.x', '7.0.x', '8.0.x']
```

### Monorepo Support

For monorepos, generate per-package:

```bash
# Generate for each package
./.dev-aid/scripts/generate-ci.sh packages/api -o .github/workflows/api.yml
./.dev-aid/scripts/generate-ci.sh packages/web -o .github/workflows/web.yml
```

### Custom Test Commands

Modify generated workflow to use custom commands:

```yaml
- name: Run integration tests
  run: npm run test:integration

- name: Run E2E tests
  run: npm run test:e2e
```

### Parallel Jobs

Split tests for faster execution:

```yaml
test:
  strategy:
    matrix:
      test-group: [unit, integration, e2e]
  steps:
    - name: Run tests
      run: npm run test:${{ matrix.test-group }}
```

### Security Customization

Adjust security scan severity:

```yaml
- name: Run Trivy
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: 'fs'
    severity: 'CRITICAL,HIGH,MEDIUM'  # Add MEDIUM
```

### Performance Optimization

Add more aggressive caching:

```yaml
- name: Cache dependencies
  uses: actions/cache@v4
  with:
    path: |
      ~/.npm
      ~/.cache/pip
      ~/.cargo
    key: ${{ runner.os }}-deps-${{ hashFiles('**/package-lock.json') }}
```

---

## Best Practices

### 1. Run Locally First

Test your CI commands locally before pushing:

```bash
# Python
poetry run pytest

# Node.js
npm test

# Java
./gradlew test
```

### 2. Keep Dependencies Updated

Update GitHub Actions regularly:

```yaml
# Pin to major version, auto-update minor/patch
uses: actions/setup-node@v4  # ✅ Good
uses: actions/setup-node@v4.0.0  # ❌ Too specific
```

### 3. Use Matrix Testing

Test on multiple versions to catch compatibility issues:

```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.11', '3.12']  # Min, current, latest
```

### 4. Fail Fast vs Complete

```yaml
# Fail fast (stop on first failure)
strategy:
  fail-fast: true  # Default

# Complete all tests
strategy:
  fail-fast: false  # See all failures
```

### 5. Security Scanning

Never skip security scans:

```yaml
- name: Security scan
  run: npm audit --audit-level=moderate
  # Don't use: continue-on-error: true
```

---

## Integration with Dev-AID

### Hooks Integration

The CI generator works with Dev-AID hooks:

```bash
# Pre-commit: Fast local checks
# Pre-push: Full validation
# CI: Complete suite + deployment
```

### Skill Integration

Leverage Dev-AID skills:

```bash
# Use security audit skill
/dev-aid audit

# Use code health skill
/dev-aid code-health
```

### Automation Stack

Complete automation pipeline:

```
Local Dev     →  Git Hooks    →  CI/CD        →  Production
(Editor)         (Pre-commit)     (GitHub)         (Deploy)
              ↓                ↓                ↓
              Fast checks      Full tests       Security gates
              (~10s)           (~3min)          + Deploy
```

---

## Support & Feedback

### Getting Help

1. **Check this guide** - Most common issues covered
2. **Check logs** - GitHub Actions logs show detailed errors
3. **Template issues** - Open issue with project type
4. **Feature requests** - Suggest new language support

### Contributing

Want to add support for more languages?

1. Create template in `.dev-aid/templates/ci/`
2. Add detection logic to `ci-generator.py`
3. Test with real project
4. Submit PR with examples

### Roadmap

Upcoming features:
- GitLab CI support
- Azure Pipelines support
- CircleCI support
- Bitbucket Pipelines support
- Advanced monorepo support
- Performance benchmarking
- Deployment templates

---

**Generated with Dev-AID v1.5.1** | [Report Issues](https://github.com/Probably-Group/Dev-AID/issues)
