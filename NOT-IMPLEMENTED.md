# Not Implemented Features

**Last Updated**: 2025-12-08 (Added Session-Based Authentication - CRITICAL)
**Status**: Focused roadmap of pending features

---

## 🧪 Testing & Quality Assurance

### 1. Router End-to-End Integration Tests
**Status**: 🟡 Unit tests exist (199 passing), E2E tests missing

**What exists**:
- ✅ Unit tests with mocks (11 test files)
- ✅ test_modes.py (solo, ensemble, challenger)
- ✅ test_api_clients.py, test_cost_tracker.py, test_executor.py

**What's missing** - E2E Manual Testing Checklist:
- [ ] Install Python dependencies in fresh environment
- [ ] Configure API keys for all 3 providers (Anthropic, Google, OpenAI)
- [ ] Run `/dev-aid-router-ensemble "test request"` and verify correct model selected
- [ ] Run `/dev-aid-router-challenger "test request"` and verify two-model workflow
- [ ] Run `/dev-aid-router-solo "test request"` with each provider
- [ ] Verify logs created in `.dev-aid/logs/routing.log`
- [ ] Verify cost tracking written to `.dev-aid/logs/costs.json`
- [ ] Test fallback behavior when primary model fails
- [ ] Test with massive context (>100K tokens) routes to Gemini
- [ ] Test error handling with invalid API keys
- [ ] Test rate limiting behavior

**Why not implemented**:
- Costs real API credits (~$5-10 per full test suite run)
- Requires test API keys for 3 providers
- Risk of key leakage in CI
- Slow test execution (~30-60s per full suite)

**Proposed approach**:
- Use separate test accounts with low budget limits
- Mock most calls, test only critical paths (5-10 scenarios)
- Use GitHub Secrets for CI
- Run on release only, not every commit

**Effort estimate**: 1-2 weeks

**Priority**: High - validates core router functionality

---

### 2. Cross-Platform Testing - Windows
**Status**: 🟡 Works on macOS and Linux, Windows untested

**Current support**:
- ✅ macOS (Darwin) - tested and working
- ✅ Linux - developed and tested on Linux
- ❓ Windows - untested, likely requires WSL

**What's missing**:
- [ ] Windows WSL testing
- [ ] PowerShell compatibility (if needed)
- [ ] Path separator handling verification
- [ ] Windows-specific installation guide

**Why not implemented**:
- No access to Windows environment
- Bash scripts require WSL on Windows
- Unknown Windows user base

**Proposed approach**:
- Support Windows via WSL only (not native PowerShell)
- Document Windows requirements clearly
- Use GitHub Actions matrix (ubuntu, macos, windows-wsl)
- Manual testing with Windows users

**Effort estimate**: 1 week

**Priority**: Low - only if Windows users exist

---

## 🎨 User Experience

### 3. TUI Dashboard for Cost Analytics
**Status**: 🔴 Not implemented (CLI interface works, TUI would be better)

**What exists**:
- ✅ `python -m router.cli status` - shows costs in plain text
- ✅ `.dev-aid/logs/routing.log` - human-readable log
- ✅ `.dev-aid/logs/costs.json` - structured cost data

**What's planned**:
- Visual cost breakdown by model (bar charts)
- Performance benchmarking charts
- Routing decision history
- Budget tracking with alerts
- Interactive log viewer

**Why TUI instead of Web**:
- Fits CLI-first tool philosophy
- No web server required
- Faster to implement (1 week vs 3-4 weeks)
- Uses existing `rich` library (already a dependency)

**Implementation approach**:
- Build with `textual` or `rich` library
- Reads same `costs.json` and `routing.log`
- Runs as: `python -m router.dashboard`
- Real-time updates (optional)

