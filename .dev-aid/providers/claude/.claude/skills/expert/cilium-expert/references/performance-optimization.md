# Cilium Performance Optimization

## Overview

Performance optimization strategies for Cilium deployments, covering eBPF program efficiency, datapath selection, resource tuning, and monitoring overhead reduction.

## eBPF Program Optimization

### Pattern 1: Efficient Policy Selectors

**Bad** - Complex selectors cause slow policy evaluation:
```yaml
# BAD: Multiple label matches with regex-like behavior
spec:
  endpointSelector:
    matchExpressions:
    - key: app
      operator: In
      values: [frontend-v1, frontend-v2, frontend-v3, frontend-v4]
    - key: version
      operator: NotIn
      values: [deprecated, legacy]
```

**Good** - Simplified selectors with efficient matching:
```yaml
# GOOD: Single label with aggregated selector
spec:
  endpointSelector:
    matchLabels:
      app: frontend
      tier: web
```

### Pattern 2: Policy Caching with Endpoint Selectors

**Bad** - Policies that don't cache well:
```yaml
# BAD: CIDR-based rules require per-packet evaluation
egress:
- toCIDR:
  - 10.0.0.0/8
  - 172.16.0.0/12
  - 192.168.0.0/16
```

**Good** - Identity-based rules with eBPF map caching:
```yaml
# GOOD: Identity-based selectors use efficient BPF map lookups
egress:
- toEndpoints:
  - matchLabels:
      app: backend
      io.kubernetes.pod.namespace: production
- toEntities:
  - cluster
```

### Pattern 3: Minimize Policy Complexity

**Bad** - Overly complex policies:
```yaml
# BAD: 50+ ingress/egress rules per policy
spec:
  ingress:
  - fromEndpoints: [...]  # Rule 1
  - fromEndpoints: [...]  # Rule 2
  # ... 48 more rules
```

**Good** - Aggregate and simplify:
```yaml
# GOOD: Group related rules
spec:
  ingress:
  - fromEndpoints:
    - matchExpressions:
      - key: tier
        operator: In
        values: [web, api]
```

## Datapath Optimization

### Native Routing vs Tunneling

**Bad** - Tunnel mode (VXLAN) adds overhead:
```bash
# BAD: Tunnel mode encapsulation overhead
helm install cilium cilium/cilium \
  --set tunnel=vxlan
```

**Good** - Native routing (if network supports):
```bash
# GOOD: Native routing (no encapsulation)
helm install cilium cilium/cilium \
  --set tunnel=disabled \
  --set autoDirectNodeRoutes=true \
  --set ipv4NativeRoutingCIDR=10.0.0.0/8
```

### Enable Kube-proxy Replacement

**Bad** - Keep kube-proxy running:
```bash
# BAD: Dual datapath (Cilium + kube-proxy)
# Both process service traffic
```

**Good** - Full kube-proxy replacement:
```bash
# GOOD: eBPF-only datapath
helm install cilium cilium/cilium \
  --set kubeProxyReplacement=strict \
  --set k8sServiceHost=<API_SERVER_IP> \
  --set k8sServicePort=6443
```

### XDP Acceleration

```bash
# Enable XDP for packet processing at NIC level
helm upgrade cilium cilium/cilium \
  --set loadBalancer.acceleration=native \
  --set loadBalancer.mode=dsr \
  --set bpf.masquerade=true
```

## Resource Tuning

### BPF Map Sizes

**Bad** - Default map sizes for large clusters:
```bash
# BAD: May cause connection failures at scale
# Default: ctTcpMax=524288
```

**Good** - Tune based on cluster size:
```bash
# GOOD: Adjust for cluster workload
helm upgrade cilium cilium/cilium \
  --set bpf.ctTcpMax=1048576 \
  --set bpf.ctAnyMax=524288 \
  --set bpf.natMax=1048576 \
  --set bpf.neighMax=131072 \
  --set bpf.policyMapMax=131072
```

**Sizing Guidelines**:
- Small cluster (<50 nodes): Use defaults
- Medium (50-200 nodes): 2x defaults
- Large (200-1000 nodes): 4x defaults
- Very large (1000+ nodes): 8x defaults

### Agent Resource Limits

**Bad** - No resource limits:
```yaml
# BAD: Can cause OOM kills
# No limits specified
```

**Good** - Set appropriate limits:
```yaml
# GOOD: Based on cluster size
resources:
  limits:
    cpu: 4
    memory: 8Gi
  requests:
    cpu: 500m
    memory: 2Gi
```

