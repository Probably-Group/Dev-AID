# Advanced DevSecOps Patterns

This document contains advanced implementation patterns for DevSecOps engineering.

## Pattern 1: SLSA Provenance and Supply Chain Security

### Use Case
Implementing SLSA Level 3 provenance for containerized applications with cryptographic verification and transparency logging.

### Implementation

```yaml
# .github/workflows/slsa-provenance.yml
name: SLSA3 Build

on:
  push:
    tags: ['v*']

permissions: read-all

jobs:
  build:
    permissions:
      id-token: write
      packages: write
    outputs:
      digest: ${{ steps.build.outputs.digest }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Generate SBOM
        uses: anchore/sbom-action@v0.15.0
        with:
          format: spdx-json

      - name: Build and push
        id: build
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.ref_name }}
          provenance: true
          sbom: true

  provenance:
    needs: [build]
    permissions:
      id-token: write
      actions: read
      packages: write
    uses: slsa-framework/slsa-github-generator/.github/workflows/generator_container_slsa3.yml@v1.9.0
    with:
      image: ghcr.io/${{ github.repository }}
      digest: ${{ needs.build.outputs.digest }}
```

### Trade-offs

**Pros**:
- Cryptographic proof of build integrity
- Transparency logging in Rekor
- Supply chain attack resistance
- Attestation verification at deployment

**Cons**:
- Additional build time (1-2 minutes)
- Requires keyless signing infrastructure
- Complexity in verification workflows
- GitHub Actions specific implementation

---

## Pattern 2: Kubernetes Admission Controller with Kyverno

### Use Case
Policy enforcement for image signatures, security contexts, and compliance requirements using declarative policies.

### Implementation

```yaml
# kyverno/verify-images.yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-image-signatures
  annotations:
    policies.kyverno.io/category: Supply Chain Security
    policies.kyverno.io/severity: critical
spec:
  validationFailureAction: Enforce
  background: false
  rules:
    - name: verify-signature
      match:
        any:
        - resources:
            kinds: [Pod]
      verifyImages:
      - imageReferences:
        - "ghcr.io/example/*"
        attestors:
        - count: 1
          entries:
          - keyless:
              subject: "https://github.com/example/*"
              issuer: "https://token.actions.githubusercontent.com"
              rekor:
                url: https://rekor.sigstore.dev
---
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-security-context
spec:
  validationFailureAction: Enforce
  rules:
    - name: non-root-required
      match:
        any:
        - resources:
            kinds: [Pod]
      validate:
        message: "Containers must run as non-root"
        pattern:
          spec:
            securityContext:
              runAsNonRoot: true
            containers:
            - securityContext:
                runAsNonRoot: true
                readOnlyRootFilesystem: true
                capabilities:
                  drop: [ALL]
```

### Trade-offs

**Pros**:
- Declarative policy as code
- Real-time admission control
- No code changes required
- Centralized security enforcement
- Audit mode for testing

**Cons**:
- Cluster-wide deployment required
- Learning curve for Rego/CEL
- Performance impact on API server
- Policy conflicts require debugging

---

## Pattern 3: Multi-Cloud Secret Rotation

### Use Case
Automated secret rotation across multiple cloud providers with zero-downtime updates.

### Implementation

```yaml
# k8s/external-secret-rotation.yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
  namespace: production
spec:
  provider:
    vault:
      server: "https://vault.example.com"
      path: "secret"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "app-role"
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: app-secrets
  namespace: production
spec:
  refreshInterval: 1h  # Auto-refresh hourly
  secretStoreRef:
    name: vault-backend
  target:
    name: app-secrets
    creationPolicy: Owner
    template:
      type: Opaque
      data:
        DATABASE_URL: "postgresql://{{ .username }}:{{ .password }}@db:5432/app"
        API_KEY: "{{ .api_key }}"
  data:
    - secretKey: username
      remoteRef:
        key: app/database
        property: username
    - secretKey: password
      remoteRef:
        key: app/database
        property: password
    - secretKey: api_key
      remoteRef:
        key: app/api
        property: key
```

