---
name: dev-aid-prd
description: "Generate, validate, or reverse-engineer a Product Requirements Document (PRD)"
category: productivity
author: Dev-AID Team (https://probably.group)
version: 1.0.0
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(ls:*), Bash(wc:*), Bash(git:log)
---

# PRD Generator

**Arguments:** $ARGUMENTS

## Protocol

1. **Load the skill definition:**
   Read `.dev-aid/skills/expert/prd-generator/SKILL.md` and follow all instructions.

2. **Determine mode from arguments or auto-detect:**
   - `--build` → Mode 1 (Interactive Builder)
   - `--validate` → Mode 2 (Validator)
   - `--reverse-engineer` → Mode 3 (Reverse-Engineer)
   - No flag → auto-detect using the decision tree in SKILL.md Section 1.2:
     - Check if `PRD.md` exists at repo root
     - Check if code files exist (src/, lib/, app/, *.py, *.ts, etc.)
     - Follow the decision tree to select the appropriate mode

3. **Execute the selected mode:**

   **Mode 1 (Interactive Builder):**
   - Walk through the 7-step question flow from SKILL.md Section 2.1
   - Use the template from `.dev-aid/skills/expert/prd-generator/assets/prd-template.md`
   - Reference writing guidance from `.dev-aid/skills/expert/prd-generator/references/section-guidance.md`
   - Write output to `PRD.md` at repo root

   **Mode 2 (Validator):**
   - Read existing `PRD.md`
   - Score using the rubric from `.dev-aid/skills/expert/prd-generator/references/prd-completeness-checklist.md`
   - Format report using `.dev-aid/skills/expert/prd-generator/assets/validation-report-template.md`
   - Display inline with grade and recommendations

   **Mode 3 (Reverse-Engineer):**
   - Scan codebase using patterns from `.dev-aid/skills/expert/prd-generator/references/reverse-engineer-patterns.md`
   - Add `<!-- confidence: LEVEL -->` tags per section
   - Mark inferred content with `[NEEDS REVIEW]`
   - Write draft to `PRD.md` at repo root

4. **After completion:**
   - Print the output file path
   - Suggest next steps (validate if built, iterate if validated, review if reverse-engineered)
