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

