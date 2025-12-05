# DevSecOps Threat Model

This document provides a comprehensive threat model for DevSecOps implementations, covering supply chain security, container security, and infrastructure threats.

## Assets

### Critical Assets Requiring Protection

1. **Source Code Repository**
   - Criticality: HIGH
   - Contains: Application code, infrastructure definitions, secrets configurations
   - Impact if compromised: Full system compromise, intellectual property theft

2. **CI/CD Pipeline**
   - Criticality: CRITICAL
   - Contains: Build systems, deployment credentials, artifact repositories
   - Impact if compromised: Supply chain attacks, production deployment of malicious code

3. **Container Registry**
   - Criticality: HIGH
   - Contains: Container images, SBOMs, signatures
   - Impact if compromised: Malicious image distribution, backdoor injection

4. **Secrets Management System**
   - Criticality: CRITICAL
   - Contains: Database credentials, API keys, certificates
   - Impact if compromised: Complete data breach, lateral movement

5. **Kubernetes Cluster**
   - Criticality: CRITICAL
   - Contains: Running workloads, customer data, service configurations
   - Impact if compromised: Data exfiltration, service disruption, ransomware

6. **Infrastructure as Code State**
   - Criticality: HIGH
   - Contains: Terraform state, CloudFormation stacks, resource configurations
   - Impact if compromised: Infrastructure manipulation, privilege escalation

---

## Threats

### Threat 1: Compromised Dependency (Supply Chain Attack)

**Description**: Attacker injects malicious code into a third-party dependency that is automatically pulled into builds.

**Attack Vector**:
- Typosquatting similar package names
- Compromising maintainer account
- Dependency confusion attack
- Backdoored transitive dependencies

**Impact**:
- **Confidentiality**: HIGH - Exfiltration of secrets and source code
- **Integrity**: HIGH - Malicious code in production
- **Availability**: MEDIUM - Potential for destructive payloads

**Likelihood**: MEDIUM (increasing with supply chain attacks like SolarWinds, Log4Shell)

**Mitigation**:
1. Pin all dependencies with integrity hashes (package-lock.json, go.sum)
2. Use dependency scanning (Snyk, Dependabot) in CI/CD
3. Implement SBOM generation and tracking
4. Use private package registry with approved packages
5. Enable dependency review in pull requests
6. Verify package signatures when available

**Verification**:
```yaml
# .github/workflows/dependency-check.yml
name: Dependency Security

on: [pull_request]

jobs:
  dependency-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/dependency-review-action@v4
        with:
          fail-on-severity: moderate
          deny-licenses: GPL-2.0, GPL-3.0

  snyk-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high
```

---

### Threat 2: Container Image Poisoning

**Description**: Malicious or vulnerable container images deployed to production through compromised base images or registry attacks.

**Attack Vector**:
- Compromised base image in public registry
- Registry credential theft
- Man-in-the-middle during image pull
- Unsigned/unverified images

**Impact**:
- **Confidentiality**: HIGH - Runtime access to secrets and data
- **Integrity**: HIGH - Arbitrary code execution in production
- **Availability**: HIGH - Container crashes, resource exhaustion

**Likelihood**: MEDIUM

**Mitigation**:
1. Use minimal, trusted base images (distroless, alpine from verified publishers)
2. Scan all images for CVEs before deployment (Trivy, Grype)
3. Sign images with Sigstore/Cosign
4. Verify image signatures at admission (Kyverno, OPA)
5. Use content trust (Docker Content Trust, Notary)
6. Pin base images by digest, not tag

**Verification**:
```yaml
# kyverno/verify-images.yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-image-signatures
spec:
  validationFailureAction: Enforce
  rules:
    - name: verify-signature
      match:
        any:
        - resources:
            kinds: [Pod]
      verifyImages:
      - imageReferences:
        - "ghcr.io/example/*"
        attestors:
        - entries:
          - keyless:
              subject: "https://github.com/example/*"
              issuer: "https://token.actions.githubusercontent.com"
              rekor:
                url: https://rekor.sigstore.dev
```

---

### Threat 3: Secrets Leakage

**Description**: Credentials, API keys, or tokens exposed through git commits, logs, or environment variables.

**Attack Vector**:
- Hardcoded secrets in source code
- Secrets in Docker image layers
- Secrets in CI/CD logs
- Exposed .env files
- Git history containing secrets

**Impact**:
- **Confidentiality**: CRITICAL - Full credential compromise
- **Integrity**: HIGH - Unauthorized access and modification
- **Availability**: MEDIUM - Service disruption through credential abuse

**Likelihood**: HIGH (very common mistake)

**Mitigation**:
1. Never commit secrets to git (use pre-commit hooks)
2. Scan git history for secrets (TruffleHog, Gitleaks)
3. Use external secret stores (Vault, AWS Secrets Manager)
4. Implement External Secrets Operator for Kubernetes
5. Rotate secrets immediately upon detection
6. Use workload identity instead of static credentials

