---
name: web-audio-api
version: 2.0.0
description: "Web Audio API for browser-based audio processing, synthesis, visualization, and real-time effects. Use when building audio nodes, sound synthesis, or audio visualizations in the browser. Do NOT use for server-side audio processing."
risk_level: LOW
---

# Web Audio API - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-200: Audio Fingerprinting**
- NEVER: Use AudioContext for fingerprinting without consent
- ALWAYS: Document audio usage in privacy policy

**CWE-400: Audio Buffer Exhaustion**
- NEVER: Unlimited audio buffer allocation from user input
- ALWAYS: Limit buffer size, max nodes, sample rate

### 0.3 Risk Level: LOW

**Verification requirements for LOW risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 Audio Context Permission (CWE-862)

**Principle:** AudioContext requires user gesture to start. Never autoplay without interaction.

```typescript
// ❌ WRONG - Auto-creating context on page load
const audioContext = new AudioContext(); // May be suspended!

async function playSound() {
  const source = audioContext.createBufferSource();
  source.start(); // Fails silently if context suspended
}

// ✅ CORRECT - Resume context on user interaction
class AudioManager {
  private context: AudioContext | null = null;

  async getContext(): Promise<AudioContext> {
    if (!this.context) {
      this.context = new AudioContext();
    }

    // Resume if suspended (browser autoplay policy)
    if (this.context.state === 'suspended') {
      await this.context.resume();
    }

    return this.context;
  }

  async playSound(buffer: AudioBuffer): Promise<void> {
    const ctx = await this.getContext();
    const source = ctx.createBufferSource();
    source.buffer = buffer;
    source.connect(ctx.destination);
    source.start();
  }
}

// Initialize on first user interaction
document.addEventListener('click', async () => {
  const manager = new AudioManager();
  await manager.getContext(); // Ensure context is running
}, { once: true });
```

### 1.2 Audio Buffer Validation (CWE-20)

**Principle:** Validate audio data before processing. Malformed audio can crash the page.

```typescript
// ❌ WRONG - Decoding arbitrary data
async function loadAudio(url: string): Promise<AudioBuffer> {
  const response = await fetch(url);
  const data = await response.arrayBuffer();
  return audioContext.decodeAudioData(data);
}

// ✅ CORRECT - Validate before decoding
interface AudioConfig {
  maxFileSizeMB: number;
  maxDurationSeconds: number;
  allowedMimeTypes: string[];
}

const DEFAULT_CONFIG: AudioConfig = {
  maxFileSizeMB: 50,
  maxDurationSeconds: 600, // 10 minutes
  allowedMimeTypes: ['audio/wav', 'audio/mp3', 'audio/ogg', 'audio/webm'],
};

async function loadAudioSafe(
  url: string,
  config: AudioConfig = DEFAULT_CONFIG
): Promise<AudioBuffer> {
  // Check content type and size
  const headResponse = await fetch(url, { method: 'HEAD' });
  const contentType = headResponse.headers.get('content-type');
  const contentLength = parseInt(headResponse.headers.get('content-length') || '0');

  if (!config.allowedMimeTypes.some(type => contentType?.includes(type))) {
    throw new Error(`Unsupported audio type: ${contentType}`);
  }

  if (contentLength > config.maxFileSizeMB * 1024 * 1024) {
    throw new Error(`Audio file too large: ${contentLength} bytes`);
  }

  const response = await fetch(url);
  const data = await response.arrayBuffer();

  const buffer = await audioContext.decodeAudioData(data);

  if (buffer.duration > config.maxDurationSeconds) {
    throw new Error(`Audio too long: ${buffer.duration}s`);
  }

  return buffer;
}
```

### 1.3 Worklet Security (CWE-94)

**Principle:** AudioWorklet code runs in a separate thread. Validate inputs to worklets.

```typescript
// ❌ WRONG - Passing arbitrary data to worklet
class CustomProcessor extends AudioWorkletProcessor {
  process(inputs: Float32Array[][], outputs: Float32Array[][], parameters: Record<string, Float32Array>) {
    // Processing arbitrary input without validation
    const gain = parameters.gain[0];
    // ...
  }
}

// ✅ CORRECT - Validate worklet parameters
class SafeGainProcessor extends AudioWorkletProcessor {
  static get parameterDescriptors() {
    return [{
      name: 'gain',
      defaultValue: 1.0,
      minValue: 0.0,
      maxValue: 2.0, // Prevent clipping/distortion attacks
      automationRate: 'a-rate',
    }];
  }

  process(
    inputs: Float32Array[][],
    outputs: Float32Array[][],
    parameters: Record<string, Float32Array>
  ): boolean {
    const input = inputs[0];
    const output = outputs[0];

    if (!input || input.length === 0) return true;

    // Clamp gain to safe range
    const gain = Math.max(0, Math.min(2, parameters.gain[0]));

    for (let channel = 0; channel < input.length; channel++) {
      const inputChannel = input[channel];
      const outputChannel = output[channel];

      for (let i = 0; i < inputChannel.length; i++) {
        // Clamp output to prevent extreme values
        outputChannel[i] = Math.max(-1, Math.min(1, inputChannel[i] * gain));
      }
    }

    return true;
  }
}
```

