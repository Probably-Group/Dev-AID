#!/usr/bin/env bash
# Dev-AID Guide - Interactive Manual
# Feature discovery and best practices

set -euo pipefail

readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'

show_menu() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🚀 Dev-AID Interactive Guide${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "What do you want to do?"
    echo ""
    echo -e "${GREEN}1.${NC} 🏗️  Start a new project"
    echo -e "${GREEN}2.${NC} 🐛 Fix a bug or review code"
    echo -e "${GREEN}3.${NC} 🤖 Auto-generate CI/CD workflows"
    echo -e "${GREEN}4.${NC} 📊 Visualize architecture"
    echo -e "${GREEN}5.${NC} 🧪 Generate test data"
    echo -e "${GREEN}6.${NC} 📚 Check documentation drift"
    echo -e "${GREEN}7.${NC} 📖 View all available commands"
    echo -e "${GREEN}8.${NC} 💡 Best practices & tips"
    echo -e "${GREEN}9.${NC} ❌ Exit"
    echo ""
}

show_new_project() {
    echo -e "\n${YELLOW}🏗️  Starting a New Project${NC}\n"
    echo "Recommended commands:"
    echo "  1. .dev-aid/scripts/generate-ci.sh"
    echo "     → Auto-generates GitHub Actions workflow"
    echo ""
    echo "  2. .dev-aid/scripts/setup-rag.sh"
    echo "     → Sets up local semantic search"
    echo ""
    echo "  3. .dev-aid/scripts/dev-aid-guide.sh"
    echo "     → This guide (you're already here!)"
}

show_bug_fix() {
    echo -e "\n${YELLOW}🐛 Fixing Bugs / Code Review${NC}\n"
    echo "Best practices:"
    echo "  • Use Challenger Mode for security-critical code"
    echo "    /dev-aid-router-challenger \"Fix auth bug\""
    echo ""
    echo "  • Let senior-architect skill review:"
    echo "    Keywords: review, audit, anti-pattern, technical debt"
    echo ""
    echo "  • Check docs are up to date:"
    echo "    .dev-aid/scripts/sync-docs.sh"
}

show_all_commands() {
    echo -e "\n${YELLOW}📖 Available Dev-AID Commands${NC}\n"
    echo "CI/CD:"
    echo "  .dev-aid/scripts/generate-ci.sh        Auto-generate workflows"
    echo ""
    echo "Architecture:"
    echo "  .dev-aid/scripts/map-architecture.sh   Generate Mermaid diagrams"
    echo ""
    echo "Testing:"
    echo "  .dev-aid/scripts/fabricate-data.sh     Generate mock test data"
    echo ""
    echo "Documentation:"
    echo "  .dev-aid/scripts/sync-docs.sh          Check doc drift"
    echo ""
    echo "Setup:"
    echo "  .dev-aid/scripts/setup-rag.sh          Install local RAG"
    echo "  .dev-aid/scripts/setup-venv.sh         Setup Python venv"
    echo ""
    echo "Router (Multi-AI):"
    echo "  /dev-aid-router-challenger             Two-model review"
    echo "  /dev-aid-router-ensemble               Auto-route by task"
    echo "  /dev-aid-router-status                 View routing stats"
}

show_best_practices() {
    echo -e "\n${YELLOW}💡 Best Practices & Tips${NC}\n"
    echo "Security:"
    echo "  ✓ Use Challenger Mode for auth, crypto, payments"
    echo "  ✓ All workflows include gitleaks + trivy by default"
    echo "  ✓ Pre-commit hooks block when security tools missing"
    echo ""
    echo "Performance:"
    echo "  ✓ Context detection is <200ms (10x faster)"
    echo "  ✓ VCR testing = $0 cost for API client tests"
    echo "  ✓ Local RAG = private + free forever"
    echo ""
    echo "Quality:"
    echo "  ✓ Pin all dependencies (reproducible builds)"
    echo "  ✓ Check doc drift before releases"
    echo "  ✓ Generate diagrams for complex refactors"
}

main() {
    while true; do
        show_menu
        read -r -p "Enter choice [1-9]: " choice

        case $choice in
            1) show_new_project ;;
            2) show_bug_fix ;;
            3) echo -e "\n${GREEN}→${NC} .dev-aid/scripts/generate-ci.sh" ;;
            4) echo -e "\n${GREEN}→${NC} .dev-aid/scripts/map-architecture.sh" ;;
            5) echo -e "\n${GREEN}→${NC} .dev-aid/scripts/fabricate-data.sh schema.json" ;;
            6) echo -e "\n${GREEN}→${NC} .dev-aid/scripts/sync-docs.sh" ;;
            7) show_all_commands ;;
            8) show_best_practices ;;
            9) echo -e "\n${GREEN}Goodbye!${NC}\n"; exit 0 ;;
            *) echo -e "\n${YELLOW}Invalid choice. Try again.${NC}" ;;
        esac

        echo ""
        read -r -p "Press Enter to continue..."
    done
}

main "$@"
