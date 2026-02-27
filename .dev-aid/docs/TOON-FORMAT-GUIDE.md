# TOON Format Guide

TOON (Token-Optimized Object Notation) reduces token consumption by 40-60% compared to JSON, saving costs across all AI interactions.

## What is TOON?

TOON is a compact serialization format that uses YAML-like syntax for objects and CSV-like syntax for arrays of objects:

**JSON (verbose):**
```json
{
  "users": [
    {"name": "Alice", "role": "admin", "active": true},
    {"name": "Bob", "role": "user", "active": false}
  ]
}
```

**TOON (compact):**
```
users:
  name,role,active
  Alice,admin,true
  Bob,user,false
```

## How Dev-AID Uses TOON

### Configuration Files
The config loader automatically tries `.toon` files before `.json`:
- `models.toon` / `models.json` — AI model definitions
- `routing.toon` / `routing.json` — Routing rules and modes
- `orchestration.toon` / `orchestration.json` — Orchestration settings

### Migration
Run the migration script to convert existing configs:
```bash
.dev-aid/scripts/migrate-to-toon.sh
```

Original JSON files are preserved as backups. To revert, delete the `.toon` files.

### Measuring Savings
```bash
python3 .dev-aid/scripts/measure-toon-savings.py
```

### For Skill Developers
When creating skills that output structured data, prefer TOON format:

```
## Output Format

Use TOON format for structured output to minimize token usage:

components:
  name,type,language
  API Gateway,service,TypeScript
  Auth Service,service,Python
```

## Technical Details

- **Package**: `toon-format==0.9.0b1` (pure Python, no Node.js)
- **Location**: `.dev-aid/orchestration/toon/`
- **API**: `encode(data)`, `decode(toon_str)`, `json_to_toon()`, `toon_to_json()`
- **Round-trip safe**: `decode(encode(data)) == data` for all supported types

## Typical Savings

| Content Type | JSON Tokens | TOON Tokens | Savings |
|-------------|------------|------------|---------|
| Model config | ~150 | ~80 | 47% |
| Routing config | ~60 | ~35 | 42% |
| Architecture output | ~200 | ~90 | 55% |
| Tabular data (10 rows) | ~300 | ~120 | 60% |
