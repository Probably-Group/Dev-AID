## 3.1 TDD Process for Argo Configurations

Follow this workflow for all Argo implementations:

### Step 1: Write Failing Test First

Create validation workflow to test manifests before deployment:
- **Kubeval**: Validate YAML schema (`kubeval --strict`)
- **Kubeconform**: Verify CRD compliance (`kubeconform -strict`)
- **Dry-run**: Test apply without changes (`kubectl apply --dry-run=server`)

```yaml
# test/validation-workflow.yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
spec:
  entrypoint: validate
  templates:
    - name: validate
      steps:
        - - name: kubeval
            template: schema-check
        - - name: dry-run
            template: apply-test
```

### Step 2: Implement Minimum to Pass

```yaml
# Implement the actual workflow/rollout/application
# Focus on minimal viable configuration first
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-service
  template:
    # Minimal template to pass validation
```

### Step 3: Refactor with Analysis Templates

```yaml
# Add analysis templates for runtime verification
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: deployment-verification
spec:
  metrics:
    - name: pod-ready
      successCondition: result == true
      provider:
        job:
          spec:
            template:
              spec:
                containers:
                  - name: verify
                    image: bitnami/kubectl:latest
                    command: [sh, -c]
                    args:
                      - |
                        # Verify pods are ready
                        kubectl wait --for=condition=ready pod \
                          -l app=my-service --timeout=120s
                restartPolicy: Never
```

### Step 4: Run Full Verification

```bash
# Run all verification commands before committing
# 1. Lint manifests
kubeval --strict manifests/*.yaml
kubeconform -strict manifests/

# 2. Dry-run apply
kubectl apply --dry-run=server -f manifests/

# 3. Test in staging cluster
argocd app sync my-app-staging --dry-run
argocd app wait my-app-staging --health

# 4. Verify rollout status
kubectl argo rollouts status my-service -n staging

# 5. Run analysis
kubectl argo rollouts promote my-service -n staging
```

