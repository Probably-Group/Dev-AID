# Cilium Security Examples

## Overview

Security-focused examples for Cilium deployments, covering zero-trust networking, encryption, network segmentation, and threat mitigation.

## Zero-Trust Networking

### Default-Deny Namespace Policy

```yaml
# Step 1: Default deny all traffic
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

```yaml
# Step 2: Allow essential services (DNS)
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: allow-dns
  namespace: production
spec:
  endpointSelector: {}
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

```yaml
# Step 3: Allow Kubernetes API access
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: allow-api-server
  namespace: production
spec:
  endpointSelector: {}
  egress:
  - toEntities:
    - kube-apiserver
```

### Identity-Based Policies

**Bad** - IP-based policies:
```yaml
# INSECURE: IPs change, can be spoofed
egress:
- toCIDR:
  - 10.0.1.42/32
```

**Good** - Identity-based policies:
```yaml
# SECURE: Identity cannot be spoofed
egress:
- toEndpoints:
  - matchLabels:
      app: backend
      version: v2
      env: production
```

## Encryption

### WireGuard Transparent Encryption

```bash
# Enable WireGuard encryption for all pod-to-pod traffic
helm upgrade cilium cilium/cilium \
  --namespace kube-system \
  --reuse-values \
  --set encryption.enabled=true \
  --set encryption.type=wireguard

# Verify encryption status
kubectl -n kube-system exec -ti ds/cilium -- cilium encrypt status

# Check encrypted flows
hubble observe --verdict ENCRYPTED
```

### Per-Namespace Encryption

```yaml
# Force encryption for sensitive namespace
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: encrypted-namespace
  namespace: payment-processing
  annotations:
    cilium.io/encrypt: "true"
spec:
  endpointSelector: {}
  ingress:
  - fromEndpoints:
    - matchLabels:
        io.kubernetes.pod.namespace: payment-processing
  egress:
  - toEndpoints:
    - matchLabels:
        io.kubernetes.pod.namespace: payment-processing
```

### mTLS with SPIRE

```bash
# Enable mutual TLS
helm upgrade cilium cilium/cilium \
  --namespace kube-system \
  --reuse-values \
  --set authentication.mutual.spire.enabled=true \
  --set authentication.mutual.spire.install.enabled=true
```

```yaml
# Require mTLS for sensitive services
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: mtls-required
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      app: payment-service
      pci-scope: "true"
  ingress:
  - fromEndpoints:
    - matchLabels:
        app: api-gateway
    authentication:
      mode: "required"
```

## Network Segmentation

### Multi-Tenancy Isolation

```yaml
# Tenant A - Complete isolation
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: tenant-a-isolation
  namespace: tenant-a
spec:
  endpointSelector: {}
  ingress:
  - fromEndpoints:
    - matchLabels:
        io.kubernetes.pod.namespace: tenant-a
  egress:
  - toEndpoints:
    - matchLabels:
        io.kubernetes.pod.namespace: tenant-a
  - toEntities:
    - kube-apiserver
    - kube-dns
```

```yaml
# Explicit deny cross-tenant traffic
apiVersion: cilium.io/v2
kind: CiliumClusterwideNetworkPolicy
metadata:
  name: deny-cross-tenant
spec:
  endpointSelector:
    matchLabels:
      tenant: tenant-a
  ingressDeny:
  - fromEndpoints:
    - matchLabels:
        tenant: tenant-b
  egressDeny:
  - toEndpoints:
    - matchLabels:
        tenant: tenant-b
```

### Environment Isolation (Dev/Staging/Prod)

```yaml
# Production isolation - deny from dev/staging
apiVersion: cilium.io/v2
kind: CiliumClusterwideNetworkPolicy
metadata:
  name: production-isolation
spec:
  endpointSelector:
    matchLabels:
      env: production
  ingress:
  - fromEndpoints:
    - matchLabels:
        env: production
  ingressDeny:
  - fromEndpoints:
    - matchLabels:
        env: development
  - fromEndpoints:
    - matchLabels:
        env: staging
```

### PCI-DSS Segmentation

