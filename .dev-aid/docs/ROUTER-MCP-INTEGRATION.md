# Dev-AID Router - MCP Integration Guide

## Overview

Dev-AID Router now supports **Model Context Protocol (MCP) integration**, allowing the router to gather context from external tools before generating responses. This makes AI responses significantly more accurate and context-aware.

### What This Means

**Before MCP Integration:**
```
You: "Generate a database migration for user_preferences table"
Router → Claude API → Generic migration code
```

**With MCP Integration:**
```
You: "Generate a database migration for user_preferences table"
Router → Gathers context:
  - PostgreSQL MCP: Gets current schema
  - GitHub MCP: Checks for related issues
  - Code-search MCP: Finds similar migrations
Router → Claude API (with rich context) → Migration matching YOUR schema
```

---

## Architecture

### Components

1. **MCP Client** (`router/mcp_client.py`)
   - Communicates with MCP servers via stdio protocol
   - Executes MCP tools and retrieves results
   - Manages connection lifecycle

2. **MCP Registry** (`router/mcp_registry.py`)
   - Discovers MCP servers from Claude Code and Gemini CLI
   - Maps servers to capabilities (database, github, search, etc.)
   - Manages which MCPs are enabled for router use

3. **Enhanced Context Builder** (`router/context_builder.py`)
   - Gathers context from enabled MCP servers
   - Auto-selects relevant MCPs based on task type
   - Enriches AI prompts with MCP-gathered data

4. **CLI Commands** (`router/cli.py`)
   - `mcp discover` - Scan for available MCP servers
   - `mcp enable <name>` - Enable MCP for router
   - `mcp disable <name>` - Disable MCP
   - `mcp list` - Show all MCPs and their status
   - `mcp sync` - Re-scan and update configuration

### Data Flow

```
User Request
    ↓
Router Executor
    ↓
MCP Registry ← Discovers installed MCPs
    ↓
Context Builder ← Auto-selects relevant MCPs
    ↓
MCP Client Pool ← Queries each MCP server
    ↓          (postgres: schema, github: issues, code-search: code)
Enriched Context
    ↓
AI API Call ← Prompt includes MCP context
    ↓
Enhanced Response
```

---

## Installation & Setup

### Prerequisites

- Dev-AID Router installed (`.dev-aid/orchestration/setup-venv.sh`)
- At least one MCP server installed (Claude Code or Gemini CLI)

### Quick Setup

```bash
# Navigate to your project
cd your-project

# Run MCP setup (interactive)
./.dev-aid/scripts/setup-router-mcp.sh
```

This will:
1. Discover all installed MCP servers
2. Let you choose which to enable
3. Configure automatic context gathering

### Manual Setup

```bash
# Discover available MCPs
./.dev-aid/orchestration/router-cli.sh mcp discover

# Enable specific MCPs
./.dev-aid/orchestration/router-cli.sh mcp enable code-search
./.dev-aid/orchestration/router-cli.sh mcp enable postgres
./.dev-aid/orchestration/router-cli.sh mcp enable github

# Verify configuration
./.dev-aid/orchestration/router-cli.sh mcp list
```

---

## Usage

### Automatic Context Gathering

Once MCPs are enabled, the router **automatically** gathers context based on your request:

```bash
# Database-related request → Auto uses postgres MCP
./router-cli.sh execute "Add email validation to users table" --mode challenger

# GitHub-related request → Auto uses github MCP
./router-cli.sh execute "Fix issue #123 about password reset" --mode challenger

# Code analysis → Auto uses code-search MCP
./router-cli.sh execute "Refactor authentication module" --mode ensemble

# Disable MCP for a specific request
./router-cli.sh execute "What is OAuth2?" --no-mcp
```

### Smart MCP Selection

The router intelligently selects which MCPs to query based on keywords:

| Keywords in Request | MCPs Queried |
|---------------------|--------------|
| database, sql, table, schema, migration | PostgreSQL/MySQL/SQLite MCP |
| github, issue, pr, bug | GitHub MCP |
| code, function, class, refactor | Code-search MCP |
| file, directory, path | Filesystem MCP |
| Any request | Code-search (always included) |

### Example Workflow

**Scenario**: Generate database migration

```bash
# 1. Request
./router-cli.sh execute "Add user_preferences table with JSON column" --mode challenger

# 2. What happens internally:
#    - Router detects: "database" keyword
#    - Queries postgres MCP → Gets current schema
#    - Queries code-search MCP → Finds similar migrations
#    - Enriches prompt with context

# 3. Claude generates migration:
#    - Matching YOUR database schema
#    - Following YOUR migration patterns
#    - Compatible with YOUR PostgreSQL version

# 4. Gemini reviews:
#    - Checks for SQL injection vulnerabilities
#    - Validates constraints and indexes
#    - Suggests improvements

# 5. You receive:
#    - Production-ready migration
#    - Context-aware and project-specific
```

