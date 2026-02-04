#!/bin/bash
# Dev-AID Security Scan Script
# Runs all 5 security tools with best-practice configurations
#
# Usage:
#   ./security-scan.sh              # Full scan
#   ./security-scan.sh --quick      # Quick scan (skip slow checks)
#   ./security-scan.sh --fix        # Auto-fix where possible
#
# Tools & Configurations:
#   • Gitleaks  - Secret detection with .gitleaks.toml config
#   • Trivy     - Vulnerability + secret + misconfig scanning
#   • Hadolint  - Dockerfile linting (if Dockerfiles exist)
#   • Checkov   - IaC security for Terraform/K8s/GitHub Actions
#   • Opengrep  - Comprehensive SAST with 340+ rules:
#       - p/default        (Semgrep curated defaults)
#       - p/security-audit (comprehensive security)
#       - p/secrets        (hardcoded credentials)
#       - p/ci             (CI/CD security)
#       - p/cwe-top-25     (MITRE CWE Top 25)
#
# References:
#   https://semgrep.dev/r (rule registry)
#   https://aquasecurity.github.io/trivy/
#   https://github.com/gitleaks/gitleaks
#   https://www.checkov.io/

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Counters
TOTAL_FINDINGS=0
CRITICAL_FINDINGS=0

# Parse arguments
QUICK_MODE=false
AUTO_FIX=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --quick) QUICK_MODE=true; shift ;;
        --fix) AUTO_FIX=true; shift ;;
        *) shift ;;
    esac
done

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           Dev-AID Security Scan                        ║${NC}"
echo -e "${BLUE}║   5 Tools • OWASP Top 10 • Best Practices              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check for required tools
check_tool() {
    if command -v "$1" &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} $1 $(command -v "$1")"
        return 0
    elif [ -f "$HOME/.local/bin/$1" ]; then
        echo -e "  ${GREEN}✓${NC} $1 (~/.local/bin/$1)"
        export PATH="$HOME/.local/bin:$PATH"
        return 0
    else
        echo -e "  ${RED}✗${NC} $1 not found"
        return 1
    fi
}

echo -e "${CYAN}Checking tools...${NC}"
MISSING_TOOLS=0
check_tool gitleaks || MISSING_TOOLS=$((MISSING_TOOLS + 1))
check_tool trivy || MISSING_TOOLS=$((MISSING_TOOLS + 1))
check_tool hadolint || MISSING_TOOLS=$((MISSING_TOOLS + 1))
check_tool checkov || MISSING_TOOLS=$((MISSING_TOOLS + 1))
check_tool opengrep || MISSING_TOOLS=$((MISSING_TOOLS + 1))

if [ $MISSING_TOOLS -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}⚠ $MISSING_TOOLS tool(s) missing. Install with:${NC}"
    echo "  ./.dev-aid/automation/tools/install-security-tools.sh"
    echo ""
fi

echo ""

