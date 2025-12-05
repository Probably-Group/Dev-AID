# DevSecOps Security Examples

This document provides comprehensive security examples for DevSecOps implementations.

## 1. Container Security Hardening

### Example 1: Multi-Stage Build with Security Best Practices

**Secure Dockerfile**:
```dockerfile
# Dockerfile - Multi-stage with security hardening
FROM node:20-alpine AS builder
RUN apk update && apk upgrade && apk add --no-cache dumb-init
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
WORKDIR /app
COPY --chown=nodejs:nodejs package*.json ./
RUN npm ci --only=production && npm cache clean --force
COPY --chown=nodejs:nodejs . .

# Distroless runtime
FROM gcr.io/distroless/nodejs20-debian12:nonroot
COPY --from=builder /usr/bin/dumb-init /usr/bin/dumb-init
COPY --from=builder --chown=nonroot:nonroot /app /app
WORKDIR /app
USER nonroot
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["node", "server.js"]
```

**Security Features**:
- ✅ Multi-stage build excludes build tools
- ✅ Distroless base (minimal attack surface)
- ✅ Non-root user (UID 65534)
- ✅ No package manager in final image
- ✅ Process reaper (dumb-init) for zombie prevention
- ✅ Ownership properly set

**Verification**:
```bash
# Test image runs as non-root
docker run --rm app:test id
# Output: uid=65534(nonroot) gid=65534(nonroot)

# Verify no shell access
docker run --rm -it app:test /bin/sh
# Should fail - no shell in distroless
```

---

### Example 2: Kubernetes Pod Security Context

**Hardened Pod Specification**:
```yaml
# k8s/pod-security.yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-app
  labels:
    app: secure-app
spec:
  # Pod-level security context
  securityContext:
    runAsNonRoot: true
    runAsUser: 65534
    fsGroup: 65534
    seccompProfile:
      type: RuntimeDefault

  serviceAccountName: app-sa
  automountServiceAccountToken: false

  containers:
  - name: app
    image: ghcr.io/example/app:v1.0.0
    # Container-level security context
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      runAsNonRoot: true
      capabilities:
        drop: [ALL]

    resources:
      limits:
        memory: "256Mi"
        cpu: "500m"
      requests:
        memory: "128Mi"
        cpu: "250m"

    # Writable volumes for apps that need temp storage
    volumeMounts:
    - name: tmp
      mountPath: /tmp
    - name: cache
      mountPath: /app/.cache

  volumes:
  - name: tmp
    emptyDir:
      sizeLimit: 100Mi
  - name: cache
    emptyDir:
      sizeLimit: 50Mi
```

**Security Controls**:
- ✅ Non-root user enforcement
- ✅ Read-only root filesystem
- ✅ No privilege escalation
- ✅ All capabilities dropped
- ✅ Seccomp profile applied
- ✅ Resource limits set
- ✅ Service account token not mounted
- ✅ Temporary volumes with size limits

---

### Example 3: Network Policy (Zero-Trust)

**Deny-by-Default Network Policy**:
```yaml
# k8s/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-default
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-app-to-database
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: web-app
  policyTypes:
  - Egress
  egress:
  # Allow DNS
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: UDP
      port: 53
  # Allow PostgreSQL
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-ingress-to-app
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: web-app
  policyTypes:
  - Ingress
  ingress:
  # Only allow from ingress controller
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    - podSelector:
        matchLabels:
          app: nginx-ingress
    ports:
    - protocol: TCP
      port: 8080
```

**Zero-Trust Principles**:
- ✅ Default deny all traffic
- ✅ Explicit allow for required paths
- ✅ Least privilege network access
- ✅ Namespace isolation
- ✅ Port-level restrictions

---

## 2. Infrastructure as Code Security

### Example 1: Terraform Security Scanning

**Terraform Configuration with Security Best Practices**:
```hcl
# terraform/s3.tf
resource "aws_s3_bucket" "secure_bucket" {
  bucket = "my-secure-bucket"

  # Prevent accidental deletion
  lifecycle {
    prevent_destroy = true
  }
}

# Block public access
resource "aws_s3_bucket_public_access_block" "secure_bucket" {
  bucket = aws_s3_bucket.secure_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "secure_bucket" {
  bucket = aws_s3_bucket.secure_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

# Enable versioning
resource "aws_s3_bucket_versioning" "secure_bucket" {
  bucket = aws_s3_bucket.secure_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Enable logging
resource "aws_s3_bucket_logging" "secure_bucket" {
  bucket = aws_s3_bucket.secure_bucket.id

  target_bucket = aws_s3_bucket.logs.id
  target_prefix = "s3-access-logs/"
}
```

