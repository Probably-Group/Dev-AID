# Accessibility Testing Guide

## Automated Testing

### 1. jest-axe / vitest-axe

**Setup**:
```bash
npm install --save-dev jest-axe @axe-core/react
# or
npm install --save-dev vitest-axe
```

**Basic test**:
```typescript
import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/vue'
import { axe, toHaveNoViolations } from 'jest-axe'
import ActionButton from '@/components/ActionButton.vue'

expect.extend(toHaveNoViolations)

describe('ActionButton Accessibility', () => {
  it('should have no accessibility violations', async () => {
    const { container } = render(ActionButton, {
      props: { label: 'Submit Form' }
    })

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
```

**Advanced configuration**:
```typescript
it('should pass custom axe rules', async () => {
  const { container } = render(MyComponent)

  const results = await axe(container, {
    rules: {
      'color-contrast': { enabled: true },
      'label': { enabled: true }
    }
  })

  expect(results).toHaveNoViolations()
})
```

---

### 2. Testing Library Queries

**Use semantic queries**:
```typescript
import { render, screen } from '@testing-library/vue'

describe('Form Accessibility', () => {
  it('should have accessible form fields', () => {
    render(LoginForm)

    // Good: Query by role
    const emailInput = screen.getByRole('textbox', { name: 'Email' })
    const submitButton = screen.getByRole('button', { name: 'Sign in' })

    expect(emailInput).toBeTruthy()
    expect(submitButton).toBeTruthy()
  })

  it('should have accessible name', () => {
    render(ActionButton, { props: { label: 'Submit' } })

    // Accessible name comes from label prop
    const button = screen.getByRole('button', { name: 'Submit' })
    expect(button).toBeTruthy()
  })
})
```

**Query priority**:
1. `getByRole` - Most robust, reflects what assistive tech sees
2. `getByLabelText` - For form fields
3. `getByPlaceholderText` - Less preferred, but sometimes necessary
4. `getByText` - For non-interactive elements
5. `getByTestId` - Last resort

---

### 3. Keyboard Navigation Testing

```typescript
import { render, screen } from '@testing-library/vue'
import userEvent from '@testing-library/user-event'

describe('Keyboard Navigation', () => {
  it('should be keyboard focusable', async () => {
    render(ActionButton, { props: { label: 'Submit' } })

    const button = screen.getByRole('button')
    button.focus()

    expect(document.activeElement).toBe(button)
  })

  it('should handle Enter key', async () => {
    const user = userEvent.setup()
    const handleClick = vi.fn()

    render(ActionButton, {
      props: { label: 'Submit', onClick: handleClick }
    })

    const button = screen.getByRole('button')
    await user.type(button, '{Enter}')

    expect(handleClick).toHaveBeenCalled()
  })

  it('should trap focus in modal', async () => {
    const user = userEvent.setup()
    render(Modal)

    const firstButton = screen.getByRole('button', { name: 'First' })
    const lastButton = screen.getByRole('button', { name: 'Last' })

    // Focus first element
    firstButton.focus()

    // Shift+Tab should wrap to last element
    await user.keyboard('{Shift>}{Tab}{/Shift}')
    expect(document.activeElement).toBe(lastButton)

    // Tab should wrap to first element
    await user.keyboard('{Tab}')
    expect(document.activeElement).toBe(firstButton)
  })
})
```

---

### 4. ARIA State Testing

```typescript
describe('ARIA States', () => {
  it('should announce loading state', async () => {
    render(ActionButton, {
      props: { label: 'Submit', loading: true }
    })

    const button = screen.getByRole('button')
    expect(button).toHaveAttribute('aria-busy', 'true')
  })

  it('should announce expanded state', async () => {
    const user = userEvent.setup()
    render(Accordion)

    const trigger = screen.getByRole('button', { name: 'Section 1' })
    expect(trigger).toHaveAttribute('aria-expanded', 'false')

    await user.click(trigger)
    expect(trigger).toHaveAttribute('aria-expanded', 'true')
  })

  it('should announce selected state', async () => {
    render(TabPanel)

    const tab = screen.getByRole('tab', { name: 'Tab 1', selected: true })
    expect(tab).toHaveAttribute('aria-selected', 'true')
  })
})
```

---

### 5. Live Region Testing

```typescript
describe('Live Regions', () => {
  it('should announce status updates', async () => {
    const { container } = render(StatusMessage)

    const liveRegion = container.querySelector('[role="status"]')
    expect(liveRegion).toHaveAttribute('aria-live', 'polite')
    expect(liveRegion).toHaveTextContent('Operation completed')
  })

  it('should announce alerts', async () => {
    render(ErrorAlert)

    const alert = screen.getByRole('alert')
    expect(alert).toHaveTextContent('Error: Invalid input')
  })
})
```

---

## Manual Testing

### 1. Keyboard-Only Navigation

**Test with Tab key**:
- [ ] Tab through all interactive elements
- [ ] Verify focus order matches visual order
- [ ] Verify focus is always visible
- [ ] Verify no keyboard traps
- [ ] Test Shift+Tab for reverse navigation

**Test with Arrow keys** (for components like dropdowns, tabs):
- [ ] Arrow keys navigate within component
- [ ] Home/End keys work (if applicable)
- [ ] Page Up/Down work (if applicable)

**Test with Enter/Space**:
- [ ] Buttons activate with Enter and Space
- [ ] Links activate with Enter
- [ ] Checkboxes toggle with Space

**Test with Escape**:
- [ ] Modals close with Escape
- [ ] Dropdowns close with Escape
- [ ] Tooltips dismiss with Escape

---

### 2. Screen Reader Testing

