# Security Standards

## 5.1 Critical Security Controls

### 1. RBAC Hardening

**Argo CD**:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-rbac-cm
  namespace: argocd
data:
  policy.default: role:readonly
  policy.csv: |
    # Admin role
    p, role:admin, applications, *, */*, allow
    p, role:admin, clusters, *, *, allow
    p, role:admin, repositories, *, *, allow
    g, admins, role:admin

    # Developer role - limited to specific projects
    p, role:developer, applications, get, */*, allow
    p, role:developer, applications, sync, team-*/*, allow
    p, role:developer, applications, override, team-*/*, deny
    g, developers, role:developer

    # CI/CD role - automation only
    p, role:cicd, applications, sync, */*, allow
    p, role:cicd, applications, get, */*, allow
    g, cicd-bot, role:cicd
```

**Argo Workflows**:
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: workflow-executor
  namespace: workflows
rules:
  - apiGroups: [""]
    resources: [pods, pods/log]
    verbs: [get, watch, list]
  - apiGroups: [""]
    resources: [secrets]
    verbs: [get]
  - apiGroups: [argoproj.io]
    resources: [workflows]
    verbs: [get, list, watch, patch]
  # No create/delete permissions
```

### 2. Secret Management

**External Secrets Operator Integration**:
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
  namespace: backend
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: db-credentials
    creationPolicy: Owner
  data:
    - secretKey: password
      remoteRef:
        key: database/production
        property: password
```

**Sealed Secrets for GitOps**:
```bash
# Create sealed secret
kubectl create secret generic api-key \
  --from-literal=key=secret123 \
  --dry-run=client -o yaml | \
kubeseal -o yaml > sealed-api-key.yaml

# Commit sealed-api-key.yaml to Git
# SealedSecret controller decrypts in-cluster
```

### 3. Image Signature Verification

```yaml
# Argo CD with Cosign verification
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-cm
  namespace: argocd
data:
  resource.customizations.signature.argoproj.io_Application: |
    - cosign:
        publicKeyData: |
          -----BEGIN PUBLIC KEY-----
          <your-public-key>
          -----END PUBLIC KEY-----
```

### 4. Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: argocd-server
  namespace: argocd
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: argocd-server
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
      ports:
        - protocol: TCP
          port: 8080
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              name: argocd
      ports:
        - protocol: TCP
          port: 8080
    - to:
        - podSelector:
            matchLabels:
              app.kubernetes.io/name: argocd-repo-server
      ports:
        - protocol: TCP
          port: 8081
```

## 5.2 Supply Chain Security

**Workflow with SBOM & Provenance**:
```yaml
- name: build-secure
  steps:
    - - name: build
        template: kaniko-build

    - - name: generate-sbom
        template: syft-sbom

      - name: sign-image
        template: cosign-sign

    - - name: security-scan
        template: grype-scan

      - name: policy-check
        template: opa-check

- name: syft-sbom
  container:
    image: anchore/syft:latest
    command: [sh, -c]
    args:
      - |
        syft packages myregistry/app:{{workflow.parameters.version}} \
          -o spdx-json > sbom.json
        cosign attach sbom myregistry/app:{{workflow.parameters.version}} \
          --sbom sbom.json

- name: cosign-sign
  container:
    image: gcr.io/projectsigstore/cosign:latest
    command: [sh, -c]
    args:
      - |
        cosign sign --key k8s://argocd/cosign-key \
          myregistry/app:{{workflow.parameters.version}}
```

## 5.3 OWASP Top 10 2025 Mapping

| OWASP ID | Argo Component | Risk | Mitigation |
|----------|---------------|------|------------|
| A01:2025 | Argo CD RBAC | Critical | Project-level RBAC, SSO integration |
| A02:2025 | Secrets in Git | Critical | External Secrets Operator, Sealed Secrets |
| A05:2025 | Argo CD API | High | Disable anonymous access, enforce HTTPS |
| A07:2025 | Image verification | Critical | Cosign signature checks, admission controllers |
| A08:2025 | Workflow logs | Medium | Redact secrets, structured logging |

**Reference**: For complete security examples, CVE analysis, and threat modeling, see `references/argocd-guide.md` (Section 6).
