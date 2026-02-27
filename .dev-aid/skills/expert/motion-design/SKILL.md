---
name: motion-design
version: 2.0.0
description: "Motion design principles for UI animations, transitions, easing curves, and micro-interactions. Use when planning animation strategies, choosing easing curves, or designing transition choreography. Do NOT use for GSAP-specific implementation (use gsap)."
risk_level: LOW
token_budget: 3000
---
# Motion Design - Code Generation Rules

---

## 1. Security Principles

### 1.1 DOM Manipulation Safety (CWE-79)

**Principle:** Animation libraries manipulate DOM. Never animate user-controlled content without sanitization.

```typescript
// ❌ WRONG - Animating unsanitized content
function animateText(userInput: string) {
  element.innerHTML = userInput;  // XSS vulnerability
  gsap.from(element, { opacity: 0 });
}

// ✅ CORRECT - Use textContent for user data
function animateText(userInput: string) {
  element.textContent = userInput;  // Safe
  gsap.from(element, { opacity: 0 });
}
```

### 1.2 Resource Exhaustion Prevention (CWE-400)

**Principle:** Unbounded animations can freeze the browser. Always limit concurrent animations.

```typescript
// ❌ WRONG - Unbounded animation creation
items.forEach(item => {
  gsap.to(item, { x: 100 });  // Thousands of animations
});

// ✅ CORRECT - Batch with stagger or limit
const MAX_CONCURRENT = 50;
gsap.to(items.slice(0, MAX_CONCURRENT), {
  x: 100,
  stagger: 0.02,  // Spread load
});
```

### 1.3 Accessibility Compliance (WCAG 2.3.3)

**Principle:** Animations must respect user preferences and avoid seizure-inducing patterns.

---

## 2. Version Requirements

```json
{
  "gsap": "^3.12.0",
  "framer-motion": "^11.0.0",
  "@vueuse/motion": "^2.1.0",
  "animejs": "^3.2.2"
}
```

---

## 3. Code Patterns

### WHEN implementing animations, always respect prefers-reduced-motion

```typescript
// ❌ WRONG - Ignoring user preferences
const animate = () => {
  gsap.to(element, { rotation: 360, duration: 1 });
};

// ✅ CORRECT - Check reduced motion preference
const prefersReducedMotion = window.matchMedia(
  '(prefers-reduced-motion: reduce)'
).matches;

const animate = () => {
  if (prefersReducedMotion) {
    // Instant state change, no animation
    gsap.set(element, { rotation: 360 });
    return;
  }
  gsap.to(element, { rotation: 360, duration: 1 });
};

// React hook for reduced motion
import { useReducedMotion } from 'framer-motion';

function AnimatedComponent() {
  const shouldReduceMotion = useReducedMotion();

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{
        duration: shouldReduceMotion ? 0 : 0.5,
      }}
    />
  );
}
```

### WHEN using easing functions, apply appropriate curves for context

```typescript
// ❌ WRONG - Linear easing for UI (feels robotic)
gsap.to(modal, { y: 0, ease: 'none' });

// ❌ WRONG - Bounce for important UI (distracting)
gsap.to(errorMessage, { scale: 1, ease: 'bounce' });

// ✅ CORRECT - Context-appropriate easing
import { gsap } from 'gsap';

// Standard easing tokens aligned with design system
const EASING = {
  // Enter: Start fast, end slow (elements appearing)
  enter: 'power2.out',       // cubic-bezier(0.33, 1, 0.68, 1)

  // Exit: Start slow, end fast (elements leaving)
  exit: 'power2.in',         // cubic-bezier(0.32, 0, 0.67, 0)

  // Standard: Symmetric for state changes
  standard: 'power2.inOut',  // cubic-bezier(0.65, 0, 0.35, 1)

  // Emphasized: More pronounced for important UI
  emphasized: 'power3.out',  // cubic-bezier(0.16, 1, 0.3, 1)

  // Spring: Natural feel for interactive elements
  spring: 'elastic.out(1, 0.5)',
} as const;

// Duration tokens (in seconds)
const DURATION = {
  instant: 0.1,    // Micro-interactions
  fast: 0.2,       // Small UI elements
  normal: 0.3,     // Standard transitions
  slow: 0.5,       // Large elements, emphasis
  deliberate: 0.8, // Dramatic, storytelling
} as const;

// Usage
gsap.to(modal, {
  y: 0,
  opacity: 1,
  duration: DURATION.normal,
  ease: EASING.enter,
});
```

