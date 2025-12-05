# Model Quantization Techniques

## Quantization Levels

| Quantization | Bits | Memory | Quality | Use Case |
|-------------|------|--------|---------|----------|
| Q4_0 | 4 | 50% | Low | Minimum RAM |
| Q4_K_S | 4 | 50% | Medium | Low RAM |
| Q4_K_M | 4 | 52% | Good | Balanced |
| Q5_K_S | 5 | 58% | Better | More RAM |
| Q5_K_M | 5 | 60% | Better+ | Recommended |
| Q6_K | 6 | 66% | High | Quality focus |
| Q8_0 | 8 | 75% | Best | Max quality |
| F16 | 16 | 100% | Original | Baseline |

## Memory Requirements (7B Model)

| Quantization | Model Size | RAM Required |
|-------------|------------|--------------|
| Q4_K_M | 4.1 GB | 6 GB |
| Q5_K_M | 4.8 GB | 7 GB |
| Q8_0 | 7.2 GB | 10 GB |
| F16 | 14.0 GB | 18 GB |

## Quantization Selection Guidelines

### By Hardware

**Consumer Hardware (8GB RAM)**:
- Q4_K_M for 7B models
- Q5_K_M if you have 12GB+ RAM
- Consider Q4_0 only for extreme memory constraints

**Mid-Range Hardware (16GB RAM)**:
- Q5_K_M for 7B models (recommended)
- Q6_K for maximum quality
- Q8_0 if quality is critical

**High-End Hardware (32GB+ RAM)**:
- Q8_0 or F16 for best quality
- Can run multiple quantized models simultaneously

### By Use Case

**Voice Assistant (JARVIS)**:
- Q5_K_M: Best balance of quality and latency
- Q4_K_M: Acceptable if memory constrained
- Avoid Q4_0: Quality too low for natural conversation

**Code Generation**:
- Q8_0: Precision matters for code
- Q6_K: Minimum recommended
- Q5_K_M: Only if memory constrained

**Text Summarization**:
- Q5_K_M: Good balance
- Q4_K_M: Acceptable for simple summarization

**Creative Writing**:
- Q8_0: Best for creativity and nuance
- Q6_K: Good alternative
- Q5_K_M: Minimum recommended

## K-Quantization Explained

K-quantizations use importance matrices for better quality:

- **K_S (Small)**: Lower memory, faster, slightly lower quality
- **K_M (Medium)**: Balanced (recommended for most use cases)
- **K_L (Large)**: Higher memory, best quality (rarely needed)

Example for 7B model:
- Q4_K_S: 3.8 GB
- Q4_K_M: 4.1 GB (+300MB for better quality)
- Q4_K_L: 4.4 GB (+300MB more, minimal quality gain)

## Quality-Performance Tradeoffs

### Perplexity Impact

Based on typical 7B model benchmarks:

| Quantization | Perplexity Increase | Quality Loss |
|-------------|---------------------|--------------|
| Q8_0 | +0.5% | Negligible |
| Q6_K | +1.2% | Minimal |
| Q5_K_M | +2.8% | Acceptable |
| Q4_K_M | +5.2% | Noticeable |
| Q4_0 | +8.7% | Significant |

### Latency Impact

Quantization affects inference speed:

| Quantization | CPU Speed | GPU Speed |
|-------------|-----------|-----------|
| F16 | Baseline | Baseline |
| Q8_0 | 1.2x | 1.1x |
| Q6_K | 1.4x | 1.2x |
| Q5_K_M | 1.6x | 1.3x |
| Q4_K_M | 1.8x | 1.4x |

Note: GPU speedups are less dramatic than CPU due to memory bandwidth

## Layer-Wise Quantization

For optimal quality, quantize different layers differently:

```python
# Attention layers: Higher precision (Q6_K or Q8_0)
# MLP layers: Lower precision (Q4_K_M or Q5_K_M)
# Output layer: Highest precision (Q8_0 or F16)
```

This preserves quality where it matters most while reducing memory.
