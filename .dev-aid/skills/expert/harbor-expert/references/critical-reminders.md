## 14. Critical Reminders

### Pre-Implementation Checklist

#### Phase 1: Before Writing Code

- [ ] Read existing Harbor configuration and version
- [ ] Identify affected projects and replication policies
- [ ] Review current security policies (CVE blocking, content trust)
- [ ] Check existing robot accounts and their permissions
- [ ] Document current garbage collection schedule
- [ ] Write failing tests for new functionality
- [ ] Review Harbor API documentation for changes

#### Phase 2: During Implementation

- [ ] Follow TDD workflow (test first, implement, refactor)
- [ ] Apply security defaults to all new projects
- [ ] Use least privilege for robot accounts
- [ ] Configure filters for replication policies
- [ ] Enable scan-on-push for all artifacts
- [ ] Set appropriate retention policies
- [ ] Test all API calls return expected results

#### Phase 3: Before Committing

- [ ] Run full test suite (unit, integration, E2E)
- [ ] Verify all security policies are enforced
- [ ] Check garbage collection is scheduled
- [ ] Validate replication endpoints are healthy
- [ ] Confirm scanner is operational
- [ ] Review audit logs for anomalies
- [ ] Update documentation if needed

---

### Pre-Production Deployment Checklist

**Registry Configuration**:
- [ ] PostgreSQL and Redis externalized (not embedded)
- [ ] Storage backend configured (S3/GCS/Azure, not filesystem)
- [ ] TLS certificates valid and auto-renewing
- [ ] Backup strategy configured and tested
- [ ] Resource limits set (CPU, memory, storage quota)

**Security Hardening**:
- [ ] Trivy scanner integrated and set as default
- [ ] Scan-on-push enabled for all projects
- [ ] CVE blocking policy configured (HIGH/CRITICAL)
- [ ] Content trust enabled for production projects
- [ ] Tag immutability enabled for release tags
- [ ] Robot accounts follow least privilege
- [ ] OIDC/LDAP authentication configured
- [ ] Audit logging enabled

**Replication and DR**:
- [ ] Multi-region replication configured
- [ ] Replication monitoring and alerting active
- [ ] Disaster recovery runbook documented
- [ ] Failover tested within last 90 days
- [ ] RTO/RPO requirements met

**Compliance**:
- [ ] Retention policies configured
- [ ] Webhook notifications for security events
- [ ] Compliance reports generated weekly
- [ ] Signature coverage >95% for production
- [ ] CVE MTTR <7 days for critical

**Operational Readiness**:
- [ ] Garbage collection scheduled weekly
- [ ] Database vacuum scheduled monthly
- [ ] Monitoring dashboards configured
- [ ] Runbooks for common incidents
- [ ] On-call team trained on Harbor administration

---

### Critical Security Controls

**NEVER**:
- Deploy unsigned images to production
- Allow scan-failing images with CRITICAL CVEs
- Use user credentials in CI/CD (use robot accounts)
- Share robot account tokens across services
- Disable content trust for production projects
- Skip replication testing before DR events
- Allow public access to private registries

**ALWAYS**:
- Scan all images before deployment
- Sign production images with provenance
- Rotate robot account tokens every 90 days
- Monitor replication lag and failures
- Test backup/restore procedures quarterly
- Update Trivy vulnerability database daily
- Audit unusual access patterns weekly
- Document CVE exemptions with expiration

---

