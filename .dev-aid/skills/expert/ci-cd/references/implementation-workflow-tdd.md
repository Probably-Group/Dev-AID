## 7. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

Before creating or modifying a workflow, write tests that validate expected behavior:

```yaml
# .github/workflows/test-workflows.yml
name: Validate Workflows
on: [push, pull_request]

jobs:
  test-workflow-syntax:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install actionlint
        run: |
          bash <(curl https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash)
      - name: Lint workflows
        run: ./actionlint -color

  test-security-compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check permissions are explicit
        run: |
          for f in .github/workflows/*.yml; do
            if ! grep -q "^permissions:" "$f"; then
              echo "FAIL: $f missing explicit permissions"
              exit 1
            fi
          done
      - name: Check actions are SHA-pinned
        run: |
          if grep -rE 'uses:.*@v[0-9]' .github/workflows/; then
            echo "FAIL: Found unpinned actions"
            exit 1
          fi
```

📚 **See `references/testing-guide.md`** for comprehensive testing strategies.

### Step 2: Implement Minimum to Pass

Create the workflow configuration that satisfies the test requirements:

```yaml
# .github/workflows/build.yml
name: Build
on: [push]
permissions:
  contents: read
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@8ade135a41bc03ea155e62e844d188df1ea18608 # v4.1.0
      - run: npm ci && npm run build
```

### Step 3: Refactor and Optimize

Add caching, parallelization, and security enhancements:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@8ade135a41bc03ea155e62e844d188df1ea18608
      - uses: actions/setup-node@8f152de45cc393bb48ce5d89d36b731f54556e65
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci && npm run build
```

📚 **See `references/performance-optimization.md`** for caching strategies and optimization patterns.

### Step 4: Run Full Verification

```bash
# Local validation
actionlint .github/workflows/
yamllint .github/workflows/

# Security checks
grep -rE 'uses:.*@v[0-9]' .github/workflows/ && echo "FAIL: Unpinned actions" || echo "PASS"
grep -r 'echo.*secrets\.' .github/workflows/ && echo "FAIL: Secret exposure" || echo "PASS"

# Push and verify CI passes
git push && gh run watch
```

---

