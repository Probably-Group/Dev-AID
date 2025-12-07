## 3. Implementation Workflow (TDD)

Follow this workflow for all DevSecOps implementations:

### Step 1: Write Failing Security Test First

Create tests that verify security gates catch known vulnerabilities:

```yaml
# tests/security/test-pipeline-gates.yml
name: Test Security Gates
on: [push]
jobs:
  test-sast-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Create vulnerable test file
        run: echo 'eval(user_input)' > vuln.py
      - name: Run SAST - should fail
        id: sast
        continue-on-error: true
        run: semgrep --config p/security-audit vuln.py --error
      - name: Verify SAST caught vulnerability
        run: |
          [ "${{ steps.sast.outcome }}" == "success" ] && exit 1
          echo "SAST working correctly"
```

### Step 2: Implement Minimum Security Gates

Build pipeline with essential security gates:

```yaml
# .github/workflows/security-gates.yml
name: Security Gates
on:
  pull_request:
    branches: [main]
permissions:
  contents: read
  security-events: write
jobs:
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: trufflesecurity/trufflehog@v3.63.0
        with:
          path: ./
          extra_args: --fail --json
  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: semgrep/semgrep-action@v1
        with:
          config: p/security-audit
  sca:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/dependency-review-action@v4
        with:
          fail-on-severity: high
```

### Step 3: Add Container and IaC Scanning

Expand with additional security layers (container, IaC, compliance). See `references/security-examples.md` for full implementations.

### Step 4: Verify Security Gates

```bash
# Test all security gates
semgrep --test tests/security/rules/
trivy image --severity HIGH,CRITICAL --exit-code 1 app:test
conftest test terraform/ --policy policies/
pytest tests/security/ -v
```

---


