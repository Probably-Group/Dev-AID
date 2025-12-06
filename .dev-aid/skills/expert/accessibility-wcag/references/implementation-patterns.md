## 6. Implementation Patterns

### 5.1 Semantic HTML

```html
<!-- Correct landmark usage -->
<header>
  <nav aria-label="Main navigation">
    <ul>
      <li><a href="/">Home</a></li>
      <li><a href="/about">About</a></li>
    </ul>
  </nav>
</header>

<main>
  <article>
    <h1>Page Title</h1>
    <section aria-labelledby="section-heading">
      <h2 id="section-heading">Section Title</h2>
      <p>Content...</p>
    </section>
  </article>
</main>

<footer>
  <!-- Footer content -->
</footer>
```

### 5.2 Form Accessibility

```html
<form>
  <div>
    <label for="email">Email address</label>
    <input
      type="email"
      id="email"
      name="email"
      autocomplete="email"
      aria-required="true"
      aria-describedby="email-hint email-error"
    />
    <p id="email-hint" class="hint">We'll never share your email</p>
    <p id="email-error" class="error" aria-live="polite"></p>
  </div>
  <button type="submit">Save preferences</button>
</form>
```

### 5.3 Live Regions

```html
<!-- Status updates (polite, non-interrupting) -->
<div role="status" aria-live="polite" aria-atomic="true">
  <!-- Status messages appear here -->
</div>

<!-- Alert messages (assertive, interrupting) -->
<div role="alert" aria-live="assertive">
  <!-- Critical alerts appear here -->
</div>
```

### 5.4 Focus Management

```typescript
// Focus trap for modal
function trapFocus(element: HTMLElement) {
  const focusable = element.querySelectorAll<HTMLElement>(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  )
  const firstFocusable = focusable[0]
  const lastFocusable = focusable[focusable.length - 1]

  function handleKeyDown(e: KeyboardEvent) {
    if (e.key !== 'Tab') return

    if (e.shiftKey && document.activeElement === firstFocusable) {
      e.preventDefault()
      lastFocusable.focus()
    } else if (!e.shiftKey && document.activeElement === lastFocusable) {
      e.preventDefault()
      firstFocusable.focus()
    }
  }

  element.addEventListener('keydown', handleKeyDown)
  return () => element.removeEventListener('keydown', handleKeyDown)
}
```

### 5.5 Focus Styles

```css
/* Use :focus-visible for better UX */
:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}

:focus:not(:focus-visible) {
  outline: none;
}
```

### 5.6 Reduced Motion

```css
/* Respect user motion preferences */
.animated-element {
  animation: slide-in 0.5s ease-out;
}

@media (prefers-reduced-motion: reduce) {
  .animated-element {
    animation: none;
    transition: none;
  }
}
```

---

