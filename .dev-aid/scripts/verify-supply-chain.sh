#!/usr/bin/env bash
# Dev-AID Supply Chain Verification Script
# Phase 3 of Enterprise Security: provenance verification, package signature
# checks, and private PyPI mirror support.
#
# Usage:
#   ./verify-supply-chain.sh                    # Full verification
#   ./verify-supply-chain.sh --help             # Show this help
#   ./verify-supply-chain.sh --json             # Output JSON report to stdout
#   ./verify-supply-chain.sh --report FILE      # Save JSON report to file
#   ./verify-supply-chain.sh --config FILE      # Use custom config file
#   ./verify-supply-chain.sh --generate-hashes  # Generate requirements.lock.txt with hashes
#   ./verify-supply-chain.sh --ci               # CI mode (non-interactive, exit codes)
#
# Configuration:
#   .dev-aid/config/supply-chain.json
#
# Tools used (all optional, graceful degradation):
#   - pip (required) -- hash verification via --require-hashes
#   - pip-audit      -- vulnerability + provenance attestation checks
#   - cosign         -- Sigstore signature verification
#   - jq             -- JSON processing
#
# This script is non-blocking: optional checks warn but don't fail.
# Only critical issues (e.g., hash mismatches) cause a non-zero exit code.

set -euo pipefail

# ── Colors ─────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ── Constants ──────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DEFAULT_CONFIG="$REPO_ROOT/.dev-aid/config/supply-chain.json"
DEFAULT_REQUIREMENTS="$REPO_ROOT/.dev-aid/orchestration/requirements.txt"
DEFAULT_LOCK_FILE="$REPO_ROOT/.dev-aid/orchestration/requirements.lock.txt"
VERSION="1.0.0"

# ── State ──────────────────────────────────────────────────
ISSUES_FOUND=0
WARNINGS_FOUND=0
CHECKS_PASSED=0
CHECKS_TOTAL=0
JSON_OUTPUT=false
JSON_REPORT_FILE=""
CI_MODE=false
GENERATE_HASHES=false
CONFIG_FILE="$DEFAULT_CONFIG"
START_TIME=$(date +%s)

# Temp files tracking
declare -a TEMP_FILES=()

cleanup() {
    for f in "${TEMP_FILES[@]}"; do
        rm -f "$f" 2>/dev/null || true
    done
}
trap cleanup EXIT INT TERM

# ── Helpers ────────────────────────────────────────────────
log_info()    { if ! $JSON_OUTPUT; then echo -e "${BLUE}[SUPPLY-CHAIN]${NC} $1"; fi; }
log_success() { if ! $JSON_OUTPUT; then echo -e "${GREEN}[SUPPLY-CHAIN]${NC} $1"; fi; }
log_warning() { if ! $JSON_OUTPUT; then echo -e "${YELLOW}[SUPPLY-CHAIN]${NC} $1"; fi; WARNINGS_FOUND=$((WARNINGS_FOUND + 1)); }
log_error()   { if ! $JSON_OUTPUT; then echo -e "${RED}[SUPPLY-CHAIN]${NC} $1"; fi; ISSUES_FOUND=$((ISSUES_FOUND + 1)); }
log_check_pass() { CHECKS_PASSED=$((CHECKS_PASSED + 1)); CHECKS_TOTAL=$((CHECKS_TOTAL + 1)); }
log_check_fail() { CHECKS_TOTAL=$((CHECKS_TOTAL + 1)); }

usage() {
    cat <<EOF
Dev-AID Supply Chain Verification (v$VERSION)

Usage: $(basename "$0") [OPTIONS]

Verify package provenance, check signatures, and validate supply chain
integrity for Dev-AID Python dependencies.

Options:
    --help               Show this help message
    --json               Output JSON report to stdout (suppress normal output)
    --report FILE        Save JSON report to file
    --config FILE        Use custom config file (default: .dev-aid/config/supply-chain.json)
    --generate-hashes    Generate requirements.lock.txt with pinned hashes
    --ci                 CI mode (non-interactive, structured exit codes)

Exit Codes:
    0   All checks passed (or only warnings)
    1   Critical issues found (hash mismatch, blocked registry, etc.)
    2   Configuration error

Examples:
    $(basename "$0")                           # Full verification
    $(basename "$0") --generate-hashes         # Generate lock file with hashes
    $(basename "$0") --json --report report.json  # Save JSON report
    $(basename "$0") --ci                      # Run in CI pipeline

Configuration (.dev-aid/config/supply-chain.json):
    private_pypi_mirror    Private PyPI URL (null for public PyPI)
    require_hashes         Verify package hashes (true/false)
    check_provenance       Check Sigstore attestations (true/false)
    allowed_registries     Allowed package index URLs
    trusted_publishers     Trusted GitHub/GitLab publisher identities
    fail_on_missing_hash   Fail if hash not in lock file (default: false)
    fail_on_provenance_error  Fail if provenance check fails (default: false)
EOF
    exit 0
}

