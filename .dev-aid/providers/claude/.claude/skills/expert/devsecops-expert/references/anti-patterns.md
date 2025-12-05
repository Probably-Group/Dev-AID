# DevSecOps Anti-Patterns

This document describes common mistakes in DevSecOps implementations and how to avoid them.

## Mistake 1: Hardcoded Secrets

### Problem

Storing secrets directly in code, configuration files, or Kubernetes manifests.

**Bad Example**:
```yaml
# ❌ DANGER: Hardcoded secret in manifest
apiVersion: v1
kind: Secret
metadata:
  name: database-secret
  namespace: production
type: Opaque
stringData:
  password: SuperSecret123!
  api_key: sk_live_1234567890abcdef
```

```python
# ❌ DANGER: Hardcoded in code
DATABASE_URL = "postgresql://admin:password123@db.example.com:5432/app"
API_KEY = "AKIAIOSFODNN7EXAMPLE"
```

### Solution

Use external secret management systems.

**Good Example**:
```yaml
# ✅ External secret store with Vault
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: database-secret
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: database-secret
    creationPolicy: Owner
  data:
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
# ✅ Load from environment (injected by External Secrets Operator)
import os

DATABASE_URL = os.environ["DATABASE_URL"]
API_KEY = os.environ["API_KEY"]
```

### Why This Matters

- Hardcoded secrets end up in git history forever
- Secrets visible to anyone with repository access
- No rotation capability
- Difficult to audit secret access
- Violates compliance requirements (SOC2, PCI-DSS)

---

## Mistake 2: Running Containers as Root

### Problem

Containers running as root user (UID 0) create unnecessary security risks.

**Bad Example**:
```dockerfile
# ❌ DANGER: Runs as root by default
FROM node:20
WORKDIR /app
COPY . .
RUN npm install
CMD ["node", "server.js"]
```

```yaml
# ❌ No security context specified
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
  - name: app
    image: ghcr.io/example/app:latest
```

### Solution

Always run containers as non-root users.

**Good Example**:
```dockerfile
# ✅ Non-root user with minimal image
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .

FROM gcr.io/distroless/nodejs20-debian12:nonroot
COPY --from=builder --chown=nonroot:nonroot /app /app
WORKDIR /app
USER nonroot
CMD ["server.js"]
```

```yaml
# ✅ Enforce non-root with security context
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 65534
    fsGroup: 65534
  containers:
  - name: app
    image: ghcr.io/example/app:latest
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      runAsNonRoot: true
      capabilities:
        drop: [ALL]
```

### Why This Matters

- Root user can escape containers more easily
- Limits damage from container breakout
- Reduces attack surface
- Meets security compliance requirements
- Prevents accidental privilege escalation

---

## Mistake 3: No Security Gates in CI/CD

### Problem

Deploying code without security scanning allows vulnerabilities into production.

**Bad Example**:
```yaml
# ❌ DANGER: Deploy without any security checks
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t app .
      - run: docker push ghcr.io/example/app:latest
      - run: kubectl apply -f k8s/
```

### Solution

Implement multiple security gates that block deployment.

**Good Example**:
```yaml
# ✅ Multi-stage security gates
name: Secure CI/CD Pipeline

on:
  push:
    branches: [main]

jobs:
  security-gates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Gate 1: Secret scanning
      - name: Scan for secrets
        uses: trufflesecurity/trufflehog@v3.63.0
        with:
          extra_args: --fail

      # Gate 2: SAST
      - name: Static analysis
        uses: semgrep/semgrep-action@v1
        with:
          config: p/security-audit

      # Gate 3: SCA
      - name: Dependency scan
        uses: actions/dependency-review-action@v4
        with:
          fail-on-severity: high

      # Gate 4: Container scan
      - run: docker build -t app:${{ github.sha }} .
      - name: Scan image
        uses: aquasecurity/trivy-action@0.16.1
        with:
          image-ref: app:${{ github.sha }}
          severity: 'CRITICAL,HIGH'
          exit-code: '1'

  deploy:
    needs: security-gates  # Only deploy if gates pass
    runs-on: ubuntu-latest
    steps:
      - run: kubectl apply -f k8s/
```

