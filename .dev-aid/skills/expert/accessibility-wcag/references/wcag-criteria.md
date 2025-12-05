# WCAG 2.2 Success Criteria Reference

## Level A (Minimum Compliance)

### 1.1 Text Alternatives

**1.1.1 Non-text Content** (A)
- All non-text content has text alternative
- Images have alt text
- Form buttons have accessible names
- Time-based media has alternatives

```html
<!-- Good -->
<img src="logo.png" alt="Company Name" />
<button type="submit">
  <svg aria-hidden="true"><!-- icon --></svg>
  Submit Form
</button>
```

---

### 1.2 Time-based Media

**1.2.1 Audio-only and Video-only (Prerecorded)** (A)
- Provide alternative for prerecorded audio-only
- Provide alternative for prerecorded video-only

**1.2.2 Captions (Prerecorded)** (A)
- Captions for all prerecorded audio in synchronized media

**1.2.3 Audio Description or Media Alternative (Prerecorded)** (A)
- Audio description or media alternative for prerecorded video

---

### 1.3 Adaptable

**1.3.1 Info and Relationships** (A)
- Information, structure, and relationships can be programmatically determined

```html
<!-- Good: Semantic structure -->
<table>
  <thead>
    <tr>
      <th scope="col">Name</th>
      <th scope="col">Age</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>John</td>
      <td>30</td>
    </tr>
  </tbody>
</table>
```

**1.3.2 Meaningful Sequence** (A)
- Reading order is logical and intuitive

**1.3.3 Sensory Characteristics** (A)
- Instructions don't rely solely on sensory characteristics

```html
<!-- Bad -->
<p>Click the red button on the right</p>

<!-- Good -->
<p>Click the "Submit" button to continue</p>
```

---

### 1.4 Distinguishable

**1.4.1 Use of Color** (A)
- Color is not the only means of conveying information

**1.4.2 Audio Control** (A)
- Mechanism to pause/stop audio that plays automatically

---

### 2.1 Keyboard Accessible

**2.1.1 Keyboard** (A)
- All functionality available from keyboard

**2.1.2 No Keyboard Trap** (A)
- Keyboard focus can be moved away from component

```typescript
// Good: Modal with keyboard escape
modal.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closeModal()
  }
})
```

**2.1.4 Character Key Shortcuts** (A)
- Single character shortcuts can be turned off or remapped

---

### 2.2 Enough Time

**2.2.1 Timing Adjustable** (A)
- User can turn off, adjust, or extend time limits

**2.2.2 Pause, Stop, Hide** (A)
- Moving, blinking, scrolling content can be paused

---

### 2.3 Seizures and Physical Reactions

**2.3.1 Three Flashes or Below Threshold** (A)
- No content flashes more than 3 times per second

---

### 2.4 Navigable

**2.4.1 Bypass Blocks** (A)
- Mechanism to skip repeated content

```html
<!-- Good: Skip link -->
<a href="#main-content" class="skip-link">Skip to main content</a>
<main id="main-content">...</main>
```

**2.4.2 Page Titled** (A)
- Web pages have descriptive titles

**2.4.3 Focus Order** (A)
- Focus order is logical and preserves meaning

**2.4.4 Link Purpose (In Context)** (A)
- Purpose of link can be determined from link text

---

### 2.5 Input Modalities

**2.5.1 Pointer Gestures** (A)
- Single-point alternative for multipoint gestures

**2.5.2 Pointer Cancellation** (A)
- Down-event doesn't execute function

**2.5.3 Label in Name** (A)
- Accessible name contains visible text

**2.5.4 Motion Actuation** (A)
- Functionality triggered by motion can be disabled

---

### 3.1 Readable

**3.1.1 Language of Page** (A)
- Default language can be programmatically determined

```html
<html lang="en">
```

---

### 3.2 Predictable

**3.2.1 On Focus** (A)
- Focus doesn't initiate change of context

