# Advanced CI/CD Pipeline Patterns

## Pattern 1: Secure Multi-Stage GitHub Actions Pipeline

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

permissions:
  contents: read
  security-events: write
  id-token: write  # For OIDC

jobs:
  # Stage 1: Code Quality & Security
  code-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for better analysis

      - name: Run Semgrep SAST
        uses: semgrep/semgrep-action@v1
        with:
          config: p/security-audit

      - name: SonarQube Scan
        uses: sonarsource/sonarqube-scan-action@master
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}

  # Stage 2: Dependency Scanning
  dependency-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Dependency Review
        uses: actions/dependency-review-action@v4
        with:
          fail-on-severity: high

      - name: Snyk Security Scan
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

  # Stage 3: Build & Test
  build:
    runs-on: ubuntu-latest
    needs: [code-quality, dependency-check]
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests with coverage
        run: npm run test:coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3

      - name: Build application
        run: npm run build

      - name: Upload build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
          retention-days: 7

  # Stage 4: Container Build & Scan
  container:
    runs-on: ubuntu-latest
    needs: build
    outputs:
      image-digest: ${{ steps.build.outputs.digest }}
    steps:
      - uses: actions/checkout@v4

      - name: Download build artifacts
        uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Container Registry (OIDC)
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push Docker image
        id: build
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:${{ github.sha }}
            ghcr.io/${{ github.repository }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Scan image with Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ghcr.io/${{ github.repository }}:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  # Stage 5: Sign Artifacts
  sign:
    runs-on: ubuntu-latest
    needs: container
    permissions:
      packages: write
      id-token: write
    steps:
      - name: Install Cosign
        uses: sigstore/cosign-installer@v3

      - name: Sign container image
        run: |
          cosign sign --yes \
            ghcr.io/${{ github.repository }}@${{ needs.container.outputs.image-digest }}

  # Stage 6: Deploy to Staging
  deploy-staging:
    runs-on: ubuntu-latest
    needs: sign
    if: github.ref == 'refs/heads/main'
    environment: staging
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/myapp \
            myapp=ghcr.io/${{ github.repository }}:${{ github.sha }} \
            --namespace=staging

      - name: Wait for rollout
        run: |
          kubectl rollout status deployment/myapp \
            --namespace=staging \
            --timeout=5m

      - name: Run smoke tests
        run: npm run test:smoke -- --env=staging

  # Stage 7: Deploy to Production
  deploy-production:
    runs-on: ubuntu-latest
    needs: deploy-staging
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: Deploy via ArgoCD
        run: |
          argocd app set myapp \
            --parameter image.tag=${{ github.sha }}
          argocd app sync myapp --prune
          argocd app wait myapp --health --timeout 600
```

**Key Features**:
- ✅ Security scans at multiple stages (SAST, SCA, container scanning)
- ✅ Proper dependency management with artifact passing
- ✅ OIDC authentication (no static secrets)
- ✅ Layer caching for Docker builds
- ✅ Artifact signing with Cosign
- ✅ Environment-specific deployments with approvals

---

## Pattern 2: Reusable Workflow for Microservices

```yaml
# .github/workflows/reusable-service-build.yml
name: Reusable Service Build

on:
  workflow_call:
    inputs:
      service-name:
        required: true
        type: string
      node-version:
        required: false
        type: string
        default: '20'
      run-e2e-tests:
        required: false
        type: boolean
        default: false
    secrets:
      SONAR_TOKEN:
        required: true
      NPM_TOKEN:
        required: false

jobs:
  build-test-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
          cache: 'npm'
          cache-dependency-path: services/${{ inputs.service-name }}/package-lock.json

      - name: Install dependencies
        working-directory: services/${{ inputs.service-name }}
        run: npm ci

      - name: Run unit tests
        working-directory: services/${{ inputs.service-name }}
        run: npm run test:unit

      - name: Run integration tests
        if: inputs.run-e2e-tests
        working-directory: services/${{ inputs.service-name }}
        run: npm run test:integration

      - name: Build service
        working-directory: services/${{ inputs.service-name }}
        run: npm run build

      - name: SonarQube Analysis
        uses: sonarsource/sonarqube-scan-action@master
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
        with:
          projectBaseDir: services/${{ inputs.service-name }}

# Usage in caller workflow:
# jobs:
#   build-auth-service:
#     uses: ./.github/workflows/reusable-service-build.yml
#     with:
#       service-name: auth-service
#       run-e2e-tests: true
#     secrets:
#       SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

---

## Pattern 3: Matrix Testing Across Multiple Environments

```yaml
name: Matrix Testing

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        node-version: [18, 20, 21]
        exclude:
          # Don't test Node 18 on macOS
          - os: macos-latest
            node-version: 18
      fail-fast: false  # Continue testing other combinations on failure

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          flags: ${{ matrix.os }}-node${{ matrix.node-version }}
```

---

## Pattern 4: Conditional Deployment with Manual Approval

```yaml
name: Production Deployment

on:
  workflow_dispatch:  # Manual trigger only
    inputs:
      environment:
        description: 'Target environment'
        required: true
        type: choice
        options:
          - staging
          - production
      version:
        description: 'Version to deploy'
        required: true
        type: string

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Validate inputs
        run: |
          if [[ ! "${{ inputs.version }}" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            echo "Invalid version format. Expected: vX.Y.Z"
            exit 1
          fi

  deploy:
    needs: validate
    runs-on: ubuntu-latest
    environment:
      name: ${{ inputs.environment }}
      url: https://${{ inputs.environment }}.example.com
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ inputs.version }}

      - name: Deploy to ${{ inputs.environment }}
        run: |
          echo "Deploying ${{ inputs.version }} to ${{ inputs.environment }}"
          kubectl set image deployment/myapp \
            myapp=ghcr.io/${{ github.repository }}:${{ inputs.version }} \
            --namespace=${{ inputs.environment }}

      - name: Verify deployment
        run: |
          kubectl rollout status deployment/myapp \
            --namespace=${{ inputs.environment }} \
            --timeout=10m

      - name: Run health checks
        run: |
          curl -f https://${{ inputs.environment }}.example.com/health || exit 1

      - name: Notify Slack
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
          payload: |
            {
              "text": "✅ Deployed ${{ inputs.version }} to ${{ inputs.environment }}",
              "username": "GitHub Actions"
            }
```

---

## Pattern 5: Monorepo with Path-Based Triggers

```yaml
name: Monorepo CI

on:
  pull_request:
    paths:
      - 'services/**'
      - 'packages/**'

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      auth-service: ${{ steps.filter.outputs.auth-service }}
      payment-service: ${{ steps.filter.outputs.payment-service }}
      shared-lib: ${{ steps.filter.outputs.shared-lib }}
    steps:
      - uses: actions/checkout@v4

      - uses: dorny/paths-filter@v2
        id: filter
        with:
          filters: |
            auth-service:
              - 'services/auth-service/**'
            payment-service:
              - 'services/payment-service/**'
            shared-lib:
              - 'packages/shared-lib/**'

  build-auth-service:
    needs: detect-changes
    if: needs.detect-changes.outputs.auth-service == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build auth service
        working-directory: services/auth-service
        run: npm ci && npm run build

  build-payment-service:
    needs: detect-changes
    if: needs.detect-changes.outputs.payment-service == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build payment service
        working-directory: services/payment-service
        run: npm ci && npm run build

  build-shared-lib:
    needs: detect-changes
    if: needs.detect-changes.outputs.shared-lib == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build shared library
        working-directory: packages/shared-lib
        run: npm ci && npm run build && npm run test
```

---

## Pattern 6: Self-Hosted Runner with Dynamic Scaling

```yaml
name: Self-Hosted Build

jobs:
  build-large-project:
    runs-on: [self-hosted, linux, x64, high-memory]
    timeout-minutes: 120
    steps:
      - uses: actions/checkout@v4

      - name: Clean workspace
        run: |
          docker system prune -af
          rm -rf node_modules dist

      - name: Build with Docker
        run: |
          docker build \
            --cache-from ghcr.io/${{ github.repository }}:buildcache \
            --build-arg BUILDKIT_INLINE_CACHE=1 \
            -t myapp:${{ github.sha }} .

      - name: Run tests in container
        run: |
          docker run --rm \
            -v $PWD:/app \
            myapp:${{ github.sha }} \
            npm test

      - name: Cleanup
        if: always()
        run: |
          docker rmi myapp:${{ github.sha }} || true
```
