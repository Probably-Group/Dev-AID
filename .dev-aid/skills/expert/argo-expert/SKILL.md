---
name: argo-expert
version: 2.0.0
description: "GitOps with ArgoCD, Argo Workflows, and Argo Rollouts for Kubernetes continuous delivery and progressive deployments. Use when configuring ArgoCD Applications, writing Argo Workflow templates, setting up progressive rollouts, or debugging GitOps sync issues. Do NOT use for general CI/CD pipeline design without ArgoCD (use cicd-expert)."
compatibility: "ArgoCD 2.8+, Kubernetes 1.28+"
risk_level: HIGH
token_budget: 4500
---
# Argo Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.2 Security Patterns (security rules)

**CWE-200: Sensitive Information Exposure (CVE-2025-55190, CVSS 10.0)**
- Do not: Allow low-privileged users `clusters, update` permissions
- Instead: Restrict cluster access via RBAC, use `destinations` and `clusterResourceWhitelist`

**CWE-287: Improper Authentication (CVE-2024-37152)**
- Do not: Expose `/api/v1/settings` without authentication
- Instead: Require auth on all endpoints, upgrade to patched versions

**CWE-312: Cleartext Storage of Secrets**
- Do not: Store secrets in Git repos or rely on `last-applied-configuration`
- Instead: Use External Secrets Operator, Sealed Secrets, or Vault

**CWE-862: Missing Authorization**
- Do not: Rely solely on namespace patterns when sharding is enabled
- Instead: Verify RBAC at namespace AND application level

**CWE-307: Brute Force**
- Do not: Deploy without rate limiting (crash resets login counters)
- Instead: Network-level rate limiting, monitor crash-restart patterns

---

## 1. Security Principles

### 1.1 RBAC and Service Accounts (CWE-250)

**Principle:** Minimize permissions. Use dedicated service accounts with least privilege.

```yaml
# ❌ WRONG - Overly permissive
apiVersion: v1
kind: ServiceAccount
metadata:
  name: argo-workflow
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: argo-admin
roleRef:
  kind: ClusterRole
  name: cluster-admin  # Too permissive!
subjects:
  - kind: ServiceAccount
    name: argo-workflow

# ✅ CORRECT - Least privilege RBAC
apiVersion: v1
kind: ServiceAccount
metadata:
  name: argo-workflow
  namespace: argo
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: argo-workflow-role
  namespace: argo
rules:
  - apiGroups: [""]
    resources: ["pods", "pods/log"]
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["configmaps"]
    verbs: ["get"]
  - apiGroups: ["argoproj.io"]
    resources: ["workflows", "workflowtemplates"]
    verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: argo-workflow-binding
  namespace: argo
roleRef:
  kind: Role
  name: argo-workflow-role
subjects:
  - kind: ServiceAccount
    name: argo-workflow
    namespace: argo
```

### 1.2 Secret Management (CWE-798)

**Principle:** Never store secrets in Git. Use External Secrets or Sealed Secrets.

```yaml
# ❌ WRONG - Secret in plain Git
apiVersion: v1
kind: Secret
metadata:
  name: git-credentials
stringData:
  password: my-secret-password  # Will be in Git history!

# ✅ CORRECT - External Secrets Operator
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: git-credentials
  namespace: argocd
spec:
  refreshInterval: 1h
  secretStoreRef:
    kind: ClusterSecretStore
    name: vault-backend
  target:
    name: git-credentials
    creationPolicy: Owner
  data:
    - secretKey: password
      remoteRef:
        key: secret/data/argocd
        property: git-password
```

### 1.3 Network Policies (CWE-284)

**Principle:** Restrict network access for Argo components.

### 1.4 Image Security (CWE-829)

**Principle:** Use signed images. Pin image digests, not tags.

### 1.5 Sync Policy Safety (CWE-732)

**Principle:** Disable auto-pruning for production. Require manual sync for destructive changes.

### 1.6 SSO and Authentication (CWE-306)

