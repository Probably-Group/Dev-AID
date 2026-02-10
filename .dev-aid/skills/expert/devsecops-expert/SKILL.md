---
name: devsecops-expert
version: 2.0.0
description: "DevSecOps practices with shift-left security automation, SAST/DAST pipeline integration, supply chain security, and compliance as code. Use when embedding security scanning in CI/CD, implementing SBOM generation, configuring dependency vulnerability checks, or designing security gate policies. Do NOT use for application-level security patterns like OWASP Top 10 remediation (use appsec-expert)."
compatibility: "GitHub Actions or GitLab CI"
risk_level: HIGH
---

# DevSecOps Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-1035: SAST Bypass**
- NEVER: Skip SAST for "small changes"
- ALWAYS: SAST on every PR, block merge on high severity

**CWE-937: Vulnerable Dependencies**
- NEVER: Ignore dependency vulnerability alerts
- ALWAYS: Automated scanning, SLA for patching by severity

**CWE-829: Supply Chain Attacks**
- NEVER: Trust transitive dependencies blindly
- ALWAYS: SBOM generation, signature verification, reproducible builds

### 0.3 Risk Level: HIGH

**Verification requirements for HIGH risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 Shift-Left Security (CWE-1395)

**Principle:** Integrate security testing early in the pipeline. Fail fast on vulnerabilities.

```yaml
# ❌ WRONG - Security only at the end
stages:
  - build
  - test
  - deploy
  - security_scan  # Too late!

# ✅ CORRECT - Security at every stage
stages:
  - pre-commit      # Secret scanning, linting
  - build           # SAST, dependency scan
  - test            # DAST, security tests
  - staging         # Penetration testing
  - production      # Runtime protection
```

### 1.2 Supply Chain Security (CWE-1357)

**Principle:** Verify all dependencies. Sign artifacts. Use SBOM.

```yaml
# ❌ WRONG - No verification
- run: npm install

# ✅ CORRECT - Locked, verified dependencies
- run: npm ci --ignore-scripts
- run: npm audit --audit-level=high
- name: Generate SBOM
  uses: anchore/sbom-action@v0
  with:
    artifact-name: sbom.spdx
```

### 1.3 Secrets Management (CWE-798)

**Principle:** Never hardcode secrets. Use external secret managers.

```yaml
# ❌ WRONG - Secrets in manifests
env:
  - name: DB_PASSWORD
    value: "secretpassword123"

# ✅ CORRECT - External Secrets Operator
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: database-credentials
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: ClusterSecretStore
  target:
    name: database-credentials
  data:
    - secretKey: password
      remoteRef:
        key: database/production
        property: password
```

### 1.4 Least Privilege (CWE-250)

**Principle:** Containers run as non-root. Minimize capabilities. Use security contexts.

### 1.5 Defense in Depth (CWE-693)

**Principle:** Multiple security layers. Network policies, runtime protection, WAF.

### 1.6 Audit Logging (CWE-778)

**Principle:** Log all security-relevant events. Immutable audit trail.

---

## 2. Version Requirements

**ALWAYS use these minimum versions:**

```yaml
# Security scanning tools
trivy: v0.50.0+
grype: v0.74.0+
syft: v1.0.0+
cosign: v2.2.0+

# Policy engines
kyverno: v1.11.0+
gatekeeper: v3.15.0+

# Secret management
external-secrets: v0.9.0+
sealed-secrets: v0.26.0+
vault: v1.15.0+
```

---

## 3. Code Patterns

### 3.1 WHEN implementing GitHub Actions security pipeline

