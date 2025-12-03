# Tresor Commands Analysis for Dev-AID

This document analyzes which commands from `claude-code-tresor` will be integrated into Dev-AID and which will not, with detailed reasoning.

---

## ✅ Commands That WILL Be Integrated

### Security Commands

#### `/audit` - **WILL INCLUDE**
**Reason**: Core security functionality that aligns with DevSecOps best practices
**Priority**: High
**Integration Plan**:
- Copy to `.dev-aid/providers/claude/.claude/commands/security/audit.md`
- Adapt to work with Dev-AID's memory bank (security.md)
- Update to support multi-provider orchestration
**Value Proposition**: Comprehensive security audits are essential for production apps

#### `/vulnerability-scan` - **WILL INCLUDE**
**Reason**: Critical for dependency security
**Priority**: High
**Integration Plan**:
- Copy to `.dev-aid/providers/claude/.claude/commands/security/vulnerability-scan.md`
- Integrate with package managers (npm, pip, cargo, go mod)
- Auto-update security.md memory bank file
**Value Proposition**: Automated CVE scanning prevents known vulnerabilities

#### `/compliance-check` - **WILL INCLUDE**
**Reason**: Important for enterprise users (GDPR, SOC2, HIPAA)
**Priority**: Medium
**Integration Plan**:
- Copy to `.dev-aid/providers/claude/.claude/commands/security/compliance-check.md`
- Make compliance framework configurable (GDPR, SOC2, HIPAA, PCI-DSS)
- Generate compliance reports in `.dev-aid/reports/compliance/`
**Value Proposition**: Regulatory compliance is non-negotiable for many projects

---

### Performance Commands

#### `/profile` - **WILL INCLUDE**
**Reason**: Performance profiling is essential for optimization
**Priority**: Medium
**Integration Plan**:
- Copy to `.dev-aid/providers/claude/.claude/commands/performance/profile.md`
- Update to log findings in performance.md memory bank
- Support multiple profiling tools (perf, valgrind, node --prof, py-spy)
**Value Proposition**: Data-driven performance optimization

#### `/benchmark` - **WILL INCLUDE**
**Reason**: Baseline performance tracking over time
**Priority**: Medium
**Integration Plan**:
- Copy to `.dev-aid/providers/claude/.claude/commands/performance/benchmark.md`
- Store benchmarks in `.dev-aid/reports/benchmarks/` with timestamps
- Track performance regressions
**Value Proposition**: Prevents performance degradation over time

---

### Operations Commands

#### `/deploy-validate` - **WILL INCLUDE**
**Reason**: Pre-deployment validation is critical for production safety
**Priority**: High
**Integration Plan**:
- Copy to `.dev-aid/providers/claude/.claude/commands/operations/deploy-validate.md`
- Check: tests pass, linting passes, security scan clean, dependencies up-to-date
- Integrate with CI/CD pipelines
**Value Proposition**: Catch issues before they reach production

#### `/health-check` - **WILL INCLUDE**
**Reason**: System health monitoring post-deployment
**Priority**: Medium
**Integration Plan**:
- Copy to `.dev-aid/providers/claude/.claude/commands/operations/health-check.md`
- Support various health check types (HTTP, database, Redis, message queues)
- Log health status over time
**Value Proposition**: Early detection of production issues

#### `/incident-response` - **WILL INCLUDE**
**Reason**: Structured incident handling workflow
**Priority**: Medium
**Integration Plan**:
- Copy to `.dev-aid/providers/claude/.claude/commands/operations/incident-response.md`
- Create incident log in `.dev-aid/reports/incidents/`
- Guide through: detection → triage → mitigation → postmortem
**Value Proposition**: Reduces MTTR (Mean Time To Recovery)

---

### Quality Commands

#### `/code-health` - **WILL INCLUDE**
**Reason**: Code quality metrics and tracking
**Priority**: High
**Integration Plan**:
- Copy to `.dev-aid/providers/claude/.claude/commands/quality/code-health.md`
- Measure: complexity, duplication, test coverage, code smells
- Update patterns.md with discovered anti-patterns
**Value Proposition**: Proactive technical debt management

