## 9. Common Mistakes

### ❌ DON'T: Use Unverified Models

```python
# BAD - No verification
llm = Llama(model_path=user_provided_path)

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

