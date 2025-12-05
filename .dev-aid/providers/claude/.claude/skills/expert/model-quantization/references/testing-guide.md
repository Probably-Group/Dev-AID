# Model Quantization Testing Guide

## Test-Driven Development Workflow

### Step 1: Write Failing Test First

Always write tests before implementing quantization code.

```python
# tests/test_quantization.py
import pytest
from pathlib import Path

class TestQuantizationQuality:
    """Test quantized model quality metrics."""

    @pytest.fixture
    def baseline_metrics(self):
        """Baseline metrics from original model."""
        return {
            "perplexity": 5.2,
            "accuracy": 0.95,
            "latency_ms": 100
        }

    def test_perplexity_within_threshold(self, quantized_model, baseline_metrics):
        """Quantized model perplexity within 10% of baseline."""
        benchmark = QuantizationBenchmark(TEST_PROMPTS)
        results = benchmark.benchmark(quantized_model)

        max_perplexity = baseline_metrics["perplexity"] * 1.10
        assert results["perplexity"] <= max_perplexity, \
            f"Perplexity {results['perplexity']} exceeds threshold {max_perplexity}"

    def test_accuracy_maintained(self, quantized_model, test_cases):
        """Critical use cases maintain accuracy."""
        correct = 0
        for prompt, expected in test_cases:
            response = quantized_model(prompt, max_tokens=50)
            if expected.lower() in response["choices"][0]["text"].lower():
                correct += 1

        accuracy = correct / len(test_cases)
        assert accuracy >= 0.90, f"Accuracy {accuracy} below 90% threshold"

    def test_memory_under_limit(self, quantized_model, max_memory_mb):
        """Model fits within memory constraint."""
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / (1024 * 1024)

        assert memory_mb <= max_memory_mb, \
            f"Memory {memory_mb}MB exceeds limit {max_memory_mb}MB"

    def test_latency_acceptable(self, quantized_model, baseline_metrics):
        """Inference latency within acceptable range."""
        benchmark = QuantizationBenchmark(TEST_PROMPTS)
        results = benchmark.benchmark(quantized_model)

        # Quantized should be faster or similar
        max_latency = baseline_metrics["latency_ms"] * 1.5
        assert results["latency_ms"] <= max_latency
```

---

## Step 2: Implement Minimum to Pass

```python
# Implementation to make tests pass
from secure_quantizer import SecureQuantizer

quantizer = SecureQuantizer(models_dir, llama_cpp_dir)
output = quantizer.quantize(
    input_model="model-f16.gguf",
    output_name="model-Q5_K_M.gguf",
    quantization="Q5_K_M"
)
```

---

## Step 3: Refactor Following Patterns

After tests pass, refactor to improve quality:

```python
# Apply calibration data selection
calibration_data = load_representative_samples()
quantizer.set_calibration_data(calibration_data)

# Implement layer-wise quantization for sensitive layers
quantizer.set_layer_config({
    "attention": "Q6_K",  # Higher precision
    "mlp": "Q5_K_M",      # Standard precision
    "output": "Q8_0"       # Highest precision
})

# Add comprehensive logging
quantizer.enable_metrics_logging()
```

---

## Step 4: Run Full Verification

```bash
# Run all quantization tests
pytest tests/test_quantization.py -v

# Run with coverage
pytest tests/test_quantization.py --cov=quantization --cov-report=term-missing

# Run benchmarks
python -m pytest tests/test_quantization.py::TestQuantizationQuality -v --benchmark
```

---

## Comprehensive Test Suite

### Unit Tests

```python
class TestSecureQuantizer:
    """Test SecureQuantizer implementation."""

    def test_validates_input_exists(self):
        """Raises error if input model doesn't exist."""
        quantizer = SecureQuantizer("/models", "/llama.cpp")

        with pytest.raises(FileNotFoundError):
            quantizer.quantize("nonexistent.gguf", "out.gguf", "Q4_K_M")

    def test_validates_quantization_type(self):
        """Raises error for invalid quantization type."""
        quantizer = SecureQuantizer("/models", "/llama.cpp")

        with pytest.raises(ValueError, match="Invalid quantization"):
            quantizer.quantize("model.gguf", "out.gguf", "INVALID")

    def test_calculates_checksum(self, tmp_path):
        """Calculates and saves checksum correctly."""
        quantizer = SecureQuantizer(str(tmp_path), "/llama.cpp")

        # Create test file
        test_file = tmp_path / "test.gguf"
        test_file.write_bytes(b"test content")

        checksum = quantizer._calculate_checksum(test_file)
        assert len(checksum) == 64  # SHA256 length
        assert checksum.startswith("6ae8")  # Known prefix for "test content"

    def test_saves_checksum_file(self, tmp_path):
        """Saves checksum file alongside model."""
        quantizer = SecureQuantizer(str(tmp_path), "/llama.cpp")
        model_path = tmp_path / "model.gguf"

        quantizer._save_checksum(model_path, "abc123")

        checksum_file = tmp_path / "model.sha256"
        assert checksum_file.exists()
        assert "abc123  model.gguf" in checksum_file.read_text()
```

