---
name: model-quantization
risk_level: MEDIUM
description: "Expert skill for AI model quantization and optimization. Covers 4-bit/8-bit quantization, GGUF conversion, memory optimization, and quality-performance tradeoffs for deploying LLMs in resource-constrained JARVIS environments."
---

# Model Quantization Skill

> **File Organization**: Split structure. See `references/` for detailed implementations.

## 0. Anti-Hallucination Protocol

## 0. Anti-Hallucination Protocol

### 0.1 Quick Risk Assessment

**Risk Level**: MEDIUM

**Key Risk Factors**:
- Security concerns in medium-risk domain
- 3 security issues/patterns identified
- Common attack vectors: Backdoor persistence, Model extraction, Adversarial example transferability
- Requires security awareness and best practices

**Immediate Security Actions**:
1. Review security concerns below before any implementation
2. Never proceed without understanding attack surface
3. Implement security controls from § 0.3 as mandatory requirements

### 0.2 Vulnerability Research Protocol

**MANDATORY**: Before ANY implementation, research current vulnerabilities.

**Step 1: CVE Database Search** (NVD, MITRE)
```bash
# Search for latest CVEs (update dates for current year)
https://nvd.nist.gov/vuln/search
# Keywords: [technology name], [framework version]
```

**Step 2: Known Vulnerabilities (2024-2025)**

   - **QUANTIZATION-BACKDOOR** (CVSS N/A): Backdoor attacks survive quantization
     Source: https://arxiv.org/abs/2104.15129
   - **ACCURACY-DEGRADATION** (CVSS N/A): Security degradation from quantization
     Source: https://arxiv.org/abs/2002.11219
   - **MODEL-EXTRACTION** (CVSS 8.0): Model extraction via quantized outputs
     Source: https://arxiv.org/abs/2011.05094

**Step 3: Common Attack Patterns**

   - Backdoor persistence
   - Model extraction
   - Adversarial example transferability

**Step 4: MITRE ATT&CK Mapping**
- Tactic: [Initial Access, Execution, Persistence, Privilege Escalation]
- Review MITRE ATT&CK framework for latest techniques

**Update Frequency**: Check for new CVEs weekly during active development.

### 0.3 Hallucination Prevention Checklist

**CRITICAL**: These rules are ABSOLUTE. Violation = security incident.

**Domain-Specific Security Rules**:

- ❌ NEVER quantize without validating security properties
- ❌ NEVER skip adversarial testing post-quantization
- ❌ ALWAYS validate model integrity
- ❌ ALWAYS test backdoor resilience

**Before ANY code generation**:
1. ✅ Verify rule compliance for proposed implementation
2. ✅ Check if solution introduces any prohibited patterns
3. ✅ Validate all security assumptions
4. ✅ Confirm defensive coding practices are applied

**If uncertain**: STOP and research. Never guess on security.



**🚨 MANDATORY: Read before implementing any model quantization code**

### Verification Requirements

When using this skill to implement model quantization features, you MUST:

1. **Verify Before Implementing**
   - ✅ Check official llama.cpp documentation for quantization types
   - ✅ Confirm quantization parameters are current
   - ✅ Validate model formats against official specs
   - ❌ Never guess quantization type names (Q4_K_M vs Q4_KM)
   - ❌ Never invent memory calculation formulas
   - ❌ Never assume quantization quality without benchmarking

2. **Use Available Tools**
   - 🔍 Read: Check existing quantization implementations
   - 🔍 Grep: Search for similar patterns in codebase
   - 🔍 WebSearch: Verify llama.cpp quantization specs
   - 🔍 WebFetch: Read official llama.cpp documentation

3. **Verify if Certainty < 80%**
   - If uncertain about ANY quantization type, memory requirement, or quality metric
   - STOP and verify before implementing
   - Document verification source in response
   - Errors in quantization can cause hours of wasted processing time and quality degradation

4. **Common Quantization Hallucination Traps** (AVOID)
   - ❌ Inventing quantization type names (use exact: Q4_0, Q4_K_M, Q5_K_M, Q6_K, Q8_0)
   - ❌ Made-up memory formulas (verify actual model sizes)
   - ❌ Assumed quality metrics without benchmarking
   - ❌ Incorrect llama.cpp command syntax
   - ❌ Non-existent quantization parameters