```python
# scripts/rotate-secrets.py
#!/usr/bin/env python3
"""
Automated secret rotation workflow
"""
import hvac
import time
from datetime import datetime, timedelta

def rotate_database_password(vault_client, role_name):
    """Rotate database password using Vault dynamic secrets"""

    # Request new credentials
    new_creds = vault_client.secrets.database.generate_credentials(
        name=role_name,
        ttl="24h"
    )

    # Store in Vault
    vault_client.secrets.kv.v2.create_or_update_secret(
        path="app/database",
        secret={
            "username": new_creds["data"]["username"],
            "password": new_creds["data"]["password"],
            "rotated_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
        }
    )

    print(f"✅ Rotated database credentials: {new_creds['data']['username']}")

    # External Secrets Operator will automatically sync within refreshInterval
    return new_creds

def main():
    client = hvac.Client(url="https://vault.example.com")
    client.auth.kubernetes.login(role="rotation-service")

    # Rotate all secrets
    rotate_database_password(client, "app-db-role")

if __name__ == "__main__":
    main()
```

### Trade-offs

**Pros**:
- Zero-downtime rotation
- Automatic synchronization
- Centralized secret management
- Audit trail in Vault
- Multi-cloud support

**Cons**:
- External Secrets Operator dependency
- Vault infrastructure required
- Refresh interval latency
- Network dependency for secret access

---

## Pattern 4: Progressive Security Rollout

### Use Case
Gradually enforce security policies across environments without breaking production.

### Implementation

```yaml
# kyverno/progressive-policy.yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: progressive-security
  annotations:
    policies.kyverno.io/description: |
      Progressive rollout: Audit in dev, enforce in staging/prod
spec:
  validationFailureAction: "{{ request.object.metadata.namespace == 'production' && 'Enforce' || 'Audit' }}"
  rules:
    - name: require-resource-limits
      match:
        any:
        - resources:
            kinds: [Pod]
            namespaces: [development, staging, production]
      validate:
        message: "Resource limits required for CPU and memory"
        pattern:
          spec:
            containers:
            - resources:
                limits:
                  memory: "?*"
                  cpu: "?*"
```

```bash
# scripts/progressive-rollout.sh
#!/bin/bash
# Progressive security policy rollout

POLICY="require-resource-limits"

echo "Phase 1: Audit mode in all environments"
kubectl patch clusterpolicy $POLICY --type=merge -p '
  spec:
    validationFailureAction: Audit
'

sleep 7d  # Monitor for a week

echo "Phase 2: Enforce in development"
kubectl patch clusterpolicy $POLICY --type=merge -p '
  spec:
    validationFailureAction: Enforce
' --namespace=development

sleep 7d  # Monitor for a week

echo "Phase 3: Enforce in staging"
kubectl patch clusterpolicy $POLICY --type=merge -p '
  spec:
    validationFailureAction: Enforce
' --namespace=staging

sleep 7d  # Monitor for a week

echo "Phase 4: Enforce in production"
kubectl patch clusterpolicy $POLICY --type=merge -p '
  spec:
    validationFailureAction: Enforce
' --namespace=production

echo "✅ Progressive rollout complete"
```

### Trade-offs

**Pros**:
- Risk mitigation through gradual rollout
- Time to fix issues before production
- Metrics collection at each phase
- Rollback capability

**Cons**:
- Extended deployment timeline
- Requires monitoring infrastructure
- Manual intervention between phases
- Environment drift during rollout

---

## Pattern 5: Container Image Build Cache Optimization

### Use Case
Dramatically reduce build times using aggressive layer caching and multi-stage builds.

### Implementation

```dockerfile
# Dockerfile - Advanced multi-stage with cache optimization
# syntax=docker/dockerfile:1.4

# Stage 1: Dependencies cache
FROM node:20-alpine AS deps
WORKDIR /app
# Copy only dependency files to maximize cache hits
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --only=production

# Stage 2: Build cache
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN --mount=type=cache,target=/root/.npm \
    --mount=type=cache,target=/app/.next/cache \
    npm run build

# Stage 3: Security scanning layer
FROM aquasec/trivy:latest AS scanner
COPY --from=builder /app /scan
RUN trivy fs --severity HIGH,CRITICAL --exit-code 1 /scan

# Stage 4: Runtime
FROM gcr.io/distroless/nodejs20-debian12:nonroot
COPY --from=builder --chown=nonroot:nonroot /app/dist /app/dist
COPY --from=builder --chown=nonroot:nonroot /app/node_modules /app/node_modules
WORKDIR /app
USER nonroot
CMD ["dist/server.js"]
```

