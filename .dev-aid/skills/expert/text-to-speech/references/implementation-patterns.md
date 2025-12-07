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
        audio_chunks = []
        for _, _, audio in generator:
            audio_chunks.append(audio)

        if not audio_chunks:
            raise TTSError("No audio generated")

        # Concatenate and save
        full_audio = np.concatenate(audio_chunks)
        sf.write(str(audio_path), full_audio, 24000)

        logger.info("tts.synthesized",
                   text_length=len(text),
                   audio_duration=len(full_audio) / 24000)

        return str(audio_path)

    def _validate_text(self, text: str) -> bool:
        """Validate text input."""
        if not text or not text.strip():
            return False

        # Length limit (prevent DoS)
        if len(text) > 5000:
            logger.warning("tts.text_too_long", length=len(text))
            return False

        return True

    def _filter_sensitive(self, text: str) -> str:
        """Filter sensitive content from text."""
        import re

        filtered = text
        for pattern in self.blocked_patterns:
            if re.search(pattern, filtered, re.IGNORECASE):
                logger.warning("tts.sensitive_content_filtered")
                filtered = re.sub(pattern + r'\S+', '[FILTERED]', filtered, flags=re.IGNORECASE)

        return filtered

    def cleanup(self):
        """Clean up temp files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
```

### Pattern 2: Streaming TTS

```python
# Stream audio chunks as generated for low latency
with sd.OutputStream(samplerate=24000, channels=1) as stream:
    for _, _, audio in pipeline(text, voice=voice):
        stream.write(audio)  # Play immediately
```

### Pattern 3: Audio Caching

```python
# Cache common phrases with hash key
cache_key = hashlib.sha256(f"{text}:{voice}".encode()).hexdigest()
cache_path = cache_dir / f"{cache_key}.wav"
if cache_path.exists():
    return str(cache_path)  # Cache hit
# Generate, save to cache, return path
```

### Pattern 4: Voice Manager

```python
# Lazy-load engines per voice type
VOICES = {"default": "af_heart", "formal": "af_bella"}

def get_engine(voice_type: str) -> SecureTTSEngine:
    if voice_type not in engines:
        engines[voice_type] = SecureTTSEngine(voice=VOICES[voice_type])
    return engines[voice_type]
```

### Pattern 5: Resource Limits

```python
# Semaphore for concurrency + timeout for protection
async with asyncio.Semaphore(2):
    result = await asyncio.wait_for(
        loop.run_in_executor(None, engine.synthesize, text),
        timeout=30.0
    )
```

---

