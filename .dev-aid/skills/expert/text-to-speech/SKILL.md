---
name: text-to-speech
risk_level: MEDIUM
description: "Expert skill for implementing text-to-speech with Kokoro TTS. Covers voice synthesis, audio generation, performance optimization, and secure handling of generated audio for JARVIS voice assistant."
---

# Text-to-Speech Skill

> **File Organization**: Split structure. See `references/` for detailed implementations.


### 0.4 Progressive Disclosure (500-Line Limit)

**⚠️ CRITICAL**: This SKILL.md file MUST stay <500 lines for Claude Code to load it.

**If this file is approaching 500 lines**:
- Move detailed examples to `references/advanced-patterns.md`
- Move security examples to `references/security-examples.md`
- Move troubleshooting to `references/troubleshooting.md`
- Keep only summaries and links in main file

📚 **For complete progressive disclosure guide**: See `../../../template-references/progressive-disclosure.md`

---

## 0. Anti-Hallucination Protocol

## 0. Anti-Hallucination Protocol

### 0.1 Quick Risk Assessment

**Risk Level**: MEDIUM

**Key Risk Factors**:
- Security concerns in medium-risk domain
- 3 security issues/patterns identified
- Common attack vectors: Voice cloning/deepfakes, Phishing via TTS, SSML injection
- Requires security awareness and best practices

**Immediate Security Actions**:
1. Review security concerns below before any implementation
2. Never proceed without understanding attack surface
3. Implement security controls from § 0.3 as mandatory requirements

### 0.2 Vulnerability Research Protocol

**MANDATORY**: Before ANY implementation, research current vulnerabilities.

**Step 1: CVE Database Search** (NVD, MITRE)
```bash
# Search for latest CVEs (update dates for current year)
https://nvd.nist.gov/vuln/search
# Keywords: [technology name], [framework version]
```

**Step 2: Known Vulnerabilities (2024-2025)**

   - **TTS-ABUSE** (CVSS N/A): TTS abuse for phishing/scams
     Source: https://www.w3.org/TR/speech-synthesis/
   - **VOICE-CLONING** (CVSS 9.0): Deepfake voice generation
     Source: https://arxiv.org/abs/2104.00355
   - **SSML-INJECTION** (CVSS N/A): SSML injection attacks
     Source: https://www.w3.org/TR/speech-synthesis11/

**Step 3: Common Attack Patterns**

   - Voice cloning/deepfakes
   - Phishing via TTS
   - SSML injection
   - Audio watermark removal

**Step 4: MITRE ATT&CK Mapping**
- Tactic: [Initial Access, Execution, Persistence, Privilege Escalation]
- Review MITRE ATT&CK framework for latest techniques

**Update Frequency**: Check for new CVEs weekly during active development.

### 0.3 Hallucination Prevention Checklist

**CRITICAL**: These rules are ABSOLUTE. Violation = security incident.

**Domain-Specific Security Rules**:

- ❌ NEVER generate voice without consent
- ❌ NEVER allow SSML from untrusted sources
- ❌ ALWAYS implement rate limiting
- ❌ ALWAYS watermark generated audio

**Before ANY code generation**:
1. ✅ Verify rule compliance for proposed implementation
2. ✅ Check if solution introduces any prohibited patterns
3. ✅ Validate all security assumptions
4. ✅ Confirm defensive coding practices are applied

**If uncertain**: STOP and research. Never guess on security.


## 1. Overview

**Risk Level**: MEDIUM - Generates audio output, potential for inappropriate content synthesis, resource-intensive

You are an expert in text-to-speech systems with deep expertise in Kokoro TTS, voice synthesis, and audio generation optimization. Your mastery spans model configuration, voice customization, streaming audio output, and secure handling of synthesized speech.

You excel at:
- Kokoro TTS deployment and voice configuration
- Real-time streaming synthesis for low latency
- Voice customization and prosody control
- Audio output optimization and format conversion
- Content filtering for appropriate synthesis

**Primary Use Cases**:
- JARVIS voice responses
- Real-time speech synthesis with natural prosody
- Offline TTS (no cloud dependency)
- Multi-voice support for different contexts

---

## 2. Core Principles

- **TDD First** - Write tests before implementation. Verify synthesis output, audio quality, and error handling.
- **Performance Aware** - Optimize for latency: streaming synthesis, model caching, audio chunking.
- **Security First** - Filter content, validate inputs, clean up generated files.
- **Resource Efficient** - Manage GPU/CPU usage, limit concurrency, timeout protection.

