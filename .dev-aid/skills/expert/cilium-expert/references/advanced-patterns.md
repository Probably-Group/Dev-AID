# Cilium Advanced Patterns

## Overview

Advanced implementation patterns for Cilium including multi-cluster networking, service mesh features, canary deployments, and complex security scenarios.

## Multi-Cluster Networking

### ClusterMesh Setup

```bash
# Cluster 1 (us-east)
helm install cilium cilium/cilium \
  --namespace kube-system \
  --set cluster.name=us-east \
  --set cluster.id=1 \
  --set clustermesh.useAPIServer=true \
  --set clustermesh.apiserver.service.type=LoadBalancer

# Cluster 2 (us-west)
helm install cilium cilium/cilium \
  --namespace kube-system \
  --set cluster.name=us-west \
  --set cluster.id=2 \
  --set clustermesh.useAPIServer=true \
  --set clustermesh.apiserver.service.type=LoadBalancer

# Connect clusters
cilium clustermesh connect --context us-east --destination-context us-west

# Verify connection
cilium clustermesh status
```

### Global Services

```yaml
# Global Service (accessible from all clusters)
apiVersion: v1
kind: Service
metadata:
  name: global-backend
  namespace: production
  annotations:
    service.cilium.io/global: "true"
    service.cilium.io/shared: "true"
spec:
  type: ClusterIP
  selector:
    app: backend
  ports:
  - port: 8080
    protocol: TCP
```

### Cross-Cluster Network Policies

```yaml
# Cross-cluster network policy
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: allow-cross-cluster
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
        # Matches pods in ANY connected cluster
    toPorts:
    - ports:
      - port: "8080"
        protocol: TCP
```

### Cluster Affinity

```yaml
# Prefer local cluster, failover to remote
apiVersion: v1
kind: Service
metadata:
  name: affinity-backend
  namespace: production
  annotations:
    service.cilium.io/global: "true"
    service.cilium.io/affinity: "local"
spec:
  type: ClusterIP
  selector:
    app: backend
  ports:
  - port: 8080
```

## Service Mesh Patterns

### Canary Deployments with Traffic Splitting

```yaml
# Stable backend deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-stable
  namespace: production
spec:
  replicas: 9
  selector:
    matchLabels:
      app: backend
      version: stable
  template:
    metadata:
      labels:
        app: backend
        version: stable
    spec:
      containers:
      - name: backend
        image: backend:v1.0.0
---
# Canary backend deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-canary
  namespace: production
spec:
  replicas: 1  # 10% traffic
  selector:
    matchLabels:
      app: backend
      version: canary
  template:
    metadata:
      labels:
        app: backend
        version: canary
    spec:
      containers:
      - name: backend
        image: backend:v2.0.0
---
# Service for traffic splitting
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: production
spec:
  selector:
    app: backend  # Matches both stable and canary
  ports:
  - port: 8080
```

### Circuit Breaking

```yaml
apiVersion: cilium.io/v2
kind: CiliumEnvoyConfig
metadata:
  name: circuit-breaker
  namespace: production
spec:
  services:
  - name: backend
    namespace: production
  resources:
  - "@type": type.googleapis.com/envoy.config.cluster.v3.Cluster
    name: backend
    connect_timeout: 5s
    circuit_breakers:
      thresholds:
      - priority: DEFAULT
        max_connections: 1000
        max_pending_requests: 100
        max_requests: 1000
        max_retries: 3
    outlier_detection:
      consecutive_5xx: 5
      interval: 30s
      base_ejection_time: 30s
      max_ejection_percent: 50
```

### Retries and Timeouts

```yaml
apiVersion: cilium.io/v2
kind: CiliumEnvoyConfig
metadata:
  name: retry-policy
  namespace: production
spec:
  services:
  - name: backend
    namespace: production
  resources:
  - "@type": type.googleapis.com/envoy.config.route.v3.RouteConfiguration
    name: backend-route
    virtual_hosts:
    - name: backend
      domains: ["*"]
      routes:
      - match:
          prefix: "/"
        route:
          cluster: backend
          timeout: 15s
          retry_policy:
            retry_on: "5xx"
            num_retries: 3
            per_try_timeout: 5s
```