```yaml
# ❌ WRONG - Insecure pipeline
name: CI
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm install
      - run: npm test
      - run: docker build -t myapp .
      - run: docker push myapp

# ✅ CORRECT - Secure CI/CD pipeline
name: Secure CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read
  security-events: write
  id-token: write  # For OIDC

jobs:
  # Stage 1: Pre-flight checks
  preflight:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
        with:
          fetch-depth: 0  # Full history for secret scanning

      - name: Secret scanning
        uses: trufflesecurity/trufflehog@main
        with:
          extra_args: --only-verified

      - name: Detect hardcoded secrets
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  # Stage 2: SAST and dependency scanning
  security-scan:
    needs: preflight
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v3
        with:
          languages: javascript, python

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v3

      - name: Dependency Review
        uses: actions/dependency-review-action@v4
        if: github.event_name == 'pull_request'
        with:
          fail-on-severity: high
          deny-licenses: GPL-3.0, AGPL-3.0

      - name: Run Semgrep
        uses: semgrep/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/secrets
            p/owasp-top-ten

  # Stage 3: Build with SBOM
  build:
    needs: security-scan
    runs-on: ubuntu-latest
    outputs:
      digest: ${{ steps.build.outputs.digest }}
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        id: build
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          sbom: true
          provenance: true
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Generate SBOM
        uses: anchore/sbom-action@v0
        with:
          image: ghcr.io/${{ github.repository }}:${{ github.sha }}
          artifact-name: sbom.spdx.json
          output-file: sbom.spdx.json

      - name: Upload SBOM
        uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: sbom.spdx.json

  # Stage 4: Container scanning
  container-scan:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Scan with Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ghcr.io/${{ github.repository }}:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'

      - name: Upload Trivy results
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: 'trivy-results.sarif'

      - name: Scan with Grype
        uses: anchore/scan-action@v4
        with:
          image: ghcr.io/${{ github.repository }}:${{ github.sha }}
          fail-build: true
          severity-cutoff: high

  # Stage 5: Sign artifacts
  sign:
    needs: [build, container-scan]
    runs-on: ubuntu-latest
    steps:
      - name: Install Cosign
        uses: sigstore/cosign-installer@v3

      - name: Sign container image
        env:
          COSIGN_EXPERIMENTAL: 1
        run: |
          cosign sign --yes ghcr.io/${{ github.repository }}@${{ needs.build.outputs.digest }}

      - name: Verify signature
        run: |
          cosign verify \
            --certificate-identity-regexp="https://github.com/${{ github.repository }}" \
            --certificate-oidc-issuer=https://token.actions.githubusercontent.com \
            ghcr.io/${{ github.repository }}@${{ needs.build.outputs.digest }}

  # Stage 6: Deploy with policy enforcement
  deploy:
    needs: sign
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683

      - name: Deploy to Kubernetes
        run: |
          kubectl apply -f k8s/
          kubectl rollout status deployment/myapp -n production
```

### 3.2 WHEN implementing Kyverno policies

```yaml
# ❌ WRONG - No policy enforcement
# Just deploy and hope for the best

# ✅ CORRECT - Comprehensive security policies
---
# Require signed images
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-image-signature
spec:
  validationFailureAction: Enforce
  background: true
  rules:
    - name: verify-signature
      match:
        any:
          - resources:
              kinds:
                - Pod
      verifyImages:
        - imageReferences:
            - "ghcr.io/myorg/*"
          attestors:
            - entries:
                - keyless:
                    subject: "https://github.com/myorg/*"
                    issuer: "https://token.actions.githubusercontent.com"
                    rekor:
                      url: https://rekor.sigstore.dev
---
# Require security context
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-security-context
spec:
  validationFailureAction: Enforce
  rules:
    - name: require-run-as-non-root
      match:
        any:
          - resources:
              kinds:
                - Pod
      exclude:
        any:
          - resources:
              namespaces:
                - kube-system
      validate:
        message: "Containers must run as non-root"
        pattern:
          spec:
            securityContext:
              runAsNonRoot: true
            containers:
              - securityContext:
                  runAsNonRoot: true
                  allowPrivilegeEscalation: false
                  capabilities:
                    drop:
                      - ALL
                  readOnlyRootFilesystem: true

    - name: require-resource-limits
      match:
        any:
          - resources:
              kinds:
                - Pod
      validate:
        message: "Resource limits are required"
        pattern:
          spec:
            containers:
              - resources:
                  limits:
                    memory: "?*"
                    cpu: "?*"
                  requests:
                    memory: "?*"
                    cpu: "?*"
---
# Disallow privileged containers
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: disallow-privileged
spec:
  validationFailureAction: Enforce
  rules:
    - name: deny-privileged
      match:
        any:
          - resources:
              kinds:
                - Pod
      validate:
        message: "Privileged containers are not allowed"
        pattern:
          spec:
            containers:
              - =(securityContext):
                  =(privileged): false
            =(initContainers):
              - =(securityContext):
                  =(privileged): false
---
# Require network policies
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-network-policy
spec:
  validationFailureAction: Audit
  rules:
    - name: require-network-policy
      match:
        any:
          - resources:
              kinds:
                - Namespace
      generate:
        apiVersion: networking.k8s.io/v1
        kind: NetworkPolicy
        name: default-deny
        namespace: "{{request.object.metadata.name}}"
        data:
          spec:
            podSelector: {}
            policyTypes:
              - Ingress
              - Egress
```

### 3.3 WHEN implementing DAST with OWASP ZAP

