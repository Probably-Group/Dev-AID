---
name: aid-router-challenger
description: Execute with Challenger mode - Claude generates, Gemini reviews for security issues
tags: [routing, multi-ai, security, review]
---

# 🔍 Challenger Mode Execution

Execute your request with **Challenger mode**: Claude (primary) generates the solution, then Gemini (challenger) reviews it for security issues, logic errors, and improvements.

## 📋 How It Works

```
1. Claude generates implementation
   └─ Uses devsecops-expert skill
   └─ Follows security best practices
   └─ Implements your feature

2. Gemini reviews Claude's work
   └─ Scans for OWASP Top 10 vulnerabilities
   └─ Checks edge cases and logic errors
   └─ Identifies performance issues
   └─ Rates severity (LOW/MEDIUM/HIGH/CRITICAL)

3. If issues found → Claude refines
   └─ Addresses Gemini's feedback
   └─ Provides improved implementation

4. You see both perspectives
   ├─ Original implementation
   ├─ Security critique
   └─ Improved version (if needed)
```

## 🎯 Usage

**Basic Usage:**
```
/dev-aid-router-challenger "Implement OAuth2 authentication with JWT tokens"
```

**With Specific Context:**
```
/dev-aid-router-challenger "Add password reset functionality" --context "Using existing auth system in src/auth/"
```

**For Code Review:**
```
/dev-aid-router-challenger "Review the authentication changes I just made"
```

## 🚀 Implementation

### Step 1: Understand the Request

Extract the user's request from the command:
- If provided as argument: Use that directly
- If no argument: Ask user to provide the request

### Step 2: Gather Context

Collect relevant context for routing:
```python
context = {
    "memory_bank": {
        "security": read_file(".dev-aid/memory-bank/security.md"),
        "patterns": read_file(".dev-aid/memory-bank/patterns.md"),
        "decisions": read_file(".dev-aid/memory-bank/decisions.md")
    },
    "active_skills": ["devsecops-expert", "owasp-guardian"],
    "files_edited": get_recent_files_edited(),
    "git_diff": get_current_git_diff()
}
```

### Step 3: Primary Generation (Claude)

Execute the user's request with full Dev-AID context:

**Prompt for Claude (Primary):**
```
You are implementing a security-critical feature.

**Context from Memory Bank:**
{security.md content}
{patterns.md content}
{decisions.md content}

**Active Skills:**
- devsecops-expert: Follow OWASP Top 10 best practices
- owasp-guardian: Security-first implementation

**User Request:**
{user_request}

**Requirements:**
1. Implement the feature following TDD
2. Apply security best practices
3. Handle edge cases
4. Include error handling
5. Add appropriate logging

Provide complete, production-ready implementation.
```

### Step 4: Challenger Review (Gemini)

Send Claude's output to Gemini for security review:

**Prompt for Gemini (Challenger):**
```
You are a critical security reviewer. Analyze this implementation for vulnerabilities.

**Original Request:**
{user_request}

**Implementation to Review:**
{claude_implementation}

**Review Instructions:**
Analyze the code for:

1. **OWASP Top 10 Vulnerabilities:**
   - Injection flaws (SQL, XSS, Command injection)
   - Broken authentication
   - Sensitive data exposure
   - XML external entities (XXE)
   - Broken access control
   - Security misconfiguration
   - Cross-site scripting (XSS)
   - Insecure deserialization
   - Using components with known vulnerabilities
   - Insufficient logging & monitoring

2. **Logic Errors:**
   - Race conditions
   - Off-by-one errors
   - Null pointer exceptions
   - Edge cases not handled

3. **Performance Issues:**
   - N+1 queries
   - Inefficient algorithms
   - Memory leaks

4. **Best Practice Violations:**
   - Missing input validation
   - Lack of rate limiting
   - Insufficient error handling
   - Poor secret management

**Output Format:**
```
ISSUES FOUND: <number>
SEVERITY: <LOW|MEDIUM|HIGH|CRITICAL>

DETAILED CRITIQUE:
1. [Issue description]
   Location: [file:line or code snippet]
   Risk: [security/performance/logic]
   Impact: [what could go wrong]

2. [Next issue...]

RECOMMENDATIONS:
- [Specific fix for issue 1]
- [Specific fix for issue 2]
...

POSITIVE ASPECTS:
- [What was done well]
```
```

### Step 5: Parse Review Results

Extract structured data from Gemini's review:
```python
import re

def parse_review(review_text):
    # Extract issues count
    issues_match = re.search(r'ISSUES FOUND:\s*(\d+)', review_text)
    issues_count = int(issues_match.group(1)) if issues_match else 0

    # Extract severity
    severity_match = re.search(
        r'SEVERITY:\s*(LOW|MEDIUM|HIGH|CRITICAL)',
        review_text,
        re.IGNORECASE
    )
    severity = severity_match.group(1).upper() if severity_match else "UNKNOWN"

    # Extract detailed critique
    critique_match = re.search(
        r'DETAILED CRITIQUE:\s*(.+?)(?=RECOMMENDATIONS:)',
        review_text,
        re.DOTALL
    )
    critique = critique_match.group(1).strip() if critique_match else ""

    # Extract recommendations
    rec_match = re.search(
        r'RECOMMENDATIONS:\s*(.+?)(?=POSITIVE ASPECTS:|$)',
        review_text,
        re.DOTALL
    )
    recommendations = rec_match.group(1).strip() if rec_match else ""

    return {
        "issues_count": issues_count,
        "severity": severity,
        "critique": critique,
        "recommendations": recommendations
    }
```

