# Enhancement: Auto-Populate Provider Context Files

## Current Problem

When user runs `reconfigure.sh` to add a provider (e.g., Gemini), the script generates a template with placeholder markers:

```markdown
**Project**: [CUSTOMIZE: Add your project name and description]

### Tech Stack
[CUSTOMIZE: Add your technology stack]
- Frontend:
- Backend:
- Database:
```

**Issue**: User must manually fill in information that the script could auto-detect.

---

## Proposed Solution

### Phase 1: Detect Project Information

When generating a provider context file, automatically analyze the project:

```bash
auto_populate_project_info() {
    local project_root="$DEV_AID_ROOT/.."

    # Detect project name
    PROJECT_NAME=$(basename "$project_root")

    # Detect tech stack
    FRONTEND=""
    BACKEND=""
    DATABASE=""
    DEPLOYMENT=""

    # Check for JavaScript/TypeScript frontend
    if [ -f "$project_root/package.json" ]; then
        # Read package.json
        if command -v jq &> /dev/null; then
            local deps=$(jq -r '.dependencies | keys[]' "$project_root/package.json" 2>/dev/null)

            # Detect frontend frameworks
            if echo "$deps" | grep -q "react"; then FRONTEND="React"; fi
            if echo "$deps" | grep -q "vue"; then FRONTEND="Vue.js"; fi
            if echo "$deps" | grep -q "angular"; then FRONTEND="Angular"; fi
            if echo "$deps" | grep -q "svelte"; then FRONTEND="Svelte"; fi
            if echo "$deps" | grep -q "next"; then FRONTEND="Next.js"; fi

            # Detect backend frameworks
            if echo "$deps" | grep -q "express"; then BACKEND="Node.js/Express"; fi
            if echo "$deps" | grep -q "fastify"; then BACKEND="Node.js/Fastify"; fi
            if echo "$deps" | grep -q "nest"; then BACKEND="NestJS"; fi

            # Detect databases
            if echo "$deps" | grep -q "mongoose"; then DATABASE="MongoDB (Mongoose)"; fi
            if echo "$deps" | grep -q "pg\|postgres"; then DATABASE="PostgreSQL"; fi
            if echo "$deps" | grep -q "mysql"; then DATABASE="MySQL"; fi
            if echo "$deps" | grep -q "prisma"; then DATABASE="Prisma ORM"; fi
        fi
    fi

    # Check for Python backend
    if [ -f "$project_root/requirements.txt" ] || [ -f "$project_root/pyproject.toml" ]; then
        if grep -q "flask\|django\|fastapi" "$project_root/requirements.txt" 2>/dev/null; then
            if grep -q "flask" "$project_root/requirements.txt"; then BACKEND="Python/Flask"; fi
            if grep -q "django" "$project_root/requirements.txt"; then BACKEND="Python/Django"; fi
            if grep -q "fastapi" "$project_root/requirements.txt"; then BACKEND="Python/FastAPI"; fi
        fi
    fi

    # Check for Go backend
    if [ -f "$project_root/go.mod" ]; then
        BACKEND="Go"
        if grep -q "gin-gonic/gin" "$project_root/go.mod"; then BACKEND="Go/Gin"; fi
        if grep -q "gofiber/fiber" "$project_root/go.mod"; then BACKEND="Go/Fiber"; fi
    fi

    # Check for Rust backend
    if [ -f "$project_root/Cargo.toml" ]; then
        BACKEND="Rust"
        if grep -q "actix-web" "$project_root/Cargo.toml"; then BACKEND="Rust/Actix"; fi
        if grep -q "rocket" "$project_root/Cargo.toml"; then BACKEND="Rust/Rocket"; fi
    fi

    # Check for Docker
    if [ -f "$project_root/Dockerfile" ]; then
        DEPLOYMENT="Docker"
    fi
    if [ -f "$project_root/docker-compose.yml" ]; then
        DEPLOYMENT="Docker Compose"
    fi
    if [ -d "$project_root/.github/workflows" ]; then
        DEPLOYMENT="${DEPLOYMENT}, GitHub Actions"
    fi
}
```

### Phase 2: Generate Pre-Populated Templates

Replace placeholder markers with detected information:

```bash
generate_claude_template_populated() {
    cat > "$1" <<EOF
# Development Context for Claude

## 🤖 You Are Part of Dev-AID

**Dev-AID** (Development AI Driver) is a multi-model AI orchestration system.

## 📋 Current Project Context

**Project**: $PROJECT_NAME

### Tech Stack
- Frontend: ${FRONTEND:-"Not detected"}
- Backend: ${BACKEND:-"Not detected"}
- Database: ${DATABASE:-"Not detected"}
- Deployment: ${DEPLOYMENT:-"Not detected"}

### Repository Structure
$(tree -L 2 -d "$DEV_AID_ROOT/.." 2>/dev/null || echo "Run 'tree -L 2 -d' to see structure")

**Note**: Auto-detected from codebase. Customize as needed.

[rest of template...]
EOF
}
```

### Phase 3: Fallback for Unknown Information

For information that can't be auto-detected, provide helpful hints instead of generic placeholders:

```markdown
### Documentation Standards
<!-- No .editorconfig or style guide detected -->
<!-- Consider adding: -->
<!-- - Style: Google/Airbnb/Standard -->
<!-- - Tone: Technical/Friendly/Formal -->
<!-- - Format: Markdown/JSDoc/Sphinx -->
```

---

## Implementation Priority

**High Priority**:
- Auto-detect project name (from directory name)
- Auto-detect tech stack (from package.json, requirements.txt, go.mod, Cargo.toml)
- Auto-detect repository structure (basic tree output)

**Medium Priority**:
- Auto-detect deployment setup (Docker, CI/CD)
- Auto-detect testing frameworks
- Auto-detect code style/linting config

**Low Priority**:
- Auto-detect documentation patterns
- Auto-detect team size (from git history)
- Auto-detect active sprint info

---

## User Experience

### Before (Current)
```
✓ Created GEMINI.md and symlink
📝 Please customize: .dev-aid/providers/gemini/GEMINI.md

[User opens file, sees 15 [CUSTOMIZE: ...] markers, feels overwhelmed]
```

### After (Enhanced)
```
✓ Created GEMINI.md with detected project info
📝 Auto-detected: React frontend, Node.js/Express backend, PostgreSQL
📝 Review and update: .dev-aid/providers/gemini/GEMINI.md

[User opens file, sees pre-filled tech stack, makes minor tweaks]
```

---

## Benefits

1. **Lower barrier to entry**: Users can start immediately without manual setup
2. **Reduce cognitive load**: One less decision to make during setup
3. **Increase accuracy**: Auto-detection reduces typos/mistakes
4. **Time savings**: 5-10 minutes saved per context file
5. **Better defaults**: Detected info is more accurate than generic placeholders

---

## Implementation Checklist

- [ ] Add `detect_project_info()` function to reconfigure.sh
- [ ] Update all 3 template generators (Claude, Gemini, OpenAI)
- [ ] Test with various project types (JS, Python, Go, Rust)
- [ ] Update documentation to mention auto-population
- [ ] Add logging: "Auto-detected: React, Express, PostgreSQL"
- [ ] Handle edge cases (monorepos, multi-language projects)
