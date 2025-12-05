# UI/UX Anti-Patterns and Common Mistakes

## Overview

This document catalogs common UI/UX mistakes and anti-patterns to avoid. Each section shows the problematic approach and the correct solution.

---

## 1. Overusing Glass-Morphism

### ❌ DON'T: Stack Multiple Glass Layers

**Problem**: Too many glass-morphism layers create visual noise and hurt readability.

```css
/* ❌ Bad - Too many layers */
.page {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.section {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.nested-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}
```

### ✅ DO: Strategic Use of Glass Effect

**Solution**: Use glass-morphism sparingly on focal points only.

```css
/* ✅ Good - Strategic use */
.page {
  background: var(--bg-solid);
  /* Solid background for base */
}

.card {
  background: var(--surface-glass);
  backdrop-filter: blur(20px);
  /* Glass effect only on interactive cards */
}

.nested-content {
  background: transparent;
  /* No additional glass layers */
}
```

**Guidelines**:
- Use glass-morphism for 1-2 layers maximum
- Reserve it for focal points (modals, cards, overlays)
- Ensure sufficient contrast for text readability
- Test on different background images

---

## 2. Ignoring Information Density

### ❌ DON'T: Waste Screen Space

**Problem**: Excessive padding/margins reduce usable screen space, especially on mobile.

```css
/* ❌ Bad - Wasted space */
.widget {
  padding: 48px;
  margin: 32px;
}

.card-title {
  margin-bottom: 32px;
}

.form-field {
  margin-bottom: 40px;
}
```

### ✅ DO: Use Appropriate Density

**Solution**: Follow spacing system based on content hierarchy and device size.

```css
/* ✅ Good - Appropriate density */
.widget {
  padding: var(--space-4); /* 16px */
  margin: var(--space-3); /* 12px */
}

.card-title {
  margin-bottom: var(--space-3); /* 12px */
}

.form-field {
  margin-bottom: var(--space-4); /* 16px */
}

/* Adjust for larger screens */
@media (min-width: 1024px) {
  .widget {
    padding: var(--space-6); /* 32px */
  }
}
```

**Guidelines**:
- Use 8px spacing grid consistently
- Adjust density for screen size
- Higher density for data-heavy interfaces
- Lower density for marketing/landing pages

---

## 3. Neglecting Loading States

### ❌ DON'T: Show Nothing While Loading

**Problem**: Users don't know if the app is working or broken.

```jsx
/* ❌ Bad - No feedback */
function UserProfile({ userId }) {
  const { data } = useQuery(['user', userId])

  return data ? <Profile user={data} /> : null
}
```

### ✅ DO: Provide Complete State Handling

**Solution**: Handle all states: loading, error, empty, and success.

```jsx
/* ✅ Good - Complete states */
function UserProfile({ userId }) {
  const { data, loading, error } = useQuery(['user', userId])

  if (loading) {
    return <ProfileSkeleton />
  }

  if (error) {
    return (
      <ErrorMessage
        error={error}
        retry={() => refetch()}
      />
    )
  }

  if (!data) {
    return <EmptyState message="User not found" />
  }

  return <Profile user={data} />
}
```

**Required States**:
- **Loading**: Skeleton screens or progress indicators
- **Error**: Error message with retry option
- **Empty**: Clear empty state with call-to-action
- **Success**: Rendered content

---

## 4. Poor Focus Management

### ❌ DON'T: Hide or Ignore Focus States

**Problem**: Keyboard users can't navigate effectively.

```css
/* ❌ Bad - No focus indicators */
button:focus {
  outline: none;
}

a:focus {
  outline: 0;
}
```

### ✅ DO: Provide Clear Focus Indicators

**Solution**: Make focus states visible and distinct.

```css
/* ✅ Good - Visible focus states */
:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
  border-radius: 4px;
}

/* Custom focus for interactive elements */
button:focus-visible {
  box-shadow:
    0 0 0 3px rgba(0, 188, 212, 0.3),
    inset 0 0 0 2px var(--color-primary-500);
}
```

**Guidelines**:
- Never remove focus outline without replacement
- Use `:focus-visible` to show focus only for keyboard
- Ensure 3:1 contrast ratio for focus indicators
- Test navigation with Tab key

---

## 5. Inconsistent Visual Hierarchy

### ❌ DON'T: Use Random Sizes and Weights

**Problem**: Inconsistent typography confuses users about importance.

```css
/* ❌ Bad - Inconsistent sizing */
.title-1 { font-size: 32px; font-weight: 700; }
.title-2 { font-size: 28px; font-weight: 600; }
.heading { font-size: 24px; font-weight: 700; }
.subtitle { font-size: 19px; font-weight: 500; }
.text { font-size: 16px; }
```

### ✅ DO: Use Typography Scale

**Solution**: Follow modular scale for consistent hierarchy.

```css
/* ✅ Good - Modular scale (1.25 ratio) */
.heading-1 {
  font-size: var(--font-size-3xl); /* 2.441rem */
  font-weight: 700;
  line-height: var(--line-height-tight);
}

.heading-2 {
  font-size: var(--font-size-2xl); /* 1.953rem */
  font-weight: 600;
  line-height: var(--line-height-tight);
}

.heading-3 {
  font-size: var(--font-size-xl); /* 1.563rem */
  font-weight: 600;
  line-height: var(--line-height-normal);
}

.body {
  font-size: var(--font-size-base); /* 1rem */
  font-weight: 400;
  line-height: var(--line-height-normal);
}
```

