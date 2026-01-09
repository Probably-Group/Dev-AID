# CLAUDE.md Smart Initialization Plan

## Overview
Enhanced CLAUDE.md initialization that preserves user content, validates accuracy, applies progressive disclosure for large files, and provides clear migration reports.

## Requirements

### 1. Backup Strategy
- **Format**: `CLAUDE_original-backup.md` (clear, no timestamp clutter)
- **Location**: `.dev-aid/backups/CLAUDE_original-backup_YYYYMMDD_HHMMSS.md`
- **Symlink**: Create `CLAUDE_original-backup.md` → latest backup for easy access
- **Behavior**: Always backup before any modification

### 2. Content Validation
Detect and flag issues in existing CLAUDE.md:

#### Technology Stack Validation
- **Outdated versions**: "React 16" when project uses React 18
- **Missing technologies**: Project uses TypeScript but CLAUDE.md doesn't mention it
- **Deprecated tools**: Mentions Bower, Grunt when project uses npm, Webpack
- **Wrong framework**: Says Angular but project is React-based

#### Instruction Validation
- **Conflicting rules**: "Never use TypeScript" but project is TypeScript-based
- **Invalid paths**: References `/old-src/` when actual path is `/src/`
- **Deprecated patterns**: Suggests Class Components when project uses Hooks
- **Security issues**: Hardcoded credentials, API keys in examples

#### Quality Checks
- **Duplicate sections**: Same instruction repeated multiple times
- **Contradictions**: "Always use X" followed by "Never use X"
- **Formatting issues**: Broken markdown, malformed code blocks
- **Length check**: Total line count for progressive disclosure decision

### 3. Progressive Disclosure (>500 lines)

Split strategy when merged content exceeds 500 lines:

```
CLAUDE.md (Main File - ≤500 lines)
├── Core role and responsibilities
├── Memory bank integration
├── Essential tech stack summary
├── Critical guidelines (top 10-15)
└── References to extended documentation

.dev-aid/providers/claude/
├── CLAUDE_extended.md (Auto-generated detailed content)
│   ├── Complete tech stack details
│   ├── All Dev-AID best practices
│   ├── Memory bank detailed usage
│   └── Advanced patterns
│
└── CLAUDE_custom.md (User's original preserved content)
    ├── Custom instructions from original CLAUDE.md
    ├── Project-specific guidelines
    └── Team conventions
```

#### Main CLAUDE.md Structure
```markdown
# Project Context for Claude

## Role & Responsibilities
[Essential role definition - 20-30 lines]

## Memory Bank
[Key memory bank usage - 10-15 lines]
📖 Detailed memory bank usage: See .dev-aid/providers/claude/CLAUDE_extended.md#memory-bank

## Tech Stack (Summary)
- Frontend: React 18, TypeScript
- Backend: Node.js, Express
[10-15 lines max]
📖 Complete tech stack: See .dev-aid/providers/claude/CLAUDE_extended.md#tech-stack

## Critical Guidelines
1. [Most important rule]
2. [Second most important]
...
10. [10th most important]
📖 Complete guidelines: See .dev-aid/providers/claude/CLAUDE_extended.md#guidelines

## Custom Project Instructions
[Top 5-10 custom instructions from original CLAUDE.md]
📖 All custom instructions: See .dev-aid/providers/claude/CLAUDE_custom.md

---
*This file is managed by Dev-AID. Original content preserved in CLAUDE_custom.md*
```

#### Prioritization Logic
1. **Critical** (must be in main file):
   - Role definition
   - Memory bank basics
   - Tech stack summary (5-10 lines)
   - Top 10 most important rules

2. **Important** (goes to CLAUDE_extended.md):
   - Complete tech stack
   - All Dev-AID patterns
   - Detailed best practices
   - Advanced usage

3. **Custom** (goes to CLAUDE_custom.md):
   - All user's original content
   - Project-specific rules
   - Team conventions
   - Historical context

