---
name: model-quantization
version: 2.0.0
description: "Model quantization techniques for 4-bit/8-bit inference with GGUF format conversion and optimization. Use when quantizing models, converting to GGUF, or optimizing inference size. Do NOT use for model training or fine-tuning."
risk_level: MEDIUM
token_budget: 3500
---
# Model Quantization - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.2 Security Patterns (security rules)

**CWE-502: Model File Deserialization**
- Do not: Load models from untrusted sources (pickle-based formats)
- Instead: Verify model checksums, use safetensors format, scan for malware

---

## 1. Security Principles

### 1.1 Model File Validation (CWE-502)

**Principle:** GGUF/safetensors files can be crafted maliciously. Validate before loading.

```python
# ❌ WRONG - Loading arbitrary model files
from llama_cpp import Llama

def load_model(path: str):
    return Llama(model_path=path)  # Arbitrary file execution

# ✅ CORRECT - Validate model files before loading
import hashlib
import struct
from pathlib import Path

GGUF_MAGIC = b'GGUF'
SAFETENSORS_MAGIC = b'{'  # JSON header

TRUSTED_HASHES = {
    "llama-2-7b-q4_k_m.gguf": "abc123...",
    "mistral-7b-q5_k_m.gguf": "def456...",
}

def validate_model_file(path: Path) -> bool:
    """Validate model file before loading."""
    if not path.exists():
        raise FileNotFoundError(f"Model not found: {path}")

    # Check file extension
    if path.suffix not in ('.gguf', '.safetensors'):
        raise ValueError(f"Unsupported format: {path.suffix}")

    # Validate magic bytes
    with open(path, 'rb') as f:
        magic = f.read(4)

    if path.suffix == '.gguf' and magic != GGUF_MAGIC:
        raise ValueError("Invalid GGUF file")

    # Verify hash for known models (optional but recommended)
    if path.name in TRUSTED_HASHES:
        file_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if file_hash != TRUSTED_HASHES[path.name]:
            raise ValueError("Model hash mismatch - file may be corrupted")

    return True

def safe_load_model(path: str):
    """Load model with validation."""
    model_path = Path(path)
    validate_model_file(model_path)

    from llama_cpp import Llama
    return Llama(model_path=str(model_path))
```

### 1.2 Resource Exhaustion Prevention (CWE-400)

**Principle:** Quantization is memory-intensive. Enforce limits to prevent OOM.

```python
# ❌ WRONG - No resource limits
def quantize_model(input_path, output_path, quant_type):
    from transformers import AutoModelForCausalLM
    model = AutoModelForCausalLM.from_pretrained(input_path)  # May OOM
    # ... quantize

# ✅ CORRECT - Check resources before loading
import os
import psutil
from pathlib import Path

QUANT_MEMORY_MULTIPLIERS = {
    'q4_0': 0.25,
    'q4_k_m': 0.28,
    'q5_k_m': 0.35,
    'q8_0': 0.5,
    'f16': 1.0,
}

def estimate_memory_requirement(
    model_params_b: float,
    quant_type: str
) -> float:
    """Estimate memory in GB for quantization."""
    base_memory = model_params_b * 2  # FP16 base
    multiplier = QUANT_MEMORY_MULTIPLIERS.get(quant_type, 1.0)
    # Need ~2x for conversion process
    return base_memory * multiplier * 2

def check_resources(model_params_b: float, quant_type: str) -> bool:
    """Check if system has enough resources."""
    required_gb = estimate_memory_requirement(model_params_b, quant_type)
    available_gb = psutil.virtual_memory().available / (1024 ** 3)

    if required_gb > available_gb:
        raise MemoryError(
            f"Quantization requires ~{required_gb:.1f}GB, "
            f"but only {available_gb:.1f}GB available"
        )
    return True
```

### 1.3 Path Traversal Prevention (CWE-22)

**Principle:** User-provided model paths must be validated against traversal attacks.

```python
# ❌ WRONG - Direct path concatenation
def get_model_path(model_name: str) -> str:
    return f"/models/{model_name}"  # Allows ../../../etc/passwd

# ✅ CORRECT - Validate and resolve paths safely
from pathlib import Path

MODELS_DIR = Path("/models").resolve()

def safe_model_path(model_name: str) -> Path:
    """Get safe model path, preventing traversal."""
    # Validate model name (allowlist approach)
    if not model_name.replace('-', '').replace('_', '').isalnum():
        raise ValueError(f"Invalid model name: {model_name}")

    # Construct and validate path
    model_path = (MODELS_DIR / model_name).resolve()

    # Ensure path is within models directory
    if not str(model_path).startswith(str(MODELS_DIR)):
        raise ValueError("Path traversal detected")

    return model_path
```

---

## 2. Version Requirements

