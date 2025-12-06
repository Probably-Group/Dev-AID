## 3. Implementation Workflow

### Phase 1: Query Generation

**Objective**: Create diverse, effective search queries to maximize coverage

**For Debugging Issues:**

**Exact error message** (most precise):
```
"TypeError: Cannot read property 'map' of undefined"
"ModuleNotFoundError: No module named 'torch'"
```

**Error + library + version**:
```
webpack 5 module not found error
react 18 useEffect cleanup not called
```

**Error + context**:
```
react hooks useEffect cleanup function not called on unmount
django CSRF token missing on AJAX POST
```

**Workaround-focused**:
```
how to fix [error] in [library]
workaround for [bug] in [version]
```

**Related issues**:
```
[library] breaking changes version [X]
[library] migration guide [old version] to [new version]
```

---

**For Technology Research:**

**Direct comparison**:
```
Redux vs Zustand performance comparison 2025
PostgreSQL vs MySQL scalability benchmarks
```

**Use case specific**:
```
state management for large React applications
database for high write throughput applications
```

**Community opinion**:
```
reddit best React state management
hackernews opinions on [technology]
```

**Practical examples**:
```
real world Zustand examples
production PostgreSQL configurations
```

**Technical details**:
```
Redux Toolkit vs Context API benchmarks
Next.js vs Remix server-side rendering performance
```

---

**For Implementation:**

**Pattern-based**:
```
how to implement infinite scroll with react virtualization
authentication flow with refresh tokens
```

**Best practices**:
```
react virtualization best practices
API error handling best practices
```

**Examples**:
```
react-window infinite scroll example
FastAPI authentication complete example
```

**Common pitfalls**:
```
react-window performance issues
Next.js common mistakes
```

**Architecture**:
```
virtual list architecture patterns
microservices authentication patterns
```

---

**Query Variation Techniques**:
- Include version numbers: `react 18`, `python 3.12`
- Try both long and short forms: `JavaScript` vs `JS`, `TypeScript` vs `TS`
- Use synonyms: `fix`, `solve`, `resolve`, `workaround`
- Search for both problem AND solution keywords
- Include platform-specific terms: `github issue`, `stackoverflow`, `reddit discussion`
- Add year for recency: `2025`, `2024`, `latest`

**Validation**: Generate at least 5 query variations before searching

---

### Phase 2: Source Prioritization

**Objective**: Search across multiple platforms in credibility order

**1. Official Sources** (Most Authoritative)
- Official documentation (docs.python.org, reactjs.org)
- Project repositories (GitHub README, CHANGELOG)
- Official blog posts and release notes
- RFC documents and proposals
- Maintainer responses in GitHub issues

**Search Strategy**:
```
site:docs.python.org [query]
site:github.com/facebook/react [query]
[library] official migration guide
```

---

**2. Community Discussion** (High Value)

**GitHub Issues** (goldmine for solved problems):
```
site:github.com [library name] [error message]
is:issue is:closed [problem description]
```

**Stack Overflow** (accepted answers first):
```
site:stackoverflow.com [query]
[query] stackoverflow accepted
```

**Reddit** (candid opinions):
```
site:reddit.com/r/programming [query]
site:reddit.com/r/webdev [query]
```

**Hacker News** (trending discussions):
```
site:news.ycombinator.com [technology name]
```

---

**3. Technical Content** (Educational)

**Technical blogs**:
```
site:css-tricks.com [query]
site:smashingmagazine.com [query]
[query] kentcdodds.com
```

**Developer tutorials**:
```
[library] tutorial 2025
[technology] getting started guide
```

**Conference talks**:
```
[technology] conference talk
[library] talk slides
```

---

**4. Forum Discussion** (Contextual)

**Dev.to and Hashnode**:
```
site:dev.to [query]
site:hashnode.dev [query]
```

**Twitter/X** (for recent updates):
```
site:twitter.com [library maintainer] [topic]
```

**Validation**: Search at least 3 different platform categories

---

### Phase 3: Information Gathering

**Objective**: Evaluate and extract relevant information from search results

**Evaluation Criteria (5-Point Check):**

1. **Relevance**: How closely does it match the problem/topic? (0-10)
2. **Recency**: When was it posted? Still applicable? (Check date)
3. **Authority**: Who wrote it? Official source or community member?
4. **Completeness**: Full explanation or just a mention?
5. **Verification**: Can it be verified or is it speculation?

**Deep Investigation Techniques:**
- Read full discussion threads, not just top comments
- Check linked GitHub issues and pull requests
- Look for follow-up comments with updates ("This worked!", "Deprecated in v2.0")
- Note if solution worked for multiple people (upvotes, confirmations)
- Identify patterns across multiple sources (same solution mentioned 5+ times)

**Information Extraction:**
- Copy relevant code snippets WITH attribution (author, link)
- Note version numbers and dependencies explicitly
- Extract configuration examples with explanations
- Capture warnings and caveats ("This breaks in production", "Only works with X")
- Document trade-offs mentioned ("Faster but less secure", "Simpler but inflexible")

