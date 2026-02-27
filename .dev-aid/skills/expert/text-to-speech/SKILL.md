---
name: text-to-speech
version: 2.0.0
description: "Text-to-speech with Kokoro TTS for local voice synthesis, SSML processing, and audio generation. Use when implementing voice output, speech synthesis, or TTS pipelines. Do NOT use for cloud TTS APIs (use cloud-api-integration)."
risk_level: MEDIUM
token_budget: 4000
---
# Text To Speech - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.2 Security Patterns (security rules)

**CWE-79: SSML Injection**
- Do not: `<speak>${userText}</speak>` without escaping
- Instead: Escape SSML special characters, validate SSML structure

**CWE-200: Voice Cloning Consent**
- Do not: Clone voices without explicit consent
- Instead: Consent for custom voices, watermarking if applicable

---

## 1. Security Principles

### 1.1 Text Input Sanitization (CWE-79, CWE-94)

**Principle:** Text input may contain malicious content. Sanitize before synthesis.

```python
# ❌ WRONG - Synthesizing arbitrary input
def speak(text: str):
    model.synthesize(text)

# ✅ CORRECT - Sanitize and validate input
import re
from dataclasses import dataclass

@dataclass
class TTSConfig:
    max_length: int = 5000
    allowed_chars_pattern: str = r"[\w\s.,!?;:'\"-]+"

def sanitize_text(text: str, config: TTSConfig = TTSConfig()) -> str:
    """Sanitize text for TTS synthesis."""
    # Limit length
    if len(text) > config.max_length:
        text = text[:config.max_length]

    # Remove control characters
    text = "".join(c for c in text if c.isprintable() or c in "\n\t")

    # Normalize whitespace
    text = " ".join(text.split())

    # Remove potentially harmful patterns (SSML injection if supported)
    text = re.sub(r"<[^>]+>", "", text)

    return text.strip()
```

### 1.2 Resource Management (CWE-400)

**Principle:** TTS models consume significant memory. Implement proper resource limits.

```python
# ❌ WRONG - Loading model per request
def synthesize(text: str) -> bytes:
    model = load_model("kokoro-v0.19")  # ~1GB per request!
    return model(text)

# ✅ CORRECT - Singleton model with concurrency control
import threading
from contextlib import contextmanager
from dataclasses import dataclass

@dataclass
class ModelConfig:
    model_name: str = "kokoro-v0.19"
    device: str = "auto"  # auto, cpu, cuda
    max_concurrent: int = 1

class TTSModelPool:
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

        import torch

        self._config = config
        self._semaphore = threading.Semaphore(config.max_concurrent)

        # Determine device
        if config.device == "auto":
            self._device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self._device = config.device

        # Load model once
        from kokoro import KokoroTTS
        self._model = KokoroTTS(config.model_name)
        self._model.to(self._device)

        self._initialized = True

    @contextmanager
    def acquire(self):
        """Acquire model for synthesis with concurrency control."""
        if not self._initialized:
            raise RuntimeError("Model pool not initialized")

        acquired = self._semaphore.acquire(timeout=30)
        if not acquired:
            raise TimeoutError("Could not acquire model within timeout")

        try:
            yield self._model
        finally:
            self._semaphore.release()
```

### 1.3 Output Validation (CWE-20)

**Principle:** Validate generated audio before returning to prevent corrupted output.

```python
# ❌ WRONG - No output validation
def synthesize(text: str) -> np.ndarray:
    return model.generate(text)

# ✅ CORRECT - Validate output
import numpy as np
from dataclasses import dataclass

@dataclass
class AudioValidation:
    valid: bool
    error: str | None = None
    duration_seconds: float = 0
    sample_rate: int = 0

def validate_audio(
    audio: np.ndarray,
    sample_rate: int,
    max_duration: float = 300.0,
) -> AudioValidation:
    """Validate generated audio."""

    # Check for empty output
    if audio.size == 0:
        return AudioValidation(False, "Empty audio generated")

    # Check for NaN or Inf
    if np.any(np.isnan(audio)) or np.any(np.isinf(audio)):
        return AudioValidation(False, "Audio contains NaN or Inf values")

    # Check duration
    duration = len(audio) / sample_rate
    if duration > max_duration:
        return AudioValidation(False, f"Audio too long: {duration:.1f}s > {max_duration}s")

    # Check amplitude (should be normalized)
    max_amplitude = np.max(np.abs(audio))
    if max_amplitude > 1.0:
        return AudioValidation(False, f"Audio not normalized: max={max_amplitude:.2f}")

    # Check for silence (possible generation failure)
    rms = np.sqrt(np.mean(audio**2))
    if rms < 0.001:
        return AudioValidation(False, "Audio is silent (RMS < 0.001)")

    return AudioValidation(
        valid=True,
        duration_seconds=duration,
        sample_rate=sample_rate,
    )
```