---

## Configuration

### MCP Config File

Location: `~/.dev-aid/orchestration/config/mcp-config.json`

```json
{
  "version": "1.0.0",
  "servers": {
    "code-search": {
      "name": "code-search",
      "enabled": true,
      "capabilities": ["search"],
      "source": "claude"
    },
    "postgres": {
      "name": "postgres",
      "enabled": true,
      "capabilities": ["database"],
      "source": "claude"
    },
    "github": {
      "name": "github",
      "enabled": false,
      "capabilities": ["github"],
      "source": "gemini"
    }
  }
}
```

### Enabling/Disabling MCPs

```bash
# Enable MCP
./router-cli.sh mcp enable postgres
# ✅ Enabled 'postgres' for router use
#    Source: claude
#    Capabilities: database

# Disable MCP
./router-cli.sh mcp disable github
# ✅ Disabled 'github' for router use
#    The server is still installed, just not used by router
```

---

## Supported MCP Servers

### Officially Tested

| MCP Server | Capability | Status | Notes |
|------------|------------|--------|-------|
| code-search | search | ✅ Tested | Dev-AID Local Search |
| postgres | database | ✅ Tested | PostgreSQL schema access |
| github | github | ✅ Tested | Issue/PR search |

### Community MCPs (Should Work)

| MCP Server | Capability | Expected Behavior |
|------------|------------|-------------------|
| mysql | database | Database schema access |
| sqlite | database | Local database queries |
| filesystem | filesystem | Advanced file operations |
| slack | communication | Team notifications |
| linear | project-management | Issue tracking |
| brave-search | search | Web search |

**Note**: Community MCPs have not been tested but should work given they follow MCP protocol specifications.

---

## Managing MCPs

### Adding New MCP Server

**Option 1: Claude Code**
```bash
# Add MCP (example: PostgreSQL)
claude mcp add postgres --scope user -- \
  npx -y @modelcontextprotocol/server-postgres

# Router will auto-discover it
./.dev-aid/orchestration/router-cli.sh mcp sync

# Enable for router
./.dev-aid/orchestration/router-cli.sh mcp enable postgres
```

**Option 2: Gemini CLI**
```bash
# Edit config manually
nano ~/.gemini/mcp.json

# Add server to "mcpServers" section
# Then sync
./.dev-aid/orchestration/router-cli.sh mcp sync
```

### Removing MCP Server

```bash
# Disable in router (keeps server installed)
./router-cli.sh mcp disable postgres

# To fully remove (Claude Code):
claude mcp remove postgres

# To fully remove (Gemini CLI):
# Edit ~/.gemini/mcp.json and remove server entry
```

### Re-scanning After Changes

```bash
# If you add/remove MCPs in Claude Code or Gemini CLI
./router-cli.sh mcp sync

# This will:
# - Re-discover all MCPs
# - Update capability mappings
# - Preserve your enabled/disabled preferences
```

---

## Troubleshooting

### MCPs Not Discovered

**Problem**: `mcp discover` finds no servers

**Solutions**:
1. Check if Claude Code or Gemini CLI is installed:
   ```bash
   claude mcp list  # Should show MCPs
   ```

2. Verify config files exist:
   ```bash
   ls ~/.claude-code/config.json
   ls ~/.gemini/mcp.json
   ```

3. Add an MCP manually and re-scan:
   ```bash
   claude mcp add code-search --scope user -- \
     uv run --directory ~/.local/share/claude-context-local \
     python mcp_server/server.py

   ./router-cli.sh mcp sync
   ```

### MCP Enabled But Not Working

**Problem**: MCP is enabled but router doesn't use it

**Debug**:
1. Check MCP status:
   ```bash
   ./router-cli.sh mcp list
   # Should show "✓ Enabled"
   ```

2. Verify MCP server is running:
   ```bash
   claude mcp list  # Should show "Active"
   ```

3. Check router execution logs:
   ```bash
   # Look for MCP context in logs
   ./router-cli.sh execute "test" --mode solo --verbose
   ```

### Wrong MCP Selected

**Problem**: Router uses wrong MCP for task

**Example**: Database request uses github MCP instead of postgres MCP

**Cause**: Keyword detection may be imperfect

**Solutions**:
1. Use more specific keywords:
   - Instead of: "Fix the data problem"
   - Use: "Fix the database schema for users table"

2. Check capability mappings:
   ```bash
   ./router-cli.sh mcp list
   # Verify capabilities are correct
   ```

### MCP Connection Errors

**Problem**: "Failed to connect to MCP server"

**Solutions**:
1. Restart the MCP server:
   ```bash
   # Claude Code
   claude mcp restart <name>
   ```