```yaml
# Isolate PCI cardholder data environment (CDE)
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: pci-cde-isolation
  namespace: payment-processing
spec:
  endpointSelector:
    matchLabels:
      pci-scope: "true"
  ingress:
  # Only allow from authorized gateways
  - fromEndpoints:
    - matchLabels:
        app: payment-gateway
        pci-authorized: "true"
    toPorts:
    - ports:
      - port: "8443"
        protocol: TCP
      rules:
        http:
        - method: "POST"
          path: "/api/v1/payment"
          headers:
          - "Authorization: Bearer .*"
  egress:
  # Only allow to PCI-compliant services
  - toEndpoints:
    - matchLabels:
        pci-scope: "true"
  # Allow encrypted external payment processors
  - toFQDNs:
    - matchName: "api.stripe.com"
    - matchName: "api.paypal.com"
    toPorts:
    - ports:
      - port: "443"
        protocol: TCP
```

## Egress Control

### FQDN-Based Egress Filtering

```yaml
# Restrict egress to approved domains only
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: egress-whitelist
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      app: webapp
  egress:
  # Approved SaaS services
  - toFQDNs:
    - matchName: "api.stripe.com"
    - matchName: "api.sendgrid.com"
    - matchName: "api.twilio.com"
    - matchPattern: "*.amazonaws.com"
    toPorts:
    - ports:
      - port: "443"
        protocol: TCP
  # Allow DNS
  - toEndpoints:
    - matchLabels:
        k8s-app: kube-dns
    toPorts:
    - ports:
      - port: "53"
        protocol: UDP
      rules:
        dns:
        - matchPattern: "*.stripe.com"
        - matchPattern: "*.sendgrid.com"
        - matchPattern: "*.twilio.com"
        - matchPattern: "*.amazonaws.com"
  # Allow cluster services
  - toEntities:
    - kube-apiserver
```

### DNS Security Policies

```yaml
# Block known malicious domains
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: dns-security
  namespace: production
spec:
  endpointSelector: {}
  egress:
  - toEndpoints:
    - matchLabels:
        k8s-app: kube-dns
    toPorts:
    - ports:
      - port: "53"
        protocol: UDP
      rules:
        dns:
        # Block common malware C2 domains
        - matchPattern: "*.tk"
          action: DENY
        - matchPattern: "*.top"
          action: DENY
        - matchPattern: "*.xyz"
          action: DENY
        # Block known DGA patterns
        - matchPattern: "*[0-9]{10,}*"
          action: DENY
```

## L7 Security Policies

### API Gateway Protection

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: api-gateway-security
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      app: api-gateway
  ingress:
  - fromEndpoints:
    - matchLabels:
        app: frontend
    toPorts:
    - ports:
      - port: "443"
        protocol: TCP
      rules:
        http:
        # Only allow specific HTTP methods
        - method: "GET|POST|PUT|DELETE"
          path: "/api/v1/.*"
          headers:
          # Require authentication
          - "Authorization: Bearer .*"
          # Prevent header injection
          - "X-Forwarded-For: ^[0-9.]+$"
          # Content type validation
          - "Content-Type: application/json"
        # Block SQL injection patterns
        - method: "GET"
          path: "/api/v1/users"
          headers:
          # Deny if query contains SQL keywords
          - mismatch:
              name: "query"
              value: ".*(union|select|insert|update|delete|drop).*"
```

### Rate Limiting via L7 Policy

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: rate-limit-api
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      app: public-api
  ingress:
  - fromEntities:
    - world
    toPorts:
    - ports:
      - port: "443"
        protocol: TCP
      rules:
        http:
        # Rate limit to 100 req/min per client
        - method: "POST"
          path: "/api/v1/.*"
          headerMatches:
          - name: "X-RateLimit-Remaining"
            value: "^[1-9][0-9]*$"
```

## Host Firewall

### Node Protection

```yaml
apiVersion: cilium.io/v2
kind: CiliumClusterwideNetworkPolicy
metadata:
  name: host-firewall-ingress
spec:
  nodeSelector: {}
  ingress:
  # SSH from bastion only
  - fromCIDR:
    - 10.0.1.0/24  # Bastion subnet
    toPorts:
    - ports:
      - port: "22"
        protocol: TCP
  # Kubernetes API
  - fromCIDR:
    - 0.0.0.0/0
    toPorts:
    - ports:
      - port: "6443"
        protocol: TCP
  # Kubelet API (only from control plane)
  - fromCIDR:
    - 10.0.0.0/24  # Control plane subnet
    toPorts:
    - ports:
      - port: "10250"
        protocol: TCP
  # Cilium health checks
  - fromEntities:
    - cluster
    toPorts:
    - ports:
      - port: "4240"
        protocol: TCP
  # Deny all other ingress
  ingressDeny:
  - fromCIDR:
    - 0.0.0.0/0
```

