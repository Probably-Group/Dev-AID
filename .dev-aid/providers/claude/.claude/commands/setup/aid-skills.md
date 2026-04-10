---
name: aid-skills
description: "List Dev-AID skills and host-project skills installed in this project"
category: setup
author: Dev-AID Team (https://probably.group)
version: 2.0.0
---

# Dev-AID Skills

Show a categorized list of every skill available in this project — both Dev-AID scaffold skills and host-project skills (if any) — with brief descriptions, collision warnings, and the precedence rule.

## Instructions for Claude

### Step 1: Detect host-project skills

Before listing Dev-AID skills, check whether the host project has its own `skills/` directory. Look in these locations (in order):

- `skills/` at the repo root
- `.claude/skills/`
- `docs/skills/`

A host-project skill is any directory containing a `SKILL.md` file within one of these paths. If none of these directories exist, skip the host-project section entirely.

### Step 2: Collect Dev-AID skills

Read the skills registry index if it exists:

```
.dev-aid/skills/registry/skills-index.json
```

If it does not exist, walk the directories:

- **Expert skills** — `.dev-aid/skills/expert/*/SKILL.md`
- **Process skills** — `.dev-aid/skills/process/*/SKILL.md`
- **Core skills** — `.dev-aid/skills/core/*/SKILL.md`

For each skill, extract the `name` and `description` from the SKILL.md frontmatter (between `---` blocks).

### Step 3: Detect name collisions

Compare the directory names of host-project skills against Dev-AID skill directory names. A collision exists when both the host project and Dev-AID have a skill with the same directory name (e.g. the host has `skills/fastapi/SKILL.md` and Dev-AID has `.dev-aid/skills/expert/fastapi/SKILL.md`).

### Step 4: Render output

Use this format (adjust counts to actual values):

```
📚 Skills Overview

## Host Project Skills (N)
(Only shown when the host project has a skills/ directory)
- <skill-name>: <one-line description>
- <skill-name>: <description> ⚠️ name collision with .dev-aid/skills/expert/<same-name>
...

Precedence: host-project skills take priority over Dev-AID skills with the
same name. When both exist, agents should read the host-project copy. The
Dev-AID copy is the upstream default and may be overridden intentionally.

---

## Dev-AID Expert (N)
- <skill-name>: <one-line description>
...

## Dev-AID Process (N)
- <skill-name>: <one-line description>
...

## Dev-AID Core (N)
- <skill-name>: <one-line description>
...

💡 Skills auto-load based on the files you're working with. The session-start
   hook (`skill-activation-conservative.sh`) suggests up to 3 skills per
   session based on file patterns and keywords. To see what's currently
   active, look at the skill suggestions printed at session start.

📖 Architecture: .dev-aid/docs/SKILLS-ARCHITECTURE.md
```

### Step 5: Handle filters

If `$ARGUMENTS` is non-empty, treat it as a filter:
- `host` — only show host-project skills
- `expert`, `process`, or `core` — only show that Dev-AID category
- `collisions` — only show skills with name collisions

### Step 6: Keep it concise

One line per skill, no walls of text. If there are more than 30 skills in a category, group them by sub-category if `skills-index.json` provides one, otherwise show the first 30 alphabetically with a "(+ N more)" footer.

## Precedence rule

When a host-project skill and a Dev-AID skill share the same name:

1. **Agents should use the host-project copy.** The host project's `skills/<name>/SKILL.md` is treated as the authoritative version.
2. **Dev-AID's copy is the upstream default.** It may have been intentionally overridden by the host project — respect that override.
3. **The collision warning exists so users know** both copies exist and can reconcile them (e.g. rename the Dev-AID skill, merge content, or delete the override).

## Common follow-up questions

If the user asks "which skills are loaded right now?", explain that the session-start hook prints suggested skills at the start of each Claude Code session, and that the `auto_load_max_skills` setting in `.dev-aid/config/skill-rules.json` (or the default of 3) caps the number of suggestions per session.
