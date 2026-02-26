# Dev-AID Presets

Stack-specific presets that generate substantive rules, troubleshooting playbooks,
smoke tests, and session recovery plans for target projects.

## Bundled Presets

| Preset | Description |
|--------|-------------|
| `generic` | Minimal scaffolding for any project |
| `python-fastapi` | Python/FastAPI backend with API contracts, database patterns |
| `typescript-node` | TypeScript/Node.js with eslint, vitest, Zod patterns |
| `fullstack` | Backend + frontend with cross-service contracts |
| `kubernetes-gitops` | K8s infrastructure with GitOps, network policies, deployment verification |

## How Presets Work

Presets are Bash scripts that define variables consumed by `setup-dev-aid.sh`.
They are **data, not code** — they set configuration variables that the setup
phases use to generate files.

### Variables a Preset Must Define

| Variable | Purpose |
|----------|---------|
| `preset_name` | Short identifier |
| `preset_description` | One-line description |
| `RULES_FILES` | Newline-delimited `filename\|description` pairs |
| `TECH_STACK` | Markdown table rows for technology stack |
| `CONTEXT_LOADING_TABLE` | Task-to-file mapping for context loading |
| `CONTEXT_GROUPS` | Named file bundles for quick loading |
| `WORKFLOW` | Development workflow instructions |
| `PROJECT_OVERVIEW` | Default project description |
| `WORKSPACE_STRUCTURE` | Directory tree (supports `{{PROJECT_NAME}}`) |
| `TROUBLESHOOTING_SECTIONS` | Symptom/Diagnosis/Fix playbook content |
| `MEMORY_TOPICS` | `filename\|description` pairs for memory bank |
| `COMMANDS` | Newline-delimited slash command filenames |
| `RULES_CONTENT_*` | Substantive content per rules file |
| `SMOKE_SCRIPTS` | `filename\|title\|checks_var` entries (optional) |
| `LINT_LANGUAGES` | Supported lint languages description |

### Rules Content Variable Naming

`RULES_CONTENT_<FILENAME_UPPER>` where hyphens become underscores:
- `api-contracts.md` -> `RULES_CONTENT_API_CONTRACTS`
- `cross-service.md` -> `RULES_CONTENT_CROSS_SERVICE`
- `network-policies.md` -> `RULES_CONTENT_NETWORK_POLICIES`

## Community Presets

Place custom presets in `~/.dev-aid/presets/`. They follow the same format as
bundled presets and are auto-discovered during setup.

### Creating a Community Preset

1. Copy any bundled preset as a starting point:
   ```bash
   mkdir -p ~/.dev-aid/presets
   cp .dev-aid/presets/generic.sh ~/.dev-aid/presets/my-stack.sh
   ```

2. Edit `preset_name`, `preset_description`, and all variables

3. Run `setup-dev-aid.sh` — your preset will appear in the selection menu

### Sharing Presets

Community presets are regular Bash scripts. Share them via:
- Git repositories
- Gists
- Copy into `~/.dev-aid/presets/` on any machine
