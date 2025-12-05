# CI/CD Performance Patterns

## Pattern 1: Dependency Caching

```yaml
# BAD: No caching - reinstalls every time
- name: Install dependencies
  run: npm install

# GOOD: Cache with hash-based keys
- name: Cache npm dependencies
  uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-npm-

- name: Install dependencies
  run: npm ci
```

## Pattern 2: Parallel Job Execution

```yaml
# BAD: Sequential jobs
jobs:
  lint:
    runs-on: ubuntu-latest
  test:
    needs: lint  # Waits for lint
  security:
    needs: test  # Waits for test

# GOOD: Independent jobs run in parallel
jobs:
  lint:
    runs-on: ubuntu-latest
  test:
    runs-on: ubuntu-latest  # Parallel with lint
  security:
    runs-on: ubuntu-latest  # Parallel with lint and test
  build:
    needs: [lint, test, security]  # Only build waits
```

## Pattern 3: Artifact Optimization

```yaml
# BAD: Upload entire node_modules
- uses: actions/upload-artifact@v4
  with:
    name: build
    path: .  # Includes node_modules!

# GOOD: Upload only build outputs with compression
- uses: actions/upload-artifact@v4
  with:
    name: build
    path: dist/
    retention-days: 7
    compression-level: 9
```

## Pattern 4: Incremental Builds

```yaml
# BAD: Full rebuild every time
- name: Build
  run: npm run build

# GOOD: Cache build outputs
- name: Cache build
  uses: actions/cache@v3
  with:
    path: |
      dist
      .next/cache
      node_modules/.cache
    key: ${{ runner.os }}-build-${{ hashFiles('src/**') }}

- name: Build
  run: npm run build
```

## Pattern 5: Conditional Workflows

```yaml
# BAD: Run everything on every change
on: [push]
jobs:
  test-frontend:
    runs-on: ubuntu-latest
  test-backend:
    runs-on: ubuntu-latest

# GOOD: Path-filtered triggers
on:
  push:
    paths:
      - 'src/frontend/**'
      - 'src/backend/**'

jobs:
  detect-changes:
    outputs:
      frontend: ${{ steps.filter.outputs.frontend }}
      backend: ${{ steps.filter.outputs.backend }}
    steps:
      - uses: dorny/paths-filter@v2
        id: filter
        with:
          filters: |
            frontend:
              - 'src/frontend/**'
            backend:
              - 'src/backend/**'

  test-frontend:
    needs: detect-changes
    if: needs.detect-changes.outputs.frontend == 'true'
    runs-on: ubuntu-latest

  test-backend:
    needs: detect-changes
    if: needs.detect-changes.outputs.backend == 'true'
    runs-on: ubuntu-latest
```

## Pattern 6: Docker Layer Caching

```yaml
# BAD: No layer caching
- uses: docker/build-push-action@v5
  with:
    context: .
    push: true

# GOOD: GitHub Actions cache for layers
- uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

## Pattern 7: Smart Caching Strategy

```yaml
name: Optimized Build with Caching

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Cache npm dependencies
      - name: Cache npm modules
        uses: actions/cache@v3
        with:
          path: ~/.npm
          key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}
          restore-keys: |
            ${{ runner.os }}-npm-

      # Cache build outputs
      - name: Cache build
        uses: actions/cache@v3
        with:
          path: |
            dist
            .next/cache
          key: ${{ runner.os }}-build-${{ hashFiles('src/**') }}
          restore-keys: |
            ${{ runner.os }}-build-

      # Cache Docker layers
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          cache-from: type=gha
          cache-to: type=gha,mode=max
          push: false
```
