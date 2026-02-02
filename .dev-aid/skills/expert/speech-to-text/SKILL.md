---
name: speech-to-text
version: 2.0.0
description: "Speech-to-text integration with Faster Whisper for accurate transcription and real-time processing."
risk_level: MEDIUM
---

# Speech To Text - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-200: Audio Recording Privacy**
- NEVER: Record without explicit user consent/indicator
- ALWAYS: Clear recording indicator, consent flow, secure storage

**CWE-312: Transcript Storage**
- NEVER: Store transcripts with PII unencrypted
- ALWAYS: Encrypt transcripts, retention policies, user deletion rights

### 0.3 Risk Level: MEDIUM

**Verification requirements for MEDIUM risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 Audio Input Validation (CWE-20)

**Principle:** Audio files can be crafted maliciously. Validate format and size before processing.

```python
# ❌ WRONG - Processing arbitrary audio files
def transcribe(audio_path: str) -> str:
    model = whisper.load_model("base")
    return model.transcribe(audio_path)["text"]

# ✅ CORRECT - Validate audio before processing
import os
import wave
import struct
from pathlib import Path
from dataclasses import dataclass

MAX_AUDIO_SIZE_MB = 100
MAX_DURATION_SECONDS = 600  # 10 minutes
ALLOWED_FORMATS = {".wav", ".mp3", ".m4a", ".ogg", ".flac"}

@dataclass
class AudioValidationResult:
    valid: bool
    error: str | None = None
    duration_seconds: float = 0
    sample_rate: int = 0
    channels: int = 0

def validate_audio_file(path: Path) -> AudioValidationResult:
    """Validate audio file before processing."""

    # Check file exists and extension
    if not path.exists():
        return AudioValidationResult(False, "File not found")

    if path.suffix.lower() not in ALLOWED_FORMATS:
        return AudioValidationResult(False, f"Invalid format: {path.suffix}")

    # Check file size
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > MAX_AUDIO_SIZE_MB:
        return AudioValidationResult(False, f"File too large: {size_mb:.1f}MB > {MAX_AUDIO_SIZE_MB}MB")

    # Get audio metadata
    try:
        import soundfile as sf
        info = sf.info(str(path))
        duration = info.duration
        sample_rate = info.samplerate
        channels = info.channels
    except Exception as e:
        return AudioValidationResult(False, f"Cannot read audio: {e}")

    if duration > MAX_DURATION_SECONDS:
        return AudioValidationResult(
            False,
            f"Audio too long: {duration:.0f}s > {MAX_DURATION_SECONDS}s"
        )

    return AudioValidationResult(
        valid=True,
        duration_seconds=duration,
        sample_rate=sample_rate,
        channels=channels,
    )
```

### 1.2 Resource Management (CWE-400)

**Principle:** Whisper models consume significant GPU/CPU memory. Implement proper resource limits.

```python
# ❌ WRONG - Loading model per request
def transcribe_request(audio_path: str) -> str:
    model = whisper.load_model("large")  # 10GB VRAM per request!
    return model.transcribe(audio_path)["text"]

# ✅ CORRECT - Singleton model with resource management
import threading
from contextlib import contextmanager
from dataclasses import dataclass
import torch

@dataclass
class ModelConfig:
    model_size: str = "base"
    device: str = "auto"
    compute_type: str = "float16"
    cpu_threads: int = 4

class WhisperModelPool:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, config: ModelConfig | None = None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def initialize(self, config: ModelConfig):
        if self._initialized:
            return

        self._config = config
        self._model_lock = threading.Semaphore(1)  # Single concurrent inference

        # Determine device
        if config.device == "auto":
            self._device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self._device = config.device

        # Load model once
        from faster_whisper import WhisperModel
        self._model = WhisperModel(
            config.model_size,
            device=self._device,
            compute_type=config.compute_type if self._device == "cuda" else "int8",
            cpu_threads=config.cpu_threads,
        )

        self._initialized = True

    @contextmanager
    def acquire(self):
        """Acquire model for inference with concurrency control."""
        if not self._initialized:
            raise RuntimeError("Model pool not initialized")

        acquired = self._model_lock.acquire(timeout=30)
        if not acquired:
            raise TimeoutError("Could not acquire model within timeout")

        try:
            yield self._model
        finally:
            self._model_lock.release()

# Global pool
_pool = WhisperModelPool()

def get_model_pool() -> WhisperModelPool:
    return _pool
```

