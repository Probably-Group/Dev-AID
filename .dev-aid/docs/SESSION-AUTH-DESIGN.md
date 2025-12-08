# Session-Based Authentication Support - Design Document

**Version**: 1.0
**Created**: 2025-12-08
**Priority**: High - Blocks adoption for majority of developers
**Issue**: Most developers have consumer subscriptions (Claude Pro/Max, Gemini CLI) with session auth, not API keys

---

## 🚨 Problem Statement

### Current Limitation

Dev-AID router **requires API keys** for all providers:
```bash
# .dev-aid/config/.env
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
OPENAI_API_KEY=sk-...
```

### Real-World User Scenarios

**Scenario A: Developer with Claude Pro subscription**
- Has Claude Pro ($20/mo) or Max ($100/mo)
- Logged in via `claude` CLI (session-based auth)
- **No API key available** - Anthropic doesn't provide API keys for consumer accounts
- **Can't use Dev-AID router** ❌

**Scenario B: Developer with Gemini CLI**
- Logged in via `gcloud auth application-default login`
- Uses Application Default Credentials (ADC)
- Has API key from AI Studio, but prefers not to expose it
- **Can't leverage existing auth** ❌

**Scenario C: Developer with ChatGPT Plus**
- Has ChatGPT Plus ($20/mo)
- **No API access at all** - separate API subscription required ($0.50-$60/request)
- **Can't use OpenAI in router** ❌

### Impact

- **80-90% of AI tool users** have consumer subscriptions, not API keys
- Dev-AID router is **unusable** for this majority
- Users must either:
  - Buy separate API subscriptions (expensive, redundant)
  - Not use Dev-AID router at all (loses 95% cost savings)

---

## 🎯 Solution: Hybrid Authentication Strategy

### Approach: Detect and Reuse Session Auth → Fallback to API Keys

**Priority Order**:
1. **Session-based auth** (if CLI is authenticated)
2. **API key** (if provided in .env)
3. **Skip provider** (if neither available)

---

## 🏗️ Architecture

### Authentication Flow

