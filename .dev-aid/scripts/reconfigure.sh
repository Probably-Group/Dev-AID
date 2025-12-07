#!/bin/bash

# Dev-AID Reconfiguration Script
# Change settings without breaking existing memory/context

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEV_AID_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_DIR="$DEV_AID_ROOT/.dev-aid/config"
BACKUP_DIR="$DEV_AID_ROOT/.dev-aid/config/backups"

print_color() {
    local color="$1"
    shift
    echo -e "${color}$*${NC}"
}

print_header() {
    echo ""
    print_color "$CYAN" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_color "$CYAN" "$1"
    print_color "$CYAN" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# Backup existing configuration
backup_config() {
    print_header "Backing Up Current Configuration"

    mkdir -p "$BACKUP_DIR"
    local backup_timestamp
    backup_timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_path="$BACKUP_DIR/config_$backup_timestamp"

    mkdir -p "$backup_path"

    # Backup configuration files (but not API keys for security)
    cp "$CONFIG_DIR/settings.json" "$backup_path/" 2>/dev/null || true
    cp "$CONFIG_DIR/orchestration.json" "$backup_path/" 2>/dev/null || true
    cp "$CONFIG_DIR/models.json" "$backup_path/" 2>/dev/null || true
    cp "$CONFIG_DIR/skill-rules.json" "$backup_path/" 2>/dev/null || true

    print_color "$GREEN" "✓ Configuration backed up to: $backup_path"
    print_color "$YELLOW" "  (API keys NOT backed up for security)"

    echo "$backup_path" > "$BACKUP_DIR/.latest"
}

# Restore from backup
restore_from_backup() {
    if [ ! -f "$BACKUP_DIR/.latest" ]; then
        print_color "$RED" "No backups found!"
        return 1
    fi

    local latest_backup
    latest_backup=$(cat "$BACKUP_DIR/.latest")

    if [ ! -d "$latest_backup" ]; then
        print_color "$RED" "Latest backup not found: $latest_backup"
        return 1
    fi

    print_color "$CYAN" "Restoring from: $latest_backup"

    cp "$latest_backup/settings.json" "$CONFIG_DIR/" 2>/dev/null || true
    cp "$latest_backup/orchestration.json" "$CONFIG_DIR/" 2>/dev/null || true
    cp "$latest_backup/models.json" "$CONFIG_DIR/" 2>/dev/null || true
    cp "$latest_backup/skill-rules.json" "$CONFIG_DIR/" 2>/dev/null || true

    print_color "$GREEN" "✓ Configuration restored!"
}

# Show current configuration
show_current_config() {
    print_header "Current Configuration"

    if [ ! -f "$CONFIG_DIR/settings.json" ]; then
        print_color "$RED" "No configuration found. Run install.sh first."
        exit 1
    fi

    if command -v jq &> /dev/null; then
        echo "Standing Context:     $(jq -r '.standing_context_budget' "$CONFIG_DIR/settings.json") (~$(jq -r '.standing_context_tokens' "$CONFIG_DIR/settings.json") tokens)"
        echo "Auto-Activation:      $(jq -r '.auto_activation' "$CONFIG_DIR/settings.json")"
        echo "Orchestration Mode:   $(jq -r '.orchestration_mode' "$CONFIG_DIR/settings.json")"
        echo "Enabled Providers:    $(jq -r '.enabled_providers | join(", ")' "$CONFIG_DIR/settings.json")"

        local mapping=$(jq -r '.task_model_mapping' "$CONFIG_DIR/settings.json")
        if [ "$mapping" != "null" ] && [ "$mapping" != "{}" ]; then
            echo ""
            echo "Model Assignments:"
            jq -r '.task_model_mapping | to_entries[] | "  \(.key): \(.value)"' "$CONFIG_DIR/settings.json"
        fi
    else
        cat "$CONFIG_DIR/settings.json"
    fi

    echo ""
}

# Main reconfiguration menu
reconfigure_menu() {
    while true; do
        print_header "Dev-AID Reconfiguration"

        echo "What would you like to change?"
        echo ""
        echo "  1) Standing Context Budget"
        echo "  2) Auto-Activation Strategy"
        echo "  3) Orchestration Mode"
        echo "  4) Enable/Disable Providers"
        echo "  5) Model Assignments"
        echo "  6) API Keys"
        echo "  7) View Current Configuration"
        echo "  8) Restore from Backup"
        echo "  9) Exit"
        echo ""
        read -p "Select option [1-9]: " choice

        case $choice in
            1) change_context_budget ;;
            2) change_auto_activation ;;
            3) change_orchestration_mode ;;
            4) change_providers ;;
            5) change_model_assignments ;;
            6) change_api_keys ;;
            7) show_current_config ;;
            8) restore_from_backup ;;
            9)
                print_color "$GREEN" "Configuration saved!"
                echo ""
                print_color "$YELLOW" "💡 Restart your AI session for changes to take effect."
                exit 0
                ;;
            *)
                print_color "$RED" "Invalid choice. Please select 1-9."
                ;;
        esac
    done
}

