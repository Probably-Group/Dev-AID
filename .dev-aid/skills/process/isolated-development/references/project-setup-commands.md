# Project Setup Commands

Per-language setup commands for isolated development worktrees.

## Detection Priority

Check files in this order to determine project type and setup commands:

| Priority | File | Type | Setup Command |
|----------|------|------|---------------|
| 1 | `pnpm-lock.yaml` | Node.js (pnpm) | `pnpm install` |
| 2 | `yarn.lock` | Node.js (yarn) | `yarn install` |
| 3 | `bun.lockb` | Node.js (bun) | `bun install` |
| 4 | `package-lock.json` | Node.js (npm) | `npm install` |
| 5 | `package.json` | Node.js (npm) | `npm install` |
| 6 | `Cargo.toml` | Rust | `cargo build` |
| 7 | `go.mod` | Go | `go mod download` |
| 8 | `poetry.lock` | Python (poetry) | `poetry install` |
| 9 | `uv.lock` | Python (uv) | `uv sync` |
| 10 | `Pipfile.lock` | Python (pipenv) | `pipenv install` |
| 11 | `pyproject.toml` | Python (pip/poetry) | See below |
| 12 | `requirements.txt` | Python (pip) | `pip install -r requirements.txt` |
| 13 | `pom.xml` | Java (Maven) | `mvn install` |
| 14 | `build.gradle` | Java (Gradle) | `./gradlew build` |
| 15 | `Gemfile` | Ruby | `bundle install` |
| 16 | `composer.json` | PHP | `composer install` |

## Node.js

### npm
```bash
npm install
npm run build  # if build script exists
```

### yarn
```bash
yarn install
yarn build  # if build script exists
```

### pnpm
```bash
pnpm install
pnpm build  # if build script exists
```

### bun
```bash
bun install
bun run build  # if build script exists
```

### Post-Install Verification
```bash
# Verify installation
npm test  # or yarn/pnpm/bun test

# If TypeScript
npx tsc --noEmit
```

---

## Python

### pip (with requirements.txt)
```bash
# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# If dev requirements exist
pip install -r requirements-dev.txt
```

### poetry
```bash
poetry install
poetry shell  # Optional: activate environment
```

### uv
```bash
uv sync
```

### pipenv
```bash
pipenv install --dev
pipenv shell  # Optional: activate environment
```

### pyproject.toml (modern pip)
```bash
pip install -e ".[dev]"
```

### Post-Install Verification
```bash
# Verify installation
pytest -v
mypy .
```

---

## Rust

### cargo
```bash
cargo build
cargo test  # Verify
```

### With specific features
```bash
cargo build --features "feature1,feature2"
```

### Post-Install Verification
```bash
cargo test
cargo clippy
```

---

## Go

### go modules
```bash
go mod download
go build ./...
```

### Post-Install Verification
```bash
go test ./...
go vet ./...
```

---

## Java

### Maven
```bash
mvn install -DskipTests
mvn test  # Verify
```

### Gradle
```bash
./gradlew build -x test
./gradlew test  # Verify
```

---

## Ruby

### Bundler
```bash
bundle install
bundle exec rake  # or `rspec` for tests
```

---

## PHP

### Composer
```bash
composer install
./vendor/bin/phpunit  # Verify
```

---

## Multi-Language Projects

For monorepos or multi-language projects:

```bash
# Run setup for each detected type
# Example: Node.js frontend + Python backend

cd frontend && npm install && cd ..
cd backend && pip install -r requirements.txt && cd ..
```

---

## Environment Variables

### Copy environment template
```bash
# If .env.example exists
cp .env.example .env

# Edit with required values
# NEVER commit .env to git
```

### Required environment variables
Check `README.md` or `.env.example` for required variables.

---

## Database Setup

### If migrations exist
```bash
# Python (Django)
python manage.py migrate

# Python (Alembic)
alembic upgrade head

# Node.js (Prisma)
npx prisma migrate dev

# Node.js (TypeORM)
npm run typeorm migration:run
```

### Seed data
```bash
# If seed script exists
npm run seed
# or
python manage.py loaddata fixtures.json
```

---

## Docker-Based Setup

### If docker-compose.yml exists
```bash
# Start services
docker-compose up -d

# Build if needed
docker-compose build

# Verify
docker-compose ps
```

---

## Baseline Verification

After setup, always run:

```bash
# Tests
[language-specific-test-command]

# Lint (optional but recommended)
[language-specific-lint-command]

# Type check (if applicable)
[language-specific-type-check]
```

If any verification fails:
1. **STOP** work
2. **Report** the failure
3. **Ask** for guidance before proceeding

A failing baseline means the issue may be environment-related, not code-related.
