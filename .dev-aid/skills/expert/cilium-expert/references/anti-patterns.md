# Cilium Anti-Patterns

## Overview

Common mistakes and anti-patterns to avoid when deploying and managing Cilium. Learn from these mistakes to prevent production outages and security issues.

## Policy Anti-Patterns

### Anti-Pattern 1: No Default-Deny Policies

❌ **WRONG**: Assume cluster is secure without policies

```yaml
# No network policies = all traffic allowed!
# Pods can talk to anything, anywhere
# Lateral movement is trivial for attackers
```

**Impact**:
- Zero network security
- Lateral movement attacks
- Data exfiltration risk
- Compliance violations

✅ **CORRECT**: Implement default-deny per namespace

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: default-deny
  namespace: production
spec:
  endpointSelector: {}
  ingress: []
  egress: []
```

### Anti-Pattern 2: Forgetting DNS in Default-Deny

❌ **WRONG**: Block all egress without allowing DNS

```yaml
# Pods can't resolve DNS names!
# All DNS queries fail
spec:
  egress: []  # Nothing allowed
```

**Impact**:
- DNS resolution failures
- Application startup failures
- Service discovery broken

✅ **CORRECT**: Always allow DNS

```yaml
egress:
- toEndpoints:
  - matchLabels:
      io.kubernetes.pod.namespace: kube-system
      k8s-app: kube-dns
  toPorts:
  - ports:
    - port: "53"
      protocol: UDP
```

### Anti-Pattern 3: Using IP Addresses Instead of Labels

❌ **WRONG**: Hard-code pod IPs

```yaml
egress:
- toCIDR:
  - 10.0.1.42/32  # Pod IP - will break when pod restarts
```

**Impact**:
- Breaks when pods restart
- Difficult to maintain
- No identity verification
- Security bypass risk

✅ **CORRECT**: Use identity-based selectors

```yaml
egress:
- toEndpoints:
  - matchLabels:
      app: backend
      version: v2
```

### Anti-Pattern 4: Not Testing Policies in Audit Mode

❌ **WRONG**: Deploy enforcing policies directly to production

```yaml
# No audit mode - might break production traffic
spec:
  endpointSelector: {...}
  ingress: [...]
```

**Impact**:
- Unexpected service outages
- Broken dependencies
- Emergency rollbacks
- Customer impact

✅ **CORRECT**: Test with audit mode first

```yaml
metadata:
  annotations:
    cilium.io/policy-audit-mode: "true"
spec:
  endpointSelector: {...}
  ingress: [...]
# Review Hubble logs for AUDIT verdicts
# Remove annotation when ready to enforce
```

### Anti-Pattern 5: Overly Broad FQDN Patterns

❌ **WRONG**: Allow entire TLDs

```yaml
toFQDNs:
- matchPattern: "*.com"  # Allows ANY .com domain!
- matchPattern: "*"      # Allows EVERYTHING!
```

**Impact**:
- Defeats purpose of egress control
- Data exfiltration risk
- Malware C2 communication
- Compliance violations

✅ **CORRECT**: Be specific with domains

```yaml
toFQDNs:
- matchName: "api.stripe.com"
- matchPattern: "*.stripe.com"  # Only Stripe subdomains
```

### Anti-Pattern 6: Missing Namespace Labels

❌ **WRONG**: Allow cross-namespace without namespace selector

```yaml
ingress:
- fromEndpoints:
  - matchLabels:
      app: frontend
  # Missing namespace label - allows ANY namespace!
```

**Impact**:
- Cross-namespace traffic leaks
- Multi-tenant isolation broken
- Security boundary bypass

✅ **CORRECT**: Always include namespace

```yaml
ingress:
- fromEndpoints:
  - matchLabels:
      app: frontend
      io.kubernetes.pod.namespace: production
```

### Anti-Pattern 7: Conflicting Policies

❌ **WRONG**: Multiple policies with conflicting rules

```yaml
# Policy 1: Allow all egress
egress:
- toEntities:
  - world

# Policy 2: Deny all egress (same selector)
egress: []
```

**Impact**:
- Unpredictable behavior
- Difficult troubleshooting
- Policy confusion
- Security gaps

✅ **CORRECT**: Single source of truth per endpoint

```yaml
# One policy per endpoint selector
# Or use explicit deny rules
```

## Observability Anti-Patterns

### Anti-Pattern 8: Missing Hubble for Troubleshooting

❌ **WRONG**: Deploy Cilium without observability

```yaml
# Can't see why traffic is being dropped!
# Blind troubleshooting with kubectl logs
# No visibility into policy enforcement
```

**Impact**:
- Hours of debugging
- Unknown policy denies
- No security visibility
- Compliance gaps

✅ **CORRECT**: Always enable Hubble

```bash
helm upgrade cilium cilium/cilium \
  --set hubble.relay.enabled=true \
  --set hubble.ui.enabled=true

