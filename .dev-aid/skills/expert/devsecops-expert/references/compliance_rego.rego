# Extracted from SKILL.md Section 3.6 — Compliance as Code with OPA/Rego
# Covers: CIS Kubernetes Benchmark, SOC2 controls, PCI-DSS requirements.

package compliance

import future.keywords.in

# CIS Kubernetes Benchmark checks
deny[msg] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    not container.securityContext.runAsNonRoot
    msg := sprintf("Container %s must set runAsNonRoot", [container.name])
}

deny[msg] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    container.securityContext.privileged
    msg := sprintf("Container %s must not be privileged", [container.name])
}

# SOC2 controls
deny[msg] {
    input.kind == "Deployment"
    not input.spec.template.spec.serviceAccountName
    msg := "Deployments must specify a service account"
}

deny[msg] {
    input.kind == "Service"
    input.spec.type == "LoadBalancer"
    not input.metadata.annotations["service.beta.kubernetes.io/aws-load-balancer-internal"]
    msg := "LoadBalancer services must be internal"
}

# PCI-DSS requirements
deny[msg] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    env := container.env[_]
    contains(lower(env.name), "password")
    env.value != null
    msg := sprintf("Container %s has hardcoded password in env", [container.name])
}

# Generate compliance report
compliance_report = {
    "passed": count([r | r := deny[_]; false]),
    "failed": count(deny),
    "violations": deny,
    "timestamp": time.now_ns(),
    "frameworks": ["CIS", "SOC2", "PCI-DSS"],
}
