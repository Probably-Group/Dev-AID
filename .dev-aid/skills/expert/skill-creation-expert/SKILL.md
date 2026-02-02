---
name: skill-creation-expert
version: 4.0.0
description: "Template for creating Claude Code skills with anti-hallucination protocols, CWE security patterns, and proper structure."
---

# Skill Creation Template

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE creating any skill:**
1. Run `/list-skills` to verify no duplicate/similar skill exists
2. Determine if Technical or Non-Technical domain
3. Research authoritative sources for the technology
4. Never invent CWE patterns - use known vulnerabilities

### 0.2 Risk Level: LOW

**Verification requirements:**
- Validate skill structure follows template
- Ensure Section 0.2 has proper CWE patterns (not generic links)
- Confirm NEVER/ALWAYS rules are actionable

---

## 1. How Skills Work

Skills are **instructions for Claude** loaded into context when invoked. Every section must answer: **"What should Claude do when generating code?"**

**NOT documentation** - Claude doesn't need explanations, it needs rules.

---

## 2. Required Skill Structure

Every skill MUST follow this structure:

```markdown
---
name: [technology]-expert
version: 1.0.0
description: "[15-25 word elevator pitch - visible in /list-skills]"
risk_level: [LOW|MEDIUM|HIGH|CRITICAL]
---

# [Technology] Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification
[Standard verification steps]

### 0.2 Security Patterns (NEVER violate)  ← TECHNICAL SKILLS ONLY
[Technology-specific CWE patterns - see Section 4]

### 0.3 Risk Level: [LEVEL]
[Verification requirements for this risk level]

---

## 1. Security Principles
[NEVER/ALWAYS rules with ❌ WRONG / ✅ CORRECT code]

## 2. Version Requirements
[Minimum safe versions to use]

## 3. Code Patterns
[WHEN X → use this exact template]

## 4. Anti-Patterns
[NEVER do X - with code examples]

## 5. Testing
[How to test in this technology]

## 6. Pre-Generation Checklist
[Final verification before generating]
```

---

## 3. Skill Categories

### Technical Skills (require Section 0.2 with CWE patterns)

| Category | Skills | Key CWEs |
|----------|--------|----------|
| **Backend/Python** | fastapi, python, celery | CWE-89, CWE-78, CWE-502 |
| **Frontend/JS** | javascript, typescript, vue3, nuxt4 | CWE-79, CWE-1321, CWE-94 |
| **Bash/Shell** | bash-expert | CWE-78, CWE-20, CWE-377 |
| **Rust** | rust, tauri | CWE-119, CWE-252, CWE-362 |
| **Database** | sqlite, sqlcipher, database-design | CWE-89, CWE-312, CWE-732 |
| **APIs** | api-expert, graphql, rest-api, websocket | CWE-285, CWE-918, CWE-352 |
| **DevOps/K8s** | cicd, argo, cilium, harbor, talos | CWE-798, CWE-829, CWE-306 |
| **Security** | encryption, appsec, sandboxing | CWE-327, CWE-287, CWE-269 |
| **AI/ML** | llm-integration, cloud-api | CWE-74 (prompt injection) |

### Non-Technical Skills (simpler Section 0.2)

- `design-systems`, `ui-ux-design`, `accessibility-wcag`
- `deep-research-expert`, `web-research-expert`
- `senior-architect`, `plan-review-expert`, `refactoring-expert`
- `prompt-engineering`, `prompt-engineering-expert`

---

## 4. Section 0.2: CWE Security Patterns

### For Technical Skills

**Section 0.2 MUST contain technology-specific NEVER/ALWAYS rules:**

```markdown
### 0.2 Security Patterns (NEVER violate)

**CWE-89: SQL Injection**
- NEVER: `f"SELECT * FROM users WHERE id = {user_id}"`
- ALWAYS: `cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))`

**CWE-78: Command Injection**
- NEVER: `os.system(user_input)` or `subprocess.run(cmd, shell=True)`
- ALWAYS: `subprocess.run([binary, arg1], shell=False)`

**CWE-79: XSS**
- NEVER: `element.innerHTML = userInput`
- ALWAYS: `element.textContent = userInput`
```

### For Non-Technical Skills

```markdown
### 0.2 Risk Level: [LEVEL]

**Verification requirements:**
- Cross-reference recommendations with industry standards
- Cite sources when making specific claims
- Acknowledge when best practices vary by context
```

---

## 5. Researching Security Patterns

### Hybrid Approach (Recommended)

**For well-known technologies** (Python, JS, Bash, Rust, SQL):
- Use established CWE patterns from training knowledge
- These are timeless vulnerability classes, not specific CVEs
- Focus on 3-5 most critical patterns per technology

**For niche technologies** (Kanidm, SurrealDB, Cilium, etc.):
- Web search for security advisories and CVEs
- Check: GitHub Security Advisories, OSV.dev, CISA KEV
- Look for documented attack patterns in official docs

