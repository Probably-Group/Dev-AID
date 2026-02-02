# Process Skills

**7 process skills** that enforce disciplined workflows — behavioral protocols, not just knowledge.

## What Are Process Skills?

Process skills differ fundamentally from expert skills:

| Aspect | Expert Skills | Process Skills |
|--------|--------------|----------------|
| **Purpose** | Declarative knowledge ("what to know") | Behavioral protocols ("how to work") |
| **Role** | Provide best practices and patterns | Enforce workflow discipline |
| **Loading** | Context-aware (auto-loads on keywords) | Auto-triggers on specific events |
| **Example** | "Use strict mode for TypeScript" | "NO completion claims without test evidence" |

## Key Insight

Process skills adopt methodology patterns from proven development practices (TDD, root cause analysis, staged review) but enhance them with Dev-AID infrastructure:

- **Router Integration**: Challenger mode for cross-model verification
- **Local Search**: FAISS semantic search for pattern matching
- **Security Tools**: Correlation with Trivy/Gitleaks findings
- **Task Tracking**: Integration with Dev-AID task list

## Available Process Skills

### 1. verification-gate (CRITICAL)
**Purpose**: No completion claims without evidence

Prevents false completion claims by requiring actual test/build output before claiming success.

**Key Features**:
- Language-aware verification commands (auto-detects Python/Node/Rust/Go)
- Forbidden phrases detection ("should work", "probably fixed")
- Integration with challenger mode for cross-model verification

**Triggers**: `completion_claim`, "done", "fixed", "implemented", "finished"

### 2. tdd-protocol (HIGH)
**Purpose**: Enforce RED-GREEN-REFACTOR cycle

No production code without a failing test first.

**Key Features**:
- Test templates per language
- FAISS search for similar existing tests
- Configurable enforcement (strict/warning/off)

**Triggers**: `new_feature`, `bug_fix`, `implementation_request`

### 3. systematic-debugging (HIGH)
**Purpose**: Root cause first, fix second

Prevents random fix attempts by enforcing systematic investigation.

**Key Features**:
- Four-phase protocol (Investigation → Pattern Analysis → Hypothesis → Implementation)
- Local search integration for error pattern matching
- Security tool correlation (Trivy/Gitleaks findings)
- 3-strike rule (3+ failed fixes → architectural review)

**Triggers**: `error_message`, `stack_trace`, "bug", "broken", "not working", "fails"

### 4. isolated-development (MEDIUM)
**Purpose**: Git worktree per feature/issue

Creates clean, isolated development environments.

**Key Features**:
- Auto-create worktree from GitHub issue number
- Integration with `dev-aid-resolve-issue`
- Project type detection for setup commands

**Triggers**: `new_feature`, `issue_resolution`, "start work on"

### 5. design-first (MEDIUM)
**Purpose**: Think before coding

Enforces design exploration before implementation.

**Key Features**:
- Deep research integration
- Memory bank persistence for decisions
- YAGNI enforcement
- 2-3 options presentation with trade-offs

**Triggers**: `new_feature`, `architecture_change`, "implement", "add feature"

### 6. staged-review (MEDIUM)
**Purpose**: Two-stage review (spec → quality)

Separates specification compliance from code quality review.

**Key Features**:
- Stage 1: Does code match specification?
- Stage 2: Is code quality acceptable?
- Challenger mode integration
- Security checks via existing tools
- No performative responses rule

**Triggers**: `pr_review`, `code_complete`, "review"

### 7. plan-execution (MEDIUM)
**Purpose**: Batch execution with checkpoints

Executes plans systematically with feedback loops.

**Key Features**:
- 3-task batches with checkpoints
- Cost tracking per batch
- Task list integration
- Blocker protocol (stop, describe, propose solutions, wait)

**Triggers**: `plan_file`, "execute plan", "implement plan"

## Configuration

Process skills are configured in `.dev-aid/config/process-skills.json`:

```json
{
  "version": "1.0.0",
  "enforcement": {
    "verification-gate": { "level": "strict", "autoTrigger": true },
    "tdd-protocol": { "level": "warning", "autoTrigger": false },
    "systematic-debugging": { "level": "warning", "autoTrigger": true },
    "isolated-development": { "level": "off", "autoTrigger": false },
    "design-first": { "level": "warning", "autoTrigger": false },
    "staged-review": { "level": "warning", "autoTrigger": true },
    "plan-execution": { "level": "warning", "autoTrigger": false }
  }
}
```

### Enforcement Levels

| Level | Behavior |
|-------|----------|
| `strict` | Block action until protocol is followed |
| `warning` | Warn but allow proceeding |
| `off` | No enforcement (not recommended for verification-gate) |

### Auto-Trigger

When `autoTrigger: true`, the skill activates automatically on matching events/keywords.
When `autoTrigger: false`, the skill must be explicitly invoked.

## Directory Structure

```
.dev-aid/skills/process/
├── README.md                      # This file
├── verification-gate/
│   ├── SKILL.md                   # ~300 tokens
│   └── references/
│       └── language-commands.md   # Per-language verification commands
├── tdd-protocol/
│   ├── SKILL.md                   # ~400 tokens
│   └── references/
│       ├── language-patterns.md
│       └── test-templates.md
├── systematic-debugging/
│   ├── SKILL.md                   # ~450 tokens
│   └── references/
│       └── investigation-patterns.md
├── isolated-development/
│   ├── SKILL.md                   # ~300 tokens
│   └── references/
│       └── project-setup-commands.md
├── design-first/
│   ├── SKILL.md                   # ~350 tokens
│   └── references/
│       └── design-templates.md
├── staged-review/
│   ├── SKILL.md                   # ~400 tokens
│   └── references/
│       └── review-checklists.md
└── plan-execution/
    ├── SKILL.md                   # ~350 tokens
    └── references/
        └── checkpoint-protocols.md
```

## Key Differences from Superpowers

| Aspect | Superpowers | Dev-AID Process Skills |
|--------|-------------|------------------------|
| Verification commands | Generic | Language-aware auto-detection |
| Model usage | Single model | Multi-model via router |
| Search capability | None | FAISS local semantic search |
| Security integration | None | Gitleaks, Trivy, Opengrep |
| Cost tracking | None | Per-workflow analytics |
| Issue integration | Manual | Auto-worktree from GitHub issue |
| Design decisions | Ephemeral | Persisted in memory bank |
| Review | Single-stage | Two-stage + challenger mode |

## Usage

Process skills activate automatically based on triggers when `autoTrigger: true`.

For manual invocation:
```
/verification-gate
/tdd-protocol
/systematic-debugging
/isolated-development
/design-first
/staged-review
/plan-execution
```

## Integration with Dev-AID

Process skills integrate with existing Dev-AID infrastructure:

- **Router**: Use challenger mode for verification
- **Local Search**: Find similar patterns/tests
- **Security Tools**: Correlate findings
- **Task List**: Track progress
- **Memory Bank**: Persist decisions
- **Core Skills**: Connect to test-runner, code-reviewer

## Metrics

Track process skill effectiveness:

- **verification-gate**: False completion rate (target: <5%)
- **tdd-protocol**: Tests before code percentage
- **systematic-debugging**: Fix attempts per bug (target: <3)
- **isolated-development**: Worktree usage rate
- **design-first**: Options presented before coding
- **staged-review**: Issues caught per stage
- **plan-execution**: Batch completion rate
