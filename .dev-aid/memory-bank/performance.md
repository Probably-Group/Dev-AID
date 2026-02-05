# Performance Baselines & Optimizations

**Purpose**: Performance knowledge and optimization history (team-shared)
**Note**: For personal AI notes, use Claude's built-in memory (`~/.claude/projects/*/memory/`)

---

## Performance Baselines

### API Endpoints (P95 Latency)
**Target**: <100ms P95

| Endpoint | P50 | P95 | P99 | Status |
|----------|-----|-----|-----|--------|
| GET /api/example | --ms | --ms | --ms | -- |

---

## Optimization History

### OPT-001: [Optimization Title]
**Date**: YYYY-MM-DD
**Problem**: Description of the performance issue
**Impact**: Before → After metrics

**Before**:
```typescript
// Slow code
```

**After**:
```typescript
// Optimized code
```

**Results**:
- Metric 1: X → Y
- Metric 2: A → B

---

## Performance Targets

### Core Web Vitals
| Metric | Target | Current |
|--------|--------|---------|
| LCP | <2.5s | -- |
| FID | <100ms | -- |
| CLS | <0.1 | -- |

### Backend
| Metric | Target | Current |
|--------|--------|---------|
| API P95 | <100ms | -- |
| Memory (avg) | <1GB | -- |
| CPU (avg) | <70% | -- |

---

## Performance Best Practices

### Database
- Use indexes on frequently queried columns
- Avoid N+1 queries (use joins/includes)
- Paginate large result sets
- Use connection pooling

### Caching
- Redis for frequently accessed data
- CDN for static assets
- HTTP caching headers
- Cache invalidation strategy

### Frontend
- Code splitting
- Lazy loading
- Image optimization
- Minimize bundle size

---

**Usage**: Reference when optimizing performance.
Update baselines after major changes.
Document all optimizations with before/after metrics.
