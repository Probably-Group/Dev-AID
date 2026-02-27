---
name: harbor-expert
version: 2.0.0
description: "Harbor container registry management with vulnerability scanning, Trivy integration, Notary artifact signing, and RBAC configuration. Use when deploying Harbor, configuring image scanning policies, setting up replication rules, or managing registry access control. Do NOT use for Docker Hub, ECR, GCR, or other non-Harbor registries."
compatibility: "Harbor 2.9+, Docker/containerd"
risk_level: HIGH
token_budget: 5500
---
# Harbor Container Registry Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.2 Security Patterns (security rules)

**CWE-639: BOLA Vulnerability (CVE-2024-22278)**
- Do not: Grant Maintainer role to untrusted users (can manipulate cross-project)
- Instead: Upgrade to v2.9.5+/v2.10.3+/v2.11.0+, apply least privilege

**CWE-269: Privilege Escalation (CVE-2019-16097)**
- Do not: Expose Harbor with default settings to internet
- Instead: Change default admin creds, disable self-registration, network controls

**CWE-862: Missing Authorization (CVE-2022-46463)**
- Do not: Assume private repos are inaccessible to unauthenticated users
- Instead: Penetration test access controls, implement network segmentation

**CWE-345: Missing Signature Verification**
- Do not: Pull images without content trust/signature verification
- Instead: Enable Notary/Cosign, configure "Prevent Vulnerable Images" policy

---

## 1. Security Principles

### 1.1 Image Signing with Cosign (CWE-494)

**Principle:** Sign all images. Verify signatures before deployment.

```yaml
# ❌ WRONG - No signature verification
apiVersion: v1
kind: Pod
spec:
  containers:
    - image: harbor.example.com/myapp:latest

# ✅ CORRECT - Policy requires signed images (with Kyverno)
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-harbor-signatures
spec:
  validationFailureAction: Enforce
  rules:
    - name: verify-signature
      match:
        any:
          - resources:
              kinds:
                - Pod
      verifyImages:
        - imageReferences:
            - "harbor.example.com/*"
          attestors:
            - entries:
                - keys:
                    publicKeys: |-
                      -----BEGIN PUBLIC KEY-----
                      MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE...
                      -----END PUBLIC KEY-----
```

### 1.2 Vulnerability Scanning (CWE-1395)

**Principle:** Scan all images. Block deployment of critical vulnerabilities.

### 1.3 RBAC and Project Isolation (CWE-284)

**Principle:** Use projects for tenant isolation. Apply least privilege.

### 1.4 Robot Accounts (CWE-798)

**Principle:** Use robot accounts for CI/CD. Never hardcode credentials.

### 1.5 Replication Security (CWE-319)

**Principle:** Use TLS for replication. Verify remote registry certificates.

### 1.6 Webhook Security (CWE-352)

**Principle:** Authenticate webhooks. Validate payload signatures.

---

## 2. Version Requirements

Use these minimum versions:

```yaml
harbor: v2.10.0+
trivy: v0.50.0+
cosign: v2.2.0+
notation: v1.1.0+
```

---

## 3. Code Patterns

### 3.1 WHEN configuring Harbor with Helm

