---
name: design-systems
version: 2.0.0
description: "Design system architecture with token-based theming, component APIs, and cross-platform consistency. Use when building design systems, defining design tokens, or creating component libraries. Do NOT use for individual component styling (use tailwindcss)."
risk_level: LOW
token_budget: 4500
---
# Design Systems - Code Generation Rules

---

## 1. Security Principles

### 1.1 XSS Prevention in Dynamic Theming (CWE-79)

**Principle:** Never interpolate user input into CSS or style attributes.

```typescript
// ❌ WRONG - CSS injection vulnerability
const Theme = ({ userColor }) => (
  <style>{`
    .button { background: ${userColor}; }
  `}</style>
);

// ✅ CORRECT - Validated CSS custom properties
const VALID_COLORS = ['primary', 'secondary', 'accent'] as const;
type ValidColor = typeof VALID_COLORS[number];

function isValidColor(color: string): color is ValidColor {
  return VALID_COLORS.includes(color as ValidColor);
}

const Theme = ({ colorKey }: { colorKey: string }) => {
  if (!isValidColor(colorKey)) {
    throw new Error(`Invalid color key: ${colorKey}`);
  }

  return (
    <div style={{ '--button-bg': `var(--color-${colorKey})` } as React.CSSProperties}>
      {children}
    </div>
  );
};
```

### 1.2 Content Security Policy (CWE-1021)

**Principle:** Design systems must support strict CSP. No inline styles where avoidable.

```typescript
// ❌ WRONG - Inline styles break CSP
<div style="background: red">

// ✅ CORRECT - CSS classes or CSS custom properties
<div className={styles.errorBackground}>
// or
<div style={{ backgroundColor: 'var(--color-error)' }}>
```

### 1.3 Token Validation (CWE-20)

**Principle:** Validate all design tokens at build time. Reject invalid values.

### 1.4 Dependency Security (CWE-1104)

**Principle:** Audit CSS-in-JS libraries for prototype pollution and injection risks.

### 1.5 Asset Integrity (CWE-353)

**Principle:** Use SRI for external fonts and stylesheets.

### 1.6 Accessible by Default

**Principle:** All components must meet WCAG 2.1 AA. Never compromise accessibility for styling.

---

## 2. Version Requirements

Use these minimum versions:

```json
{
  "@vanilla-extract/css": "^1.14.0",
  "@vanilla-extract/recipes": "^0.5.0",
  "style-dictionary": "^4.0.0",
  "radix-ui": "^1.0.0",
  "tailwindcss": "^3.4.0",
  "clsx": "^2.0.0"
}
```

---

## 3. Code Patterns

### 3.1 WHEN defining design tokens

```typescript
// ❌ WRONG - Unstructured, no type safety
const colors = {
  blue: '#0066cc',
  red: '#cc0000',
};

// ✅ CORRECT - Structured, type-safe tokens with Style Dictionary
// tokens/base/colors.json
{
  "color": {
    "base": {
      "blue": {
        "50": { "value": "#eff6ff", "type": "color" },
        "100": { "value": "#dbeafe", "type": "color" },
        "500": { "value": "#3b82f6", "type": "color" },
        "900": { "value": "#1e3a8a", "type": "color" }
      }
    },
    "semantic": {
      "primary": {
        "value": "{color.base.blue.500}",
        "type": "color",
        "description": "Primary brand color"
      },
      "primary-hover": {
        "value": "{color.base.blue.600}",
        "type": "color"
      }
    },
    "component": {
      "button": {
        "primary": {
          "background": { "value": "{color.semantic.primary}" },
          "background-hover": { "value": "{color.semantic.primary-hover}" },
          "text": { "value": "{color.base.white}" }
        }
      }
    }
  }
}

// style-dictionary.config.js
import StyleDictionary from 'style-dictionary';

export default {
  source: ['tokens/**/*.json'],
  platforms: {
    css: {
      transformGroup: 'css',
      buildPath: 'dist/css/',
      files: [{
        destination: 'variables.css',
        format: 'css/variables',
        options: {
          outputReferences: true,
        },
      }],
    },
    typescript: {
      transformGroup: 'js',
      buildPath: 'dist/ts/',
      files: [{
        destination: 'tokens.ts',
        format: 'javascript/es6',
      }],
    },
  },
};
```

