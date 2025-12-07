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

# [Skill Name]

## 0. Anti-Hallucination Protocol

### Critical Verification Requirements
- **NEVER [X] without [Y]** - [Specific requirement]
- **NEVER [A] without [B]** - [Specific requirement]
[3-5 critical requirements]

### Common Hallucination Traps
1. **[Trap name]** - [Description of hallucination]
2. **[Trap name]** - [Description]
[3-5 domain-specific traps]

### Self-Check Checklist
Before [delivering/executing/recommending]:
- [ ] [Verification step 1]
- [ ] [Verification step 2]
[5-10 verification steps]

## 1. Overview

**Expertise**: [One-sentence description]

**Risk Level**: [Low/Medium/High/Critical] ([reason])

**Key Capabilities**:
- [Capability 1]
- [Capability 2]
- [Capability 3-5]

**When to Use This Skill**:
- [Use case 1]
- [Use case 2]
- [Use case 3-5]

## 2. Core Principles

### [Principle 1 Name]
- **[Sub-principle]** - [Description]
- **[Sub-principle]** - [Description]

### [Principle 2 Name]
- **[Sub-principle]** - [Description]

### [Principle 3-4 Name]
[3-4 core principles total]

## 3. Implementation Workflow

### Step 1: [Action Name]

**Objective**: [What this step achieves]

**Actions**:
1. [Concrete action 1]
2. [Concrete action 2]

**Validation**: [How to verify this step is complete]

---

### Step 2: [Action Name]

[Same structure]

---

[Continue for 3-8 major workflow steps]

## 4. Quality Standards

### [Standard Category 1]
- **[Metric/requirement]**: [Description]

### [Standard Category 2-3]
[2-3 quality standard categories]

## 5. Advanced Techniques (Optional)

[Advanced patterns, optimizations, edge cases]

## 6. Common Patterns & Solutions (Optional)

### Pattern: [Common scenario]
**Problem**: [Issue description]
**Solution**: [Approach]

[3-5 common patterns]

## 7. Integration with Dev-AID

**Related Skills**:
- `[skill-name]` ([how it complements this skill])

**Workflow Integration**:
- Use BEFORE [scenario]
- Use WHEN [scenario]

## 8. References

For detailed information, see:
- `references/[topic].md` - [Description]

---

**Remember**: [Key reminder about anti-hallucination or critical workflow step]
```

**Line Count Check**: Verify SKILL.md < 500 lines. If exceeds, extract to references/

**Validation**: All 8 sections present, anti-hallucination protocol complete

---

### Phase 4: Update skills-index.json

**CRITICAL**: This step is MANDATORY for all new skills

**Action**: Add entry to `/path/to/.dev-aid/skills/registry/skills-index.json`

**JSON Entry Template**:
```json
{
  "[skill-name]": {
    "activation": {
      "primary_keywords": ["keyword1", "keyword2", "keyword3"],
      "secondary_keywords": ["keyword4", "keyword5", "keyword6"],
      "file_patterns": ["*/pattern/*", "*.extension"],
      "technologies": ["Framework1", "Framework2"],
      "confidence_weights": {
        "keyword1": 0.35,
        "keyword2": 0.30,
        "keyword3": 0.25
      },
      "requires": ["dependency-skill-1"],
      "exclude_with": ["conflicting-skill-1"]
    }
  }
}
```

**Scoring System**:
- Primary keywords: 10 points each
- Technologies: 8 points each
- Secondary keywords: 5 points each
- Confidence weights: Bonus multiplier (0.1-0.4)
- Minimum threshold for auto-loading: 5 points

**Validation**: JSON is valid, skill appears in registry

---

### Phase 5: Create References (If Needed)

**Action**: Extract detailed content if SKILL.md approaches 500 lines

**Common Reference Files**:
- `advanced-patterns.md` - Complex usage patterns
- `anti-patterns.md` - What NOT to do
- `examples.md` - Comprehensive code examples
- `security-guide.md` - Security-specific details (for security skills)
- `performance-guide.md` - Performance optimization details

**Validation**: Main SKILL.md remains under 500 lines, references exist

---

### Phase 6: Test Skill Activation

**Action**: Verify skill can be auto-loaded

**Test Method**:
```bash
# Run skill selection script with test context
cd /path/to/.dev-aid/orchestration
./select-skills.sh "Test context with [primary keyword]"
```

**Expected Result**: Skill appears in selected skills list

**Validation**: Skill auto-loads when keywords match

---

### Phase 7: Document Skill Creation

**Action**: Create brief documentation

**File**: `[skill-name]/README.md` (optional but recommended)

```markdown
# [Skill Name]

**Purpose**: [One sentence]

**Auto-Activation**: Triggers when project contains:
- Keywords: [list]
- File patterns: [list]
- Technologies: [list]

**Manual Activation**: Reference this skill by name when [scenario]

**Examples**:
- [Use case 1]
- [Use case 2]

**Credit**: [Attribution if applicable]
```

**Validation**: README exists and is clear

## 4. Quality Standards

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

## 5. Common Skill Patterns

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

## 6. Integration with Dev-AID

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

## 7. Documentation Requirements

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

## 8. References

For detailed information, see:
- `references/dev-aid-template-spec.md` - Complete template specification
- `references/anti-hallucination-patterns.md` - Domain-specific hallucination patterns
- `references/skills-index-reference.md` - Detailed skills-index.json configuration
- `references/example-skills.md` - Sample skills following template

---

**Remember**: NEVER create skills without anti-hallucination protocol (Section 0), ALWAYS update skills-index.json, and ALWAYS keep SKILL.md under 500 lines. Begin by asking: "What expertise should this skill provide?"