```
# llama.cpp Python bindings
llama-cpp-python>=0.2.50
# AutoGPTQ for GPU quantization
auto-gptq>=0.7.0
# AWQ for activation-aware quantization
autoawq>=0.2.0
# bitsandbytes for 4/8-bit
bitsandbytes>=0.43.0
# GGUF conversion tools
gguf>=0.6.0
# Transformers for model loading
transformers>=4.38.0
```

---

## 3. Code Patterns

### WHEN converting to GGUF format, use proper quantization types

```python
# ❌ WRONG - Arbitrary quantization without understanding impact
subprocess.run(f"./quantize model.gguf model-q4.gguf q4_0", shell=True)

# ✅ CORRECT - Type-safe quantization with llama.cpp
import subprocess
from pathlib import Path
from enum import Enum
from dataclasses import dataclass

class GGUFQuantType(Enum):
    """Supported GGUF quantization types with quality/size tradeoffs."""
    Q4_0 = "q4_0"      # 4-bit, fastest, lowest quality
    Q4_K_M = "q4_k_m"  # 4-bit K-quant, good balance
    Q5_K_M = "q5_k_m"  # 5-bit K-quant, better quality
    Q6_K = "q6_k"      # 6-bit K-quant, near-FP16 quality
    Q8_0 = "q8_0"      # 8-bit, high quality, larger

@dataclass
class QuantResult:
    input_size_gb: float
    output_size_gb: float
    compression_ratio: float
    quant_type: GGUFQuantType

def quantize_gguf(
    input_path: Path,
    output_path: Path,
    quant_type: GGUFQuantType,
    llama_cpp_path: Path = Path("./llama.cpp")
) -> QuantResult:
    """Quantize a model to GGUF format safely."""

    # Validate paths
    if not input_path.exists():
        raise FileNotFoundError(f"Input model not found: {input_path}")

    quantize_bin = llama_cpp_path / "quantize"
    if not quantize_bin.exists():
        raise FileNotFoundError("llama.cpp quantize binary not found")

    # Get input size
    input_size = input_path.stat().st_size / (1024 ** 3)

    # Run quantization (no shell=True)
    result = subprocess.run(
        [
            str(quantize_bin),
            str(input_path),
            str(output_path),
            quant_type.value,
        ],
        capture_output=True,
        text=True,
        timeout=3600,  # 1 hour timeout
    )

    if result.returncode != 0:
        raise RuntimeError(f"Quantization failed: {result.stderr}")

    output_size = output_path.stat().st_size / (1024 ** 3)

    return QuantResult(
        input_size_gb=input_size,
        output_size_gb=output_size,
        compression_ratio=input_size / output_size,
        quant_type=quant_type,
    )
```

### WHEN using bitsandbytes quantization, configure properly

```python
# ❌ WRONG - Hardcoded quantization config
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

model = AutoModelForCausalLM.from_pretrained(
    "model",
    quantization_config=BitsAndBytesConfig(load_in_4bit=True)
)

# ✅ CORRECT - Configurable quantization with validation
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
from pydantic import BaseModel, Field
import torch

class BnBQuantConfig(BaseModel):
    """Validated bitsandbytes quantization configuration."""
    bits: int = Field(4, ge=4, le=8)
    double_quant: bool = True
    quant_type: str = Field("nf4", pattern="^(fp4|nf4)$")
    compute_dtype: str = Field("bfloat16", pattern="^(float16|bfloat16|float32)$")

def load_quantized_model(
    model_id: str,
    config: BnBQuantConfig,
    device_map: str = "auto"
):
    """Load model with bitsandbytes quantization."""

    # Check CUDA availability
    if not torch.cuda.is_available():
        raise RuntimeError("bitsandbytes requires CUDA")

    # Map compute dtype
    dtype_map = {
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
        "float32": torch.float32,
    }
    compute_dtype = dtype_map[config.compute_dtype]

    # Create BnB config
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=(config.bits == 4),
        load_in_8bit=(config.bits == 8),
        bnb_4bit_use_double_quant=config.double_quant,
        bnb_4bit_quant_type=config.quant_type,
        bnb_4bit_compute_dtype=compute_dtype,
    )

    return AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=bnb_config,
        device_map=device_map,
        trust_remote_code=False,  # Never trust remote code
    )
```

### WHEN running inference with quantized models, handle context properly

