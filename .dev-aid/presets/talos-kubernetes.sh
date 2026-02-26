#!/usr/bin/env bash
# Preset: Talos Linux / Kubernetes cluster operations / Cilium CNI

preset_name="talos-kubernetes"
preset_description="Talos Linux cluster operations, bare-metal/VM Kubernetes, Cilium CNI, talosctl management"

# Rules files: newline-delimited "filename|description" pairs
RULES_FILES="talos-config.md|Machine config patches, talosctl commands, system extensions, network config, secure boot
cluster-ops.md|Cluster lifecycle: bootstrap, upgrade, scale, etcd ops, node maintenance, health checks
networking.md|Cilium on Talos: kube-proxy replacement, network policies, Hubble, BGP, LB-IPAM, DNS
cross-service.md|ArgoCD GitOps, storage (Longhorn/Rook-Ceph), sealed-secrets/SOPS, monitoring, talhelper"

# Technology stack entries
TECH_STACK="| OS | Talos Linux 1.9+ |
| Orchestration | Kubernetes 1.32+ |
| CNI | Cilium 1.17+ (kube-proxy replacement) |
| GitOps | ArgoCD |
| Config Gen | talhelper v3 |
| Storage | Longhorn / Rook-Ceph |
| Secrets | SOPS + age / sealed-secrets |
| Monitoring | Prometheus + Grafana |
| CLI | talosctl, kubectl, cilium-cli, hubble |"

# Context loading table entries
CONTEXT_LOADING_TABLE="| **New node / scale cluster** | \`.claude/rules/talos-config.md\`, \`.claude/rules/cluster-ops.md\` |
| **Talos upgrade** | \`.claude/rules/cluster-ops.md\` (Upgrade section) |
| **Network policy change** | \`.claude/rules/networking.md\` |
| **Deploy new workload** | \`.claude/rules/cross-service.md\`, \`.claude/rules/networking.md\` |
| **etcd operations** | \`.claude/rules/cluster-ops.md\` (etcd section) |
| **Debugging** | \`.claude/rules/troubleshooting.md\` |
| **Architecture decisions** | \`docs/decisions/index.md\` |"

# Context groups
CONTEXT_GROUPS='### `talos`
Read: `.claude/rules/talos-config.md`, `talos/`, `talconfig.yaml`

### `cluster`
Read: `.claude/rules/cluster-ops.md`, `.claude/rules/talos-config.md`
After changes: Run `talosctl health`

### `network`
Read: `.claude/rules/networking.md`, `kustomize/infra/cilium/`

### `deploy`
Read: `.claude/rules/cross-service.md`, `kustomize/apps/`

### `debug`
Read: `.claude/rules/troubleshooting.md`'

# Development workflow
WORKFLOW='### Cluster Operations Workflow

All Talos configuration is declarative. Machine configs are generated from `talconfig.yaml`
and applied via `talosctl`.

```bash
# Generate configs from talhelper
talhelper genconfig

# Apply machine config to a node
talosctl apply-config --nodes <ip> --file clusterconfig/<node>.yaml

# Check cluster health
talosctl health --nodes <control-plane-ip>

# View cluster dashboard (live TUI)
talosctl dashboard --nodes <control-plane-ip>

# Check node services
talosctl services --nodes <ip>

# Get cluster members
talosctl get members --nodes <control-plane-ip>

# Check Kubernetes nodes
kubectl get nodes -o wide

