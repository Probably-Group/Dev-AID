"""Protocol for ConfigLoader interface used by mode classes."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple, runtime_checkable

from ..auth_detector import AuthCredentials

# Keys the executor threads through **kwargs for orchestration bookkeeping but
# that are NOT valid provider API parameters. They must be stripped before a
# request reaches client.send_request()/messages.create(), whose SDK signatures
# reject unknown keyword arguments with TypeError (audit finding H3).
ORCHESTRATION_ONLY_KWARGS = frozenset({"mcp_context", "context_size"})


def provider_kwargs(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Return kwargs safe to forward to a provider API call.

    Drops orchestration-only keys (see ORCHESTRATION_ONLY_KWARGS) so they do
    not leak into the provider SDK, while preserving genuine API params
    (e.g. max_tokens, temperature).
    """
    return {k: v for k, v in kwargs.items() if k not in ORCHESTRATION_ONLY_KWARGS}


@runtime_checkable
class ModeConfigProtocol(Protocol):
    """Protocol describing the ConfigLoader interface used by mode classes."""

    root: Path
    models: Dict[str, Any]

    def get_default_model(self) -> str: ...

    def get_model_config(self, model_name: str) -> Optional[Dict[str, Any]]: ...

    def validate_provider(self, provider: str) -> Tuple[bool, str]: ...

    def get_auth_credentials(self, provider: str) -> Optional[AuthCredentials]: ...

    def get_routing_config(self) -> Dict[str, Any]: ...

    def get_fallback_chain(self) -> List[str]: ...
