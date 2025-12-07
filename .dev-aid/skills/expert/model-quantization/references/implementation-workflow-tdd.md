## 5. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```python
# tests/test_quantization.py
import pytest

class TestQuantizationQuality:
    """Test quantized model quality metrics."""

    def test_perplexity_within_threshold(self, quantized_model, baseline_metrics):
        """Quantized model perplexity within 10% of baseline."""
        benchmark = QuantizationBenchmark(TEST_PROMPTS)
        results = benchmark.benchmark(quantized_model)

        max_perplexity = baseline_metrics["perplexity"] * 1.10
        assert results["perplexity"] <= max_perplexity

    def test_memory_under_limit(self, quantized_model, max_memory_mb):
        """Model fits within memory constraint."""
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / (1024 * 1024)
        assert memory_mb <= max_memory_mb
```

**See `references/testing-guide.md` for comprehensive test suite**

### Step 2: Implement Minimum to Pass

```python
# Implement quantization to make tests pass
quantizer = SecureQuantizer(models_dir, llama_cpp_dir)
output = quantizer.quantize(
    input_model="model-f16.gguf",
    output_name="model-Q5_K_M.gguf",
    quantization="Q5_K_M"
)
```

### Step 3: Refactor Following Patterns

- Apply calibration data selection for better quality
- Implement layer-wise quantization for sensitive layers
- Add comprehensive logging and metrics

### Step 4: Run Full Verification

```bash
# Run all quantization tests
pytest tests/test_quantization.py -v

# Run with coverage
pytest tests/test_quantization.py --cov=quantization --cov-report=term-missing
```

---

