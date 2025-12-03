"""
Dev-AID Router Modes

- solo: Single model handles all tasks
- ensemble: Route to best model based on task type
- challenger: Primary generates, challenger reviews
"""

from .solo import SoloMode
from .ensemble import EnsembleMode
from .challenger import ChallengerMode

__all__ = ["SoloMode", "EnsembleMode", "ChallengerMode"]