### Why This Matters

- Prevents vulnerable code from reaching production
- Catches issues early when they're cheaper to fix
- Provides audit trail for compliance
- Shifts security left in development lifecycle
- Reduces security incident risk

---

## Mistake 4: Unsigned/Unverified Container Images

### Problem

Deploying container images without signature verification allows malicious images.

**Bad Example**:
```bash
# ❌ No verification of image authenticity
kubectl run app --image=ghcr.io/example/app:latest

# ❌ Could be compromised image, registry poisoning, MITM attack
```

```yaml
# ❌ No admission control to verify signatures
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
  - name: app
    image: ghcr.io/example/app:latest  # Unverified!
```

### Solution

Sign images and verify signatures at admission.

**Good Example**:
```yaml
# ✅ Sign images in CI
name: Build and Sign

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: ghcr.io/example/app:${{ github.sha }}

      - uses: sigstore/cosign-installer@v3
      - name: Sign image
        run: |
          cosign sign --yes \
            ghcr.io/example/app:${{ github.sha }}
```

```yaml
# ✅ Verify signatures with Kyverno
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-image-signatures
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
```

### Why This Matters

- Prevents registry poisoning attacks
- Ensures image provenance
- Protects against MITM attacks
- Meets supply chain security requirements (SLSA)
- Provides audit trail of image origins

---

## Mistake 5: Overly Permissive RBAC

### Problem

Granting excessive permissions to service accounts or users.

**Bad Example**:
```yaml
# ❌ DANGER: Cluster admin for application service account
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: app-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin  # Full cluster access!
subjects:
- kind: ServiceAccount
  name: app-sa
  namespace: production
```

```yaml
# ❌ Wildcard permissions
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: app-role
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
```

### Solution

Apply least privilege principle with minimal, scoped permissions.

**Good Example**:
```yaml
# ✅ Minimal namespace-scoped permissions
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: app-role
  namespace: production
rules:
# Only read specific secret
- apiGroups: [""]
  resources: ["secrets"]
  resourceNames: ["app-secrets"]
  verbs: ["get"]

# Only read configmaps
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: app-binding
  namespace: production
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: app-role
subjects:
- kind: ServiceAccount
  name: app-sa
  namespace: production
```

### Why This Matters

- Limits blast radius during compromise
- Prevents privilege escalation attacks
- Meets compliance requirements
- Reduces accidental misconfigurations
- Easier to audit and maintain

---

## Mistake 6: Using :latest Tag

### Problem

Using `:latest` tag prevents reproducible deployments and bypasses image scanning.

**Bad Example**:
```yaml
# ❌ DANGER: latest tag changes unpredictably
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  template:
    spec:
      containers:
      - name: app
        image: ghcr.io/example/app:latest  # Which version?
        imagePullPolicy: Always  # Pulls on every restart
```

### Solution

Use immutable tags with digest pinning.

**Good Example**:
```yaml
# ✅ Pinned by digest (immutable)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  template:
    spec:
      containers:
      - name: app
        image: ghcr.io/example/app:v1.2.3@sha256:abc123...
        imagePullPolicy: IfNotPresent
```

```yaml
# ✅ Enforce with Kyverno policy
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: disallow-latest-tag
spec:
  validationFailureAction: Enforce
  rules:
    - name: require-image-tag
      match:
        any:
        - resources:
            kinds: [Pod]
      validate:
        message: "Image tag 'latest' is not allowed"
        pattern:
          spec:
            containers:
            - image: "!*:latest"
```

### Why This Matters

- Ensures reproducible deployments
- Allows proper vulnerability scanning
- Enables rollback to known versions
- Prevents unexpected changes
- Required for production stability

---

## Mistake 7: No Resource Limits

### Problem

Containers without resource limits can consume all node resources.

**Bad Example**:
```yaml
# ❌ No resource limits - can OOM node
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
  - name: app
    image: ghcr.io/example/app:v1.0.0
    # No resources specified!
```

### Solution

Always set resource requests and limits.

