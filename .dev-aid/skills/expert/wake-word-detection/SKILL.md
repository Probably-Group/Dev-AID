---
name: wake-word-detection
version: 2.0.0
description: "Wake word detection with openWakeWord for local keyword spotting and voice-activated triggers. Use when implementing wake words, keyword detection, or always-on listening. Do NOT use for full voice assistants or cloud wake word services."
risk_level: MEDIUM
token_budget: 4500
---
# Wake Word Detection - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.2 Security Patterns (security rules)

**CWE-200: Always-On Listening Privacy**
- Do not: Process/store audio beyond wake word detection
- Instead: Local-only processing, clear privacy indicators

**CWE-287: Wake Word Spoofing**
- Do not: Single wake word as authentication
- Instead: Wake word triggers auth flow, not direct actions

---

## 1. Security Principles

### 1.1 Audio Privacy (CWE-200, CWE-312)

**Principle:** Audio contains sensitive data. Never store raw audio longer than needed.

```python
# ❌ WRONG - Storing all audio indefinitely
class WakeWordDetector:
    def __init__(self):
        self.audio_history = []  # Stores everything forever!

    def process(self, audio_chunk):
        self.audio_history.append(audio_chunk)
        return self.model.predict(audio_chunk)

# ✅ CORRECT - Minimal audio retention with secure cleanup
from dataclasses import dataclass
from collections import deque
import numpy as np
import secrets

@dataclass
class PrivacyConfig:
    max_buffer_seconds: float = 2.0
    clear_on_detection: bool = True
    secure_wipe: bool = True

class SecureAudioBuffer:
    def __init__(self, sample_rate: int, config: PrivacyConfig):
        self._sample_rate = sample_rate
        self._config = config
        self._max_samples = int(config.max_buffer_seconds * sample_rate)
        self._buffer = deque(maxlen=self._max_samples)

    def add(self, chunk: np.ndarray) -> None:
        for sample in chunk:
            self._buffer.append(sample)

    def get_audio(self) -> np.ndarray:
        return np.array(self._buffer, dtype=np.float32)

    def clear(self) -> None:
        if self._config.secure_wipe:
            # Overwrite with random data before clearing
            for i in range(len(self._buffer)):
                self._buffer[i] = secrets.randbelow(2**16) / 2**15 - 1
        self._buffer.clear()
```

### 1.2 Model Integrity (CWE-494)

**Principle:** Verify model files haven't been tampered with.

```python
# ❌ WRONG - Loading models without verification
def load_model(path: str):
    return onnxruntime.InferenceSession(path)

# ✅ CORRECT - Verify model integrity before loading
import hashlib
from pathlib import Path
from dataclasses import dataclass

@dataclass
class ModelManifest:
    path: str
    sha256: str
    version: str

TRUSTED_MODELS: dict[str, ModelManifest] = {
    "hey_jarvis": ModelManifest(
        path="models/hey_jarvis_v0.6.0.onnx",
        sha256="a1b2c3d4e5f6...",  # Actual hash from release
        version="0.6.0",
    ),
}

def verify_model_integrity(model_path: Path, expected_hash: str) -> bool:
    """Verify model file hasn't been tampered with."""
    sha256 = hashlib.sha256()
    with open(model_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest() == expected_hash

def load_verified_model(model_name: str) -> ort.InferenceSession:
    """Load model only after integrity verification."""
    if model_name not in TRUSTED_MODELS:
        raise ValueError(f"Unknown model: {model_name}")

    manifest = TRUSTED_MODELS[model_name]
    model_path = Path(manifest.path)

    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    if not verify_model_integrity(model_path, manifest.sha256):
        raise SecurityError(f"Model integrity check failed: {model_path}")

    return ort.InferenceSession(str(model_path))
```

### 1.3 Resource Limits (CWE-400)

**Principle:** Prevent resource exhaustion from audio processing.

