---
name: web-audio-api
description: Web Audio API for JARVIS audio feedback and voice processing
risk_level: LOW
version: 1.0.0
---

# Web Audio API Skill


### 0.4 Progressive Disclosure (500-Line Limit)

**⚠️ CRITICAL**: This SKILL.md file MUST stay <500 lines for Claude Code to load it.

**If this file is approaching 500 lines**:
- Move detailed examples to `references/advanced-patterns.md`
- Move security examples to `references/security-examples.md`
- Move troubleshooting to `references/troubleshooting.md`
- Keep only summaries and links in main file

📚 **For complete progressive disclosure guide**: See `../../../template-references/progressive-disclosure.md`

---

## 1. Overview

This skill provides Web Audio API expertise for creating audio feedback, voice processing, and sound effects in the JARVIS AI Assistant.

**Risk Level**: LOW - Audio processing with minimal security surface

**Primary Use Cases**:
- HUD audio feedback (beeps, alerts)
- Voice input processing
- Spatial audio for 3D HUD elements
- Real-time audio visualization
- Text-to-speech integration

## 2. Core Responsibilities

### 2.1 Fundamental Principles

1. **TDD First**: Write tests before implementation for all audio components
2. **Performance Aware**: Optimize for 60fps with minimal audio latency
3. **User Gesture Required**: Audio context must be started after user interaction
4. **Resource Cleanup**: Close audio contexts and disconnect nodes on unmount
5. **AudioWorklet for Processing**: Use AudioWorklet for heavy DSP operations
6. **Accessibility**: Provide visual alternatives to audio feedback
7. **Volume Control**: Respect system and user volume preferences
8. **Error Handling**: Gracefully handle audio permission denials

## 3. Technology Stack & Versions

### 3.1 Browser Support

| Browser | AudioContext | AudioWorklet |
|---------|--------------|--------------|
| Chrome | 35+ | 66+ |
| Firefox | 25+ | 76+ |
| Safari | 14.1+ | 14.1+ |

### 3.2 TypeScript Types

```typescript
// types/audio.ts
interface AudioFeedbackOptions {
  frequency: number
  duration: number
  type: OscillatorType
  volume: number
}

interface SpatialAudioPosition {
  x: number
  y: number
  z: number
}
```


## 4. Quality Assurance Checklist

**Before implementing this skill, ensure**:

### 4.1 Pre-Implementation Setup
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] Pre-commit hooks installed (`pre-commit install`)
- [ ] Linters installed (black, isort, flake8, mypy, bandit)

### 4.2 Dependency Management
- [ ] All dependencies pinned with exact versions (==)
- [ ] No manual transitive dependency pins
- [ ] Dependencies tested in clean environment

### 4.3 Code Quality Gates (Run BEFORE committing)
- [ ] `black .` - Code formatted
- [ ] `isort .` - Imports sorted
- [ ] `flake8 . --max-line-length=120` - No linting errors
- [ ] `mypy . --ignore-missing-imports` - Type checking passes
- [ ] `bandit -r .` - Security scan clean

### 4.4 Security Validation
- [ ] Input validation for ALL external inputs
- [ ] Path traversal prevention implemented
- [ ] Command injection prevention (no shell=True)
- [ ] SQL injection prevention (parameterized queries)
- [ ] Secrets not in code or error messages

📚 **For complete security validation guide**: See `../../../template-references/security-framework.md`

### 4.5 Test Coverage Requirements
- [ ] Tests written BEFORE implementation (TDD)
- [ ] Unit tests for all public functions
- [ ] Edge case tests (empty, null, max values)
- [ ] Security tests (injection, traversal, overflow)
- [ ] Code coverage >80%

### 4.6 Documentation Requirements
- [ ] Docstrings for all public functions/classes
- [ ] Security considerations documented
- [ ] Examples of correct usage
- [ ] Known limitations documented

---

## 5. Implementation Patterns

async function initialize() {
    if (audioContext.value) return
    audioContext.value = new AudioContext()
    if (audioContext.value.state === 'suspended') await audioContext.value.resume()
    isInitialized.value = true
  }

📚 **For complete details**: See `references/implementation-patterns.md`

---
## 6. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```typescript
// tests/composables/useHUDSounds.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useHUDSounds } from '~/composables/useHUDSounds'