### Research Checklist

1. **Search for CVEs**: `"[technology] CVE site:github.com/advisories"`
2. **Check official security docs**: `[technology] security best practices`
3. **Find injection patterns**: `"[technology] injection" OR "[technology] security vulnerability"`
4. **Look for OWASP mappings**: `OWASP [technology]`

### Common CWE Categories by Technology Type

| Tech Type | Primary CWEs |
|-----------|--------------|
| Web Backend | CWE-89 (SQLi), CWE-78 (Command), CWE-22 (Path Traversal) |
| Web Frontend | CWE-79 (XSS), CWE-1321 (Prototype Pollution), CWE-352 (CSRF) |
| Shell Scripts | CWE-78 (Injection), CWE-20 (Input Val), CWE-377 (Temp Files) |
| APIs | CWE-285 (Auth), CWE-918 (SSRF), CWE-400 (DoS) |
| Crypto | CWE-327 (Weak Algo), CWE-321 (Hardcoded Key), CWE-328 (Weak KDF) |
| Identity/Auth | CWE-287 (Auth), CWE-522 (Weak Creds), CWE-307 (Brute Force) |
| Containers/K8s | CWE-250 (Privilege), CWE-306 (Missing Auth), CWE-829 (Supply Chain) |

---

## 6. Creating a New Skill - Workflow

### Step 1: Pre-Creation Research

```bash
# Check for duplicates
/list-skills

# Determine category
Is this Technical or Non-Technical?
```

### Step 2: Create Directory

```bash
mkdir -p ~/.claude/skills/[skill-name]
```

### Step 3: Write SKILL.md

1. **Frontmatter**: name, version, description (15-25 words), risk_level
2. **Section 0**: Anti-Hallucination Protocol
   - 0.1: Mandatory Verification
   - 0.2: Security Patterns (technical) OR Risk Level (non-technical)
   - 0.3: Risk Level and requirements
3. **Sections 1-6**: Follow template structure

### Step 4: Research Security Patterns (Technical Skills)

```markdown
For [technology]:
1. What are the common injection vectors?
2. What authentication/authorization issues exist?
3. What data exposure risks exist?
4. What resource exhaustion attacks are possible?
```

### Step 5: Write CWE Patterns

For each vulnerability found:

```markdown
**CWE-XXX: [Vulnerability Name]**
- NEVER: `[bad code pattern]`
- ALWAYS: `[good code pattern]`
```

### Step 6: Test the Skill

```bash
# Invoke the skill
/[skill-name]

# Verify it loads and patterns are actionable
```

---

## 7. Anti-Patterns in Skill Writing

**NEVER** write generic research links:
```markdown
# ❌ WRONG - not actionable
### 0.2 Vulnerability Research
Check these sources: GHSA, OSV, CISA KEV

# ✅ CORRECT - actionable patterns
### 0.2 Security Patterns (NEVER violate)
**CWE-89: SQL Injection**
- NEVER: `db.execute(f"SELECT * FROM users WHERE id = {id}")`
- ALWAYS: `db.execute("SELECT * FROM users WHERE id = ?", [id])`
```

**NEVER** write passive documentation:
```markdown
# ❌ WRONG - describes, doesn't instruct
SQL injection is a vulnerability where attackers can execute
malicious SQL code. It's important to use parameterized queries.

# ✅ CORRECT - actionable rule
**NEVER** use f-strings in SQL (CWE-89):
```python
# ❌ WRONG
query = f"SELECT * FROM users WHERE id = {user_id}"

# ✅ CORRECT
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```
```

**NEVER** forget the WHY (CWE reference):
```markdown
# ❌ WRONG - no justification
Don't use eval().

# ✅ CORRECT - references vulnerability
**NEVER** use `eval()` with external data (CWE-94):
```

---

## 8. Checklist for New Skills

### Structure
- [ ] Has frontmatter with name, version, description, risk_level
- [ ] Description is 15-25 words (visible in /list-skills)
- [ ] Section 0 (Anti-Hallucination) is present
- [ ] Section 0.2 has CWE patterns (technical) or Risk Level (non-technical)

### Content Quality
- [ ] All rules are WHEN/NEVER/ALWAYS format
- [ ] All bad patterns have ❌ WRONG example
- [ ] All good patterns have ✅ CORRECT example
- [ ] CWE references on security patterns
- [ ] No passive documentation, only actionable rules

### Security (Technical Skills)
- [ ] 3-5 CWE patterns in Section 0.2
- [ ] Patterns are technology-specific (not generic)
- [ ] Patterns researched from CVEs/advisories (niche tech)
- [ ] Patterns from training knowledge (well-known tech)

### Final
- [ ] Skill invocable via `/[skill-name]`
- [ ] No similar/duplicate skill exists
- [ ] Follows 6-section structure after Section 0
