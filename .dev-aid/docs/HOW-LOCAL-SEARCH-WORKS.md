# How Dev-AID Local Search Works

## The Simple Answer

When you ask Claude Code or Gemini CLI: **"Find authentication functions"**

**What happens behind the scenes:**

```
You → Claude/Gemini → Detects "code search" intent
                    ↓
              Uses local MCP tool
                    ↓
         Dev-AID Local Search searches locally
                    ↓
              Returns results ($0 cost)
                    ↓
         Claude/Gemini presents results to you
```

**Key point**: The AI automatically decides to use the local search tool instead of trying to answer from memory or cloud API.

---

## Tool Compatibility (MCP Protocol)

Dev-AID Local Search uses the **Model Context Protocol (MCP)** - an open standard for connecting AI tools to external data sources.

### ✅ Auto-Configured (Zero Setup)

These tools are automatically configured by `setup-rag.sh`:

- **Claude Code / Claude Desktop** - Official Anthropic CLI
- **Gemini CLI** - Google's AI development tool

### ✅ Compatible (Manual Setup Required)

These tools support MCP but require manual configuration:

- **VS Code + GitHub Copilot** (Generally available as of VS Code 1.102+)
- **Cursor** (via `.cursor/mcp.json`)
- **Windsurf** (Native MCP support in Settings → Cascade → MCP Servers)
- **Cline** (VS Code extension with full MCP support)
- **Zed** (Preview version, called "Context Servers")
- **JetBrains IDEs** (IntelliJ IDEA, PyCharm, WebStorm, etc.)
- **Eclipse** (Generally available)
- **Xcode** (Generally available)

**Manual configuration**: Add the MCP server config to your tool's settings. See `.dev-aid/scripts/setup-rag.sh` for the configuration format.

### ❌ Not Compatible

- **GitHub Codex API** (standalone) - No MCP support
- **GitHub Copilot** (without VS Code) - No MCP support
- **Older AI coding tools** without MCP protocol support

---

## The Technical Flow

### 1. Setup Phase (One-Time)

When you run `.dev-aid/scripts/setup-rag.sh`:

```bash
# Installs Dev-AID Local Search (embedded in .dev-aid/local-search/)
pip3 install -e .dev-aid/local-search/

# Registers it as an MCP server with your AI tool
claude mcp add code-search --scope user -- \
    python3 .dev-aid/local-search/mcp_server/server.py
```

**Key difference from external versions**: This is fully self-contained in the Dev-AID repository. No external GitHub dependencies, no separate installations - everything is embedded and maintained by Dev-AID.

### 2. What This Registration Does

After registration, your Claude Code or Gemini CLI gains a **new tool** called `code-search`:

```json
{
  "mcpServers": {
    "code-search": {
      "command": "python3",
      "args": [".dev-aid/local-search/mcp_server/server.py"],
      "capabilities": [
        "search_code",
        "index_directory",
        "get_index_status",
        "list_projects",
        "clear_index"
      ]
    }
  }
}
```

**Implementation**: `.dev-aid/local-search/mcp_server/server.py` - Self-contained MCP server owned and maintained by Dev-AID (not external dependency).

### 3. Runtime Phase (Every Query)

When you chat with Claude or Gemini:

**User**: "Find authentication functions"

**AI's internal decision tree**:
```
Is this a code search query? → YES
Do I have a local search tool? → YES (code-search MCP server)
Should I use it? → YES (more accurate than my knowledge)
```

**AI calls tool**:
```python
# AI automatically invokes:
await mcp_client.call_tool(
    name="code-search",
    arguments={
        "query": "authentication functions",
        "similarity_threshold": 0.7
    }
)
```

**Tool executes locally**:
```
1. Loads your indexed codebase (~1.2GB model in RAM)
2. Performs semantic search using EmbeddingGemma
3. Returns top 10 matching code snippets
4. All happens on YOUR machine ($0 API cost)
```

**AI receives results and responds**:
```
"I found 5 authentication functions in your codebase:

1. src/auth/login.py:45 - login_user()
2. src/auth/jwt.py:78 - verify_token()
3. src/auth/oauth.py:120 - oauth_callback()
..."
```

---

## Why This Works Automatically

### The AI Has Tools

Think of MCP tools like giving the AI "superpowers":

| Without Local Search | With Local Search (MCP) |
|---------------------|------------------------|
| AI guesses based on knowledge cutoff | AI searches YOUR actual code |
| Generic answers | Project-specific answers |
| May hallucinate function names | Returns real functions that exist |
| Uses cloud API (costs $$) | Uses local tool ($0 cost) |

### Tool Selection is Automatic

The AI model automatically decides when to use tools based on:

1. **Query pattern**: "Find...", "Search for...", "Where is..."
2. **Context**: You're in a code project directory
3. **Tool availability**: code-search tool is registered and available
4. **Capability match**: Query needs codebase search → use codebase search tool

**Example decision logic** (conceptual):
```python
def should_use_local_search(user_query: str, available_tools: list) -> bool:
    search_keywords = ["find", "search", "where", "locate", "show me"]
    code_keywords = ["function", "class", "method", "implementation"]

    has_search_intent = any(kw in user_query.lower() for kw in search_keywords)
    has_code_intent = any(kw in user_query.lower() for kw in code_keywords)
    has_tool = "code-search" in available_tools

    return has_search_intent and has_code_intent and has_tool
```

