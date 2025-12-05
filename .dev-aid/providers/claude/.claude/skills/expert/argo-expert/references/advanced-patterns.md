# Top 7 Patterns

## 4.1 App-of-Apps Pattern (Argo CD)

**Use Case**: Manage multiple applications as a single unit, enable self-service app creation

```yaml
# apps/root-app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: root-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/gitops-apps
    targetRevision: main
    path: apps
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

```yaml
# apps/backend-app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: backend-api
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: production
  source:
    repoURL: https://github.com/org/backend-api
    targetRevision: v2.1.0
    path: k8s/overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: backend
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

**Best Practices**:
- Use separate repos for app definitions vs. manifests
- Enable finalizers to cascade deletion
- Set retry policies for transient failures
- Use Projects for RBAC boundaries

## 4.2 ApplicationSet with Multiple Clusters

**Use Case**: Deploy same app to multiple clusters with environment-specific config

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: microservice-rollout
  namespace: argocd
spec:
  generators:
    - matrix:
        generators:
          - git:
              repoURL: https://github.com/org/cluster-config
              revision: HEAD
              files:
                - path: "clusters/**/config.json"
          - list:
              elements:
                - app: payment-service
                  namespace: payments
                - app: order-service
                  namespace: orders
  template:
    metadata:
      name: '{{app}}-{{cluster.name}}'
      labels:
        environment: '{{cluster.environment}}'
        app: '{{app}}'
    spec:
      project: '{{cluster.environment}}'
      source:
        repoURL: https://github.com/org/services
        targetRevision: '{{cluster.targetRevision}}'
        path: '{{app}}/k8s/overlays/{{cluster.environment}}'
      destination:
        server: '{{cluster.server}}'
        namespace: '{{namespace}}'
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
        syncOptions:
          - CreateNamespace=true
          - PruneLast=true
      ignoreDifferences:
        - group: apps
          kind: Deployment
          jsonPointers:
            - /spec/replicas  # Allow HPA to manage replicas
```

**Matrix Generator Benefits**:
- Combine cluster list with app list
- DRY configuration across environments
- Dynamic discovery from Git

## 4.3 Sync Waves & Hooks (Argo CD)

**Use Case**: Control deployment order, run migration jobs

```yaml
# 01-namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: database
  annotations:
    argocd.argoproj.io/sync-wave: "-5"
---
# 02-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
  namespace: database
  annotations:
    argocd.argoproj.io/sync-wave: "-3"
type: Opaque
data:
  password: <base64>
---
# 03-migration-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration-v2
  namespace: database
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/hook-delete-policy: BeforeHookCreation
    argocd.argoproj.io/sync-wave: "0"
spec:
  template:
    spec:
      containers:
        - name: migrate
          image: myapp/migrations:v2.0
          command: ["./migrate", "up"]
      restartPolicy: Never
  backoffLimit: 3
---
# 04-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
  namespace: database
  annotations:
    argocd.argoproj.io/sync-wave: "5"
spec:
  replicas: 3
  template:
    spec:
      containers:
        - name: api
          image: myapp/api:v2.0
```

**Sync Wave Strategy**:
- `-5 to -1`: Infrastructure (namespaces, CRDs, secrets)
- `0`: Migrations, setup jobs
- `1-10`: Applications (databases first, then apps)
- `11+`: Verification, smoke tests

## 4.4 Canary Deployment with Analysis (Argo Rollouts)

**Use Case**: Safe progressive rollout with automated metrics validation

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: payment-api
  namespace: payments
spec:
  replicas: 10
  revisionHistoryLimit: 5
  selector:
    matchLabels:
      app: payment-api
  template:
    metadata:
      labels:
        app: payment-api
    spec:
      containers:
        - name: api
          image: payment-api:v2.1.0
          ports:
            - containerPort: 8080
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
  strategy:
    canary:
      maxSurge: "25%"
      maxUnavailable: 0
      steps:
        - setWeight: 10
        - pause: {duration: 2m}
        - analysis:
            templates:
              - templateName: success-rate
              - templateName: latency-p95
            args:
              - name: service-name
                value: payment-api
        - setWeight: 25
        - pause: {duration: 5m}
        - setWeight: 50
        - pause: {duration: 10m}
        - setWeight: 75
        - pause: {duration: 5m}
      trafficRouting:
        istio:
          virtualService:
            name: payment-api
            routes:
              - primary
      analysis:
        successfulRunHistoryLimit: 5
        unsuccessfulRunHistoryLimit: 3
```

