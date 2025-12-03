---
name: aid-router-ensemble
description: Smart routing - automatically selects best AI model based on task type
tags: [routing, multi-ai, smart-routing, optimization]
---

# 🎯 Ensemble Mode - Smart Routing

Automatically route your request to the best AI model based on task type, optimizing for quality and cost.

## 📋 How It Works

```
Your Request
     ↓
Task Classification (semantic routing)
     ↓
  ┌──┴──────────────────────┐
  │                          │
Massive Context?   Code Generation?   Documentation?   Security?
     ↓                   ↓                  ↓             ↓
Gemini 2.0 Flash   Claude Sonnet    GPT-4o      Claude Sonnet
(2M context)       (best coder)     (clear docs) (security expert)
```

## 🎯 Usage

**Automatic Routing:**
```
/aid-router-ensemble "Analyze the entire codebase for performance issues"
→ Routes to: Gemini 2.0 Flash (massive context capability)

/aid-router-ensemble "Implement user authentication with OAuth2"
→ Routes to: Claude Sonnet (best for code generation + security)

/aid-router-ensemble "Write comprehensive API documentation"
→ Routes to: GPT-4o (excellent at documentation)
```

**Force Specific Model:**
```
/aid-router-ensemble "Analyze code" --model gemini-flash
```

**Show Routing Decision:**
```
/aid-router-ensemble "Your request here" --explain
→ Shows why a particular model was chosen
```

## 🧠 Task Classification

### Semantic Routing (Fast - Recommended)

Uses embeddings to classify tasks in <50ms:

```python
Task Examples                          → Route
────────────────────────────────────────────────
"analyze entire codebase"              → massive_context
"read all files in src/"               → massive_context
"summarize the whole project"          → massive_context

"implement feature X"                  → code_generation
"write a function to Y"                → code_generation
"create class Z"                       → code_generation

"audit for security"                   → security_audit
"find vulnerabilities"                 → security_audit
"check OWASP compliance"               → security_audit

"write README"                         → documentation
"document the API"                     → documentation
"explain how this works"               → documentation

"fix this bug"                         → debugging
"why is this failing"                  → debugging
"troubleshoot error"                   → debugging

"design architecture"                  → complex_reasoning
"evaluate trade-offs"                  → complex_reasoning
"recommend approach"                   → complex_reasoning
```

### Task → Model Mapping

| Task Type | Model | Why? | Cost/1M Tokens |
|-----------|-------|------|----------------|
| **massive_context** | Gemini 2.0 Flash | 2M token window | $0.075 input |
| **code_generation** | Claude Sonnet 4.5 | Best coder | $3.00 input |
| **security_audit** | Claude Sonnet 4.5 | Security expert | $3.00 input |
| **documentation** | GPT-4o | Clear writing | $5.00 input |
| **debugging** | Claude Sonnet 4.5 | Great at reasoning | $3.00 input |
| **complex_reasoning** | Claude Opus 4.5 | Maximum capability | $15.00 input |

## 🚀 Implementation

### Step 1: Classify Task

```python
def classify_task(request: str) -> str:
    """
    Classify user request into task type

    Returns: massive_context | code_generation | security_audit |
             documentation | debugging | complex_reasoning
    """

    # Keyword matching (simple but fast)
    request_lower = request.lower()

    # Massive context indicators
    if any(kw in request_lower for kw in [
        "entire codebase",
        "all files",
        "whole project",
        "analyze everything",
        "read all",
        "review entire"
    ]):
        return "massive_context"

    # Security indicators
    if any(kw in request_lower for kw in [
        "security",
        "vulnerability",
        "audit",
        "owasp",
        "exploit",
        "penetration test"
    ]):
        return "security_audit"

    # Documentation indicators
    if any(kw in request_lower for kw in [
        "document",
        "readme",
        "explain",
        "tutorial",
        "guide",
        "how to"
    ]):
        return "documentation"

    # Debugging indicators
    if any(kw in request_lower for kw in [
        "bug",
        "error",
        "fix",
        "debug",
        "broken",
        "not working",
        "failing"
    ]):
        return "debugging"

    # Complex reasoning indicators
    if any(kw in request_lower for kw in [
        "design",
        "architecture",
        "trade-off",
        "evaluate",
        "recommend",
        "best approach",
        "should i"
    ]):
        return "complex_reasoning"

    # Default to code generation
    return "code_generation"
```

### Step 2: Route to Model

