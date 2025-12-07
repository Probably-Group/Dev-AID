## 5. Implementation Patterns

### 4.1 Token Architecture

```css
/* tokens/core.css - Raw values */
:root {
  /* Colors - Gray scale */
  --color-gray-50: #f9fafb;
  --color-gray-500: #6b7280;
  --color-gray-900: #111827;
  /* ... gray-100 through gray-800 */

  /* Colors - Blue scale */
  --color-blue-500: #3b82f6;
  --color-blue-600: #2563eb;

  /* Spacing (8px base): --space-0 through --space-16 */
  --space-4: 1rem;
  --space-6: 1.5rem;

  /* Typography */
  --font-size-base: 1rem;
  --font-weight-medium: 500;
  --line-height-normal: 1.5;

  /* Radii */
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;

  /* Shadows */
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
}
```

```css
/* tokens/semantic.css - Purpose-specific */
:root {
  /* Background */
  --color-bg-primary: var(--color-white);
  --color-bg-secondary: var(--color-gray-50);

  /* Text */
  --color-text-primary: var(--color-gray-900);
  --color-text-secondary: var(--color-gray-600);

  /* Border & Interactive */
  --color-border-default: var(--color-gray-200);
  --color-interactive-primary: var(--color-blue-600);

  /* Component spacing */
  --spacing-component-md: var(--space-3);
  --spacing-component-lg: var(--space-4);
}
```

### 4.2 Theme Switching

```css
/* themes/light.css */
:root,
[data-theme="light"] {
  --color-bg-primary: var(--color-white);
  --color-text-primary: var(--color-gray-900);
  --color-border-default: var(--color-gray-200);
}

/* themes/dark.css */
[data-theme="dark"] {
  --color-bg-primary: var(--color-gray-900);
  --color-text-primary: var(--color-gray-50);
  --color-border-default: var(--color-gray-700);
}
```

```typescript
// Theme switcher (condensed)
function ThemeProvider({ children }: Props) {
  const [theme, setTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    const saved = localStorage.getItem("theme") as "light" | "dark" | null;
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)");
    setTheme(saved || (prefersDark.matches ? "dark" : "light"));
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  const toggle = () => {
    const next = theme === "light" ? "dark" : "light";
    setTheme(next);
    localStorage.setItem("theme", next);
  };

  return (
    <ThemeContext.Provider value={{ theme, toggle }}>
      {children}
    </ThemeContext.Provider>
  );
}
```

### 4.3 Component API Design

```typescript
// Consistent prop patterns
interface ButtonProps {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  disabled?: boolean;
  loading?: boolean;
  children: ReactNode;
  onClick?: () => void;
}

function Button({ variant = "primary", size = "md", ...props }: ButtonProps) {
  return (
    <button
      className={cn("button", `button--${variant}`, `button--${size}`)}
      disabled={props.disabled || props.loading}
      onClick={props.onClick}
    >
      {props.children}
    </button>
  );
}
```

### 4.4 Composition Patterns

```typescript
// Compound components
function Card({ children }: { children: ReactNode }) {
  return <div className="card">{children}</div>;
}
Card.Header = ({ children }) => <div className="card-header">{children}</div>;
Card.Body = ({ children }) => <div className="card-body">{children}</div>;
Card.Footer = ({ children }) => <div className="card-footer">{children}</div>;

// Usage: <Card><Card.Header>Title</Card.Header><Card.Body>...</Card.Body></Card>
```

### 4.5 Token Export Formats

```typescript
// Export tokens in multiple formats
const tokens = {
  colors: { primary: "#3b82f6", secondary: "#6b7280" },
  spacing: { sm: "8px", md: "16px", lg: "24px" }
};

// CSS Custom Properties
function toCSS(tokens: Tokens): string {
  let css = ":root {\n";
  for (const [category, values] of Object.entries(tokens)) {
    for (const [key, value] of Object.entries(values))
      css += `  --${category}-${key}: ${value};\n`;
  }
  return css + "}";
}

// Tailwind config
function toTailwind(tokens: Tokens): TailwindConfig {
  return { theme: { extend: { colors: tokens.colors, spacing: tokens.spacing } } };
}
```

---