# Change functions (simplified versions of installer functions)
change_context_budget() {
    print_header "Change Standing Context Budget"

    echo "Current: $(jq -r '.standing_context_budget' "$CONFIG_DIR/settings.json")"
    echo ""
    echo "A) Minimal (~500 tokens)"
    echo "B) Balanced (~1,000 tokens)"
    echo "C) Comprehensive (~1,500 tokens)"
    echo ""
    read -p "New choice [A/B/C] or Enter to skip: " choice

    case $choice in
        [Aa]) update_setting "standing_context_budget" "minimal" && update_setting "standing_context_tokens" "500" ;;
        [Bb]) update_setting "standing_context_budget" "balanced" && update_setting "standing_context_tokens" "1000" ;;
        [Cc]) update_setting "standing_context_budget" "comprehensive" && update_setting "standing_context_tokens" "1500" ;;
        "") print_color "$YELLOW" "Skipped" ;;
        *) print_color "$RED" "Invalid choice" ;;
    esac
}

change_auto_activation() {
    print_header "Change Auto-Activation Strategy"

    echo "Current: $(jq -r '.auto_activation' "$CONFIG_DIR/settings.json")"
    echo ""
    echo "A) Suggest Only"
    echo "B) Conservative Load"
    echo "C) Smart Load"
    echo ""
    read -p "New choice [A/B/C] or Enter to skip: " choice

    case $choice in
        [Aa]) update_setting "auto_activation" "suggest" ;;
        [Bb]) update_setting "auto_activation" "conservative" ;;
        [Cc]) update_setting "auto_activation" "smart" ;;
        "") print_color "$YELLOW" "Skipped" ;;
        *) print_color "$RED" "Invalid choice" ;;
    esac
}

change_orchestration_mode() {
    print_header "Change Orchestration Mode"

    echo "Current: $(jq -r '.orchestration_mode' "$CONFIG_DIR/settings.json")"
    echo ""
    echo "A) None (Manual)"
    echo "B) Solo"
    echo "C) Ensemble"
    echo "D) Challenger"
    echo ""
    read -p "New choice [A/B/C/D] or Enter to skip: " choice

    case $choice in
        [Aa]) update_setting "orchestration_mode" "none" ;;
        [Bb]) update_setting "orchestration_mode" "solo" ;;
        [Cc]) update_setting "orchestration_mode" "ensemble" ;;
        [Dd]) update_setting "orchestration_mode" "challenger" ;;
        "") print_color "$YELLOW" "Skipped" ;;
        *) print_color "$RED" "Invalid choice" ;;
    esac
}