```python
def route_to_model(task_type: str, config: dict) -> dict:
    """
    Get model configuration for task type

    Returns:
        {
            "model_name": "claude-sonnet",
            "provider": "anthropic",
            "reasoning": "Best for code generation"
        }
    """

    # Get task routes from config
    task_routes = config.get("modes", {}).get("ensemble", {}).get("task_routes", {})

    # Default mapping
    default_routes = {
        "massive_context": {
            "model": "gemini-flash",
            "reasoning": "2M token context window handles large codebases"
        },
        "code_generation": {
            "model": "claude-sonnet",
            "reasoning": "Best code generation quality"
        },
        "security_audit": {
            "model": "claude-sonnet",
            "reasoning": "Excellent security expertise"
        },
        "documentation": {
            "model": "gpt-4o",
            "reasoning": "Clear, comprehensive documentation"
        },
        "debugging": {
            "model": "claude-sonnet",
            "reasoning": "Strong reasoning for debugging"
        },
        "complex_reasoning": {
            "model": "claude-opus",
            "reasoning": "Maximum capability for complex analysis"
        }
    }

    route = default_routes.get(task_type, default_routes["code_generation"])
    model_name = task_routes.get(task_type, route["model"])

    return {
        "model_name": model_name,
        "reasoning": route["reasoning"]
    }
```

### Step 3: Execute Request

```python
def execute_ensemble(request: str, config: dict, explain: bool = False):
    """Execute request with ensemble routing"""

    # 1. Classify task
    task_type = classify_task(request)

    # 2. Route to model
    routing = route_to_model(task_type, config)
    model_name = routing["model_name"]
    reasoning = routing["reasoning"]

    # 3. Show routing decision if requested
    if explain:
        print(f"""
🎯 Routing Decision
──────────────────
Task Type: {task_type}
Selected Model: {model_name}
Reasoning: {reasoning}
        """)

    # 4. Get model configuration
    models = config["models"]
    model_config = models[model_name]
    provider = model_config["provider"]

    # 5. Gather context
    context = gather_dev_aid_context()

    # 6. Execute with chosen model
    import time
    start = time.time()

    if provider == "anthropic":
        response = execute_with_anthropic(
            model=model_config["model"],
            request=request,
            context=context
        )
    elif provider == "google":
        response = execute_with_gemini(
            model=model_config["model"],
            request=request,
            context=context
        )
    elif provider == "openai":
        response = execute_with_openai(
            model=model_config["model"],
            request=request,
            context=context
        )

    latency = (time.time() - start) * 1000  # ms

    # 7. Calculate cost
    cost = calculate_cost(
        model_name=model_name,
        input_tokens=response["tokens_used"]["input"],
        output_tokens=response["tokens_used"]["output"],
        model_config=model_config
    )

    # 8. Log routing decision
    log_routing_decision(
        mode="ENSEMBLE",
        task_type=task_type,
        model=model_name,
        cost=cost,
        latency=latency
    )

    # 9. Format output
    return format_ensemble_output(
        response=response,
        model_name=model_name,
        task_type=task_type,
        reasoning=reasoning,
        cost=cost,
        latency=latency
    )

def gather_dev_aid_context():
    """Gather Dev-AID context for request"""
    return {
        "memory_bank": {
            "activeContext": read_file_if_exists(".dev-aid/memory-bank/activeContext.md"),
            "patterns": read_file_if_exists(".dev-aid/memory-bank/patterns.md"),
            "decisions": read_file_if_exists(".dev-aid/memory-bank/decisions.md")
        },
        "active_skills": get_active_skills(),
        "git_context": get_git_context()
    }
```

### Step 4: Format Output

```python
def format_ensemble_output(response, model_name, task_type, reasoning, cost, latency):
    """Format ensemble execution output"""

    return f"""
# 🎯 Ensemble Mode Result

## Routing Decision
- **Task Type:** {task_type}
- **Selected Model:** {model_name}
- **Reasoning:** {reasoning}

---

## Response

{response["content"]}

---

## Metrics
- **Cost:** ${cost:.4f}
- **Tokens:** {response["tokens_used"]["input"]}→{response["tokens_used"]["output"]}
- **Latency:** {latency:.0f}ms

---

## Cost Comparison

**Your choice:** {model_name} - ${cost:.4f}

**Alternative costs for same request:**
{generate_cost_comparison(response["tokens_used"], model_name)}

**Savings:** {calculate_savings(cost, response["tokens_used"])}
"""

def generate_cost_comparison(tokens_used, chosen_model):
    """Generate cost comparison table"""

    models_cost = {
        "claude-opus": calculate_cost_for_model("claude-opus", tokens_used),
        "claude-sonnet": calculate_cost_for_model("claude-sonnet", tokens_used),
        "claude-haiku": calculate_cost_for_model("claude-haiku", tokens_used),
        "gemini-flash": calculate_cost_for_model("gemini-flash", tokens_used),
        "gpt-4o": calculate_cost_for_model("gpt-4o", tokens_used),
    }

    output = "| Model | Cost | vs. Your Choice |\n"
    output += "|-------|------|------------------|\n"

    chosen_cost = models_cost[chosen_model]

    for model, cost in sorted(models_cost.items(), key=lambda x: x[1]):
        marker = " ✓" if model == chosen_model else ""
        diff = cost - chosen_cost
        diff_str = f"+${diff:.4f}" if diff > 0 else f"${diff:.4f}"
        output += f"| {model}{marker} | ${cost:.4f} | {diff_str} |\n"

    return output
```