```python
# ❌ WRONG - Unbounded processing
def process_audio_stream(stream):
    while True:
        chunk = stream.read()
        result = model.predict(chunk)

# ✅ CORRECT - Resource-limited processing
import asyncio
from dataclasses import dataclass

@dataclass
class ResourceConfig:
    max_concurrent_inferences: int = 1
    inference_timeout_ms: int = 100
    max_queue_size: int = 10
    chunk_size_samples: int = 1280  # 80ms at 16kHz

class ResourceLimitedDetector:
    def __init__(self, model, config: ResourceConfig):
        self._model = model
        self._config = config
        self._semaphore = asyncio.Semaphore(config.max_concurrent_inferences)
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=config.max_queue_size)

    async def process_chunk(self, chunk: np.ndarray) -> float | None:
        """Process audio chunk with resource limits."""
        # Drop if queue full (prevent backpressure)
        try:
            self._queue.put_nowait(chunk)
        except asyncio.QueueFull:
            return None  # Drop frame

        async with self._semaphore:
            try:
                chunk = await asyncio.wait_for(
                    self._queue.get(),
                    timeout=self._config.inference_timeout_ms / 1000,
                )
                return self._model.predict(chunk)
            except asyncio.TimeoutError:
                return None
```

---

## 2. Version Requirements

```
openwakeword>=0.6.0
numpy>=1.24.0
sounddevice>=0.4.6
onnxruntime>=1.16.0
# Optional: GPU support
onnxruntime-gpu>=1.16.0
```

---

## 3. Code Patterns

### WHEN setting up openWakeWord, use proper configuration

```python
# ❌ WRONG - Default configuration without tuning
from openwakeword import Model

model = Model()
while True:
    audio = mic.read()
    prediction = model.predict(audio)

# ✅ CORRECT - Production-ready configuration
from openwakeword import Model
from openwakeword.utils import download_models
from dataclasses import dataclass
import numpy as np
import logging

logger = logging.getLogger(__name__)

@dataclass
class WakeWordConfig:
    model_names: list[str]
    threshold: float = 0.5
    trigger_level: int = 3  # Consecutive detections required
    sample_rate: int = 16000
    chunk_size_ms: int = 80
    vad_threshold: float = 0.3
    inference_framework: str = "onnx"

class OpenWakeWordDetector:
    def __init__(self, config: WakeWordConfig):
        self._config = config
        self._chunk_size = int(config.sample_rate * config.chunk_size_ms / 1000)

        # Download models if needed
        for model_name in config.model_names:
            download_models(model_name)

        # Initialize model with custom settings
        self._model = Model(
            wakeword_models=config.model_names,
            inference_framework=config.inference_framework,
        )

        # Tracking for trigger level
        self._detection_counts: dict[str, int] = {
            name: 0 for name in config.model_names
        }

    def process(self, audio_chunk: np.ndarray) -> dict[str, bool]:
        """Process audio and return triggered wake words."""
        # Ensure correct shape and type
        if audio_chunk.dtype != np.int16:
            audio_chunk = (audio_chunk * 32767).astype(np.int16)

        # Get predictions
        predictions = self._model.predict(audio_chunk)

        triggered = {}
        for model_name in self._config.model_names:
            score = predictions.get(model_name, 0)

            if score >= self._config.threshold:
                self._detection_counts[model_name] += 1
            else:
                self._detection_counts[model_name] = 0

            # Trigger only after consecutive detections
            triggered[model_name] = (
                self._detection_counts[model_name] >= self._config.trigger_level
            )

            if triggered[model_name]:
                logger.info(f"Wake word detected: {model_name} (score: {score:.3f})")
                self._detection_counts[model_name] = 0  # Reset after trigger

        return triggered

    def reset(self) -> None:
        """Reset detection state."""
        self._model.reset()
        for key in self._detection_counts:
            self._detection_counts[key] = 0
```

### WHEN streaming audio input, handle device lifecycle