```yaml
# ❌ WRONG - Insecure defaults
# No TLS, default admin password, no scanning

# ✅ CORRECT - Production Harbor configuration
# values.yaml
expose:
  type: ingress
  tls:
    enabled: true
    certSource: secret
    secret:
      secretName: harbor-tls
      notarySecretName: notary-tls
  ingress:
    hosts:
      core: harbor.example.com
      notary: notary.example.com
    className: nginx
    annotations:
      nginx.ingress.kubernetes.io/ssl-redirect: "true"
      nginx.ingress.kubernetes.io/proxy-body-size: "0"
      cert-manager.io/cluster-issuer: letsencrypt-prod

externalURL: https://harbor.example.com

persistence:
  enabled: true
  persistentVolumeClaim:
    registry:
      storageClass: fast-ssd
      size: 500Gi
    database:
      storageClass: fast-ssd
      size: 50Gi
    redis:
      storageClass: fast-ssd
      size: 10Gi
    trivy:
      storageClass: fast-ssd
      size: 50Gi

# Security settings
harborAdminPassword: "${HARBOR_ADMIN_PASSWORD}"  # From secret

database:
  type: external
  external:
    host: postgres.example.com
    port: 5432
    username: harbor
    password: "${DATABASE_PASSWORD}"
    sslmode: require
    coreDatabase: harbor_core
    notaryServerDatabase: harbor_notary_server
    notarySignerDatabase: harbor_notary_signer

redis:
  type: external
  external:
    addr: redis.example.com:6379
    password: "${REDIS_PASSWORD}"
    sentinelMasterSet: harbor-master

# Trivy scanner
trivy:
  enabled: true
  gitHubToken: "${GITHUB_TOKEN}"  # For advisory DB updates
  skipUpdate: false
  offlineScan: false
  timeout: 10m0s
  resources:
    requests:
      cpu: 200m
      memory: 512Mi
    limits:
      cpu: 1000m
      memory: 2Gi

# Notary (image signing)
notary:
  enabled: true

# Core settings
core:
  secretName: harbor-core-secret
  xsrfKey: "${XSRF_KEY}"
  configOverwriteJson: |
    {
      "auth_mode": "oidc_auth",
      "oidc_name": "Keycloak",
      "oidc_endpoint": "https://keycloak.example.com/realms/harbor",
      "oidc_client_id": "harbor",
      "oidc_client_secret": "${OIDC_CLIENT_SECRET}",
      "oidc_scope": "openid,profile,email,groups",
      "oidc_groups_claim": "groups",
      "oidc_admin_group": "harbor-admins",
      "oidc_auto_onboard": true,
      "oidc_user_claim": "preferred_username"
    }

# Security contexts
containerSecurityContext:
  runAsUser: 10000
  runAsNonRoot: true
  allowPrivilegeEscalation: false
  seccompProfile:
    type: RuntimeDefault
  capabilities:
    drop:
      - ALL

podSecurityContext:
  runAsUser: 10000
  runAsGroup: 10000
  fsGroup: 10000

# Network policies
networkPolicies:
  enabled: true
```

### 3.2 WHEN creating projects and RBAC