# Detect project information for auto-populating context files
detect_project_info() {
    local project_root="$DEV_AID_ROOT/.."

    # Detect project name
    PROJECT_NAME=$(basename "$(cd "$project_root" && pwd)")

    # Initialize variables
    FRONTEND=""
    BACKEND=""
    DATABASE=""
    DEPLOYMENT=""
    DEPENDENCIES=""

    # Check for JavaScript/TypeScript frontend
    if [ -f "$project_root/package.json" ]; then
        if command -v jq &> /dev/null; then
            local deps
            deps=$(jq -r '.dependencies | keys[]' "$project_root/package.json" 2>/dev/null)
            local dev_deps
            dev_deps=$(jq -r '.devDependencies | keys[]' "$project_root/package.json" 2>/dev/null)
            local all_deps="$deps $dev_deps"

            # Detect frontend frameworks
            echo "$all_deps" | grep -q "react" && FRONTEND="React"
            echo "$all_deps" | grep -q "vue" && FRONTEND="Vue.js"
            echo "$all_deps" | grep -q "@angular/core" && FRONTEND="Angular"
            echo "$all_deps" | grep -q "svelte" && FRONTEND="Svelte"
            echo "$all_deps" | grep -q "next" && FRONTEND="Next.js"
            echo "$all_deps" | grep -q "@remix-run" && FRONTEND="Remix"

            # Detect backend frameworks
            echo "$all_deps" | grep -q "express" && BACKEND="Node.js/Express"
            echo "$all_deps" | grep -q "fastify" && BACKEND="Node.js/Fastify"
            echo "$all_deps" | grep -q "@nestjs/core" && BACKEND="NestJS"
            echo "$all_deps" | grep -q "koa" && BACKEND="Node.js/Koa"

            # Detect databases
            echo "$all_deps" | grep -q "mongoose" && DATABASE="MongoDB (Mongoose)"
            echo "$all_deps" | grep -q "pg\|postgres" && DATABASE="PostgreSQL"
            echo "$all_deps" | grep -q "mysql" && DATABASE="MySQL"
            echo "$all_deps" | grep -q "sqlite3" && DATABASE="SQLite"
            echo "$all_deps" | grep -q "prisma" && DATABASE="${DATABASE:+$DATABASE, }Prisma ORM"
            echo "$all_deps" | grep -q "typeorm" && DATABASE="${DATABASE:+$DATABASE, }TypeORM"

            # Get top 5 dependencies for reference
            DEPENDENCIES=$(echo "$deps" | head -5 | tr '\n' ', ' | sed 's/, $//')
        fi
    fi

    # Check for Python backend
    if [ -f "$project_root/requirements.txt" ]; then
        if grep -qi "flask" "$project_root/requirements.txt"; then BACKEND="Python/Flask"; fi
        if grep -qi "django" "$project_root/requirements.txt"; then BACKEND="Python/Django"; fi
        if grep -qi "fastapi" "$project_root/requirements.txt"; then BACKEND="Python/FastAPI"; fi

        # Python databases
        if grep -qi "psycopg2\|asyncpg" "$project_root/requirements.txt"; then DATABASE="PostgreSQL"; fi
        if grep -qi "pymongo" "$project_root/requirements.txt"; then DATABASE="MongoDB"; fi
        if grep -qi "sqlalchemy" "$project_root/requirements.txt"; then DATABASE="${DATABASE:+$DATABASE, }SQLAlchemy ORM"; fi
    fi

    # Check for Go backend
    if [ -f "$project_root/go.mod" ]; then
        BACKEND="Go"
        if grep -q "gin-gonic/gin" "$project_root/go.mod"; then BACKEND="Go/Gin"; fi
        if grep -q "gofiber/fiber" "$project_root/go.mod"; then BACKEND="Go/Fiber"; fi
        if grep -q "gorilla/mux" "$project_root/go.mod"; then BACKEND="Go/Gorilla Mux"; fi
    fi

    # Check for Rust backend
    if [ -f "$project_root/Cargo.toml" ]; then
        BACKEND="Rust"
        if grep -q "actix-web" "$project_root/Cargo.toml"; then BACKEND="Rust/Actix"; fi
        if grep -q "rocket" "$project_root/Cargo.toml"; then BACKEND="Rust/Rocket"; fi
        if grep -q "axum" "$project_root/Cargo.toml"; then BACKEND="Rust/Axum"; fi
    fi

    # Check for deployment setup
    if [ -f "$project_root/Dockerfile" ]; then
        DEPLOYMENT="Docker"
    fi
    if [ -f "$project_root/docker-compose.yml" ]; then
        DEPLOYMENT="${DEPLOYMENT:+$DEPLOYMENT, }Docker Compose"
    fi
    if [ -d "$project_root/.github/workflows" ]; then
        DEPLOYMENT="${DEPLOYMENT:+$DEPLOYMENT, }GitHub Actions"
    fi
    if [ -f "$project_root/.gitlab-ci.yml" ]; then
        DEPLOYMENT="${DEPLOYMENT:+$DEPLOYMENT, }GitLab CI"
    fi

    # Set defaults if nothing detected
    PROJECT_NAME="${PROJECT_NAME:-my-project}"
    FRONTEND="${FRONTEND:-Not detected}"
    BACKEND="${BACKEND:-Not detected}"
    DATABASE="${DATABASE:-Not detected}"
    DEPLOYMENT="${DEPLOYMENT:-Not detected}"
    DEPENDENCIES="${DEPENDENCIES:-None detected}"
}

