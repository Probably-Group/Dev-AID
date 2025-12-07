## 6. Essential Talos Patterns

### Pattern 1: Production Cluster Bootstrap with HA Control Plane

```bash
# Generate cluster configuration with 3 control plane nodes
talosctl gen config talos-prod-cluster https://10.0.1.10:6443 \
  --with-secrets secrets.yaml \
  --config-patch-control-plane @control-plane-patch.yaml \
  --config-patch-worker @worker-patch.yaml

# Apply configuration to first control plane node
talosctl apply-config --insecure \
  --nodes 10.0.1.10 \
  --file controlplane.yaml

# Bootstrap etcd on first control plane
talosctl bootstrap --nodes 10.0.1.10 \
  --endpoints 10.0.1.10 \
  --talosconfig=./talosconfig

# Apply to additional control plane nodes
talosctl apply-config --insecure --nodes 10.0.1.11 --file controlplane.yaml
talosctl apply-config --insecure --nodes 10.0.1.12 --file controlplane.yaml

# Verify etcd cluster health
talosctl -n 10.0.1.10,10.0.1.11,10.0.1.12 etcd members

# Apply to worker nodes
for node in 10.0.1.20 10.0.1.21 10.0.1.22; do
  talosctl apply-config --insecure --nodes $node --file worker.yaml
done

# Bootstrap Kubernetes and retrieve kubeconfig
talosctl kubeconfig --nodes 10.0.1.10 --force

# Verify cluster
kubectl get nodes
kubectl get pods -A
```

**Key Points**:
- ✅ Always use `--with-secrets` to save secrets for future operations
- ✅ Bootstrap etcd only once on first control plane node
- ✅ Use machine config patches for environment-specific settings
- ✅ Verify etcd health before proceeding to Kubernetes bootstrap
- ✅ Keep secrets.yaml in secure, encrypted storage (Vault, age-encrypted Git)

**📚 For complete installation workflows** (bare-metal, cloud providers, network configs):
- See [`references/installation-guide.md`](/home/user/Dev-AID/.dev-aid/providers/claude/.claude/skills/expert/talos-os-expert/references/installation-guide.md)

---

### Pattern 2: Machine Config Patch for Custom Networking

```yaml
# control-plane-patch.yaml
machine:
  network:
    hostname: cp-01
    interfaces:
      - interface: eth0
        dhcp: false
        addresses:
          - 10.0.1.10/24
        routes:
          - network: 0.0.0.0/0
            gateway: 10.0.1.1
        vip:
          ip: 10.0.1.100  # Virtual IP for control plane HA
      - interface: eth1
        dhcp: false
        addresses:
          - 192.168.1.10/24  # Management network
    nameservers:
      - 8.8.8.8
      - 1.1.1.1
    timeServers:
      - time.cloudflare.com

  install:
    disk: /dev/sda
    image: ghcr.io/siderolabs/installer:v1.6.0
    wipe: false

  kubelet:
    extraArgs:
      feature-gates: GracefulNodeShutdown=true
      rotate-server-certificates: true
    nodeIP:
      validSubnets:
        - 10.0.1.0/24  # Force kubelet to use cluster network

  files:
    - content: |
        [plugins."io.containerd.grpc.v1.cri"]
          enable_unprivileged_ports = true
      path: /etc/cri/conf.d/20-customization.part
      op: create

cluster:
  network:
    cni:
      name: none  # Will install Cilium manually
    dnsDomain: cluster.local
    podSubnets:
      - 10.244.0.0/16
    serviceSubnets:
      - 10.96.0.0/12

  apiServer:
    certSANs:
      - 10.0.1.100
      - cp.talos.example.com
    extraArgs:
      audit-log-path: /var/log/kube-apiserver-audit.log
      audit-policy-file: /etc/kubernetes/audit-policy.yaml
      feature-gates: ServerSideApply=true

  controllerManager:
    extraArgs:
      bind-address: 0.0.0.0

  scheduler:
    extraArgs:
      bind-address: 0.0.0.0

  etcd:
    extraArgs:
      listen-metrics-urls: http://0.0.0.0:2381
```

**Apply the patch**:
```bash
# Merge patch with base config
talosctl gen config talos-prod https://10.0.1.100:6443 \
  --config-patch-control-plane @control-plane-patch.yaml \
  --output-types controlplane -o controlplane.yaml

# Apply to node
talosctl apply-config --nodes 10.0.1.10 --file controlplane.yaml
```

---

### Pattern 3: Talos OS In-Place Upgrade with Validation

```bash
# Check current version
talosctl -n 10.0.1.10 version

# Plan upgrade (check what will change)
talosctl -n 10.0.1.10 upgrade --dry-run \
  --image ghcr.io/siderolabs/installer:v1.6.1

# Upgrade control plane nodes one at a time
for node in 10.0.1.10 10.0.1.11 10.0.1.12; do
  echo "Upgrading control plane node $node"

  # Upgrade with preserve=true (keeps ephemeral data)
  talosctl -n $node upgrade \
    --image ghcr.io/siderolabs/installer:v1.6.1 \
    --preserve=true \
    --wait

  # Wait for node to be ready
  kubectl wait --for=condition=Ready node/$node --timeout=10m

  # Verify etcd health
  talosctl -n $node etcd member list

  # Brief pause before next node
  sleep 30
done

# Upgrade worker nodes (can be done in parallel batches)
talosctl -n 10.0.1.20,10.0.1.21,10.0.1.22 upgrade \
  --image ghcr.io/siderolabs/installer:v1.6.1 \
  --preserve=true

# Verify cluster health
kubectl get nodes
talosctl -n 10.0.1.10 health --wait-timeout=10m
```

**Critical Points**:
- ✅ Always upgrade control plane nodes one at a time
- ✅ Use `--preserve=true` to maintain state and avoid data loss
- ✅ Verify etcd health between control plane upgrades
- ✅ Test upgrade path in staging environment first
- ✅ Have rollback plan (keep previous installer image available)

---