**Verification**:
```yaml
# .github/workflows/secret-scan.yml
name: Secret Scanning

on: [push, pull_request]

jobs:
  trufflehog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: TruffleHog Secret Scan
        uses: trufflesecurity/trufflehog@v3.63.0
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
          extra_args: --fail --json
```

---

### Threat 4: Privilege Escalation via Misconfigured RBAC

**Description**: Attacker gains elevated privileges in Kubernetes through overly permissive RBAC policies.

**Attack Vector**:
- Service account with excessive permissions
- Binding to cluster-admin role
- Wildcards in RBAC rules
- Pod with hostPath volume access
- Privileged containers

**Impact**:
- **Confidentiality**: HIGH - Access to all cluster secrets
- **Integrity**: CRITICAL - Ability to modify any resource
- **Availability**: CRITICAL - Cluster-wide destruction capability

**Likelihood**: MEDIUM

**Mitigation**:
1. Implement least privilege RBAC
2. Avoid cluster-admin bindings
3. Use namespace-scoped Roles instead of ClusterRoles
4. Audit RBAC permissions regularly
5. Disable automountServiceAccountToken by default
6. Use Pod Security Standards (restricted mode)

**Verification**:
```bash
# Audit RBAC for overly permissive bindings
kubectl get clusterrolebindings -o json | \
  jq -r '.items[] | select(.roleRef.name=="cluster-admin") | .metadata.name'

# Find service accounts with cluster-admin
kubectl get rolebindings,clusterrolebindings -A -o json | \
  jq -r '.items[] | select(.roleRef.name=="cluster-admin") |
    {namespace: .metadata.namespace, name: .metadata.name, subjects: .subjects}'
```

---

### Threat 5: CI/CD Pipeline Compromise

**Description**: Attacker gains access to CI/CD system to inject malicious code or steal credentials.

**Attack Vector**:
- Stolen GitHub Actions tokens
- Malicious pull requests modifying workflows
- Compromised runner/agent
- Insecure workflow permissions
- Third-party action backdoors

**Impact**:
- **Confidentiality**: CRITICAL - Access to all deployment secrets
- **Integrity**: CRITICAL - Arbitrary code deployment
- **Availability**: HIGH - Service disruption

**Likelihood**: MEDIUM (targeted attacks on CI/CD increasing)

**Mitigation**:
1. Enforce branch protection with required reviews
2. Use ephemeral build environments
3. Implement workflow approval for external contributors
4. Pin third-party actions by SHA
5. Use minimal workflow permissions
6. Audit pipeline changes
7. Separate build and deploy credentials

**Verification**:
```yaml
# .github/workflows/secure-workflow.yml
name: Secure Build

on:
  pull_request:
    branches: [main]

permissions:
  contents: read  # Minimal permissions

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4  # Pinned version

      - name: Build
        run: npm ci && npm run build

      - name: Security Scan
        uses: aquasecurity/trivy-action@0.16.1  # Pinned by SHA
        with:
          scan-type: 'fs'
          severity: 'CRITICAL,HIGH'
```

---

### Threat 6: Infrastructure Drift and Misconfigurations

**Description**: Manual changes to infrastructure bypassing IaC, leading to security misconfigurations.

**Attack Vector**:
- Console changes not in Terraform
- Disabled security groups
- Publicly exposed databases
- Unencrypted storage
- Missing network policies

**Impact**:
- **Confidentiality**: HIGH - Data exposure through misconfiguration
- **Integrity**: MEDIUM - Unauthorized modifications
- **Availability**: MEDIUM - Service disruptions

**Likelihood**: HIGH (common in fast-moving teams)

**Mitigation**:
1. Enforce IaC for all infrastructure changes
2. Scan IaC for misconfigurations (Checkov, tfsec, Terrascan)
3. Implement policy as code (OPA, Sentinel)
4. Drift detection (terraform plan in CI)
5. Automated remediation of drift
6. Audit trail for all infrastructure changes

**Verification**:
```yaml
# .github/workflows/iac-scan.yml
name: IaC Security Scan

on:
  pull_request:
    paths:
      - 'terraform/**'
      - 'k8s/**'

jobs:
  checkov:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Checkov
        uses: bridgecrewio/checkov-action@master
        with:
          directory: terraform/
          framework: terraform
          soft_fail: false
          output_format: sarif
          download_external_modules: true

  tfsec:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run tfsec
        uses: aquasecurity/tfsec-action@v1.0.0
        with:
          soft_fail: false
```

---

### Threat 7: Container Escape / Runtime Exploitation

**Description**: Attacker breaks out of container to access host system or other containers.

**Attack Vector**:
- Privileged containers
- Host namespace sharing
- Kernel vulnerabilities
- Container runtime CVEs
- Mounted host filesystem

**Impact**:
- **Confidentiality**: CRITICAL - Access to all node data
- **Integrity**: CRITICAL - Host compromise
- **Availability**: CRITICAL - Node destruction

