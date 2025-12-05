# Top 7 UX Patterns

> **Reference Document**: Essential UX patterns with detailed implementation examples for the UI/UX Expert skill.

---

## Table of Contents

1. [Progressive Disclosure](#pattern-1-progressive-disclosure)
2. [Error Prevention & Recovery](#pattern-2-clear-error-prevention--recovery)
3. [Logical Information Architecture](#pattern-3-logical-information-architecture)
4. [Effective Form Design](#pattern-4-effective-form-design)
5. [Responsive Touch Targets](#pattern-5-responsive-touch-targets)
6. [Loading States & Feedback](#pattern-6-loading-states--feedback)
7. [Consistent Visual Hierarchy](#pattern-7-consistent-visual-hierarchy)

---

## Pattern 1: Progressive Disclosure

Reveal information progressively to reduce cognitive load.

### When to Use
- Complex forms with many fields
- Advanced settings or options
- Multi-step processes
- Feature-rich dashboards

### Implementation
```
[Step Indicator]
Step 1 of 3: Basic Info

[Form Fields - Only Essential]
Name: [_______]
Email: [_______]

[Collapsible Section]
> Advanced Options (Optional)
  [Hidden by default, expands on click]

[Primary Action]
[Continue →]

Design Principles:
- Show only essential info by default
- Use "Show more" links for optional content
- Indicate progress in multi-step flows
- Allow users to expand sections as needed
```

### Accessibility
Ensure expanded/collapsed state is announced to screen readers using `aria-expanded`.

```html
<button aria-expanded="false" aria-controls="advanced-options">
  Advanced Options
</button>
<div id="advanced-options" hidden>
  <!-- Optional fields -->
</div>
```

---

## Pattern 2: Clear Error Prevention & Recovery

Design to prevent errors and help users recover gracefully.

### Implementation
```
[Input Field with Validation]
Email Address
[user@example] ⚠️
└─ "Please include '@' in the email address"
   (Inline, real-time validation)

[Confirmation Dialog]
┌─────────────────────────────┐
│ Delete Account?             │
│                             │
│ This action cannot be       │
│ undone. All your data will  │
│ be permanently deleted.     │
│                             │
│ Type "DELETE" to confirm:   │
│ [_______]                   │
│                             │
│ [Cancel] [Delete Account]  │
└─────────────────────────────┘

Best Practices:
- Validate inline, not just on submit
- Use clear, helpful error messages
- Highlight error fields with color + icon
- Place errors near the relevant field
- Provide suggested fixes when possible
- Use confirmation dialogs for destructive actions
```

### Accessibility
Use `aria-invalid` and `aria-describedby` to link errors to fields.

```html
<input
  id="email"
  type="email"
  aria-invalid="true"
  aria-describedby="email-error"
>
<span id="email-error" role="alert">
  Please enter a valid email address
</span>
```

---

## Pattern 3: Logical Information Architecture

Organize content in a way that matches user mental models.

### Card Sorting Approach
1. Conduct open card sorts with users
2. Identify common groupings
3. Create clear navigation hierarchy
4. Use familiar categorization

### Navigation Patterns
```
[Primary Navigation]
Top-level (5-7 items max)
├─ Dashboard
├─ Projects
├─ Team
├─ Settings
└─ Help

[Breadcrumbs]
Home > Projects > Website Redesign > Design Files

[Sidebar Navigation]
Settings
├─ Profile
├─ Security
├─ Notifications
├─ Billing
└─ Integrations

Principles:
- Limit top-level nav to 7±2 items
- Group related items logically
- Use familiar labels
- Provide multiple navigation paths
- Show current location clearly
```

### Best Practices
- Use familiar categorization (match users' mental models)
- Provide multiple ways to find content
- Show clear location indicators (breadcrumbs, active states)
- Test navigation with real users through tree testing
- Keep navigation consistent across the application

---

## Pattern 4: Effective Form Design

Design forms that are easy to complete with minimal errors.

### Best Practices
```
[Single Column Layout]
Full Name *
[________________________]

Email Address *
[________________________]
Helper text: We'll never share your email

Password *
[________________________] [👁️ Show]
At least 8 characters, including a number

[Label Above Input - Scannable]

[Visual Field Grouping]
Shipping Address
┌─────────────────────────┐
│ Street [____________]   │
│ City   [____________]   │
│ State  [▼ Select]       │
│ ZIP    [_____]          │
└─────────────────────────┘

Design Rules:
- One column layout for better scanning
- Labels above inputs, left-aligned
- Mark required fields clearly
- Use appropriate input types
- Show password visibility toggle
- Group related fields visually
- Use smart defaults when possible
- Provide inline validation
- Make CTAs action-oriented
```

### Accessibility
Associate labels with inputs using `for`/`id`, mark required fields semantically.

```html
<label for="email">
  Email Address <span aria-label="required">*</span>
</label>
<input
  id="email"
  type="email"
  required
  aria-required="true"
  placeholder="user@example.com"
>
```

### Form Completion Tips
- Auto-format inputs (phone numbers, credit cards)
- Show character count for limited fields
- Save progress for long forms
- Allow users to review before submitting
- Provide clear success confirmation

---

## Pattern 5: Responsive Touch Targets

Design for both mouse and touch input.

### Touch Target Sizing
```
[Mobile Touch Targets - 44x44px minimum]

❌ Too Small:
[Submit] (30x30px - hard to tap)

✅ Proper Size:
[    Submit    ] (48x48px - easy to tap)

[Button Spacing]
Minimum 8px between interactive elements

[Mobile Action Bar]
┌─────────────────────────┐
│                         │
│  [Large tap area for    │
│   primary action]       │
│                         │
│  [ Primary Action  ]    │ 48px height
│                         │
└─────────────────────────┘

Guidelines:
- 44x44px minimum (WCAG 2.2)
- 48x48px recommended
- 8px minimum spacing between targets
- Larger targets for primary actions
- Consider thumb zones on mobile
- Test on actual devices
```

### Thumb Zone Considerations
On mobile devices, design for one-handed use:
- Place primary actions in easy-to-reach zones
- Bottom of screen is most accessible for thumbs
- Avoid placing critical actions in top corners
- Consider both left and right-handed users

### Implementation Example
```css
/* Touch-friendly button */
.touch-target {
  min-width: 44px;
  min-height: 44px;
  padding: 12px 24px;
  margin: 4px; /* Spacing between targets */
}

/* Even better: 48x48px */
.touch-target-recommended {
  min-width: 48px;
  min-height: 48px;
  padding: 14px 28px;
  margin: 4px;
}
```

---

## Pattern 6: Loading States & Feedback

Provide clear feedback for all user actions.

### Loading Patterns
```
[Skeleton Screens - Better than spinners]
┌─────────────────────────┐
│ ▓▓▓▓▓▓▓▓░░░░░░░░░░      │ (Title loading)
│ ░░░░░░░░░░░░░░░░        │ (Description)
│ ▓▓▓▓░░░░ ▓▓▓▓░░░░      │ (Cards loading)
└─────────────────────────┘

[Progress Indicators]
Uploading file... 47%
[████████░░░░░░░░░░]

[Optimistic UI]
User clicks "Like" →
1. Show liked state immediately
2. Send request in background
3. Revert if request fails

[Toast Notifications]
┌─────────────────────────┐
│ ✓ Settings saved        │
└─────────────────────────┘
(Auto-dismiss after 3-5s)

Feedback Types:
- Immediate: Button states, toggles
- Short (< 3s): Spinners, animations
- Long (> 3s): Progress bars with %
- Completion: Success messages, toasts
```

### Accessibility
Announce loading states to screen readers using `aria-live` regions.

```html
<!-- Loading announcement -->
<div aria-live="polite" aria-atomic="true">
  <span v-if="loading">Loading content...</span>
</div>

<!-- Progress with percentage -->
<div role="progressbar" aria-valuenow="47" aria-valuemin="0" aria-valuemax="100">
  Uploading: 47%
</div>

<!-- Button with loading state -->
<button aria-busy="true" disabled>
  <span class="spinner" aria-hidden="true"></span>
  Saving...
</button>
```

### Feedback Timing Guidelines
- **Instant** (< 100ms): Felt instantaneous, no indicator needed
- **Brief** (100ms - 1s): Show spinner or progress indicator
- **Moderate** (1s - 10s): Show progress bar with percentage
- **Long** (> 10s): Show detailed progress, allow cancellation

---

## Pattern 7: Consistent Visual Hierarchy

Guide users' attention through clear hierarchy.

### Hierarchy Techniques
```
[Typography Scale]
H1: 32px / 2rem (Page title)
H2: 24px / 1.5rem (Section heading)
H3: 20px / 1.25rem (Subsection)
Body: 16px / 1rem (Base text)
Small: 14px / 0.875rem (Helper text)

[Visual Weight]
1. Size (larger = more important)
2. Color (high contrast = emphasis)
3. Weight (bold = important)
4. Spacing (more space = separation)

[Z-Pattern for Scanning]
Logo ─────────────→ CTA
↓
Headline
↓
Content ─────────→ Image

[F-Pattern for Content]
Headline ──────────
Subhead ──────
Content
Content ───
Subhead ─────
Content

Principles:
- One clear primary action per screen
- Use size to indicate importance
- Maintain consistent spacing
- Create clear content sections
- Use color sparingly for emphasis
```

### Implementing Visual Hierarchy

**Size & Scale**:
```css
/* Type scale */
h1 { font-size: 2rem; }     /* 32px */
h2 { font-size: 1.5rem; }   /* 24px */
h3 { font-size: 1.25rem; }  /* 20px */
body { font-size: 1rem; }   /* 16px */
small { font-size: 0.875rem; } /* 14px */
```

**Color & Contrast**:
- Primary actions: High contrast (e.g., blue button on white)
- Secondary actions: Medium contrast (e.g., gray button)
- Tertiary actions: Low contrast (e.g., text link)

**Spacing**:
```css
/* Consistent spacing scale (8px base) */
.space-xs { margin: 8px; }
.space-sm { margin: 16px; }
.space-md { margin: 24px; }
.space-lg { margin: 32px; }
.space-xl { margin: 48px; }
```

### Visual Hierarchy Checklist
- [ ] One clear primary action per page
- [ ] Typography scale creates clear levels
- [ ] Spacing groups related elements
- [ ] Color highlights important elements
- [ ] Contrast makes text readable
- [ ] Layout guides eye through content
- [ ] White space prevents clutter

---

## Summary

These 7 UX patterns form the foundation of good user experience design:

1. **Progressive Disclosure**: Reduce cognitive load by revealing information gradually
2. **Error Prevention & Recovery**: Help users avoid mistakes and recover gracefully
3. **Logical Information Architecture**: Organize content to match user mental models
4. **Effective Form Design**: Make forms easy to complete with minimal friction
5. **Responsive Touch Targets**: Design for both mouse and touch input
6. **Loading States & Feedback**: Provide clear feedback for all user actions
7. **Consistent Visual Hierarchy**: Guide attention through clear hierarchy

Apply these patterns consistently across your interfaces to create intuitive, user-friendly experiences.

**Related References**:
- See `design-patterns.md` for complete UI pattern library and component guidelines
- See `accessibility-guide.md` for WCAG 2.2 implementation details
- See `performance-patterns.md` for optimization strategies
