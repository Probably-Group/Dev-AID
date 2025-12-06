## 9. Common Mistakes

### ❌ Use Raw Values
```css
/* Bad */ .button { background: #3b82f6; padding: 12px; }
/* Good */ .button { background: var(--color-interactive-primary); padding: var(--spacing-component-md); }
```

### ❌ Inconsistent APIs
```typescript
/* Bad */ <Button size="large" /> <Input sizing="lg" />
/* Good */ <Button size="lg" /> <Input size="lg" />
```

### ❌ Skip Semantic Layer
```css
/* Bad */ .card { background: var(--color-gray-50); }
/* Good */ .card { background: var(--color-bg-secondary); }
```

---

