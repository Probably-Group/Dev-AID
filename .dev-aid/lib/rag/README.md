# RAG Dependency Management

## Overview

Dev-AID's local search functionality is powered by `claude-context-local`. To ensure stability and prevent breakage if the upstream repository becomes unavailable, we provide multiple installation strategies.

## Installation Strategies

### Option 1: Use Vendored Copy (Recommended for Production)

Fork the upstream repository to your organization and vendor it:

```bash
# 1. Fork https://github.com/FarhanAliRaza/claude-context-local to your org

# 2. Set the fork URL as an environment variable
export RAG_REPO_URL="https://github.com/YOUR_ORG/claude-context-local"

# 3. Run setup with custom repo
./.dev-aid/scripts/setup-rag.sh
```

### Option 2: Use Git Submodule (For Development)

Add the dependency as a submodule for version control:

```bash
# Add submodule
git submodule add https://github.com/FarhanAliRaza/claude-context-local .dev-aid/lib/rag/vendor/claude-context-local

# Initialize and update
git submodule update --init --recursive

# Run installation from vendored copy
./.dev-aid/scripts/setup-rag.sh --vendored
```

### Option 3: Use Upstream (Default, Less Stable)

Install directly from the upstream repository:

```bash
./.dev-aid/scripts/setup-rag.sh
```

**Warning:** This depends on the upstream repository remaining available.

## Maintenance

### Updating Vendored Copy

If using a fork:

```bash
# Pull latest changes from upstream
cd .dev-aid/lib/rag/vendor/claude-context-local
git pull origin main

# Update checksum in setup-rag.sh
curl -fsSL "https://raw.githubusercontent.com/YOUR_ORG/claude-context-local/main/scripts/install.sh" | shasum -a 256
```

### Updating Submodule

If using a submodule:

```bash
# Update to latest version
git submodule update --remote .dev-aid/lib/rag/vendor/claude-context-local

# Commit the update
git add .dev-aid/lib/rag/vendor/claude-context-local
git commit -m "chore: update RAG dependency"
```

## Security

All installation methods verify SHA256 checksums before execution. See `.dev-aid/scripts/setup-rag.sh` for checksum values.

To update checksums after vendoring:

```bash
# Calculate new checksum
curl -fsSL "YOUR_INSTALL_SCRIPT_URL" | shasum -a 256

# Update EXPECTED_CHECKSUM in setup-rag.sh
```

## Troubleshooting

### Repository Not Available

If the upstream repository is deleted:

1. Use one of the cached forks:
   - Check https://github.com/search?q=claude-context-local+fork
   - Or restore from Git history if previously vendored

2. Contact Dev-AID maintainers for the canonical fork

### Installation Fails

Check:
- Network connectivity
- Checksum matches (security verification)
- Python 3.12+ is installed
- Sufficient disk space (~2GB for models)