### 3.2 WHEN creating component variants with Vanilla Extract

```typescript
// ❌ WRONG - String-based variants, no type safety
const Button = ({ variant }) => (
  <button className={`btn-${variant}`}>  {/* No validation! */}
    {children}
  </button>
);

// ✅ CORRECT - Type-safe variants with recipes
// button.css.ts
import { recipe, RecipeVariants } from '@vanilla-extract/recipes';
import { tokens } from '../tokens.css';

export const button = recipe({
  base: {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: tokens.radius.md,
    fontWeight: tokens.fontWeight.medium,
    transition: 'all 150ms ease',
    cursor: 'pointer',

    ':focus-visible': {
      outline: `2px solid ${tokens.color.focus}`,
      outlineOffset: '2px',
    },

    ':disabled': {
      opacity: 0.5,
      cursor: 'not-allowed',
    },
  },

  variants: {
    intent: {
      primary: {
        backgroundColor: tokens.color.primary,
        color: tokens.color.onPrimary,
        ':hover:not(:disabled)': {
          backgroundColor: tokens.color.primaryHover,
        },
      },
      secondary: {
        backgroundColor: 'transparent',
        color: tokens.color.primary,
        border: `1px solid ${tokens.color.primary}`,
        ':hover:not(:disabled)': {
          backgroundColor: tokens.color.primaryLight,
        },
      },
      danger: {
        backgroundColor: tokens.color.error,
        color: tokens.color.onError,
        ':hover:not(:disabled)': {
          backgroundColor: tokens.color.errorHover,
        },
      },
    },

    size: {
      sm: {
        height: '32px',
        paddingInline: tokens.space[3],
        fontSize: tokens.fontSize.sm,
      },
      md: {
        height: '40px',
        paddingInline: tokens.space[4],
        fontSize: tokens.fontSize.base,
      },
      lg: {
        height: '48px',
        paddingInline: tokens.space[6],
        fontSize: tokens.fontSize.lg,
      },
    },

    fullWidth: {
      true: { width: '100%' },
    },
  },

  defaultVariants: {
    intent: 'primary',
    size: 'md',
  },

  compoundVariants: [
    {
      variants: { intent: 'secondary', size: 'sm' },
      style: { paddingInline: tokens.space[2] },
    },
  ],
});

export type ButtonVariants = RecipeVariants<typeof button>;

// Button.tsx
import { button, ButtonVariants } from './button.css';
import { clsx } from 'clsx';

interface ButtonProps extends ButtonVariants {
  children: React.ReactNode;
  className?: string;
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
}

export function Button({
  children,
  className,
  intent,
  size,
  fullWidth,
  disabled,
  type = 'button',
  ...props
}: ButtonProps) {
  return (
    <button
      type={type}
      disabled={disabled}
      className={clsx(button({ intent, size, fullWidth }), className)}
      {...props}
    >
      {children}
    </button>
  );
}
```

### 3.3 WHEN implementing dark mode

```typescript
// ❌ WRONG - Hardcoded theme values
const Button = styled.button`
  background: ${props => props.theme === 'dark' ? '#333' : '#fff'};
`;

// ✅ CORRECT - CSS custom properties with theme tokens
// theme.css.ts
import { createTheme, createThemeContract } from '@vanilla-extract/css';

// Define the contract (shape of theme)
export const themeContract = createThemeContract({
  color: {
    background: null,
    surface: null,
    text: {
      primary: null,
      secondary: null,
      muted: null,
    },
    border: null,
    focus: null,
  },
  shadow: {
    sm: null,
    md: null,
    lg: null,
  },
});

// Light theme implementation
export const lightTheme = createTheme(themeContract, {
  color: {
    background: '#ffffff',
    surface: '#f8fafc',
    text: {
      primary: '#0f172a',
      secondary: '#475569',
      muted: '#94a3b8',
    },
    border: '#e2e8f0',
    focus: '#3b82f6',
  },
  shadow: {
    sm: '0 1px 2px rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px rgba(0, 0, 0, 0.1)',
  },
});

// Dark theme implementation
export const darkTheme = createTheme(themeContract, {
  color: {
    background: '#0f172a',
    surface: '#1e293b',
    text: {
      primary: '#f8fafc',
      secondary: '#cbd5e1',
      muted: '#64748b',
    },
    border: '#334155',
    focus: '#60a5fa',
  },
  shadow: {
    sm: '0 1px 2px rgba(0, 0, 0, 0.3)',
    md: '0 4px 6px rgba(0, 0, 0, 0.4)',
    lg: '0 10px 15px rgba(0, 0, 0, 0.5)',
  },
});

// ThemeProvider.tsx
import { useEffect, useState } from 'react';
import { lightTheme, darkTheme } from './theme.css';

type Theme = 'light' | 'dark' | 'system';

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>('system');

  useEffect(() => {
    const root = document.documentElement;

    // Remove existing theme classes
    root.classList.remove(lightTheme, darkTheme);

    if (theme === 'system') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      root.classList.add(prefersDark ? darkTheme : lightTheme);
    } else {
      root.classList.add(theme === 'dark' ? darkTheme : lightTheme);
    }
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}
```

