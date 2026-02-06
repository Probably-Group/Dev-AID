# Dev-AID Validator Framework

Automated compliance checking for skill-specific coding standards. Each skill can include a `validate.py` that enforces its rules.

## Quick Start

```bash
# Run all validators on current project
python3 .dev-aid/scripts/run-validators.py --target-dir .

# Run only validators matching project technologies
python3 .dev-aid/scripts/run-validators.py --filter-context --target-dir .

# Run a specific validator
python3 .dev-aid/skills/expert/bash-expert/validate.py --target-dir .
python3 .dev-aid/skills/expert/python/validate.py --target-dir .

# JSON output (for CI/scripts)
python3 .dev-aid/scripts/run-validators.py --json --strict --target-dir .
```

## Available Validators

| Skill | Path | Checks |
|-------|------|--------|
| bash-expert | `.dev-aid/skills/expert/bash-expert/validate.py` | Shebang, strict mode, IFS, trap, syntax, eval/backticks, test brackets, variable braces, local vars, readonly, chmod, mktemp, curl pipe, unquoted subshell |
| python | `.dev-aid/skills/expert/python/validate.py` | shell=True, eval/exec, pickle, hardcoded secrets, generic exceptions, print in libs, type annotations, coverage |

## CLI Options

All validators share a common CLI interface:

```
validate.py [--strict] [--json] [--target-dir <dir>] [files...]
```

| Flag | Description |
|------|-------------|
| `--strict` | Treat WARN as FAIL |
| `--json` | Machine-readable JSON output |
| `--target-dir` | Directory to scan (default: `.`) |
| `files...` | Specific files to validate (overrides `--target-dir`) |

The runner (`run-validators.py`) adds:

| Flag | Description |
|------|-------------|
| `--filter-context` | Only run validators matching detected project technologies |
| `--validators name1,name2` | Run only named validators |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks pass |
| 1 | At least one FAIL found |
| 2 | Runner error (no validators found, etc.) |

## Output Formats

### Text (default)

Human-readable, color-coded. Shows per-file violations grouped by validator.

### JSON

```json
{
  "target_dir": "/path/to/project",
  "validators_run": 2,
  "results": [
    {
      "name": "Bash Expert Compliance",
      "files_scanned": 15,
      "violations": [...],
      "totals": {"fail": 0, "warn": 3},
      "status": "PASS"
    }
  ],
  "totals": {"pass": 2, "fail": 0, "error": 0}
}
```

## Creating a Validator for a New Skill

1. Create `validate.py` in your skill directory (e.g., `.dev-aid/skills/expert/my-skill/validate.py`)

2. Import the shared library:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "lib"))
from validator_common import (
    Violation,
    ValidatorResult,
    create_argument_parser,
    run_validator_main,
    find_files,
)
```

3. Implement your checks as functions returning `List[Violation]`:

```python
def check_something(lines, filepath):
    violations = []
    # ... your check logic ...
    if problem_found:
        violations.append(
            Violation(filepath, line_number, "check-name", "description", "FAIL")
        )
    return violations
```

4. Wire it up with the standard main:

```python
def main():
    parser = create_argument_parser("my-validator", "My Skill Validator")
    args = parser.parse_args()

    target_dir = Path(args.target_dir).resolve()
    files = args.files or find_files(str(target_dir), [".ext"])

    violations = []
    for f in files:
        violations.extend(check_something(...))

    result = ValidatorResult(
        name="My Skill Compliance",
        skill_path=str(Path(__file__).resolve().parent),
        files_scanned=len(files),
        violations=violations,
    )
    return run_validator_main(result, args)
```

The runner will auto-discover your `validate.py` — no registration needed.

## Severity Levels

- **FAIL**: Must-fix issues (security risks, broken patterns)
- **WARN**: Should-fix issues (style, best practices)

With `--strict`, all WARN become FAIL.

## Architecture

```
.dev-aid/
├── lib/
│   └── validator_common.py      # Shared types, parsing, output formatting
├── scripts/
│   └── run-validators.py        # Auto-discovery runner
└── skills/
    ├── core/*/validate.py       # Core skill validators (always run)
    ├── expert/*/validate.py     # Expert skill validators
    └── process/*/validate.py    # Process skill validators
```