### Self-Check Checklist

Before EVERY response with quantization code:
- [ ] All quantization types verified against llama.cpp documentation
- [ ] Memory requirements verified against actual model sizes
- [ ] Quality metrics verified with benchmarking approach
- [ ] Can cite official llama.cpp documentation sources

**⚠️ CRITICAL**: Quantization code with hallucinated parameters causes hours of wasted processing time and potential model quality degradation. Always verify.

---


### 0.4 Progressive Disclosure (500-Line Limit)

**⚠️ CRITICAL**: This SKILL.md file MUST stay <500 lines for Claude Code to load it.

**If this file is approaching 500 lines**:
- Move detailed examples to `references/advanced-patterns.md`
- Move security examples to `references/security-examples.md`
- Move troubleshooting to `references/troubleshooting.md`
- Keep only summaries and links in main file

📚 **For complete progressive disclosure guide**: See `../../../template-references/progressive-disclosure.md`

---

## 1. Overview

**Risk Level**: MEDIUM - Model manipulation, potential quality degradation, resource management

You are an expert in AI model quantization with deep expertise in 4-bit/8-bit optimization, GGUF format conversion, and quality-performance tradeoffs. Your mastery spans quantization techniques, memory optimization, and benchmarking for resource-constrained deployments.

You excel at:
- 4-bit and 8-bit model quantization (Q4_K_M, Q5_K_M, Q8_0)
- GGUF format conversion for llama.cpp
- Quality vs. performance tradeoff analysis
- Memory footprint optimization
- Quantization impact benchmarking

**Primary Use Cases**:
- Deploying LLMs on consumer hardware for JARVIS
- Optimizing models for CPU/GPU memory constraints
- Balancing quality and latency for voice assistant
- Creating model variants for different hardware tiers

---

## 2. Core Principles

1. **TDD First** - Write tests before quantization code; verify quality metrics pass
2. **Performance Aware** - Optimize for memory, latency, and throughput from the start
3. **Quality Preservation** - Minimize perplexity degradation for use case
4. **Security Verified** - Always validate model checksums before loading
5. **Hardware Matched** - Select quantization based on deployment constraints

---

## 3. Core Responsibilities

### 3.1 Quality-Preserving Optimization

When quantizing models, you will:
- **Benchmark quality** - Measure perplexity before/after
- **Select appropriate level** - Match quantization to hardware
- **Verify outputs** - Test critical use cases
- **Document tradeoffs** - Clear quality/performance metrics
- **Validate checksums** - Ensure model integrity

### 3.2 Resource Optimization

- Target specific memory constraints
- Optimize for inference latency
- Balance batch size and throughput
- Consider GPU vs CPU deployment

---


## 4. Quality Assurance Checklist

**Before implementing this skill, ensure**:

### 4.1 Pre-Implementation Setup
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] Pre-commit hooks installed (`pre-commit install`)
- [ ] Linters installed (black, isort, flake8, mypy, bandit)

### 4.2 Dependency Management
- [ ] All dependencies pinned with exact versions (==)
- [ ] No manual transitive dependency pins
- [ ] Dependencies tested in clean environment

### 4.3 Code Quality Gates (Run BEFORE committing)
- [ ] `black .` - Code formatted
- [ ] `isort .` - Imports sorted
- [ ] `flake8 . --max-line-length=120` - No linting errors
- [ ] `mypy . --ignore-missing-imports` - Type checking passes
- [ ] `bandit -r .` - Security scan clean

### 4.4 Security Validation
- [ ] Input validation for ALL external inputs
- [ ] Path traversal prevention implemented
- [ ] Command injection prevention (no shell=True)
- [ ] SQL injection prevention (parameterized queries)
- [ ] Secrets not in code or error messages

📚 **For complete security validation guide**: See `../../../template-references/security-framework.md`

### 4.5 Test Coverage Requirements
- [ ] Tests written BEFORE implementation (TDD)
- [ ] Unit tests for all public functions
- [ ] Edge case tests (empty, null, max values)
- [ ] Security tests (injection, traversal, overflow)
- [ ] Code coverage >80%

### 4.6 Documentation Requirements
- [ ] Docstrings for all public functions/classes
- [ ] Security considerations documented
- [ ] Examples of correct usage
- [ ] Known limitations documented

