#!/usr/bin/env python3
"""Measure token usage across Dev-AID SKILL.md files.

Reports per-skill and per-agent-combination totals, counts aggressive
language instances, and supports baseline comparison.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Agent definitions: agent_name -> list of skill names
AGENT_SKILLS: Dict[str, List[str]] = {
    "pr-reviewer": ["appsec-expert", "senior-architect", "devsecops-expert"],
    "test-generator": ["python", "typescript-expert"],
    "tech-debt-hunter": ["senior-architect", "refactoring-expert"],
    "ci-fixer": ["cicd-expert", "bash-expert"],
    "conflict-resolver": [],
    "research-agent": ["deep-research-expert", "web-research-expert"],
    "onboarding-agent": [],
    "doc-auditor": [],
    "dod-gate": ["devsecops-expert"],
}

AGGRESSIVE_PATTERNS = [
    (r"\bNEVER\b", "NEVER"),
    (r"\bALWAYS\b", "ALWAYS"),
    (r"\bCRITICAL\b", "CRITICAL"),
    (r"\bMUST\b", "MUST"),
    (r"\bWARNING\b", "WARNING"),
]

SKILLS_ROOT = Path(__file__).resolve().parent.parent / "skills"


def estimate_tokens(text: str) -> int:
    """Rough token estimate: chars // 4."""
    return len(text) // 4


def count_aggressive(text: str) -> Dict[str, int]:
    """Count aggressive language instances."""
    counts: Dict[str, int] = {}
    for pattern, label in AGGRESSIVE_PATTERNS:
        matches = re.findall(pattern, text)
        if matches:
            counts[label] = len(matches)
    return counts


def analyze_skill(path: Path) -> Dict[str, Any]:
    """Analyze a single SKILL.md file."""
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()
    chars = len(content)
    tokens = estimate_tokens(content)
    aggressive = count_aggressive(content)
    aggressive_total = sum(aggressive.values())

    # Extract skill name from directory
    skill_name = path.parent.name
    category = path.parent.parent.name

    return {
        "name": skill_name,
        "category": category,
        "path": str(path),
        "lines": len(lines),
        "chars": chars,
        "tokens": tokens,
        "aggressive_language": aggressive,
        "aggressive_total": aggressive_total,
    }


def find_all_skills(root: Path) -> List[Path]:
    """Find all SKILL.md files."""
    skills: List[Path] = []
    for category_dir in sorted(root.iterdir()):
        if not category_dir.is_dir():
            continue
        for skill_dir in sorted(category_dir.iterdir()):
            skill_file = skill_dir / "SKILL.md"
            if skill_file.is_file():
                skills.append(skill_file)
    return skills


def print_report(
    skills_data: List[Dict[str, Any]],
    agent_name: Optional[str] = None,
) -> None:
    """Print formatted report."""
    # Sort by tokens descending
    sorted_skills = sorted(skills_data, key=lambda s: s["tokens"], reverse=True)

    total_lines = sum(s["lines"] for s in sorted_skills)
    total_chars = sum(s["chars"] for s in sorted_skills)
    total_tokens = sum(s["tokens"] for s in sorted_skills)
    total_aggressive = sum(s["aggressive_total"] for s in sorted_skills)

    # Aggregate aggressive counts
    agg_counts: Dict[str, int] = {}
    for s in sorted_skills:
        for label, count in s["aggressive_language"].items():
            agg_counts[label] = agg_counts.get(label, 0) + count

    header = "SKILL TOKEN ANALYSIS"
    if agent_name:
        header += f" — Agent: {agent_name}"
    print(f"\n{'=' * 70}")
    print(f" {header}")
    print(f"{'=' * 70}\n")

    # Per-skill table
    print(f"{'Skill':<35} {'Cat':<8} {'Lines':>6} {'Tokens':>7} {'Aggressive':>10}")
    print(f"{'-' * 35} {'-' * 8} {'-' * 6} {'-' * 7} {'-' * 10}")
    for s in sorted_skills:
        print(
            f"{s['name']:<35} {s['category']:<8} {s['lines']:>6} "
            f"{s['tokens']:>7} {s['aggressive_total']:>10}"
        )

    print(f"\n{'TOTALS':<35} {'':8} {total_lines:>6} {total_tokens:>7} {total_aggressive:>10}")

    # Aggressive language breakdown
    print(f"\nAggressive Language Breakdown:")
    for label in ["NEVER", "ALWAYS", "MUST", "CRITICAL", "WARNING"]:
        count = agg_counts.get(label, 0)
        print(f"  {label:<12} {count:>5}")
    print(f"  {'TOTAL':<12} {total_aggressive:>5}")

    # Category summary
    print(f"\nBy Category:")
    cat_totals: Dict[str, Dict[str, int]] = {}
    for s in sorted_skills:
        cat = s["category"]
        if cat not in cat_totals:
            cat_totals[cat] = {"count": 0, "tokens": 0, "lines": 0}
        cat_totals[cat]["count"] += 1
        cat_totals[cat]["tokens"] += s["tokens"]
        cat_totals[cat]["lines"] += s["lines"]

    for cat, totals in sorted(cat_totals.items()):
        avg = totals["tokens"] // totals["count"] if totals["count"] else 0
        print(
            f"  {cat:<12} {totals['count']:>3} skills, "
            f"{totals['tokens']:>7} tokens, "
            f"{totals['lines']:>6} lines (avg {avg} tokens/skill)"
        )

    # Agent combination analysis
    if not agent_name:
        print(f"\nAgent System Prompt Estimates:")
        skill_map = {s["name"]: s for s in sorted_skills}
        for agent, skill_names in sorted(AGENT_SKILLS.items()):
            if not skill_names:
                continue
            agent_tokens = sum(
                skill_map[n]["tokens"] for n in skill_names if n in skill_map
            )
            skill_list = ", ".join(skill_names)
            print(f"  {agent:<25} {agent_tokens:>7} tokens  ({skill_list})")

    print()


