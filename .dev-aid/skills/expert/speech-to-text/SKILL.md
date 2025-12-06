---
name: speech-to-text
risk_level: MEDIUM
description: "Expert skill for implementing speech-to-text with Faster Whisper. Covers audio processing, transcription optimization, privacy protection, and secure handling of voice data for JARVIS voice assistant."
---

# Speech-to-Text Skill

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

## 1. Overview

**Risk Level**: MEDIUM - Processes audio input, potential privacy concerns, resource-intensive

You are an expert in speech-to-text systems with deep expertise in Faster Whisper, audio processing, and transcription optimization. Your mastery spans model selection, audio preprocessing, real-time transcription, and privacy protection for voice data.

You excel at:
- Faster Whisper deployment and optimization
- Audio preprocessing and noise reduction
- Real-time streaming transcription
- Privacy-preserving voice processing
- Multi-language and accent handling

**Primary Use Cases**:
- JARVIS voice command recognition
- Real-time transcription with low latency
- Offline speech recognition (no cloud dependency)
- Multi-language support for accessibility

---

## 2. Core Principles

1. **TDD First** - Write tests before implementation; verify accuracy metrics
2. **Performance Aware** - Optimize latency, memory, and throughput for real-time use
3. **Privacy First** - Process locally, delete immediately, never log content
4. **Security Conscious** - Validate inputs, secure temp files, filter PII

---

## 3. Core Responsibilities

### 2.1 Privacy-First Audio Processing

When implementing STT, you will:
- **Process locally** - No audio sent to external services
- **Minimize retention** - Delete audio after transcription
- **Secure temp files** - Use encrypted temporary storage
- **Log carefully** - Never log audio content or transcriptions with PII
- **Validate audio** - Check format and size before processing

### 2.2 Performance Optimization

- Optimize model selection for hardware (GPU/CPU)
- Implement voice activity detection (VAD)
- Use streaming for real-time feedback
- Minimize latency for responsive voice assistant

---

## 3. Technical Foundation

### 3.1 Core Technologies

**Faster Whisper**

| Use Case | Version | Notes |
|----------|---------|-------|
| **Production** | faster-whisper>=1.0.0 | CTranslate2 optimized |
| **Minimum** | faster-whisper>=0.9.0 | Stable API |

**Supporting Libraries**

```python
# requirements.txt
faster-whisper>=1.0.0
numpy>=1.24.0
soundfile>=0.12.0
webrtcvad>=2.0.10  # Voice activity detection
pydub>=0.25.0  # Audio processing
structlog>=23.0
```

### 3.2 Model Selection Guide

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| tiny | 39MB | Fastest | Low | Testing |
| base | 74MB | Fast | Medium | Quick responses |
| small | 244MB | Medium | Good | General use |
| medium | 769MB | Slow | Better | Complex audio |
| large-v3 | 1.5GB | Slowest | Best | Maximum accuracy |

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

## 5. Implementation Workflow (TDD)

class TestSTTEngine:
    @pytest.fixture
    def engine(self):
        from jarvis.stt import SecureSTTEngine
        return SecureSTTEngine(model_size="base", device="cpu")

📚 **For complete details**: See `references/implementation-workflow-tdd.md`

---
## 6. Performance Patterns

### Pattern 1: Streaming Transcription (Low Latency)

```python
# GOOD - Stream chunks for real-time feedback
def process_chunk(self, chunk, sr=16000):
    self.buffer.append(chunk)
    if sum(len(c) for c in self.buffer) / sr >= 0.5:
        audio = np.concatenate(self.buffer)
        segments, _ = self.model.transcribe(audio, vad_filter=True)
        self.buffer = []
        return " ".join(s.text for s in segments)
    return None

# BAD - Wait for complete audio
result = model.transcribe(audio_path)  # User waits for entire recording
```

### Pattern 2: VAD Preprocessing (Reduce Processing)

```python
# GOOD - Filter silence before transcription
import webrtcvad
vad = webrtcvad.Vad(2)

def extract_speech(audio, sr=16000):
    audio_int16 = (audio * 32767).astype(np.int16)
    frame_size = int(sr * 30 / 1000)  # 30ms frames
    return np.concatenate([
        audio[i:i+frame_size] for i in range(0, len(audio_int16), frame_size)
        if len(audio_int16[i:i+frame_size]) == frame_size
        and vad.is_speech(audio_int16[i:i+frame_size].tobytes(), sr)
    ])

# BAD - Process entire audio including silence
model.transcribe(audio_path)  # Wastes compute on silence
```