### WHEN creating scroll-linked animations, use intersection observer pattern

```typescript
// ❌ WRONG - Scroll event listener (performance killer)
window.addEventListener('scroll', () => {
  elements.forEach(el => {
    const rect = el.getBoundingClientRect();
    if (rect.top < window.innerHeight) {
      gsap.to(el, { opacity: 1 });
    }
  });
});

// ✅ CORRECT - IntersectionObserver with GSAP ScrollTrigger
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

// Reveal animation on scroll
function createScrollReveal(
  elements: HTMLElement[],
  options: { stagger?: number; threshold?: number } = {}
) {
  const { stagger = 0.1, threshold = 0.2 } = options;

  gsap.set(elements, { opacity: 0, y: 30 });

  elements.forEach((element, index) => {
    gsap.to(element, {
      opacity: 1,
      y: 0,
      duration: DURATION.normal,
      ease: EASING.enter,
      delay: index * stagger,
      scrollTrigger: {
        trigger: element,
        start: `top ${100 - threshold * 100}%`,
        once: true,  // Animate only once
      },
    });
  });
}

// Parallax with performance guard
function createParallax(element: HTMLElement, speed: number = 0.5) {
  // Respect reduced motion
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    return;
  }

  gsap.to(element, {
    yPercent: -50 * speed,
    ease: 'none',
    scrollTrigger: {
      trigger: element,
      start: 'top bottom',
      end: 'bottom top',
      scrub: true,
    },
  });
}
```

### WHEN animating with Framer Motion, use layout animations efficiently

```tsx
// ❌ WRONG - Animating width/height (triggers layout)
<motion.div
  animate={{ width: isOpen ? 300 : 0 }}  // Layout thrashing
/>

// ✅ CORRECT - Use layout animations for size changes
import { motion, AnimatePresence, LayoutGroup } from 'framer-motion';

function ExpandableCard({ isExpanded, children }: Props) {
  return (
    <motion.div
      layout
      transition={{
        layout: { duration: 0.3, ease: [0.4, 0, 0.2, 1] },
      }}
      style={{
        overflow: 'hidden',
        borderRadius: 12,
      }}
    >
      <motion.div layout="position">
        {children}
      </motion.div>
    </motion.div>
  );
}

// Shared element transitions
function ImageGrid({ items, selectedId, onSelect }) {
  return (
    <LayoutGroup>
      <div className="grid">
        {items.map(item => (
          <motion.div
            key={item.id}
            layoutId={`card-${item.id}`}
            onClick={() => onSelect(item.id)}
          >
            <motion.img
              layoutId={`image-${item.id}`}
              src={item.src}
            />
          </motion.div>
        ))}
      </div>

      <AnimatePresence>
        {selectedId && (
          <motion.div
            layoutId={`card-${selectedId}`}
            className="modal"
          >
            <motion.img
              layoutId={`image-${selectedId}`}
              src={items.find(i => i.id === selectedId)?.src}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </LayoutGroup>
  );
}
```

### WHEN creating complex sequences, use timeline composition

```typescript
// ❌ WRONG - Nested callbacks (callback hell)
gsap.to(a, {
  x: 100,
  onComplete: () => {
    gsap.to(b, {
      y: 50,
      onComplete: () => {
        gsap.to(c, { opacity: 0 });
      },
    });
  },
});

// ✅ CORRECT - Timeline composition with labels
import { gsap } from 'gsap';

interface SequenceStep {
  targets: gsap.TweenTarget;
  vars: gsap.TweenVars;
  position?: string | number;
}

function createSequence(
  steps: SequenceStep[],
  options: { paused?: boolean; onComplete?: () => void } = {}
): gsap.core.Timeline {
  const tl = gsap.timeline({
    paused: options.paused ?? false,
    onComplete: options.onComplete,
  });

  steps.forEach(({ targets, vars, position }) => {
    tl.to(targets, vars, position);
  });

  return tl;
}

// Complex modal animation
function createModalAnimation(modal: HTMLElement) {
  const overlay = modal.querySelector('.overlay');
  const content = modal.querySelector('.content');
  const items = modal.querySelectorAll('.item');

  return gsap.timeline({ paused: true })
    // Phase 1: Overlay fade
    .to(overlay, {
      opacity: 1,
      duration: DURATION.fast,
    })
    // Phase 2: Content scale up (at 50% of overlay)
    .fromTo(content,
      { scale: 0.9, opacity: 0 },
      {
        scale: 1,
        opacity: 1,
        duration: DURATION.normal,
        ease: EASING.emphasized,
      },
      '-=0.1'  // Overlap slightly
    )
    // Label for items
    .addLabel('itemsStart')
    // Phase 3: Staggered items
    .from(items, {
      y: 20,
      opacity: 0,
      duration: DURATION.fast,
      stagger: 0.05,
      ease: EASING.enter,
    }, 'itemsStart');
}

// Usage
const modalAnim = createModalAnimation(modalElement);
modalAnim.play();  // Open
modalAnim.reverse();  // Close
```