```
┌─────────────────────────────────────────────────────────┐
│  Dev-AID Router Initialization                          │
└─────────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│  For each provider (claude, gemini, openai):            │
│                                                           │
│  1. Try Session Auth (detect_session_auth())            │
│     ├─ Claude: Check ~/.config/claude/config.json       │
│     ├─ Gemini: Check ADC credentials                    │
│     └─ OpenAI: Not supported (API-only)                 │
│                                                           │
│  2. If session found → Use session token                │
│     └─ Success! No API key needed                       │
│                                                           │
│  3. Else: Try API Key (get_api_key())                   │
│     └─ Read from ANTHROPIC_API_KEY env var              │
│                                                           │
│  4. If API key found → Use API key                      │
│     └─ Success! Traditional auth                        │
│                                                           │
│  5. Else: Skip provider                                 │
│     └─ Warning: Provider unavailable                    │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 Implementation Plan

### Phase 1: Session Detection Module (Week 1)

Create `.dev-aid/orchestration/router/auth_detector.py`:

```python
"""
Authentication Detection Module

Detects existing session-based authentication from CLI tools and
provides unified interface for both session auth and API keys.
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class AuthCredentials:
    """Unified authentication credentials"""

    provider: str  # "claude", "gemini", "openai"
    auth_type: str  # "session", "api_key", "adc"
    credentials: Dict[str, Any]  # Provider-specific auth data
    source: str  # Where auth was found (e.g., "~/.config/claude/config.json")


class AuthDetector:
    """Detect and manage authentication across multiple providers"""

    def __init__(self):
        self.home = Path.home()

    def detect_all(self) -> Dict[str, Optional[AuthCredentials]]:
        """
        Detect authentication for all providers

        Returns:
            Dict mapping provider name to AuthCredentials (or None if not found)
        """
        return {
            "claude": self.detect_claude_auth(),
            "gemini": self.detect_gemini_auth(),
            "openai": self.detect_openai_auth(),
        }

    def detect_claude_auth(self) -> Optional[AuthCredentials]:
        """
        Detect Claude CLI session authentication

        Claude Code CLI stores session data in:
        - macOS/Linux: ~/.config/claude/config.json
        - Windows: %APPDATA%\claude\config.json

        Returns:
            AuthCredentials if session found, None otherwise
        """
        # Try standard Claude config locations
        config_paths = [
            self.home / ".config" / "claude" / "config.json",  # Linux/macOS
            self.home / "AppData" / "Roaming" / "claude" / "config.json",  # Windows
            self.home / ".claude" / "config.json",  # Alternative location
        ]

        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path) as f:
                        config = json.load(f)

                    # Extract session token (structure may vary by CLI version)
                    session_token = config.get("sessionToken") or config.get("session_token")
                    if session_token:
                        logger.info(f"Found Claude session auth at: {config_path}")
                        return AuthCredentials(
                            provider="claude",
                            auth_type="session",
                            credentials={"session_token": session_token},
                            source=str(config_path)
                        )
                except Exception as e:
                    logger.warning(f"Failed to read Claude config at {config_path}: {e}")

        # Try API key as fallback
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            logger.info("Using Claude API key from environment")
            return AuthCredentials(
                provider="claude",
                auth_type="api_key",
                credentials={"api_key": api_key},
                source="ANTHROPIC_API_KEY environment variable"
            )

        logger.warning("No Claude authentication found (neither session nor API key)")
        return None

    def detect_gemini_auth(self) -> Optional[AuthCredentials]:
        """
        Detect Google/Gemini authentication

        Priority:
        1. Application Default Credentials (ADC) from gcloud CLI
        2. GOOGLE_API_KEY environment variable

        ADC locations:
        - macOS/Linux: ~/.config/gcloud/application_default_credentials.json
        - Windows: %APPDATA%\gcloud\application_default_credentials.json

        Returns:
            AuthCredentials if auth found, None otherwise
        """
        # Try ADC (Application Default Credentials)
        adc_paths = [
            self.home / ".config" / "gcloud" / "application_default_credentials.json",
            self.home / "AppData" / "Roaming" / "gcloud" / "application_default_credentials.json",
        ]

        for adc_path in adc_paths:
            if adc_path.exists():
                try:
                    with open(adc_path) as f:
                        adc_config = json.load(f)

                    # ADC file contains refresh token or service account credentials
                    if adc_config.get("type") or adc_config.get("refresh_token"):
                        logger.info(f"Found Google ADC at: {adc_path}")
                        return AuthCredentials(
                            provider="gemini",
                            auth_type="adc",
                            credentials={"adc_path": str(adc_path)},
                            source=str(adc_path)
                        )
                except Exception as e:
                    logger.warning(f"Failed to read Google ADC at {adc_path}: {e}")

        # Try API key as fallback
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            logger.info("Using Google API key from environment")
            return AuthCredentials(
                provider="gemini",
                auth_type="api_key",
                credentials={"api_key": api_key},
                source="GOOGLE_API_KEY environment variable"
            )

        logger.warning("No Google/Gemini authentication found (neither ADC nor API key)")
        return None

    def detect_openai_auth(self) -> Optional[AuthCredentials]:
        """
        Detect OpenAI authentication

        Note: OpenAI is API-key only. ChatGPT Plus subscription does NOT
        provide API access. Users must purchase separate API credits.

        Returns:
            AuthCredentials if API key found, None otherwise
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            logger.info("Using OpenAI API key from environment")
            return AuthCredentials(
                provider="openai",
                auth_type="api_key",
                credentials={"api_key": api_key},
                source="OPENAI_API_KEY environment variable"
            )

        logger.warning("No OpenAI API key found. Note: ChatGPT Plus does NOT include API access.")
        return None
