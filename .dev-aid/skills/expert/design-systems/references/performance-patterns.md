## 8. Performance Patterns

### 7.1 CSS Custom Properties Optimization

**Bad** - Redundant property declarations:
```css
.button { background: var(--color-blue-500); }
.button:hover { background: var(--color-blue-600); }
.button:active { background: var(--color-blue-700); }
```

**Good** - Single property with state modifiers:
```css
.button {
  --button-bg: var(--color-blue-500);
  background: var(--button-bg);
}
.button:hover { --button-bg: var(--color-blue-600); }
.button:active { --button-bg: var(--color-blue-700); }
```

### 7.2 Tree-Shaking Token Exports

**Bad** - Importing entire token object:
```typescript
import { tokens } from './tokens'
const primary = tokens.colors.blue[500]
```

**Good** - Named exports for tree-shaking:
```typescript
import { colorBlue500 } from './tokens/colors'
const primary = colorBlue500
```

### 7.3 Lazy Loading Theme Files

**Bad** - Loading all themes upfront:
```typescript
import './themes/light.css'
import './themes/dark.css'
import './themes/high-contrast.css'
```

**Good** - Dynamic theme loading:
```typescript
async function loadTheme(theme: string) {
  await import(`./themes/${theme}.css`)
  document.documentElement.dataset.theme = theme
}
```

### 7.4 Token Computation Optimization

**Bad** - Runtime calculations:
```css
.card { padding: calc(var(--space-4) * 1.5); }
```

**Good** - Pre-computed semantic tokens:
```css
:root { --spacing-card: 1.5rem; }
.card { padding: var(--spacing-card); }
```

### 7.5 Responsive Image Tokens

**Bad** - Fixed image sizes:
```css
.avatar { width: 48px; height: 48px; }
```

**Good** - Token-based responsive sizing:
```css
:root {
  --avatar-size-sm: 2rem;
  --avatar-size-md: 3rem;
  --avatar-size-lg: 4rem;
}
.avatar { width: var(--avatar-size-md); aspect-ratio: 1; }
```

---