```python
# ❌ WRONG - No error handling, no cleanup
import sounddevice as sd

stream = sd.InputStream(samplerate=16000, channels=1)
stream.start()
while True:
    audio, _ = stream.read(1280)
    process(audio)

# ✅ CORRECT - Proper device management
import sounddevice as sd
import numpy as np
from typing import Callable
import threading
import logging

logger = logging.getLogger(__name__)

class AudioStreamManager:
    def __init__(
        self,
        sample_rate: int = 16000,
        chunk_size: int = 1280,
        device: int | str | None = None,
    ):
        self._sample_rate = sample_rate
        self._chunk_size = chunk_size
        self._device = device
        self._stream: sd.InputStream | None = None
        self._callbacks: list[Callable[[np.ndarray], None]] = []
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio stream."""
        if status:
            logger.warning(f"Audio stream status: {status}")

        # Convert to float32 normalized
        audio = indata[:, 0].astype(np.float32)

        for callback in self._callbacks:
            try:
                callback(audio)
            except Exception as e:
                logger.error(f"Callback error: {e}")

    def add_callback(self, callback: Callable[[np.ndarray], None]) -> None:
        self._callbacks.append(callback)

    def start(self) -> None:
        """Start audio capture."""
        if self._stream is not None:
            raise RuntimeError("Stream already running")

        self._stop_event.clear()

        try:
            self._stream = sd.InputStream(
                samplerate=self._sample_rate,
                blocksize=self._chunk_size,
                device=self._device,
                channels=1,
                dtype=np.float32,
                callback=self._audio_callback,
            )
            self._stream.start()
            logger.info(f"Audio stream started (device: {self._device})")
        except sd.PortAudioError as e:
            logger.error(f"Failed to start audio stream: {e}")
            raise

    def stop(self) -> None:
        """Stop audio capture and cleanup."""
        self._stop_event.set()

        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception as e:
                logger.error(f"Error stopping stream: {e}")
            finally:
                self._stream = None

        logger.info("Audio stream stopped")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
```

### WHEN handling detections, implement cooldown and callbacks

```python
# ❌ WRONG - Multiple rapid triggers
def on_audio(audio):
    if detector.detect(audio):
        activate_assistant()  # May trigger 10 times in a row!

# ✅ CORRECT - Cooldown and proper callback system
from dataclasses import dataclass
from typing import Callable
import time
import asyncio

@dataclass
class DetectionEvent:
    wake_word: str
    confidence: float
    timestamp: float
    audio_context: np.ndarray | None = None

class WakeWordListener:
    def __init__(
        self,
        detector: OpenWakeWordDetector,
        cooldown_seconds: float = 2.0,
        capture_context: bool = True,
        context_seconds: float = 1.0,
    ):
        self._detector = detector
        self._cooldown = cooldown_seconds
        self._capture_context = capture_context
        self._context_samples = int(context_seconds * 16000)

        self._last_detection: float = 0
        self._callbacks: list[Callable[[DetectionEvent], None]] = []
        self._audio_buffer = SecureAudioBuffer(16000, PrivacyConfig())

    def on_detection(self, callback: Callable[[DetectionEvent], None]) -> None:
        """Register detection callback."""
        self._callbacks.append(callback)

    def process_audio(self, audio: np.ndarray) -> None:
        """Process audio chunk."""
        if self._capture_context:
            self._audio_buffer.add(audio)

        results = self._detector.process(audio)

        for wake_word, triggered in results.items():
            if not triggered:
                continue

            now = time.time()
            if now - self._last_detection < self._cooldown:
                continue  # Still in cooldown

            self._last_detection = now

            event = DetectionEvent(
                wake_word=wake_word,
                confidence=results.get(f"{wake_word}_score", 0.0),
                timestamp=now,
                audio_context=(
                    self._audio_buffer.get_audio()
                    if self._capture_context else None
                ),
            )

            # Clear buffer after detection (privacy)
            self._audio_buffer.clear()

            # Notify callbacks
            for callback in self._callbacks:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Detection callback error: {e}")

    async def process_audio_async(self, audio: np.ndarray) -> None:
        """Async version for event loop integration."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.process_audio, audio)
```

