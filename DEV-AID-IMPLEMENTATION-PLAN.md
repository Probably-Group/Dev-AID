# Dev-AID (Development AI Driver) - Implementation Plan

**Version**: 2.1.0
**Architecture**: Multi-Model, User-Configurable, Provider-Agnostic
**Philosophy**: Intelligent Orchestration Across AI Models
**Latest Update**: 2025-11-26 - Granular Control & Transparency

---

## 🎯 Vision

Transform the Claude-specific setup into **Dev-AID**: a universal AI development assistant that orchestrates multiple AI models (Claude, Gemini, OpenAI, OpenRouter) with configurable workflows.

## 🆕 Latest Enhancements (v2.1.0)

### Granular Model Selection
Users now assign specific models to specific task types during installation:
- ✅ Code generation → Choose: Claude Sonnet/Opus, Gemini, etc.
- ✅ Massive context → Choose: Gemini Flash/Pro, Claude
- ✅ Documentation → Choose: OpenAI GPT-4o, Claude
- ✅ Security analysis → Choose: Claude Sonnet, Gemini Pro
- ✅ Challenger review → Choose: Any enabled model

### None (Manual) Orchestration Mode
New 4th mode for maximum user control:
- ✅ No automatic routing
- ✅ User explicitly selects: `@claude`, `@gemini`, `@openai`
- ✅ Perfect for single-AI users or learning different models

### Reconfiguration System
Change settings anytime without breaking existing setup:
- ✅ Interactive menu: `.dev-aid/scripts/reconfigure.sh`
- ✅ Automatic backup before changes
- ✅ Memory bank preserved
- ✅ Configuration validation
- ✅ Rollback capability

### Context Sharing Transparency
Full visibility into multi-model collaboration:
- ✅ Logging: `.dev-aid/logs/context-sharing.log`
- ✅ Tracks: Which model, what task, execution time, costs
- ✅ Privacy-safe: Metadata only, no code/secrets
- ✅ Configurable: Can disable logging
- ✅ Documentation: `.dev-aid/docs/CONTEXT-SHARING.md`

### Smart API Key Collection
Only asks for keys you need:
- ✅ Installer detects enabled providers
- ✅ Only prompts for relevant API keys
- ✅ Stored in `.dev-aid/config/.env` (gitignored)
- ✅ Can add/update later via reconfigure

---

## 🏗️ Architecture Overview

### Directory Structure

```
project-root/
├── .dev-aid/                          # All Dev-AID files (hidden from repo clutter)
│   ├── config/
│   │   ├── settings.json              # User configuration
│   │   ├── models.json                # Model credentials & preferences
│   │   ├── orchestration.json         # Orchestration mode settings
│   │   └── skill-rules.json           # Auto-activation rules
│   ├── providers/
│   │   ├── claude/
│   │   │   ├── CLAUDE.md              # Claude-specific context (symlinked to root)
│   │   │   ├── .claude/               # Claude Code-specific files
│   │   │   │   ├── settings.json
│   │   │   │   ├── skills/
│   │   │   │   ├── agents/
│   │   │   │   ├── commands/
│   │   │   │   └── hooks/
│   │   │   └── README.md
│   │   ├── gemini/
│   │   │   ├── GEMINI.md              # Gemini-specific context (symlinked to root)
│   │   │   └── .gemini/               # Gemini-specific files
│   │   ├── openai/
│   │   │   ├── OPENAI.md              # OpenAI-specific context (symlinked to root)
│   │   │   └── .openai/               # OpenAI-specific files
│   │   └── openrouter/
│   │       ├── OPENROUTER.md          # OpenRouter-specific context
│   │       └── .openrouter/
│   ├── memory-bank/                   # Shared institutional knowledge
│   │   ├── activeContext.md           # Current sprint/session
│   │   ├── patterns.md                # Code patterns
│   │   ├── decisions.md               # ADRs
│   │   ├── security.md                # Security context
│   │   ├── performance.md             # Performance baselines
│   │   ├── testing.md                 # Test strategies
│   │   └── chaos.md                   # Chaos experiments
│   ├── orchestration/
│   │   ├── router.sh                  # AI model router
│   │   ├── modes/
│   │   │   ├── none.sh                # Manual mode (NEW v2.1)
│   │   │   ├── solo.sh                # Single model mode
│   │   │   ├── ensemble.sh            # Multi-model collaboration
│   │   │   └── challenger.sh          # Model A + B review
│   │   └── workflows/
│   │       ├── massive-context.sh     # Gemini for large context
│   │       ├── precise-code.sh        # Claude for code generation
│   │       └── security-review.sh     # Multi-model security
│   ├── scripts/
│   │   ├── install.sh                 # Interactive installer (6-step wizard)
│   │   ├── reconfigure.sh             # Reconfiguration tool (NEW v2.1)
│   │   ├── init-project.sh            # Initialize new project
│   │   └── utils/
│   ├── logs/                          # Logging directory (NEW v2.1)
│   │   ├── context-sharing.log        # Model collaboration logs
│   │   └── .gitkeep
│   ├── temp/                          # Temporary handoff files (NEW v2.1)
│   │   └── .gitkeep
│   ├── docs/
│   │   ├── CONTEXT-SHARING.md         # How models collaborate (NEW v2.1)
│   │   ├── COMPONENTS-MANIFEST.md     # Source attribution
│   │   └── LEGACY-IMPLEMENTATION-PLAN.md
│   └── .gitignore                     # Protects .env, logs (NEW v2.1)
├── CLAUDE.md -> .dev-aid/providers/claude/CLAUDE.md     # Symlink (if enabled)
├── GEMINI.md -> .dev-aid/providers/gemini/GEMINI.md     # Symlink (if enabled)
├── OPENAI.md -> .dev-aid/providers/openai/OPENAI.md     # Symlink (if enabled)
└── README.md                          # Project-specific readme
```