```yaml
# ❌ WRONG - No DAST testing
# Deploy without runtime security testing

# ✅ CORRECT - Automated DAST in CI/CD
name: DAST Scan

on:
  workflow_run:
    workflows: ["Deploy to Staging"]
    types:
      - completed

jobs:
  dast:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'success' }}

    steps:
      - uses: actions/checkout@v4

      - name: Wait for deployment
        run: |
          for i in {1..30}; do
            if curl -sf https://staging.example.com/health; then
              echo "Application is ready"
              exit 0
            fi
            sleep 10
          done
          echo "Timeout waiting for application"
          exit 1

      - name: ZAP Baseline Scan
        uses: zaproxy/action-baseline@v0.12.0
        with:
          target: 'https://staging.example.com'
          rules_file_name: '.zap/rules.tsv'
          cmd_options: '-a'

      - name: ZAP Full Scan
        uses: zaproxy/action-full-scan@v0.10.0
        with:
          target: 'https://staging.example.com'
          rules_file_name: '.zap/rules.tsv'
          cmd_options: '-a -j'

      - name: Upload ZAP Report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: zap-report
          path: report_html.html

# .zap/rules.tsv - Configure scan rules
# WARN = warning only, FAIL = fail the build
# ID    Action
10021   WARN    # X-Content-Type-Options Missing
10038   FAIL    # Content Security Policy Missing
40012   FAIL    # Cross-Site Scripting (Reflected)
40014   FAIL    # Cross-Site Scripting (Persistent)
90019   FAIL    # Server Side Code Injection
90020   FAIL    # Remote OS Command Injection
```

### 3.4 WHEN implementing secure Dockerfile

```dockerfile
# ❌ WRONG - Insecure Dockerfile
FROM node:latest
COPY . .
RUN npm install
USER root
EXPOSE 80
CMD ["npm", "start"]

# ✅ CORRECT - Hardened multi-stage Dockerfile
# Build stage
FROM node:20-alpine AS builder

# Create non-root user for build
RUN addgroup -g 1001 appgroup && \
    adduser -u 1001 -G appgroup -D appuser

WORKDIR /app

# Copy only dependency files first (layer caching)
COPY --chown=appuser:appgroup package*.json ./

# Install dependencies with locked versions
RUN npm ci --only=production --ignore-scripts && \
    npm cache clean --force

# Copy source code
COPY --chown=appuser:appgroup . .

# Build application
RUN npm run build

# Production stage
FROM gcr.io/distroless/nodejs20-debian12 AS production

# Copy only necessary files from builder
COPY --from=builder /app/dist /app/dist
COPY --from=builder /app/node_modules /app/node_modules
COPY --from=builder /app/package.json /app/package.json

WORKDIR /app

# Use non-root user (distroless default is nonroot)
USER nonroot:nonroot

# Expose non-privileged port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD ["/nodejs/bin/node", "-e", "require('http').get('http://localhost:8080/health')"]

# Run application
CMD ["dist/index.js"]

# Security labels
LABEL org.opencontainers.image.source="https://github.com/myorg/myapp"
LABEL org.opencontainers.image.description="My secure application"
LABEL org.opencontainers.image.licenses="MIT"
```

### 3.5 WHEN implementing secrets rotation

```python
# ❌ WRONG - Static secrets
import os
DB_PASSWORD = os.environ["DB_PASSWORD"]  # Never rotated!

# ✅ CORRECT - Dynamic secrets with Vault
from hvac import Client as VaultClient
from functools import lru_cache
from datetime import datetime, timedelta
import threading

class SecretManager:
    def __init__(self, vault_addr: str, role: str):
        self.client = VaultClient(url=vault_addr)
        self.role = role
        self._cache: dict[str, tuple[str, datetime]] = {}
        self._lock = threading.Lock()

        # Authenticate with Kubernetes service account
        self._authenticate_kubernetes()

    def _authenticate_kubernetes(self):
        """Authenticate using Kubernetes service account."""
        with open('/var/run/secrets/kubernetes.io/serviceaccount/token') as f:
            jwt = f.read()

        self.client.auth.kubernetes.login(
            role=self.role,
            jwt=jwt,
            mount_point='kubernetes',
        )

    def get_database_credentials(self) -> tuple[str, str]:
        """Get dynamic database credentials."""
        return self._get_dynamic_secret('database/creds/myapp-role')

    def _get_dynamic_secret(self, path: str) -> tuple[str, str]:
        """Get dynamic secret with automatic rotation."""
        with self._lock:
            if path in self._cache:
                secret, expiry = self._cache[path]
                if datetime.now() < expiry:
                    return secret

            # Fetch new credentials
            response = self.client.secrets.database.generate_credentials(
                name=path.split('/')[-1],
                mount_point='database',
            )

            username = response['data']['username']
            password = response['data']['password']
            lease_duration = response['lease_duration']

            # Cache with buffer before expiry
            expiry = datetime.now() + timedelta(seconds=lease_duration * 0.8)
            self._cache[path] = ((username, password), expiry)

            return username, password


# Kubernetes deployment with Vault sidecar
"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    metadata:
      annotations:
        vault.hashicorp.com/agent-inject: "true"
        vault.hashicorp.com/role: "myapp"
        vault.hashicorp.com/agent-inject-secret-db: "database/creds/myapp-role"
        vault.hashicorp.com/agent-inject-template-db: |
          {{- with secret "database/creds/myapp-role" -}}
          export DB_USER="{{ .Data.username }}"
          export DB_PASSWORD="{{ .Data.password }}"
          {{- end }}
    spec:
      serviceAccountName: myapp
      containers:
        - name: myapp
          image: myapp:latest
"""
```

