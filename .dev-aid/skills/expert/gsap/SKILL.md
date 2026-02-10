---
name: gsap
version: 2.0.0
description: "GSAP animation patterns for timelines, tweens, ScrollTrigger, and complex motion sequences. Use when implementing GSAP animations, building scroll-driven effects, or orchestrating timeline sequences. Do NOT use for CSS transitions or non-GSAP animation libraries."
compatibility: "GSAP 3.12+"
risk_level: LOW
---

# GSAP Animation Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-79: XSS via Animation Targets**
- NEVER: `gsap.to(userSelector, {innerHTML: userContent})`
- ALWAYS: Sanitize selectors, never animate innerHTML with user data

### 0.3 Risk Level: LOW

**Verification requirements for LOW risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 DOM Manipulation Safety (CWE-79)

**Principle:** Never animate elements using untrusted selectors or inject user content.

```typescript
// ❌ WRONG - User-controlled selector
function animateElement(userSelector: string) {
  gsap.to(userSelector, { opacity: 0 });  // XSS risk!
}

// ✅ CORRECT - Validated element reference
function animateElement(element: HTMLElement | null) {
  if (!element) return;
  gsap.to(element, { opacity: 0 });
}

// ✅ CORRECT - Allowlist selectors
const ALLOWED_SELECTORS = ['.hero', '.card', '.modal'] as const;
type AllowedSelector = typeof ALLOWED_SELECTORS[number];

function animateBySelector(selector: AllowedSelector) {
  gsap.to(selector, { opacity: 0 });
}
```

### 1.2 Performance Safety (CWE-400)

**Principle:** Avoid layout thrashing. Use transforms over layout properties.

```typescript
// ❌ WRONG - Causes layout thrashing
gsap.to('.element', {
  left: 100,    // Triggers layout
  top: 100,     // Triggers layout
  width: 200,   // Triggers layout
});

// ✅ CORRECT - GPU-accelerated transforms
gsap.to('.element', {
  x: 100,       // transform: translateX()
  y: 100,       // transform: translateY()
  scale: 1.2,   // transform: scale()
});
```

### 1.3 Memory Management (CWE-401)

**Principle:** Always kill animations on component unmount. Use contexts for cleanup.

### 1.4 Accessibility (WCAG 2.1)

**Principle:** Respect `prefers-reduced-motion`. Provide static alternatives.

### 1.5 Bundle Size Optimization

**Principle:** Import only needed plugins. Use tree-shaking.

### 1.6 Event Handler Safety (CWE-400)

**Principle:** Debounce scroll/resize-triggered animations.

---

## 2. Version Requirements

**ALWAYS use these minimum versions:**

```json
{
  "gsap": "^3.12.0",
  "@gsap/react": "^2.1.0"
}
```

---

## 3. Code Patterns

### 3.1 WHEN creating basic animations

```typescript
// ❌ WRONG - No cleanup, hardcoded values
useEffect(() => {
  gsap.to('.box', { x: 100 });
}, []);

// ✅ CORRECT - React integration with GSAP Context
import { useRef, useLayoutEffect } from 'react';
import gsap from 'gsap';
import { useGSAP } from '@gsap/react';

// Register plugins once at app level
gsap.registerPlugin(ScrollTrigger, Flip);

interface AnimatedBoxProps {
  delay?: number;
  duration?: number;
}

function AnimatedBox({ delay = 0, duration = 1 }: AnimatedBoxProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const boxRef = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      // Check for reduced motion preference
      const prefersReducedMotion = window.matchMedia(
        '(prefers-reduced-motion: reduce)'
      ).matches;

      if (prefersReducedMotion) {
        // Set final state without animation
        gsap.set(boxRef.current, { x: 100, opacity: 1 });
        return;
      }

      // Animation with proper element reference
      gsap.to(boxRef.current, {
        x: 100,
        opacity: 1,
        duration,
        delay,
        ease: 'power2.out',
      });
    },
    { scope: containerRef, dependencies: [delay, duration] }
  );

  return (
    <div ref={containerRef}>
      <div ref={boxRef} className="box" style={{ opacity: 0 }}>
        Content
      </div>
    </div>
  );
}
```

