---
name: prd-generator
version: 2.0.0
description: "Product Requirements Document generator with three modes: interactive builder, validator, and reverse-engineer from existing code. Use when creating PRDs for new projects, validating existing PRDs for completeness, or generating PRDs from existing codebases. Do NOT use for technical architecture docs (use senior-architect) or implementation plans (use plan-review-expert)."
risk_level: LOW
token_budget: 2500
---

# PRD Generator — Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Verification Rules

- **Never invent features** — In reverse-engineer mode, every feature listed MUST trace to actual code (route, handler, component, test, or config file)
- **Never fabricate metrics** — Success metrics in generated PRDs must be marked `[PLACEHOLDER]` unless user provides real data
- **Never assume tech stack** — Detect from package files, not from directory names or conventions
- **Mark confidence explicitly** — Every reverse-engineered section gets `<!-- confidence: HIGH|MEDIUM|LOW|UNCONFIRMED -->` as an HTML comment
- **Distinguish facts from inference** — If inferring a feature from test names or directory structure, say "inferred from" not "the project has"

### 0.2 Scope Boundaries

- PRDs describe **what** and **why**, not **how** — avoid implementation details in Core Features
- User stories use `As a [persona], I want [action] so that [benefit]` format — no technical jargon in the user-facing part
- Acceptance criteria are testable boolean conditions, not vague quality statements
- "Out of Scope" must be explicit, not just "everything not listed"

## 1. Overview

### 1.1 Three Modes

| Mode | Trigger | Input | Output |
|------|---------|-------|--------|
| **Interactive Builder** | No PRD + fresh project, or `--build` flag | User answers 7 guided questions | `PRD.md` at repo root |
| **Validator** | PRD.md exists, or `--validate` flag | Existing PRD.md | Validation report with grade |
| **Reverse-Engineer** | No PRD + existing codebase, or `--reverse-engineer` flag | Codebase scanning | Draft `PRD.md` with confidence tags |

### 1.2 Auto-Detection Decision Tree

```
Has PRD.md at repo root?
├── YES → Mode 2 (Validator)
└── NO
    ├── Has code files? (src/, lib/, app/, *.py, *.ts, *.rs, etc.)
    │   ├── YES → Offer choice: Mode 1 (Build from scratch) or Mode 3 (Reverse-engineer)
    │   └── NO → Mode 1 (Interactive Builder)
    └── Flag override: --build, --validate, --reverse-engineer always wins
```

### 1.3 PRD Output Schema (11 sections)

All generated PRDs use this `## N. Title` heading format for cross-skill compatibility:

```markdown
# PRD: {Project Name}
> Version: 1.0 | Status: Draft | Author: {name} | Created: {date} | Updated: {date}

## 1. Problem Statement
## 2. Target Users
## 3. Goals and Success Metrics
## 4. Core Features
## 5. Technical Constraints
## 6. Out of Scope
## 7. MVP Scope
## 8. Architecture Overview
## 9. Dependencies and Risks
## 10. Timeline and Milestones
## 11. Open Questions
```

## 2. Mode 1 — Interactive Builder

### 2.1 Question Flow

Walk the user through 7 steps. For each step, provide examples and accept multi-line input where appropriate.

**Step 1: Project Identity**
- Ask: project name, one-line description
- Default project name: basename of the repo root directory

**Step 2: Problem Statement**
- Ask: "What problem does this project solve? Who experiences it? What happens if it's not solved?"
- Guide: should be 2-4 sentences, focused on the pain point, not the solution
- Reject if it describes a solution instead of a problem

**Step 3: Target Users**
- Ask: "Who are the primary users? Describe 1-3 personas with their role, goal, and pain point."
- Format each persona as: `**{Role}** — {Goal}. Pain point: {frustration}`

**Step 4: Core Features**
- Ask: "List the main features. For each, I'll ask for a user story and acceptance criteria."
- For each feature:
  - User story: `As a [persona from Step 3], I want [action] so that [benefit]`
  - Acceptance criteria: 2-4 testable conditions
  - Priority: Must-have / Should-have / Nice-to-have

**Step 5: Technical Constraints**
- Auto-detect from project files (language, framework, existing infra)
- Present detected constraints and ask user to confirm/add/remove
- Include: language, framework, deployment target, browser support, performance requirements

**Step 6: MVP Scope**
- Show all features from Step 4 with their priorities
- Ask: "Which features are in the MVP (first release)?"
- Must include at least all Must-have features
- Organize into phases if user wants phased delivery

**Step 7: Open Questions**
- Ask: "What decisions are still unresolved? What needs research or stakeholder input?"
- Suggest common open questions based on the project type (auth strategy, hosting, pricing model, etc.)

### 2.2 Output

Write `PRD.md` at the repo root using the template from `assets/prd-template.md`. Fill all 11 sections from the collected answers. Sections not covered by the 7 steps (Goals/Metrics, Architecture Overview, Dependencies/Risks, Timeline) get stub text with `[TODO: ...]` markers.

## 3. Mode 2 — Validator

### 3.1 Process

1. Read the existing PRD.md
2. Score each of the 11 sections using the rubric in `references/prd-completeness-checklist.md`
3. Calculate weighted score and letter grade
4. Generate a validation report using `assets/validation-report-template.md`

