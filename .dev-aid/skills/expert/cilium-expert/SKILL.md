---
name: cilium-expert
version: 2.0.0
description: "Kubernetes networking with Cilium eBPF including network policies, service mesh, L7 policies, and Hubble observability. Use when writing CiliumNetworkPolicy resources, configuring eBPF-based networking, setting up Hubble monitoring, or implementing zero-trust network segmentation. Do NOT use for non-Cilium CNI plugins like Calico, Flannel, or Weave."
compatibility: "Cilium 1.14+, Kubernetes 1.28+, Linux with eBPF"
risk_level: HIGH
---

# Cilium Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-863: Authorization Bypass (CVE-2025-30162)**
- NEVER: Assume egress policies work with Gateway API + LB-IPAM/BGP
- ALWAYS: Test egress policies specifically, upgrade to v1.15.15+/v1.16.8+/v1.17.2+

**CWE-436: IPv6 Policy Bypass (CVE-2023-27594)**
- NEVER: Route IPv6 through Cilium without verifying policy enforcement
- ALWAYS: Disable IPv6 if not needed, verify policies for both IP versions

**CWE-319: Cleartext Transmission (CVE-2024-25630)**
- NEVER: Assume all traffic encrypted with WireGuard enabled
- ALWAYS: Verify encryption on all paths, check for unencrypted packet leaks

**CWE-284: Default Allow Policy**
- NEVER: Rely on default "allow all" without explicit deny policies
- ALWAYS: Set `policyEnforcementMode: always`, create default-deny policies

### 0.3 Risk Level: HIGH

**Verification requirements for HIGH risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 Default Deny Network Policy (CWE-284)

**Principle:** Start with deny-all policy. Explicitly allow required traffic only.

```yaml
# ❌ WRONG - No default deny
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: allow-frontend
spec:
  endpointSelector:
    matchLabels:
      app: frontend
  ingress:
    - fromEndpoints:
        - {}  # Allows all!

# ✅ CORRECT - Default deny with explicit allows
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: default-deny
  namespace: production
spec:
  endpointSelector: {}  # Apply to all pods
  ingress: []  # Deny all ingress
  egress: []   # Deny all egress
---
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      app: backend
  ingress:
    - fromEndpoints:
        - matchLabels:
            app: frontend
      toPorts:
        - ports:
            - port: "8080"
              protocol: TCP
```

### 1.2 Identity-Based Access Control (CWE-863)

**Principle:** Use Cilium identities for workload authentication. Never rely on IP addresses.

### 1.3 L7 Policy Enforcement (CWE-20)

**Principle:** Use L7 policies to validate HTTP methods, paths, and headers.

### 1.4 Encryption in Transit (CWE-319)

**Principle:** Enable WireGuard or IPsec for pod-to-pod encryption.

### 1.5 Egress Control (CWE-918)

**Principle:** Control egress to prevent data exfiltration. Use FQDN policies.

### 1.6 Hubble Observability (CWE-778)

**Principle:** Enable Hubble for network visibility and audit logging.

---

## 2. Version Requirements

**ALWAYS use these minimum versions:**

```yaml
cilium: v1.15.0+
hubble: v0.13.0+
cilium-cli: v0.16.0+
kubernetes: v1.28.0+
```

---

## 3. Code Patterns

### 3.1 WHEN implementing network policies

```yaml
# ❌ WRONG - Overly permissive policy
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: allow-all-web
spec:
  endpointSelector:
    matchLabels:
      role: web
  ingress:
    - fromEntities:
        - world  # Allows all external traffic!
      toPorts:
        - ports:
            - port: "443"

# ✅ CORRECT - Restrictive policy with L7 rules
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: web-api-policy
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      app: api
      tier: backend

  ingress:
    # Allow from frontend pods only
    - fromEndpoints:
        - matchLabels:
            app: frontend
            tier: web
      toPorts:
        - ports:
            - port: "8080"
              protocol: TCP
          rules:
            http:
              # L7: Only allow specific paths and methods
              - method: "GET"
                path: "/api/v1/users/.*"
              - method: "POST"
                path: "/api/v1/users"
                headers:
                  - 'Content-Type: application/json'
              - method: "GET"
                path: "/health"

    # Allow from Prometheus for scraping
    - fromEndpoints:
        - matchLabels:
            app: prometheus
            namespace: monitoring
      toPorts:
        - ports:
            - port: "9090"
              protocol: TCP
          rules:
            http:
              - method: "GET"
                path: "/metrics"

  egress:
    # Allow to database
    - toEndpoints:
        - matchLabels:
            app: postgres
            tier: database
      toPorts:
        - ports:
            - port: "5432"
              protocol: TCP

    # Allow DNS resolution
    - toEndpoints:
        - matchLabels:
            k8s:io.kubernetes.pod.namespace: kube-system
            k8s-app: kube-dns
      toPorts:
        - ports:
            - port: "53"
              protocol: UDP
          rules:
            dns:
              - matchPattern: "*.production.svc.cluster.local"
              - matchPattern: "*.kube-system.svc.cluster.local"
```

