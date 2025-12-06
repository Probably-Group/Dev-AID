## 3. Technical Foundation

### Color System

```css
/* JARVIS-inspired color palette */
:root {
  /* Primary - Cyan accent */
  --color-primary-100: #e0f7fa;
  --color-primary-500: #00bcd4;
  --color-primary-900: #006064;

  /* Surface - Glass effect base */
  --surface-glass: rgba(255, 255, 255, 0.08);
  --surface-glass-hover: rgba(255, 255, 255, 0.12);
  --surface-glass-active: rgba(255, 255, 255, 0.16);

  /* Status colors */
  --color-success: #4caf50;
  --color-warning: #ff9800;
  --color-error: #f44336;
  --color-info: #2196f3;

  /* Text - WCAG AA compliant */
  --text-primary: rgba(255, 255, 255, 0.95);
  --text-secondary: rgba(255, 255, 255, 0.7);
  --text-disabled: rgba(255, 255, 255, 0.38);
}
```

### Typography Scale

```css
/* Modular type scale (1.25 ratio) */
:root {
  --font-size-xs: 0.64rem;    /* 10.24px */
  --font-size-sm: 0.8rem;     /* 12.8px */
  --font-size-base: 1rem;     /* 16px */
  --font-size-lg: 1.25rem;    /* 20px */
  --font-size-xl: 1.563rem;   /* 25px */
  --font-size-2xl: 1.953rem;  /* 31.25px */
  --font-size-3xl: 2.441rem;  /* 39.06px */

  /* Line heights */
  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;
}

/* Font families */
body {
  font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
}

code {
  font-family: "JetBrains Mono", "Fira Code", monospace;
}
```

### Spacing System

```css
/* 8px base grid */
:root {
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.5rem;    /* 24px */
  --space-6: 2rem;      /* 32px */
  --space-8: 3rem;      /* 48px */
  --space-10: 4rem;     /* 64px */
}
```

### Responsive Breakpoints

```css
/* Mobile-first breakpoints */
:root {
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
  --breakpoint-2xl: 1536px;
}
```

---


