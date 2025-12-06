## 5. Implementation Patterns

### 4.1 Setup Store with TypeScript

```typescript
// stores/jarvis.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface SystemMetrics {
  cpu: number
  memory: number
  network: number
  timestamp: number
}

interface JARVISState {
  status: 'idle' | 'listening' | 'processing' | 'responding'
  securityLevel: 'normal' | 'elevated' | 'lockdown'
}

export const useJarvisStore = defineStore('jarvis', () => {
  // State
  const state = ref<JARVISState>({
    status: 'idle',
    securityLevel: 'normal'
  })

  const metrics = ref<SystemMetrics>({
    cpu: 0,
    memory: 0,
    network: 0,
    timestamp: Date.now()
  })

  // Getters
  const isActive = computed(() =>
    state.value.status !== 'idle'
  )

  const systemHealth = computed(() => {
    const avg = (metrics.value.cpu + metrics.value.memory) / 2
    if (avg > 90) return 'critical'
    if (avg > 70) return 'warning'
    return 'healthy'
  })

  // Actions
  function updateMetrics(newMetrics: Partial<SystemMetrics>) {
    // ✅ Validate input
    if (newMetrics.cpu !== undefined) {
      metrics.value.cpu = Math.max(0, Math.min(100, newMetrics.cpu))
    }
    if (newMetrics.memory !== undefined) {
      metrics.value.memory = Math.max(0, Math.min(100, newMetrics.memory))
    }
    if (newMetrics.network !== undefined) {
      metrics.value.network = Math.max(0, newMetrics.network)
    }
    metrics.value.timestamp = Date.now()
  }

  function setStatus(newStatus: JARVISState['status']) {
    state.value.status = newStatus
  }

  function setSecurityLevel(level: JARVISState['securityLevel']) {
    state.value.securityLevel = level

    // ✅ Audit security changes
    console.info(`Security level changed to: ${level}`)
  }

  return {
    state,
    metrics,
    isActive,
    systemHealth,
    updateMetrics,
    setStatus,
    setSecurityLevel
  }
})
```

### 4.2 User Preferences Store (with Persistence)

```typescript
// stores/preferences.ts
export const usePreferencesStore = defineStore('preferences', () => {
  const preferences = ref({
    theme: 'dark' as 'dark' | 'light',
    hudOpacity: 0.8,
    soundEnabled: true
  })

  function updatePreference<K extends keyof typeof preferences.value>(
    key: K, value: typeof preferences.value[K]
  ) {
    if (key === 'hudOpacity' && (value < 0 || value > 1)) return
    preferences.value[key] = value
  }

  return { preferences, updatePreference }
}, {
  persist: {
    key: 'jarvis-preferences',
    paths: ['preferences.theme', 'preferences.hudOpacity']
    // ❌ Never persist: tokens, passwords, API keys
  }
})
```

### 4.3 Command Queue Store

```typescript
// stores/commands.ts
interface Command {
  id: string
  action: string
  status: 'pending' | 'executing' | 'completed' | 'failed'
}

export const useCommandStore = defineStore('commands', () => {
  const queue = ref<Command[]>([])
  const history = ref<Command[]>([])
  const MAX_HISTORY = 100

  const pendingCommands = computed(() =>
    queue.value.filter(cmd => cmd.status === 'pending')
  )

  function addCommand(action: string) {
    const cmd: Command = { id: crypto.randomUUID(), action, status: 'pending' }
    queue.value.push(cmd)
    return cmd.id
  }

  function completeCommand(id: string, status: 'completed' | 'failed') {
    const idx = queue.value.findIndex(cmd => cmd.id === id)
    if (idx !== -1) {
      const [cmd] = queue.value.splice(idx, 1)
      cmd.status = status
      history.value = [cmd, ...history.value].slice(0, MAX_HISTORY)
    }
  }

  return { queue, history, pendingCommands, addCommand, completeCommand }
})
```

### 4.4 SSR-Safe Store Usage

```vue
<script setup lang="ts">
// ✅ Safe for SSR - store initialized per-request
const jarvisStore = useJarvisStore()

// ✅ Fetch data on server
const { data } = await useFetch('/api/metrics')

// Update store with fetched data
if (data.value) {
  jarvisStore.updateMetrics(data.value)
}
</script>
```

### 4.5 Store Composition

```typescript
// stores/dashboard.ts
export const useDashboardStore = defineStore('dashboard', () => {
  // ✅ Compose from other stores
  const jarvisStore = useJarvisStore()
  const commandStore = useCommandStore()

  const dashboardStatus = computed(() => ({
    systemHealth: jarvisStore.systemHealth,
    pendingCommands: commandStore.pendingCommands.length,
    isActive: jarvisStore.isActive
  }))

  return {
    dashboardStatus
  }
})
```

