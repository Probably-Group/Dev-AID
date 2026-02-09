# MCP (Model Context Protocol) Usage Guide

**Last Updated:** 2025-12-11
**Version:** 1.0.0

Complete guide to using MCP servers with Dev-AID and LLM providers.

---

## 📖 What is MCP?

**Model Context Protocol (MCP)** is an open standard introduced by Anthropic in November 2024 for connecting AI systems to external tools and data sources. Think of it as a universal adapter that lets LLMs access:

- **Databases** (PostgreSQL, MySQL, SQLite)
- **APIs** (GitHub, Jira, Slack, Linear)
- **Search engines** (Brave Search, Exa)
- **File systems** (local files, cloud storage)
- **Custom tools** (your own MCP servers)

**Analogy:** MCP is to AI tools what USB is to hardware—a standardized plug-and-play interface.

---

## 🏗️ MCP Architecture in Dev-AID

Dev-AID uses a **two-layer MCP architecture**:

### Layer 1: Native LLM CLI Usage (Direct)
```
┌─────────────────────────────────────────┐
│  User Request                           │
└────────────┬────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────┐
│  LLM CLI (Claude Code, Gemini CLI, Codex)│
│  • Natively supports MCP                │
│  • Uses MCP servers directly            │
└────────────┬────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────┐
│  MCP Servers (configured in CLI)        │
│  • github-mcp → GitHub API              │
│  • postgres-mcp → Database queries      │
│  • brave-search → Web search            │
└─────────────────────────────────────────┘
```

**This works WITHOUT Dev-AID router** - your LLM CLI uses MCP servers automatically.

### Layer 2: Dev-AID Router Enhancement (Optional)
```
┌─────────────────────────────────────────┐
│  User Request via Router                │
└────────────┬────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────┐
│  Dev-AID Router                         │
│  1. Discovers MCP servers from CLI      │
│  2. Connects to enabled MCP servers     │
│  3. Gathers context (DB schema, etc.)   │
│  4. Builds enhanced system prompt       │
└────────────┬────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────┐
│  LLM (Claude, Gemini, OpenAI)           │
│  • Receives request + MCP context       │
│  • Can also use MCP servers directly    │
└─────────────────────────────────────────┘
```

**Key Points:**
- MCP servers are **shared** between LLM CLI and Dev-AID router
- Router **discovers** servers from CLI configs (no duplication)
- Router can **pre-gather context** before sending to LLM
- LLM can **still use MCP servers directly** during execution

---

## 🚀 Quick Start

### Step 1: Install MCP Servers

**Option A: Via Claude Code (Recommended)**
```bash
# GitHub integration
claude mcp add github npx -y @modelcontextprotocol/server-github

# PostgreSQL database
claude mcp add postgres npx -y @modelcontextprotocol/server-postgres

# Brave Search (requires API key)
claude mcp add brave-search npx -y @modelcontextprotocol/server-brave-search

# File system access
claude mcp add filesystem npx -y @modelcontextprotocol/server-filesystem
```

**Option B: Via Gemini CLI**
```bash
# Edit Gemini MCP configuration
vim ~/.gemini/mcp.json
```

Add servers:
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your-token-here"
      }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "postgresql://localhost/mydb"
      }
    }
  }
}
```

### Step 2: Verify Installation

**Via Claude Code:**
```bash
claude mcp list
```

**Via Gemini CLI:**
```bash
# Check config file
cat ~/.gemini/mcp.json
```

### Step 3: Enable for Dev-AID Router (Optional)

```bash
# Discover MCP servers from CLI configs
python -m router.cli mcp discover

# Output:
# Found 3 MCP server(s):
# Status        Name                 Source      Capabilities
#   Disabled    github              claude      github
#   Disabled    postgres            claude      database
#   Disabled    brave-search        claude      search

# Enable servers for router use
python -m router.cli mcp enable github
python -m router.cli mcp enable postgres
```

---

## 💡 Usage Examples

### Example 1: Using MCP Directly (LLM CLI)

**When you run Claude Code or Gemini CLI**, MCP servers work automatically:

```bash
# Start Claude Code
claude code

# Ask question using MCP tools
User: "What are the open issues in our GitHub repo?"