### 1.3 Output Sanitization (CWE-79)

**Principle:** Transcribed text may contain malicious content if audio was crafted. Sanitize outputs.

---

## 2. Version Requirements

```
# Faster Whisper (recommended for production)
faster-whisper>=1.0.0
# Audio processing
soundfile>=0.12.0
numpy>=1.24.0
# Optional: Original Whisper
openai-whisper>=20231117
# VAD for chunking
silero-vad>=4.0
```

---

## 3. Code Patterns

### WHEN transcribing with Faster Whisper, use proper configuration

```python
# ❌ WRONG - Default settings without optimization
model = WhisperModel("large-v3")
segments, info = model.transcribe(audio_path)
text = " ".join(s.text for s in segments)

# ✅ CORRECT - Production-ready transcription
from faster_whisper import WhisperModel
from dataclasses import dataclass, field
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class TranscriptionConfig:
    language: str | None = None  # Auto-detect if None
    beam_size: int = 5
    best_of: int = 5
    temperature: float = 0.0
    vad_filter: bool = True
    vad_min_silence_duration_ms: int = 500
    word_timestamps: bool = False
    initial_prompt: str | None = None

@dataclass
class TranscriptionSegment:
    start: float
    end: float
    text: str
    confidence: float
    words: list[dict] = field(default_factory=list)

@dataclass
class TranscriptionResult:
    text: str
    segments: list[TranscriptionSegment]
    language: str
    language_probability: float
    duration: float

class FasterWhisperTranscriber:
    def __init__(self, model_pool: WhisperModelPool):
        self._pool = model_pool

    def transcribe(
        self,
        audio_path: Path,
        config: TranscriptionConfig = TranscriptionConfig(),
    ) -> TranscriptionResult:
        """Transcribe audio file with production settings."""

        # Validate input
        validation = validate_audio_file(audio_path)
        if not validation.valid:
            raise ValueError(f"Invalid audio: {validation.error}")

        with self._pool.acquire() as model:
            segments_gen, info = model.transcribe(
                str(audio_path),
                language=config.language,
                beam_size=config.beam_size,
                best_of=config.best_of,
                temperature=config.temperature,
                vad_filter=config.vad_filter,
                vad_parameters={
                    "min_silence_duration_ms": config.vad_min_silence_duration_ms,
                },
                word_timestamps=config.word_timestamps,
                initial_prompt=config.initial_prompt,
            )

            segments = []
            full_text_parts = []

            for segment in segments_gen:
                segments.append(TranscriptionSegment(
                    start=segment.start,
                    end=segment.end,
                    text=segment.text.strip(),
                    confidence=segment.avg_logprob,
                    words=[
                        {"word": w.word, "start": w.start, "end": w.end, "probability": w.probability}
                        for w in (segment.words or [])
                    ],
                ))
                full_text_parts.append(segment.text.strip())

            return TranscriptionResult(
                text=" ".join(full_text_parts),
                segments=segments,
                language=info.language,
                language_probability=info.language_probability,
                duration=info.duration,
            )
```

### WHEN processing real-time audio, use VAD chunking

