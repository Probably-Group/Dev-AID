# Universal Skill/Agent Template

> **Purpose**: This template provides a language-independent, role-independent structure for creating new Claude AI Skills and Agents. Use this template to maintain consistency across all skills while adapting content to specific domains.

---

## Template Structure

```yaml
---
name: [skill-name-kebab-case]
description: "[2-3 sentence description: What this skill does, when to use it, what problems it solves. Be specific about use cases and primary capabilities.]"
model: [sonnet|opus|haiku]  # Optional: specify AI model
---
```

---

## File Organization & Progressive Disclosure Strategy

### Why Use Progressive Disclosure for ALL Skills?

**Claude Code Performance Benefits**:
- **Optimal Loading**: Main SKILL.md loads 2-4x faster (300-500 lines vs 1000+ lines)
- **Progressive Disclosure**: Reference files loaded only when Claude needs specific details
- **Token Efficiency**: Avoids loading large files into context unnecessarily
- **Better Organization**: Clear separation of essentials vs deep-dive content
- **Scalability**: Easy to add new content without bloating main file

**🚨 MANDATORY: All skills MUST use the references/ structure** (except trivial skills <300 lines)

### Standard Structure for ALL Skills

```
my-skill/
├── SKILL.md                           # Main skill (300-500 lines)
├── references/
│   ├── quick-reference.md            # Commands, API reference, cheat sheets
│   ├── examples/
│   │   ├── security-examples.md      # Extended security code examples
│   │   ├── integration-examples.md   # Integration patterns
│   │   └── advanced-patterns.md      # Advanced implementation patterns
│   ├── compliance/
│   │   ├── gdpr-guide.md            # GDPR implementation details
│   │   ├── hipaa-guide.md           # HIPAA compliance guide
│   │   └── pci-dss-guide.md         # PCI-DSS requirements
│   └── troubleshooting/
│       ├── common-issues.md         # Detailed troubleshooting
│       └── debug-workflows.md       # Step-by-step debug guides
└── README.md                          # Skill overview (for humans)
```

### Creating the references/ Structure

**🚨 STEP-BY-STEP: Creating a New Skill with Progressive Disclosure**

1. **Create Directory Structure**:
   ```bash
   mkdir -p my-skill/references
   touch my-skill/SKILL.md
   ```

2. **Plan Content Distribution**:
   - **Main SKILL.md**: Core concepts, top 3-5 patterns, summaries
   - **references/**: Detailed implementations, full examples, advanced content

3. **Create Reference Files** (minimum recommended):
   ```bash
   touch my-skill/references/advanced-patterns.md
   touch my-skill/references/security-examples.md    # HIGH/MEDIUM risk
   touch my-skill/references/anti-patterns.md
   ```

4. **Write Main SKILL.md First** (300-500 lines):
   - Include frontmatter, overview, core responsibilities
   - Add 3-7 essential implementation patterns with brief code examples
   - Include OWASP/security summary tables (not full examples)
   - Add top 3-5 common mistakes
   - Include condensed pre-deployment checklist
   - **Add clear links** to reference files at relevant sections

5. **Write Reference Files** (no line limits):
   - Complete implementations with full code examples
   - All OWASP categories with detailed mitigations
   - All common mistakes with before/after examples
   - Extended troubleshooting workflows
   - Performance optimization guides

6. **Link References in Main File**:
   ```markdown
   **📚 For complete implementation details**:
   - See `references/advanced-patterns.md`

   **📚 For detailed security examples** (all 10 OWASP categories):
   - See `references/security-examples.md`
   ```

### What to Keep in Main SKILL.md (300-500 lines)

**MUST INCLUDE** in main SKILL.md:
- ✅ Frontmatter (name, description, model)
- ✅ Section 1: Overview (risk level, core expertise)
- ✅ Section 2: Core Responsibilities/Principles
- ✅ Section 4: Implementation Patterns (5-10 key patterns with code)
- ✅ Section 5: Security Standards (SUMMARIZED - link to details in references/)
  - 5.1: Top 3-5 critical vulnerabilities (not all 10)
  - 5.2: OWASP mapping table only (not full examples)
  - 5.3: Input validation overview (1-2 examples, link to more)
  - 5.4: Secrets management essentials
  - 5.5: Error handling essentials
- ✅ Section 8: Common Mistakes (5-10 critical anti-patterns)
- ✅ Section 13: Pre-Deployment Checklist (condensed)
- ✅ Section 14: Summary
- ✅ **References section** pointing to external files

### What to Move to references/ Directory

**MOVE TO REFERENCES**:
- ❌ Section 5.1: Full vulnerability details (10 CVEs) → `references/security-examples.md`
- ❌ Section 5.2: Full OWASP examples for all 10 categories → `references/security-examples.md`
- ❌ Section 6: Full testing guide → `references/testing-guide.md`
- ❌ Section 9: Quick reference → `references/quick-reference.md`
- ❌ Section 10: Integration examples → `references/integration-examples.md`
- ❌ Section 11: Detailed troubleshooting → `references/troubleshooting/`
- ❌ Section 12: Deployment details → `references/deployment-guide.md`
- ❌ Section 15: Full threat modeling (5+ scenarios) → `references/threat-model.md`
- ❌ Section 16: Compliance details → `references/compliance/`

### How to Reference External Files

**In main SKILL.md**, add references like this:

```markdown
## 5. Security Standards (Overview)

### 5.1 Critical Vulnerabilities (Top 3)

[Include 3 most critical vulnerabilities with brief examples]

**📚 For complete vulnerability analysis** (10 CVEs, full exploitation scenarios, detection methods):
- See `references/security-examples.md`

### 5.2 OWASP Top 10 2025 Mapping

| OWASP ID | Category | Risk Level | Quick Mitigation |
|----------|----------|------------|------------------|
| A01:2025 | Broken Access Control | Critical | Authorize every request |
| A02:2025 | Security Misconfiguration | High | Secure defaults, disable debug |
| [... condensed table ...]

**📚 For detailed OWASP guidance** (all 10 categories with code examples):
- See `references/security-examples.md#owasp-top-10-2025`

---

## 9. Quick Reference

**Essential Commands**:
```bash
# Top 5 most common commands
command1 --option
command2 --option
```

**📚 For complete quick reference** (all commands, config templates, keyboard shortcuts):
- See `references/quick-reference.md`

---

## 11. Troubleshooting

### Top 3 Common Issues

[Include 3 most frequent issues with solutions]

**📚 For comprehensive troubleshooting**:
- See `references/troubleshooting/common-issues.md`
- See `references/troubleshooting/debug-workflows.md`

---

## 15. Threat Modeling

### Critical Attack Scenarios (Top 3)

[Include 3 most critical attack scenarios with mitigations]

**📚 For complete threat model** (5+ attack scenarios, STRIDE analysis):
- See `references/threat-model.md`

---

## 16. Compliance

**Applicable Regulations**: GDPR, HIPAA, PCI-DSS

**Quick Compliance Checklist**:
- [ ] Data encryption at rest and in transit
- [ ] Access controls enforced
- [ ] Audit logging enabled
