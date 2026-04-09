"""
Model Recommender Module

Recommends optimal local LLM models based on hardware capabilities.
Matches hardware profiles to compatible models and ranks them by performance.
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .hardware_detector import HardwareProfile

logger = logging.getLogger(__name__)


@dataclass
class ModelRecommendation:
    """A recommended model with compatibility info"""

    model_id: str
    model_name: str
    tier: str
    score: int
    vram_required_gb: float
    compatibility: str  # "optimal", "good", "marginal", "cpu_only"
    explanation: str
    capabilities: List[str]
    context_window: int
    # True if the model is trained for native function/tool calling. Surfaced
    # so callers (e.g. agent loops) can filter the recommendation set when
    # the task requires structured tool dispatch — see issue #142.
    supports_tool_calling: bool = False


@dataclass
class RecommendationResult:
    """Complete recommendation result"""

    hardware_tier: str
    recommendations: List[ModelRecommendation]
    warnings: List[str]
    notes: List[str]


class ModelRecommender:
    """Recommends local LLM models based on hardware capabilities"""

    def __init__(self, models_config: Optional[Dict[str, Any]] = None):
        """
        Initialize recommender with models configuration

        Args:
            models_config: Optional pre-loaded config. If None, loads from models.json
        """
        if models_config is None:
            self.models_config = self._load_models_config()
        else:
            self.models_config = models_config

        self.local_config = self.models_config.get("local", {})
        self.local_models = self.local_config.get("models", {})

    def _load_models_config(self) -> Dict[str, Any]:
        """Load models configuration from models.json"""
        # Try multiple possible locations
        config_paths = [
            Path(__file__).parent.parent.parent / "config" / "models.json",
            Path.cwd() / ".dev-aid" / "config" / "models.json",
        ]

        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path) as f:
                        result: Dict[str, Any] = json.load(f)
                        return result
                except Exception as e:
                    logger.warning(f"Failed to load models.json from {config_path}: {e}")

        logger.error("Could not find models.json configuration")
        return {}

    def recommend(
        self,
        hardware: HardwareProfile,
        requires_tool_calling: bool = False,
    ) -> RecommendationResult:
        """
        Get model recommendations based on hardware profile

        Args:
            hardware: HardwareProfile from hardware detection
            requires_tool_calling: If True, filter the candidate set to only
                models with ``supports_tool_calling: true`` in models.json.
                Used by callers (e.g. agent loops) that need structured tool
                dispatch and would silently fail on a model that can't emit
                native function calls. See issue #142.

        Returns:
            RecommendationResult with ranked recommendations
        """
        recommendations: List[ModelRecommendation] = []
        warnings: List[str] = []
        notes: List[str] = []

        # Get available VRAM
        available_vram = hardware.available_vram_gb

        # Apple Silicon uses unified memory
        if hardware.is_apple_silicon:
            # Can use up to 75% of RAM for ML
            available_vram = hardware.ram_gb * 0.75
            notes.append(
                f"Apple Silicon detected with {hardware.ram_gb}GB unified memory. "
                f"~{available_vram:.1f}GB available for ML workloads."
            )

        # No GPU - CPU only mode
        if not hardware.has_gpu or available_vram < 3:
            warnings.append(
                "No GPU detected or insufficient VRAM. "
                "Models will run on CPU (slower but functional)."
            )
            # For CPU-only, use RAM as the limit (with buffer)
            available_vram = min(
                hardware.ram_gb * 0.5, 8
            )  # Use up to 50% of RAM, max 8GB equivalent
            notes.append(
                f"CPU inference will use up to {available_vram:.1f}GB of RAM. "
                "Consider smaller models for better performance."
            )

        if requires_tool_calling:
            notes.append(
                "Tool-calling required: only models with native function "
                "calling support are considered."
            )

        # Evaluate each model
        for model_name, model_config in self.local_models.items():
            # Filter out non-tool-calling models when the caller requires it.
            # This runs BEFORE the VRAM check so the result set's "no models
            # found" warning correctly attributes the empty set to the filter
            # rather than to hardware constraints.
            supports_tools = bool(model_config.get("supports_tool_calling", False))
            if requires_tool_calling and not supports_tools:
                continue

            vram_required = model_config.get("vram_min_gb", 0)
            tier = model_config.get("tier", "unknown")
            score = model_config.get("score", 0)

            # Determine compatibility
            if vram_required <= available_vram * 0.8:
                # Plenty of headroom
                compatibility = "optimal"
                explanation = (
                    f"Runs comfortably with {available_vram - vram_required:.1f}GB VRAM headroom"
                )
            elif vram_required <= available_vram:
                # Tight fit but should work
                compatibility = "good"
                explanation = (
                    f"Fits in available VRAM ({vram_required}GB of {available_vram:.1f}GB)"
                )
            elif vram_required <= available_vram * 1.2:
                # Might work with quantization or memory pressure
                compatibility = "marginal"
                explanation = (
                    f"May require quantization or experience memory pressure "
                    f"({vram_required}GB needed, {available_vram:.1f}GB available)"
                )
            else:
                # Won't fit - skip or mark as CPU-only
                if vram_required > 16 and not hardware.has_gpu:
                    compatibility = "cpu_only"
                    explanation = f"Requires {vram_required}GB VRAM - will run on CPU (slow)"
                else:
                    # Skip models that are way too large
                    continue

            recommendation = ModelRecommendation(
                model_id=model_config.get("id", model_name),
                model_name=model_name,
                tier=tier,
                score=score,
                vram_required_gb=vram_required,
                compatibility=compatibility,
                explanation=explanation,
                capabilities=model_config.get("capabilities", []),
                context_window=model_config.get("context_window", 0),
                supports_tool_calling=supports_tools,
            )
            recommendations.append(recommendation)

        # Sort by: compatibility (optimal > good > marginal > cpu_only), then by score
        compatibility_order = {"optimal": 0, "good": 1, "marginal": 2, "cpu_only": 3}
        recommendations.sort(key=lambda r: (compatibility_order.get(r.compatibility, 99), -r.score))

        # Add tier-specific notes
        hw_tier = hardware.recommended_tier
        tier_notes = {
            "enterprise": "Enterprise-class hardware. All models supported including 80GB+ models.",
            "pro": "Professional hardware. Most models supported, including 48GB models.",
            "high": "High-end hardware. Supports most coding models including 32B parameters.",
            "mid": "Mid-range hardware. Good for 22B and smaller models.",
            "entry": "Entry-level GPU. Best with smaller models like Phi-4-Mini.",
            "cpu_only": "CPU-only mode. Recommend smallest models for acceptable performance.",
        }
        if hw_tier in tier_notes:
            notes.append(tier_notes[hw_tier])

        return RecommendationResult(
            hardware_tier=hw_tier,
            recommendations=recommendations,
            warnings=warnings,
            notes=notes,
        )

    def get_best_model(
        self,
        hardware: HardwareProfile,
        requires_tool_calling: bool = False,
    ) -> Optional[ModelRecommendation]:
        """
        Get the single best recommended model

        Args:
            hardware: HardwareProfile from hardware detection
            requires_tool_calling: Forwarded to ``recommend()`` — see #142.

        Returns:
            Best ModelRecommendation or None if no models available
        """
        result = self.recommend(hardware, requires_tool_calling=requires_tool_calling)
        if result.recommendations:
            return result.recommendations[0]
        return None

    def get_model_by_tier(
        self,
        hardware: HardwareProfile,
        target_tier: str,
        requires_tool_calling: bool = False,
    ) -> Optional[ModelRecommendation]:
        """
        Get best model for a specific tier

        Args:
            hardware: HardwareProfile from hardware detection
            target_tier: Tier to filter by ("entry", "mid", "high", "pro", "enterprise")
            requires_tool_calling: Forwarded to ``recommend()`` — see #142.

        Returns:
            Best matching ModelRecommendation or None
        """
        result = self.recommend(hardware, requires_tool_calling=requires_tool_calling)
        for rec in result.recommendations:
            if rec.tier == target_tier and rec.compatibility in ("optimal", "good"):
                return rec
        return None


def format_recommendations(result: RecommendationResult) -> str:
    """
    Format recommendations as human-readable string

    Args:
        result: RecommendationResult from recommender

    Returns:
        Formatted string for display
    """
    lines = []

    lines.append(f"Hardware Tier: {result.hardware_tier.upper()}")
    lines.append("")

    # Warnings first
    if result.warnings:
        lines.append("WARNINGS:")
        for warning in result.warnings:
            lines.append(f"  - {warning}")
        lines.append("")

    # Notes
    if result.notes:
        lines.append("NOTES:")
        for note in result.notes:
            lines.append(f"  - {note}")
        lines.append("")

    # Recommendations
    lines.append("RECOMMENDED MODELS:")
    lines.append("-" * 60)

    for i, rec in enumerate(result.recommendations, 1):
        compat_emoji = {
            "optimal": "[OK]",
            "good": "[+]",
            "marginal": "[~]",
            "cpu_only": "[CPU]",
        }.get(rec.compatibility, "[ ]")

        lines.append(f"{i}. {compat_emoji} {rec.model_name}")
        lines.append(f"   Model ID: {rec.model_id}")
        lines.append(f"   Tier: {rec.tier} | Score: {rec.score} | VRAM: {rec.vram_required_gb}GB")
        lines.append(f"   Compatibility: {rec.compatibility}")
        lines.append(f"   {rec.explanation}")
        if rec.capabilities:
            lines.append(f"   Capabilities: {', '.join(rec.capabilities)}")
        lines.append("")

    if not result.recommendations:
        lines.append("  No compatible models found for your hardware.")
        lines.append("  Consider using cloud providers instead.")

    return "\n".join(lines)


# CLI usage
if __name__ == "__main__":
    import sys

    from .hardware_detector import detect_hardware

    logging.basicConfig(level=logging.INFO)

    print("Detecting hardware and generating recommendations...\n")

    hardware = detect_hardware()
    recommender = ModelRecommender()
    result = recommender.recommend(hardware)

    print(format_recommendations(result))

    sys.exit(0)