```

### Phase 2: Update API Clients to Support Session Auth (Week 1)

**Modify `api_clients.py` to accept `AuthCredentials` instead of just `api_key`:**

```python
class BaseAIClient(ABC):
    """Base class for AI provider clients"""

    def __init__(self, auth: AuthCredentials, model_config: Dict[str, Any]):
        """
        Initialize AI client

        Args:
            auth: Authentication credentials (session or API key)
            model_config: Model configuration from models.json
        """
        self.auth = auth
        self.model_config = model_config
        self.provider = model_config.get("provider", "unknown")


class AnthropicClient(BaseAIClient):
    """Client for Anthropic Claude API"""

    def __init__(self, auth: AuthCredentials, model_config: Dict[str, Any]):
        super().__init__(auth, model_config)

        try:
            import anthropic

            if auth.auth_type == "session":
                # Use session token (if Claude SDK supports it)
                # NOTE: As of Dec 2024, Anthropic SDK may not support session tokens directly
                # Workaround: Use undocumented API endpoint with session header
                self.client = anthropic.Anthropic(
                    api_key="dummy",  # SDK requires api_key parameter
                    default_headers={"Authorization": f"Bearer {auth.credentials['session_token']}"}
                )
            elif auth.auth_type == "api_key":
                # Traditional API key auth
                self.client = anthropic.Anthropic(api_key=auth.credentials["api_key"])
            else:
                raise ValueError(f"Unsupported auth type for Anthropic: {auth.auth_type}")

        except ImportError:
            raise ImportError(
                "anthropic package not installed. "
                "Install with: pip install anthropic"
            )


class GoogleClient(BaseAIClient):
    """Client for Google Gemini API"""

    def __init__(self, auth: AuthCredentials, model_config: Dict[str, Any]):
        super().__init__(auth, model_config)

        try:
            from google import genai
            from google.genai import types

            if auth.auth_type == "adc":
                # Use Application Default Credentials
                # Google SDK automatically detects ADC
                self.client = genai.Client()  # No api_key needed!
            elif auth.auth_type == "api_key":
                # Traditional API key auth
                self.client = genai.Client(api_key=auth.credentials["api_key"])
            else:
                raise ValueError(f"Unsupported auth type for Google: {auth.auth_type}")

            self.types = types

        except ImportError:
            raise ImportError(
                "google-genai package not installed. "
                "Install with: pip install google-genai"
            )
```

### Phase 3: Update Config Loader (Week 1)

**Modify `config_loader.py` to use `AuthDetector`:**

```python
from .auth_detector import AuthDetector, AuthCredentials

class ConfigLoader:
    def __init__(self, dev_aid_root: Optional[Path] = None):
        # ... existing code ...

        # Initialize auth detector
        self.auth_detector = AuthDetector()
        self._detected_auth = None  # Cache auth detection results

    def get_auth_credentials(self, provider: str) -> Optional[AuthCredentials]:
        """
        Get authentication credentials for a provider

        Tries in order:
        1. Session-based auth (if CLI is authenticated)
        2. API key (from environment)
        3. None (provider unavailable)

        Args:
            provider: Provider name (claude, gemini, openai)

        Returns:
            AuthCredentials or None
        """
        # Lazy-load auth detection (runs once)
        if self._detected_auth is None:
            self._detected_auth = self.auth_detector.detect_all()

        return self._detected_auth.get(provider)

    # Keep old method for backward compatibility
    def get_api_key(self, provider: str) -> Optional[str]:
        """
        DEPRECATED: Use get_auth_credentials() instead

        Get API key for a provider (legacy method)
        """
        auth = self.get_auth_credentials(provider)
        if auth and auth.auth_type == "api_key":
            return auth.credentials["api_key"]
        return None