## 📊 Cost Optimization Examples

### Example 1: Massive Context Analysis

```
Request: "Analyze the entire codebase and identify all API endpoints"

Traditional (Claude Sonnet for everything):
- Tokens: 250,000 input → 5,000 output
- Cost: 250K * $3.00/1M + 5K * $15.00/1M = $0.750 + $0.075 = $0.825

Ensemble (Routes to Gemini):
- Tokens: 250,000 input → 5,000 output
- Cost: 250K * $0.075/1M + 5K * $0.30/1M = $0.019 + $0.002 = $0.021

Savings: $0.804 (97% cheaper!)
```

### Example 2: Code Generation

```
Request: "Implement user authentication with JWT tokens"

Ensemble (Routes to Claude Sonnet):
- Tokens: 15,000 input → 8,000 output
- Cost: 15K * $3.00/1M + 8K * $15.00/1M = $0.045 + $0.120 = $0.165

Perfect choice! Claude is the best coder.
```

### Example 3: Documentation

```
Request: "Write comprehensive API documentation for the auth module"

Traditional (Claude Sonnet):
- Cost: $0.180

Ensemble (Routes to GPT-4o):
- Cost: $0.165

Savings: $0.015 + better documentation quality
```

## 🔧 Configuration

Ensemble routing is configured in `.dev-aid/config/routing.json`:

```json
{
  "modes": {
    "ensemble": {
      "enabled": true,
      "routing_strategy": "semantic",
      "task_routes": {
        "massive_context": "gemini-flash",
        "code_generation": "claude-sonnet",
        "security_audit": "claude-sonnet",
        "documentation": "gpt-4o",
        "debugging": "claude-sonnet",
        "complex_reasoning": "claude-opus"
      }
    }
  }
}
```

## 🎯 Example Session

```
User: /aid-router-ensemble "Read all 200 files and create an architecture diagram"

🎯 Routing Decision
──────────────────
Task Type: massive_context
Selected Model: gemini-flash
Reasoning: 2M token context window handles large codebases

[Executes with Gemini...]

# 🎯 Ensemble Mode Result

## Routing Decision
- **Task Type:** massive_context
- **Selected Model:** gemini-flash
- **Reasoning:** 2M token context window handles large codebases

---

## Response

I've analyzed all 200 files in your codebase. Here's the architecture:

[Comprehensive analysis...]

---

## Metrics
- **Cost:** $0.021
- **Tokens:** 250,000→5,000
- **Latency:** 8,500ms

---

## Cost Comparison

**Your choice:** gemini-flash - $0.021

**Alternative costs for same request:**
| Model | Cost | vs. Your Choice |
|-------|------|------------------|
| gemini-flash ✓ | $0.021 | $0.000 |
| claude-haiku | $0.065 | +$0.044 |
| gpt-4o | $0.325 | +$0.304 |
| claude-sonnet | $0.825 | +$0.804 |
| claude-opus | $3.825 | +$3.804 |

**Savings:** $0.804 vs. Claude Sonnet (97% cheaper!)
```

## 🚨 Fallback Handling

If primary model fails, automatically falls back:

```python
def execute_with_fallback(request, primary_model):
    """Execute with automatic fallback"""

    fallback_chain = config["fallback_chain"]

    for model in [primary_model] + fallback_chain:
        try:
            return execute_with_model(model, request)
        except Exception as e:
            log_error(f"{model} failed: {e}")
            if model == fallback_chain[-1]:
                raise Exception("All models failed")
            else:
                log_info(f"Falling back to {fallback_chain[fallback_chain.index(model)+1]}")
```

---

**Now execute ensemble routing above!**

1. Parse user request
2. Classify task type (semantic routing)
3. Route to optimal model
4. Execute request with model
5. Calculate cost and metrics
6. Format output with cost comparison
