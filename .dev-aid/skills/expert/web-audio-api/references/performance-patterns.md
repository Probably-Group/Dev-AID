## 7. Performance Patterns

### 6.1 AudioWorklet for Processing

```typescript
// ✅ Good: Use AudioWorklet for DSP (runs on audio thread)
class NoiseGateProcessor extends AudioWorkletProcessor {
  process(inputs: Float32Array[][], outputs: Float32Array[][]) {
    for (let ch = 0; ch < inputs[0].length; ch++) {
      for (let i = 0; i < inputs[0][ch].length; i++) {
        outputs[0][ch][i] = Math.abs(inputs[0][ch][i]) > 0.01 ? inputs[0][ch][i] : 0
      }
    }
    return true
  }
}
registerProcessor('noise-gate', NoiseGateProcessor)

// ❌ Bad: ScriptProcessorNode (deprecated, blocks main thread)
```

### 6.2 Buffer Pooling

```typescript
// ✅ Good: Reuse audio buffers
class AudioBufferPool {
  private pool: AudioBuffer[] = []
  constructor(ctx: AudioContext, size: number, length: number) {
    for (let i = 0; i < size; i++) {
      this.pool.push(ctx.createBuffer(2, length, ctx.sampleRate))
    }
  }
  acquire(): AudioBuffer | undefined { return this.pool.pop() }
  release(buffer: AudioBuffer) {
    for (let ch = 0; ch < buffer.numberOfChannels; ch++) {
      buffer.getChannelData(ch).fill(0)
    }
    this.pool.push(buffer)
  }
}

// ❌ Bad: Create new buffer each time
const buffer = ctx.createBuffer(2, 44100, 44100) // Allocates memory each call
```

### 6.3 Offline Rendering

```typescript
// ✅ Good: Pre-render complex sounds
async function prerenderSound(): Promise<AudioBuffer> {
  const offlineCtx = new OfflineAudioContext(2, 44100, 44100)
  const osc = offlineCtx.createOscillator()
  const gain = offlineCtx.createGain()
  osc.connect(gain).connect(offlineCtx.destination)
  gain.gain.setValueAtTime(0, 0)
  gain.gain.linearRampToValueAtTime(1, 0.01)
  gain.gain.exponentialRampToValueAtTime(0.001, 1)
  osc.start(); osc.stop(1)
  return offlineCtx.startRendering()
}

// ❌ Bad: Generate complex sounds in real-time (multiple oscillators computed live)
```

### 6.4 Node Graph Optimization

```typescript
// ✅ Good: Reuse master gain node
const masterGain = ctx.createGain()
masterGain.connect(ctx.destination)
function playSound(buffer: AudioBuffer) {
  const source = ctx.createBufferSource()
  source.buffer = buffer
  source.connect(masterGain)
  source.start()
}

// ❌ Bad: Create full chain for each sound (gain + compressor per play)
```

### 6.5 Memory Management

```typescript
// ✅ Good: Disconnect and cleanup nodes
function playOneShot(buffer: AudioBuffer) {
  const source = ctx.createBufferSource()
  source.buffer = buffer
  source.connect(masterGain)
  source.onended = () => source.disconnect()
  source.start()
}

// ✅ Good: Limit concurrent sounds (max 8)
class SoundManager {
  private activeSources = new Set<AudioBufferSourceNode>()
  play(buffer: AudioBuffer) {
    if (this.activeSources.size >= 8) this.activeSources.values().next().value?.stop()
    const source = ctx.createBufferSource()
    source.buffer = buffer
    source.connect(masterGain)
    source.onended = () => { source.disconnect(); this.activeSources.delete(source) }
    this.activeSources.add(source)
    source.start()
  }
}

// ❌ Bad: Never cleanup - nodes stay in memory after playback
const source = ctx.createBufferSource()
source.connect(ctx.destination)
source.start()
```

