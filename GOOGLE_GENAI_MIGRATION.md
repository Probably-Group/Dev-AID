# Google Generative AI SDK Migration Plan

**From:** `google-generativeai` 0.1.0rc1 (DEPRECATED, EOL Aug 31, 2025)
**To:** `google-genai` 1.53.0 (Unified SDK)
**Date Created:** 2025-12-08

---

## 🚨 Why This Migration is Critical

- **EOL Date:** August 31, 2025 (less than 9 months away)
- **Current Status:** Using release candidate (0.1.0rc1) - UNSTABLE
- **Risk:** No bug fixes or security patches after EOL
- **New SDK:** Officially recommended by Google

---

## 📍 Current Usage Analysis

### Files Affected (2 files)

1. **`.dev-aid/orchestration/router/api_clients.py`** (Lines 224-323)
   - Class: `GeminiClient`
   - Usage: Model initialization, content generation, chat conversations
   - Complexity: Medium (supports both single-turn and multi-turn)

2. **`.dev-aid/orchestration/models-updater.py`** (Lines 16, 113-140)
   - Function: `discover_google_models()`
   - Usage: List available models for auto-discovery
   - Complexity: Low (simple list operation)

### Current API Calls

```python
# api_clients.py
import google.generativeai as genai
genai.configure(api_key=api_key)
gemini_model = genai.GenerativeModel(model)
response = gemini_model.generate_content(prompt, generation_config=...)
chat = gemini_model.start_chat(history=...)
response = chat.send_message(last_message)

# models-updater.py
import google.generativeai as genai
genai.configure(api_key=api_key)
models = genai.list_models()
```

---

## 🔄 Migration Mapping

### 1. Import Changes

**Before:**
```python
import google.generativeai as genai
```

**After:**
```python
from google import genai
from google.genai import types  # For config objects
```

### 2. Client Initialization

**Before:**
```python
genai.configure(api_key=api_key)
# Global configuration
```

**After:**
```python
# Client-based initialization
client = genai.Client(api_key=api_key)
# Store client as instance variable
```

### 3. Content Generation (Single-Turn)

**Before:**
```python
gemini_model = genai.GenerativeModel(model)
response = gemini_model.generate_content(
    prompt,
    generation_config={
        "temperature": temperature,
        "max_output_tokens": max_tokens,
    }
)
content = response.text
```

**After:**
```python
response = client.models.generate_content(
    model=model,
    contents=prompt,
    config=types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_tokens
    )
)
content = response.text
```

### 4. Chat Conversations (Multi-Turn)

**Before:**
```python
gemini_model = genai.GenerativeModel(model)
chat = gemini_model.start_chat(history=conversation_parts[:-1])
response = chat.send_message(last_message)
```

**After:**
```python
# Option 1: Use contents list directly
response = client.models.generate_content(
    model=model,
    contents=conversation_parts  # Full conversation history
)

# Option 2: Use chat session
chat = client.chats.create(model=model)
for turn in conversation_parts[:-1]:
    chat.send_message(turn["parts"][0])
response = chat.send_message(last_message)
```

### 5. Model Listing

**Before:**
```python
models = genai.list_models()
for model in models:
    model_id = model.name.replace("models/", "")
```

**After:**
```python
models = client.models.list()
for model in models:
    model_id = model.name  # Already without "models/" prefix
```

---

## 📝 Implementation Plan

### Phase 1: Update api_clients.py (30-45 min)

**File:** `.dev-aid/orchestration/router/api_clients.py`

**Changes Required:**

1. **Update imports** (line 224):
```python
# OLD
import google.generativeai as genai

# NEW
from google import genai
from google.genai import types
```

2. **Update __init__** (lines 220-232):
```python
def __init__(self, api_key: str, model_config: Dict[str, Any]):
    super().__init__(api_key, model_config)

    try:
        from google import genai
        from google.genai import types

        # Create client instance instead of global configure
        self.client = genai.Client(api_key=api_key)
        self.types = types  # Store for later use
    except ImportError:
        raise ImportError(
            "google-genai package not installed. "
            "Install with: pip install google-genai"
        )
```

3. **Update send_request - single-turn** (lines 261-301):
```python
# Build config object
config = self.types.GenerateContentConfig(
    temperature=temperature,
    max_output_tokens=max_tokens,
)

# Make API call
response = self.client.models.generate_content(
    model=model,
    contents=prompt,
    config=config
)

# Extract response
content = response.text

# Token counting (if available in response)
input_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0)
output_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0)

# Fallback to estimation if not available
if input_tokens == 0:
    input_tokens = len(prompt.split()) * 1.3
if output_tokens == 0:
    output_tokens = len(content.split()) * 1.3
```

4. **Update send_request - multi-turn** (lines 303-323):
```python
# Convert to new contents format
contents = []
for part in conversation_parts:
    contents.append({
        "role": part["role"],
        "parts": [{"text": part["parts"][0]}]
    })

# Make API call
response = self.client.models.generate_content(
    model=model,
    contents=contents,
    config=config
)

content = response.text
# Token counting same as above
```

