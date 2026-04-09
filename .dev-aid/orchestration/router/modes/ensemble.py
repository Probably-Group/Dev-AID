"""
Ensemble Mode - Route to best model based on task type
"""

from typing import Any, Dict, Tuple

from ..api_clients import Message, create_client
from ..context_builder import ContextBuilder, build_system_prompt
from ..task_classifier import TaskClassifier, TaskType
from ._protocol import ModeConfigProtocol


class EnsembleMode:
    """Ensemble mode: Intelligent routing based on task type"""

    def __init__(self, config_loader: ModeConfigProtocol, context_builder: ContextBuilder) -> None:
        """
        Initialize ensemble mode

        Args:
            config_loader: ConfigLoader instance
            context_builder: ContextBuilder instance
        """
        self.config = config_loader
        self.context_builder = context_builder
        self.classifier = TaskClassifier()

    def execute(self, request: str, context_size: int = 0, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute request in ensemble mode

        Args:
            request: User request
            context_size: Estimated context size in tokens
            **kwargs: Additional parameters

        Returns:
            Result dictionary
        """
        # Classify task
        task_type, keywords, confidence = self.classifier.classify(request, context_size)

        # Get routing configuration
        routing_config = self.config.get_routing_config()

        # Get recommended model for task type
        recommended_model = self.classifier.get_model_for_task(TaskType(task_type), routing_config)

        # Get model configuration
        model_config = self.config.get_model_config(recommended_model)

        if not model_config:
            # Fallback to default
            recommended_model = self.config.get_default_model()
            model_config = self.config.get_model_config(recommended_model)

        # If even the default model has no config, the install is broken
        # in a way the ensemble path can't recover from. Surface a clear
        # error rather than crash on the next dict access.
        if model_config is None:
            return {
                "success": False,
                "mode": "ensemble",
                "task_type": task_type,
                "error": (
                    f"No model configuration found for '{recommended_model}' or the "
                    f"default model. Check .dev-aid/config/models.json."
                ),
            }

        provider = model_config["provider"]

        # Check if provider is enabled
        is_valid, error = self.config.validate_provider(provider)

        selected_model = recommended_model
        used_fallback = False

        if not is_valid:
            # Use fallback chain
            selected_model, model_config, provider = self._get_fallback_model()
            used_fallback = True

        # Get authentication credentials
        auth = self.config.get_auth_credentials(provider)
        if not auth:
            # Try fallback chain if no auth for selected model
            selected_model, model_config, provider = self._get_fallback_model()
            auth = self.config.get_auth_credentials(provider)
            used_fallback = True

            if not auth:
                return {
                    "success": False,
                    "mode": "ensemble",
                    "task_type": task_type,
                    "error": (
                        "No authentication found for any provider. "
                        "Please configure at least one provider by either: "
                        "(1) Signing in to a provider CLI, or "
                        "(2) Setting API keys in .env"
                    ),
                }

        # Create client
        client = create_client(provider, auth, model_config)

        # Build context
        context = self.context_builder.build_context(prompt=request)

        # Add MCP context if provided
        if "mcp_context" in kwargs and kwargs["mcp_context"]:
            context.mcp_context = kwargs["mcp_context"]

        system_prompt = build_system_prompt(context, self.context_builder)

        # Prepare messages
        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=request),
        ]

        # Get model ID
        model_id = model_config.get("id", selected_model)

        # Execute request
        try:
            response = client.send_request(messages=messages, model=model_id, **kwargs)

            # Get explanation
            explanation = self.classifier.explain_classification(
                TaskType(task_type), keywords, confidence
            )

            return {
                "success": True,
                "mode": "ensemble",
                "task_type": task_type,
                "task_confidence": confidence,
                "explanation": explanation,
                "recommended_model": recommended_model,
                "selected_model": selected_model,
                "used_fallback": used_fallback,
                "provider": provider,
                "response": response.content,
                "tokens_used": response.tokens_used,
                "cost": response.cost,
                "latency_ms": response.latency_ms,
                "metadata": response.metadata,
                "matched_keywords": len(keywords),
            }

        except (RuntimeError, ValueError, ConnectionError, TimeoutError) as e:
            return {
                "success": False,
                "mode": "ensemble",
                "task_type": task_type,
                "selected_model": selected_model,
                "provider": provider,
                "error": str(e),
            }

    def _get_fallback_model(self) -> Tuple[str, Dict[str, Any], str]:
        """
        Get first available model from fallback chain

        Returns:
            Tuple of (model_name, model_config, provider)
        """
        fallback_chain = self.config.get_fallback_chain()

        for model_name in fallback_chain:
            model_config = self.config.get_model_config(model_name)

            if model_config:
                provider = model_config["provider"]
                is_valid, _ = self.config.validate_provider(provider)

                if is_valid:
                    return model_name, model_config, provider

        # Last resort: default model. If even this is missing, raise — the
        # caller's contract is to return a usable triple, not to silently
        # propagate None and crash on the next dict access.
        model_name = self.config.get_default_model()
        model_config = self.config.get_model_config(model_name)
        if model_config is None:
            raise RuntimeError(
                f"No model configuration found for default model '{model_name}'. "
                f"Check .dev-aid/config/models.json."
            )
        provider = model_config["provider"]

        return model_name, model_config, provider

    def get_info(self) -> Dict[str, Any]:
        """Get information about ensemble mode configuration"""
        routing_config = self.config.get_routing_config()
        ensemble_config = routing_config.get("modes", {}).get("ensemble", {})

        task_routes = ensemble_config.get("task_routes", {})

        return {
            "mode": "ensemble",
            "description": "Route to best model based on task type",
            "enabled": ensemble_config.get("enabled", True),
            "routing_strategy": ensemble_config.get("routing_strategy", "semantic"),
            "task_routes": task_routes,
            "fallback_chain": self.config.get_fallback_chain(),
        }

    def estimate_cost_comparison(self, tokens_used: Dict[str, int]) -> Dict[str, float]:
        """
        Estimate cost across all available models

        Args:
            tokens_used: Dict with "input" and "output" token counts

        Returns:
            Dict mapping model names to costs
        """
        costs = {}

        # Get all models from config
        for provider, provider_config in self.config.models.items():
            if not isinstance(provider_config, dict):
                continue

            models = provider_config.get("models", {})

            for short_name, model_config in models.items():
                if not isinstance(model_config, dict):
                    continue

                cost_config = model_config.get("cost_per_1m_tokens", {})
                input_cost = cost_config.get("input", 0)
                output_cost = cost_config.get("output", 0)

                total_cost = (tokens_used["input"] / 1_000_000) * input_cost + (
                    tokens_used["output"] / 1_000_000
                ) * output_cost

                model_name = f"{provider}-{short_name}"
                costs[model_name] = total_cost

        return costs
