## 6. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```python
# tests/test_wake_word.py
import pytest
import numpy as np
from unittest.mock import Mock, patch

class TestWakeWordDetector:
    """TDD tests for wake word detection."""

    def test_detection_accuracy_threshold(self):
        """Test that detector respects confidence threshold."""
        from wake_word import SecureWakeWordDetector

        detector = SecureWakeWordDetector(threshold=0.7)
        callback = Mock()
        test_audio = np.random.randn(16000).astype(np.float32)

        with patch.object(detector.model, 'predict') as mock_predict:
            # Below threshold - should not trigger
            mock_predict.return_value = {"hey_jarvis": np.array([0.5])}
            detector._test_process(test_audio, callback)
            callback.assert_not_called()

            # Above threshold - should trigger
            mock_predict.return_value = {"hey_jarvis": np.array([0.8])}
            detector._test_process(test_audio, callback)
            callback.assert_called_once()

    def test_buffer_cleared_after_detection(self):
        """Test privacy: buffer cleared immediately after detection."""
        from wake_word import SecureWakeWordDetector

        detector = SecureWakeWordDetector()
        detector.audio_buffer.extend(np.zeros(16000))

        with patch.object(detector.model, 'predict') as mock_predict:
            mock_predict.return_value = {"hey_jarvis": np.array([0.9])}
            detector._process_audio()

        assert len(detector.audio_buffer) == 0, "Buffer must be cleared"

    def test_cpu_usage_under_threshold(self):
        """Test CPU usage stays under 5%."""
        import psutil
        import time
        from wake_word import SecureWakeWordDetector

        detector = SecureWakeWordDetector()
        process = psutil.Process()
        start_time = time.time()

        while time.time() - start_time < 10:
            audio = np.random.randn(1600).astype(np.float32)
            detector.audio_buffer.extend(audio)
            if len(detector.audio_buffer) >= 16000:
                detector._process_audio()

        avg_cpu = process.cpu_percent() / psutil.cpu_count()
        assert avg_cpu < 5, f"CPU usage too high: {avg_cpu}%"

    def test_memory_footprint(self):
        """Test memory usage stays under 100MB."""
        import tracemalloc
        from wake_word import SecureWakeWordDetector

        tracemalloc.start()
        detector = SecureWakeWordDetector()

        for _ in range(600):
            audio = np.random.randn(1600).astype(np.float32)
            detector.audio_buffer.extend(audio)

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_mb = peak / 1024 / 1024
        assert peak_mb < 100, f"Memory too high: {peak_mb}MB"
```

### Step 2: Implement Minimum to Pass

```python
class SecureWakeWordDetector:
    def __init__(self, threshold=0.5):
        self.threshold = threshold
        self.model = Model(wakeword_models=["hey_jarvis"])
        self.audio_buffer = deque(maxlen=24000)

    def _test_process(self, audio, callback):
        predictions = self.model.predict(audio)
        for model_name, scores in predictions.items():
            if np.max(scores) > self.threshold:
                self.audio_buffer.clear()
                callback(model_name, np.max(scores))
                break
```

### Step 3: Run Full Verification

```bash
pytest tests/test_wake_word.py -v
pytest --cov=wake_word --cov-report=term-missing
```

---

