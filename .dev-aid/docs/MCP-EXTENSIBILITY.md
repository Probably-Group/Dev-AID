# MCP Extensibility - Using Multiple MCP Servers with Dev-AID

## TL;DR

✅ **Yes!** You can use Dev-AID alongside ANY other MCP servers
✅ **Automatic**: The AI sees all MCP servers and uses them intelligently
✅ **No conflicts**: Dev-AID only adds one server (`code-search`)
✅ **Works together**: Multiple MCP servers enhance each other

---

## What Are MCP Servers?

**Model Context Protocol (MCP)** is an open standard (created by Anthropic) that lets AI tools connect to external data sources and tools.

Think of MCP servers like **browser extensions for AI**:
- Each server adds specific capabilities
- You can have many at once
- The AI automatically knows which to use
- They work together seamlessly

---

## Dev-AID's MCP Philosophy

**Dev-AID is MCP-friendly, not MCP-exclusive.**

We provide ONE MCP server:
- **Name**: `code-search`
- **Purpose**: Local semantic code search (Dev-AID Local Search)
- **Scope**: Your codebase only

**We don't:**
- ❌ Interfere with other MCP servers
- ❌ Require exclusive use
- ❌ Manage other MCP servers for you

**We do:**
- ✅ Play nice with existing MCP configurations
- ✅ Provide clear instructions if config exists
- ✅ Use additive installation (Claude Code)
- ✅ Respect existing servers (Gemini CLI)

---

## Popular MCP Servers You Might Want

### 🔧 Development Tools

