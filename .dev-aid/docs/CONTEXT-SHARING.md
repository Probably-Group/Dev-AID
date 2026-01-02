# Context Sharing in Dev-AID

## Overview

When multiple AI models collaborate in **Ensemble** or **Challenger** mode, they need to share context and information. This document explains how context flows between models and how it's logged for transparency.

---

## 🔄 How Context Sharing Works

### Architecture

```
User Request
     ↓
Router (.dev-aid/orchestration/router.sh)
     ↓
  Analyzes task type
     ↓
┌────────────────────────────────┐
│  Selects appropriate model(s)  │
│                                │
│  Solo:       Model A only      │
│  Ensemble:   Model A → Model B │
│  Challenger: Model A ⇄ Model B │
│  None:       User chooses      │
└────────────────────────────────┘
     ↓
Context Passthrough
     ↓
.dev-aid/logs/context-sharing.log (optional logging)
```

---

## 📝 Context Sharing Mechanisms

### 1. Shared Memory Bank

All AI models have access to the **shared memory bank**:

```
.dev-aid/memory-bank/
├── activeContext.md       # Current project state (all models read this)
├── patterns.md            # Code patterns (all models read this)
├── decisions.md           # ADRs (all models read this)
├── security.md            # Security context
├── performance.md         # Performance baselines
├── testing.md             # Test strategies
└── chaos.md               # Chaos experiments
```

**Key Point**: Memory bank is **provider-agnostic** - renamed from `CLAUDE-*.md` to generic names so all AI models can access the same institutional knowledge.

### 2. Provider Context Files

Each AI model receives a **customized context file** explaining:
- Its role in the system
- When it should be invoked
- How to collaborate with other models
- Access to shared memory bank

```
CLAUDE.md  → Claude reads this (symlinked to .dev-aid/providers/claude/CLAUDE.md)
GEMINI.md  → Gemini reads this (symlinked to .dev-aid/providers/gemini/GEMINI.md)
OPENAI.md  → OpenAI reads this (symlinked to .dev-aid/providers/openai/OPENAI.md)
```

### 3. Router-Mediated Handoffs

In **Ensemble** and **Challenger** modes, the router coordinates context passing:

#### Ensemble Mode Example:

```bash
User: "Analyze entire repository and refactor authentication"

# Step 1: Router analyzes task
Router: context_size = 200K tokens
Router: Assigns to Gemini (massive context capability)

# Step 2: Gemini executes
Gemini: Reads 200 files
Gemini: Outputs analysis to .dev-aid/logs/context-sharing.log
Gemini: Creates handoff file: .dev-aid/temp/handoff_12345.md

# Step 3: Router passes to Claude
Router: Loads handoff_12345.md
Router: Assigns implementation to Claude

# Step 4: Claude executes
Claude: Reads handoff analysis
Claude: Generates refactored code
Claude: Logs completion to context-sharing.log
```

#### Challenger Mode Example:

```bash
User: "Implement OAuth2 authentication"

# Step 1: Primary model (Claude) generates
Claude: Implements OAuth2 code
Claude: Writes to .dev-aid/temp/primary_output_67890.md

# Step 2: Challenger model (Gemini) reviews
Gemini: Reads primary_output_67890.md
Gemini: Reviews for security, edge cases, alternatives
Gemini: Writes critique to .dev-aid/temp/challenger_review_67890.md

# Step 3: User receives both
Router: Combines outputs
Router: Shows both perspectives to user
Router: Logs full interaction to context-sharing.log
```

---

## 📊 Logging System

### Location

```
.dev-aid/logs/context-sharing.log
```

### What's Logged

When **context_sharing.logging.enabled = true** in `settings.json`:

```
2025-11-26 10:30:15 [INFO] User request: "Analyze repo and refactor auth"
2025-11-26 10:30:15 [ROUTER] Mode: ensemble
2025-11-26 10:30:15 [ROUTER] Task type: massive_context
2025-11-26 10:30:15 [ROUTER] Context size: 200,000 tokens
2025-11-26 10:30:15 [ROUTER] Selected model: gemini-2.0-flash
2025-11-26 10:30:15 [ROUTER] Reason: Massive context (>100K tokens)
2025-11-26 10:31:42 [GEMINI] Analysis complete (87 seconds)
2025-11-26 10:31:42 [GEMINI] Files analyzed: 203
2025-11-26 10:31:42 [GEMINI] Output: .dev-aid/temp/handoff_abc123.md
2025-11-26 10:31:42 [ROUTER] Handing off to: claude-sonnet-4.5
2025-11-26 10:31:42 [ROUTER] Handoff file: handoff_abc123.md (1,200 tokens)
2025-11-26 10:33:15 [CLAUDE] Implementation complete (93 seconds)
2025-11-26 10:33:15 [CLAUDE] Files modified: 12
2025-11-26 10:33:15 [CLAUDE] Tests generated: 8
2025-11-26 10:33:15 [ROUTER] Workflow complete (180 seconds total)
2025-11-26 10:33:15 [COST] Gemini: $0.015 | Claude: $0.45 | Total: $0.465
```

### Log Levels

Configure in `.dev-aid/config/settings.json`:

```json
{
  "context_sharing": {
    "logging": {
      "enabled": true,
      "log_file": ".dev-aid/logs/context-sharing.log",
      "log_level": "info"    // Options: debug, info, warn, error
    }
  }
}
```

- **debug**: Everything (includes full context dumps)
- **info**: Standard workflow tracking (recommended)
- **warn**: Only warnings and errors
- **error**: Only errors

---

## 🔍 Viewing Logs

### Real-time Monitoring

```bash
# Watch logs in real-time
tail -f .dev-aid/logs/context-sharing.log

# Filter for specific model
grep "GEMINI" .dev-aid/logs/context-sharing.log

# View cost summary
grep "COST" .dev-aid/logs/context-sharing.log
```

### Log Analysis

```bash
# How many times was each model used today?
grep -E "$(date +%Y-%m-%d)" .dev-aid/logs/context-sharing.log | \
  grep "Selected model" | \
  awk '{print $NF}' | \
  sort | uniq -c

# Total cost for last 7 days
grep "COST" .dev-aid/logs/context-sharing.log | \
  tail -n 100 | \
  awk -F'Total: $' '{sum += $2} END {print "Total: $"sum}'
```

---

## 🛡️ Privacy & Security

### What's Logged

✅ **Logged**:
- Timestamps
- Model selections
- Task types
- File counts
- Token counts
- Execution times
- Costs

❌ **NOT Logged** (unless `log_level = debug`):
- Actual code content
- API responses
- User data
- Secrets

### Log Rotation

Logs automatically rotate when they reach 10MB:

```
context-sharing.log         (current)
context-sharing.log.1       (previous)
context-sharing.log.2       (older)
...
context-sharing.log.10      (oldest, auto-deleted)
```

### Disable Logging

If you don't want logging:

```json
{
  "context_sharing": {
    "enabled": true,
    "logging": {
      "enabled": false    // Turn off logging
    }
  }
}
```

Context still flows between models, but nothing is written to disk.

---

## 🔄 Handoff Files

Temporary files used for context passing:

### Location

```
.dev-aid/temp/
├── handoff_abc123.md           # Gemini → Claude analysis
├── primary_output_xyz789.md    # Claude's implementation
├── challenger_review_xyz789.md # Gemini's review
└── .cleanup_marker
```

### Lifecycle

1. **Created**: When Model A completes its work
2. **Read**: By Model B via router
3. **Deleted**: After successful handoff (or after 24 hours)

### Format

Handoff files use structured markdown:

```markdown
# Handoff: Gemini → Claude

## Task
Analyze repository and identify authentication patterns

## Context
- Total files analyzed: 203
- Authentication files: 12
- Current implementation: JWT-based
- Issues found: 3 security vulnerabilities

## Findings

### Security Issues
1. [HIGH] Hardcoded secret in auth.config.js:45
2. [MEDIUM] Missing token expiration check
3. [LOW] Weak password validation

### Architecture
Current auth flow:
1. User submits credentials
2. API validates via JWT
3. Token stored in localStorage (INSECURE!)

## Recommendations for Implementation
1. Move secret to environment variable
2. Implement token refresh mechanism
3. Use httpOnly cookies instead of localStorage
4. Add rate limiting to auth endpoints

## Files to Modify
- src/auth/auth.config.js
- src/auth/jwt.service.ts
- src/middleware/auth.middleware.ts
- src/routes/auth.routes.ts

## Next Steps
Claude should:
- Implement secure JWT configuration
- Refactor storage mechanism
- Add comprehensive tests
- Update documentation
```

