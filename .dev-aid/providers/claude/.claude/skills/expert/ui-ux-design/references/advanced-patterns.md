# UI/UX Advanced Patterns

## HUD Layout Structure

### Use Case
Creating heads-up display (HUD) interfaces for AI assistants and futuristic applications.

**Implementation**:
```html
<!-- Main HUD container -->
<div class="hud-container">
  <!-- Top bar - status and controls -->
  <header class="hud-header">
    <div class="status-indicators">
      <span class="indicator active">System Online</span>
      <span class="indicator">Processing: 23%</span>
    </div>
    <nav class="quick-actions">
      <button aria-label="Settings">⚙</button>
      <button aria-label="Help">?</button>
    </nav>
  </header>

  <!-- Main content area -->
  <main class="hud-main">
    <!-- Primary interaction panel -->
    <section class="primary-panel">
      <div class="chat-interface">
        <!-- Conversation display -->
      </div>
      <div class="input-area">
        <!-- User input -->
      </div>
    </section>

    <!-- Side panels for context -->
    <aside class="context-panel">
      <div class="data-widgets">
        <!-- Status widgets -->
      </div>
    </aside>
  </main>

  <!-- Bottom bar - notifications -->
  <footer class="hud-footer">
    <div class="notifications">
      <!-- System notifications -->
    </div>
  </footer>
</div>
```

**Styling**:
```css
.hud-container {
  display: grid;
  grid-template-rows: auto 1fr auto;
  height: 100vh;
  background: linear-gradient(135deg, #0a0e1a 0%, #1a1f2e 100%);
}

.hud-header,
.hud-footer {
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: var(--space-4);
}

.hud-main {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: var(--space-4);
  padding: var(--space-4);
  overflow: hidden;
}

@media (max-width: 768px) {
  .hud-main {
    grid-template-columns: 1fr;
  }

  .context-panel {
    display: none;
  }
}
```

---

## Attention Management System

### Use Case
Prioritize notifications and information based on importance without overwhelming users.

**Implementation**:
```typescript
// Attention priority queue
interface AttentionItem {
  id: string;
  priority: "critical" | "high" | "normal" | "low";
  content: string;
  duration?: number;
  timestamp: number;
}

class AttentionManager {
  private queue: AttentionItem[] = [];
  private activeItem: AttentionItem | null = null;

  add(item: Omit<AttentionItem, 'id' | 'timestamp'>): void {
    const newItem: AttentionItem = {
      ...item,
      id: crypto.randomUUID(),
      timestamp: Date.now()
    };

    // Insert by priority
    const index = this.queue.findIndex(i =>
      this.getPriorityValue(i.priority) < this.getPriorityValue(newItem.priority)
    );

    if (index === -1) {
      this.queue.push(newItem);
    } else {
      this.queue.splice(index, 0, newItem);
    }

    this.notify();
  }

  private getPriorityValue(priority: string): number {
    const values = { critical: 4, high: 3, normal: 2, low: 1 };
    return values[priority] || 0;
  }

  private notify(): void {
    if (this.activeItem) return; // Don't interrupt active item

    const next = this.queue.shift();
    if (!next) return;

    this.activeItem = next;
    this.display(next);

    // Auto-dismiss after duration
    if (next.duration) {
      setTimeout(() => {
        this.dismiss(next.id);
      }, next.duration);
    }
  }

  private display(item: AttentionItem): void {
    // Emit event for UI to handle
    window.dispatchEvent(new CustomEvent('attention:show', {
      detail: item
    }));
  }

  dismiss(id: string): void {
    if (this.activeItem?.id === id) {
      this.activeItem = null;
      this.notify(); // Show next item
    }
  }
}
```

**Visual Priority Levels**:
```css
/* Priority levels through visual weight */

/* Critical - highest attention */
.priority-critical {
  color: var(--color-error);
  font-weight: 700;
  font-size: var(--font-size-lg);
  animation: pulse 1s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.9;
    transform: scale(1.02);
  }
}

/* High - significant attention */
.priority-high {
  color: var(--color-warning);
  font-weight: 600;
  font-size: var(--font-size-base);
}

/* Normal - default */
.priority-normal {
  color: var(--text-primary);
  font-weight: 400;
}

/* Low - reduced attention */
.priority-low {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

/* Ambient - minimal attention */
.priority-ambient {
  color: var(--text-disabled);
  font-size: var(--font-size-xs);
}
```