### 4. Progressive Disclosure Detection (NEW in v1.3.0-beta.10)

Before applying any changes, detect if user already uses progressive disclosure:

#### Detection Checks
1. **Rules Directory**: Check for `.<provider>/rules/` with `.md` files
   - `.claude/rules/*.md` for Claude
   - `.gemini/rules/*.md` for Gemini
   - `.openai/rules/*.md` for OpenAI

2. **@ File References**: Scan existing context file for `@path/to/file.md` patterns
   - `@.claude/rules/security.md`
   - `@./custom-instructions.md`
   - `@~/shared/team-conventions.md`

#### Behavior When Detected
- **Skip redundant splitting**: Don't apply progressive disclosure if already in use
- **Preserve structure**: Leave `.claude/rules/` and `@` references untouched
- **Enhance only**: Add Dev-AID template content to main file without restructuring

### 5. Quality Assessment (NEW in v1.3.0-beta.10)

Assess content quality to determine merge strategy:

#### Quality Thresholds
- **Minimum Lines**: 20 lines (below = `poor`)
- **Minimum Sections**: 3 sections (below = `draft`)
- **Minimum Section Lines**: 3 lines per section (below = `incomplete`)

#### Placeholder Detection
Patterns that indicate incomplete content:
- `TODO`, `FIXME`, `XXX`, `TBD`
- `ADD.*HERE`, `INSERT.*HERE`, `DESCRIBE.*HERE`
- `PLACEHOLDER`, `YOUR.*HERE`, `LOREM.*IPSUM`
- `FILL IN`, `REPLACE THIS`, `UPDATE THIS`

#### Recommended Sections
Check for presence of:
- Role/Responsibilities/Purpose
- Tech Stack/Technologies/Framework
- Guidelines/Rules/Conventions/Standards
- Workflow/Process/Development
- Testing/Quality/Lint

#### Quality Levels
- **`good`**: Meets all thresholds, no placeholders, has recommended sections
- **`incomplete`**: Missing some recommended sections or minimal section content
- **`draft`**: Below minimum sections or significant placeholders
- **`poor`**: Below minimum lines or mostly placeholders

### 6. Content Merging Process (8-Step Flow)

```
┌─────────────────────────────────────┐
│ 1. Backup existing context file     │
│    .dev-aid/backups/CLAUDE_original │
│    -backup_20260102_143022.md       │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 2. Detect progressive disclosure    │
│    - Check .<provider>/rules/       │
│    - Scan for @ file references     │
│    - Record existing structure      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 3. Assess content quality           │
│    - Count lines and sections       │
│    - Detect placeholders            │
│    - Check recommended sections     │
│    - Determine quality level        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 4. Validate content                 │
│    - Check tech stack accuracy      │
│    - Detect conflicts               │
│    - Find invalid references        │
│    - Flag security issues           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 5. Merge with Dev-AID template      │
│    - Combine validated sections     │
│    - Enhance low-quality content    │
│    - Remove duplicates              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 6. Apply progressive disclosure     │
│    (or skip if already in use)      │
└──────────────┬──────────────────────┘
               │
       ┌───────┴───────┐
       │               │
   Already          New to PD
   using PD            │
       │               │
       ▼               ▼
┌─────────────┐  ┌──────────────┐
│ Skip split  │  │ >500 lines?  │
│ Keep user's │  │ Apply split  │
│ structure   │  │ if needed    │
└──────┬──────┘  └──────┬───────┘
       │                │
       └────────┬───────┘
                ▼
┌─────────────────────────────────────┐
│ 7. Create symlink                   │
│    CLAUDE.md → .dev-aid/providers/  │
│    claude/CLAUDE.md                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 8. Generate migration report        │
│    - Issues found & resolutions     │
│    - Quality assessment results     │
│    - Progressive disclosure status  │
│    - Actions taken                  │
└─────────────────────────────────────┘
```