---

## 3. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```python
# tests/test_tts_engine.py
import pytest
from pathlib import Path

class TestSecureTTSEngine:
    def test_synthesize_returns_valid_audio(self, tts_engine):
        audio_path = tts_engine.synthesize("Hello test")
        assert Path(audio_path).exists()
        assert audio_path.endswith('.wav')

    def test_audio_has_correct_sample_rate(self, tts_engine):
        import soundfile as sf
        audio_path = tts_engine.synthesize("Test")
        _, sample_rate = sf.read(audio_path)
        assert sample_rate == 24000

    def test_rejects_empty_text(self, tts_engine):
        with pytest.raises(ValidationError):
            tts_engine.synthesize("")

    def test_rejects_text_exceeding_limit(self, tts_engine):
        with pytest.raises(ValidationError):
            tts_engine.synthesize("x" * 6000)

    def test_filters_sensitive_content(self, tts_engine):
        audio_path = tts_engine.synthesize("password: secret123")
        assert Path(audio_path).exists()

    def test_cleanup_removes_temp_files(self, tts_engine):
        tts_engine.synthesize("Test")
        temp_dir = tts_engine.temp_dir
        tts_engine.cleanup()
        assert not Path(temp_dir).exists()

@pytest.fixture
def tts_engine():
    from jarvis.tts import SecureTTSEngine
    engine = SecureTTSEngine(voice="af_heart")
    yield engine
    engine.cleanup()
```

### Step 2: Implement Minimum to Pass

Implement SecureTTSEngine with required methods. Focus only on making tests pass.

### Step 3: Refactor Following Patterns

After tests pass, refactor for streaming output, caching, and async compatibility.

### Step 4: Run Full Verification

```bash
pytest tests/test_tts_engine.py -v                    # Run tests
pytest --cov=jarvis.tts --cov-report=term-missing     # Coverage
mypy src/jarvis/tts/                                  # Type check
python -m jarvis.tts --test "Hello JARVIS"            # Integration
```

---


## 4. Quality Assurance Checklist

**Before implementing this skill, ensure**:

### 4.1 Pre-Implementation Setup
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] Pre-commit hooks installed (`pre-commit install`)
- [ ] Linters installed (black, isort, flake8, mypy, bandit)

### 4.2 Dependency Management
- [ ] All dependencies pinned with exact versions (==)
- [ ] No manual transitive dependency pins
- [ ] Dependencies tested in clean environment

### 4.3 Code Quality Gates (Run BEFORE committing)
- [ ] `black .` - Code formatted
- [ ] `isort .` - Imports sorted
- [ ] `flake8 . --max-line-length=120` - No linting errors
- [ ] `mypy . --ignore-missing-imports` - Type checking passes
- [ ] `bandit -r .` - Security scan clean

### 4.4 Security Validation
- [ ] Input validation for ALL external inputs
- [ ] Path traversal prevention implemented
- [ ] Command injection prevention (no shell=True)
- [ ] SQL injection prevention (parameterized queries)
- [ ] Secrets not in code or error messages

📚 **For complete security validation guide**: See `../../../template-references/security-framework.md`

### 4.5 Test Coverage Requirements
- [ ] Tests written BEFORE implementation (TDD)
- [ ] Unit tests for all public functions
- [ ] Edge case tests (empty, null, max values)
- [ ] Security tests (injection, traversal, overflow)
- [ ] Code coverage >80%

### 4.6 Documentation Requirements
- [ ] Docstrings for all public functions/classes
- [ ] Security considerations documented
- [ ] Examples of correct usage
- [ ] Known limitations documented

---

## 5. Performance Patterns

## 5. Performance Patterns

📚 **For complete details**: See `references/performance-patterns.md`

---
## 6. Core Responsibilities

### 5.1 Secure Audio Generation

When implementing TTS, you will:
- **Filter input text** - Block inappropriate or harmful content
- **Validate text length** - Prevent DoS via excessive generation
- **Secure output storage** - Proper permissions on generated audio
- **Clean up files** - Delete generated audio after playback
- **Log safely** - Don't log sensitive text content

### 5.2 Performance Optimization

- Optimize for real-time streaming output
- Implement audio caching for repeated phrases
- Balance quality vs. latency for voice assistant use
- Manage GPU/CPU resources efficiently

---

## 7. Technical Foundation

### 6.1 Core Technologies

**Kokoro TTS**

| Use Case | Version | Notes |
|----------|---------|-------|
| **Production** | kokoro>=0.3.0 | Latest stable |

**Supporting Libraries**

```python
# requirements.txt
kokoro>=0.3.0
numpy>=1.24.0
soundfile>=0.12.0
sounddevice>=0.4.6
scipy>=1.10.0
pydantic>=2.0
structlog>=23.0
```

### 6.2 Voice Configuration

| Voice | Style | Use Case |
|-------|-------|----------|
| af_heart | Warm, friendly | Default JARVIS |
| af_bella | Professional | Formal responses |
| am_adam | Male | Alternative voice |
| bf_emma | British | Accent variation |

---

## 8. Implementation Patterns

### Pattern 1: Secure TTS Engine

```python
from kokoro import KPipeline
import soundfile as sf
import numpy as np
from pathlib import Path
import tempfile
import os
import structlog

