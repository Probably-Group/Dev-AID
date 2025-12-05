# Common Mistakes and Anti-Patterns

This document outlines common mistakes and anti-patterns to avoid when working with Talos OS.

---

## Mistake 1: Bootstrapping etcd Multiple Times

```bash
# ❌ BAD: Running bootstrap on multiple control plane nodes
talosctl bootstrap --nodes 10.0.1.10
talosctl bootstrap --nodes 10.0.1.11  # This will create a split-brain!

# ✅ GOOD: Bootstrap only once on first control plane
talosctl bootstrap --nodes 10.0.1.10
# Other nodes join automatically via machine config
```

**Why it matters**: Multiple bootstrap operations create separate etcd clusters, causing split-brain and data inconsistency.

---

## Mistake 2: Losing Talos Secrets

```bash
# ❌ BAD: Not saving secrets during generation
talosctl gen config my-cluster https://10.0.1.100:6443

# ✅ GOOD: Always save secrets for future operations
talosctl gen config my-cluster https://10.0.1.100:6443 \
  --with-secrets secrets.yaml

# Store secrets.yaml in encrypted vault (age, SOPS, Vault)
age-encrypt -r <public-key> secrets.yaml > secrets.yaml.age
```

**Why it matters**: Without secrets, you cannot add nodes, rotate certificates, or recover the cluster. This is catastrophic.

---

## Mistake 3: Upgrading All Control Plane Nodes Simultaneously

```bash
# ❌ BAD: Upgrading all control plane at once
talosctl -n 10.0.1.10,10.0.1.11,10.0.1.12 upgrade --image ghcr.io/siderolabs/installer:v1.6.1

# ✅ GOOD: Sequential upgrade with validation
for node in 10.0.1.10 10.0.1.11 10.0.1.12; do
  talosctl -n $node upgrade --image ghcr.io/siderolabs/installer:v1.6.1 --wait
  kubectl wait --for=condition=Ready node/$node --timeout=10m
  sleep 30
done
```

**Why it matters**: Simultaneous upgrades can cause cluster-wide outage if something goes wrong. Etcd needs majority quorum.

---

## Mistake 4: Using `--mode=staged` Without Understanding Implications

```bash
# ❌ RISKY: Using staged mode without plan
talosctl apply-config --nodes 10.0.1.10 --file config.yaml --mode=staged

# ✅ BETTER: Understand mode implications
# - auto (default): Applies immediately, reboots if needed
# - no-reboot: Applies without reboot (use for config changes that don't require reboot)
# - reboot: Always reboots to apply changes
# - staged: Applies on next reboot (use for planned maintenance windows)

talosctl apply-config --nodes 10.0.1.10 --file config.yaml --mode=no-reboot
# Then manually reboot when ready
talosctl -n 10.0.1.10 reboot
```

---

## Mistake 5: Not Validating Machine Configs Before Applying

```bash
# ❌ BAD: Applying config without validation
talosctl apply-config --nodes 10.0.1.10 --file config.yaml

# ✅ GOOD: Validate first
talosctl validate --config config.yaml --mode metal

# Check what will change
talosctl -n 10.0.1.10 get machineconfig -o yaml > current-config.yaml
diff current-config.yaml config.yaml

# Then apply
talosctl apply-config --nodes 10.0.1.10 --file config.yaml
```

---

## Mistake 6: Insufficient Disk Space for etcd

```yaml
# ❌ BAD: Using small root disk without etcd quota
machine:
  install:
    disk: /dev/sda  # Only 32GB disk

# ✅ GOOD: Proper disk sizing and etcd quota
machine:
  install:
    disk: /dev/sda  # Minimum 120GB recommended

  kubelet:
    extraArgs:
      eviction-hard: nodefs.available<10%,nodefs.inodesFree<5%

cluster:
  etcd:
    extraArgs:
      quota-backend-bytes: "8589934592"  # 8GB quota
      auto-compaction-retention: "1000"
      snapshot-count: "10000"
```

**Why it matters**: etcd can fill disk causing cluster failure. Always monitor disk usage and set quotas.

---

## Mistake 7: Exposing Talos API to Public Internet

```yaml
# ❌ DANGEROUS: Talos API accessible from anywhere
machine:
  network:
    interfaces:
      - interface: eth0
        addresses:
          - 203.0.113.10/24  # Public IP
        # Talos API (50000) now exposed to internet!

# ✅ GOOD: Separate networks for management and cluster
machine:
  network:
    interfaces:
      - interface: eth0
        addresses:
          - 10.0.1.10/24  # Private cluster network
      - interface: eth1
        addresses:
          - 192.168.1.10/24  # Management network (firewalled)
```

**Why it matters**: Talos API provides full cluster control. Always use private networks and firewall rules.

---

## Mistake 8: Not Testing Upgrades in Non-Production First

```bash
# ❌ BAD: Upgrading production directly
talosctl -n prod-node upgrade --image ghcr.io/siderolabs/installer:v1.7.0

# ✅ GOOD: Test upgrade path
# 1. Upgrade staging environment
talosctl --context staging -n staging-node upgrade --image ghcr.io/siderolabs/installer:v1.7.0

# 2. Verify staging cluster health
kubectl --context staging get nodes
kubectl --context staging get pods -A

# 3. Run integration tests
# 4. Document any issues or manual steps required
# 5. Only then upgrade production with documented procedure
```
