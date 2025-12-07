## 3. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```yaml
# .github/workflows/test-pipeline.yml
name: Test Pipeline Configuration
on: [push]
jobs:
  validate-workflow:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate workflow syntax
        run: |
          bash <(curl https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash)
          ./actionlint -color
      - name: Verify security scans required
        run: |
          grep -A 10 "deploy:" .github/workflows/ci-cd.yml | grep -q "needs:.*security" || exit 1
      - name: Verify minimal permissions
        run: grep -q "^permissions:" .github/workflows/ci-cd.yml || exit 1
```

### Step 2: Implement Minimum to Pass

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline
permissions:
  contents: read
  security-events: write
on:
  push:
    branches: [main]
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "Security scan"
  deploy:
    needs: [security]
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying..."
```

### Step 3: Refactor and Verify

```bash
actionlint                          # Validate syntax
act -n                              # Dry run locally
gh workflow run test-pipeline.yml   # Run tests
```

---


