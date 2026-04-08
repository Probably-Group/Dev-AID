#!/usr/bin/env bash
# Dev-AID PRD Functions Library
# Provides PRD wizard and mode detection for setup-dev-aid.sh.
# Sourced by setup-dev-aid.sh — not run directly.

set -euo pipefail

# Determine which PRD mode to suggest based on project state.
# Sets: SUGGESTED_PRD_MODE (build|reverse-engineer|validate|none)
suggest_prd_mode() {
    SUGGESTED_PRD_MODE="none"

    if [ "$STATE_HAS_PRD" = true ]; then
        SUGGESTED_PRD_MODE="validate"
        return 0
    fi

    # No PRD exists — check for code
    local has_code=false
    local project_root="$1"

    # Check for common code indicators
    for pattern in "*.py" "*.ts" "*.js" "*.rs" "*.go" "*.java" "*.rb"; do
        if compgen -G "$project_root/$pattern" > /dev/null 2>&1 || \
           compgen -G "$project_root/src/$pattern" > /dev/null 2>&1 || \
           compgen -G "$project_root/lib/$pattern" > /dev/null 2>&1 || \
           compgen -G "$project_root/app/$pattern" > /dev/null 2>&1; then
            has_code=true
            break
        fi
    done

    if [ "$has_code" = true ]; then
        if is_fresh_install; then
            # Fresh install with existing code — offer choice
            SUGGESTED_PRD_MODE="choose"
        else
            # Existing Dev-AID setup with code but no PRD
            SUGGESTED_PRD_MODE="reverse-engineer"
        fi
    else
        # No code, no PRD — interactive builder
        SUGGESTED_PRD_MODE="build"
    fi
}

# Run the interactive PRD builder wizard (Mode 1).
# Writes PRD.md at the project root.
run_prd_wizard() {
    local project_root="$1"
    local project_name
    project_name="$(basename "$project_root")"

    # Skip the interactive wizard entirely in non-interactive mode (--yes).
    # The wizard contains 7 read-prompt steps that would hang in CI/headless.
    if [ "${NON_INTERACTIVE:-false}" = true ]; then
        print_color "${YELLOW:-\033[1;33m}" "  PRD wizard skipped in non-interactive mode (use --wizard-only to run interactively later)"
        return 0
    fi

    echo ""
    print_color "${CYAN:-\033[0;36m}" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_color "${CYAN:-\033[0;36m}" "  PRD Builder — Create a Product Requirements Document"
    print_color "${CYAN:-\033[0;36m}" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Step 1: Project name & description
    echo -e "${YELLOW:-\033[1;33m}Step 1/7: Project Identity${NC:-\033[0m}"
    read -r -p "Project name [$project_name]: " prd_name
    prd_name="${prd_name:-$project_name}"

    read -r -p "One-line description: " prd_description
    echo ""

    # Step 2: Problem statement
    echo -e "${YELLOW:-\033[1;33m}Step 2/7: Problem Statement${NC:-\033[0m}"
    echo "  What problem does this project solve? Who experiences it?"
    echo "  (Focus on the pain, not the solution. Press Enter twice to finish.)"
    prd_problem=""
    while IFS= read -r line; do
        [ -z "$line" ] && break
        prd_problem="${prd_problem}${line}\n"
    done
    echo ""

    # Step 3: Target users
    echo -e "${YELLOW:-\033[1;33m}Step 3/7: Target Users${NC:-\033[0m}"
    echo "  Describe your primary user personas (role, goal, pain point)."
    echo "  (One per line. Press Enter on empty line to finish.)"
    prd_users=""
    while IFS= read -r line; do
        [ -z "$line" ] && break
        prd_users="${prd_users}${line}\n"
    done
    echo ""

    # Step 4: Core features
    echo -e "${YELLOW:-\033[1;33m}Step 4/7: Core Features${NC:-\033[0m}"
    echo "  List the main features (one per line). Press Enter on empty line to finish."
    prd_features=""
    while IFS= read -r line; do
        [ -z "$line" ] && break
        prd_features="${prd_features}- ${line}\n"
    done
    echo ""

    # Step 5: Technical constraints
    echo -e "${YELLOW:-\033[1;33m}Step 5/7: Technical Constraints${NC:-\033[0m}"
    echo "  Language, framework, deployment target, etc. (one per line, Enter to finish.)"
    prd_constraints=""
    while IFS= read -r line; do
        [ -z "$line" ] && break
        prd_constraints="${prd_constraints}- ${line}\n"
    done
    echo ""

    # Step 6: MVP scope
    echo -e "${YELLOW:-\033[1;33m}Step 6/7: MVP Scope${NC:-\033[0m}"
    echo "  Which features are in the first release? (one per line, Enter to finish.)"
    prd_mvp=""
    while IFS= read -r line; do
        [ -z "$line" ] && break
        prd_mvp="${prd_mvp}- ${line}\n"
    done
    echo ""

    # Step 7: Open questions
    echo -e "${YELLOW:-\033[1;33m}Step 7/7: Open Questions${NC:-\033[0m}"
    echo "  What decisions are still unresolved? (one per line, Enter to finish.)"
    prd_questions=""
    while IFS= read -r line; do
        [ -z "$line" ] && break
        prd_questions="${prd_questions}- ${line}\n"
    done
    echo ""

    # Write PRD.md
    local prd_date
    prd_date="$(date +%Y-%m-%d)"

    cat > "$project_root/PRD.md" << PRDEOF
# PRD: ${prd_name}

> **Version:** 1.0 | **Status:** Draft | **Author:** $(whoami) | **Created:** ${prd_date} | **Updated:** ${prd_date}

## 1. Problem Statement

$(echo -e "$prd_problem")

## 2. Target Users

$(echo -e "$prd_users")

## 3. Goals and Success Metrics

[TODO: Add measurable goals and success metrics]

## 4. Core Features

$(echo -e "$prd_features")

[TODO: Add user stories and acceptance criteria for each feature]

## 5. Technical Constraints

$(echo -e "$prd_constraints")

## 6. Out of Scope

[TODO: List what is explicitly NOT in scope]

## 7. MVP Scope

$(echo -e "$prd_mvp")

## 8. Architecture Overview

[TODO: Add high-level architecture description]

## 9. Dependencies and Risks

[TODO: List external dependencies and project risks]

## 10. Timeline and Milestones

[TODO: Define project timeline and milestones]

## 11. Open Questions

$(echo -e "$prd_questions")
PRDEOF

    echo -e "${GREEN:-\033[0;32m}PRD.md created at: $project_root/PRD.md${NC:-\033[0m}"
    echo -e "${CYAN:-\033[0;36m}Tip: Use /dev-aid-prd --validate to check completeness${NC:-\033[0m}"
}

# Helper to print colored text (fallback if not already defined)
if ! type print_color &>/dev/null 2>&1; then
    print_color() {
        local color="$1"
        shift
        echo -e "${color}$*${NC:-\033[0m}"
    }
fi