# Troubleshoot with visibility
hubble observe --verdict DROPPED
```

### Anti-Pattern 9: Not Monitoring Policy Enforcement

❌ **WRONG**: Set policies and forget

**Impact**:
- Unknown security incidents
- Policy drift
- Undetected attacks
- Compliance violations

✅ **CORRECT**: Continuous monitoring

```bash
# Alert on policy denies
hubble observe --verdict DENIED --output json | \
  jq -r '.flow | "\(.time) \(.source.namespace)/\(.source.pod_name) -> \(.destination.namespace)/\(.destination.pod_name) DENIED"'

# Export metrics to Prometheus
# Alert on spike in dropped flows
```

### Anti-Pattern 10: Full Flow Capture in Production

❌ **WRONG**: 100% flow sampling in large clusters

```yaml
hubble:
  metrics:
    enabled: true
  # No sampling - captures everything
```

**Impact**:
- High CPU usage
- Memory pressure
- Disk space exhaustion
- Performance degradation

✅ **CORRECT**: Sample flows in production

```yaml
hubble:
  metrics:
    enabled:
      - dns:query;ignoreAAAA
      - drop
      - flow:sourceContext=pod;destinationContext=pod
  redact:
    enabled: true
```

## Resource Anti-Patterns

### Anti-Pattern 11: Insufficient Resource Limits

❌ **WRONG**: No resource limits on Cilium agents

```yaml
# Can cause OOM kills, crashes
# Agents compete with workload pods
# Node instability
```

**Impact**:
- Agent OOM kills
- Network disruption
- Node instability
- Cluster outages

✅ **CORRECT**: Set appropriate limits

```yaml
resources:
  limits:
    memory: 4Gi
    cpu: 2
  requests:
    memory: 2Gi
    cpu: 500m
```

### Anti-Pattern 12: Default BPF Map Sizes for Large Clusters

❌ **WRONG**: Use defaults for 1000+ node clusters

```bash
# Default map sizes too small
# Connection tracking failures
# Packet drops
```

**Impact**:
- Connection failures
- Dropped packets
- Service disruptions
- Scalability issues

✅ **CORRECT**: Tune based on cluster size

```bash
helm upgrade cilium cilium/cilium \
  --set bpf.ctTcpMax=1048576 \
  --set bpf.ctAnyMax=524288 \
  --set bpf.natMax=1048576 \
  --set bpf.policyMapMax=131072
```

## Performance Anti-Patterns

### Anti-Pattern 13: L7 Policies on All Traffic

❌ **WRONG**: Enable L7 parsing everywhere

```yaml
# L7 parsing on all pods causes high overhead
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

**Impact**:
- High CPU usage
- Increased latency
- Memory pressure
- Reduced throughput

✅ **CORRECT**: L7 only where needed

```yaml
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

### Anti-Pattern 14: Tunnel Mode When Native Routing Available

❌ **WRONG**: Use VXLAN on flat network

```bash
# Unnecessary encapsulation overhead
helm install cilium cilium/cilium \
  --set tunnel=vxlan
```

**Impact**:
- Reduced throughput
- Increased latency
- CPU overhead
- MTU issues

✅ **CORRECT**: Use native routing

```bash
helm install cilium cilium/cilium \
  --set tunnel=disabled \
  --set autoDirectNodeRoutes=true
```

### Anti-Pattern 15: Complex Policy Selectors

❌ **WRONG**: Overly complex label matching

```yaml
spec:
  endpointSelector:
    matchExpressions:
    - key: app
      operator: In
      values: [v1, v2, v3, v4, v5, v6, v7, v8]
    - key: tier
      operator: NotIn
      values: [deprecated, legacy, old]
    - key: region
      operator: Exists
```

**Impact**:
- Slow policy evaluation
- High CPU usage
- Policy regeneration delays

✅ **CORRECT**: Simplify selectors

```yaml
spec:
  endpointSelector:
    matchLabels:
      app: frontend
      tier: active
```

## Deployment Anti-Patterns

### Anti-Pattern 16: Upgrading Cilium in Production First

❌ **WRONG**: Test upgrades in production

```bash
# YOLO upgrade production
helm upgrade cilium cilium/cilium \
  --version 1.14.0
```

**Impact**:
- Production outages
- Data plane disruption
- Unexpected behavior
- Emergency rollbacks

✅ **CORRECT**: Test in staging first

```bash
# Test in staging
cilium connectivity test --test-namespace=cilium-test