### 3.2 WHEN creating complex timelines

```typescript
// ❌ WRONG - No structure, hard to maintain
gsap.to('.a', { x: 100 });
gsap.to('.b', { y: 50, delay: 0.5 });
gsap.to('.c', { scale: 1.2, delay: 1 });

// ✅ CORRECT - Structured timeline with labels
import gsap from 'gsap';

interface TimelineConfig {
  onComplete?: () => void;
  paused?: boolean;
}

function createHeroTimeline(
  container: HTMLElement,
  config: TimelineConfig = {}
): gsap.core.Timeline {
  const { onComplete, paused = false } = config;

  // Query elements within container (scoped)
  const heading = container.querySelector<HTMLElement>('.hero-heading');
  const subheading = container.querySelector<HTMLElement>('.hero-subheading');
  const cta = container.querySelector<HTMLElement>('.hero-cta');
  const image = container.querySelector<HTMLElement>('.hero-image');

  // Validate elements exist
  if (!heading || !subheading || !cta || !image) {
    console.warn('Hero timeline: Missing required elements');
    return gsap.timeline(); // Return empty timeline
  }

  const tl = gsap.timeline({
    paused,
    onComplete,
    defaults: {
      ease: 'power3.out',
      duration: 0.8,
    },
  });

  // Set initial states
  gsap.set([heading, subheading, cta], { opacity: 0, y: 30 });
  gsap.set(image, { opacity: 0, scale: 0.9 });

  // Build timeline with labels
  tl.addLabel('start')
    .to(heading, { opacity: 1, y: 0 }, 'start')
    .to(subheading, { opacity: 1, y: 0 }, 'start+=0.2')
    .addLabel('content')
    .to(cta, { opacity: 1, y: 0 }, 'content')
    .to(image, { opacity: 1, scale: 1, duration: 1 }, 'content-=0.3')
    .addLabel('complete');

  return tl;
}

// Usage in React
function HeroSection() {
  const containerRef = useRef<HTMLDivElement>(null);
  const timelineRef = useRef<gsap.core.Timeline | null>(null);

  useGSAP(
    () => {
      if (!containerRef.current) return;

      timelineRef.current = createHeroTimeline(containerRef.current, {
        onComplete: () => console.log('Animation complete'),
      });
    },
    { scope: containerRef }
  );

  // Expose control methods
  const replay = () => timelineRef.current?.restart();
  const pause = () => timelineRef.current?.pause();

  return (
    <section ref={containerRef} className="hero">
      <h1 className="hero-heading">Welcome</h1>
      <p className="hero-subheading">Discover more</p>
      <button className="hero-cta">Get Started</button>
      <img className="hero-image" src="/hero.jpg" alt="Hero" />
    </section>
  );
}
```

### 3.3 WHEN implementing ScrollTrigger