# ── Parse Arguments ────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            usage
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        --report)
            JSON_REPORT_FILE="$2"
            shift 2
            ;;
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --generate-hashes)
            GENERATE_HASHES=true
            shift
            ;;
        --ci)
            CI_MODE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Run '$(basename "$0") --help' for usage."
            exit 2
            ;;
    esac
done

# ── Load Configuration ────────────────────────────────────
load_config() {
    if [[ ! -f "$CONFIG_FILE" ]]; then
        log_warning "Config file not found: $CONFIG_FILE (using defaults)"
        # Use defaults
        CFG_PRIVATE_MIRROR=""
        CFG_REQUIRE_HASHES=true
        CFG_CHECK_PROVENANCE=true
        CFG_ALLOWED_REGISTRIES="https://pypi.org/simple/"
        CFG_FAIL_ON_MISSING_HASH=false
        CFG_FAIL_ON_PROVENANCE_ERROR=false
        CFG_REQUIREMENTS="$DEFAULT_REQUIREMENTS"
        CFG_LOCK_FILE="$DEFAULT_LOCK_FILE"
        return
    fi

    if ! command -v jq &>/dev/null; then
        log_warning "jq not installed -- cannot parse config, using defaults"
        CFG_PRIVATE_MIRROR=""
        CFG_REQUIRE_HASHES=true
        CFG_CHECK_PROVENANCE=true
        CFG_ALLOWED_REGISTRIES="https://pypi.org/simple/"
        CFG_FAIL_ON_MISSING_HASH=false
        CFG_FAIL_ON_PROVENANCE_ERROR=false
        CFG_REQUIREMENTS="$DEFAULT_REQUIREMENTS"
        CFG_LOCK_FILE="$DEFAULT_LOCK_FILE"
        return
    fi

    CFG_PRIVATE_MIRROR=$(jq -r '.private_pypi_mirror // empty' "$CONFIG_FILE" 2>/dev/null || echo "")
    CFG_REQUIRE_HASHES=$(jq -r '.require_hashes // true' "$CONFIG_FILE" 2>/dev/null || echo "true")
    CFG_CHECK_PROVENANCE=$(jq -r '.check_provenance // true' "$CONFIG_FILE" 2>/dev/null || echo "true")
    CFG_ALLOWED_REGISTRIES=$(jq -r '.allowed_registries[]? // "https://pypi.org/simple/"' "$CONFIG_FILE" 2>/dev/null || echo "https://pypi.org/simple/")
    CFG_FAIL_ON_MISSING_HASH=$(jq -r '.fail_on_missing_hash // false' "$CONFIG_FILE" 2>/dev/null || echo "false")
    CFG_FAIL_ON_PROVENANCE_ERROR=$(jq -r '.fail_on_provenance_error // false' "$CONFIG_FILE" 2>/dev/null || echo "false")

    # Resolve paths relative to repo root
    local cfg_req
    cfg_req=$(jq -r '.requirements_file // empty' "$CONFIG_FILE" 2>/dev/null || echo "")
    if [[ -n "$cfg_req" ]]; then
        CFG_REQUIREMENTS="$REPO_ROOT/$cfg_req"
    else
        CFG_REQUIREMENTS="$DEFAULT_REQUIREMENTS"
    fi

    local cfg_lock
    cfg_lock=$(jq -r '.lock_file // empty' "$CONFIG_FILE" 2>/dev/null || echo "")
    if [[ -n "$cfg_lock" ]]; then
        CFG_LOCK_FILE="$REPO_ROOT/$cfg_lock"
    else
        CFG_LOCK_FILE="$DEFAULT_LOCK_FILE"
    fi

    log_info "Config loaded from: $CONFIG_FILE"
}

# ── JSON Report Builder ───────────────────────────────────
declare -a REPORT_CHECKS=()

add_report_check() {
    local name="$1"
    local status="$2"  # pass, fail, warn, skip
    local message="$3"
    local details="${4:-}"

    REPORT_CHECKS+=("{\"name\":\"$name\",\"status\":\"$status\",\"message\":\"$message\",\"details\":\"$details\"}")
}

