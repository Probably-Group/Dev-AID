# Not Implemented Features - Analysis & Roadmap

**Date**: 2025-12-05
**Version**: 1.1.0
**Status**: Comprehensive analysis of incomplete features

---

## Executive Summary

This document catalogues features that are **documented but not yet implemented** in Dev-AID, explains **why they're not implemented**, and proposes **paths forward** where clarification is needed.

---

## ✅ Recently Completed (2025-12-05)

### 1. Active Skill Detection in Router
**Status**: ✅ IMPLEMENTED

**What was done**:
- Added `_detect_active_skills()` method to `context_builder.py`
- Integrates with `detect-context-enhanced.sh` and `select-skills.sh`
- Skills now included in AI system prompts

**Location**: `.dev-aid/orchestration/router/context_builder.py:176-234`

### 2. Automated Tests Structure
**Status**: ✅ IMPLEMENTED

**What was done**:
- Created 3 comprehensive test files:
  - `test_context_builder.py` - 15+ test cases
  - `test_task_classifier.py` - 15+ test cases
  - `test_cost_tracker.py` - 15+ test cases
- Added `run_tests.sh` test runner
- Updated test documentation

**Location**: `.dev-aid/orchestration/tests/`

---

## 🚫 Dropped Items

### 1. Interactive Installation Wizard
**Status**: ❌ DROPPED (per user request)

**Reason**: Manual JSON configuration is sufficient for technical users. Interactive wizard would add complexity without significant benefit.

**Alternative**: Keep current manual configuration with good documentation.

---

## 📦 External Dependencies (Cannot Implement Without Source Repos)

### 1. 35 Planned Agents
**Status**: 🔴 BLOCKED - Source repositories don't exist

**Issue**: COMPONENTS-MANIFEST.md references agents from external repos:
- `claude-code-tresor` (15 agents)
- `claude-code-infrastructure-showcase` (4 agents)
- `my-claude-code-setup` (4 agents)
- `claude-code-skill-factory` (4 agents)

**These repositories are not available in the current environment.**

**Options**:
1. **Create agents from scratch** - Would require defining complete specifications for all 35 agents
2. **Skip agents entirely** - Current system works with just skills and commands
3. **Wait for source repos** - If they become available, install using manifest instructions
4. **Hybrid approach** - Create only the most useful agents (5-10) based on common use cases

**Recommendation**: **Option 2 - Skip for now**. The system functions well without them. Claude Code's built-in Task tool provides similar functionality.

### 2. Additional 8 Commands
**Status**: 🔴 BLOCKED - Source repositories don't exist

**Missing commands** (from COMPONENTS-MANIFEST.md):
- Workflow commands: prompt-create, prompt-run, todo-add, todo-check, handoff-create
- Memory commands: update-memory-bank, cleanup-context
- Development commands: build-skill, build-agent, validate-output

**Options**:
1. **Create from scratch** - Define and implement each command
2. **Use existing workarounds** - Current system has sufficient commands
3. **Wait for source repos**

**Recommendation**: **Option 2 - Use existing**. Current 12 commands cover essential functionality.

---

## 🔮 Future Features (Need Architectural Decisions)

### 1. RAG Integration (Phase 5)
**Status**: 🟡 DOCUMENTED BUT NOT IMPLEMENTED

**What's missing**:
- `router/mcp_client.py` - MCP protocol client
- `router/mcp_registry.py` - MCP server discovery
- Integration with `claude-context-local`
- `/aid-router-challenger-rag` command functionality

**Why not implemented**:
- MCP protocol still evolving
- `claude-context-local` exists but isn't integrated
- Requires significant testing infrastructure
- Current context builder loads memory bank files (works well enough)

**Questions needing clarification**:
1. **Which RAG backend to prioritize?**
   - A. `claude-context-local` (100% local, free)
   - B. LightRAG (newer, better performance)
   - C. LlamaIndex (most mature)
   - D. Support multiple backends

2. **When should RAG trigger automatically?**
   - A. Always (every request)
   - B. Only for large codebase queries
   - C. User opt-in per request
   - D. Configurable threshold

3. **How to handle RAG failures?**
   - A. Fall back to memory bank only
   - B. Return error to user
   - C. Retry with different backend

**Proposed approach**:
- Start with `claude-context-local` (Option 1A) - already documented
- Trigger only for massive_context tasks (Option 2B) - cost-effective
- Fall back gracefully (Option 3A) - best UX

**Effort estimate**: 2-3 weeks (integration + testing)

### 2. MCP Integration Infrastructure
**Status**: 🟡 400+ lines of docs written, zero code

