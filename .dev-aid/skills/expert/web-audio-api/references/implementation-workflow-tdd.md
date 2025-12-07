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