# Check Cilium status
cilium status
hubble observe --follow
```

### Change Workflow

1. Edit `talconfig.yaml` or patch files
2. Run `talhelper genconfig` to regenerate configs
3. Diff: `talosctl apply-config --nodes <ip> --file <config> --dry-run`
4. Apply: `talosctl apply-config --nodes <ip> --file <config>`
5. If reboot required: `talosctl reboot --nodes <ip>` (one node at a time)
6. Verify: `talosctl health`

### Deployment Checklist (New Workload)

1. Kustomize manifests in `kustomize/apps/<service>/`
2. ArgoCD Application definition
3. CiliumNetworkPolicy for the namespace
4. Secrets via SOPS/sealed-secrets
5. Monitoring (ServiceMonitor/PodMonitor)
6. Resource limits and health probes'

# Project overview
PROJECT_OVERVIEW="Talos Linux Kubernetes cluster infrastructure. Managed declaratively via talhelper, talosctl, and ArgoCD GitOps."

# Workspace structure
WORKSPACE_STRUCTURE='{{PROJECT_NAME}}/
├── CLAUDE.md
├── .claude/
│   ├── rules/
│   │   ├── talos-config.md
│   │   ├── cluster-ops.md
│   │   ├── networking.md
│   │   ├── cross-service.md
│   │   └── troubleshooting.md
│   ├── hooks/
│   │   └── lint-on-edit.sh
│   ├── memory/
│   │   ├── MEMORY.md
│   │   ├── cluster-state.md
│   │   ├── talos-upgrades.md
│   │   ├── networking-issues.md
│   │   ├── etcd-operations.md
│   │   └── debugging.md
│   └── commands/
│       ├── review.md
│       ├── plan.md
│       ├── cluster-health.md
│       ├── node-status.md
│       └── smoke.md
├── talos/
│   ├── talconfig.yaml       # talhelper config (source of truth)
│   ├── talsecret.sops.yaml  # Encrypted cluster secrets
│   ├── patches/
│   │   ├── global.yaml      # Patches applied to all nodes
│   │   ├── controlplane.yaml
│   │   └── worker.yaml
│   └── clusterconfig/       # Generated configs (gitignored)
├── kustomize/
│   ├── apps/                # Application manifests
│   ├── infra/               # Infrastructure (Cilium, ArgoCD, etc.)
│   └── base/                # Shared base resources
├── docs/
│   ├── plans/
│   │   └── .plan-template.md
│   └── decisions/
│       ├── index.md
│       └── adr-template.md
└── scripts/
    ├── smoke-cluster.sh
    ├── smoke-talos.sh
    └── etcd-snapshot.sh'

# Smoke test scripts: "filename|title|checks_variable_name"
SMOKE_SCRIPTS="smoke-talos.sh|Talos Cluster Health Checks|SMOKE_TALOS_CHECKS
smoke-cluster.sh|Kubernetes & Cilium Health Checks|SMOKE_K8S_CHECKS"

# Smoke test check bodies (referenced by variable name above)
# shellcheck disable=SC2034
SMOKE_TALOS_CHECKS='section "Talos CLI"

if command -v talosctl >/dev/null 2>&1; then
  TALOS_VERSION=$(talosctl version --client 2>/dev/null | grep "Tag:" | awk "{print \$2}" | head -1)
  pass "talosctl installed: ${TALOS_VERSION:-unknown version}"
else
  fail "talosctl not found — install from https://github.com/siderolabs/talos/releases"
fi

if command -v talhelper >/dev/null 2>&1; then
  pass "talhelper installed"
else
  warn "talhelper not found — install: brew install talhelper"
fi

section "Talos Cluster Connectivity"

TALOS_ENDPOINT="${TALOS_ENDPOINT:-}"
if [[ -z "$TALOS_ENDPOINT" ]]; then
  TALOS_ENDPOINT=$(talosctl config info 2>/dev/null | grep "Endpoints:" | awk "{print \$2}" | head -1)
fi

if [[ -n "$TALOS_ENDPOINT" ]]; then
  if talosctl version --nodes "$TALOS_ENDPOINT" --short 2>/dev/null | grep -q "Tag:"; then
    pass "Talos API reachable at $TALOS_ENDPOINT"
  else
    fail "Cannot reach Talos API at $TALOS_ENDPOINT"
  fi
else
  warn "No Talos endpoint configured — set TALOS_ENDPOINT or configure talosctl"
fi

section "Talos Health"

if talosctl health --nodes "$TALOS_ENDPOINT" --wait-timeout 10s 2>/dev/null; then
  pass "talosctl health passed"
else
  warn "talosctl health check failed or timed out"
fi

section "Talos Members"

MEMBER_COUNT=$(talosctl get members --nodes "$TALOS_ENDPOINT" 2>/dev/null | grep -c "Member" || true)
if [[ "$MEMBER_COUNT" -gt 0 ]]; then
  pass "Cluster has $MEMBER_COUNT member(s)"
else
  warn "Could not retrieve cluster members"
fi

section "etcd Health"

ETCD_STATUS=$(talosctl etcd status --nodes "$TALOS_ENDPOINT" 2>/dev/null)
if echo "$ETCD_STATUS" | grep -qi "healthy\|true"; then
  pass "etcd is healthy"
elif [[ -n "$ETCD_STATUS" ]]; then
  warn "etcd status uncertain — review manually: talosctl etcd status"
else
  warn "Could not check etcd status"
fi

section "Talos Configuration"

if [[ -f "talos/talconfig.yaml" ]]; then
  pass "talconfig.yaml found"
else
  warn "talos/talconfig.yaml not found"
fi

if [[ -f "talos/talsecret.sops.yaml" ]]; then
  pass "Encrypted cluster secrets found"
else
  warn "talos/talsecret.sops.yaml not found — secrets may not be configured"
fi

if [[ -d "talos/patches" ]]; then
  PATCH_COUNT=$(ls talos/patches/*.yaml 2>/dev/null | wc -l | tr -d " ")
  pass "Found $PATCH_COUNT machine config patch file(s)"
else
  warn "talos/patches/ directory not found"
fi'

# shellcheck disable=SC2034
SMOKE_K8S_CHECKS='section "Kubernetes Connectivity"

if ! command -v kubectl >/dev/null 2>&1; then
  fail "kubectl not found"
else

NODE_COUNT=$(kubectl get nodes --no-headers 2>/dev/null | wc -l | tr -d " ")
if [[ "$NODE_COUNT" -gt 0 ]]; then
  pass "Cluster reachable — $NODE_COUNT node(s)"
else
  fail "Cannot reach Kubernetes API (kubectl get nodes failed)"
fi

READY_NODES=$(kubectl get nodes --no-headers 2>/dev/null | grep -c " Ready" || true)
if [[ "$READY_NODES" -eq "$NODE_COUNT" ]]; then
  pass "All $NODE_COUNT node(s) Ready"
else
  fail "$READY_NODES/$NODE_COUNT nodes Ready"
fi

section "Core System Pods"

for NS in kube-system; do
  NOT_RUNNING=$(kubectl get pods -n "$NS" --no-headers 2>/dev/null | grep -v "Running\|Completed" | wc -l | tr -d " ")
  if [[ "$NOT_RUNNING" -eq 0 ]]; then
    pass "$NS: all pods healthy"
  else
    warn "$NS: $NOT_RUNNING pod(s) not Running/Completed"
  fi
done

section "Cilium"

if command -v cilium >/dev/null 2>&1; then
  CILIUM_OK=$(cilium status --brief 2>/dev/null | grep -c "OK" || true)
  if [[ "$CILIUM_OK" -gt 0 ]]; then
    pass "Cilium status: OK"
  else
    warn "Cilium status check failed — run: cilium status"
  fi
else
  # Fallback: check Cilium pods directly
  CILIUM_PODS=$(kubectl get pods -n kube-system -l k8s-app=cilium --no-headers 2>/dev/null | wc -l | tr -d " ")
  CILIUM_RUNNING=$(kubectl get pods -n kube-system -l k8s-app=cilium --no-headers 2>/dev/null | grep -c "Running" || true)
  if [[ "$CILIUM_PODS" -gt 0 ]] && [[ "$CILIUM_RUNNING" -eq "$CILIUM_PODS" ]]; then
    pass "Cilium: $CILIUM_RUNNING/$CILIUM_PODS agent pods Running"
  elif [[ "$CILIUM_PODS" -gt 0 ]]; then
    warn "Cilium: $CILIUM_RUNNING/$CILIUM_PODS agent pods Running"
  else
    warn "No Cilium pods found in kube-system"
  fi
fi

section "Hubble"

if command -v hubble >/dev/null 2>&1; then
  if hubble status 2>/dev/null | grep -q "Healthy"; then
    pass "Hubble relay is healthy"
  else
    warn "Hubble relay not healthy — run: hubble status"
  fi
else
  HUBBLE_PODS=$(kubectl get pods -n kube-system -l k8s-app=hubble-relay --no-headers 2>/dev/null | grep -c "Running" || true)
  if [[ "$HUBBLE_PODS" -gt 0 ]]; then
    pass "Hubble relay pod running"
  else
    warn "Hubble relay not detected (hubble CLI not installed, no relay pod found)"
  fi
fi

section "ArgoCD"

ARGOCD_PODS=$(kubectl get pods -n argocd --no-headers 2>/dev/null | wc -l | tr -d " ")
ARGOCD_RUNNING=$(kubectl get pods -n argocd --no-headers 2>/dev/null | grep -c "Running" || true)
if [[ "$ARGOCD_PODS" -gt 0 ]] && [[ "$ARGOCD_RUNNING" -eq "$ARGOCD_PODS" ]]; then
  pass "ArgoCD: $ARGOCD_RUNNING/$ARGOCD_PODS pods Running"
elif [[ "$ARGOCD_PODS" -gt 0 ]]; then
  warn "ArgoCD: $ARGOCD_RUNNING/$ARGOCD_PODS pods Running"
else
  warn "ArgoCD namespace not found or no pods"
fi

section "Deployments"

TOTAL_DEPLOY=$(kubectl get deployments -A --no-headers 2>/dev/null | wc -l | tr -d " ")
READY_DEPLOY=$(kubectl get deployments -A --no-headers 2>/dev/null | awk '"'"'{split($3,a,"/"); if(a[1]==a[2]) print}'"'"' | wc -l | tr -d " ")
if [[ "$READY_DEPLOY" -eq "$TOTAL_DEPLOY" ]]; then
  pass "All $TOTAL_DEPLOY deployments ready"
else
  warn "$READY_DEPLOY/$TOTAL_DEPLOY deployments ready"
fi

fi'

# Troubleshooting sections
TROUBLESHOOTING_SECTIONS='## 1. Talos API / Connectivity

### Symptom: `talosctl` commands fail with "connection refused" or "deadline exceeded"

**Diagnosis:** Talos API unreachable. Could be wrong endpoint, firewall blocking port 50000,
or the node is down/rebooting.

**Fix:**
```bash
# Verify endpoint configuration
talosctl config info

