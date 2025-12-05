# Dev-AID Changelog

All notable changes to Dev-AID will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] - 2025-12-05

### Added

#### Hook-Based Skill Auto-Loading (NEW!)
- **Intelligent Context Detection**: Analyzes project files, dependencies, and tech stack to identify relevant technologies
- **Scoring Algorithm**: Ranks skills using weighted scoring (primary keywords: 10pts, technologies: 8pts, secondary keywords: 5pts)
- **SessionStart Hooks**: Auto-loads relevant skills once per session for both Claude Code and Gemini CLI
- **External Registry**: `.dev-aid/skills/registry/skills-index.json` with activation metadata for all skills
- **Universal Architecture**: Same auto-loading logic works across all AI providers

#### New Components
- **detect-context.sh**: Scans project for file patterns, config files (package.json, requirements.txt), and technology indicators
- **select-skills.sh**: Intelligent skill selector with scoring, conflict resolution, and dependency management
- **validate-bash-scripts.sh**: Compliance checker for bash-expert skill guidelines (32 validation checks)
- **Claude SessionStart Hook**: `.dev-aid/providers/claude/.claude/hooks/session-start.sh` displays auto-loaded skills
- **Gemini SessionStart Hook**: `.dev-aid/providers/gemini/.gemini/hooks/session-start.sh` updates GEMINI.md once per session
- **Gemini Configuration**: `.dev-aid/providers/gemini/.gemini/settings.json` for hook management

#### Skills Registry
- **10 Initial Skills**: api-expert, bash-expert, devsecops-expert, typescript-expert, fastapi-expert, graphql-expert, docker-expert, python, rust, cicd-expert
- **Metadata Format**: Keywords, file patterns, technologies, confidence weights, dependencies, exclusions
- **Extensible Design**: Easy to add new skills with activation rules

### Changed
- **GEMINI.md Update Strategy**: Now updated ONCE at session start (not after every prompt) for better performance
- **Skills Architecture**: Enhanced from v2.0 (Shared Skills) to v3.0 (Hook-Based Auto-Loading + Shared Skills)
- **Documentation**: Comprehensive update to SKILLS-ARCHITECTURE.md with new sections on hook-based system

### Technical Details
- **Compliance**: All Bash scripts follow bash-expert skill guidelines with strict mode, proper quoting, input validation
- **Validation**: 32/32 checks passed for bash-expert compliance
- **JSON Validation**: All JSON files validated with jq
- **Testing**: End-to-end testing confirmed for both Claude and Gemini providers

### Benefits
- ✅ **Zero manual skill management** - Skills auto-load based on project context
- ✅ **GEMINI.md efficiency** - Updated once per session, not per prompt
- ✅ **Multi-provider consistency** - Same logic for Claude, Gemini, future providers
- ✅ **Intelligent selection** - Top 5 relevant skills chosen automatically
- ✅ **Respects limits** - Honors Claude's 2000-line Read tool limit

---

## [1.0.0] - 2025-12-04

### Added

#### Multi-AI Router (NEW!)
- **Challenger Mode**: Claude generates, Gemini reviews, with optional auto-refinement
- **Ensemble Mode**: Automatic routing to optimal AI based on task classification
- **Solo Mode**: Single model for predictable workflows
- **Cost Tracking**: Real-time cost monitoring with daily budgets and logging
- **Slash Commands**: `/dev-aid-router-challenger`, `/dev-aid-router-ensemble`, `/dev-aid-router-status`
- **Full API Integration**: Anthropic, Google, OpenAI clients with unified interface
- **Virtual Environment Support**: Complete dependency isolation with automated setup

#### Local Semantic Search (NEW!)
- **claude-context-local Integration**: 100% local RAG with $0 cost
- **EmbeddingGemma Model**: Google's embedding model for semantic search
- **MCP Native**: Works with Claude Code and Gemini CLI out of the box
- **Auto-indexing**: Git hooks for automatic codebase reindexing
- **Setup Scripts**: One-command installation (`.dev-aid/scripts/setup-rag.sh`)
- **Status Monitoring**: Check RAG health with `rag-status.sh`

#### Documentation
- **DEPENDENCY-ISOLATION.md**: Complete three-layer isolation architecture guide
- **STORAGE-LOCATIONS.md**: Where files are stored and why (5MB vs 2.7GB breakdown)
- **ROUTER-INSTALL.md**: Step-by-step router installation with isolation benefits
- **ROUTER-IMPLEMENTATION-PLAN.md**: Full implementation roadmap
- **VENV-INFO.md**: Virtual environment deep-dive (venv vs Anaconda)
- **Enhanced README**: Native integration positioning, benefits comparison tables

#### Infrastructure
- **VERSION File**: Semantic versioning for update tracking
- **CHANGELOG.md**: Release notes and version history
- **Update Mechanism**: `update-dev-aid.sh` script for safe upgrades
- **Enhanced .gitignore**: Runtime files, costs, logs properly excluded

### Changed
- **Product Positioning**: From "NOT a standalone CLI" to "works natively inside tools you use"
- **Router Implementation**: Bash scripts → Full Python package with API integration
- **Dependency Management**: Manual pip install → Automated venv setup with `setup-venv.sh`

### Security
- **Isolated Dependencies**: Router venv + RAG uv environment + system Python (zero pollution)
- **API Key Protection**: `.env` files properly ignored in Git
- **No System Pollution**: All packages in isolated environments

---

## Release Notes

### v1.0.0 - Initial Production Release

This is the first production-ready release of Dev-AID with complete multi-AI orchestration and local semantic search capabilities.

**Highlights**:
- ✅ 65 expert skills across 10+ domains
- ✅ Multi-AI routing with cost optimization
- ✅ 100% local RAG ($0 forever, private)
- ✅ Complete dependency isolation
- ✅ Automated security scanning (5 tools)
- ✅ Works with Claude Code, Cursor, Gemini CLI

**Breaking Changes**: None (first release)

**Migration Guide**: N/A (first release)

---

## Version History

- **1.0.0** (2025-12-04) - Initial production release

---

## Upcoming Features (Planned)

### v1.1.0 (Q1 2025)
- [ ] Web dashboard for cost analytics
- [ ] Model performance benchmarking
- [ ] Custom routing rules via UI
- [ ] Multi-repository RAG support

### v1.2.0 (Q2 2025)
- [ ] LightRAG integration option
- [ ] LlamaIndex adapter
- [ ] Cloud RAG fallback
- [ ] Team cost allocation

---

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for how to propose changes.

---

## Support

- **Documentation**: `.dev-aid/docs/`
- **Issues**: [GitHub Issues](https://github.com/your-org/dev-aid/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/dev-aid/discussions)