---

## 2. Version Requirements

```
# Kokoro TTS (recommended)
kokoro>=0.3.0
# Audio processing
numpy>=1.24.0
soundfile>=0.12.0
sounddevice>=0.4.6
# Resampling
librosa>=0.10.0
# Optional: GPU acceleration
torch>=2.0.0
```

---

## 3. Code Patterns

### WHEN implementing TTS synthesis, use proper configuration

```python
# ❌ WRONG - Hardcoded parameters
def speak(text: str):
    audio = model.generate(text, speed=1.0)
    sd.play(audio, 24000)

# ✅ CORRECT - Configurable synthesis
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
import soundfile as sf

@dataclass
class VoiceConfig:
    voice_id: str = "af"  # Kokoro voice
    speed: float = 1.0
    pitch: float = 1.0
    sample_rate: int = 24000

@dataclass
class SynthesisResult:
    audio: np.ndarray
    sample_rate: int
    duration_seconds: float
    text: str
    voice: str

class KokoroSynthesizer:
    def __init__(self, pool: TTSModelPool):
        self._pool = pool

    def synthesize(
        self,
        text: str,
        config: VoiceConfig = VoiceConfig(),
    ) -> SynthesisResult:
        """Synthesize text to speech."""

        # Sanitize input
        clean_text = sanitize_text(text)
        if not clean_text:
            raise ValueError("Text is empty after sanitization")

        with self._pool.acquire() as model:
            # Generate audio
            audio, sample_rate = model.generate(
                clean_text,
                voice=config.voice_id,
                speed=config.speed,
            )

            # Validate output
            validation = validate_audio(audio, sample_rate)
            if not validation.valid:
                raise RuntimeError(f"Audio generation failed: {validation.error}")

            return SynthesisResult(
                audio=audio,
                sample_rate=sample_rate,
                duration_seconds=validation.duration_seconds,
                text=clean_text,
                voice=config.voice_id,
            )

    def synthesize_to_file(
        self,
        text: str,
        output_path: Path,
        config: VoiceConfig = VoiceConfig(),
    ) -> SynthesisResult:
        """Synthesize and save to file."""
        result = self.synthesize(text, config)

        # Save with proper format
        sf.write(
            str(output_path),
            result.audio,
            result.sample_rate,
            subtype="PCM_16",
        )

        return result
```

### WHEN streaming audio output, use buffered playback

```python
# ❌ WRONG - Blocking playback
def speak(text: str):
    audio = synthesize(text)
    sd.play(audio, 24000)
    sd.wait()  # Blocks entire thread

# ✅ CORRECT - Non-blocking streaming playback
import queue
import threading
import sounddevice as sd
import numpy as np
from dataclasses import dataclass

@dataclass
class AudioChunk:
    data: np.ndarray
    is_last: bool = False

class StreamingPlayer:
    def __init__(self, sample_rate: int = 24000, buffer_size: int = 1024):
        self._sample_rate = sample_rate
        self._buffer_size = buffer_size
        self._queue: queue.Queue[AudioChunk | None] = queue.Queue(maxsize=10)
        self._stream: sd.OutputStream | None = None
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def _audio_callback(self, outdata, frames, time, status):
        """Callback for sounddevice stream."""
        try:
            chunk = self._queue.get_nowait()
            if chunk is None or chunk.is_last:
                outdata.fill(0)
                raise sd.CallbackStop()

            # Handle chunk size mismatch
            if len(chunk.data) < frames:
                outdata[:len(chunk.data), 0] = chunk.data
                outdata[len(chunk.data):, 0] = 0
            else:
                outdata[:, 0] = chunk.data[:frames]

        except queue.Empty:
            outdata.fill(0)

    def start(self):
        """Start the audio stream."""
        self._stop_event.clear()
        self._stream = sd.OutputStream(
            samplerate=self._sample_rate,
            channels=1,
            callback=self._audio_callback,
            blocksize=self._buffer_size,
        )
        self._stream.start()

    def play_chunk(self, audio: np.ndarray, is_last: bool = False):
        """Queue audio chunk for playback."""
        self._queue.put(AudioChunk(audio, is_last))

    def stop(self):
        """Stop playback and cleanup."""
        self._stop_event.set()
        self._queue.put(None)
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def wait(self):
        """Wait for playback to complete."""
        self._queue.join()
```

### WHEN handling long text, use sentence-based chunking

