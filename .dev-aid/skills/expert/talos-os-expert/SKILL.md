---
name: talos-os-expert
version: 2.0.0
description: "Talos Linux deployment with machine configs, secure boot, disk encryption, and upgrades."
risk_level: HIGH
---

# Talos OS Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-522: Insufficiently Protected Credentials**
- NEVER: Generate machine configs without reviewing included secrets
- ALWAYS: `talosctl gen secrets` separately, store securely, pass with `--from-secrets`

**CWE-306: Missing Authentication**
- NEVER: Expose Talos API endpoints without mTLS
- ALWAYS: Require client certificates for all API access

**CWE-311: Missing Encryption**
- NEVER: Store machine configs with plaintext secrets
- ALWAYS: Enable disk encryption, encrypt configs at rest

**CWE-250: Execution with Unnecessary Privilege**
- NEVER: Run workloads on control plane nodes
- ALWAYS: Use taints/tolerations, dedicated worker nodes

### 0.3 Risk Level: HIGH

**Verification requirements for HIGH risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 Machine Config Security (CWE-798, CWE-312)

**Principle:** Machine configs contain sensitive data. Encrypt secrets, never commit plaintext.

```yaml
# ❌ WRONG - Plaintext secrets in machine config
machine:
  token: "abcdef.1234567890abcdef"
  ca:
    crt: |
      -----BEGIN CERTIFICATE-----
      ...
    key: |
      -----BEGIN RSA PRIVATE KEY-----
      ...

# ✅ CORRECT - Use SOPS encryption for secrets
# encrypt with: sops -e -i machineconfig.yaml
machine:
  token: ENC[AES256_GCM,data:...,type:str]
  ca:
    crt: ENC[AES256_GCM,data:...,type:str]
    key: ENC[AES256_GCM,data:...,type:str]
sops:
  kms:
    - arn: arn:aws:kms:us-east-1:123456789012:key/...
```

### 1.2 Secure Boot and TPM (CWE-693)

**Principle:** Enable Secure Boot and TPM for hardware-backed security where supported.

```yaml
# ❌ WRONG - No secure boot configuration
machine:
  install:
    disk: /dev/sda

# ✅ CORRECT - Secure boot with disk encryption
machine:
  install:
    disk: /dev/sda
    bootloader: true
    wipe: false
  systemDiskEncryption:
    ephemeral:
      provider: luks2
      keys:
        - slot: 0
          tpm: {}
    state:
      provider: luks2
      keys:
        - slot: 0
          tpm: {}
  features:
    rbac: true
    kubernetesTalosAPIAccess:
      enabled: true
      allowedRoles:
        - os:reader
      allowedKubernetesNamespaces:
        - kube-system
```

### 1.3 API Access Control (CWE-284)

**Principle:** Restrict talosctl API access. Use certificate-based auth with role restrictions.

```yaml
# ❌ WRONG - No API restrictions
machine:
  features:
    kubernetesTalosAPIAccess:
      enabled: true

# ✅ CORRECT - Restricted API access
machine:
  features:
    rbac: true
    kubernetesTalosAPIAccess:
      enabled: true
      allowedRoles:
        - os:reader  # Read-only by default
      allowedKubernetesNamespaces:
        - monitoring  # Only monitoring namespace

# Separate admin config for maintenance
# talosctl config new admin-config --roles os:admin
```

### 1.4 Network Hardening (CWE-923)

**Principle:** Minimize network exposure. Disable unnecessary interfaces and services.

```yaml
# ❌ WRONG - Default network configuration
machine:
  network:
    hostname: node1

# ✅ CORRECT - Hardened network configuration
machine:
  network:
    hostname: node1
    interfaces:
      - interface: eth0
        addresses:
          - 192.168.1.10/24
        routes:
          - network: 0.0.0.0/0
            gateway: 192.168.1.1
        mtu: 1500
        dhcp: false  # Static IP, no DHCP
    nameservers:
      - 192.168.1.1
    extraHostEntries:
      - ip: 192.168.1.100
        aliases:
          - api.cluster.local
  # Firewall rules (Talos 1.6+)
  network:
    kubespan:
      enabled: true  # Encrypted mesh networking
```

---

## 2. Version Requirements

```yaml
# Talos version compatibility
talos: ">=1.6.0"
kubernetes: ">=1.29.0,<1.31.0"  # Check compat matrix

# Extensions (if needed)
extensions:
  - ghcr.io/siderolabs/intel-ucode:20231114
  - ghcr.io/siderolabs/i915-ucode:20231114
```

