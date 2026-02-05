# Local LLM Developer Guide

Guide for developers who want to extend, customize, or integrate Dev-AID's local LLM support.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface                            │
│    setup-local-llm.sh  │  Python CLI  │  Router Integration │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                  ModelRecommender                            │
│    - Matches hardware to models                              │
│    - Ranks by compatibility (optimal/good/marginal/cpu_only) │
│    - Reads from models.json                                  │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                  HardwareDetector                            │
│    - Detects GPU (NVIDIA, Apple Silicon, AMD)                │
│    - Detects VRAM and system RAM                             │
│    - Returns HardwareProfile dataclass                       │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                   LocalLLMClient                             │
│    - Implements BaseAIClient interface                       │
│    - Uses OpenAI SDK with custom base_url                    │
│    - Supports Ollama, LM Studio, llama.cpp                   │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│              Local Inference Backends                        │
│    Ollama (11434) │ LM Studio (1234) │ llama.cpp (8080)     │
└─────────────────────────────────────────────────────────────┘
```

## Extension Points

### 1. Adding New Models

Add models to `.dev-aid/config/models.json`:

```json
{
  "local": {
    "models": {
      "your-new-model": {
        "id": "model-name:tag",        // Ollama model ID
        "context_window": 32768,
        "capabilities": ["code", "analysis"],
        "vram_min_gb": 16,             // Minimum VRAM required
        "score": 70,                   // Benchmark score (0-100)
        "tier": "mid",                 // entry/mid/high/pro/enterprise
        "cost_per_1m_tokens": {
          "input": 0.0,
          "output": 0.0
        }
      }
    }
  }
}
```

**Key fields:**
- `id`: Model identifier used by the backend (e.g., `ollama pull <id>`)
- `vram_min_gb`: Minimum VRAM for acceptable performance
- `score`: Benchmark score for ranking (higher = better)
- `tier`: Maps to hardware tier for recommendations

### 2. Adding New Backends

To add a new backend (e.g., vLLM, text-generation-webui):

```python
# In local_client.py

class LocalLLMClient(BaseAIClient):
    DEFAULT_PORTS = {
        "ollama": 11434,
        "lm_studio": 1234,
        "llama_cpp": 8080,
        "vllm": 8000,           # Add your backend
        "tgw": 5000,            # text-generation-webui
    }
```

If your backend is NOT OpenAI-compatible, override the `send_request` method:

```python
class VLLMClient(LocalLLMClient):
    """Custom client for vLLM with non-standard API"""

    def send_request(self, messages, model, max_tokens=4096, **kwargs):
        # Custom API call implementation
        response = requests.post(
            f"{self.base_url}/generate",
            json={
                "prompt": self._format_prompt(messages),
                "max_tokens": max_tokens,
            }
        )
        # Parse and return APIResponse
```

### 3. Custom Hardware Detection

Extend `HardwareDetector` for specialized hardware:

```python
class HardwareDetector:
    def _detect_custom_gpu(self) -> Optional[GPUInfo]:
        """Detect custom/specialized GPU (e.g., Intel Arc, TPU)"""
        try:
            # Your detection logic here
            result = subprocess.run(
                ["your-detection-tool", "--query"],
                capture_output=True,
                text=True,
            )
            # Parse and return GPUInfo
        except Exception:
            return None

    def _detect_gpu(self) -> Optional[GPUInfo]:
        # Add to detection chain
        custom = self._detect_custom_gpu()
        if custom:
            return custom
        # ... existing detection logic
```

### 4. Custom Recommendation Logic

Override `ModelRecommender` for custom matching:

```python
class CustomRecommender(ModelRecommender):
    def recommend(self, hardware: HardwareProfile) -> RecommendationResult:
        # Add custom logic before standard recommendations
        if hardware.gpu and "RTX 5090" in hardware.gpu.name:
            # Special handling for next-gen GPUs
            pass

        # Call parent implementation
        result = super().recommend(hardware)

        # Post-process recommendations
        for rec in result.recommendations:
            if "code" in rec.capabilities:
                rec.score += 10  # Boost coding models

        return result
```

## Integration Patterns

### Pattern 1: Direct API Usage

```python
from router.local_client import LocalLLMClient, create_local_auth
from router.api_clients import Message

# Create auth for Ollama
auth = create_local_auth("ollama")

# Create client
client = LocalLLMClient(auth, {"provider": "local"})

# Verify connection
if client.verify_connection():
    # Send request
    response = client.send_request(
        messages=[Message(role="user", content="Write a hello world in Python")],
        model="qwen2.5-coder:32b",
        max_tokens=1000,
    )
    print(response.content)
    print(f"Cost: ${response.cost}")  # Always 0.0 for local
```

### Pattern 2: With Hardware Detection

```python
from router.hardware_detector import detect_hardware
from router.model_recommender import ModelRecommender

# Auto-detect hardware
hardware = detect_hardware()
print(f"Detected: {hardware.gpu.name} with {hardware.available_vram_gb}GB VRAM")

# Get model recommendations
recommender = ModelRecommender()
result = recommender.recommend(hardware)

# Use best recommended model
best_model = result.recommendations[0]
print(f"Recommended: {best_model.model_name} ({best_model.compatibility})")
```

### Pattern 3: Factory Pattern Integration

```python
from router.api_clients import create_client
from router.auth_detector import AuthDetector

# Auto-detect local server
detector = AuthDetector()
local_auth = detector.detect_local_auth()

if local_auth:
    # Create client via factory
    client = create_client("local", local_auth, {"provider": "local"})
    # Use client...