```python
# ❌ WRONG - Processing entire stream without chunking
def transcribe_stream(audio_stream):
    buffer = []
    for chunk in audio_stream:
        buffer.append(chunk)
    return transcribe(np.concatenate(buffer))

# ✅ CORRECT - VAD-based chunking for real-time
import numpy as np
from dataclasses import dataclass
from collections import deque
import torch

@dataclass
class VADConfig:
    sample_rate: int = 16000
    frame_duration_ms: int = 30
    silence_threshold: float = 0.5
    min_speech_duration_ms: int = 250
    max_speech_duration_ms: int = 30000
    padding_ms: int = 300

class SileroVAD:
    def __init__(self, config: VADConfig = VADConfig()):
        self.config = config
        self._model, self._utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
        )
        self._model.eval()

    def is_speech(self, audio_chunk: np.ndarray) -> float:
        """Returns speech probability for audio chunk."""
        tensor = torch.from_numpy(audio_chunk).float()
        with torch.no_grad():
            return self._model(tensor, self.config.sample_rate).item()

class StreamingTranscriber:
    def __init__(
        self,
        transcriber: FasterWhisperTranscriber,
        vad: SileroVAD,
        config: VADConfig = VADConfig(),
    ):
        self._transcriber = transcriber
        self._vad = vad
        self._config = config

        self._buffer = deque(maxlen=self._max_frames())
        self._speech_frames: list[np.ndarray] = []
        self._is_speaking = False
        self._silence_frames = 0

    def _max_frames(self) -> int:
        return int(
            self._config.max_speech_duration_ms /
            self._config.frame_duration_ms
        )

    def process_frame(self, frame: np.ndarray) -> TranscriptionResult | None:
        """Process audio frame, return transcription when speech ends."""

        speech_prob = self._vad.is_speech(frame)
        is_speech = speech_prob > self._config.silence_threshold

        if is_speech:
            self._silence_frames = 0
            if not self._is_speaking:
                # Speech started - include padding
                self._speech_frames = list(self._buffer)
                self._is_speaking = True
            self._speech_frames.append(frame)
        else:
            self._silence_frames += 1

            if self._is_speaking:
                # Add padding frames
                self._speech_frames.append(frame)

                silence_ms = self._silence_frames * self._config.frame_duration_ms

                if silence_ms > self._config.padding_ms:
                    # Speech ended - transcribe
                    return self._transcribe_speech()

        self._buffer.append(frame)
        return None

    def _transcribe_speech(self) -> TranscriptionResult | None:
        """Transcribe accumulated speech frames."""
        if not self._speech_frames:
            return None

        speech_ms = len(self._speech_frames) * self._config.frame_duration_ms
        if speech_ms < self._config.min_speech_duration_ms:
            self._reset()
            return None

        audio = np.concatenate(self._speech_frames)

        # Save to temp file for transcription
        import tempfile
        import soundfile as sf

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            sf.write(f.name, audio, self._config.sample_rate)
            result = self._transcriber.transcribe(Path(f.name))

        self._reset()
        return result

    def _reset(self):
        self._speech_frames = []
        self._is_speaking = False
        self._silence_frames = 0

    def flush(self) -> TranscriptionResult | None:
        """Flush any remaining speech."""
        if self._is_speaking and self._speech_frames:
            return self._transcribe_speech()
        return None
```

### WHEN handling multiple languages, use detection with confidence

```python
# ❌ WRONG - Assuming single language
result = model.transcribe(audio, language="en")

# ✅ CORRECT - Language detection with fallback
from dataclasses import dataclass

@dataclass
class LanguageDetectionResult:
    language: str
    confidence: float
    is_confident: bool

def detect_language(
    audio_path: Path,
    model_pool: WhisperModelPool,
    confidence_threshold: float = 0.7,
) -> LanguageDetectionResult:
    """Detect language with confidence scoring."""

    with model_pool.acquire() as model:
        # Use first 30 seconds for detection
        segments, info = model.transcribe(
            str(audio_path),
            language=None,  # Auto-detect
            beam_size=1,    # Fast detection
            best_of=1,
        )
        # Consume generator to get info
        _ = list(segments)

    return LanguageDetectionResult(
        language=info.language,
        confidence=info.language_probability,
        is_confident=info.language_probability >= confidence_threshold,
    )

def transcribe_multilingual(
    audio_path: Path,
    model_pool: WhisperModelPool,
    preferred_language: str | None = None,
) -> TranscriptionResult:
    """Transcribe with language detection and validation."""

    # Detect language first
    detection = detect_language(audio_path, model_pool)

    # Use detected language if confident, otherwise prefer specified
    if detection.is_confident:
        language = detection.language
    elif preferred_language:
        language = preferred_language
    else:
        language = detection.language  # Best guess

    logger.info(
        f"Using language: {language} "
        f"(detected: {detection.language} @ {detection.confidence:.0%})"
    )

    transcriber = FasterWhisperTranscriber(model_pool)
    return transcriber.transcribe(
        audio_path,
        TranscriptionConfig(language=language),
    )
```

