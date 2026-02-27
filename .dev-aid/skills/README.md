# Dev-AID Skills System

**5 core skills** for automated checking + **74 expert skills** for domain expertise + **7 process skills** for workflow enforcement, all following the **two-tier template v2.0.0** with comprehensive quality assurance and progressive disclosure.

## 🔄 Core vs Expert vs Process Skills

### Core Skills (5 available, 2 enabled by default)
**Purpose**: Automated tool execution on file save
**Loading**: Always loaded at session start (configurable)
**Token Cost**: ~250 tokens each

**What they do:**
- Actually RUN tools automatically (tests, linters, type checkers)
- Provide real-time feedback on file save
- Block or warn about issues immediately

**Available:**
- ✅ `code-reviewer` - Real-time code quality suggestions (enabled by default)
- ✅ `secret-scanner` - Prevent credential leaks (enabled by default)
- ⏸️ `test-runner` - Auto-run relevant tests (disabled by default)
- ⏸️ `linter` - Auto-lint code (disabled by default)
- ⏸️ `type-checker` - Auto-check types (disabled by default)

**Configuration**: Run `/dev-aid-config-core-skills` to enable/disable

### Expert Skills (74 available)
**Purpose**: Domain-specific knowledge and guidance
**Loading**: Context-aware (auto-loads based on files/keywords)
**Token Cost**: ~200-500 tokens each (max 2-3 loaded per prompt)

**What they do:**
- Provide best practices, patterns, and architectural guidance
- Include checklists (e.g., "Run npm test")
- Give advice on HOW to write code correctly
- Do NOT execute tools automatically

**Example**: `typescript-expert` tells you "Use strict types", but doesn't run `tsc`

### Process Skills (7 available) 🆕
**Purpose**: Behavioral protocols that enforce disciplined workflows
**Loading**: Auto-triggers on specific events/keywords (configurable)
**Token Cost**: ~300-450 tokens each

**What they do:**
- Enforce workflow discipline (TDD, verification, systematic debugging)
- Block actions until protocols are followed (when strict)
- Integrate with Dev-AID infrastructure (router, local search, security tools)

**Available:**
- ✅ `verification-gate` - No completion claims without evidence (strict by default)
- ⚠️ `tdd-protocol` - Enforce RED-GREEN-REFACTOR cycle
- ⚠️ `systematic-debugging` - Root cause first, fix second
- ⏸️ `isolated-development` - Git worktree per feature/issue
- ⚠️ `design-first` - Think before coding
- ⚠️ `staged-review` - Two-stage review (spec → quality)
- ⚠️ `plan-execution` - Batch execution with checkpoints

**Legend**: ✅ = strict, ⚠️ = warning, ⏸️ = off

**Configuration**: Edit `.dev-aid/config/process-skills.json` or use `/dev-aid-config-process-skills`

### Key Difference
| | Core Skills | Expert Skills | Process Skills |
|---|---|---|---|
| **Role** | Automated checking | Knowledge & guidance | Workflow enforcement |
| **Execution** | Runs tools (tsc, eslint) | Provides advice only | Enforces protocols |
| **Loading** | Always at start | Context-aware | Event-triggered |
| **Example** | "❌ Type error at line 45" | "Use strict types" | "Show test evidence before claiming done" |

## 📁 Directory Structure

```
.dev-aid/skills/
├── README.md                    # This file
├── SKILL_QUICKSTART.md          # Quick-start guide for creating new skills
├── SKILL_TEMPLATE.md            # Main template (<500 lines, Claude Code compatible)
├── template-references/         # Extended template documentation
│   ├── security-framework.md    # Complete security protocol (2,021 lines)
│   ├── owasp-2025-guide.md      # OWASP Top 10 2025 guidance (774 lines)
│   ├── threat-modeling.md       # STRIDE methodology (241 lines)
│   ├── compliance-guide.md      # GDPR/HIPAA/PCI-DSS (301 lines)
│   └── progressive-disclosure.md # 500-line limit guidance (200 lines)
├── core/                        # Core system skills (5 available)
│   ├── code-reviewer/           # Enabled by default
│   ├── secret-scanner/          # Enabled by default
│   ├── test-runner/             # Disabled by default (configurable)
│   ├── linter/                  # Disabled by default (configurable)
│   └── type-checker/            # Disabled by default (configurable)
├── expert/                      # Expert domain skills (74)
│   ├── [skill-name]/
│   │   ├── SKILL.md            # Main skill file (<500 lines)
│   │   └── references/         # Extended content (optional)
│   │       ├── implementation-workflow-tdd.md
│   │       ├── implementation-patterns.md
│   │       ├── performance-patterns.md
│   │       └── ...
├── process/                     # Process workflow skills (7) 🆕
│   ├── README.md               # Process skills overview
│   ├── verification-gate/      # No completion claims without evidence
│   ├── tdd-protocol/           # RED-GREEN-REFACTOR enforcement
│   ├── systematic-debugging/   # Root cause investigation
│   ├── isolated-development/   # Git worktree per feature
│   ├── design-first/           # Think before coding
│   ├── staged-review/          # Two-stage code review
│   └── plan-execution/         # Batch execution with checkpoints
└── registry/
    └── skills-index.json        # Skill metadata and activation triggers
```

