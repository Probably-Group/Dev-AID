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
