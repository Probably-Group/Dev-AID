# CI/CD Security & Supply Chain

## Top 3 Security Concerns

### 1. Secrets Exposure in Pipelines

**Risk**: Secrets leaked in logs, environment variables, or committed to repositories.

**Mitigation**:
```yaml
# ✅ GOOD: Use OIDC for cloud authentication
- name: Configure AWS Credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789012:role/GitHubActions
    aws-region: us-east-1

# ✅ GOOD: Mask secrets in logs
- name: Use secret safely
  run: |
    echo "::add-mask::${{ secrets.API_KEY }}"
    echo "API_KEY is set"  # Never echo the actual value

# ❌ BAD: Exposing secrets
- run: echo "API_KEY=${{ secrets.API_KEY }}"  # Will appear in logs!
```

### 2. Supply Chain Attacks via Compromised Actions

**Risk**: Third-party GitHub Actions could be malicious or compromised.

**Mitigation**:
```yaml
# ✅ GOOD: Pin actions to SHA
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1

# ✅ GOOD: Restrict to specific organization
permissions:
  actions: read
  contents: read

# ❌ BAD: Using latest tag
- uses: some-org/action@main  # Can change anytime!
```

### 3. Insufficient Pipeline Isolation

**Risk**: Jobs accessing resources from other projects or environments.

**Mitigation**:
```yaml
# ✅ GOOD: Minimal permissions
permissions:
  contents: read
  packages: write

# ✅ GOOD: Environment-specific secrets
jobs:
  deploy-prod:
    environment: production  # Separate secret scope
    steps:
      - name: Deploy
        run: deploy.sh
        env:
          API_KEY: ${{ secrets.PROD_API_KEY }}  # Only available in prod environment
```

---

## OWASP CI/CD Top 10 Risk Mapping

| Risk ID | Category | Impact | Mitigation |
|---------|----------|--------|------------|
| CICD-SEC-1 | Insufficient Flow Control | Critical | Branch protection, required reviews, status checks |
| CICD-SEC-2 | Inadequate Identity & Access | Critical | OIDC, least privilege, short-lived tokens |
| CICD-SEC-3 | Dependency Chain Abuse | High | SCA scanning, dependency pinning, SBOM |
| CICD-SEC-4 | Poisoned Pipeline Execution | Critical | Separate build/deploy, validate inputs |
| CICD-SEC-5 | Insufficient PBAC | High | Environment protection, manual approvals |
| CICD-SEC-6 | Insufficient Credential Hygiene | Critical | Secrets scanning, rotation, vault integration |
| CICD-SEC-7 | Insecure System Configuration | High | Harden runners, network isolation |
| CICD-SEC-8 | Ungoverned Usage | Medium | Policy as code, compliance gates |
| CICD-SEC-9 | Improper Artifact Integrity | High | Sign artifacts, verify provenance |
| CICD-SEC-10 | Insufficient Logging | Medium | Structured logs, audit trails, SIEM integration |

---

## Security Implementation Examples

### SAST/DAST Integration

```yaml
jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # SAST with Semgrep
      - name: Semgrep Scan
        uses: semgrep/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/secrets
            p/owasp-top-ten

      # SAST with CodeQL
      - name: Initialize CodeQL
        uses: github/codeql-action/init@v2
        with:
          languages: javascript, python

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v2
```

### Secrets Management

```yaml
jobs:
  secrets-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for secret detection

      # Scan for committed secrets
      - name: Gitleaks Scan
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      # Scan for secrets in current code
      - name: TruffleHog Scan
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
```

### Artifact Signing with Cosign

```yaml
jobs:
  sign-artifacts:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      packages: write
    steps:
      - name: Install Cosign
        uses: sigstore/cosign-installer@v3

      - name: Sign container image
        run: |
          cosign sign --yes ghcr.io/${{ github.repository }}@${DIGEST}

      - name: Generate SBOM
        uses: anchore/sbom-action@v0
        with:
          image: ghcr.io/${{ github.repository }}:${{ github.sha }}
          format: spdx-json
          output-file: sbom.spdx.json

      - name: Attest SBOM
        run: |
          cosign attest --yes \
            --predicate sbom.spdx.json \
            --type spdxjson \
            ghcr.io/${{ github.repository }}@${DIGEST}
```

### Container Image Scanning

```yaml
jobs:
  container-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Scan with Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ghcr.io/${{ github.repository }}:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
          exit-code: 1  # Fail on vulnerabilities

      - name: Scan with Grype
        uses: anchore/scan-action@v3
        with:
          image: ghcr.io/${{ github.repository }}:${{ github.sha }}
          fail-build: true
          severity-cutoff: high

      - name: Upload results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: 'trivy-results.sarif'
```

### Dependency Scanning

```yaml
jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # GitHub native dependency review
      - name: Dependency Review
        uses: actions/dependency-review-action@v4
        with:
          fail-on-severity: high
          allow-licenses: MIT, Apache-2.0, BSD-3-Clause

      # Snyk scanning
      - name: Snyk Security Scan
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high

      # Generate SBOM
      - name: Generate SBOM
        run: |
          npm install -g @cyclonedx/cyclonedx-npm
          cyclonedx-npm --output-file sbom.json
```

---

## Security Checklist

### Before Deployment

- [ ] All third-party actions pinned to commit SHA
- [ ] Workflow permissions set to minimum required
- [ ] OIDC/Workload Identity configured (no static secrets)
- [ ] Branch protection rules enabled
- [ ] Required status checks configured
- [ ] CODEOWNERS file in place
- [ ] Secrets scanning enabled in pre-commit hooks
- [ ] SAST/SCA integrated into CI pipeline
- [ ] Container images scanned for vulnerabilities
- [ ] Artifacts signed with Cosign/Sigstore
- [ ] SBOM generated for all dependencies
- [ ] Environment protection rules configured
- [ ] Manual approval required for production
- [ ] Audit logging enabled
- [ ] Security alerts configured

### Runtime Security

- [ ] Secrets masked in logs
- [ ] No hardcoded credentials in code
- [ ] Environment-specific secrets isolated
- [ ] Service accounts use least privilege
- [ ] Network policies restrict runner access
- [ ] Self-hosted runners hardened
- [ ] Pipeline execution logs retained
- [ ] Incident response plan documented