```

### Phase 4: Update Mode Handlers (Week 1)

**Modify `modes/solo.py` (and ensemble, challenger):**

```python
def execute(self, request: str, **kwargs) -> Dict[str, Any]:
    # ... existing code ...

    # Get authentication credentials (session or API key)
    auth = self.config.get_auth_credentials(provider)

    if not auth:
        return {
            "success": False,
            "mode": "solo",
            "model": model_name,
            "provider": provider,
            "error": f"No authentication found for {provider}. "
                    f"Please either: (1) Sign in to {provider} CLI, or "
                    f"(2) Set {provider.upper()}_API_KEY in .env"
        }

    # Create client with auth credentials
    client = create_client(provider, auth, model_config)

    # ... rest of execution ...
```

**Update `create_client()` signature:**

```python
def create_client(provider: str, auth: AuthCredentials, model_config: Dict[str, Any]) -> BaseAIClient:
    """
    Factory function to create appropriate AI client

    Args:
        provider: Provider name ("anthropic", "google", "openai")
        auth: Authentication credentials (session or API key)
        model_config: Model configuration

    Returns:
        Initialized AI client
    """
    clients = {
        "anthropic": AnthropicClient,
        "google": GoogleClient,
        "openai": OpenAIClient,
    }

    client_class = clients.get(provider)
    if not client_class:
        raise ValueError(f"Unknown provider: {provider}")

    return client_class(auth, model_config)
```

### Phase 5: Update CLI and Documentation (Week 2)

**Update `router-cli.sh`:**

```bash
#!/bin/bash
# ... existing code ...

# Show authentication status
if [ "$1" = "status" ]; then
    echo "🔐 Authentication Status:"
    python -m router.cli auth-status
    exit 0
fi
```

**Add CLI command `router/cli.py`:**

```python
@app.command()
def auth_status():
    """Show authentication status for all providers"""
    from .auth_detector import AuthDetector

    detector = AuthDetector()
    auth_results = detector.detect_all()

    print("\n🔐 Authentication Status:\n")

    for provider, auth in auth_results.items():
        if auth:
            icon = "✅"
            status = f"{auth.auth_type.upper()} ({auth.source})"
        else:
            icon = "❌"
            status = "Not authenticated"

        print(f"{icon} {provider.title()}: {status}")

    print("\nTo authenticate:")
    print("  Claude:  claude login")
    print("  Gemini:  gcloud auth application-default login")
    print("  OpenAI:  export OPENAI_API_KEY=sk-...")
```

**Update ROUTER-INSTALL.md:**

```markdown
## Step 2: Configure Authentication (New: Session Auth Supported!)

Dev-AID now supports **two authentication methods**:

### Option A: Session-Based Auth (Recommended for Consumer Accounts)

**If you have Claude Pro/Max, Gemini CLI, or GitHub Copilot:**

```bash
# Claude Code CLI
claude login  # Opens browser to authenticate

# Gemini CLI
gcloud auth application-default login  # Opens browser

# OpenAI (API-only, no session auth available)
export OPENAI_API_KEY=sk-...
```

**Verify authentication:**
```bash
./router-cli.sh auth-status

# Expected output:
# 🔐 Authentication Status:
# ✅ Claude: SESSION (~/.config/claude/config.json)
# ✅ Gemini: ADC (~/.config/gcloud/application_default_credentials.json)
# ❌ OpenAI: Not authenticated
```

### Option B: API Keys (For Developers with API Subscriptions)

If you have separate API subscriptions, create `.dev-aid/config/.env`:

```bash
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
OPENAI_API_KEY=sk-...
```

**Priority**: Session auth is tried first, then API keys. Both can coexist!
```

---

## 🧪 Testing Strategy

### Unit Tests

```python
# tests/test_auth_detector.py

def test_detect_claude_session(mock_claude_config):
    """Test Claude session detection"""
    detector = AuthDetector()
    auth = detector.detect_claude_auth()

    assert auth is not None
    assert auth.provider == "claude"
    assert auth.auth_type == "session"
    assert "session_token" in auth.credentials


def test_fallback_to_api_key(monkeypatch):
    """Test fallback to API key if session not found"""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")

    detector = AuthDetector()
    auth = detector.detect_claude_auth()

    assert auth is not None
    assert auth.auth_type == "api_key"