---

## Real-World Examples

### Example 1: Direct Search

**You ask**:
```
"Find all database migration functions"
```

**AI thinks**:
- Query type: Code search ✓
- Tool available: code-search ✓
- Decision: Use local tool

**AI does**:
```python
# Calls MCP tool
results = await mcp.call_tool("code-search", {
    "query": "database migration functions"
})

# Gets local results:
# - migrations/001_create_users.py:migrate_up()
# - migrations/002_add_indexes.py:migrate_up()
# - db/migrator.py:run_migrations()
```

**You get**: Real functions from YOUR codebase, not generic examples.

---

### Example 2: Combined with Router

**You use slash command**:
```
/dev-aid-router-challenger-rag "Add OAuth2 authentication"
```

**What happens**:
1. **RAG searches locally** → Finds your existing auth patterns
2. **Claude generates** → Implementation matching YOUR style
3. **Gemini reviews** → Security checks against YOUR codebase
4. **You get** → Code that fits your project perfectly

---

### Example 3: Without Explicit Command

**You just chat naturally**:
```
You: "I need to add rate limiting. How do we handle similar things?"
```

**AI automatically**:
1. Detects "how do we" = search codebase
2. Uses local search tool
3. Finds: `middleware/rate_limit.py`, `utils/throttle.py`
4. Shows: "You already have rate limiting in middleware/rate_limit.py using Redis..."

**No special command needed** - the AI just knows to search locally.

---

## Configuration: How AI Knows Tool Exists

### For Claude Code

After `setup-rag.sh` runs, this is added to `~/.claude-code/config.json`:

```json
{
  "mcpServers": {
    "code-search": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/home/user/.local/share/claude-context-local",
        "python",
        "mcp_server/server.py"
      ]
    }
  }
}
```

Now every time you start Claude Code, it sees `code-search` as an available tool.

### For Gemini CLI

Similar configuration in `~/.gemini/mcp.json`:

```json
{
  "servers": {
    "code-search": {
      "command": "uv",
      "args": ["run", "...mcp_server/server.py"]
    }
  }
}
```

---

## Verification: Check If It's Working

### Method 1: Check MCP Registration

```bash
# For Claude Code
claude mcp list

# Should show:
# code-search ✓ Active
```

### Method 2: Test Search

```bash
# Direct command
dev-aid-search status

# Should show:
# ✓ Installed: claude-context-local v1.x.x
# ✓ Indexed: 1,234 files
```

### Method 3: Ask AI Directly

In Claude Code or Gemini CLI:
```
You: "What tools do you have access to?"
AI: "I have access to: code-search (semantic codebase search), ..."
```

---

## Cost Comparison

### Without Local Search (Cloud API):

```
You: "Find all authentication functions"
Claude: *searches knowledge, may hallucinate*
Cost: ~$0.03 (input tokens for context)
Accuracy: 60% (generic answer)
```

### With Local Search (MCP Tool):

```
You: "Find all authentication functions"
Claude: *calls local MCP tool*
Cost: $0.00 (runs on your machine)
Accuracy: 100% (your actual code)
```

---

## When Does AI Use Local Search?

### AI WILL use local search for:

✅ "Find authentication functions"
✅ "Where is the login logic?"
✅ "Show me similar error handling patterns"
✅ "Search for database query methods"
✅ "Locate all API endpoints"

### AI WILL NOT use local search for:

❌ "What is OAuth2?" (general knowledge question)
❌ "Write a quicksort algorithm" (no need to search codebase)
❌ "Explain how JWT works" (educational, not code search)

**The AI is smart enough to decide** when local search is useful vs when to use its own knowledge.

---

## Summary

**How it works in 3 steps:**

1. **Setup** (once): `setup-rag.sh` registers local search as MCP tool
2. **Runtime** (automatic): AI sees tool and decides when to use it
3. **Result** (instant): Local search runs on your machine, $0 cost

**Key insight**: You don't need to explicitly tell the AI to "use local search". It automatically knows when a query needs codebase search vs general knowledge.

**Think of it like**: Giving the AI a superpower - once it has the tool, it knows when to use it, just like you know when to use Google vs looking in your notes.

---

## Troubleshooting

### AI Not Using Local Search?

**Check 1**: Is MCP server registered?
```bash
claude mcp list  # Should show code-search
```

**Check 2**: Is codebase indexed?
```bash
dev-aid-search status  # Should show indexed files
```

**Check 3**: Be more explicit
Instead of: "Tell me about auth"
Try: "Find authentication functions in this codebase"

### Tool Call Errors?

**Check logs**:
```bash
tail -f ~/.dev-aid/logs/rag-mcp.log
```

**Re-register**:
```bash
./.dev-aid/scripts/setup-rag.sh
```

---

## Further Reading

- **MCP Protocol**: See `.dev-aid/providers/claude/.claude/skills/expert/mcp/SKILL.md`
- **Storage Details**: See `.dev-aid/docs/STORAGE-LOCATIONS.md`
- **Update Guide**: See `.dev-aid/docs/UPDATING.md`