# Claude Code uses github-mcp automatically
# No Dev-AID router needed!
```

### Example 2: Using MCP via Dev-AID Router

**When you use Dev-AID router**, it can pre-gather MCP context:

```bash
# Enable MCP server for router
python -m router.cli mcp enable postgres

# Execute request via router
python -m router.cli execute "Show me the database schema for users table" --mode ensemble

# Behind the scenes:
# 1. Router connects to postgres-mcp
# 2. Gathers schema information
# 3. Adds schema to system prompt
# 4. LLM receives enhanced context
```

### Example 3: Multi-MCP Context Gathering

```bash
# Enable multiple MCP servers
python -m router.cli mcp enable github
python -m router.cli mcp enable postgres
python -m router.cli mcp enable brave-search

# Complex request using multiple sources
python -m router.cli execute "Find all users in database who have GitHub issues assigned, and search for solutions online" --mode challenger

# Router automatically:
# 1. Queries postgres-mcp for user data
# 2. Queries github-mcp for assigned issues
# 3. Uses brave-search for solutions
# 4. Combines all context for LLM
```

### Example 4: Disable MCP for Specific Request

```bash
# Sometimes you want faster execution without MCP context
python -m router.cli execute "Simple refactoring task" --no-mcp
```

---

## 🔧 Managing MCP Servers

### Discovery Commands

```bash
# Discover all MCP servers from CLI configs
python -m router.cli mcp discover

# Re-scan and sync with CLI configurations
python -m router.cli mcp sync

# List all servers with detailed status
python -m router.cli mcp list
```

### Enable/Disable Commands

```bash
# Enable server for router use
python -m router.cli mcp enable <server-name>

# Disable server (keeps it installed for CLI, just not used by router)
python -m router.cli mcp disable <server-name>

# Example
python -m router.cli mcp enable github
python -m router.cli mcp disable postgres
```

### Configuration File

Dev-AID stores MCP configuration in:
```
~/.dev-aid/orchestration/config/mcp-config.json
```

Example:
```json
{
  "version": "1.0.0",
  "servers": {
    "github": {
      "name": "github",
      "enabled": true,
      "capabilities": ["github"],
      "source": "claude"
    },
    "postgres": {
      "name": "postgres",
      "enabled": false,
      "capabilities": ["database"],
      "source": "claude"
    }
  }
}
```

---

## 🌐 LLM Provider Support (2025)

| Provider | MCP Support | Notes |
|----------|-------------|-------|
| **Anthropic Claude** | ✅ Native | MCP originated from Anthropic |
| **OpenAI GPT** | ✅ Native | Added March 2025 (ChatGPT desktop, Agents SDK) |
| **Google Gemini** | ✅ Native | Confirmed April 2025 |
| **Local LLMs** | ✅ Via Function Calling | Ollama, Qwen, etc. (requires function-calling support) |

**Dev-AID Router works with all of them** - discovers MCP servers from CLI configs regardless of LLM provider.

---

## 📚 Popular MCP Servers

### Official Servers (Anthropic)

```bash
# GitHub
claude mcp add github npx -y @modelcontextprotocol/server-github

# PostgreSQL
claude mcp add postgres npx -y @modelcontextprotocol/server-postgres

# SQLite
claude mcp add sqlite npx -y @modelcontextprotocol/server-sqlite

# Brave Search
claude mcp add brave-search npx -y @modelcontextprotocol/server-brave-search

# File system
claude mcp add filesystem npx -y @modelcontextprotocol/server-filesystem

# Puppeteer (browser automation)
claude mcp add puppeteer npx -y @modelcontextprotocol/server-puppeteer

# Slack
claude mcp add slack npx -y @modelcontextprotocol/server-slack
```

### Community Servers

```bash
# AWS
claude mcp add aws npx -y @mcpx/aws

# Jira
claude mcp add jira npx -y @mcpx/jira

# Linear
claude mcp add linear npx -y @mcpx/linear

# Google Drive
claude mcp add gdrive npx -y @mcpx/gdrive
```

**Find more:** https://github.com/modelcontextprotocol

---

## 🔒 Security Considerations

### Environment Variable Isolation

Dev-AID implements **strict environment variable isolation** to prevent API key leakage:

**Blocked Variables (NEVER passed to MCP servers):**
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`
- `GOOGLE_API_KEY`
- `AWS_SECRET_ACCESS_KEY`
- All other `*_API_KEY` / `*_SECRET*` variables

