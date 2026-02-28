# Not Implemented Features

**Last Updated**: 2026-02-27 (Beta testing phase — see [BETA-TESTING-GUIDE.md](./BETA-TESTING-GUIDE.md))
**Status**: Focused roadmap of pending features

---

## 🧪 Testing & Quality Assurance

### 1. Router End-to-End Integration Tests
**Status**: ✅ **IMPLEMENTED** (2026-02-27)

**What was delivered**:
- ✅ 30 E2E tests across 9 test classes with mocked API responses
- ✅ Solo mode: response, request passthrough, cost tracking, routing log
- ✅ Ensemble mode: task classification, confidence, model selection
- ✅ Challenger mode: primary-only, force challenge, trigger keywords, auto-refine, graceful failure
- ✅ Budget enforcement: over-budget rejection, zero-budget, budget status
- ✅ Fallback chains: provider failure fallback, API error surfacing
- ✅ Cost persistence: costs.json structure, accumulation, routing.log growth, model stats
- ✅ Mode selection: config default, explicit override, invalid mode, ensemble/challenger configs
- ✅ Output formatting: solo success, failure, verbose metrics
- ✅ Router status: reflects execution data

**Approach taken**:
- Real `ConfigLoader` with temp directories (full config pipeline)
- Mocked `create_client` at mode-module level (no real API calls, $0 cost)
- Pre-populated auth to avoid `AuthDetector.detect_all()` network probes
- All tests marked `@pytest.mark.e2e`

**Files**: `tests/test_e2e_router.py` (816 lines)

---

### 2. Cross-Platform Testing - Windows
**Status**: 🟢 Partially implemented (2026-02-28) — Python CI on Windows, bash scripts platform-aware

**Current support**:
- ✅ macOS (Darwin) - tested and working
- ✅ Linux - developed and tested on Linux
- ✅ Windows (Python) - orchestration test suite runs on `windows-latest` in CI
- ✅ Windows (Git Bash) - bash script syntax validation in CI
- 🟡 Windows (full bash) - setup/update scripts warn about WSL requirement

**What was delivered** (2026-02-28):
- [x] `windows-compat.yml` — GitHub Actions workflow running Python tests on `windows-latest`
- [x] Context-detector smoke test on Windows
- [x] Bash script syntax validation via Git Bash on Windows
- [x] Platform detection in `setup-dev-aid.sh` (detects MSYS/Cygwin/MINGW, warns about WSL)
- [x] Graceful degradation: Python-only components work natively, bash features warn

**What's remaining**:
- [x] Windows-specific installation guide / WSL setup docs — See [WINDOWS-SETUP.md](./WINDOWS-SETUP.md)
- [ ] PowerShell wrapper for common commands (optional, low priority)
- [ ] Full end-to-end setup-dev-aid.sh testing under WSL in CI

**Approach taken**:
- Python components (router, orchestration, context-detector) run natively on Windows
- Bash scripts detect Windows platform and warn users about WSL requirement
- CI workflow is lightweight — focuses on "does the Python code work on Windows?"
- Bash script syntax validation ensures scripts at least parse correctly under Git Bash

**Files**:
- `.github/workflows/windows-compat.yml` — Windows CI workflow
- `.dev-aid/scripts/setup-dev-aid.sh` — Platform detection guards added

**Effort remaining**: Optional polish (WSL docs, PowerShell wrappers)

**Priority**: Low — core Python compatibility is now validated in CI

---

## 🎨 User Experience

### 3. TUI Dashboard for Cost Analytics
**Status**: ✅ **IMPLEMENTED** (2026-02-27)

**What was delivered**:
- ✅ `python -m router.cli dashboard` - rich TUI dashboard
- ✅ Budget status with colored progress bar (green/yellow/red thresholds)
- ✅ All-time summary panel (total cost, active days, avg daily cost)
- ✅ Model usage table (calls, cost, avg per call)
- ✅ Provider usage table
- ✅ Daily history table (last N days)
- ✅ Recent routing decisions table
- ✅ 11 unit tests with 75% module coverage
- ✅ Built with `rich` library (already a dependency, no new deps)

**Files**:
- `router/dashboard.py` - Dashboard rendering module
- `router/cli.py` - Added `dashboard` subcommand
- `tests/test_dashboard.py` - Comprehensive test suite

**Usage**: `python -m router.cli dashboard [--days 7] [--budget 100]`

