# Deep Research Guide

Multi-provider research system with smart routing, semantic caching, and MCP integration.

## Overview

Dev-AID Deep Research connects your AI tools to external knowledge via three research providers. A smart router automatically selects the best provider based on query complexity, with aggressive caching to minimize API costs.

**Module:** `.dev-aid/deep-research/`

## Providers

| Provider | Depths | Best For | Speed | API Key |
|----------|--------|----------|-------|---------|
| **Tavily** | Quick, Standard | Factual lookups, documentation, how-to | 3-5s | `TAVILY_API_KEY` |
| **Perplexity Sonar** | Standard, Deep | Comparisons, implementation guides, synthesis | 8-30s | `PERPLEXITY_API_KEY` |
| **Gemini Deep Research** | Deep only | Architecture analysis, comprehensive research | 2-5 min | `GOOGLE_API_KEY` |

### Provider Details

**Tavily** — Fast factual search with LLM-friendly responses. Free tier: 1,000 credits/month. Quick uses 1 credit, Standard uses 2.

**Perplexity Sonar** — Multi-source synthesis with citations. Uses `sonar` model for standard and `sonar-deep-research` for deep queries.

**Gemini Deep Research** — Multi-step comprehensive research synthesizing hundreds of sources. Uses async polling with configurable timeout (default 5 minutes).

## Smart Routing

The router classifies queries into three complexity levels and selects the optimal provider:

| Complexity | Triggers | Routes To |
|-----------|----------|-----------|
| **Simple** | "what is", "define", "syntax", "latest version" | Tavily Quick |
| **Moderate** | "how to", "implement", "setup", "tutorial" | Tavily Standard |
| **Complex** | "compare", "architecture", "pros and cons", 30+ words | Gemini Deep |

Fallback chain: if the primary provider is unavailable, the router falls back (Gemini → Perplexity → Tavily).

## CLI Usage

Install: the CLI is available as `dev-aid-research` after setting up the deep-research module.

```bash
# Auto-routed research (smart provider selection)
dev-aid-research search "What is GraphQL?"

# Force specific depth
dev-aid-research search --depth deep "Compare Redis vs Memcached"

# Force specific provider
dev-aid-research search --provider perplexity-sonar "React vs Vue comparison"

# Fast factual lookup
dev-aid-research quick "Python list append syntax"

# Comprehensive deep research
dev-aid-research deep "Kubernetes networking architecture"
dev-aid-research deep --timeout 600 "State of JavaScript ecosystem 2025"

# Provider status
dev-aid-research providers

# Cache management
dev-aid-research cache --entries
dev-aid-research clear-cache --all
dev-aid-research clear-cache --provider tavily
```

### CLI Options

| Option | Description |
|--------|-------------|
| `--depth, -d` | `quick\|standard\|deep\|auto` (default: auto) |
| `--provider, -p` | Force provider: `tavily`, `perplexity-sonar`, `gemini-deep-research` |
| `--sources, -s` | Max sources 1-50 (default: 10) |
| `--no-cache` | Skip cache, force fresh results |
| `--json` | Output raw JSON instead of formatted display |
| `--timeout` | Max seconds for deep research (default: 300) |

## MCP Tools

Six tools are exposed via the MCP JSON-RPC interface for use by AI coding tools:

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `research` | Auto-routed research | `query`, `depth`, `provider`, `max_sources`, `use_cache` |
| `quick_research` | Fast factual lookup | `query`, `use_cache` |
| `deep_research` | Comprehensive research | `query`, `timeout_seconds`, `use_cache` |
| `get_providers` | Check provider availability | (none) |
| `get_cache_status` | View cache statistics | `include_entries` |
| `clear_cache` | Clear cached results | `query`, `provider`, `clear_all` |

### MCP Server

Start the MCP server (stdio protocol):

```bash
python -m deep_research.mcp_server.server
```

The server reads JSON-RPC requests from stdin and writes responses to stdout. Set `DEBUG=1` for verbose logging to stderr.

## Caching

Research results are cached to minimize API calls and reduce costs.

- **Location:** `~/.dev-aid/cache/research/`
- **Key:** SHA256 hash of `normalized_query:provider:depth`
- **Default TTL:** 24 hours (configurable 1-48 hours per request)
- **Normalization:** Queries lowercased and whitespace-trimmed for better hit rates
- **Cleanup:** Expired entries cleaned automatically on status checks

## Configuration

### Environment Variables

| Variable | Required For | Notes |
|----------|-------------|-------|
| `TAVILY_API_KEY` | Tavily provider | [Get key](https://tavily.com) |
| `PERPLEXITY_API_KEY` | Perplexity Sonar | [Get key](https://perplexity.ai) |
| `GOOGLE_API_KEY` | Gemini Deep Research | [Get key](https://aistudio.google.com) |

All variables are optional — only providers with configured API keys are available. The router automatically adjusts to available providers.

### Dependencies

- Python >=3.10
- `httpx` — async HTTP client
- `pydantic` — request validation
- `click` + `rich` — CLI interface
- `google-genai` — Gemini API client

## Slash Command

```bash
/aid-research "async patterns" deep    # From Claude Code / Gemini CLI
```

This invokes the research agent which uses the deep research system internally.

## Architecture

```
.dev-aid/deep-research/
├── providers/           # Tavily, Perplexity, Gemini implementations
│   └── base.py          # Abstract ResearchProvider + data models
├── routing/
│   └── smart_router.py  # Query complexity classification & routing
├── cache/
│   └── research_cache.py # File-based cache with TTL
├── mcp_server/
│   ├── server.py        # MCP JSON-RPC server (stdio)
│   ├── cli.py           # CLI entry point
│   └── validation.py    # Pydantic request validators
└── tests/               # Provider, routing, and cache tests
```