### 3.6 WHEN implementing compliance as code

```python
# ❌ WRONG - Manual compliance checks
# Run checklist manually before each release

# ✅ CORRECT - Automated compliance with Open Policy Agent
# policy/compliance.rego
package compliance

import future.keywords.in

# CIS Kubernetes Benchmark checks
deny[msg] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    not container.securityContext.runAsNonRoot
    msg := sprintf("Container %s must set runAsNonRoot", [container.name])
}

deny[msg] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    container.securityContext.privileged
    msg := sprintf("Container %s must not be privileged", [container.name])
}

# SOC2 controls
deny[msg] {
    input.kind == "Deployment"
    not input.spec.template.spec.serviceAccountName
    msg := "Deployments must specify a service account"
}

deny[msg] {
    input.kind == "Service"
    input.spec.type == "LoadBalancer"
    not input.metadata.annotations["service.beta.kubernetes.io/aws-load-balancer-internal"]
    msg := "LoadBalancer services must be internal"
}

# PCI-DSS requirements
deny[msg] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    env := container.env[_]
    contains(lower(env.name), "password")
    env.value != null
    msg := sprintf("Container %s has hardcoded password in env", [container.name])
}

# Generate compliance report
compliance_report = {
    "passed": count([r | r := deny[_]; false]),
    "failed": count(deny),
    "violations": deny,
    "timestamp": time.now_ns(),
    "frameworks": ["CIS", "SOC2", "PCI-DSS"],
}
```

---

## 4. Anti-Patterns

**NEVER:**
- Deploy without security scanning
- Skip image signing
- Use `latest` tags in production
- Run containers as root
- Hardcode secrets in manifests or code
- Skip SBOM generation
- Deploy without network policies
- Use mutable infrastructure
- Disable security policies for "convenience"
- Skip audit logging

---

## 5. Testing

**ALWAYS test security controls:**

```bash
#!/bin/bash
# security-pipeline-test.sh
set -euo pipefail

echo "=== Testing Security Pipeline ==="

# Test 1: Secret scanning catches secrets
echo "Test 1: Secret scanning..."
if echo 'API_KEY="sk-test123"' | gitleaks detect --no-git -v 2>/dev/null; then
    echo "FAIL: Secret not detected"
    exit 1
fi
echo "PASS: Secret detected"

# Test 2: Container scanning catches vulnerabilities
echo "Test 2: Container scanning..."
trivy image --severity CRITICAL --exit-code 1 alpine:3.10 2>/dev/null && {
    echo "FAIL: Vulnerable image not flagged"
    exit 1
}
echo "PASS: Vulnerable image flagged"

# Test 3: Policy enforcement blocks non-compliant manifests
echo "Test 3: Policy enforcement..."
cat <<EOF | kubectl apply --dry-run=server -f - 2>&1 | grep -q "denied"
apiVersion: v1
kind: Pod
metadata:
  name: test-privileged
spec:
  containers:
    - name: test
      image: nginx
      securityContext:
        privileged: true
EOF
echo "PASS: Privileged container blocked"

# Test 4: Image signature verification
echo "Test 4: Signature verification..."
if cosign verify --key cosign.pub ghcr.io/myorg/myapp:latest; then
    echo "PASS: Signature verified"
else
    echo "FAIL: Signature verification failed"
    exit 1
fi

echo "=== All Security Tests Passed ==="
```

---

## 6. Pre-Generation Checklist

**BEFORE generating any DevSecOps code:**

- [ ] Secret scanning in pre-commit hooks
- [ ] SAST integrated in CI pipeline
- [ ] Dependency scanning with vulnerability checks
- [ ] Container images scanned before push
- [ ] Images signed with Sigstore/Cosign
- [ ] SBOM generated for all builds
- [ ] Policy enforcement (Kyverno/Gatekeeper)
- [ ] DAST testing in staging
- [ ] Secrets from external managers (Vault/ESO)
- [ ] Audit logging enabled
- [ ] Network policies default deny
- [ ] Compliance checks automated

---

**Performance**: Quality over speed. Verify all code examples compile. Never skip security checks. See `template-references/performance-notes.md` for full guidelines.