# Test connectivity (Talos API listens on port 50000)
nc -zv <node-ip> 50000

# If node is rebooting, wait and retry
talosctl dmesg --nodes <ip> --follow

# If endpoint changed (e.g., after IP reassignment)
talosctl config endpoint <new-ip>
talosctl config node <new-ip>
```

---

### Symptom: `talosctl` returns "certificate signed by unknown authority"

**Diagnosis:** Talosconfig does not match the cluster CA. Common after regenerating cluster
secrets or using the wrong talosconfig file.

**Fix:**
```bash
# Check which talosconfig is active
talosctl config info

# Regenerate talosconfig from talhelper
talhelper genconfig
# Copy the new talosconfig:
cp talos/clusterconfig/talosconfig ~/.talos/config

# Or merge into existing config
talosctl config merge talos/clusterconfig/talosconfig
```

---

## 2. Cluster Bootstrap / etcd

### Symptom: `talosctl bootstrap` hangs or returns "etcd is not ready"

**Diagnosis:** etcd cannot form quorum. This happens when bootstrapping on the wrong node,
network is not ready, or there is a stale etcd data directory.

**Fix:**
```bash
# Bootstrap must run on exactly ONE control plane node
talosctl bootstrap --nodes <first-control-plane-ip>

# Check etcd member list
talosctl etcd members --nodes <cp-ip>

# If etcd is in a bad state after a failed bootstrap
# WARNING: This destroys etcd data — only for fresh clusters
talosctl reset --nodes <ip> --graceful=false
# Then re-apply config and bootstrap again
```

---

### Symptom: etcd alarm `NOSPACE` — cluster becomes read-only

**Diagnosis:** etcd database exceeded its storage quota (default 2GB in Talos). Happens with
high churn (many events, leases, or frequent writes).

**Fix:**
```bash
# Check etcd alarms
talosctl etcd alarm list --nodes <cp-ip>

# Compact and defragment etcd
talosctl etcd defrag --nodes <cp-ip>

# Disarm the alarm after freeing space
talosctl etcd alarm disarm --nodes <cp-ip>

# Increase quota in machine config if needed (patch):
# cluster:
#   etcd:
#     extraArgs:
#       quota-backend-bytes: "4294967296"  # 4GB
```

---

## 3. Talos Upgrades

### Symptom: Node stuck after `talosctl upgrade` — not coming back online

**Diagnosis:** Upgrade image failed to download, disk too full, or incompatible system extension.

**Fix:**
```bash
# Check upgrade status
talosctl dmesg --nodes <ip> --follow

# If node is stuck in maintenance mode
talosctl dashboard --nodes <ip>

# Force a reboot if node is responsive but stuck
talosctl reboot --nodes <ip>