**Usage**:
```typescript
const attention = new AttentionManager();

// Critical system alert
attention.add({
  priority: 'critical',
  content: 'System error detected',
  duration: 0 // Requires manual dismissal
});

// Normal notification
attention.add({
  priority: 'normal',
  content: 'Task completed',
  duration: 5000
});

// Low priority update
attention.add({
  priority: 'low',
  content: 'New message',
  duration: 3000
});
```

---

## Micro-Interactions

```css
/* Button press feedback */
.button {
  transition: transform 0.1s ease, box-shadow 0.1s ease;
}

.button:active {
  transform: scale(0.98);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
}

/* Input focus */
.input {
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input:focus {
  border-color: var(--color-primary-500);
  box-shadow: 0 0 0 3px rgba(0, 188, 212, 0.2);
}
```

## Progressive Loading

```tsx
// Skeleton loading pattern
function DataDisplay({ data, loading }: Props) {
  if (loading) {
    return (
      <div className="skeleton-container">
        <div className="skeleton skeleton-title" />
        <div className="skeleton skeleton-text" />
        <div className="skeleton skeleton-text" />
      </div>
    );
  }

  return <Content data={data} />;
}

// CSS
.skeleton {
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.1) 25%,
    rgba(255, 255, 255, 0.2) 50%,
    rgba(255, 255, 255, 0.1) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

## Data Visualization

```tsx
// Circular progress indicator
function CircularProgress({ value, max, size = 100 }: Props) {
  const percentage = (value / max) * 100;
  const circumference = 2 * Math.PI * 40;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <svg width={size} height={size} viewBox="0 0 100 100">
      {/* Background circle */}
      <circle
        cx="50" cy="50" r="40"
        fill="none"
        stroke="rgba(255,255,255,0.1)"
        strokeWidth="8"
      />
      {/* Progress circle */}
      <circle
        cx="50" cy="50" r="40"
        fill="none"
        stroke="var(--color-primary-500)"
        strokeWidth="8"
        strokeLinecap="round"
        strokeDasharray={circumference}
        strokeDashoffset={strokeDashoffset}
        transform="rotate(-90 50 50)"
      />
      {/* Value text */}
      <text
        x="50" y="50"
        textAnchor="middle"
        dominantBaseline="middle"
        fill="var(--text-primary)"
        fontSize="20"
      >
        {Math.round(percentage)}%
      </text>
    </svg>
  );
}
```

## Contextual Menus

```tsx
// Right-click context menu
function ContextMenu({ items, position, onClose }: Props) {
  return (
    <div
      className="context-menu glass-card"
      style={{ left: position.x, top: position.y }}
      onBlur={onClose}
    >
      {items.map(item => (
        <button
          key={item.id}
          className="context-menu-item"
          onClick={() => {
            item.action();
            onClose();
          }}
        >
          {item.icon && <span className="icon">{item.icon}</span>}
          <span className="label">{item.label}</span>
          {item.shortcut && <span className="shortcut">{item.shortcut}</span>}
        </button>
      ))}
    </div>
  );
}
```

## Notification Toast System

```tsx
// Toast notification manager
const ToastContext = createContext<ToastManager>(null);

function ToastProvider({ children }: Props) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = (toast: Omit<Toast, 'id'>) => {
    const id = crypto.randomUUID();
    setToasts(prev => [...prev, { ...toast, id }]);

    if (toast.duration !== 0) {
      setTimeout(() => removeToast(id), toast.duration || 5000);
    }
  };

  return (
    <ToastContext.Provider value={{ addToast, removeToast }}>
      {children}
      <div className="toast-container">
        {toasts.map(toast => (
          <Toast key={toast.id} {...toast} onClose={() => removeToast(toast.id)} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}
```

## Drag and Drop

```tsx
// Sortable list with drag and drop
function SortableList({ items, onReorder }: Props) {
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);

  const handleDragStart = (index: number) => {
    setDraggedIndex(index);
  };

  const handleDragOver = (e: DragEvent, index: number) => {
    e.preventDefault();
    if (draggedIndex === null || draggedIndex === index) return;

    const newItems = [...items];
    const [removed] = newItems.splice(draggedIndex, 1);
    newItems.splice(index, 0, removed);

    onReorder(newItems);
    setDraggedIndex(index);
  };

  return (
    <ul className="sortable-list">
      {items.map((item, index) => (
        <li
          key={item.id}
          draggable
          onDragStart={() => handleDragStart(index)}
          onDragOver={(e) => handleDragOver(e, index)}
          className={draggedIndex === index ? 'dragging' : ''}
        >
          {item.content}
        </li>
      ))}
    </ul>
  );
}
```