### 3.4 WHEN building accessible components with Radix

```typescript
// ❌ WRONG - Custom implementation without a11y
const Dropdown = ({ items }) => {
  const [open, setOpen] = useState(false);
  return (
    <div onClick={() => setOpen(!open)}>
      {open && items.map(item => <div key={item}>{item}</div>)}
    </div>
  );
};

// ✅ CORRECT - Radix primitives with design system styling
import * as DropdownMenu from '@radix-ui/react-dropdown-menu';
import { dropdownStyles } from './dropdown.css';

interface DropdownItem {
  label: string;
  onSelect: () => void;
  icon?: React.ReactNode;
  disabled?: boolean;
  destructive?: boolean;
}

interface DropdownProps {
  trigger: React.ReactNode;
  items: DropdownItem[];
  align?: 'start' | 'center' | 'end';
}

export function Dropdown({ trigger, items, align = 'end' }: DropdownProps) {
  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        {trigger}
      </DropdownMenu.Trigger>

      <DropdownMenu.Portal>
        <DropdownMenu.Content
          className={dropdownStyles.content}
          align={align}
          sideOffset={4}
        >
          {items.map((item, index) => (
            <DropdownMenu.Item
              key={index}
              className={dropdownStyles.item({
                destructive: item.destructive,
              })}
              disabled={item.disabled}
              onSelect={item.onSelect}
            >
              {item.icon && (
                <span className={dropdownStyles.itemIcon}>{item.icon}</span>
              )}
              {item.label}
            </DropdownMenu.Item>
          ))}
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  );
}

// dropdown.css.ts
import { style } from '@vanilla-extract/css';
import { recipe } from '@vanilla-extract/recipes';
import { themeContract } from './theme.css';

export const dropdownStyles = {
  content: style({
    minWidth: '180px',
    backgroundColor: themeContract.color.surface,
    borderRadius: '8px',
    padding: '4px',
    boxShadow: themeContract.shadow.lg,
    border: `1px solid ${themeContract.color.border}`,

    // Animation
    animationDuration: '150ms',
    animationTimingFunction: 'cubic-bezier(0.16, 1, 0.3, 1)',

    selectors: {
      '&[data-state="open"]': {
        animationName: 'fadeIn, slideDown',
      },
    },
  }),

  item: recipe({
    base: {
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      padding: '8px 12px',
      borderRadius: '4px',
      fontSize: '14px',
      color: themeContract.color.text.primary,
      cursor: 'pointer',
      outline: 'none',

      selectors: {
        '&[data-highlighted]': {
          backgroundColor: themeContract.color.background,
        },
        '&[data-disabled]': {
          color: themeContract.color.text.muted,
          cursor: 'not-allowed',
        },
      },
    },

    variants: {
      destructive: {
        true: {
          color: 'var(--color-error)',
          selectors: {
            '&[data-highlighted]': {
              backgroundColor: 'var(--color-error-light)',
            },
          },
        },
      },
    },
  }),

  itemIcon: style({
    width: '16px',
    height: '16px',
    flexShrink: 0,
  }),
};
```

### 3.5 WHEN creating spacing and layout utilities