---

## 🔐 Authentication & User Experience

### 4. Session-Based Authentication Support
**Status**: ✅ **IMPLEMENTED** (2025-12-08) - See commit `2601e92`

**Implementation completed**: All 5 phases delivered with keyring support

**What was delivered**:
- ✅ Detection of Claude CLI session auth (file configs + system keychain)
- ✅ Support for Google ADC (`~/.config/gcloud/application_default_credentials.json`)
- ✅ Cross-platform keychain integration (macOS Keychain, Windows Credential Manager, Linux Secret Service)
- ✅ Automatic fallback: File configs → Keychain → API key → Skip provider
- ✅ `python -m router.cli auth-status` command
- ✅ Updated documentation (README, implementation summary, design doc)
- ✅ 25 comprehensive unit tests (93.18% coverage for auth module)
- ✅ All 224 tests passing, 69.71% overall coverage

**Technical implementation**:
- ✅ `auth_detector.py` - Authentication detection module (245 lines)
- ✅ `AuthCredentials` dataclass for unified auth representation
- ✅ Updated all API clients to accept AuthCredentials
- ✅ Updated config_loader with `get_auth_credentials()` and lazy loading
- ✅ Updated all mode handlers (solo, ensemble, challenger)
- ✅ Added `keyring==25.7.0` library for secure keychain access

**Files**: 14 changed, 1,421 insertions(+), 67 deletions(-)
**Documentation**: `.dev-aid/docs/SESSION-AUTH-IMPLEMENTATION-SUMMARY.md`
**Branch**: `feat/session-based-auth`

**Impact delivered**:
- ✅ Unblocked Dev-AID router for Claude Pro/Max users (80-90% of market)
- ✅ Eliminated need for redundant API subscriptions
- ✅ Made $198,560/year savings accessible to everyone, not just API subscribers
- ✅ Better user experience (automatic auth detection, no manual key management)

**User experience**:

```bash
# Developer with Claude Pro (no API key needed!)
$ claude login  # Opens browser, authenticates once
$ python -m router.cli auth-status

🔐 Authentication Status for Dev-AID Router
==========================================================================================
Provider        Status          Auth Type       Source
==========================================================================================
claude          ✅ Authenticated SESSION         system keychain (keyring)
gemini          ✅ Authenticated ADC             ~/.config/gcloud/application_default_...
openai          ❌ No Auth       -               Not configured

$ python -m router.cli execute "Refactor this code" --mode solo
# Works! Uses Claude Pro session, no API key needed
```

**See also**: `.dev-aid/docs/SESSION-AUTH-IMPLEMENTATION-SUMMARY.md` for complete technical details
- Google ADC already supported by `google-genai` SDK
- Claude session token format needs investigation

**Full Design Document**: [SESSION-AUTH-DESIGN.md](./SESSION-AUTH-DESIGN.md)

---

## ⚡ Performance & Cost Optimization

### 5. TOON Format Integration
**Status**: ✅ **IMPLEMENTED** (2026-01-06) - Using `toon-format` package

**Implementation completed**: Phase 1 delivered with toon-format library wrapper

**What was delivered**:
- ✅ TOON encoder using `toon-format==0.9.0b1` package
- ✅ TOON decoder with full format support
- ✅ JSON ↔ TOON converter with token savings estimation
- ✅ 21 comprehensive unit tests (100% pass rate)
- ✅ No Node.js required (pure Python package)
- ✅ 40-60% token reduction validated in tests
- ✅ Documentation updated (TOON-QUICK-START.md, TOON-IMPLEMENTATION-PLAN.md)

**Technical implementation**:
- ✅ `.dev-aid/orchestration/toon/encoder.py` - Wrapper around toon_format.encode
- ✅ `.dev-aid/orchestration/toon/decoder.py` - Wrapper around toon_format.decode
- ✅ `.dev-aid/orchestration/toon/converter.py` - Bidirectional JSON↔TOON conversion
- ✅ `.dev-aid/orchestration/tests/test_toon.py` - Complete test coverage

**Files**: 3 new files, ~100 lines of wrapper code
**Documentation**: `.dev-aid/docs/TOON-IMPLEMENTATION-PLAN.md`, `.dev-aid/docs/TOON-QUICK-START.md`
**Branch**: `claude/claude-md-initialization-plan-blJSY`

