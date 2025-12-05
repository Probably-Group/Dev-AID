# Testing Guide for Talos OS

This document contains comprehensive testing patterns for Talos OS clusters.

---

## Configuration Testing

```bash
#!/bin/bash
# tests/talos-config-tests.sh

# Validate all machine configs
validate_configs() {
  for config in controlplane.yaml worker.yaml; do
    echo "Validating $config..."
    talosctl validate --config $config --mode metal || exit 1
  done
}

# Test config generation is reproducible
test_reproducibility() {
  talosctl gen config test-cluster https://10.0.1.100:6443 \
    --with-secrets secrets.yaml \
    --output-dir /tmp/gen1

  talosctl gen config test-cluster https://10.0.1.100:6443 \
    --with-secrets secrets.yaml \
    --output-dir /tmp/gen2

  # Configs should be identical (except timestamps)
  diff <(yq 'del(.machine.time)' /tmp/gen1/controlplane.yaml) \
       <(yq 'del(.machine.time)' /tmp/gen2/controlplane.yaml)
}

# Test secrets are properly encrypted
test_secrets_encryption() {
  # Verify secrets file doesn't contain plaintext
  if grep -q "BEGIN RSA PRIVATE KEY" secrets.yaml; then
    echo "ERROR: Unencrypted secrets detected!"
    exit 1
  fi
}
```

---

## Cluster Health Testing

```bash
#!/bin/bash
# tests/cluster-health-tests.sh

# Test all nodes are ready
test_nodes_ready() {
  local expected_nodes=$1
  local ready_nodes=$(kubectl get nodes --no-headers | grep -c "Ready")

  if [ "$ready_nodes" -ne "$expected_nodes" ]; then
    echo "ERROR: Expected $expected_nodes nodes, got $ready_nodes"
    kubectl get nodes
    exit 1
  fi
}

# Test etcd cluster health
test_etcd_health() {
  local nodes=$1

  # Check all members present
  local members=$(talosctl -n $nodes etcd members | grep -c "started")
  if [ "$members" -ne 3 ]; then
    echo "ERROR: Expected 3 etcd members, got $members"
    exit 1
  fi

  # Check no alarms
  local alarms=$(talosctl -n $nodes etcd alarm list 2>&1)
  if [[ "$alarms" != *"no alarms"* ]]; then
    echo "ERROR: etcd alarms detected: $alarms"
    exit 1
  fi
}

# Test critical system pods
test_system_pods() {
  local failing=$(kubectl get pods -n kube-system --no-headers | \
    grep -v "Running\|Completed" | wc -l)

  if [ "$failing" -gt 0 ]; then
    echo "ERROR: $failing system pods not running"
    kubectl get pods -n kube-system | grep -v "Running\|Completed"
    exit 1
  fi
}
```

---

## Upgrade Testing

```bash
#!/bin/bash
# tests/upgrade-tests.sh

# Test upgrade dry-run
test_upgrade_dry_run() {
  local node=$1
  local new_image=$2

  echo "Testing upgrade dry-run to $new_image..."
  talosctl -n $node upgrade --dry-run --image $new_image || exit 1
}

# Test rollback capability
test_rollback_preparation() {
  local node=$1

  # Ensure we have previous image info
  local current=$(talosctl -n $node version --short | grep "Tag:" | awk '{print $2}')
  echo "Current version: $current"

  # Verify etcd snapshot exists
  talosctl -n $node etcd snapshot /tmp/pre-upgrade-backup.snapshot || exit 1
  echo "Backup created successfully"
}

# Full upgrade test (for staging)
test_full_upgrade() {
  local node=$1
  local new_image=$2

  # 1. Create backup
  talosctl -n $node etcd snapshot /tmp/upgrade-backup.snapshot

  # 2. Perform upgrade
  talosctl -n $node upgrade --image $new_image --preserve=true --wait

  # 3. Wait for node ready
  kubectl wait --for=condition=Ready node/$node --timeout=10m

  # 4. Verify health
  talosctl -n $node health --wait-timeout=5m
}
```

---

## Security Compliance Testing

```bash
#!/bin/bash
# tests/security-tests.sh

# Test disk encryption
test_disk_encryption() {
  local node=$1

  local encrypted=$(talosctl -n $node get disks -o yaml | grep -c 'encrypted: true')
  if [ "$encrypted" -lt 1 ]; then
    echo "ERROR: Disk encryption not enabled on $node"
    exit 1
  fi
}

# Test minimal services
test_minimal_services() {
  local node=$1
  local max_services=10

  local running=$(talosctl -n $node services | grep -c "Running")
  if [ "$running" -gt "$max_services" ]; then
    echo "ERROR: Too many services ($running > $max_services) on $node"
    talosctl -n $node services
    exit 1
  fi
}

# Test API access restrictions
test_api_access() {
  local node=$1

  # Should not be accessible from public internet
  # This test assumes you're running from inside the network
  timeout 5 talosctl -n $node version > /dev/null || {
    echo "ERROR: Cannot access Talos API on $node"
    exit 1
  }
}

# Run all security tests
run_security_suite() {
  local nodes="10.0.1.10 10.0.1.11 10.0.1.12"

  for node in $nodes; do
    echo "Running security tests on $node..."
    test_disk_encryption $node
    test_minimal_services $node
    test_api_access $node
  done

  echo "All security tests passed!"
}
```
