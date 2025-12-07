## 5. Core Implementation Patterns

### 4.1 Glass-Morphism Card

```css
.glass-card {
  /* Glass effect */
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);

  /* Border for definition */
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 12px;

  /* Subtle shadow */
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);

  /* Padding */
  padding: var(--space-4);
}

.glass-card:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.2);
}
```

### 4.2 Accessible Focus States

```css
/* Focus visible - WCAG 2.1 compliant */
:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

