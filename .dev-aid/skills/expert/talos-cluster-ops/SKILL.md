---
name: talos-cluster-ops
version: 2.0.0
description: "Kubernetes cluster operations on Talos Linux including troubleshooting, health monitoring, upgrades, and workload debugging. Use when diagnosing pod crashes, node issues, cluster health, Cilium networking, Longhorn storage, or ArgoCD sync failures on Talos clusters. Do NOT use for Talos machine config generation or OS-level configuration (use talos-os-expert)."
compatibility: "Kubernetes 1.28+, talosctl, kubectl"
risk_level: HIGH
token_budget: 3000
---
# Talos Cluster Ops - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.2 Security Patterns (security rules)

**CWE-256: Unprotected Credentials Storage**
- Do not: Store `talosconfig` or cluster secrets in unencrypted Git repos
- Instead: Encrypt with SOPS, store in secure vaults, never commit secrets

**CWE-306: Missing API Authentication**
- Do not: Expose Talos API (port 50000) without mTLS authentication
- Instead: Use cluster ID/secret tokens, keep discovery tokens secure

**CWE-284: Improper Access Control**
- Do not: Use VIP for `talosctl` access (single point of compromise)
- Instead: VIP for `kubectl` only; distribute `talosctl` across control plane nodes

**CWE-693: Protection Mechanism Failure**
- Do not: Disable control plane taints for workload scheduling
- Instead: Maintain control plane isolation, use dedicated worker nodes

---

## 1. Security Principles

### 1.1 Credential Security (CWE-798, CWE-522)

**Principle:** Never expose talosconfig, kubeconfig, or bootstrap tokens. Use short-lived credentials.

```bash
# ❌ WRONG - Credentials in shell history
talosctl --talosconfig /path/to/talosconfig --nodes 192.168.1.10 health

# ✅ CORRECT - Environment variable
export TALOSCONFIG=/path/to/talosconfig
talosctl --nodes 192.168.1.10 health

# ❌ WRONG - Long-lived admin kubeconfig
kubectl --kubeconfig admin.kubeconfig get pods

# ✅ CORRECT - Service account with RBAC
kubectl create serviceaccount monitoring -n monitoring
kubectl create rolebinding monitoring --role=pod-reader --serviceaccount=monitoring:monitoring
```

### 1.2 Network Policy Default Deny (CWE-284)

**Principle:** Implement zero-trust networking. Default deny all traffic, explicitly allow required paths.

```yaml
# ❌ WRONG - No network policies (all traffic allowed)
apiVersion: v1
kind: Namespace
metadata:
  name: production

# ✅ CORRECT - Default deny with explicit allows
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: default-deny
  namespace: production
spec:
  endpointSelector: {}
  ingress:
    - {}
  egress:
    - {}
---
# Allow specific traffic
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: allow-api-to-db
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      app: database
  ingress:
    - fromEndpoints:
        - matchLabels:
            app: api
      toPorts:
        - ports:
            - port: "5432"
              protocol: TCP
```

### 1.3 Pod Security Standards (CWE-250)

**Principle:** Enforce least privilege. No root, read-only filesystem, drop capabilities.

```yaml
# ❌ WRONG - Privileged container
spec:
  containers:
    - name: app
      securityContext:
        privileged: true

# ✅ CORRECT - Restricted security context
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 65534
    fsGroup: 65534
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: app
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop:
            - ALL
      resources:
        limits:
          memory: "256Mi"
          cpu: "500m"
        requests:
          memory: "128Mi"
          cpu: "100m"
```

### 1.4 Secret Management (CWE-312)

**Principle:** Never store secrets in Git. Use External Secrets, Sealed Secrets, or SOPS.

```yaml
# ❌ WRONG - Plaintext secret in Git
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
stringData:
  password: "super-secret-password"

# ✅ CORRECT - External Secrets from Vault
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: ClusterSecretStore
  target:
    name: db-credentials
  data:
    - secretKey: password
      remoteRef:
        key: secret/data/production/database
        property: password
```

---

## 2. Version Requirements

