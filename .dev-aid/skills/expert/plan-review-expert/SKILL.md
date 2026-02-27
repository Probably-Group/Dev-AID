---
name: plan-review-expert
version: 2.0.0
description: "Implementation plan review for identifying critical flaws, missing edge cases, and better alternatives. Use when reviewing implementation plans, technical proposals, or design documents. Do NOT use for code review (use appsec-expert)."
risk_level: LOW
token_budget: 3500
---
# Plan Review Expert - Code Generation Rules

---

## 1. Review Principles

### 1.1 Completeness Verification

**Principle:** Every plan must address all requirements. Missing steps cause implementation failures.

```markdown
# ❌ WRONG - Incomplete plan review
Plan looks good, proceed with implementation.

# ✅ CORRECT - Structured completeness check
## Plan Review: User Authentication Feature

### Requirements Coverage
| Requirement | Plan Section | Status |
|-------------|--------------|--------|
| User login | §2.1 | ✅ Covered |
| Password reset | - | ❌ MISSING |
| Session management | §2.3 | ⚠️ Partial |
| Rate limiting | - | ❌ MISSING |

### Critical Gaps
1. **Password reset flow** - No mention of forgot password functionality
2. **Rate limiting** - Login endpoint needs brute-force protection
3. **Session expiry** - Plan mentions sessions but no expiry strategy

### Recommendation
BLOCK - Address gaps before implementation
```

### 1.2 Risk Identification

**Principle:** Identify technical debt, security holes, and scalability issues before they're built.

```typescript
// Plan review risk assessment structure
interface PlanRiskAssessment {
  technical: RiskItem[];
  security: RiskItem[];
  scalability: RiskItem[];
  maintainability: RiskItem[];
}

interface RiskItem {
  description: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  planSection: string;
  mitigation: string;
}

// ❌ WRONG - Vague risk assessment
const badReview = "There might be some performance issues.";

// ✅ CORRECT - Specific, actionable risk items
const properReview: PlanRiskAssessment = {
  technical: [
    {
      description: "N+1 query in user list endpoint",
      severity: "HIGH",
      planSection: "§3.2 API Endpoints",
      mitigation: "Add eager loading or use DataLoader pattern"
    }
  ],
  security: [
    {
      description: "JWT stored in localStorage",
      severity: "CRITICAL",
      planSection: "§4.1 Authentication",
      mitigation: "Use httpOnly cookies with SameSite=Strict"
    }
  ],
  scalability: [],
  maintainability: [
    {
      description: "Business logic mixed with controller",
      severity: "MEDIUM",
      planSection: "§3.2 API Endpoints",
      mitigation: "Extract to service layer"
    }
  ]
};
```

### 1.3 Dependency Analysis

**Principle:** Identify blocking dependencies and parallel work opportunities.

---

## 2. Version Requirements

```
# Plan review is process-based, no runtime dependencies
# Tools for documentation
mermaid-cli>=10.0.0  # Diagram validation
markdown-lint>=0.35  # Markdown structure check
```

---

## 3. Code Patterns

### WHEN reviewing implementation plans, use structured analysis

```python
# ❌ WRONG - Unstructured review
def review_plan(plan: str) -> str:
    return "LGTM"

# ✅ CORRECT - Structured plan review
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class ReviewVerdict(Enum):
    APPROVE = "approve"
    APPROVE_WITH_COMMENTS = "approve_with_comments"
    REQUEST_CHANGES = "request_changes"
    BLOCK = "block"

class Severity(Enum):
    INFO = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ReviewComment:
    section: str
    severity: Severity
    issue: str
    suggestion: str
    blocking: bool = False

@dataclass
class PlanReview:
    verdict: ReviewVerdict
    summary: str
    comments: list[ReviewComment] = field(default_factory=list)
    missing_sections: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines = [
            f"# Plan Review",
            f"",
            f"**Verdict:** {self.verdict.value.upper()}",
            f"",
            f"## Summary",
            self.summary,
            f"",
        ]

        if self.missing_sections:
            lines.extend([
                "## Missing Sections",
                *[f"- [ ] {s}" for s in self.missing_sections],
                "",
            ])

        if self.comments:
            lines.extend([
                "## Review Comments",
                "",
            ])
            for c in self.comments:
                icon = "🚫" if c.blocking else "⚠️" if c.severity.value >= 2 else "💡"
                lines.extend([
                    f"### {icon} {c.section}",
                    f"**Severity:** {c.severity.name}",
                    f"",
                    f"**Issue:** {c.issue}",
                    f"",
                    f"**Suggestion:** {c.suggestion}",
                    "",
                ])

        return "\n".join(lines)

# Usage
def review_authentication_plan(plan_content: str) -> PlanReview:
    review = PlanReview(
        verdict=ReviewVerdict.REQUEST_CHANGES,
        summary="Plan covers core auth flow but missing critical security controls.",
    )

    # Check for required sections
    required = ["rate limiting", "password policy", "session management", "audit logging"]
    for req in required:
        if req.lower() not in plan_content.lower():
            review.missing_sections.append(req.title())

    # Add specific feedback
    if "localstorage" in plan_content.lower() and "jwt" in plan_content.lower():
        review.comments.append(ReviewComment(
            section="Token Storage",
            severity=Severity.CRITICAL,
            issue="JWT stored in localStorage is vulnerable to XSS attacks",
            suggestion="Use httpOnly cookies with SameSite=Strict flag",
            blocking=True,
        ))

    if review.missing_sections or any(c.blocking for c in review.comments):
        review.verdict = ReviewVerdict.BLOCK

    return review
```