# If completely unresponsive, check IPMI/BMC console for boot errors
# Common cause: system extension incompatible with new Talos version
# Fix: remove extension from machine config, apply, then upgrade
```

---

### Symptom: `talosctl upgrade` fails with "image not found" or pull error

**Diagnosis:** Cannot pull the Talos installer image. Could be registry unreachable, image
tag typo, or custom registry authentication issue.

**Fix:**
```bash
# Verify the image exists
crane manifest ghcr.io/siderolabs/installer:v1.9.0

# If using a private registry, check machine config registries section:
# machine:
#   registries:
#     mirrors:
#       ghcr.io:
#         endpoints:
#           - https://your-registry.example.com
#     config:
#       your-registry.example.com:
#         auth:
#           username: ...
#           password: ...

# Upgrade with explicit image
talosctl upgrade --nodes <ip> --image ghcr.io/siderolabs/installer:v1.9.0
```

---

## 4. Cilium / Networking

### Symptom: Pods cannot resolve DNS after Cilium install on Talos

**Diagnosis:** CoreDNS pods not running because Cilium is not ready, or kube-proxy was not
fully replaced. Talos with Cilium requires disabling kube-proxy in the machine config.

**Fix:**
```bash
# Verify kube-proxy is disabled in machine config
# cluster:
#   proxy:
#     disabled: true

# Check Cilium agent status
cilium status
kubectl -n kube-system get pods -l k8s-app=cilium

# Check CoreDNS pods
kubectl -n kube-system get pods -l k8s-app=kube-dns

# If CoreDNS is crashing, check if Cilium is fully ready first
cilium connectivity test

# Restart CoreDNS after Cilium is healthy
kubectl -n kube-system rollout restart deployment coredns
```

---

### Symptom: Hubble shows DROPPED verdicts between pods that should communicate

**Diagnosis:** Missing or incorrect CiliumNetworkPolicy. Remember: use container port
(post-DNAT), not service port. Also check namespace labels.

**Fix:**
```bash
# Identify drops
hubble observe --verdict DROPPED --namespace <ns> --follow

# Check which policy is causing the drop
hubble observe --verdict DROPPED -o json | jq ".drop_reason_desc"

# Verify container port (not service port)
kubectl get pod -n <ns> <pod> -o jsonpath="{.spec.containers[*].ports}"

# Check policy endpoints
kubectl get cnp -n <ns> -o yaml

# If using BPF, check map pressure
cilium-dbg bpf policy get --all -o json | \
  jq "to_entries | map({id: .key, count: (.value | length)}) | sort_by(-.count) | .[:5]"
```

---

## 5. Storage

### Symptom: PVC stuck in Pending — Longhorn volume not provisioning

**Diagnosis:** Longhorn not ready, no available nodes with sufficient disk, or storage class
misconfigured.

**Fix:**
```bash
# Check Longhorn manager
kubectl -n longhorn-system get pods

# Check Longhorn nodes
kubectl -n longhorn-system get nodes.longhorn.io

# Check events on the PVC
kubectl describe pvc -n <ns> <pvc-name>

# Verify storage class exists
kubectl get storageclass

# For Talos specifically: ensure the disk is mounted and accessible
# Longhorn needs a dedicated partition or disk, configured in Talos machine config:
# machine:
#   disks:
#     - device: /dev/sdb
#       partitions:
#         - mountpoint: /var/lib/longhorn
```

---

*Add entries as you encounter and solve issues. Use the Symptom -> Diagnosis -> Fix format.*'

# Memory topics: "filename|description" pairs
MEMORY_TOPICS="cluster-state.md|Current cluster health, node IPs, Talos/K8s versions, node roles
talos-upgrades.md|Upgrade history, extension compatibility, rollback notes
networking-issues.md|Cilium policy issues, DNS problems, Hubble observations
etcd-operations.md|etcd snapshots, compaction history, alarm events
debugging.md|Common errors encountered and their solutions"

# Slash commands to scaffold
COMMANDS="review.md
plan.md
cluster-health.md
node-status.md
smoke.md"

# --- Substantive Rules Content ---

# shellcheck disable=SC2034
RULES_CONTENT_TALOS_CONFIG='# Talos Machine Configuration

> **When to use:** Adding nodes, modifying machine config, system extensions, network config, disk setup.
>
> **Read first for:** Any talosctl apply-config, machine patch, or node provisioning task.

## Config Generation with talhelper

`talconfig.yaml` is the single source of truth. Never edit generated configs directly.

```yaml
# talconfig.yaml
clusterName: my-cluster
talosVersion: v1.9.0
kubernetesVersion: v1.32.0
endpoint: https://10.0.0.10:6443

nodes:
  - hostname: cp-01
    ipAddress: 10.0.0.11
    controlPlane: true
    installDiskSelector:
      busPath: /pci0000:00/0000:00:1f.2/ata1/host0/target0:0:0/0:0:0:0/
    machineSpec:
      secureboot: true
    patches:
      - patches/controlplane.yaml
      - patches/global.yaml

  - hostname: worker-01
    ipAddress: 10.0.0.21
    controlPlane: false
    installDiskSelector:
      size: ">= 100GB"
    patches:
      - patches/worker.yaml
      - patches/global.yaml
```

```bash
# Generate all configs
talhelper genconfig

# Validate generated configs
talhelper validate