---

### Integration Tests

```python
class TestQuantizationIntegration:
    """Test complete quantization workflow."""

    @pytest.fixture
    def test_model(self, tmp_path):
        """Create test model for quantization."""
        # Download or create small test model
        model_path = tmp_path / "test-model-f16.gguf"
        # ... create test model ...
        return model_path

    def test_full_quantization_pipeline(self, test_model, tmp_path):
        """Test complete quantization from F16 to Q4_K_M."""
        quantizer = SecureQuantizer(str(tmp_path), "/opt/llama.cpp")

        output = quantizer.quantize(
            test_model.name,
            "test-model-Q4_K_M.gguf",
            "Q4_K_M"
        )

        # Verify output exists
        assert Path(output).exists()

        # Verify checksum exists
        assert Path(output).with_suffix(".sha256").exists()

        # Verify size is smaller
        original_size = test_model.stat().st_size
        quantized_size = Path(output).stat().st_size
        assert quantized_size < original_size * 0.6  # Should be ~50% for Q4

    def test_multiple_quantization_levels(self, test_model, tmp_path):
        """Test creating multiple quantization levels."""
        quantizer = SecureQuantizer(str(tmp_path), "/opt/llama.cpp")

        quantizations = ["Q4_K_M", "Q5_K_M", "Q8_0"]
        outputs = []

        for quant in quantizations:
            output = quantizer.quantize(
                test_model.name,
                f"test-model-{quant}.gguf",
                quant
            )
            outputs.append(output)

        # All outputs exist
        assert all(Path(out).exists() for out in outputs)

        # Sizes are ordered (Q4 < Q5 < Q8)
        sizes = [Path(out).stat().st_size for out in outputs]
        assert sizes[0] < sizes[1] < sizes[2]
```

---

### Quality Benchmark Tests

```python
class TestQuantizationBenchmark:
    """Test quality benchmarking."""

    @pytest.fixture
    def test_prompts(self):
        """Standard test prompts for benchmarking."""
        return [
            "The capital of France is",
            "Write a haiku about testing",
            "Explain quantum computing in simple terms",
            "What is 2 + 2?",
            "Complete the phrase: To be or not to"
        ]

    def test_measures_perplexity(self, quantized_model, test_prompts):
        """Benchmark measures perplexity correctly."""
        benchmark = QuantizationBenchmark(test_prompts)
        results = benchmark.benchmark(quantized_model)

        assert "perplexity" in results
        assert results["perplexity"] > 0
        assert results["perplexity"] < 100  # Reasonable range

    def test_measures_latency(self, quantized_model, test_prompts):
        """Benchmark measures latency correctly."""
        benchmark = QuantizationBenchmark(test_prompts)
        results = benchmark.benchmark(quantized_model)

        assert "latency_ms" in results
        assert results["latency_ms"] > 0
        assert results["latency_ms"] < 10000  # Less than 10 seconds

    def test_compares_quantization_levels(self, test_prompts, tmp_path):
        """Compare quality across quantization levels."""
        benchmark = QuantizationBenchmark(test_prompts)

        q4_results = benchmark.benchmark(str(tmp_path / "model-Q4_K_M.gguf"))
        q5_results = benchmark.benchmark(str(tmp_path / "model-Q5_K_M.gguf"))
        q8_results = benchmark.benchmark(str(tmp_path / "model-Q8_0.gguf"))

        # Higher quantization should have better (lower) perplexity
        assert q4_results["perplexity"] >= q5_results["perplexity"]
        assert q5_results["perplexity"] >= q8_results["perplexity"]
```

---

### Performance Tests

