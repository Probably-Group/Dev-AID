# Dev-AID Scaffold — Scope Marker

**This directory (`.dev-aid/`) is the Dev-AID development addon. It is NOT
part of the host project's source.**

## What this means for AI assistants

When you are invoked in a session running inside a host project that has
Dev-AID installed, the layout looks like this:

```
<host-project-root>/      ← the actual product the user is building
├── src/                  ← host project source (edit this for host tasks)
├── tests/                ← host project tests
├── ...                   ← other host project files
└── .dev-aid/             ← Dev-AID scaffold (THIS DIRECTORY — managed)
    ├── HOST_PROJECT.md   ← you are reading this file
    ├── orchestration/
    ├── skills/
    └── ...
```

### Default scope

- **Edits target the host project**, not Dev-AID.
- The user's "implement feature X" / "fix bug Y" / "refactor Z" requests refer
  to the host project's code at the parent directory, not to anything under
  `.dev-aid/`.
- Code-writing agents (test-gen, ci-fix, conflict-resolve, debt, etc.) should
  default to host-project files.

### When it IS appropriate to edit `.dev-aid/`

Only when the user has **explicitly** asked you to:

- Contribute upstream to Dev-AID itself ("fix this bug in the Dev-AID router",
  "add a new skill to Dev-AID", "improve the orchestration module")
- Customize Dev-AID configuration for this project (`.dev-aid/config/`,
  `.dev-aid/memory-bank/` once the user has signaled they want to populate it)
- Update memory-bank files after the user has flagged them as customized

If a user request is ambiguous and the closest file match is under `.dev-aid/`,
**ask first**: "Did you mean to edit the Dev-AID scaffold file at
`.dev-aid/...`, or the host project file at `src/...`?"

### Why this marker exists

Without an explicit scope signal, AI assistants pattern-match on file
contents and can silently start editing scaffold files when the user wanted
host-project files. The result: the user gets changes to a managed scaffold
they shouldn't be modifying, and the host project doesn't get the change at
all. This file (and the matching `HOST PROJECT BELOW` divider in CLAUDE.md)
exists so that scope is unambiguous.

### Memory-bank files

`.dev-aid/memory-bank/*.md` files ship with generic Dev-AID defaults. Until
the user explicitly customizes them for their project, treat them as soft
guidance, not as binding host-project conventions. (See issue #146 for the
matching marker proposal.)

---

*Maintained by Dev-AID. Do not delete — the scope check in agent prompts and
the SessionStart hook depend on this file being present.*