```yaml
# analysis-template.yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
  namespace: payments
spec:
  args:
    - name: service-name
  metrics:
    - name: success-rate
      interval: 1m
      successCondition: result[0] >= 0.95
      failureLimit: 3
      provider:
        prometheus:
          address: http://prometheus.monitoring:9090
          query: |
            sum(rate(http_requests_total{
              service="{{args.service-name}}",
              status=~"2.."
            }[5m]))
            /
            sum(rate(http_requests_total{
              service="{{args.service-name}}"
            }[5m]))
---
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: latency-p95
  namespace: payments
spec:
  args:
    - name: service-name
  metrics:
    - name: latency-p95
      interval: 1m
      successCondition: result[0] < 500
      failureLimit: 3
      provider:
        prometheus:
          address: http://prometheus.monitoring:9090
          query: |
            histogram_quantile(0.95,
              sum(rate(http_request_duration_seconds_bucket{
                service="{{args.service-name}}"
              }[5m])) by (le)
            ) * 1000
```

**Key Features**:
- Gradual traffic shift (10% → 25% → 50% → 75% → 100%)
- Automated analysis at each step
- Auto-rollback on metric failures
- Traffic routing via Istio/NGINX

## 4.5 Workflow DAG with Artifacts (Argo Workflows)

**Use Case**: Complex CI/CD pipeline with artifact passing

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: cicd-pipeline-
  namespace: workflows
spec:
  entrypoint: main
  serviceAccountName: workflow-executor
  volumeClaimTemplates:
    - metadata:
        name: workspace
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 10Gi

  templates:
    - name: main
      dag:
        tasks:
          - name: checkout
            template: git-clone

          - name: unit-tests
            template: run-tests
            dependencies: [checkout]
            arguments:
              parameters:
                - name: test-type
                  value: "unit"

          - name: build-image
            template: docker-build
            dependencies: [unit-tests]

          - name: security-scan
            template: trivy-scan
            dependencies: [build-image]

          - name: integration-tests
            template: run-tests
            dependencies: [build-image]
            arguments:
              parameters:
                - name: test-type
                  value: "integration"

          - name: deploy-staging
            template: deploy
            dependencies: [security-scan, integration-tests]
            arguments:
              parameters:
                - name: environment
                  value: "staging"

          - name: smoke-tests
            template: run-tests
            dependencies: [deploy-staging]
            arguments:
              parameters:
                - name: test-type
                  value: "smoke"

          - name: deploy-production
            template: deploy
            dependencies: [smoke-tests]
            arguments:
              parameters:
                - name: environment
                  value: "production"

    - name: git-clone
      container:
        image: alpine/git:latest
        command: [sh, -c]
        args:
          - |
            git clone https://github.com/org/app.git /workspace/src
            cd /workspace/src && git checkout $GIT_COMMIT
        volumeMounts:
          - name: workspace
            mountPath: /workspace
        env:
          - name: GIT_COMMIT
            value: "{{workflow.parameters.git-commit}}"

    - name: run-tests
      inputs:
        parameters:
          - name: test-type
      container:
        image: myapp/test-runner:latest
        command: [sh, -c]
        args:
          - |
            cd /workspace/src
            make test-{{inputs.parameters.test-type}}
        volumeMounts:
          - name: workspace
            mountPath: /workspace
      outputs:
        artifacts:
          - name: test-results
            path: /workspace/src/test-results
            s3:
              key: "{{workflow.name}}/{{inputs.parameters.test-type}}-results.xml"

    - name: docker-build
      container:
        image: gcr.io/kaniko-project/executor:latest
        args:
          - --context=/workspace/src
          - --dockerfile=/workspace/src/Dockerfile
          - --destination=myregistry/app:{{workflow.parameters.version}}
          - --cache=true
        volumeMounts:
          - name: workspace
            mountPath: /workspace
      outputs:
        parameters:
          - name: image-digest
            valueFrom:
              path: /workspace/digest

    - name: deploy
      inputs:
        parameters:
          - name: environment
      resource:
        action: apply
        manifest: |
          apiVersion: argoproj.io/v1alpha1
          kind: Application
          metadata:
            name: app-{{inputs.parameters.environment}}
            namespace: argocd
          spec:
            project: default
            source:
              repoURL: https://github.com/org/app
              targetRevision: {{workflow.parameters.version}}
              path: k8s/overlays/{{inputs.parameters.environment}}
            destination:
              server: https://kubernetes.default.svc
              namespace: {{inputs.parameters.environment}}
            syncPolicy:
              automated:
                prune: true

  arguments:
    parameters:
      - name: git-commit
        value: "main"
      - name: version
        value: "v1.0.0"
