---
name: wake-word-detection
risk_level: MEDIUM
description: "Expert skill for implementing wake word detection with openWakeWord. Covers audio monitoring, keyword spotting, privacy protection, and efficient always-listening systems for JARVIS voice assistant."
---

# Wake Word Detection Skill


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
- Common attack vectors: Adversarial wake word triggering, False activation attacks, Privacy violations
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

   - **FALSE-WAKE** (CVSS N/A): False wake word activation
     Source: https://arxiv.org/abs/1904.05734
   - **ADVERSARIAL-AUDIO** (CVSS 7.5): Adversarial wake word attacks
     Source: https://www.usenix.org/conference/usenixsecurity19/
   - **PRIVACY-ALWAYS-ON** (CVSS N/A): Always-on microphone privacy risks
     Source: https://www.ftc.gov/business-guidance/blog/2023/06/voice-cloning-ai-scams

**Step 3: Common Attack Patterns**

   - Adversarial wake word triggering
   - False activation attacks
   - Privacy violations

**Step 4: MITRE ATT&CK Mapping**
- Tactic: [Initial Access, Execution, Persistence, Privilege Escalation]
- Review MITRE ATT&CK framework for latest techniques

**Update Frequency**: Check for new CVEs weekly during active development.

### 0.3 Hallucination Prevention Checklist

**CRITICAL**: These rules are ABSOLUTE. Violation = security incident.

**Domain-Specific Security Rules**:

- ❌ NEVER store audio before wake word
- ❌ NEVER process audio without user indicator
- ❌ ALWAYS implement false positive mitigation
- ❌ ALWAYS use on-device processing

**Before ANY code generation**:
1. ✅ Verify rule compliance for proposed implementation
2. ✅ Check if solution introduces any prohibited patterns
3. ✅ Validate all security assumptions
4. ✅ Confirm defensive coding practices are applied

**If uncertain**: STOP and research. Never guess on security.


## 1. Overview

**Risk Level**: MEDIUM - Continuous audio monitoring, privacy implications, resource constraints

You are an expert in wake word detection with deep expertise in openWakeWord, keyword spotting, and always-listening systems.

**Primary Use Cases**:
- JARVIS activation phrase detection ("Hey JARVIS")
- Always-listening with minimal resource usage
- Offline wake word detection (no cloud dependency)

---

## 2. Core Principles

- **TDD First** - Write tests before implementation code
- **Performance Aware** - Optimize for CPU, memory, and latency
- **Privacy Preserving** - Never store audio, minimize buffers
- **Accuracy Focused** - Minimize false positives/negatives
- **Resource Efficient** - Target <5% CPU, <100MB memory

---

## 3. Core Responsibilities

### 3.1 Privacy-First Monitoring

- **Process locally** - Never send audio to external services
- **Buffer minimally** - Only keep audio needed for detection
- **Discard non-wake** - Immediately discard non-wake audio
- **User control** - Easy disable/pause functionality

### 3.2 Efficiency Requirements

- Minimal CPU usage (<5% average)
- Low memory footprint (<100MB)
- Low latency detection (<500ms)
- Low false positive rate (<1 per hour)

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

## 5. Technical Foundation

```python
# requirements.txt
openwakeword>=0.6.0
numpy>=1.24.0
sounddevice>=0.4.6
onnxruntime>=1.16.0
```

---

## 6. Implementation Workflow (TDD)

class TestWakeWordDetector:
    """TDD tests for wake word detection."""

📚 **For complete details**: See `references/implementation-workflow-tdd.md`

---
## 7. Implementation Patterns

### Pattern 1: Secure Wake Word Detector

```python
from openwakeword.model import Model
import numpy as np
import sounddevice as sd
from collections import deque
import structlog

logger = structlog.get_logger()

class SecureWakeWordDetector:
    """Privacy-preserving wake word detection."""

    def __init__(self, model_path: str = None, threshold: float = 0.5, sample_rate: int = 16000):
        if model_path:
            self.model = Model(wakeword_models=[model_path])
        else:
            self.model = Model(wakeword_models=["hey_jarvis"])

        self.threshold = threshold
        self.sample_rate = sample_rate
        self.buffer_size = int(sample_rate * 1.5)
        self.audio_buffer = deque(maxlen=self.buffer_size)
        self.is_listening = False
        self.on_wake = None

    def start(self, callback):
        """Start listening for wake word."""
        self.on_wake = callback
        self.is_listening = True

        def audio_callback(indata, frames, time, status):
            if not self.is_listening:
                return
            audio = indata[:, 0] if len(indata.shape) > 1 else indata
            self.audio_buffer.extend(audio)
            if len(self.audio_buffer) >= self.sample_rate:
                self._process_audio()

        self.stream = sd.InputStream(
            samplerate=self.sample_rate, channels=1, dtype=np.float32,
            callback=audio_callback, blocksize=int(self.sample_rate * 0.1)
        )
        self.stream.start()

    def _process_audio(self):
        """Process audio buffer for wake word."""
        audio = np.array(list(self.audio_buffer))
        predictions = self.model.predict(audio)

        for model_name, scores in predictions.items():
            if np.max(scores) > self.threshold:
                self.audio_buffer.clear()  # Privacy: clear immediately
                if self.on_wake:
                    self.on_wake(model_name, np.max(scores))
                break

    def stop(self):
        """Stop listening."""
        self.is_listening = False
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        self.audio_buffer.clear()
```

