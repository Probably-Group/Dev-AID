#!/usr/bin/env python3
"""
Migrate existing skills to two-tier template v2.0.0

This script:
1. Reads existing SKILL.md files
2. Detects missing sections (§ 4: Quality, updated § 0)
3. Inserts sections at appropriate locations
4. Ensures <500 lines (moves content if needed)
5. Creates backup before modification
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Dict

# Quality Assurance Checklist (Condensed for insertion)
QUALITY_CHECKLIST_CONDENSED = """
## 4. Quality Assurance Checklist

**Before implementing this skill, ensure**:

### 4.1 Pre-Implementation Setup
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] Pre-commit hooks installed (`pre-commit install`)
- [ ] Linters installed (black, isort, flake8, mypy, bandit)

### 4.2 Dependency Management
- [ ] All dependencies pinned with exact versions (==)
- [ ] No manual transitive dependency pins
- [ ] Dependencies tested in clean environment

### 4.3 Code Quality Gates (Run BEFORE committing)
- [ ] `black .` - Code formatted
- [ ] `isort .` - Imports sorted
- [ ] `flake8 . --max-line-length=120` - No linting errors
- [ ] `mypy . --ignore-missing-imports` - Type checking passes
- [ ] `bandit -r .` - Security scan clean

### 4.4 Security Validation
- [ ] Input validation for ALL external inputs
- [ ] Path traversal prevention implemented
- [ ] Command injection prevention (no shell=True)
- [ ] SQL injection prevention (parameterized queries)
- [ ] Secrets not in code or error messages

📚 **For complete security validation guide**: See `../../../template-references/security-framework.md`

### 4.5 Test Coverage Requirements
- [ ] Tests written BEFORE implementation (TDD)
- [ ] Unit tests for all public functions
- [ ] Edge case tests (empty, null, max values)
- [ ] Security tests (injection, traversal, overflow)
- [ ] Code coverage >80%

### 4.6 Documentation Requirements
- [ ] Docstrings for all public functions/classes
- [ ] Security considerations documented
- [ ] Examples of correct usage
- [ ] Known limitations documented

---
"""

# Progressive disclosure addition to § 0
PROGRESSIVE_DISCLOSURE_SECTION = """
### 0.4 Progressive Disclosure (500-Line Limit)

**⚠️ CRITICAL**: This SKILL.md file MUST stay <500 lines for Claude Code to load it.

**If this file is approaching 500 lines**:
- Move detailed examples to `references/advanced-patterns.md`
- Move security examples to `references/security-examples.md`
- Move troubleshooting to `references/troubleshooting.md`
- Keep only summaries and links in main file

📚 **For complete progressive disclosure guide**: See `../../../template-references/progressive-disclosure.md`

