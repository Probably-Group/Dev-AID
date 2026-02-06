"""
Dev-AID Router Modes

- solo: Single model handles all tasks
- ensemble: Route to best model based on task type
- challenger: Primary generates, challenger reviews
"""

from ._protocol import ModeConfigProtocol
from .challenger import ChallengerMode
from .ensemble import EnsembleMode
from .solo import SoloMode

__all__ = ["SoloMode", "EnsembleMode", "ChallengerMode", "ModeConfigProtocol"]