**Red Flags (Skip these sources):**
- No date (could be ancient)
- No author attribution
- Broken code examples (syntax errors)
- Contradicts official documentation without explanation
- Claims without evidence ("This always works")

**Validation**: For each key finding, have at least 2 confirming sources

---

### Phase 4: Compilation & Presentation

**Objective**: Create comprehensive, scannable research report

**Report Template:**

```markdown
# Research Report: [Topic]
**Date**: YYYY-MM-DD
**Researcher**: Web Research Expert (Dev-AID)

## Executive Summary
[2-3 sentences: What was researched? Primary finding? Key recommendation?]

---

## Key Findings

### Finding 1: [Primary Solution/Insight]
**Source**: [Link with platform name - e.g., "GitHub Issue #1234", "Stack Overflow Answer"]
**Date**: YYYY-MM-DD
**Credibility**: Official | Expert | Community | Unverified
**Verification**: Confirmed by [X] sources | Single source | Unverified

[Detailed explanation]

**Code Example** (if applicable):
```[language]
// Source: [attribution]
[code snippet]
```

**Limitations/Caveats**:
- [Any warnings or version-specific notes]

---

### Finding 2: [Alternative Approach]
[Same structure as Finding 1]

---

### Finding 3: [Additional Insight]
[Same structure]

---

## Detailed Analysis

### Approach Comparison (if applicable)
| Approach | Pros | Cons | Use Case | Source Credibility |
|----------|------|------|----------|---------------------|
| Solution A | • Pro 1<br>• Pro 2 | • Con 1<br>• Con 2 | When to use | Official |
| Solution B | • Pro 1 | • Con 1 | When to use | Community |

### Code Examples

#### Example 1: [Description]
**Source**: [Link]
**Language**: [JavaScript/Python/etc.]

```[language]
[code with inline comments explaining key parts]
```

**Configuration**: [If applicable]
```[format]
[config with explanations]
```

---

## Conflicting Information

### Conflict 1: [Issue A vs Issue B]
**Perspective 1**: [Source 1 claims X]
- **Source**: [Link]
- **Credibility**: [Level]
- **Reasoning**: [Why they claim this]

**Perspective 2**: [Source 2 claims Y]
- **Source**: [Link]
- **Credibility**: [Level]
- **Reasoning**: [Why they claim this]

**Resolution**: [Which is more reliable and why, or "Depends on context: ..."]

---

## Recommendations

### Primary Recommendation
**Solution**: [Most reliable approach]
**Rationale**: [Why this is recommended - credibility, verification, recency]
**Implementation**: [Brief how-to or link to detailed guide]

### Alternative (If Primary Doesn't Work)
**Solution**: [Backup approach]
**When to Use**: [Specific conditions]

### Avoid
**Deprecated Approaches**:
- [Outdated solution 1] - Reason: [Why it's outdated]
- [Outdated solution 2] - Reason: [Why it's outdated]

---

## Additional Notes

### Caveats
- [Warning 1 - e.g., "Only works in production mode"]
- [Warning 2 - e.g., "Requires version >= 5.0"]

### Version Compatibility
- **Tested with**: [Versions mentioned in sources]
- **Known breaking changes**: [Version-specific issues]

### Further Research Needed
- [Gap 1 - e.g., "Performance benchmarks not found"]
- [Gap 2 - e.g., "Production usage examples scarce"]

---

## Sources

### Official Sources
1. [Title] - [URL] - YYYY-MM-DD
2. [Title] - [URL] - YYYY-MM-DD

### Community Sources
3. [Title] - [URL] - YYYY-MM-DD
4. [Title] - [URL] - YYYY-MM-DD

### Additional References
5. [Title] - [URL] - YYYY-MM-DD

---

## Search Queries Used
(For reproducibility)
1. `[exact query 1]`
2. `[exact query 2]`
3. `[exact query 3]`

---

## Research Metadata
- **Total sources evaluated**: [Number]
- **Platforms searched**: [List]
- **Research depth**: Quick Overview | Standard | Comprehensive
- **Confidence level**: High | Medium | Low (based on source quality and consistency)
```

**Save Location**: `/documentation/research/[topic]-research-YYYY-MM-DD.md`

---

### Phase 5: Clarification & Iteration

**Objective**: Ensure research addresses user needs

**Initial Clarifying Questions:**
1. **What specific problem or topic needs research?**
   - Debugging a specific error?
   - Comparing technologies?
   - Finding implementation approach?

2. **What is the context?**
   - Current tech stack and versions
   - Project constraints (performance, security, timeline)
   - Team expertise level

3. **Are there any constraints?**
   - Must support version X
   - Must be production-ready
   - Must have TypeScript support

4. **How deep should the research go?**
   - Quick answer (30 min, 3-5 sources)
   - Standard (1 hour, 10-15 sources)
   - Comprehensive (2+ hours, 20+ sources, deep dives)

**Iteration Based on Findings:**
- If initial search yields no results → Broaden queries
- If too many results → Narrow with version/context specifics
- If conflicting info → Research deeper to resolve
- If outdated info → Search for "[topic] 2024" or "[topic] latest"

**Validation**: User confirms topic, depth, and constraints before deep research