### Pattern 2: False Positive Reduction

```python
class RobustDetector:
    """Reduce false positives with confirmation."""

    def __init__(self, detector: SecureWakeWordDetector):
        self.detector = detector
        self.detection_history = []
        self.confirmation_window = 2.0
        self.min_confirmations = 2

    def on_potential_wake(self, model: str, confidence: float):
        now = time.time()
        self.detection_history.append({"time": now, "confidence": confidence})
        self.detection_history = [d for d in self.detection_history if now - d["time"] < self.confirmation_window]

        if len(self.detection_history) >= self.min_confirmations:
            avg_confidence = np.mean([d["confidence"] for d in self.detection_history])
            if avg_confidence > 0.6:
                self.detection_history.clear()
                return True
        return False
```

---

## 8. Performance Patterns

### Pattern 1: Model Quantization

```python
# Good - Use quantized ONNX model
import onnxruntime as ort

class QuantizedDetector:
    def __init__(self, model_path: str):
        sess_options = ort.SessionOptions()
    ## 7. Implementation Patterns

## 7. Implementation Patterns

📚 **For complete details**: See `references/implementation-patterns.md`

---
elf.last_activity = time.time()

    def check_privacy_mode(self) -> bool:
        if self._is_dnd_enabled():
            return False
        if time.time() - self.last_activity > 3600:
            return False
        return self.is_enabled

# Data minimization
MAX_BUFFER_SECONDS = 2.0
def on_wake_detected():
    audio_buffer.clear()  # Delete immediately
```

---

## 10. Common Mistakes

```python
# BAD - Stores all audio
def on_audio(chunk):
    with open("audio.raw", "ab") as f:
        f.write(chunk)

# GOOD - Discard after processing
def on_audio(chunk):
    buffer.extend(chunk)
    process_buffer()

# BAD - Large buffer
buffer = deque(maxlen=sample_rate * 60)  # 1 minute!

# GOOD - Minimal buffer
buffer = deque(maxlen=sample_rate * 1.5)  # 1.5 seconds
```

---

## 11. Pre-Implementation Checklist

### Phase 1: Before Writing Code

- [ ] Read TDD workflow section completely
- [ ] Set up test file with detection accuracy tests
- [ ] Define threshold and performance targets
- [ ] Identify which performance patterns apply
- [ ] Review privacy requirements

### Phase 2: During Implementation

- [ ] Write failing test for each feature first
- [ ] Implement minimal code to pass test
- [ ] Apply performance patterns (VAD, quantization)
- [ ] Buffer size minimal (<2 seconds)
- [ ] Audio cleared after detection

### Phase 3: Before Committing

- [ ] All tests pass: `pytest tests/test_wake_word.py -v`
- [ ] Coverage >80%: `pytest --cov=wake_word`
- [ ] False positive rate <1/hour tested
- [ ] CPU usage <5% measured
- [ ] Memory usage <100MB verified
- [ ] Audio never stored to disk

---

## 12. Summary

Your goal is to create wake word detection that is:
- **Private**: Audio processed locally, minimal retention
- **Efficient**: Low CPU (<5%), low memory (<100MB)
- **Accurate**: Low false positive rate (<1/hour)
- **Test-Driven**: All features have tests first

**Critical Reminders**:
1. Write tests before implementation
2. Never store audio to disk
3. Keep buffer minimal (<2 seconds)
4. Apply performance patterns (VAD, quantization)
## 8. Performance Patterns

class QuantizedDetector:
    def __init__(self, model_path: str):
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        self.session = ort.InferenceSession(model_path, sess_options, providers=['CPUExecutionProvid...

📚 **For complete details**: See `references/performance-patterns.md`

---
