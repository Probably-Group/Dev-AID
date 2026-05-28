"""Dev-AID Deep Research MCP Server.

Provides external research capabilities via MCP (Model Context Protocol).
Supports three providers: Tavily, Perplexity Sonar, and Gemini Deep Research.

Run as stdio server: python -m deep_research.mcp_server.server
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

from pydantic import ValidationError

from cache.research_cache import ResearchCache
from providers.base import ProviderError, ResearchDepth, ResearchResult
from providers.gemini_deep import GeminiDeepResearchProvider
from providers.perplexity import PerplexityProvider
from providers.tavily import TavilyProvider
from routing.smart_router import SmartRouter
from .validation import (
    CacheStatusRequest,
    ClearCacheRequest,
    DeepResearchRequest,
    QuickResearchRequest,
    ResearchRequest,
)

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Application error with safe user-facing message."""

    def __init__(self, message: str, internal: Optional[str] = None):
        self.message = message
        if internal:
            logger.error(f"{message}: {internal}")
        super().__init__(message)


class DeepResearchServer:
    """MCP Server for deep research.

    Provides tools for:
    - research: Main research query with smart routing
    - quick_research: Fast factual lookups
    - deep_research: Comprehensive multi-step research
    - get_providers: Check provider availability
    - get_cache_status: View cache statistics
    - clear_cache: Clear cached results
    """

    def __init__(self):
        """Initialize research server with providers and cache."""
        self.cache = ResearchCache()
        self.providers: Dict[str, Any] = {}
        self.router: Optional[SmartRouter] = None
        self._init_providers()

    def _init_providers(self) -> None:
        """Initialize available providers."""
        provider_classes = [
            TavilyProvider,
            PerplexityProvider,
            GeminiDeepResearchProvider,
        ]

        providers_list = []
        for cls in provider_classes:
            try:
                provider = cls()
                if provider.is_available():
                    self.providers[provider.name] = provider
                    providers_list.append(provider)
                    logger.info(f"Initialized provider: {provider.name}")
                else:
                    logger.debug(f"Provider not available: {cls.__name__}")
            except Exception as e:
                logger.warning(f"Failed to initialize {cls.__name__}: {e}")

        if providers_list:
            self.router = SmartRouter(providers_list)
            logger.info(f"Router initialized with {len(providers_list)} providers")
        else:
            logger.warning("No research providers available!")

    async def research(
        self,
        query: str,
        depth: str = "auto",
        provider: Optional[str] = None,
        max_sources: int = 10,
        use_cache: bool = True,
        cache_ttl_hours: int = 24,
        prefer_speed: bool = False,
    ) -> Dict[str, Any]:
        """Execute research query with smart routing.

        Args:
            query: Research query
            depth: Research depth (quick/standard/deep/auto)
            provider: Specific provider to use
            max_sources: Maximum sources to return
            use_cache: Use cached results if available
            cache_ttl_hours: Cache TTL in hours
            prefer_speed: Prefer faster providers

        Returns:
            Research result dictionary
        """
        if not self.router:
            raise AppError("No research providers available")

        # Route the query
        if depth == "auto":
            routing = self.router.route(
                query,
                prefer_speed=prefer_speed,
                force_provider=provider,
            )
            target_depth = routing.depth
            target_provider = routing.provider
            reasoning = routing.reasoning
        else:
            target_depth = ResearchDepth(depth)
            routing = self.router.route(
                query,
                prefer_speed=prefer_speed,
                force_provider=provider,
                force_depth=target_depth,
            )
            target_provider = routing.provider
            reasoning = routing.reasoning

        # Check cache
        if use_cache:
            cached = self.cache.get(query, target_provider, target_depth)
            if cached:
                logger.info(f"Cache hit for query: {query[:50]}...")
                return self._format_result(cached, reasoning, cached=True)

        # Execute research
        provider_instance = self.providers.get(target_provider)
        if not provider_instance:
            raise AppError(f"Provider not available: {target_provider}")

        try:
            result = await provider_instance.search(
                query=query,
                depth=target_depth,
                max_sources=max_sources,
            )
        except ProviderError as e:
            raise AppError(e.message)
        except Exception as e:
            raise AppError("Research failed", str(e))

        # Cache result
        if use_cache:
            self.cache.set(result, ttl_hours=cache_ttl_hours)

        return self._format_result(result, reasoning, cached=False)

    async def quick_research(
        self,
        query: str,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """Fast factual lookup.

        Args:
            query: Quick research query
            use_cache: Use cached results

        Returns:
            Research result dictionary
        """
        return await self.research(
            query=query,
            depth="quick",
            use_cache=use_cache,
            prefer_speed=True,
        )

    async def deep_research(
        self,
        query: str,
        use_cache: bool = True,
        timeout_seconds: int = 300,
    ) -> Dict[str, Any]:
        """Comprehensive multi-step research.

        Args:
            query: Deep research query
            use_cache: Use cached results
            timeout_seconds: Max wait time

        Returns:
            Research result dictionary
        """
        return await self.research(
            query=query,
            depth="deep",
            use_cache=use_cache,
        )

    def get_providers_status(self) -> Dict[str, Any]:
        """Get provider availability status.

        Returns:
            Dictionary with provider status
        """
        all_providers = {
            "tavily": {
                "available": "tavily" in self.providers,
                "supported_depths": ["quick", "standard"],
                "env_var": "TAVILY_API_KEY",
            },
            "perplexity-sonar": {
                "available": "perplexity-sonar" in self.providers,
                "supported_depths": ["standard", "deep"],
                "env_var": "PERPLEXITY_API_KEY",
            },
            "gemini-deep-research": {
                "available": "gemini-deep-research" in self.providers,
                "supported_depths": ["deep"],
                "env_var": "GOOGLE_API_KEY",
            },
        }

        return {
            "available_providers": list(self.providers.keys()),
            "total_available": len(self.providers),
            "providers": all_providers,
        }

    def get_cache_status(self, include_entries: bool = False) -> Dict[str, Any]:
        """Get cache statistics.

        Args:
            include_entries: Include entry details

        Returns:
            Cache statistics dictionary
        """
        # Cleanup expired entries first
        expired = self.cache.cleanup_expired()

        stats = self.cache.get_stats()
        stats["expired_cleaned"] = expired

        if include_entries:
            stats["entries"] = [
                {
                    "key": key,
                    "provider": entry.provider,
                    "depth": entry.depth,
                    "query_preview": entry.query_preview,
                }
                for key, entry in self.cache._index.items()
            ]

        return stats

    def clear_cache(
        self,
        query: Optional[str] = None,
        provider: Optional[str] = None,
        clear_all: bool = False,
    ) -> Dict[str, Any]:
        """Clear cache entries.

        Args:
            query: Specific query to clear
            provider: Clear all from provider
            clear_all: Clear everything

        Returns:
            Result dictionary
        """
        if clear_all:
            count = self.cache.clear_all()
            return {"status": "cleared", "entries_removed": count}

        depth = None
        if provider:
            depth_map = {
                "tavily": ResearchDepth.STANDARD,
                "perplexity-sonar": ResearchDepth.STANDARD,
                "gemini-deep-research": ResearchDepth.DEEP,
            }
            depth = depth_map.get(provider)

        count = self.cache.invalidate(
            query=query,
            provider=provider,
            depth=depth,
        )

        return {"status": "cleared", "entries_removed": count}

    def _format_result(
        self,
        result: ResearchResult,
        reasoning: str,
        cached: bool,
    ) -> Dict[str, Any]:
        """Format result for MCP response.

        Args:
            result: Research result
            reasoning: Routing reasoning
            cached: Whether from cache

        Returns:
            Formatted dictionary
        """
        return {
            "query": result.query,
            "content": result.content,
            "sources": result.sources,
            "provider": result.provider,
            "depth": result.depth.value,
            "citations": result.citations,
            "confidence_score": result.confidence_score,
            "processing_time_ms": result.processing_time_ms,
            "cached": cached,
            "routing_reasoning": reasoning,
            "metadata": result.metadata,
        }


class MCPRequestHandler:
    """Handler for MCP JSON-RPC requests."""

    def __init__(self, server: DeepResearchServer):
        self.server = server

    def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request."""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {
                "name": "devaid-deep-research",
                "version": "1.0.0",
            },
        }

    def handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request."""
        return {
            "tools": [
                {
                    "name": "research",
                    "description": "Execute research query with automatic provider routing based on query complexity",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Research query",
                            },
                            "depth": {
                                "type": "string",
                                "enum": ["quick", "standard", "deep", "auto"],
                                "default": "auto",
                                "description": "Research depth level",
                            },
                            "provider": {
                                "type": "string",
                                "description": "Specific provider (tavily, perplexity-sonar, gemini-deep-research)",
                            },
                            "max_sources": {
                                "type": "integer",
                                "default": 10,
                                "description": "Maximum sources to return",
                            },
                            "use_cache": {
                                "type": "boolean",
                                "default": True,
                                "description": "Use cached results if available",
                            },
                            "prefer_speed": {
                                "type": "boolean",
                                "default": False,
                                "description": "Prefer faster providers",
                            },
                        },
                        "required": ["query"],
                    },
                },
                {
                    "name": "quick_research",
                    "description": "Fast factual lookup using Tavily basic search",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Quick research query",
                            },
                            "use_cache": {
                                "type": "boolean",
                                "default": True,
                            },
                        },
                        "required": ["query"],
                    },
                },
                {
                    "name": "deep_research",
                    "description": "Comprehensive multi-step research using Gemini or Perplexity",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Deep research query",
                            },
                            "use_cache": {
                                "type": "boolean",
                                "default": True,
                            },
                            "timeout_seconds": {
                                "type": "integer",
                                "default": 300,
                                "description": "Max wait time (60-600s)",
                            },
                        },
                        "required": ["query"],
                    },
                },
                {
                    "name": "get_providers",
                    "description": "Get available research providers and their status",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                    },
                },
                {
                    "name": "get_cache_status",
                    "description": "Get research cache statistics",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "include_entries": {
                                "type": "boolean",
                                "default": False,
                                "description": "Include entry details",
                            },
                        },
                    },
                },
                {
                    "name": "clear_cache",
                    "description": "Clear research cache entries",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Specific query to clear",
                            },
                            "provider": {
                                "type": "string",
                                "description": "Clear all from provider",
                            },
                            "clear_all": {
                                "type": "boolean",
                                "default": False,
                                "description": "Clear all entries",
                            },
                        },
                    },
                },
            ]
        }

    async def handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        try:
            if tool_name == "research":
                validated = ResearchRequest(**arguments)
                result = await self.server.research(
                    query=validated.query,
                    depth=validated.depth,
                    provider=validated.provider,
                    max_sources=validated.max_sources,
                    use_cache=validated.use_cache,
                    cache_ttl_hours=validated.cache_ttl_hours,
                    prefer_speed=validated.prefer_speed,
                )

            elif tool_name == "quick_research":
                validated = QuickResearchRequest(**arguments)
                result = await self.server.quick_research(
                    query=validated.query,
                    use_cache=validated.use_cache,
                )

            elif tool_name == "deep_research":
                validated = DeepResearchRequest(**arguments)
                result = await self.server.deep_research(
                    query=validated.query,
                    use_cache=validated.use_cache,
                    timeout_seconds=validated.timeout_seconds,
                )

            elif tool_name == "get_providers":
                result = self.server.get_providers_status()

            elif tool_name == "get_cache_status":
                validated = CacheStatusRequest(**arguments)
                result = self.server.get_cache_status(
                    include_entries=validated.include_entries,
                )

            elif tool_name == "clear_cache":
                validated = ClearCacheRequest(**arguments)
                result = self.server.clear_cache(
                    query=validated.query,
                    provider=validated.provider,
                    clear_all=validated.clear_all,
                )

            else:
                raise ValueError(f"Unknown tool: {tool_name}")

            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

        except ValidationError as e:
            error_msg = e.errors()[0].get("msg", str(e))
            raise AppError(f"Invalid request: {error_msg}", str(e))
        except AppError:
            raise
        except Exception as e:
            raise AppError("Tool execution failed", str(e))