### 3.2 WHEN configuring FQDN-based egress

```yaml
# ❌ WRONG - Allow all external traffic
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
spec:
  egress:
    - toEntities:
        - world

# ✅ CORRECT - FQDN-restricted egress
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: external-api-egress
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      app: payment-service

  egress:
    # Allow DNS first
    - toEndpoints:
        - matchLabels:
            k8s:io.kubernetes.pod.namespace: kube-system
            k8s-app: kube-dns
      toPorts:
        - ports:
            - port: "53"
              protocol: UDP
          rules:
            dns:
              - matchPattern: "*"

    # Allow specific external APIs only
    - toFQDNs:
        - matchName: "api.stripe.com"
        - matchName: "api.paypal.com"
      toPorts:
        - ports:
            - port: "443"
              protocol: TCP

    # Allow AWS services (pattern match)
    - toFQDNs:
        - matchPattern: "*.amazonaws.com"
        - matchPattern: "*.s3.*.amazonaws.com"
      toPorts:
        - ports:
            - port: "443"
              protocol: TCP
```

### 3.3 WHEN enabling encryption

```yaml
# ❌ WRONG - No encryption
apiVersion: cilium.io/v2
kind: CiliumConfig
metadata:
  name: cilium-config
spec:
  encryption:
    enabled: false

# ✅ CORRECT - WireGuard encryption enabled
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: cilium
  namespace: kube-system
spec:
  chart:
    spec:
      chart: cilium
      version: "1.15.x"
      sourceRef:
        kind: HelmRepository
        name: cilium
  values:
    # Enable WireGuard encryption
    encryption:
      enabled: true
      type: wireguard
      wireguard:
        userspaceFallback: false

    # Enable node-to-node encryption
    nodeEncryption: true

    # Enable strict mode (require encryption)
    encryption:
      strictMode:
        enabled: true
        cidr: "10.0.0.0/8"
        allowRemoteNodeIdentities: false

    # Hubble observability
    hubble:
      enabled: true
      relay:
        enabled: true
      ui:
        enabled: true
      metrics:
        enabled:
          - dns
          - drop
          - tcp
          - flow
          - port-distribution
          - icmp
          - httpV2:exemplars=true;labelsContext=source_ip,source_namespace,source_workload,destination_ip,destination_namespace,destination_workload,traffic_direction

    # Security context
    securityContext:
      privileged: false
      capabilities:
        ciliumAgent:
          - CHOWN
          - KILL
          - NET_ADMIN
          - NET_RAW
          - IPC_LOCK
          - SYS_MODULE
          - SYS_ADMIN
          - SYS_RESOURCE
          - DAC_OVERRIDE
          - FOWNER
          - SETGID
          - SETUID
```

### 3.4 WHEN implementing cluster mesh

```yaml
# ✅ CORRECT - Secure cluster mesh configuration
apiVersion: cilium.io/v2
kind: CiliumClusterConfig
metadata:
  name: cluster-mesh-config
spec:
  cluster:
    name: cluster-1
    id: 1

  clustermesh:
    # Enable cluster mesh
    enabled: true

    # API server configuration
    apiserver:
      replicas: 3
      resources:
        requests:
          cpu: 100m
          memory: 128Mi
        limits:
          cpu: 1000m
          memory: 1Gi

      # TLS configuration
      tls:
        auto:
          enabled: true
          method: helm
          certValidityDuration: 1095  # 3 years

    # Use kvstoremesh for better performance
    useAPIServer: true

---
# Cross-cluster network policy
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: cross-cluster-api
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      app: api-gateway

  ingress:
    - fromEndpoints:
        - matchLabels:
            app: frontend
            # Allow from any cluster
            io.cilium.k8s.policy.cluster: "*"
      toPorts:
        - ports:
            - port: "443"
              protocol: TCP

  egress:
    - toEndpoints:
        - matchLabels:
            app: backend-service
            # Target specific cluster
            io.cilium.k8s.policy.cluster: "cluster-2"
      toPorts:
        - ports:
            - port: "8080"
              protocol: TCP
```

### 3.5 WHEN configuring Hubble for observability