---

## 4. Anti-Patterns

**NEVER:**
- Load Whisper models per-request (use singleton pool)
- Process audio files without size/duration validation
- Skip VAD for real-time streaming
- Assume single language without detection
- Block on transcription in async contexts
- Store raw audio longer than needed (privacy)
- Use `large` model without GPU (too slow)

---

## 5. Testing

```python
import pytest
import numpy as np
from pathlib import Path
from speech_to_text import (
    validate_audio_file,
    FasterWhisperTranscriber,
    WhisperModelPool,
    ModelConfig,
    TranscriptionConfig,
)

class TestAudioValidation:

    def test_rejects_oversized_file(self, tmp_path):
        """Should reject files over size limit."""
        large_file = tmp_path / "large.wav"
        # Create file larger than limit
        large_file.write_bytes(b"\x00" * (101 * 1024 * 1024))

        result = validate_audio_file(large_file)
        assert not result.valid
        assert "too large" in result.error.lower()

    def test_rejects_invalid_format(self, tmp_path):
        """Should reject unsupported formats."""
        bad_file = tmp_path / "audio.exe"
        bad_file.write_bytes(b"not audio")

        result = validate_audio_file(bad_file)
        assert not result.valid
        assert "invalid format" in result.error.lower()

    def test_accepts_valid_wav(self, tmp_path):
        """Should accept valid WAV files."""
        import soundfile as sf

        wav_file = tmp_path / "test.wav"
        audio = np.random.randn(16000).astype(np.float32)  # 1 second
        sf.write(str(wav_file), audio, 16000)

        result = validate_audio_file(wav_file)
        assert result.valid
        assert 0.9 < result.duration_seconds < 1.1

class TestModelPool:

    def test_singleton_pattern(self):
        """Model pool should be singleton."""
        pool1 = WhisperModelPool()
        pool2 = WhisperModelPool()
        assert pool1 is pool2

    def test_concurrency_control(self):
        """Should limit concurrent model access."""
        pool = WhisperModelPool()
        pool.initialize(ModelConfig(model_size="tiny"))

        # First acquire should succeed
        with pool.acquire() as model:
            assert model is not None

            # Second acquire should timeout
            with pytest.raises(TimeoutError):
                with pool.acquire():
                    pass

class TestTranscription:

    @pytest.fixture
    def model_pool(self):
        pool = WhisperModelPool()
        pool.initialize(ModelConfig(model_size="tiny"))
        return pool

    def test_transcription_result_structure(self, model_pool, tmp_path):
        """Transcription result should have expected structure."""
        import soundfile as sf

        # Create test audio with speech-like pattern
        wav_file = tmp_path / "test.wav"
        audio = np.random.randn(16000 * 3).astype(np.float32)
        sf.write(str(wav_file), audio, 16000)

        transcriber = FasterWhisperTranscriber(model_pool)
        result = transcriber.transcribe(wav_file)

        assert hasattr(result, "text")
        assert hasattr(result, "segments")
        assert hasattr(result, "language")
        assert result.duration > 0
```

---

## 6. Pre-Generation Checklist

**BEFORE generating speech-to-text code:**

- [ ] Input validation: Audio size/duration/format checked
- [ ] Model pooling: Singleton pattern for model management
- [ ] Concurrency: Semaphore limiting concurrent inference
- [ ] VAD integration: Using VAD for streaming/chunking
- [ ] Language detection: Confidence-based language selection
- [ ] Resource limits: Memory/GPU constraints respected
- [ ] Privacy: Raw audio not retained unnecessarily
- [ ] Timeout handling: Long transcriptions have timeouts
