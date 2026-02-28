#!/usr/bin/env python3
"""
Convert all JSON config files in .dev-aid/config/ to TOON format.

Usage:
    /path/to/orchestration/venv/bin/python convert_configs_to_toon.py

Keeps original .json files as fallback. Creates .toon equivalents.
Verifies roundtrip: JSON -> encode -> TOON -> decode -> verify matches.
"""

import json
import os
import sys

# Add orchestration dir to path so we can import the toon module
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ORCHESTRATION_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "orchestration")
CONFIG_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "config")

sys.path.insert(0, ORCHESTRATION_DIR)

from toon import encode, decode


def deep_equal(a, b, path=""):
    """Deep comparison that provides detailed mismatch info."""
    if type(a) != type(b):
        return False, f"Type mismatch at {path}: {type(a).__name__} vs {type(b).__name__}"

    if isinstance(a, dict):
        if set(a.keys()) != set(b.keys()):
            missing_in_b = set(a.keys()) - set(b.keys())
            missing_in_a = set(b.keys()) - set(a.keys())
            msg = f"Key mismatch at {path}:"
            if missing_in_b:
                msg += f" missing in decoded: {missing_in_b}"
            if missing_in_a:
                msg += f" extra in decoded: {missing_in_a}"
            return False, msg
        for key in a:
            eq, msg = deep_equal(a[key], b[key], f"{path}.{key}")
            if not eq:
                return False, msg
        return True, ""

    if isinstance(a, list):
        if len(a) != len(b):
            return False, f"List length mismatch at {path}: {len(a)} vs {len(b)}"
        for i, (x, y) in enumerate(zip(a, b)):
            eq, msg = deep_equal(x, y, f"{path}[{i}]")
            if not eq:
                return False, msg
        return True, ""

    if isinstance(a, float):
        if abs(a - b) > 1e-9:
            return False, f"Float mismatch at {path}: {a} vs {b}"
        return True, ""

    if a != b:
        return False, f"Value mismatch at {path}: {repr(a)} vs {repr(b)}"

    return True, ""


def convert_file(json_path):
    """Convert a single JSON config file to TOON format."""
    basename = os.path.basename(json_path)
    name_no_ext = os.path.splitext(basename)[0]
    toon_path = os.path.join(CONFIG_DIR, f"{name_no_ext}.toon")

    print(f"\n{'='*60}")
    print(f"Converting: {basename} -> {name_no_ext}.toon")
    print(f"{'='*60}")

    # 1. Load JSON
    with open(json_path, "r", encoding="utf-8") as f:
        original_data = json.load(f)

    json_size = os.path.getsize(json_path)

    # 2. Encode to TOON
    toon_str = encode(original_data)

    # 3. Write TOON file
    with open(toon_path, "w", encoding="utf-8") as f:
        f.write(toon_str)

    toon_size = os.path.getsize(toon_path)

    # 4. Verify roundtrip: decode TOON back and compare
    with open(toon_path, "r", encoding="utf-8") as f:
        toon_content = f.read()

    decoded_data = decode(toon_content)

    eq, msg = deep_equal(original_data, decoded_data)

    if eq:
        savings = ((json_size - toon_size) / json_size * 100) if json_size > 0 else 0
        print(f"  PASS - Roundtrip verified")
        print(f"  JSON: {json_size:,} bytes -> TOON: {toon_size:,} bytes ({savings:.1f}% smaller)")
    else:
        print(f"  FAIL - Roundtrip mismatch: {msg}")
        # Remove the bad TOON file
        os.remove(toon_path)
        return False

    return True


def main():
    print("Dev-AID Config Migration: JSON -> TOON")
    print("=" * 60)
    print(f"Config directory: {CONFIG_DIR}")
    print(f"Orchestration dir: {ORCHESTRATION_DIR}")

    # Find all .json files in config dir
    json_files = sorted([
        f for f in os.listdir(CONFIG_DIR)
        if f.endswith(".json") and not f.startswith(".")
    ])

    print(f"\nFound {len(json_files)} JSON config files:")
    for f in json_files:
        print(f"  - {f}")

    # Convert each file
    results = {}
    for json_file in json_files:
        json_path = os.path.join(CONFIG_DIR, json_file)
        try:
            success = convert_file(json_path)
            results[json_file] = "PASS" if success else "FAIL"
        except Exception as e:
            print(f"  ERROR: {e}")
            results[json_file] = f"ERROR: {e}"

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    passed = sum(1 for v in results.values() if v == "PASS")
    failed = sum(1 for v in results.values() if v != "PASS")

    for name, status in results.items():
        icon = "PASS" if status == "PASS" else "FAIL"
        print(f"  [{icon}] {name}")

    print(f"\n{passed}/{len(results)} files converted successfully")
    if failed:
        print(f"{failed} files failed")
        sys.exit(1)

    print("\nOriginal .json files preserved as fallback.")
    print("config_loader.py will prefer .toon files when available.")


if __name__ == "__main__":
    main()