```yaml
# Talos versions - check compatibility matrix
talos: ">=1.6.0"
kubernetes: ">=1.29.0"

# Key components
cilium: ">=1.15.0"
longhorn: ">=1.6.0"
argocd: ">=2.10.0"
```

---

## 3. Code Patterns

### WHEN troubleshooting pod crashes, use structured investigation

```bash
# ❌ WRONG - Random commands without context
kubectl logs pod-name
kubectl describe pod pod-name

# ✅ CORRECT - Structured investigation
#!/bin/bash
set -euo pipefail

investigate_pod() {
    local namespace=$1
    local pod=$2

    echo "=== Pod Status ==="
    kubectl get pod "$pod" -n "$namespace" -o wide

    echo "=== Pod Events ==="
    kubectl get events -n "$namespace" \
        --field-selector "involvedObject.name=$pod" \
        --sort-by='.lastTimestamp'

    echo "=== Container Status ==="
    kubectl get pod "$pod" -n "$namespace" -o jsonpath='{range .status.containerStatuses[*]}
Container: {.name}
  Ready: {.ready}
  Restart Count: {.restartCount}
  State: {.state}
  Last State: {.lastState}
{end}'

    echo "=== Recent Logs (last restart) ==="
    kubectl logs "$pod" -n "$namespace" --previous --tail=100 2>/dev/null || \
        kubectl logs "$pod" -n "$namespace" --tail=100

    echo "=== Resource Usage ==="
    kubectl top pod "$pod" -n "$namespace" --containers 2>/dev/null || echo "Metrics unavailable"
}
```

### WHEN checking cluster health, verify all components

```bash
# ❌ WRONG - Only checking nodes
kubectl get nodes

# ✅ CORRECT - Comprehensive health check
#!/bin/bash
set -euo pipefail

check_cluster_health() {
    local failed=0

    echo "=== Talos Node Health ==="
    for node in $(talosctl get members -o json | jq -r '.[].spec.addresses[0]'); do
        if ! talosctl --nodes "$node" health --wait-timeout 30s 2>/dev/null; then
            echo "FAIL: Node $node unhealthy"
            ((failed++))
        fi
    done

    echo "=== Kubernetes Node Status ==="
    kubectl get nodes -o custom-columns=\
'NAME:.metadata.name,STATUS:.status.conditions[?(@.type=="Ready")].status,VERSION:.status.nodeInfo.kubeletVersion'

    echo "=== System Pods ==="
    kubectl get pods -n kube-system -o wide | grep -v Running && ((failed++)) || true

    echo "=== Cilium Status ==="
    cilium status --wait 2>/dev/null || ((failed++))

    echo "=== Longhorn Status ==="
    kubectl get nodes.longhorn.io -o custom-columns=\
'NAME:.metadata.name,READY:.status.conditions[?(@.type=="Ready")].status,SCHEDULABLE:.status.conditions[?(@.type=="Schedulable")].status'

    echo "=== ArgoCD Applications ==="
    kubectl get applications -n argocd -o custom-columns=\
'NAME:.metadata.name,SYNC:.status.sync.status,HEALTH:.status.health.status'

    if [[ $failed -gt 0 ]]; then
        echo "CLUSTER UNHEALTHY: $failed issues found"
        return 1
    fi
    echo "CLUSTER HEALTHY"
}
```

### WHEN investigating Cilium networking issues, use Hubble

```bash
# ❌ WRONG - Guessing at network issues
kubectl logs -n kube-system -l app.kubernetes.io/name=cilium

# ✅ CORRECT - Structured network debugging
#!/bin/bash
set -euo pipefail

debug_cilium_connectivity() {
    local src_namespace=$1
    local src_pod=$2
    local dst_namespace=$3
    local dst_service=$4

    echo "=== Cilium Endpoint Status ==="
    kubectl get ciliumendpoints -n "$src_namespace" "$src_pod" -o yaml

    echo "=== Network Policy Evaluation ==="
    cilium policy trace \
        --src-k8s-pod "$src_namespace:$src_pod" \
        --dst-k8s-pod "$dst_namespace:$dst_service"

    echo "=== Hubble Flow Observation (30s) ==="
    hubble observe \
        --namespace "$src_namespace" \
        --pod "$src_pod" \
        --protocol TCP \
        --verdict DROPPED \
        --last 100

    echo "=== Service Endpoints ==="
    kubectl get endpoints "$dst_service" -n "$dst_namespace" -o yaml
}
```