**What's missing**:
- MCP client implementation
- MCP registry auto-discovery
- CLI commands: `mcp discover`, `mcp enable`, `mcp list`
- Context injection from MCP servers

**Why not implemented**:
- Waiting for MCP ecosystem to stabilize
- Claude Code's MCP support is recent
- Risk of building on moving foundation

**Questions needing clarification**:
1. **Should we implement custom MCP client or use library?**
   - A. Custom implementation (full control)
   - B. Use `mcp` Python package (if exists)
   - C. Wait for official Anthropic MCP SDK

2. **Which MCP servers to prioritize?**
   - A. Database (postgres, mysql, sqlite)
   - B. GitHub (issues, PRs)
   - C. Code search (dev-aid local)
   - D. All of the above

3. **How to handle MCP timeouts?**
   - A. Hard timeout (5s, fail fast)
   - B. Configurable per-server timeout
   - C. Async with cancellation

**Proposed approach**:
- Wait for option 1C (official SDK) - safest bet
- Implement option 2C (code search) first - highest value
- Use option 3A (hard timeout) - simplest

**Effort estimate**: 3-4 weeks (after SDK available)

### 3. Web Dashboard for Cost Analytics
**Status**: 🔴 PLANNED FOR v1.2.0 (Q2 2025)

**What's planned**:
- Visual cost breakdown by model
- Performance benchmarking charts
- Custom routing rules UI
- Multi-repository RAG dashboard

**Why not implemented**:
- Current CLI interface works well
- Web UI adds significant complexity
- Limited user demand (assumption)

**Questions needing clarification**:
1. **Is a web dashboard actually needed?**
   - User feedback: Do technical users prefer CLI or web UI?
   - Use case: Is this for teams or individuals?

2. **Which framework to use?**
   - A. Next.js (React)
   - B. Svelte/SvelteKit
   - C. Simple Flask + HTML/CSS
   - D. TUI (terminal UI) with textual/rich

3. **Where should dashboard run?**
   - A. Local web server (localhost:3000)
   - B. Static HTML generated on demand
   - C. Terminal UI (no web server)

**Proposed approach**:
- **Option D (TUI)** - best fit for CLI-first tool
- Build with `rich` or `textual` library
- Reads same `costs.json` and `routing.log`
- Runs as: `python -m router.dashboard`

**Effort estimate**: 1 week (TUI), 3-4 weeks (web)

---

## 🧪 Testing Gaps (Need Resources)

### 1. API Integration Tests
**Status**: 🟡 ZERO COVERAGE

**What's missing**:
- Tests with real API keys
- End-to-end routing tests
- Error handling with API failures
- Rate limiting behavior

**Why not implemented**:
- Costs real API credits
- Requires test API keys
- Risk of key leakage in CI
- Slow test execution

**Questions needing clarification**:
1. **Where to get test API keys?**
   - A. Separate test accounts
   - B. Sandbox/test mode (if available)
   - C. Mock servers instead

2. **How to prevent cost runaway?**
   - A. Strict token limits per test
   - B. Mock most calls, test few critical paths
   - C. Run only on release, not every commit

3. **How to secure keys in CI?**
   - A. GitHub Secrets
   - B. Environment variables (manual run only)
   - C. Don't run in CI at all

**Proposed approach**:
- Use option 1B (sandbox if available) or 1A (separate accounts)
- Use option 2B (mock most, test critical)
- Use option 3A (GitHub Secrets) for CI

**Effort estimate**: 1-2 weeks

### 2. Cross-Platform Compatibility
**Status**: 🟡 TESTED ON LINUX ONLY

**What's missing**:
- Windows testing
- macOS testing
- Path separator handling
- Shell script compatibility

**Why not implemented**:
- Development on Linux only
- No access to Windows/macOS environments
- Bash scripts may not work on Windows

**Questions needing clarification**:
1. **Should we support Windows?**
   - User base: Is Windows support required?
   - If yes, use WSL or native PowerShell?

2. **How to test cross-platform?**
   - A. GitHub Actions matrix (ubuntu, macos, windows)
   - B. Docker containers
   - C. Manual testing

**Proposed approach**:
- Support macOS (similar to Linux)
- Support Windows via WSL (not native)
- Document Windows requirements clearly
- Use GitHub Actions for macOS testing

**Effort estimate**: 1 week

### 3. Load Testing
**Status**: 🔴 ZERO COVERAGE

**What's missing**:
- Performance under 100+ requests
- Memory usage patterns
- Concurrent request handling
- Rate limit handling

**Why not implemented**:
- Not critical for MVP
- Requires load testing infrastructure
- Costs API credits

**Recommended approach**:
- Use `locust` or `k6` for load testing
- Test locally with mock responses
- Measure: latency, memory, throughput
- Document performance characteristics