# Diff before applying
talosctl apply-config --nodes 10.0.0.11 --file clusterconfig/my-cluster-cp-01.yaml --dry-run
```

## Machine Config Structure

```yaml
# Control plane machine config (key sections)
machine:
  type: controlplane   # or "worker"
  token: <machine-token>

  network:
    hostname: cp-01
    interfaces:
      - deviceSelector:
          busPath: "0000:01:00.0"    # Stable device selection
        addresses:
          - 10.0.0.11/24
        routes:
          - network: 0.0.0.0/0
            gateway: 10.0.0.1
        dhcp: false
        vip:
          ip: 10.0.0.10               # Shared VIP for control plane

    nameservers:
      - 10.0.0.1

  install:
    disk: /dev/sda                     # Or use installDiskSelector in talhelper
    image: ghcr.io/siderolabs/installer:v1.9.0
    extensions:
      - image: ghcr.io/siderolabs/iscsi-tools:v0.1.6
      - image: ghcr.io/siderolabs/util-linux-tools:2.40.4

  # Kernel arguments
  kernel:
    modules:
      - name: br_netfilter
      - name: ip_tables

  sysctls:
    net.core.somaxconn: "65535"
    net.ipv4.ip_forward: "1"
    vm.nr_hugepages: "1024"

  # Kubelet configuration
  kubelet:
    extraArgs:
      rotate-server-certificates: "true"
    nodeIP:
      validSubnets:
        - 10.0.0.0/24

  # Time synchronization
  time:
    servers:
      - time.cloudflare.com

  # Disk encryption (optional)
  systemDiskEncryption:
    state:
      provider: luks2
      keys:
        - slot: 0
          tpm: {}
    ephemeral:
      provider: luks2
      keys:
        - slot: 0
          tpm: {}

cluster:
  clusterName: my-cluster
  controlPlane:
    endpoint: https://10.0.0.10:6443

  # Disable kube-proxy (Cilium replaces it)
  proxy:
    disabled: true

  # Cluster discovery
  discovery:
    enabled: true
    registries:
      kubernetes:
        disabled: false
      service:
        disabled: true     # Disable external discovery service

  # etcd configuration
  etcd:
    extraArgs:
      listen-metrics-urls: http://0.0.0.0:2381

  # Inline manifests (applied at bootstrap)
  inlineManifests:
    - name: cilium
      contents: |
        # Cilium Helm values or manifest
```

## Machine Config Patches

Patches are YAML strategic merge patches applied on top of the base config.

```yaml
# patches/global.yaml — applied to ALL nodes
machine:
  sysctls:
    fs.inotify.max_user_watches: "1048576"
    fs.inotify.max_user_instances: "8192"
  time:
    servers:
      - time.cloudflare.com
  kubelet:
    extraArgs:
      rotate-server-certificates: "true"
```

```yaml
# patches/controlplane.yaml
cluster:
  allowSchedulingOnControlPlanes: false
  etcd:
    extraArgs:
      listen-metrics-urls: http://0.0.0.0:2381
  apiServer:
    extraArgs:
      oidc-issuer-url: https://auth.example.com
      oidc-client-id: kubernetes
```

```yaml
# patches/worker.yaml
machine:
  disks:
    - device: /dev/sdb
      partitions:
        - mountpoint: /var/lib/longhorn
  kubelet:
    extraMounts:
      - destination: /var/lib/longhorn
        type: bind
        source: /var/lib/longhorn
        options:
          - bind
          - rshared
          - rw
```

## System Extensions

Extensions add functionality to the immutable Talos rootfs (drivers, tools, etc.).

```yaml
machine:
  install:
    extensions:
      - image: ghcr.io/siderolabs/iscsi-tools:v0.1.6       # iSCSI (Longhorn)
      - image: ghcr.io/siderolabs/util-linux-tools:2.40.4   # util-linux
      - image: ghcr.io/siderolabs/qemu-guest-agent:9.2.0    # QEMU/Proxmox
      - image: ghcr.io/siderolabs/intel-ucode:20241112      # Intel microcode
      - image: ghcr.io/siderolabs/i915-ucode:20241112       # Intel GPU firmware
      - image: ghcr.io/siderolabs/gasket-driver:2.1.0       # Coral TPU
```

Check available extensions: `crane ls ghcr.io/siderolabs`

**Important:** Extension versions must be compatible with the Talos version. Always check
the [Talos extensions compatibility matrix](https://github.com/siderolabs/extensions).

## Secure Boot

```yaml
# In talconfig.yaml
nodes:
  - hostname: cp-01
    machineSpec:
      secureboot: true

# Uses the SecureBoot installer image variant automatically
# Requires TPM 2.0 for disk encryption with secureboot
```

## Common talosctl Commands

```bash
# Config management
talosctl config info                         # Show current context
talosctl config endpoint <ip>               # Set API endpoint
talosctl config node <ip>                   # Set default node
talosctl config merge <talosconfig>         # Merge another config

# Node inspection
talosctl get members                        # Cluster members
talosctl services --nodes <ip>              # Running services
talosctl mounts --nodes <ip>                # Mounted filesystems
talosctl disks --nodes <ip>                 # Available disks
talosctl dmesg --nodes <ip> --follow        # Kernel messages
talosctl logs kubelet --nodes <ip> --follow # Service logs

# Config operations
talosctl apply-config --nodes <ip> --file <config>           # Apply
talosctl apply-config --nodes <ip> --file <config> --dry-run # Diff only
talosctl edit machineconfig --nodes <ip>                     # Edit live (emergency only)

# Maintenance
talosctl reboot --nodes <ip>
talosctl shutdown --nodes <ip>
talosctl reset --nodes <ip> --graceful     # Wipe and reset node
```'

# shellcheck disable=SC2034
RULES_CONTENT_CLUSTER_OPS='# Cluster Operations

> **When to use:** Bootstrap, upgrade, scale, etcd operations, node maintenance.
>
> **Read first for:** Any cluster lifecycle operation, upgrade planning, etcd management.

## Cluster Bootstrap

Bootstrap is a **one-time** operation on the **first control plane node only**.

```bash
# 1. Generate configs
talhelper genconfig

