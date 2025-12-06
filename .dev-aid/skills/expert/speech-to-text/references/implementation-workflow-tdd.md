## 5. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```python
# tests/test_stt_engine.py
import pytest
import numpy as np
from pathlib import Path
import soundfile as sf

class TestSTTEngine:
    @pytest.fixture
    def engine(self):
        from jarvis.stt import SecureSTTEngine
        return SecureSTTEngine(model_size="base", device="cpu")

    def test_transcription_returns_string(self, engine, tmp_path):
        audio = np.zeros(16000, dtype=np.float32)
        path = tmp_path / "test.wav"
        sf.write(path, audio, 16000)
        assert isinstance(engine.transcribe(str(path)), str)

    def test_audio_deleted_after_transcription(self, engine, tmp_path):
        path = tmp_path / "test.wav"
        sf.write(path, np.zeros(16000, dtype=np.float32), 16000)
        engine.transcribe(str(path))
        assert not path.exists()

    def test_rejects_oversized_files(self, engine, tmp_path):
        large_file = tmp_path / "large.wav"
        large_file.write_bytes(b"0" * (51 * 1024 * 1024))
        with pytest.raises(Exception):
            engine.transcribe(str(large_file))

class TestSTTPerformance:
    @pytest.fixture
    def engine(self):
        from jarvis.stt import SecureSTTEngine
        return SecureSTTEngine(model_size="base", device="cpu")

    def test_latency_under_300ms(self, engine, tmp_path):
        import time
        audio = np.random.randn(16000).astype(np.float32) * 0.1
        path = tmp_path / "short.wav"
        sf.write(path, audio, 16000)
        start = time.perf_counter()
        engine.transcribe(str(path))
        assert (time.perf_counter() - start) * 1000 < 300

    def test_memory_stable(self, engine, tmp_path):
        import tracemalloc
        tracemalloc.start()
        initial = tracemalloc.get_traced_memory()[0]
        for i in range(10):
            path = tmp_path / f"test_{i}.wav"
            sf.write(path, np.random.randn(16000).astype(np.float32) * 0.1, 16000)
            engine.transcribe(str(path))
        growth = (tracemalloc.get_traced_memory()[0] - initial) / 1024 / 1024
        tracemalloc.stop()
        assert growth < 50, f"Memory grew {growth:.1f}MB"
```

### Step 2: Implement Minimum to Pass

```python
# jarvis/stt/engine.py
from faster_whisper import WhisperModel

class SecureSTTEngine:
    def __init__(self, model_size="base", device="cpu", compute_type="int8"):
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe(self, audio_path: str) -> str:
        # Minimum implementation to pass tests
        segments, _ = self.model.transcribe(audio_path)
        return " ".join(s.text for s in segments).strip()
```

### Step 3: Refactor with Full Implementation

Add validation, security, cleanup, and optimizations from Pattern 1.

### Step 4: Run Full Verification

```bash
# Run all STT tests
pytest tests/test_stt_engine.py -v --tb=short

# Run with coverage
pytest tests/test_stt_engine.py --cov=jarvis.stt --cov-report=term-missing

# Run performance tests only
pytest tests/test_stt_engine.py -k "performance" -v
```

---