### WHEN implementing micro-interactions, use GPU-accelerated properties

```typescript
// ❌ WRONG - Animating expensive properties
gsap.to(element, {
  left: 100,      // Triggers layout
  width: 200,     // Triggers layout
  boxShadow: '0 10px 20px rgba(0,0,0,0.2)',  // Expensive
});

// ✅ CORRECT - GPU-accelerated transforms and opacity
import { gsap } from 'gsap';

// Prefer transform and opacity (compositor-only)
const SAFE_PROPERTIES = [
  'x', 'y', 'z',           // translateX/Y/Z
  'rotation', 'rotationX', 'rotationY', 'rotationZ',
  'scale', 'scaleX', 'scaleY',
  'opacity',
] as const;

// Button press effect
function createPressEffect(button: HTMLElement) {
  const state = { pressed: false };

  const handleDown = () => {
    if (state.pressed) return;
    state.pressed = true;

    gsap.to(button, {
      scale: 0.95,
      duration: 0.1,
      ease: 'power2.out',
    });
  };

  const handleUp = () => {
    if (!state.pressed) return;
    state.pressed = false;

    gsap.to(button, {
      scale: 1,
      duration: 0.2,
      ease: EASING.spring,
    });
  };

  button.addEventListener('pointerdown', handleDown);
  button.addEventListener('pointerup', handleUp);
  button.addEventListener('pointerleave', handleUp);

  // Cleanup function
  return () => {
    button.removeEventListener('pointerdown', handleDown);
    button.removeEventListener('pointerup', handleUp);
    button.removeEventListener('pointerleave', handleUp);
  };
}

// Hover magnetic effect
function createMagneticEffect(
  element: HTMLElement,
  strength: number = 0.3
) {
  const prefersReducedMotion = window.matchMedia(
    '(prefers-reduced-motion: reduce)'
  ).matches;

  if (prefersReducedMotion) return () => {};

  const handleMove = (e: PointerEvent) => {
    const rect = element.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    const deltaX = (e.clientX - centerX) * strength;
    const deltaY = (e.clientY - centerY) * strength;

    gsap.to(element, {
      x: deltaX,
      y: deltaY,
      duration: 0.3,
      ease: 'power2.out',
    });
  };

  const handleLeave = () => {
    gsap.to(element, {
      x: 0,
      y: 0,
      duration: 0.5,
      ease: EASING.spring,
    });
  };

  element.addEventListener('pointermove', handleMove);
  element.addEventListener('pointerleave', handleLeave);

  return () => {
    element.removeEventListener('pointermove', handleMove);
    element.removeEventListener('pointerleave', handleLeave);
  };
}
```

---

## 4. Anti-Patterns

Do not:
- Animate `left`/`top`/`width`/`height` when transform works
- Ignore `prefers-reduced-motion` media query
- Create unbounded animation loops without kill conditions
- Use `scroll` event listener instead of IntersectionObserver
- Chain animations with nested callbacks
- Animate more than 50 elements simultaneously
- Use flash/strobe effects faster than 3Hz (seizure risk)

---

## 5. Testing

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { gsap } from 'gsap';

describe('Motion Design Patterns', () => {
  beforeEach(() => {
    // Reset GSAP
    gsap.killTweensOf('*');
# ... (additional test cases follow same pattern)
```

---

## 6. Pre-Generation Checklist

Before generating animation code:

- [ ] Reduced motion: `prefers-reduced-motion` check implemented
- [ ] GPU properties: Using transform/opacity over layout properties
- [ ] Resource limits: Max 50 concurrent animations
- [ ] Scroll handling: IntersectionObserver, not scroll events
- [ ] Easing tokens: Context-appropriate curves from design system
- [ ] Duration tokens: Consistent timing from design system
- [ ] Cleanup: Event listeners removed on unmount
- [ ] Timeline pattern: Using timelines for sequences, not callbacks
- [ ] Seizure safety: No flashing > 3Hz

---
