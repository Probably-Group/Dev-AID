"""
Local LLM API Client

Provides unified interface for local LLM inference backends:
- Ollama (default, port 11434)
- LM Studio (port 1234)
- llama.cpp server (port 8080)

All backends use OpenAI-compatible API format.
"""

import logging
from typing import Any, Dict, List, Optional

import requests

from .api_clients import APIResponse, BaseAIClient, Message, track_api_call
from .auth_detector import AuthCredentials
from .local_backends import DEFAULT_PORTS, detect_available_backend
from .token_estimation import estimate_tokens

logger = logging.getLogger(__name__)


class LocalLLMClient(BaseAIClient):
    """Client for local LLM inference via OpenAI-compatible API"""

    # Use shared DEFAULT_PORTS from local_backends module
    DEFAULT_PORTS = DEFAULT_PORTS

    def __init__(self, auth: AuthCredentials, model_config: Dict[str, Any]):
        """
        Initialize local LLM client

        Args:
            auth: AuthCredentials with local server info
            model_config: Model configuration from models.json
        """
        super().__init__(auth, model_config)

        # Get backend configuration
        self.backend = auth.credentials.get("backend", "ollama")
        self.base_url = auth.credentials.get("base_url", self._get_default_url())

        # Ensure URL ends with /v1 for OpenAI compatibility
        if not self.base_url.endswith("/v1"):
            self.base_url = self.base_url.rstrip("/") + "/v1"

        self.provider = "local"

        # Initialize OpenAI client for API calls
        try:
            import openai

            self.client = openai.OpenAI(
                base_url=self.base_url,
                api_key="not-needed",  # Local servers don't require API key
            )
            logger.info(f"Initialized local LLM client: {self.backend} at {self.base_url}")

        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")

    def _get_default_url(self) -> str:
        """Get default URL based on backend"""
        port = self.DEFAULT_PORTS.get(self.backend, 11434)
        return f"http://localhost:{port}/v1"

    def verify_connection(self, timeout: float = 5.0) -> bool:
        """
        Verify connection to local LLM server

        Args:
            timeout: Connection timeout in seconds

        Returns:
            True if server is reachable and responding
        """
        try:
            # Try to list models (works on all backends)
            models_url = self.base_url.replace("/v1", "") + "/api/tags"

            # Ollama uses /api/tags, others use /v1/models
            if self.backend == "ollama":
                response = requests.get(models_url, timeout=timeout)
            else:
                response = requests.get(f"{self.base_url}/models", timeout=timeout)

            if response.status_code == 200:
                logger.info(f"Successfully connected to {self.backend} at {self.base_url}")
                return True

            logger.warning(f"Server responded with status {response.status_code}: {response.text}")
            return False

        except requests.exceptions.ConnectionError:
            logger.warning(
                f"Cannot connect to {self.backend} at {self.base_url}. " f"Is the server running?"
            )
            return False
        except requests.exceptions.Timeout:
            logger.warning(f"Connection to {self.backend} timed out after {timeout}s")
            return False
        except Exception as e:
            logger.warning(f"Failed to verify connection: {e}")
            return False

    def list_models(self) -> List[str]:
        """
        List available models on the local server

        Returns:
            List of model IDs available
        """
        try:
            if self.backend == "ollama":
                # Ollama uses different endpoint
                api_url = self.base_url.replace("/v1", "") + "/api/tags"
                response = requests.get(api_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    return [m["name"] for m in data.get("models", [])]
                return []
            else:
                # Standard OpenAI-compatible endpoint
                models_response = self.client.models.list()
                return [m.id for m in models_response.data]

        except Exception as e:
            logger.warning(f"Failed to list models: {e}")
            return []

    @track_api_call
    def send_request(
        self,
        messages: List[Message],
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> APIResponse:
        """
        Send request to local LLM server

        Args:
            messages: List of messages (conversation history)
            model: Model ID to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 - 1.0)
            **kwargs: Additional parameters. Notably ``tools=[...]`` is
                forwarded to the OpenAI-compatible chat completions endpoint;
                Ollama / LM Studio / llama.cpp servers that support native
                tool calling will return parsed tool calls in the response,
                which we surface on ``APIResponse.tool_calls``.

        Returns:
            APIResponse object
        """
        # Convert messages to OpenAI format
        api_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

        # Make API call
        response = self.client.chat.completions.create(
            model=model,
            messages=api_messages,  # type: ignore[arg-type]
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )

        # Extract response data
        choice = response.choices[0]
        content = choice.message.content or ""

        # Parse tool_calls if the model emitted any. Ollama (and the
        # OpenAI-compat endpoint generally) returns these as
        # response.choices[0].message.tool_calls, a list of
        # ChatCompletionMessageToolCall objects with .id, .type, and
        # .function.{name,arguments}. Before issue #140 we dropped this
        # entirely on the floor, which made native tool calling on local
        # models invisible to the router and forced agents into brittle
        # free-text parsing fallbacks.
        tool_calls = self._parse_tool_calls(getattr(choice.message, "tool_calls", None))

        # Get token counts (may not be available on all backends)
        input_tokens = getattr(response.usage, "prompt_tokens", 0) if response.usage else 0
        output_tokens = getattr(response.usage, "completion_tokens", 0) if response.usage else 0

        # Estimate tokens if not provided
        if input_tokens == 0:
            input_tokens = estimate_tokens(" ".join(msg.content for msg in messages))
        if output_tokens == 0:
            output_tokens = estimate_tokens(content)

        # Local models have zero cost
        cost = 0.0

        return APIResponse(
            content=content,
            model=model,
            provider="local",
            tokens_used={"input": input_tokens, "output": output_tokens},
            cost=cost,
            latency_ms=None,  # Set by decorator
            metadata={
                "backend": self.backend,
                "finish_reason": choice.finish_reason,
                "response_id": response.id,
            },
            tool_calls=tool_calls,
        )

    @staticmethod
    def _parse_tool_calls(
        raw_tool_calls: Optional[List[Any]],
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Normalize OpenAI/Ollama tool_calls into a JSON-friendly list of dicts.

        The OpenAI Python client returns ChatCompletionMessageToolCall pydantic
        objects (or, when an Ollama-compat server returns dicts, plain dicts).
        Both shapes need to round-trip the same way through ``APIResponse``.
        Empty / None inputs return None so callers can keep the simple
        ``if response.tool_calls:`` check.
        """
        if not raw_tool_calls:
            return None

        normalized: List[Dict[str, Any]] = []
        for tc in raw_tool_calls:
            if isinstance(tc, dict):
                # Already a dict (Ollama bare-/api/chat or LM Studio shape).
                fn = tc.get("function", {}) or {}
                normalized.append(
                    {
                        "id": tc.get("id"),
                        "type": tc.get("type", "function"),
                        "function": {
                            "name": fn.get("name"),
                            "arguments": fn.get("arguments"),
                        },
                    }
                )
                continue

            # OpenAI SDK pydantic object — pull attributes individually so we
            # don't depend on a model_dump() that may differ across SDK versions.
            fn_obj = getattr(tc, "function", None)
            normalized.append(
                {
                    "id": getattr(tc, "id", None),
                    "type": getattr(tc, "type", "function"),
                    "function": {
                        "name": getattr(fn_obj, "name", None) if fn_obj else None,
                        "arguments": getattr(fn_obj, "arguments", None) if fn_obj else None,
                    },
                }
            )
        return normalized

    def chat_completion_with_tools(
        self,
        messages: List[Message],
        model: str,
        tools: List[Dict[str, Any]],
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> APIResponse:
        """
        Convenience wrapper that forwards an explicit ``tools`` schema list
        to ``send_request`` and returns an APIResponse whose ``tool_calls``
        field is populated when the model decides to call a tool.

        ``tools`` is the standard OpenAI-style schema:
            [{"type": "function", "function": {"name": ..., "description": ...,
              "parameters": {<JSON Schema>}}}]

        This is the canonical entry point for agents that need structured
        tool dispatch on a local model — see issue #140.
        """
        return self.send_request(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            tools=tools,
            **kwargs,
        )

    def chat_completion_structured(
        self,
        messages: List[Message],
        model: str,
        schema: Dict[str, Any],
        max_tokens: int = 4096,
        temperature: float = 0.0,
        **kwargs: Any,
    ) -> APIResponse:
        """
        Request structured (JSON-schema-constrained) output from a local LLM.

        Uses Ollama's native ``format`` parameter, which applies FSM-based
        constrained decoding (via xgrammar / GBNF internally). The model is
        mathematically guaranteed to emit valid JSON matching ``schema``,
        eliminating the retry-on-ValidationError loop that the pre-2024
        pattern required (see SKILL.md section 3.3 before this PR).

        ``schema`` is a standard JSON Schema object::

            {"type": "object",
             "properties": {"city": {"type": "string"}},
             "required": ["city"]}

        or a Pydantic-generated schema (``MyModel.model_json_schema()``).

        The response's ``content`` field will contain the raw JSON string.
        Callers can then ``json.loads(response.content)`` or
        ``MyModel.model_validate_json(response.content)`` on it — the parse
        is guaranteed not to fail for schema-valid output, so no retry loop
        is needed.

        Implementation note: We pass the schema via ``extra_body={"format":
        schema}`` instead of the OpenAI SDK's ``response_format`` parameter.
        This bypasses the OpenAI-compatibility layer (which has known
        property-ordering issues in Ollama — see ollama/ollama#10001) and
        talks directly to Ollama's native format engine.

        For LM Studio and llama.cpp backends the equivalent mechanism is
        GBNF grammar injection; this method doesn't automatically translate
        the JSON schema to GBNF. LM Studio's recent versions accept JSON
        schema via the ``response_format`` parameter directly, so callers
        targeting LM Studio should use ``send_request(response_format=...)``
        instead.

        Args:
            messages: Conversation messages
            model: Model ID
            schema: JSON Schema dict (or Pydantic ``model_json_schema()``)
            max_tokens: Maximum tokens (default 4096)
            temperature: Sampling temperature (default 0.0 for deterministic
                structured output)
            **kwargs: Forwarded to ``send_request``

        Returns:
            APIResponse whose ``content`` is a JSON string matching ``schema``
        """
        return self.send_request(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            extra_body={"format": schema},
            **kwargs,
        )

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate cost - always zero for local models

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Always 0.0 for local inference
        """
        return 0.0


def detect_local_server() -> Optional[Dict[str, Any]]:
    """
    Detect running local LLM server.

    Delegates to shared local_backends.detect_available_backend().

    Returns:
        Dict with backend info if found, None otherwise
    """
    return detect_available_backend()


def create_local_auth(
    backend: str = "ollama",
    base_url: Optional[str] = None,
) -> AuthCredentials:
    """
    Create AuthCredentials for local LLM server

    Args:
        backend: Backend type ("ollama", "lm_studio", "llama_cpp")
        base_url: Optional custom base URL

    Returns:
        AuthCredentials configured for local server
    """
    if base_url is None:
        port = LocalLLMClient.DEFAULT_PORTS.get(backend, 11434)
        base_url = f"http://localhost:{port}/v1"

    return AuthCredentials(
        provider="local",
        auth_type="local",
        credentials={
            "backend": backend,
            "base_url": base_url,
        },
        source=f"local {backend} server",
    )


# CLI usage
if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    print("Detecting local LLM server...")
    server = detect_local_server()

    if server:
        print(f"\nFound: {server['backend']} at {server['base_url']}")

        # Create client and test
        auth = create_local_auth(server["backend"], server["base_url"])
        client = LocalLLMClient(auth, {"provider": "local"})

        if client.verify_connection():
            print("\nAvailable models:")
            models = client.list_models()
            for model in models[:10]:  # Show first 10
                print(f"  - {model}")

            if len(models) > 10:
                print(f"  ... and {len(models) - 10} more")

            if models:
                print(f"\nTesting with model: {models[0]}")
                try:
                    response = client.send_request(
                        messages=[Message(role="user", content="Say 'Hello from local LLM!'")],
                        model=models[0],
                        max_tokens=50,
                    )
                    print(f"Response: {response.content}")
                    print(f"Tokens: {response.tokens_used}")
                    print(f"Cost: ${response.cost:.4f} (free!)")
                except Exception as e:
                    print(f"Test failed: {e}")
        else:
            print("Failed to connect to server")
    else:
        print("\nNo local LLM server detected.")
        print("Start one of the following:")
        print("  - Ollama: ollama serve")
        print("  - LM Studio: Launch the app")
        print("  - llama.cpp: ./llama-server -m model.gguf")

    sys.exit(0)
