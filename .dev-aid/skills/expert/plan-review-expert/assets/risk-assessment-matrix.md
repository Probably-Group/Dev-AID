# Risk Assessment Matrix

## Project Info

| Field | Value |
|-------|-------|
| **Project** | [Project Name] |
| **Assessor** | [Name] |
| **Date** | [YYYY-MM-DD] |

---

## 5x5 Risk Matrix

Combine **Probability** (rows) and **Impact** (columns) to determine risk level.

|  | Negligible | Minor | Moderate | Major | Catastrophic |
|--|-----------|-------|----------|-------|-------------|
| **Almost Certain** | Medium | High | High | Critical | Critical |
| **Likely** | Low | Medium | High | High | Critical |
| **Possible** | Low | Medium | Medium | High | High |
| **Unlikely** | Low | Low | Medium | Medium | High |
| **Rare** | Low | Low | Low | Medium | Medium |

### Legend

- **Critical** -- Immediate action required; blocks approval
- **High** -- Must be mitigated before implementation proceeds
- **Medium** -- Should be mitigated; monitor actively
- **Low** -- Accept and monitor; address opportunistically

---

## Risk Register

### Technical Risks

| ID | Risk Description | Probability | Impact | Level | Mitigation | Owner |
|----|-----------------|-------------|--------|-------|------------|-------|
| T-01 | [e.g., Chosen database cannot handle projected load] | [Possible] | [Major] | [High] | [Mitigation strategy] | [Name] |
| T-02 | [e.g., Third-party API has no SLA guarantees] | [Likely] | [Moderate] | [High] | [Mitigation strategy] | [Name] |
| T-03 | [e.g., Untested migration path from legacy system] | [Unlikely] | [Major] | [Medium] | [Mitigation strategy] | [Name] |

### Schedule Risks

| ID | Risk Description | Probability | Impact | Level | Mitigation | Owner |
|----|-----------------|-------------|--------|-------|------------|-------|
| S-01 | [e.g., Key team member unavailable during sprint] | [Possible] | [Moderate] | [Medium] | [Mitigation strategy] | [Name] |
| S-02 | [e.g., Dependency on external team delivery] | [Likely] | [Major] | [High] | [Mitigation strategy] | [Name] |

### Resource Risks

| ID | Risk Description | Probability | Impact | Level | Mitigation | Owner |
|----|-----------------|-------------|--------|-------|------------|-------|
| R-01 | [e.g., Insufficient infrastructure budget] | [Unlikely] | [Moderate] | [Medium] | [Mitigation strategy] | [Name] |
| R-02 | [e.g., Skill gap in required technology] | [Possible] | [Minor] | [Medium] | [Mitigation strategy] | [Name] |

### Security Risks

| ID | Risk Description | Probability | Impact | Level | Mitigation | Owner |
|----|-----------------|-------------|--------|-------|------------|-------|
| X-01 | [e.g., Authentication bypass in new auth flow] | [Unlikely] | [Catastrophic] | [High] | [Mitigation strategy] | [Name] |
| X-02 | [e.g., Data exposure during migration] | [Possible] | [Major] | [High] | [Mitigation strategy] | [Name] |

---

## Summary

| Level | Count | Action Required |
|-------|-------|-----------------|
| Critical | [N] | Immediate resolution before proceeding |
| High | [N] | Mitigation plan required before approval |
| Medium | [N] | Monitor and mitigate during implementation |
| Low | [N] | Accept and track |

---

## Review Notes

- [Additional context, dependencies between risks, or escalation criteria]
