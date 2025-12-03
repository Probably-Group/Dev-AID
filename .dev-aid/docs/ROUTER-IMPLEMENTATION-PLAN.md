# Router Implementation Plan

**Status:** In Development
**Started:** 2025-12-03
**Target Completion:** Phase 1-3 (Core Functionality)
**Architecture:** Python-based (better than bash for API calls)

---

## 🎯 Overview

Implement the missing execution layer for Dev-AID's multi-AI router to enable actual model switching, multi-model orchestration, and cost tracking.

**Current State:** Router has decision logic but only prints recommendations
**Target State:** Router actually executes with different AI providers

---

## 📋 Implementation Phases

### Phase 1: Foundation (Priority: CRITICAL) ⚡

**Goal:** Enable basic API calls to different providers

**Components:**
1. ✅ Python environment setup
2. ✅ API client for Anthropic (Claude)
3. ✅ API client for Google (Gemini)
4. ✅ API client for OpenAI (GPT)
5. ✅ Configuration loader
6. ✅ Basic executor

**Deliverable:** Can execute a request with any configured model

**Files:**
```
.dev-aid/orchestration/router/
├── __init__.py
├── api_clients.py      # API wrappers for all providers
├── config_loader.py    # Load Dev-AID configs
└── executor.py         # Basic execution engine
```

**Estimated Time:** 2-3 days
**Lines of Code:** ~400

---

### Phase 2: Ensemble Mode (Priority: HIGH) 🎯

**Goal:** Automatic task classification and routing

**Components:**
1. ✅ Task classifier (keyword-based)
2. ✅ Routing logic (map task type → model)
3. ✅ Context builder (memory bank, skills)
4. ✅ Ensemble mode implementation
5. ✅ Cost calculation

**Deliverable:** `/aid-router-ensemble` works end-to-end

**Files:**
```
.dev-aid/orchestration/router/
├── task_classifier.py   # Classify task type
├── context_builder.py   # Gather Dev-AID context
├── cost_tracker.py      # Calculate & track costs
└── modes/
    └── ensemble.py      # Ensemble mode logic
```

**Estimated Time:** 2-3 days
**Lines of Code:** ~350

---

### Phase 3: Challenger Mode (Priority: HIGH) ⚔️

**Goal:** Multi-model review workflow

**Components:**
1. ✅ Primary generation step
2. ✅ Context handoff mechanism
3. ✅ Challenger review step
4. ✅ Refinement step (optional)
5. ✅ Response formatting

**Deliverable:** `/aid-router-challenger` works end-to-end

**Files:**
```
.dev-aid/orchestration/router/
├── handoff.py           # Multi-model context passing
└── modes/
    ├── solo.py          # Solo mode
    └── challenger.py    # Challenger mode logic
```

**Estimated Time:** 3-4 days
**Lines of Code:** ~400

---

### Phase 4: Monitoring & CLI (Priority: MEDIUM) 📊

**Goal:** Visibility into routing decisions and costs

**Components:**
1. ✅ Structured logging
2. ✅ Cost tracking database (JSON)
3. ✅ Status reporter
4. ✅ CLI interface
5. ✅ Integration with slash commands

**Deliverable:**
- `/aid-router-status` shows real data
- All costs logged
- CLI tool for manual invocation

**Files:**
```
.dev-aid/orchestration/router/
├── logger.py            # Structured logging
├── analytics.py         # Cost analytics & reporting
└── cli.py               # CLI interface

.dev-aid/logs/
├── routing.log          # Routing decisions
└── costs.json           # Cost tracking
```

**Estimated Time:** 2-3 days
**Lines of Code:** ~350

---

### Phase 5: RAG Integration (Priority: LOW) 🔍

**Goal:** Use local semantic search before routing

**Components:**
1. ✅ RAG query integration
2. ✅ Context injection
3. ✅ `/aid-router-challenger-rag` command

**Deliverable:** RAG-enhanced routing works

**Estimated Time:** 1-2 days
**Lines of Code:** ~150

---

## 🏗️ Architecture

### Python Package Structure

```
.dev-aid/orchestration/router/
├── __init__.py                 # Package initialization
├── api_clients.py              # API wrappers
│   ├── AnthropicClient
│   ├── GoogleClient
│   └── OpenAIClient
├── config_loader.py            # Load Dev-AID configs
├── context_builder.py          # Build AI context
├── task_classifier.py          # Classify task type
├── cost_tracker.py             # Cost calculation
├── logger.py                   # Structured logging
├── analytics.py                # Cost analytics
├── handoff.py                  # Multi-model coordination
├── executor.py                 # Main execution engine
├── cli.py                      # CLI interface
└── modes/
    ├── __init__.py
    ├── solo.py                 # Solo mode
    ├── ensemble.py             # Ensemble mode
    └── challenger.py           # Challenger mode
```

### Integration Points

```
Slash Command (.md file)
        ↓
    Bash Wrapper (.dev-aid/orchestration/router.sh)
        ↓
    Python CLI (python -m router.cli)
        ↓
    Executor (router/executor.py)
        ↓
    API Clients (router/api_clients.py)
        ↓
    AI Provider APIs
        ↓
    Formatted Response
```

---

## 🔧 Technical Decisions

### 1. Language: Python (not Bash)

**Why:**
- Better HTTP/API handling (`requests` library)
- JSON parsing is native
- Async support for parallel calls
- Rich ecosystem for AI APIs
- Easier error handling
- Type hints for maintainability

**Trade-off:** Adds Python dependency, but already needed for RAG

### 2. API Libraries