---

## 🔧 Configuration Wizard (Interactive Installer)

### Questions During Installation

#### 1. **Standing Context Budget**
```
How much token budget for standing context?

A. Minimal (~500 tokens)
   - Fastest startup (<1s)
   - Only essential auto-loads
   - Best for: Quick tasks, small projects

B. Balanced (~1,000 tokens)  [RECOMMENDED]
   - Fast startup (~2s)
   - Memory bank + 2 essential skills
   - Best for: Most projects

C. Comprehensive (~1,500 tokens)
   - Slower startup (~3s)
   - Full memory bank + 3-4 skills
   - Best for: Complex enterprise projects

Your choice [A/B/C]:
```

#### 2. **Auto-Activation Strategy**
```
How should Dev-AID auto-load skills/capabilities?

A. Suggest Only (0 tokens)
   - No auto-loading
   - Manual activation only
   - Best for: Explicit control

B. Smart Load (AI decides)
   - AI analyzes context
   - Auto-loads relevant skills
   - Best for: Experienced users

C. Conservative Load (file patterns)  [RECOMMENDED]
   - Pattern matching (*.test.* → TDD)
   - Max 2-3 skills per prompt
   - Best for: Predictable workflows

Your choice [A/B/C]:
```

#### 3. **AI Provider Selection**
```
Which AI providers do you have access to?
(Select all that apply)

1. Claude (Anthropic)
   • Strengths: Precise code generation, security analysis
   • Context: 200K tokens
   • Cost: $3/1M tokens (Sonnet)
   Enable Claude? [Y/n]:

2. Gemini (Google)
   • Strengths: Massive context (2M tokens), fast processing
   • Context: 2,000K tokens
   • Cost: $0.075/1M tokens (Flash)
   Enable Gemini? [y/N]:

3. OpenAI (ChatGPT)
   • Strengths: General tasks, documentation, versatile
   • Context: 128K tokens
   • Cost: $5/1M tokens (GPT-4o)
   Enable OpenAI? [y/N]:

4. OpenRouter (Multi-provider)
   • Strengths: Access to multiple models, automatic routing
   Enable OpenRouter? [y/N]:
```

#### 4. **Orchestration Mode**
```
How should AI models work together?

A. None (Manual Selection)     [NEW v2.1]
   • You explicitly choose which AI for each task
   • No automatic routing
   • Best for: Maximum control, single AI usage

B. Solo Mode
   • Single default model handles all tasks
   • Simple, straightforward
   • Best for: Single AI subscription

C. Ensemble Mode  [RECOMMENDED for multi-AI]
   • Automatic routing based on task type
   • Cost optimization
   • Best for: Multiple AI subscriptions

D. Challenger Mode
   • Primary generates, challenger reviews
   • Multi-perspective analysis
   • Best for: High-security, critical code

Your choice [A/B/C/D]:
```