**Principle:** Always configure SSO. Disable local admin in production.

---

## 2. Version Requirements

Use these minimum versions:

```yaml
# ArgoCD
argocd: v2.10.0+
# Argo Workflows
argo-workflows: v3.5.0+
# Argo Rollouts
argo-rollouts: v1.6.0+
# Argo Events
argo-events: v1.9.0+
```

---

## 3. Code Patterns

### 3.1 WHEN setting up ArgoCD Application

```yaml
# ❌ WRONG - No sync policy, auto-prune enabled
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
spec:
  destination:
    namespace: default
    server: https://kubernetes.default.svc
  source:
    repoURL: https://github.com/org/repo
    path: manifests
  syncPolicy:
    automated:
      prune: true  # Dangerous!
      selfHeal: true

# ✅ CORRECT - Production-safe ArgoCD Application
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
  labels:
    app.kubernetes.io/name: my-app
    app.kubernetes.io/part-of: platform
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: production  # Use AppProjects!

  source:
    repoURL: https://github.com/org/repo.git
    targetRevision: v1.2.3  # Pin to tag, not HEAD
    path: manifests/production

    # Helm values override
    helm:
      valueFiles:
        - values-production.yaml
      parameters:
        - name: image.tag
          value: "v1.2.3"

  destination:
    server: https://kubernetes.default.svc
    namespace: my-app

  syncPolicy:
    automated:
      prune: false  # Manual prune for production
      selfHeal: true
      allowEmpty: false
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
      - PruneLast=true
      - RespectIgnoreDifferences=true
      - ApplyOutOfSyncOnly=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m

  ignoreDifferences:
    - group: apps
      kind: Deployment
      jsonPointers:
        - /spec/replicas  # Allow HPA to manage replicas

  revisionHistoryLimit: 10
```

### 3.2 WHEN creating AppProjects

```yaml
# ❌ WRONG - Default project with no restrictions
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: default
spec:
  sourceRepos:
    - '*'  # Any repo!
  destinations:
    - namespace: '*'
      server: '*'  # Any cluster/namespace!

# ✅ CORRECT - Restricted AppProject
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: production
  namespace: argocd
spec:
  description: Production applications

  # Allowed source repositories
  sourceRepos:
    - 'https://github.com/myorg/*'
    - 'https://charts.helm.sh/stable'

  # Allowed destinations
  destinations:
    - namespace: 'prod-*'
      server: https://kubernetes.default.svc

  # Allowed cluster resources
  clusterResourceWhitelist:
    - group: ''
      kind: Namespace
    - group: 'rbac.authorization.k8s.io'
      kind: ClusterRole
    - group: 'rbac.authorization.k8s.io'
      kind: ClusterRoleBinding

  # Denied resources (never sync these)
  namespaceResourceBlacklist:
    - group: ''
      kind: ResourceQuota
    - group: ''
      kind: LimitRange

  # Allowed namespace resources
  namespaceResourceWhitelist:
    - group: '*'
      kind: '*'

  # Role definitions
  roles:
    - name: developer
      description: Developer access
      policies:
        - p, proj:production:developer, applications, get, production/*, allow
        - p, proj:production:developer, applications, sync, production/*, allow
      groups:
        - developers

    - name: admin
      description: Admin access
      policies:
        - p, proj:production:admin, applications, *, production/*, allow
      groups:
        - platform-admins

  # Sync windows (maintenance windows)
  syncWindows:
    - kind: deny
      schedule: '0 22 * * *'  # Deny syncs 10 PM - 6 AM
      duration: 8h
      applications:
        - '*'
    - kind: allow
      schedule: '0 10 * * 1-5'  # Allow weekdays 10 AM
      duration: 8h
      manualSync: true
      applications:
        - '*'
```

### 3.3 WHEN creating Argo Workflows