**GitHub MCP** ([official](https://github.com/modelcontextprotocol/servers))
- Manage repos, PRs, issues
- Search code across GitHub
- Create releases, manage workflows

**Git MCP**
- Local git operations
- Branch management, commits
- History analysis

**Filesystem MCP**
- Advanced file operations
- Directory traversal
- File watching

### 💾 Database Access

**PostgreSQL MCP**
- Query databases
- Schema exploration
- Data analysis

**SQLite MCP**
- Local database operations
- Business intelligence
- Embedded database management

**Supabase MCP**
- Cloud database integration
- Real-time subscriptions
- Auth and storage

### 🔗 Team Collaboration

**Slack MCP** ([korotovsky/slack-mcp-server](https://github.com/korotovsky/slack-mcp-server))
- Send messages to channels
- Read DMs and group chats
- Monitor notifications

**Linear MCP**
- Issue tracking
- Project management
- Sprint planning

**Jira MCP**
- Task management
- Workflow automation

### 📚 Knowledge & Search

**Brave Search MCP**
- Privacy-focused web search
- Real-time information
- No tracking

**EXA Search MCP**
- Semantic web search
- Academic papers
- Technical documentation

**Memory MCP**
- Persistent context
- Cross-session knowledge
- Personal knowledge base

### 🌐 APIs & Services

**Puppeteer MCP**
- Browser automation
- Web scraping
- E2E testing

**AWS MCP**
- Cloud resource management
- Deployment automation

**Docker MCP**
- Container management
- Image operations

---

## How Multiple MCP Servers Work Together

### Example Scenario

You have installed:
- Dev-AID Local Search (`code-search`)
- GitHub MCP (`github`)
- PostgreSQL MCP (`postgres`)
- Slack MCP (`slack`)

**You ask**: "Find the authentication function, check if there's a GitHub issue about password reset, query how many users have reset passwords this month, and notify the team in Slack"

**What happens**:

```
1. AI analyzes request → Needs 4 different tools

2. Uses code-search MCP (Dev-AID):
   → Searches your local codebase
   → Finds: src/auth/reset_password.py

3. Uses github MCP:
   → Searches GitHub issues
   → Finds: Issue #453 "Password reset security concern"

4. Uses postgres MCP:
   → Queries: SELECT COUNT(*) FROM password_resets
              WHERE reset_at >= NOW() - INTERVAL '1 month'
   → Result: 1,247 resets

5. Uses slack MCP:
   → Sends message to #engineering channel
   → "Password reset analysis complete: 1,247 resets this month.
      Related issue: #453"

6. AI presents unified response to you
```

**Key insight**: The AI orchestrates ALL tools automatically. You just ask naturally.

---

## Installing Additional MCP Servers

### For Claude Code (Additive - Safe)

Claude Code uses `claude mcp add` which is **additive** (won't overwrite):

```bash
# Add Dev-AID (if not already added)
./.dev-aid/scripts/setup-rag.sh

# Add GitHub MCP
claude mcp add github --scope user -- npx -y @modelcontextprotocol/server-github

# Add PostgreSQL MCP
claude mcp add postgres --scope user -- npx -y @modelcontextprotocol/server-postgres

# Add Slack MCP
claude mcp add slack --scope user -- npx -y slack-mcp-server

# Verify all servers
claude mcp list
# Should show: code-search, github, postgres, slack
```

### For Gemini CLI (Manual Merge Required)

Gemini CLI uses `~/.gemini/mcp.json` which must be edited manually:

```json
{
  "mcpServers": {
    "code-search": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "~/.local/share/claude-context-local",
        "python",
        "mcp_server/server.py"
      ]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "postgresql://user:pass@localhost/db"
      }
    },
    "slack": {
      "command": "npx",
      "args": ["-y", "slack-mcp-server"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-your-token"
      }
    }
  }
}
```

**Important**: Dev-AID's `setup-rag.sh` detects existing config and provides manual instructions to avoid overwriting your servers.

---

## Dev-AID Router + Other MCP Servers

**Can Dev-AID's router use other MCP servers?**

Currently: **Indirectly, yes!**

When you use Dev-AID router commands like `/dev-aid-router-challenger`:
1. Router sends request to Claude/Gemini via API
2. Claude/Gemini sees ALL your MCP servers
3. They can use any available server
4. Results come back to router

**Example**:
```
/dev-aid-router-challenger "Review our authentication code and check
                        if there are any related GitHub issues"

→ Claude generates code review (uses code-search MCP + github MCP)
→ Gemini reviews Claude's analysis (uses same MCPs)
→ You get comprehensive review with GitHub context
```

**Future possibility**: Dev-AID router could directly integrate with MCP servers for richer orchestration. This would require architectural changes.

---

## Finding MCP Servers

### Official Resources

**Official Registry** (Preview):
- https://github.com/modelcontextprotocol/registry

**Official Servers** (Reference implementations):
- https://github.com/modelcontextprotocol/servers

**Examples & Docs**:
- https://modelcontextprotocol.io/examples

### Community Registries

**Smithery** - MCP server registry by Henry Mao
- https://smithery.ai/

**Awesome MCP Servers** (Curated lists):
- https://github.com/punkpeye/awesome-mcp-servers
- https://github.com/appcypher/awesome-mcp-servers

**PulseMCP** - Community hub & weekly newsletter
- https://pulsemcp.com/

---

## Best Practices

### 1. Start Small

Don't install 20 MCP servers at once. Start with:
- Dev-AID Local Search (code search)
- GitHub MCP (if you use GitHub)
- Maybe one database or communication tool

### 2. Test Each Server

After adding a server, verify it works:

```bash
# Claude Code
claude mcp list  # Should show your new server

# Then test in conversation
"What MCP tools do you have access to?"
```

### 3. Manage Credentials Securely

Many MCP servers need API keys:

```json
{
  "mcpServers": {
    "github": {
      "env": {
        "GITHUB_TOKEN": "ghp_YourTokenHere"  // Use environment variables!
      }
    }
  }
}
```

**Better**: Use environment variables:

```bash
# ~/.bashrc or ~/.zshrc
export GITHUB_TOKEN="ghp_YourTokenHere"
export SLACK_BOT_TOKEN="xoxb-YourTokenHere"
```

```json
{
  "mcpServers": {
    "github": {
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"  // References env var
      }
    }
  }
}
```

### 4. Document Your Setup

Keep a list of installed MCP servers:

```bash
# Dev-AID project root
echo "code-search" >> .dev-aid/mcp-servers.txt
echo "github" >> .dev-aid/mcp-servers.txt
echo "postgres" >> .dev-aid/mcp-servers.txt
```

---

## Troubleshooting

### AI Not Using MCP Server

**Check 1**: Is it installed?
```bash
claude mcp list  # Claude Code
cat ~/.gemini/mcp.json  # Gemini CLI
```

**Check 2**: Is it configured correctly?
- Check command path
- Verify environment variables
- Test server manually

**Check 3**: Be explicit in your query
Instead of: "Show me the code"
Try: "Search my local codebase for authentication functions"

### Conflicting Server Names

If two servers have the same name, only one will be used.

**Bad**:
```json
{
  "mcpServers": {
    "search": { ... },  // Which search?
    "search": { ... }   // This overwrites the first one!
  }
}
```

**Good**:
```json
{
  "mcpServers": {
    "code-search": { ... },
    "web-search": { ... }
  }
}
```

### Performance Issues

Too many MCP servers can slow down AI startup.

**Solution**: Remove unused servers or use tool-specific configs.

---

## FAQ

### Q: Will adding MCP servers break Dev-AID?

**A**: No! Dev-AID only cares about its own `code-search` server. Other servers are invisible to Dev-AID's router but visible to the AI.

### Q: Can I use Dev-AID without any other MCP servers?

**A**: Yes! Dev-AID works perfectly standalone.

### Q: Can I remove the code-search MCP server?

**A**: Yes, but you'll lose Dev-AID Local Search functionality. The router will still work.

### Q: Do MCP servers slow down the AI?

**A**: Slightly. Each server adds tools the AI must consider. 3-5 servers is reasonable, 20+ may cause latency.

### Q: Can MCP servers see each other?

**A**: No. MCP servers are isolated. Only the AI can orchestrate between them.

### Q: Can I create my own MCP server?

**A**: Yes! See https://modelcontextprotocol.io/docs for the specification and examples.

---

## Summary

**Dev-AID + Other MCP Servers = Supercharged AI Development**

- ✅ Use as many MCP servers as you want
- ✅ Dev-AID respects existing configurations
- ✅ AI automatically orchestrates all tools
- ✅ No conflicts, no complexity
- ✅ Each server enhances the others

**Think of it like a plugin ecosystem** - install what you need, ignore what you don't, everything works together.

---

## Further Reading

- **Official MCP Documentation**: https://modelcontextprotocol.io/
- **Dev-AID Local Search Details**: [HOW-LOCAL-SEARCH-WORKS.md](./HOW-LOCAL-SEARCH-WORKS.md)
- **Community MCP Servers**: https://github.com/punkpeye/awesome-mcp-servers
- **Building MCP Servers**: https://modelcontextprotocol.io/docs/concepts/architecture