- **Anthropic:** Official `anthropic` SDK
- **Google:** Official `google-generativeai` SDK
- **OpenAI:** Official `openai` SDK

### 3. Configuration

Use existing JSON configs:
- `.dev-aid/config/settings.json`
- `.dev-aid/config/routing.json`
- `.dev-aid/config/models.json`
- `.dev-aid/config/.env` (API keys)

### 4. Logging

- **Format:** JSON lines for structured logging
- **Location:** `.dev-aid/logs/routing.log`
- **Cost Data:** `.dev-aid/logs/costs.json`

### 5. Error Handling

- Fallback chain if primary model fails
- Graceful degradation (fall back to Claude)
- Log all errors
- User-friendly error messages

---

## 📦 Dependencies

### Python Packages (add to requirements.txt)

```txt
anthropic>=0.18.0       # Anthropic API
google-generativeai>=0.3.0  # Google Gemini API
openai>=1.0.0           # OpenAI API
python-dotenv>=1.0.0    # Load .env files
requests>=2.31.0        # HTTP requests
pydantic>=2.0.0         # Data validation
rich>=13.0.0            # Pretty CLI output (optional)
```

### System Requirements

- Python 3.9+
- pip
- Valid API keys for enabled providers

---

## 🧪 Testing Strategy

### Unit Tests

```python
tests/
├── test_api_clients.py     # Mock API calls
├── test_classifier.py      # Task classification
├── test_executor.py        # Execution logic
├── test_cost_tracker.py    # Cost calculations
└── test_modes.py           # Each mode
```

### Integration Tests

1. **Solo Mode:** Single request with Claude
2. **Ensemble Mode:** Task routes to correct model
3. **Challenger Mode:** Two-model workflow
4. **Cost Tracking:** Logs written correctly
5. **Fallback:** Handles API failures

### Manual Testing Checklist

- [ ] Install Python dependencies
- [ ] Configure API keys
- [ ] Run `/aid-router-ensemble "test request"`
- [ ] Verify correct model selected
- [ ] Check logs created
- [ ] Verify cost calculated
- [ ] Test with each provider
- [ ] Test fallback on failure

---

## 🚀 Rollout Plan

### Stage 1: Development (Current)

- Implement Phase 1-3
- Internal testing
- Documentation

### Stage 2: Beta Testing

- Enable for solo mode first (safest)
- Test with real workloads
- Gather feedback
- Fix bugs

### Stage 3: Ensemble Release

- Enable ensemble mode
- Monitor costs
- Optimize routing logic
- Performance tuning

### Stage 4: Challenger Release

- Enable challenger mode
- Test multi-model workflows
- Refine handoff mechanism

### Stage 5: Polish

- RAG integration
- Advanced analytics
- UI improvements
- Documentation refinement

---

## 📊 Success Metrics

### Functional Metrics

- [ ] Can call Anthropic API
- [ ] Can call Google API
- [ ] Can call OpenAI API
- [ ] Task classification accuracy > 80%
- [ ] Ensemble mode routes correctly
- [ ] Challenger mode completes workflow
- [ ] All costs logged

### Performance Metrics

- [ ] Routing decision < 50ms
- [ ] API call latency < 5s (typical)
- [ ] No API failures due to router bugs
- [ ] Cost tracking accurate (< 1% error)

### User Experience Metrics

- [ ] Clear routing explanations
- [ ] Cost comparison shown
- [ ] Errors are user-friendly
- [ ] Status command provides insights

---

## ⚠️ Risks & Mitigations

### Risk 1: API Key Management

**Risk:** Users don't have all API keys
**Mitigation:** Graceful degradation, clear error messages

### Risk 2: Cost Overruns

**Risk:** Ensemble mode unexpectedly uses expensive models
**Mitigation:** Daily budget limits, cost warnings, dry-run mode

### Risk 3: API Rate Limits

**Risk:** Hit provider rate limits
**Mitigation:** Exponential backoff, fallback chain, error handling

### Risk 4: Context Size Limits

**Risk:** Context exceeds model limits
**Mitigation:** Truncation strategy, warn user, route to larger context model

### Risk 5: Breaking Changes

**Risk:** Router breaks existing workflows
**Mitigation:** Router is opt-in, solo mode is default, extensive testing

---

## 🎯 Phase 1 Implementation Tasks (Next Steps)

### Task 1.1: Setup Python Environment
- [ ] Create `requirements.txt`
- [ ] Create `router/` package
- [ ] Add `.gitignore` entries
- [ ] Test import structure

### Task 1.2: Configuration Loader
- [ ] Load `settings.json`
- [ ] Load `routing.json`
- [ ] Load `models.json`
- [ ] Load API keys from `.env`
- [ ] Validation

### Task 1.3: API Clients
- [ ] `AnthropicClient` class
- [ ] `GoogleClient` class
- [ ] `OpenAIClient` class
- [ ] Unified interface
- [ ] Error handling

### Task 1.4: Basic Executor
- [ ] Load configuration
- [ ] Select model
- [ ] Call API
- [ ] Format response
- [ ] CLI entry point

### Task 1.5: Testing
- [ ] Test with Claude
- [ ] Test with Gemini (if key available)
- [ ] Test error handling
- [ ] Test with invalid config

---

## 📝 Next Actions

1. ✅ Create this plan document
2. ⏭️ Create `requirements.txt`
3. ⏭️ Create Python package structure
4. ⏭️ Implement `config_loader.py`
5. ⏭️ Implement `api_clients.py`
6. ⏭️ Implement `executor.py`
7. ⏭️ Create CLI interface
8. ⏭️ Test end-to-end
9. ⏭️ Move to Phase 2

---

**Let's build this! 🚀**