**Effort estimate**: 1 week

---

## 🔐 Security Enhancements (Enterprise Features)

### Supply Chain Security Features
**Status**: 🟡 TODOS in security.md

**Missing features**:
- Fine-grained permissions
- Security scanning in CI
- SCA (Software Composition Analysis) in CI/CD
- Supply chain security
- SIEM integration

**Why not implemented**:
- Enterprise-grade features
- Target users are individual developers, not enterprises
- Significant infrastructure investment required

**Questions needing clarification**:
1. **What is the target user profile?**
   - A. Individual developers (current focus)
   - B. Small teams (2-5 people)
   - C. Enterprises (10+ people)

2. **Which security features are highest priority?**
   - Rank: CI scanning, SIEM, fine-grained perms, SCA

**Proposed approach**:
- **For individuals**: Keep current security model
- **For small teams**: Add CI scanning (Bandit, safety)
- **For enterprises**: Provide integration guides, not implementations

**Effort estimate**: 2-3 weeks for CI scanning

---

## 📊 Summary Table

| Feature | Status | Blocking Issue | Recommendation | Effort |
|---------|--------|----------------|----------------|--------|
| ✅ Active Skill Detection | Done | - | - | Done |
| ✅ Automated Tests | Done | - | - | Done |
| ❌ 35 Agents | Blocked | No source repos | Skip for now | N/A |
| ❌ 8 Commands | Blocked | No source repos | Skip for now | N/A |
| 🟡 RAG Integration | Design needed | Architecture decisions | Start with claude-context-local | 2-3 weeks |
| 🟡 MCP Integration | Waiting | MCP SDK maturity | Wait for official SDK | 3-4 weeks |
| 🟡 Web Dashboard | User feedback needed | Unclear value | TUI instead of web | 1 week |
| 🟡 API Integration Tests | Resources needed | API keys, cost | Mock most, test critical paths | 1-2 weeks |
| 🟡 Cross-Platform | Testing needed | No macOS/Windows access | GitHub Actions for macOS | 1 week |
| 🔴 Load Testing | Low priority | Not critical | Use locust with mocks | 1 week |
| 🔐 Supply Chain Security | Target unclear | Enterprise vs individual | CI scanning only | 2-3 weeks |

---

## 🎯 Proposed Implementation Priorities

### High Priority (Next Sprint)
1. **RAG Integration** - High value, clear approach
   - Start with `claude-context-local`
   - Trigger for massive_context tasks only
   - Fall back gracefully

2. **API Integration Tests** - Critical for confidence
   - Set up test API keys
   - Mock most, test critical paths
   - Add to CI pipeline

### Medium Priority (Next Month)
3. **Cross-Platform Testing** - Expand user base
   - Set up GitHub Actions matrix
   - Test on macOS (similar to Linux)
   - Document Windows/WSL requirements

4. **TUI Dashboard** - Better UX than web
   - Build with `rich` or `textual`
   - Show costs, performance, routing decisions
   - Runs as `python -m router.dashboard`

### Low Priority (Backlog)
5. **MCP Integration** - Wait for SDK
   - Monitor MCP ecosystem
   - Implement once official SDK available

6. **Load Testing** - Performance validation
   - Use locust with mocks
   - Measure latency, memory, throughput

7. **CI Security Scanning** - If targeting teams
   - Add Bandit, safety, pip-audit
   - Run on every PR

### Not Recommended
- ❌ Web Dashboard (TUI is better fit)
- ❌ 35 Agents from missing repos (no source)
- ❌ Enterprise SIEM integration (wrong target)

---

## ❓ Questions for User/Stakeholders

### Critical Questions (Block RAG Implementation)
1. **RAG Backend**: Which to prioritize - claude-context-local, LightRAG, or LlamaIndex?
2. **RAG Trigger**: Always, only for large queries, or user opt-in?

### Important Questions (Affect Roadmap)
3. **Dashboard**: Is TUI acceptable, or must it be web-based?
4. **Target Users**: Individual developers, small teams, or enterprises?
5. **Windows Support**: Required, or WSL-only acceptable?

### Nice-to-Have Questions
6. **API Integration Tests**: Can we get test API keys/budgets?
7. **Cross-Platform**: Need native Windows support, or WSL okay?

---

## 📝 Next Steps

1. **Review this document** with stakeholders
2. **Get answers** to critical questions (1-2)
3. **Prioritize** based on user feedback
4. **Start with RAG integration** (highest value)
5. **Add API tests** (build confidence)
6. **Iterate** based on usage data

---

**Last Updated**: 2025-12-05
**Maintainer**: Dev-AID Team
**Status**: Living document - update as implementation progresses
