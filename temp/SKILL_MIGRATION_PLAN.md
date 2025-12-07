# Skill Migration Plan: Updating 72 Skills to Two-Tier Template

**Date**: 2025-12-06
**Status**: ✅ **COMPLETED** (PR #62)
**Scope**: Migrate 72 existing skills to new merged template format
**Goal**: Add QA sections without breaking existing skills or CI

---

## ✅ Migration Complete!

**Completion Date**: 2025-12-06
**Pull Request**: [#62 - Migrate all 72 skills to two-tier template v2.0.0](https://github.com/martinholovsky/Dev-AID/pull/62)

### Final Results
- ✅ All 72 skills migrated to v2.0.0 template
- ✅ All 72 skills have § 4: Quality Assurance Checklist
- ✅ All 72 skills under 500-line limit (Claude Code compatible)
- ✅ 47 skills automatically condensed with references/
- ✅ 5 skills manually condensed
- ✅ 193 files changed (+18,125 insertions, -9,803 deletions)

### Migration Tools Created
- `migrate-skills-to-v2.py` - Automated migration script
- `condense-skills.py` - Automated condensing script

---

## Original Plan (For Reference)

---

## Current State Analysis

### Statistics
- **Total Skills**: 72
- **Have § 0**: ✅ All 72 (Anti-Hallucination Protocol)
- **Have § 4 Quality**: ❌ None (0/72) - **THIS IS THE PROBLEM**
- **Exceed 500 lines**: ❌ 4 skills (need fixing)
  - web-research-expert: 632 lines
  - skill-creation-expert: 601 lines
  - plan-review-expert: 572 lines
  - refactoring-expert: 522 lines
- **At limit (499 lines)**: ⚠️ Many skills (no room for new content)

### The Problem

**Existing skills are missing**:
1. § 4: Quality Assurance Checklist (8 subsections) - **CRITICAL**
2. Updated § 0: Security-First Framework (has old Anti-Hallucination only)
3. References to template-references/ for detailed content
4. Progressive disclosure guidance

**This will cause**:
- ❌ CI failures (skills don't follow QA checklist)
- ❌ Inconsistent quality standards
- ❌ No dependency management guidance
- ❌ No pre-commit hooks setup
- ❌ No security validation templates

---

## Migration Strategy Options

### Option A: Automated Script Migration ⚡ (Recommended)

**Approach**: Create Python migration script to automate bulk updates

**Pros**:
- Fast (can process all 72 skills in minutes)
- Consistent formatting
- Repeatable and testable
- Can handle edge cases systematically
- Easy to rollback if issues

**Cons**:
- Requires careful script development
- Need thorough testing before running
- Risk of edge cases not handled

**Time**: 2-3 hours (script dev) + 30 min (execution) + 2 hours (review)

---

### Option B: Gradual Manual Migration 🐌

**Approach**: Update skills as they're used or encounter issues

**Pros**:
- No risk of breaking working skills
- Can handle each skill's unique needs
- Learn from early migrations

**Cons**:
- Inconsistent state for months
- CI will fail on old skills
- Time-consuming (72 skills × 15 min = 18 hours)
- Easy to forget skills

**Time**: 18+ hours over weeks/months

---

### Option C: Batch Processing with Review ✅ (Safest)

**Approach**: Group by risk level, process in batches, review each batch

**Pros**:
- Systematic and organized
- Can test each batch before proceeding
- Easy rollback per batch
- Trackable progress
- Combines automation + human review

**Cons**:
- Slower than full automation
- Still requires significant time

**Time**: 4-5 hours total

---

### Option D: Template Migration Agent 🤖

**Approach**: Create specialized agent/Task to handle migration

**Pros**:
- Leverages existing Task tool
- Can make intelligent decisions
- Handles complex cases well

**Cons**:
- Complex to set up
- Slower than script
- Agent might hallucinate changes

**Time**: 1 hour (setup) + 3-4 hours (execution + review)

---

## Recommended Approach: **Hybrid (A + C)**

**Combine automated script with batched review**

### Phase 1: Create Migration Script (2 hours)

**Script Responsibilities**:
1. Read SKILL.md
2. Detect existing sections
3. Insert § 4: Quality Assurance Checklist (condensed version)
4. Update § 0: Add risk assessment and progressive disclosure
5. Add references to template-references/ in appropriate sections
6. Verify <500 lines after changes
7. If >500 lines, suggest content to move to references/
8. Create backup before changes

**Script Output**:
- Modified SKILL.md
- Migration report (what changed)
- Warnings if manual review needed
- List of skills exceeding 500 lines

### Phase 2: Batch Processing by Risk Level (3 hours)

**Batch 1: LOW Risk Skills** (~30 skills)
- Documentation, UI/UX, testing skills
- Add § 4: Quality Checklist (focus on QA, skip security deep-dive)
- Quick review, minimal risk
- Test 2-3 skills thoroughly, then batch-process rest

**Batch 2: MEDIUM Risk Skills** (~25 skills)
- API, data processing, application code
- Add § 4: Quality Checklist + enhanced security section
- Add vulnerability research reminder
- Review each skill for security appropriateness

**Batch 3: HIGH Risk Skills** (~17 skills)
- Security, infrastructure, auth, data storage
- Add complete § 4: Quality Checklist
- Ensure § 0.2: Vulnerability Research is present
- Add links to all template-references/
- **MANDATORY**: Manual review of each skill

### Phase 3: Fix Oversized Skills (1 hour)

**4 skills >500 lines**:
1. Identify verbose content (examples, troubleshooting, etc.)
2. Move to references/ directory
3. Add links in main SKILL.md
4. Verify <500 lines after migration

### Phase 4: Validation & Testing (1 hour)

**Per-Batch Testing**:
- Run quality gates on sample skills
- Verify skills load in Claude Code
- Test skill activation via select-skills.sh
- Check no regressions in CI

---

## Detailed Migration Script Design

### Script: `migrate-skills-to-v2.py`

```python
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

def insert_quality_section(content: str) -> str:
    """Insert § 4: Quality Assurance Checklist"""

    # Find where to insert (after § 3, before § 5 or § 4 if exists)
    # Look for ## 4. or ## 5. to determine insertion point
    section_4_match = re.search(r'^## 4\.', content, re.MULTILINE)
    section_5_match = re.search(r'^## 5\.', content, re.MULTILINE)

    if section_4_match:
        # § 4 exists, check if it's Quality Assurance
        if 'Quality Assurance' in content[section_4_match.start():section_4_match.start()+200]:
            return content  # Already has it
        else:
            # Insert before existing § 4, renumber sections after
            insertion_point = section_4_match.start()
            content = content[:insertion_point] + QUALITY_CHECKLIST_CONDENSED + "\n" + renumber_sections(content[insertion_point:], offset=1)
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

def migrate_all_skills(batch: str = 'all', dry_run: bool = True) -> List[Dict]:
    """Migrate all skills or specific batch"""

    skills = find_skills()
    results = []

    # Filter by batch if specified
    if batch == 'low':
        # Filter LOW risk skills
        skills = [s for s in skills if 'LOW' in analyze_skill(s).get('risk_level', '')]
    elif batch == 'medium':
        skills = [s for s in skills if 'MEDIUM' in analyze_skill(s).get('risk_level', '')]
    elif batch == 'high':
        skills = [s for s in skills if 'HIGH' in analyze_skill(s).get('risk_level', '')]

    print(f"🔄 Migrating {len(skills)} skills (batch: {batch}, dry_run: {dry_run})...")

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

    args = parser.parse_args()

    dry_run = not args.execute

    if not dry_run:
        print("⚠️  EXECUTING MIGRATION (changes will be made)")
        print("   Backups will be created (.md.backup)")
        input("Press Enter to continue or Ctrl+C to cancel...")

    results = migrate_all_skills(batch=args.batch, dry_run=dry_run)
    print_summary(results)
```

### Usage

```bash
# Dry run (preview changes)
python migrate-skills-to-v2.py --dry-run --batch all

# Execute LOW risk batch
python migrate-skills-to-v2.py --execute --batch low

# Execute MEDIUM risk batch (with review)
python migrate-skills-to-v2.py --execute --batch medium

# Execute HIGH risk batch (manual review each)
python migrate-skills-to-v2.py --execute --batch high

# Execute all (only after testing batches)
python migrate-skills-to-v2.py --execute --batch all
```

---

## Implementation Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Phase 1**: Script Development | 2 hours | Create migrate-skills-to-v2.py, test on 2-3 skills |
| **Phase 2**: Batch 1 (LOW risk) | 30 min | Migrate ~30 LOW risk skills, quick review |
| **Phase 3**: Batch 2 (MEDIUM risk) | 1 hour | Migrate ~25 MEDIUM risk skills, detailed review |
| **Phase 4**: Batch 3 (HIGH risk) | 1.5 hours | Migrate ~17 HIGH risk skills, **manual review each** |
| **Phase 5**: Fix Oversized Skills | 1 hour | Fix 4 skills >500 lines (move content to references/) |
| **Phase 6**: Validation & Testing | 1 hour | Test skill loading, CI checks, skill activation |
| **TOTAL** | **7 hours** | Full migration with review |

---

## Risk Mitigation

### Safeguards

1. **Backups**: Script creates .backup files before any changes
2. **Dry Run**: Default mode, must explicitly --execute
3. **Batch Processing**: Can stop/rollback after each batch
4. **Git Commits**: Commit each batch separately for easy rollback
5. **Testing**: Test 2-3 skills thoroughly before batch processing

### Rollback Plan

```bash
# Rollback single skill
mv .dev-aid/skills/expert/SKILL_NAME/SKILL.md.backup \
   .dev-aid/skills/expert/SKILL_NAME/SKILL.md

# Rollback entire batch (if committed separately)
git revert <commit-hash>

# Rollback all (if needed)
git reset --hard <commit-before-migration>
```

---

## Alternative: Gradual Migration

If automated approach is too risky, use gradual migration:

### Week 1: Critical Skills (HIGH risk)
- Manually migrate top 5 most-used HIGH risk skills
- Test thoroughly
- Learn from issues

### Week 2: Remaining HIGH Risk
- Migrate remaining HIGH risk skills using learnings
- Create template for MEDIUM risk

### Week 3: MEDIUM Risk
- Batch migrate MEDIUM risk skills
- Spot check 25%

### Week 4: LOW Risk + Cleanup
- Batch migrate LOW risk skills
- Fix any remaining issues
- Update documentation

---

## Recommendation

**Use Hybrid Approach (Option A + C)**:

1. **Develop script** (2 hours) - Worth the investment
2. **Test on 3 skills** (30 min) - One of each risk level
3. **Batch migrate with review** (4 hours):
   - LOW risk: Quick batch
   - MEDIUM risk: Detailed review
   - HIGH risk: Manual review each
4. **Commit in batches** - Easy rollback
5. **Validate** - Test CI, skill loading, activation

**Total Time**: ~7 hours
**Risk**: Low (backups + batch commits + testing)
**Benefit**: All 72 skills consistent, CI-compliant, future-proof

---

## Next Steps

1. **Review this plan** - Agree on approach
2. **Create migration script** - Implement migrate-skills-to-v2.py
3. **Test on 3 skills** - One LOW, one MEDIUM, one HIGH
4. **Execute Batch 1 (LOW)** - Lowest risk, most skills
5. **Review results** - Adjust script if needed
6. **Execute Batch 2 & 3** - MEDIUM and HIGH
7. **Fix oversized skills** - 4 skills >500 lines
8. **Final validation** - CI, testing, documentation

---

**Status**: Ready to implement
**Estimated Completion**: 1 day (with testing and review)