### 7. Validation Report Format

```markdown
# 📋 CLAUDE.md Migration Report
Generated: 2026-01-02 14:30:22

## ✅ Successfully Preserved
- ✓ Custom role definition (15 lines)
- ✓ Project-specific coding standards (23 lines)
- ✓ Team conventions (8 lines)
- ✓ API documentation references (5 lines)
**Total preserved**: 51 lines of custom content

## ⚠️ Issues Detected & Resolutions

### 1. Outdated Technology References
**Issue**: Mentions "React 16.8" but project uses "React 18.2"
**Location**: Original line 45
**Resolution**: Updated to current version (React 18.2.0)
**Action**: AUTO-FIXED ✓

### 2. Conflicting Instructions
**Issue**: "Avoid using TypeScript" conflicts with project's .ts files
**Location**: Original line 78
**Resolution**: Removed conflicting statement, project is TypeScript-based
**Action**: AUTO-RESOLVED ✓

### 3. Invalid File Path
**Issue**: References `/old-src/components/` (directory not found)
**Location**: Original line 112
**Current path**: `/src/components/`
**Resolution**: Updated path reference
**Action**: AUTO-FIXED ✓

### 4. Deprecated Pattern
**Issue**: Recommends React Class Components
**Location**: Original line 134
**Resolution**: Updated to recommend functional components with hooks
**Action**: FLAGGED - Please review

### 5. Duplicate Section
**Issue**: "Code Style Guidelines" section appears twice
**Locations**: Lines 56-78 and 201-219
**Resolution**: Merged into single section, removed duplicates
**Action**: AUTO-RESOLVED ✓

## 📊 Migration Statistics
- **Original file**: 687 lines
- **Dev-AID template**: 425 lines
- **Merged total**: 892 lines
- **After deduplication**: 658 lines
- **Final size**: 658 lines

## 🔀 Progressive Disclosure Applied
**Reason**: Content exceeds 500 lines (658 lines total)

**File structure created**:
```
CLAUDE.md (Main - 450 lines)
├── Core role and context
├── Essential tech stack summary
├── Top 15 critical guidelines
└── Quick reference links

.dev-aid/providers/claude/CLAUDE_extended.md (158 lines)
├── Complete tech stack details
├── All Dev-AID best practices
└── Advanced patterns

.dev-aid/providers/claude/CLAUDE_custom.md (50 lines)
├── All your original custom instructions
├── Project-specific guidelines
└── Team conventions
```

## 🔍 Action Required

### Items Needing Your Review:
1. **Line 134 (CLAUDE_custom.md:23)**: Deprecated React pattern flagged
   - Review and update if needed

### Automatic Fixes Applied:
- Updated 3 technology version references
- Resolved 2 path conflicts
- Merged 1 duplicate section
- Removed 1 conflicting instruction

## 📁 Backup Information
**Original file backed up to**:
- `.dev-aid/backups/CLAUDE_original-backup_20260102_143022.md`
- Symlink: `CLAUDE_original-backup.md` → latest backup

## ✨ Next Steps
1. Review flagged items in CLAUDE_custom.md
2. Test the new CLAUDE.md with your AI assistant
3. Customize CLAUDE_custom.md as needed
4. Run `dev-aid validate-context` to verify setup

---
**Status**: ✅ Migration completed successfully
**Review recommended**: Yes (1 item flagged)
```

### 6. Validation Logic Implementation

#### Technology Stack Validator
```bash
validate_tech_stack() {
    local content="$1"
    local project_root="$2"
    local issues=()

    # Detect actual project tech stack
    local actual_stack=$(detect_project_info "$project_root")

    # Extract tech mentions from CLAUDE.md
    local mentioned_stack=$(extract_tech_mentions "$content")

    # Compare and find discrepancies
    # - Outdated versions
    # - Missing technologies
    # - Wrong framework
    # - Deprecated tools

    # Return structured issues array
}
```

