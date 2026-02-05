# Local LLM Guide for Dev-AID

Complete guide to running AI models locally for offline, private, and cost-free inference.

## Table of Contents

1. [Key Terminology](#key-terminology)
2. [Overview](#overview)
3. [Hardware Requirements](#hardware-requirements)
4. [Quick Start](#quick-start)
5. [Inference Runtimes](#inference-runtimes)
6. [Model Selection](#model-selection)
7. [Setup Walkthrough](#setup-walkthrough)
8. [Configuration](#configuration)
9. [Troubleshooting](#troubleshooting)
10. [Performance Tips](#performance-tips)

## Key Terminology

> **Important:** Understanding the difference between runtimes and models prevents confusion.

| Term | What It Is | Examples |
|------|------------|----------|
| **Inference Runtime** | Software that loads and runs AI models on your hardware. Think of it like a "player" for models. | Ollama, LM Studio, llama.cpp, vLLM |
| **Model** | The actual AI "brain" - weights trained on data that generate responses. | Qwen2.5-Coder, Phi-4, Codestral, Llama 3 |
| **GGUF** | A file format for storing quantized models. Like MP3 for audio. | `qwen2.5-coder-32b.Q4_K_M.gguf` |
| **Quantization** | Compression that reduces model size/VRAM at slight quality cost. | Q4_K_M (small), Q8_0 (large), FP16 (huge) |

**Analogy:**
```
Inference Runtime  =  Video Player (VLC, QuickTime)
Model              =  Video File (movie.mp4)
GGUF               =  File Format (MP4, MKV)
Quantization       =  Compression (720p, 1080p, 4K)
```

**Common Misconception:**
- ❌ "I'm using Ollama" (implies Ollama is a model)
- ✅ "I'm using Ollama to run Qwen2.5-Coder" (correct - runtime + model)

## Overview

### Why Local LLMs?

| Benefit | Description |
|---------|-------------|
| **Privacy** | Your code never leaves your machine |
| **Offline** | Works without internet connection |
| **Zero Cost** | No API fees or usage limits |
| **Speed** | No network latency (with good hardware) |
| **Control** | Choose exactly which model to run |

### Trade-offs

| Consideration | Local | Cloud |
|---------------|-------|-------|
| Setup | More complex | Simple API key |
| Hardware | Requires GPU | None |
| Quality | Good (open models) | Best (frontier models) |
| Updates | Manual | Automatic |

## Hardware Requirements

### GPU VRAM Guide

VRAM is the primary constraint for local LLMs. More VRAM = larger/better models.

| VRAM | Model Capability | Example GPUs |
|------|------------------|--------------|
| 3-4GB | Small models only | GTX 1060, RTX 3050 |
| 8GB | Entry-level coding | RTX 3060, RTX 4060 |
| 12-16GB | Mid-tier models | RTX 3090, RTX 4080 |
| 20-24GB | Large coding models | RTX 4090, A5000 |
| 48GB | Pro-tier models | A6000, RTX 6000 |
| 80GB+ | Enterprise models | A100, H100 |

### Apple Silicon Guide

Apple Silicon uses unified memory - GPU can access most of system RAM:

| Chip | Unified Memory | Usable for ML | Recommended Model |
|------|----------------|---------------|-------------------|
| M1 (8GB) | 8GB | ~6GB | Phi-4-Mini |
| M1 Pro (16GB) | 16GB | ~12GB | Codestral 22B |
| M2 Max (32GB) | 32GB | ~24GB | Qwen2.5-Coder 32B |
| M3 Max (64GB) | 64GB | ~48GB | GLM-4.7 Thinking |
| M3 Ultra (128GB) | 128GB | ~96GB | Any model |

### CPU-Only Mode

Running without GPU is possible but slow:

- Expect 5-20x slower inference
- Use smallest models (Phi-4-Mini)
- Ensure 32GB+ RAM
- Consider quantized models

## Quick Start

### Option 1: Setup Wizard (Recommended)

```bash
# Run interactive setup
./.dev-aid/scripts/setup-local-llm.sh
```

The wizard will:
1. Detect your hardware
2. Recommend appropriate models
3. Install backend (if needed)
4. Download recommended model
5. Configure Dev-AID

### Option 2: Manual Setup

```bash
# 1. Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Start server
ollama serve

# 3. Pull a model
ollama pull qwen2.5-coder:32b

# 4. Enable in config
# Edit .dev-aid/config/models.json
# Set "local" -> "enabled": true

# 5. Update .env
echo "LOCAL_INFERENCE_BACKEND=ollama" >> .dev-aid/config/.env
```

## Inference Runtimes

> **Remember:** These are **runtimes** (software to run models), not models themselves.
> You download models separately and run them through these runtimes.

| Runtime | Type | Port | Best For |
|---------|------|------|----------|
| **Ollama** | CLI + Server | 11434 | Most users, easy setup |
| **LM Studio** | GUI App | 1234 | Visual model browsing |
| **llama.cpp** | C++ Library | 8080 | Maximum control, performance |
| **vLLM** | Python Server | 8000 | Production, high throughput |

### Ollama (Recommended)

**What it is:** A CLI tool and server that makes running local models as easy as `docker pull`.

**Best for:** Most users, easy setup, integrated model library

```bash
# Install the Ollama runtime
curl -fsSL https://ollama.ai/install.sh | sh

# Start the Ollama server (runtime)
ollama serve

# Download models (these are the actual AI models, not Ollama itself)
ollama pull phi4-mini           # Small, fast model
ollama pull codestral:22b       # Mid-tier coding model
ollama pull qwen2.5-coder:32b   # Large coding model

# List downloaded models
ollama list

# Run a model directly (Ollama runtime + Qwen model)
ollama run qwen2.5-coder:32b "Write a Python function"
```

**Pros:**
- Easiest to use
- Built-in model library (downloads from ollama.com/library)
- Auto-manages quantization
- Good community support

**Cons:**
- Less control over model loading
- Larger install size

### LM Studio

**What it is:** A desktop GUI application for downloading and running local models.

**Best for:** Users who prefer GUI, browsing models visually

1. Download from [lmstudio.ai](https://lmstudio.ai)
2. Launch application
3. Browse and download models (from HuggingFace)
4. Start local server (port 1234)

**Pros:**
- Visual model browser
- Easy model management
- Real-time generation preview

**Cons:**
- Requires GUI
- Larger resource footprint

### llama.cpp

**Best for:** Advanced users, maximum control, minimal overhead

```bash
# Build from source
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make -j LLAMA_CUDA=1  # For NVIDIA GPU

# Download GGUF model from HuggingFace
# Example: https://huggingface.co/TheBloke/Qwen2.5-Coder-32B-GGUF

# Start server
./llama-server \
  -m qwen2.5-coder-32b.Q4_K_M.gguf \
  --port 8080 \
  --n-gpu-layers 99
```

**Pros:**
- Most efficient
- Full control
- Minimal dependencies

**Cons:**
- Manual model management
- Requires building from source

## Model Selection

### Top Models for Coding (2026)

| Rank | Model | Score | VRAM | Best For |
|------|-------|-------|------|----------|
| 1 | Qwen2.5-Coder 32B | 68 | 20GB | Best bang-for-buck |
| 2 | Codestral 22B | 72 | 14GB | Mid-tier excellence |
| 3 | Phi-4-Mini | 58 | 3GB | Entry-level/fast |
| 4 | GLM-4.7 Thinking | 74 | 48GB | Deep reasoning |
| 5 | Kimi-K2-Thinking | 83 | 80GB | Best-in-class |

### Model by Use Case

| Use Case | Recommended Model | Why |
|----------|-------------------|-----|
| Quick code snippets | Phi-4-Mini | Fast, low resources |
| General coding | Qwen2.5-Coder 32B | Best value |
| Code review | Codestral 22B | Good analysis |
| Complex reasoning | GLM-4.7 Thinking | Deep thinking |
| Architecture design | Kimi-K2-Thinking | Highest quality |

### Quantization Levels

Models come in different quantization levels (quality vs size trade-off):

| Level | Size | Quality | Use When |
|-------|------|---------|----------|
| Q2_K | Smallest | Lowest | Desperate for VRAM |
| Q4_K_M | Small | Good | Recommended for most |
| Q5_K_M | Medium | Better | If VRAM allows |
| Q6_K | Large | Great | High VRAM systems |
| Q8_0 | Largest | Best | Enterprise hardware |
| FP16 | Huge | Maximum | Testing only |

## Configuration

### Environment Variables

Create/edit `.dev-aid/config/.env`:

```bash
# Backend selection (ollama, lm_studio, llama_cpp)
LOCAL_INFERENCE_BACKEND=ollama

# Custom URLs (override defaults)
LOCAL_OLLAMA_URL=http://localhost:11434/v1
LOCAL_LM_STUDIO_URL=http://localhost:1234/v1
LOCAL_LLAMA_CPP_URL=http://localhost:8080/v1

# Default model (optional)
LOCAL_DEFAULT_MODEL=qwen2.5-coder:32b
```

### Enable in models.json

Edit `.dev-aid/config/models.json`:

```json
{
  "local": {
    "enabled": true,  // <-- Set to true
    "provider": "local",
    "inference_backend": "ollama",
    ...
  }
}
```

## Troubleshooting

### Server Not Responding

```bash
# Check Ollama
curl http://localhost:11434/api/tags

# Check LM Studio
curl http://localhost:1234/v1/models

# Check llama.cpp
curl http://localhost:8080/v1/models
```

### Out of Memory (OOM)

Symptoms: Server crashes, "CUDA out of memory" errors

Solutions:
1. Use smaller model
2. Use more aggressive quantization (Q4_K_M → Q2_K)
3. Close other GPU applications
4. Reduce context length: `--ctx-size 2048`

### Slow Inference

Symptoms: Very long response times

Solutions:
1. Verify GPU is being used:
   ```bash
   # NVIDIA
   nvidia-smi

   # AMD
   rocm-smi

   # Apple
   powermetrics --samplers gpu_power
   ```
2. Use smaller model for quick tasks
3. Reduce `max_tokens` in requests
4. Check thermal throttling

### Model Not Loading

Symptoms: "Model not found" errors

Solutions:
```bash
# List available models
ollama list

# Re-download model
ollama pull qwen2.5-coder:32b

# Check model name matches exactly
```

### Connection Refused

Symptoms: Cannot connect to server

Solutions:
```bash
# Start the server
ollama serve

# Check if port is in use
lsof -i :11434

# Check firewall
sudo ufw status
```

## Performance Tips

### Optimize for Speed

1. **Use GPU offloading**: Load all layers to GPU
   ```bash
   # llama.cpp
   ./llama-server -m model.gguf --n-gpu-layers 99
   ```

2. **Reduce context size**: Lower context = faster
   ```bash
   ollama run model --ctx-size 4096
   ```

3. **Use Flash Attention** (if supported):
   ```bash
   ./llama-server -m model.gguf --flash-attn
   ```

### Optimize for Quality

1. **Use larger models** when possible
2. **Use less quantization** (Q6_K vs Q4_K_M)
3. **Increase context** for long documents:
   ```bash
   ollama run model --ctx-size 32768
   ```

### Batch Processing

For multiple requests:

```python
# Use streaming for real-time output
response = client.chat.completions.create(
    model="qwen2.5-coder:32b",
    messages=[...],
    stream=True
)
for chunk in response:
    print(chunk.choices[0].delta.content, end="")
```

## Comparison: Local vs Cloud

| Aspect | Local | Claude/GPT/Gemini |
|--------|-------|-------------------|
| Cost | $0 | $0.25-75/M tokens |
| Privacy | Complete | Data sent to cloud |
| Latency | GPU-dependent | Network-dependent |
| Quality | Good (68-83 score) | Best (85-95 score) |
| Offline | Yes | No |
| Setup | Complex | Simple |
| Limits | Hardware only | Rate limits |

### When to Use Local

- Sensitive/proprietary code
- No internet access
- Cost optimization
- Learning/experimentation
- Bulk processing

### When to Use Cloud

- Maximum quality needed
- No GPU available
- Complex reasoning tasks
- First-time setup

## Resources

- [Ollama Documentation](https://ollama.ai/docs)
- [LM Studio](https://lmstudio.ai)
- [llama.cpp](https://github.com/ggerganov/llama.cpp)
- [HuggingFace Models](https://huggingface.co/models?search=gguf)
- [Open LLM Leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard)
