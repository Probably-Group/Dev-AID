"""
Tests for Local LLM Client

Tests hardware detection, model recommendations, and local inference client.
"""

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from router.api_clients import Message
from router.auth_detector import AuthCredentials
from router.hardware_detector import (
    GPUInfo,
    GPUVendor,
    HardwareDetector,
    HardwareProfile,
    create_manual_profile,
    detect_hardware,
)
from router.local_client import LocalLLMClient, create_local_auth, detect_local_server
from router.model_recommender import (
    ModelRecommendation,
    ModelRecommender,
    RecommendationResult,
    format_recommendations,
)

# ============================================================================
# Hardware Detection Tests
# ============================================================================


class TestHardwareProfile:
    """Tests for HardwareProfile dataclass"""

    def test_available_vram_with_gpu(self):
        """Test VRAM detection with GPU present"""
        gpu = GPUInfo(vendor=GPUVendor.NVIDIA, name="RTX 4090", vram_gb=24.0)
        profile = HardwareProfile(
            cpu_name="Test CPU",
            cpu_cores=8,
            cpu_threads=16,
            ram_gb=32.0,
            gpu=gpu,
            os_name="Linux",
            os_version="5.0",
            architecture="x86_64",
        )
        assert profile.available_vram_gb == 24.0

    def test_available_vram_no_gpu(self):
        """Test VRAM detection without GPU"""
        gpu = GPUInfo(vendor=GPUVendor.NONE, name="None", vram_gb=0.0)
        profile = HardwareProfile(
            cpu_name="Test CPU",
            cpu_cores=8,
            cpu_threads=16,
            ram_gb=32.0,
            gpu=gpu,
            os_name="Linux",
            os_version="5.0",
            architecture="x86_64",
        )
        assert profile.available_vram_gb == 0.0

    def test_has_gpu(self):
        """Test GPU detection"""
        gpu = GPUInfo(vendor=GPUVendor.NVIDIA, name="RTX 4090", vram_gb=24.0)
        profile = HardwareProfile(
            cpu_name="Test CPU",
            cpu_cores=8,
            cpu_threads=16,
            ram_gb=32.0,
            gpu=gpu,
            os_name="Linux",
            os_version="5.0",
            architecture="x86_64",
        )
        assert profile.has_gpu is True

    def test_no_gpu(self):
        """Test no GPU case"""
        gpu = GPUInfo(vendor=GPUVendor.NONE, name="None", vram_gb=0.0)
        profile = HardwareProfile(
            cpu_name="Test CPU",
            cpu_cores=8,
            cpu_threads=16,
            ram_gb=32.0,
            gpu=gpu,
            os_name="Linux",
            os_version="5.0",
            architecture="x86_64",
        )
        assert profile.has_gpu is False

    def test_is_apple_silicon(self):
        """Test Apple Silicon detection"""
        gpu = GPUInfo(vendor=GPUVendor.APPLE, name="M2 Max", vram_gb=32.0, metal_supported=True)
        profile = HardwareProfile(
            cpu_name="Apple M2 Max",
            cpu_cores=12,
            cpu_threads=12,
            ram_gb=32.0,
            gpu=gpu,
            os_name="Darwin",
            os_version="23.0.0",
            architecture="arm64",
        )
        assert profile.is_apple_silicon is True

    @pytest.mark.parametrize(
        "vram,expected_tier",
        [
            (0, "cpu_only"),
            (3, "entry"),
            (14, "mid"),
            (20, "high"),
            (48, "pro"),
            (80, "enterprise"),
        ],
    )
    def test_recommended_tier(self, vram: float, expected_tier: str):
        """Test tier recommendation based on VRAM"""
        gpu = GPUInfo(vendor=GPUVendor.NVIDIA, name="Test GPU", vram_gb=vram)
        profile = HardwareProfile(
            cpu_name="Test CPU",
            cpu_cores=8,
            cpu_threads=16,
            ram_gb=32.0,
            gpu=gpu,
            os_name="Linux",
            os_version="5.0",
            architecture="x86_64",
        )
        assert profile.recommended_tier == expected_tier


