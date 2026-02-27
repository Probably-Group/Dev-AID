#!/usr/bin/env python3
"""Measure TOON vs JSON token savings for Dev-AID configs and skills."""

import json
import sys
from pathlib import Path

# Add orchestration to path
script_dir = Path(__file__).parent
orchestration_dir = script_dir.parent / "orchestration"
sys.path.insert(0, str(orchestration_dir))

from toon import encode


def estimate_tokens(text: str) -> int:
    """Rough token estimate: 1 token ≈ 4 characters."""
    return len(text) // 4


def measure_file(filepath: Path) -> dict:
    """Measure savings for a JSON file."""
    if not filepath.exists():
        return {"file": filepath.name, "status": "not found"}

    json_str = filepath.read_text()
    data = json.loads(json_str)
    toon_str = encode(data)

    json_tokens = estimate_tokens(json_str)
    toon_tokens = estimate_tokens(toon_str)
    savings_pct = ((json_tokens - toon_tokens) / json_tokens * 100) if json_tokens > 0 else 0

    return {
        "file": filepath.name,
        "json_bytes": len(json_str),
        "toon_bytes": len(toon_str),
        "json_tokens": json_tokens,
        "toon_tokens": toon_tokens,
        "savings_pct": round(savings_pct, 1),
    }


def main():
    config_dir = script_dir.parent / "config"

    print("=" * 60)
    print("TOON Token Savings Report")
    print("=" * 60)
    print()

    total_json = 0
    total_toon = 0

    for filename in ["models.json", "routing.json", "orchestration.json", "settings.json"]:
        result = measure_file(config_dir / filename)
        if result.get("status") == "not found":
            print(f"  {filename:<25} — not found (skipped)")
            continue

        total_json += result["json_tokens"]
        total_toon += result["toon_tokens"]

        print(f"  {result['file']:<25} JSON: {result['json_tokens']:>5} tokens → TOON: {result['toon_tokens']:>5} tokens ({result['savings_pct']:>5.1f}% saved)")

    print()
    if total_json > 0:
        total_savings = ((total_json - total_toon) / total_json * 100)
        print(f"  {'TOTAL':<25} JSON: {total_json:>5} tokens → TOON: {total_toon:>5} tokens ({total_savings:>5.1f}% saved)")

    # Sample skill output measurement
    print()
    print("-" * 60)
    print("Sample Skill Output Savings (architecture analysis):")
    print("-" * 60)

    sample_output = {
        "components": [
            {"name": "API Gateway", "type": "service", "endpoints": 12, "language": "TypeScript"},
            {"name": "Auth Service", "type": "service", "endpoints": 8, "language": "Python"},
            {"name": "Database", "type": "datastore", "endpoints": 0, "language": "PostgreSQL"},
            {"name": "Cache", "type": "infrastructure", "endpoints": 0, "language": "Redis"},
            {"name": "Queue", "type": "infrastructure", "endpoints": 0, "language": "RabbitMQ"},
        ],
        "dependencies": [
            {"from": "API Gateway", "to": "Auth Service", "type": "sync"},
            {"from": "API Gateway", "to": "Database", "type": "sync"},
            {"from": "API Gateway", "to": "Cache", "type": "sync"},
            {"from": "Auth Service", "to": "Database", "type": "sync"},
            {"from": "Auth Service", "to": "Queue", "type": "async"},
        ]
    }

    json_str = json.dumps(sample_output)
    toon_str = encode(sample_output)
    json_t = estimate_tokens(json_str)
    toon_t = estimate_tokens(toon_str)
    savings = ((json_t - toon_t) / json_t * 100) if json_t > 0 else 0

    print(f"  JSON: {json_t} tokens ({len(json_str)} bytes)")
    print(f"  TOON: {toon_t} tokens ({len(toon_str)} bytes)")
    print(f"  Savings: {savings:.1f}%")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
