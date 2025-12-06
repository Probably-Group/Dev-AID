---
name: skill-creation-expert
description: "Interactive guide for building custom Dev-AID skills with anti-hallucination protocols, proper structure, and automatic skills-index.json registration"
risk_level: low
version: "2.0.0"
credit: |
  Based on: Alireza Rezvani's agents-guide (GitHub: alirezarezvani)
  Source: https://github.com/alirezarezvani/claude-code-skill-factory
  Commit: 61135a053f00d5f56504bac3699fc56aac5ffb5f
  License: MIT
  Adapted to Dev-AID Skill Template by: Dev-AID Team
---

# Skill Creation Expert

## 0. Anti-Hallucination Protocol

## 0. Anti-Hallucination Protocol

### 0.1 Quick Risk Assessment

**Risk Level**: LOW

**Key Risk Factors**:
- Security concerns in low-risk domain
- 3 security issues/patterns identified
- Common attack vectors: Prompt injection in templates, Generated vulnerable code, Template injection
- Requires security awareness and best practices

**Immediate Security Actions**:
1. Review security concerns below before any implementation
2. Never proceed without understanding attack surface
3. Implement security controls from § 0.3 as mandatory requirements

### 0.3 Hallucination Prevention Checklist

**CRITICAL**: These rules are ABSOLUTE. Violation = security incident.

**Domain-Specific Security Rules**:

- ❌ NEVER generate code without security review
- ❌ NEVER use unsanitized input in templates
- ❌ ALWAYS validate generated code
- ❌ ALWAYS include security checklists

**Before ANY code generation**:
1. ✅ Verify rule compliance for proposed implementation
2. ✅ Check if solution introduces any prohibited patterns
3. ✅ Validate all security assumptions
4. ✅ Confirm defensive coding practices are applied

**If uncertain**: STOP and research. Never guess on security.



### Critical Verification Requirements
- **NEVER create skills without understanding domain** - Research the topic thoroughly first
- **NEVER skip anti-hallucination protocol section** - Section 0 is mandatory for ALL skills
- **NEVER forget to update skills-index.json** - Every new skill MUST be registered for auto-injection
- **NEVER exceed 500-line limit for SKILL.md** - Move detailed content to references/

### Common Hallucination Traps
1. **Generic expertise claims** - Using vague capabilities instead of specific, verifiable skills
2. **Missing verification checklist** - Creating skills without self-check mechanisms
3. **Invented best practices** - Claiming patterns without citing authoritative sources
4. **Incomplete workflow** - Skipping critical steps in implementation process
5. **Forgetting references/ extraction** - Keeping all content in SKILL.md instead of splitting

### Self-Check Checklist
Before creating any skill:
- [ ] Researched the domain thoroughly (not guessing expertise)
- [ ] Identified common hallucination traps for this domain
- [ ] Created comprehensive anti-hallucination protocol (Section 0)
- [ ] Defined concrete, testable core principles (Section 2)
- [ ] Documented step-by-step workflow (Section 3)
- [ ] Added self-check checklists at critical workflow steps
- [ ] Extracted detailed content to references/ if approaching 500 lines
- [ ] Created skills-index.json entry with activation keywords
- [ ] Validated skill follows Dev-AID template structure


### 0.4 Progressive Disclosure (500-Line Limit)

**⚠️ CRITICAL**: This SKILL.md file MUST stay <500 lines for Claude Code to load it.

**If this file is approaching 500 lines**:
- Move detailed examples to `references/advanced-patterns.md`
- Move security examples to `references/security-examples.md`
- Move troubleshooting to `references/troubleshooting.md`
- Keep only summaries and links in main file

📚 **For complete progressive disclosure guide**: See `../../../template-references/progressive-disclosure.md`

---

## 1. Overview

**Expertise**: Interactive skill creation for Dev-AID with proper template structure, anti-hallucination protocols, and automatic registration

**Risk Level**: Low (file creation only)

**Key Capabilities**:
- Guided skill creation through 7-8 simple questions
- Automatic Dev-AID template application
- Anti-hallucination protocol generation
- skills-index.json registration
- Cross-provider skill setup (Claude, Gemini, etc.)
- References/ directory structure creation

**When to Use This Skill**:
- Creating new domain-expert skills for Dev-AID
- Building specialized workflow skills
- Developing team-specific expertise skills
- Converting external prompts/agents to Dev-AID skills

## 2. Core Principles

### Dev-AID Skill Template Compliance
- **Required sections**: 0 (Anti-Hallucination), 1 (Overview), 2 (Principles), 3 (Workflow), 4+ (Domain-Specific)
- **500-line limit**: Main SKILL.md must be under 500 lines
- **References extraction**: Detailed content goes to references/ directory
- **Cross-provider**: Skills work with all AI providers (Claude, Gemini, etc.)