**3.2.2 On Input** (A)
- Changing setting doesn't automatically cause change of context

**3.2.6 Consistent Help** (A) - NEW in 2.2
- Help mechanisms appear in consistent order

---

### 3.3 Input Assistance

**3.3.1 Error Identification** (A)
- Errors are identified and described to user

**3.3.2 Labels or Instructions** (A)
- Labels or instructions provided when input is required

```html
<label for="email">Email address</label>
<input
  type="email"
  id="email"
  aria-required="true"
  aria-describedby="email-hint"
/>
<p id="email-hint">We'll never share your email</p>
```

**3.3.7 Redundant Entry** (A) - NEW in 2.2
- Information previously entered can be auto-populated

---

### 4.1 Compatible

**4.1.2 Name, Role, Value** (A)
- Name and role can be programmatically determined

```html
<button
  type="button"
  aria-pressed="false"
  aria-label="Toggle dark mode"
>
  <svg aria-hidden="true"><!-- icon --></svg>
</button>
```

---

## Level AA (Standard Compliance)

### 1.3 Adaptable

**1.3.4 Orientation** (AA)
- Content not restricted to single orientation

**1.3.5 Identify Input Purpose** (AA)
- Purpose of input fields can be programmatically determined

```html
<input
  type="email"
  autocomplete="email"
  aria-label="Email address"
/>
```

---

### 1.4 Distinguishable

**1.4.3 Contrast (Minimum)** (AA)
- Text has contrast ratio of at least 4.5:1
- Large text has contrast ratio of at least 3:1

**1.4.4 Resize Text** (AA)
- Text can be resized to 200% without loss of content

**1.4.5 Images of Text** (AA)
- Use text instead of images of text

**1.4.10 Reflow** (AA)
- Content reflows at 320px without horizontal scrolling

**1.4.11 Non-text Contrast** (AA)
- UI components have contrast ratio of at least 3:1

**1.4.12 Text Spacing** (AA)
- No loss of content when text spacing is adjusted

**1.4.13 Content on Hover or Focus** (AA)
- Additional content on hover/focus is dismissible, hoverable, persistent

---

### 2.4 Navigable

**2.4.5 Multiple Ways** (AA)
- Multiple ways to locate pages within set

**2.4.6 Headings and Labels** (AA)
- Headings and labels describe topic or purpose

**2.4.7 Focus Visible** (AA)
- Keyboard focus indicator is visible

```css
:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}
```

**2.4.11 Focus Not Obscured (Minimum)** (AA) - NEW in 2.2
- Focused element is at least partially visible

---

### 2.5 Input Modalities

**2.5.7 Dragging Movements** (AA) - NEW in 2.2
- Single pointer alternative for dragging movements

**2.5.8 Target Size (Minimum)** (AA) - NEW in 2.2
- Touch targets at least 24x24 CSS pixels

---

### 3.1 Readable

**3.1.2 Language of Parts** (AA)
- Language of each passage can be programmatically determined

```html
<p>The French word for cat is <span lang="fr">chat</span>.</p>
```

---

### 3.2 Predictable

**3.2.3 Consistent Navigation** (AA)
- Navigation mechanisms in consistent order

**3.2.4 Consistent Identification** (AA)
- Components with same functionality identified consistently

---

### 3.3 Input Assistance

**3.3.3 Error Suggestion** (AA)
- Error suggestions provided when errors detected

**3.3.4 Error Prevention (Legal, Financial, Data)** (AA)
- Submissions are reversible, checked, or confirmed

**3.3.8 Accessible Authentication (Minimum)** (AA) - NEW in 2.2
- Authentication doesn't rely on cognitive function test

```html
<!-- Good: Support password managers -->
<input
  type="password"
  autocomplete="current-password"
/>
```

---

## Level AAA (Enhanced Compliance)

### 1.4 Distinguishable

**1.4.6 Contrast (Enhanced)** (AAA)
- Text has contrast ratio of at least 7:1
- Large text has contrast ratio of at least 4.5:1

