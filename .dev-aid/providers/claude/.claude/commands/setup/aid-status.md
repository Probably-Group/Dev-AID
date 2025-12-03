---
name: aid-status
description: Show current Dev-AID configuration and setup status
category: setup
author: Dev-AID Team
version: 1.0.0
---

# Dev-AID Status & Configuration

Display comprehensive information about your current Dev-AID setup.

## What This Command Shows

1. **Orchestration Configuration**
   - Current orchestration mode (None, Solo, Ensemble, Challenger)
   - Enabled providers (Claude, Gemini, OpenAI, OpenRouter)
   - Task-to-model mappings

2. **Context Budget**
   - Standing context budget setting
   - Estimated token usage
   - Auto-activation strategy

3. **Provider Context Files**
   - Which provider context files exist (CLAUDE.md, GEMINI.md, OPENAI.md)
   - Location and status of symlinks
   - Whether files need customization

4. **Memory Bank Status**
   - Which memory bank files exist
   - File sizes and last modified dates
   - Completeness check

5. **API Keys**
   - Which API keys are configured (masked for security)
   - Which providers are ready to use

6. **File Locations**
   - Configuration directory
   - Memory bank directory
   - Provider directories

## Usage

Simply run:
```
/aid-status
```

## Output

You should see a formatted report like:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Dev-AID Configuration Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎭 Orchestration
   Mode:              ensemble
   Enabled Providers: claude, gemini

   Task Assignments:
   • code_generation  → claude-sonnet-4.5
   • massive_context  → gemini-2.0-flash
   • documentation    → claude-sonnet-4.5
   • security         → claude-sonnet-4.5

📊 Context Budget
   Standing Context:  balanced (~1,000 tokens)
   Auto-Activation:   smart

📁 Provider Context Files
   ✅ CLAUDE.md       → .dev-aid/providers/claude/CLAUDE.md
   ✅ GEMINI.md       → .dev-aid/providers/gemini/GEMINI.md
   ⚠️  OPENAI.md      (not configured)

🧠 Memory Bank
   ✅ activeContext.md   (1.2 KB, updated 2 hours ago)
   ✅ decisions.md       (3.5 KB, updated 1 day ago)
   ✅ patterns.md        (2.8 KB, updated 3 days ago)
   ⚠️  security.md       (empty - needs content)
   ⚠️  performance.md    (empty - needs content)
   ✅ testing.md         (1.9 KB, updated 1 day ago)
   ❌ chaos.md           (missing)

🔑 API Keys
   ✅ ANTHROPIC_API_KEY  (configured)
   ✅ GOOGLE_API_KEY     (configured)
   ❌ OPENAI_API_KEY     (not configured)

📂 File Locations
   Config:      .dev-aid/config/
   Memory Bank: .dev-aid/memory-bank/
   Providers:   .dev-aid/providers/

💡 Recommendations
   • Complete CLAUDE.md customization with project-specific details
   • Add content to security.md for security context
   • Add content to performance.md for performance baselines
   • Create chaos.md if you plan to run chaos experiments

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Implementation

### Step 1: Read Configuration Files

```bash
# Read settings.json for orchestration config
cat .dev-aid/config/settings.json

# Read .env for API keys (mask values)
cat .dev-aid/config/.env
```

### Step 2: Check Provider Context Files

```bash
# Check which context files exist
ls -lh .dev-aid/providers/claude/CLAUDE.md 2>/dev/null
ls -lh .dev-aid/providers/gemini/GEMINI.md 2>/dev/null
ls -lh .dev-aid/providers/openai/OPENAI.md 2>/dev/null

# Check symlinks at project root
ls -lh ../CLAUDE.md 2>/dev/null
ls -lh ../GEMINI.md 2>/dev/null
ls -lh ../OPENAI.md 2>/dev/null
```

### Step 3: Check Memory Bank

```bash
# List all memory bank files with sizes
ls -lh .dev-aid/memory-bank/*.md 2>/dev/null

# Check which files are empty
for file in .dev-aid/memory-bank/*.md; do
    if [ ! -s "$file" ]; then
        echo "$file is empty"
    fi
done
```

### Step 4: Check API Keys (Masked)

```bash
# Check which keys exist in .env (don't show values)
if [ -f .dev-aid/config/.env ]; then
    grep -E "^[A-Z]" .dev-aid/config/.env | sed 's/=.*/=***/'
fi
```

### Step 5: Generate Recommendations

Based on the findings, provide actionable recommendations:

- If provider context files exist but have [CUSTOMIZE] tags → recommend customization
- If memory bank files are empty → recommend adding content
- If API keys are missing → recommend adding them
- If orchestration mode is "none" but multiple providers enabled → suggest switching to ensemble

## When to Use This Command

Run `/aid-status` when:

1. **After Installation**
   - Verify setup completed correctly
   - Check what needs customization

2. **Before Major Changes**
   - Review current config before reconfiguring
   - Understand current setup

3. **Troubleshooting**
   - Verify providers are configured
   - Check API keys are set
   - Confirm memory bank is populated

4. **Team Onboarding**
   - Show new developers the current setup
   - Help them understand Dev-AID configuration

5. **Regular Checkups**
   - Monthly review of configuration
   - Ensure everything is up to date

## Next Steps After Running Status

Based on the status output:

### If Files Need Customization
```bash
# Edit context files
vim .dev-aid/providers/claude/CLAUDE.md
vim .dev-aid/providers/gemini/GEMINI.md
```

### If Memory Bank is Incomplete
```bash
# Run analysis to populate memory bank
/aid-analyze
```

### If API Keys Missing
```bash
# Edit .env file
vim .dev-aid/config/.env

# Add missing keys:
# ANTHROPIC_API_KEY=sk-ant-...
# GOOGLE_API_KEY=...
# OPENAI_API_KEY=sk-...
```

### If Reconfiguration Needed
```bash
# Run reconfiguration script
.dev-aid/scripts/reconfigure.sh
```

## Notes

- API key values are NEVER displayed (masked as ***)
- File sizes shown in human-readable format (KB, MB)
- Relative timestamps (e.g., "2 hours ago")
- Color-coded output (green=good, yellow=warning, red=missing)

---

**This command provides visibility into your Dev-AID setup without making any changes.**
