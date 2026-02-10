# Deployment Checklist

## Release Info

| Field | Value |
|-------|-------|
| **Version** | [v1.2.3] |
| **Release Date** | [YYYY-MM-DD] |
| **Release Manager** | [Name] |
| **Environment** | [Production / Staging] |
| **Deploy Method** | [Rolling / Blue-Green / Canary] |

---

## Pre-Deployment

### Code Quality
- [ ] All CI pipeline checks passing (lint, test, build)
- [ ] Code review approved by [N] reviewer(s)
- [ ] No open Critical/High issues in the release milestone

### Testing
- [ ] Unit tests passing with >= [N]% coverage
- [ ] Integration tests passing
- [ ] E2E/smoke tests passing on staging
- [ ] Performance/load tests run (if applicable)

### Security
- [ ] Security scan clean (no Critical/High findings)
- [ ] Dependency audit clean (no known vulnerabilities)
- [ ] Secret scan clean (Gitleaks/TruffleHog)
- [ ] SAST scan reviewed (Semgrep/Bandit)

### Versioning
- [ ] Version bumped in [package.json / pyproject.toml / VERSION]
- [ ] Changelog updated with user-facing changes
- [ ] Git tag created: [vX.Y.Z]

### Documentation
- [ ] API documentation updated (if endpoints changed)
- [ ] Runbook updated (if operational procedures changed)
- [ ] Migration guide provided (if breaking changes)

---

## Deployment

### Infrastructure
- [ ] Database migrations tested and ready
- [ ] Environment variables / secrets configured
- [ ] Feature flags set to expected state
- [ ] Sufficient capacity for rollout

### Rollback Plan
- [ ] Rollback procedure documented
- [ ] Previous version artifact available
- [ ] Database rollback script tested (if applicable)
- [ ] Rollback trigger criteria defined: [e.g., error rate > 5%]

### Execution
- [ ] Deploy to staging and verify
- [ ] Deploy to production (canary/rolling)
- [ ] Verify health checks passing
- [ ] Verify smoke tests passing

---

## Post-Deployment

### Monitoring
- [ ] Application health dashboard shows green
- [ ] Error rate within normal bounds
- [ ] Latency / response time within SLA
- [ ] No unexpected alerts triggered

### Communication
- [ ] Team notified of successful deployment
- [ ] Stakeholders informed (if user-facing changes)
- [ ] Incident channel monitored for [N] minutes post-deploy

### Cleanup
- [ ] Feature flags cleaned up (if temporary)
- [ ] Old deployment artifacts retained per policy
- [ ] Post-mortem scheduled (if issues encountered)

---

## Sign-off

| Role | Name | Approved | Date |
|------|------|----------|------|
| Release Manager | [Name] | [ ] | [Date] |
| QA Lead | [Name] | [ ] | [Date] |
| On-Call Engineer | [Name] | [ ] | [Date] |
