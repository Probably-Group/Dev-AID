---
name: aid-help
description: "Show all available Dev-AID commands — agents, router, quality, security, and more"
category: agents
author: Dev-AID Team (https://probably.group)
version: 1.0.0
---

# Dev-AID Command Reference

Print the following reference guide for the user. Do NOT execute any commands — just display this information.

---

**All commands have short `aid-*` aliases.** Type `aid-` in autocomplete to browse everything.

## 🤖 Agent Commands

| Short Alias | Full Command | Description |
|------------|-------------|-------------|
| `aid-pr` | `dev-aid-agent-pr-review` | Review PR for security, quality, architecture |
| `aid-test` | `dev-aid-agent-test-gen` | Generate tests for untested code |
| `aid-debt` | `dev-aid-agent-tech-debt` | Scan for code smells and tech debt |
| `aid-ci` | `dev-aid-agent-ci-fix` | Diagnose and fix CI failures |
| `aid-conflict` | `dev-aid-agent-conflict-resolve` | Resolve merge conflicts intelligently |
| `aid-research` | `dev-aid-agent-research` | Deep research on technical topics |
| `aid-onboard` | `dev-aid-agent-onboard` | Generate codebase onboarding guide |
| `aid-docs` | `dev-aid-agent-doc-audit` | Audit documentation for drift and gaps |

**CLI (for scripts/CI):** `dev-aid-agent <agent> [options] --json --dry-run`

## 🔀 Router Commands

| Short Alias | Full Command | Description |
|------------|-------------|-------------|
| `aid-challenger` | `dev-aid-router-challenger` | Two-AI review: Claude generates, Gemini reviews |
| `aid-challenger-rag` | `dev-aid-router-challenger-rag` | Challenger mode + local RAG search |
| `aid-ensemble` | `dev-aid-router-ensemble` | Smart routing to optimal AI per task |
| `aid-router-status` | `dev-aid-router-status` | View routing stats and cost breakdown |

## 🔒 Security Commands

| Short Alias | Full Command | Description |
|------------|-------------|-------------|
| `aid-audit` | `dev-aid-audit` | Comprehensive security audit (Gitleaks, Trivy, Opengrep) |
| `aid-vulnscan` | `dev-aid-vulnerability-scan` | Deep CVE scanning for dependencies |

## ✅ Quality Commands

| Short Alias | Full Command | Description |
|------------|-------------|-------------|
| `aid-health` | `dev-aid-code-health` | Code quality assessment and metrics |
| `aid-debt-report` | `dev-aid-debt-analysis` | Tech debt identification and prioritization |
| `aid-review` | `dev-aid-review-staged` | Pre-commit review (security, quality, tests) |

## 🚀 Productivity Commands

| Short Alias | Full Command | Description |
|------------|-------------|-------------|
| `aid-commit` | `dev-aid-commit-plan` | Analyze changes and propose atomic commits |
| `aid-api` | `dev-aid-api-contract` | Generate OpenAPI specs and TypeScript clients |

## ⚙️ Setup & Maintenance Commands

| Short Alias | Full Command | Description |
|------------|-------------|-------------|
| `aid-analyze` | `dev-aid-analyze` | Analyze codebase and generate adaptation plan |
| `aid-status` | `dev-aid-status` | Show Dev-AID configuration and setup status |
| `aid-config` | `dev-aid-config-core-skills` | Configure auto-loaded core skills |
| `aid-skill` | `dev-aid-build-skill` | Generate custom expert skill |
| `aid-models` | `dev-aid-models-update` | Update AI model registry |
| `aid-deploy` | `dev-aid-deploy-validate` | Pre-deployment validation |

## 📦 Utility Scripts

```bash
.dev-aid/scripts/generate-ci.sh          # Auto-generate CI/CD workflows
.dev-aid/scripts/map-architecture.sh      # Generate architecture diagrams
.dev-aid/scripts/fabricate-data.sh        # Generate mock test data
.dev-aid/scripts/sync-docs.sh            # Detect documentation drift
.dev-aid/scripts/dev-aid-guide.sh        # Interactive feature discovery
.dev-aid/scripts/draft-pr.sh             # Generate PR descriptions
.dev-aid/scripts/onboard.sh              # Onboard new developers
.dev-aid/scripts/setup-rag.sh            # Set up local semantic search
.dev-aid/scripts/setup-local-llm.sh      # Set up local LLM
```

## 📖 More Information

- **Commands reference:** `.dev-aid/docs/COMMANDS-REFERENCE.md`
- **Agent framework:** `.dev-aid/docs/Dev-AID-AGENTS.md`
- **Full README:** `README.md`

---

**Tip:** Type `aid-` to see all short aliases in autocomplete.
