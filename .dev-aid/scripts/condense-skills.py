#!/usr/bin/env python3
"""
Condense skills that exceed 500 lines by moving content to references/

This script:
1. Identifies skills >500 lines
2. Analyzes sections that can be moved to references/
3. Creates references/ directory
4. Moves verbose content (examples, patterns, troubleshooting)
5. Adds links in main file
6. Ensures final file <500 lines
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

def find_oversized_skills() -> List[Path]:
    """Find all SKILL.md files >500 lines"""
    skills_dir = Path(".dev-aid/skills/expert")
    if not skills_dir.exists():
        repo_root = Path(__file__).parent.parent.parent
        skills_dir = repo_root / ".dev-aid" / "skills" / "expert"

    oversized = []
    for skill_path in skills_dir.glob("*/SKILL.md"):
        with open(skill_path, 'r') as f:
            line_count = len(f.readlines())
        if line_count > 500:
            oversized.append(skill_path)

    return oversized

def analyze_sections(content: str) -> Dict[str, Tuple[int, int]]:
    """Analyze sections in SKILL.md and return their positions"""
    sections = {}

    # Find all sections
    for match in re.finditer(r'^## (\d+)\. (.+?)$', content, re.MULTILINE):
        section_num = match.group(1)
        section_title = match.group(2)
        section_start = match.start()

        # Find next section or end of file
        next_section = re.search(r'^## \d+\.', content[section_start+1:], re.MULTILINE)
        if next_section:
            section_end = section_start + next_section.start() + 1
        else:
            section_end = len(content)

        sections[f"{section_num}. {section_title}"] = (section_start, section_end)

    return sections

def identify_movable_sections(content: str, sections: Dict[str, Tuple[int, int]]) -> List[str]:
    """Identify sections that can be moved to references/"""
    movable = []

    for section_name, (start, end) in sections.items():
        section_content = content[start:end]
        section_lines = len(section_content.split('\n'))

        # Criteria for movable sections:
        # 1. Large sections (>100 lines)
        # 2. Sections with lots of code examples
        # 3. Sections with "Examples", "Patterns", "Troubleshooting", "Advanced"

        if section_lines > 100:
            movable.append(section_name)
        elif any(keyword in section_name for keyword in [
            'Example', 'Pattern', 'Troubleshooting', 'Advanced',
            'Deep Dive', 'Reference', 'Tutorial'
        ]):
            if section_lines > 50:
                movable.append(section_name)
        elif section_content.count('```') > 4:  # Many code blocks
            movable.append(section_name)

    return movable

def create_condensed_summary(section_content: str, section_name: str) -> str:
    """Create a condensed summary of a section"""
    # Extract first paragraph as summary
    paragraphs = [p.strip() for p in section_content.split('\n\n') if p.strip() and not p.strip().startswith('```')]

    # Find first meaningful paragraph (skip section header)
    summary = ""
    for para in paragraphs[:3]:
        if not para.startswith('#') and len(para) > 50:
            summary = para
            break

    if not summary and paragraphs:
        summary = paragraphs[0]

    return summary[:300] + "..." if len(summary) > 300 else summary

def condense_skill(skill_path: Path, dry_run: bool = True) -> Dict:
    """Condense a single oversized skill"""

    result = {
        'skill': skill_path.parent.name,
        'original_lines': 0,
        'new_lines': 0,
        'sections_moved': [],
        'references_created': [],
        'status': 'NO_CHANGES',
        'warnings': []
    }

    # Read content
    with open(skill_path, 'r') as f:
        content = f.read()

    result['original_lines'] = len(content.split('\n'))

    if result['original_lines'] <= 500:
        result['warnings'].append('Skill already under 500 lines')
        return result

    # Analyze sections
    sections = analyze_sections(content)
    movable_sections = identify_movable_sections(content, sections)

    if not movable_sections:
        result['warnings'].append('No movable sections identified - manual intervention needed')
        result['status'] = 'MANUAL_REQUIRED'
        return result

    # Create references directory
    references_dir = skill_path.parent / "references"

    # Move sections to references
    new_content = content
    for section_name in movable_sections:
        if section_name not in sections:
            continue

        start, end = sections[section_name]
        section_content = content[start:end]

        # Create reference filename
        ref_filename = re.sub(r'^\d+\.\s*', '', section_name)
        ref_filename = re.sub(r'[^\w\s-]', '', ref_filename)
        ref_filename = re.sub(r'\s+', '-', ref_filename).lower()
        ref_filename = f"{ref_filename}.md"

        # Create condensed replacement
        summary = create_condensed_summary(section_content, section_name)
        replacement = f"## {section_name}\n\n{summary}\n\n📚 **For complete details**: See `references/{ref_filename}`\n\n---\n"

        # Replace in content
        new_content = new_content[:start] + replacement + new_content[end:]

        # Track moved section
        result['sections_moved'].append(section_name)
        result['references_created'].append(ref_filename)

        # Prepare reference file content
        if not dry_run:
            references_dir.mkdir(exist_ok=True)
            ref_path = references_dir / ref_filename
            with open(ref_path, 'w') as f:
                f.write(section_content)

    result['new_lines'] = len(new_content.split('\n'))

    # Check if still oversized
    if result['new_lines'] > 500:
        result['warnings'].append(f'Still exceeds 500 lines: {result["new_lines"]} lines')
        result['warnings'].append('Additional manual condensing needed')
        result['status'] = 'PARTIAL'
    else:
        result['status'] = 'SUCCESS'

    # Write changes
    if not dry_run and result['sections_moved']:
        # Create backup
        import shutil
        backup_path = skill_path.with_suffix('.md.backup-condense')
        shutil.copy2(skill_path, backup_path)

        # Write condensed content
        with open(skill_path, 'w') as f:
            f.write(new_content)

    return result

def condense_all_oversized(dry_run: bool = True) -> List[Dict]:
    """Condense all oversized skills"""

    skills = find_oversized_skills()
    results = []

    print(f"🔄 Condensing {len(skills)} oversized skills (dry_run: {dry_run})...")

    for skill_path in sorted(skills):
        result = condense_skill(skill_path, dry_run=dry_run)
        results.append(result)

        # Print progress
        status_emoji = {'SUCCESS': '✅', 'PARTIAL': '⚠️', 'MANUAL_REQUIRED': '❌', 'NO_CHANGES': '⏭️'}
        print(f"\n{status_emoji.get(result['status'], '❓')} {result['skill']}: {result['original_lines']} → {result['new_lines']} lines")

        if result['sections_moved']:
            print(f"   📦 Moved {len(result['sections_moved'])} sections:")
            for section in result['sections_moved']:
                print(f"      - {section}")

        for warning in result['warnings']:
            print(f"   ⚠️  {warning}")

    return results

def print_summary(results: List[Dict]):
    """Print condensing summary"""
    total = len(results)
    success = len([r for r in results if r['status'] == 'SUCCESS'])
    partial = len([r for r in results if r['status'] == 'PARTIAL'])
    manual = len([r for r in results if r['status'] == 'MANUAL_REQUIRED'])
    no_changes = len([r for r in results if r['status'] == 'NO_CHANGES'])

    print("\n" + "="*60)
    print("📊 CONDENSING SUMMARY")
    print("="*60)
    print(f"Total skills processed: {total}")
    print(f"✅ Successfully condensed: {success}")
    print(f"⚠️  Partially condensed: {partial}")
    print(f"❌ Manual intervention required: {manual}")
    print(f"⏭️  No changes needed: {no_changes}")

    if partial:
        print("\n⚠️  Skills still exceeding 500 lines (manual intervention needed):")
        for r in results:
            if r['status'] == 'PARTIAL':
                print(f"   - {r['skill']}: {r['new_lines']} lines (reduced from {r['original_lines']})")

    if manual:
        print("\n❌ Skills requiring manual condensing:")
        for r in results:
            if r['status'] == 'MANUAL_REQUIRED':
                print(f"   - {r['skill']}: {r['original_lines']} lines")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Condense oversized skills to <500 lines')
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='Dry run (no actual changes)')
    parser.add_argument('--execute', action='store_true',
                        help='Execute condensing (overrides dry-run)')
    parser.add_argument('--skill', type=str,
                        help='Condense specific skill only')

    args = parser.parse_args()

    dry_run = not args.execute

    if not dry_run:
        print("⚠️  EXECUTING CONDENSING (changes will be made)")
        print("   Backups will be created (.md.backup-condense)")
        input("Press Enter to continue or Ctrl+C to cancel...")

    if args.skill:
        # Condense specific skill
        skill_path = Path(f".dev-aid/skills/expert/{args.skill}/SKILL.md")
        if not skill_path.exists():
            print(f"❌ Skill not found: {args.skill}")
            exit(1)
        result = condense_skill(skill_path, dry_run=dry_run)
        print_summary([result])
    else:
        # Condense all oversized skills
        results = condense_all_oversized(dry_run=dry_run)
        print_summary(results)
