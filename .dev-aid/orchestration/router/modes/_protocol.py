"""Protocol for ConfigLoader interface used by mode classes."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple, runtime_checkable

from ..auth_detector import AuthCredentials


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