```yaml
# ❌ WRONG - No security context, unlimited resources
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  name: build-pipeline
spec:
  entrypoint: build
  templates:
    - name: build
      container:
        image: docker:latest  # Mutable tag!
        command: [docker, build, .]

# ✅ CORRECT - Secure Argo Workflow
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: build-pipeline-
  namespace: argo
  labels:
    workflows.argoproj.io/archive-strategy: "true"
spec:
  entrypoint: main
  serviceAccountName: workflow-sa

  # Security settings
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000

  # Pod-level settings
  podGC:
    strategy: OnPodCompletion
    deleteDelayDuration: 600s

  # TTL for completed workflows
  ttlStrategy:
    secondsAfterCompletion: 3600
    secondsAfterSuccess: 3600
    secondsAfterFailure: 86400

  # Resource defaults
  podSpecPatch: |
    containers:
      - name: main
        resources:
          limits:
            memory: 512Mi
            cpu: 500m
          requests:
            memory: 256Mi
            cpu: 100m

  # Artifact storage
  artifactRepositoryRef:
    configMap: artifact-repositories
    key: default-artifact-repository

  # Arguments
  arguments:
    parameters:
      - name: git-revision
        value: "main"
      - name: image-tag
        value: "latest"

  templates:
    - name: main
      dag:
        tasks:
          - name: checkout
            template: git-checkout
            arguments:
              parameters:
                - name: revision
                  value: "{{workflow.parameters.git-revision}}"

          - name: test
            template: run-tests
            dependencies: [checkout]

          - name: build
            template: build-image
            dependencies: [test]

    - name: git-checkout
      inputs:
        parameters:
          - name: revision
      container:
        image: alpine/git:v2.43.0@sha256:abc123...  # Pin digest
        command: [sh, -c]
        args:
          - |
            git clone --depth 1 --branch {{inputs.parameters.revision}} \
              https://github.com/org/repo.git /workspace
        workingDir: /workspace
        securityContext:
          readOnlyRootFilesystem: true
          allowPrivilegeEscalation: false
        volumeMounts:
          - name: workspace
            mountPath: /workspace

    - name: run-tests
      container:
        image: node:20-alpine@sha256:def456...
        command: [npm, test]
        workingDir: /workspace
        securityContext:
          readOnlyRootFilesystem: true
          allowPrivilegeEscalation: false
        volumeMounts:
          - name: workspace
            mountPath: /workspace

    - name: build-image
      container:
        image: gcr.io/kaniko-project/executor:v1.19.0@sha256:ghi789...
        args:
          - --dockerfile=Dockerfile
          - --context=/workspace
          - --destination=registry.example.com/app:{{workflow.parameters.image-tag}}
          - --cache=true
        securityContext:
          readOnlyRootFilesystem: true
          allowPrivilegeEscalation: false
        volumeMounts:
          - name: workspace
            mountPath: /workspace
          - name: docker-config
            mountPath: /kaniko/.docker

  volumes:
    - name: workspace
      emptyDir: {}
    - name: docker-config
      secret:
        secretName: docker-registry-credentials
```

### 3.4 WHEN implementing Argo Rollouts