# 2. Apply config to all nodes (they will install and reboot)
talosctl apply-config --insecure --nodes 10.0.0.11 --file clusterconfig/cluster-cp-01.yaml
talosctl apply-config --insecure --nodes 10.0.0.12 --file clusterconfig/cluster-cp-02.yaml
talosctl apply-config --insecure --nodes 10.0.0.13 --file clusterconfig/cluster-cp-03.yaml
talosctl apply-config --insecure --nodes 10.0.0.21 --file clusterconfig/cluster-worker-01.yaml

# 3. Wait for nodes to install and reboot (~2-5 minutes)

# 4. Bootstrap etcd on the FIRST control plane node ONLY
talosctl bootstrap --nodes 10.0.0.11

# 5. Retrieve kubeconfig
talosctl kubeconfig --nodes 10.0.0.11 -f ./kubeconfig
export KUBECONFIG=./kubeconfig

# 6. Verify
talosctl health --nodes 10.0.0.11
kubectl get nodes
```

**CRITICAL:** Never run `talosctl bootstrap` on more than one node. It will corrupt etcd.

## Talos Upgrade

Upgrade one node at a time. Control plane first, then workers.

```bash
# 1. Check current versions
talosctl version --nodes 10.0.0.11

# 2. Snapshot etcd BEFORE upgrading
talosctl etcd snapshot --nodes 10.0.0.11 etcd-backup-pre-upgrade.snapshot

# 3. Upgrade control plane nodes one at a time
talosctl upgrade --nodes 10.0.0.11 --image ghcr.io/siderolabs/installer:v1.9.1
# Wait for node to come back and be Ready
kubectl get nodes -w

talosctl upgrade --nodes 10.0.0.12 --image ghcr.io/siderolabs/installer:v1.9.1
# Wait...

talosctl upgrade --nodes 10.0.0.13 --image ghcr.io/siderolabs/installer:v1.9.1
# Wait...

# 4. Upgrade worker nodes
talosctl upgrade --nodes 10.0.0.21 --image ghcr.io/siderolabs/installer:v1.9.1
# Wait...

# 5. Verify all nodes upgraded
talosctl version --nodes 10.0.0.11,10.0.0.12,10.0.0.13,10.0.0.21

# 6. Verify cluster health
talosctl health --nodes 10.0.0.11
kubectl get nodes
```

### Upgrade with System Extensions

When upgrading with custom extensions, use the Talos Image Factory or build a custom installer:

```bash
# Using Image Factory (recommended)
# Go to https://factory.talos.dev, select version + extensions, get image ID
talosctl upgrade --nodes <ip> --image factory.talos.dev/installer/<schematic-id>:v1.9.1
```

## Kubernetes Upgrade

Separate from Talos OS upgrade. Update the `kubernetesVersion` in talconfig.yaml and re-apply.

```bash
# 1. Update talconfig.yaml: kubernetesVersion: v1.32.1
# 2. Regenerate configs
talhelper genconfig

# 3. Apply to control plane nodes (triggers rolling k8s component upgrade)
talosctl apply-config --nodes 10.0.0.11 --file clusterconfig/cluster-cp-01.yaml
# Repeat for each control plane node, one at a time

# 4. Verify
kubectl get nodes -o wide  # Check VERSION column
```

## Scaling the Cluster

### Adding a Node

```bash
# 1. Add node to talconfig.yaml
# 2. Generate config
talhelper genconfig

# 3. Apply to new node (--insecure for first contact)
talosctl apply-config --insecure --nodes <new-ip> --file clusterconfig/cluster-<hostname>.yaml

# 4. Wait for install and reboot
# 5. Verify
kubectl get nodes
```

### Removing a Worker Node

```bash
# 1. Drain the node
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# 2. Delete from Kubernetes
kubectl delete node <node-name>

# 3. Reset the Talos node (wipes it clean)
talosctl reset --nodes <ip> --graceful

# 4. Remove from talconfig.yaml
```

### Removing a Control Plane Node

```bash
# WARNING: Ensure you maintain etcd quorum (need majority of CP nodes alive)

# 1. Remove from etcd first
talosctl etcd remove-member --nodes <other-cp-ip> <node-to-remove>

# 2. Then drain and delete from Kubernetes
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data
kubectl delete node <node-name>

# 3. Reset the node
talosctl reset --nodes <ip> --graceful

# 4. Remove from talconfig.yaml
```

## etcd Operations

### Snapshots (Backup)

```bash
# Take a snapshot (run on any control plane node)
talosctl etcd snapshot --nodes <cp-ip> ./etcd-backup-$(date +%Y%m%d-%H%M%S).snapshot

# Automate with cron or CronJob — store off-cluster
```

### Health Check

```bash
# Quick health
talosctl etcd status --nodes <cp-ip>

# Member list
talosctl etcd members --nodes <cp-ip>

# Alarms
talosctl etcd alarm list --nodes <cp-ip>
```

### Defragmentation

Run periodically to reclaim space (especially after heavy churn):

```bash
# Defrag on each control plane node
talosctl etcd defrag --nodes 10.0.0.11
talosctl etcd defrag --nodes 10.0.0.12
talosctl etcd defrag --nodes 10.0.0.13
```

## Node Maintenance

```bash
# Cordon (prevent new pods from scheduling)
kubectl cordon <node-name>

# Drain (evict existing pods)
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data --timeout=300s

# Perform maintenance (reboot, hardware, etc.)
talosctl reboot --nodes <ip>
# Or: talosctl shutdown --nodes <ip>

# Uncordon when done
kubectl uncordon <node-name>
```

## Health Checks

```bash
# Comprehensive Talos health check
talosctl health --nodes <cp-ip> --wait-timeout 5m