---

## 3. Code Patterns

### WHEN generating machine configs, use talosctl with patches

```bash
# ❌ WRONG - Manual config editing
vim machineconfig.yaml
talosctl apply-config --insecure --nodes 192.168.1.10 --file machineconfig.yaml

# ✅ CORRECT - Generate with patches
#!/bin/bash
set -euo pipefail

generate_machine_config() {
    local cluster_name=$1
    local cluster_endpoint=$2
    local output_dir=$3

    # Generate base configs
    talosctl gen config "$cluster_name" "$cluster_endpoint" \
        --output-dir "$output_dir" \
        --with-docs=false \
        --with-examples=false

    # Apply security patches
    talosctl machineconfig patch "$output_dir/controlplane.yaml" \
        --patch @patches/security.yaml \
        --patch @patches/network.yaml \
        --output "$output_dir/controlplane-patched.yaml"

    # Encrypt secrets
    sops -e -i "$output_dir/controlplane-patched.yaml"
}
```

### WHEN applying machine config patches, use structured patches

```yaml
# patches/security.yaml
# ❌ WRONG - Inline secrets
machine:
  token: "plain-text-token"

# ✅ CORRECT - Reference external secrets
machine:
  features:
    rbac: true
  sysctls:
    # Kernel hardening
    net.ipv4.conf.all.rp_filter: "1"
    net.ipv4.conf.default.rp_filter: "1"
    net.ipv4.icmp_echo_ignore_broadcasts: "1"
    net.ipv4.conf.all.accept_redirects: "0"
    net.ipv4.conf.default.accept_redirects: "0"
    net.ipv4.conf.all.secure_redirects: "0"
    net.ipv4.conf.default.secure_redirects: "0"
    kernel.randomize_va_space: "2"
  kubelet:
    extraArgs:
      rotate-server-certificates: "true"
      protect-kernel-defaults: "true"
    extraConfig:
      serverTLSBootstrap: true
```

### WHEN upgrading Talos, use staged rollout

```bash
# ❌ WRONG - Upgrade all nodes at once
talosctl upgrade --nodes 192.168.1.10,192.168.1.11,192.168.1.12 \
    --image ghcr.io/siderolabs/installer:v1.7.0

# ✅ CORRECT - Staged upgrade with health checks
#!/bin/bash
set -euo pipefail

upgrade_cluster() {
    local image=$1
    local nodes=("${@:2}")

    for node in "${nodes[@]}"; do
        echo "=== Upgrading $node ==="

        # Pre-upgrade health check
        if ! talosctl --nodes "$node" health --wait-timeout 60s; then
            echo "ERROR: Node $node unhealthy, aborting"
            return 1
        fi

        # Cordon in Kubernetes
        kubectl cordon "$node"

        # Drain workloads
        kubectl drain "$node" \
            --ignore-daemonsets \
            --delete-emptydir-data \
            --timeout=300s

        # Perform upgrade
        talosctl --nodes "$node" upgrade \
            --image "$image" \
            --preserve \
            --wait

        # Wait for node to be ready
        echo "Waiting for node to rejoin..."
        until talosctl --nodes "$node" health --wait-timeout 300s; do
            sleep 10
        done

        # Uncordon
        kubectl uncordon "$node"

        # Post-upgrade health check
        if ! kubectl wait node "$node" --for=condition=Ready --timeout=300s; then
            echo "ERROR: Node $node not ready after upgrade"
            return 1
        fi

        echo "=== $node upgraded successfully ==="
        sleep 30  # Cool-down between nodes
    done
}
```

### WHEN configuring disk encryption, use TPM with recovery keys

```yaml
# ❌ WRONG - Encryption without recovery option
machine:
  systemDiskEncryption:
    state:
      provider: luks2
      keys:
        - slot: 0
          tpm: {}

# ✅ CORRECT - TPM with static recovery key
machine:
  systemDiskEncryption:
    ephemeral:
      provider: luks2
      keys:
        - slot: 0
          tpm: {}
        - slot: 1
          static:
            passphrase: ${RECOVERY_KEY}  # From SOPS
    state:
      provider: luks2
      keys:
        - slot: 0
          tpm: {}
        - slot: 1
          static:
            passphrase: ${RECOVERY_KEY}  # From SOPS
```

### WHEN bootstrapping a new cluster, validate before applying

