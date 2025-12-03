"""
API Clients for Different AI Providers

Provides unified interface for:
- Anthropic (Claude)
- Google (Gemini)
- OpenAI (GPT)
"""

import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class Message:
    """Represents a chat message"""
    role: str  # "user", "assistant", "system"
    content: str


@dataclass
class APIResponse:
    """Unified response format from all providers"""
    content: str
    model: str
    provider: str
    tokens_used: Dict[str, int]  # {"input": N, "output": M}
    cost: Optional[float] = None
    latency_ms: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseAIClient(ABC):
    """Base class for AI provider clients"""

    def __init__(self, api_key: str, model_config: Dict[str, Any]):
        """
        Initialize AI client

        Args:
            api_key: API key for the provider
            model_config: Model configuration from models.json
        """
        self.api_key = api_key
        self.model_config = model_config
        self.provider = model_config.get("provider", "unknown")

    @abstractmethod
    def send_request(
        self,
        messages: List[Message],
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> APIResponse:
        """
        Send request to AI provider

        Args:
            messages: List of messages (conversation history)
            model: Model ID to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 - 1.0)
            **kwargs: Provider-specific parameters

        Returns:
            APIResponse object
        """
        pass

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate cost based on token usage

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost in USD
        """
        costs = self.model_config.get("cost_per_1m_tokens", {})
        input_cost_per_m = costs.get("input", 0)
        output_cost_per_m = costs.get("output", 0)

        input_cost = (input_tokens / 1_000_000) * input_cost_per_m
        output_cost = (output_tokens / 1_000_000) * output_cost_per_m

        return input_cost + output_cost


class AnthropicClient(BaseAIClient):
    """Client for Anthropic Claude API"""

    def __init__(self, api_key: str, model_config: Dict[str, Any]):
        super().__init__(api_key, model_config)

        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError(
                "anthropic package not installed. "
                "Install with: pip install anthropic"
            )

    def send_request(
        self,
        messages: List[Message],
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> APIResponse:
        """Send request to Anthropic API"""

        import time
        start_time = time.time()

        # Convert messages to Anthropic format
        api_messages = []
        system_message = None

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                api_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        # Prepare request parameters
        request_params = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": api_messages
        }

        if system_message:
            request_params["system"] = system_message

        # Add any additional kwargs
        request_params.update(kwargs)

        try:
            # Make API call
            response = self.client.messages.create(**request_params)

            latency_ms = (time.time() - start_time) * 1000

            # Extract response data
            content = response.content[0].text
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            # Calculate cost
            cost = self.calculate_cost(input_tokens, output_tokens)

            return APIResponse(
                content=content,
                model=model,
                provider="anthropic",
                tokens_used={"input": input_tokens, "output": output_tokens},
                cost=cost,
                latency_ms=latency_ms,
                metadata={
                    "stop_reason": response.stop_reason,
                    "response_id": response.id
                }
            )

        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {str(e)}")


class GoogleClient(BaseAIClient):
    """Client for Google Gemini API"""

    def __init__(self, api_key: str, model_config: Dict[str, Any]):
        super().__init__(api_key, model_config)

        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.genai = genai
        except ImportError:
            raise ImportError(
                "google-generativeai package not installed. "
                "Install with: pip install google-generativeai"
            )

    def send_request(
        self,
        messages: List[Message],
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> APIResponse:
        """Send request to Google Gemini API"""

        import time
        start_time = time.time()

        # Create model instance
        gemini_model = self.genai.GenerativeModel(model)

        # Convert messages to Gemini format
        # Gemini uses a different format - combine messages into conversation
        conversation_parts = []
        system_instruction = None

        for msg in messages:
            if msg.role == "system":
                system_instruction = msg.content
            elif msg.role == "user":
                conversation_parts.append({"role": "user", "parts": [msg.content]})
            elif msg.role == "assistant":
                conversation_parts.append({"role": "model", "parts": [msg.content]})

        # For simple single-turn requests
        if len(conversation_parts) == 1 and conversation_parts[0]["role"] == "user":
            prompt = conversation_parts[0]["parts"][0]
            if system_instruction:
                prompt = f"{system_instruction}\n\n{prompt}"

            # Generation config
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }

            try:
                # Make API call
                response = gemini_model.generate_content(
                    prompt,
                    generation_config=generation_config
                )

                latency_ms = (time.time() - start_time) * 1000

                # Extract response
                content = response.text

                # Gemini doesn't return token counts in all responses
                # We'll estimate or use default values
                input_tokens = len(prompt.split()) * 1.3  # Rough estimate
                output_tokens = len(content.split()) * 1.3

                # Calculate cost
                cost = self.calculate_cost(int(input_tokens), int(output_tokens))

                return APIResponse(
                    content=content,
                    model=model,
                    provider="google",
                    tokens_used={"input": int(input_tokens), "output": int(output_tokens)},
                    cost=cost,
                    latency_ms=latency_ms,
                    metadata={
                        "finish_reason": getattr(response.candidates[0], "finish_reason", None) if response.candidates else None
                    }
                )

            except Exception as e:
                raise RuntimeError(f"Google Gemini API error: {str(e)}")

        else:
            # Multi-turn conversation
            chat = gemini_model.start_chat(history=conversation_parts[:-1])
            last_message = conversation_parts[-1]["parts"][0]

            try:
                response = chat.send_message(last_message)
                latency_ms = (time.time() - start_time) * 1000

                content = response.text
                input_tokens = len(last_message.split()) * 1.3
                output_tokens = len(content.split()) * 1.3
                cost = self.calculate_cost(int(input_tokens), int(output_tokens))

                return APIResponse(
                    content=content,
                    model=model,
                    provider="google",
                    tokens_used={"input": int(input_tokens), "output": int(output_tokens)},
                    cost=cost,
                    latency_ms=latency_ms
                )

            except Exception as e:
                raise RuntimeError(f"Google Gemini API error: {str(e)}")


class OpenAIClient(BaseAIClient):
    """Client for OpenAI API"""

    def __init__(self, api_key: str, model_config: Dict[str, Any]):
        super().__init__(api_key, model_config)

        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError(
                "openai package not installed. "
                "Install with: pip install openai"
            )

    def send_request(
        self,
        messages: List[Message],
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> APIResponse:
        """Send request to OpenAI API"""

        import time
        start_time = time.time()

        # Convert messages to OpenAI format
        api_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        try:
            # Make API call
            response = self.client.chat.completions.create(
                model=model,
                messages=api_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )

            latency_ms = (time.time() - start_time) * 1000

            # Extract response data
            content = response.choices[0].message.content
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens

            # Calculate cost
            cost = self.calculate_cost(input_tokens, output_tokens)

            return APIResponse(
                content=content,
                model=model,
                provider="openai",
                tokens_used={"input": input_tokens, "output": output_tokens},
                cost=cost,
                latency_ms=latency_ms,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "response_id": response.id
                }
            )

        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")


def create_client(provider: str, api_key: str, model_config: Dict[str, Any]) -> BaseAIClient:
    """
    Factory function to create appropriate AI client

    Args:
        provider: Provider name ("anthropic", "google", "openai")
        api_key: API key for the provider
        model_config: Model configuration

    Returns:
        Appropriate client instance

    Raises:
        ValueError: If provider is not supported
    """
    clients = {
        "anthropic": AnthropicClient,
        "google": GoogleClient,
        "openai": OpenAIClient,
    }

    client_class = clients.get(provider.lower())

    if not client_class:
        raise ValueError(
            f"Unsupported provider: {provider}\n"
            f"Supported providers: {', '.join(clients.keys())}"
        )

    return client_class(api_key, model_config)


# Example usage
if __name__ == "__main__":
    # This is for testing purposes
    print("API Clients module - ready for import")
    print("Supported providers: Anthropic, Google (Gemini), OpenAI")