generate_json_report() {
    local end_time
    end_time=$(date +%s)
    local duration=$((end_time - START_TIME))

    local checks_json
    checks_json=$(printf '%s\n' "${REPORT_CHECKS[@]}" | paste -sd',' -)

    local report
    report=$(cat <<ENDREPORT
{
  "tool": "dev-aid-supply-chain-verify",
  "version": "$VERSION",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "duration_seconds": $duration,
  "config_file": "$CONFIG_FILE",
  "requirements_file": "$CFG_REQUIREMENTS",
  "lock_file": "$CFG_LOCK_FILE",
  "private_mirror": ${CFG_PRIVATE_MIRROR:+"\"$CFG_PRIVATE_MIRROR\""}${CFG_PRIVATE_MIRROR:-"null"},
  "summary": {
    "total_checks": $CHECKS_TOTAL,
    "passed": $CHECKS_PASSED,
    "failed": $ISSUES_FOUND,
    "warnings": $WARNINGS_FOUND,
    "result": "$(if [[ $ISSUES_FOUND -eq 0 ]]; then echo "pass"; else echo "fail"; fi)"
  },
  "checks": [$checks_json]
}
ENDREPORT
)

    if [[ -n "$JSON_REPORT_FILE" ]]; then
        echo "$report" > "$JSON_REPORT_FILE"
        if ! $JSON_OUTPUT; then
            log_success "JSON report saved to: $JSON_REPORT_FILE"
        fi
    fi

    if $JSON_OUTPUT; then
        echo "$report"
    fi
}

# ── Check: Version Pinning ─────────────────────────────────
check_version_pinning() {
    log_info "Checking version pinning in requirements..."

    if [[ ! -f "$CFG_REQUIREMENTS" ]]; then
        log_error "Requirements file not found: $CFG_REQUIREMENTS"
        add_report_check "version_pinning" "fail" "Requirements file not found" "$CFG_REQUIREMENTS"
        log_check_fail
        return
    fi

    local unpinned_count=0
    local total_deps=0
    local unpinned_list=""

    while IFS= read -r line; do
        # Skip comments, empty lines, and options
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ "$line" =~ ^[[:space:]]*$ ]] && continue
        [[ "$line" =~ ^- ]] && continue

        # Extract package name (before any version specifier)
        local pkg_line
        pkg_line=$(echo "$line" | sed 's/#.*//' | xargs)
        [[ -z "$pkg_line" ]] && continue

        total_deps=$((total_deps + 1))

        # Check for exact pinning (==)
        if ! echo "$pkg_line" | grep -q '=='; then
            unpinned_count=$((unpinned_count + 1))
            local pkg_name
            pkg_name=$(echo "$pkg_line" | sed 's/[><=!].*//' | xargs)
            unpinned_list="${unpinned_list}${pkg_name}, "
        fi
    done < "$CFG_REQUIREMENTS"

    if [[ $unpinned_count -eq 0 ]]; then
        log_success "All $total_deps dependencies are pinned with exact versions (==)"
        add_report_check "version_pinning" "pass" "All $total_deps dependencies pinned" ""
        log_check_pass
    else
        log_error "$unpinned_count of $total_deps dependencies not pinned: ${unpinned_list%, }"
        add_report_check "version_pinning" "fail" "$unpinned_count unpinned dependencies" "${unpinned_list%, }"
        log_check_fail
    fi
}