---

## 🎯 Configuration Examples

### Example 1: Ensemble with Full Logging

```json
{
  "orchestration_mode": "ensemble",
  "context_sharing": {
    "enabled": true,
    "logging": {
      "enabled": true,
      "log_file": ".dev-aid/logs/context-sharing.log",
      "log_level": "info"
    }
  },
  "task_model_mapping": {
    "code_generation": "claude-sonnet-4.5",
    "massive_context": "gemini-2.0-flash",
    "documentation": "gpt-4o"
  }
}
```

### Example 2: Challenger with Debug Logging

```json
{
  "orchestration_mode": "challenger",
  "context_sharing": {
    "enabled": true,
    "logging": {
      "enabled": true,
      "log_file": ".dev-aid/logs/context-sharing.log",
      "log_level": "debug"    // Includes full context
    }
  },
  "task_model_mapping": {
    "default": "claude-sonnet-4.5",
    "challenger": "gemini-2.0-pro"
  }
}
```

### Example 3: None Mode (No Sharing)

```json
{
  "orchestration_mode": "none",
  "context_sharing": {
    "enabled": false    // User manually selects models
  }
}
```

---

## 🔧 Troubleshooting

### Issue: Context not being passed

**Check**:
1. Verify `context_sharing.enabled = true`
2. Check logs: `cat .dev-aid/logs/context-sharing.log`
3. Verify handoff files exist: `ls -la .dev-aid/temp/`

### Issue: Logs growing too large

**Solutions**:
1. Reduce log level to `warn` or `error`
2. Enable log rotation (enabled by default)
3. Manually clean old logs: `rm .dev-aid/logs/context-sharing.log.*`

### Issue: Models not collaborating

**Check**:
1. Verify orchestration mode: `jq '.orchestration_mode' .dev-aid/config/settings.json`
2. Ensure multiple providers enabled
3. Check model assignments in settings.json

---

## 📚 Related Documentation

- [Router MCP Integration](ROUTER-MCP-INTEGRATION.md) - MCP integration guide
- [Automation Guide](AUTOMATION-GUIDE.md) - Automation workflows and examples
- [Skills Architecture](SKILLS-ARCHITECTURE.md) - Expert skills system architecture

---

## 🎓 Best Practices

1. **Enable Info-Level Logging**: Provides transparency without bloat
2. **Review Logs Weekly**: Understand model usage patterns
3. **Monitor Costs**: Use cost logs to optimize model selection
4. **Clean Temp Files**: Old handoff files are auto-deleted, but verify periodically
5. **Debug Mode Sparingly**: Only use for troubleshooting (generates large logs)

---

## 🔧 Smart Context File Initialization

Dev-AID features intelligent context file initialization for **all providers** that preserves your existing content while adding Dev-AID capabilities.

**Supported Providers**:
- ✅ **CLAUDE.md** - Claude-specific context
- ✅ **GEMINI.md** - Gemini-specific context
- ✅ **OPENAI.md** - OpenAI-specific context

### Features

**Automatic Backup**:
- Original files backed up to `.dev-aid/backups/{PROVIDER}_original-backup_TIMESTAMP.md`
- Easy-access symlinks: `{PROVIDER}_original-backup.md` → latest backup
- Never lose your existing instructions
- Per-provider backup tracking

**Content Validation**:
- Detects outdated technology versions
- Finds conflicting instructions
- Identifies invalid file paths
- Flags security issues
- Auto-fixes common problems
- Works for all provider context files

**Progressive Disclosure (>500 lines)**:
- Main file: Core content ≤450 lines
- Extended file: Detailed Dev-AID documentation
- Custom file: Your original instructions preserved
- Cross-referenced for easy navigation
- Applied to any large context file

**Migration Report**:
- Shows all issues found and fixed
- Lists items needing manual review
- Provides clear next steps
- Saved to `.dev-aid/logs/{provider}-context-migration_TIMESTAMP.log`
- Provider-specific reporting

