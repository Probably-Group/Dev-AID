---
name: devsecops-expert
version: 2.0.0
description: "DevSecOps practices with shift-left security automation, SAST/DAST pipeline integration, supply chain security, and compliance as code. Use when embedding security scanning in CI/CD, implementing SBOM generation, configuring dependency vulnerability checks, or designing security gate policies. Do NOT use for application-level security patterns like OWASP Top 10 remediation (use appsec-expert)."
compatibility: "GitHub Actions or GitLab CI"
risk_level: HIGH
token_budget: 2000
---
# DevSecOps Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.2 Security Patterns (security rules)

**CWE-1035: SAST Bypass**
- Do not: Skip SAST for "small changes"
- Instead: SAST on every PR, block merge on high severity

**CWE-937: Vulnerable Dependencies**
- Do not: Ignore dependency vulnerability alerts
- Instead: Automated scanning, SLA for patching by severity

**CWE-829: Supply Chain Attacks**
- Do not: Trust transitive dependencies blindly
- Instead: SBOM generation, signature verification, reproducible builds

---

## 1. Security Principles

### 1.1 Shift-Left Security (CWE-1395)

**Principle:** Integrate security testing early in the pipeline. Fail fast on vulnerabilities.

```yaml
# WRONG - Security only at the end
stages:
  - build
  - test
  - deploy
  - security_scan  # Too late!

# CORRECT - Security at every stage
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
# WRONG - No verification
- run: npm install

# CORRECT - Locked, verified dependencies
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
# WRONG - Secrets in manifests
env:
  - name: DB_PASSWORD
    value: "secretpassword123"

# CORRECT - External Secrets Operator
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

```yaml
# WRONG - Running as root with all capabilities
spec:
  containers:
    - name: app
      securityContext:
        privileged: true

# CORRECT - Non-root with minimal capabilities
spec:
  securityContext:
    runAsNonRoot: true
  containers:
    - name: app
      securityContext:
        runAsNonRoot: true
        allowPrivilegeEscalation: false
        capabilities:
          drop: [ALL]
        readOnlyRootFilesystem: true
```

### 1.5 Defense in Depth (CWE-693)

**Principle:** Multiple security layers. Network policies, runtime protection, WAF.

```yaml
# WRONG - No network segmentation
# All pods can talk to all pods

# CORRECT - Default deny with explicit allow
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
```

### 1.6 Audit Logging (CWE-778)

**Principle:** Log all security-relevant events. Immutable audit trail.

---

## 2. Version Requirements

Use these minimum versions:

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

Six-stage pipeline: preflight (secret scanning) -> SAST/dependency scan -> build with SBOM
-> container scan (Trivy + Grype) -> sign with Cosign -> deploy with policy enforcement.
Pin actions to commit SHAs; set minimal `permissions`; use OIDC for keyless signing.

```yaml
# WRONG - Insecure pipeline
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

# CORRECT - See references/secure_pipeline.yml for full 6-stage pipeline
# Key elements: pinned SHAs, minimal permissions, OIDC id-token
permissions:
  contents: read
  security-events: write
  id-token: write
```

See `references/secure_pipeline.yml` for complete example.

### 3.2 WHEN implementing Kyverno policies

Enforce image signature verification (keyless Sigstore), require non-root security context
with dropped capabilities, mandate resource limits, block privileged containers, and
auto-generate default-deny NetworkPolicies for new namespaces.

See `references/kyverno_policies.yml` for complete example.

### 3.3 WHEN implementing DAST with OWASP ZAP

Trigger after staging deployment via `workflow_run`. Health-check wait loop, then run
ZAP baseline + full scan. Configure severity rules in `.zap/rules.tsv` (WARN vs FAIL).

See `references/dast_zap.yml` for complete example.

### 3.4 WHEN implementing secure Dockerfile

Multi-stage build: alpine builder with non-root user and locked deps, distroless production
image. Read-only filesystem, non-privileged port, HEALTHCHECK, OCI labels.

```dockerfile
# WRONG - Insecure Dockerfile
FROM node:latest
COPY . .
RUN npm install
USER root
EXPOSE 80
CMD ["npm", "start"]

# CORRECT - Hardened multi-stage build (see references/secure_dockerfile for full version)
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production --ignore-scripts

FROM gcr.io/distroless/nodejs20-debian12 AS production
COPY --from=builder /app/dist /app/dist
USER nonroot:nonroot
EXPOSE 8080
CMD ["dist/index.js"]
```

See `references/secure_dockerfile` for complete example.

### 3.5 WHEN implementing secrets rotation

Dynamic credentials via HashiCorp Vault with K8s service account auth. Thread-safe
credential cache with TTL buffer. Deploy with Vault Agent sidecar annotations.

```python
# WRONG - Static secrets
DB_PASSWORD = os.environ["DB_PASSWORD"]  # Never rotated!

# CORRECT - Dynamic secrets with Vault (see references/secret_rotation.py)
# - Authenticate with K8s service account
# - Fetch dynamic DB credentials with lease TTL
# - Thread-safe cache with 80% TTL buffer
# - Vault Agent sidecar for transparent injection
```

See `references/secret_rotation.py` for complete example.

### 3.6 WHEN implementing compliance as code

Automated policy checks with Open Policy Agent (Rego). CIS Kubernetes Benchmark
(runAsNonRoot, no privileged), SOC2 (service accounts), PCI-DSS (no hardcoded passwords).
Generates compliance report with violation counts and framework coverage.

See `references/compliance_rego.rego` for complete example.

---

## 4. Anti-Patterns

Do not:
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

Test security controls with integration tests covering: secret scanning detection,
container vulnerability scanning, policy enforcement (privileged pod denial),
and image signature verification.

See `references/security_pipeline_test.sh` for complete test script.

---

## 6. Pre-Generation Checklist

Before generating DevSecOps code:

- [ ] Secret scanning in pre-commit hooks
- [ ] SAST + dependency scanning integrated in CI pipeline
- [ ] Container images scanned and signed before push
- [ ] Policy enforcement active (Kyverno/Gatekeeper)
- [ ] Secrets from external managers (Vault/ESO), never hardcoded
