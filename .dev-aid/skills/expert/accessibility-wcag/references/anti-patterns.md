# Accessibility Anti-Patterns and Common Mistakes

## DON'T: Use Color Alone to Convey Information

### Problem
Users with color blindness or low vision cannot distinguish information conveyed only through color.

### Bad Example
```html
<span style="color: red;">Error</span>
<span style="color: green;">Success</span>
```

### Good Example
```html
<span class="error">
  <svg aria-hidden="true" focusable="false">
    <use href="#icon-error" />
  </svg>
  Error: Invalid email format
</span>

<span class="success">
  <svg aria-hidden="true" focusable="false">
    <use href="#icon-check" />
  </svg>
  Success: Form submitted
</span>
```

### Why it's better
- Icon provides visual indicator beyond color
- Text describes the actual state/error
- Works for colorblind users
- Meets WCAG 2.2 Level A (1.4.1 Use of Color)

---

## DON'T: Use Non-Semantic Elements for Interactive Components

### Problem
Divs and spans don't have built-in keyboard support, focus management, or screen reader semantics.

### Bad Example
```html
<div onclick="handleClick()">Click me</div>
<span onclick="submitForm()">Submit</span>
```

### Good Example
```html
<button type="button" onclick="handleClick()">Click me</button>
<button type="submit" onclick="submitForm()">Submit</button>
```

### Why it's better
- Native keyboard support (Enter/Space)
- Automatically focusable
- Screen readers announce as "button"
- Role and states built-in

---

## DON'T: Hide Focus Indicators Globally

### Problem
Keyboard users cannot see where they are on the page.

### Bad Example
```css
*:focus {
  outline: none;
}

button:focus {
  outline: none;
}
```

### Good Example
```css
/* Remove default for custom styling */
*:focus {
  outline: none;
}

/* Add custom focus indicator */
*:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}

/* Only hide outline for mouse users */
*:focus:not(:focus-visible) {
  outline: none;
}
```

### Why it's better
- Keyboard users see focus
- Mouse users don't see unnecessary outlines
- Meets WCAG 2.2 Level AA (2.4.7 Focus Visible)

---

## DON'T: Use placeholder as a Label

### Problem
Placeholders disappear on input, aren't always announced by screen readers, and have insufficient contrast.

### Bad Example
```html
<input type="email" placeholder="Enter your email" />
```

### Good Example
```html
<label for="email">Email address</label>
<input
  type="email"
  id="email"
  name="email"
  placeholder="example@domain.com"
  aria-describedby="email-hint"
/>
<p id="email-hint" class="hint">We'll never share your email</p>
```

### Why it's better
- Label always visible
- Screen readers announce label
- Placeholder provides example format
- Hint provides additional context

---

## DON'T: Create Keyboard Traps

### Problem
Users cannot escape from a component using only keyboard.

### Bad Example
```typescript
// Modal that traps focus but has no escape
function openModal() {
  modal.style.display = 'block'
  modal.querySelector('input').focus()
  // No way to close without mouse
}
```

### Good Example
```typescript
function openModal() {
  const modal = document.querySelector('.modal')
  const closeButton = modal.querySelector('.close-button')
  const focusableElements = modal.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  )

  modal.style.display = 'block'
  closeButton.focus()

  // Trap focus within modal
  modal.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeModal()
    }
    // Handle Tab trapping (see focus-trap pattern)
  })
}
```

### Why it's better
- Escape key closes modal
- Focus trapped within modal
- Users can exit via keyboard
- Meets WCAG 2.2 Level A (2.1.2 No Keyboard Trap)

---

## DON'T: Use Insufficient Color Contrast

### Problem
Low contrast text is hard to read for users with low vision.

### Bad Example
```css
.text {
  color: #999999; /* Light gray */
  background: #ffffff; /* White */
  /* Contrast ratio: 2.85:1 - FAILS */
}
```

### Good Example
```css
.text {
  color: #595959; /* Dark gray */
  background: #ffffff; /* White */
  /* Contrast ratio: 7.0:1 - PASSES AAA */
}

/* Or use system colors */
.text {
  color: CanvasText;
  background: Canvas;
}
```

### Why it's better
- Meets WCAG 2.2 Level AA (4.5:1 for normal text)
- Readable for users with low vision
- System colors respect user preferences

---

## DON'T: Rely on Hover-Only Content

### Problem
Touch screen and keyboard users cannot hover.

### Bad Example
```html
<div class="tooltip-container">
  <span>Help</span>
  <div class="tooltip">This is helpful information</div>
</div>

<style>
.tooltip { display: none; }
.tooltip-container:hover .tooltip { display: block; }
</style>
```

### Good Example
```html
<button
  type="button"
  aria-describedby="tooltip-1"
  aria-expanded="false"
  onclick="toggleTooltip()"
>
  Help
</button>
<div id="tooltip-1" role="tooltip" hidden>
  This is helpful information
</div>
```

