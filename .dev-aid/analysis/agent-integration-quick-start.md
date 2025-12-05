# Agent Integration Quick Start Guide

**Quick reference for integrating agents into Dev-AID**

---

## Top 10 Agents to Integrate (Priority Order)

### Tier 1: Ready to Use (Week 1) - 5 agents

| # | Agent | Source | Category | Effort | Value |
|---|-------|--------|----------|--------|-------|
| 1 | **refactor-planner** ⭐⭐⭐ | infrastructure-showcase | code-quality | 1-2h | Highest |
| 2 | **documentation-architect** ⭐⭐ | infrastructure-showcase | documentation | 1-2h | High |
| 3 | **web-research-specialist** ⭐⭐ | infrastructure-showcase | research | 1-2h | High |
| 4 | **plan-reviewer** ⭐⭐ | infrastructure-showcase | planning | 1-2h | High |
| 5 | **prompts-guide** ⭐ | skill-factory | creation | 1h | Medium |

### Tier 2: Minor Adaptation (Weeks 2-3) - 5 agents

| # | Agent | Source | Category | Effort | Value |
|---|-------|--------|----------|--------|-------|
| 6 | **test-engineer** ⭐⭐ | tresor | code-quality | 2-4h | High |
| 7 | **code-architecture-reviewer** ⭐ | infrastructure-showcase | code-quality | 2-3h | Medium |
| 8 | **performance-tuner** ⭐ | tresor | performance | 2-4h | Medium |
| 9 | **agents-guide** ⭐ | skill-factory | creation | 2-3h | Medium |
| 10 | **docs-writer** | tresor | documentation | 3-4h | Low |

---

## Repository URLs

```bash
# Clone these repositories for access to agents
git clone https://github.com/diet103/claude-code-infrastructure-showcase
git clone https://github.com/alirezarezvani/claude-code-tresor
git clone https://github.com/alirezarezvani/claude-code-skill-factory
```

---

## Dev-AID Agent Format (Template)

```yaml
---
name: agent-name
description: Clear one-line description
activation: |
  - "trigger phrase one"
  - "trigger phrase two"
  - "activation pattern three"
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
model: claude-sonnet-4-5
expertise:
  - Domain area 1
  - Domain area 2
color: "#HEX_COLOR"
category: category-name
---

# Agent Name

You are an expert [domain] with deep knowledge of...

## Your Expertise

### 1. Domain Knowledge
...

## Your Responsibilities

### When Activated
1. Step 1
2. Step 2

## Guidelines
- Guideline 1
- Guideline 2

## Activation

You activate when users say:
- "Trigger phrase"
```

---

## Category Structure

```
.dev-aid/providers/claude/.claude/agents/
├── setup/
│   └── dev-aid-setup-advisor.md
├── code-quality/
│   ├── refactor-planner.md              # NEW
│   ├── code-architecture-reviewer.md    # NEW
│   └── test-engineer.md                 # NEW
├── documentation/
│   ├── documentation-architect.md       # NEW
│   └── docs-writer.md                   # NEW
├── research/
│   └── web-research-specialist.md       # NEW
├── planning/
│   └── plan-reviewer.md                 # NEW
├── performance/
│   └── performance-tuner.md             # NEW
└── creation/
    ├── agents-guide.md                  # NEW
    └── prompts-guide.md                 # NEW
```

---

## Color Scheme

| Category | Color | Hex |
|----------|-------|-----|
| Setup | Blue | `#4A90E2` |
| Code Quality | Purple | `#9B59B6` |
| Documentation | Light Blue | `#3498DB` |
| Research | Orange | `#E67E22` |
| Planning | Teal | `#16A085` |
| Performance | Red | `#E74C3C` |
| Creation | Yellow | `#F39C12` |

---

## Integration Checklist (Per Agent)

### Pre-Integration
- [ ] Read original agent file
- [ ] Assess quality and relevance
- [ ] Check for overlaps with Dev-AID skills
- [ ] Identify hardcoded paths

### Adaptation
- [ ] Add YAML frontmatter
- [ ] Condense if verbose (target 50% reduction)
- [ ] Remove skill delegation instructions
- [ ] Update hardcoded paths
- [ ] Define activation triggers (3-5 phrases)
- [ ] Set category and color

### Testing
- [ ] Test agent activation
- [ ] Verify tool access
- [ ] Check for conflicts
- [ ] Validate with real scenarios

### Deployment
- [ ] Place in category directory
- [ ] Update documentation
- [ ] Create example use cases

---

## Quick Adaptation Steps

### 1. Infrastructure-Showcase Agents (Easy - 1-2h each)

**Original Format**:
```markdown
# Agent Name

**Description**: What it does

**When to use**:
- Scenario 1
- Scenario 2

## Purpose
...

## Instructions
...
```

**Adaptation**:
1. Add YAML frontmatter (copy template above)
2. Convert "When to use" → `activation` triggers
3. Add tools, model, expertise, color, category
4. Keep existing prompt structure
5. Deploy to appropriate category folder

**Example Command**:
```bash
# Copy agent to Dev-AID
cp ~/infrastructure-showcase/.claude/agents/refactor-planner.md \
   /home/user/Dev-AID/.dev-aid/providers/claude/.claude/agents/code-quality/

# Edit to add YAML frontmatter
# Test activation
```