```yaml
# ❌ WRONG - Immediate full rollout
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-app
spec:
  replicas: 10
  strategy:
    canary:
      steps:
        - setWeight: 100  # Immediate full deployment!

# ✅ CORRECT - Progressive delivery with analysis
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-app
  namespace: production
spec:
  replicas: 10

  selector:
    matchLabels:
      app: my-app

  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: app
          image: registry.example.com/app:v1.2.3
          ports:
            - containerPort: 8080
          livenessProbe:
            httpGet:
              path: /health/live
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
          resources:
            limits:
              memory: 512Mi
              cpu: 500m
            requests:
              memory: 256Mi
              cpu: 100m

  strategy:
    canary:
      # Traffic management
      canaryService: my-app-canary
      stableService: my-app-stable

      trafficRouting:
        istio:
          virtualService:
            name: my-app-vsvc
            routes:
              - primary

      # Progressive steps
      steps:
        - setWeight: 5
        - pause: { duration: 5m }

        - setWeight: 10
        - analysis:
            templates:
              - templateName: success-rate
            args:
              - name: service-name
                value: my-app-canary

        - setWeight: 25
        - pause: { duration: 10m }

        - setWeight: 50
        - analysis:
            templates:
              - templateName: latency-check

        - setWeight: 75
        - pause: { duration: 15m }

        - setWeight: 100

      # Anti-affinity for canary/stable
      antiAffinity:
        requiredDuringSchedulingIgnoredDuringExecution: {}

      # Abort conditions
      abortScaleDownDelaySeconds: 30

      # Analysis on background
      analysis:
        templates:
          - templateName: continuous-success-rate
        startingStep: 2
---
# Analysis Template
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  args:
    - name: service-name
  metrics:
    - name: success-rate
      interval: 30s
      count: 10
      successCondition: result[0] >= 0.95
      failureLimit: 3
      provider:
        prometheus:
          address: http://prometheus:9090
          query: |
            sum(rate(http_requests_total{
              service="{{args.service-name}}",
              status=~"2.."
            }[5m])) /
            sum(rate(http_requests_total{
              service="{{args.service-name}}"
            }[5m]))
```

### 3.5 WHEN configuring ArgoCD SSO

```yaml
# ❌ WRONG - Local admin enabled, no SSO
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-cm
data:
  admin.enabled: "true"
  # No OIDC config

# ✅ CORRECT - SSO with OIDC, admin disabled
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-cm
  namespace: argocd
data:
  # Disable local admin
  admin.enabled: "false"

  # OIDC configuration
  oidc.config: |
    name: Okta
    issuer: https://your-org.okta.com
    clientID: $argocd-oidc-secret:oidc.clientId
    clientSecret: $argocd-oidc-secret:oidc.clientSecret
    requestedScopes:
      - openid
      - profile
      - email
      - groups
    requestedIDTokenClaims:
      groups:
        essential: true

  # URL configuration
  url: https://argocd.example.com

  # Dex disabled when using direct OIDC
  dex.config: ""
---
# RBAC configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-rbac-cm
  namespace: argocd
data:
  policy.default: role:readonly

  policy.csv: |
    # Admins can do anything
    g, platform-admins, role:admin

    # Developers can sync their apps
    p, role:developer, applications, get, */*, allow
    p, role:developer, applications, sync, */*, allow
    p, role:developer, applications, action/*, */*, allow
    p, role:developer, logs, get, */*, allow
    g, developers, role:developer

    # Viewers can only read
    p, role:viewer, applications, get, */*, allow
    p, role:viewer, logs, get, */*, allow
    g, viewers, role:viewer

  scopes: '[groups, email]'
```

---

## 4. Anti-Patterns

Do not:
- Use `cluster-admin` for Argo service accounts
- Store secrets in Git (use External Secrets)
- Enable auto-prune in production without approval
- Use mutable image tags (`:latest`)
- Skip AnalysisTemplates for Rollouts
- Disable SSO in production
- Allow `*` in AppProject destinations
- Skip sync windows for production

---

## 5. Testing

**ALWAYS test GitOps configurations:**

```bash
#!/bin/bash
# Test ArgoCD manifests before commit

set -euo pipefail

# Validate YAML syntax
echo "Validating YAML..."
# ... (additional test cases follow same pattern)
```

---

## 6. Pre-Generation Checklist

Before generating any Argo configurations:

- [ ] Service accounts use least-privilege RBAC
- [ ] Secrets use External Secrets or Sealed Secrets
- [ ] Images pinned by digest, not tag
- [ ] AppProjects restrict source repos and destinations
- [ ] Auto-prune disabled for production
- [ ] Sync windows configured for maintenance
- [ ] SSO configured, local admin disabled
- [ ] AnalysisTemplates defined for Rollouts
- [ ] Network policies restrict Argo components
- [ ] Pod security contexts enforce non-root

---
