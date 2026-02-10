# Performance & Quality Guidelines for Expert Skills

> **Purpose**: Shared reference for all expert skills. Link here instead of inlining these guidelines in each SKILL.md.

---

## Anti-Laziness Principles

1. **Take the time to be thorough** — Never skip steps to save tokens. A correct, complete answer at 2000 tokens beats an incomplete one at 500.
2. **Verify all code examples** — Every code snippet must compile/run. If you're unsure, say so rather than guessing.
3. **Never skip security checks** — Even for "simple" tasks. The simple ones are where vulnerabilities hide.
4. **Read before writing** — Always read the existing code/config before proposing changes. Understand the context.
5. **Complete the loop** — If you start a multi-step process, finish it. Don't leave partial implementations.

## Per-Risk-Level Verification

### LOW Risk (Documentation, UI, Design)
- Verify markdown renders correctly
- Check all links are valid
- Confirm examples match current API versions
- Review for accessibility (alt text, heading hierarchy)

### MEDIUM Risk (Application Code, APIs)
- All code examples must include error handling
- Validate against OWASP Top 10 for relevant categories
- Check for input validation on all external inputs
- Verify dependency versions are current and pinned
- Test edge cases: empty input, null, unicode, max length

### HIGH/CRITICAL Risk (Security, Infrastructure, Auth)
- Full threat model review before implementation
- Verify against known CVEs (NVD database)
- Defense-in-depth: multiple layers of validation
- Audit logging for all security-relevant operations
- Test for privilege escalation, injection, and traversal
- Verify secrets handling (no logging, no error messages)

## Chunking Guidance for Large Outputs

When generating large outputs (>100 lines):
1. **Plan first** — Outline the structure before writing
2. **Generate in sections** — Complete one logical section at a time
3. **Verify between sections** — Check consistency before continuing
4. **Maintain context** — Reference earlier sections to ensure coherence

## Output Quality Checklist

Before finalizing any output:
- [ ] All code examples are syntactically correct
- [ ] Version numbers are verified (not assumed)
- [ ] Security recommendations match current best practices
- [ ] No hallucinated APIs, methods, or configuration options
- [ ] Error handling is present where needed
- [ ] Edge cases are addressed or acknowledged
- [ ] References to external docs use real, verifiable URLs

---

**Version**: 1.0.0
