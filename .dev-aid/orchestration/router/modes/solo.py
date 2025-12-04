"""
Solo Mode - Single model handles all tasks
"""

from typing import Dict, Any
from ..api_clients import Message, APIResponse, create_client
from ..context_builder import ContextBuilder, build_system_prompt


class SoloMode:
    """Solo mode: Single default model handles everything"""

    def __init__(self, config_loader, context_builder: ContextBuilder):
        """
        Initialize solo mode

        Args:
            config_loader: ConfigLoader instance
            context_builder: ContextBuilder instance
        """
        self.config = config_loader
        self.context_builder = context_builder

    def execute(self, request: str, **kwargs) -> Dict[str, Any]:
        """
        Execute request in solo mode

        Args:
            request: User request
            **kwargs: Additional parameters

        Returns:
            Result dictionary
        """
        # Get default model
        model_name = self.config.get_default_model()
        model_config = self.config.get_model_config(model_name)

        if not model_config:
            raise ValueError(f"Model configuration not found for: {model_name}")

        provider = model_config["provider"]

        # Validate provider
        is_valid, error = self.config.validate_provider(provider)
        if not is_valid:
            raise RuntimeError(error)

        # Get API key
        api_key = self.config.get_api_key(provider)

        # Create client
        client = create_client(provider, api_key, model_config)

        # Build context
        context = self.context_builder.build_context()
        system_prompt = build_system_prompt(context, self.context_builder)

        # Prepare messages
        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=request)
        ]

        # Get model ID
        model_id = model_config.get("id", model_name)

        # Execute request
        try:
            response = client.send_request(
                messages=messages,
                model=model_id,
                **kwargs
            )

            return {
                "success": True,
                "mode": "solo",
                "model": model_name,
                "provider": provider,
                "response": response.content,
                "tokens_used": response.tokens_used,
                "cost": response.cost,
                "latency_ms": response.latency_ms,
                "metadata": response.metadata
            }

        except Exception as e:
            return {
                "success": False,
                "mode": "solo",
                "model": model_name,
                "provider": provider,
                "error": str(e)
            }

    def get_info(self) -> Dict[str, Any]:
        """Get information about solo mode configuration"""
        model_name = self.config.get_default_model()

        return {
            "mode": "solo",
            "description": "Single model handles all tasks",
            "default_model": model_name,
            "enabled": True
        }