def save_baseline(
    skills_data: List[Dict[str, Any]], output_path: Path
) -> None:
    """Save baseline metrics to JSON."""
    baseline = {
        "skills": {s["name"]: s for s in skills_data},
        "totals": {
            "skill_count": len(skills_data),
            "total_lines": sum(s["lines"] for s in skills_data),
            "total_chars": sum(s["chars"] for s in skills_data),
            "total_tokens": sum(s["tokens"] for s in skills_data),
            "total_aggressive": sum(s["aggressive_total"] for s in skills_data),
        },
    }
    output_path.write_text(json.dumps(baseline, indent=2))
    print(f"Baseline saved to {output_path}")


def compare_baselines(
    current: List[Dict[str, Any]], baseline_path: Path
) -> None:
    """Compare current metrics against a baseline."""
    baseline = json.loads(baseline_path.read_text())
    baseline_skills = baseline["skills"]
    baseline_totals = baseline["totals"]

    current_map = {s["name"]: s for s in current}
    current_totals = {
        "skill_count": len(current),
        "total_lines": sum(s["lines"] for s in current),
        "total_tokens": sum(s["tokens"] for s in current),
        "total_aggressive": sum(s["aggressive_total"] for s in current),
    }

    print(f"\n{'=' * 70}")
    print(f" COMPARISON vs {baseline_path.name}")
    print(f"{'=' * 70}\n")

    # Overall comparison
    for metric in ["skill_count", "total_lines", "total_tokens", "total_aggressive"]:
        old = baseline_totals.get(metric, 0)
        new = current_totals[metric]
        diff = new - old
        pct = (diff / old * 100) if old else 0
        sign = "+" if diff >= 0 else ""
        label = metric.replace("_", " ").title()
        print(f"  {label:<20} {old:>8} → {new:>8}  ({sign}{diff}, {sign}{pct:.1f}%)")

    # Per-skill changes (biggest movers)
    print(f"\nBiggest Token Changes:")
    changes: List[tuple] = []
    for name, skill in current_map.items():
        old_tokens = baseline_skills.get(name, {}).get("tokens", 0)
        diff = skill["tokens"] - old_tokens
        if diff != 0:
            changes.append((name, old_tokens, skill["tokens"], diff))

    changes.sort(key=lambda x: x[3])
    for name, old, new, diff in changes[:10]:
        sign = "+" if diff >= 0 else ""
        print(f"  {name:<35} {old:>6} → {new:>6}  ({sign}{diff})")

    if len(changes) > 10:
        rest = changes[10:]
        for name, old, new, diff in rest[-5:]:
            sign = "+" if diff >= 0 else ""
            print(f"  {name:<35} {old:>6} → {new:>6}  ({sign}{diff})")

    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure SKILL.md token usage")
    parser.add_argument(
        "--agent",
        help="Show combined prompt for a specific agent",
    )
    parser.add_argument(
        "--compare",
        type=Path,
        help="Compare against a baseline JSON file",
    )
    parser.add_argument(
        "--save-baseline",
        type=Path,
        help="Save baseline to JSON file",
    )
    parser.add_argument(
        "--skills-root",
        type=Path,
        default=SKILLS_ROOT,
        help="Root directory for skills",
    )
    args = parser.parse_args()

    skill_paths = find_all_skills(args.skills_root)
    if not skill_paths:
        print(f"No SKILL.md files found in {args.skills_root}", file=sys.stderr)
        sys.exit(1)

    all_data = [analyze_skill(p) for p in skill_paths]

    if args.agent:
        agent_skill_names = AGENT_SKILLS.get(args.agent)
        if agent_skill_names is None:
            print(f"Unknown agent: {args.agent}", file=sys.stderr)
            print(f"Known agents: {', '.join(AGENT_SKILLS.keys())}", file=sys.stderr)
            sys.exit(1)
        filtered = [s for s in all_data if s["name"] in agent_skill_names]
        print_report(filtered, agent_name=args.agent)
    else:
        print_report(all_data)

    if args.compare:
        compare_baselines(all_data, args.compare)

    if args.save_baseline:
        save_baseline(all_data, args.save_baseline)


if __name__ == "__main__":
    main()
