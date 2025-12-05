#!/usr/bin/env bash
#
# Script: select-skills.sh
# Description: Selects relevant skills based on context using scoring algorithm
# Usage: select-skills.sh "context keywords" [max_skills]
#

# Strict mode: exit on error, undefined variables, pipe failures
set -euo pipefail

# Script directory (portable way)
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# Cleanup function (always runs on exit)
cleanup() {
    local exit_code=$?
    # Cleanup temporary files if any
    [[ -n "${TEMP_SCORES:-}" ]] && rm -f "$TEMP_SCORES" 2>/dev/null || true
    exit "$exit_code"
}
trap cleanup EXIT INT TERM

# Configuration
readonly REGISTRY_FILE="${SCRIPT_DIR}/../skills/registry/skills-index.json"
readonly MAX_SKILLS="${2:-5}"
readonly MIN_SCORE=5

# Input validation
if [[ $# -lt 1 ]]; then
    echo "Usage: $SCRIPT_NAME \"context keywords\" [max_skills]" >&2
    exit 1
fi

readonly CONTEXT="$1"

# Validate registry file exists
if [[ ! -f "$REGISTRY_FILE" ]]; then
    echo "Error: Registry file not found: $REGISTRY_FILE" >&2
    exit 1
fi

# Validate jq is available
if ! command -v jq >/dev/null 2>&1; then
    echo "Error: jq is required but not installed" >&2
    exit 1
fi

# Temporary file for scores
TEMP_SCORES=$(mktemp) || exit 1
chmod 600 "$TEMP_SCORES"

# Calculate score for a skill based on context
calculate_skill_score() {
    local skill_name="$1"
    local context_lower
    context_lower="$(echo "$CONTEXT" | tr '[:upper:]' '[:lower:]')"
    local score=0

    # Extract skill activation data from registry
    local skill_data
    skill_data=$(jq -r ".\"$skill_name\".activation" "$REGISTRY_FILE" 2>/dev/null) || return 1

    # Check if skill data is null
    if [[ "$skill_data" == "null" ]]; then
        return 1
    fi

    # Score primary keywords (10 points each)
    local primary_keywords
    primary_keywords=$(echo "$skill_data" | jq -r '.primary_keywords[]' 2>/dev/null) || true
    if [[ -n "$primary_keywords" ]]; then
        while IFS= read -r keyword; do
            [[ -z "$keyword" ]] && continue
            local keyword_lower
            keyword_lower="$(echo "$keyword" | tr '[:upper:]' '[:lower:]')"
            if echo "$context_lower" | grep -q -i -F "$keyword_lower"; then
                score=$((score + 10))
            fi
        done <<< "$primary_keywords"
    fi

    # Score secondary keywords (5 points each)
    local secondary_keywords
    secondary_keywords=$(echo "$skill_data" | jq -r '.secondary_keywords[]' 2>/dev/null) || true
    if [[ -n "$secondary_keywords" ]]; then
        while IFS= read -r keyword; do
            [[ -z "$keyword" ]] && continue
            local keyword_lower
            keyword_lower="$(echo "$keyword" | tr '[:upper:]' '[:lower:]')"
            if echo "$context_lower" | grep -q -i -F "$keyword_lower"; then
                score=$((score + 5))
            fi
        done <<< "$secondary_keywords"
    fi

    # Score technologies (8 points each)
    local technologies
    technologies=$(echo "$skill_data" | jq -r '.technologies[]' 2>/dev/null) || true
    if [[ -n "$technologies" ]]; then
        while IFS= read -r tech; do
            [[ -z "$tech" ]] && continue
            local tech_lower
            tech_lower="$(echo "$tech" | tr '[:upper:]' '[:lower:]')"
            if echo "$context_lower" | grep -q -i -F "$tech_lower"; then
                score=$((score + 8))
            fi
        done <<< "$technologies"
    fi

    # Apply confidence weights for specific keywords
    local confidence_weights
    confidence_weights=$(echo "$skill_data" | jq -r '.confidence_weights // {} | to_entries[] | "\(.key)|\(.value)"' 2>/dev/null) || true
    if [[ -n "$confidence_weights" ]]; then
        while IFS='|' read -r weight_key weight_value; do
            [[ -z "$weight_key" ]] && continue
            local weight_key_lower
            weight_key_lower="$(echo "$weight_key" | tr '[:upper:]' '[:lower:]')"
            if echo "$context_lower" | grep -q -i -F "$weight_key_lower"; then
                # Convert float to integer percentage (0.3 -> 30)
                local boost
                boost=$(echo "$weight_value * 100" | bc 2>/dev/null || echo "0")
                score=$((score + ${boost%.*}))
            fi
        done <<< "$confidence_weights"
    fi

    echo "$score"
}

# Filter excluded skills
is_excluded() {
    local skill_name="$1"
    local selected_skills="$2"

    # Get exclude_with list for this skill
    local exclude_list
    exclude_list=$(jq -r ".\"$skill_name\".activation.exclude_with[]" "$REGISTRY_FILE" 2>/dev/null) || return 1

    # Check if any excluded skill is already selected
    while IFS= read -r excluded_skill; do
        [[ -z "$excluded_skill" ]] && continue
        if echo "$selected_skills" | grep -q -w "$excluded_skill"; then
            return 0  # Excluded
        fi
    done <<< "$exclude_list"

    return 1  # Not excluded
}

# Main skill selection logic
main() {
    # Get all skill names from registry
    local all_skills
    all_skills=$(jq -r 'keys[]' "$REGISTRY_FILE" 2>/dev/null) || {
        echo "Error: Failed to parse registry file" >&2
        exit 1
    }

    # Calculate scores for all skills
    while IFS= read -r skill_name; do
        [[ -z "$skill_name" ]] && continue

        local score
        score=$(calculate_skill_score "$skill_name") || continue

        # Only include skills with score above minimum
        if [[ "$score" -ge "$MIN_SCORE" ]]; then
            echo "$score|$skill_name" >> "$TEMP_SCORES"
        fi
    done <<< "$all_skills"

    # Sort by score (descending) and select top skills
    local selected_skills=""
    local count=0

    while IFS='|' read -r score skill_name; do
        [[ -z "$skill_name" ]] && continue

        # Check if skill should be excluded based on already selected skills
        if ! is_excluded "$skill_name" "$selected_skills" 2>/dev/null; then
            echo "$skill_name"
            selected_skills="$selected_skills $skill_name"
            count=$((count + 1))

            # Check if we've reached max skills
            if [[ "$count" -ge "$MAX_SKILLS" ]]; then
                break
            fi
        fi
    done < <(sort -t'|' -k1 -rn "$TEMP_SCORES" 2>/dev/null || true)

    # Add required dependencies for selected skills
    if [[ -n "$selected_skills" ]]; then
        for skill in $selected_skills; do
            local requires
            requires=$(jq -r ".\"$skill\".activation.requires[]" "$REGISTRY_FILE" 2>/dev/null) || continue
            while IFS= read -r required_skill; do
                [[ -z "$required_skill" ]] && continue
                # Only add if not already selected and not in output
                if ! echo "$selected_skills" | grep -q -w "$required_skill"; then
                    echo "$required_skill"
                    selected_skills="$selected_skills $required_skill"
                fi
            done <<< "$requires"
        done
    fi
}

# Run main function
main