// Mock AudioContext nodes
const mockOscillator = { connect: vi.fn(), start: vi.fn(), stop: vi.fn(), frequency: { value: 440 } }
const mockGainNode = { connect: vi.fn(), gain: { value: 1, exponentialRampToValueAtTime: vi.fn() } }
const mockAudioContext = {
  state: 'running', currentTime: 0, destination: {},
  createOscillator: vi.fn(() => mockOscillator),
  createGain: vi.fn(() => mockGainNode),
  resume: vi.fn(), close: vi.fn()
}
vi.stubGlobal('AudioContext', vi.fn(() => mockAudioContext))

describe('useHUDSounds', () => {
  beforeEach(() => vi.clearAllMocks())

  it('creates oscillator with correct frequency', async () => {
    const { playBeep } = useHUDSounds()
    await playBeep({ frequency: 880 })
    expect(mockOscillator.frequency.value).toBe(880)
  })

  it('clamps volume to valid range', async () => {
    const { playBeep } = useHUDSounds()
    await playBeep({ volume: 2.5 })
    expect(mockGainNode.gain.value).toBeLessThanOrEqual(1)
  })

  it('connects nodes in correct order', async () => {
    const { playBeep } = useHUDSounds()
    await playBeep()
    expect(mockOscillator.connect).toHaveBeenCalledWith(mockGainNode)
    expect(mockGainNode.connect).toHaveBeenCalledWith(mockAudioContext.destination)
  })
})
```

### Step 2: Implement Minimum to Pass

```typescript
// composables/useHUDSounds.ts
export function useHUDSounds() {
  // Implementation from section 4.2
  // Only add features that tests require
}
```

### Step 3: Refactor Following Patterns

After tests pass, refactor to:
- Extract shared audio context logic
- Add proper TypeScript types
- Implement cleanup on unmount

### Step 4: Run Full Verification

```bash
# Run all audio-related tests
npm test -- --grep "audio|sound|HUD"

# Check types
npm run typecheck

# Verify no memory leaks in browser
npm run dev  # Test manually with DevTools Memory tab
```

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
functio## 6. Implementation Workflow (TDD)

// Mock AudioContext nodes
const mockOscillator = { connect: vi.fn(), start: vi.fn(), stop: vi.fn(), frequency: { value: 440 } }
const mockGainNode = { connect: vi.fn(), gain: { value: 1, exponentialRampToValueAtTime: vi.fn() } }
const mockAudioContext = {
  state: 'running', currentTime: 0, destina...

📚 **For complete details**: See `references/implementation-workflow-tdd.md`

---
 handleClick = async () => { await audioContext.resume(); playSound() }

// ❌ Memory leak - no cleanup
const audioContext = new AudioContext()

// ✅ Proper cleanup
onUnmounted(() => audioContext.close())

// ❌ New context per sound - performance killer
function playSound() { const ctx = new AudioContext() }

// ✅ Reuse context
const ctx = new AudioContext()
function playSound() { /* reuse ctx */ }
```

## 11. Pre-Implementation Checklist

### Phase 1: Before Writing Code

- [ ] Tests written for audio node creation and connections
- [ ] Tests written for volume clamping and validation
- [ ] Performance requirements identified (latency, concurrent sounds)
- [ ] AudioWorklet needed for DSP? Worklet file created
- [ ] Buffer pool size calculated for expected usage

### Phase 2: During Implementation

- [ ] User gesture required for AudioContext initialization
- [ ] Audio context reused (not created per sound)
- [ ] Nodes disconnected in onended callbacks
- [ ] Volume bounds validated (0-1 range)
- [ ] Microphone permissions handled gracefully
- [ ] Error states provide visual feedback

### Phase 3: Before Committing

- [ ] All audio tests pass: `npm test -- --grep "audio"`
- [ ] Type checking passes: `npm run typecheck`
- [ ] No memory leaks (tested in DevTools Memory tab)
- [ ] Audio context closed on component unmount
- [ ] Visual alternatives provided for accessibility
- [ ] Sound can be disabled via user preferences
- [ ] Volume respects system preferences

## 12. Summary

Web Audio API for JARVIS: Initialize after user gesture, cleanup on unmount, handle permission denials, provide visual alternatives. See `references/advanced-patterns.md`
## 7. Performance Patterns

// ❌ Bad: ScriptProcessorNode (deprecated, blocks main thread)
```

📚 **For complete details**: See `references/performance-patterns.md`

---