**Likelihood**: LOW (requires vulnerability, but high impact)

**Mitigation**:
1. Never run privileged containers
2. Drop all capabilities
3. Use read-only root filesystem
4. Enable seccomp/AppArmor/SELinux
5. No host namespace sharing
6. Keep container runtime updated
7. Runtime security monitoring (Falco)

**Verification**:
```yaml
# k8s/pod-security-standard.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

```yaml
# Falco rule for privilege escalation detection
- rule: Detect Privilege Escalation
  desc: Detect attempts to escalate privileges
  condition: >
    spawned_process and container and
    (proc.name in (su, sudo, setuid)) and
    user.uid != 0
  output: >
    Privilege escalation attempt
    (user=%user.name command=%proc.cmdline container=%container.name)
  priority: WARNING
```

---

### Threat 8: Network-Based Attacks

**Description**: Lateral movement or data exfiltration through insecure network configurations.

**Attack Vector**:
- No network segmentation
- Missing network policies
- Unencrypted pod-to-pod traffic
- Exposed internal services
- No egress filtering

**Impact**:
- **Confidentiality**: HIGH - Traffic interception
- **Integrity**: MEDIUM - Man-in-the-middle attacks
- **Availability**: MEDIUM - DDoS from compromised pods

**Likelihood**: MEDIUM

**Mitigation**:
1. Implement deny-by-default network policies
2. Enable service mesh for mTLS (Istio, Linkerd)
3. Egress filtering with allow-list
4. Network segmentation by namespace
5. Disable NodePort/LoadBalancer for internal services
6. Network policy auditing

**Verification**:
```bash
# Check for pods without network policies
kubectl get pods --all-namespaces -o json | \
  jq -r '.items[] |
    select(.metadata.namespace != "kube-system") |
    select(.metadata.labels | length > 0) |
    {namespace: .metadata.namespace, pod: .metadata.name, labels: .metadata.labels}'

# Verify network policy exists for namespace
kubectl get networkpolicies -n production
```

---

## Security Controls Matrix

| Threat | Mitigation | Status | Verification Method |
|--------|-----------|---------|---------------------|
| Compromised Dependency | Dependency scanning + SBOM | ✅ Implemented | GitHub dependency review, Snyk |
| Container Image Poisoning | Image signing + admission control | ✅ Implemented | Kyverno signature verification |
| Secrets Leakage | External secret store + scanning | ✅ Implemented | TruffleHog, External Secrets Operator |
| RBAC Privilege Escalation | Least privilege RBAC | ✅ Implemented | RBAC audit scripts |
| CI/CD Compromise | Branch protection + ephemeral builds | ✅ Implemented | GitHub Actions security settings |
| Infrastructure Drift | IaC scanning + drift detection | ✅ Implemented | Checkov, tfsec, Terraform plan |
| Container Escape | Pod Security Standards + runtime monitoring | ✅ Implemented | PSS enforcement, Falco |
| Network Attacks | Network policies + service mesh | ✅ Implemented | NetworkPolicy audit, Istio mTLS |

---

## Risk Assessment

### High Priority Threats (Address Immediately)
1. **Secrets Leakage** - Likelihood: HIGH, Impact: CRITICAL
2. **CI/CD Compromise** - Likelihood: MEDIUM, Impact: CRITICAL
3. **RBAC Privilege Escalation** - Likelihood: MEDIUM, Impact: CRITICAL

### Medium Priority Threats (Address Soon)
4. **Compromised Dependency** - Likelihood: MEDIUM, Impact: HIGH
5. **Container Image Poisoning** - Likelihood: MEDIUM, Impact: HIGH
6. **Infrastructure Drift** - Likelihood: HIGH, Impact: MEDIUM

### Lower Priority Threats (Monitor)
7. **Container Escape** - Likelihood: LOW, Impact: CRITICAL
8. **Network Attacks** - Likelihood: MEDIUM, Impact: MEDIUM

---

## Continuous Monitoring

### Detection Mechanisms

1. **Security Scanning**:
   - SAST: Semgrep, CodeQL (on every PR)
   - DAST: OWASP ZAP (nightly)
   - SCA: Snyk, Dependabot (daily)
   - Container: Trivy (on every build)
   - IaC: Checkov (on every PR)

2. **Runtime Monitoring**:
   - Falco for runtime behavior
   - Network policy violations
   - RBAC audit logs
   - Secret access logs

3. **Metrics and Alerting**:
   - Failed security gates (alert on >5%)
   - Vulnerability trends (weekly review)
   - Secret rotation age (alert on >90 days)
   - Container image age (alert on >30 days)

### Incident Response

**Detection → Investigation → Containment → Remediation → Lessons Learned**

1. Security gate failure alerts to #security-alerts
2. Automated rollback on critical vulnerabilities
3. Secret rotation on leak detection
4. Immediate revocation of compromised credentials
