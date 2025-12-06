## 7. Implementation Patterns

### Pattern 1: Secure Faster Whisper Setup

```python
from faster_whisper import WhisperModel
from pathlib import Path
import tempfile, os, structlog

logger = structlog.get_logger()

class SecureSTTEngine:
    def __init__(self, model_size="base", device="cpu", compute_type="int8"):
        valid_sizes = ["tiny", "base", "small", "medium", "large-v3"]
        if model_size not in valid_sizes:
            raise ValueError(f"Invalid model size: {model_size}")

        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        self.temp_dir = tempfile.mkdtemp(prefix="jarvis_stt_")
        os.chmod(self.temp_dir, 0o700)

    def transcribe(self, audio_path: str) -> str:
        path = Path(audio_path).resolve()
        if not self._validate_audio_file(path):
            raise ValidationError("Invalid audio file")

        try:
            segments, info = self.model.transcribe(
                str(path), beam_size=5, vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            text = " ".join(s.text for s in segments)
            logger.info("stt.transcribed", duration=info.duration)
            return text.strip()
        finally:
            path.unlink(missing_ok=True)

    def _validate_audio_file(self, path: Path) -> bool:
        if not path.exists():
            return False
        if path.stat().st_size > 50 * 1024 * 1024:
            return False
        return path.suffix.lower() in {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}

    def cleanup(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
```

### Pattern 2: Privacy-Preserving Transcription

```python
class PrivacyAwareSTT:
    """STT with privacy protections."""

    def __init__(self, engine: SecureSTTEngine):
        self.engine = engine

    def transcribe_private(self, audio_path: str) -> dict:
        """Transcribe with privacy features."""
        # Transcribe
        text = self.engine.transcribe(audio_path)

        # Remove PII patterns
        cleaned = self._remove_pii(text)

        # Log without content
        logger.info("stt.transcribed_private",
                   word_count=len(cleaned.split()),
                   had_pii=cleaned != text)

        return {
            "text": cleaned,
            "privacy_filtered": cleaned != text
        }

    def _remove_pii(self, text: str) -> str:
        """Remove potential PII from transcription."""
        import re

        # Phone numbers
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)

        # Email addresses
        text = re.sub(r'\b[\w.-]+@[\w.-]+\.\w+\b', '[EMAIL]', text)

        # Social security numbers
        text = re.sub(r'\b\d{3}[-]?\d{2}[-]?\d{4}\b', '[SSN]', text)

        # Credit card numbers
        text = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD]', text)

        return text
```

---