### etcd Protection

```yaml
apiVersion: cilium.io/v2
kind: CiliumClusterwideNetworkPolicy
metadata:
  name: etcd-protection
spec:
  endpointSelector:
    matchLabels:
      component: etcd
  ingress:
  # Only API servers can access etcd
  - fromEndpoints:
    - matchLabels:
        component: kube-apiserver
    toPorts:
    - ports:
      - port: "2379"
        protocol: TCP
      - port: "2380"
        protocol: TCP
  ingressDeny:
  # Deny all other access
  - fromEndpoints:
    - {}
```

## Threat Detection

### Suspicious Traffic Monitoring

```bash
# Monitor for data exfiltration (large egress to internet)
hubble observe \
  --to-entity world \
  --verdict FORWARDED \
  --output json | \
  jq 'select(.flow.Summary.bytes_sent > 1000000)'

# Monitor for DNS tunneling
hubble observe \
  --protocol dns \
  --output json | \
  jq 'select(.l7.dns.query | length > 50)'

# Monitor for port scanning
hubble observe \
  --verdict DROPPED \
  --output json | \
  jq 'select(.drop_reason_desc == "Policy denied") | group_by(.source.pod_name) | map(select(length > 10))'
```

### Automated Threat Response

```yaml
# Example: Auto-quarantine pods with suspicious traffic
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: quarantine-suspicious-pods
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      threat-level: high
  ingress: []
  egress:
  # Only allow DNS and logging
  - toEntities:
    - kube-dns
  - toEndpoints:
    - matchLabels:
        app: logging-agent
```

## Compliance Examples

### HIPAA Network Isolation

```yaml
# Isolate PHI data tier
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: phi-isolation
  namespace: healthcare
spec:
  endpointSelector:
    matchLabels:
      data-classification: phi
  ingress:
  # Only authorized application tier
  - fromEndpoints:
    - matchLabels:
        app: healthcare-app
        hipaa-authorized: "true"
    toPorts:
    - ports:
      - port: "5432"
        protocol: TCP
  egress:
  # Only to encrypted backup
  - toEndpoints:
    - matchLabels:
        app: backup-service
        encryption: aes-256
```

### SOC2 Audit Logging

```yaml
# Enable audit logging for compliance
hubble:
  export:
    static:
      enabled: true
      filePath: /var/run/cilium/hubble/audit.log
      maxSizeMB: 100
      maxBackups: 90  # 90 days retention
      fieldMask:
        - time
        - verdict
        - source.namespace
        - source.pod_name
        - destination.namespace
        - destination.pod_name
        - destination.fqdn
        - l7
```

## Security Testing

### Penetration Test Policy

```yaml
# Allow controlled pen-testing from specific pods
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: pentest-policy
  namespace: security
spec:
  endpointSelector:
    matchLabels:
      app: pentest-pod
  egress:
  # Allow scanning target namespace only
  - toEndpoints:
    - matchLabels:
        io.kubernetes.pod.namespace: target-namespace
  # Log all activity
  annotations:
    cilium.io/policy-audit-mode: "true"
```

### Red Team Simulation

```bash
# Monitor during red team exercise
hubble observe \
  --namespace production \
  --verdict DROPPED \
  --output json | \
  tee redteam-$(date +%Y%m%d).log | \
  jq -r '.flow | "\(.time) \(.source.namespace)/\(.source.pod_name) -> \(.destination.namespace)/\(.destination.pod_name) \(.drop_reason_desc)"'
```

## Best Practices

1. **Defense in Depth**: Layer multiple security controls
2. **Least Privilege**: Grant minimum necessary access
3. **Zero Trust**: Never trust, always verify
4. **Encrypt Everything**: Use WireGuard or mTLS
5. **Monitor Continuously**: Alert on policy violations
6. **Regular Audits**: Review policies quarterly
7. **Incident Response**: Have runbooks for policy-related incidents
8. **Test Policies**: Use audit mode before enforcement
9. **Document Intent**: Explain why each policy exists
10. **Compliance First**: Design policies to meet regulatory requirements