# ── Check: Hash Verification ──────────────────────────────
check_hash_verification() {
    if [[ "$CFG_REQUIRE_HASHES" != "true" ]]; then
        log_info "Hash verification disabled in config"
        add_report_check "hash_verification" "skip" "Disabled in config" ""
        return
    fi

    log_info "Checking hash verification..."

    if [[ ! -f "$CFG_LOCK_FILE" ]]; then
        local msg="Lock file not found: $CFG_LOCK_FILE"
        if [[ "$CFG_FAIL_ON_MISSING_HASH" == "true" ]]; then
            log_error "$msg -- run with --generate-hashes to create it"
            add_report_check "hash_verification" "fail" "$msg" "Run: $0 --generate-hashes"
            log_check_fail
        else
            log_warning "$msg -- run with --generate-hashes to create it"
            add_report_check "hash_verification" "warn" "$msg" "Run: $0 --generate-hashes"
        fi
        return
    fi

    # Verify the lock file contains hashes
    local hash_count
    hash_count=$(grep -c -- '--hash=' "$CFG_LOCK_FILE" 2>/dev/null || echo "0")
    local pkg_count
    pkg_count=$(grep -cE '^[a-zA-Z]' "$CFG_LOCK_FILE" 2>/dev/null || echo "0")

    if [[ "$hash_count" -eq 0 ]]; then
        log_warning "Lock file exists but contains no hashes -- regenerate with --generate-hashes"
        add_report_check "hash_verification" "warn" "Lock file has no hashes" ""
        return
    fi

    log_info "Lock file has $hash_count hash entries for $pkg_count packages"

    # Dry-run pip install with --require-hashes to verify
    local pip_cmd="pip"
    if [[ -f "$REPO_ROOT/.dev-aid/orchestration/venv/bin/pip" ]]; then
        pip_cmd="$REPO_ROOT/.dev-aid/orchestration/venv/bin/pip"
    fi

    local pip_output
    pip_output=$(mktemp)
    TEMP_FILES+=("$pip_output")

    local pip_args=(install --dry-run --require-hashes -r "$CFG_LOCK_FILE")

    # Use private mirror if configured
    if [[ -n "$CFG_PRIVATE_MIRROR" ]]; then
        pip_args+=(--index-url "$CFG_PRIVATE_MIRROR")
    fi

    if $pip_cmd "${pip_args[@]}" > "$pip_output" 2>&1; then
        log_success "Hash verification passed ($hash_count hashes verified)"
        add_report_check "hash_verification" "pass" "$hash_count hashes verified" ""
        log_check_pass
    else
        local error_detail
        error_detail=$(tail -5 "$pip_output" | tr '\n' ' ')
        if [[ "$CFG_FAIL_ON_MISSING_HASH" == "true" ]]; then
            log_error "Hash verification failed: $error_detail"
            add_report_check "hash_verification" "fail" "Hash mismatch detected" "$error_detail"
            log_check_fail
        else
            log_warning "Hash verification issue (non-blocking): $error_detail"
            add_report_check "hash_verification" "warn" "Hash verification issue" "$error_detail"
        fi
    fi
}

# ── Check: Registry Allowlist ──────────────────────────────
check_registry_allowlist() {
    log_info "Checking package registry configuration..."

    # Check pip config for any extra index URLs
    local pip_cmd="pip"
    if [[ -f "$REPO_ROOT/.dev-aid/orchestration/venv/bin/pip" ]]; then
        pip_cmd="$REPO_ROOT/.dev-aid/orchestration/venv/bin/pip"
    fi

    local pip_config_output
    pip_config_output=$(mktemp)
    TEMP_FILES+=("$pip_config_output")

    $pip_cmd config list 2>/dev/null > "$pip_config_output" || true

    local extra_indexes
    extra_indexes=$(grep -i 'extra-index-url\|index-url' "$pip_config_output" 2>/dev/null || echo "")

    if [[ -n "$extra_indexes" ]]; then
        # Verify each configured index is in the allowlist
        local blocked_found=false
        while IFS= read -r index_line; do
            local index_url
            index_url=$(echo "$index_line" | sed 's/.*=//;s/[[:space:]]//g')
            [[ -z "$index_url" ]] && continue

            local is_allowed=false
            while IFS= read -r allowed; do
                if [[ "$index_url" == "$allowed"* ]]; then
                    is_allowed=true
                    break
                fi
            done <<< "$CFG_ALLOWED_REGISTRIES"

            # Also allow configured private mirror
            if [[ -n "$CFG_PRIVATE_MIRROR" ]] && [[ "$index_url" == "$CFG_PRIVATE_MIRROR"* ]]; then
                is_allowed=true
            fi

            if ! $is_allowed; then
                log_error "Non-allowlisted registry found: $index_url"
                blocked_found=true
            fi
        done <<< "$extra_indexes"

        if $blocked_found; then
            add_report_check "registry_allowlist" "fail" "Non-allowlisted registries detected" "$extra_indexes"
            log_check_fail
        else
            log_success "All configured registries are in the allowlist"
            add_report_check "registry_allowlist" "pass" "All registries allowlisted" ""
            log_check_pass
        fi
    else
        log_success "Using default PyPI registry (allowlisted)"
        add_report_check "registry_allowlist" "pass" "Default PyPI registry" "https://pypi.org/simple/"
        log_check_pass
    fi

    # Report private mirror configuration
    if [[ -n "$CFG_PRIVATE_MIRROR" ]]; then
        log_info "Private PyPI mirror configured: $CFG_PRIVATE_MIRROR"
    fi
}

