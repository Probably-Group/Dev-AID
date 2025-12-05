# Cilium Observability with Hubble

## Overview

Hubble provides deep network visibility for Cilium-powered Kubernetes clusters. This guide covers comprehensive observability patterns, troubleshooting workflows, and monitoring setup.

## Installation & Setup

### Basic Hubble Installation

```bash
# Install Hubble with Relay and UI
helm upgrade cilium cilium/cilium \
  --namespace kube-system \
  --reuse-values \
  --set hubble.relay.enabled=true \
  --set hubble.ui.enabled=true \
  --set hubble.metrics.enabled=true

# Verify installation
kubectl -n kube-system get pods -l k8s-app=hubble-relay
kubectl -n kube-system get pods -l k8s-app=hubble-ui

# Port-forward to Hubble UI
cilium hubble ui
# Opens browser to http://localhost:12000
```

### Advanced Hubble Configuration

```yaml
# Full Hubble configuration via Helm values
hubble:
  enabled: true

  # Relay configuration (aggregates flows from all agents)
  relay:
    enabled: true
    replicas: 2
    resources:
      limits:
        memory: 1Gi
        cpu: 1
      requests:
        memory: 512Mi
        cpu: 100m
    prometheus:
      enabled: true
      port: 9965

  # UI configuration
  ui:
    enabled: true
    replicas: 1
    ingress:
      enabled: true
      hosts:
        - hubble.example.com

  # Metrics for Prometheus
  metrics:
    enabled:
      - dns:query;ignoreAAAA
      - drop
      - tcp
      - flow
      - icmp
      - http
    serviceMonitor:
      enabled: true

  # Export flows to external systems
  export:
    static:
      enabled: true
      filePath: /var/run/cilium/hubble/events.log
      maxSizeMB: 10
      maxBackups: 5
      compress: true

  # Redact sensitive information
  redact:
    enabled: true
    httpURLQuery: true
    httpUserInfo: true
```

## Hubble CLI Commands

### Basic Flow Observation

```bash
# Watch all flows in real-time
hubble observe

# Watch flows in specific namespace
hubble observe --namespace production

# Show last N flows
hubble observe --last 100

# Filter by verdict
hubble observe --verdict DROPPED
hubble observe --verdict FORWARDED

# Filter by protocol
hubble observe --protocol http
hubble observe --protocol dns

# JSON output
hubble observe --output json
```

### Advanced Filtering

```bash
# Show flows from specific pod
hubble observe --pod production/frontend-7d4c8b6f9-x2m5k

# Show flows between pods
hubble observe \
  --from-pod production/frontend-7d4c8b6f9-x2m5k \
  --to-pod production/backend-5f8d9c4b2-p7k3n

# Filter by labels
hubble observe --from-label app=frontend --to-label app=backend

# HTTP method filtering
hubble observe --http-method GET

# HTTP status filtering
hubble observe --http-status 404
```

## Troubleshooting Workflows

### Debug Policy Denies

```bash
# Step 1: Identify dropped flows
hubble observe --verdict DROPPED --namespace production

# Step 2: Filter to specific pods
hubble observe \
  --verdict DROPPED \
  --from-pod production/frontend-7d4c8b6f9-x2m5k \
  --to-label app=backend

# Step 3: Check drop reason
hubble observe \
  --verdict DROPPED \
  --from-pod production/frontend-7d4c8b6f9-x2m5k \
  --output json | jq -r '.flow.drop_reason_desc'
```

### Debug DNS Issues

```bash
# Check DNS queries
hubble observe --protocol dns --namespace production

# Look for failed DNS queries
hubble observe --protocol dns --verdict DROPPED

# Check DNS responses
hubble observe --protocol dns --output json | \
  jq -r '.flow | "\(.time) \(.source.pod_name) queried \(.l7.dns.query) -> \(.verdict)"'
```

## Prometheus Metrics

### Key Metrics

```promql
# Policy denies per second
rate(cilium_drop_count_total{reason="Policy denied"}[5m])

# HTTP response codes
sum by (status) (rate(hubble_http_responses_total[5m]))

# DNS queries per second
rate(hubble_dns_queries_total[5m])

# Failed DNS queries
rate(hubble_dns_queries_total{rcode!="NOERROR"}[5m])
```

### Example Alerts

```yaml
groups:
- name: cilium-alerts
  rules:
  - alert: HighPolicyDenyRate
    expr: rate(cilium_drop_count_total{reason="Policy denied"}[5m]) > 10
    for: 5m
    labels:
      severity: warning
```

## Best Practices

1. **Enable Hubble from Day 1**: Don't wait for issues
2. **Use Selective L7 Visibility**: Only where needed (overhead)
3. **Export Critical Flows**: Send policy denies to SIEM
4. **Set Up Alerts**: Monitor deny rates, DNS failures
5. **Redact Sensitive Data**: Enable redaction for headers/URLs
6. **Test Before Enforce**: Use audit mode first