```

**DAG Benefits**:
- Parallel execution where possible
- Artifact passing between steps
- Dependency management
- Failure isolation

## 4.6 Retry Strategies & Error Handling (Argo Workflows)

**Use Case**: Resilient workflows with exponential backoff

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: resilient-pipeline-
spec:
  entrypoint: main
  onExit: cleanup

  templates:
    - name: main
      retryStrategy:
        limit: 3
        retryPolicy: "Always"
        backoff:
          duration: "10s"
          factor: 2
          maxDuration: "5m"
      steps:
        - - name: fetch-data
            template: api-call
            continueOn:
              failed: true

        - - name: process-data
            template: process
            when: "{{steps.fetch-data.status}} == Succeeded"

          - name: fallback
            template: use-cache
            when: "{{steps.fetch-data.status}} != Succeeded"

        - - name: notify
            template: send-notification
            arguments:
              parameters:
                - name: status
                  value: "{{steps.process-data.status}}"

    - name: api-call
      retryStrategy:
        limit: 5
        retryPolicy: "OnError"
        backoff:
          duration: "5s"
          factor: 2
      container:
        image: curlimages/curl:latest
        command: [sh, -c]
        args:
          - |
            curl -f -X GET https://api.example.com/data > /tmp/data.json
            if [ $? -ne 0 ]; then
              echo "API call failed"
              exit 1
            fi
      outputs:
        artifacts:
          - name: data
            path: /tmp/data.json

    - name: cleanup
      container:
        image: alpine:latest
        command: [sh, -c]
        args:
          - |
            echo "Workflow {{workflow.status}}"
            # Send metrics, cleanup resources
```

**Retry Policies**:
- `Always`: Retry on any failure
- `OnError`: Retry on error exit codes
- `OnFailure`: Retry on transient failures
- `OnTransientError`: K8s API errors only

## 4.7 Multi-Cluster Hub-Spoke with AppProject RBAC

**Use Case**: Centralized GitOps management with tenant isolation

```yaml
# Hub cluster: argocd installation
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: team-backend
  namespace: argocd
spec:
  description: Backend team applications

  sourceRepos:
    - https://github.com/org/backend-*

  destinations:
    - namespace: backend-*
      server: https://prod-cluster-1.example.com
    - namespace: backend-*
      server: https://prod-cluster-2.example.com
    - namespace: backend-staging
      server: https://staging-cluster.example.com

  clusterResourceWhitelist:
    - group: ""
      kind: Namespace

  namespaceResourceWhitelist:
    - group: apps
      kind: Deployment
    - group: ""
      kind: Service
    - group: ""
      kind: ConfigMap
    - group: ""
      kind: Secret

  roles:
    - name: developer
      description: Developers can view and sync apps
      policies:
        - p, proj:team-backend:developer, applications, get, team-backend/*, allow
        - p, proj:team-backend:developer, applications, sync, team-backend/*, allow
      groups:
        - backend-devs

    - name: admin
      description: Admins have full control
      policies:
        - p, proj:team-backend:admin, applications, *, team-backend/*, allow
      groups:
        - backend-admins

  syncWindows:
    - kind: deny
      schedule: "0 22 * * *"
      duration: 6h
      applications:
        - '*-production'
      manualSync: true
```

```yaml
# Register remote cluster
apiVersion: v1
kind: Secret
metadata:
  name: prod-cluster-1
  namespace: argocd
  labels:
    argocd.argoproj.io/secret-type: cluster
type: Opaque
stringData:
  name: prod-cluster-1
  server: https://prod-cluster-1.example.com
  config: |
    {
      "bearerToken": "<token>",
      "tlsClientConfig": {
        "insecure": false,
        "caData": "<base64-ca-cert>"
      }
    }
```

**RBAC Strategy**:
- AppProjects enforce boundaries
- SSO groups map to project roles
- Sync windows prevent off-hours changes
- Resource whitelists limit permissions
