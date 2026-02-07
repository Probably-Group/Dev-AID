"""
Built-in team definitions for common development workflows.

Each team composes agents from the AGENTS registry with role-specific
prompts and optional provider/model overrides.
"""

from typing import Dict

from ..core.team_models import AgentSlot, TeamDefinition

# ── PR Review Team ───────────────────────────────────────────────────

PR_REVIEW_TEAM = TeamDefinition(
    name="pr-review-team",
    description="Comprehensive PR review from security, quality, and test coverage perspectives",
    agents=[
        AgentSlot(
            name="security-reviewer",
            agent_def_name="pr-reviewer",
            role_prompt=(
                "You are the SECURITY reviewer on this team. Focus exclusively on:\n"
                "- Authentication and authorization flaws\n"
                "- Input validation and sanitization issues\n"
                "- Injection vulnerabilities (SQL, command, path traversal)\n"
                "- Secrets or credentials in code\n"
                "- Insecure cryptographic usage\n"
                "- OWASP Top 10 vulnerabilities\n\n"
                "Do NOT review code style, naming, or test coverage — other "
                "reviewers handle those."
            ),
        ),
        AgentSlot(
            name="quality-reviewer",
            agent_def_name="pr-reviewer",
            role_prompt=(
                "You are the CODE QUALITY reviewer on this team. Focus exclusively on:\n"
                "- Code readability and maintainability\n"
                "- Design patterns and architecture concerns\n"
                "- Error handling and edge cases\n"
                "- Performance issues (N+1 queries, unnecessary allocations)\n"
                "- Code duplication and abstraction opportunities\n"
                "- Naming conventions and documentation\n\n"
                "Do NOT review security vulnerabilities or test coverage — other "
                "reviewers handle those."
            ),
        ),
        AgentSlot(
            name="test-coverage-reviewer",
            agent_def_name="pr-reviewer",
            role_prompt=(
                "You are the TEST COVERAGE reviewer on this team. Focus exclusively on:\n"
                "- Missing test cases for new/changed code\n"
                "- Edge case coverage\n"
                "- Test quality (meaningful assertions, not just smoke tests)\n"
                "- Integration vs unit test balance\n"
                "- Mocking strategy appropriateness\n"
                "- Regression test suggestions\n\n"
                "Do NOT review security or code style — other reviewers handle those."
            ),
        ),
    ],
    workflow="parallel",
    max_budget_usd=2.0,
    aggregation_strategy="merge_sections",
    timeout_seconds=300,
)

# ── Security Audit Team ──────────────────────────────────────────────

SECURITY_AUDIT_TEAM = TeamDefinition(
    name="security-audit-team",
    description="Deep security audit with vulnerability, auth, and dependency analysis",
    agents=[
        AgentSlot(
            name="vulnerability-scanner",
            agent_def_name="pr-reviewer",
            role_prompt=(
                "You are a VULNERABILITY SCANNER. Systematically scan the codebase for:\n"
                "- Injection vulnerabilities (SQL, NoSQL, OS command, LDAP)\n"
                "- Cross-site scripting (XSS) and cross-site request forgery (CSRF)\n"
                "- Insecure deserialization\n"
                "- Server-side request forgery (SSRF)\n"
                "- Path traversal and file inclusion\n"
                "- Race conditions and TOCTOU bugs\n\n"
                "Report findings with severity (Critical/High/Medium/Low), "
                "affected file/line, and remediation steps."
            ),
        ),
        AgentSlot(
            name="auth-reviewer",
            agent_def_name="pr-reviewer",
            role_prompt=(
                "You are an AUTHENTICATION & AUTHORIZATION reviewer. Analyze:\n"
                "- Authentication mechanisms (password hashing, token management)\n"
                "- Authorization checks (RBAC, ABAC, missing checks)\n"
                "- Session management (fixation, hijacking, expiry)\n"
                "- OAuth/OIDC implementation correctness\n"
                "- API key and secret management\n"
                "- Privilege escalation vectors\n\n"
                "Report findings with severity and remediation steps."
            ),
        ),
        AgentSlot(
            name="dependency-auditor",
            agent_def_name="tech-debt-hunter",
            role_prompt=(
                "You are a DEPENDENCY AUDITOR. Analyze project dependencies for:\n"
                "- Known CVEs in direct and transitive dependencies\n"
                "- Outdated packages with available security patches\n"
                "- Packages with suspicious or abandoned maintenance\n"
                "- License compliance issues\n"
                "- Supply chain attack indicators\n\n"
                "Use the project's lock files and manifest to identify all dependencies."
            ),
        ),
    ],
    workflow="parallel",
    max_budget_usd=3.0,
    aggregation_strategy="merge_sections",
    timeout_seconds=600,
)

