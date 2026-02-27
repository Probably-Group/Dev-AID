# Section Writing Guidance

Per-section tips for writing high-quality PRD content.

## 1. Problem Statement

**Goal:** Explain the pain, not the cure.

- Start with who is affected: "Team leads at mid-size companies..."
- Quantify the problem: "...spend 2+ hours daily..."
- Describe the consequence: "...resulting in delayed decisions and missed deadlines"
- Test: can you read this section without knowing what the project IS? If yes, it's good.

**Red flags:**
- Mentions the product name → rewrite to focus on the problem
- Uses words like "build", "create", "implement" → solution language, not problem language
- No specific actor mentioned → add who experiences the problem

## 2. Target Users

**Goal:** Make abstract users concrete.

- Each persona needs: **Role** (job title or archetype), **Goal** (what they want to achieve), **Pain point** (what blocks them)
- Personas should be distinct — if two personas have the same goals and pain points, merge them
- The personas here determine the "As a..." in Core Features user stories

**Red flags:**
- "Users" without qualification → who specifically?
- Only one persona for a multi-role product → add admin, end-user, etc.
- Personas that don't map to any feature → remove or add features

## 3. Goals and Success Metrics

**Goal:** Define what "done well" looks like with numbers.

- Each goal should link back to the Problem Statement
- Metrics must be measurable: time, count, percentage, boolean
- Include both leading indicators (adoption, usage) and lagging indicators (retention, satisfaction)
- Format: "**Goal:** Reduce time-to-insight. **Metric:** Dashboard loads in < 3s; users check dashboard 3x/week."

**Red flags:**
- "Improve user experience" → unmeasurable, needs a specific metric
- Metrics without baselines → add "from X to Y" or "target: Z"
- Goals that don't relate to the Problem Statement → remove or update Problem

## 4. Core Features

**Goal:** Describe capabilities, not implementation.

- Each feature gets: name, description, user story, acceptance criteria, priority
- User story format: `As a [persona], I want [action] so that [benefit]`
- Acceptance criteria: 2-4 conditions that can be answered yes/no
- Priority: Must-have (MVP), Should-have (v1.1), Nice-to-have (future)

**Red flags:**
- "Implement JWT authentication" → implementation detail; rewrite as "Users can create accounts and log in securely"
- Acceptance criteria with "should be good" → not testable; use specific conditions
- All features marked Must-have → re-prioritize; real MVPs have trade-offs

## 5. Technical Constraints

**Goal:** Document what's fixed, not what you'll build.

- Language and version (e.g., "Python 3.11+")
- Framework requirements (e.g., "FastAPI for API layer")
- Deployment target (e.g., "AWS ECS, us-east-1")
- Browser/platform support (e.g., "Last 2 versions of Chrome, Firefox, Safari")
- Performance requirements (e.g., "API response < 200ms p95")
- Compliance requirements (e.g., "GDPR, SOC 2")

**Red flags:**
- No version numbers → add specific versions
- Constraints that are actually features → move to Core Features
- Missing deployment info → where does this run?

## 6. Out of Scope

**Goal:** Prevent scope creep by being explicit about what you're NOT building.

- List items that stakeholders might reasonably expect but are excluded
- Provide brief rationale: "Mobile app — deferred to Phase 2 after web validation"
- Include items discussed and rejected, not just things nobody thought of

**Red flags:**
- Empty section → there's ALWAYS something out of scope
- "Everything not listed" → not helpful; be specific
- Items that contradict Core Features → inconsistency to resolve

## 7. MVP Scope

**Goal:** Define the minimum set that delivers the core value proposition.

- Select from Core Features (Section 4) — reference by name
- MVP = features a user needs to get value on day one
- If phased: Phase 1 (MVP) → Phase 2 → Phase 3 with clear feature mapping
- The MVP should be small enough to ship in one focused sprint/milestone

**Red flags:**
- MVP = all features → defeats the purpose; cut harder
- MVP missing a feature needed to make other MVP features useful → dependency gap
- No clear criteria for what makes the cut → add a principle (e.g., "core workflow only")

## 8. Architecture Overview

**Goal:** Describe the system shape at a PRD level, not detailed design.

- Major components/services and their responsibilities
- How data flows between components
- External integration points
- Appropriate level: box-and-arrow, not class diagrams
- This section bridges PRD and architecture design

**Red flags:**
- Database schema details → too detailed for PRD
- Class/function names → move to architecture doc
- No mention of data flow → add how information moves through the system

## 9. Dependencies and Risks

**Goal:** Identify what could go wrong and what you depend on.

**Dependencies:**
- External APIs and services
- Third-party libraries with specific version requirements
- Data sources and their availability
- Team/stakeholder dependencies

**Risks (format):**
- Risk description
- Likelihood: High / Medium / Low
- Impact: High / Medium / Low
- Mitigation strategy

**Red flags:**
- No risks listed → every project has risks; common ones: schedule, dependency, technical
- Risks without mitigation → add at least one mitigation per risk
- Missing external dependencies → check .env.example for API keys

## 10. Timeline and Milestones

**Goal:** Set expectations for delivery cadence.

- Phase-based: Phase 1 (MVP) by date, Phase 2 by date, etc.
- Each milestone has: deliverables (features from Section 4), estimated duration
- Include key decision points and review gates
- Dates can be relative ("4 weeks after kickoff") if absolute dates aren't known

**Red flags:**
- Single date with no phases → add intermediate milestones
- No deliverables per milestone → what ships when?
- Unrealistic compression → flag if all features in one milestone

## 11. Open Questions

**Goal:** Document unresolved decisions that block progress.

- Each question should identify: the question, why it matters, who can answer it
- Format: "**Q:** Should we support OAuth2 or magic links? **Impact:** Affects auth feature design. **Owner:** Product lead"
- Good PRDs are honest about what's unknown
- Questions should be actionable — "should we...?" not "what if...?"

**Red flags:**
- "None" → suspicious; every early-stage project has unknowns
- Questions that should be decisions → make the call and document it
- No owner for questions → assign someone to resolve each one