```yaml
# ❌ WRONG - Single project, everyone has access
# All images in library, all users admin

# ✅ CORRECT - Project structure with RBAC via API
# Python script to configure Harbor projects
import requests
from typing import Optional
from dataclasses import dataclass
from enum import Enum

class Role(Enum):
    PROJECT_ADMIN = 1
    DEVELOPER = 2
    GUEST = 3
    MAINTAINER = 4
    LIMITED_GUEST = 5

@dataclass
class HarborConfig:
    url: str
    username: str
    password: str
    verify_ssl: bool = True

class HarborClient:
    def __init__(self, config: HarborConfig):
        self.config = config
        self.session = requests.Session()
        self.session.auth = (config.username, config.password)
        self.session.verify = config.verify_ssl
        self.base_url = f"{config.url}/api/v2.0"

    def create_project(
        self,
        name: str,
        public: bool = False,
        storage_limit: int = -1,
        enable_content_trust: bool = True,
        auto_scan: bool = True,
        severity: str = "high",
        prevent_vulnerable: bool = True,
    ) -> dict:
        """Create project with security policies."""

        payload = {
            "project_name": name,
            "public": public,
            "storage_limit": storage_limit,
            "metadata": {
                "enable_content_trust": str(enable_content_trust).lower(),
                "auto_scan": str(auto_scan).lower(),
                "severity": severity,
                "prevent_vul": str(prevent_vulnerable).lower(),
                "reuse_sys_cve_allowlist": "true",
            },
        }

        response = self.session.post(
            f"{self.base_url}/projects",
            json=payload,
        )
        response.raise_for_status()

        # Get created project
        return self.get_project(name)

    def get_project(self, name: str) -> dict:
        response = self.session.get(f"{self.base_url}/projects?name={name}")
        response.raise_for_status()
        projects = response.json()
        return projects[0] if projects else None

    def add_project_member(
        self,
        project_name: str,
        username: str,
        role: Role,
    ) -> None:
        """Add user to project with specific role."""

        project = self.get_project(project_name)
        if not project:
            raise ValueError(f"Project not found: {project_name}")

        payload = {
            "role_id": role.value,
            "member_user": {"username": username},
        }

        response = self.session.post(
            f"{self.base_url}/projects/{project['project_id']}/members",
            json=payload,
        )
        response.raise_for_status()

    def add_project_group(
        self,
        project_name: str,
        group_name: str,
        role: Role,
        group_type: int = 1,  # 1=LDAP/OIDC group
    ) -> None:
        """Add OIDC/LDAP group to project."""

        project = self.get_project(project_name)

        payload = {
            "role_id": role.value,
            "member_group": {
                "group_name": group_name,
                "group_type": group_type,
            },
        }

        response = self.session.post(
            f"{self.base_url}/projects/{project['project_id']}/members",
            json=payload,
        )
        response.raise_for_status()

    def create_robot_account(
        self,
        name: str,
        project_name: str,
        permissions: list[str],
        expires_at: int = -1,  # -1 = never
    ) -> dict:
        """Create robot account for CI/CD."""

        project = self.get_project(project_name)

        payload = {
            "name": name,
            "duration": expires_at,
            "level": "project",
            "permissions": [
                {
                    "kind": "project",
                    "namespace": project_name,
                    "access": [
                        {"resource": perm.split(":")[0], "action": perm.split(":")[1]}
                        for perm in permissions
                    ],
                }
            ],
        }

        response = self.session.post(
            f"{self.base_url}/robots",
            json=payload,
        )
        response.raise_for_status()
        return response.json()

# Example: Setup projects
def setup_harbor_projects():
    config = HarborConfig(
        url="https://harbor.example.com",
        username=os.environ["HARBOR_ADMIN_USER"],
        password=os.environ["HARBOR_ADMIN_PASSWORD"],
    )

    client = HarborClient(config)

    # Create production project (strict security)
    client.create_project(
        name="production",
        public=False,
        enable_content_trust=True,
        auto_scan=True,
        prevent_vulnerable=True,
        severity="high",
    )

    # Add OIDC groups
    client.add_project_group("production", "platform-team", Role.PROJECT_ADMIN)
    client.add_project_group("production", "developers", Role.DEVELOPER)

    # Create robot for CI/CD
    robot = client.create_robot_account(
        name="ci-push",
        project_name="production",
        permissions=[
            "repository:push",
            "repository:pull",
            "artifact:read",
            "tag:create",
            "tag:list",
        ],
    )
    print(f"Robot token: {robot['secret']}")  # Store securely!
```

### 3.3 WHEN implementing CI/CD image push with signing

```yaml
# ❌ WRONG - No scanning, no signing
- docker push harbor.example.com/myapp:latest

# ✅ CORRECT - GitHub Actions with scanning and signing
name: Build and Push to Harbor

on:
  push:
    branches: [main]
    tags: ['v*']

env:
  REGISTRY: harbor.example.com
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write  # For OIDC

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Harbor
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ secrets.HARBOR_ROBOT_NAME }}
          password: ${{ secrets.HARBOR_ROBOT_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=sha,prefix=
            type=ref,event=tag
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build image
        id: build
        uses: docker/build-push-action@v6
        with:
          context: .
          push: false
          load: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      # Scan before push
      - name: Scan with Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'

      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: 'trivy-results.sarif'

      # Push after scan passes
      - name: Push image
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          sbom: true
          provenance: true

      # Sign with Cosign
      - name: Install Cosign
        uses: sigstore/cosign-installer@v3

      - name: Sign image with Cosign
        env:
          COSIGN_KEY: ${{ secrets.COSIGN_PRIVATE_KEY }}
          COSIGN_PASSWORD: ${{ secrets.COSIGN_PASSWORD }}
        run: |
          cosign sign --key env://COSIGN_KEY \
            --yes \
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}@${{ steps.build.outputs.digest }}

      - name: Verify signature
        run: |
          cosign verify --key ${{ secrets.COSIGN_PUBLIC_KEY }} \
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}@${{ steps.build.outputs.digest }}
```