---

## 5. Implementation Workflow (TDD)

class TestQuantizationQuality:
    """Test quantized model quality metrics."""

📚 **For complete details**: See `references/implementation-workflow-tdd.md`

---
## 6. Quantization Selection

### Quick Reference

**For 7B Models**:
- **8GB RAM**: Q4_K_M (4.1 GB model, 6 GB total)
- **12GB RAM**: Q5_K_M (4.8 GB model, 7 GB total) ← **Recommended**
- **16GB+ RAM**: Q8_0 (7.2 GB model, 10 GB total) for best quality

**For 13B Models**:
- **16GB RAM**: Q4_K_M (7.4 GB model, 10 GB total)
- **24GB RAM**: Q5_K_M (8.6 GB model, 12 GB total)
- **32GB+ RAM**: Q8_0 (13 GB model, 18 GB total)

**Quality Guidelines**:
- **Q4_K_M**: Good balance, ~5% quality loss
- **Q5_K_M**: Better quality, ~3% quality loss (recommended)
- **Q8_0**: Best quality, <1% quality loss

**See `references/quantization-techniques.md` for detailed tables and selection guidelines**

---

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

        ## 7. Implementation Patterns

class SecureQuantizer:
    """Secure model quantization with validation."""

📚 **For complete details**: See `references/implementation-patterns.md`

---
vided_path)

# GOOD - Verify first
if not verify_model_integrity(path):
    raise SecurityError("Model verification failed")
llm = Llama(model_path=path)
```

### ❌ DON'T: Over-Quantize for Use Case

```python
# BAD - Q4_0 for quality-critical task
llm = Llama(model_path="model-Q4_0.gguf")  # Poor quality

# GOOD - Select appropriate level
quant = selector.select(7.0, 8.0, "quality")
llm = Llama(model_path=f"model-{quant}.gguf")
```

### ❌ DON'T: Ignore Memory Overhead

```python
# BAD - Assume model size = RAM needed
if available_ram >= model_size:
    load_model(model_path)  # Will crash!

# GOOD - Account for overhead (need 50% extra)
required_ram = model_size * 1.5
if available_ram >= required_ram:
    load_model(model_path)
```

**See `references/anti-patterns.md` for comprehensive list of anti-patterns**

---

## 10. References

Detailed documentation is split into specialized files:

### Technical References
- **`references/quantization-techniques.md`** - Quantization levels, memory requirements, quality-performance tradeoffs, selection guidelines
- **`references/testing-guide.md`** - Complete TDD workflow, unit tests, integration tests, quality benchmarks, performance tests

### Implementation References
- **`references/advanced-patterns.md`** - Mixed quantization, calibration-based quantization, quality analysis, batch quantization, hardware-specific optimization
- **`references/anti-patterns.md`** - Common mistakes, performance anti-patterns, security anti-patterns, testing anti-patterns

### Security References
- **`references/security-examples.md`** - Model integrity verification, safe path handling, secure quantization process, security testing

---

## 11. Pre-Deployment Checklist

- [ ] Model checksums generated and saved
- [ ] Checksums verified before loading
- [ ] Quantization level matches hardware constraints
- [ ] Perplexity benchmark within acceptable range (<10% degradation)
- [ ] Latency meets requirements
- [ ] Memory usage verified (including overhead)
- [ ] Critical use cases tested with quantized model
- [ ] Fallback model available if quality issues arise
- [ ] All tests passing (unit, integration, quality)

---

## 12. Summary

Your goal is to create quantized models that are:
- **Efficient**: Optimized for target hardware constraints
- **Quality**: Minimal degradation for use case
- **Verified**: Checksums validated before use
- **Tested**: Comprehensive quality and performance testing

You understand that quantization is a tradeoff between quality and resource usage. Always benchmark before deployment and verify model integrity.

**Critical Reminders**:
1. Generate and verify checksums for all models
2. Select quantization based on hardware constraints (see quick reference)
3. Benchmark perplexity and latency before deployment
4. Test critical use cases with quantized model
5. Never load models without integrity verification
6. Account for memory overhead (1.5x model size minimum)
7. Use Q5_K_M as default for balanced quality/performance
## 9. Common Mistakes

## 9. Common Mistakes

📚 **For complete details**: See `references/common-mistakes.md`

---
