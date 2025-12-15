"""
TOON (Token-Oriented Object Notation) integration for Dev-AID

Provides utilities to encode/decode TOON format, reducing token consumption
by 40-60% compared to JSON in LLM interactions.
"""

from .encoder import encode
from .decoder import decode
from .converter import json_to_toon, toon_to_json

__all__ = ["encode", "decode", "json_to_toon", "toon_to_json"]
__version__ = "1.0.0"
