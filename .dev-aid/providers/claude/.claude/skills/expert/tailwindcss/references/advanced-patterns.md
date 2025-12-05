# Tailwind CSS Advanced Patterns

## 1. Implementation Patterns

### 1.1 HUD Panel Component

```vue
<template>
  <div class="
    relative
    bg-jarvis-bg-panel/80
    border border-jarvis-primary/30
    rounded-lg
    p-4
    backdrop-blur-sm
    shadow-lg shadow-jarvis-primary/10
  ">
    <!-- Scanline overlay -->
    <div class="
      absolute inset-0
      bg-gradient-to-b from-transparent via-jarvis-primary/5 to-transparent
      animate-scan
      pointer-events-none
    " />

    <!-- Content -->
    <div class="relative z-10">
      <h3 class="
        font-display
        text-jarvis-primary
        text-lg
        uppercase
        tracking-wider
        mb-2
      ">
        {{ title }}
      </h3>
      <slot />
    </div>
  </div>
</template>
```

**Use Case**: Primary container for JARVIS HUD sections with holographic effects.

**Key Features**:
- Semi-transparent background with backdrop blur
- Animated scanline overlay for HUD aesthetic
- Border glow using primary color
- Z-index layering for content over effects

### 1.2 Status Indicator

```vue
<template>
  <div class="flex items-center gap-2">
    <span :class="[
      'w-2 h-2 rounded-full',
      {
        'bg-jarvis-primary animate-pulse': status === 'active',
        'bg-jarvis-warning': status === 'warning',
        'bg-jarvis-danger animate-ping': status === 'error',
        'bg-gray-500': status === 'inactive'
      }
    ]" />
    <span class="text-sm text-gray-300">{{ label }}</span>
  </div>
</template>
```

**Use Case**: Visual status indicators with color-coded states.

**Key Features**:
- Dynamic color binding based on status
- Animation for active/error states
- Accessible with text labels
- Small footprint for inline use

### 1.3 Button Variants

```vue
<template>
  <button :class="[
    'px-4 py-2 rounded font-medium transition-all duration-200',
    'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-jarvis-bg-dark',
    {
      'bg-jarvis-primary text-black hover:bg-jarvis-primary/90 focus:ring-jarvis-primary':
        variant === 'primary',
      'bg-transparent border border-jarvis-secondary text-jarvis-secondary hover:bg-jarvis-secondary/10 focus:ring-jarvis-secondary':
        variant === 'secondary',
      'bg-jarvis-danger text-white hover:bg-jarvis-danger/90 focus:ring-jarvis-danger':
        variant === 'danger'
    }
  ]">
    <slot />
  </button>
</template>
```

**Use Case**: Consistent button styling with multiple variants.

**Key Features**:
- Primary, secondary, and danger variants
- Hover state transitions
- Accessible focus rings
- Consistent spacing and typography

## 2. Complex Layouts

### 2.1 HUD Dashboard Grid

```vue
<template>
  <div class="
    grid
    grid-cols-12
    gap-4
    h-screen
    p-4
    bg-jarvis-bg-dark
  ">
    <!-- Top status bar -->
    <div class="col-span-12 h-12 flex items-center justify-between">
      <StatusIndicators />
      <SystemTime />
    </div>

    <!-- Left sidebar -->
    <div class="col-span-2 space-y-4">
      <NavigationPanel />
      <QuickActions />
    </div>

    <!-- Main content -->
    <div class="col-span-7 flex flex-col gap-4">
      <MainDisplay class="flex-1" />
      <BottomControls />
    </div>

    <!-- Right sidebar -->
    <div class="col-span-3 space-y-4">
      <MetricsPanel />
      <AlertsPanel />
    </div>
  </div>
</template>
```

**Use Case**: Full-screen dashboard layout with multiple panels.

**Key Features**:
- 12-column grid system for precise layout control
- Full viewport height
- Status bar spanning full width
- Responsive sidebar widths

## 3. Custom Animations

### 3.1 Glitch Effect

```javascript
// tailwind.config.js
animation: {
  'glitch': 'glitch 1s infinite linear alternate-reverse',
  'glitch-1': 'glitch-1 0.8s infinite linear alternate-reverse',
  'glitch-2': 'glitch-2 0.9s infinite linear alternate-reverse'
},
keyframes: {
  glitch: {
    '0%, 100%': { transform: 'translate(0)' },
    '20%': { transform: 'translate(-2px, 2px)' },
    '40%': { transform: 'translate(-2px, -2px)' },
    '60%': { transform: 'translate(2px, 2px)' },
    '80%': { transform: 'translate(2px, -2px)' }
  },
  'glitch-1': {
    '0%, 100%': { clipPath: 'inset(0 0 0 0)' },
    '50%': { clipPath: 'inset(5% 0 80% 0)' }
  }
}
```

**Use Case**: Holographic glitch effects for HUD elements.

**Usage**:
```vue
<div class="animate-glitch">Glitching Text</div>
```

## 4. Responsive HUD

### 4.1 Mobile-First Layout

```vue
<template>
  <div class="
    flex
    flex-col md:flex-row
    gap-4
    p-2 md:p-4
  ">
    <!-- Collapses on mobile -->
    <aside class="
      w-full md:w-64
      flex md:flex-col
      gap-2
      overflow-x-auto md:overflow-visible
    ">
      <MiniPanel v-for="panel in panels" :key="panel.id" />
    </aside>

    <!-- Main content expands -->
    <main class="flex-1 min-h-[300px] md:min-h-[500px]">
      <slot />
    </main>
  </div>
</template>
```

**Use Case**: Responsive HUD that adapts to mobile and desktop.

**Key Features**:
- Vertical layout on mobile, horizontal on desktop
- Scrollable sidebar on mobile
- Flexible main content area
- Minimum heights for proper rendering

## 5. Custom Plugins

### 5.1 Holographic Glow Plugin

```javascript
// plugins/holographic.js
const plugin = require('tailwindcss/plugin')

module.exports = plugin(function({ addUtilities, theme }) {
  const glows = {}

  Object.entries(theme('colors.jarvis')).forEach(([name, color]) => {
    if (typeof color === 'string') {
      glows[`.glow-${name}`] = {
        boxShadow: `0 0 10px ${color}, 0 0 20px ${color}40, 0 0 30px ${color}20`
      }
      glows[`.text-glow-${name}`] = {
        textShadow: `0 0 10px ${color}`
      }
    }
  })

  addUtilities(glows)
})
```

**Use Case**: Generate glow utilities from theme colors.

**Usage**:
```vue
<div class="glow-primary">Glowing box</div>
<h1 class="text-glow-primary">Glowing text</h1>
```

**Configuration**:
```javascript
// tailwind.config.js
plugins: [
  require('./plugins/holographic')
]
```