```python
# ❌ WRONG - Unbounded context, no resource management
from llama_cpp import Llama

llm = Llama(model_path="model.gguf")
output = llm(prompt, max_tokens=-1)  # Unlimited tokens

# ✅ CORRECT - Bounded inference with proper config
from llama_cpp import Llama
from pydantic import BaseModel, Field
from contextlib import contextmanager
from typing import Iterator

class InferenceConfig(BaseModel):
    """Validated inference configuration."""
    max_tokens: int = Field(512, ge=1, le=4096)
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    top_p: float = Field(0.9, ge=0.0, le=1.0)
    top_k: int = Field(40, ge=1, le=100)
    repeat_penalty: float = Field(1.1, ge=1.0, le=2.0)

class QuantizedLLM:
    """Safe wrapper for quantized LLM inference."""

    def __init__(
        self,
        model_path: str,
        n_ctx: int = 2048,
        n_gpu_layers: int = -1,
        n_threads: int | None = None,
    ):
        import os

        # Validate model path
        validate_model_file(Path(model_path))

        # Set thread count safely
        if n_threads is None:
            n_threads = min(os.cpu_count() or 4, 8)

        self._llm = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_gpu_layers=n_gpu_layers,
            n_threads=n_threads,
            verbose=False,
        )

    def generate(
        self,
        prompt: str,
        config: InferenceConfig = InferenceConfig()
    ) -> str:
        """Generate text with bounded parameters."""

        # Validate prompt length
        tokens = self._llm.tokenize(prompt.encode())
        if len(tokens) > self._llm.n_ctx() - config.max_tokens:
            raise ValueError("Prompt too long for context window")

        output = self._llm(
            prompt,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            top_p=config.top_p,
            top_k=config.top_k,
            repeat_penalty=config.repeat_penalty,
            stop=["</s>", "\n\n\n"],  # Reasonable stop tokens
        )

        return output["choices"][0]["text"]

    def stream(
        self,
        prompt: str,
        config: InferenceConfig = InferenceConfig()
    ) -> Iterator[str]:
        """Stream generation with bounded parameters."""

        for chunk in self._llm(
            prompt,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            stream=True,
        ):
            yield chunk["choices"][0]["text"]
```

### WHEN converting HuggingFace models to GGUF, validate intermediate steps

```python
# ❌ WRONG - Direct conversion without checks
# python convert.py model/ --outfile model.gguf

# ✅ CORRECT - Staged conversion with validation
from pathlib import Path
import subprocess
import json
from transformers import AutoConfig

def convert_hf_to_gguf(
    hf_model_path: Path,
    output_path: Path,
    quant_type: GGUFQuantType = GGUFQuantType.Q4_K_M,
    llama_cpp_path: Path = Path("./llama.cpp")
) -> Path:
    """Convert HuggingFace model to quantized GGUF."""

    # Validate source model
    config_path = hf_model_path / "config.json"
    if not config_path.exists():
        raise ValueError("Not a valid HuggingFace model directory")

    with open(config_path) as f:
        config = json.load(f)

    # Check supported architectures
    supported_archs = {
        "LlamaForCausalLM", "MistralForCausalLM", "Phi3ForCausalLM",
        "Qwen2ForCausalLM", "GemmaForCausalLM"
    }
    arch = config.get("architectures", [None])[0]
    if arch not in supported_archs:
        raise ValueError(f"Unsupported architecture: {arch}")

    # Step 1: Convert to FP16 GGUF
    fp16_path = output_path.with_suffix('.fp16.gguf')
    convert_script = llama_cpp_path / "convert_hf_to_gguf.py"

    result = subprocess.run(
        [
            "python", str(convert_script),
            str(hf_model_path),
            "--outfile", str(fp16_path),
            "--outtype", "f16",
        ],
        capture_output=True,
        text=True,
        timeout=7200,  # 2 hour timeout for large models
    )

    if result.returncode != 0:
        raise RuntimeError(f"Conversion failed: {result.stderr}")

    # Validate FP16 output
    validate_model_file(fp16_path)

    # Step 2: Quantize to target type
    final_result = quantize_gguf(
        input_path=fp16_path,
        output_path=output_path,
        quant_type=quant_type,
        llama_cpp_path=llama_cpp_path,
    )

    # Clean up intermediate file
    fp16_path.unlink()

    print(f"Conversion complete: {final_result.compression_ratio:.1f}x compression")
    return output_path
```

---

## 4. Anti-Patterns

Do not:
- Load model files without validating magic bytes/format
- Use `shell=True` in subprocess calls for quantization
- Trust user-provided paths without traversal checks
- Allow unlimited tokens in inference
- Set `trust_remote_code=True` when loading models
- Ignore memory requirements before quantization
- Skip hash validation for production deployments

---

## 5. Testing

```python
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

class TestModelQuantization:

    def test_validate_model_file_rejects_invalid_magic(self, tmp_path):
# ... (additional test cases follow same pattern)
```

---

## 6. Pre-Generation Checklist

Before generating quantization code:

- [ ] Model validation: Magic bytes checked before loading
- [ ] Path safety: User paths validated against traversal
- [ ] Resource checks: Memory requirements estimated before loading
- [ ] Subprocess safety: No `shell=True`, commands as lists
- [ ] Trust boundary: `trust_remote_code=False` for HF models
- [ ] Inference bounds: max_tokens, temperature, top_p limited
- [ ] Hash validation: Known models verified by hash in production
- [ ] Timeout handling: Long operations have timeout guards

---