## 🎯 Skill Template v2.0.0

All skills follow a unified two-tier template structure:

### Main SKILL.md (<500 lines)

**Required Sections:**
- § 0: Security-First Framework & Anti-Hallucination Protocol ⭐ **FULLY ENRICHED**
  - 0.1: Quick Risk Assessment (LOW/MEDIUM/HIGH) - **100% complete (74/74 skills)**
  - 0.2: Vulnerability Research Protocol (MEDIUM/HIGH only) - **100% complete (57/57 MEDIUM/HIGH skills)**
  - 0.3: Hallucination Prevention Checklist - **100% complete (74/74 skills)**
  - 0.4: Progressive Disclosure (500-line limit guidance)
- § 1: Overview
- § 2: Core Responsibilities
- § 3: Implementation Workflow (TDD)
- § 4: Quality Assurance Checklist ⭐ **NEW**
  - 4.1: Pre-Implementation Setup
  - 4.2: Dependency Management
  - 4.3: Code Quality Gates
  - 4.4: Security Validation
  - 4.5: Test Coverage Requirements
  - 4.6: Documentation Requirements
- § 5: Common Pitfalls to Avoid
- § 6-8: Domain-specific sections
- § 9: References

### references/ Directory (Extended Content)

**Optional but Recommended:**
- Detailed implementation examples
- Advanced patterns and workflows
- Performance optimization guides
- Security deep-dives
- Troubleshooting guides

## 📊 Current Skills Inventory

### Core Skills (5 available, 2 enabled by default)

**Enabled by default:**
- `code-reviewer` (~250 tokens) - Real-time code quality checks
- `secret-scanner` (~250 tokens) - Prevent credential leaks

**Available (opt-in):**
- `test-runner` (~250 tokens) - Auto-run tests on file save
- `linter` (~250 tokens) - Auto-lint code on file save
- `type-checker` (~250 tokens) - Auto-check types on file save

**Total token cost:**
- Minimal (default): 500 tokens (0.25% of 200k budget)
- Maximum (all enabled): 1,250 tokens (0.625% of 200k budget)

**Configure**: Run `/dev-aid-config-core-skills` to choose which core skills to enable

### Expert Skills (74)

**Development & Languages (14):**
- api-expert, async-expert, bash-expert
- fastapi-expert, graphql-expert, javascript-expert
- python, rust, typescript-expert
- vue3, nuxt4, llm-integration, mcp

**Security & Infrastructure (19):**
- appsec-expert, devsecops-expert, encryption
- kanidm-expert, sandboxing, security-auditing
- argo-expert, cilium-expert, harbor-expert
- talos-os-expert, talos-cluster-ops, ci-cd, cicd-expert
- cross-platform-builds, auto-update-systems
- browser-automation, dbus, os-keychain
- skill-creation-expert, senior-architect

**Data & Databases (7):**
- celery-expert, database-design
- graph-database-expert, rabbitmq-expert
- sqlcipher, sqlite, surrealdb-expert

**UI/UX & Design (8):**
- accessibility-wcag, design-systems
- gsap, motion-design, tailwindcss
- ui-ux-design, ui-ux-expert
- pinia

**Graphics & Media (6):**
- glsl, webgl, web-audio-api
- speech-to-text, text-to-speech
- wake-word-detection

**Cloud & APIs (4):**
- cloud-api-integration, rest-api-design
- json-rpc, websocket

**Platform-Specific (5):**
- applescript, macos-accessibility
- linux-at-spi2, windows-ui-automation
- tauri