#### Instruction Validator
```bash
validate_instructions() {
    local content="$1"
    local project_root="$2"
    local issues=()

    # Check for conflicts with project reality
    # - "Never use X" when project uses X
    # - Invalid file paths
    # - Deprecated patterns

    # Check for internal contradictions
    # - Conflicting rules
    # - Duplicate sections

    # Security checks
    # - Hardcoded secrets
    # - Insecure patterns

    # Return structured issues array
}
```

#### Auto-Resolution Logic
```bash
auto_resolve_issue() {
    local issue_type="$1"
    local issue_data="$2"

    case "$issue_type" in
        "outdated_version")
            # Auto-update to detected version
            return "auto_fixed"
            ;;
        "conflicting_instruction")
            # Remove conflicting instruction, log it
            return "auto_resolved"
            ;;
        "invalid_path")
            # Update to correct path if detectable
            return "auto_fixed"
            ;;
        "deprecated_pattern")
            # Flag for user review
            return "flagged_review"
            ;;
        "duplicate_section")
            # Merge duplicates
            return "auto_resolved"
            ;;
        *)
            # Unknown issue type
            return "flagged_review"
            ;;
    esac
}
```

### 7. Progressive Disclosure Implementation

#### Line Counter
```bash
count_lines() {
    local file="$1"
    wc -l < "$file" | tr -d ' '
}
```

#### Content Splitter
```bash
split_large_context() {
    local merged_file="$1"
    local line_count=$(count_lines "$merged_file")

    if [ "$line_count" -le 500 ]; then
        echo "No split needed: $line_count lines"
        return 0
    fi

    echo "Applying progressive disclosure: $line_count lines"

    # Extract sections
    local core_content=$(extract_core_sections "$merged_file")
    local extended_content=$(extract_extended_sections "$merged_file")
    local custom_content=$(extract_custom_sections "$merged_file")

    # Prioritize content
    local main_content=$(prioritize_for_main "$core_content" "$custom_content")

    # Ensure main_content ≤ 450 lines (leave buffer for headers/footers)
    if [ "$(echo "$main_content" | wc -l)" -gt 450 ]; then
        main_content=$(truncate_to_critical "$main_content" 450)
    fi

    # Create files
    create_main_file "$main_content" ".dev-aid/providers/claude/CLAUDE.md"
    create_extended_file "$extended_content" ".dev-aid/providers/claude/CLAUDE_extended.md"
    create_custom_file "$custom_content" ".dev-aid/providers/claude/CLAUDE_custom.md"

    # Add cross-references
    add_cross_references
}
```

#### Section Prioritization
```bash
prioritize_for_main() {
    local core="$1"
    local custom="$2"

    # Priority order:
    # 1. Role definition (MUST HAVE)
    # 2. Memory bank basics (MUST HAVE)
    # 3. Tech stack summary (5-10 lines) (MUST HAVE)
    # 4. Top 10-15 critical rules (MUST HAVE)
    # 5. Top 5-10 custom instructions (IMPORTANT)

    local result=""
    result+=$(extract_section "$core" "Role" | head -30)
    result+=$(extract_section "$core" "Memory Bank" | head -15)
    result+=$(extract_section "$core" "Tech Stack" | create_summary 10)
    result+=$(extract_section "$core" "Guidelines" | head -200)
    result+=$(extract_section "$custom" "Custom" | head -100)

    echo "$result"
}
```

### 8. User Interaction Flow

