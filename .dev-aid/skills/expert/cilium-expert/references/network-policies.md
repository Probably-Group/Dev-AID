# Cilium Network Policy Reference

## Overview

Comprehensive examples of Cilium network policies covering L3/L4, L7 (HTTP/gRPC/Kafka), DNS-based policies, and advanced patterns.

## L3/L4 Network Policies

### Basic Allow/Deny Patterns

```yaml
# Default deny all ingress/egress in namespace
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  endpointSelector: {}
  ingress: []
  egress: []
```

```yaml
# Allow DNS for all pods
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
      rules:
        dns:
        - matchPattern: "*"
```

```yaml
# Allow specific pod-to-pod communication
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: frontend-to-backend
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      app: frontend
  egress:
  - toEndpoints:
    - matchLabels:
        app: backend
        io.kubernetes.pod.namespace: production
    toPorts:
    - ports:
      - port: "8080"
        protocol: TCP
```

### Namespace Isolation

```yaml
# Isolate tenants by namespace
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: tenant-isolation
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
# Environment isolation (dev/staging/prod)
apiVersion: cilium.io/v2
kind: CiliumClusterwideNetworkPolicy
metadata:
  name: env-isolation
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
```

## L7 HTTP Policies

### Path-Based Filtering

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: api-gateway-policy
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
      - port: "8080"
        protocol: TCP
      rules:
        http:
        - method: "GET"
          path: "/api/v1/(users|products)/.*"
          headers:
          - "X-API-Key: .*"
        - method: "POST"
          path: "/api/v1/orders"
          headers:
          - "Content-Type: application/json"
```

### Method and Header-Based Filtering

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: strict-http-policy
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      app: secure-api
  ingress:
  - fromEndpoints:
    - matchLabels:
        app: authorized-client
    toPorts:
    - ports:
      - port: "443"
        protocol: TCP
      rules:
        http:
        - method: "GET|POST|PUT|DELETE"
          path: "/api/.*"
          headers:
          - "Authorization: Bearer .*"
          - "Content-Type: application/json"
```

## DNS-Based Policies

### FQDN Egress Control

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: external-api-access
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      app: payment-processor
  egress:
  # Allow specific external domains
  - toFQDNs:
    - matchName: "api.stripe.com"
    - matchName: "api.paypal.com"
    - matchPattern: "*.amazonaws.com"
    toPorts:
    - ports:
      - port: "443"
        protocol: TCP
  # Allow Kubernetes DNS
  - toEndpoints:
    - matchLabels:
        io.kubernetes.pod.namespace: kube-system
        k8s-app: kube-dns
    toPorts:
    - ports:
      - port: "53"
        protocol: UDP
      rules:
        dns:
        - matchPattern: "*.stripe.com"
        - matchPattern: "*.paypal.com"
        - matchPattern: "*.amazonaws.com"
```

### DNS Security Policies

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: dns-security
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      app: webapp
  egress:
  # Only allow approved domains
  - toEndpoints:
    - matchLabels:
        k8s-app: kube-dns
    toPorts:
    - ports:
      - port: "53"
        protocol: UDP
      rules:
        dns:
        # Explicitly list allowed domains
        - matchName: "api.company.com"
        - matchPattern: "*.company.com"
        - matchName: "cdn.cloudflare.com"
        # Block common C2 domains
        - matchPattern: "*.tk"
          action: DENY
        - matchPattern: "*.top"
          action: DENY
```

## gRPC Policies

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: grpc-policy
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      app: grpc-server
  ingress:
  - fromEndpoints:
    - matchLabels:
        app: grpc-client
    toPorts:
    - ports:
      - port: "50051"
        protocol: TCP
      rules:
        l7proto: grpc
        http:
        - method: "POST"
          path: "/myapi.UserService/GetUser"
        - method: "POST"
          path: "/myapi.UserService/CreateUser"
```

## Kafka Policies

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: kafka-policy
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      app: kafka-consumer
  egress:
  - toEndpoints:
    - matchLabels:
        app: kafka-broker
    toPorts:
    - ports:
      - port: "9092"
        protocol: TCP
      rules:
        kafka:
        - role: "consume"
          topic: "orders"
        - role: "consume"
          topic: "payments"
```