### Anti-Hallucination First
- **Section 0 mandatory**: Every skill MUST have anti-hallucination protocol
- **Domain-specific traps**: Identify common hallucinations for this expertise area
- **Self-check checklists**: Provide verification steps at critical workflow points
- **Concrete requirements**: "NEVER X without Y" - specific, testable rules

### Automatic Registration
- **skills-index.json required**: Every new skill MUST be added to registry
- **Activation keywords**: Define primary/secondary keywords for auto-loading
- **File patterns**: Specify file types that trigger this skill
- **Technologies**: List relevant frameworks/tools that activate this skill

### Structured Workflow
- **Step-by-step**: Number each workflow step clearly
- **Validation checkpoints**: Add "Validation:" line after each critical step
- **Examples included**: Provide concrete code/config examples
- **Progressive refinement**: Build complexity gradually

## 3. Implementation Workflow

### Phase 1: Initial Questioning

**Question 1: Skill Purpose**
```
What expertise should this skill provide?

Examples:
- Security code review with OWASP Top 10
- React performance optimization patterns
- Database schema design best practices
- API design with REST/GraphQL standards

Your answer: ___
```

**Validation**: Purpose is specific and domain-focused (not "general coding help")

---

**Question 2: Risk Level**
```
What is the risk level for this domain?

1. Low - Information/guidance only (documentation, research)
2. Medium - Code review/analysis (no execution)
3. High - Code generation/modification (test carefully)
4. Critical - Security/infrastructure changes (expert review required)

Your choice (1-4): ___
```

**Rationale**: Risk level determines anti-hallucination protocol depth

---

**Question 3: Core Capabilities**
```
What are 3-5 core capabilities this skill provides?

Be specific and actionable:
✅ "Identifies SQL injection vulnerabilities in database queries"
❌ "Improves security"

Your capabilities:
1. ___
2. ___
3. ___
```

**Validation**: Each capability is concrete and testable

---

**Question 4: Common Hallucination Traps**
```
What common mistakes or hallucinations could occur in this domain?

Examples for "security-expert":
- Claiming vulnerability exists without proof
- Recommending deprecated security practices
- Missing context-specific security requirements

Your hallucination traps:
1. ___
2. ___
3. ___
```

**Validation**: At least 3 domain-specific hallucination traps identified

---

**Question 5: Skill Name**
```
Skill name (kebab-case, ends with -expert)?

Examples:
- security-review-expert
- react-performance-expert
- api-design-expert

Your name: ___
```

**Validation**: Follows kebab-case, ends with -expert or appropriate suffix

---

**Question 6: Activation Keywords**
```
What keywords should trigger auto-loading of this skill?

Primary keywords (10 points each): ___
Secondary keywords (5 points each): ___
File patterns (matches files): ___
Technologies (matches package.json, etc.): ___

Examples for "api-design-expert":
- Primary: REST API, RESTful, OpenAPI
- Secondary: endpoint, route, API documentation
- File patterns: */routes/*, */api/*, openapi.yaml
- Technologies: FastAPI, Express, NestJS
```

**Validation**: At least 3 primary keywords, 3 secondary keywords defined

---

**Question 7: Required Dependencies**
```
Does this skill require other skills to be loaded?

Examples:
- security-expert might require: devsecops-expert
- api-design-expert might require: devsecops-expert
- None (standalone skill)

Your dependencies: ___
```

---

**Question 8: Conflicting Skills**
```
Are there skills that conflict with this one?

Examples:
- graphql-expert conflicts with: rest-api-design
- sql-expert conflicts with: nosql-expert

Your conflicts: ___
```

**Validation**: Identify logical conflicts (REST vs GraphQL, SQL vs NoSQL)

---

### Phase 2: Generate Skill Structure

**Action**: Create skill directory and files

**Directory Structure**:
```
.dev-aid/skills/expert/[skill-name]/
├── SKILL.md (< 500 lines)
└── references/
    ├── advanced-patterns.md
    ├── anti-patterns.md
    ├── examples.md
    └── [domain-specific].md
```

**Validation**: Directory created at correct path

---

### Phase 3: Generate SKILL.md

**Action**: Create main skill file using Dev-AID template

**Template Structure**:

```markdown
---
name: [skill-name]
description: "[Elevator pitch in 10-15 words]"
risk_level: [low|medium|high|critical]
version: "1.0.0"
credit: |
  [Attribution if based on external source]
---


📚 **For complete skill template with all sections**: See `references/skill-template-example.md`


## 4. Quality Assurance Checklist

**Before implementing this skill, ensure**:

### 4.1 Pre-Implementation Setup
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] Pre-commit hooks installed (`pre-commit install`)
- [ ] Linters installed (black, isort, flake8, mypy, bandit)

### 4.2 Dependency Management
- [ ] All dependencies pinned with exact versions (==)
- [ ] No manual transitive dependency pins
- [ ] Dependencies tested in clean environment

### 4.3 Code Quality Gates (Run BEFORE committing)
- [ ] `black .` - Code formatted
- [ ] `isort .` - Imports sorted
- [ ] `flake8 . --max-line-length=120` - No linting errors
- [ ] `mypy . --ignore-missing-imports` - Type checking passes
- [ ] `bandit -r .` - Security scan clean

### 4.4 Security Validation
- [ ] Input validation for ALL external inputs
- [ ] Path traversal prevention implemented
- [ ] Command injection prevention (no shell=True)
- [ ] SQL injection prevention (parameterized queries)
- [ ] Secrets not in code or error messages

📚 **For complete security validation guide**: See `../../../template-references/security-framework.md`

### 4.5 Test Coverage Requirements
- [ ] Tests written BEFORE implementation (TDD)
- [ ] Unit tests for all public functions
- [ ] Edge case tests (empty, null, max values)
- [ ] Security tests (injection, traversal, overflow)
- [ ] Code coverage >80%

### 4.6 Documentation Requirements
- [ ] Docstrings for all public functions/classes
- [ ] Security considerations documented
- [ ] Examples of correct usage
- [ ] Known limitations documented

---

## 5. Quality Standards

### Skill Quality Requirements

**Anti-Hallucination Protocol**:
- Minimum 3 "NEVER X without Y" requirements
- Minimum 3 domain-specific hallucination traps
- Minimum 5 self-check checklist items
- All requirements are specific and testable

**Workflow Documentation**:
- Each step has clear objective
- Each step has concrete actions (not vague "analyze")
- Each step has validation checkpoint
- Steps are numbered and sequential

**Activation Configuration**:
- Minimum 3 primary keywords
- Minimum 3 secondary keywords
- At least 1 file pattern OR 1 technology trigger
- Confidence weights sum appropriately

**File Organization**:
- SKILL.md under 500 lines
- Detailed content in references/
- skills-index.json updated
- Cross-provider compatibility maintained

### Naming Conventions

**Skill Names**:
- Kebab-case: `api-design-expert`
- Descriptive suffix: `-expert`, `-specialist`, `-master`
- Domain-focused: `security-review-expert` not `code-helper`

**File Names**:
- SKILL.md (uppercase, exactly this)
- references/ (lowercase, exactly this)
- Reference files: `advanced-patterns.md` (kebab-case)

## 6. Common Skill Patterns

### Expert Skills (Most Common)
**Purpose**: Domain expertise (security, performance, API design)
**Risk**: Medium to High
**Structure**: Deep anti-hallucination protocol, comprehensive workflow
**Examples**: `devsecops-expert`, `api-expert`, `performance-expert`

### Specialist Skills
**Purpose**: Narrow, specialized knowledge (specific framework/tool)
**Risk**: Low to Medium
**Structure**: Focused workflow, tool-specific guidance
**Examples**: `fastapi-expert`, `docker-expert`, `tailwindcss`

### Meta Skills
**Purpose**: Skills for creating/managing other skills or prompts
**Risk**: Low
**Structure**: Interactive workflow, template generation
**Examples**: `skill-creation-expert`, `prompt-engineering-expert`

## 7. Integration with Dev-AID

**CRITICAL REQUIREMENT**: Every new skill MUST be added to skills-index.json

**Why This Matters**:
- Auto-injection depends on skills-index.json
- Skills not in registry will NEVER auto-load
- Missing registration = skill is invisible to system

**Verification Process**:
After creating skill:
1. Check skills-index.json has new entry
2. Run select-skills.sh with test context
3. Verify skill appears in output
4. Test with real project context

**Related Skills**:
- `prompt-engineering-expert` (for creating mega-prompts)
- `plan-review-expert` (for reviewing skill design before implementation)

## 8. Documentation Requirements

**MANDATORY DOCUMENTATION**: Every Dev-AID skill creation guide MUST include:

### skills-index.json Update Requirement
**Location**: Add this to all skill creation documentation

```markdown
## IMPORTANT: Registering Your Skill

**EVERY new skill MUST be added to skills-index.json for auto-injection.**

### Steps:
1. Open `/path/to/.dev-aid/skills/registry/skills-index.json`
2. Add entry following template:
   ```json
   {
     "your-skill-name": {
       "activation": {
         "primary_keywords": [...],
         "secondary_keywords": [...],
         "file_patterns": [...],
         "technologies": [...],
         "confidence_weights": {...},
         "requires": [...],
         "exclude_with": [...]
       }
     }
   }
   ```
3. Validate JSON syntax
4. Test activation with: `./select-skills.sh "test context"`

**If you skip this step, your skill will NEVER auto-load.**
```

## 9. References

For detailed information, see:
- `references/dev-aid-template-spec.md` - Complete template specification
- `references/anti-hallucination-patterns.md` - Domain-specific hallucination patterns
- `references/skills-index-reference.md` - Detailed skills-index.json configuration
- `references/example-skills.md` - Sample skills following template

---

**Remember**: NEVER create skills without anti-hallucination protocol (Section 0), ALWAYS update skills-index.json, and ALWAYS keep SKILL.md under 500 lines. Begin by asking: "What expertise should this skill provide?"