def test_no_auth_found():
    """Test behavior when no auth found"""
    detector = AuthDetector()
    auth = detector.detect_claude_auth()

    assert auth is None
```

### Integration Tests

```bash
# Manual test checklist

1. Claude Session Auth:
   - [ ] Sign in to Claude CLI: `claude login`
   - [ ] Run: `./router-cli.sh execute "test" --mode solo`
   - [ ] Verify: Request succeeds without API key in .env

2. Gemini ADC Auth:
   - [ ] Sign in to gcloud: `gcloud auth application-default login`
   - [ ] Run: `./router-cli.sh execute "test" --mode ensemble`
   - [ ] Verify: Gemini requests work without GOOGLE_API_KEY

3. API Key Fallback:
   - [ ] Remove session files
   - [ ] Set API keys in .env
   - [ ] Verify: Router still works

4. No Auth Error:
   - [ ] Remove both session and API keys
   - [ ] Verify: Clear error message shown
```

---

## 📊 Implementation Timeline

| Week | Tasks | Deliverables |
|------|-------|--------------|
| Week 1 | Phase 1-3: Auth detection + API clients | Working session auth for Claude & Gemini |
| Week 1 | Phase 4: Update mode handlers | All router modes support session auth |
| Week 2 | Phase 5: CLI + Documentation | `auth-status` command, updated docs |
| Week 2 | Testing + Bug fixes | Unit tests, integration tests, fixes |

**Total Effort**: 1-2 weeks

---

## 🚧 Known Limitations & Workarounds

### 1. Anthropic SDK May Not Support Session Tokens

**Issue**: The official `anthropic` Python SDK is designed for API keys, not session tokens.

**Workaround Options**:
- **Option A**: Use undocumented API endpoint with session header (fragile, may break)
- **Option B**: Extract session token and convert to API-compatible format (if possible)
- **Option C**: Wait for official SDK support and document limitation for now

**Recommendation**: Start with Option A, document as "experimental", add fallback message.

### 2. ChatGPT Plus != API Access

**Issue**: ChatGPT Plus subscription does NOT provide API access.

**Solution**: Clear error message explaining this:
```
❌ OpenAI: Not authenticated
Note: ChatGPT Plus does not include API access.
To use OpenAI in Dev-AID router, purchase API credits at:
https://platform.openai.com/
```

### 3. Token Expiration

**Issue**: Session tokens expire and need refresh.

**Solution**:
- Detect expired tokens (401 errors)
- Show helpful error: "Session expired. Please re-authenticate: `claude login`"
- Auto-retry after user re-authenticates

---

## ✅ Success Criteria

- [ ] Developers with Claude Pro/Max can use router without API key
- [ ] Developers with Gemini CLI can use router without API key
- [ ] API key fallback still works for users who prefer it
- [ ] Clear error messages when no auth found
- [ ] `auth-status` command shows current authentication
- [ ] Documentation updated with both methods
- [ ] Unit tests cover all auth paths
- [ ] Integration tests verify real CLI auth works

---

## 📝 Open Questions

1. **Claude session token format**: Does Anthropic SDK accept session tokens? Need to investigate actual Claude CLI auth mechanism.

2. **Token refresh**: How do we handle expired sessions? Auto-refresh or just show error?

3. **Security**: Should we cache session tokens in memory or re-read from disk each time?

4. **Windows support**: Are auth file locations correct for Windows?

5. **Backward compatibility**: Should we keep old `get_api_key()` method or deprecate immediately?

---

**Next Steps**:
1. Research Claude CLI authentication mechanism (session token format)
2. Prototype Phase 1 (AuthDetector) with real Claude CLI session
3. Test if Anthropic SDK accepts session tokens
4. If not, implement workaround or document limitation
5. Proceed with full implementation

---

**Implementation Owner**: TBD
**Reviewers**: TBD
**Target Release**: v1.3.0 (alongside TOON format integration)