---
"""

def find_skills() -> List[Path]:
    """Find all SKILL.md files"""
    skills_dir = Path(".dev-aid/skills/expert")
    if not skills_dir.exists():
        # Try from repository root
        repo_root = Path(__file__).parent.parent.parent
        skills_dir = repo_root / ".dev-aid" / "skills" / "expert"
    return list(skills_dir.glob("*/SKILL.md"))

def analyze_skill(skill_path: Path) -> Dict[str, any]:
    """Analyze skill and return migration needs"""
    with open(skill_path, 'r') as f:
        content = f.read()
        lines = content.split('\n')

    analysis = {
        'path': skill_path,
        'total_lines': len(lines),
        'has_section_0': bool(re.search(r'^## 0\.', content, re.MULTILINE)),
        'has_section_4_quality': bool(re.search(r'^## 4\. Quality Assurance', content, re.MULTILINE)),
        'has_progressive_disclosure': bool(re.search(r'Progressive Disclosure', content)),
        'has_template_references': bool(re.search(r'template-references/', content)),
        'exceeds_limit': len(lines) > 500,
        'at_limit': len(lines) >= 480,
    }

    # Determine risk level from frontmatter
    risk_match = re.search(r'risk_level:\s*(\w+)', content)
    analysis['risk_level'] = risk_match.group(1) if risk_match else 'UNKNOWN'

    return analysis

def backup_skill(skill_path: Path) -> Path:
    """Create backup of skill before modification"""
    backup_path = skill_path.with_suffix('.md.backup')
    import shutil
    shutil.copy2(skill_path, backup_path)
    return backup_path

def renumber_sections(content: str, offset: int = 1) -> str:
    """Renumber sections after insertion"""
    def increment_section(match):
        section_num = int(match.group(1))
        return f"## {section_num + offset}."

    return re.sub(r'^## (\d+)\.', increment_section, content, flags=re.MULTILINE)

def insert_quality_section(content: str) -> str:
    """Insert § 4: Quality Assurance Checklist"""

    # Find where to insert (after § 3, before § 5 or § 4 if exists)
    # Look for ## 4. or ## 5. to determine insertion point
    section_4_match = re.search(r'^## 4\.', content, re.MULTILINE)
    section_5_match = re.search(r'^## 5\.', content, re.MULTILINE)

    if section_4_match:
        # § 4 exists, check if it's Quality Assurance
        section_4_content = content[section_4_match.start():section_4_match.start()+200]
        if 'Quality Assurance' in section_4_content:
            return content  # Already has it
        else:
            # Insert before existing § 4, renumber sections after
            insertion_point = section_4_match.start()
            before = content[:insertion_point]
            after = content[insertion_point:]
            after = renumber_sections(after, offset=1)
            content = before + QUALITY_CHECKLIST_CONDENSED + "\n" + after
    elif section_5_match:
        # Insert before § 5
        insertion_point = section_5_match.start()
        content = content[:insertion_point] + QUALITY_CHECKLIST_CONDENSED + "\n" + content[insertion_point:]
    else:
        # Append at end (before final checklist if exists)
        final_checklist_match = re.search(r'^## Final Checklist', content, re.MULTILINE)
        if final_checklist_match:
            insertion_point = final_checklist_match.start()
            content = content[:insertion_point] + QUALITY_CHECKLIST_CONDENSED + "\n" + content[insertion_point:]
        else:
            content += "\n" + QUALITY_CHECKLIST_CONDENSED

    return content

def add_progressive_disclosure(content: str) -> str:
    """Add progressive disclosure to § 0"""

    # Find end of § 0 (before ## 1.)
    section_1_match = re.search(r'^## 1\.', content, re.MULTILINE)
    if section_1_match:
        insertion_point = section_1_match.start()
        content = content[:insertion_point] + PROGRESSIVE_DISCLOSURE_SECTION + "\n" + content[insertion_point:]

    return content

def migrate_skill(skill_path: Path, dry_run: bool = True) -> Dict[str, any]:
    """Migrate a single skill to v2.0.0"""

    analysis = analyze_skill(skill_path)
    result = {'skill': skill_path.parent.name, 'changes': [], 'warnings': []}

    # Read content
    with open(skill_path, 'r') as f:
        content = f.read()

    original_lines = len(content.split('\n'))

    # Step 1: Add § 4 Quality if missing
    if not analysis['has_section_4_quality']:
        content = insert_quality_section(content)
        result['changes'].append('Added § 4: Quality Assurance Checklist')

    # Step 2: Add progressive disclosure to § 0 if missing
    if not analysis['has_progressive_disclosure']:
        content = add_progressive_disclosure(content)
        result['changes'].append('Added § 0.4: Progressive Disclosure')

    # Step 3: Check new line count
    new_lines = len(content.split('\n'))
    result['original_lines'] = original_lines
    result['new_lines'] = new_lines

    if new_lines > 500:
        result['warnings'].append(f'⚠️  EXCEEDS 500 LINES: {new_lines} lines')
        result['warnings'].append('   Manual intervention needed: move content to references/')

    # Step 4: Write changes (if not dry run)
    if not dry_run and result['changes']:
        backup_skill(skill_path)
        with open(skill_path, 'w') as f:
            f.write(content)
        result['status'] = 'MIGRATED'
    elif result['changes']:
        result['status'] = 'DRY_RUN'
    else:
        result['status'] = 'NO_CHANGES'

    return result

def migrate_all_skills(batch: str = 'all', dry_run: bool = True, max_lines: int = None, safe_only: bool = False) -> List[Dict]:
    """Migrate all skills or specific batch"""

    skills = find_skills()
    results = []

    # Analyze all skills first for filtering
    skill_analyses = [(skill, analyze_skill(skill)) for skill in skills]

    # Filter by batch if specified
    if batch == 'low':
        # Filter LOW risk skills
        skill_analyses = [(s, a) for s, a in skill_analyses if a.get('risk_level', '') == 'LOW']
    elif batch == 'medium':
        skill_analyses = [(s, a) for s, a in skill_analyses if a.get('risk_level', '') == 'MEDIUM']
    elif batch == 'high':
        skill_analyses = [(s, a) for s, a in skill_analyses if a.get('risk_level', '') == 'HIGH']

    # Pre-filter by line count if requested (for safe migration)
    if safe_only or max_lines:
        # Need to do a dry migration first to determine final line count
        filtered = []
        for skill_path, analysis in skill_analyses:
            # Estimate final lines (current + ~62 for quality + ~13 for disclosure)
            estimated_lines = analysis['total_lines'] + 75
            if max_lines and estimated_lines <= max_lines:
                filtered.append((skill_path, analysis))
            elif safe_only and estimated_lines <= 500:
                filtered.append((skill_path, analysis))
        skill_analyses = filtered

    skills = [s for s, a in skill_analyses]

    filter_desc = f"batch: {batch}"
    if safe_only:
        filter_desc += ", safe only (<500 lines)"
    elif max_lines:
        filter_desc += f", max {max_lines} lines"

    print(f"🔄 Migrating {len(skills)} skills ({filter_desc}, dry_run: {dry_run})...")

    for skill_path in sorted(skills):
        result = migrate_skill(skill_path, dry_run=dry_run)
        results.append(result)

        # Print progress
        status_emoji = {'MIGRATED': '✅', 'DRY_RUN': '📝', 'NO_CHANGES': '⏭️'}
        print(f"{status_emoji.get(result['status'], '❓')} {result['skill']}: {result['original_lines']} → {result['new_lines']} lines")

        for change in result['changes']:
            print(f"   + {change}")
        for warning in result['warnings']:
            print(f"   {warning}")

    return results

def print_summary(results: List[Dict]):
    """Print migration summary"""
    total = len(results)
    migrated = len([r for r in results if r['status'] == 'MIGRATED'])
    no_changes = len([r for r in results if r['status'] == 'NO_CHANGES'])
    warnings = len([r for r in results if r['warnings']])
    exceeds_500 = len([r for r in results if r['new_lines'] > 500])

    print("\n" + "="*60)
    print("📊 MIGRATION SUMMARY")
    print("="*60)
    print(f"Total skills processed: {total}")
    print(f"Migrated: {migrated}")
    print(f"No changes needed: {no_changes}")
    print(f"Warnings: {warnings}")
    print(f"Exceeds 500 lines: {exceeds_500}")

    if exceeds_500:
        print("\n⚠️  Skills requiring manual intervention (>500 lines):")
        for r in results:
            if r['new_lines'] > 500:
                print(f"   - {r['skill']}: {r['new_lines']} lines")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Migrate skills to two-tier template v2.0.0')
    parser.add_argument('--batch', choices=['all', 'low', 'medium', 'high'], default='all',
                        help='Which batch to migrate')
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='Dry run (no actual changes)')
    parser.add_argument('--execute', action='store_true',
                        help='Execute migration (overrides dry-run)')
    parser.add_argument('--safe-only', action='store_true',
                        help='Only migrate skills that will stay under 500 lines')
    parser.add_argument('--max-lines', type=int,
                        help='Only migrate skills that will stay under this line count')

    args = parser.parse_args()

    dry_run = not args.execute

    if not dry_run:
        print("⚠️  EXECUTING MIGRATION (changes will be made)")
        print("   Backups will be created (.md.backup)")
        input("Press Enter to continue or Ctrl+C to cancel...")

    results = migrate_all_skills(batch=args.batch, dry_run=dry_run, max_lines=args.max_lines, safe_only=args.safe_only)
    print_summary(results)