# Generate CLAUDE.md template
generate_claude_template() {
    # Detect project info
    detect_project_info

    cat > "$1" <<EOF
# Development Context for Claude

## 🤖 You Are Part of Dev-AID

**Dev-AID** (Development AI Driver) is a multi-model AI orchestration system.
You are working alongside other AI models (Gemini, OpenAI, etc.) to provide
state-of-the-art development assistance.

## 🎯 Your Role & Specialty

As **Claude Sonnet 4.5**, your primary capabilities:
- **Precise code generation** - Writing clean, efficient code
- **Deep code analysis** - Understanding complex codebases
- **Security expertise** - Identifying vulnerabilities, OWASP coverage
- **Reasoning & planning** - Breaking down complex problems

You are the **primary code generator** in this setup.

## 📋 Current Project Context

**Project**: $PROJECT_NAME

### Tech Stack
- Frontend: $FRONTEND
- Backend: $BACKEND
- Database: $DATABASE
- Deployment: $DEPLOYMENT

### Active Sprint Goals
See: \`.dev-aid/memory-bank/activeContext.md\`

## 🧠 Memory Bank (Institutional Knowledge)

The project maintains a **Memory Bank** for persistent context across sessions:

| File | Purpose | Auto-Load |
|------|---------|-----------|
| \`activeContext.md\` | Current sprint/session state | ✅ Yes |
| \`patterns.md\` | Proven code patterns & anti-patterns | On-demand |
| \`decisions.md\` | Architecture Decision Records (ADRs) | On-demand |
| \`security.md\` | Security context, OWASP coverage | On-demand |
| \`performance.md\` | Performance baselines & bottlenecks | On-demand |
| \`testing.md\` | Test strategies, coverage goals, TDD | On-demand |
| \`chaos.md\` | Chaos experiments, resilience tests | On-demand |

**Location**: \`.dev-aid/memory-bank/\`

## 🛡️ Security & Quality Standards

This project follows elite development standards:

### TDD (Test-Driven Development)
When writing code:
1. Write test first
2. Implement minimal code to pass
3. Refactor for quality

### DevSecOps
- **Never commit secrets** (API keys, passwords, tokens)
- **Validate all inputs** at system boundaries
- **Follow OWASP Top 10** guidelines
- See \`.dev-aid/memory-bank/security.md\` for context

### Code Quality
- **No code smells** (long functions, deep nesting, magic numbers)
- **Follow patterns** in \`.dev-aid/memory-bank/patterns.md\`
- **Document decisions** in \`.dev-aid/memory-bank/decisions.md\`

## 🎓 Best Practices

1. **Always check Memory Bank first** before making decisions
2. **Update Memory Bank** when you learn something new
3. **Follow TDD** for code changes
4. **Run security scans** before commits
5. **Document architectural decisions** in ADR format
6. **Stay within token budgets** for performance

---

**Auto-detected project info** - Customize as needed!
EOF
}

# Generate GEMINI.md template
generate_gemini_template() {
    # Detect project info
    detect_project_info

    cat > "$1" <<EOF
# Development Context for Gemini

## 🤖 You Are Part of Dev-AID

**Dev-AID** (Development AI Driver) is a multi-model AI orchestration system.
You are working alongside other AI models (Claude, OpenAI, etc.) to provide
state-of-the-art development assistance.

## 🎯 Your Role & Specialty

As **Gemini 2.0 Flash/Pro**, your primary capabilities:
- **Massive context analysis** - 1M-2M token window for full repository scans
- **Cross-file refactoring** - Understanding dependencies across entire codebase
- **Pattern detection** - Finding similarities and inconsistencies at scale
- **Multi-file understanding** - Holistic codebase comprehension

You are the **massive context specialist** in this setup.

## 📋 Current Project Context

**Project**: $PROJECT_NAME

### Repository Structure
\`\`\`
/
├── dev-aid/              # Dev-AID working installation
├── dev-aid-standalone/   # Distribution package
├── claude-code-tresor/   # Tresor commands reference
└── [other directories]
\`\`\`

### Tech Stack
- Frontend: $FRONTEND
- Backend: $BACKEND
- Database: $DATABASE
- Deployment: $DEPLOYMENT

### Key Dependencies
$DEPENDENCIES

## 🧠 Memory Bank (Institutional Knowledge)

The project maintains a **Memory Bank** for persistent context across sessions:

| File | Purpose |
|------|---------|
| `activeContext.md` | Current sprint/session state |
| `patterns.md` | Proven code patterns & anti-patterns |
| `decisions.md` | Architecture Decision Records (ADRs) |
| `security.md` | Security context, OWASP coverage |
| `performance.md` | Performance baselines & bottlenecks |
| `testing.md` | Test strategies, coverage goals |
| `chaos.md` | Chaos experiments, resilience tests |

**Location**: \`.dev-aid/memory-bank/\`

## 💡 When to Use Your Strengths

### Ideal Tasks for Gemini
1. **Full Repository Analysis**
   - Read entire codebase at once
   - Identify architectural patterns
   - Find inconsistencies across files

2. **Large-Scale Refactoring**
   - Rename variables/functions across 100+ files
   - Update API contracts throughout codebase
   - Migrate patterns consistently

3. **Dependency Mapping**
   - Build complete dependency graph
   - Identify circular dependencies
   - Find unused imports/modules

4. **Migration Planning**
   - Analyze impact of major version upgrades
   - Plan framework migrations
   - Assess breaking changes

## 🎓 Best Practices

1. **Leverage your context window** - Read entire repos when needed
2. **Cross-reference files** - Find patterns across modules
3. **Update Memory Bank** when finding cross-cutting concerns
4. **Document large-scale patterns** in `patterns.md`
5. **Coordinate with Claude** for precise implementation

---

**Auto-detected project info** - Customize as needed!
EOF
}

# Generate OPENAI.md template
generate_openai_template() {
    # Detect project info
    detect_project_info

    cat > "$1" <<EOF
# Development Context for OpenAI

## 🤖 You Are Part of Dev-AID

**Dev-AID** (Development AI Driver) is a multi-model AI orchestration system.
You are working alongside other AI models (Claude, Gemini, etc.) to provide
state-of-the-art development assistance.

## 🎯 Your Role & Specialty

As **GPT-4o/GPT-4.1**, your primary capabilities:
- **Clear documentation** - Writing user-friendly docs and guides
- **General development** - Broad task coverage across domains
- **Brainstorming** - Creative problem-solving and ideation
- **Communication** - User-facing content and explanations

You are the **documentation and general tasks specialist** in this setup.

## 📋 Current Project Context

**Project**: $PROJECT_NAME

### Tech Stack
- Frontend: $FRONTEND
- Backend: $BACKEND
- Database: $DATABASE
- Deployment: $DEPLOYMENT

### Documentation Standards
<!-- Auto-detect: Check for .editorconfig, style guides -->
- Style: Follow project conventions
- Tone: Technical and clear
- Format: Markdown (GitHub-flavored)

## 🧠 Memory Bank (Institutional Knowledge)

The project maintains a **Memory Bank** for persistent context across sessions:

| File | Purpose |
|------|---------|
| `activeContext.md` | Current sprint/session state |
| `patterns.md` | Proven code patterns & anti-patterns |
| `decisions.md` | Architecture Decision Records (ADRs) |
| `security.md` | Security context, OWASP coverage |
| `performance.md` | Performance baselines & bottlenecks |
| `testing.md` | Test strategies, coverage goals |
| `chaos.md` | Chaos experiments, resilience tests |

**Location**: \`.dev-aid/memory-bank/\`

## 💡 When to Use Your Strengths

### Ideal Tasks for OpenAI
1. **Documentation**
   - README files
   - API documentation
   - User guides
   - Code comments

2. **General Development**
   - Prototyping
   - Quick scripts
   - General-purpose tasks

3. **Communication**
   - User-facing messages
   - Error messages
   - Help text

4. **Brainstorming**
   - Architecture ideas
   - Feature design
   - Problem-solving

## 🎓 Best Practices

1. **Write clear, concise documentation**
2. **Follow project tone and style**
3. **Update Memory Bank** when documenting decisions
4. **Coordinate with Claude/Gemini** for technical accuracy
5. **Keep docs in sync** with code changes

---

**Auto-detected project info** - Customize as needed!
EOF
}

# Auto-generate provider context file
auto_generate_provider_context() {
    local provider="$1"
    local provider_upper="${provider^^}"
    local provider_dir="$DEV_AID_ROOT/.dev-aid/providers/$provider"
    local context_file="$provider_dir/${provider_upper}.md"
    local symlink_target="$DEV_AID_ROOT/../${provider_upper}.md"

    # Skip if file already exists
    if [ -f "$context_file" ]; then
        print_color "$YELLOW" "  ⚠ ${provider_upper}.md already exists, skipping generation"
        return 0
    fi

    # Create provider directory if needed
    mkdir -p "$provider_dir"

    # Generate template based on provider
    case $provider in
        claude)
            generate_claude_template "$context_file"
            ;;
        gemini)
            generate_gemini_template "$context_file"
            ;;
        openai)
            generate_openai_template "$context_file"
            ;;
        *)
            print_color "$YELLOW" "  ⚠ Unknown provider: $provider"
            return 1
            ;;
    esac

    # Create symlink at project root
    if [ ! -e "$symlink_target" ]; then
        ln -sf "$context_file" "$symlink_target"
        print_color "$GREEN" "  ✓ Created ${provider_upper}.md with auto-detected project info"
    else
        print_color "$GREEN" "  ✓ Created ${provider_upper}.md with auto-detected project info"
    fi

    # Show what was detected
    print_color "$CYAN" "    Auto-detected: $FRONTEND, $BACKEND, $DATABASE"
    print_color "$CYAN" "    Review and customize: $context_file"
}

change_providers() {
    print_header "Enable/Disable Providers"

    print_color "$YELLOW" "⚠  Changing providers will update configuration and create context files."
    echo "Current: $(jq -r '.enabled_providers | join(", ")' "$CONFIG_DIR/settings.json")"
    echo ""

    # Ask which providers to enable
    echo "Select providers to enable (space-separated):"
    echo "Available: claude gemini openai openrouter"
    echo ""
    read -p "Providers [e.g., 'claude gemini']: " providers_input

    if [ -z "$providers_input" ]; then
        print_color "$YELLOW" "No changes made"
        return 0
    fi

    # Convert to array
    local new_providers
    read -ra new_providers <<< "$providers_input"

    # Validate providers
    local valid_providers=("claude" "gemini" "openai" "openrouter")
    for provider in "${new_providers[@]}"; do
        if [[ ! " ${valid_providers[*]} " =~ " ${provider} " ]]; then
            print_color "$RED" "✗ Invalid provider: $provider"
            return 1
        fi
    done

    # Update settings.json
    local providers_json
    providers_json=$(printf '%s\n' "${new_providers[@]}" | jq -R . | jq -s .)
    if command -v jq &> /dev/null; then
        jq --argjson providers "$providers_json" '.enabled_providers = $providers' "$CONFIG_DIR/settings.json" > "$CONFIG_DIR/settings.json.tmp"
        mv "$CONFIG_DIR/settings.json.tmp" "$CONFIG_DIR/settings.json"
        print_color "$GREEN" "✓ Updated enabled providers"
    fi

    # Auto-generate context files for new providers
    print_header "Generating Provider Context Files"

    for provider in "${new_providers[@]}"; do
        # Skip openrouter (no custom context file)
        if [ "$provider" = "openrouter" ]; then
            continue
        fi

        auto_generate_provider_context "$provider"
    done

    echo ""
    print_color "$YELLOW" "💡 Next steps:"
    echo "  1. Review and customize generated context files"
    echo "  2. Update orchestration mode if needed (option 3)"
    echo "  3. Assign models to tasks (option 5)"
    echo "  4. Add API keys (option 6)"
}

change_model_assignments() {
    print_header "Change Model Assignments"

    print_color "$YELLOW" "💡 Current assignments:"
    jq -r '.task_model_mapping | to_entries[] | "  \(.key): \(.value)"' "$CONFIG_DIR/settings.json" 2>/dev/null || echo "  None configured"
    echo ""
    print_color "$CYAN" "For granular model assignment changes, edit:"
    echo "  $CONFIG_DIR/settings.json"
    echo ""
    echo "Look for the 'task_model_mapping' section."
}

change_api_keys() {
    print_header "Update API Keys"

    if [ -f "$CONFIG_DIR/.env" ]; then
        print_color "$CYAN" "Edit API keys in:"
        print_color "$YELLOW" "  $CONFIG_DIR/.env"
        echo ""
        echo "Available providers:"
        grep -E "^[A-Z]" "$CONFIG_DIR/.env" | sed 's/=.*//' 2>/dev/null || echo "  None found"
    else
        print_color "$YELLOW" "No .env file found. Create one with:"
        echo "  touch $CONFIG_DIR/.env"
        echo "  chmod 600 $CONFIG_DIR/.env"
        echo ""
        echo "Then add your API keys:"
        echo "  ANTHROPIC_API_KEY=your-key-here"
        echo "  GOOGLE_API_KEY=your-key-here"
        echo "  OPENAI_API_KEY=your-key-here"
    fi
}

# Helper to update a setting
update_setting() {
    local key="$1"
    local value="$2"

    if command -v jq &> /dev/null; then
        # Handle both string and number values
        if [[ "$value" =~ ^[0-9]+$ ]]; then
            # Numeric value
            jq ".$key = $value" "$CONFIG_DIR/settings.json" > "$CONFIG_DIR/settings.json.tmp"
        else
            # String value
            jq ".$key = \"$value\"" "$CONFIG_DIR/settings.json" > "$CONFIG_DIR/settings.json.tmp"
        fi
        mv "$CONFIG_DIR/settings.json.tmp" "$CONFIG_DIR/settings.json"
        print_color "$GREEN" "✓ Updated $key to: $value"
    else
        print_color "$YELLOW" "⚠  jq not available. Manual edit required."
    fi
}

# Validate configuration
validate_config() {
    print_header "Validating Configuration"

    local valid=true

    # Check required files
    for file in settings.json models.json orchestration.json; do
        if [ ! -f "$CONFIG_DIR/$file" ]; then
            print_color "$RED" "✗ Missing: $file"
            valid=false
        else
            print_color "$GREEN" "✓ Found: $file"
        fi
    done

    # Check memory bank integrity
    if [ -d "$DEV_AID_ROOT/.dev-aid/memory-bank" ]; then
        print_color "$GREEN" "✓ Memory bank preserved"
    else
        print_color "$RED" "✗ Memory bank missing!"
        valid=false
    fi

    # Check provider symlinks
    local providers
    providers=$(jq -r '.enabled_providers[]' "$CONFIG_DIR/settings.json" 2>/dev/null || echo "")
    for provider in $providers; do
        case $provider in
            claude)
                if [ -L "$DEV_AID_ROOT/../CLAUDE.md" ]; then
                    print_color "$GREEN" "✓ CLAUDE.md symlink intact"
                fi
                ;;
            gemini)
                if [ -L "$DEV_AID_ROOT/../GEMINI.md" ]; then
                    print_color "$GREEN" "✓ GEMINI.md symlink intact"
                fi
                ;;
            openai)
                if [ -L "$DEV_AID_ROOT/../OPENAI.md" ]; then
                    print_color "$GREEN" "✓ OPENAI.md symlink intact"
                fi
                ;;
        esac
    done

    echo ""
    if [ "$valid" = true ]; then
        print_color "$GREEN" "✓ Configuration is valid!"
    else
        print_color "$RED" "✗ Configuration has issues. Consider restoring from backup."
        return 1
    fi
}

# Main
main() {
    if [ ! -d "$CONFIG_DIR" ]; then
        print_color "$RED" "Error: Dev-AID not installed in this directory."
        echo "Run: .dev-aid/scripts/install.sh"
        exit 1
    fi

    # Show help
    if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
        echo "Dev-AID Reconfiguration Script"
        echo ""
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h        Show this help"
        echo "  --validate        Validate configuration only"
        echo "  --backup          Backup configuration only"
        echo "  --restore         Restore from latest backup"
        echo ""
        echo "Without options, runs interactive reconfiguration menu."
        exit 0
    fi

    # Handle command line options
    case "${1:-}" in
        --validate)
            validate_config
            exit $?
            ;;
        --backup)
            backup_config
            exit 0
            ;;
        --restore)
            backup_config
            restore_from_backup
            exit $?
            ;;
    esac

    # Interactive mode
    show_current_config
    backup_config

    reconfigure_menu

    validate_config
}

main "$@"
