# Architecture Review

## Review Metadata

| Field | Value |
|-------|-------|
| **System/Module** | [Name and version] |
| **Reviewer** | [Name] |
| **Review Date** | [YYYY-MM-DD] |
| **Codebase Size** | [N files, N LOC] |

---

## 1. System Overview

[Brief description of the system purpose, main components, and boundaries. Include a high-level diagram reference if available.]

### Component Map
- **[Component A]** -- [Responsibility]
- **[Component B]** -- [Responsibility]
- **[Component C]** -- [Responsibility]

---

## 2. Complexity Analysis

### Cyclomatic Complexity (Top Offenders)

| File | Function | Cyclomatic | Cognitive | LOC | Parameters |
|------|----------|-----------|-----------|-----|------------|
| [path/file.py] | [function_name] | [N] | [N] | [N] | [N] |
| [path/file.py] | [function_name] | [N] | [N] | [N] | [N] |
| [path/file.py] | [function_name] | [N] | [N] | [N] | [N] |

**Thresholds:** Cyclomatic > 10, Cognitive > 15, LOC > 50, Parameters > 5

### Cognitive Complexity Hotspots
- [File/function with deeply nested logic]
- [File/function with complex conditional chains]

---

## 3. Dependency Analysis

### Layer Structure
[Describe the intended layers: API -> Services -> Domain -> Repositories]

### Layer Violations

| Source | Target | Violation |
|--------|--------|-----------|
| [module.path] | [module.path] | [api importing from repositories directly] |

### Circular Dependencies
- [module_a -> module_b -> module_a]
- [None found]

---

## 4. Anti-Patterns Found

| # | Anti-Pattern | Location | Severity | Description |
|---|-------------|----------|----------|-------------|
| 1 | [God Class] | [path/file.py] | [High] | [Class with N methods and N LOC] |
| 2 | [Shotgun Surgery] | [multiple files] | [Medium] | [Change requires touching N files] |
| 3 | [Feature Envy] | [path/file.py:func] | [Low] | [Function uses N methods from other class] |

---

## 5. Performance Concerns

| # | Issue | Location | Impact | Recommendation |
|---|-------|----------|--------|----------------|
| 1 | [O(n^2) algorithm in hot path] | [path/file.py:line] | [High] | [Use hash map for O(n) lookup] |
| 2 | [N+1 query pattern] | [path/file.py:line] | [Medium] | [Add eager loading / batch query] |
| 3 | [Unbounded memory allocation] | [path/file.py:line] | [Medium] | [Add pagination / streaming] |

---

## 6. Security Concerns

| # | Issue | Location | Severity | CWE |
|---|-------|----------|----------|-----|
| 1 | [Description] | [path/file.py] | [Critical/High/Medium] | [CWE-NNN] |
| 2 | [Description] | [path/file.py] | [Critical/High/Medium] | [CWE-NNN] |

---

## 7. Recommendations

| # | Recommendation | Priority | Effort | Impact |
|---|---------------|----------|--------|--------|
| 1 | [Specific recommendation] | [P0/P1/P2] | [S/M/L/XL] | [High/Medium/Low] |
| 2 | [Specific recommendation] | [P0/P1/P2] | [S/M/L/XL] | [High/Medium/Low] |
| 3 | [Specific recommendation] | [P0/P1/P2] | [S/M/L/XL] | [High/Medium/Low] |

---

## 8. Decision Log

| Decision | Rationale | Alternatives Considered | Date |
|----------|-----------|------------------------|------|
| [Architectural decision] | [Why this approach was chosen] | [Other options evaluated] | [Date] |
| [Architectural decision] | [Why this approach was chosen] | [Other options evaluated] | [Date] |