#### 5. **Model Assignment per Task Type** [NEW v2.1]
```
Assign AI models to specific task types for optimal performance.

1. Code Generation & Refactoring
   (Writing code, refactoring, implementing features)

   Available models:
   1) claude-sonnet-4.5 (Balanced, $3/1M)
   2) claude-opus-4 (Most capable, $15/1M)
   3) gemini-2.0-flash (2M context, $0.075/1M)

   Select model [1-3]: _

2. Massive Context Analysis (if Gemini enabled)
   (Reading 100+ files, repository-wide analysis)

   → gemini-2.0-flash (recommended)

3. Documentation & Explanations
   (Writing READMEs, docs, code comments)

   → gpt-4o (if OpenAI enabled) or claude-sonnet-4.5

4. Security Analysis & Audits
   (Security reviews, vulnerability detection)

   → claude-sonnet-4.5 (recommended)

5. Challenger Model (if Challenger mode selected)
   (Reviews and challenges primary model's output)

   → gemini-2.0-pro or other enabled model
```

#### 6. **API Key Configuration** [NEW v2.1]
```
Enter API keys for your enabled providers.
💡 Tip: Keys are stored in .dev-aid/config/.env (gitignored)

Claude (Anthropic) API Key
Get your key from: https://console.anthropic.com/
ANTHROPIC_API_KEY: ********
✓ Claude API key saved

Gemini (Google) API Key (if enabled)
Get your key from: https://aistudio.google.com/app/apikey
GOOGLE_API_KEY: ********
✓ Gemini API key saved

OpenAI API Key (if enabled)
Get your key from: https://platform.openai.com/api-keys
OPENAI_API_KEY: ********
✓ OpenAI API key saved

Note: Only prompts for providers selected in Step 3!
```

---

## 🎭 Orchestration Modes

### Solo Mode
```yaml
mode: solo
default_model: claude-sonnet-4.5
routing: simple
```

**Behavior**:
- All requests → default model
- Simplest configuration
- Lowest cost

### Ensemble Mode
```yaml
mode: ensemble
routing_strategy: capability_based

capabilities:
  massive_context:
    model: gemini-2.0-flash
    trigger: file_count > 50 || total_lines > 10000

  code_generation:
    model: claude-sonnet-4.5
    trigger: task_type == "code" || tools_needed

  documentation:
    model: gpt-4-turbo
    trigger: task_type == "docs" || markdown_files

  quick_questions:
    model: claude-haiku
    trigger: response_time < 2s_required
```

**Behavior**:
- Router analyzes task
- Selects best model for capability
- Can chain models (Gemini reads → Claude writes)

### Challenger Mode
```yaml
mode: challenger
primary_model: claude-sonnet-4.5
challenger_model: gemini-2.0-pro

challenge_triggers:
  - security_sensitive: true
  - refactoring: major
  - performance_critical: true
  - new_architecture: true

challenge_workflow:
  1. Primary generates solution
  2. Challenger reviews + critiques
  3. Primary revises (optional)
  4. User sees both perspectives
```

**Behavior**:
- Primary model generates
- Challenger reviews for:
  - Security vulnerabilities
  - Performance issues
  - Edge cases
  - Alternative approaches
- User gets multi-perspective analysis

---

## 🔌 Provider Integration

### Universal Context Format

Each provider gets a symlinked context file in root:

**CLAUDE.md** (symlinked from `.dev-aid/providers/claude/CLAUDE.md`)
```markdown
# Development Context for Claude

## Current Project
[Auto-populated from .dev-aid/memory-bank/activeContext.md]

## Your Role
You are working with Dev-AID, a multi-model AI orchestrator.
Your specialty: Precise code generation and analysis.

## Available Tools
[Provider-specific tools: Read, Edit, Write, Bash, etc.]

## Memory Bank
See .dev-aid/memory-bank/ for:
- patterns.md - Proven code patterns
- decisions.md - ADRs
- security.md - Security context
[...]
```