# ============================================================================
# 1. GITLEAKS - Secret Detection
# ============================================================================
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}1/5 GITLEAKS - Secret Detection${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if command -v gitleaks &> /dev/null; then
    echo "Config: .gitleaks.toml (path exclusions for test/docs)"
    echo ""

    GITLEAKS_OUTPUT=$(gitleaks detect --source . --no-git 2>&1) || true
    if echo "$GITLEAKS_OUTPUT" | grep -q "no leaks found"; then
        echo -e "${GREEN}✓ No secrets detected${NC}"
    else
        LEAK_COUNT=$(echo "$GITLEAKS_OUTPUT" | grep -oP 'leaks found: \K\d+' || echo "0")
        echo -e "${RED}✗ Found $LEAK_COUNT potential secrets${NC}"
        TOTAL_FINDINGS=$((TOTAL_FINDINGS + LEAK_COUNT))
        CRITICAL_FINDINGS=$((CRITICAL_FINDINGS + LEAK_COUNT))
    fi
else
    echo -e "${YELLOW}⚠ Skipped (gitleaks not installed)${NC}"
fi

echo ""

# ============================================================================
# 2. TRIVY - Vulnerability & Misconfiguration Scanning
# ============================================================================
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}2/5 TRIVY - Vulnerability Scanning${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if command -v trivy &> /dev/null; then
    echo "Scanners: vuln, misconfig"
    echo "Severity: HIGH, CRITICAL"
    echo "Skip: venv, node_modules, .git"
    echo ""

    TRIVY_ARGS="fs --scanners vuln,misconfig --severity HIGH,CRITICAL"
    TRIVY_ARGS="$TRIVY_ARGS --skip-dirs venv --skip-dirs .venv --skip-dirs node_modules --skip-dirs .git"

    if $QUICK_MODE; then
        TRIVY_ARGS="$TRIVY_ARGS --skip-dirs .dev-aid/local-search/venv"
    fi

    TRIVY_OUTPUT=$(trivy $TRIVY_ARGS . 2>&1) || true

    # Count HIGH/CRITICAL findings (handle empty/zero gracefully)
    VULN_COUNT=$(echo "$TRIVY_OUTPUT" | grep -cE "HIGH|CRITICAL" 2>/dev/null || echo "0")
    VULN_COUNT=$(echo "$VULN_COUNT" | tr -d '[:space:]')
    [ -z "$VULN_COUNT" ] && VULN_COUNT=0

    if [ "$VULN_COUNT" -eq 0 ]; then
        echo -e "${GREEN}✓ No HIGH/CRITICAL vulnerabilities${NC}"
    else
        echo -e "${YELLOW}⚠ Found $VULN_COUNT HIGH/CRITICAL items${NC}"
        TOTAL_FINDINGS=$((TOTAL_FINDINGS + VULN_COUNT))
    fi
else
    echo -e "${YELLOW}⚠ Skipped (trivy not installed)${NC}"
fi

echo ""

# ============================================================================
# 3. HADOLINT - Dockerfile Linting
# ============================================================================
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}3/5 HADOLINT - Dockerfile Linting${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

DOCKERFILES=$(find . -name "Dockerfile*" -not -path "./.git/*" -not -path "*/venv/*" 2>/dev/null)

if [ -z "$DOCKERFILES" ]; then
    echo -e "${BLUE}ℹ No Dockerfiles found${NC}"
elif command -v hadolint &> /dev/null; then
    HADOLINT_ERRORS=0
    for df in $DOCKERFILES; do
        echo "Scanning: $df"
        HADOLINT_OUTPUT=$(hadolint --failure-threshold error "$df" 2>&1) || true
        if [ -n "$HADOLINT_OUTPUT" ]; then
            echo "$HADOLINT_OUTPUT"
            HADOLINT_ERRORS=$((HADOLINT_ERRORS + 1))
        fi
    done

    if [ $HADOLINT_ERRORS -eq 0 ]; then
        echo -e "${GREEN}✓ All Dockerfiles pass${NC}"
    else
        echo -e "${YELLOW}⚠ $HADOLINT_ERRORS Dockerfile(s) have issues${NC}"
        TOTAL_FINDINGS=$((TOTAL_FINDINGS + HADOLINT_ERRORS))
    fi
else
    echo -e "${YELLOW}⚠ Skipped (hadolint not installed)${NC}"
fi

echo ""

# ============================================================================
# 4. CHECKOV - IaC Security
# ============================================================================
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}4/5 CHECKOV - Infrastructure as Code Security${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if command -v checkov &> /dev/null; then
    echo "Scanning: .github/workflows, .dev-aid/templates"
    echo "Framework: GitHub Actions, Kubernetes, Terraform"
    echo ""

    CHECKOV_DIRS=""
    [ -d ".github" ] && CHECKOV_DIRS="$CHECKOV_DIRS -d .github"
    [ -d ".dev-aid/templates" ] && CHECKOV_DIRS="$CHECKOV_DIRS -d .dev-aid/templates"

    if [ -n "$CHECKOV_DIRS" ]; then
        CHECKOV_OUTPUT=$(checkov $CHECKOV_DIRS --quiet --compact 2>&1) || true
        CHECKOV_FAILED=$(echo "$CHECKOV_OUTPUT" | grep -c "FAILED" || echo "0")

        if [ "$CHECKOV_FAILED" -eq 0 ]; then
            echo -e "${GREEN}✓ IaC security checks pass${NC}"
        else
            echo -e "${YELLOW}⚠ $CHECKOV_FAILED IaC issues found${NC}"
            TOTAL_FINDINGS=$((TOTAL_FINDINGS + CHECKOV_FAILED))
        fi
    else
        echo -e "${BLUE}ℹ No IaC directories found${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Skipped (checkov not installed)${NC}"
fi

echo ""

# ============================================================================
# 5. OPENGREP - Comprehensive SAST (340+ rules)
# ============================================================================
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}5/5 OPENGREP - Static Application Security Testing${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

OPENGREP_CMD="opengrep"
[ -f "$HOME/.local/bin/opengrep" ] && OPENGREP_CMD="$HOME/.local/bin/opengrep"

if command -v $OPENGREP_CMD &> /dev/null; then
    echo "Rulesets (340+ rules):"
    echo "  • p/default        - Semgrep's curated default rules"
    echo "  • p/security-audit - Comprehensive security patterns"
    echo "  • p/secrets        - Hardcoded secrets & credentials"
    echo "  • p/ci             - CI/CD security (GitHub Actions, etc)"
    echo "  • p/cwe-top-25     - MITRE CWE Top 25 vulnerabilities"
    echo ""

    # Build command with comprehensive rulesets
    OPENGREP_ARGS="scan"
    OPENGREP_ARGS="$OPENGREP_ARGS --config p/default"
    OPENGREP_ARGS="$OPENGREP_ARGS --config p/security-audit"
    OPENGREP_ARGS="$OPENGREP_ARGS --config p/secrets"
    OPENGREP_ARGS="$OPENGREP_ARGS --config p/ci"
    OPENGREP_ARGS="$OPENGREP_ARGS --config p/cwe-top-25"

    if $AUTO_FIX; then
        OPENGREP_ARGS="$OPENGREP_ARGS --autofix"
    fi

    echo "Running scan (this may take 1-2 minutes)..."
    OPENGREP_OUTPUT=$($OPENGREP_CMD $OPENGREP_ARGS . 2>&1) || true

    # Parse findings count and rules count (macOS compatible - no grep -P)
    OPENGREP_COUNT=$(echo "$OPENGREP_OUTPUT" | grep -o '[0-9]* findings' | head -1 | grep -o '[0-9]*' || echo "0")
    RULES_COUNT=$(echo "$OPENGREP_OUTPUT" | grep -o 'Ran [0-9]*' | head -1 | grep -o '[0-9]*' || echo "340+")
    [ -z "$OPENGREP_COUNT" ] && OPENGREP_COUNT=0

    if [ "$OPENGREP_COUNT" -eq 0 ]; then
        echo -e "${GREEN}✓ No SAST findings (scanned with $RULES_COUNT rules)${NC}"
    else
        echo -e "${RED}✗ Found $OPENGREP_COUNT SAST issues (from $RULES_COUNT rules)${NC}"
        echo ""
        # Show summary of findings
        echo "$OPENGREP_OUTPUT" | grep -E "❯❯❱|❯❱" | head -20
        TOTAL_FINDINGS=$((TOTAL_FINDINGS + OPENGREP_COUNT))
        CRITICAL_FINDINGS=$((CRITICAL_FINDINGS + OPENGREP_COUNT))
    fi
else
    echo -e "${YELLOW}⚠ Skipped (opengrep not installed)${NC}"
    echo "  Install: curl -fsSL https://raw.githubusercontent.com/opengrep/opengrep/main/install.sh | bash"
fi

echo ""

# ============================================================================
# Summary
# ============================================================================
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    SCAN SUMMARY                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ $TOTAL_FINDINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All security scans passed!${NC}"
    echo ""
    echo "Your codebase has no detected issues from:"
    echo "  • Gitleaks (secrets)"
    echo "  • Trivy (vulnerabilities)"
    echo "  • Hadolint (Dockerfiles)"
    echo "  • Checkov (IaC)"
    echo "  • Opengrep (OWASP Top 10)"
    EXIT_CODE=0
else
    echo -e "${YELLOW}⚠ Total findings: $TOTAL_FINDINGS${NC}"
    if [ $CRITICAL_FINDINGS -gt 0 ]; then
        echo -e "${RED}  Critical/High: $CRITICAL_FINDINGS${NC}"
    fi
    echo ""
    echo "Run individual tools for details:"
    echo "  gitleaks detect --source . --no-git -v"
    echo "  trivy fs --scanners vuln,misconfig ."
    echo "  checkov -d .github --compact"
    echo "  opengrep scan --config p/security-audit ."
    EXIT_CODE=1
fi

echo ""
echo -e "${BLUE}Scan completed at $(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo ""

exit $EXIT_CODE