async def handle_mcp_request_async(
    server: DeepResearchServer, request: Dict[str, Any]
) -> Dict[str, Any]:
    """Handle MCP JSON-RPC request asynchronously.

    Args:
        server: DeepResearchServer instance
        request: JSON-RPC request dictionary

    Returns:
        JSON-RPC response dictionary
    """
    method = request.get("method", "")
    params = request.get("params", {})
    request_id = request.get("id")

    handler = MCPRequestHandler(server)

    try:
        if method == "initialize":
            result = handler.handle_initialize(params)
        elif method == "tools/list":
            result = handler.handle_tools_list(params)
        elif method == "tools/call":
            result = await handler.handle_tools_call(params)
        elif method == "notifications/initialized":
            # Acknowledgement, no response needed
            return {}
        else:
            raise ValueError(f"Unknown method: {method}")

        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    except AppError as e:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32603, "message": e.message},
        }
    except Exception as e:
        logger.exception(f"Unexpected error handling {method}")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32603, "message": "Internal server error"},
        }


def main() -> None:
    """Main entry point for stdio MCP server."""
    logging.basicConfig(
        level=logging.DEBUG if os.getenv("DEBUG") == "1" else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )

    logger.info("Starting Dev-AID Deep Research MCP Server")
    server = DeepResearchServer()

    async def process_stdin() -> None:
        """Process JSON-RPC requests from stdin."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                request = json.loads(line)
                response = await handle_mcp_request_async(server, request)
                if response:  # Skip empty responses (notifications)
                    print(json.dumps(response), flush=True)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
                print(
                    json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "error": {"code": -32700, "message": "Parse error"},
                        }
                    ),
                    flush=True,
                )

    asyncio.run(process_stdin())


if __name__ == "__main__":
    main()
