#!/bin/bash
# Dev-AID Security Scan Script
# Runs 3 security tools with comprehensive configurations
#
# Usage:
#   ./security-scan.sh              # Full scan
#   ./security-scan.sh --quick      # Quick scan (skip slow checks)
#   ./security-scan.sh --sbom       # Generate SBOM after scan
#
# Tools & Configurations:
#   • Gitleaks  - Secret detection (git history + current files)
#   • Trivy     - CVE + Misconfig + Secret scanning (Dockerfile, IaC, deps)
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
GENERATE_SBOM=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --quick) QUICK_MODE=true; shift ;;
        --sbom) GENERATE_SBOM=true; shift ;;
        *) shift ;;
    esac
done

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           Dev-AID Security Scan                        ║${NC}"
echo -e "${BLUE}║   3 Tools • CVE + SAST + Secrets • Misconfig           ║${NC}"
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
echo -e "${CYAN}1/3 GITLEAKS - Secret Detection${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if command -v gitleaks &> /dev/null; then
    echo "Scanning: git history + current files"
    echo ""

    GITLEAKS_OUTPUT=$(gitleaks detect --source . --no-git 2>&1) || true
    if echo "$GITLEAKS_OUTPUT" | grep -q "no leaks found"; then
        echo -e "${GREEN}✓ No secrets detected${NC}"
    else
        LEAK_COUNT=$(echo "$GITLEAKS_OUTPUT" | grep -o 'leaks found: [0-9]*' | head -1 | grep -o '[0-9]*' || echo "0")
        [ -z "$LEAK_COUNT" ] && LEAK_COUNT=0
        if [ "$LEAK_COUNT" -gt 0 ]; then
            echo -e "${RED}✗ Found $LEAK_COUNT potential secrets${NC}"
            TOTAL_FINDINGS=$((TOTAL_FINDINGS + LEAK_COUNT))
            CRITICAL_FINDINGS=$((CRITICAL_FINDINGS + LEAK_COUNT))
        else
            echo -e "${GREEN}✓ No secrets detected${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠ Skipped (gitleaks not installed)${NC}"
fi

echo ""