```bash
# ❌ WRONG - Apply without validation
talosctl apply-config --insecure --nodes 192.168.1.10 \
    --file controlplane.yaml

# ✅ CORRECT - Validate and dry-run first
#!/bin/bash
set -euo pipefail

bootstrap_node() {
    local node_ip=$1
    local config_file=$2
    local role=$3  # controlplane or worker

    # Decrypt if SOPS encrypted
    local decrypted_config
    decrypted_config=$(mktemp)
    sops -d "$config_file" > "$decrypted_config"
    trap "rm -f $decrypted_config" EXIT

    # Validate config
    echo "=== Validating config ==="
    if ! talosctl validate --config "$decrypted_config" --mode metal; then
        echo "ERROR: Invalid configuration"
        return 1
    fi

    # Check node is in maintenance mode
    echo "=== Checking node state ==="
    local state
    state=$(talosctl --nodes "$node_ip" --insecure version 2>/dev/null | grep -c "maintenance" || true)
    if [[ "$state" -eq 0 ]]; then
        echo "WARNING: Node not in maintenance mode"
        read -p "Continue anyway? (y/N) " -n 1 -r
        [[ $REPLY =~ ^[Yy]$ ]] || return 1
    fi

    # Apply config
    echo "=== Applying config ==="
    talosctl apply-config \
        --nodes "$node_ip" \
        --file "$decrypted_config" \
        --insecure

    # Wait for node
    echo "=== Waiting for node ==="
    until talosctl --nodes "$node_ip" health --wait-timeout 300s 2>/dev/null; do
        echo "Waiting for node to become healthy..."
        sleep 10
    done

    # Bootstrap if first controlplane
    if [[ "$role" == "controlplane" ]]; then
        echo "=== Bootstrapping etcd ==="
        talosctl --nodes "$node_ip" bootstrap
    fi

    echo "=== Node $node_ip configured successfully ==="
}
```

---

## 4. Anti-Patterns

**NEVER:**
- Store machine configs with plaintext secrets in Git
- Skip Secure Boot on supported hardware
- Use `--insecure` in production scripts
- Upgrade all nodes simultaneously
- Disable RBAC for API access
- Use DHCP without static fallback in production
- Skip config validation before applying
- Ignore pre-upgrade health checks

---

## 5. Testing

```bash
#!/bin/bash
set -euo pipefail

test_talos_config() {
    local config_file=$1
    local failed=0

    echo "TEST: Config syntax validation"
    if ! talosctl validate --config "$config_file" --mode metal; then
        echo "FAIL: Invalid config syntax"
        ((failed++))
    fi

    echo "TEST: RBAC enabled"
    if ! yq '.machine.features.rbac' "$config_file" | grep -q "true"; then
        echo "FAIL: RBAC not enabled"
        ((failed++))
    fi

    echo "TEST: No plaintext secrets"
    if yq '.machine.token' "$config_file" | grep -qv "^ENC\["; then
        echo "FAIL: Plaintext token detected"
        ((failed++))
    fi

    echo "TEST: Disk encryption configured"
    if ! yq '.machine.systemDiskEncryption' "$config_file" | grep -q "luks2"; then
        echo "WARN: Disk encryption not configured"
    fi

    echo "TEST: Kernel hardening sysctls"
    if ! yq '.machine.sysctls' "$config_file" | grep -q "rp_filter"; then
        echo "WARN: Kernel hardening not applied"
    fi

    return $failed
}

test_live_node() {
    local node=$1

    echo "TEST: Node health"
    talosctl --nodes "$node" health --wait-timeout 60s

    echo "TEST: Secure boot status"
    talosctl --nodes "$node" read /sys/firmware/efi/efivars/SecureBoot-* 2>/dev/null || \
        echo "INFO: Secure Boot status unavailable"

    echo "TEST: Disk encryption active"
    talosctl --nodes "$node" ls /dev/mapper/ | grep -q "luks" || \
        echo "WARN: Disk encryption may not be active"

    echo "TEST: API RBAC"
    # Should fail without proper role
    if talosctl --nodes "$node" reboot --dry-run 2>&1 | grep -q "access denied"; then
        echo "PASS: RBAC restricting access"
    fi
}
```

---

## 6. Pre-Generation Checklist

**BEFORE generating Talos configs:**

- [ ] Secrets encrypted with SOPS or similar
- [ ] RBAC enabled for Talos API
- [ ] Secure Boot configured (if hardware supports)
- [ ] Disk encryption with TPM + recovery key
- [ ] Network hardening sysctls applied
- [ ] Static IPs (no production DHCP)
- [ ] Config validated before applying
- [ ] Staged upgrade procedures documented
- [ ] kubernetesTalosAPIAccess restricted