# What it checks:
# - All nodes are reachable
# - etcd is healthy (quorum, no alarms)
# - Kubernetes API server responds
# - All nodes are Ready
# - All system pods are running

# Live dashboard (TUI)
talosctl dashboard --nodes <cp-ip>
# Shows: CPU, memory, disk, network, services, logs
```'

# shellcheck disable=SC2034
RULES_CONTENT_NETWORKING='# Networking (Cilium on Talos)

> **When to use:** Network policies, connectivity debugging, Hubble, BGP, load balancer config.
>
> **Read first for:** Any CiliumNetworkPolicy change, DNS issues, traffic debugging.

## Cilium as kube-proxy Replacement

Talos with Cilium requires kube-proxy to be **disabled** in the machine config:

```yaml
# In machine config (or talconfig.yaml)
cluster:
  proxy:
    disabled: true
```

Cilium Helm values for Talos:

```yaml
# kustomize/infra/cilium/values.yaml
ipam:
  mode: kubernetes
kubeProxyReplacement: true
k8sServiceHost: 10.0.0.10            # Control plane VIP or endpoint
k8sServicePort: 6443
securityContext:
  capabilities:
    ciliumAgent:
      - CHOWN
      - KILL
      - NET_ADMIN
      - NET_RAW
      - IPC_LOCK
      - SYS_ADMIN
      - SYS_RESOURCE
      - DAC_OVERRIDE
      - FOWNER
      - SETGID
      - SETUID
    cleanCiliumState:
      - NET_ADMIN
      - SYS_ADMIN
      - SYS_RESOURCE
cgroup:
  autoMount:
    enabled: false
  hostRoot: /sys/fs/cgroup
hubble:
  enabled: true
  relay:
    enabled: true
  ui:
    enabled: true
```

## CiliumNetworkPolicy

### Default-Deny Baseline

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: default-deny
  namespace: my-app
spec:
  endpointSelector: {}      # Matches all pods in namespace
  ingress:
    - {}                     # Deny all ingress (empty rule)
  egress:
    - {}                     # Deny all egress (empty rule)
```

### Allow Specific Traffic

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: my-service-policy
  namespace: my-app
spec:
  endpointSelector:
    matchLabels:
      app: my-service
  ingress:
    - fromEndpoints:
        - matchLabels:
            k8s:io.kubernetes.pod.namespace: ingress-nginx
      toPorts:
        - ports:
            - port: "8080"           # ALWAYS container port, not service port
              protocol: TCP
  egress:
    # DNS (required for all pods)
    - toEndpoints:
        - matchLabels:
            k8s:io.kubernetes.pod.namespace: kube-system
            k8s-app: kube-dns
      toPorts:
        - ports:
            - port: "53"
              protocol: UDP
            - port: "53"
              protocol: TCP
    # Database access
    - toEndpoints:
        - matchLabels:
            k8s:io.kubernetes.pod.namespace: database
            app: postgres
      toPorts:
        - ports:
            - port: "5432"
              protocol: TCP
```

### Critical Rules

| Rule | Reason |
|------|--------|
| **ALWAYS** use container port in `toPorts` | Cilium evaluates post-DNAT (pod port, not service port) |
| **AVOID** `toEntities: cluster` with `toPorts` | Creates ~19K BPF entries per port — causes map overflow |
| **USE** `toEndpoints` with namespace labels | Targeted entries, scales correctly |
| **AVOID** L7 DNS rules / `toFQDNs` | ~25K proxy redirect entries per endpoint |

## Hubble Observability

```bash
# Follow all traffic in a namespace
hubble observe --namespace my-app --follow

# Show only dropped traffic
hubble observe --verdict DROPPED --follow

# Filter by source/destination
hubble observe --from-pod my-app/my-service --follow
hubble observe --to-pod database/postgres --follow

# Show DNS queries
hubble observe --protocol DNS --follow

# Export as JSON for analysis
hubble observe --namespace my-app -o json > hubble-export.json

# Check Hubble status
hubble status
```

## BGP with Cilium

For bare-metal clusters, Cilium can peer with network routers via BGP:

```yaml
apiVersion: cilium.io/v2alpha1
kind: CiliumBGPPeeringPolicy
metadata:
  name: bgp-peering
spec:
  nodeSelector:
    matchLabels:
      bgp-policy: enabled
  virtualRouters:
    - localASN: 64512
      exportPodCIDR: true
      neighbors:
        - peerAddress: 10.0.0.1/32
          peerASN: 64501
          connectRetryTimeSeconds: 120
          holdTimeSeconds: 90
          keepAliveTimeSeconds: 30
```

## Cilium LB-IPAM (LoadBalancer IP Assignment)

Replace MetalLB with Cilium native LB-IPAM:

```yaml
apiVersion: cilium.io/v2alpha1
kind: CiliumLoadBalancerIPPool
metadata:
  name: main-pool
spec:
  blocks:
    - start: 10.0.0.200
      stop: 10.0.0.250

---
apiVersion: cilium.io/v2alpha1
kind: CiliumL2AnnouncementPolicy
metadata:
  name: l2-announce
spec:
  nodeSelector:
    matchExpressions:
      - key: node-role.kubernetes.io/control-plane
        operator: DoesNotExist
  interfaces:
    - ^eth[0-9]+
  externalIPs: true
  loadBalancerIPs: true
```

## DNS (CoreDNS on Talos)

CoreDNS runs as a deployment in `kube-system`. On Talos, it is deployed via the Talos
bootstrap manifests.

```bash
# Check CoreDNS pods
kubectl -n kube-system get pods -l k8s-app=kube-dns

# Test DNS resolution from a pod
kubectl run -it --rm dns-test --image=busybox:1.36 --restart=Never -- nslookup kubernetes.default

