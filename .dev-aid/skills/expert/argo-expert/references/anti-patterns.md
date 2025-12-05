# Common Mistakes

## 8.1 Argo CD Anti-Patterns

**Mistake 1: Auto-sync without prune in production**
```yaml
# WRONG: Can leave orphaned resources
syncPolicy:
  automated:
    selfHeal: true
    # Missing prune: true

# CORRECT:
syncPolicy:
  automated:
    prune: true
    selfHeal: true
  syncOptions:
    - PruneLast=true  # Delete resources last
```

**Mistake 2: Ignoring sync waves**
```yaml
# WRONG: Random deployment order
# Database and app deploy simultaneously, app crashes

# CORRECT: Use sync waves
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "1"  # Database first
---
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "5"  # App second
```

**Mistake 3: No resource finalizers**
```yaml
# WRONG: Deletion leaves resources behind
metadata:
  name: my-app

# CORRECT: Cascade deletion
metadata:
  name: my-app
  finalizers:
    - resources-finalizer.argocd.argoproj.io
```

## 8.2 Argo Workflows Anti-Patterns

**Mistake 4: No resource limits**
```yaml
# WRONG: Can exhaust cluster resources
container:
  image: myapp:latest
  # No limits!

# CORRECT: Always set limits
container:
  image: myapp:latest
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"
```

**Mistake 5: Infinite retry loops**
```yaml
# WRONG: Retries forever on permanent failure
retryStrategy:
  limit: 999
  retryPolicy: "Always"

# CORRECT: Limit retries, use backoff
retryStrategy:
  limit: 3
  retryPolicy: "OnTransientError"
  backoff:
    duration: "10s"
    factor: 2
    maxDuration: "5m"
```

## 8.3 Argo Rollouts Anti-Patterns

**Mistake 6: No analysis templates**
```yaml
# WRONG: Blind canary without validation
strategy:
  canary:
    steps:
      - setWeight: 50
      - pause: {duration: 5m}

# CORRECT: Automated analysis
strategy:
  canary:
    steps:
      - setWeight: 10
      - analysis:
          templates:
            - templateName: success-rate
            - templateName: error-rate
      - setWeight: 50
```

**Mistake 7: Immediate full rollout**
```yaml
# WRONG: No gradual increase
steps:
  - setWeight: 100  # All traffic at once!

# CORRECT: Progressive steps
steps:
  - setWeight: 10
  - pause: {duration: 2m}
  - setWeight: 25
  - pause: {duration: 5m}
  - setWeight: 50
  - pause: {duration: 10m}
```

## 8.4 Security Mistakes

**Mistake 8: Storing secrets in Git**
```yaml
# WRONG: Plain secrets in Git repo
apiVersion: v1
kind: Secret
data:
  password: cGFzc3dvcmQxMjM=  # base64 is NOT encryption!

# CORRECT: Use Sealed Secrets or External Secrets
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
spec:
  secretStoreRef:
    name: vault-backend
```

**Mistake 9: Overly permissive RBAC**
```yaml
# WRONG: Admin for everyone
p, role:developer, *, *, */*, allow

# CORRECT: Least privilege
p, role:developer, applications, get, team-*/*, allow
p, role:developer, applications, sync, team-*/*, allow
```

**Mistake 10: No image verification**
```yaml
# WRONG: Deploy any image
spec:
  containers:
    - image: myregistry/app:latest  # No verification!

# CORRECT: Verify signatures
# Use admission controller + cosign
# Or Argo CD image updater with signature checks
```