# If successful, upgrade production with caution
helm upgrade cilium cilium/cilium \
  --version 1.14.0 \
  --set agent.updateStrategy.rollingUpdate.maxUnavailable=1
```

### Anti-Pattern 17: Not Running Connectivity Tests

❌ **WRONG**: Skip pre-upgrade testing

```bash
# Just upgrade without testing
helm upgrade cilium cilium/cilium
```

**Impact**:
- Unknown issues
- Runtime failures
- Policy breakage
- Service disruptions

✅ **CORRECT**: Always run connectivity test

```bash
# Before upgrade
cilium connectivity test

# After upgrade
cilium connectivity test --test-namespace=cilium-test
```

### Anti-Pattern 18: Missing Backup Procedures

❌ **WRONG**: No backup of Cilium configs

**Impact**:
- Cannot rollback
- Lost configurations
- Emergency recovery failures

✅ **CORRECT**: Backup before changes

```bash
# Backup ConfigMaps
kubectl get cm cilium-config -n kube-system -o yaml > cilium-config-backup.yaml

# Backup CNPs
kubectl get cnp --all-namespaces -o yaml > policies-backup.yaml

# Backup Helm values
helm get values cilium -n kube-system > values-backup.yaml
```

## Security Anti-Patterns

### Anti-Pattern 19: Disabled Encryption on Sensitive Traffic

❌ **WRONG**: No encryption for PII/PHI/PCI data

```bash
# Plaintext pod-to-pod traffic
# Network sniffing possible
```

**Impact**:
- Data exposure
- Compliance violations
- Security breaches
- Regulatory fines

✅ **CORRECT**: Enable WireGuard or mTLS

```bash
helm upgrade cilium cilium/cilium \
  --set encryption.enabled=true \
  --set encryption.type=wireguard
```

### Anti-Pattern 20: World-Wide Egress Allowed

❌ **WRONG**: Allow all internet access

```yaml
egress:
- toEntities:
  - world  # Allows EVERYTHING on the internet
```

**Impact**:
- Data exfiltration
- Malware C2 communication
- Compliance violations
- No egress control

✅ **CORRECT**: Explicit FQDN whitelist

```yaml
egress:
- toFQDNs:
  - matchName: "api.approved-service.com"
  - matchPattern: "*.approved-domain.com"
```

### Anti-Pattern 21: No Host Firewall

❌ **WRONG**: Unprotected Kubernetes nodes

```bash
# Nodes accessible from anywhere
# SSH exposed to internet
# No node-level policies
```

**Impact**:
- Node compromise
- Cluster takeover
- Lateral movement
- Data breaches

✅ **CORRECT**: Implement host firewall

```yaml
apiVersion: cilium.io/v2
kind: CiliumClusterwideNetworkPolicy
metadata:
  name: host-firewall
spec:
  nodeSelector: {}
  ingress:
  - fromCIDR:
    - 10.0.1.0/24  # Bastion only
    toPorts:
    - ports:
      - port: "22"
        protocol: TCP
```

## Operations Anti-Patterns

### Anti-Pattern 22: Manual Policy Management

❌ **WRONG**: `kubectl apply` policies manually

**Impact**:
- Configuration drift
- No version control
- Difficult rollbacks
- Team coordination issues

✅ **CORRECT**: GitOps with Argo/Flux

```yaml
# Store policies in Git
# Use Argo CD or Flux for deployment
# Automated rollbacks
# Audit trail
```

### Anti-Pattern 23: No Alerts on Policy Denies

❌ **WRONG**: Don't monitor policy enforcement

**Impact**:
- Unknown security events
- Missed attacks
- No incident detection
- Blind spots

✅ **CORRECT**: Alert on anomalies

```yaml
# Prometheus alert
- alert: HighPolicyDenyRate
  expr: rate(cilium_drop_count_total{reason="Policy denied"}[5m]) > 10
  for: 5m
  labels:
    severity: warning
```

## Summary

**Key Takeaways**:
1. ✅ Always default-deny, then allow specific traffic
2. ✅ Test policies in audit mode before enforcement
3. ✅ Use identity-based policies, not IPs
4. ✅ Enable Hubble for troubleshooting
5. ✅ Set resource limits on Cilium agents
6. ✅ Monitor policy enforcement continuously
7. ✅ Use L7 policies selectively
8. ✅ Test upgrades in non-production first
9. ✅ Enable encryption for sensitive data
10. ✅ Implement GitOps for policy management

**Remember**: Cilium controls cluster networking. Small mistakes can cause big outages. Always test, monitor, and validate before deploying to production.