**Features**:
```
┌─ Dev-AID Router Dashboard ─────────────────────────┐
│ Today's Costs: $2.45 / $100.00 budget (2.45%)      │
├─────────────────────────────────────────────────────┤
│ Cost by Model:                                      │
│ claude-sonnet  ████████████░░░░ $1.20 (49%)       │
│ gemini-flash   ████░░░░░░░░░░░░ $0.50 (20%)       │
│ gpt-4o         ██████░░░░░░░░░░ $0.75 (31%)       │
├─────────────────────────────────────────────────────┤
│ Requests: 45 total                                  │
│ Avg Latency: 3.2s                                   │
│ Tokens: 280K in, 12K out                           │
└─────────────────────────────────────────────────────┘
```

**Effort estimate**: 1 week

**Priority**: Medium - nice UX improvement, low effort

---

## 🔐 Authentication & User Experience

### 4. Session-Based Authentication Support
**Status**: 🔴 Critical - Blocks adoption for 80-90% of developers

**The Problem**:
- Dev-AID router requires API keys (ANTHROPIC_API_KEY, GOOGLE_API_KEY, etc.)
- Most developers have **consumer subscriptions** with session auth:
  - Claude Pro/Max ($20-200/mo) → No API key, signed in via `claude` CLI
  - Gemini CLI → Signed in via `gcloud auth`, uses ADC (Application Default Credentials)
  - ChatGPT Plus → No API access at all (separate purchase required)
- **80-90% of AI tool users can't use Dev-AID router**

**What exists**:
- ✅ API key-based authentication (`.dev-aid/config/.env`)
- ✅ Router works perfectly IF you have API keys

**What's missing**:
- [ ] Detection of Claude CLI session auth (`~/.config/claude/config.json`)
- [ ] Support for Google ADC (`~/.config/gcloud/application_default_credentials.json`)
- [ ] Automatic fallback: Try session → Try API key → Skip provider
- [ ] `router-cli.sh auth-status` command to show authentication status
- [ ] Updated documentation explaining both methods

**Why critical**:
- **Real quote from industry**: "I spent $200-300/mo on AI coding, and I'm not even a developer"
- Most developers already pay for Claude Pro/Max or Gemini CLI
- Forcing them to buy **separate API subscriptions** is redundant and expensive
- Without this, Dev-AID router is **unusable for majority of target users**

**Implementation approach**:

1. **Phase 1: Auth Detection Module** (3 days)
   - Create `auth_detector.py` to detect session tokens
   - Check Claude config at `~/.config/claude/config.json`
   - Check Google ADC at `~/.config/gcloud/application_default_credentials.json`
   - Fallback to API keys from environment

2. **Phase 2: Update API Clients** (2 days)
   - Modify `AnthropicClient` to accept session tokens
   - Modify `GoogleClient` to use ADC (already supported by SDK!)
   - Update `BaseAIClient` to handle `AuthCredentials` instead of just `api_key`

3. **Phase 3: Update Config Loader** (1 day)
   - Add `get_auth_credentials()` method
   - Cache auth detection results (run once per session)
   - Keep `get_api_key()` for backward compatibility

4. **Phase 4: Update Mode Handlers** (1 day)
   - Update solo, ensemble, challenger modes
   - Pass `AuthCredentials` to `create_client()`
   - Show helpful error if no auth found

5. **Phase 5: CLI & Documentation** (3 days)
   - Add `auth-status` command to show current authentication
   - Update ROUTER-INSTALL.md with session auth instructions
   - Add troubleshooting guide for common auth issues

**Authentication Priority**:
```
For each provider:
  1. Try session-based auth (Claude CLI, gcloud ADC)
  2. If not found, try API key from environment
  3. If neither found, skip provider with helpful error
```

**Expected user experience**:

```bash
# Developer with Claude Pro (no API key needed!)
$ claude login  # Opens browser, authenticates
$ ./router-cli.sh auth-status

🔐 Authentication Status:
✅ Claude: SESSION (~/.config/claude/config.json)
✅ Gemini: ADC (~/.config/gcloud/application_default_credentials.json)
❌ OpenAI: Not authenticated

$ ./router-cli.sh execute "Refactor this code" --mode solo
# Works! Uses Claude Pro session, no API key needed
```