```typescript
// ❌ WRONG - No cleanup, global scope
ScrollTrigger.create({
  trigger: '.section',
  start: 'top center',
  onEnter: () => gsap.to('.section', { opacity: 1 }),
});

// ✅ CORRECT - Scoped ScrollTrigger with cleanup
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

interface ScrollAnimationConfig {
  trigger: HTMLElement;
  animation: gsap.core.Tween | gsap.core.Timeline;
  start?: string;
  end?: string;
  scrub?: boolean | number;
  pin?: boolean;
  markers?: boolean;
}

function createScrollAnimation(config: ScrollAnimationConfig): ScrollTrigger {
  const {
    trigger,
    animation,
    start = 'top 80%',
    end = 'bottom 20%',
    scrub = false,
    pin = false,
    markers = false,
  } = config;

  return ScrollTrigger.create({
    trigger,
    start,
    end,
    scrub,
    pin,
    markers: process.env.NODE_ENV === 'development' && markers,
    animation,
    // Accessibility: Disable in reduced motion mode
    onRefresh: (self) => {
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        self.disable();
        animation.progress(1); // Set to end state
      }
    },
  });
}

// React component with ScrollTrigger
function ParallaxSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const imageRef = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      if (!sectionRef.current || !imageRef.current) return;

      // Create animation
      const parallaxTween = gsap.fromTo(
        imageRef.current,
        { y: -50 },
        { y: 50, ease: 'none' }
      );

      // Create ScrollTrigger (auto-cleaned by useGSAP)
      createScrollAnimation({
        trigger: sectionRef.current,
        animation: parallaxTween,
        scrub: true,
        start: 'top bottom',
        end: 'bottom top',
      });
    },
    { scope: sectionRef }
  );

  return (
    <section ref={sectionRef} className="parallax-section">
      <div ref={imageRef} className="parallax-image" />
    </section>
  );
}

// Batch ScrollTrigger animations for performance
function createBatchedScrollAnimations(
  elements: HTMLElement[],
  animationProps: gsap.TweenVars
): void {
  ScrollTrigger.batch(elements, {
    onEnter: (batch) => {
      gsap.to(batch, {
        ...animationProps,
        stagger: 0.1,
        overwrite: true,
      });
    },
    onLeave: (batch) => {
      gsap.to(batch, {
        opacity: 0,
        y: -20,
        stagger: 0.05,
        overwrite: true,
      });
    },
    onEnterBack: (batch) => {
      gsap.to(batch, {
        ...animationProps,
        stagger: 0.1,
        overwrite: true,
      });
    },
  });
}
```

### 3.4 WHEN implementing Flip animations

```typescript
// ❌ WRONG - Manual position calculation
const rect1 = el.getBoundingClientRect();
// ... move element
const rect2 = el.getBoundingClientRect();
gsap.from(el, { x: rect1.left - rect2.left });

// ✅ CORRECT - GSAP Flip plugin
import gsap from 'gsap';
import { Flip } from 'gsap/Flip';

gsap.registerPlugin(Flip);

interface FlipAnimationOptions {
  duration?: number;
  ease?: string;
  stagger?: number;
  onComplete?: () => void;
}

function animateLayoutChange(
  elements: HTMLElement[],
  layoutChangeCallback: () => void,
  options: FlipAnimationOptions = {}
): gsap.core.Timeline {
  const {
    duration = 0.5,
    ease = 'power2.inOut',
    stagger = 0.05,
    onComplete,
  } = options;

  // Capture initial state
  const state = Flip.getState(elements);

  // Perform layout change
  layoutChangeCallback();

  // Animate from old to new positions
  return Flip.from(state, {
    duration,
    ease,
    stagger,
    absolute: true,
    onComplete,
    // Handle elements that were added
    onEnter: (elements) => {
      return gsap.fromTo(
        elements,
        { opacity: 0, scale: 0.8 },
        { opacity: 1, scale: 1, duration: 0.3 }
      );
    },
    // Handle elements that were removed
    onLeave: (elements) => {
      return gsap.to(elements, {
        opacity: 0,
        scale: 0.8,
        duration: 0.3,
      });
    },
  });
}

// React Flip animation hook
function useFlipAnimation<T>(
  items: T[],
  containerRef: React.RefObject<HTMLElement>
) {
  const itemsRef = useRef<T[]>(items);

  useGSAP(
    () => {
      if (!containerRef.current) return;
      if (itemsRef.current === items) return;

      const elements = containerRef.current.querySelectorAll<HTMLElement>('[data-flip-item]');
      if (!elements.length) return;

      // Capture state before React re-render
      const state = Flip.getState(elements);

      // Update ref after layout
      itemsRef.current = items;

      // Animate after React commit
      requestAnimationFrame(() => {
        const newElements = containerRef.current?.querySelectorAll<HTMLElement>('[data-flip-item]');
        if (!newElements) return;

        Flip.from(state, {
          duration: 0.4,
          ease: 'power2.out',
          stagger: 0.02,
          absolute: true,
        });
      });
    },
    { scope: containerRef, dependencies: [items] }
  );
}
```