**Sizing by Cluster**:
- Small: 2Gi memory, 1 CPU
- Medium: 4Gi memory, 2 CPU
- Large: 8Gi memory, 4 CPU
- Very large: 16Gi memory, 8 CPU

### Operator Resource Limits

```yaml
operator:
  resources:
    limits:
      cpu: 2
      memory: 2Gi
    requests:
      cpu: 100m
      memory: 512Mi
  replicas: 2  # HA
```

## L7 Policy Optimization

### Pattern 1: Selective L7 Enforcement

**Bad** - L7 policies on all traffic:
```yaml
# BAD: L7 parsing on all pods causes high overhead
spec:
  endpointSelector: {}
  ingress:
  - toPorts:
    - ports:
      - port: "8080"
      rules:
        http:
        - method: ".*"
```

**Good** - L7 only where needed:
```yaml
# GOOD: L7 only on specific services
spec:
  endpointSelector:
    matchLabels:
      app: api-gateway
      requires-l7: "true"
  ingress:
  - toPorts:
    - ports:
      - port: "8080"
      rules:
        http:
        - method: "GET|POST"
          path: "/api/v1/.*"
```

### Pattern 2: Efficient L7 Rules

**Bad** - Overly broad regex:
```yaml
# BAD: Expensive regex evaluation
http:
- path: ".*"
- path: "/.*"
```

**Good** - Specific patterns:
```yaml
# GOOD: Precise matching
http:
- path: "/api/v1/users"
- path: "/api/v1/products"
```

## Hubble Performance Tuning

### Pattern 1: Reduce Flow Capture Overhead

**Bad** - Full flow capture in production:
```yaml
# BAD: 100% sampling causes high CPU/memory
hubble:
  metrics:
    enabled: true
```

**Good** - Sampling for production:
```yaml
# GOOD: Sample flows
hubble:
  metrics:
    enabled:
      - dns:query;ignoreAAAA
      - drop
      - tcp
      - flow:sourceContext=pod;destinationContext=pod
      - http
  # Reduce cardinality
  redact:
    enabled: true
    httpURLQuery: true
    httpUserInfo: true
    httpHeaders:
      allow: ["Content-Type"]
```

### Pattern 2: Limit Flow Export

**Bad** - Export all flows:
```yaml
# BAD: High disk/network usage
export:
  static:
    enabled: true
```

**Good** - Export critical flows only:
```yaml
# GOOD: Selective export
export:
  static:
    enabled: true
    fieldMask:
      - time
      - verdict
      - drop_reason
      - source.namespace
      - destination.namespace
    # Filter: only export drops/denies
    filters:
      - verdict: ["DROPPED", "DENIED"]
```

## DNS Optimization

### Node-Local DNS Cache

**Bad** - All DNS queries to cluster DNS:
```bash
# BAD: Cross-node DNS latency
# Default CoreDNS
```

**Good** - Enable node-local DNS:
```bash
# GOOD: Local caching
helm upgrade cilium cilium/cilium \
  --set nodeLocalDNS.enabled=true \
  --set dnsproxy.enableDNSCompression=true \
  --set dnsproxy.endpointMaxIpPerHostname=50
```

### DNS Proxy Tuning

```bash
helm upgrade cilium cilium/cilium \
  --set dnsproxy.minTTL=300 \
  --set dnsproxy.maxTTL=3600 \
  --set dnsproxy.idleConnectionTimeout=120s
```

## Connection Tracking Optimization

### Pattern 1: GC Tuning

**Bad** - Default GC settings for high-connection workloads:
```bash
# BAD: May cause memory pressure
# Default GC interval
```

**Good** - Tune GC based on workload:
```bash
# GOOD: Adjust CT GC
helm upgrade cilium cilium/cilium \
  --set bpf.ctGCInterval=10s \
  --set bpf.ctMapEntriesGlobalTCP=1048576 \
  --set bpf.ctMapEntriesGlobalAny=524288
```

### Pattern 2: Timeout Tuning

```bash
# Adjust timeouts for workload
helm upgrade cilium cilium/cilium \
  --set bpf.ctTimeoutTCP=900s \
  --set bpf.ctTimeoutAny=60s
```

## Monitoring & Profiling

### Enable Metrics for Performance Analysis

```bash
# Enable detailed metrics
helm upgrade cilium cilium/cilium \
  --set prometheus.enabled=true \
  --set operator.prometheus.enabled=true \
  --set hubble.metrics.enabled="{dns,drop,tcp,flow,port-distribution,icmp,http}"
```