**GEMINI.md** (symlinked from `.dev-aid/providers/gemini/GEMINI.md`)
```markdown
# Development Context for Gemini

## Current Project
[Auto-populated from .dev-aid/memory-bank/activeContext.md]

## Your Role
You are working with Dev-AID, a multi-model AI orchestrator.
Your specialty: Massive context analysis (2M tokens).

## When to Use You
- Repository-wide analysis
- Large file processing
- Context-heavy research

## Memory Bank
See .dev-aid/memory-bank/ for shared context.
```

**OPENAI.md** (symlinked from `.dev-aid/providers/openai/OPENAI.md`)
```markdown
# Development Context for OpenAI

## Current Project
[Auto-populated from .dev-aid/memory-bank/activeContext.md]

## Your Role
You are working with Dev-AID, a multi-model AI orchestrator.
Your specialty: General development tasks and documentation.

## Memory Bank
See .dev-aid/memory-bank/ for shared context.
```

---

## 📦 Installation Flow

```bash
# Download Dev-AID
git clone https://github.com/user/dev-aid
cd dev-aid

# Run interactive installer
./install.sh

# Installer workflow:
# 1. Welcome + explanation
# 2. Configuration wizard (5 questions above)
# 3. API key collection (secure)
# 4. Provider setup (symlinks, configs)
# 5. Test connections
# 6. Generate .dev-aid/ structure
# 7. Initialize memory bank
# 8. Done!
```

### Install Script Features

```bash
#!/bin/bash
# install.sh

# 1. Check prerequisites
check_dependencies() {
  # git, curl, jq, etc.
}

# 2. Configuration wizard
run_wizard() {
  # Interactive prompts
  # Save to .dev-aid/config/settings.json
}

# 3. Provider setup
setup_providers() {
  # For each enabled provider:
  # - Create .dev-aid/providers/{provider}/
  # - Generate context file
  # - Create symlink to root
  # - Test API connection
}

# 4. Orchestration setup
setup_orchestration() {
  # Based on mode selection:
  # - Configure router
  # - Set up workflows
}

# 5. Memory bank initialization
init_memory_bank() {
  # Create 7 memory bank files
  # Populate with templates
}

# 6. Final touches
finalize() {
  # Create .gitignore entries
  # Initialize hooks (if Claude Code detected)
  # Display summary
}
```

---

## 🧠 Router Implementation

### router.sh (Orchestration Engine)

```bash
#!/bin/bash
# .dev-aid/orchestration/router.sh

DEV_AID_CONFIG=".dev-aid/config"

# Load configuration
source "$DEV_AID_CONFIG/settings.json"
source "$DEV_AID_CONFIG/models.json"
source "$DEV_AID_CONFIG/orchestration.json"

# Router function
route_task() {
  local task_type="$1"
  local context_size="$2"
  local security_level="$3"

  case "$ORCHESTRATION_MODE" in
    solo)
      echo "$DEFAULT_MODEL"
      ;;

    ensemble)
      # Capability-based routing
      if [ "$context_size" -gt 100000 ]; then
        echo "gemini-2.0-flash"  # Massive context
      elif [ "$task_type" = "code" ]; then
        echo "claude-sonnet-4.5"  # Precise code
      elif [ "$task_type" = "docs" ]; then
        echo "gpt-4-turbo"  # Documentation
      else
        echo "$DEFAULT_MODEL"
      fi
      ;;

    challenger)
      # Primary + challenger
      echo "$PRIMARY_MODEL,$CHALLENGER_MODEL"
      ;;
  esac
}

# Execute with selected model(s)
execute_with_model() {
  local model="$1"
  local prompt="$2"

  # Call appropriate API
  case "$model" in
    claude-*)
      call_claude_api "$model" "$prompt"
      ;;
    gemini-*)
      call_gemini_api "$model" "$prompt"
      ;;
    gpt-*)
      call_openai_api "$model" "$prompt"
      ;;
  esac
}

# API wrappers
call_claude_api() { ... }
call_gemini_api() { ... }
call_openai_api() { ... }
```

---

## 📊 Configuration Files

### .dev-aid/config/settings.json
```json
{
  "dev_aid_version": "2.0.0",
  "project_name": "my-project",

  "standing_context_budget": "balanced",
  "standing_context_tokens": 1000,

  "auto_activation": "conservative",
  "auto_load_max_skills": 3,

  "orchestration_mode": "ensemble",

  "enabled_providers": ["claude", "gemini"],

  "default_model": "claude-sonnet-4.5",

  "memory_bank": {
    "auto_load": ["activeContext.md"],
    "on_demand": ["patterns.md", "decisions.md", "security.md"]
  }
}
```