### 3.5 WHEN implementing reduced motion support

```typescript
// ❌ WRONG - No accessibility consideration
gsap.to('.element', { x: 100, duration: 1 });

// ✅ CORRECT - Full reduced motion support
import gsap from 'gsap';

interface AccessibleAnimationConfig {
  target: gsap.TweenTarget;
  vars: gsap.TweenVars;
  reducedMotionVars?: gsap.TweenVars;
}

class AccessibleAnimations {
  private prefersReducedMotion: boolean;
  private mediaQuery: MediaQueryList;

  constructor() {
    this.mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    this.prefersReducedMotion = this.mediaQuery.matches;

    // Listen for preference changes
    this.mediaQuery.addEventListener('change', (e) => {
      this.prefersReducedMotion = e.matches;
    });
  }

  get reducedMotion(): boolean {
    return this.prefersReducedMotion;
  }

  to(config: AccessibleAnimationConfig): gsap.core.Tween {
    const { target, vars, reducedMotionVars } = config;

    if (this.prefersReducedMotion) {
      // Instant transition or reduced alternative
      const reducedVars = reducedMotionVars ?? {
        ...vars,
        duration: 0,
      };
      return gsap.set(target, reducedVars) as unknown as gsap.core.Tween;
    }

    return gsap.to(target, vars);
  }

  timeline(vars?: gsap.TimelineVars): gsap.core.Timeline {
    if (this.prefersReducedMotion) {
      // Return timeline that immediately completes
      return gsap.timeline({
        ...vars,
        defaults: { duration: 0 },
      });
    }

    return gsap.timeline(vars);
  }

  // Create animation that respects user preference
  createAnimation(
    target: gsap.TweenTarget,
    fullMotion: gsap.TweenVars,
    reducedMotion?: gsap.TweenVars
  ): gsap.core.Tween {
    return this.to({
      target,
      vars: fullMotion,
      reducedMotionVars: reducedMotion,
    });
  }
}

// Singleton instance
export const a11yAnimations = new AccessibleAnimations();

// Usage
function AnimatedComponent() {
  const boxRef = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    a11yAnimations.createAnimation(
      boxRef.current,
      // Full animation
      { x: 100, rotation: 360, duration: 1, ease: 'elastic.out' },
      // Reduced motion alternative
      { x: 100, duration: 0.2, ease: 'power2.out' }
    );
  });

  return <div ref={boxRef}>Animated content</div>;
}
```

### 3.6 WHEN optimizing performance

```typescript
// ❌ WRONG - Layout thrashing, no optimization
elements.forEach((el) => {
  gsap.to(el, {
    width: el.offsetWidth + 100,  // Forces reflow
    left: 100,                     // Layout property
  });
});

// ✅ CORRECT - Performance-optimized animations
import gsap from 'gsap';

// Force GPU acceleration
gsap.config({
  force3D: true,
  nullTargetWarn: false,
});

// Performance utilities
const perfUtils = {
  // Batch DOM reads before writes
  batchAnimate(
    elements: HTMLElement[],
    getProps: (el: HTMLElement, index: number) => gsap.TweenVars
  ): gsap.core.Tween[] {
    // Read phase - gather all measurements
    const configs = elements.map((el, i) => ({
      element: el,
      props: getProps(el, i),
    }));

    // Write phase - apply all animations
    return configs.map(({ element, props }) =>
      gsap.to(element, {
        ...props,
        // Use transform properties only
        x: props.x ?? 0,
        y: props.y ?? 0,
        scale: props.scale ?? 1,
        rotation: props.rotation ?? 0,
      })
    );
  },

  // Use will-change hint
  prepareForAnimation(elements: HTMLElement[]): void {
    elements.forEach((el) => {
      el.style.willChange = 'transform, opacity';
    });
  },

  // Clean up will-change after animation
  cleanupAfterAnimation(elements: HTMLElement[]): void {
    elements.forEach((el) => {
      el.style.willChange = 'auto';
    });
  },

  // Throttled scroll handler
  createScrollHandler(
    callback: () => void,
    throttleMs: number = 16
  ): () => void {
    let ticking = false;

    return () => {
      if (!ticking) {
        requestAnimationFrame(() => {
          callback();
          ticking = false;
        });
        ticking = true;
      }
    };
  },
};

// Usage with proper cleanup
function PerformantAnimations() {
  const itemsRef = useRef<HTMLDivElement[]>([]);

  useGSAP(() => {
    const items = itemsRef.current.filter(Boolean);

    // Prepare for animation
    perfUtils.prepareForAnimation(items);

    // Create staggered animation
    gsap.from(items, {
      opacity: 0,
      y: 30,
      stagger: 0.1,
      duration: 0.6,
      ease: 'power2.out',
      onComplete: () => {
        // Cleanup will-change
        perfUtils.cleanupAfterAnimation(items);
      },
    });
  });

  return (
    <div>
      {[0, 1, 2, 3].map((i) => (
        <div
          key={i}
          ref={(el) => {
            if (el) itemsRef.current[i] = el;
          }}
        >
          Item {i}
        </div>
      ))}
    </div>
  );
}
```