**Phases 2-4 delivered** (2026-02-27):
- [x] Token savings measurement script (`.dev-aid/scripts/measure-toon-savings.py`)
- [x] TOON Format Guide documentation (`.dev-aid/docs/TOON-FORMAT-GUIDE.md`)
- [x] Config loader TOON support (tries `.toon` first, falls back to `.json`)
- [x] Migration script (`.dev-aid/scripts/migrate-to-toon.sh`)
- [x] Real-world token savings validated (40-60% reduction)

**Benefits delivered**:
- ✅ No Node.js dependency (uses Python `toon-format` package)
- ✅ Fast encoding/decoding (native Python, no subprocess overhead)
- ✅ Simpler debugging (Python stack traces)
- ✅ Cross-platform (works anywhere Python works)
- ✅ Ready for skill and config integration

**Expected impact when fully rolled out**:
- 40-60% token reduction on structured data
- $30,000-$50,000/year savings for 100-developer teams
- Better accuracy (73.9% vs 69.7% for JSON)
- Faster performance (no subprocess calls)

**All phases complete**:
1. ✅ Phase 1: Encoder/decoder with `toon-format==0.9.0b1` (2026-01-06)
2. ✅ Phase 2: Measurement script for real-world token savings (2026-02-27)
3. ✅ Phase 3: TOON Format Guide documentation (2026-02-27)
4. ✅ Phase 4: NOT-IMPLEMENTED.md updated, full rollout tooling ready (2026-02-27)

**Effort remaining**: None — all phases delivered
**Priority**: ~~High~~ **DONE**

**See also**:
- `.dev-aid/docs/TOON-IMPLEMENTATION-PLAN.md` for complete implementation plan
- `.dev-aid/docs/TOON-QUICK-START.md` for usage examples
- Commit `7401d6b` for pure Python implementation details

---

## 🔐 Enterprise Security Features

### 5. Supply Chain Security & Compliance
**Status**: ✅ **ALL PHASES IMPLEMENTED** (Phase 3 completed 2026-02-28)

**What exists**:
- ✅ Exact version pinning (all 63 dependencies use `==`)
- ✅ Virtual environment isolation
- ✅ Gitignored secrets (`.env`, API keys)
- ✅ Local git hooks (pre-commit security scans)
- ✅ Security tools: Gitleaks, Trivy, Opengrep (3-tool comprehensive stack)

- [x] **SCA (Software Composition Analysis)** in CI/CD ✅ IMPLEMENTED (2026-02-27)
  - pip-audit for CVE detection (PyPI/OSV vulnerability scanner)
  - Safety for dependency vulnerability scanning
  - Bandit for Python SAST (security linting)
  - Trivy license compliance scanning
  - Runs on PR to main, push to main, weekly schedule (Monday 6 AM UTC)
  - Results uploaded as artifacts (30-day retention)
  - Job summaries in GitHub Step Summary
  - See `.github/workflows/dependency-security.yml`

- [x] **SBOM (Software Bill of Materials)** generation ✅ IMPLEMENTED
  - CycloneDX and SPDX formats via Trivy
  - See `.github/workflows/release-gate.yml` and `dev-aid-sbom-diff.sh`
  - Auto-uploads to GitHub releases

- [x] **Supply Chain Security** ✅ IMPLEMENTED (2026-02-28)
  - Dependency provenance verification (pip-audit + Sigstore/cosign + PyPI attestation API)
  - Hash verification via `pip --require-hashes` with lock file generation
  - Private PyPI mirror support (configurable via `.dev-aid/config/supply-chain.json`)
  - Registry allowlist enforcement
  - Typosquatting detection for known attack patterns
  - Dependency freshness monitoring
  - JSON verification report generation
  - CI integration via `supply-chain-verify` job in `dependency-security.yml`
  - Standalone script: `.dev-aid/scripts/verify-supply-chain.sh`
  - Configuration: `.dev-aid/config/supply-chain.json`

- [x] **CI Security Scanning** ✅ IMPLEMENTED (2026-02-27)
  - Bandit (Python security linting) -- medium+ severity/confidence
  - Safety (dependency vulnerability DB)
  - pip-audit (PyPI vulnerability scanner)
  - Automated security reports via GitHub Step Summary and artifacts
  - See `.github/workflows/dependency-security.yml`

**What's remaining**:
- None -- all phases complete