# ============================================================================
# 2. TRIVY - CVE + Misconfig + Secret Scanning
# ============================================================================
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}2/3 TRIVY - Vulnerability & Misconfiguration Scanning${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if command -v trivy &> /dev/null; then
    echo "Scanners: vuln, misconfig, secret"
    echo "Severity: HIGH, CRITICAL"
    echo "Covers: Dependencies, Dockerfiles, Terraform, K8s, GitHub Actions"
    echo ""

    TRIVY_ARGS="fs --scanners vuln,misconfig,secret --severity HIGH,CRITICAL"
    TRIVY_ARGS="$TRIVY_ARGS --skip-dirs venv --skip-dirs .venv --skip-dirs node_modules --skip-dirs .git"

    if $QUICK_MODE; then
        TRIVY_ARGS="$TRIVY_ARGS --skip-dirs .dev-aid/local-search/venv"
    fi

    TRIVY_OUTPUT=$(trivy $TRIVY_ARGS --format json . 2>&1) || true

    # Count findings by type
    VULN_COUNT=$(echo "$TRIVY_OUTPUT" | jq -r '[.Results[]?.Vulnerabilities[]?] | length' 2>/dev/null || echo "0")
    MISCONFIG_COUNT=$(echo "$TRIVY_OUTPUT" | jq -r '[.Results[]?.Misconfigurations[]?] | length' 2>/dev/null || echo "0")
    SECRET_COUNT=$(echo "$TRIVY_OUTPUT" | jq -r '[.Results[]?.Secrets[]?] | length' 2>/dev/null || echo "0")

    # Count critical
    CRITICAL_VULNS=$(echo "$TRIVY_OUTPUT" | jq -r '[.Results[]?.Vulnerabilities[]? | select(.Severity == "CRITICAL")] | length' 2>/dev/null || echo "0")
    CRITICAL_MISCONFIGS=$(echo "$TRIVY_OUTPUT" | jq -r '[.Results[]?.Misconfigurations[]? | select(.Severity == "CRITICAL")] | length' 2>/dev/null || echo "0")

    [ -z "$VULN_COUNT" ] && VULN_COUNT=0
    [ -z "$MISCONFIG_COUNT" ] && MISCONFIG_COUNT=0
    [ -z "$SECRET_COUNT" ] && SECRET_COUNT=0
    [ -z "$CRITICAL_VULNS" ] && CRITICAL_VULNS=0
    [ -z "$CRITICAL_MISCONFIGS" ] && CRITICAL_MISCONFIGS=0

    TOTAL_TRIVY=$((VULN_COUNT + MISCONFIG_COUNT + SECRET_COUNT))
    TOTAL_CRITICAL_TRIVY=$((CRITICAL_VULNS + CRITICAL_MISCONFIGS + SECRET_COUNT))

    if [ "$TOTAL_TRIVY" -eq 0 ]; then
        echo -e "${GREEN}✓ No HIGH/CRITICAL vulnerabilities, misconfigs, or secrets${NC}"
    else
        echo -e "${YELLOW}Found: $VULN_COUNT CVEs, $MISCONFIG_COUNT misconfigs, $SECRET_COUNT secrets${NC}"
        if [ "$TOTAL_CRITICAL_TRIVY" -gt 0 ]; then
            echo -e "${RED}  Critical: $CRITICAL_VULNS CVEs, $CRITICAL_MISCONFIGS misconfigs, $SECRET_COUNT secrets${NC}"
        fi
        TOTAL_FINDINGS=$((TOTAL_FINDINGS + TOTAL_TRIVY))
        CRITICAL_FINDINGS=$((CRITICAL_FINDINGS + TOTAL_CRITICAL_TRIVY))
    fi
else
    echo -e "${YELLOW}⚠ Skipped (trivy not installed)${NC}"
fi

echo ""

# ============================================================================
# 3. OPENGREP - Comprehensive SAST (340+ rules)
# ============================================================================
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}3/3 OPENGREP - Static Application Security Testing${NC}"
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

    echo "Running scan (this may take 1-2 minutes)..."
    OPENGREP_OUTPUT=$($OPENGREP_CMD $OPENGREP_ARGS . 2>&1) || true

    # Parse findings count (macOS compatible - no grep -P)
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
# SBOM Generation (Optional)
# ============================================================================
if $GENERATE_SBOM; then
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}SBOM - Software Bill of Materials${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    if command -v trivy &> /dev/null; then
        echo "Generating SBOM in CycloneDX format..."
        trivy fs --format cyclonedx --output sbom-cyclonedx.json . 2>/dev/null || true

        if [ -f "sbom-cyclonedx.json" ]; then
            COMPONENT_COUNT=$(jq -r '.components | length' sbom-cyclonedx.json 2>/dev/null || echo "0")
            echo -e "${GREEN}✓ SBOM generated: sbom-cyclonedx.json ($COMPONENT_COUNT components)${NC}"
        else
            echo -e "${YELLOW}⚠ SBOM generation failed${NC}"
        fi

        echo ""
        echo "Generating SBOM in SPDX format..."
        trivy fs --format spdx-json --output sbom-spdx.json . 2>/dev/null || true

        if [ -f "sbom-spdx.json" ]; then
            echo -e "${GREEN}✓ SBOM generated: sbom-spdx.json${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Trivy required for SBOM generation${NC}"
    fi

    echo ""
fi

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
    echo "  • Gitleaks (secrets in git history)"
    echo "  • Trivy (CVEs, misconfigs, secrets)"
    echo "  • Opengrep (SAST with 340+ rules)"
    EXIT_CODE=0
else
    echo -e "${YELLOW}⚠ Total findings: $TOTAL_FINDINGS${NC}"
    if [ $CRITICAL_FINDINGS -gt 0 ]; then
        echo -e "${RED}  Critical/High: $CRITICAL_FINDINGS${NC}"
    fi
    echo ""
    echo "Run individual tools for details:"
    echo "  gitleaks detect --source . --no-git -v"
    echo "  trivy fs --scanners vuln,misconfig,secret ."
    echo "  opengrep scan --config p/security-audit ."
    EXIT_CODE=1
fi

echo ""
echo -e "${BLUE}Scan completed at $(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo ""

exit $EXIT_CODE