#### `/debt-analysis` - **WILL INCLUDE**
**Reason**: Technical debt identification and prioritization
**Priority**: High
**Integration Plan**:
- Copy to `.dev-aid/providers/claude/.claude/commands/quality/debt-analysis.md`
- Create debt backlog in `.dev-aid/reports/debt/`
- Prioritize by impact and effort
**Value Proposition**: Strategic debt paydown planning

---

## ❌ Commands That WILL NOT Be Integrated

**Note**: The following commands either don't exist in Tresor or won't be included for the reasons stated.

### Reason Category 1: Overlap with Dev-AID Core Features

#### Workflow Commands (11 total) - **WILL NOT INCLUDE**
**Commands**: `/review`, `/todo-add`, `/todo-check`, `/whats-next`, `/create-prompt`, `/run-prompt`, `/handoff-create`, etc.

**Reason**: Dev-AID already has TodoWrite tool and workflow management
**Alternative**: Use Claude Code's built-in TodoWrite tool
**Overlap**: Both track tasks, manage workflows, create handoffs
**Decision**: Keep Dev-AID focused on multi-provider orchestration, not duplicating Claude Code's core features

---

### Reason Category 2: Useful But Lower Priority

#### `/scaffold` - **MAYBE LATER**
**Reason**: Code scaffolding/boilerplate generation
**Value**: Useful for project initialization
**Decision**: Phase 4 (future consideration) - not critical for v1.0
**Why Not Now**: Focus on security, performance, operations first

#### `/test-gen` - **MAYBE LATER**
**Reason**: Test generation is valuable but not critical
**Value**: Automated test creation
**Decision**: Phase 4 (future consideration)
**Why Not Now**: Dev-AID promotes TDD (tests written first), not generated after

#### `/docs-gen` - **MAYBE LATER**
**Reason**: Documentation generation
**Value**: Automated README, API docs generation
**Decision**: Phase 4 (future consideration)
**Why Not Now**: Focus on core orchestration and security first

---

### Reason Category 3: Development Tools (Can Add Custom)

#### `/development/*` Commands - **USER CAN ADD**
**Reason**: General development utilities
**Decision**: Users can copy these commands if needed
**Installation**:
```bash
cp claude-code-tresor/commands/development/* \
   .dev-aid/providers/claude/.claude/commands/custom/
```

---

### Reason Category 4: Out of Scope (Speculative Examples)

**Note**: The following were mentioned in earlier analysis but **don't actually exist in Tresor**:

- `/setup-analysis` - Doesn't exist (we have `/aid-analyze`)
- `/context-init` - Doesn't exist (install.sh handles this)
- `/claude-optimize` - Doesn't exist (was speculative example)
- `/prompt-engineering` - Doesn't exist (was speculative example)
- `/ml-pipeline` - Doesn't exist (was speculative example)
- `/blockchain-audit` - Doesn't exist (was speculative example)
- `/mobile-deploy` - Doesn't exist (was speculative example)
- `/git-history-clean` - Doesn't exist (was speculative example)
- `/dependency-graph` - Doesn't exist (was speculative example)
- `/pair-programming` - Doesn't exist (was speculative example)
- `/code-golf` - Doesn't exist (was speculative example)

---

## 📊 Summary Statistics

**Total Tresor Commands Available**: 24

**Will Include**: 10 commands (42%)
- Security: 3 commands (audit, vulnerability-scan, compliance-check)
- Performance: 2 commands (profile, benchmark)
- Operations: 3 commands (deploy-validate, health-check, incident-response)
- Quality: 2 commands (code-health, debt-analysis)

**Will Not Include**: 14 commands (58%)
- Workflow management: 11 commands (overlap with TodoWrite tool)
- Lower priority: 3 commands (scaffold, test-gen, docs-gen - maybe Phase 4)

