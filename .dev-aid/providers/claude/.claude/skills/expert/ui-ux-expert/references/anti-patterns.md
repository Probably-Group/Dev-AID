# Common UI/UX Anti-Patterns

> **Reference Document**: Common UI/UX mistakes and how to avoid them for the UI/UX Expert skill.

---

## Table of Contents

1. [Insufficient Color Contrast](#1-insufficient-color-contrast)
2. [Color as Only Visual Indicator](#2-color-as-only-visual-indicator)
3. [Tiny Touch Targets on Mobile](#3-tiny-touch-targets-on-mobile)
4. [Non-Semantic HTML](#4-non-semantic-html)
5. [Missing Form Labels](#5-missing-form-labels)
6. [Inconsistent Patterns](#6-inconsistent-patterns)
7. [Unclear Error Messages](#7-unclear-error-messages)
8. [Auto-Playing Media](#8-auto-playing-media)
9. [Complex Navigation](#9-complex-navigation)
10. [No Loading or Error States](#10-no-loading-or-error-states)

---

## 1. Insufficient Color Contrast

### ❌ Mistake
```
Light gray text on white background
#CCCCCC on #FFFFFF (1.6:1 contrast)
Fails WCAG AA - unreadable for many users
```

**Why It's Bad**:
- Users with low vision cannot read the text
- Fails WCAG 2.2 Level AA accessibility standards
- Poor readability in bright environments
- Excludes users with color vision deficiencies

### ✅ Solution
```
Use sufficient contrast ratios:
- Body text: #333333 on #FFFFFF (12.6:1)
- Secondary text: #666666 on #FFFFFF (5.7:1)
- Always test with contrast checker tools
```

**Requirements**:
- Normal text (< 24px): **4.5:1 minimum** (WCAG AA)
- Large text (≥ 24px): **3:1 minimum** (WCAG AA)
- UI components: **3:1 minimum** (WCAG AA)

**Tools to Use**:
- WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
- Chrome DevTools Accessibility Panel
- Stark plugin for Figma

---

## 2. Color as Only Visual Indicator

### ❌ Mistake
```
Error shown only by red border
[_________] (red border)
No icon, no text - fails for colorblind users
```

**Why It's Bad**:
- ~8% of men and ~0.5% of women have color vision deficiency
- Information is lost for colorblind users
- Fails WCAG 2.2 SC 1.4.1 (Use of Color)
- Users may not understand what the color means

### ✅ Solution
```
Use multiple indicators:
⚠️ [_________]
└─ "Email address is required"

Combine: Color + Icon + Text
```

**Best Practices**:
- Always combine color with text labels
- Use icons to reinforce meaning
- Provide text alternatives for color-coded information
- Test with color blindness simulators

**Examples**:
```html
<!-- Bad: Color only -->
<span style="color: red;">Required</span>

<!-- Good: Color + Icon + Text -->
<span class="text-red-600">
  <svg class="icon-error" aria-hidden="true">...</svg>
  <span>Required field</span>
</span>
```

---

## 3. Tiny Touch Targets on Mobile

### ❌ Mistake
```
[×] Close button: 20x20px
Too small for reliable tapping
```

**Why It's Bad**:
- Users struggle to tap small targets accurately
- Leads to frustration and misclicks
- Fails WCAG 2.2 SC 2.5.8 (Target Size - Minimum)
- Particularly difficult for users with motor impairments

### ✅ Solution
```
[    ×    ] Minimum 44x44px tap area
Even if icon is smaller, padding increases hit area
```

**Requirements**:
- **WCAG 2.2 Level AA**: 24x24px minimum
- **Recommended**: 44x44px minimum
- **Best practice**: 48x48px for primary actions
- **Spacing**: 8px minimum between touch targets

**Implementation**:
```css
/* Ensure touch-friendly targets */
.touch-target {
  min-width: 44px;
  min-height: 44px;
  padding: 12px;
}

/* Icon can be smaller, but clickable area is large */
.icon-button {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-button svg {
  width: 24px;
  height: 24px;
}
```

---

## 4. Non-Semantic HTML

### ❌ Mistake
```html
<div onclick="submit()">Submit</div>
Not keyboard accessible, no semantic meaning
```

**Why It's Bad**:
- Not keyboard accessible (cannot be focused with Tab)
- Screen readers don't identify it as a button
- No default button behaviors (Enter, Space)
- Requires extra JavaScript for accessibility
- Fails WCAG 2.2 SC 4.1.2 (Name, Role, Value)

### ✅ Solution
```html
<button type="submit">Submit</button>
Semantic, keyboard accessible by default
```

**Always Use Semantic HTML**:
- `<button>` for buttons
- `<a>` for links (navigation)
- `<nav>` for navigation regions
- `<main>` for main content
- `<article>` for independent content
- `<aside>` for complementary content
- `<header>` and `<footer>` for page regions

**When to Use Each**:
```html
<!-- Navigation to different page/URL -->
<a href="/about">About Us</a>

<!-- Triggers an action on the same page -->
<button onclick="openModal()">Open Dialog</button>

<!-- Submits a form -->
<button type="submit">Submit Form</button>
```

---

## 5. Missing Form Labels

### ❌ Mistake
```html
<input type="text" placeholder="Enter email">
Screen readers can't identify the field
```

**Why It's Bad**:
- Screen readers cannot identify the input's purpose
- Placeholder text disappears when user types
- Fails WCAG 2.2 SC 1.3.1 (Info and Relationships)
- Poor usability for all users

### ✅ Solution
```html
<label for="email">Email Address</label>
<input id="email" type="email" placeholder="user@example.com">
```

**Best Practices**:
- Always use `<label>` elements with `for` attribute
- Label should be visible (not just in placeholder)
- Mark required fields clearly
- Use `aria-describedby` for help text

**Complete Example**:
```html
<div class="form-field">
  <label for="email">
    Email Address
    <span aria-label="required">*</span>
  </label>
  <input
    id="email"
    type="email"
    required
    aria-required="true"
    aria-describedby="email-hint"
    placeholder="user@example.com"
  >
  <span id="email-hint" class="hint-text">
    We'll never share your email
  </span>
</div>
```

---

## 6. Inconsistent Patterns

### ❌ Mistake
```
- Save button is blue on page 1
- Save button is green on page 2
- Save button position changes
```

**Why It's Bad**:
- Confuses users and increases cognitive load
- Breaks learned patterns and muscle memory
- Appears unprofessional and unpolished
- Reduces user confidence in the application

### ✅ Solution
```
Create design system with consistent:
- Component styles
- Button positions
- Interaction patterns
- Terminology
```

**Design System Checklist**:
- [ ] Define color palette with specific use cases
- [ ] Establish typography scale
- [ ] Create spacing system (4px or 8px grid)
- [ ] Document component variations and states
- [ ] Define consistent terminology
- [ ] Establish button hierarchy (primary, secondary, tertiary)
- [ ] Define consistent layouts and positions
- [ ] Use consistent iconography

**Example Consistency Rules**:
```
Primary Action:
- Color: Blue (#0066CC)
- Position: Bottom right or top right
- Label: Action verb (Save, Submit, Continue)

Secondary Action:
- Color: Gray (#6B7280)
- Position: Left of primary action
- Label: Cancel, Back, Skip

Destructive Action:
- Color: Red (#DC2626)
- Requires confirmation dialog
- Label: Delete, Remove, Clear
```

---

## 7. Unclear Error Messages

### ❌ Mistake
```
"Error: Invalid input"
Doesn't tell user what's wrong or how to fix it
```

**Why It's Bad**:
- User doesn't know what went wrong
- No guidance on how to fix the problem
- Increases user frustration
- May cause users to abandon the task

### ✅ Solution
```
"Password must be at least 8 characters and include a number"
Clear, actionable, helpful
```

**Error Message Best Practices**:
1. **Be specific**: Tell exactly what's wrong
2. **Be helpful**: Explain how to fix it
3. **Be polite**: Don't blame the user
4. **Be visible**: Place error near the relevant field
5. **Be timely**: Show errors at the right moment

**Good Error Message Examples**:
```
❌ Bad: "Invalid email"
✅ Good: "Email address must include an @ symbol"

❌ Bad: "Error 422"
✅ Good: "This username is already taken. Please choose a different one."

❌ Bad: "Password error"
✅ Good: "Password must be at least 8 characters and include at least one number"

❌ Bad: "Invalid date"
✅ Good: "Date must be in the format MM/DD/YYYY"
```

---

## 8. Auto-Playing Media

### ❌ Mistake
```
Video with sound auto-plays on page load
Disorienting for screen reader users
```

**Why It's Bad**:
- Competes with screen reader audio
- Startles users with unexpected sound
- Drains battery and bandwidth
- Fails WCAG 2.2 SC 1.4.2 (Audio Control)
- Poor user experience for everyone

### ✅ Solution
```
- Never auto-play with sound
- Provide play/pause controls
- Show captions by default
- Allow users to control media
```

**Media Best Practices**:
```html
<!-- Auto-play without sound is OK, but provide controls -->
<video
  autoplay
  muted
  loop
  playsinline
  controls
  aria-label="Background video"
>
  <source src="video.mp4" type="video/mp4">
  <track kind="captions" src="captions.vtt" srclang="en" label="English">
</video>

<!-- Better: Let user initiate playback -->
<video
  controls
  preload="metadata"
  poster="thumbnail.jpg"
>
  <source src="video.mp4" type="video/mp4">
  <track kind="captions" src="captions.vtt" srclang="en" label="English" default>
</video>
```

**Requirements**:
- Provide play/pause controls
- Include captions for all video content
- Allow users to stop, pause, and control volume
- Don't auto-play audio for more than 3 seconds
- Provide a way to disable animations (prefers-reduced-motion)

---

## 9. Complex Navigation

### ❌ Mistake
```
Main navigation with 15+ top-level items
Mega-menu with 100+ links
Overwhelming and hard to scan
```

**Why It's Bad**:
- Cognitive overload for users
- Difficult to scan and find items
- Poor mobile experience
- Increases time to complete tasks

### ✅ Solution
```
- Limit top-level nav to 5-7 items
- Use clear hierarchy
- Group related items
- Provide search for large sites
```

**Navigation Best Practices**:

**Top-Level Navigation**:
- 5-7 items maximum (follows Miller's Law: 7±2 items)
- Use clear, familiar labels
- Order by importance or frequency of use
- Consider card sorting with users

**Hierarchical Organization**:
```
Level 1: Main Categories (5-7 items)
├─ Level 2: Subcategories (5-7 per category)
│  └─ Level 3: Specific pages (avoid going deeper if possible)
```

**For Large Sites**:
- Provide robust search functionality
- Use breadcrumbs for wayfinding
- Include a sitemap
- Consider faceted navigation for complex content

**Mobile Considerations**:
- Use hamburger menu or bottom navigation
- Prioritize most important items
- Make touch targets large enough (48px)
- Test with one-handed use

---

## 10. No Loading or Error States

### ❌ Mistake
```
[Submit] → Click → Nothing happens → User clicks again
No feedback, user is confused
```

**Why It's Bad**:
- Users don't know if action was registered
- May lead to duplicate submissions
- Increases user anxiety and frustration
- Makes app feel unresponsive or broken

### ✅ Solution
```
[Submit] → [Submitting...] → [✓ Saved]
Clear feedback at every step
```

**Required States for All Interactive Elements**:

1. **Default**: Resting state
2. **Hover**: Mouse is over element
3. **Focus**: Element is keyboard-focused
4. **Active**: Element is being clicked/tapped
5. **Loading**: Action is in progress
6. **Success**: Action completed successfully
7. **Error**: Action failed
8. **Disabled**: Element is not interactive

**Implementation Example**:
```html
<!-- Button with all states -->
<button
  class="btn"
  :class="{
    'btn-loading': isLoading,
    'btn-success': isSuccess,
    'btn-error': isError
  }"
  :disabled="isLoading || isDisabled"
  :aria-busy="isLoading"
  @click="handleSubmit"
>
  <span v-if="isLoading" class="spinner" aria-hidden="true"></span>
  <span v-if="isSuccess" class="check-icon" aria-hidden="true">✓</span>
  <span v-if="isError" class="error-icon" aria-hidden="true">⚠</span>
  {{ buttonText }}
</button>
```

**Loading State Best Practices**:
- Disable button during loading to prevent duplicate submissions
- Show loading indicator (spinner, skeleton, progress bar)
- Update button text ("Saving..." instead of "Save")
- Use `aria-busy="true"` for screen readers
- For long operations, show progress percentage
- Allow users to cancel long-running operations

**Success/Error Feedback**:
- Show clear success message (toast, checkmark)
- Show specific error message with recovery steps
- Auto-dismiss success messages after 3-5 seconds
- Keep error messages visible until user takes action

---

## Summary

Avoid these common UI/UX mistakes to create better user experiences:

1. **Color Contrast**: Test and ensure 4.5:1 for text, 3:1 for UI
2. **Color Indicators**: Never rely on color alone, add icons and text
3. **Touch Targets**: 44x44px minimum, 48x48px recommended
4. **Semantic HTML**: Use proper elements (`<button>`, `<a>`, etc.)
5. **Form Labels**: Always label inputs with visible `<label>` elements
6. **Consistency**: Create and follow a design system
7. **Error Messages**: Be specific, helpful, and actionable
8. **Auto-Play**: Never auto-play audio, provide user controls
9. **Navigation**: Limit top-level items to 5-7, use clear hierarchy
10. **Feedback**: Provide loading, success, and error states

**Testing Checklist**:
- [ ] Run automated accessibility audits (axe, WAVE)
- [ ] Test with screen readers (NVDA, JAWS, VoiceOver)
- [ ] Check color contrast ratios
- [ ] Test keyboard navigation
- [ ] Verify touch target sizes on mobile devices
- [ ] Test with color blindness simulators
- [ ] Review all interactive states
- [ ] Validate with real users

By avoiding these anti-patterns, you'll create more accessible, usable, and professional interfaces.