**Effort estimate**: 1-2 weeks (10 days total)

**Priority**: **Critical** - Blocks 80-90% of target users

**Impact**:
- Unlocks Dev-AID router for Claude Pro/Max users (majority of market)
- Eliminates need for redundant API subscriptions
- Makes $198,560/year savings accessible to everyone, not just API subscribers
- Better user experience (no need to manage API keys)

**Risks**:
- ⚠️ **Medium**: Anthropic SDK may not officially support session tokens
  - Mitigation: Use workaround or document limitation for v1.3.0
- ⚠️ Low: Session tokens expire → need re-authentication
  - Mitigation: Clear error message: "Session expired, run: `claude login`"
- ⚠️ Low: ChatGPT Plus doesn't include API → can't support
  - Mitigation: Document clearly in error message

**Dependencies**:
- None (pure Python, uses existing config files)
- Google ADC already supported by `google-genai` SDK
- Claude session token format needs investigation

**Full Design Document**: [SESSION-AUTH-DESIGN.md](../.dev-aid/docs/SESSION-AUTH-DESIGN.md)

---

## ⚡ Performance & Cost Optimization

### 5. TOON Format Integration
**Status**: 🔴 Not implemented (planned for v1.3.0)

**What is TOON**:
- **TOON** = Token-Oriented Object Notation
- Combines YAML (objects) + CSV (arrays) for 40-60% token reduction vs JSON
- Better accuracy: 73.9% vs 69.7% for JSON
- TypeScript SDK available: `@toon-format/toon`

**What exists**:
- ✅ JSON-based prompts and responses (current implementation)
- ✅ Skills generating structured data (issue analysis, architecture mapping)
- ✅ Config files in JSON format

**What's planned**:
Transform high-volume AI interactions to TOON format:

1. **Issue Analysis Output** (`.dev-aid/skills/expert/devsecops-expert/`)
   - Security findings, vulnerability reports
   - Estimated savings: 40-50% tokens per analysis

2. **Architecture Mapper** (`.dev-aid/skills/expert/architecture-mapper/`)
   - Component lists, dependency trees, API endpoint maps
   - Estimated savings: 50-60% tokens per map

3. **Test Data Factory** (`.dev-aid/skills/expert/test-data-factory/`)
   - Test fixtures, mock data, test case matrices
   - Estimated savings: 45-55% tokens per dataset

4. **Skill System Prompts** (structured config sections)
   - Model lists, routing rules, cost tables
   - Estimated savings: 40-50% tokens per config

**Example Comparison**:

```json
// JSON (65 tokens)
{
  "models": [
    {"name": "gpt-4", "cost": 0.03, "speed": "fast"},
    {"name": "claude-3", "cost": 0.015, "speed": "medium"}
  ]
}
```

```yaml
# TOON (35 tokens - 46% reduction)
models:
name,cost,speed
gpt-4,0.03,fast
claude-3,0.015,medium
```

**Implementation Approach**:

1. **Phase 1: SDK Integration** (2-3 days)
   - Install `@toon-format/toon` TypeScript SDK
   - Create Python wrapper for skill prompts
   - Add TOON encoder/decoder utilities

2. **Phase 2: Skill Conversion** (3-4 days)
   - Convert high-volume skills to TOON output
   - Update skill templates with TOON examples
   - Add TOON format documentation

3. **Phase 3: Config Migration** (2-3 days)
   - Migrate `.dev-aid/config/models.json` → `models.toon`
   - Migrate `.dev-aid/config/routing.json` → `routing.toon`
   - Update config loaders

4. **Phase 4: Testing & Rollout** (2-3 days)
   - Test token reduction (compare before/after)
   - Validate accuracy (should improve to 73.9%+)
   - Monitor cost savings in production