### Pattern 3: Model Quantization (Memory + Speed)

```python
# GOOD - Quantized for CPU
engine = SecureSTTEngine(model_size="small", device="cpu", compute_type="int8")

# GOOD - Float16 for GPU
engine = SecureSTTEngine(model_size="medium", device="cuda", compute_type="float16")

# BAD - Full precision unnecessarily
engine = SecureSTTEngine(model_size="small", device="cpu", compute_type="float32")
```

### Pattern 4: Batch Processing (Throughput)

```python
# GOOD - Process multiple files in parallel
from concurrent.futures import ThreadPoolExecutor

def transcribe_batch(engine, paths):
    with ThreadPoolExecutor(max_workers=4) as ex:
        return list(ex.map(engine.transcribe, paths))

# BAD - Sequential processing
results = [engine.transcribe(p) for p in paths]  # Blocks on each
```

### Pattern 5: Audio Buffering (Memory Efficiency)

```python
# GOOD - Fixed-size ring buffer
class RingBuffer:
    def __init__(self, max_samples):
        self.buffer = np.zeros(max_samples, dtype=np.float32)
        self.idx = 0

    def append(self, audio):
        n = len(audio)
        end = (self.idx + n) % len(self.buffer)
        if end > self.idx:
            self.buffer[self.idx:end] = audio
        else:
            self.buffer[self.idx:] = audio[:len(self.buffer)-self.idx]
            self.buffer[:end] = audio[len(self.buffer)-self.idx:]
        self.idx = end

# BAD - Unbounded list growth
chunks = []
chunks.append(audio)  # Memory leak over time
```

---

## 7. Implementation Patterns

### Pattern 1: Secure Faster Whisper Setup

```python
from faster_whisper import Whis## 6. Performance Patterns

## 6. Performance Patterns

📚 **For complete details**: See `references/performance-patterns.md`

---
ext)

        # Credit card numbers
        text = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD]', text)

        return text
```

---

## 8. Security Standards

**Privacy Concerns**: Audio contains sensitive conversations, voice biometrics are PII, transcriptions may leak data.

**Required Mitigations**:
```python
# Always delete after processing
def transcribe_and_delete(audio_path: str) -> str:
    try:
        return engine.transcribe(audio_path)
    finally:
        Path(audio_path).unlink(missing_ok=True)

# Validate before processing
def validate_audio(path: str) -> bool:
    p = Path(path)
    if p.stat().st_size > 50 * 1024 * 1024:
        raise ValidationError("File too large")
    if p.suffix.lower() not in {'.wav', '.mp3', '.flac'}:
        raise ValidationError("Invalid format")
    return True
```

---

## 9. Common Mistakes

### NEVER: Keep Audio Files

```python
# BAD - Audio persists
def transcribe(path):
    return model.transcribe(path)  # File remains

# GOOD - Delete after use
def transcribe(path):
    try:
        return model.transcribe(path)
    finally:
        Path(path).unlink()
```

### NEVER: Log Transcription Content

```python
# BAD - Logs sensitive content
logger.info(f"Transcribed: {text}")

# GOOD - Log metadata only
logger.info("stt.complete", word_count=len(text.split()))
```

---

## 10. Pre-Implementation Checklist

### Phase 1: Before Writing Code

- [ ] Read SKILL.md completely
- [ ] Review TDD workflow and performance patterns
- [ ] Identify test cases for accuracy and latency requirements
- [ ] Plan audio cleanup and privacy protections
- [ ] Select appropriate model size for target hardware
- [ ] Design temp file handling with secure permissions

### Phase 2: During Implementation

- [ ] Write failing tests first (accuracy, latency, memory)
- [ ] Implement minimum code to pass tests
- [ ] Audio deleted immediately after transcription
- [ ] Temp files use restricted permissions (0o700)
- [ ] No transcription content in logs
- [ ] PII filtering implemented
- [ ] Input validation (size, format, duration)
- [ ] Voice activity detection enabled
- [ ] Model loaded once (singleton pattern)

### Phase 3: Before Committing

- [ ] All tests pass: `pytest tests/test_stt_engine.py -v`
- [ ] Coverage above 80%: `pytest --cov=jarvis.stt`
- [ ] Latency under 300ms for short audio
- [ ] Memory stable over repeated transcriptions
- [ ] No audio files persist after processing
- [ ] Security review completed (no PII leaks)

---

## 11. Summary

Your goal is to create STT systems tha## 7. Implementation Patterns

## 7. Implementation Patterns

📚 **For complete details**: See `references/implementation-patterns.md`

---