### 3.2 Scoring Summary

Each section is scored 0-3:
- **3 (Complete)** — Section fully addresses its purpose with specific, actionable content
- **2 (Partial)** — Section exists but missing key elements or too vague
- **1 (Stub)** — Section exists as a placeholder with minimal content
- **0 (Missing)** — Section absent or empty

### 3.3 Weights

| Section | Weight | Max Weighted |
|---------|--------|-------------|
| 1. Problem Statement | 3x | 9 |
| 2. Target Users | 2x | 6 |
| 3. Goals and Success Metrics | 3x | 9 |
| 4. Core Features | 3x | 9 |
| 5. Technical Constraints | 2x | 6 |
| 6. Out of Scope | 1x | 3 |
| 7. MVP Scope | 3x | 9 |
| 8. Architecture Overview | 2x | 6 |
| 9. Dependencies and Risks | 2x | 6 |
| 10. Timeline and Milestones | 1x | 3 |
| 11. Open Questions | 1x | 3 |
| **Total** | | **69** |

### 3.4 Grade Thresholds

| Grade | Score Range | Meaning |
|-------|-----------|---------|
| A | 90-100% (62-69) | Production-ready PRD |
| B | 75-89% (52-61) | Good, minor gaps |
| C | 60-74% (42-51) | Usable but needs work |
| D | 40-59% (28-41) | Significant gaps |
| F | 0-39% (0-27) | Incomplete, needs major revision |

### 3.5 Output

Display the validation report inline. For each section scoring below 3, provide specific recommendations for improvement.

## 4. Mode 3 — Reverse-Engineer

### 4.1 Scanning Strategy

Scan the codebase to infer PRD sections. See `references/reverse-engineer-patterns.md` for detailed file-to-section mappings.

**High-level mapping:**

| PRD Section | Source Files |
|-------------|-------------|
| Problem Statement | README.md, ABOUT.md, package.json description |
| Target Users | README.md "for" sections, docs/*, CONTRIBUTING.md |
| Core Features | Route files, handlers, components, CLI commands, test names |
| Technical Constraints | package.json, pyproject.toml, Cargo.toml, go.mod, Dockerfile |
| Architecture Overview | Directory structure, docker-compose.yml, config files |
| MVP Scope | Git log frequency analysis, recent feature branches |
| Dependencies/Risks | Lock files, external service configs, CI/CD files |

### 4.2 Confidence Assignment

- **HIGH** — Direct textual evidence (README says "this project does X")
- **MEDIUM** — Strong code evidence (auth/ directory + JWT dependency → authentication feature)
- **LOW** — Indirect inference (test file names suggest feature, but no direct code path confirmed)
- **UNCONFIRMED** — Placeholder derived from project type conventions, not actual code

### 4.3 Output

Generate a draft `PRD.md` with:
- All 11 sections populated where evidence exists
- `<!-- confidence: LEVEL -->` HTML comment after each section heading
- `[NEEDS REVIEW]` markers on inferred content for user to verify
- Summary at the top: "This PRD was auto-generated from codebase analysis. Sections marked [NEEDS REVIEW] require human verification."

## 5. Common Pitfalls

### WHEN writing Core Features
- **Wrong**: "Implement JWT authentication with refresh tokens" (implementation detail)
- **Right**: "User authentication — users can create accounts, log in, and maintain sessions"
- Features describe capabilities, not technical approaches

### WHEN writing Success Metrics
- **Wrong**: "The app should be fast" (unmeasurable)
- **Right**: "Page load time < 2s on 3G connection" (testable)
- Every metric must have a number or boolean condition

### WHEN defining MVP Scope
- **Wrong**: Listing all features as MVP (defeats the purpose)
- **Right**: Selecting the minimum set that delivers the core value proposition
- MVP should be deliverable in a single focused sprint/milestone

### WHEN writing Problem Statement
- **Wrong**: "We need a dashboard" (solution, not problem)
- **Right**: "Team leads spend 2+ hours daily gathering metrics from 5 different tools" (actual pain)
- Problem statements never mention the solution

### WHEN reverse-engineering
- **Wrong**: Listing every file as a feature
- **Right**: Grouping related files into user-facing capabilities
- A directory with 20 React components is ONE feature, not 20

## 6. Integration with Other Skills

| Skill | Integration Point |
|-------|------------------|
| `plan-review-expert` | Reads PRD sections 4 (Features) and 7 (MVP Scope) to validate implementation plans |
| `senior-architect` | Reads PRD section 8 (Architecture) as input for architecture decisions |
| `design-first` | Uses PRD sections 2 (Users) and 4 (Features) for design system decisions |
| `api-expert` | References PRD section 5 (Technical Constraints) for API design |

The `## N. Title` heading format enables these skills to parse specific PRD sections by number.

## 7. References

- **Scoring rubric**: `references/prd-completeness-checklist.md`
- **Reverse-engineer patterns**: `references/reverse-engineer-patterns.md`
- **Section writing guidance**: `references/section-guidance.md`
- **PRD template**: `assets/prd-template.md`
- **Validation report template**: `assets/validation-report-template.md`
