## 5. Top 7 Implementation Patterns

### Pattern 1: Harbor Production Deployment with HA

**Docker Compose Setup**:
```yaml
# docker-compose.yml - Production Harbor with external database
services:
  registry:
    image: goharbor/registry-photon:v2.10.0
    restart: always
    volumes:
      - /data/registry:/storage

  core:
    image: goharbor/harbor-core:v2.10.0
    restart: always
    environment:
      CORE_SECRET: ${CORE_SECRET}
      POSTGRESQL_HOST: postgres.example.com
      REDIS_HOST: redis.example.com:6379

  trivy:
    image: goharbor/trivy-adapter-photon:v2.10.0
    restart: always
    environment:
      SCANNER_TRIVY_VULN_TYPE: "os,library"
      SCANNER_TRIVY_SEVERITY: "UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL"

# Use external PostgreSQL/Redis and S3 storage for production
# Configure via harbor.yml: database.host, redis.host, storage.s3 settings
```

---

### Pattern 2: Trivy Scanning with CVE Policies

```bash
# Configure Trivy scanner via Harbor API
curl -X POST "https://harbor.example.com/api/v2.0/scanners" \
  -u "admin:password" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Trivy",
    "url": "http://trivy:8080",
    "description": "Primary vulnerability scanner"
  }'
```

**Project-level CVE Policy**:
```json
{
  "cve_allowlist": {
    "items": [{"cve_id": "CVE-2023-12345"}],
    "expires_at": 1735689600
  },
  "severity": "high",
  "scan_on_push": true,
  "prevent_vulnerable": true
}
```

See `references/security-scanning.md` for complete Trivy integration and CVE policy patterns.

---

### Pattern 3: Robot Accounts for CI/CD

```bash
# Create robot account with scoped permissions
curl -X POST "https://harbor.example.com/api/v2.0/projects/library/robots" \
  -u "admin:password" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "github-actions",
    "duration": 90,
    "permissions": [{
      "namespace": "library",
      "access": [
        {"resource": "repository", "action": "pull"},
        {"resource": "repository", "action": "push"}
      ]
    }]
  }'
```

**Use in GitHub Actions**:
```yaml
- name: Login to Harbor
  uses: docker/login-action@v3
  with:
    registry: harbor.example.com
    username: robot$github-actions
    password: ${{ secrets.HARBOR_ROBOT_TOKEN }}
```

---

### Pattern 4: Multi-Region Replication

```bash
# Create replication endpoint
curl -X POST "https://harbor.example.com/api/v2.0/registries" \
  -u "admin:password" \
  -d '{
    "name": "harbor-eu",
    "url": "https://harbor-eu.example.com",
    "credential": {"access_key": "robot$replication", "access_secret": "token"},
    "insecure": false
  }'

# Create replication rule with filters
curl -X POST "https://harbor.example.com/api/v2.0/replication/policies" \
  -u "admin:password" \
  -d '{
    "name": "replicate-production",
    "filters": [
      {"type": "name", "value": "library/app-*"},
      {"type": "tag", "value": "v*"}
    ],
    "trigger": {"type": "scheduled", "trigger_settings": {"cron": "0 2 * * *"}}
  }'
```

See `references/replication-guide.md` for disaster recovery strategies.

---

### Pattern 5: Image Signing with Cosign

```bash
# Enable content trust
curl -X PUT "https://harbor.example.com/api/v2.0/projects/1/metadata/enable_content_trust" \
  -u "admin:password" \
  -d '{"enable_content_trust": "true"}'

# Sign with Cosign (keyless OIDC)
export COSIGN_EXPERIMENTAL=1
cosign sign --oidc-issuer https://token.actions.githubusercontent.com \
  harbor.example.com/library/app:v1.0.0

# Verify signature
cosign verify --certificate-identity-regexp "https://github.com/example/*" \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  harbor.example.com/library/app:v1.0.0
```

**Kyverno Policy** (verify in admission controller):
```yaml
spec:
  validationFailureAction: Enforce
  rules:
    - verifyImages:
      - imageReferences: ["harbor.example.com/library/*"]
        attestors:
        - entries:
          - keyless:
              subject: "https://github.com/example/*"
```
See `references/security-standards.md` for complete signature verification policies.

---

### Pattern 6: Retention Policies and Tag Immutability

```bash
# Configure retention policy
curl -X POST "https://harbor.example.com/api/v2.0/projects/library/retentions" \
  -u "admin:password" \
  -d '{
    "rules": [{
      "action": "retain",
      "template": "latestPushedK",
      "params": {"latestPushedK": 10},
      "tag_selectors": [{"pattern": "v*"}]
    }],
    "trigger": {"kind": "Schedule", "settings": {"cron": "0 0 * * 0"}}
  }'

# Enable tag immutability
curl -X POST "https://harbor.example.com/api/v2.0/projects/library/immutabletagrules" \
  -u "admin:password" \
  -d '{
    "tag_selectors": [{"pattern": "v*.*.*"}],
    "scope_selectors": {"repository": [{"pattern": "production/**"}]}
  }'
```

---

### Pattern 7: Webhook Automation

```bash
# Configure webhook for scan results
curl -X POST "https://harbor.example.com/api/v2.0/projects/library/webhook/policies" \
  -u "admin:password" \
  -d '{
    "name": "notify-security-team",
    "event_types": ["SCANNING_COMPLETED", "SCANNING_FAILED"],
    "targets": [{
      "type": "http",
      "address": "https://slack.com/api/webhooks/xxx"
    }]
  }'
```

**Webhook Payload**:
```json
{
  "type": "harbor.scanning.completed",
  "data": {
    "repository": "library/app",
    "tag": "v1.0.0",
    "scan_overview": {
      "severity": "High",
      "summary": {"Critical": 0, "High": 5, "Medium": 12}
    }
  }
}
```

---