**Good Example**:
```yaml
# ✅ Resource limits prevent resource exhaustion
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
  - name: app
    image: ghcr.io/example/app:v1.0.0
    resources:
      requests:
        memory: "128Mi"
        cpu: "250m"
      limits:
        memory: "256Mi"
        cpu: "500m"
```

```yaml
# ✅ Enforce with Kyverno policy
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-resource-limits
spec:
  validationFailureAction: Enforce
  rules:
    - name: check-resource-limits
      match:
        any:
        - resources:
            kinds: [Pod]
      validate:
        message: "Resource limits are required"
        pattern:
          spec:
            containers:
            - resources:
                limits:
                  memory: "?*"
                  cpu: "?*"
```

### Why This Matters

- Prevents resource exhaustion attacks
- Enables proper capacity planning
- Improves cluster stability
- Meets production reliability requirements
- Allows fair resource distribution

---

## Mistake 8: Storing Infrastructure State in Version Control

### Problem

Committing Terraform state files exposes sensitive data.

**Bad Example**:
```bash
# ❌ DANGER: State file contains secrets
git add terraform.tfstate
git commit -m "Update infrastructure"
git push
```

```gitignore
# ❌ State not ignored
*.tf
*.tfvars
# terraform.tfstate missing!
```

### Solution

Use remote backends with encryption and state locking.

**Good Example**:
```hcl
# ✅ Remote backend with encryption
terraform {
  backend "s3" {
    bucket         = "terraform-state-prod"
    key            = "app/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
    kms_key_id     = "arn:aws:kms:us-east-1:123456789:key/abc-def"
  }
}
```

```.gitignore
# ✅ Ignore state files
*.tfstate
*.tfstate.*
*.tfvars
.terraform/
```

### Why This Matters

- State files contain plaintext secrets
- Prevents accidental secret exposure
- Enables team collaboration with locking
- Provides state backup and versioning
- Required for production Terraform usage

---

## Mistake 9: No Network Segmentation

### Problem

Flat network allows lateral movement between all pods.

**Bad Example**:
```yaml
# ❌ No NetworkPolicy - all pods can talk to all pods
apiVersion: v1
kind: Namespace
metadata:
  name: production
# No network policies defined!
```

### Solution

Implement deny-by-default network policies.

**Good Example**:
```yaml
# ✅ Deny all traffic by default
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
---
# ✅ Allow only required traffic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-app-to-db
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
  # Allow database only
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
```

### Why This Matters

- Prevents lateral movement during breach
- Limits blast radius of compromised pods
- Enforces zero-trust networking
- Required for multi-tenant security
- Meets compliance requirements

---

## Mistake 10: Ignoring Security Scan Results

### Problem

Running security scans but not acting on findings.

**Bad Example**:
```yaml
# ❌ Scans run but don't block deployment
security-scan:
  steps:
    - run: semgrep --error
      continue-on-error: true  # Ignores failures!

    - run: trivy image app
      continue-on-error: true  # Ignores CVEs!

deploy:
  steps:
    - run: kubectl apply -f k8s/  # Deploys anyway!
```

### Solution

Make security scans blocking with appropriate thresholds.

**Good Example**:
```yaml
# ✅ Security failures block deployment
security-scan:
  steps:
    - run: semgrep --error
      # Fails pipeline on error

    - run: trivy image --severity HIGH,CRITICAL --exit-code 1 app
      # Fails on high/critical CVEs

deploy:
  needs: security-scan  # Only runs if security passes
  steps:
    - run: kubectl apply -f k8s/
```

### Why This Matters

- Prevents vulnerable code in production
- Creates accountability for security issues
- Forces developers to address vulnerabilities
- Meets security compliance requirements
- Reduces security incident risk

---

## Summary

**Top 3 Most Critical Anti-Patterns to Avoid:**

1. **Hardcoded Secrets** - Use external secret stores
2. **No Security Gates** - Implement blocking security scans
3. **Overly Permissive RBAC** - Apply least privilege

**Remember**: Security anti-patterns compound - one mistake often enables others. Fix systematically starting with highest risk.