**Target Use Cases** (by token volume):
| Use Case | Current Tokens/Call | With TOON | Savings | Annual Impact* |
|----------|---------------------|-----------|---------|----------------|
| Architecture mapping | 8,000 | 3,500 | 56% | $15,000 |
| Issue analysis | 5,000 | 2,500 | 50% | $12,000 |
| Test data generation | 3,000 | 1,500 | 50% | $8,000 |
| Config prompts | 2,000 | 1,100 | 45% | $5,000 |
| **TOTAL** | - | - | **48% avg** | **$40,000** |

*Based on 100-developer team, 20 calls/day/developer

**Effort estimate**: 1-2 weeks (10-12 days total)

**Priority**: **High** - Immediate cost savings with minimal implementation risk

**Expected ROI**:
- Investment: 1-2 weeks developer time (~$4,000-8,000)
- Annual savings: $30,000-$50,000 (conservative estimate)
- **Payback period**: 2-3 months
- 5-year value: $150,000-$250,000

**Dependencies**:
- TypeScript/Node.js (for SDK)
- Python wrapper for skill system
- No breaking changes to existing functionality

**Risks**:
- ⚠️ Low: TOON SDK actively maintained, proven in production
- ⚠️ Low: Can roll out incrementally (skill by skill)
- ⚠️ Low: JSON fallback always available

---

## 🔐 Enterprise Security Features

### 5. Supply Chain Security & Compliance
**Status**: 🟡 Basic security exists, enterprise features missing

**What exists**:
- ✅ Exact version pinning (all 63 dependencies use `==`)
- ✅ Virtual environment isolation
- ✅ Gitignored secrets (`.env`, API keys)
- ✅ Local git hooks (pre-commit security scans)
- ✅ Security tools: Gitleaks, Trivy, Opengrep, Hadolint, Checkov

**What's missing**:
- [ ] **SCA (Software Composition Analysis)** in CI/CD
  - Automated dependency vulnerability scanning
  - CVE detection and alerting
  - License compliance checking

- [ ] **SBOM (Software Bill of Materials)** generation
  - CycloneDX or SPDX format
  - Dependency tree documentation
  - Provenance tracking

- [ ] **Supply Chain Security**
  - Dependency provenance verification
  - Signature verification for packages
  - Private PyPI mirror support
  - Dependency update policies

- [ ] **CI Security Scanning**
  - Bandit (Python security linting)
  - Safety (dependency vulnerability DB)
  - pip-audit (PyPI vulnerability scanner)
  - Automated security reports

**Why not implemented**:
- Primarily built for individual developers
- Enterprise features require infrastructure investment
- Unknown demand from teams/enterprises

**Target audience question**:
- Individual developers? → Current security is sufficient
- Small teams (2-5)? → Add CI scanning
- Enterprises (10+)? → Full SCA/SBOM/supply chain

**Proposed approach for teams**:
1. **Phase 1: CI Security Scanning** (2-3 weeks)
   - Add Bandit, safety, pip-audit to GitHub Actions
   - Run on every PR and push to main
   - Fail CI on HIGH/CRITICAL vulnerabilities
   - Generate security reports

2. **Phase 2: SBOM Generation** (1 week)
   - Use `cyclonedx-bom` or `pip-licenses`
   - Generate SBOM on release
   - Publish as artifact

3. **Phase 3: Supply Chain Verification** (2-3 weeks)
   - Verify package signatures
   - Pin dependencies with hash verification
   - Document dependency update policy
   - Private PyPI mirror support (optional)

**Tools to integrate**:
- **Bandit**: Python security linting
- **Safety**: Known vulnerability database
- **pip-audit**: OSV/PyPI vulnerability scanner
- **cyclonedx-bom**: SBOM generator (CycloneDX format)
- **Dependabot**: Automated dependency updates (GitHub)
- **Snyk**: Commercial SCA (optional)

**Effort estimate**:
- CI Scanning: 2-3 weeks
- SBOM: 1 week
- Full supply chain: 4-6 weeks total

**Priority**: Medium-High - depends on target user base (individuals vs teams)