```yaml
# .github/workflows/optimized-build.yml
name: Optimized Container Build

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: docker/setup-buildx-action@v3

      - name: Cache Docker layers
        uses: actions/cache@v4
        with:
          path: /tmp/.buildx-cache
          key: buildx-${{ github.sha }}
          restore-keys: |
            buildx-

      - name: Build with cache
        uses: docker/build-push-action@v5
        with:
          context: .
          cache-from: |
            type=local,src=/tmp/.buildx-cache
            type=registry,ref=ghcr.io/${{ github.repository }}:cache
          cache-to: |
            type=local,dest=/tmp/.buildx-cache-new,mode=max
            type=registry,ref=ghcr.io/${{ github.repository }}:cache,mode=max
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}

      # Prevent cache from growing indefinitely
      - name: Rotate cache
        run: |
          rm -rf /tmp/.buildx-cache
          mv /tmp/.buildx-cache-new /tmp/.buildx-cache
```

### Trade-offs

**Pros**:
- 80-90% faster builds on cache hits
- Reduced network transfer
- Lower CI costs
- Parallel layer building

**Cons**:
- Cache invalidation complexity
- Storage costs for cache
- Debugging cache issues
- Requires BuildKit

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Security Scanning in Production Only

**Problem**: Waiting until production deployment to scan for vulnerabilities allows insecure code to reach critical environments.

**Bad Example**:
```yaml
# ❌ DANGER: Only scan in production
deploy-production:
  steps:
    - run: kubectl apply -f k8s/
    - run: trivy image app:latest  # Too late!
```

**Better Approach**:
```yaml
# ✅ Shift-left: Scan early in pipeline
security-gates:
  steps:
    - run: semgrep --error
    - run: trivy image --severity HIGH,CRITICAL --exit-code 1

deploy-production:
  needs: security-gates  # Blocked until gates pass
  steps:
    - run: kubectl apply -f k8s/
```

**Why Better**: Security issues caught in development cost 10x less to fix than in production, and prevent security incidents.

---

### Anti-Pattern 2: Shared Service Account Tokens

**Problem**: Using the same service account token across multiple services violates least privilege and makes credential rotation impossible.

**Bad Example**:
```yaml
# ❌ All services use same token
apiVersion: v1
kind: ServiceAccount
metadata:
  name: shared-sa
---
apiVersion: v1
kind: Pod
metadata:
  name: app-1
spec:
  serviceAccountName: shared-sa  # Shared token
---
apiVersion: v1
kind: Pod
metadata:
  name: app-2
spec:
  serviceAccountName: shared-sa  # Same token!
```

**Better Approach**:
```yaml
# ✅ Dedicated service account per service
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-1-sa
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-2-sa
---
apiVersion: v1
kind: Pod
metadata:
  name: app-1
spec:
  serviceAccountName: app-1-sa
---
apiVersion: v1
kind: Pod
metadata:
  name: app-2
spec:
  serviceAccountName: app-2-sa
```

**Why Better**: Isolated credentials enable precise RBAC, easier rotation, and blast radius limitation during compromise.

---

### Anti-Pattern 3: No Fail-Fast for Security Gates

**Problem**: Continuing CI/CD pipeline execution when security gates fail allows insecure code to progress.

**Bad Example**:
```yaml
# ❌ DANGER: continue-on-error allows failures
security:
  steps:
    - run: semgrep --error
      continue-on-error: true  # Ignores failures!
    - run: trivy image app
      continue-on-error: true  # Ignores CVEs!

deploy:
  steps:
    - run: kubectl apply -f k8s/  # Deploys anyway!
```

**Better Approach**:
```yaml
# ✅ Fail fast on security issues
security:
  steps:
    - run: semgrep --error  # Fails pipeline on issues
    - run: trivy image --severity HIGH,CRITICAL --exit-code 1  # Fails on CVEs

deploy:
  needs: security  # Only runs if security passes
  steps:
    - run: kubectl apply -f k8s/
```

**Why Better**: Fail-fast prevents insecure code deployment and forces developers to address security issues immediately.