---

## 4. Anti-Patterns

**NEVER:**
- Animate layout properties (left, top, width, height)
- Use user-provided selectors without validation
- Skip animation cleanup on unmount
- Ignore `prefers-reduced-motion`
- Create animations in render functions
- Use `innerHTML` for animated content
- Forget to kill ScrollTriggers
- Animate during scroll without throttling

---

## 5. Testing

**ALWAYS test GSAP animations:**

```typescript
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import gsap from 'gsap';

describe('GSAP Animations', () => {
  beforeEach(() => {
    // Speed up animations for testing
    gsap.globalTimeline.timeScale(100);
  });

  afterEach(() => {
    // Clean up all animations
    gsap.killTweensOf('*');
    gsap.globalTimeline.timeScale(1);
  });

  it('animates element to target position', async () => {
    const element = document.createElement('div');
    document.body.appendChild(element);

    gsap.to(element, { x: 100, duration: 1 });

    // Wait for animation to complete
    await gsap.globalTimeline.then();

    const transform = element.style.transform;
    expect(transform).toContain('translate');
  });

  it('respects reduced motion preference', () => {
    // Mock matchMedia
    vi.spyOn(window, 'matchMedia').mockReturnValue({
      matches: true,
      media: '(prefers-reduced-motion: reduce)',
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    } as unknown as MediaQueryList);

    const animations = new AccessibleAnimations();
    expect(animations.reducedMotion).toBe(true);
  });

  it('cleans up animations on kill', () => {
    const element = document.createElement('div');
    const tween = gsap.to(element, { x: 100, duration: 10 });

    expect(tween.isActive()).toBe(true);

    tween.kill();

    expect(tween.isActive()).toBe(false);
  });

  it('timeline completes in correct order', async () => {
    const calls: string[] = [];

    const tl = gsap.timeline();
    tl.call(() => calls.push('first'))
      .call(() => calls.push('second'), [], '+=0.1')
      .call(() => calls.push('third'), [], '+=0.1');

    await tl.then();

    expect(calls).toEqual(['first', 'second', 'third']);
  });
});
```

---

## 6. Pre-Generation Checklist

**BEFORE generating any GSAP code:**

- [ ] Using transform properties (x, y, scale, rotation)
- [ ] Animation cleanup on component unmount
- [ ] `prefers-reduced-motion` respected
- [ ] Element references validated before animation
- [ ] ScrollTrigger markers disabled in production
- [ ] No user-provided selectors without validation
- [ ] Stagger used for list animations
- [ ] `will-change` cleaned up after animation
- [ ] Timelines use labels for maintainability
- [ ] useGSAP hook used for React integration

---

**Performance**: Quality over speed. Verify all code examples compile. Never skip security checks. See `template-references/performance-notes.md` for full guidelines.