2. Check MCP server logs (server-specific)

3. Disable and re-enable:
   ```bash
   ./router-cli.sh mcp disable <name>
   ./router-cli.sh mcp enable <name>
   ```

---

## Best Practices

### 1. Start Small

Don't enable 10 MCPs at once. Start with:
- **code-search** (always useful)
- **One task-specific MCP** (postgres OR github, not both initially)

### 2. Test Each MCP

After enabling an MCP, test it:
```bash
# Enable postgres
./router-cli.sh mcp enable postgres

# Test with database request
./router-cli.sh execute "Describe the users table schema" --mode solo

# Verify it includes database context in response
```

### 3. Use Descriptive Requests

Help the router select the right MCPs:
- ✅ "Generate PostgreSQL migration for users table"
- ❌ "Update the table"

### 4. Monitor Costs

MCP queries add minimal cost (they run locally), but they may increase prompt size:
```bash
./router-cli.sh status
# Check: Today's Activity → Average Cost
```

### 5. Sync Regularly

If you manage MCPs outside the router:
```bash
# Weekly sync
./router-cli.sh mcp sync
```

---

## Performance Considerations

### Context Size

MCP-gathered context increases prompt size:
- **code-search**: +500-2000 tokens (5 code snippets)
- **postgres schema**: +200-1000 tokens (table definitions)
- **github issues**: +300-800 tokens (3 issue summaries)

**Impact**: Slightly higher costs, significantly better accuracy

### Latency

MCP queries add ~100-500ms per server:
- **code-search**: ~200ms (local search)
- **postgres**: ~100ms (schema query)
- **github**: ~300ms (API call)

**Total**: +500-1000ms request time for 3 MCPs

**Trade-off**: Acceptable latency for much better responses

### Optimization

To minimize latency:
1. Only enable MCPs you frequently use
2. Disable MCPs for simple requests
3. Use `--mode solo` for quick responses (less MCP queries)

---

## FAQ

### Q: Will this work with other AI tools?

**A**: The MCP infrastructure is router-specific, but if your AI tool (Claude Code, Gemini CLI, etc.) has MCP support, it can use the same MCP servers you configure here.

### Q: Can I use MCPs without the router?

**A**: Yes! MCPs work directly with Claude Code/Gemini CLI. The router integration just makes MCPs available when using the router's orchestration modes.

### Q: Do MCPs send data to the cloud?

**A**: Most MCPs (like code-search, postgres) run 100% locally. Some (like github, slack) make API calls. Check each MCP's documentation.

### Q: Can I create my own MCP for the router?

**A**: Yes! Create any MCP following the MCP specification, register it with Claude Code/Gemini CLI, then enable it for the router. The router will auto-detect its capabilities based on the name.

### Q: What if two MCPs have the same capability?

**A**: The router uses the first enabled MCP it finds for each capability. Order is undefined, so only enable one MCP per capability.

### Q: Can I force a specific MCP to be used?

**A**: Currently, MCP selection is automatic. Manual MCP selection is planned for a future release.

---

## Roadmap

### Phase 1 (Completed)
- ✅ MCP client implementation
- ✅ MCP registry and discovery
- ✅ CLI commands (discover, enable, disable, list, sync)
- ✅ Interactive setup script

### Phase 2 (Completed)
- ✅ Context builder MCP integration
- ✅ Smart MCP selection based on task type
- ✅ Auto-context gathering

### Phase 3 (Completed)
- ✅ Executor integration with async MCP initialization
- ✅ Full end-to-end MCP context gathering workflow
- ✅ All modes (solo, ensemble, challenger) use MCP context
- ✅ CLI flag for disabling MCP (--no-mcp)

### Phase 4 (Planned)
- ⏳ Manual MCP selection (--mcp flag)
- ⏳ MCP priority configuration
- ⏳ Custom capability mappings
- ⏳ MCP query caching
- ⏳ Parallel MCP queries for performance

---

## Related Documentation

- **[MCP-EXTENSIBILITY.md](./MCP-EXTENSIBILITY.md)** - Using Dev-AID with other MCP servers
- **[HOW-LOCAL-SEARCH-WORKS.md](./HOW-LOCAL-SEARCH-WORKS.md)** - How MCP protocol enables local search
- **[ROUTER-INSTALL.md](../orchestration/ROUTER-INSTALL.md)** - Router installation guide
- **Official MCP Docs**: https://modelcontextprotocol.io/

---

## Contributing

Found a bug or have a feature request? Please file an issue on GitHub.

Want to add support for a new MCP capability? See the capability detection in `router/mcp_registry.py:_infer_capabilities()`.

---

**Last Updated**: 2026-04-08
**Dev-AID Version**: 1.5.1
**MCP Integration Version**: 1.0.0 (Phases 1-3 Complete - Fully Functional)
