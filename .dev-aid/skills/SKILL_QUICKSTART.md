# Skill Development Quick-Start Guide

**5-Minute Guide to Creating Production-Ready Skills**

---

## TL;DR - Quick Command

```bash
# Use the slash command
/dev-aid-build-skill

# Or manually:
cp -r .dev-aid/skills/SKILL_TEMPLATE.md .dev-aid/skills/expert/my-skill/SKILL.md
```

---

## Table of Contents

1. [Quick Decision Tree](#quick-decision-tree)
2. [3-Step Process](#3-step-process)
3. [Risk-Based Template Selection](#risk-based-template-selection)
4. [Examples by Skill Type](#examples-by-skill-type)
5. [Common Mistakes to Avoid](#common-mistakes-to-avoid)
6. [Checklist Before Submission](#checklist-before-submission)

---

## Quick Decision Tree

**Start here →** What are you building?

```
📄 Documentation/Guides
│
├─→ Use: Standard Template (LOW risk)
└─→ Focus: Quality checklist, TDD

🎨 UI/UX/Design
│
├─→ Use: Standard Template (LOW risk)
└─→ Focus: Accessibility, WCAG compliance

⚙️ APIs/Data Processing
│
├─→ Use: Template + Security Framework (MEDIUM risk)
└─→ MUST: Vulnerability research, OWASP check

🔐 Security/Infrastructure/Auth
│
├─→ Use: Full Template + All References (HIGH risk)
└─→ MUST: Vulnerability research, threat model, OWASP, compliance
```

---

## 3-Step Process

### Step 1: Choose Your Template (30 seconds)

| Risk Level | Template | Time to Create |
|------------|----------|----------------|
| 🟢 **LOW** | SKILL_TEMPLATE.md only | 5-10 min |
| 🟡 **MEDIUM** | SKILL_TEMPLATE.md + security references | 15-20 min |
| 🔴 **HIGH** | SKILL_TEMPLATE.md + all references | 30-45 min |

### Step 2: Run the Command (5 minutes)

```bash
# Interactive mode (recommended)
/dev-aid-build-skill

# Manual mode
cd .dev-aid/skills
mkdir -p expert/my-skill/references
cp SKILL_TEMPLATE.md expert/my-skill/SKILL.md
```

### Step 3: Customize and Verify (5-30 minutes)

**All Skills (Required)**:
- [ ] Update frontmatter (name, description, risk_level)
- [ ] Complete § 0.1: Risk Assessment
- [ ] Run quality gates: `black . && isort . && flake8 . && mypy .`
- [ ] Write tests (TDD) before implementation
- [ ] Verify <500 lines: `wc -l SKILL.md`

**MEDIUM Risk (Additional)**:
- [ ] Complete § 0.2: Vulnerability Research
- [ ] Search [NVD Database](https://nvd.nist.gov/) for CVEs (2022-2025)
- [ ] Document top 5 vulnerabilities in skill

**HIGH Risk (Additional)**:
- [ ] Review template-references/security-framework.md
- [ ] Create threat model (template-references/threat-modeling.md)
- [ ] Check OWASP Top 10 2025 compliance
- [ ] Review compliance requirements (GDPR/HIPAA/PCI-DSS)

---

## Risk-Based Template Selection

### 🟢 LOW Risk Examples

**Use Cases**: Documentation, UI/UX, design, testing, tutorials

**Template**: Standard SKILL_TEMPLATE.md

**Focus On**:
- § 4: Quality Assurance Checklist
- § 6: Testing Strategy
- Progressive disclosure (keep <500 lines)

**Skip**:
- Vulnerability research
- Threat modeling
- Compliance reviews

**Example Skills**: markdown-expert, ui-ux-design, accessibility-wcag

---

### 🟡 MEDIUM Risk Examples

**Use Cases**: APIs, data processing, application code, CLI tools

**Template**: SKILL_TEMPLATE.md + security-framework.md reference

**MUST Complete**:
- ✅ § 0.1: Risk Assessment
- ✅ § 0.2: Vulnerability Research Protocol
  - Search NVD for domain CVEs (2022-2025)
  - Review OWASP Top 10 2025 applicability
  - Document top 5-10 vulnerabilities
- ✅ § 0.3: Hallucination Prevention Checklist

**Reference**:
- `template-references/security-framework.md` (vulnerability research)
- `template-references/owasp-2025-guide.md` (applicable categories)

**Example Skills**: api-expert, graphql-expert, fastapi-expert

---

### 🔴 HIGH Risk Examples

**Use Cases**: Security, infrastructure, authentication, data storage, production systems

**Template**: SKILL_TEMPLATE.md + ALL template-references/

**MANDATORY Steps**:
1. ✅ Complete § 0.2: Vulnerability Research (full protocol)
2. ✅ Review `template-references/security-framework.md` (all sections)
3. ✅ Create threat model using `template-references/threat-modeling.md`
4. ✅ Check all OWASP Top 10 2025 categories (template-references/owasp-2025-guide.md)
5. ✅ Review compliance (template-references/compliance-guide.md)
6. ✅ Implement security controls matrix
7. ✅ Document attack scenarios

**Example Skills**: devsecops-expert, bash-expert, kanidm-expert, harbor-expert

---

## Examples by Skill Type

### Example 1: Creating a Documentation Skill (LOW Risk)

```bash
# Step 1: Create skill
/dev-aid-build-skill

# Answers:
# Skill name: markdown-expert
# Domain: Markdown documentation and technical writing
# Expertise: syntax, formatting, best practices, accessibility
# Risk level: A (LOW)
# Security sensitive: n
# Model: A (Sonnet)

# Step 2: Customize SKILL.md
# - Focus on § 4: Quality checklist
# - Add markdown-specific patterns
# - Include accessibility guidelines

# Step 3: Verify
wc -l .dev-aid/skills/expert/markdown-expert/SKILL.md  # Must be <500
pytest tests/ --cov  # Must be >80% coverage
black . && isort . && flake8 .  # Must pass
```

**Time**: 5-10 minutes

---

### Example 2: Creating an API Skill (MEDIUM Risk)

```bash
# Step 1: Create skill
/dev-aid-build-skill

# Answers:
# Skill name: rest-api-expert
# Domain: REST API design and implementation
# Expertise: REST principles, versioning, auth, error handling
# Risk level: B (MEDIUM)
# Security sensitive: Y
# Model: A (Sonnet)

# Step 2: MANDATORY vulnerability research
# Visit: https://nvd.nist.gov/
# Search: "REST API vulnerabilities 2022-2025"
# Document: Top 10 CVEs in SKILL.md § 5

# Step 3: Review security references
cat .dev-aid/skills/template-references/security-framework.md
cat .dev-aid/skills/template-references/owasp-2025-guide.md

# Step 4: Customize SKILL.md
# - Add § 0.2: Vulnerability Research results
# - Include OWASP A01 (Broken Access Control)
# - Include OWASP A02 (Security Misconfiguration)
# - Include OWASP A03 (Injection)
# - Add API-specific security patterns

# Step 5: Verify
wc -l .dev-aid/skills/expert/rest-api-expert/SKILL.md
bandit -r references/  # Security scan
pytest tests/ --cov
```

**Time**: 15-20 minutes

---

### Example 3: Creating a Security Skill (HIGH Risk)

```bash
# Step 1: Create skill
/dev-aid-build-skill

# Answers:
# Skill name: kubernetes-security-expert
# Domain: Kubernetes security hardening
# Expertise: RBAC, network policies, pod security, secrets
# Risk level: C (HIGH)
# Security sensitive: Y
# Model: B (Opus)

# Step 2: MANDATORY comprehensive security review
# 2a. Vulnerability Research (MANDATORY)
# - Search NVD: "Kubernetes vulnerabilities 2022-2025"
# - Search CVE: pod escape, privilege escalation
# - Document ALL critical CVEs in SKILL.md

# 2b. Review ALL security references (MANDATORY)
cat .dev-aid/skills/template-references/security-framework.md
cat .dev-aid/skills/template-references/owasp-2025-guide.md
cat .dev-aid/skills/template-references/threat-modeling.md
cat .dev-aid/skills/template-references/compliance-guide.md

# 2c. Create threat model (MANDATORY)
cp .dev-aid/skills/template-references/threat-modeling.md \
   .dev-aid/skills/expert/kubernetes-security-expert/references/threat-model.md

# Edit threat-model.md:
# - Assets: Cluster, nodes, pods, secrets, etcd
# - Threats: STRIDE analysis for each asset
# - Attack scenarios: Pod escape, RBAC bypass, network policy evasion
# - Security controls: Mitigations for each threat

# 2d. OWASP compliance (MANDATORY)
# - Review ALL 10 OWASP 2025 categories
# - Document K8s-specific mitigations for each
# - Add to references/security-examples.md

# 2e. Compliance (if applicable)
# - GDPR: Data protection in K8s
# - HIPAA: PHI storage requirements
# - PCI-DSS: Payment data handling

# Step 3: Customize SKILL.md
# - Complete § 0: Security-First Framework (ALL subsections)
# - Add K8s-specific security patterns
# - Include security controls matrix
# - Add compliance checklists

# Step 4: Create comprehensive references/
mkdir -p references
cp -r ../SKILL_TEMPLATE.md/references/ .
# Customize each reference file for Kubernetes

# Step 5: Verify (STRICT)
wc -l SKILL.md  # MUST be <500
wc -l references/*.md  # Can be unlimited
bandit -r . --severity-level high  # Must pass
trivy config .  # Must pass
pytest tests/ --cov --cov-fail-under=90  # Must be >90%
shellcheck references/*.sh  # Must pass
```

**Time**: 30-45 minutes (due to comprehensive security review)

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Exceeding 500-Line Limit

**Problem**: Main SKILL.md is 847 lines, Claude Code can't load it

**Solution**:
```bash
# Check line count
wc -l SKILL.md

# If >500, move content to references/
mv "detailed examples" references/advanced-patterns.md
mv "security examples" references/security-examples.md
mv "troubleshooting" references/troubleshooting.md
```

### ❌ Mistake 2: Skipping Vulnerability Research (MEDIUM/HIGH Risk)

**Problem**: Skill created without CVE research, missing critical vulnerabilities

**Solution**:
```bash
# MANDATORY for MEDIUM/HIGH risk
# 1. Search NVD database
open https://nvd.nist.gov/
# Search: "[your domain] vulnerabilities 2022-2025"

# 2. Document findings in SKILL.md
# Add top 5-10 CVEs with mitigations

# 3. Verify completion
grep -i "CVE-202" SKILL.md || echo "ERROR: No CVE research found!"
```

### ❌ Mistake 3: Not Using Progressive Disclosure

**Problem**: All content in main SKILL.md, file is too large

**Solution**:
```markdown
## Main SKILL.md (Keep concise)
Brief security summary with top 3 vulnerabilities

📚 **For complete vulnerability analysis**: See `references/security-examples.md`

## references/security-examples.md (Unlimited)
- Full CVE details
- Exploitation scenarios
- Complete mitigations
- Code examples
```

### ❌ Mistake 4: Forgetting Quality Gates

**Problem**: Code fails CI with linting errors

**Solution**:
```bash
# Run BEFORE committing
black .
isort .
flake8 . --max-line-length=120
mypy . --ignore-missing-imports
bandit -r .
shellcheck **/*.sh
pytest --cov --cov-fail-under=80
```

### ❌ Mistake 5: No skills-index.json Entry

**Problem**: Skill never auto-loads because it's not registered

**Solution**:
```bash
# MANDATORY: Add to .dev-aid/skills/registry/skills-index.json
{
  "my-skill": {
    "activation": {
      "primary_keywords": ["keyword1", "keyword2"],
      "secondary_keywords": ["keyword3", "keyword4"],
      "file_patterns": ["*.ext"],
      "technologies": ["tech1", "tech2"]
    }
  }
}

# Verify activation
cd .dev-aid/orchestration
./select-skills.sh "test query with keywords"
```

---

## Checklist Before Submission

### Pre-Submission Checklist (ALL Skills)

- [ ] **Line Count**: Main SKILL.md <500 lines (`wc -l SKILL.md`)
- [ ] **Frontmatter**: Complete (name, description, risk_level, version)
- [ ] **§ 0.1**: Risk assessment completed
- [ ] **§ 0.3**: Hallucination prevention checklist reviewed
- [ ] **Quality Gates**: All pass
  - [ ] `black .` - Code formatted
  - [ ] `isort .` - Imports sorted
  - [ ] `flake8 . --max-line-length=120` - No linting errors
  - [ ] `mypy . --ignore-missing-imports` - Type checking passes
  - [ ] `bandit -r .` - Security scan clean
  - [ ] `shellcheck **/*.sh` - Bash scripts pass (if applicable)
- [ ] **Tests**: All passing with >80% coverage
  - [ ] `pytest --cov --cov-fail-under=80`
- [ ] **Documentation**: Complete
  - [ ] Docstrings for all public functions
  - [ ] Examples of correct usage
  - [ ] Known limitations documented
- [ ] **skills-index.json**: Entry added and tested
- [ ] **Git**: Clean commit with conventional commits format

### Additional Checklist (MEDIUM Risk)

- [ ] **§ 0.2**: Vulnerability research completed
  - [ ] NVD database searched for CVEs (2022-2025)
  - [ ] Top 5-10 vulnerabilities documented
  - [ ] Mitigations included
- [ ] **OWASP**: Applicable categories reviewed
  - [ ] A01: Broken Access Control
  - [ ] A02: Security Misconfiguration
  - [ ] A03: Injection
  - [ ] (others as applicable)
- [ ] **References**: security-framework.md reviewed

### Additional Checklist (HIGH Risk)

- [ ] **§ 0.2**: COMPLETE vulnerability research protocol
  - [ ] NVD database comprehensive search
  - [ ] MITRE ATT&CK review
  - [ ] CWE analysis
  - [ ] ALL critical CVEs documented
- [ ] **OWASP**: ALL 10 categories reviewed and documented
- [ ] **Threat Model**: Created using STRIDE methodology
  - [ ] Assets identified
  - [ ] Threats analyzed
  - [ ] Attack scenarios documented
  - [ ] Security controls matrix complete
- [ ] **Compliance**: Reviewed (if applicable)
  - [ ] GDPR requirements
  - [ ] HIPAA requirements
  - [ ] PCI-DSS requirements
- [ ] **References**: ALL template references reviewed
  - [ ] security-framework.md
  - [ ] owasp-2025-guide.md
  - [ ] threat-modeling.md
  - [ ] compliance-guide.md
- [ ] **Security Review**: Completed by second person
- [ ] **Penetration Testing**: Patterns tested (if applicable)

---

## Quick Reference

### File Locations

```
.dev-aid/skills/
├── SKILL_TEMPLATE.md              # Main template (477 lines)
├── SKILL_QUICKSTART.md            # This guide
├── template-references/           # Detailed references
│   ├── security-framework.md      # Complete security protocol (2,021 lines)
│   ├── owasp-2025-guide.md        # OWASP Top 10 2025 (774 lines)
│   ├── threat-modeling.md         # STRIDE methodology (241 lines)
│   ├── compliance-guide.md        # GDPR/HIPAA/PCI-DSS (301 lines)
│   └── progressive-disclosure.md  # 500-line limit guidance (200 lines)
└── expert/
    └── your-skill/
        ├── SKILL.md               # <500 lines
        └── references/            # Unlimited lines
            ├── advanced-patterns.md
            ├── security-examples.md
            ├── threat-model.md
            └── ...
```

### Commands

```bash
# Create skill
/dev-aid-build-skill

# Quality gates
black . && isort . && flake8 . && mypy . && bandit -r .

# Test
pytest --cov --cov-fail-under=80

# Verify line count
wc -l SKILL.md  # Must be <500

# Test skill activation
cd .dev-aid/orchestration
./select-skills.sh "test query"

# Commit
git add . && git commit -m "feat: add my-skill"
```

### External Links

- [NVD Database](https://nvd.nist.gov/) - CVE vulnerability search
- [MITRE ATT&CK](https://attack.mitre.org/) - Attack patterns
- [OWASP Top 10 2025](https://owasp.org/Top10/) - Web application security
- [CWE](https://cwe.mitre.org/) - Common Weakness Enumeration

---

## Getting Help

**Question**: How do I know if my skill is LOW/MEDIUM/HIGH risk?

**Answer**: Use this guide:
- **LOW**: Documentation, UI/UX, design, testing, tutorials
- **MEDIUM**: APIs, data processing, application code, CLI tools
- **HIGH**: Security, infrastructure, auth, data storage, production systems

**Question**: My SKILL.md is 623 lines, what do I do?

**Answer**: Move content to `references/`:
```bash
# Move detailed content
mv "security examples section" references/security-examples.md
mv "troubleshooting section" references/troubleshooting.md
mv "advanced patterns section" references/advanced-patterns.md

# Add links in main SKILL.md
echo "📚 See references/security-examples.md" >> SKILL.md
```

**Question**: Do I need to create a threat model for a React component library?

**Answer**: No. React component library is LOW risk. Threat models are MANDATORY only for HIGH-risk skills (security, infrastructure, auth).

**Question**: Where do I find examples of existing skills?

**Answer**:
```bash
ls .dev-aid/skills/expert/
# Examples:
# - devsecops-expert (HIGH risk, complete security framework)
# - api-expert (MEDIUM risk, vulnerability research)
# - ui-ux-expert (LOW risk, standard template)
```

---

**Version**: 1.0.0
**Last Updated**: 2025-12-06
**Template Version**: SKILL_TEMPLATE.md v2.0.0

🤖 Generated with [Claude Code](https://claude.com/claude-code)
