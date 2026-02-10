# Dependency Analysis Report

## Metadata

| Field | Value |
|-------|-------|
| **System** | [Name] |
| **Analyzer** | [Name] |
| **Date** | [YYYY-MM-DD] |
| **Modules Analyzed** | [N] |
| **Total Dependencies** | [N] |

---

## 1. Layer Violations

Allowed dependency direction: [API -> Services -> Domain -> Repositories -> (none)]

| Source Module | Target Module | Expected Direction | Actual | Severity |
|--------------|---------------|-------------------|--------|----------|
| [api.routes] | [repositories.user_repo] | api -> services | api -> repositories | High |
| [domain.models] | [services.user_service] | domain -> (none) | domain -> services | Critical |
| [services.order] | [api.schemas] | services -> domain | services -> api | Medium |

**Total Violations:** [N]

---

## 2. Circular Dependencies

| Cycle | Modules Involved | Suggested Break Point |
|-------|-----------------|----------------------|
| Cycle 1 | [module_a -> module_b -> module_c -> module_a] | [Extract interface in module_a, depend on interface] |
| Cycle 2 | [module_x -> module_y -> module_x] | [Use dependency inversion, introduce protocol] |

**Total Cycles:** [N]

---

## 3. Coupling Metrics

### Per-Module Analysis

| Module | Ca (Afferent) | Ce (Efferent) | Instability (I) | Abstractness (A) | D (Distance) |
|--------|---------------|---------------|-----------------|-------------------|--------------|
| [core.domain] | [N] | [N] | [0.0-1.0] | [0.0-1.0] | [0.0-1.0] |
| [api.routes] | [N] | [N] | [0.0-1.0] | [0.0-1.0] | [0.0-1.0] |
| [services] | [N] | [N] | [0.0-1.0] | [0.0-1.0] | [0.0-1.0] |
| [repositories] | [N] | [N] | [0.0-1.0] | [0.0-1.0] | [0.0-1.0] |
| [utils] | [N] | [N] | [0.0-1.0] | [0.0-1.0] | [0.0-1.0] |

### Metric Definitions

- **Ca (Afferent Coupling):** Number of modules that depend on this module. High = many dependents (stable core).
- **Ce (Efferent Coupling):** Number of modules this module depends on. High = many dependencies (fragile).
- **Instability (I):** Ce / (Ca + Ce). Range 0 (stable) to 1 (unstable).
- **Abstractness (A):** Ratio of abstract types to total types. Range 0 (concrete) to 1 (abstract).
- **Distance (D):** |A + I - 1|. Distance from the Main Sequence. Ideal = 0.

---

## 4. Stability Index

### Main Sequence Plot

```
Abstractness (A)
1.0 |  Zone of          .
    |  Uselessness   .    .
    |             .         .
0.5 |          .    IDEAL     .
    |       .     LINE          .
    |    .                        .
0.0 |___.___________________________.
    0.0                          1.0
                Instability (I)
```

### Zone Analysis

| Module | Zone | Action |
|--------|------|--------|
| [module_name] | Main Sequence (ideal) | None needed |
| [module_name] | Zone of Pain (stable + concrete) | Add abstractions / interfaces |
| [module_name] | Zone of Uselessness (unstable + abstract) | Remove unused abstractions |

---

## 5. High-Coupling Hotspots

| Module | Dependents (Ca) | Risk | Recommendation |
|--------|-----------------|------|----------------|
| [utils/helpers.py] | [N modules] | Change here breaks [N] modules | [Split into focused utilities] |
| [models/base.py] | [N modules] | Core dependency | [Ensure high test coverage] |
| [config.py] | [N modules] | Global config coupling | [Use dependency injection] |

---

## 6. Recommendations

1. **Break circular dependencies** -- [Specific module pairs and extraction strategy]
2. **Fix layer violations** -- [Specific imports to redirect through proper layers]
3. **Reduce coupling hotspots** -- [Split large utility modules, use protocols/interfaces]
4. **Improve abstractness** -- [Add protocols for modules in Zone of Pain]

---

## 7. Dependency Graph

[Reference to generated dependency graph visualization, e.g. pydeps output]

```
[Simplified ASCII or Mermaid diagram of key dependency flows]
```