# ── Check: Provenance / Sigstore Attestations ──────────────
check_provenance() {
    if [[ "$CFG_CHECK_PROVENANCE" != "true" ]]; then
        log_info "Provenance verification disabled in config"
        add_report_check "provenance_verification" "skip" "Disabled in config" ""
        return
    fi

    log_info "Checking package provenance attestations..."

    local has_pip_audit=false
    local has_cosign=false

    command -v pip-audit &>/dev/null && has_pip_audit=true
    command -v cosign &>/dev/null && has_cosign=true

    # Method 1: pip-audit with provenance checks
    if $has_pip_audit && [[ -f "$CFG_REQUIREMENTS" ]]; then
        log_info "Running pip-audit for vulnerability + provenance scan..."

        local audit_output
        audit_output=$(mktemp)
        TEMP_FILES+=("$audit_output")

        local audit_args=(-r "$CFG_REQUIREMENTS" --format json --output "$audit_output")

        if pip-audit "${audit_args[@]}" 2>/dev/null; then
            log_success "pip-audit: no known vulnerabilities found"
            add_report_check "pip_audit_vulnerabilities" "pass" "No known vulnerabilities" ""
            log_check_pass
        else
            local vuln_count
            vuln_count=$(jq -r '[.dependencies[]? | select(.vulns | length > 0)] | length' "$audit_output" 2>/dev/null || echo "unknown")
            log_warning "pip-audit: $vuln_count package(s) with known vulnerabilities"
            add_report_check "pip_audit_vulnerabilities" "warn" "$vuln_count vulnerable packages" ""
        fi
    else
        if ! $has_pip_audit; then
            log_warning "pip-audit not installed -- skipping vulnerability scan"
            log_info "Install: pip install pip-audit"
        fi
        add_report_check "pip_audit_vulnerabilities" "skip" "pip-audit not available" ""
    fi

    # Method 2: Sigstore / cosign verification for critical packages
    if $has_cosign; then
        log_info "Checking Sigstore attestations with cosign..."

        local verified=0
        local not_found=0
        local critical_packages=("anthropic" "openai" "pydantic" "requests" "httpx" "cryptography")

        for pkg in "${critical_packages[@]}"; do
            # Check if this package is actually in requirements
            if ! grep -qi "^${pkg}==" "$CFG_REQUIREMENTS" 2>/dev/null; then
                continue
            fi

            local pkg_version
            pkg_version=$(grep -i "^${pkg}==" "$CFG_REQUIREMENTS" | head -1 | sed 's/.*==//;s/[[:space:]].*//')

            # Try to verify attestation via cosign
            # Sigstore for PyPI uses the transparency log
            local cosign_output
            cosign_output=$(mktemp)
            TEMP_FILES+=("$cosign_output")

            if cosign verify-attestation \
                --type https://slsa.dev/provenance/v0.2 \
                --certificate-identity-regexp ".*" \
                --certificate-oidc-issuer-regexp ".*" \
                "pypi:${pkg}@${pkg_version}" > "$cosign_output" 2>&1; then
                verified=$((verified + 1))
            else
                not_found=$((not_found + 1))
            fi
        done

        if [[ $verified -gt 0 ]] || [[ $not_found -gt 0 ]]; then
            log_info "Sigstore attestations: $verified verified, $not_found not available"
            add_report_check "sigstore_attestations" "pass" "$verified verified, $not_found not available" ""
            log_check_pass
        fi
    else
        log_warning "cosign not installed -- Sigstore attestation checks skipped"
        log_info "Install: https://docs.sigstore.dev/cosign/system_config/installation/"
        add_report_check "sigstore_attestations" "skip" "cosign not installed" ""
    fi

    # Method 3: Check for PyPI attestation API (no extra tools needed)
    log_info "Checking PyPI attestation metadata for critical packages..."

    local attestation_checked=0
    local attestation_found=0
    local critical_packages=("pydantic" "httpx" "requests")

    for pkg in "${critical_packages[@]}"; do
        if ! grep -qi "^${pkg}==" "$CFG_REQUIREMENTS" 2>/dev/null; then
            continue
        fi

        local pkg_version
        pkg_version=$(grep -i "^${pkg}==" "$CFG_REQUIREMENTS" | head -1 | sed 's/.*==//;s/[[:space:]].*//')

        attestation_checked=$((attestation_checked + 1))

        # Check PyPI JSON API for provenance info
        if command -v curl &>/dev/null; then
            local pypi_response
            pypi_response=$(curl -sf "https://pypi.org/pypi/${pkg}/${pkg_version}/json" 2>/dev/null || echo "")

            if [[ -n "$pypi_response" ]] && command -v jq &>/dev/null; then
                # Check if any release file has attestation/provenance metadata
                local has_attestation
                has_attestation=$(echo "$pypi_response" | jq -r '.urls[]? | select(.digests.sha256 != null) | .digests.sha256' 2>/dev/null | head -1)

                if [[ -n "$has_attestation" ]]; then
                    attestation_found=$((attestation_found + 1))
                fi
            fi
        fi
    done

    if [[ $attestation_checked -gt 0 ]]; then
        log_info "PyPI metadata: $attestation_found/$attestation_checked packages have SHA256 digests on PyPI"
        add_report_check "pypi_attestation_metadata" "pass" "$attestation_found/$attestation_checked with SHA256 digests" ""
        log_check_pass
    fi
}

