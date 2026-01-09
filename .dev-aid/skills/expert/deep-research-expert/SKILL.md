---
name: deep-research-expert
description: "Deep research specialist using Gemini Deep Research, Tavily, and Perplexity Sonar for comprehensive external knowledge gathering"
risk_level: low
version: "1.0.0"
credit: |
  Created by: Dev-AID Team
  License: MIT
---

# Deep Research Expert

## 0. Anti-Hallucination Protocol

### 0.1 Quick Risk Assessment

**Risk Level**: LOW

**Key Risk Factors**:
- External API dependencies (network required)
- Information currency (results may be cached up to 48h)
- Source verification required for critical decisions

**Immediate Actions**:
1. Always verify critical information from multiple sources
2. Note cache status in responses (cached results may be older)
3. Cite all sources explicitly with URLs
4. Cross-reference with official documentation when possible

### 0.2 Vulnerability Research Protocol

Before providing research results, verify:
- [ ] Sources are reputable and current
- [ ] Multiple sources confirm key facts
- [ ] Dates are noted for time-sensitive information
- [ ] Conflicting information is highlighted

### 0.3 Hallucination Prevention Checklist

**CRITICAL**: These rules are ABSOLUTE.

**Domain-Specific Rules**:
- NEVER present cached results as real-time without noting cache age
- NEVER fabricate citations or source URLs
- ALWAYS include source URLs for verifiable claims
- ALWAYS note the provider and depth level used
- NEVER claim certainty about rapidly changing information (versions, prices)

---

## 1. Overview

**Expertise**: Multi-provider deep research using Gemini Deep Research, Tavily, and Perplexity Sonar

**Risk Level**: Low (research only, no code execution)

**Key Capabilities**:
- Automatic routing between quick search and deep research based on query complexity
- 24-48 hour aggressive caching to reduce costs
- Multi-source citation aggregation
- Technology comparison and evaluation
- Current documentation and version lookup

**When to Use This Skill**:
- Research latest library versions and best practices
- Compare technologies (Redis vs Memcached, React vs Vue)
- Find comprehensive implementation guides
- Investigate breaking changes and migrations
- Gather multi-source perspectives on architecture decisions

---

## 2. Provider Selection Guide

| Query Type | Best Provider | Depth | Typical Time | Cost |
|------------|--------------|-------|--------------|------|
| Quick facts (syntax, versions) | Tavily | quick | 2-5s | 1 credit |
| How-to guides | Tavily/Perplexity | standard | 5-10s | 2 credits |
| Comparisons | Perplexity Sonar | standard | 10-20s | Token-based |
| Deep research | Gemini | deep | 2-5 min | API credits |
| Architecture analysis | Gemini | deep | 2-5 min | API credits |

### Auto-Routing Logic

The system automatically selects providers based on query complexity:

**SIMPLE queries** (what is, define, syntax, error):
- Routes to Tavily basic search
- ~3 seconds, 1 credit

**MODERATE queries** (how-to, implementation):
- Routes to Tavily advanced or Perplexity standard
- ~5-10 seconds

**COMPLEX queries** (compare, architecture, best practices):
- Routes to Gemini Deep Research
- Fallback: Perplexity sonar-deep-research
- 2-5 minutes

---

## 3. Usage

### Manual Invocation

Use the `/dev-aid-research` command or CLI:

```bash
# Auto-routed research
dev-aid-research search "What are the best practices for React 19 Server Components?"

# Quick factual lookup
dev-aid-research quick "Latest stable Node.js version"

# Deep comprehensive research
dev-aid-research deep "Compare Prisma vs Drizzle ORM for TypeScript in 2025"
```

### CLI Options

- `--depth quick|standard|deep|auto` - Research depth (default: auto)
- `--provider tavily|perplexity-sonar|gemini-deep-research` - Force provider
- `--no-cache` - Skip cache, force fresh results
- `--sources N` - Maximum sources (default: 10)
- `--json` - Output as JSON

### Examples

```bash
# Quick version lookup
dev-aid-research quick "What version is Python 3.13?"

# Technology comparison (auto-routes to deep)
dev-aid-research search "Compare FastAPI vs Django for REST APIs in 2025"

# Force specific provider
dev-aid-research search --provider perplexity-sonar "GraphQL best practices"

# Force fresh results (no cache)
dev-aid-research search --no-cache "Current Next.js App Router recommendations"
```

---

## 4. Integration with Dev-AID

### Auto-Trigger Conditions

Research is automatically triggered when:
1. Local code search returns empty results AND query contains research keywords
2. Query explicitly mentions "research" or "external"
3. Query contains time-sensitive keywords (latest, 2025, current version)

### Research Keywords (Auto-Trigger)

- "latest", "current version", "best practice"
- "compare", "comparison", "alternatives"
- "documentation", "tutorial", "how to"
- "2024", "2025", "2026" (year references)
- "new feature", "recently", "updated"

### Related Skills

- `web-research-expert` - Complements with structured research methodology
- `plan-review-expert` - Uses research findings for plan validation
- `api-expert` - Research API integration approaches

---

## 5. Configuration

### Environment Variables

```bash
# Required for respective providers
TAVILY_API_KEY=...       # Tavily (free: 1000 credits/mo)
PERPLEXITY_API_KEY=...   # Perplexity Sonar
GOOGLE_API_KEY=...       # Gemini Deep Research
```

### Cache Settings

- Default TTL: 24 hours
- Maximum TTL: 48 hours
- Cache location: `~/.dev-aid/cache/research/`

To clear cache:
```bash
dev-aid-research clear-cache --all
```

---

## 6. Best Practices

### For Accurate Research

1. **Be specific** - "React 19 Server Components best practices" beats "React best practices"
2. **Include context** - "Python 3.12 async patterns for FastAPI" gives better results
3. **Note versions** - Include specific versions when researching libraries

### For Cost Efficiency

1. **Use cache** - Default 24h cache reduces API calls significantly
2. **Start quick** - Use `--depth quick` for simple lookups
3. **Batch research** - Group related queries to maximize cache hits

### For Verification

1. **Check citations** - Always review source URLs
2. **Note cache status** - Cached results may be hours old
3. **Cross-reference** - For critical decisions, verify with official docs

---

## 7. Troubleshooting

### No providers available
- Check API keys are set in environment
- Run `dev-aid-research providers` to see status

### Slow deep research
- Gemini Deep Research takes 2-5 minutes by design
- Use `--depth standard` for faster results

### Stale results
- Use `--no-cache` to force fresh results
- Clear cache with `dev-aid-research clear-cache`

---

**Remember**: Always cite sources. Note cache status. Verify critical information with official documentation.
