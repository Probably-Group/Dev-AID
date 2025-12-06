## 5. Implementation Patterns

### 4.1 Audio Context Management

```typescript
// composables/useAudioContext.ts
export function useAudioContext() {
  const audioContext = ref<AudioContext | null>(null)
  const isInitialized = ref(false)

  async function initialize() {
    if (audioContext.value) return
    audioContext.value = new AudioContext()
    if (audioContext.value.state === 'suspended') await audioContext.value.resume()
    isInitialized.value = true
  }

  onUnmounted(() => {
    audioContext.value?.close()
    audioContext.value = null
  })

  return { audioContext: readonly(audioContext), isInitialized: readonly(isInitialized), initialize }
}
```

### 4.2 HUD Beep Feedback

```typescript
// composables/useHUDSounds.ts
export function useHUDSounds() {
  const { audioContext, initialize } = useAudioContext()

  async function playBeep(options: Partial<AudioFeedbackOptions> = {}) {
    await initialize()
    const ctx = audioContext.value
    if (!ctx) return

    const { frequency = 440, duration = 0.1, type = 'sine', volume = 0.3 } = options
    const safeVolume = Math.max(0, Math.min(1, volume))

    const oscillator = ctx.createOscillator()
    const gainNode = ctx.createGain()
    oscillator.type = type
    oscillator.frequency.value = frequency
    gainNode.gain.value = safeVolume
    gainNode.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration)

    oscillator.connect(gainNode).connect(ctx.destination)
    oscillator.start()
    oscillator.stop(ctx.currentTime + duration)
  }

  const sounds = {
    confirm: () => playBeep({ frequency: 880, duration: 0.1, volume: 0.2 }),
    alert: () => playBeep({ frequency: 440, duration: 0.3, type: 'square', volume: 0.4 }),
    error: () => playBeep({ frequency: 220, duration: 0.5, type: 'sawtooth', volume: 0.3 }),
    click: () => playBeep({ frequency: 1000, duration: 0.05, volume: 0.1 })
  }
  return { playBeep, sounds }
}
```

### 4.3 Audio Visualization

```typescript
// composables/useAudioVisualization.ts
export function useAudioVisualization() {
  const { audioContext, initialize } = useAudioContext()
  let analyser: AnalyserNode | null = null
  let dataArray: Uint8Array | null = null

  async function setupAnalyser(source: AudioNode) {
    await initialize()
    const ctx = audioContext.value
    if (!ctx) return
    analyser = ctx.createAnalyser()
    analyser.fftSize = 256
    dataArray = new Uint8Array(analyser.frequencyBinCount)
    source.connect(analyser)
  }

  function getFrequencyData(): Uint8Array | null {
    if (!analyser || !dataArray) return null
    analyser.getByteFrequencyData(dataArray)
    return dataArray
  }

  return { setupAnalyser, getFrequencyData }
}
```

### 4.4 Spatial Audio for 3D HUD

```typescript
// composables/useSpatialAudio.ts
export function useSpatialAudio() {
  const { audioContext, initialize } = useAudioContext()
  let panner: PannerNode | null = null

  async function createSpatialSource(position: SpatialAudioPosition) {
    await initialize()
    const ctx = audioContext.value
    if (!ctx) return null
    panner = ctx.createPanner()
    panner.panningModel = 'HRTF'
    panner.distanceModel = 'inverse'
    setPosition(position)
    return panner
  }

  function setPosition(pos: SpatialAudioPosition) {
    if (!panner) return
    panner.positionX.value = pos.x
    panner.positionY.value = pos.y
    panner.positionZ.value = pos.z
  }

  return { createSpatialSource, setPosition }
}
```

### 4.5 Microphone Input

```typescript
// composables/useMicrophone.ts
export function useMicrophone() {
  const { audioContext, initialize } = useAudioContext()
  const stream = ref<MediaStream | null>(null)
  const isListening = ref(false)
  const error = ref<string | null>(null)

  async function startListening() {
    try {
      await initialize()
      stream.value = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true }
      })
      isListening.value = true
      return stream.value
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Microphone access denied'
      return null
    }
  }

  function stopListening() {
    stream.value?.getTracks().forEach(track => track.stop())
    stream.value = null
    isListening.value = false
  }

  onUnmounted(() => stopListening())

  return { stream: readonly(stream), isListening: readonly(isListening), error: readonly(error), startListening, stopListening }
}
```

