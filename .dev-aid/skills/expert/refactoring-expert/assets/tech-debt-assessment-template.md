# Technical Debt Assessment

## Metadata

| Field | Value |
|-------|-------|
| **Project/Module** | [Name] |
| **Assessor** | [Name] |
| **Date** | [YYYY-MM-DD] |
| **Scope** | [Full codebase / specific module] |

---

## 1. Code Quality

| # | Description | Severity (1-5) | Effort (S/M/L/XL) | Impact (Low/Med/High) | Location |
|---|-------------|---------------|-------------------|----------------------|----------|
| CQ-01 | [God class with N methods and N LOC] | [4] | [L] | [High] | [path/file.py] |
| CQ-02 | [Duplicated logic across N files] | [3] | [M] | [Medium] | [path/dir/] |
| CQ-03 | [Deep nesting (5+ levels) in critical path] | [3] | [S] | [Medium] | [path/file.py:func] |
| CQ-04 | [Inconsistent naming conventions] | [2] | [M] | [Low] | [project-wide] |

---

## 2. Architecture

| # | Description | Severity (1-5) | Effort (S/M/L/XL) | Impact (Low/Med/High) | Location |
|---|-------------|---------------|-------------------|----------------------|----------|
| AR-01 | [Circular dependency between modules] | [5] | [L] | [High] | [module_a <-> module_b] |
| AR-02 | [Layer violation: API directly calls repository] | [4] | [M] | [High] | [path/routes.py] |
| AR-03 | [Missing service layer, business logic in controllers] | [4] | [XL] | [High] | [api/ directory] |
| AR-04 | [Monolithic module should be split] | [3] | [L] | [Medium] | [path/utils.py] |

---

## 3. Testing

| # | Description | Severity (1-5) | Effort (S/M/L/XL) | Impact (Low/Med/High) | Location |
|---|-------------|---------------|-------------------|----------------------|----------|
| TS-01 | [No tests for [critical module]] | [5] | [L] | [High] | [path/module/] |
| TS-02 | [Test coverage below N% threshold] | [4] | [M] | [High] | [project-wide] |
| TS-03 | [Flaky test: [test name]] | [3] | [S] | [Medium] | [tests/test_file.py] |
| TS-04 | [No integration tests for [feature]] | [3] | [M] | [Medium] | [tests/] |

---

## 4. Documentation

| # | Description | Severity (1-5) | Effort (S/M/L/XL) | Impact (Low/Med/High) | Location |
|---|-------------|---------------|-------------------|----------------------|----------|
| DC-01 | [No API documentation for [endpoints]] | [3] | [M] | [Medium] | [api/] |
| DC-02 | [Outdated README with wrong setup instructions] | [3] | [S] | [Medium] | [README.md] |
| DC-03 | [Missing docstrings on public functions] | [2] | [M] | [Low] | [project-wide] |

---

## 5. Dependencies

| # | Description | Severity (1-5) | Effort (S/M/L/XL) | Impact (Low/Med/High) | Location |
|---|-------------|---------------|-------------------|----------------------|----------|
| DP-01 | [Dependency [name] has known CVE: [CVE-ID]] | [5] | [S] | [High] | [requirements.txt] |
| DP-02 | [Major version behind: [pkg] v[old] -> v[new]] | [3] | [M] | [Medium] | [package.json] |
| DP-03 | [Unused dependency: [name]] | [1] | [S] | [Low] | [requirements.txt] |
| DP-04 | [No lock file, non-reproducible builds] | [4] | [S] | [High] | [project root] |

---

## 6. Security

| # | Description | Severity (1-5) | Effort (S/M/L/XL) | Impact (Low/Med/High) | Location |
|---|-------------|---------------|-------------------|----------------------|----------|
| SC-01 | [Hardcoded secret/credential] | [5] | [S] | [High] | [path/config.py] |
| SC-02 | [Missing input validation on [endpoint]] | [4] | [M] | [High] | [path/routes.py] |
| SC-03 | [SQL string concatenation instead of parameterized] | [5] | [M] | [High] | [path/queries.py] |

---

## Priority Matrix

| Priority | Items | Criteria |
|----------|-------|----------|
| **P0 -- Immediate** | [SC-01, DP-01, SC-03] | Severity 5 + High Impact |
| **P1 -- This Sprint** | [AR-01, TS-01, SC-02] | Severity 4-5 + High Impact |
| **P2 -- Next Sprint** | [CQ-01, AR-02, AR-03, TS-02] | Severity 3-4 + Medium-High Impact |
| **P3 -- Backlog** | [CQ-02, CQ-03, DC-01, DP-02] | Severity 2-3 + Medium Impact |
| **P4 -- Opportunistic** | [CQ-04, DC-02, DC-03, DP-03] | Severity 1-2 + Low Impact |

---

## Recommended Sequence

1. **Security fixes first** (P0) -- [SC-01, DP-01, SC-03] -- blocks everything else
2. **Test foundation** (P1) -- [TS-01] -- needed before safe refactoring
3. **Architecture cleanup** (P2) -- [AR-01, AR-02] -- enables further improvements
4. **Code quality** (P3) -- [CQ-01, CQ-02] -- reduces ongoing maintenance cost
5. **Documentation** (P4) -- [DC-01, DC-02] -- improves onboarding

---

## Summary

| Category | Total Items | P0 | P1 | P2 | P3 | P4 |
|----------|------------|----|----|----|----|-----|
| Code Quality | [N] | [N] | [N] | [N] | [N] | [N] |
| Architecture | [N] | [N] | [N] | [N] | [N] | [N] |
| Testing | [N] | [N] | [N] | [N] | [N] | [N] |
| Documentation | [N] | [N] | [N] | [N] | [N] | [N] |
| Dependencies | [N] | [N] | [N] | [N] | [N] | [N] |
| Security | [N] | [N] | [N] | [N] | [N] | [N] |
| **Total** | **[N]** | **[N]** | **[N]** | **[N]** | **[N]** | **[N]** |
