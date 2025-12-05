---
name: aid-build-skill
description: Generate a new expert skill using the Martins AI Templates structure
category: setup
author: Dev-AID Team
version: 1.0.0
---

# Build New Expert Skill

Create a new expert skill following the Martins AI Templates structure with comprehensive documentation and references.

## Overview

This command guides you through creating a professional, production-ready skill that follows Dev-AID's style guide and best practices.

**What you'll create:**
- Main SKILL.md file with anti-hallucination protocol
- References directory with advanced patterns
- Security examples (if applicable)
- Threat model (for security-sensitive skills)
- Complete frontmatter configuration

**📁 Shared Architecture:**
- Skills are stored in `.dev-aid/skills/` (provider-agnostic)
- Accessible by Claude, Gemini, OpenAI, and future AI providers
- Single source of truth - one skill, all providers benefit

**⚠️ CRITICAL CONSTRAINT:**
- **Main SKILL.md MUST be under 500 lines** (Claude Code loading limit)
- Extract verbose content to `references/` directory to keep main file concise
- Core concepts and workflow in main file, detailed examples in references

**Time:** ~5-10 minutes depending on complexity

---

## Execution Steps

### Phase 1: Gather Information

Ask the user these questions to build the skill:

**Question 1: Skill Name**
```
What's the name of your skill? (kebab-case recommended)
Examples: mongodb-expert, kubernetes-security, react-testing

Your answer: ___
```

**Question 2: Domain/Technology**
```
What technology or domain does this skill cover?
Examples: MongoDB database design, Kubernetes security, React testing patterns

Your answer: ___
```

**Question 3: Expertise Level**
```
What expertise areas should this skill include? (comma-separated)
Examples:
- For MongoDB: schema design, indexing, aggregation, replication
- For K8s Security: RBAC, network policies, pod security, secrets management
- For React Testing: Jest, React Testing Library, E2E testing, mocking

Your answer: ___
```

**Question 4: Risk Level**
```
What's the risk level for this domain?
A. 🟢 LOW - Documentation, UI/UX, design
B. 🟡 MEDIUM - General development, non-critical features
C. 🔴 HIGH - Security, infrastructure, data handling, production systems

Your choice [A/B/C]: ___
```

**Question 5: Security Sensitive?**
```
Does this skill involve security-critical operations?
(If yes, will generate threat model and security examples)

Y/n: ___
```

**Question 6: Model Recommendation**
```
Which model should be recommended for this skill?
A. Sonnet (default - balanced)
B. Opus (complex reasoning)
C. Haiku (fast, simple tasks)

Your choice [A/B/C]: ___
```

---

### Phase 2: Generate Skill Structure

Based on the answers, create the skill directory and files:

**⚠️ IMPORTANT:** Keep main SKILL.md under 500 lines (Claude Code loading limit). Extract detailed examples, verbose patterns, and extensive code samples to reference files.

```bash
# Create directory structure (shared across all AI providers)
SKILL_DIR=".dev-aid/skills/expert/${SKILL_NAME}"
mkdir -p "$SKILL_DIR/references"

# Create main SKILL.md (MUST BE <500 LINES)
cat > "$SKILL_DIR/SKILL.md" <<'EOF'
# [Content based on template - see Phase 3]
# Keep concise: core concepts, essential patterns, workflow
# Extract verbose content to references/
EOF

# Create references for detailed content
cat > "$SKILL_DIR/references/advanced-patterns.md" <<'EOF'
# [Advanced patterns - see Phase 4]
EOF

cat > "$SKILL_DIR/references/anti-patterns.md" <<'EOF'
# [Common mistakes and anti-patterns]
EOF

cat > "$SKILL_DIR/references/performance-optimization.md" <<'EOF'
# [Performance patterns and optimization strategies]
EOF

cat > "$SKILL_DIR/references/testing-guide.md" <<'EOF'
# [Comprehensive testing examples and strategies]
EOF

# If security-sensitive, create additional files
if [[ "$SECURITY_SENSITIVE" == "Y" ]]; then
  cat > "$SKILL_DIR/references/security-examples.md" <<'EOF'
# [Security examples - see Phase 5]
EOF

  cat > "$SKILL_DIR/references/threat-model.md" <<'EOF'
# [Threat model - see Phase 6]
EOF
fi
```