## Entity-Based Policies

```yaml
# Allow access to cluster services
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: allow-cluster-entities
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      app: webapp
  egress:
  # Allow Kubernetes API server
  - toEntities:
    - kube-apiserver
  # Allow DNS
  - toEntities:
    - kube-dns
  # Allow all cluster services
  - toEntities:
    - cluster
  # Allow external world (internet)
  - toEntities:
    - world
    toPorts:
    - ports:
      - port: "443"
        protocol: TCP
```

## Host Firewall

```yaml
apiVersion: cilium.io/v2
kind: CiliumClusterwideNetworkPolicy
metadata:
  name: host-firewall
spec:
  nodeSelector: {}
  ingress:
  # Allow SSH from bastion hosts only
  - fromCIDR:
    - 10.0.1.0/24
    toPorts:
    - ports:
      - port: "22"
        protocol: TCP
  # Allow Kubernetes API server
  - fromEntities:
    - cluster
    toPorts:
    - ports:
      - port: "6443"
        protocol: TCP
  # Allow kubelet API
  - fromEntities:
    - cluster
    toPorts:
    - ports:
      - port: "10250"
        protocol: TCP
  # Allow node-to-node
  - fromCIDR:
    - 10.0.0.0/16
    toPorts:
    - ports:
      - port: "4240"
        protocol: TCP
      - port: "4244"
        protocol: TCP
  egress:
  - toEntities:
    - all
```

## Advanced Patterns

### Canary Deployment Policy

```yaml
# Allow gradual traffic shift to canary
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: canary-policy
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      app: frontend
  egress:
  # Stable backend
  - toEndpoints:
    - matchLabels:
        app: backend
        version: stable
    toPorts:
    - ports:
      - port: "8080"
        protocol: TCP
  # Canary backend
  - toEndpoints:
    - matchLabels:
        app: backend
        version: canary
    toPorts:
    - ports:
      - port: "8080"
        protocol: TCP
```

### Service Mesh mTLS

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: mtls-required
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      app: payment-service
  ingress:
  - fromEndpoints:
    - matchLabels:
        app: api-gateway
    authentication:
      mode: "required"
```

### Rate Limiting (via Envoy)

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: rate-limit-policy
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
      - port: "8080"
        protocol: TCP
      rules:
        http:
        - method: "POST"
          path: "/api/.*"
          headerMatches:
          - mismatch:
              name: "X-Rate-Limit"
              value: "exceeded"
```

## Testing & Validation

### Audit Mode Testing

```yaml
# Test policy without enforcement
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: audit-mode-policy
  namespace: production
  annotations:
    cilium.io/policy-audit-mode: "true"
spec:
  endpointSelector:
    matchLabels:
      app: webapp
  ingress:
  - fromEndpoints:
    - matchLabels:
        app: frontend
```

### Policy Validation Script

```bash
#!/bin/bash
# Validate policies before applying

# Check syntax
kubectl apply --dry-run=client -f policy.yaml

# Apply in audit mode first
kubectl apply -f policy.yaml

# Monitor for 1 hour
hubble observe --verdict AUDIT --namespace production

# If no issues, remove audit annotation
kubectl annotate cnp audit-mode-policy -n production \
  cilium.io/policy-audit-mode-

# Verify enforcement
hubble observe --verdict DENIED --namespace production
```

## Best Practices

1. **Default Deny**: Start with deny-all, then allow specific traffic
2. **Identity Over IPs**: Use labels instead of CIDR where possible
3. **Always Allow DNS**: Include kube-dns in every namespace policy
4. **Namespace Labels**: Prevent cross-namespace traffic leaks
5. **Audit Mode First**: Test policies before enforcing
6. **L7 Selectively**: Only use L7 policies where needed (overhead)
7. **Document Intent**: Use annotations to explain policy purpose
8. **Version Control**: Store policies in Git, use GitOps
9. **Monitor Continuously**: Alert on unexpected policy denies
10. **Regular Reviews**: Quarterly review and remove unused policies