logger = structlog.get_logger()

class SecureTTSEngine:
    """Secure text-to-speech with content filtering."""

    def __init__(self, voice: str = "af_heart", lang_code: str = "a"):
        # Initialize Kokoro pipeline
        self.pipeline = KPipeline(lang_code=lang_code)
        self.voice = voice

        # Content filter patterns
        self.blocked_patterns = [
            r"password\s*[:=]",
            r"api[_-]?key\s*[:=]",
            r"secret\s*[:=]",
        ]

        # Create secure temp directory
        self.temp_dir = tempfile.mkdtemp(prefix="jarvis_tts_")
        os.chmod(self.temp_dir, 0o700)

        logger.info("tts.initialized", voice=voice)

    def synthesize(self, text: str) -> str:
        """Synthesize text to audio file."""
        # Validate and filter input
        if not self._validate_text(text):
            raise ValidationError("Invalid text input")

        filtered_text = self._filter_sensitive(text)

        # Generate audio
        audio_path = Path(self.temp_dir) / f"{uuid.uuid4()}.wav"

        generator = self.pipeline(
            filtered_text,
            voice=self.voice,
            speed=1.0
        )

        # Collect audio chunks
    ## 8. Implementation Patterns

## 8. Implementation Patterns

📚 **For complete details**: See `references/implementation-patterns.md`

---

    engine.synthesize(filtered)
```

### NEVER: Unlimited Generation

```python
# BAD - Can generate very long audio
engine.synthesize(long_text)  # No limit

# GOOD - Enforce limits
if len(text) > 5000:
    raise ValidationError("Text too long")
engine.synthesize(text)
```

---

## 11. Pre-Implementation Checklist

### Before Writing Code

- [ ] Write failing tests for TTS synthesis output
- [ ] Define expected audio format (24kHz WAV)
- [ ] Plan content filtering patterns
- [ ] Design caching strategy for common phrases
- [ ] Review Kokoro TTS API documentation

### During Implementation

- [ ] Run tests after each method implementation
- [ ] Implement streaming output for low latency
- [ ] Add input validation (length, characters)
- [ ] Implement sensitive content filtering
- [ ] Set up secure temp directory with 0o700 permissions
- [ ] Add concurrency limits (max 2 workers)
- [ ] Implement timeout protection (30s default)

### Before Committing

- [ ] All TTS tests pass: `pytest tests/test_tts_engine.py -v`
- [ ] Coverage meets threshold: `pytest --cov=jarvis.tts`
- [ ] Type checking passes: `mypy src/jarvis/tts/`
- [ ] No sensitive text logged
- [ ] Generated audio cleanup verified
- [ ] Voice preloading tested
- [ ] Integration test passes: `python -m jarvis.tts --test`

---

## 12. Summary

Your goal is to create TTS systems that are:
- **Fast**: Real-time streaming for responsive voice assistant
- **Safe**: Content filtering for appropriate synthesis
- **Efficient**: Caching for common phrases

You understand that TTS requires input validation and content filtering to prevent synthesis of inappropriate content. Always enforce text length limits and clean up generated audio files.

**Critical Reminders**:
1. Filter text content before synthesis
2. Enforce text length limits (max 5000 chars)
3. Delete generated audio after playback
4. Never log sensitive text content
5. Cache common phrases for performance
