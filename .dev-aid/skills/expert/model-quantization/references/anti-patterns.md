# Model Quantization Anti-Patterns

## Common Mistakes to Avoid

### DON'T: Use Unverified Models

**Bad Example**:
```python
# BAD - No verification
llm = Llama(model_path=user_provided_path)
```

**Good Example**:
```python
# GOOD - Verify first
if not verify_model_integrity(path):
    raise SecurityError("Model verification failed")
llm = Llama(model_path=path)
```

**Why it's bad**: Unverified models could be tampered with or corrupted, leading to security vulnerabilities or incorrect outputs.

---

### DON'T: Over-Quantize for Use Case

**Bad Example**:
```python
# BAD - Q4_0 for quality-critical task
llm = Llama(model_path="model-Q4_0.gguf")  # Poor quality
```

**Good Example**:
```python
# GOOD - Select appropriate level
selector = QuantizationSelector()
quant = selector.select(7.0, 8.0, "quality")
llm = Llama(model_path=f"model-{quant}.gguf")
```

**Why it's bad**: Over-quantizing degrades quality below acceptable thresholds. Q4_0 is only suitable for non-critical use cases.

---

### DON'T: Ignore Memory Overhead

**Bad Example**:
```python
# BAD - Assume model size = RAM needed
if available_ram >= model_size:
    load_model(model_path)  # Will crash!
```

**Good Example**:
```python
# GOOD - Account for overhead
required_ram = model_size * 1.5  # 50% overhead
if available_ram >= required_ram:
    load_model(model_path)
```

**Why it's bad**: Models need additional RAM for context, KV cache, and operations. Always reserve 2-4GB extra.

---

### DON'T: Skip Benchmarking

**Bad Example**:
```python
# BAD - Deploy without testing
quantizer.quantize(model, "model-Q4_K_M.gguf", "Q4_K_M")
# Deploy directly to production
```

**Good Example**:
```python
# GOOD - Benchmark before deployment
quantizer.quantize(model, "model-Q4_K_M.gguf", "Q4_K_M")
benchmark = QuantizationBenchmark(TEST_PROMPTS)
results = benchmark.benchmark("model-Q4_K_M.gguf")

if results["perplexity"] > MAX_PERPLEXITY:
    logger.error("Quality too low, trying Q5_K_M")
    quantizer.quantize(model, "model-Q5_K_M.gguf", "Q5_K_M")
```

**Why it's bad**: Quantization quality varies by model. Always benchmark on your specific use cases.

---

### DON'T: Use Invalid Quantization Types

**Bad Example**:
```python
# BAD - Typo or invalid type
quantizer.quantize(model, output, "Q4_KM")  # Should be Q4_K_M
```

**Good Example**:
```python
# GOOD - Validate before use
VALID_TYPES = ["Q4_0", "Q4_K_S", "Q4_K_M", "Q5_K_S", "Q5_K_M", "Q6_K", "Q8_0"]
if quantization not in VALID_TYPES:
    raise ValueError(f"Invalid quantization: {quantization}")
quantizer.quantize(model, output, quantization)
```

**Why it's bad**: Typos cause quantization failures after hours of processing.

---

### DON'T: Quantize Already Quantized Models

**Bad Example**:
```python
# BAD - Double quantization
quantizer.quantize("model-Q8_0.gguf", "model-Q4_K_M.gguf", "Q4_K_M")
```

**Good Example**:
```python
# GOOD - Always quantize from F16
quantizer.quantize("model-F16.gguf", "model-Q4_K_M.gguf", "Q4_K_M")
```

**Why it's bad**: Quantizing quantized models compounds errors. Always quantize from F16 baseline.

---

### DON'T: Forget to Save Checksums

**Bad Example**:
```python
# BAD - No checksum saved
quantizer.quantize(input, output, "Q5_K_M")
# No way to verify integrity later
```

**Good Example**:
```python
# GOOD - Save checksum
output_path = quantizer.quantize(input, output, "Q5_K_M")
checksum = calculate_checksum(output_path)
save_checksum(output_path, checksum)
```