**CI Pipeline Scanning**:
```yaml
# .gitlab-ci.yml
stages:
  - validate
  - security-scan

terraform-validate:
  stage: validate
  image: hashicorp/terraform:1.6.6
  script:
    - terraform init -backend=false
    - terraform validate
    - terraform fmt -check

checkov-scan:
  stage: security-scan
  image: bridgecrew/checkov:latest
  script:
    - checkov --directory terraform/ \
        --framework terraform \
        --output cli \
        --output junitxml \
        --output-file-path reports/ \
        --hard-fail-on HIGH,CRITICAL

tfsec-scan:
  stage: security-scan
  image: aquasec/tfsec:latest
  script:
    - tfsec terraform/ \
        --minimum-severity HIGH \
        --soft-fail false \
        --format junit > tfsec-report.xml
  artifacts:
    reports:
      junit: tfsec-report.xml

terrascan:
  stage: security-scan
  image: tenable/terrascan:latest
  script:
    - terrascan scan -i terraform \
        -d terraform/ \
        --severity high \
        --non-recursive \
        --verbose
```

---

### Example 2: Policy as Code with OPA

**OPA Policy for Kubernetes**:
```rego
# policies/kubernetes/pod-security.rego
package kubernetes.admission

# Deny privileged containers
deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    container.securityContext.privileged
    msg := sprintf("Privileged container not allowed: %v", [container.name])
}

# Require non-root user
deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    not container.securityContext.runAsNonRoot
    msg := sprintf("Container must run as non-root: %v", [container.name])
}

# Require read-only root filesystem
deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    not container.securityContext.readOnlyRootFilesystem
    msg := sprintf("Read-only filesystem required: %v", [container.name])
}

# Deny host namespaces
deny[msg] {
    input.request.kind.kind == "Pod"
    input.request.object.spec.hostNetwork
    msg := "Host network not allowed"
}

deny[msg] {
    input.request.kind.kind == "Pod"
    input.request.object.spec.hostPID
    msg := "Host PID namespace not allowed"
}

deny[msg] {
    input.request.kind.kind == "Pod"
    input.request.object.spec.hostIPC
    msg := "Host IPC namespace not allowed"
}

# Require resource limits
deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    not container.resources.limits.memory
    msg := sprintf("Memory limit required: %v", [container.name])
}

deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    not container.resources.limits.cpu
    msg := sprintf("CPU limit required: %v", [container.name])
}

# Disallow latest tag
deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    endswith(container.image, ":latest")
    msg := sprintf("Image tag 'latest' not allowed: %v", [container.name])
}

# Require image from approved registry
deny[msg] {
    input.request.kind.kind == "Pod"
    container := input.request.object.spec.containers[_]
    not startswith(container.image, "ghcr.io/approved/")
    msg := sprintf("Image must be from approved registry: %v", [container.image])
}
```

**Testing OPA Policies**:
```bash
# Test policies in CI
conftest test k8s-manifests/ --policy policies/

# Test specific manifest
conftest test k8s/pod.yaml --policy policies/pod-security.rego

# Run policy unit tests
conftest verify policies/

# Generate coverage report
conftest verify --coverage policies/
```

---

## 3. Secrets Management

### Example 1: External Secrets Operator with Vault

**Vault Configuration**:
```hcl
# vault/policies/app-policy.hcl
path "secret/data/app/*" {
  capabilities = ["read"]
}

path "database/creds/app-role" {
  capabilities = ["read"]
}
```

**Kubernetes External Secret**:
```yaml
# k8s/external-secret.yaml
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
          serviceAccountRef:
            name: app-sa
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: app-secrets
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: SecretStore

  target:
    name: app-secrets
    creationPolicy: Owner
    template:
      type: Opaque
      engineVersion: v2
      data:
        DATABASE_URL: "postgresql://{{ .username }}:{{ .password }}@db:5432/app"
        API_KEY: "{{ .api_key }}"
        REDIS_PASSWORD: "{{ .redis_password }}"

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

    - secretKey: redis_password
      remoteRef:
        key: app/redis
        property: password
```

