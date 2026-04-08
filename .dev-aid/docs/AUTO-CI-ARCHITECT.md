# Auto-CI Architect Specification

## Overview
The **Auto-CI Architect** is a specialized skill in Dev-AID designed to autonomously generate, validate, and maintain CI/CD workflows for any project. It analyzes the project structure, detects languages/frameworks, and produces best-practice pipelines (GitHub Actions, GitLab CI) with built-in security gating.

## Goals
1.  **Zero-Config CI**: Detect project type (e.g., Node.js + Postgres) and generate a working pipeline instantly.
2.  **Security-First**: All generated pipelines include `opengrep`, `trivy`, and `gitleaks` by default.
3.  **Drift Detection**: Monitor existing workflows for deprecated actions or insecure patterns.

## Detection Logic
The architect scans for:
*   `package.json` -> Node.js workflows (npm test, npm audit).
*   `pyproject.toml` -> Python workflows (pytest, ruff, mypy).
*   `Cargo.toml` -> Rust workflows (cargo test, clippy).
*   `Dockerfile` -> Container + misconfig scanning (Trivy).
*   `terraform/` -> IaC misconfig scanning (Trivy).

## Generated Components
1.  **PR Check (`pr-check.yml`)**:
    *   Fast feedback loop (Linting, Unit Tests).
    *   Commit message validation.
2.  **Security Gate (`security.yml`)**:
    *   SAST (Opengrep).
    *   Secret Scanning (Gitleaks).
    *   Dependency Audit.
3.  **Release Pipeline (`release.yml`)**:
    *   Semantic versioning.
    *   Changelog generation.
    *   Artifact publishing (Docker Hub, PyPI, NPM).

## CLI Usage
```bash
# Auto-detect and generate
/dev-aid ci generate

# specific platform
/dev-aid ci generate --platform gitlab

# Audit existing
/dev-aid ci audit
```

## Integration with Senior Architect Skill
The Auto-CI Architect leverages the `senior-architect` skill rules:
*   **Fail Closed**: Pipelines fail on security findings.
*   **Pinned Dependencies**: All Actions use SHA pinning.
*   **Immutable Artifacts**: Builds once, tests many.