### Key Performance Metrics

```promql
# BPF map pressure
cilium_bpf_map_pressure > 0.8

# Policy regeneration time
histogram_quantile(0.99, rate(cilium_policy_regeneration_time_stats_seconds_bucket[5m]))

# Datapath latency
histogram_quantile(0.99, rate(cilium_datapath_conntrack_gc_duration_seconds_bucket[5m]))

# L7 proxy overhead
rate(cilium_proxy_upstream_reply_seconds_sum[5m]) / rate(cilium_proxy_upstream_reply_seconds_count[5m])

# Agent memory usage
cilium_agent_memory_bytes

# Endpoint regeneration rate
rate(cilium_endpoint_regenerations_total[5m])
```

### Profiling Cilium Agent

```bash
# Enable pprof
kubectl -n kube-system port-forward ds/cilium 6060:6060

# CPU profile
curl http://localhost:6060/debug/pprof/profile?seconds=30 > cpu.prof
go tool pprof -http=:8080 cpu.prof

# Memory profile
curl http://localhost:6060/debug/pprof/heap > mem.prof
go tool pprof -http=:8080 mem.prof

# Goroutine profile
curl http://localhost:6060/debug/pprof/goroutine > goroutine.prof
```

## Network Optimization

### MTU Configuration

```bash
# Set optimal MTU (avoid fragmentation)
helm upgrade cilium cilium/cilium \
  --set mtu=1500  # Or 9000 for jumbo frames
```

### Bandwidth Manager

```bash
# Enable bandwidth management for QoS
helm upgrade cilium cilium/cilium \
  --set bandwidthManager.enabled=true
```

### BBR Congestion Control

```bash
# Enable BBR for better throughput
kubectl -n kube-system exec ds/cilium -- \
  sysctl -w net.ipv4.tcp_congestion_control=bbr
```

## Upgrade Strategies

### Rolling Update Best Practices

```bash
# Pre-pull images
kubectl -n kube-system set image ds/cilium \
  cilium-agent=quay.io/cilium/cilium:v1.14.0 \
  --dry-run=server

# Gradual rollout
helm upgrade cilium cilium/cilium \
  --set agent.updateStrategy.type=RollingUpdate \
  --set agent.updateStrategy.rollingUpdate.maxUnavailable=1

# Monitor during upgrade
watch kubectl -n kube-system get pods -l k8s-app=cilium
```

### Pre-flight Checks

```bash
# Run connectivity test before upgrade
cilium connectivity test

# Verify current health
cilium status

# Check for deprecated features
helm template cilium cilium/cilium --validate
```

## Troubleshooting Performance Issues

### High CPU Usage

```bash
# Check policy complexity
kubectl get cnp --all-namespaces -o json | jq '[.items[] | {name: .metadata.name, namespace: .metadata.namespace, rules: (.spec.ingress | length) + (.spec.egress | length)}] | sort_by(.rules) | reverse'

# Check endpoint count
kubectl -n kube-system exec ds/cilium -- cilium endpoint list | wc -l

# Check BPF map usage
kubectl -n kube-system exec ds/cilium -- cilium bpf map list
```

### High Memory Usage

```bash
# Check CT table size
kubectl -n kube-system exec ds/cilium -- cilium bpf ct list global | wc -l

# Check for memory leaks
kubectl top pods -n kube-system -l k8s-app=cilium

# Review resource limits
kubectl get ds cilium -n kube-system -o jsonpath='{.spec.template.spec.containers[0].resources}'
```

### Packet Drops

```bash
# Check for policy denies
hubble observe --verdict DROPPED --last 1000

# Check BPF program stats
kubectl -n kube-system exec ds/cilium -- cilium bpf metrics list

# Check for XDP drops
kubectl -n kube-system exec ds/cilium -- cilium bpf lb list
```

## Best Practices Summary

1. **Use Native Routing**: Avoid tunnel overhead when possible
2. **Enable kube-proxy Replacement**: Single eBPF datapath
3. **Tune BPF Map Sizes**: Based on cluster size and workload
4. **Set Resource Limits**: Prevent OOM kills and resource contention
5. **Selective L7 Policies**: Only where security requires it
6. **Sample Hubble Flows**: Reduce observability overhead in production
7. **Node-Local DNS**: Reduce DNS latency
8. **Monitor Performance**: Set up alerts for BPF map pressure, high latency
9. **Regular Profiling**: Identify bottlenecks before they impact users
10. **Test Upgrades**: Always test in non-production first