```yaml
# ✅ CORRECT - Comprehensive Hubble configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: hubble-config
  namespace: kube-system
data:
  config.yaml: |
    # Enable flow visibility
    enableIPv4: true
    enableIPv6: false

    # Metrics configuration
    metrics:
      enabled:
        - dns:query;ignoreAAAA
        - drop
        - tcp
        - flow
        - icmp
        - http

    # Flow export (for SIEM integration)
    export:
      static:
        enabled: true
        filePath: /var/run/cilium/hubble/events.log
        allowList:
          - '{"verdict":["DROPPED","ERROR"]}'
        fieldMask:
          - time
          - source
          - destination
          - verdict
          - drop_reason
          - l7

---
# Hubble UI with authentication
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: hubble-ui
  namespace: kube-system
  annotations:
    nginx.ingress.kubernetes.io/auth-type: basic
    nginx.ingress.kubernetes.io/auth-secret: hubble-ui-auth
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - hubble.internal.example.com
      secretName: hubble-ui-tls
  rules:
    - host: hubble.internal.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: hubble-ui
                port:
                  number: 80
```

### 3.6 WHEN implementing service mesh features

```yaml
# ✅ CORRECT - Cilium service mesh with mTLS
apiVersion: cilium.io/v2
kind: CiliumEnvoyConfig
metadata:
  name: envoy-lb-listener
  namespace: production
spec:
  services:
    - name: api-service
      namespace: production

  backendServices:
    - name: api-backend
      namespace: production

  resources:
    - "@type": type.googleapis.com/envoy.config.listener.v3.Listener
      name: api-listener
      filter_chains:
        - filters:
            - name: envoy.filters.network.http_connection_manager
              typed_config:
                "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
                stat_prefix: api_ingress
                http_filters:
                  # Rate limiting
                  - name: envoy.filters.http.local_ratelimit
                    typed_config:
                      "@type": type.googleapis.com/envoy.extensions.filters.http.local_ratelimit.v3.LocalRateLimit
                      stat_prefix: http_local_rate_limiter
                      token_bucket:
                        max_tokens: 100
                        tokens_per_fill: 100
                        fill_interval: 1s
                      filter_enabled:
                        runtime_key: local_rate_limit_enabled
                        default_value:
                          numerator: 100
                          denominator: HUNDRED

                  # Router
                  - name: envoy.filters.http.router
                    typed_config:
                      "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router

---
# Ingress policy with TLS termination
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: ingress-tls-policy
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      app: ingress-gateway

  ingress:
    - fromEntities:
        - world
      toPorts:
        - ports:
            - port: "443"
              protocol: TCP
          terminatingTLS:
            secret:
              name: ingress-tls-cert
              namespace: production
            trustedCA: |
              -----BEGIN CERTIFICATE-----
              ...
              -----END CERTIFICATE-----
          rules:
            http:
              - method: "GET|POST|PUT|DELETE"
                path: "/api/.*"
                headers:
                  - 'X-Request-ID: .*'
```

---

## 4. Anti-Patterns

**NEVER:**
- Deploy without default-deny policies
- Use IP-based policies (use labels/identities)
- Allow `world` entity without L7 filtering
- Disable Hubble in production
- Skip encryption for sensitive workloads
- Allow unrestricted egress
- Use `fromEntities: [all]` in ingress
- Forget DNS egress for FQDN policies

---

## 5. Testing

**ALWAYS test network policies:**

```bash
#!/bin/bash
# Test Cilium network policies

set -euo pipefail

# Verify Cilium is healthy
cilium status --wait

# Test connectivity
cilium connectivity test

# Verify policy enforcement
cilium policy get -o jsonpath='{.spec}'

# Test specific policy
kubectl run test-pod --image=curlimages/curl --rm -it --restart=Never -- \
  curl -v --max-time 5 http://api-service.production:8080/health

# Check Hubble flows
hubble observe --namespace production --verdict DROPPED --last 100

# Verify encryption
cilium encrypt status

# Export policy for review
cilium policy get -o yaml > policies-backup.yaml
```

---

## 6. Pre-Generation Checklist

**BEFORE generating any Cilium configuration:**

- [ ] Default deny policy exists
- [ ] Policies use labels, not IPs
- [ ] L7 rules validate HTTP methods/paths
- [ ] FQDN policies for external egress
- [ ] DNS egress allowed for FQDN policies
- [ ] Encryption enabled (WireGuard/IPsec)
- [ ] Hubble enabled for observability
- [ ] Cross-cluster policies use cluster identities
- [ ] Ingress TLS termination configured
- [ ] Rate limiting for public endpoints

---

**Performance**: Quality over speed. Verify all code examples compile. Never skip security checks. See `template-references/performance-notes.md` for full guidelines.