# ── Architect-Implement Team ─────────────────────────────────────────

ARCHITECT_IMPLEMENT_TEAM = TeamDefinition(
    name="architect-implement-team",
    description="Plan with a senior architect, implement, then review the result",
    agents=[
        AgentSlot(
            name="architect",
            agent_def_name="research",
            provider="anthropic",
            model="claude-opus-4-6",
            role_prompt=(
                "You are a SENIOR ARCHITECT. Your job is to:\n"
                "1. Analyze the codebase structure and patterns\n"
                "2. Design the implementation plan with specific files to create/modify\n"
                "3. Define interfaces and data models\n"
                "4. Identify risks and edge cases\n\n"
                "Output a structured implementation plan in markdown. "
                "Do NOT write any code — just the plan."
            ),
        ),
        AgentSlot(
            name="implementer",
            agent_def_name="test-generator",
            depends_on=["architect"],
            role_prompt=(
                "You are an IMPLEMENTER. You will receive an architect's plan "
                "in the team context. Follow it precisely:\n"
                "1. Read the plan from prior agent results\n"
                "2. Implement each file change as specified\n"
                "3. Follow existing code patterns and conventions\n"
                "4. Write clean, tested code\n\n"
                "Do NOT deviate from the plan without good reason."
            ),
        ),
        AgentSlot(
            name="reviewer",
            agent_def_name="pr-reviewer",
            depends_on=["implementer"],
            role_prompt=(
                "You are the FINAL REVIEWER. Check the implementation against "
                "the architect's plan:\n"
                "1. Verify all planned changes were implemented\n"
                "2. Check for bugs, edge cases, and security issues\n"
                "3. Verify code follows project conventions\n"
                "4. Confirm tests cover the new functionality\n\n"
                "Report any discrepancies between plan and implementation."
            ),
        ),
    ],
    workflow="dag",
    max_budget_usd=5.0,
    aggregation_strategy="concatenate",
    timeout_seconds=900,
)

# ── Issue Resolution Team ────────────────────────────────────────────

ISSUE_RESOLUTION_TEAM = TeamDefinition(
    name="issue-resolution-team",
    description="Investigate an issue, fix it, and add regression tests",
    agents=[
        AgentSlot(
            name="researcher",
            agent_def_name="research",
            role_prompt=(
                "You are the RESEARCHER. Your job is to:\n"
                "1. Reproduce or understand the reported issue\n"
                "2. Identify the root cause by reading relevant code\n"
                "3. Document the affected components and potential fix approach\n\n"
                "Output a root cause analysis with specific file/line references. "
                "Do NOT fix the code — just investigate."
            ),
        ),
        AgentSlot(
            name="fixer",
            agent_def_name="ci-fixer",
            depends_on=["researcher"],
            role_prompt=(
                "You are the FIXER. You will receive a root cause analysis "
                "from the researcher. Apply the fix:\n"
                "1. Read the researcher's analysis from prior results\n"
                "2. Make the minimal code change to fix the issue\n"
                "3. Ensure the fix doesn't introduce regressions\n\n"
                "Keep changes focused and minimal."
            ),
        ),
        AgentSlot(
            name="test-writer",
            agent_def_name="test-generator",
            depends_on=["fixer"],
            role_prompt=(
                "You are the TEST WRITER. After the fix is applied:\n"
                "1. Write regression tests that would have caught the bug\n"
                "2. Add edge case tests around the fixed area\n"
                "3. Verify existing tests still pass\n\n"
                "Focus on preventing this specific issue from recurring."
            ),
        ),
    ],
    workflow="dag",
    max_budget_usd=4.0,
    aggregation_strategy="concatenate",
    timeout_seconds=600,
)

# ── Registry ─────────────────────────────────────────────────────────

BUILTIN_TEAMS: Dict[str, TeamDefinition] = {
    "pr-review-team": PR_REVIEW_TEAM,
    "security-audit-team": SECURITY_AUDIT_TEAM,
    "architect-implement-team": ARCHITECT_IMPLEMENT_TEAM,
    "issue-resolution-team": ISSUE_RESOLUTION_TEAM,
}
