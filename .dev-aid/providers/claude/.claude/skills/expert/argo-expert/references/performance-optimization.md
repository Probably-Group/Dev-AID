# Performance Patterns

## 6.1 Workflow Caching

**Good: Use memoization for expensive steps**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
spec:
  templates:
    - name: expensive-build
      memoize:
        key: "{{inputs.parameters.commit-sha}}"
        maxAge: "24h"
        cache:
          configMap:
            name: build-cache
      container:
        image: build-image:latest
        command: [make, build]
```

**Bad: Rebuild everything every time**
```yaml
# No caching - rebuilds from scratch on every run
- name: expensive-build
  container:
    image: build-image:latest
    command: [make, build]
```

## 6.2 Parallelism Tuning

**Good: Configure appropriate parallelism limits**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
spec:
  parallelism: 10  # Limit concurrent pods
  templates:
    - name: fan-out
      parallelism: 5  # Template-level limit
      steps:
        - - name: parallel-task
            template: worker
            withItems: "{{workflow.parameters.items}}"
```

**Bad: Unbounded parallelism exhausts resources**
```yaml
# No limits - can spawn thousands of pods
spec:
  templates:
    - name: fan-out
      steps:
        - - name: parallel-task
            template: worker
            withItems: "{{workflow.parameters.large-list}}"  # 10000 items!
```

## 6.3 Artifact Optimization

**Good: Use artifact compression and GC**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
spec:
  artifactGC:
    strategy: OnWorkflowDeletion
  templates:
    - name: generate-artifact
      outputs:
        artifacts:
          - name: output
            path: /tmp/output
            archive:
              tar:
                compressionLevel: 6  # Compress large artifacts
            s3:
              key: "{{workflow.name}}/output.tar.gz"
```

**Bad: Uncompressed artifacts fill storage**
```yaml
# No compression, no GC - artifacts accumulate forever
outputs:
  artifacts:
    - name: output
      path: /tmp/large-output
      s3:
        key: "artifacts/output"
```

## 6.4 Sync Window Management

**Good: Configure sync windows for controlled deployments**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
spec:
  syncWindows:
    # Allow syncs during business hours
    - kind: allow
      schedule: "0 9 * * 1-5"
      duration: 10h
      applications:
        - '*'
    # Deny syncs during maintenance
    - kind: deny
      schedule: "0 2 * * 0"
      duration: 4h
      applications:
        - '*-production'
      manualSync: true  # Allow manual override
    # Rate limit auto-sync
    - kind: allow
      schedule: "*/30 * * * *"
      duration: 5m
      applications:
        - '*'
```

**Bad: Unrestricted syncs cause deployment storms**
```yaml
# No sync windows - apps sync continuously
spec:
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
  # Missing sync windows = potential deployment storms
```

## 6.5 Resource Quotas

**Good: Set resource limits for workflows and controllers**
```yaml
# Workflow resource limits
apiVersion: argoproj.io/v1alpha1
kind: Workflow
spec:
  podSpecPatch: |
    containers:
      - name: main
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
  activeDeadlineSeconds: 3600  # 1 hour timeout

---
# Argo CD controller tuning
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-cmd-params-cm
data:
  controller.status.processors: "20"
  controller.operation.processors: "10"
  controller.self.heal.timeout.seconds: "5"
  controller.repo.server.timeout.seconds: "60"
```

**Bad: No limits cause resource exhaustion**
```yaml
# No resource limits - can exhaust cluster
spec:
  templates:
    - name: memory-hog
      container:
        image: myapp:latest
        # Missing resource limits!
```

## 6.6 ApplicationSet Rate Limiting

**Good: Control ApplicationSet generation rate**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
spec:
  generators:
    - git:
        repoURL: https://github.com/org/config
        revision: HEAD
        files:
          - path: "apps/**/config.json"
  strategy:
    type: RollingSync
    rollingSync:
      steps:
        - matchExpressions:
            - key: env
              operator: In
              values: [staging]
        - matchExpressions:
            - key: env
              operator: In
              values: [production]
          maxUpdate: 25%  # Only update 25% at a time
```

**Bad: Update all applications simultaneously**
```yaml
# No rolling strategy - updates all apps at once
spec:
  generators:
    - git:
        # Generates 100+ applications
  # Missing strategy = all apps update simultaneously
```

## 6.7 Repo Server Optimization

**Good: Configure repo server caching and scaling**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: argocd-repo-server
spec:
  replicas: 3  # Scale for high load
  template:
    spec:
      containers:
        - name: argocd-repo-server
          env:
            - name: ARGOCD_EXEC_TIMEOUT
              value: "3m"
            - name: ARGOCD_GIT_ATTEMPTS_COUNT
              value: "3"
          resources:
            requests:
              cpu: 500m
              memory: 1Gi
            limits:
              cpu: 2
              memory: 4Gi
          volumeMounts:
            - name: repo-cache
              mountPath: /tmp
      volumes:
        - name: repo-cache
          emptyDir:
            medium: Memory
            sizeLimit: 2Gi
```

**Bad: Default repo server config for large deployments**
```yaml
# Single replica, no tuning - becomes bottleneck
spec:
  replicas: 1
  template:
    spec:
      containers:
        - name: argocd-repo-server
          # Default settings - slow for 100+ apps
```