class TestHardwareDetector:
    """Tests for HardwareDetector class"""

    def test_detect_returns_profile(self):
        """Test that detect returns a HardwareProfile"""
        detector = HardwareDetector()
        profile = detector.detect()
        assert isinstance(profile, HardwareProfile)
        assert profile.cpu_name is not None
        assert profile.ram_gb > 0

    @patch("router.hardware_detector.subprocess.run")
    def test_nvidia_gpu_detection(self, mock_run):
        """Test NVIDIA GPU detection via nvidia-smi"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="NVIDIA GeForce RTX 4090, 24576, 535.154.05",
        )

        detector = HardwareDetector()
        gpu = detector._detect_nvidia_gpu()

        assert gpu is not None
        assert gpu.vendor == GPUVendor.NVIDIA
        assert "RTX 4090" in gpu.name
        assert gpu.vram_gb == 24.0

    @patch("router.hardware_detector.subprocess.run")
    def test_nvidia_gpu_not_found(self, mock_run):
        """Test when nvidia-smi is not available"""
        mock_run.side_effect = FileNotFoundError("nvidia-smi not found")

        detector = HardwareDetector()
        gpu = detector._detect_nvidia_gpu()

        assert gpu is None


class TestManualProfile:
    """Tests for manual profile creation"""

    def test_create_manual_profile_nvidia(self):
        """Test creating manual profile for NVIDIA GPU"""
        profile = create_manual_profile(vram_gb=24.0, ram_gb=32.0, gpu_vendor="nvidia")

        assert profile.available_vram_gb == 24.0
        assert profile.ram_gb == 32.0
        assert profile.gpu.vendor == GPUVendor.NVIDIA

    def test_create_manual_profile_apple(self):
        """Test creating manual profile for Apple Silicon"""
        profile = create_manual_profile(vram_gb=48.0, ram_gb=64.0, gpu_vendor="apple")

        assert profile.gpu.vendor == GPUVendor.APPLE

    def test_create_manual_profile_cpu_only(self):
        """Test creating manual profile for CPU-only"""
        profile = create_manual_profile(vram_gb=0.0, ram_gb=32.0, gpu_vendor="none")

        assert profile.gpu.vendor == GPUVendor.NONE
        assert profile.recommended_tier == "cpu_only"


# ============================================================================
# Model Recommender Tests
# ============================================================================


class TestModelRecommender:
    """Tests for ModelRecommender class"""

    @pytest.fixture
    def mock_models_config(self) -> Dict[str, Any]:
        """Create mock models configuration"""
        return {
            "local": {
                "enabled": True,
                "provider": "local",
                "models": {
                    "phi-4-mini": {
                        "id": "phi4-mini",
                        "context_window": 16384,
                        "vram_min_gb": 3,
                        "score": 58,
                        "tier": "entry",
                        "capabilities": ["code", "general"],
                    },
                    "codestral-22b": {
                        "id": "codestral:22b",
                        "context_window": 32768,
                        "vram_min_gb": 14,
                        "score": 72,
                        "tier": "mid",
                        "capabilities": ["code", "analysis"],
                    },
                    "qwen2.5-coder-32b": {
                        "id": "qwen2.5-coder:32b",
                        "context_window": 32768,
                        "vram_min_gb": 20,
                        "score": 68,
                        "tier": "high",
                        "capabilities": ["code", "reasoning"],
                    },
                },
            }
        }

    def test_recommend_for_entry_hardware(self, mock_models_config):
        """Test recommendations for entry-level hardware"""
        recommender = ModelRecommender(mock_models_config)
        profile = create_manual_profile(vram_gb=4.0, ram_gb=16.0)

        result = recommender.recommend(profile)

        assert isinstance(result, RecommendationResult)
        assert len(result.recommendations) > 0
        # Entry hardware should get phi-4-mini as optimal
        optimal = [r for r in result.recommendations if r.compatibility == "optimal"]
        assert len(optimal) > 0

    def test_recommend_for_high_hardware(self, mock_models_config):
        """Test recommendations for high-end hardware"""
        recommender = ModelRecommender(mock_models_config)
        profile = create_manual_profile(vram_gb=24.0, ram_gb=32.0)

        result = recommender.recommend(profile)

        assert len(result.recommendations) >= 3
        # Should have all models as optimal or good
        optimal_or_good = [
            r for r in result.recommendations if r.compatibility in ("optimal", "good")
        ]
        assert len(optimal_or_good) == 3

    def test_recommend_for_cpu_only(self, mock_models_config):
        """Test recommendations for CPU-only systems"""
        recommender = ModelRecommender(mock_models_config)
        profile = create_manual_profile(vram_gb=0.0, ram_gb=32.0, gpu_vendor="none")

        result = recommender.recommend(profile)

        assert len(result.warnings) > 0
        assert "No GPU detected" in result.warnings[0]

    def test_get_best_model(self, mock_models_config):
        """Test getting single best model"""
        recommender = ModelRecommender(mock_models_config)
        profile = create_manual_profile(vram_gb=24.0, ram_gb=32.0)

        best = recommender.get_best_model(profile)

        assert best is not None
        assert isinstance(best, ModelRecommendation)
        assert best.compatibility in ("optimal", "good")

    def test_format_recommendations(self, mock_models_config):
        """Test human-readable formatting"""
        recommender = ModelRecommender(mock_models_config)
        profile = create_manual_profile(vram_gb=24.0, ram_gb=32.0)

        result = recommender.recommend(profile)
        formatted = format_recommendations(result)

        assert isinstance(formatted, str)
        assert "Hardware Tier:" in formatted
        assert "RECOMMENDED MODELS:" in formatted

    # ------------------------------------------------------------------
    # supports_tool_calling filter (issue #142)
    # ------------------------------------------------------------------

    @pytest.fixture
    def mock_models_config_mixed_tools(self) -> Dict[str, Any]:
        """Models config where only some entries declare tool-calling support."""
        return {
            "local": {
                "enabled": True,
                "provider": "local",
                "models": {
                    "no-tools": {
                        "id": "no-tools:7b",
                        "context_window": 8192,
                        "vram_min_gb": 4,
                        "score": 50,
                        "tier": "entry",
                        "capabilities": ["code"],
                        # supports_tool_calling intentionally omitted →
                        # treated as False
                    },
                    "tools-mid": {
                        "id": "tools-mid:14b",
                        "context_window": 16384,
                        "vram_min_gb": 10,
                        "score": 70,
                        "tier": "mid",
                        "capabilities": ["code", "reasoning"],
                        "supports_tool_calling": True,
                    },
                    "tools-high": {
                        "id": "tools-high:32b",
                        "context_window": 32768,
                        "vram_min_gb": 20,
                        "score": 80,
                        "tier": "high",
                        "capabilities": ["code", "reasoning", "complex_tasks"],
                        "supports_tool_calling": True,
                    },
                },
            }
        }

    def test_default_includes_models_without_tool_calling(self, mock_models_config_mixed_tools):
        """Without requires_tool_calling, all hardware-fitting models are returned."""
        recommender = ModelRecommender(mock_models_config_mixed_tools)
        profile = create_manual_profile(vram_gb=24.0, ram_gb=32.0)

        result = recommender.recommend(profile)
        names = {r.model_name for r in result.recommendations}
        assert "no-tools" in names
        assert "tools-mid" in names
        assert "tools-high" in names

    def test_requires_tool_calling_excludes_unflagged_models(self, mock_models_config_mixed_tools):
        """With requires_tool_calling=True, models without the flag are filtered out."""
        recommender = ModelRecommender(mock_models_config_mixed_tools)
        profile = create_manual_profile(vram_gb=24.0, ram_gb=32.0)

        result = recommender.recommend(profile, requires_tool_calling=True)
        names = {r.model_name for r in result.recommendations}
        assert "no-tools" not in names
        assert "tools-mid" in names
        assert "tools-high" in names
        # Notes should explain what we filtered on
        assert any("Tool-calling required" in n for n in result.notes)
        # All returned recommendations carry the flag
        assert all(r.supports_tool_calling for r in result.recommendations)

    def test_requires_tool_calling_yields_empty_when_no_match(self, mock_models_config_mixed_tools):
        """If no model in the candidate set has the flag, returns an empty result."""
        config_no_tools = {
            "local": {
                "enabled": True,
                "provider": "local",
                "models": {
                    "no-tools": mock_models_config_mixed_tools["local"]["models"]["no-tools"],
                },
            }
        }
        recommender = ModelRecommender(config_no_tools)
        profile = create_manual_profile(vram_gb=24.0, ram_gb=32.0)

        result = recommender.recommend(profile, requires_tool_calling=True)
        assert result.recommendations == []

    def test_get_best_model_forwards_tool_calling_filter(self, mock_models_config_mixed_tools):
        """get_best_model honors the filter and never returns an unflagged model."""
        recommender = ModelRecommender(mock_models_config_mixed_tools)
        profile = create_manual_profile(vram_gb=24.0, ram_gb=32.0)

        best = recommender.get_best_model(profile, requires_tool_calling=True)
        assert best is not None
        assert best.supports_tool_calling
        assert best.model_name in ("tools-mid", "tools-high")

    def test_get_model_by_tier_forwards_tool_calling_filter(self, mock_models_config_mixed_tools):
        """get_model_by_tier honors the filter when picking a tier-specific model."""
        recommender = ModelRecommender(mock_models_config_mixed_tools)
        profile = create_manual_profile(vram_gb=24.0, ram_gb=32.0)

        # Tier "entry" only has the no-tools model, so the filtered call
        # returns None — proving the filter is applied before the tier match.
        no_match = recommender.get_model_by_tier(profile, "entry", requires_tool_calling=True)
        assert no_match is None

        # Tier "mid" has tools-mid which is flagged.
        match = recommender.get_model_by_tier(profile, "mid", requires_tool_calling=True)
        assert match is not None
        assert match.model_name == "tools-mid"


# ============================================================================
# Local Client Tests
# ============================================================================


class TestLocalLLMClient:
    """Tests for LocalLLMClient class"""

    @pytest.fixture
    def mock_local_auth(self) -> AuthCredentials:
        """Create mock local auth credentials"""
        return AuthCredentials(
            provider="local",
            auth_type="local",
            credentials={
                "backend": "ollama",
                "base_url": "http://localhost:11434/v1",
            },
            source="test fixture",
        )

    @pytest.fixture
    def mock_local_config(self) -> Dict[str, Any]:
        """Create mock local model config"""
        return {
            "provider": "local",
            "model_id": "phi4-mini",
            "cost_per_1m_tokens": {"input": 0.0, "output": 0.0},
        }

    def test_client_initialization(self, mock_local_auth, mock_local_config):
        """Test client initializes correctly"""
        with patch("openai.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client

            client = LocalLLMClient(mock_local_auth, mock_local_config)

            assert client.backend == "ollama"
            assert client.base_url == "http://localhost:11434/v1"
            assert client.provider == "local"
            mock_openai.assert_called_once()

    def test_calculate_cost_always_zero(self, mock_local_auth, mock_local_config):
        """Test that local models always have zero cost"""
        with patch("openai.OpenAI"):
            client = LocalLLMClient(mock_local_auth, mock_local_config)

        cost = client.calculate_cost(1000000, 1000000)
        assert cost == 0.0

    def test_create_local_auth(self):
        """Test creating local auth credentials"""
        auth = create_local_auth("ollama")

        assert auth.provider == "local"
        assert auth.auth_type == "local"
        assert auth.credentials["backend"] == "ollama"
        assert "11434" in auth.credentials["base_url"]

    def test_create_local_auth_custom_url(self):
        """Test creating local auth with custom URL"""
        auth = create_local_auth("lm_studio", "http://192.168.1.100:1234/v1")

        assert auth.credentials["base_url"] == "http://192.168.1.100:1234/v1"


class TestDetectLocalServer:
    """Tests for local server detection"""

    @patch("router.local_client.requests.get")
    def test_detect_ollama_running(self, mock_get):
        """Test detecting running Ollama server"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = detect_local_server()

        assert result is not None
        assert result["backend"] == "ollama"
        assert result["port"] == 11434

    @patch("router.local_client.requests.get")
    def test_detect_no_server(self, mock_get):
        """Test when no server is running"""
        mock_get.side_effect = Exception("Connection refused")

        result = detect_local_server()

        assert result is None


