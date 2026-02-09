# Local LLM Provider

Run AI models locally for offline, private, and cost-free inference.

## Quick Start

```bash
# Run the setup wizard
./.dev-aid/scripts/setup-local-llm.sh
```

## Key Concepts

| Term | Description |
|------|-------------|
| **Inference Runtime** | Software that runs models on your GPU (Ollama, LM Studio, llama.cpp) |
| **Model** | The actual AI (Qwen, Phi, Codestral) - downloaded and run by the runtime |

> **Example:** "Running Qwen2.5-Coder using Ollama" = Model + Runtime

## Inference Runtimes

These are **runtimes** (like Docker for containers) that run AI models:

| Runtime | Port | Best For |
|---------|------|----------|
| [Ollama](https://ollama.ai) | 11434 | Easy CLI, integrated model library |
| [LM Studio](https://lmstudio.ai) | 1234 | GUI app, visual model browser |
| [llama.cpp](https://github.com/ggerganov/llama.cpp) | 8080 | C++ runtime, maximum control |

## Agent Framework Compatibility

All 8 Dev-AID agents and 4 multi-agent teams support local models via `--provider local`:

```bash
dev-aid-agent pr-reviewer --pr 42 --provider local --model qwen2.5-coder:32b
dev-aid-agent team security-audit-team -m "Audit auth" --provider local --model qwen2.5-coder:32b
```

**Requirement: Tool calling (function calling) support.** Agents rely on tool calling to read files, run searches, and execute commands. Models without tool calling support cannot run agents. Most modern coding models support this — see the recommended models below.

## Recommended Models

Based on 2026 benchmarks (Score vs VRAM efficiency):

| Model | Score | VRAM | Tier | Use Case |
|-------|-------|------|------|----------|
| Phi-4-Mini | 58 | 3GB | Entry | Quick iterations, low-end hardware |
| Codestral 22B | 72 | 14GB | Mid | Strong coding, mid-tier GPUs |
| Qwen2.5-Coder 32B | 68 | 20GB | High | Best value, prosumer GPUs |
| GLM-4.7 Thinking | 74 | 48GB | Pro | Deep reasoning, pro workstations |
| Kimi-K2-Thinking | 83 | 80GB | Enterprise | Best-in-class, data center |

## Hardware Requirements

| Tier | VRAM | RAM | Example Hardware |
|------|------|-----|------------------|
| Entry | 4-8GB | 16GB | RTX 3060, M1 Mac |
| Mid | 14-16GB | 24GB | RTX 3090, RTX 4080 |
| High | 20-24GB | 32GB | RTX 4090, Mac Studio M2 |
| Pro | 48GB+ | 64GB | A6000, Mac Studio M3 Max |
| Enterprise | 80GB+ | 128GB | A100, H100 |
| CPU-only | N/A | 32GB+ | Any modern CPU (slow) |

## Configuration

### Environment Variables

```bash
# In .dev-aid/config/.env

# Backend selection
LOCAL_INFERENCE_BACKEND=ollama  # ollama, lm_studio, llama_cpp

# Custom URLs (optional)
LOCAL_OLLAMA_URL=http://localhost:11434/v1
LOCAL_LM_STUDIO_URL=http://localhost:1234/v1
LOCAL_LLAMA_CPP_URL=http://localhost:8080/v1

# Default model (optional - auto-detected)
LOCAL_DEFAULT_MODEL=qwen2.5-coder:32b
```

### Enable in models.json

```json
{
  "local": {
    "enabled": true,  // <-- Change to true
    "provider": "local",
    ...
  }
}
```

## Backend Setup

### Ollama (Recommended)

```bash
# Install
curl -fsSL https://ollama.ai/install.sh | sh

# Start server
ollama serve

# Pull a model
ollama pull qwen2.5-coder:32b

# List models
ollama list
```

### LM Studio

1. Download from [lmstudio.ai](https://lmstudio.ai)
2. Launch the app
3. Go to "Local Server" tab
4. Enable server (runs on port 1234)
5. Download models from the browser

### llama.cpp

```bash
# Clone and build
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make -j

# Download GGUF model
# From https://huggingface.co/models?search=gguf

# Start server
./llama-server -m model.gguf --port 8080
```

## API Usage

All backends use OpenAI-compatible API:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",  # Ollama
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="qwen2.5-coder:32b",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## Troubleshooting

### Server not responding

```bash
# Check if server is running
curl http://localhost:11434/api/tags  # Ollama
curl http://localhost:1234/v1/models  # LM Studio
curl http://localhost:8080/v1/models  # llama.cpp
```

### Out of memory

- Try a smaller model
- Use quantized versions (Q4_K_M, Q5_K_M)
- Close other GPU-using applications

### Slow inference

- CPU-only is naturally slower
- Check GPU is being used: `nvidia-smi` or `rocm-smi`
- Consider smaller/quantized models

## Cost

**$0.00** - All local inference is free!

No API keys required. No usage limits. Complete privacy.
