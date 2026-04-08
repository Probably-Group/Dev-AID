---
name: aid-skills
description: "List Dev-AID skills installed in this project"
category: setup
author: Dev-AID Team (https://probably.group)
version: 1.0.0
---

# Dev-AID Skills

Show a categorized list of every Dev-AID skill installed in this project, with brief descriptions and pointers to the activation rules.

## Instructions for Claude

1. Read the skills registry index to determine the canonical skill list:

   ```
   .dev-aid/skills/registry/skills-index.json
   ```

   If the file does not exist, fall back to walking the directories below.

2. List the contents of each category:

   - **Expert skills** — `.dev-aid/skills/expert/*/SKILL.md`
   - **Process skills** — `.dev-aid/skills/process/*/SKILL.md`
   - **Core skills** — `.dev-aid/skills/core/*/SKILL.md`

3. For each skill, extract the `name` and `description` from the SKILL.md frontmatter (the lines between the leading `---` blocks).

4. Render output in this shape (use the actual counts you find):

   ```
   📚 Dev-AID Skills (74 expert + 8 process + 5 core = 87 total)

   ## Expert (74)
   - <skill-name>: <one-line description>
   ...

   ## Process (8)
   - <skill-name>: <one-line description>
   ...

   ## Core (5)
   - <skill-name>: <one-line description>
   ...

   💡 Skills auto-load based on the files you're working with. The session-start
      hook (`skill-activation-conservative.sh`) suggests up to 3 skills per
      session based on file patterns and keywords. To see what's currently
      active, look at the skill suggestions printed at session start.

   📖 Architecture: .dev-aid/docs/SKILLS-ARCHITECTURE.md
   ```

5. If `$ARGUMENTS` is non-empty, treat it as a category filter (`expert`, `process`, or `core`) and only list that category.

6. Keep the output concise — one line per skill, no walls of text. If there are more than 30 skills in a category, group them by sub-category if `skills-index.json` provides one, otherwise show the first 30 alphabetically with a "(+ N more)" footer.

## Common follow-up questions

If the user asks "which skills are loaded right now?", explain that the session-start hook prints suggested skills at the start of each Claude Code session, and that the `auto_load_max_skills` setting in `.dev-aid/config/skill-rules.json` (or the default of 3) caps the number of suggestions per session.