### 3.4 WHEN configuring replication

```yaml
# ❌ WRONG - Unencrypted replication, no filters
# Replicate everything without verification

# ✅ CORRECT - Secure replication policy via API
import requests
from dataclasses import dataclass
from typing import Optional

@dataclass
class ReplicationPolicy:
    name: str
    src_registry_id: int
    dest_registry_id: int
    src_namespaces: list[str]
    dest_namespace: Optional[str] = None
    trigger_type: str = "manual"  # manual, scheduled, event_based
    cron: Optional[str] = None  # For scheduled
    filters: Optional[list[dict]] = None
    override: bool = True
    enabled: bool = True
    speed: int = -1  # -1 = unlimited

class HarborReplication:
    def __init__(self, client: HarborClient):
        self.client = client

    def create_registry_endpoint(
        self,
        name: str,
        url: str,
        credential_type: str = "basic",
        access_key: str = "",
        access_secret: str = "",
        insecure: bool = False,
    ) -> int:
        """Register remote registry for replication."""

        payload = {
            "name": name,
            "url": url,
            "credential": {
                "type": credential_type,
                "access_key": access_key,
                "access_secret": access_secret,
            },
            "insecure": insecure,
        }

        response = self.client.session.post(
            f"{self.client.base_url}/registries",
            json=payload,
        )
        response.raise_for_status()

        # Get registry ID
        registries = self.client.session.get(
            f"{self.client.base_url}/registries?name={name}"
        ).json()
        return registries[0]["id"]

    def create_replication_policy(self, policy: ReplicationPolicy) -> int:
        """Create replication policy with filters."""

        filters = policy.filters or []

        # Add default filters for security
        filters.extend([
            # Only replicate signed images
            {"type": "label", "value": "signed=true"},
            # Exclude images with critical vulnerabilities
            {"type": "label", "value": "vulnerability!=critical"},
        ])

        trigger = {"type": policy.trigger_type}
        if policy.trigger_type == "scheduled":
            trigger["trigger_settings"] = {"cron": policy.cron}

        payload = {
            "name": policy.name,
            "src_registry": {"id": policy.src_registry_id},
            "dest_registry": {"id": policy.dest_registry_id},
            "dest_namespace": policy.dest_namespace,
            "trigger": trigger,
            "filters": filters,
            "replicate_deletion": False,  # Don't sync deletes
            "override": policy.override,
            "enabled": policy.enabled,
            "speed": policy.speed,
        }

        response = self.client.session.post(
            f"{self.client.base_url}/replication/policies",
            json=payload,
        )
        response.raise_for_status()

        # Get policy ID
        policies = self.client.session.get(
            f"{self.client.base_url}/replication/policies?name={policy.name}"
        ).json()
        return policies[0]["id"]

# Example: Setup cross-region replication
def setup_replication():
    client = HarborClient(config)
    replication = HarborReplication(client)

    # Register DR site
    dr_registry_id = replication.create_registry_endpoint(
        name="dr-harbor",
        url="https://harbor-dr.example.com",
        access_key=os.environ["DR_ROBOT_NAME"],
        access_secret=os.environ["DR_ROBOT_TOKEN"],
        insecure=False,
    )

    # Create replication policy
    replication.create_replication_policy(ReplicationPolicy(
        name="production-to-dr",
        src_registry_id=0,  # 0 = local Harbor
        dest_registry_id=dr_registry_id,
        src_namespaces=["production"],
        dest_namespace="production-replica",
        trigger_type="event_based",  # Replicate on push
        filters=[
            {"type": "name", "value": "production/**"},
            {"type": "tag", "value": "v*"},  # Only version tags
        ],
    ))
```

