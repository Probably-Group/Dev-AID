# Performance Optimization Patterns

This document contains performance optimization patterns for Talos OS clusters.

---

## Pattern 1: Image Optimization

**Good: Optimized Installer Image Configuration**
```yaml
machine:
  install:
    disk: /dev/sda
    image: ghcr.io/siderolabs/installer:v1.6.0
    # Use specific version, not latest
    wipe: false  # Preserve data on upgrades

  # Pre-pull system extension images
  registries:
    mirrors:
      docker.io:
        endpoints:
          - https://registry-mirror.example.com  # Local mirror
      ghcr.io:
        endpoints:
          - https://ghcr-mirror.example.com
    config:
      registry-mirror.example.com:
        tls:
          insecureSkipVerify: false  # Always verify TLS
```

**Bad: Unoptimized Image Configuration**
```yaml
machine:
  install:
    disk: /dev/sda
    image: ghcr.io/siderolabs/installer:latest  # Don't use latest
    wipe: true  # Unnecessary data loss on every change
    # No registry mirrors - slow pulls from internet
```

---

## Pattern 2: Resource Limits and etcd Optimization

**Good: Properly Tuned etcd and Kubelet**
```yaml
cluster:
  etcd:
    extraArgs:
      quota-backend-bytes: "8589934592"      # 8GB quota
      auto-compaction-retention: "1000"       # Keep 1000 revisions
      snapshot-count: "10000"                 # Snapshot every 10k txns
      heartbeat-interval: "100"               # 100ms heartbeat
      election-timeout: "1000"                # 1s election timeout
      max-snapshots: "5"                      # Keep 5 snapshots
      max-wals: "5"                           # Keep 5 WAL files

machine:
  kubelet:
    extraArgs:
      kube-reserved: cpu=200m,memory=512Mi
      system-reserved: cpu=200m,memory=512Mi
      eviction-hard: memory.available<500Mi,nodefs.available<10%
      image-gc-high-threshold: "85"
      image-gc-low-threshold: "80"
      max-pods: "110"
```

**Bad: Default Settings Without Limits**
```yaml
cluster:
  etcd: {}  # No quotas - can fill disk

machine:
  kubelet: {}  # No reservations - system can OOM
```

---

## Pattern 3: Kernel Tuning for Performance

**Good: Optimized Kernel Parameters**
```yaml
machine:
  sysctls:
    # Network performance
    net.core.somaxconn: "32768"
    net.core.netdev_max_backlog: "16384"
    net.ipv4.tcp_max_syn_backlog: "8192"
    net.ipv4.tcp_slow_start_after_idle: "0"
    net.ipv4.tcp_tw_reuse: "1"

    # Memory management
    vm.swappiness: "0"                    # Disable swap
    vm.overcommit_memory: "1"             # Allow overcommit
    vm.panic_on_oom: "0"                  # Don't panic on OOM

    # File descriptors
    fs.file-max: "2097152"
    fs.inotify.max_user_watches: "1048576"
    fs.inotify.max_user_instances: "8192"

    # Conntrack for high connection counts
    net.netfilter.nf_conntrack_max: "1048576"
    net.nf_conntrack_max: "1048576"

  # CPU scheduler optimization
  kernel:
    modules:
      - name: br_netfilter
      - name: overlay
```

**Bad: No Kernel Tuning**
```yaml
machine:
  sysctls: {}  # Default limits may cause connection drops
  # Missing required kernel modules
```

---

## Pattern 4: Storage Optimization

**Good: Optimized Storage Configuration**
```yaml
machine:
  install:
    disk: /dev/sda
    diskSelector:
      size: '>= 120GB'
      type: ssd            # Prefer SSD for etcd
      model: 'Samsung*'    # Target specific hardware

  # Encryption with performance options
  systemDiskEncryption:
    state:
      provider: luks2
      keys:
        - slot: 0
          tpm: {}
      options:
        - no_read_workqueue   # Improve read performance
        - no_write_workqueue  # Improve write performance
    ephemeral:
      provider: luks2
      keys:
        - slot: 0
          tpm: {}
      cipher: aes-xts-plain64
      keySize: 256           # Balance security/performance
      options:
        - no_read_workqueue
        - no_write_workqueue

  # Configure disks for data workloads
  disks:
    - device: /dev/sdb
      partitions:
        - mountpoint: /var/lib/longhorn
          size: 0  # Use all remaining space
```

**Bad: Unoptimized Storage**
```yaml
machine:
  install:
    disk: /dev/sda  # No selector - might use slow HDD
    wipe: true      # Data loss risk

  systemDiskEncryption:
    state:
      provider: luks2
      cipher: aes-xts-plain64
      keySize: 512  # Slower than necessary
      # Missing performance options
```

---

## Pattern 5: Network Performance

**Good: Optimized Network Stack**
```yaml
machine:
  network:
    interfaces:
      - interface: eth0
        dhcp: false
        addresses:
          - 10.0.1.10/24
        mtu: 9000           # Jumbo frames for cluster traffic
        routes:
          - network: 0.0.0.0/0
            gateway: 10.0.1.1
            metric: 100

    # Use performant DNS
    nameservers:
      - 10.0.1.1            # Local DNS resolver
      - 1.1.1.1             # Cloudflare as backup

cluster:
  network:
    cni:
      name: none            # Install optimized CNI separately
    podSubnets:
      - 10.244.0.0/16
    serviceSubnets:
      - 10.96.0.0/12

  proxy:
    mode: ipvs              # Better performance than iptables
    extraArgs:
      ipvs-scheduler: lc    # Least connections
```

**Bad: Default Network Settings**
```yaml
machine:
  network:
    interfaces:
      - interface: eth0
        dhcp: true          # Less predictable
        # No MTU optimization

cluster:
  proxy:
    mode: iptables          # Slower for large clusters
```