**Other (10):**
- model-quantization, plan-review-expert, prd-generator
- refactoring-expert, web-research-expert

### Process Skills (7) 🆕

**Quality Enforcement:**
- `verification-gate` (~300 tokens) - No completion claims without evidence
- `tdd-protocol` (~400 tokens) - Enforce RED-GREEN-REFACTOR cycle
- `systematic-debugging` (~450 tokens) - Root cause first, fix second
- `staged-review` (~400 tokens) - Two-stage review (spec → quality)

**Workflow Management:**
- `isolated-development` (~300 tokens) - Git worktree per feature/issue
- `design-first` (~350 tokens) - Think before coding
- `plan-execution` (~350 tokens) - Batch execution with checkpoints

**Total token cost:**
- Balanced profile (default): ~1,500 tokens
- Strict profile (all enabled): ~2,550 tokens

**Configure**: Edit `.dev-aid/config/process-skills.json`

## 🚀 Creating New Skills

See [SKILL_QUICKSTART.md](./SKILL_QUICKSTART.md) for a comprehensive guide.

**Quick Steps:**
1. Run `/dev-aid-build-skill` command
2. Answer questions to determine risk level
3. Fill out template sections
4. Follow § 4: Quality Assurance Checklist
5. Keep under 500 lines (move extras to references/)

## ✅ Quality Assurance

All skills now enforce:
- ✅ Exact version pinning for dependencies (==)
- ✅ Pre-commit hooks (black, isort, flake8, mypy, bandit)
- ✅ Security validation protocols
- ✅ Test-driven development workflow
- ✅ >80% test coverage
- ✅ Comprehensive documentation

## 📖 Template References

For detailed guidance, see:
- **Security Framework**: `template-references/security-framework.md`
- **OWASP 2025 Guide**: `template-references/owasp-2025-guide.md`
- **Threat Modeling**: `template-references/threat-modeling.md`
- **Compliance**: `template-references/compliance-guide.md`
- **Progressive Disclosure**: `template-references/progressive-disclosure.md`

## 🔄 Migration History

**v2.1.0 (2026-02-02)**: Skills Migration from Dotfiles
- ✅ Replaced all 69 shared skills with improved dotfiles versions
- ✅ Added 3 new skills: `talos-cluster-ops`, `nuxt4`, `vue3`
- ✅ Removed 4 duplicate skills: `async-programming`, `typescript`, `fastapi`, `vue-nuxt`
- ✅ All skills now follow unified v2.0.0 template with CWE-based security patterns
- ✅ More concise NEVER/ALWAYS format (vs verbose CVE research protocols)
- ✅ 2-3x more code examples and patterns per skill
- ✅ Skills synced from personal dotfiles for improved quality

**v2.0.0 (2025-12-07)**: [PR #62](https://github.com/Probably-Group/Dev-AID/pull/62)
- ✅ Migrated all 72 skills to two-tier template
- ✅ Added § 4: Quality Assurance Checklist to all skills
- ✅ Added § 0.4: Progressive Disclosure guidance
- ✅ Condensed 49 skills with references/ directories
- ✅ All skills now <500 lines (Claude Code compatible)
- ✅ **Enriched all 72 skills with domain-specific security content:**
  - § 0.1: Quick Risk Assessment with domain-specific risk factors
  - § 0.2: Vulnerability Research Protocol with 150+ current CVEs from 2024-2025
  - § 0.3: Hallucination Prevention Checklist with tailored security rules
  - All CVEs include CVSS scores and verification sources
  - All HIGH/MEDIUM skills mapped to MITRE ATT&CK framework

## 🛠️ Migration Tools

- **migrate-skills-to-v2.py**: Automated migration script
  - Adds § 4 Quality Assurance Checklist
  - Adds § 0.4 Progressive Disclosure
  - Batch processing support

- **condense-skills.py**: Automated condensing script
  - Identifies large movable sections
  - Creates references/ structure
  - Maintains <500 line limit

## 📝 Skill Registration

All skills must be registered in `registry/skills-index.json` with:
- Activation triggers (keywords, file patterns, technologies)
- Metadata (name, version, domain, risk level)
- Confidence weights for context-aware activation

## 🔗 Related Documentation

- [Skill Quick-Start Guide](./SKILL_QUICKSTART.md)
- [Skill Template](./SKILL_TEMPLATE.md)
- [Process Skills Overview](./process/README.md) 🆕