### Phase 2: Update models-updater.py (15-20 min)

**File:** `.dev-aid/orchestration/models-updater.py`

**Changes Required:**

1. **Update import** (line 16):
```python
# OLD
import google.generativeai as genai

# NEW
from google import genai
```

2. **Update discover_google_models()** (lines 105-143):
```python
def discover_google_models(self) -> List[ModelInfo]:
    """Discover Gemini models from Google API"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠ No GOOGLE_API_KEY found, skipping Gemini models")
        return []

    try:
        # Create client
        client = genai.Client(api_key=api_key)

        # List available models
        models = client.models.list()

        discovered = []
        for model in models:
            # model.name is already cleaned (no "models/" prefix in new SDK)
            model_id = model.name

            # Only process Gemini models
            if not model_id.startswith("gemini"):
                continue

            # Rest of the logic remains the same
            match = re.search(r"gemini-(\d+)\.(\d+)-(flash|pro)", model_id)
            if match:
                major = int(match.group(1))
                minor = int(match.group(2))
                tier = match.group(3)
                version = float(f"{major}.{minor}")

                discovered.append(
                    ModelInfo(id=model_id, tier=tier, version=version, provider="gemini")
                )

        return discovered

    except Exception as e:
        print(f"⚠ Error discovering Google models: {e}")
        return []
```

### Phase 3: Update Dependencies (5 min)

**File:** `.dev-aid/orchestration/requirements.txt`

```diff
# OLD
- google-generativeai==0.1.0rc1  # Google Gemini API

# NEW
+ google-genai==1.53.0           # Google Gemini API (Unified SDK)
```

**File:** `.dev-aid/orchestration/pyproject.toml`

```diff
# OLD
- "google-generativeai>=0.3.0",

# NEW
+ "google-genai>=1.53.0",
```

### Phase 4: Testing (15-20 min)

**Test checklist:**

1. **Unit tests:**
```bash
cd .dev-aid/orchestration
source venv/bin/activate
pytest tests/ -v -k google
```

2. **Manual API test:**
```bash
# Set API key
export GOOGLE_API_KEY="your-key-here"

# Test with router
python -c "
from router.api_clients import GeminiClient
client = GeminiClient('your-key', {'models': {}})
response = client.send_request(
    messages=[{'role': 'user', 'content': 'Say hello'}],
    model='gemini-2.0-flash',
    max_tokens=50
)
print(response.content)
"
```

3. **Test model discovery:**
```bash
python models-updater.py --dry-run
```

---

## ⚠️ Breaking Changes to Watch For

### 1. Response Object Structure

The new SDK may have different response object attributes:
- Check `response.text` still works
- Check `response.candidates[0].finish_reason` path
- Verify token counting: `response.usage_metadata`

### 2. Error Handling

Error types and messages may have changed:
- Update error handling in `@track_api_call` decorator
- Test rate limiting errors
- Test invalid API key errors

### 3. Chat History Format

Multi-turn conversation format may differ:
- Old: `{"role": "user", "parts": [content]}`
- New: Verify if format changed

---

## 🔄 Rollback Plan

If migration fails:

```bash
# 1. Revert code changes
git checkout HEAD -- .dev-aid/orchestration/router/api_clients.py
git checkout HEAD -- .dev-aid/orchestration/models-updater.py
git checkout HEAD -- .dev-aid/orchestration/requirements.txt
git checkout HEAD -- .dev-aid/orchestration/pyproject.toml

# 2. Reinstall old package
cd .dev-aid/orchestration
source venv/bin/activate
pip install google-generativeai==0.1.0rc1

# 3. Run tests
pytest tests/ -v
```

---

## 📊 Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| API incompatibility | Low | High | Thorough testing, rollback plan ready |
| Response format changes | Medium | Medium | Defensive coding, check attributes exist |
| Token counting differences | Medium | Low | Keep estimation fallback |
| Chat session behavior | Low | Medium | Test multi-turn conversations |

---

## ✅ Success Criteria

- [ ] All imports updated
- [ ] Client initialization working
- [ ] Single-turn generation working
- [ ] Multi-turn conversations working
- [ ] Model listing working
- [ ] All existing tests pass
- [ ] Manual API test successful
- [ ] Token counting accurate (or reasonable estimation)
- [ ] Error handling robust
- [ ] Documentation updated

---

## 📅 Timeline

**Total Estimated Time:** 1.5 - 2 hours

- Phase 1 (api_clients.py): 30-45 min
- Phase 2 (models-updater.py): 15-20 min
- Phase 3 (dependencies): 5 min
- Phase 4 (testing): 15-20 min
- Buffer for issues: 15-30 min

**Recommended Execution:** Single session, with rollback ready

---

## 📚 Resources

- **Migration Guide:** https://ai.google.dev/gemini-api/docs/migrate
- **New SDK Docs:** https://googleapis.github.io/python-genai/
- **PyPI Package:** https://pypi.org/project/google-genai/
- **GitHub Repo:** https://github.com/googleapis/python-genai

---

**Next Step:** Execute Phase 1 (update api_clients.py)