---

### Phase 3: Generate Main SKILL.md

**⚠️ 500-LINE LIMIT:** Main SKILL.md must stay under 500 lines for Claude Code to load it. Keep content concise:
- Core principles and workflow (essential)
- 2-3 key implementation patterns (condensed examples)
- Brief security/performance summaries with references
- Move verbose examples, detailed patterns, and extensive code to `references/`

Use this template structure (adapt based on user's answers):

````markdown
---
name: ${SKILL_NAME}
description: "${DESCRIPTION}"
model: ${MODEL}
---

# ${TITLE}

## 0. Anti-Hallucination Protocol

**🚨 MANDATORY: Read before implementing any code using this skill**

### Verification Requirements

When using this skill to implement ${DOMAIN} features, you MUST:

1. **Verify Before Implementing**
   - ✅ Check official ${TECHNOLOGY} documentation
   - ✅ Confirm ${KEY_PATTERNS} are current
   - ✅ Validate best practices against official guides
   - ❌ Never guess configuration options
   - ❌ Never invent API methods
   - ❌ Never assume compatibility without checking

2. **Use Available Tools**
   - 🔍 Read: Check existing codebase for patterns
   - 🔍 Grep: Search for similar implementations
   - 🔍 WebSearch: Verify specs in official docs
   - 🔍 WebFetch: Read official documentation

3. **Verify if Certainty < 80%**
   - If uncertain about ANY ${DOMAIN} feature/config/pattern
   - STOP and verify before implementing
   - Document verification source in response
   - Errors in ${DOMAIN} can cause [production issues, security vulnerabilities, data loss]

4. **Common ${DOMAIN} Hallucination Traps** (AVOID)
   - ❌ [List common mistakes specific to this domain]
   - ❌ [e.g., Invented configuration options]
   - ❌ [e.g., Made-up API methods]
   - ❌ [e.g., Non-existent best practices]

### Self-Check Checklist

Before EVERY response with ${DOMAIN} code:
- [ ] All ${KEY_CONCEPTS} verified against official docs
- [ ] Configuration options verified against current version
- [ ] Best practices verified against official guides
- [ ] Can cite official documentation sources

**⚠️ CRITICAL**: ${DOMAIN} code with hallucinated patterns causes ${CONSEQUENCES}. Always verify.

---

## 1. Overview

You are an elite ${DOMAIN} expert with deep expertise in:

${EXPERTISE_AREAS}

You design ${DOMAIN} solutions that are:
- **Secure**: Defense against common vulnerabilities
- **Scalable**: Efficient and performant patterns
- **Maintainable**: Clear, documented, testable code
- **Production-Ready**: Proper error handling, monitoring, logging

**Risk Level**: ${RISK_LEVEL} - ${RISK_DESCRIPTION}

### Core Principles

1. **TDD First** - Write tests before implementation
2. **Performance Aware** - Design for scale
3. **Security by Default** - Security mitigations in every component
4. **Documentation Driven** - Document patterns and decisions
5. **Fail Fast** - Validate early, return clear errors

---

## 2. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

[Provide language-specific test example]

### Step 2: Implement Minimum Code

[Provide minimal implementation example]

### Step 3: Refactor

[Provide refactoring example]

### Step 4: Document

[Provide documentation example]

---

## 3. Best Practices

### ${PRACTICE_CATEGORY_1}

[List best practices with examples]

### ${PRACTICE_CATEGORY_2}

[List best practices with examples]

### ${PRACTICE_CATEGORY_3}

[List best practices with examples]

---

## 4. Common Patterns

### Pattern 1: ${PATTERN_NAME}

**Use Case**: [When to use this pattern]

**Implementation**:
```${LANGUAGE}
[Code example]
```

**Pros**:
- [Advantage 1]
- [Advantage 2]

**Cons**:
- [Limitation 1]
- [Limitation 2]

---

## 5. Security Considerations

[If security-sensitive, include detailed security guidance]

### Common Vulnerabilities

1. **${VULNERABILITY_1}**
   - Description: [What it is]
   - Mitigation: [How to prevent]
   - Example: [Code example]

2. **${VULNERABILITY_2}**
   - Description: [What it is]
   - Mitigation: [How to prevent]
   - Example: [Code example]

---

## 6. Performance Optimization

### ${OPTIMIZATION_CATEGORY_1}

[Optimization strategies with examples]

### ${OPTIMIZATION_CATEGORY_2}

[Optimization strategies with examples]

---

## 7. References

**⚠️ NOTE:** Detailed content belongs in `references/` to keep main file under 500 lines.

See `references/` directory for:
- `advanced-patterns.md` - Advanced implementation patterns and complex examples
- `anti-patterns.md` - Common mistakes and how to avoid them
- `performance-optimization.md` - Performance patterns and optimization strategies
- `testing-guide.md` - Comprehensive testing examples and TDD workflow
${SECURITY_SENSITIVE ? "- `security-examples.md` - Security-focused examples and CVE mitigations\n- `threat-model.md` - Comprehensive threat analysis" : ""}

---

## 8. Quick Reference

### Common Commands/APIs

```${LANGUAGE}
[Quick reference examples]
```

### Configuration

```${CONFIG_FORMAT}
[Configuration examples]
```

### Troubleshooting

**Problem**: [Common issue]
**Solution**: [How to fix]

**Problem**: [Common issue]
**Solution**: [How to fix]
````

---

### Phase 4: Generate Advanced Patterns

Create `references/advanced-patterns.md`:

````markdown
# Advanced ${DOMAIN} Patterns

## Pattern 1: ${ADVANCED_PATTERN_1}

### Use Case
[When to use this advanced pattern]

### Implementation
```${LANGUAGE}
[Complex implementation example]
```

### Trade-offs
**Pros**:
- [Advanced benefit 1]
- [Advanced benefit 2]

**Cons**:
- [Complexity trade-off 1]
- [Complexity trade-off 2]

---

## Pattern 2: ${ADVANCED_PATTERN_2}

[Similar structure]

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: ${ANTI_PATTERN_1}

**Problem**: [What's wrong with this approach]

**Bad Example**:
```${LANGUAGE}
[Bad code]
```

**Better Approach**:
```${LANGUAGE}
[Good code]
```

**Why Better**: [Explanation]
````

---

### Phase 5: Generate Security Examples (if applicable)

Create `references/security-examples.md`:

````markdown
# ${DOMAIN} Security Examples

## 1. Input Validation

### Scenario: [Security scenario]

**Vulnerable Code**:
```${LANGUAGE}
[Insecure example]
```

**Secure Code**:
```${LANGUAGE}
[Secure example]
```

**Explanation**: [Why this is secure]

---

## 2. Authentication & Authorization

[Security examples for auth]

---

## 3. Data Protection

[Security examples for data handling]

---

## 4. Security Checklist

Before deploying ${DOMAIN} code:
- [ ] [Security check 1]
- [ ] [Security check 2]
- [ ] [Security check 3]
````

---

### Phase 6: Generate Threat Model (if security-sensitive)

Create `references/threat-model.md`:

````markdown
# ${DOMAIN} Threat Model

## Assets

What needs protection:
- **[Asset 1]**: [Description and criticality]
- **[Asset 2]**: [Description and criticality]

---

## Threats

### Threat 1: ${THREAT_NAME}

**Description**: [What the threat is]

**Attack Vector**: [How it could be exploited]

**Impact**:
- Confidentiality: [HIGH/MEDIUM/LOW]
- Integrity: [HIGH/MEDIUM/LOW]
- Availability: [HIGH/MEDIUM/LOW]

**Likelihood**: [HIGH/MEDIUM/LOW]

**Mitigation**:
1. [Mitigation strategy 1]
2. [Mitigation strategy 2]

**Verification**:
```${LANGUAGE}
[Test to verify mitigation]
```

---

[Repeat for each threat]

---

## Security Controls Matrix

| Threat | Mitigation | Status | Verification |
|--------|-----------|---------|--------------|
| ${THREAT_1} | ${MITIGATION_1} | ✅ Implemented | ${TEST_1} |
| ${THREAT_2} | ${MITIGATION_2} | ✅ Implemented | ${TEST_2} |
````

---

### Phase 7: Update Skill Rules

Add the new skill to `.dev-aid/config/skill-rules.json`:

```bash
# Add file pattern rule
jq '.rules += [{
  "pattern": "*.${FILE_EXTENSION}",
  "skills": ["${SKILL_NAME}"],
  "priority": 8
}]' .dev-aid/config/skill-rules.json > tmp.json && mv tmp.json .dev-aid/config/skill-rules.json
```

---

### Phase 8: Verification & Summary

After generating all files:

```bash
# Verify SKILL.md line count
LINE_COUNT=$(wc -l < "${SKILL_DIR}/SKILL.md")
if [ "$LINE_COUNT" -gt 500 ]; then
  echo "⚠️  WARNING: SKILL.md has $LINE_COUNT lines (max: 500)"
  echo "   Claude Code cannot load files over 500 lines!"
  echo "   Extract verbose content to references/ directory"
  exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Skill Created Successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📁 Files Created:"
echo "  • ${SKILL_DIR}/SKILL.md ($LINE_COUNT lines)"
echo "  • ${SKILL_DIR}/references/advanced-patterns.md"
echo "  • ${SKILL_DIR}/references/anti-patterns.md"
echo "  • ${SKILL_DIR}/references/performance-optimization.md"
echo "  • ${SKILL_DIR}/references/testing-guide.md"
if [[ "$SECURITY_SENSITIVE" == "Y" ]]; then
  echo "  • ${SKILL_DIR}/references/security-examples.md"
  echo "  • ${SKILL_DIR}/references/threat-model.md"
fi
echo ""
echo "📊 Skill Stats:"
echo "  • Name: ${SKILL_NAME}"
echo "  • Model: ${MODEL}"
echo "  • Risk Level: ${RISK_LEVEL}"
echo "  • Security Sensitive: ${SECURITY_SENSITIVE}"
echo "  • Line Count: $LINE_COUNT / 500 ✅"
echo ""
echo "🔄 Next Steps:"
echo "  1. Review and customize the generated skill"
echo "  2. Add specific examples for your domain"
echo "  3. Test the skill activation: 'use ${SKILL_NAME} skill'"
echo "  4. Update references with real-world patterns"
echo ""
echo "📚 Documentation:"
echo "  .dev-aid/docs/DEV-AID-STYLE-GUIDE.md"
echo ""
```

---

## Usage Examples

### Example 1: Create MongoDB Expert Skill

```
/aid-build-skill

→ What's the name of your skill? mongodb-expert
→ What technology does this cover? MongoDB database design and optimization
→ Expertise areas? schema design, indexing, aggregation, replication, sharding
→ Risk level? B (MEDIUM)
→ Security sensitive? Y
→ Model recommendation? A (Sonnet)

✅ Skill created at: .dev-aid/providers/claude/.claude/skills/expert/mongodb-expert/
```

### Example 2: Create React Testing Skill

```
/aid-build-skill

→ What's the name of your skill? react-testing-expert
→ What technology does this cover? React component testing
→ Expertise areas? Jest, React Testing Library, E2E testing, mocking, snapshots
→ Risk level? A (LOW)
→ Security sensitive? n
→ Model recommendation? A (Sonnet)

✅ Skill created at: .dev-aid/providers/claude/.claude/skills/expert/react-testing-expert/
```

---

## Success Criteria

- [ ] All questions answered by user
- [ ] Skill directory created
- [ ] SKILL.md generated with proper frontmatter
- [ ] **⚠️ SKILL.md is under 500 lines** (Claude Code loading limit)
- [ ] references/advanced-patterns.md created
- [ ] references/anti-patterns.md created
- [ ] references/performance-optimization.md created
- [ ] references/testing-guide.md created
- [ ] Security files created (if applicable)
- [ ] Skill rules updated
- [ ] Summary displayed to user
- [ ] Files are properly formatted markdown
- [ ] Follows Martins AI Templates structure

---

## Notes

**Template Source**: Based on martins-ai-templates skill structure

**Customization**: Users should customize generated content with:
- Real code examples from their domain
- Specific configuration options
- Actual API methods and patterns
- Domain-specific anti-patterns

**Validation**: After generation, review:
- Anti-hallucination protocol is relevant
- Best practices are accurate
- Security considerations are comprehensive
- Examples are syntactically correct