```python
class TestQuantizationPerformance:
    """Test performance characteristics."""

    def test_memory_usage(self, quantized_model):
        """Memory usage is within expected bounds."""
        import psutil

        process = psutil.Process()
        initial_mem = process.memory_info().rss / (1024 * 1024)

        # Load model
        from llama_cpp import Llama
        llm = Llama(model_path=quantized_model)

        loaded_mem = process.memory_info().rss / (1024 * 1024)
        memory_used = loaded_mem - initial_mem

        # Q4_K_M 7B should use ~6GB
        assert memory_used < 8000  # Less than 8GB

    def test_inference_speed(self, quantized_model):
        """Inference speed meets requirements."""
        from llama_cpp import Llama
        import time

        llm = Llama(model_path=quantized_model, n_ctx=512)

        start = time.time()
        llm("The quick brown fox", max_tokens=50)
        duration = time.time() - start

        # Should complete in reasonable time
        assert duration < 30  # Less than 30 seconds for 50 tokens

    @pytest.mark.slow
    def test_batch_inference(self, quantized_model):
        """Batch inference is efficient."""
        from llama_cpp import Llama
        import time

        llm = Llama(model_path=quantized_model, n_ctx=2048)
        prompts = ["Test prompt"] * 10

        start = time.time()
        for prompt in prompts:
            llm(prompt, max_tokens=20)
        duration = time.time() - start

        avg_per_prompt = duration / len(prompts)
        assert avg_per_prompt < 10  # Less than 10s per prompt
```

---

### Security Tests

```python
class TestQuantizationSecurity:
    """Test security aspects."""

    def test_checksum_verification(self, tmp_path):
        """Checksum verification detects tampering."""
        model_path = tmp_path / "model.gguf"
        model_path.write_bytes(b"original content")

        # Create checksum
        original_checksum = hashlib.sha256(b"original content").hexdigest()
        checksum_path = tmp_path / "model.sha256"
        checksum_path.write_text(f"{original_checksum}  model.gguf")

        # Verify passes for original
        assert verify_model_integrity(str(model_path))

        # Tamper with model
        model_path.write_bytes(b"tampered content")

        # Verify fails after tampering
        assert not verify_model_integrity(str(model_path))

    def test_path_validation(self):
        """Path validation prevents traversal."""
        with pytest.raises(SecurityError):
            validate_model_path("../../../etc/passwd", "/var/models")

        with pytest.raises(SecurityError):
            validate_model_path("/etc/passwd", "/var/models")

    def test_subprocess_timeout(self, tmp_path):
        """Quantization subprocess has timeout."""
        quantizer = SecureQuantizer(str(tmp_path), "/opt/llama.cpp")

        # Mock long-running process
        with pytest.raises(subprocess.TimeoutExpired):
            # This would timeout if process runs too long
            pass
```

---

## Test Fixtures

```python
# conftest.py
import pytest
from pathlib import Path

@pytest.fixture(scope="session")
def models_dir(tmp_path_factory):
    """Temporary models directory for tests."""
    return tmp_path_factory.mktemp("models")

@pytest.fixture
def quantized_model(models_dir):
    """Quantized test model."""
    # Create or download small test model
    model_path = models_dir / "test-Q4_K_M.gguf"
    # ... setup model ...
    return str(model_path)

@pytest.fixture
def test_cases():
    """Test cases for accuracy testing."""
    return [
        ("What is 2+2?", "4"),
        ("The capital of France is", "Paris"),
        ("Complete: Hello", "world"),
    ]

@pytest.fixture
def max_memory_mb():
    """Maximum memory constraint for tests."""
    return 8000  # 8GB
```

---

## Running Tests

### Basic Test Run

```bash
# Run all tests
pytest tests/test_quantization.py

# Run specific test class
pytest tests/test_quantization.py::TestQuantizationQuality

# Run specific test
pytest tests/test_quantization.py::TestQuantizationQuality::test_perplexity_within_threshold
```

### With Coverage

```bash
# Generate coverage report
pytest tests/test_quantization.py --cov=quantization --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Performance Testing

```bash
# Run only performance tests
pytest tests/test_quantization.py -m performance

# Skip slow tests
pytest tests/test_quantization.py -m "not slow"
```

### Continuous Integration

```yaml
# .github/workflows/test.yml
name: Quantization Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements-test.txt

      - name: Run tests
        run: |
          pytest tests/test_quantization.py -v --cov=quantization

      - name: Upload coverage
        uses: codecov/codecov-action@v2
```