---

### 2. Tresor Agents (Medium - 2-4h each)

**Issues to Fix**:
- ❌ 2000+ token prompts (too verbose)
- ❌ Skill delegation confusion
- ❌ Repetitive content

**Adaptation**:
1. Add YAML frontmatter
2. **Condense prompt to 50%**:
   - Remove skill delegation instructions
   - Remove repetitive framework documentation
   - Keep core expertise and examples
   - Keep practical code samples
3. Define clear scope
4. Add activation triggers
5. Deploy

**Example - test-engineer condensation**:
- Original: 2000+ tokens
- Remove: 1000+ tokens of skill coordination
- Keep: Testing strategy, coverage targets, frameworks, code examples
- Result: ~1000 token focused prompt

---

### 3. Skill-Factory Agents (Easy - 1h each)

**Already Compatible**:
- ✅ Has YAML frontmatter
- ✅ Uses Dev-AID format
- ✅ Clear structure

**Minimal Changes**:
1. Update category if needed
2. Verify activation triggers
3. Deploy

---

## Example: Refactor-Planner Integration (30 min)

```bash
# 1. Get original
cd ~/infrastructure-showcase
cat .claude/agents/refactor-planner.md

# 2. Copy to Dev-AID
cp .claude/agents/refactor-planner.md \
   /home/user/Dev-AID/.dev-aid/providers/claude/.claude/agents/code-quality/refactor-planner.md

# 3. Edit to add YAML frontmatter (use template)
nano /home/user/Dev-AID/.dev-aid/providers/claude/.claude/agents/code-quality/refactor-planner.md

# 4. Test
cd /home/user/Dev-AID
claude
# Say: "create a refactoring plan"
# Verify: Agent activates correctly

# 5. Done!
```

---

## Common YAML Frontmatter Values

### Activation Patterns

**Refactoring**:
```yaml
activation: |
  - "create a refactoring plan"
  - "analyze code for refactoring"
  - "plan refactoring for"
  - "refactoring strategy"
```

**Documentation**:
```yaml
activation: |
  - "create documentation"
  - "generate docs for"
  - "document this codebase"
  - "documentation plan"
```

**Testing**:
```yaml
activation: |
  - "create test strategy"
  - "design test suite"
  - "testing recommendations"
  - "how should I test"
```

**Performance**:
```yaml
activation: |
  - "optimize performance"
  - "profile this code"
  - "performance analysis"
  - "identify bottlenecks"
```

**Research**:
```yaml
activation: |
  - "research this error"
  - "find solutions for"
  - "investigate this issue"
  - "search for information"
```

**Planning**:
```yaml
activation: |
  - "review this plan"
  - "validate implementation plan"
  - "assess development plan"
  - "plan review"
```

### Common Tools
```yaml
tools:
  - Read      # Read files
  - Write     # Create files
  - Edit      # Modify files
  - Bash      # Execute commands
  - Grep      # Search content
  - Glob      # Find files
```

### Common Expertise Areas
```yaml
expertise:
  - Code refactoring
  - Design patterns
  - SOLID principles
  - Testing strategy
  - Documentation
  - Performance optimization
  - Security auditing
  - Architecture design
```

---

## Troubleshooting

### Issue: Agent doesn't activate with trigger phrase
**Solution**: Check activation patterns match user input, ensure YAML syntax correct

### Issue: Agent overlaps with existing skill
**Solution**: Review Dev-AID's 65+ skills, consider if agent duplicates functionality

### Issue: Prompt too verbose
**Solution**: Condense to 50%, remove skill delegation, focus on core workflow

### Issue: Hardcoded paths in agent
**Solution**: Replace with project-agnostic paths (`./dev/active/`, `./.dev-aid/`)

### Issue: Unclear scope boundaries
**Solution**: Define what agent does AND doesn't do, clarify delegation to skills

---

## Success Metrics (Review after 30 days)

Track for each agent:
1. **Usage Frequency**: How often invoked?
2. **User Satisfaction**: Providing value?
3. **Activation Success**: Triggers working?
4. **Scope Clarity**: Clear boundaries?
5. **Quality Issues**: Prompt problems?

**Decision Points**:
- ✅ High usage + high value → Keep
- ⚠️ Low usage + high value → Improve activation triggers
- ⚠️ High usage + low value → Refine prompt
- ❌ Low usage + low value → Deprecate

---

## Next Steps

**Week 1**: Deploy Tier 1 agents (5 agents, ~5-10 hours)
1. refactor-planner
2. documentation-architect
3. web-research-specialist
4. plan-reviewer
5. prompts-guide

**Weeks 2-3**: Adapt Tier 2 agents (5 agents, ~10-20 hours)
6. test-engineer
7. code-architecture-reviewer
8. performance-tuner
9. agents-guide
10. docs-writer

**Week 4+**: Monitor, iterate, refine
- Track usage metrics
- Gather feedback
- Adjust activation triggers
- Refine prompts based on real use
- Deprecate low-value agents

---

**Total Time Investment**: 15-30 hours over 3-4 weeks
**Expected ROI**: 10-12 production-ready agents enhancing Dev-AID
**Risk**: Low - Start with high-quality agents, iterate based on feedback

---

**Ready to start? Begin with refactor-planner!**