## Advanced Security Patterns

### Dynamic Egress Gateway

```yaml
# Egress gateway pod with static IP
apiVersion: v1
kind: Pod
metadata:
  name: egress-gateway
  namespace: egress
  labels:
    app: egress-gateway
spec:
  hostNetwork: true
  containers:
  - name: proxy
    image: envoy:latest
---
# Policy to route traffic through gateway
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: egress-via-gateway
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      egress-policy: gateway
  egress:
  # Route to external via gateway
  - toEndpoints:
    - matchLabels:
        app: egress-gateway
        io.kubernetes.pod.namespace: egress
  egressDeny:
  # Deny direct external access
  - toEntities:
    - world
```

### Mutual TLS Between Services

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: mtls-between-services
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      app: payment-service
  ingress:
  - fromEndpoints:
    - matchLabels:
        app: order-service
    authentication:
      mode: "required"
    toPorts:
    - ports:
      - port: "8443"
        protocol: TCP
      rules:
        http:
        - method: "POST"
          path: "/api/v1/charge"
```

### Service Identity Verification

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: verify-spiffe-id
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      app: secure-api
  ingress:
  - fromEndpoints:
    - matchLabels:
        app: trusted-client
    authentication:
      mode: "required"
    toPorts:
    - ports:
      - port: "443"
        protocol: TCP
      terminatingTLS:
        secret:
          name: server-cert
      originatingTLS:
        secret:
          name: client-cert
        trusted:
          - "spiffe://cluster.local/ns/production/sa/trusted-client"
```

## Advanced L7 Policies

### gRPC with Method-Level Authorization

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: grpc-method-authz
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      app: user-service
  ingress:
  # Read-only methods
  - fromEndpoints:
    - matchLabels:
        role: reader
    toPorts:
    - ports:
      - port: "50051"
        protocol: TCP
      rules:
        l7proto: grpc
        http:
        - method: "POST"
          path: "/user.v1.UserService/GetUser"
        - method: "POST"
          path: "/user.v1.UserService/ListUsers"
  # Write methods
  - fromEndpoints:
    - matchLabels:
        role: writer
    toPorts:
    - ports:
      - port: "50051"
        protocol: TCP
      rules:
        l7proto: grpc
        http:
        - method: "POST"
          path: "/user.v1.UserService/CreateUser"
        - method: "POST"
          path: "/user.v1.UserService/UpdateUser"
        - method: "POST"
          path: "/user.v1.UserService/DeleteUser"
```

### Kafka Topic Authorization

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: kafka-topic-authz
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      app: kafka-broker
  ingress:
  # Order service can produce to orders topic
  - fromEndpoints:
    - matchLabels:
        app: order-service
    toPorts:
    - ports:
      - port: "9092"
        protocol: TCP
      rules:
        kafka:
        - role: "produce"
          topic: "orders"
  # Payment service can consume from orders
  - fromEndpoints:
    - matchLabels:
        app: payment-service
    toPorts:
    - ports:
      - port: "9092"
        protocol: TCP
      rules:
        kafka:
        - role: "consume"
          topic: "orders"
        - role: "produce"
          topic: "payments"
```

### HTTP Header-Based Routing

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: header-based-routing
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      app: api-gateway
  ingress:
  # Premium users get access to v2 API
  - fromEndpoints:
    - matchLabels:
        tier: premium
    toPorts:
    - ports:
      - port: "443"
        protocol: TCP
      rules:
        http:
        - method: "GET|POST"
          path: "/api/v2/.*"
          headers:
          - "X-User-Tier: premium"
  # Free users limited to v1 API
  - fromEndpoints:
    - matchLabels:
        tier: free
    toPorts:
    - ports:
      - port: "443"
        protocol: TCP
      rules:
        http:
        - method: "GET"
          path: "/api/v1/.*"
