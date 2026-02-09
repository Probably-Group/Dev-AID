"""
Tests for Local LLM Client

Tests hardware detection, model recommendations, and local inference client.
"""

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

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