**Speculative Commands (Don't Exist)**: 11
- These were examples in earlier analysis but aren't actual Tresor commands

---

## 🎯 Integration Roadmap

### Phase 1: High Priority (Week 1-2)
Commands that provide immediate security and deployment value:

1. `/aid-audit` (rename from `/audit`)
2. `/aid-vulnerability-scan` (rename from `/vulnerability-scan`)
3. `/aid-deploy-validate` (rename from `/deploy-validate`)
4. `/aid-code-health` (rename from `/code-health`)
5. `/aid-debt-analysis` (rename from `/debt-analysis`)

### Phase 2: Medium Priority (Week 3-4)
Commands that enhance operations and compliance:

6. `/aid-compliance-check` (rename from `/compliance-check`)
7. `/aid-health-check` (rename from `/health-check`)
8. `/aid-incident-response` (rename from `/incident-response`)

### Phase 3: Lower Priority (Week 5-6)
Performance optimization commands:

9. `/aid-profile` (rename from `/profile`)
10. `/aid-benchmark` (rename from `/benchmark`)

---

## 🔧 Adaptation Requirements

When integrating Tresor commands, we need to:

### 1. Rename with `aid-` Prefix
**Before**: `/audit`
**After**: `/aid-audit`
**Reason**: Distinguish Dev-AID commands from user custom commands

### 2. Integrate with Memory Bank
**Example**: `/aid-audit` should update `.dev-aid/memory-bank/security.md` with findings
**Pattern**: All commands should log learnings to appropriate memory bank file

### 3. Support Multi-Provider Orchestration
**Example**: `/aid-code-health` should work whether Claude, Gemini, or OpenAI is running it
**Pattern**: Commands should be provider-agnostic in their implementation

### 4. Add Configuration Support
**Example**: `/aid-compliance-check` should read compliance requirements from settings
**Pattern**: Commands should respect Dev-AID configuration files

### 5. Update Output Paths
**Before**: Output to root directory
**After**: Output to `.dev-aid/reports/<category>/`
**Pattern**: Standardize report locations

---

## 📝 Command Template for Integration

When adapting a Tresor command:

```markdown
---
name: aid-[command-name]
description: [Brief description]
category: [security|performance|operations|quality]
author: Dev-AID Team (adapted from Tresor)
version: 1.0.0
---

# [Command Name]

[Original command description, adapted for Dev-AID]

## Dev-AID Integration

### Memory Bank Updates
This command updates the following memory bank files:
- `.dev-aid/memory-bank/[relevant-file].md`

### Report Output
Reports are saved to:
- `.dev-aid/reports/[category]/[timestamp]-[command-name].md`

### Multi-Provider Support
This command works with all enabled providers:
- Claude: [How it works with Claude]
- Gemini: [How it works with Gemini]
- OpenAI: [How it works with OpenAI]

## Usage

[Original usage instructions]

## Configuration

[Dev-AID-specific configuration options]

## Example Output

[Example with Dev-AID paths]
```

---

## 💡 Recommendations for Users

### For Users Who Want Excluded Commands

If you need a command we decided not to include:

1. **Create Custom Command**: Copy from Tresor to your `.dev-aid/providers/claude/.claude/commands/custom/`
2. **Adapt as Needed**: Modify for your specific workflow
3. **Share with Community**: If useful, contribute back to Dev-AID

### Example: Adding `/blockchain-audit` Yourself

```bash
# Copy the command
cp ~/claude-code-tresor/commands/security/blockchain-audit.md \
   .dev-aid/providers/claude/.claude/commands/custom/

# Rename with aid- prefix
mv .dev-aid/providers/claude/.claude/commands/custom/blockchain-audit.md \
   .dev-aid/providers/claude/.claude/commands/custom/aid-blockchain-audit.md

# Now use it
/aid-blockchain-audit
```

---

## 📖 Related Documentation

- [Commands Reference](./COMMANDS-REFERENCE.md) - Full list of Dev-AID commands
- [Custom Commands Guide](./CUSTOM-COMMANDS.md) - How to create your own commands
- [Memory Bank Guide](./MEMORY-BANK.md) - Understanding the memory bank system

---

**Last Updated**: 2025-11-26
**Version**: 1.0.0
**Status**: Integration in progress (Phase 1)
