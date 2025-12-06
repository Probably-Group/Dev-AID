## 5. Implementation Patterns

### 4.1 Enter/Exit Animations

```css
/* Slide up and fade */
@keyframes slideUpFadeIn {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Usage */
.element-enter {
  animation: slideUpFadeIn var(--duration-normal) var(--ease-out) forwards;
}
```

### 4.2 Spring Physics

```typescript
// Spring presets for natural motion
const springPresets = {
  gentle: { stiffness: 120, damping: 14 },
  wobbly: { stiffness: 180, damping: 12 },
  stiff: { stiffness: 400, damping: 30 },
  default: { stiffness: 300, damping: 20 }
};
```

### 4.3 Loading States

```css
/* Pulse animation */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
.loading-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Spinner */
@keyframes spin {
  to { transform: rotate(360deg); }
}
.spinner {
  animation: spin 1s linear infinite;
}
```

### 4.4 HUD Effects

```css
/* Glow pulse */
@keyframes glowPulse {
  0%, 100% { box-shadow: 0 0 10px var(--color-primary-500); }
  50% { box-shadow: 0 0 20px var(--color-primary-500), 0 0 30px var(--color-primary-500); }
}
.hud-glow {
  animation: glowPulse 2s ease-in-out infinite;
}
```

### 4.5 Staggered Animations

```typescript
// Stagger by 50ms per item
const staggerDelay = (index: number) => index * 0.05
```

### 4.6 Reduced Motion Support

```css
/* Disable animations for reduced motion preference */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