```

## Advanced Observability

### Distributed Tracing Integration

```yaml
# Enable tracing with OpenTelemetry
hubble:
  export:
    dynamic:
      enabled: true
      config:
        configMapName: hubble-tracing-config
        content:
          - name: otel-export
            type: opentelemetry
            endpoint: otel-collector.observability:4317
            headers:
              x-trace-id: "{.flow.trace_id}"
            tls:
              enabled: true
              ca: /etc/cilium/certs/ca.crt
```

### Custom Metrics Export

```yaml
# Export custom metrics to Prometheus
hubble:
  metrics:
    enabled:
      - dns:query;ignoreAAAA
      - drop:sourceContext=pod;destinationContext=pod
      - tcp:sourceContext=pod;destinationContext=pod
      - flow:sourceContext=pod;destinationContext=pod;labelsContext=source_namespace,destination_namespace
      - port-distribution:sourceContext=pod;destinationContext=pod
      - icmp:sourceContext=pod;destinationContext=pod
      - http:sourceContext=pod;destinationContext=pod;labelsContext=source_namespace,destination_namespace
    # Custom labels
    customLabels:
      - source_namespace
      - destination_namespace
      - traffic_direction
```

### Flow Aggregation

```yaml
# Aggregate flows for analytics
apiVersion: v1
kind: ConfigMap
metadata:
  name: hubble-flow-aggregation
  namespace: kube-system
data:
  config.yaml: |
    aggregation:
      - name: namespace-traffic-matrix
        fields:
          - source.namespace
          - destination.namespace
          - verdict
        interval: 1m
      - name: service-latency
        fields:
          - destination.service
          - l7.latency_ns
        interval: 5m
```

## Testing & Validation

### Comprehensive Connectivity Test

```bash
#!/bin/bash
# comprehensive-connectivity-test.sh

# Test pod-to-pod
cilium connectivity test \
  --test pod-to-pod \
  --test pod-to-world \
  --test pod-to-cidr

# Test services
cilium connectivity test \
  --test service-to-service \
  --test service-to-world

# Test policies
cilium connectivity test \
  --test policy \
  --test policy-audit

# Test L7
cilium connectivity test \
  --test l7-http \
  --test l7-https

# Test encryption
cilium connectivity test \
  --test encryption

# Test multi-cluster (if ClusterMesh)
cilium connectivity test \
  --test pod-to-remote-clustermesh-service
```

### Policy Validation Pipeline

```yaml
# GitLab CI pipeline
stages:
  - validate
  - test
  - deploy

validate-policies:
  stage: validate
  script:
    - kubectl apply --dry-run=client -f policies/
    - cilium policy validate policies/

test-policies:
  stage: test
  script:
    - kubectl apply -f policies/ --namespace=staging
    - kubectl annotate cnp --all -n staging cilium.io/policy-audit-mode="true"
    - sleep 300  # Monitor for 5 minutes
    - ./scripts/check-audit-denies.sh
    - kubectl annotate cnp --all -n staging cilium.io/policy-audit-mode-

deploy-policies:
  stage: deploy
  when: manual
  script:
    - kubectl apply -f policies/ --namespace=production
```

## Best Practices

1. **Multi-Cluster**: Use ClusterMesh for HA and DR
2. **Service Mesh**: Leverage sidecar-less architecture for performance
3. **Canary**: Test new versions with gradual traffic shifting
4. **Circuit Breaking**: Prevent cascade failures
5. **mTLS**: Secure service-to-service communication
6. **Method-Level AuthZ**: Fine-grained access control
7. **Distributed Tracing**: Correlate network flows with application traces
8. **Automated Testing**: CI/CD pipeline for policy validation
9. **Audit Mode**: Always test before enforcement
10. **Documentation**: Document complex patterns and rationale
