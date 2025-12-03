"""
Dev-AID Router - Multi-AI Orchestration Engine

Enables intelligent routing between different AI providers (Anthropic, Google, OpenAI)
with support for solo, ensemble, and challenger modes.
"""

__version__ = "1.0.0"
__author__ = "Dev-AID Contributors"

from .executor import execute_request
from .config_loader import load_config

__all__ = ["execute_request", "load_config"]