---

## 6. Ignoring Mobile Touch Targets

### ❌ DON'T: Make Touch Targets Too Small

**Problem**: Small buttons are hard to tap on mobile devices.

```css
/* ❌ Bad - Too small for touch */
.icon-button {
  width: 24px;
  height: 24px;
  padding: 4px;
}
```

### ✅ DO: Ensure Minimum 44x44px Touch Targets

**Solution**: Meet accessibility guidelines for touch target size.

```css
/* ✅ Good - Proper touch target */
.icon-button {
  min-width: 44px;
  min-height: 44px;
  padding: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.icon-button svg {
  width: 24px;
  height: 24px;
}
```

**Guidelines**:
- Minimum 44x44px for all interactive elements
- Add padding around icons to increase hit area
- Provide sufficient spacing between touch targets (8px minimum)
- Test on actual mobile devices

---

## 7. Lack of Animation Consideration

### ❌ DON'T: Force Animations on Everyone

**Problem**: Animations can cause motion sickness or distraction for some users.

```css
/* ❌ Bad - Always animates */
.card {
  transition: all 0.3s ease;
}

.card:hover {
  transform: scale(1.1) rotate(5deg);
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.notification {
  animation: bounce 1s infinite;
}
```

### ✅ DO: Respect Motion Preferences

**Solution**: Respect `prefers-reduced-motion` user preference.

```css
/* ✅ Good - Respects preferences */
.card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Disable animations for those who prefer reduced motion */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

---

## 8. Poor Color Contrast

### ❌ DON'T: Use Low-Contrast Text

**Problem**: Low contrast makes text hard to read, especially for users with visual impairments.

```css
/* ❌ Bad - Insufficient contrast */
.text-muted {
  color: rgba(255, 255, 255, 0.3); /* Contrast ratio: 1.5:1 */
}

.on-primary {
  color: #00bcd4; /* Cyan on white: 2.1:1 */
}
```

### ✅ DO: Ensure WCAG AA Compliance

**Solution**: Meet minimum 4.5:1 contrast ratio for normal text.

```css
/* ✅ Good - Sufficient contrast */
.text-primary {
  color: rgba(255, 255, 255, 0.95); /* 18:1 on dark bg */
}

.text-secondary {
  color: rgba(255, 255, 255, 0.7); /* 8.5:1 on dark bg */
}

.text-disabled {
  color: rgba(255, 255, 255, 0.38); /* 4.7:1 on dark bg */
}
```

**Contrast Requirements**:
- Normal text (< 18pt): 4.5:1 minimum
- Large text (≥ 18pt): 3:1 minimum
- UI components and graphics: 3:1 minimum
- WCAG AAA: 7:1 for normal text, 4.5:1 for large text

**Tools**:
- WebAIM Contrast Checker
- Chrome DevTools contrast ratio tool
- Stark plugin for Figma

---

## 9. Overusing z-index

### ❌ DON'T: Create Z-Index Wars

**Problem**: Random z-index values create unpredictable stacking.

```css
/* ❌ Bad - Z-index chaos */
.modal { z-index: 9999; }
.dropdown { z-index: 99999; }
.tooltip { z-index: 999999; }
.popup { z-index: 9999999; }
```

### ✅ DO: Use Z-Index Scale

**Solution**: Define a consistent z-index scale.

```css
/* ✅ Good - Defined scale */
:root {
  --z-dropdown: 1000;
  --z-sticky: 1020;
  --z-fixed: 1030;
  --z-modal-backdrop: 1040;
  --z-modal: 1050;
  --z-popover: 1060;
  --z-tooltip: 1070;
}

.modal-backdrop {
  z-index: var(--z-modal-backdrop);
}

.modal {
  z-index: var(--z-modal);
}

.tooltip {
  z-index: var(--z-tooltip);
}
```

---

## 10. Not Testing Edge Cases

### ❌ DON'T: Only Test Happy Path

**Problem**: Real-world data often breaks layouts.

```jsx
/* ❌ Bad - Assumes perfect data */
<div className="user-card">
  <h3>{user.name}</h3>
  <p>{user.bio}</p>
  <img src={user.avatar} />
</div>
```

### ✅ DO: Handle All Data Scenarios

**Solution**: Test with edge cases and handle them gracefully.

```jsx
/* ✅ Good - Handles edge cases */
<div className="user-card">
  <h3 className="truncate" title={user.name}>
    {user.name || 'Anonymous User'}
  </h3>
  <p className="line-clamp-3">
    {user.bio || 'No bio provided'}
  </p>
  <img
    src={user.avatar || '/default-avatar.png'}
    alt={user.name}
    onError={(e) => {
      e.target.src = '/default-avatar.png'
    }}
  />
</div>
```

**Edge Cases to Test**:
- Empty states (no data)
- Very long text (names, descriptions)
- Missing images or broken URLs
- Special characters in text
- RTL languages
- Different screen sizes
- Slow network conditions
- Errors and failures

---

## Summary

Avoid these common pitfalls by:
1. Following established design systems
2. Testing with real data and edge cases
3. Respecting user preferences and accessibility
4. Using consistent scales (spacing, typography, z-index)
5. Providing feedback for all states
6. Testing on multiple devices and browsers

Always prioritize user experience over visual trends.
