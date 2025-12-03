#!/bin/bash

# Dev-AID Challenger Mode
# Primary model generates, challenger reviews

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEV_AID_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
CONFIG_DIR="$DEV_AID_ROOT/.dev-aid/config"

# Load challenger configuration
load_challenger_config() {
    if command -v jq &> /dev/null; then
        PRIMARY_MODEL=$(jq -r '.challenger.primary_model' "$CONFIG_DIR/orchestration.json")
        CHALLENGER_MODEL=$(jq -r '.challenger.challenger_model' "$CONFIG_DIR/orchestration.json")
    else
        # Fallback
        PRIMARY_MODEL="claude-sonnet-4.5"
        CHALLENGER_MODEL="gemini-2.0-pro"
    fi
}

# Check if task should be challenged
should_challenge() {
    local task_type="${1:-general}"
    local keywords="${2:-}"

    # Security-sensitive tasks
    if echo "$keywords" | grep -qiE "(auth|password|token|secret|crypto|security)"; then
        echo "security_sensitive"
        return 0
    fi

    # Performance-critical tasks
    if echo "$keywords" | grep -qiE "(performance|optimize|bottleneck|cache|query)"; then
        echo "performance_critical"
        return 0
    fi

    # Major refactoring
    if echo "$keywords" | grep -qiE "(refactor|restructure|rewrite)"; then
        echo "major_refactoring"
        return 0
    fi

    # New architecture
    if echo "$keywords" | grep -qiE "(architecture|design|structure|framework)"; then
        echo "new_architecture"
        return 0
    fi

    # Default: no challenge needed
    return 1
}

# Challenger mode main logic
challenger_mode() {
    local task_type="${1:-general}"
    local keywords="${2:-}"

    load_challenger_config

    echo "⚔️  Challenger Mode: Multi-Model Review"
    echo ""
    echo "Primary Model: $PRIMARY_MODEL"
    echo "Challenger Model: $CHALLENGER_MODEL"
    echo ""

    # Check if this task should be challenged
    local challenge_reason=""
    if challenge_reason=$(should_challenge "$task_type" "$keywords"); then
        echo "🔍 Challenge Triggered: $challenge_reason"
        echo ""
        echo "Workflow:"
        echo "  1️⃣  $PRIMARY_MODEL generates solution"
        echo "  2️⃣  $CHALLENGER_MODEL reviews and critiques"
        echo "       • Security vulnerabilities"
        echo "       • Performance issues"
        echo "       • Edge cases"
        echo "       • Alternative approaches"
        echo "  3️⃣  $PRIMARY_MODEL revises (if needed)"
        echo "  4️⃣  You see both perspectives"
        echo ""
        echo "✨ Benefit: Higher quality through adversarial review"
    else
        echo "ℹ️  No challenge needed for this task type."
        echo ""
        echo "Using solo mode with $PRIMARY_MODEL"
        echo ""
        echo "💡 Challenge is triggered for:"
        echo "   • Security-sensitive code (auth, passwords, tokens)"
        echo "   • Performance-critical code (queries, caching)"
        echo "   • Major refactoring"
        echo "   • New architecture decisions"
    fi

    echo ""
}

# Main execution
main() {
    local task_type="${1:-general}"
    local keywords="${2:-}"

    challenger_mode "$task_type" "$keywords"
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
