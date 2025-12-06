## 9. Quick Reference

### Essential Checklist

**Before Implementation**:
- [ ] Component requirements documented
- [ ] Write failing tests first
- [ ] Design tokens identified

**During Implementation**:
- [ ] Tests passing incrementally
- [ ] Color system applied consistently
- [ ] Typography scale used correctly
- [ ] Spacing follows 8px grid
- [ ] Loading states include skeletons

**Before Committing**:
- [ ] All tests pass
- [ ] Accessibility audit passes (WCAG AA)
- [ ] Focus states visible
- [ ] Touch targets ≥44px
- [ ] Reduced motion supported
- [ ] Mobile/tablet/desktop tested
- [ ] Lighthouse score > 90

### Common Commands

```bash
# Run tests
npm run test
npm run test:watch
npm run test:coverage

# Accessibility
npm run test:a11y

# Visual regression
npm run test:visual

# Performance
npm run test:perf

# Build
npm run build
```

### Browser Support Verification

Always check modern CSS features on:
- [Can I Use](https://caniuse.com) - Browser compatibility
- [MDN Web Docs](https://developer.mozilla.org) - CSS/JS reference
- [WCAG 2.1](https://www.w3.org/WAI/WCAG21/quickref/) - Accessibility guidelines

---