else:
    print("No local server running. Start Ollama with: ollama serve")
```

### Pattern 4: Router Integration

The local client integrates with Dev-AID's router for intelligent routing:

```python
# In routing.json
{
  "modes": {
    "ensemble": {
      "task_routes": {
        "simple_code": "local",          // Route simple tasks to local
        "complex_reasoning": "claude-opus" // Keep complex tasks in cloud
      }
    }
  }
}
```

## Customization Examples

### Example 1: Custom Model Scoring

```python
def calculate_model_score(model_config: dict, hardware: HardwareProfile) -> float:
    """Custom scoring algorithm"""
    base_score = model_config.get("score", 50)

    # Bonus for code-focused models
    if "code" in model_config.get("capabilities", []):
        base_score += 10

    # Penalty if VRAM is tight
    vram_required = model_config.get("vram_min_gb", 0)
    vram_available = hardware.available_vram_gb
    if vram_required > vram_available * 0.8:
        base_score -= 15

    return base_score
```

### Example 2: Environment-Based Configuration

```python
import os

def get_backend_config():
    """Configure backend from environment"""
    return {
        "backend": os.getenv("LOCAL_INFERENCE_BACKEND", "ollama"),
        "base_url": os.getenv("LOCAL_BASE_URL", "http://localhost:11434/v1"),
        "timeout": float(os.getenv("LOCAL_TIMEOUT", "60")),
    }
```

### Example 3: Health Monitoring

```python
import time

class LocalLLMHealthMonitor:
    def __init__(self, client: LocalLLMClient):
        self.client = client
        self.last_check = 0
        self.is_healthy = False

    def check_health(self, interval: float = 30.0) -> bool:
        """Periodic health check with caching"""
        now = time.time()
        if now - self.last_check < interval:
            return self.is_healthy

        self.is_healthy = self.client.verify_connection(timeout=2.0)
        self.last_check = now
        return self.is_healthy
```

## Testing

### Unit Testing with Mocks

```python
from unittest.mock import MagicMock, patch
import pytest

def test_hardware_detection():
    with patch("subprocess.run") as mock_run:
        # Mock nvidia-smi output
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="NVIDIA RTX 4090, 24576, 535.154.05"
        )

        from router.hardware_detector import HardwareDetector
        detector = HardwareDetector()
        gpu = detector._detect_nvidia_gpu()

        assert gpu is not None
        assert gpu.vram_gb == 24.0

def test_local_client_zero_cost():
    """Local models should always have zero cost"""
    with patch("openai.OpenAI"):
        from router.local_client import LocalLLMClient, create_local_auth

        auth = create_local_auth("ollama")
        client = LocalLLMClient(auth, {"provider": "local"})

        cost = client.calculate_cost(1_000_000, 1_000_000)
        assert cost == 0.0
```

### Integration Testing

```python
@pytest.mark.integration
def test_full_local_inference():
    """Test full inference pipeline (requires running Ollama)"""
    from router.local_client import detect_local_server, create_local_auth, LocalLLMClient
    from router.api_clients import Message

    server = detect_local_server()
    if not server:
        pytest.skip("No local server running")

    auth = create_local_auth(server["backend"])
    client = LocalLLMClient(auth, {"provider": "local"})

    response = client.send_request(
        messages=[Message(role="user", content="Say hello")],
        model="phi4-mini",
        max_tokens=50,
    )

    assert len(response.content) > 0
    assert response.cost == 0.0
```

## Best Practices

### 1. Graceful Degradation

```python
def get_best_available_client():
    """Fall back gracefully if local server unavailable"""
    from router.local_client import detect_local_server
    from router.auth_detector import AuthDetector

    # Try local first
    local_server = detect_local_server()
    if local_server:
        return create_client("local", ...)

    # Fall back to cloud
    detector = AuthDetector()
    cloud_auth = detector.detect_claude_auth() or detector.detect_openai_auth()
    if cloud_auth:
        return create_client(cloud_auth.provider, cloud_auth, ...)

    raise RuntimeError("No AI provider available")
```

### 2. Model Warmup

```python
def warmup_model(client: LocalLLMClient, model: str):
    """Warm up model to reduce first-request latency"""
    try:
        client.send_request(
            messages=[Message(role="user", content="Hi")],
            model=model,
            max_tokens=1,
        )
    except Exception:
        pass  # Ignore warmup errors
```

### 3. Streaming Support

```python
def stream_response(client: LocalLLMClient, messages, model):
    """Stream responses for better UX"""
    # OpenAI SDK supports streaming
    stream = client.client.chat.completions.create(
        model=model,
        messages=[{"role": m.role, "content": m.content} for m in messages],
        stream=True,
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

## Troubleshooting

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("router.local_client").setLevel(logging.DEBUG)
logging.getLogger("router.hardware_detector").setLevel(logging.DEBUG)
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "Connection refused" | Server not running | Start Ollama: `ollama serve` |
| "Model not found" | Model not downloaded | `ollama pull model-name` |
| "Out of memory" | Insufficient VRAM | Use smaller model or quantization |
| Slow inference | No GPU offloading | Check nvidia-smi during inference |

## Contributing

When contributing to local LLM support:

1. **Add tests** for new functionality
2. **Update models.json** for new models
3. **Document** hardware requirements
4. **Test** on multiple backends (Ollama, LM Studio, llama.cpp)
5. **Follow** existing code patterns

## Resources

- [Ollama API Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [LM Studio Server](https://lmstudio.ai/docs/local-server)
- [llama.cpp Server](https://github.com/ggerganov/llama.cpp/tree/master/examples/server)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