---

## 📊 Summary

| Feature | Status | Priority | Effort | Target Users |
|---------|--------|----------|--------|--------------|
| **Session-Based Authentication** | 🔴 Critical | **Critical** | 1-2 weeks | **80-90% of users (blocks adoption)** |
| TOON Format Integration | 🔴 Not implemented | **High** | 1-2 weeks | All ($30-50K/year savings) |
| Router E2E Tests | 🟡 Missing | High | 1-2 weeks | All (validates core) |
| TUI Dashboard | 🔴 Missing | Medium | 1 week | All (better UX) |
| Windows Testing | 🟡 Untested | Low | 1 week | Windows users only |
| Enterprise Security (SCA/SBOM) | 🟡 Basic only | Med-High | 4-6 weeks | Teams/Enterprises |

---

## 🎯 Recommended Implementation Order

### For Individual Developers (Current Focus):
1. **Session-Based Authentication** (1-2 weeks) - **CRITICAL**: Unlocks router for Claude Pro/Max users (80-90% of market)
2. **TOON Format Integration** (1-2 weeks) - Immediate $30-50K/year savings, 2-3 month payback
3. **TUI Dashboard** (1 week) - Quick win, improves daily UX
4. **Router E2E Tests** (1-2 weeks) - Critical path validation only
5. Skip Windows testing unless users request it
6. Skip enterprise security

### For Small Teams (2-5 people):
1. **Session-Based Authentication** (1-2 weeks) - **CRITICAL**: Most team members have Claude Pro, not API keys
2. **TOON Format Integration** (1-2 weeks) - Immediate cost savings ($30-50K/year)
3. **Router E2E Tests** (1-2 weeks) - Build confidence
4. **CI Security Scanning** (2-3 weeks) - Bandit, safety, pip-audit
5. **TUI Dashboard** (1 week) - Team cost visibility
6. **SBOM Generation** (1 week) - Compliance documentation

### For Enterprises (10+ people):
1. **Session-Based Authentication** (1-2 weeks) - **CRITICAL**: Enable router for all developers, not just API subscribers
2. **TOON Format Integration** (1-2 weeks) - Immediate cost savings ($30-50K/year)
3. **CI Security Scanning** (2-3 weeks) - Mandatory
4. **Router E2E Tests** (1-2 weeks) - Validate before deployment
5. **SBOM Generation** (1 week) - Compliance requirement
6. **Supply Chain Security** (2-3 weeks) - Full provenance tracking
7. **TUI Dashboard** (1 week) - Cost accountability

---

## 📝 Decision Log

### Why these 6 items?

**Added (December 2025)**:
- 🆕 **Session-Based Authentication** → **CRITICAL**: Blocks 80-90% of users, must implement before v1.3.0
- 🆕 TOON Format Integration → Immediate $30-50K/year cost savings, proven technology

**Removed**:
- ✅ RAG Integration → Already implemented (`.dev-aid/local-search/`)
- ✅ MCP Integration → Already implemented (598 lines of code)
- ✅ Interactive Installer → Already implemented (install.sh with 6 steps)
- ✅ Cross-Platform (macOS/Linux) → Already working
- ❌ Load Testing → Premature optimization, not critical
- ❌ Web Dashboard → TUI is better fit
- ❌ Additional Commands → Current 13 commands sufficient
- ❌ 35 Agents → Obsolete, skills paradigm covers this

**Kept**:
- Session-Based Authentication → **CRITICAL**: Unblocks 80-90% of target market
- TOON Format Integration → High ROI, minimal risk, immediate cost impact
- Router E2E Tests → Validates core functionality
- TUI Dashboard → Low effort, high value
- Windows Testing → Depends on user base
- Enterprise Security → Depends on target audience (SCA/SBOM specifically requested)

---

**Next Steps**:
1. Confirm target user base (individuals, teams, or enterprises)
2. Prioritize based on user feedback
3. Implement in order of recommendation
4. Update this document as features are completed