# Check CoreDNS Corefile
kubectl -n kube-system get configmap coredns -o yaml
```

### Talos DNS Quirk

Talos uses its own DNS proxy on the host (port 127.0.0.53). Pods use CoreDNS via the
cluster DNS service IP. If you see host-level DNS issues:

```bash
# Check Talos host DNS
talosctl read /etc/resolv.conf --nodes <ip>

# Verify machine.network.nameservers in config
talosctl get addresses --nodes <ip>
```

## Verifying Network Policies

```bash
# List all CiliumNetworkPolicies
kubectl get cnp -A

# Describe a specific policy
kubectl describe cnp -n <ns> <policy-name>

# Check BPF map pressure (prevent overflow)
cilium-dbg bpf policy get --all -o json | \
  jq "to_entries | map({id: .key, count: (.value | length)}) | sort_by(-.count) | .[:5]"

# Test connectivity between pods
cilium connectivity test

# Check Cilium endpoint status
cilium-dbg endpoint list
```'

# shellcheck disable=SC2034
RULES_CONTENT_CROSS_SERVICE='# Cross-Service Patterns

> **When to use:** ArgoCD GitOps, storage, secrets, monitoring, shared conventions.
>
> **Read first for:** Deploying workloads, configuring storage, managing secrets, observability.

## ArgoCD GitOps

All workload changes flow through git. ArgoCD watches the repo and syncs to the cluster.

```yaml
# ArgoCD Application definition
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-service
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/infra.git
    targetRevision: main
    path: kustomize/apps/my-service
  destination:
    server: https://kubernetes.default.svc
    namespace: my-service
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
      - ServerSideApply=true
```

```bash
# Check sync status
argocd app list
argocd app get my-service

# Force sync
argocd app sync my-service

# View diff
argocd app diff my-service

# Rollback
argocd app history my-service
argocd app rollback my-service <revision>
```

## Storage (Longhorn on Talos)

Longhorn requires iSCSI tools (system extension) and a dedicated disk/partition.

### Talos Machine Config for Longhorn

```yaml
# Worker node patch
machine:
  install:
    extensions:
      - image: ghcr.io/siderolabs/iscsi-tools:v0.1.6
      - image: ghcr.io/siderolabs/util-linux-tools:2.40.4

  disks:
    - device: /dev/sdb
      partitions:
        - mountpoint: /var/lib/longhorn

  kubelet:
    extraMounts:
      - destination: /var/lib/longhorn
        type: bind
        source: /var/lib/longhorn
        options: [bind, rshared, rw]
```

### StorageClass

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: longhorn
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: driver.longhorn.io
allowVolumeExpansion: true
reclaimPolicy: Delete
parameters:
  numberOfReplicas: "3"
  staleReplicaTimeout: "2880"
  dataLocality: best-effort
```

## Secrets Management

### SOPS + age (Recommended)

```bash
# Generate an age key (one time)
age-keygen -o age.agekey
# Store the public key in .sops.yaml, the private key OUTSIDE the repo

# .sops.yaml
creation_rules:
  - path_regex: .*\.sops\.yaml$
    age: age1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Encrypt a file
sops --encrypt --in-place secrets/my-secret.sops.yaml

# Decrypt (needs SOPS_AGE_KEY_FILE or SOPS_AGE_KEY env)
export SOPS_AGE_KEY_FILE=~/.config/sops/age/keys.txt
sops --decrypt secrets/my-secret.sops.yaml

# Edit encrypted file
sops secrets/my-secret.sops.yaml
```

### Sealed Secrets (Alternative)

```bash
# Encrypt a secret
kubectl create secret generic my-secret --from-literal=password=s3cr3t --dry-run=client -o yaml | \
  kubeseal --format yaml > sealed-my-secret.yaml

# Apply sealed secret (controller decrypts in-cluster)
kubectl apply -f sealed-my-secret.yaml
```

## Monitoring

### Prometheus ServiceMonitor

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: my-service
  namespace: monitoring
  labels:
    release: prometheus
spec:
  namespaceSelector:
    matchNames: [my-service]
  selector:
    matchLabels:
      app: my-service
  endpoints:
    - port: metrics
      interval: 30s
      path: /metrics
```

### Key Alerts for Talos Clusters

```yaml
# PrometheusRule for Talos-specific alerts
groups:
  - name: talos-cluster
    rules:
      - alert: TalosNodeUnreachable
        expr: up{job="talos"} == 0
        for: 5m
        labels:
          severity: critical

      - alert: EtcdHighLatency
        expr: histogram_quantile(0.99, rate(etcd_disk_wal_fsync_duration_seconds_bucket[5m])) > 0.5
        for: 10m
        labels:
          severity: warning

      - alert: EtcdDatabaseSize
        expr: etcd_server_quota_backend_bytes - etcd_mvcc_db_total_size_in_bytes < 100000000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "etcd database approaching quota (< 100MB free)"
```

## kubectl Patterns

```bash
# Common debugging commands
kubectl get events -A --sort-by=.metadata.creationTimestamp | tail -20
kubectl top nodes
kubectl top pods -A --sort-by=memory | head -20

# Get pods not in Running/Completed state
kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded

# Get resource usage vs requests
kubectl describe nodes | grep -A10 "Allocated resources"

# Watch rollout
kubectl rollout status deployment/<name> -n <ns> --timeout=300s
```

## Required Labels

```yaml
metadata:
  labels:
    app.kubernetes.io/name: <service>
    app.kubernetes.io/part-of: <project>
    app.kubernetes.io/managed-by: argocd
    app.kubernetes.io/version: <version>
```

## Resource Limits

Every container must have resource requests and limits:

```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    memory: 512Mi
    # CPU limits are controversial — omit for burstable workloads
```'

LINT_LANGUAGES="YAML (yamllint + kustomize build), Shell (shellcheck), JSON"
