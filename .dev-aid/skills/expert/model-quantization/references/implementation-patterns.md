## 7. Implementation Patterns

### Pattern 1: Secure Model Quantization Pipeline

```python
from pathlib import Path
import subprocess
import hashlib
import structlog

class SecureQuantizer:
    """Secure model quantization with validation."""

    def __init__(self, models_dir: str, llama_cpp_dir: str):
        self.models_dir = Path(models_dir)
        self.quantize_bin = Path(llama_cpp_dir) / "quantize"
        if not self.quantize_bin.exists():
            raise FileNotFoundError("llama.cpp quantize binary not found")

    def quantize(self, input_model: str, output_name: str, quantization: str = "Q4_K_M") -> str:
        """Quantize model with validation."""
        input_path = self.models_dir / input_model
        output_path = self.models_dir / output_name

        # Validate
        if not input_path.exists():
            raise FileNotFoundError(f"Model not found: {input_path}")
        valid_types = ["Q4_0", "Q4_K_S", "Q4_K_M", "Q5_K_S", "Q5_K_M", "Q6_K", "Q8_0"]
        if quantization not in valid_types:
            raise ValueError(f"Invalid quantization: {quantization}")

        # Run quantization
        result = subprocess.run(
            [str(self.quantize_bin), str(input_path), str(output_path), quantization],
            capture_output=True, text=True, timeout=3600
        )

        if result.returncode != 0:
            raise QuantizationError(f"Quantization failed: {result.stderr}")

        # Save checksum
        checksum = self._calculate_checksum(output_path)
        output_path.with_suffix(".sha256").write_text(f"{checksum}  {output_path.name}")

        return str(output_path)

    def _calculate_checksum(self, path: Path) -> str:
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
```

### Pattern 2: Quality Benchmarking

```python
class QuantizationBenchmark:
    """Benchmark quantization quality."""

    def __init__(self, test_prompts: list[str]):
        self.test_prompts = test_prompts

    def benchmark(self, model_path: str) -> dict:
        from llama_cpp import Llama
        llm = Llama(model_path=model_path, n_ctx=512, verbose=False)

        return {
            "perplexity": self._measure_perplexity(llm),
            "latency_ms": self._measure_latency(llm),
            "memory_mb": self._measure_memory(llm)
        }

    def _measure_latency(self, llm) -> float:
        import time, numpy as np
        latencies = []
        for prompt in self.test_prompts[:5]:
            start = time.time()
            llm(prompt, max_tokens=50)
            latencies.append((time.time() - start) * 1000)
        return np.mean(latencies)
```

### Pattern 3: Quantization Selection

```python
class QuantizationSelector:
    """Select optimal quantization for hardware."""

    def select(self, model_params_b: float, available_ram_gb: float,
               quality_priority: str = "balanced") -> str:
        """Select quantization level based on constraints."""

        memory_per_param = {"Q4_K_M": 0.5, "Q5_K_M": 0.625, "Q6_K": 0.75, "Q8_0": 1.0}
        quality_scores = {"Q4_K_M": 0.7, "Q5_K_M": 0.85, "Q6_K": 0.92, "Q8_0": 0.98}

        usable_ram = available_ram_gb - 2
        candidates = [q for q, mem in memory_per_param.items()
                     if model_params_b * mem <= usable_ram]

        if not candidates:
            raise ValueError(f"No quantization fits in {available_ram_gb}GB RAM")

        if quality_priority == "quality":
            return max(candidates, key=lambda q: quality_scores[q])
        elif quality_priority == "speed":
            return min(candidates, key=lambda q: memory_per_param[q])
        else:
            return max(candidates, key=lambda q: quality_scores[q])
```

**See `references/advanced-patterns.md` for mixed quantization, calibration, and hardware-specific optimization**

---