---

## 2. Version Requirements

```
# Web Audio API is native - no npm packages required
# For TypeScript types:
@types/web-audio-api>=0.0.0 (deprecated, use lib.dom.d.ts)

# Useful utilities:
tone>=14.8.0
standardized-audio-context>=25.3.0
```

---

## 3. Code Patterns

### WHEN creating audio graphs, use proper node cleanup

```typescript
// ❌ WRONG - Nodes not disconnected (memory leak)
function createEffect() {
  const gain = audioContext.createGain();
  const filter = audioContext.createBiquadFilter();
  gain.connect(filter);
  filter.connect(audioContext.destination);
  return { gain, filter };
}

// ✅ CORRECT - Managed audio graph with cleanup
class AudioGraph {
  private nodes: Set<AudioNode> = new Set();
  private connections: Map<AudioNode, AudioNode[]> = new Map();

  constructor(private context: AudioContext) {}

  createGain(): GainNode {
    const node = this.context.createGain();
    this.nodes.add(node);
    return node;
  }

  createFilter(type: BiquadFilterType): BiquadFilterNode {
    const node = this.context.createBiquadFilter();
    node.type = type;
    this.nodes.add(node);
    return node;
  }

  connect(source: AudioNode, destination: AudioNode): void {
    source.connect(destination);
    const existing = this.connections.get(source) || [];
    existing.push(destination);
    this.connections.set(source, existing);
  }

  disconnect(node: AudioNode): void {
    node.disconnect();
    this.connections.delete(node);
  }

  dispose(): void {
    // Disconnect all nodes
    for (const node of this.nodes) {
      try {
        node.disconnect();
      } catch {
        // Node may already be disconnected
      }
    }
    this.nodes.clear();
    this.connections.clear();
  }
}
```

### WHEN implementing real-time audio, use AudioWorklet

```typescript
// ❌ WRONG - Using deprecated ScriptProcessorNode
const processor = audioContext.createScriptProcessor(4096, 1, 1);
processor.onaudioprocess = (event) => {
  // Runs on main thread, causes audio glitches!
  const input = event.inputBuffer.getChannelData(0);
  const output = event.outputBuffer.getChannelData(0);
  // Process...
};

// ✅ CORRECT - AudioWorklet for real-time processing
// worklet.ts (separate file)
class VolumeProcessor extends AudioWorkletProcessor {
  private volume = 0;

  process(inputs: Float32Array[][]): boolean {
    const input = inputs[0]?.[0];
    if (!input) return true;

    // Calculate RMS volume
    let sum = 0;
    for (let i = 0; i < input.length; i++) {
      sum += input[i] * input[i];
    }
    this.volume = Math.sqrt(sum / input.length);

    // Send to main thread (throttled)
    this.port.postMessage({ volume: this.volume });

    return true;
  }
}

registerProcessor('volume-processor', VolumeProcessor);

// main.ts
async function setupVolumeMetering(context: AudioContext): Promise<AudioWorkletNode> {
  await context.audioWorklet.addModule('/worklets/volume-processor.js');

  const volumeNode = new AudioWorkletNode(context, 'volume-processor');

  volumeNode.port.onmessage = (event) => {
    const { volume } = event.data;
    updateVolumeUI(volume);
  };

  return volumeNode;
}
```

### WHEN handling microphone input, request permission properly