### WHEN identifying architectural issues, use pattern detection

```python
# ❌ WRONG - Ad-hoc issue detection
issues = []
if "api" in plan:
    issues.append("Check API design")

# ✅ CORRECT - Pattern-based issue detection
from dataclasses import dataclass
import re

@dataclass
class ArchPattern:
    name: str
    pattern: re.Pattern
    severity: Severity
    issue_template: str
    suggestion_template: str

ANTIPATTERNS = [
    ArchPattern(
        name="God Object",
        pattern=re.compile(r"single\s+(class|module|service)\s+.*\b(all|everything|handles)\b", re.I),
        severity=Severity.HIGH,
        issue_template="Plan describes a {match} that handles too many responsibilities",
        suggestion_template="Split into focused services following Single Responsibility Principle",
    ),
    ArchPattern(
        name="Shared Database",
        pattern=re.compile(r"(services?|microservices?)\s+.*\bshared?\s+database\b", re.I),
        severity=Severity.MEDIUM,
        issue_template="Multiple services sharing a database creates tight coupling",
        suggestion_template="Consider database-per-service or event sourcing pattern",
    ),
    ArchPattern(
        name="Synchronous Chain",
        pattern=re.compile(r"(calls?|invokes?)\s+.*\bthen\s+(calls?|invokes?)\s+.*\bthen\b", re.I),
        severity=Severity.MEDIUM,
        issue_template="Long synchronous call chains increase latency and failure risk",
        suggestion_template="Consider async messaging or saga pattern for multi-step operations",
    ),
    ArchPattern(
        name="Missing Error Handling",
        pattern=re.compile(r"(api|endpoint|service)\s+(?!.*\b(error|exception|failure|retry)\b)", re.I),
        severity=Severity.HIGH,
        issue_template="Service described without error handling strategy",
        suggestion_template="Add error handling, retries, circuit breaker, and fallback strategies",
    ),
]

def detect_antipatterns(plan_content: str) -> list[ReviewComment]:
    comments = []
    for ap in ANTIPATTERNS:
        match = ap.pattern.search(plan_content)
        if match:
            comments.append(ReviewComment(
                section=f"Architecture: {ap.name}",
                severity=ap.severity,
                issue=ap.issue_template.format(match=match.group(0)),
                suggestion=ap.suggestion_template,
                blocking=ap.severity == Severity.CRITICAL,
            ))
    return comments
```

### WHEN generating alternative approaches, provide comparison

```markdown
# ❌ WRONG - Single alternative without context
Consider using microservices instead.

# ✅ CORRECT - Structured alternatives comparison
## Alternative Approaches

### Option A: Monolith (Current Plan)
**Pros:**
- Simpler deployment
- Easier debugging
- Lower operational overhead

**Cons:**
- Scaling requires full app scaling
- Team coupling on releases
- Technology lock-in

**Best for:** Small team, early stage, < 10K users

---

### Option B: Modular Monolith
**Pros:**
- Clear module boundaries
- Easier to split later
- Simpler than microservices

**Cons:**
- Still single deployment
- Requires discipline to maintain boundaries

**Best for:** Growing team, planning future scale

---

### Option C: Microservices
**Pros:**
- Independent scaling
- Team autonomy
- Technology flexibility

**Cons:**
- Operational complexity
- Network latency
- Distributed debugging

**Best for:** Large team, high scale, multiple domains

---

### Recommendation
Given the current team size (3 engineers) and expected scale (< 50K users),
**Option B (Modular Monolith)** provides the best balance of simplicity
and future flexibility.
```

