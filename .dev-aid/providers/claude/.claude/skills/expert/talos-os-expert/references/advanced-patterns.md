# Advanced Talos Patterns

This document contains advanced patterns for Talos OS cluster management.

---

## Pattern 4: Disk Encryption with TPM Integration

```yaml
# disk-encryption-patch.yaml
machine:
  install:
    disk: /dev/sda
    wipe: true
    diskSelector:
      size: '>= 100GB'
      model: 'Samsung SSD*'

  systemDiskEncryption:
    state:
      provider: luks2
      keys:
        - slot: 0
          tpm: {}  # Use TPM 2.0 for key sealing
      options:
        - no_read_workqueue
        - no_write_workqueue
    ephemeral:
      provider: luks2
      keys:
        - slot: 0
          tpm: {}
      cipher: aes-xts-plain64
      keySize: 512
      options:
        - no_read_workqueue
        - no_write_workqueue

# For non-TPM environments, use static key
# machine:
#   systemDiskEncryption:
#     state:
#       provider: luks2
#       keys:
#         - slot: 0
#           static:
#             passphrase: "your-secure-passphrase-from-vault"
```

**Apply encryption configuration**:
```bash
# Generate config with encryption patch
talosctl gen config encrypted-cluster https://10.0.1.100:6443 \
  --config-patch-control-plane @disk-encryption-patch.yaml \
  --with-secrets secrets.yaml

# WARNING: This will wipe the disk during installation
talosctl apply-config --insecure --nodes 10.0.1.10 --file controlplane.yaml

# Verify encryption is active
talosctl -n 10.0.1.10 get encryptionconfig
talosctl -n 10.0.1.10 disks
```

**📚 For complete security hardening** (secure boot, KMS, audit policies):
- See [`references/security-hardening.md`](/home/user/Dev-AID/.dev-aid/providers/claude/.claude/skills/expert/talos-os-expert/references/security-hardening.md)

---

## Pattern 5: Multi-Cluster Management with Contexts

```bash
# Generate configs for multiple clusters
talosctl gen config prod-us-east https://prod-us-east.example.com:6443 \
  --with-secrets secrets-prod-us-east.yaml \
  --output-types talosconfig \
  -o talosconfig-prod-us-east

talosctl gen config prod-eu-west https://prod-eu-west.example.com:6443 \
  --with-secrets secrets-prod-eu-west.yaml \
  --output-types talosconfig \
  -o talosconfig-prod-eu-west

# Merge contexts into single config
talosctl config merge talosconfig-prod-us-east
talosctl config merge talosconfig-prod-eu-west

# List available contexts
talosctl config contexts

# Switch between clusters
talosctl config context prod-us-east
talosctl -n 10.0.1.10 version

talosctl config context prod-eu-west
talosctl -n 10.10.1.10 version

# Use specific context without switching
talosctl --context prod-us-east -n 10.0.1.10 get members
```

---

## Pattern 6: Emergency Diagnostics and Recovery

```bash
# Check node health comprehensively
talosctl -n 10.0.1.10 health --server=false

# View system logs
talosctl -n 10.0.1.10 dmesg --tail
talosctl -n 10.0.1.10 logs kubelet
talosctl -n 10.0.1.10 logs etcd
talosctl -n 10.0.1.10 logs containerd

# Check service status
talosctl -n 10.0.1.10 services
talosctl -n 10.0.1.10 service kubelet status
talosctl -n 10.0.1.10 service etcd status

# Network diagnostics
talosctl -n 10.0.1.10 interfaces
talosctl -n 10.0.1.10 routes
talosctl -n 10.0.1.10 netstat --tcp --listening

# Disk and mount information
talosctl -n 10.0.1.10 disks
talosctl -n 10.0.1.10 mounts

# etcd diagnostics
talosctl -n 10.0.1.10 etcd members
talosctl -n 10.0.1.10 etcd status
talosctl -n 10.0.1.10 etcd alarm list

# Get machine configuration currently applied
talosctl -n 10.0.1.10 get machineconfig -o yaml

# Reset node (DESTRUCTIVE - use with caution)
# talosctl -n 10.0.1.10 reset --graceful --reboot

# Force reboot if node is unresponsive
# talosctl -n 10.0.1.10 reboot --mode=force
```

---

## Pattern 7: GitOps Machine Config Management

```yaml
# .github/workflows/talos-apply.yml
name: Apply Talos Machine Configs

on:
  push:
    branches: [main]
    paths:
      - 'talos/clusters/**/*.yaml'
  pull_request:
    paths:
      - 'talos/clusters/**/*.yaml'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install talosctl
        run: |
          curl -sL https://talos.dev/install | sh

      - name: Validate machine configs
        run: |
          talosctl validate --config talos/clusters/prod/controlplane.yaml --mode metal
          talosctl validate --config talos/clusters/prod/worker.yaml --mode metal

  apply-staging:
    needs: validate
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4

      - name: Configure talosctl
        run: |
          echo "${{ secrets.TALOS_CONFIG_STAGING }}" > /tmp/talosconfig
          export TALOSCONFIG=/tmp/talosconfig

      - name: Apply control plane config
        run: |
          talosctl apply-config \
            --nodes 10.0.1.10,10.0.1.11,10.0.1.12 \
            --file talos/clusters/staging/controlplane.yaml \
            --mode=reboot

      - name: Wait for nodes
        run: |
          sleep 60
          talosctl -n 10.0.1.10 health --wait-timeout=10m

  apply-production:
    needs: apply-staging
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: Apply production configs
        run: |
          # Apply to control plane with rolling update
          for node in 10.1.1.10 10.1.1.11 10.1.1.12; do
            talosctl apply-config --nodes $node \
              --file talos/clusters/prod/controlplane.yaml \
              --mode=reboot
            sleep 120  # Wait between control plane nodes
          done
```