### Step 6: Refinement (If Needed)

If severity is HIGH or CRITICAL, ask Claude to refine:

**Prompt for Claude (Refinement):**
```
Based on the security review feedback, improve your implementation.

**Original Request:**
{user_request}

**Your Previous Implementation:**
{claude_implementation}

**Security Review Feedback:**
{gemini_review}

**Instructions:**
Address ALL issues identified in the review:
1. Fix security vulnerabilities
2. Handle edge cases mentioned
3. Improve performance where noted
4. Apply recommended best practices

Provide the complete improved implementation with explanations of what you fixed.
```

### Step 7: Format Output for User

Present results in clear, actionable format:

```markdown
# 🎯 Challenger Mode Results

## Primary Implementation (Claude Sonnet 4.5)

{claude_implementation}

**Metrics:**
- Cost: ${cost:.4f}
- Tokens: {input_tokens}→{output_tokens}
- Time: {duration}s

---

## 🔍 Challenger Review (Gemini 2.0 Flash)

**Issues Found:** {issues_count}
**Severity:** {severity}

### Detailed Critique

{detailed_critique}

### Recommendations

{recommendations}

**Review Cost:** ${review_cost:.4f}

---

{if issues_found and severity in ["HIGH", "CRITICAL"]}
## ✨ Improved Implementation (Claude Sonnet 4.5)

{improved_implementation}

**What Was Fixed:**
{explanation_of_fixes}

**Additional Cost:** ${refinement_cost:.4f}
{endif}

---

## 💰 Total Cost

- Primary: ${primary_cost:.4f}
- Review: ${review_cost:.4f}
{if refined}
- Refinement: ${refinement_cost:.4f}
{endif}
**Total: ${total_cost:.4f}**

---

## 🎓 Takeaways

{if no issues}
✅ **Excellent work!** No security issues found. The implementation follows best practices.
{elif severity == "LOW"}
✅ **Good implementation** with minor suggestions for improvement.
{elif severity == "MEDIUM"}
⚠️ **Review recommended.** Some issues should be addressed before production.
{elif severity in ["HIGH", "CRITICAL"]}
🚨 **Action required!** Critical issues found. Use the improved implementation above.
{endif}
```

## 🔧 Configuration

Challenger mode can be configured in `.dev-aid/config/routing.json`:

```json
{
  "challenger": {
    "enabled": true,
    "primary_model": "claude-sonnet",
    "challenger_model": "gemini-flash",
    "auto_refine_on": ["HIGH", "CRITICAL"],
    "review_triggers": [
      "auth",
      "authentication",
      "password",
      "crypto",
      "encryption",
      "token",
      "session",
      "oauth",
      "jwt",
      "security"
    ]
  }
}
```

## 📊 When to Use Challenger Mode

**Perfect for:**
- ✅ Authentication & authorization systems
- ✅ Payment processing
- ✅ Cryptographic implementations
- ✅ API security
- ✅ Data validation & sanitization
- ✅ Session management
- ✅ Any security-critical code

**Not necessary for:**
- ❌ UI components (no security risk)
- ❌ Documentation
- ❌ Configuration files
- ❌ Simple CRUD operations (unless handling sensitive data)

## 🎯 Example Session

```
User: /dev-aid-router-challenger "Implement password reset with email verification"

[Claude generates implementation]
✅ Generated: Password reset flow with email verification
   - Email validation
   - Token generation with expiry
   - Secure password hashing
   Cost: $0.045

[Gemini reviews]
🔍 Found 2 issues (MEDIUM severity):
   1. Token doesn't expire - could be reused indefinitely
   2. No rate limiting - vulnerable to abuse

[Claude refines]
✨ Improved implementation:
   - Added 15-minute token expiration
   - Implemented rate limiting (3 attempts/hour)
   Additional Cost: $0.038

💰 Total: $0.083

Result: Production-ready password reset with security validated by two AIs!
```

## 🚨 Error Handling

If challenger review fails:
```
⚠️ Challenger review failed (Gemini API error)
Falling back to primary implementation only.
Recommendation: Run /dev-aid-audit manually to verify security.
```

## 📝 Logging

All challenger executions are logged to `.dev-aid/logs/routing.log`:
```
2025-11-27 14:23:15 [CHALLENGER] Request: "Implement OAuth2 authentication"
2025-11-27 14:23:15 [PRIMARY] Model: claude-sonnet | Cost: $0.045
2025-11-27 14:23:42 [REVIEW] Model: gemini-flash | Issues: 2 | Severity: MEDIUM
2025-11-27 14:24:10 [REFINE] Model: claude-sonnet | Cost: $0.038
2025-11-27 14:24:10 [TOTAL] Cost: $0.083 | Time: 55s
```

---

**Now execute the challenger workflow above!**

1. Parse user's request
2. Gather context (memory bank, active skills, git diff)
3. Execute primary generation with Claude
4. Execute challenger review with Gemini
5. Refine if needed
6. Format and present results

Begin implementation now.