**Why it's bad**: Without checksums, you can't detect file corruption or tampering.

---

### DON'T: Use Blocking Calls for Long Operations

**Bad Example**:
```python
# BAD - Blocks for hours
def quantize_all():
    for model in models:
        quantizer.quantize(model, f"{model}-Q4.gguf", "Q4_K_M")
        # Application frozen for hours
```

**Good Example**:
```python
# GOOD - Use async or progress tracking
import asyncio

async def quantize_all():
    tasks = []
    for model in models:
        task = asyncio.create_task(
            quantize_async(model, f"{model}-Q4.gguf", "Q4_K_M")
        )
        tasks.append(task)
    await asyncio.gather(*tasks)
```

**Why it's bad**: Quantization takes hours. Always provide progress feedback.

---

### DON'T: Hardcode Paths

**Bad Example**:
```python
# BAD - Hardcoded paths
llm = Llama(model_path="/home/user/models/llama-7b.gguf")
```

**Good Example**:
```python
# GOOD - Use configuration
from pathlib import Path

MODELS_DIR = Path(os.getenv("MODELS_DIR", "/var/jarvis/models"))
model_path = MODELS_DIR / "llama-7b.gguf"
llm = Llama(model_path=str(model_path))
```

**Why it's bad**: Hardcoded paths break in different environments.

---

### DON'T: Ignore Error Handling

**Bad Example**:
```python
# BAD - No error handling
result = subprocess.run(["./quantize", input, output, quant_type])
return output  # What if it failed?
```

**Good Example**:
```python
# GOOD - Handle errors
result = subprocess.run(
    ["./quantize", input, output, quant_type],
    capture_output=True,
    timeout=3600
)

if result.returncode != 0:
    logger.error("quantize.failed", stderr=result.stderr)
    raise QuantizationError(f"Quantization failed: {result.stderr}")

return output
```

**Why it's bad**: Silent failures waste time and cause downstream errors.

---

## Performance Anti-Patterns

### DON'T: Use Wrong Context Size

```python
# BAD - Context too large for memory
llm = Llama(model_path=path, n_ctx=8192)  # Eats 4GB extra!

# GOOD - Match to use case
llm = Llama(model_path=path, n_ctx=2048)  # Sufficient for most tasks
```

### DON'T: Load Multiple Large Models

```python
# BAD - Load all models at once
models = [Llama(f"model-{q}.gguf") for q in quantizations]  # OOM!

# GOOD - Load on demand
def get_model(quant: str):
    return Llama(f"model-{quant}.gguf")
```

---

## Security Anti-Patterns

### DON'T: Trust User-Provided Paths

```python
# BAD - Path traversal vulnerability
model_path = user_input["model"]
llm = Llama(model_path=model_path)  # Can load /etc/passwd!

# GOOD - Validate paths
model_path = validate_model_path(user_input["model"], MODELS_DIR)
llm = Llama(model_path=str(model_path))
```

### DON'T: Run Quantization as Root

```bash
# BAD - Root privileges for quantization
sudo ./quantize model.gguf output.gguf Q4_K_M

# GOOD - Use dedicated user
su - jarvis -c "./quantize model.gguf output.gguf Q4_K_M"
```

---

## Testing Anti-Patterns

### DON'T: Skip Quality Tests

```python
# BAD - No quality validation
quantizer.quantize(model, output, "Q4_K_M")
# Deploy to production immediately

# GOOD - Test quality first
quantizer.quantize(model, output, "Q4_K_M")
assert test_quality(output) >= MIN_QUALITY
```

### DON'T: Test Only Happy Path

```python
# BAD - Only test success
def test_quantize():
    result = quantizer.quantize("model.gguf", "out.gguf", "Q4_K_M")
    assert result

# GOOD - Test failures too
def test_quantize_invalid_type():
    with pytest.raises(ValueError):
        quantizer.quantize("model.gguf", "out.gguf", "INVALID")

def test_quantize_missing_input():
    with pytest.raises(FileNotFoundError):
        quantizer.quantize("missing.gguf", "out.gguf", "Q4_K_M")
```
