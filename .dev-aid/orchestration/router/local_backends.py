"""Shared local LLM backend configuration for Dev-AID Router"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class BackendConfig:
    """Configuration for a local LLM backend"""

    name: str
    port: int
    health_path: str


# Ordered list of known local LLM backends
LOCAL_BACKENDS: List[BackendConfig] = [
    BackendConfig(name="ollama", port=11434, health_path="/api/tags"),
    BackendConfig(name="lm_studio", port=1234, health_path="/v1/models"),
    BackendConfig(name="llama_cpp", port=8080, health_path="/v1/models"),
]

# Default ports by backend name (for quick lookup)
DEFAULT_PORTS: Dict[str, int] = {b.name: b.port for b in LOCAL_BACKENDS}


def detect_available_backend(
    preferred: Optional[str] = None,
    custom_urls: Optional[Dict[str, Optional[str]]] = None,
    timeout: float = 2.0,
) -> Optional[Dict[str, Any]]:
    """
    Detect a running local LLM backend.

    Checks default ports for Ollama, LM Studio, and llama.cpp.

    Args:
        preferred: Preferred backend name to check first
        custom_urls: Dict mapping backend name to custom URL (or None)
        timeout: HTTP request timeout in seconds

    Returns:
        Dict with backend info if found, None otherwise
    """
    if custom_urls is None:
        custom_urls = {}

    # Order backends so preferred is first
    backends = list(LOCAL_BACKENDS)
    if preferred:
        for i, b in enumerate(backends):
            if b.name == preferred:
                backends.insert(0, backends.pop(i))
                break

    for backend in backends:
        try:
            custom_url = custom_urls.get(backend.name)
            if custom_url:
                url = custom_url.rstrip("/v1").rstrip("/") + backend.health_path
                base_url = custom_url
            else:
                url = f"http://localhost:{backend.port}{backend.health_path}"
                base_url = f"http://localhost:{backend.port}/v1"

            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                logger.info("Found %s server on port %d", backend.name, backend.port)
                return {
                    "backend": backend.name,
                    "port": backend.port,
                    "base_url": base_url,
                }
        except Exception:
            continue

    logger.debug("No local LLM server detected")
    return None
