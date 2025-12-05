# Harbor Security Standards

## 5.1 Image Signing Requirements

**Content Trust Policy**:
- All production images MUST be signed before deployment
- Use Cosign with keyless signing (OIDC) for transparency
- Attach SBOMs to all signed images
- Verify signatures in admission controllers (Kyverno)
- Track signature coverage metrics (target: 100% for prod)

**Signing Workflow**:
1. Build image in CI/CD pipeline
2. Scan with Trivy (must pass CVE policy)
3. Generate SBOM with Syft or Trivy
4. Sign image with Cosign (ephemeral keys via OIDC)
5. Attach SBOM as artifact
6. Push to Harbor registry
7. Verify signature before Kubernetes deployment

---

## 5.2 Vulnerability Management

**CVE Policy Enforcement**:
- **CRITICAL**: Block all deployments, require immediate fix
- **HIGH**: Block production, allow dev with time-bound exemption
- **MEDIUM**: Alert only, track in security dashboard
- **LOW/UNKNOWN**: Log for awareness

**Scan Configuration**:
- Scan on push: Enabled for all projects
- Automatic rescan: Daily at 2 AM UTC
- Vulnerability database update: Every 6 hours
- Scan timeout: 10 minutes per image
- Retention: Keep scan results for 90 days

**Exemption Process**:
1. Security team reviews CVE impact
2. Create allowlist entry with expiration date
3. Document mitigation or compensating controls
4. Track exemptions in compliance reports
5. Alert 7 days before exemption expires

---

## 5.3 RBAC and Access Control

**Project Roles**:
- **Project Admin**: Full control, manage members, configure policies
- **Developer**: Push/pull images, view scan results, cannot change policies
- **Guest**: Pull images only, read-only access to metadata
- **Limited Guest**: Pull specific repositories only

**Robot Account Best Practices**:
- Use robot accounts for all automation (never user credentials)
- Scope to single project with minimal permissions
- Set expiration (90 days max, rotate at 60 days)
- Use descriptive names: `robot$service-environment-action`
- Audit robot account usage weekly
- Revoke immediately when service is decommissioned

**OIDC Integration**:
```yaml
# Harbor OIDC configuration
auth_mode: oidc_auth
oidc_name: Keycloak
oidc_endpoint: https://keycloak.example.com/auth/realms/harbor
oidc_client_id: harbor
oidc_client_secret: ${OIDC_SECRET}
oidc_scope: openid,profile,email,groups
oidc_verify_cert: true
oidc_auto_onboard: true
oidc_user_claim: preferred_username
oidc_group_claim: groups
```

---

## 5.4 Supply Chain Security

**Artifact Integrity**:
- Enable content trust for all production projects
- Require signatures from trusted issuers only
- Verify SBOM presence and completeness
- Track artifact provenance from source to deployment
- Implement cosign verification in admission controllers

**Base Image Security**:
- Use official minimal base images (distroless, alpine, chainguard)
- Scan base images before use
- Pin base images with digest (not tags)
- Monitor base image CVE notifications
- Update base images within 7 days of security patches

**Compliance Tracking**:
- Generate weekly compliance reports
- Track metrics: signature coverage, scan pass rate, CVE MTTR
- Audit artifact access patterns
- Alert on unsigned production deployments
- Monthly security review with stakeholders