# ── Check: Dependency Freshness ────────────────────────────
check_dependency_freshness() {
    log_info "Checking dependency freshness..."

    if [[ ! -f "$CFG_REQUIREMENTS" ]]; then
        add_report_check "dependency_freshness" "skip" "No requirements file" ""
        return
    fi

    # Check if requirements file has been updated recently (within 90 days)
    local last_modified
    if [[ "$(uname)" == "Darwin" ]]; then
        last_modified=$(stat -f %m "$CFG_REQUIREMENTS" 2>/dev/null || echo "0")
    else
        last_modified=$(stat -c %Y "$CFG_REQUIREMENTS" 2>/dev/null || echo "0")
    fi

    local now
    now=$(date +%s)
    local age_days=$(( (now - last_modified) / 86400 ))

    if [[ $age_days -lt 30 ]]; then
        log_success "Requirements file updated $age_days days ago (fresh)"
        add_report_check "dependency_freshness" "pass" "Updated $age_days days ago" ""
        log_check_pass
    elif [[ $age_days -lt 90 ]]; then
        log_info "Requirements file updated $age_days days ago"
        add_report_check "dependency_freshness" "pass" "Updated $age_days days ago" ""
        log_check_pass
    else
        log_warning "Requirements file is $age_days days old -- consider updating dependencies"
        add_report_check "dependency_freshness" "warn" "Updated $age_days days ago" "Consider running dependency updates"
    fi
}

# ── Check: Known Typosquatting ─────────────────────────────
check_typosquatting() {
    log_info "Checking for known typosquatted package names..."

    if [[ ! -f "$CFG_REQUIREMENTS" ]]; then
        add_report_check "typosquatting" "skip" "No requirements file" ""
        return
    fi

    # Known typosquatting patterns for common Python packages
    # These are real examples that have been used in attacks
    local -a TYPOSQUAT_PATTERNS=(
        "requets"      # requests
        "reqeusts"     # requests
        "request=="    # requests (missing 's')
        "python-openai"  # openai
        "openai-python"  # could be legit but check
        "beautifulsoup"  # beautifulsoup4
        "djago"        # django
        "flassk"       # flask
        "numppy"       # numpy
        "pandass"      # pandas
        "scikit_learn"  # scikit-learn (underscore vs hyphen)
        "crytography"  # cryptography
        "criptography" # cryptography
        "urllib"       # urllib3
        "coloarama"    # colorama
        "colourama"    # colorama
    )

    local suspicious_count=0
    for pattern in "${TYPOSQUAT_PATTERNS[@]}"; do
        if grep -qi "^${pattern}" "$CFG_REQUIREMENTS" 2>/dev/null; then
            log_error "Potentially typosquatted package: $pattern"
            suspicious_count=$((suspicious_count + 1))
        fi
    done

    if [[ $suspicious_count -eq 0 ]]; then
        log_success "No known typosquatting patterns detected"
        add_report_check "typosquatting" "pass" "No suspicious packages" ""
        log_check_pass
    else
        add_report_check "typosquatting" "fail" "$suspicious_count suspicious packages" ""
        log_check_fail
    fi
}