```typescript
// ❌ WRONG - No permission handling
async function startMicrophone() {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const source = audioContext.createMediaStreamSource(stream);
  source.connect(audioContext.destination); // Feedback loop!
}

// ✅ CORRECT - Proper permission and feedback prevention
class MicrophoneManager {
  private stream: MediaStream | null = null;
  private source: MediaStreamAudioSourceNode | null = null;

  async requestAccess(): Promise<boolean> {
    try {
      // Check permission first
      const permission = await navigator.permissions.query(
        { name: 'microphone' as PermissionName }
      );

      if (permission.state === 'denied') {
        throw new Error('Microphone permission denied');
      }

      this.stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      return true;
    } catch (error) {
      console.error('Microphone access failed:', error);
      return false;
    }
  }

  connect(context: AudioContext, destination: AudioNode): MediaStreamAudioSourceNode {
    if (!this.stream) {
      throw new Error('Call requestAccess() first');
    }

    this.source = context.createMediaStreamSource(this.stream);
    // DON'T connect directly to destination (feedback!)
    // Connect to processing chain instead
    this.source.connect(destination);

    return this.source;
  }

  stop(): void {
    if (this.source) {
      this.source.disconnect();
      this.source = null;
    }

    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }
  }
}
```

### WHEN scheduling audio, use AudioContext time

```typescript
// ❌ WRONG - Using setTimeout for audio timing
function playSequence(notes: number[]) {
  notes.forEach((note, i) => {
    setTimeout(() => {
      playNote(note);
    }, i * 500); // Imprecise!
  });
}

// ✅ CORRECT - Use AudioContext currentTime
class AudioScheduler {
  private scheduleAheadTime = 0.1; // Schedule 100ms ahead
  private lookahead = 25; // Check every 25ms

  constructor(private context: AudioContext) {}

  scheduleNote(
    buffer: AudioBuffer,
    startTime: number,
    duration?: number
  ): AudioBufferSourceNode {
    const source = this.context.createBufferSource();
    source.buffer = buffer;
    source.connect(this.context.destination);

    source.start(startTime);
    if (duration !== undefined) {
      source.stop(startTime + duration);
    }

    return source;
  }

  scheduleSequence(
    buffers: AudioBuffer[],
    startTime: number,
    noteDuration: number
  ): void {
    let time = startTime;

    for (const buffer of buffers) {
      this.scheduleNote(buffer, time, noteDuration);
      time += noteDuration;
    }
  }

  // Get precise current time
  get now(): number {
    return this.context.currentTime;
  }
}
```

---

## 4. Anti-Patterns

**NEVER:**
- Create AudioContext before user interaction (will be suspended)
- Connect microphone directly to destination (feedback loop)
- Use ScriptProcessorNode (deprecated, use AudioWorklet)
- Use setTimeout/setInterval for audio timing
- Forget to disconnect nodes (memory leaks)
- Decode untrusted audio without size/duration limits
- Ignore context state (suspended/running/closed)

---

## 5. Testing

```typescript
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

describe('AudioManager', () => {
  let manager: AudioManager;

  beforeEach(() => {
    manager = new AudioManager();
  });

  afterEach(() => {
    manager.dispose();
  });

  it('should resume suspended context on getContext', async () => {
    // Mock suspended context
    const mockContext = {
      state: 'suspended',
      resume: vi.fn().mockResolvedValue(undefined),
    };

    vi.spyOn(window, 'AudioContext').mockImplementation(
      () => mockContext as unknown as AudioContext
    );

    await manager.getContext();

    expect(mockContext.resume).toHaveBeenCalled();
  });

  it('should reject oversized audio files', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      headers: {
        get: (name: string) => {
          if (name === 'content-length') return '100000000'; // 100MB
          if (name === 'content-type') return 'audio/wav';
          return null;
        },
      },
    });

    await expect(
      loadAudioSafe('https://example.com/huge.wav')
    ).rejects.toThrow('Audio file too large');
  });
});

describe('AudioGraph', () => {
  it('should disconnect all nodes on dispose', () => {
    const mockContext = new AudioContext();
    const graph = new AudioGraph(mockContext);

    const gain = graph.createGain();
    const filter = graph.createFilter('lowpass');
    graph.connect(gain, filter);

    const disconnectSpy = vi.spyOn(gain, 'disconnect');

    graph.dispose();

    expect(disconnectSpy).toHaveBeenCalled();
  });
});
```

---

## 6. Pre-Generation Checklist

**BEFORE generating Web Audio code:**

- [ ] AudioContext: Created after user interaction, resume if suspended
- [ ] Audio loading: Size and duration limits enforced
- [ ] Node cleanup: All nodes tracked and disconnected on dispose
- [ ] Microphone: Permission handled, no direct destination connection
- [ ] Real-time: Using AudioWorklet, not ScriptProcessorNode
- [ ] Timing: Using AudioContext.currentTime, not setTimeout
- [ ] Worklet parameters: Min/max values defined and enforced
- [ ] Output clamping: Values limited to [-1, 1] range

---

**Performance**: Quality over speed. Verify all code examples compile. Never skip security checks. See `template-references/performance-notes.md` for full guidelines.