### WHEN reviewing security aspects, use threat checklist

```python
# ❌ WRONG - Generic security comment
# "Make sure it's secure"

# ✅ CORRECT - STRIDE-based security review
from enum import Enum
from dataclasses import dataclass

class ThreatCategory(Enum):
    SPOOFING = "Spoofing"          # Pretending to be someone else
    TAMPERING = "Tampering"         # Modifying data
    REPUDIATION = "Repudiation"     # Denying actions
    INFO_DISCLOSURE = "Info Disclosure"  # Exposing data
    DENIAL_OF_SERVICE = "DoS"       # Preventing access
    ELEVATION = "Elevation"         # Gaining unauthorized access

@dataclass
class ThreatCheck:
    category: ThreatCategory
    question: str
    plan_should_address: str

SECURITY_CHECKLIST = [
    ThreatCheck(
        ThreatCategory.SPOOFING,
        "How are users authenticated?",
        "Authentication mechanism (OAuth, JWT, sessions)"
    ),
    ThreatCheck(
        ThreatCategory.SPOOFING,
        "How are API calls authenticated?",
        "API authentication (API keys, tokens, mTLS)"
    ),
    ThreatCheck(
        ThreatCategory.TAMPERING,
        "How is input validated?",
        "Input validation strategy (schema validation, sanitization)"
    ),
    ThreatCheck(
        ThreatCategory.TAMPERING,
        "How is data integrity ensured?",
        "Data integrity controls (checksums, signatures)"
    ),
    ThreatCheck(
        ThreatCategory.REPUDIATION,
        "How are actions logged?",
        "Audit logging for sensitive operations"
    ),
    ThreatCheck(
        ThreatCategory.INFO_DISCLOSURE,
        "How is sensitive data protected?",
        "Encryption at rest and in transit"
    ),
    ThreatCheck(
        ThreatCategory.INFO_DISCLOSURE,
        "What data is exposed in errors?",
        "Error handling without sensitive data leakage"
    ),
    ThreatCheck(
        ThreatCategory.DENIAL_OF_SERVICE,
        "How is rate limiting handled?",
        "Rate limiting on public endpoints"
    ),
    ThreatCheck(
        ThreatCategory.ELEVATION,
        "How is authorization enforced?",
        "RBAC or ABAC authorization model"
    ),
]

def security_review(plan_content: str) -> list[ReviewComment]:
    """Review plan against STRIDE threat model."""
    comments = []
    plan_lower = plan_content.lower()

    for check in SECURITY_CHECKLIST:
        # Simple keyword detection (in practice, use NLP or manual review)
        keywords = check.plan_should_address.lower().split()
        if not any(kw in plan_lower for kw in keywords if len(kw) > 4):
            comments.append(ReviewComment(
                section=f"Security: {check.category.value}",
                severity=Severity.HIGH,
                issue=f"Plan does not address: {check.question}",
                suggestion=f"Add section covering: {check.plan_should_address}",
                blocking=check.category in [ThreatCategory.SPOOFING, ThreatCategory.ELEVATION],
            ))

    return comments
```

---

## 4. Anti-Patterns

Do not:
- Approve plans without checking for missing requirements
- Skip security review for "internal" services
- Ignore scalability concerns for "MVP"
- Accept vague descriptions ("handle errors appropriately")
- Rubber-stamp plans without structured analysis
- Miss dependency ordering and blocking items

---

## 5. Testing

```python
import pytest
from plan_review import PlanReview, review_authentication_plan, detect_antipatterns

class TestPlanReview:

    def test_detects_missing_rate_limiting(self):
        """Plans without rate limiting should be flagged."""
# ... (additional test cases follow same pattern)
```

---

## 6. Pre-Generation Checklist

Before approving any plan:

- [ ] Requirements coverage: All requirements mapped to plan sections
- [ ] Security review: STRIDE checklist completed
- [ ] Scalability: Load expectations and scaling strategy documented
- [ ] Error handling: Failure modes and recovery documented
- [ ] Dependencies: Blocking items identified and ordered
- [ ] Alternatives: At least one alternative considered
- [ ] Missing sections: All critical sections present
- [ ] Antipattern scan: No architectural antipatterns detected

**Templates**: See `assets/` for reusable output templates.

---