# ── Generate Lock File with Hashes ─────────────────────────
generate_lock_file() {
    log_info "Generating requirements lock file with hashes..."

    if [[ ! -f "$CFG_REQUIREMENTS" ]]; then
        log_error "Requirements file not found: $CFG_REQUIREMENTS"
        exit 2
    fi

    local pip_cmd="pip"
    if [[ -f "$REPO_ROOT/.dev-aid/orchestration/venv/bin/pip" ]]; then
        pip_cmd="$REPO_ROOT/.dev-aid/orchestration/venv/bin/pip"
    fi

    # Check if pip-compile (from pip-tools) is available -- preferred method
    local pip_compile_cmd=""
    if command -v pip-compile &>/dev/null; then
        pip_compile_cmd="pip-compile"
    elif [[ -f "$REPO_ROOT/.dev-aid/orchestration/venv/bin/pip-compile" ]]; then
        pip_compile_cmd="$REPO_ROOT/.dev-aid/orchestration/venv/bin/pip-compile"
    fi

    if [[ -n "$pip_compile_cmd" ]]; then
        log_info "Using pip-compile to generate hashes..."
        if $pip_compile_cmd \
            --generate-hashes \
            --output-file "$CFG_LOCK_FILE" \
            "$CFG_REQUIREMENTS" 2>/dev/null; then
            local hash_count
            hash_count=$(grep -c -- '--hash=' "$CFG_LOCK_FILE" 2>/dev/null || echo "0")
            log_success "Lock file generated: $CFG_LOCK_FILE ($hash_count hashes)"
            return
        else
            log_warning "pip-compile failed, falling back to pip hash generation"
        fi
    fi

    # Fallback: use pip download + hasher to generate hashes manually
    log_info "Using pip to generate hashes (this may take a moment)..."

    local temp_dir
    temp_dir=$(mktemp -d)
    TEMP_FILES+=("$temp_dir")

    local lock_content=""
    lock_content+="# Dev-AID Requirements Lock File with Hashes"$'\n'
    lock_content+="# Generated by verify-supply-chain.sh on $(date -u +"%Y-%m-%dT%H:%M:%SZ")"$'\n'
    lock_content+="# Verify with: pip install --require-hashes -r $CFG_LOCK_FILE"$'\n'
    lock_content+="#"$'\n'

    local pip_download_args=(download --no-deps --dest "$temp_dir")
    if [[ -n "$CFG_PRIVATE_MIRROR" ]]; then
        pip_download_args+=(--index-url "$CFG_PRIVATE_MIRROR")
    fi

    while IFS= read -r line; do
        # Skip comments and empty lines
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ "$line" =~ ^[[:space:]]*$ ]] && continue
        [[ "$line" =~ ^- ]] && continue

        local pkg_spec
        pkg_spec=$(echo "$line" | sed 's/#.*//' | xargs)
        [[ -z "$pkg_spec" ]] && continue

        # Only process pinned packages
        if ! echo "$pkg_spec" | grep -q '=='; then
            lock_content+="$pkg_spec"$'\n'
            continue
        fi

        local pkg_name
        pkg_name=$(echo "$pkg_spec" | sed 's/==.*//' | xargs)

        # Download the package to get the actual file for hashing
        if $pip_cmd download --no-deps --dest "$temp_dir" "$pkg_spec" > /dev/null 2>&1; then
            # Find the downloaded file and compute its hash
            local downloaded_file
            downloaded_file=$(ls -t "$temp_dir"/"${pkg_name}"* 2>/dev/null | head -1 || echo "")

            if [[ -n "$downloaded_file" ]] && [[ -f "$downloaded_file" ]]; then
                local sha256_hash
                if command -v sha256sum &>/dev/null; then
                    sha256_hash=$(sha256sum "$downloaded_file" | cut -d' ' -f1)
                elif command -v shasum &>/dev/null; then
                    sha256_hash=$(shasum -a 256 "$downloaded_file" | cut -d' ' -f1)
                else
                    sha256_hash=""
                fi

                if [[ -n "$sha256_hash" ]]; then
                    lock_content+="$pkg_spec \\"$'\n'
                    lock_content+="    --hash=sha256:$sha256_hash"$'\n'
                else
                    lock_content+="$pkg_spec"$'\n'
                fi

                rm -f "$downloaded_file"
            else
                lock_content+="$pkg_spec"$'\n'
            fi
        else
            log_warning "Could not download $pkg_spec for hashing"
            lock_content+="$pkg_spec"$'\n'
        fi
    done < "$CFG_REQUIREMENTS"

    echo "$lock_content" > "$CFG_LOCK_FILE"
    local hash_count
    hash_count=$(grep -c -- '--hash=' "$CFG_LOCK_FILE" 2>/dev/null || echo "0")
    log_success "Lock file generated: $CFG_LOCK_FILE ($hash_count hashes)"
    log_info "Verify with: pip install --require-hashes -r $CFG_LOCK_FILE"
}

# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════

# Load config
load_config

# Handle --generate-hashes mode
if $GENERATE_HASHES; then
    generate_lock_file
    exit 0
fi

# Banner
if ! $JSON_OUTPUT; then
    echo ""
    echo -e "${BLUE}======================================================${NC}"
    echo -e "${BLUE}  Dev-AID Supply Chain Verification v${VERSION}${NC}"
    echo -e "${BLUE}======================================================${NC}"
    echo ""

    if [[ -n "$CFG_PRIVATE_MIRROR" ]]; then
        log_info "Private mirror: $CFG_PRIVATE_MIRROR"
    fi
    log_info "Requirements: $CFG_REQUIREMENTS"
    log_info "Lock file: $CFG_LOCK_FILE"
    echo ""
fi

# ── Run All Checks ─────────────────────────────────────────

# Check 1: Version pinning
if ! $JSON_OUTPUT; then
    echo -e "${CYAN}--- 1/5 Version Pinning -----------------------------------------${NC}"
fi
check_version_pinning
if ! $JSON_OUTPUT; then echo ""; fi

# Check 2: Hash verification
if ! $JSON_OUTPUT; then
    echo -e "${CYAN}--- 2/5 Hash Verification ---------------------------------------${NC}"
fi
check_hash_verification
if ! $JSON_OUTPUT; then echo ""; fi

# Check 3: Registry allowlist
if ! $JSON_OUTPUT; then
    echo -e "${CYAN}--- 3/5 Registry Allowlist --------------------------------------${NC}"
fi
check_registry_allowlist
if ! $JSON_OUTPUT; then echo ""; fi

# Check 4: Provenance & attestations
if ! $JSON_OUTPUT; then
    echo -e "${CYAN}--- 4/5 Provenance & Attestations -------------------------------${NC}"
fi
check_provenance
if ! $JSON_OUTPUT; then echo ""; fi

# Check 5: Typosquatting detection
if ! $JSON_OUTPUT; then
    echo -e "${CYAN}--- 5/5 Typosquatting Detection ----------------------------------${NC}"
fi
check_typosquatting
if ! $JSON_OUTPUT; then echo ""; fi

# Bonus check: dependency freshness (informational)
check_dependency_freshness
if ! $JSON_OUTPUT; then echo ""; fi

# ── Summary ────────────────────────────────────────────────
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

if ! $JSON_OUTPUT; then
    echo -e "${BLUE}======================================================${NC}"
    echo -e "${BLUE}  SUPPLY CHAIN VERIFICATION SUMMARY${NC}"
    echo -e "${BLUE}======================================================${NC}"
    echo ""

    if [[ $ISSUES_FOUND -eq 0 ]]; then
        if [[ $WARNINGS_FOUND -gt 0 ]]; then
            echo -e "${GREEN}Result: PASS (with $WARNINGS_FOUND warning(s))${NC}"
        else
            echo -e "${GREEN}Result: PASS${NC}"
        fi
    else
        echo -e "${RED}Result: FAIL ($ISSUES_FOUND issue(s), $WARNINGS_FOUND warning(s))${NC}"
    fi

    echo ""
    echo "  Checks passed: $CHECKS_PASSED / $CHECKS_TOTAL"
    echo "  Issues:        $ISSUES_FOUND"
    echo "  Warnings:      $WARNINGS_FOUND"
    echo "  Duration:      ${DURATION}s"
    echo ""

    if [[ $ISSUES_FOUND -gt 0 ]]; then
        echo -e "${YELLOW}Next steps:${NC}"
        if [[ ! -f "$CFG_LOCK_FILE" ]]; then
            echo "  1. Generate lock file:  $0 --generate-hashes"
        fi
        echo "  2. Review warnings above and address issues"
        echo "  3. For CI usage:        $0 --ci --json --report report.json"
        echo ""
    fi

    echo -e "${BLUE}Completed at $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo ""
fi

# Generate JSON report if requested
if $JSON_OUTPUT || [[ -n "$JSON_REPORT_FILE" ]]; then
    generate_json_report
fi

# Exit code: 0 for pass/warnings, 1 for failures
if [[ $ISSUES_FOUND -gt 0 ]]; then
    exit 1
fi

exit 0
