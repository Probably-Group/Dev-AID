# Context Detector - Performance-Optimized Skill Selection

## Overview

The context detector is a high-performance Python implementation that analyzes your project to automatically detect relevant technologies and select appropriate Dev-AID skills.

**Performance:** <200ms (vs. 2000ms+ with old bash implementation)

## Architecture

### Components

1. **`context-detector.py`** - Main Python implementation (320 lines)
   - Single-pass file scanning
   - Efficient data structures (sets, dicts)
   - Reads patterns from skills-index.json dynamically

2. **`detect-context.sh`** - Bash wrapper (28 lines)
   - Maintains backward compatibility
   - Simple delegation to Python backend

3. **`select-skills.sh`** - Bash wrapper (31 lines)
   - Maintains backward compatibility
   - Simple delegation to Python backend

### Performance Improvements

| Metric | Old (Bash) | New (Python) | Improvement |
|--------|-----------|--------------|-------------|
| **Execution Time** | 2000ms+ | <200ms | **10x faster** |
| **File Scanning** | Multiple passes | Single pass | **O(n²) → O(n)** |
| **Pattern Loading** | Hardcoded | Dynamic from JSON | Maintainable |
| **Code Size** | 367 lines | 320+59 lines | 84% reduction in bash |

## Usage

### Mode 1: Detect Context Only

Analyzes project and returns detected keywords:

```bash
./.dev-aid/orchestration/context-detector.py detect .

# Output: Python Bash Docker FastAPI
```

### Mode 2: Select Skills Only

Takes context keywords and returns top skills:

```bash
./.dev-aid/orchestration/context-detector.py select "python fastapi docker" 5

# Output:
# fastapi-expert
# python
# docker-expert
# devsecops-expert
# api-expert
```

### Mode 3: Auto (Detect + Select)

Combines both operations for convenience:

```bash
./.dev-aid/orchestration/context-detector.py auto . 5

# Detects context AND selects skills in one pass
```

### Backward Compatibility

The bash wrappers maintain the original interface:

```bash
# Still works exactly as before
./.dev-aid/orchestration/detect-context.sh .
./.dev-aid/orchestration/select-skills.sh "python fastapi" 3
```

## How It Works

### Context Detection

1. **Config File Analysis**
   - Extracts dependencies from `package.json`, `requirements.txt`, `Cargo.toml`, `go.mod`, `Gemfile`
   - Maps package names to import names (e.g., `python-dotenv` → `dotenv`)

2. **File Extension Detection**
   - Scans files for technology indicators: `.py`, `.ts`, `.rs`, `.go`, `.vue`, etc.
   - Limited to 1000 files to prevent slowdown on large repos

3. **Special File Detection**
   - Checks for `Dockerfile`, `docker-compose.yml`, `.github/workflows/`, etc.

### Skill Selection

1. **Scoring Algorithm**
   - Primary keywords: 10 points
   - Technologies: 8 points
   - Secondary keywords: 5 points
   - Confidence weights: variable boost (0-100 points)

2. **Conflict Resolution**
   - Respects `exclude_with` rules in skills-index.json
   - Example: `api-expert` excludes `graphql-expert` (mutually exclusive)

3. **Dependency Management**
   - Automatically includes required skills
   - Example: `fastapi-expert` requires `devsecops-expert`

## Configuration

### Skills Registry

All patterns are defined in `.dev-aid/skills/registry/skills-index.json`:

```json
{
  "fastapi-expert": {
    "activation": {
      "primary_keywords": ["FastAPI", "fastapi"],
      "secondary_keywords": ["API", "REST", "async"],
      "file_patterns": ["**/routes/*", "**/api/*", "main.py"],
      "technologies": ["FastAPI", "Pydantic", "Uvicorn"],
      "confidence_weights": {
        "FastAPI": 0.35,
        "fastapi": 0.3
      },
      "requires": ["devsecops-expert"],
      "exclude_with": []
    }
  }
}
```

### Adding New Skills

1. Add skill metadata to `skills-index.json`
2. No code changes needed - automatically detected!

## Optimization Details

### Why Python?

**Bash Limitations:**
- O(n²) loops with nested find/grep operations
- Spawns new process for each jq/grep call
- No efficient data structures (only arrays)

**Python Advantages:**
- O(1) lookups with sets and dictionaries
- Pre-compiled patterns cached in memory
- Single-pass file iteration
- Native JSON parsing (no jq subprocess)

### Code Comparison

**Old Bash (detect-context.sh):**
```bash
# Scans entire directory for EACH pattern
for pattern_entry in "${patterns[@]}"; do
    find "$dir" -name "$pattern" -type f  # O(n) per pattern
done
```

**New Python (context-detector.py):**
```python
# Scans directory ONCE
for file_path in project_path.rglob('*'):  # O(n) total
    ext = file_path.suffix
    if ext in self.file_extensions:  # O(1) lookup
        context.add(self.file_extensions[ext])
```

### Memory Usage

- **Old Bash:** Spawns ~50 subprocesses (find, grep, jq)
- **New Python:** Single process, ~10MB memory

## Troubleshooting

### Context detection is slow

- Check if you're in a very large repository (>10,000 files)
- The detector limits scanning to 1000 files by default
- Large node_modules or vendor directories are automatically skipped

### Skills not auto-loading

- Run manually: `./.dev-aid/orchestration/context-detector.py auto .`
- Check if skills-index.json exists and is valid JSON
- Verify file patterns in skills-index.json match your project structure

### Wrong skills selected

- Skills are scored by relevance - top 5 are selected
- Adjust `primary_keywords` or `confidence_weights` in skills-index.json
- Run with higher max: `context-detector.py auto . 10`

## Development

### Running Tests

```bash
cd .dev-aid/orchestration

# Test context detection
./context-detector.py detect .

# Test skill selection
./context-detector.py select "python fastapi docker" 3

# Test auto mode
time ./context-detector.py auto . 5  # Should be <200ms
```

### Benchmarking

```bash
# Old bash version (for comparison)
time ./detect-context.sh.old .  # 2000ms+

# New Python version
time ./context-detector.py detect .  # <200ms

# 10x improvement confirmed!
```

## Migration Notes

### From v1.1.0 to v1.2.0

**No action required!** The bash wrappers maintain backward compatibility.

If you were calling bash scripts directly:
- `detect-context.sh` - Works exactly as before
- `select-skills.sh` - Works exactly as before

If you want to use Python directly (for better performance):
- Replace `./detect-context.sh .` with `./context-detector.py detect .`
- Replace `./select-skills.sh "keywords" 5` with `./context-detector.py select "keywords" 5`

## See Also

- [Skills Registry](../.dev-aid/skills/registry/skills-index.json)
- [CHANGELOG](../.dev-aid/CHANGELOG.md) - Version 1.2.0 details
- [Refactoring Expert Skill](../.dev-aid/skills/expert/refactoring-expert/SKILL.md)