### .dev-aid/config/models.json
```json
{
  "claude": {
    "enabled": true,
    "api_key_env": "ANTHROPIC_API_KEY",
    "models": {
      "sonnet": "claude-sonnet-4-5",
      "opus": "claude-opus-4",
      "haiku": "claude-haiku-4"
    },
    "default": "sonnet",
    "capabilities": ["code", "analysis", "security"]
  },

  "gemini": {
    "enabled": true,
    "api_key_env": "GOOGLE_API_KEY",
    "models": {
      "flash": "gemini-2.0-flash",
      "pro": "gemini-2.0-pro"
    },
    "default": "flash",
    "capabilities": ["massive_context", "analysis"]
  },

  "openai": {
    "enabled": false,
    "api_key_env": "OPENAI_API_KEY",
    "models": {
      "gpt4": "gpt-4-turbo",
      "gpt35": "gpt-3.5-turbo"
    },
    "default": "gpt4",
    "capabilities": ["general", "docs"]
  }
}
```

### .dev-aid/config/orchestration.json
```json
{
  "mode": "ensemble",

  "solo": {
    "model": "claude-sonnet-4.5"
  },

  "ensemble": {
    "routing_strategy": "capability_based",
    "capabilities": {
      "massive_context": {
        "model": "gemini-2.0-flash",
        "triggers": {
          "file_count_gt": 50,
          "total_lines_gt": 10000,
          "context_tokens_gt": 100000
        }
      },
      "code_generation": {
        "model": "claude-sonnet-4.5",
        "triggers": {
          "task_type": ["code", "refactor", "debug"],
          "tools_needed": true
        }
      },
      "documentation": {
        "model": "gpt-4-turbo",
        "triggers": {
          "task_type": ["docs", "readme", "comments"],
          "markdown_files": true
        }
      }
    }
  },

  "challenger": {
    "primary_model": "claude-sonnet-4.5",
    "challenger_model": "gemini-2.0-pro",
    "challenge_triggers": [
      "security_sensitive",
      "performance_critical",
      "major_refactoring",
      "new_architecture"
    ],
    "workflow": "sequential"
  }
}
```

---

## 🔄 Migration from Current Setup

### Rename & Restructure

```bash
# 1. Rename directory
mv elite-claude-dev dev-aid

# 2. Move files to new structure
mkdir -p dev-aid/.dev-aid/{config,providers,memory-bank,orchestration,scripts,docs}

# 3. Move .claude/ to providers/claude/
mv dev-aid/.claude dev-aid/.dev-aid/providers/claude/.claude

# 4. Move memory-bank/CLAUDE-*.md to memory-bank/*.md (remove CLAUDE- prefix)
for file in dev-aid/memory-bank/CLAUDE-*.md; do
  mv "$file" "${file/CLAUDE-/}"
done
mv dev-aid/memory-bank dev-aid/.dev-aid/memory-bank

# 5. Create provider context files
# (Will be done programmatically)

# 6. Update all references in files
# (Will be done with Edit tool)
```

---

## 📝 Key Updates Required

### Files to Update:
1. ✅ Rename `elite-claude-dev/` → `dev-aid/`
2. ✅ Restructure to `.dev-aid/` folder
3. ✅ Create multi-provider support
4. ✅ Create orchestration modes
5. ✅ Create interactive installer
6. ✅ Update all documentation
7. ✅ Create context symlinks
8. ✅ Update COMPONENTS-MANIFEST.md

---

## 🎯 Success Criteria

- [ ] User can run `./install.sh` and answer 5 questions
- [ ] Installation creates `.dev-aid/` with all structure
- [ ] Provider symlinks (CLAUDE.md, GEMINI.md) work correctly
- [ ] Router can select appropriate model based on task
- [ ] All three orchestration modes work
- [ ] Documentation is comprehensive and clear
- [ ] Zero breaking changes to existing repos (everything in `.dev-aid/`)

---

## 🚀 Next Steps

1. Create new dev-aid structure
2. Implement install.sh wizard
3. Create router and orchestration modes
4. Generate provider-specific context files
5. Update all documentation
6. Test installation flow
7. Commit and push
