# Chaos Engineering & Resilience

**Purpose**: Chaos experiments and resilience tracking (team-shared)
**Note**: For personal AI notes, use Claude's built-in memory (`~/.claude/projects/*/memory/`)

---

## Chaos Engineering Principles

1. **Build a hypothesis around steady-state behavior**
2. **Vary real-world events** (failures, latency, etc.)
3. **Run experiments in production** (with safeguards)
4. **Automate experiments** to run continuously
5. **Minimize blast radius**

---

## Chaos Experiments

### EXP-001: [Experiment Title]
**Date**: YYYY-MM-DD
**Hypothesis**: System gracefully degrades when [X] fails
**Method**: How to induce the failure

**Results**:
- What worked
- What didn't work
- Surprises

**Improvements Made**:
- Change 1
- Change 2

**Resilience Score**: Before → After

---

## Resilience Patterns Implemented

### Circuit Breaker
**Location**: `src/utils/circuit-breaker.ts`
**Thresholds**:
- Failure rate: >50%
- Min requests: 10
- Timeout: 30s

**Applied To**:
- External API calls
- Database queries
- Cache operations

### Retry Logic
**Strategy**: Exponential backoff
**Configuration**:
```typescript
{
  attempts: 3,
  initialDelay: 100ms,
  maxDelay: 2000ms,
  factor: 2
}
```

### Timeouts
| Operation | Timeout |
|-----------|---------|
| API calls | 5s |
| DB queries | 10s |
| External APIs | 30s |

---

## Production Incidents

### INC-001: [Incident Title]
**Date**: YYYY-MM-DD
**Duration**: X minutes
**Impact**: Description

**Root Cause**: What caused it
**Fix**: How it was fixed
**Prevention**: How to prevent recurrence

**Lessons Learned**:
- Lesson 1
- Lesson 2

---

## Resilience Targets

**SLA**: 99.9% uptime
**RTO**: <15 minutes (Recovery Time Objective)
**RPO**: <5 minutes (Recovery Point Objective)
**MTTR**: <30 minutes (Mean Time To Recovery)

---

**Usage**: Reference when planning chaos experiments.
Update after experiments or production incidents.
