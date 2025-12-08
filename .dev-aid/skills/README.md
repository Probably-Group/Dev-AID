# Dev-AID Skills System

**72 expert skills** across domains, all following the **two-tier template v2.0.0** with comprehensive quality assurance and progressive disclosure.

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
├── core/                        # Core system skills (2)
│   ├── code-reviewer/
│   └── secret-scanner/
├── expert/                      # Expert domain skills (72)
│   ├── [skill-name]/
│   │   ├── SKILL.md            # Main skill file (<500 lines)
│   │   └── references/         # Extended content (optional)
│   │       ├── implementation-workflow-tdd.md
│   │       ├── implementation-patterns.md
│   │       ├── performance-patterns.md
│   │       └── ...
└── registry/
    └── skills-index.json        # Skill metadata and activation triggers
```

## 🎯 Skill Template v2.0.0

All skills follow a unified two-tier template structure:

### Main SKILL.md (<500 lines)

**Required Sections:**
- § 0: Security-First Framework & Anti-Hallucination Protocol ⭐ **FULLY ENRICHED**
  - 0.1: Quick Risk Assessment (LOW/MEDIUM/HIGH) - **100% complete (72/72 skills)**
  - 0.2: Vulnerability Research Protocol (MEDIUM/HIGH only) - **100% complete (56/56 MEDIUM/HIGH skills)**
  - 0.3: Hallucination Prevention Checklist - **100% complete (72/72 skills)**
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

### Core Skills (2)
- code-reviewer
- secret-scanner

### Expert Skills (72)

**Development & Languages (15):**
- api-expert, async-expert, async-programming
- bash-expert, fastapi-expert, graphql-expert
- javascript-expert, python, rust
- typescript-expert, typescript
- vue-nuxt-expert, vue-nuxt
- llm-integration, mcp

**Security & Infrastructure (18):**
- appsec-expert, devsecops-expert, encryption
- kanidm-expert, sandboxing
- argo-expert, cilium-expert, harbor-expert
- talos-os-expert, ci-cd, cicd-expert
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

**Other (9):**
- model-quantization, plan-review-expert
- refactoring-expert, web-research-expert

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

**v2.0.0 (2025-12-07)**: [PR #62](https://github.com/martinholovsky/Dev-AID/pull/62)
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
