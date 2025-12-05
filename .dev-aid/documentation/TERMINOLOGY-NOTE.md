# Dev-AID Terminology: Skills vs AI Agents

## Important Clarification

**Dev-AID uses the term "Skills"** - not "AI Agents" or "Agents"

### Why This Matters

Some external projects and repositories refer to similar functionality as "AI Agents" or "Agents". This can cause confusion when discussing Dev-AID.

**Dev-AID Terminology**:
- ✅ **Skills** - Domain expertise loaded automatically or manually
- ✅ **Expert Skills** - Specialized knowledge (e.g., `devsecops-expert`, `api-expert`)
- ✅ **Core Skills** - Always-loaded foundational skills
- ✅ **Slash Commands** - User-invokable workflow commands (e.g., `/dev-aid-audit`)

**External/Incorrect Terminology** (Do NOT use for Dev-AID):
- ❌ "AI Agents" - Inaccurate terminology sometimes used by external projects
- ❌ "Agents" - Ambiguous, could refer to many things
- ❌ "Prompts" - Too generic, doesn't capture the skill injection system

### Background

Dev-AID previously experimented with importing "agents" from external repositories:
- `claude-code-infrastructure-showcase` by diet103
- `claude-code-tresor` by Alireza Rezvani
- `claude-code-skill-factory` by Alireza Rezvani

These external projects used "agent" terminology. Dev-AID has since:
1. **Deprecated the agent approach** (weaker than skills)
2. **Converted unique agents to skills** using the Dev-AID template
3. **Standardized on "Skills" terminology** throughout the system

### Key Differences: Skills vs External "Agents"

| Aspect | Dev-AID Skills | External "Agents" |
|--------|----------------|-------------------|
| **Terminology** | Skills | Agents |
| **Structure** | SKILL.md + references/ | Single .md file |
| **Anti-Hallucination** | Mandatory (Section 0) | Often missing |
| **Auto-Loading** | Yes (skills-index.json) | Manual invocation only |
| **Cross-Provider** | Yes (Claude, Gemini, etc.) | Usually Claude-only |
| **File Limit** | 500 lines (enforced) | No limit |
| **Quality Control** | 7-section template | Varies |

### When Communicating About Dev-AID

**Correct**:
- "Dev-AID skills provide domain expertise"
- "The `devsecops-expert` skill auto-loads for security tasks"
- "Create a new skill using the Dev-AID template"

**Incorrect**:
- "Dev-AID agents provide domain expertise" ❌
- "The `devsecops-expert` agent auto-loads" ❌
- "Create a new AI agent" ❌

### Historical Note

If you encounter references to "agents" in Dev-AID documentation or code, these are legacy artifacts from the experimental phase (commits around `3c019e9`) and should be updated to "skills".

### External Projects Using "Agent" Terminology

These projects have valuable content but use different terminology:
- [claude-code-infrastructure-showcase](https://github.com/diet103/claude-code-infrastructure-showcase)
- [claude-code-tresor](https://github.com/alirezarezvani/claude-code-tresor)
- [claude-code-skill-factory](https://github.com/alirezarezvani/claude-code-skill-factory)

When adapting content from these sources, always:
1. Convert "agent" terminology to "skill"
2. Apply the Dev-AID skill template
3. Add anti-hallucination protocol (Section 0)
4. Register in skills-index.json
5. Follow the 500-line limit with references/ extraction

---

**Last Updated**: 2025-12-05
**Applies To**: All Dev-AID documentation and communication