```typescript
function toggleTooltip() {
  const button = event.target
  const tooltip = document.getElementById(button.getAttribute('aria-describedby'))
  const isExpanded = button.getAttribute('aria-expanded') === 'true'

  button.setAttribute('aria-expanded', String(!isExpanded))
  tooltip.hidden = isExpanded
}
```

### Why it's better
- Works with keyboard
- Works on touch screens
- Screen readers announce tooltip
- Meets WCAG 2.2 Level A (2.1.1 Keyboard)

---

## DON'T: Use Automatic Timeouts Without Warning

### Problem
Users with disabilities may need more time to complete tasks.

### Bad Example
```typescript
// Auto-logout after 5 minutes, no warning
setTimeout(() => {
  logout()
}, 5 * 60 * 1000)
```

### Good Example
```typescript
let timeoutId: number
let warningId: number

function resetTimeout() {
  clearTimeout(timeoutId)
  clearTimeout(warningId)

  // Warn at 4 minutes
  warningId = setTimeout(() => {
    showTimeoutWarning()
  }, 4 * 60 * 1000)

  // Logout at 5 minutes
  timeoutId = setTimeout(() => {
    logout()
  }, 5 * 60 * 1000)
}

function showTimeoutWarning() {
  const dialog = document.querySelector('.timeout-dialog')
  dialog.style.display = 'block'
  dialog.querySelector('button').focus()

  // Announce to screen readers
  const liveRegion = document.querySelector('[role="alert"]')
  liveRegion.textContent = 'Your session will expire in 1 minute. Click Continue to stay logged in.'
}

// Reset timeout on user activity
document.addEventListener('keydown', resetTimeout)
document.addEventListener('mousedown', resetTimeout)
```

### Why it's better
- Warning before timeout
- User can extend session
- Screen reader announcement
- Meets WCAG 2.2 Level A (2.2.1 Timing Adjustable)

---

## DON'T: Use Images of Text

### Problem
Images of text don't scale well and can't be customized by users.

### Bad Example
```html
<img src="heading.png" alt="Welcome to our site" />
```

### Good Example
```html
<h1>Welcome to our site</h1>

<style>
h1 {
  font-family: 'Custom Font', sans-serif;
  font-size: 2rem;
  color: var(--color-primary);
}
</style>
```

### Why it's better
- Text scales with browser settings
- Users can customize fonts
- Better contrast in high contrast mode
- Translatable
- Meets WCAG 2.2 Level AA (1.4.5 Images of Text)

---

## DON'T: Use Vague Link Text

### Problem
Screen reader users often navigate by links. "Click here" provides no context.

### Bad Example
```html
<p>To learn more about accessibility, <a href="/guide">click here</a>.</p>
```

### Good Example
```html
<p>Learn more about <a href="/guide">web accessibility best practices</a>.</p>

<!-- Or if context is needed -->
<a href="/guide" aria-label="Learn more about web accessibility best practices">
  Learn more
</a>
```

### Why it's better
- Link purpose clear from text alone
- Makes sense out of context
- Better for screen reader users
- Meets WCAG 2.2 Level A (2.4.4 Link Purpose)

---

## DON'T: Disable Zoom

### Problem
Users with low vision need to zoom to read content.

### Bad Example
```html
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
```

### Good Example
```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Why it's better
- Users can zoom up to 200%
- Works with browser/OS zoom features
- Meets WCAG 2.2 Level AA (1.4.4 Resize Text)

---

## DON'T: Use Only Icons Without Text

### Problem
Icon meanings aren't universal, especially for screen reader users.

### Bad Example
```html
<button>
  <svg><!-- icon --></svg>
</button>
```

### Good Example
```html
<!-- Option 1: Visible text -->
<button>
  <svg aria-hidden="true"><!-- icon --></svg>
  Save
</button>

<!-- Option 2: Visually hidden text -->
<button aria-label="Save">
  <svg aria-hidden="true"><!-- icon --></svg>
  <span class="visually-hidden">Save</span>
</button>
```

### Why it's better
- Screen readers announce purpose
- Clear for all users
- Meets WCAG 2.2 Level A (1.1.1 Non-text Content)

---

## Summary Checklist: Avoid These Mistakes

- [ ] Don't use color alone to convey information
- [ ] Don't use divs/spans for interactive components
- [ ] Don't hide focus indicators
- [ ] Don't use placeholder as label
- [ ] Don't create keyboard traps
- [ ] Don't use insufficient contrast
- [ ] Don't rely on hover-only content
- [ ] Don't use automatic timeouts without warning
- [ ] Don't use images of text
- [ ] Don't use vague link text
- [ ] Don't disable zoom
- [ ] Don't use only icons without text