```typescript
// ❌ WRONG - Magic numbers, inconsistent spacing
<div style={{ margin: '17px', padding: '13px' }}>

// ✅ CORRECT - Design token-based spacing scale
// tokens/spacing.ts
export const spacing = {
  0: '0px',
  px: '1px',
  0.5: '2px',
  1: '4px',
  1.5: '6px',
  2: '8px',
  2.5: '10px',
  3: '12px',
  4: '16px',
  5: '20px',
  6: '24px',
  8: '32px',
  10: '40px',
  12: '48px',
  16: '64px',
  20: '80px',
  24: '96px',
} as const;

// sprinkles.css.ts (Vanilla Extract Sprinkles)
import { defineProperties, createSprinkles } from '@vanilla-extract/sprinkles';
import { spacing } from './tokens/spacing';
import { themeContract } from './theme.css';

const responsiveProperties = defineProperties({
  conditions: {
    mobile: {},
    tablet: { '@media': 'screen and (min-width: 768px)' },
    desktop: { '@media': 'screen and (min-width: 1024px)' },
  },
  defaultCondition: 'mobile',
  properties: {
    display: ['none', 'flex', 'grid', 'block', 'inline-flex'],
    flexDirection: ['row', 'column', 'row-reverse', 'column-reverse'],
    alignItems: ['stretch', 'flex-start', 'center', 'flex-end', 'baseline'],
    justifyContent: ['flex-start', 'center', 'flex-end', 'space-between', 'space-around'],
    gap: spacing,
    padding: spacing,
    paddingTop: spacing,
    paddingBottom: spacing,
    paddingLeft: spacing,
    paddingRight: spacing,
    margin: spacing,
    marginTop: spacing,
    marginBottom: spacing,
    marginLeft: spacing,
    marginRight: spacing,
  },
  shorthands: {
    p: ['padding'],
    px: ['paddingLeft', 'paddingRight'],
    py: ['paddingTop', 'paddingBottom'],
    m: ['margin'],
    mx: ['marginLeft', 'marginRight'],
    my: ['marginTop', 'marginBottom'],
  },
});

const colorProperties = defineProperties({
  conditions: {
    default: {},
    hover: { selector: '&:hover' },
    focus: { selector: '&:focus' },
  },
  defaultCondition: 'default',
  properties: {
    color: themeContract.color.text,
    backgroundColor: {
      ...themeContract.color,
      transparent: 'transparent',
    },
  },
});

export const sprinkles = createSprinkles(responsiveProperties, colorProperties);
export type Sprinkles = Parameters<typeof sprinkles>[0];

// Box.tsx - Polymorphic box with sprinkles
import { sprinkles, Sprinkles } from './sprinkles.css';

type BoxProps<T extends React.ElementType = 'div'> = {
  as?: T;
  children?: React.ReactNode;
} & Sprinkles &
  Omit<React.ComponentPropsWithoutRef<T>, keyof Sprinkles>;

export function Box<T extends React.ElementType = 'div'>({
  as,
  children,
  className,
  ...props
}: BoxProps<T>) {
  const Component = as || 'div';

  // Separate sprinkle props from native props
  const sprinkleProps: Record<string, unknown> = {};
  const nativeProps: Record<string, unknown> = {};

  for (const [key, value] of Object.entries(props)) {
    if (key in sprinkles.properties) {
      sprinkleProps[key] = value;
    } else {
      nativeProps[key] = value;
    }
  }

  return (
    <Component
      className={clsx(sprinkles(sprinkleProps as Sprinkles), className)}
      {...nativeProps}
    >
      {children}
    </Component>
  );
}
```

---

## 4. Anti-Patterns

Do not:
- Use magic numbers for spacing/sizing
- Interpolate user input into styles
- Skip dark mode support in new components
- Create components without keyboard navigation
- Use color alone to convey information
- Hardcode colors instead of tokens
- Skip focus indicators
- Create non-responsive components

---

## 5. Testing

**ALWAYS test design system components:**

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

describe('Button', () => {
# ... (additional test cases follow same pattern)
```

---

## 6. Pre-Generation Checklist

Before generating any design system code:

- [ ] Tokens defined in structured format (Style Dictionary)
- [ ] Type-safe variant system (recipes or similar)
- [ ] Dark mode support via CSS custom properties
- [ ] Accessible primitives (Radix or equivalent)
- [ ] Spacing scale is consistent
- [ ] No inline styles with user input
- [ ] Focus indicators on all interactive elements
- [ ] Responsive breakpoints defined
- [ ] Color contrast meets WCAG AA
- [ ] Components tested with axe

---