#### During Installation
```bash
# In install.sh, when setting up provider symlinks

if [ -f "$PROJECT_ROOT/CLAUDE.md" ] && [ ! -L "$PROJECT_ROOT/CLAUDE.md" ]; then
    echo ""
    echo "📋 Existing CLAUDE.md detected"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Backup
    backup_existing_claude_md "$PROJECT_ROOT/CLAUDE.md"
    echo "✓ Backed up to: CLAUDE_original-backup.md"
    echo ""

    # Validate and merge
    echo "🔍 Validating existing content..."
    validation_result=$(validate_and_merge_claude_md "$PROJECT_ROOT/CLAUDE.md")

    # Show report
    echo "$validation_result"
    echo ""

    # Ask for confirmation
    read -p "Apply these changes? [Y/n]: " confirm
    confirm=${confirm:-Y}

    if [[ "$confirm" =~ ^[Yy] ]]; then
        apply_claude_md_migration "$validation_result"
        echo "✓ CLAUDE.md successfully migrated"
    else
        echo "⚠️  Migration cancelled. Original file restored."
        restore_from_backup
    fi
else
    # No existing file, create normally
    create_default_claude_md
fi
```

#### Validation Report Display
```bash
display_validation_report() {
    local report_file="$1"

    # Show color-coded report
    echo ""
    echo "╔════════════════════════════════════════════════╗"
    echo "║     CLAUDE.md Migration Report                 ║"
    echo "╚════════════════════════════════════════════════╝"
    echo ""

    # Preserved content (green)
    echo -e "\033[32m✅ Successfully Preserved:\033[0m"
    grep -A 10 "## ✅ Successfully Preserved" "$report_file"
    echo ""

    # Issues (yellow/red)
    echo -e "\033[33m⚠️  Issues Detected:\033[0m"
    grep -A 50 "## ⚠️ Issues Detected" "$report_file"
    echo ""

    # Statistics (blue)
    echo -e "\033[34m📊 Statistics:\033[0m"
    grep -A 10 "## 📊 Migration Statistics" "$report_file"
    echo ""

    # Action required (bold)
    echo -e "\033[1m🔍 Action Required:\033[0m"
    grep -A 5 "## 🔍 Action Required" "$report_file"
    echo ""
}
```

### 9. File Structure After Migration

```
project-root/
├── CLAUDE.md (symlink → .dev-aid/providers/claude/CLAUDE.md)
├── CLAUDE_original-backup.md (symlink → latest backup)
│
└── .dev-aid/
    ├── providers/
    │   └── claude/
    │       ├── CLAUDE.md (main file, ≤500 lines)
    │       ├── CLAUDE_extended.md (if needed)
    │       └── CLAUDE_custom.md (if needed)
    │
    └── backups/
        ├── CLAUDE_original-backup_20260102_143022.md
        ├── CLAUDE_original-backup_20260101_091530.md
        └── .latest (tracks most recent backup)
```

### 10. Testing Scenarios

#### Test Case 1: Small Existing File (<200 lines)
- **Input**: Simple CLAUDE.md with basic instructions
- **Expected**: Merge into single file, no split needed
- **Validation**: Should detect and fix outdated tech mentions

#### Test Case 2: Large Existing File (>600 lines)
- **Input**: Comprehensive CLAUDE.md with extensive rules
- **Expected**: Apply progressive disclosure, split into 3 files
- **Validation**: Main file should be ≤450 lines, custom content preserved

#### Test Case 3: Outdated Content
- **Input**: CLAUDE.md mentioning React 16, jQuery, Bower
- **Expected**: Flag outdated mentions, propose updates
- **Validation**: Report should list all outdated items

#### Test Case 4: Conflicting Instructions
- **Input**: "Never use TypeScript" in TypeScript project
- **Expected**: Detect conflict, remove or flag for review
- **Validation**: Conflict should appear in report

#### Test Case 5: Invalid Paths
- **Input**: References to `/old-src/`, `/legacy/`
- **Expected**: Detect invalid paths, update to current structure
- **Validation**: All paths should be validated

#### Test Case 6: No Existing File
- **Input**: Fresh project, no CLAUDE.md
- **Expected**: Create default template normally
- **Validation**: No backup or validation needed

