# PRD Completeness Checklist — Scoring Rubric

## Scoring Scale

Each section is scored 0-3:

| Score | Level | Definition |
|-------|-------|-----------|
| 3 | Complete | Fully addresses its purpose with specific, actionable content |
| 2 | Partial | Section exists but missing key elements or too vague |
| 1 | Stub | Section exists as a placeholder with minimal content |
| 0 | Missing | Section absent or empty |

## Section-by-Section Rubric

### 1. Problem Statement (Weight: 3x)

| Score | Criteria |
|-------|---------|
| 3 | Describes the problem (not a solution), identifies who is affected, quantifies impact or frequency, explains what happens without a solution |
| 2 | Describes the problem but missing impact/frequency OR mixes in solution language |
| 1 | One vague sentence like "We need a better way to..." |
| 0 | Missing or describes only the solution |

### 2. Target Users (Weight: 2x)

| Score | Criteria |
|-------|---------|
| 3 | 2+ distinct personas with role, goal, and pain point; personas map to features in Section 4 |
| 2 | Users mentioned but no structured personas, OR only 1 persona for a multi-user product |
| 1 | Generic "users" or "developers" without persona detail |
| 0 | Missing |

### 3. Goals and Success Metrics (Weight: 3x)

| Score | Criteria |
|-------|---------|
| 3 | 3+ measurable goals with specific metrics (numbers, percentages, or boolean conditions); each goal links to the Problem Statement |
| 2 | Goals listed but metrics are vague ("improve performance") or missing numbers |
| 1 | Only high-level objectives with no metrics |
| 0 | Missing |

### 4. Core Features (Weight: 3x)

| Score | Criteria |
|-------|---------|
| 3 | 3+ features, each with user story (As a... I want... so that...) AND 2+ acceptance criteria; features are user-facing capabilities, not implementation details |
| 2 | Features listed but missing user stories OR acceptance criteria; OR features describe implementation rather than capabilities |
| 1 | Bullet list of feature names only, no stories or criteria |
| 0 | Missing |

### 5. Technical Constraints (Weight: 2x)

| Score | Criteria |
|-------|---------|
| 3 | Specifies language/framework, deployment target, compatibility requirements, and performance constraints with concrete values |
| 2 | Some constraints listed but missing key dimensions (e.g., no performance targets, no deployment info) |
| 1 | Only mentions the programming language |
| 0 | Missing |

### 6. Out of Scope (Weight: 1x)

| Score | Criteria |
|-------|---------|
| 3 | Explicitly lists 3+ items that are NOT in this project, with brief rationale for each exclusion |
| 2 | Lists exclusions but without rationale, or only 1-2 items |
| 1 | Generic "everything not listed" statement |
| 0 | Missing |

### 7. MVP Scope (Weight: 3x)

| Score | Criteria |
|-------|---------|
| 3 | Clearly identifies which features from Section 4 are in the first release; includes phased delivery if applicable; MVP is a subset, not everything |
| 2 | MVP defined but includes all features (defeating the purpose), OR no clear mapping to Section 4 features |
| 1 | Mentions "MVP" but no specific feature selection |
| 0 | Missing |

### 8. Architecture Overview (Weight: 2x)

| Score | Criteria |
|-------|---------|
| 3 | Describes major components/services, data flow, and integration points; appropriate for PRD level (not detailed design) |
| 2 | Lists components but missing data flow or integration points |
| 1 | Only mentions the tech stack without describing how components interact |
| 0 | Missing |

### 9. Dependencies and Risks (Weight: 2x)

| Score | Criteria |
|-------|---------|
| 3 | Lists external dependencies (APIs, services, data sources) AND 3+ risks with likelihood, impact, and mitigation strategy |
| 2 | Dependencies OR risks listed, but not both; OR risks lack mitigation |
| 1 | Generic risk like "project might be delayed" |
| 0 | Missing |

### 10. Timeline and Milestones (Weight: 1x)

| Score | Criteria |
|-------|---------|
| 3 | Phased timeline with milestones, deliverables per phase, and dates or relative durations |
| 2 | Milestones listed but no dates/durations, OR only a single deadline |
| 1 | "TBD" or "Q3 2025" with no breakdown |
| 0 | Missing |

### 11. Open Questions (Weight: 1x)

| Score | Criteria |
|-------|---------|
| 3 | 3+ specific unresolved questions with identified owner/stakeholder for each; questions are actionable |
| 2 | Questions listed but generic or without owners |
| 1 | Only 1 question, or "none at this time" |
| 0 | Missing |

## Grade Calculation

```
weighted_score = sum(section_score × section_weight)
max_possible = 69
percentage = (weighted_score / 69) × 100
```

| Grade | Percentage | Weighted Score |
|-------|-----------|---------------|
| A | 90-100% | 62-69 |
| B | 75-89% | 52-61 |
| C | 60-74% | 42-51 |
| D | 40-59% | 28-41 |
| F | 0-39% | 0-27 |