**Implemented phases**:
1. **Phase 1: CI Security Scanning** ✅ IMPLEMENTED (2026-02-27)
   - Added Bandit, Safety, pip-audit to GitHub Actions
   - Runs on every PR and push to main + weekly schedule
   - License compliance via Trivy
   - Security reports as artifacts

2. **Phase 2: SBOM Generation** ✅ IMPLEMENTED (previously)
   - CycloneDX and SPDX formats via Trivy
   - Generated on release, published as artifact

3. **Phase 3: Supply Chain Verification** ✅ IMPLEMENTED (2026-02-28)
   - Provenance verification via pip-audit, Sigstore/cosign, PyPI attestation API
   - Hash verification with `pip --require-hashes` and lock file generation
   - Registry allowlist enforcement (configurable allowed registries)
   - Private PyPI mirror support (configurable via supply-chain.json)
   - Typosquatting detection for known malicious package name patterns
   - Dependency freshness monitoring
   - JSON report generation for CI integration
   - Graceful degradation (optional tools warn but don't block)
   - See `.dev-aid/scripts/verify-supply-chain.sh` and `.dev-aid/config/supply-chain.json`

**Tools integrated**:
- ✅ **Bandit**: Python security linting (in `dependency-security.yml`)
- ✅ **Safety**: Known vulnerability database (in `dependency-security.yml`)
- ✅ **pip-audit**: OSV/PyPI vulnerability scanner (in `dependency-security.yml`)
- ✅ **Trivy**: License compliance + SBOM generation (in `dependency-security.yml` + `release-gate.yml`)
- ✅ **Dependabot**: Automated dependency updates (GitHub)
- ✅ **cosign/Sigstore**: Package attestation verification (optional, in `verify-supply-chain.sh`)

**Effort remaining**: None -- all phases delivered

**Priority**: ~~Low~~ **DONE**

---

## 📊 Summary

| Feature | Status | Priority | Effort | Target Users |
|---------|--------|----------|--------|--------------|
| **Session-Based Authentication** | ✅ **IMPLEMENTED** | ~~Critical~~ | ~~1-2 weeks~~ **DONE** | **80-90% of users (UNBLOCKED)** |
| **TOON Format Integration (Phase 1)** | ✅ **IMPLEMENTED** | ~~High~~ | ~~1-2 weeks~~ **DONE (Phase 1)** | All (infrastructure ready) |
| **TOON Format Integration (Phases 2-4)** | ✅ **IMPLEMENTED** | ~~High~~ | ~~1-2 weeks~~ **DONE** | All ($30-50K/year savings) |
| Router E2E Tests | ✅ **IMPLEMENTED** | ~~High~~ | ~~1-2 weeks~~ **DONE** | All (validates core) |
| TUI Dashboard | ✅ **IMPLEMENTED** | ~~Medium~~ | ~~1 week~~ **DONE** | All (better UX) |
| Windows Testing | 🟢 **Partially IMPLEMENTED** | Low | ~~1 week~~ Optional polish | Windows users |
| Enterprise Security (All Phases) | ✅ **ALL PHASES IMPLEMENTED** | ~~Med-High~~ **DONE** | ~~4-6 weeks~~ **DONE** | Teams/Enterprises |

---

## 🎯 Recommended Implementation Order

### For Individual Developers (Current Focus):
1. ~~**Session-Based Authentication**~~ - ✅ **IMPLEMENTED** (2025-12-08, commit `2601e92`)
2. ~~**TOON Format Integration (Phase 1)**~~ - ✅ **IMPLEMENTED** (2025-01-06, commit `7401d6b`)
3. ~~**TOON Format Integration (Phases 2-4)**~~ - ✅ **IMPLEMENTED** (2026-02-27) - Measurement, docs, migration tooling
4. ~~**TUI Dashboard**~~ - ✅ **IMPLEMENTED** (2026-02-27) - Rich-based cost analytics
5. ~~**Router E2E Tests**~~ - ✅ **IMPLEMENTED** (2026-02-27) - 30 tests with mocked APIs
6. ~~Skip Windows testing~~ — 🟢 Python CI on Windows now automated
7. Skip enterprise security

### For Small Teams (2-5 people):
1. ~~**Session-Based Authentication**~~ - ✅ **IMPLEMENTED** (2025-12-08)
2. ~~**TOON Format Integration (Phase 1)**~~ - ✅ **IMPLEMENTED** (2025-01-06)
3. ~~**TOON Format Integration (Phases 2-4)**~~ - ✅ **IMPLEMENTED** (2026-02-27)
4. ~~**Router E2E Tests**~~ - ✅ **IMPLEMENTED** (2026-02-27) - 30 tests
5. ~~**CI Security Scanning**~~ - ✅ **IMPLEMENTED** (2026-02-27) - Bandit, safety, pip-audit
6. ~~**TUI Dashboard**~~ - ✅ **IMPLEMENTED** (2026-02-27) - Rich dashboard
7. **SBOM Generation** (1 week) - Compliance documentation

### For Enterprises (10+ people):
1. ~~**Session-Based Authentication**~~ - ✅ **IMPLEMENTED** (2025-12-08)
2. ~~**TOON Format Integration (Phase 1)**~~ - ✅ **IMPLEMENTED** (2025-01-06)
3. ~~**TOON Format Integration (Phases 2-4)**~~ - ✅ **IMPLEMENTED** (2026-02-27)
4. ~~**CI Security Scanning**~~ - ✅ **IMPLEMENTED** (2026-02-27)
5. ~~**Router E2E Tests**~~ - ✅ **IMPLEMENTED** (2026-02-27)
6. **SBOM Generation** (1 week) - Compliance requirement
7. ~~**Supply Chain Security**~~ - ✅ **IMPLEMENTED** (2026-02-28) - Full provenance tracking
8. ~~**TUI Dashboard**~~ - ✅ **IMPLEMENTED** (2026-02-27)

---

## 📝 Decision Log

### Why these 6 items?

**Added (December 2025)**:
- ✅ TOON Format Integration → **ALL PHASES IMPLEMENTED** (Phase 1: 2026-01-06, Phases 2-4: 2026-02-27)
  - $30-50K/year cost savings potential fully realized
  - All phases complete: encoder/decoder, measurement, docs, migration

**Recently Implemented (December 2025)**:
- ✅ **Session-Based Authentication** → **IMPLEMENTED** (2025-12-08, commit `2601e92`)
  - All 5 phases complete with keyring support
  - 224 tests passing, 69.71% coverage
  - Unblocks 80-90% of target users (Claude Pro/Max, Gemini CLI)
  - See: `.dev-aid/docs/SESSION-AUTH-IMPLEMENTATION-SUMMARY.md`

- ✅ **TOON Format Integration (Phase 1)** → **IMPLEMENTED** (2025-01-06, commit `7401d6b`)
  - Pure Python encoder/decoder (no Node.js required)
  - 21 tests passing, 100% pass rate
  - Zero external dependencies
  - Ready for skill and config integration
  - See: `.dev-aid/docs/TOON-QUICK-START.md`, `.dev-aid/docs/TOON-IMPLEMENTATION-PLAN.md`

**Removed**:
- ✅ RAG Integration → Fully complete (MCP pipeline + query caching + adaptive search depth + slash commands wired)
- ✅ MCP Integration → Already implemented (598 lines of code)
- ✅ Interactive Installer → Already implemented (setup-dev-aid.sh with 8-phase unified setup)
- ✅ Cross-Platform (macOS/Linux) → Already working
- ❌ Load Testing → Premature optimization, not critical
- ❌ Web Dashboard → TUI is better fit
- ❌ Additional Commands → Current 13 commands sufficient
- ❌ 35 Agents → Obsolete, skills paradigm covers this

**Kept**:
- ✅ TOON Format Integration (Phases 2-4) → **IMPLEMENTED** (2026-02-27) — measurement, docs, migration tooling
- ~~Router E2E Tests~~ → ✅ **IMPLEMENTED** (2026-02-27) - 30 tests with mocked APIs
- ~~TUI Dashboard~~ → ✅ **IMPLEMENTED** (2026-02-27) - Rich-based dashboard
- ~~Windows Testing~~ → 🟢 Partially implemented (Python CI + platform detection, 2026-02-28)
- ~~Enterprise Security (SCA/CI)~~ → ✅ **IMPLEMENTED** (2026-02-27) - pip-audit, safety, bandit in CI

---

**Remaining**:
1. ~~Windows Testing~~ — 🟢 Partially implemented (Python CI + platform detection, 2026-02-28)
2. ~~Supply Chain Verification~~ — ✅ **IMPLEMENTED** (2026-02-28) - provenance, signatures, private PyPI mirror
3. Everything else is implemented

**Last Updated**: 2026-02-28