# ============================================================================
# Integration Tests
# ============================================================================


class TestLocalLLMIntegration:
    """Integration tests for local LLM support"""

    def test_hardware_to_recommendations_flow(self):
        """Test full flow from hardware detection to recommendations"""
        # Detect hardware
        profile = detect_hardware()
        assert isinstance(profile, HardwareProfile)

        # Get recommendations
        recommender = ModelRecommender()
        result = recommender.recommend(profile)

        assert isinstance(result, RecommendationResult)
        assert result.hardware_tier is not None

    def test_auth_detector_includes_local(self):
        """Test that auth detector can check for local servers"""
        from router.auth_detector import AuthDetector

        detector = AuthDetector()
        all_auth = detector.detect_all()

        assert "local" in all_auth
        # May or may not find a running server
        assert all_auth["local"] is None or isinstance(all_auth["local"], AuthCredentials)

    def test_create_client_factory_local(self):
        """Test client factory creates LocalLLMClient for local provider"""
        from router.api_clients import create_client

        with patch("openai.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client

            auth = create_local_auth("ollama")
            config = {"provider": "local"}

            client = create_client("local", auth, config)

            assert isinstance(client, LocalLLMClient)


# ============================================================================
# Tool Calling Tests (issue #140)
# ============================================================================


class TestLocalLLMToolCalling:
    """Tests for native tool-calling support on LocalLLMClient.

    These tests cover the issue #140 contract: when a tool-capable local
    model emits ``message.tool_calls``, ``LocalLLMClient.send_request``
    must surface them on ``APIResponse.tool_calls`` (instead of dropping
    them on the floor as the pre-#140 implementation did). The parser
    handles both the OpenAI SDK pydantic shape and the bare-dict shape
    that some Ollama-compat servers return.
    """

    @pytest.fixture
    def mock_local_auth(self) -> AuthCredentials:
        return AuthCredentials(
            provider="local",
            auth_type="local",
            credentials={
                "backend": "ollama",
                "base_url": "http://localhost:11434/v1",
            },
            source="test fixture",
        )

    @pytest.fixture
    def mock_local_config(self) -> Dict[str, Any]:
        return {
            "provider": "local",
            "model_id": "llama3.1",
            "cost_per_1m_tokens": {"input": 0.0, "output": 0.0},
        }

    @staticmethod
    def _make_openai_style_response(tool_calls=None, content=""):
        """Build a MagicMock that mimics openai SDK ChatCompletion shape."""
        usage = MagicMock()
        usage.prompt_tokens = 10
        usage.completion_tokens = 5

        message = MagicMock()
        message.content = content
        message.tool_calls = tool_calls

        choice = MagicMock()
        choice.message = message
        choice.finish_reason = "tool_calls" if tool_calls else "stop"

        response = MagicMock()
        response.choices = [choice]
        response.usage = usage
        response.id = "resp_test"
        return response

    def test_tool_calls_parsed_from_pydantic_shape(self, mock_local_auth, mock_local_config):
        """OpenAI SDK returns pydantic-style objects — parser pulls attributes."""
        with patch("openai.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client

            # Build a pydantic-like tool call (attributes, not dict keys)
            fn = MagicMock()
            fn.name = "get_weather"
            fn.arguments = '{"city": "Prague"}'
            tc = MagicMock()
            tc.id = "call_abc123"
            tc.type = "function"
            tc.function = fn

            mock_client.chat.completions.create.return_value = self._make_openai_style_response(
                tool_calls=[tc]
            )

            client = LocalLLMClient(mock_local_auth, mock_local_config)
            response = client.send_request(
                messages=[Message(role="user", content="weather in Prague?")],
                model="llama3.1",
                tools=[{"type": "function", "function": {"name": "get_weather"}}],
            )

            assert response.tool_calls is not None
            assert len(response.tool_calls) == 1
            call = response.tool_calls[0]
            assert call["id"] == "call_abc123"
            assert call["type"] == "function"
            assert call["function"]["name"] == "get_weather"
            assert call["function"]["arguments"] == '{"city": "Prague"}'
            # finish_reason should propagate through metadata
            assert response.metadata["finish_reason"] == "tool_calls"

    def test_tool_calls_parsed_from_dict_shape(self, mock_local_auth, mock_local_config):
        """Some Ollama compat servers return tool_calls as plain dicts."""
        with patch("openai.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client

            tool_call_dict = {
                "id": "call_xyz",
                "type": "function",
                "function": {
                    "name": "list_files",
                    "arguments": '{"path": "/tmp"}',
                },
            }

            mock_client.chat.completions.create.return_value = self._make_openai_style_response(
                tool_calls=[tool_call_dict]
            )

            client = LocalLLMClient(mock_local_auth, mock_local_config)
            response = client.send_request(
                messages=[Message(role="user", content="list /tmp")],
                model="llama3.1",
                tools=[{"type": "function", "function": {"name": "list_files"}}],
            )

            assert response.tool_calls is not None
            assert response.tool_calls[0]["id"] == "call_xyz"
            assert response.tool_calls[0]["function"]["name"] == "list_files"

    def test_no_tool_calls_yields_none(self, mock_local_auth, mock_local_config):
        """When the model doesn't call any tool, tool_calls should be None."""
        with patch("openai.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client

            mock_client.chat.completions.create.return_value = self._make_openai_style_response(
                tool_calls=None, content="Hello!"
            )

            client = LocalLLMClient(mock_local_auth, mock_local_config)
            response = client.send_request(
                messages=[Message(role="user", content="hi")],
                model="llama3.1",
            )

            assert response.content == "Hello!"
            assert response.tool_calls is None

    def test_chat_completion_with_tools_forwards_tools(self, mock_local_auth, mock_local_config):
        """The convenience wrapper must pass `tools` through to the API call."""
        with patch("openai.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client

            mock_client.chat.completions.create.return_value = self._make_openai_style_response(
                tool_calls=None, content="ok"
            )

            client = LocalLLMClient(mock_local_auth, mock_local_config)
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "ping",
                        "description": "ping a host",
                        "parameters": {"type": "object", "properties": {}},
                    },
                }
            ]

            client.chat_completion_with_tools(
                messages=[Message(role="user", content="ping")],
                model="llama3.1",
                tools=tools,
            )

            # Inspect the actual call to chat.completions.create
            _, call_kwargs = mock_client.chat.completions.create.call_args
            assert call_kwargs["tools"] == tools
            assert call_kwargs["model"] == "llama3.1"

    def test_parse_tool_calls_helper_handles_empty(self):
        """Static helper returns None for None and empty list."""
        assert LocalLLMClient._parse_tool_calls(None) is None
        assert LocalLLMClient._parse_tool_calls([]) is None


# ============================================================================
# Structured Output Tests (issue #141)
# ============================================================================


class TestLocalLLMStructuredOutput:
    """Tests for chat_completion_structured — FSM-constrained JSON schema output."""

    @pytest.fixture
    def mock_local_auth(self) -> AuthCredentials:
        return AuthCredentials(
            provider="local",
            auth_type="local",
            credentials={"backend": "ollama", "base_url": "http://localhost:11434/v1"},
            source="test fixture",
        )

    @pytest.fixture
    def mock_local_config(self) -> Dict[str, Any]:
        return {"provider": "local", "cost_per_1m_tokens": {"input": 0.0, "output": 0.0}}

    @staticmethod
    def _make_json_response(content: str = '{"name":"Prague","country":"CZ"}'):
        """Build a mock response that returns valid JSON content."""
        usage = MagicMock()
        usage.prompt_tokens = 20
        usage.completion_tokens = 10
        message = MagicMock()
        message.content = content
        message.tool_calls = None
        choice = MagicMock()
        choice.message = message
        choice.finish_reason = "stop"
        response = MagicMock()
        response.choices = [choice]
        response.usage = usage
        response.id = "resp_struct"
        return response

    def test_schema_forwarded_via_extra_body(self, mock_local_auth, mock_local_config):
        """The JSON schema must be passed via extra_body={'format': schema}."""
        with patch("openai.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.return_value = self._make_json_response()

            client = LocalLLMClient(mock_local_auth, mock_local_config)
            schema = {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            }

            client.chat_completion_structured(
                messages=[Message(role="user", content="Tell me about Prague")],
                model="llama3.1",
                schema=schema,
            )

            _, call_kwargs = mock_client.chat.completions.create.call_args
            assert call_kwargs["extra_body"] == {"format": schema}
            assert call_kwargs["temperature"] == 0.0  # default for structured

    def test_response_content_is_raw_json(self, mock_local_auth, mock_local_config):
        """The APIResponse.content should be the raw JSON string from the model."""
        with patch("openai.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.return_value = self._make_json_response(
                '{"city": "Prague", "population": 1300000}'
            )

            client = LocalLLMClient(mock_local_auth, mock_local_config)
            resp = client.chat_completion_structured(
                messages=[Message(role="user", content="Prague info")],
                model="llama3.1",
                schema={"type": "object", "properties": {"city": {"type": "string"}}},
            )

            import json

            parsed = json.loads(resp.content)
            assert parsed["city"] == "Prague"
            assert parsed["population"] == 1300000

    def test_default_temperature_is_zero(self, mock_local_auth, mock_local_config):
        """Structured output defaults to temperature=0.0 for determinism."""
        with patch("openai.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.return_value = self._make_json_response()

            client = LocalLLMClient(mock_local_auth, mock_local_config)
            client.chat_completion_structured(
                messages=[Message(role="user", content="x")],
                model="llama3.1",
                schema={"type": "object"},
            )

            _, call_kwargs = mock_client.chat.completions.create.call_args
            assert call_kwargs["temperature"] == 0.0

    def test_temperature_override(self, mock_local_auth, mock_local_config):
        """Callers can override the temperature."""
        with patch("openai.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.return_value = self._make_json_response()

            client = LocalLLMClient(mock_local_auth, mock_local_config)
            client.chat_completion_structured(
                messages=[Message(role="user", content="x")],
                model="llama3.1",
                schema={"type": "object"},
                temperature=0.5,
            )

            _, call_kwargs = mock_client.chat.completions.create.call_args
            assert call_kwargs["temperature"] == 0.5