**Application Usage**:
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  template:
    spec:
      serviceAccountName: app-sa
      containers:
      - name: app
        image: ghcr.io/example/app:v1.0.0
        envFrom:
        - secretRef:
            name: app-secrets  # Auto-synced from Vault
```

---

### Example 2: SOPS for Encrypted Secrets in Git

**Encrypted Secret File**:
```yaml
# secrets/production.enc.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: production
stringData:
  database_password: ENC[AES256_GCM,data:encrypted_value,iv:...,tag:...,type:str]
  api_key: ENC[AES256_GCM,data:encrypted_value,iv:...,tag:...,type:str]
```

**SOPS Configuration**:
```yaml
# .sops.yaml
creation_rules:
  - path_regex: secrets/production.*\.yaml$
    kms: 'arn:aws:kms:us-east-1:123456789:key/abc-def-ghi'
    pgp: 'FBC7B9E2A4F9289AC0C1D4843D16CEE4A27381B4'
  - path_regex: secrets/staging.*\.yaml$
    kms: 'arn:aws:kms:us-east-1:123456789:key/staging-key'
```

**Workflow**:
```bash
# Encrypt file
sops --encrypt secrets/production.yaml > secrets/production.enc.yaml

# Edit encrypted file
sops secrets/production.enc.yaml

# Decrypt and apply
sops --decrypt secrets/production.enc.yaml | kubectl apply -f -
```

---

## 4. Security Testing

### Example 1: Automated SAST Testing

**Semgrep Custom Rules**:
```yaml
# .semgrep/sql-injection.yaml
rules:
  - id: sql-injection-format-string
    pattern: |
      f"SELECT * FROM ... WHERE ... {$VAR}"
    message: SQL injection via f-string - use parameterized queries
    severity: ERROR
    languages: [python]
    metadata:
      cwe: "CWE-89: SQL Injection"
      owasp: "A03:2021 - Injection"

  - id: hardcoded-secret
    pattern: |
      $VAR = "AKIA..."
    message: Hardcoded AWS access key detected
    severity: ERROR
    languages: [python, javascript]
```

**CI Pipeline**:
```yaml
# .github/workflows/sast.yml
name: SAST

on: [pull_request]

jobs:
  semgrep:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Semgrep
        uses: semgrep/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/secrets
            p/sql-injection
            .semgrep/
        env:
          SEMGREP_APP_TOKEN: ${{ secrets.SEMGREP_APP_TOKEN }}
```

---

### Example 2: Container Security Scanning

**Trivy Scan in CI**:
```yaml
# .github/workflows/container-scan.yml
name: Container Security Scan

on: [push]

jobs:
  trivy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build image
        run: docker build -t app:${{ github.sha }} .

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@0.16.1
        with:
          image-ref: app:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: 'trivy-results.sarif'

      - name: Generate SBOM
        uses: aquasecurity/trivy-action@0.16.1
        with:
          image-ref: app:${{ github.sha }}
          format: 'spdx-json'
          output: 'sbom.spdx.json'

      - name: Upload SBOM
        uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: sbom.spdx.json
```

---

## Security Checklist

Before deploying DevSecOps pipelines:

### Code Security
- [ ] SAST scanning enabled (Semgrep/CodeQL)
- [ ] Secret scanning enabled (TruffleHog/Gitleaks)
- [ ] SCA for dependencies (Snyk/Dependabot)
- [ ] Pre-commit hooks configured

### Container Security
- [ ] Base image from trusted registry
- [ ] Multi-stage build implemented
- [ ] Non-root user configured
- [ ] Read-only filesystem
- [ ] No secrets in image layers
- [ ] Vulnerability scanning in CI
- [ ] Image signing with Cosign
- [ ] SBOM generated

### Kubernetes Security
- [ ] Pod Security Standards enforced
- [ ] Network policies (deny-by-default)
- [ ] RBAC least privilege
- [ ] Resource limits set
- [ ] Admission controllers active
- [ ] Service mesh for mTLS

### Pipeline Security
- [ ] Branch protection enabled
- [ ] Required status checks
- [ ] Ephemeral build environments
- [ ] No persistent credentials
- [ ] Artifact signing
- [ ] Audit logging enabled

### Infrastructure Security
- [ ] IaC scanning (Checkov/tfsec)
- [ ] Policy as code (OPA/Kyverno)
- [ ] Encryption at rest
- [ ] Encryption in transit
- [ ] Secrets in external store
- [ ] Automated secret rotation
