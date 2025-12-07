## 8. Performance Patterns

### Pattern 1: Model Quantization

```python
# Good - Use quantized ONNX model
import onnxruntime as ort

class QuantizedDetector:
    def __init__(self, model_path: str):
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        self.session = ort.InferenceSession(model_path, sess_options, providers=['CPUExecutionProvider'])

# Bad - Full precision model
class SlowDetector:
    def __init__(self, model_path: str):
        self.session = ort.InferenceSession(model_path)  # No optimization
```

### Pattern 2: Efficient Audio Buffering

```python
# Good - Pre-allocated numpy buffer with circular indexing
class EfficientBuffer:
    def __init__(self, size: int):
        self.buffer = np.zeros(size, dtype=np.float32)
        self.write_idx = 0
        self.size = size

    def append(self, audio: np.ndarray):
        n = len(audio)
        end_idx = (self.write_idx + n) % self.size
        if end_idx > self.write_idx:
            self.buffer[self.write_idx:end_idx] = audio
        else:
            self.buffer[self.write_idx:] = audio[:self.size - self.write_idx]
            self.buffer[:end_idx] = audio[self.size - self.write_idx:]
        self.write_idx = end_idx

# Bad - Individual appends
class SlowBuffer:
    def append(self, audio: np.ndarray):
        for sample in audio:  # Slow!
            self.buffer.append(sample)
```

### Pattern 3: VAD Preprocessing

```python
# Good - Skip inference on silence
import webrtcvad

class VADOptimizedDetector:
    def __init__(self):
        self.vad = webrtcvad.Vad(2)
        self.detector = SecureWakeWordDetector()

    def process(self, audio: np.ndarray):
        audio_int16 = (audio * 32767).astype(np.int16)
        if not self.vad.is_speech(audio_int16.tobytes(), 16000):
            return None  # Skip expensive inference
        return self.detector._process_audio()

# Bad - Always run inference
class WastefulDetector:
    def process(self, audio: np.ndarray):
        return self.detector._process_audio()  # Even on silence
```

### Pattern 4: Batch Inference

```python
# Good - Process multiple windows in single inference
class BatchDetector:
    def __init__(self, batch_size: int = 4):
        self.batch_size = batch_size
        self.pending_windows = []

    def add_window(self, audio: np.ndarray):
        self.pending_windows.append(audio)
        if len(self.pending_windows) >= self.batch_size:
            batch = np.stack(self.pending_windows)
            results = self.model.predict_batch(batch)
            self.pending_windows.clear()
            return results
        return None
```

### Pattern 5: Memory-Mapped Models

```python
# Good - Memory-map large model files
import mmap

class MmapModelLoader:
    def __init__(self, model_path: str):
        self.file = open(model_path, 'rb')
        self.mmap = mmap.mmap(self.file.fileno(), 0, access=mmap.ACCESS_READ)

# Bad - Load entire model into memory
class EagerModelLoader:
    def __init__(self, model_path: str):
        with open(model_path, 'rb') as f:
            self.model_data = f.read()  # Entire model in RAM
```

---