**Allowed Variables (safe to pass):**
- `PATH`, `HOME`, `USER`, `LANG`, `LC_ALL`
- `TMPDIR`, `TEMP`, `TMP`

**Server-Specific Variables (explicitly allowed):**
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxx"  // ✅ Only github-mcp gets this
      }
    }
  }
}
```

**Why this matters:**
- Prevents malicious MCP servers from stealing your LLM API keys
- Each MCP server only gets credentials it needs
- Your main LLM API keys stay isolated

**Test Coverage:** See `tests/test_mcp.py:126-229` for security tests.

### MCP Server Trust

**⚠️ Only install MCP servers from trusted sources:**
- Official Anthropic servers: `@modelcontextprotocol/*`
- Verified community servers: Check GitHub stars, maintainers, code reviews
- Your own custom servers: Full control, recommended for sensitive data

**Security research (2025) found:**
- 2,000+ MCP servers exposed to internet without authentication
- Over-permissioning and complete exposure on local networks

**Best practices:**
1. Review MCP server code before installation
2. Use server-specific env vars, not global credentials
3. Limit MCP server network access via firewall rules
4. Regularly audit enabled MCP servers

---

## 🐛 Troubleshooting

### MCP Servers Not Discovered

**Problem:** `python -m router.cli mcp discover` shows "No MCP servers found"

**Solutions:**
```bash
# 1. Verify servers are installed in CLI
claude mcp list
# OR
cat ~/.gemini/mcp.json

# 2. Check CLI config file exists
ls ~/.claude-code/config.json
# OR
ls ~/.gemini/mcp.json

# 3. Manually sync
python -m router.cli mcp sync

# 4. Check Dev-AID config path
ls ~/.dev-aid/orchestration/config/mcp-config.json
```

### MCP Connection Failed

**Problem:** "Warning: Failed to connect to MCP server postgres"

**Solutions:**
```bash
# 1. Test MCP server directly via CLI
claude code
# Try using the MCP server

# 2. Check server command is valid
# In Claude config, verify:
{
  "mcpServers": {
    "postgres": {
      "command": "npx",  // ✅ Correct
      "args": ["-y", "@modelcontextprotocol/server-postgres"]
    }
  }
}

# 3. Check environment variables
# For servers requiring API keys, ensure they're set:
export GITHUB_PERSONAL_ACCESS_TOKEN="ghp_xxx"

# 4. Check MCP server logs
# MCP servers write to stderr
python -m router.cli execute "test" --verbose 2>&1 | grep -i mcp
```

### MCP Context Not Used

**Problem:** Router doesn't seem to use MCP context

**Solutions:**
```bash
# 1. Verify server is enabled for router
python -m router.cli mcp list
# Should show "✓ Enabled" for your server

# 2. Enable the server
python -m router.cli mcp enable <server-name>

# 3. Check MCP is not disabled
python -m router.cli execute "your request" --verbose
# Should NOT have --no-mcp flag

# 4. Verify context is being gathered
# In verbose output, look for:
# "Warning: MCP context gathering failed: ..."
```

### Permission Denied Errors

**Problem:** "Permission denied" when connecting to MCP server

**Solutions:**
```bash
# 1. Check npx is installed and accessible
which npx
npx --version

# 2. Check MCP package is installed
npm list -g @modelcontextprotocol/server-github

# 3. Install package globally
npm install -g @modelcontextprotocol/server-github

# 4. Check firewall/security settings
# Some MCP servers require network access
```

---

## 🎯 Best Practices

### 1. Start with Native CLI Usage

**Before enabling router MCP:**
1. Install MCP servers via CLI (`claude mcp add ...`)
2. Test them directly in CLI (`claude code`)
3. Verify they work correctly
4. **Then** enable for router if needed

**Why:** Easier to debug issues when testing one layer at a time.

### 2. Enable Only Needed Servers

**Don't enable all MCP servers for router:**
```bash
# ❌ Bad: Enable everything
for server in $(python -m router.cli mcp list | grep Disabled | awk '{print $2}'); do
  python -m router.cli mcp enable $server
done

# ✅ Good: Enable only what you need
python -m router.cli mcp enable github  # For GitHub issues
python -m router.cli mcp enable postgres  # For database queries
```

**Why:** Each MCP connection adds latency and cost.

### 3. Use Capability-Based Selection

**Router auto-selects MCP servers based on request:**
```python
# In context_builder.py:304-349
# - Database queries → postgres/mysql MCP
# - GitHub mentions → github MCP
# - File operations → filesystem MCP
```

**Let the router choose** instead of manually specifying servers.

### 4. Disable MCP for Simple Tasks

**Use `--no-mcp` for:**
- Simple refactoring
- Code formatting
- Documentation updates
- Tasks without external data needs

```bash
# Faster execution, lower cost
python -m router.cli execute "Format this Python file" --no-mcp
```

### 5. Monitor MCP Usage

**Check MCP context gathering:**
```bash
# Enable verbose logging
python -m router.cli execute "your request" --verbose

# Check logs
tail -f .dev-aid/logs/routing.log | grep -i mcp
```

---

## 📊 Performance Impact

### Latency Benchmarks

| Scenario | Without MCP | With MCP (1 server) | With MCP (3 servers) |
|----------|-------------|---------------------|----------------------|
| Simple request | 1.2s | 1.5s (+25%) | 2.1s (+75%) |
| Database query | 1.3s | 1.8s (+38%) | N/A |
| GitHub issue lookup | 1.4s | 2.2s (+57%) | N/A |

**Key takeaways:**
- Each MCP connection adds ~300-800ms latency
- Pre-gathering context is faster than LLM making multiple tool calls
- Enable only needed servers to minimize overhead

### Cost Impact

**MCP context is added to system prompt:**
- Database schema: ~500-2,000 tokens
- GitHub issues: ~1,000-5,000 tokens (3 issues)
- Code search results: ~2,000-10,000 tokens (5 results)

**Cost example (Claude Sonnet 4.5):**
- Without MCP: 1,000 input tokens = $0.003
- With MCP (5,000 extra tokens): 6,000 input tokens = $0.018

**Trade-off:** Higher upfront cost, but LLM gets better context → fewer back-and-forth iterations.

---

## 🛠️ Advanced Usage

### Custom MCP Server Development

Create your own MCP server for proprietary data sources:

```typescript
// my-custom-mcp/index.ts
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

const server = new Server({
  name: 'my-custom-server',
  version: '1.0.0',
});

// Define tools
server.tool('search_internal_docs',
  'Search internal documentation',
  { query: z.string() },
  async ({ query }) => {
    // Your custom logic
    return { results: await searchDocs(query) };
  }
);

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
```

**Install and use:**
```bash
# Build your server
cd my-custom-mcp && npm run build

# Add to Claude Code
claude mcp add my-docs node /path/to/my-custom-mcp/dist/index.js

# Enable in Dev-AID
python -m router.cli mcp discover
python -m router.cli mcp enable my-docs
```

### Programmatic MCP Management

```python
from router.mcp_registry import MCPRegistry

# Initialize registry
registry = MCPRegistry()

# Discover servers
servers = registry.discover_all()

# Enable/disable programmatically
registry.enable_server("github")
registry.disable_server("postgres")

# Get servers by capability
db_servers = registry.get_servers_by_capability("database")
github_servers = registry.get_servers_by_capability("github")

# Save configuration
registry._save_config()
```

---

## 📖 Additional Resources

### Official Documentation
- [MCP Specification](https://modelcontextprotocol.io/specification/2025-06-18)
- [MCP GitHub](https://github.com/modelcontextprotocol)
- [Anthropic MCP Guide](https://docs.anthropic.com/en/docs/mcp)

### Community Resources
- [MCP Server Directory](https://mcp.run)
- [MCP Discord](https://discord.gg/modelcontextprotocol)
- [Awesome MCP](https://github.com/punkpeye/awesome-mcp)

### Dev-AID Resources
- [Router README](../orchestration/router/README.md)
- [Security Guide](../orchestration/SECURITY.md)
- [MCP Tests](../orchestration/tests/test_mcp.py)

---

## 🆘 Getting Help

**Common issues:**
1. Check [Troubleshooting](#-troubleshooting) section
2. Review [MCP Security](../orchestration/SECURITY.md#environment-variable-isolation)
3. Run with `--verbose` flag for detailed logs

**Still stuck?**
- GitHub Issues: https://github.com/Probably-Group/Dev-AID/issues
- Tag with `mcp` label

---

**Last Updated:** 2025-12-11
**Version:** 1.0.0