### WHEN handling Longhorn storage issues, check replicas and nodes

```bash
# ❌ WRONG - Just checking PVC status
kubectl get pvc

# ✅ CORRECT - Full storage investigation
#!/bin/bash
set -euo pipefail

investigate_storage() {
    local pvc_name=$1
    local namespace=$2

    echo "=== PVC Status ==="
    kubectl get pvc "$pvc_name" -n "$namespace" -o yaml

    echo "=== Bound PV ==="
    local pv=$(kubectl get pvc "$pvc_name" -n "$namespace" -o jsonpath='{.spec.volumeName}')
    kubectl get pv "$pv" -o yaml

    echo "=== Longhorn Volume ==="
    local volume=$(kubectl get pv "$pv" -o jsonpath='{.spec.csi.volumeHandle}')
    kubectl get volumes.longhorn.io "$volume" -n longhorn-system -o yaml

    echo "=== Volume Replicas ==="
    kubectl get replicas.longhorn.io -n longhorn-system \
        -l longhornvolume="$volume" \
        -o custom-columns='NAME:.metadata.name,NODE:.spec.nodeID,MODE:.status.currentState,SIZE:.status.currentSize'

    echo "=== Node Disk Status ==="
    kubectl get nodes.longhorn.io -n longhorn-system -o yaml | \
        yq '.items[].status.diskStatus'
}
```

### WHEN performing rolling updates, use proper draining

```bash
# ❌ WRONG - Force delete and recreate
kubectl delete pod app-0 --force --grace-period=0

# ✅ CORRECT - Graceful rolling update with PDB
#!/bin/bash
set -euo pipefail

safe_node_maintenance() {
    local node=$1

    # Check for PDBs
    echo "=== Checking Pod Disruption Budgets ==="
    kubectl get pdb --all-namespaces

    # Cordon node
    echo "=== Cordoning Node ==="
    kubectl cordon "$node"

    # Drain with safety checks
    echo "=== Draining Node ==="
    kubectl drain "$node" \
        --ignore-daemonsets \
        --delete-emptydir-data \
        --pod-selector='app!=critical-singleton' \
        --timeout=300s

    # Wait for workloads to stabilize
    echo "=== Waiting for Deployments ==="
    kubectl rollout status deployment --all-namespaces --timeout=300s

    # Perform maintenance on Talos
    echo "=== Talos Maintenance ==="
    talosctl --nodes "$node" upgrade --preserve

    # Uncordon
    echo "=== Uncordoning Node ==="
    kubectl uncordon "$node"
}
```

---

## 4. Anti-Patterns

Do not:
- Store talosconfig/kubeconfig in Git repositories
- Run containers as root or privileged
- Skip network policies (default allow-all)
- Use `kubectl delete --force` on stateful workloads
- Ignore Pod Disruption Budgets during maintenance
- Deploy without resource limits
- Store secrets in ConfigMaps or environment variables directly
- Skip Hubble when debugging network issues

---

## 5. Testing

```bash
# Cluster health validation script
#!/bin/bash
set -euo pipefail

test_cluster_operations() {
    local failed=0

# ... (additional test cases follow same pattern)
```

---

## 6. Pre-Generation Checklist

Before generating Talos/K8s operations code:

- [ ] Credentials from environment, not hardcoded
- [ ] Network policies enforce zero-trust (default deny)
- [ ] Pod security contexts enforce least privilege
- [ ] Secrets use External Secrets or Sealed Secrets
- [ ] Resource limits defined for all containers
- [ ] Pod Disruption Budgets protect stateful workloads
- [ ] Hubble enabled for network observability
- [ ] Longhorn replicas configured for HA
- [ ] Maintenance scripts include proper draining

---