```python
# ❌ WRONG - Synthesizing entire text at once
def speak_long_text(text: str):
    # May OOM or produce poor quality for long text
    audio = model.generate(text)
    return audio

# ✅ CORRECT - Chunk by sentences for quality and streaming
import re
from typing import Iterator

def chunk_text_by_sentences(
    text: str,
    max_chunk_chars: int = 500,
) -> Iterator[str]:
    """Split text into sentence-based chunks."""

    # Split on sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+', text)

    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if current_length + len(sentence) > max_chunk_chars and current_chunk:
            yield " ".join(current_chunk)
            current_chunk = []
            current_length = 0

        current_chunk.append(sentence)
        current_length += len(sentence) + 1

    if current_chunk:
        yield " ".join(current_chunk)

class ChunkedSynthesizer:
    def __init__(self, synthesizer: KokoroSynthesizer):
        self._synth = synthesizer

    def synthesize_long(
        self,
        text: str,
        config: VoiceConfig = VoiceConfig(),
    ) -> Iterator[SynthesisResult]:
        """Synthesize long text in chunks."""
        for chunk in chunk_text_by_sentences(text):
            yield self._synth.synthesize(chunk, config)

    def synthesize_long_combined(
        self,
        text: str,
        config: VoiceConfig = VoiceConfig(),
    ) -> SynthesisResult:
        """Synthesize and combine all chunks."""
        chunks = list(self.synthesize_long(text, config))

        if not chunks:
            raise ValueError("No audio generated")

        # Concatenate with small silence between chunks
        silence = np.zeros(int(0.1 * chunks[0].sample_rate))
        combined = np.concatenate([
            np.concatenate([c.audio, silence]) for c in chunks
        ])

        return SynthesisResult(
            audio=combined,
            sample_rate=chunks[0].sample_rate,
            duration_seconds=len(combined) / chunks[0].sample_rate,
            text=text,
            voice=config.voice_id,
        )
```

### WHEN supporting multiple voices, use voice manager

```python
# ❌ WRONG - Hardcoded voice selection
def speak(text: str, voice: str = "default"):
    return model.generate(text, voice=voice)

# ✅ CORRECT - Voice registry with validation
from dataclasses import dataclass
from typing import ClassVar

@dataclass
class Voice:
    id: str
    name: str
    language: str
    gender: str
    sample_rate: int = 24000

class VoiceRegistry:
    # Kokoro available voices
    VOICES: ClassVar[dict[str, Voice]] = {
        "af": Voice("af", "Default American Female", "en-US", "female"),
        "af_bella": Voice("af_bella", "Bella", "en-US", "female"),
        "af_sarah": Voice("af_sarah", "Sarah", "en-US", "female"),
        "am_adam": Voice("am_adam", "Adam", "en-US", "male"),
        "am_michael": Voice("am_michael", "Michael", "en-US", "male"),
        "bf_emma": Voice("bf_emma", "Emma", "en-GB", "female"),
        "bm_george": Voice("bm_george", "George", "en-GB", "male"),
    }

    @classmethod
    def get(cls, voice_id: str) -> Voice:
        if voice_id not in cls.VOICES:
            raise ValueError(
                f"Unknown voice: {voice_id}. "
                f"Available: {list(cls.VOICES.keys())}"
            )
        return cls.VOICES[voice_id]

    @classmethod
    def list_by_language(cls, language: str) -> list[Voice]:
        return [v for v in cls.VOICES.values() if v.language == language]

    @classmethod
    def list_by_gender(cls, gender: str) -> list[Voice]:
        return [v for v in cls.VOICES.values() if v.gender == gender]
```

---

## 4. Anti-Patterns

Do not:
- Load TTS model per request (use singleton pool)
- Synthesize unsanitized user input
- Block main thread during synthesis
- Skip output validation (NaN, silence, duration)
- Synthesize very long text without chunking
- Ignore sample rate mismatches when combining audio
- Store generated audio without cleanup policy

---

## 5. Testing

```python
import pytest
import numpy as np
from pathlib import Path
from text_to_speech import (
    sanitize_text,
    validate_audio,
    TTSModelPool,
# ... (additional test cases follow same pattern)
```

---

## 6. Pre-Generation Checklist

Before generating TTS code:

- [ ] Input sanitization: Control chars, SSML tags, length limits
- [ ] Model pooling: Singleton pattern for model management
- [ ] Concurrency control: Semaphore limiting inference
- [ ] Output validation: Check for NaN, silence, duration
- [ ] Chunking: Long text split by sentences
- [ ] Voice validation: Registry with known voices
- [ ] Resource cleanup: Audio file cleanup policy
- [ ] Streaming support: Non-blocking playback option

---