### How It Works

During `./install.sh` or `dev-aid reconfigure` (for all enabled providers):

1. **Detection**: Checks for existing context files
2. **Backup**: Creates timestamped backups
3. **Validation**: Analyzes content for issues
4. **Merge**: Combines with provider-specific Dev-AID template
5. **Split**: Applies progressive disclosure if needed
6. **Report**: Shows validation results

### Manual Operations

**Validate existing context file**:
```bash
# Claude
bash .dev-aid/scripts/lib/provider-context-init.sh validate . claude

# Gemini
bash .dev-aid/scripts/lib/provider-context-init.sh validate . gemini

# OpenAI
bash .dev-aid/scripts/lib/provider-context-init.sh validate . openai
```

**Restore from backup**:
```bash
# Claude
bash .dev-aid/scripts/lib/provider-context-init.sh restore . claude

# Gemini
bash .dev-aid/scripts/lib/provider-context-init.sh restore . gemini

# OpenAI
bash .dev-aid/scripts/lib/provider-context-init.sh restore . openai
```

**List backups**:
```bash
# Claude
bash .dev-aid/scripts/lib/provider-context-init.sh list-backups . claude

# Gemini
bash .dev-aid/scripts/lib/provider-context-init.sh list-backups . gemini

# OpenAI
bash .dev-aid/scripts/lib/provider-context-init.sh list-backups . openai
```

**Re-run initialization**:
```bash
# Claude
bash .dev-aid/scripts/lib/provider-context-init.sh init-interactive . claude

# Gemini
bash .dev-aid/scripts/lib/provider-context-init.sh init-interactive . gemini

# OpenAI
bash .dev-aid/scripts/lib/provider-context-init.sh init-interactive . openai
```

### File Structure After Migration

```
project-root/
├── CLAUDE.md (symlink → .dev-aid/providers/claude/CLAUDE.md)
├── GEMINI.md (symlink → .dev-aid/providers/gemini/GEMINI.md)
├── OPENAI.md (symlink → .dev-aid/providers/openai/OPENAI.md)
├── CLAUDE_original-backup.md (symlink → latest Claude backup)
├── GEMINI_original-backup.md (symlink → latest Gemini backup)
├── OPENAI_original-backup.md (symlink → latest OpenAI backup)
│
└── .dev-aid/
    ├── providers/
    │   ├── claude/
    │   │   ├── CLAUDE.md (main, ≤450 lines)
    │   │   ├── CLAUDE_extended.md (if content >500 lines)
    │   │   └── CLAUDE_custom.md (your original content)
    │   │
    │   ├── gemini/
    │   │   ├── GEMINI.md (main, ≤450 lines)
    │   │   ├── GEMINI_extended.md (if content >500 lines)
    │   │   └── GEMINI_custom.md (your original content)
    │   │
    │   └── openai/
    │       ├── OPENAI.md (main, ≤450 lines)
    │       ├── OPENAI_extended.md (if content >500 lines)
    │       └── OPENAI_custom.md (your original content)
    │
    ├── backups/
    │   ├── CLAUDE_original-backup_20260102_143022.md
    │   ├── GEMINI_original-backup_20260102_143022.md
    │   ├── OPENAI_original-backup_20260102_143022.md
    │   ├── .latest-claude (tracks most recent Claude backup)
    │   ├── .latest-gemini (tracks most recent Gemini backup)
    │   └── .latest-openai (tracks most recent OpenAI backup)
    │
    └── logs/
        ├── claude-context-migration_TIMESTAMP.log
        ├── gemini-context-migration_TIMESTAMP.log
        └── openai-context-migration_TIMESTAMP.log
```

### Best Practices

1. **Review migration report** after initialization
2. **Check flagged items** in CLAUDE_custom.md
3. **Test with your AI** to ensure context works
4. **Keep backups** (auto-cleaned, keeping last 5)
5. **Update custom content** as your project evolves

For implementation details, see [CLAUDE-MD-INITIALIZATION-PLAN.md](CLAUDE-MD-INITIALIZATION-PLAN.md).

---

**Questions?** Check `.dev-aid/logs/context-sharing.log` for real-time insights into how your AI models are collaborating!
