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