### 3.5 WHEN setting up vulnerability scanning policies

```python
# ✅ CORRECT - Configure scanning and blocking
class HarborScanning:
    def __init__(self, client: HarborClient):
        self.client = client

    def configure_project_scanning(
        self,
        project_name: str,
        auto_scan: bool = True,
        prevent_vulnerable: bool = True,
        severity_threshold: str = "high",  # low, medium, high, critical
    ) -> None:
        """Configure vulnerability scanning for project."""

        project = self.client.get_project(project_name)

        payload = {
            "metadata": {
                "auto_scan": str(auto_scan).lower(),
                "prevent_vul": str(prevent_vulnerable).lower(),
                "severity": severity_threshold,
            },
        }

        self.client.session.put(
            f"{self.client.base_url}/projects/{project['project_id']}",
            json=payload,
        )

    def configure_system_cve_allowlist(
        self,
        cve_ids: list[str],
        expires_at: Optional[int] = None,
    ) -> None:
        """Configure system-wide CVE allowlist."""

        payload = {
            "items": [{"cve_id": cve_id} for cve_id in cve_ids],
        }

        if expires_at:
            payload["expires_at"] = expires_at

        self.client.session.put(
            f"{self.client.base_url}/system/CVEAllowlist",
            json=payload,
        )

    def scan_artifact(
        self,
        project_name: str,
        repository: str,
        reference: str,  # tag or digest
    ) -> dict:
        """Trigger scan and wait for results."""

        # Trigger scan
        self.client.session.post(
            f"{self.client.base_url}/projects/{project_name}/repositories/{repository}/artifacts/{reference}/scan"
        )

        # Poll for results
        import time
        for _ in range(60):  # 5 minute timeout
            response = self.client.session.get(
                f"{self.client.base_url}/projects/{project_name}/repositories/{repository}/artifacts/{reference}"
            )
            artifact = response.json()

            scan_overview = artifact.get("scan_overview", {})
            if scan_overview:
                report = list(scan_overview.values())[0]
                if report.get("scan_status") == "Success":
                    return report

            time.sleep(5)

        raise TimeoutError("Scan did not complete in time")

    def get_vulnerability_report(
        self,
        project_name: str,
        repository: str,
        reference: str,
    ) -> list[dict]:
        """Get detailed vulnerability report."""

        response = self.client.session.get(
            f"{self.client.base_url}/projects/{project_name}/repositories/{repository}/artifacts/{reference}/additions/vulnerabilities"
        )
        response.raise_for_status()
        return response.json()
```

---

## 4. Anti-Patterns

Do not:
- Use `latest` tag in production
- Deploy unsigned images
- Skip vulnerability scanning
- Use admin credentials in CI/CD
- Replicate without filters
- Allow public projects for sensitive images
- Ignore critical vulnerabilities
- Store robot tokens in code
- Use insecure registry connections

---

## 5. Testing

**ALWAYS test Harbor configurations:**

```bash
#!/bin/bash
set -euo pipefail

HARBOR_URL="${HARBOR_URL:-https://harbor.example.com}"
PROJECT="${PROJECT:-test-project}"

echo "=== Harbor Security Tests ==="
# ... (additional test cases follow same pattern)
```

---

## 6. Pre-Generation Checklist

Before generating any Harbor code:

- [ ] TLS enabled for all connections
- [ ] OIDC/LDAP configured (not local auth)
- [ ] Projects created with auto-scan enabled
- [ ] Robot accounts used for CI/CD
- [ ] Image signing (Cosign/Notary) configured
- [ ] Vulnerability blocking enabled
- [ ] Replication uses filters
- [ ] Network policies restrict access
- [ ] Admin credentials from secrets
- [ ] Webhook authentication configured

---