**1.4.7 Low or No Background Audio** (AAA)
- Audio doesn't contain background sounds

**1.4.8 Visual Presentation** (AAA)
- Users can select colors, line spacing, text alignment
- Line length no more than 80 characters

**1.4.9 Images of Text (No Exception)** (AAA)
- Images of text only for decoration or essential

---

### 2.1 Keyboard Accessible

**2.1.3 Keyboard (No Exception)** (AAA)
- All functionality available from keyboard

---

### 2.2 Enough Time

**2.2.3 No Timing** (AAA)
- No time limits

**2.2.4 Interruptions** (AAA)
- Interruptions can be postponed or suppressed

**2.2.5 Re-authenticating** (AAA)
- Data preserved when re-authenticating

**2.2.6 Timeouts** (AAA)
- Users warned of timeouts from inactivity

---

### 2.3 Seizures and Physical Reactions

**2.3.2 Three Flashes** (AAA)
- No content flashes more than 3 times per second

**2.3.3 Animation from Interactions** (AAA)
- Motion animation can be disabled

---

### 2.4 Navigable

**2.4.8 Location** (AAA)
- Information about user's location in set of pages

**2.4.9 Link Purpose (Link Only)** (AAA)
- Purpose of link identified from link text alone

**2.4.10 Section Headings** (AAA)
- Section headings organize content

**2.4.12 Focus Not Obscured (Enhanced)** (AAA) - NEW in 2.2
- Focused element is fully visible

**2.4.13 Focus Appearance** (AAA) - NEW in 2.2
- Focus indicator has minimum size and contrast

---

### 2.5 Input Modalities

**2.5.5 Target Size (Enhanced)** (AAA)
- Touch targets at least 44x44 CSS pixels

**2.5.6 Concurrent Input Mechanisms** (AAA)
- Content doesn't restrict input modalities

---

### 3.1 Readable

**3.1.3 Unusual Words** (AAA)
- Mechanism for identifying unusual words

**3.1.4 Abbreviations** (AAA)
- Mechanism for identifying expanded form

**3.1.5 Reading Level** (AAA)
- Supplemental content for advanced reading level

**3.1.6 Pronunciation** (AAA)
- Mechanism for pronunciation of ambiguous words

---

### 3.2 Predictable

**3.2.5 Change on Request** (AAA)
- Changes of context initiated only by user request

---

### 3.3 Input Assistance

**3.3.5 Help** (AAA)
- Context-sensitive help available

**3.3.6 Error Prevention (All)** (AAA)
- All submissions are reversible, checked, or confirmed

**3.3.9 Accessible Authentication (Enhanced)** (AAA) - NEW in 2.2
- Authentication doesn't rely on cognitive function test or object recognition

---

## Quick Reference by Component

### Buttons
- ✅ 1.1.1: Accessible name
- ✅ 2.1.1: Keyboard accessible
- ✅ 2.4.7: Focus visible
- ✅ 4.1.2: Correct role and states

### Forms
- ✅ 1.3.1: Labels associated
- ✅ 1.3.5: Autocomplete attributes
- ✅ 3.3.1: Error identification
- ✅ 3.3.2: Labels provided
- ✅ 3.3.3: Error suggestions

### Images
- ✅ 1.1.1: Alt text provided
- ✅ 1.4.5: Avoid images of text
- ✅ 1.4.11: Sufficient contrast

### Navigation
- ✅ 2.4.1: Skip links
- ✅ 2.4.3: Logical focus order
- ✅ 2.4.4: Clear link purpose
- ✅ 3.2.3: Consistent navigation

### Modals/Dialogs
- ✅ 2.1.2: No keyboard trap
- ✅ 2.4.3: Focus management
- ✅ 4.1.2: Correct ARIA attributes

### Live Regions
- ✅ 4.1.3: Status messages
- ✅ Proper aria-live values
- ✅ Minimal updates