#### Test Case 7: Duplicate Sections
- **Input**: Same guidelines repeated multiple times
- **Expected**: Merge duplicates, keep single version
- **Validation**: Final file should have no duplicates

### 11. Configuration Options

Add to `.dev-aid/config/settings.json`:
```json
{
  "claude_md_initialization": {
    "auto_validate": true,
    "auto_fix_outdated": true,
    "progressive_disclosure_threshold": 500,
    "backup_format": "CLAUDE_original-backup_YYYYMMDD_HHMMSS.md",
    "backup_location": ".dev-aid/backups",
    "validation_strictness": "medium",
    "require_user_approval": true,
    "preserve_comments": true
  }
}
```

### 12. Error Handling

#### Backup Failures
- If backup fails, abort migration
- Never proceed without successful backup
- Log error and inform user

#### Validation Errors
- If validation fails, show partial results
- Allow user to proceed manually
- Provide detailed error logs

#### Split Failures
- If progressive disclosure fails, keep single file
- Warn user about large file size
- Suggest manual splitting

#### Merge Conflicts
- If auto-merge fails, present both versions
- Let user choose manually
- Provide diff view

### 13. Success Criteria

✅ **Must Have**:
- Original content always backed up with clear name
- Validation detects outdated/conflicting content
- Files >500 lines automatically split
- User sees clear migration report
- User can review and approve changes

✅ **Should Have**:
- Auto-fix common issues (outdated versions, invalid paths)
- Smart prioritization in progressive disclosure
- Cross-references between split files
- Diff view for conflicts

✅ **Nice to Have**:
- Interactive validation report (CLI UI)
- Undo/restore functionality
- Migration history tracking
- A/B testing between old and new

## Implementation Phases

### Phase 1: Foundation (Priority 1)
1. Backup mechanism
2. Basic validation (tech stack, paths)
3. Simple merge (append custom content)
4. Report generation

### Phase 2: Intelligence (Priority 2)
5. Advanced validation (conflicts, duplicates)
6. Auto-resolution logic
7. Progressive disclosure
8. User approval flow

### Phase 3: Polish (Priority 3)
9. Enhanced reporting (colors, formatting)
10. Configuration options
11. Error recovery
12. Documentation

### Phase 4: Testing (Priority 4)
13. All test scenarios
14. Edge case handling
15. Performance optimization
16. User feedback integration

## Files to Modify

### Primary Changes
- `.dev-aid/scripts/install.sh` - Add validation and merge logic
- `.dev-aid/scripts/reconfigure.sh` - Add validation for reconfig

### New Files
- `.dev-aid/scripts/lib/claude-md-validator.sh` - Validation logic
- `.dev-aid/scripts/lib/claude-md-merger.sh` - Merge logic
- `.dev-aid/scripts/lib/progressive-disclosure.sh` - Split logic
- `.dev-aid/templates/validation-report.template` - Report template

### Documentation
- `.dev-aid/docs/CLAUDE-MD-MIGRATION.md` - User-facing guide
- Update: `.dev-aid/docs/CONTEXT-SHARING.md` - Add migration info
- Update: `README.md` - Mention smart initialization

## Rollout Plan

### Week 1: Development
- Implement Phase 1 (Foundation)
- Basic testing

### Week 2: Enhancement
- Implement Phase 2 (Intelligence)
- Advanced testing

### Week 3: Polish
- Implement Phase 3 (Polish)
- Edge case testing

### Week 4: Release
- Implement Phase 4 (Testing)
- Documentation
- Beta release

## Success Metrics

- ✅ Zero data loss (100% backup success)
- ✅ High validation accuracy (>95% correct detections)
- ✅ User satisfaction (positive feedback on reports)
- ✅ Performance (migration completes in <5 seconds)
- ✅ Adoption (users approve and use merged files)

---

**Status**: Design Complete - Ready for Implementation
**Next Step**: Begin Phase 1 implementation