### WHEN supporting custom wake words, validate training data

```python
# ❌ WRONG - Training on arbitrary audio
def train_custom_wakeword(audio_files: list[str]):
    for f in audio_files:
        process_training_audio(f)

# ✅ CORRECT - Validated training pipeline
from dataclasses import dataclass
from pathlib import Path
import soundfile as sf

@dataclass
class TrainingConfig:
    min_samples: int = 50
    max_samples: int = 500
    min_duration_s: float = 0.5
    max_duration_s: float = 3.0
    required_sample_rate: int = 16000
    max_total_audio_minutes: float = 30.0

@dataclass
class TrainingValidation:
    valid: bool
    errors: list[str]
    warnings: list[str]
    stats: dict

def validate_training_data(
    audio_dir: Path,
    config: TrainingConfig,
) -> TrainingValidation:
    """Validate training audio before processing."""
    errors = []
    warnings = []
    stats = {"total_files": 0, "total_duration": 0, "valid_files": 0}

    audio_files = list(audio_dir.glob("*.wav"))
    stats["total_files"] = len(audio_files)

    if len(audio_files) < config.min_samples:
        errors.append(
            f"Insufficient samples: {len(audio_files)} < {config.min_samples}"
        )

    if len(audio_files) > config.max_samples:
        warnings.append(
            f"Too many samples: {len(audio_files)} > {config.max_samples}, "
            "will use random subset"
        )

    for audio_file in audio_files:
        try:
            info = sf.info(str(audio_file))

            if info.samplerate != config.required_sample_rate:
                errors.append(
                    f"{audio_file.name}: Wrong sample rate "
                    f"({info.samplerate} != {config.required_sample_rate})"
                )
                continue

            if info.duration < config.min_duration_s:
                warnings.append(f"{audio_file.name}: Too short ({info.duration:.2f}s)")
                continue

            if info.duration > config.max_duration_s:
                warnings.append(f"{audio_file.name}: Too long ({info.duration:.2f}s)")
                continue

            stats["valid_files"] += 1
            stats["total_duration"] += info.duration

        except Exception as e:
            errors.append(f"{audio_file.name}: Failed to read ({e})")

    total_minutes = stats["total_duration"] / 60
    if total_minutes > config.max_total_audio_minutes:
        warnings.append(
            f"Total audio too long: {total_minutes:.1f} > "
            f"{config.max_total_audio_minutes} minutes"
        )

    return TrainingValidation(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        stats=stats,
    )
```

---

## 4. Anti-Patterns

Do not:
- Store raw audio longer than necessary (privacy risk)
- Load model files without integrity verification
- Process audio without resource limits (DoS risk)
- Trigger on single detection (use trigger_level)
- Skip cooldown between detections
- Use default thresholds in production (tune per environment)
- Process audio on main thread (use callbacks/async)

---

## 5. Testing

```python
import pytest
import numpy as np
from wake_word_detection import (
    OpenWakeWordDetector,
    WakeWordConfig,
    SecureAudioBuffer,
    PrivacyConfig,
# ... (additional test cases follow same pattern)
```

---

## 6. Pre-Generation Checklist

Before generating wake word detection code:

- [ ] Privacy: Audio buffer has max duration, secure wipe
- [ ] Model integrity: SHA256 verification before loading
- [ ] Resource limits: Max concurrent inferences, queue size limits
- [ ] Detection logic: trigger_level for consecutive confirmations
- [ ] Cooldown: Prevent rapid-fire triggers
- [ ] Device handling: Proper stream lifecycle, error recovery
- [ ] Callbacks: Exception handling, async support
- [ ] Testing: Mock models for unit tests

---
