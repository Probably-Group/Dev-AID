---
name: skill-creation-expert
version: 5.0.0
description: "Creating Claude Code skills with anti-hallucination protocols, CWE security patterns, and SKILL.md structure. Use when building new skills, writing SKILL.md files, or structuring skill templates. Do NOT use for general documentation."
token_budget: 2000
---

# Skill Creation Template

## 0. Pre-Creation

Before creating any skill:
1. Run `/list-skills` to verify no duplicate/similar skill exists
2. Determine if Technical or Non-Technical domain
3. Research authoritative sources for the technology
4. Never invent CWE patterns - use known vulnerabilities

---

## 1. How Skills Work

Skills are **instructions for Claude** loaded into context when invoked. Every section must answer: **"What should Claude do when generating code?"**

Not documentation — Claude doesn't need explanations, it needs rules.

---

## 2. Required Skill Structure

Every skill follows this structure. Section 0.1/0.3 are handled by the shared preamble in `skill_loader.py` — do not include them in SKILL.md.

```markdown
---
name: [technology]-expert
version: 1.0.0
description: "[15-25 word elevator pitch]"
risk_level: [LOW|MEDIUM|HIGH|CRITICAL]
token_budget: [estimated tokens, rounded to 500]
---

# [Technology] Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.2 Security Patterns (security rules)  <- TECHNICAL SKILLS ONLY
[Technology-specific CWE patterns - see Section 4]

---

## 1. Security Principles
[Principle statements with short CORRECT code examples]

## 2. Version Requirements
[Minimum safe versions]

## 3. Code Patterns
[WHEN X -> use this pattern. Max 3 examples.]

## 4. Anti-Patterns
[Short bullet list of what not to do]

## 5. Testing
[Brief testing guidance, not full test implementations]

## 6. Pre-Generation Checklist
[Top 5 domain-specific items only]
```

### Content Size Targets

- Expert skills: **300-500 lines** (not 600+)
- Section 3: Max **3 code pattern examples** (move extras to `references/`)
- Section 6: Max **5 checklist items** (domain-specific only)
- No generic advice LLMs already know (basic OWASP prose, obvious wrong patterns)

---

## 3. Section 0.2: CWE Security Patterns

### For Technical Skills

Section 0.2 contains technology-specific Do not/Instead rules:

```markdown
### 0.2 Security Patterns (security rules)

**CWE-89: SQL Injection**
- Do not: `f"SELECT * FROM users WHERE id = {user_id}"`
- Instead: `cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))`

**CWE-78: Command Injection**
- Do not: `os.system(user_input)` or `subprocess.run(cmd, shell=True)`
- Instead: `subprocess.run([binary, arg1], shell=False)`
```

### For Non-Technical Skills

Omit Section 0.2 entirely — the shared preamble handles verification.

### Common CWE Categories

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

## 4. Content Trimming Guide

### What to include (LLMs won't do this reliably without instruction)

- **Niche CVE patterns** — version-specific vulnerabilities not reliably in training data
- **Version-specific API patterns** — e.g., Pydantic v2 `field_validator` vs v1 `validator`
- **Framework-specific gotchas** — e.g., Celery `accept_content=['pickle']` footgun
- **CORRECT code examples** — keep short, trim verbose inline comments
- **Version requirements** — prevents recommending outdated versions

### What to omit (LLMs already know this)

- Generic security prose ("SQL injection is a vulnerability where...")
- Obvious WRONG patterns every LLM avoids (`hashlib.md5(password)`, `os.system(f"ping {host}")`)
- Full implementation classes (move to `references/` subdirectory)
- Full pytest test classes (describe what to test in bullet points)
- Generic checklist items ("secrets from environment", "debug disabled")
- Passive documentation that describes rather than instructs

### Where removed code goes

Large code examples belong in `references/` subdirectory, not system prompts:

```
.dev-aid/skills/expert/<skill-name>/
├── SKILL.md          # Trimmed (instructions only, 300-500 lines)
└── references/       # Full code examples for humans/APO
```

---

## 5. Anti-Patterns in Skill Writing

Do not write generic research links:
```markdown
# ❌ WRONG - not actionable
### 0.2 Vulnerability Research
Check these sources: GHSA, OSV, CISA KEV

# ✅ CORRECT - actionable patterns
### 0.2 Security Patterns (security rules)
**CWE-89: SQL Injection**
- Do not: `db.execute(f"SELECT * FROM users WHERE id = {id}")`
- Instead: `db.execute("SELECT * FROM users WHERE id = ?", [id])`
```

Do not write passive documentation:
```markdown
# ❌ WRONG - describes, doesn't instruct
SQL injection is a vulnerability where attackers can execute
malicious SQL code. It's important to use parameterized queries.

# ✅ CORRECT - actionable rule
Do not use f-strings in SQL (CWE-89):
- WRONG: `query = f"SELECT * FROM users WHERE id = {user_id}"`
- CORRECT: `cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))`
```

---

## 6. Checklist for New Skills

- [ ] Frontmatter: name, version, description (15-25 words), risk_level, token_budget
- [ ] Section 0.2 has CWE patterns (technical) or is omitted (non-technical)
- [ ] No Section 0.1/0.3 (handled by shared preamble)
- [ ] All rules use WHEN/Do not/Instead format with code examples
- [ ] Skill is 300-500 lines (not 600+)
- [ ] Section 3 has max 3 code examples (extras in `references/`)
- [ ] Section 6 has max 5 domain-specific checklist items
- [ ] No passive documentation, only actionable rules
- [ ] No generic advice LLMs already know
