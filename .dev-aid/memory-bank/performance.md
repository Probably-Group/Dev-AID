# Performance Baselines & Optimizations

**Purpose**: Performance knowledge and optimization history
**Load Strategy**: On-demand (when working on performance)
**Update Frequency**: After optimizations or performance reviews

---

## 📊 Performance Baselines

### API Endpoints (P95 Latency)
**Target**: <100ms P95

| Endpoint | P50 | P95 | P99 | Status |
|----------|-----|-----|-----|--------|
| GET /api/users | 15ms | 45ms | 120ms | ⚠️ P99 high |
| POST /api/auth/login | 25ms | 80ms | 150ms | ✅ Good |
| GET /api/products | 20ms | 60ms | 100ms | ✅ Good |
| POST /api/orders | 40ms | 90ms | 180ms | ⚠️ Needs work |

**Last Updated**: 2025-11-25

---

## ⚡ Optimization History

### OPT-001: Database Query Optimization
**Date**: 2025-11-15
**Problem**: N+1 query in user list endpoint
**Impact**: P95 latency 450ms → 45ms (90% improvement)

**Before**:
```typescript
// N+1 query problem
const users = await db.users.findMany();
for (const user of users) {
  user.posts = await db.posts.findMany({ userId: user.id });
}
```

**After**:
```typescript
// Single query with join
const users = await db.users.findMany({
  include: { posts: true }
});
```

**Results**:
- Queries: 101 → 1
- Latency: 450ms → 45ms
- DB load: -90%

---

### OPT-002: Frontend Bundle Size
**Date**: 2025-11-10
**Problem**: Initial bundle 2.5 MB
**Impact**: FCP 3.2s → 1.1s

**Changes**:
- Code splitting by route
- Lazy loading components
- Tree shaking unused code
- Minification & compression

**Results**:
- Bundle: 2.5MB → 450KB (-82%)
- FCP: 3.2s → 1.1s
- LCP: 4.5s → 1.8s

---

### OPT-003: Redis Caching
**Date**: 2025-11-05
**Problem**: Repeated expensive calculations
**Impact**: API latency -60%

**Implementation**:
```typescript
// Cache expensive operation
const cacheKey = `product_stats_${productId}`;
let stats = await redis.get(cacheKey);

if (!stats) {
  stats = await calculateProductStats(productId);
  await redis.setex(cacheKey, 3600, JSON.stringify(stats));
}
```

**Results**:
- Cache hit rate: 85%
- Latency: 250ms → 100ms
- DB load: -70%

---

## 🎯 Performance Targets

### Core Web Vitals
| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| LCP | 1.8s | <2.5s | ✅ Good |
| FID | 45ms | <100ms | ✅ Good |
| CLS | 0.05 | <0.1 | ✅ Good |

### Backend
| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| API P95 | 80ms | <100ms | ✅ Good |
| DB Connections | 25 | <50 | ✅ Good |
| Memory (avg) | 450MB | <1GB | ✅ Good |
| CPU (avg) | 35% | <70% | ✅ Good |

---

## 🔍 Known Bottlenecks

### BOTTLENECK-001: User List Query
**Status**: In Progress
**Location**: `src/api/users.controller.ts:45`
**Issue**: Full table scan without index
**Impact**: P99 = 180ms
**Solution**: Add composite index on (created_at, status)
**ETA**: 2025-11-30

### BOTTLENECK-002: Image Processing
**Status**: Identified
**Location**: `src/utils/image.service.ts`
**Issue**: Synchronous processing blocks event loop
**Impact**: 500ms blocking time
**Solution**: Move to worker thread or queue
**ETA**: 2025-12-15

---

## 💡 Performance Best Practices

### Database
- ✅ Use indexes on frequently queried columns
- ✅ Avoid N+1 queries (use joins/includes)
- ✅ Paginate large result sets
- ✅ Use connection pooling
- ⚠️ Monitor slow query log

### Caching
- ✅ Redis for frequently accessed data
- ✅ CDN for static assets
- ✅ HTTP caching headers
- ⚠️ Cache invalidation strategy

### Frontend
- ✅ Code splitting
- ✅ Lazy loading
- ✅ Image optimization
- ✅ Minimize bundle size
- ⚠️ Prefetch critical resources

---

## 📈 Monitoring

**Tools**:
- APM: Datadog/New Relic
- RUM: Google Analytics
- Profiling: Chrome DevTools, Node.js profiler

**Alerts**:
- P95 > 100ms → Slack alert
- Error rate > 1% → PagerDuty
- CPU > 80% → Auto-scale trigger

---

**Usage**: Reference when optimizing performance.
Update baselines after major changes.
Document all optimizations with before/after metrics.
