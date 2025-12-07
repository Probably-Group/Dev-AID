## 5. Performance Patterns

### Pattern: Streaming Synthesis (Low Latency)

```python
# BAD - Wait for full audio
audio_chunks = []
for _, _, audio in pipeline(text):
    audio_chunks.append(audio)
play_audio(np.concatenate(audio_chunks))  # Long wait

# GOOD - Stream chunks immediately
with sd.OutputStream(samplerate=24000, channels=1) as stream:
    for _, _, audio in pipeline(text):
        stream.write(audio)  # Play as generated
```

### Pattern: Model Caching (Faster Startup)

```python
# BAD: pipeline = KPipeline(lang_code="a")  # Reload each time

# GOOD - Singleton pattern
class TTSEngine:
    _pipeline = None
    @classmethod
    def get_pipeline(cls):
        if cls._pipeline is None:
            cls._pipeline = KPipeline(lang_code="a")
        return cls._pipeline
```

### Pattern: Audio Chunking (Memory Efficient)

```python
# BAD: data, sr = sf.read(audio_path)  # Full file in RAM

# GOOD - Process in chunks
with sf.SoundFile(audio_path) as f:
    while f.tell() < len(f):
        yield process(f.read(24000))
```

### Pattern: Async Generation (Non-blocking)

```python
# BAD: audio = engine.synthesize(text)  # Blocks event loop

# GOOD - Run in executor
audio = await loop.run_in_executor(None, engine.synthesize, text)
```

### Pattern: Voice Preloading (Instant Response)

```python
# BAD: return SecureTTSEngine(voice=VOICES[voice_type])  # Cold start

# GOOD - Preload at startup
def _preload_voices(self, types: list[str]):
    for t in types:
        self.engines[t] = SecureTTSEngine(voice=VOICES[t])
```

---