**NVDA (Windows - Free)**:
```
Download: https://www.nvaccess.org/download/
Quick start:
- Ctrl+Alt+N: Start NVDA
- Insert+Q: Quit NVDA
- Insert+Down: Read next item
- Insert+Up: Read previous item
- Insert+Space: Toggle browse/focus mode
```

**JAWS (Windows - Commercial)**:
```
Trial: https://www.freedomscientific.com/downloads/jaws
Quick keys:
- Insert+F5: List form fields
- Insert+F7: List links
- H/Shift+H: Navigate headings
```

**VoiceOver (Mac - Built-in)**:
```
Enable: System Preferences > Accessibility > VoiceOver
Quick keys:
- Cmd+F5: Toggle VoiceOver
- VO+A: Start reading
- VO+Right/Left: Navigate
- VO+Space: Activate
- VO+U: Rotor menu
```

**Testing checklist**:
- [ ] All interactive elements announced with role
- [ ] All buttons/links have accessible names
- [ ] Form fields have associated labels
- [ ] Images have meaningful alt text
- [ ] Headings create logical structure
- [ ] Live regions announce updates
- [ ] Focus changes are announced
- [ ] Landmark regions are identified

---

### 3. Color Contrast Testing

**Browser DevTools**:
```
Chrome DevTools:
1. Open DevTools (F12)
2. Select element with text
3. View Computed > Accessibility
4. Check contrast ratio

Firefox DevTools:
1. Open DevTools (F12)
2. Inspector > Accessibility panel
3. Check contrast
```

**Online tools**:
- WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
- Coolors Contrast Checker: https://coolors.co/contrast-checker

**Automated tools**:
```bash
# Lighthouse
npx lighthouse http://localhost:3000 --only-categories=accessibility

# axe-cli
npx @axe-core/cli http://localhost:3000
```

**Requirements**:
- Normal text (< 24px): 4.5:1 (AA), 7:1 (AAA)
- Large text (≥ 24px or ≥ 19px bold): 3:1 (AA), 4.5:1 (AAA)
- UI components: 3:1 (AA)

---

### 4. Zoom and Reflow Testing

**Browser zoom**:
- [ ] Zoom to 200% (Ctrl/Cmd + Plus)
- [ ] Verify all content readable
- [ ] Verify no horizontal scrolling
- [ ] Verify layout reflows properly
- [ ] Verify touch targets still ≥ 44x44px

**Text-only zoom**:
- [ ] Firefox: View > Zoom > Zoom Text Only
- [ ] Increase to 200%
- [ ] Verify layout doesn't break

---

### 5. Reduced Motion Testing

**Enable in OS**:

**Windows**:
```
Settings > Ease of Access > Display > Show animations in Windows
```

**Mac**:
```
System Preferences > Accessibility > Display > Reduce motion
```

**Test**:
- [ ] Animations respect prefers-reduced-motion
- [ ] Transitions are instant or subtle
- [ ] Parallax effects disabled
- [ ] Auto-playing animations stop

**Browser DevTools override**:
```
Chrome DevTools:
1. Open DevTools (F12)
2. Cmd+Shift+P > "Emulate CSS prefers-reduced-motion"
3. Select "prefers-reduced-motion: reduce"
```

---

### 6. Mobile Accessibility Testing

**Touch targets**:
- [ ] All interactive elements ≥ 44x44px
- [ ] Adequate spacing between targets
- [ ] No overlapping touch targets

**Orientation**:
- [ ] Works in portrait and landscape
- [ ] Content reflows appropriately
- [ ] No content locked to single orientation

**Mobile screen readers**:

**TalkBack (Android)**:
```
Settings > Accessibility > TalkBack
Gestures:
- Swipe right: Next item
- Swipe left: Previous item
- Double-tap: Activate
- Two-finger swipe down: Start reading
```

**VoiceOver (iOS)**:
```
Settings > Accessibility > VoiceOver
Gestures:
- Swipe right: Next item
- Swipe left: Previous item
- Double-tap: Activate
- Two-finger swipe down: Read from top
```

---

## Continuous Integration Testing

### Lighthouse CI

**.lighthouserc.json**:
```json
{
  "ci": {
    "collect": {
      "url": ["http://localhost:3000"],
      "numberOfRuns": 3
    },
    "assert": {
      "preset": "lighthouse:recommended",
      "assertions": {
        "categories:accessibility": ["error", { "minScore": 0.9 }],
        "color-contrast": ["error"],
        "aria-required-attr": ["error"]
      }
    }
  }
}
```

**GitHub Actions**:
```yaml
name: Accessibility CI

on: [push, pull_request]

jobs:
  a11y:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build

      - name: Start server
        run: npm start &

      - name: Run Lighthouse CI
        run: |
          npm install -g @lhci/cli
          lhci autorun

      - name: Run axe tests
        run: npm run test:a11y
```

---

## Accessibility Testing Checklist

### Before Committing
- [ ] All automated tests pass (jest-axe, vitest)
- [ ] Keyboard navigation works
- [ ] Focus indicators visible
- [ ] Color contrast meets AA standards
- [ ] Semantic HTML used
- [ ] ARIA attributes correct

### Before Deploying
- [ ] Lighthouse accessibility score ≥ 90
- [ ] Manual screen reader testing completed
- [ ] Keyboard-only navigation tested
- [ ] Zoom to 200% tested
- [ ] Mobile accessibility tested
- [ ] Reduced motion preferences respected

### Regular Audits
- [ ] Monthly automated scans with axe
- [ ] Quarterly manual screen reader testing
- [ ] Annual WCAG 2.2 compliance audit
- [ ] User testing with assistive technology users
