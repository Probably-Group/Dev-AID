---
name: aid-router-challenger-rag
description: Challenger mode with local semantic code search (100% local, $0 cost)
tags: [routing, multi-ai, security, review, rag, semantic-search]
---

# 🔍 Challenger Mode with Local RAG

Execute your request with **Challenger mode + Semantic Search**: Local AI finds relevant code context, Claude generates with that context, then Gemini reviews for security issues.

## 🎯 Enhanced Features

**vs Standard Challenger Mode:**
- ✅ **Semantic code search** - Finds relevant existing code automatically
- ✅ **100% local** - Code never leaves your machine
- ✅ **Zero cost** - No API fees for embeddings
- ✅ **Context-aware** - Claude sees similar implementations
- ✅ **Better reviews** - Gemini checks against your codebase patterns

## 📋 How It Works

```
1. Semantic Search (local RAG)
   └─ Search codebase for relevant context
   └─ Find similar implementations
   └─ Retrieve security guidelines from memory bank
   └─ 100% local, zero cost

2. Claude generates implementation
   └─ With perfect context from your codebase
   └─ Following your existing patterns
   └─ Using similar code as reference
   └─ Implements your feature

3. Gemini reviews Claude's work
   └─ With same codebase context
   └─ Scans for OWASP Top 10 vulnerabilities
   └─ Checks consistency with existing code
   └─ Identifies performance issues
   └─ Rates severity (LOW/MEDIUM/HIGH/CRITICAL)

4. If issues found → Claude refines
   └─ Addresses Gemini's feedback
   └─ Provides improved implementation

5. You see both perspectives
   ├─ Relevant existing code (context)
   ├─ Original implementation
   ├─ Security critique
   └─ Improved version (if needed)
```

## 🚀 Usage

**Basic Usage:**
```
/aid-router-challenger-rag "Implement OAuth2 authentication with JWT tokens"
```

**What happens:**
1. Searches codebase for: "OAuth2", "authentication", "JWT", "tokens"
2. Finds existing auth patterns, security guidelines
3. Claude generates using your codebase patterns
4. Gemini reviews with same context

**With Specific Context:**
```
/aid-router-challenger-rag "Add password reset functionality"
```

**For Security-Critical Features:**
```
/aid-router-challenger-rag "Implement payment processing with Stripe"
```

## 🛠️ Setup Required

This command requires claude-context-local to be installed and indexed.

**Check if ready:**
```bash
./.dev-aid/scripts/rag-status.sh
```

**If not installed:**
```bash
./.dev-aid/scripts/setup-rag.sh
```

**If code changed, reindex:**
```bash
./.dev-aid/scripts/reindex-codebase.sh
```

## 💡 Example

**Request:**
```
/aid-router-challenger-rag "Implement password validation function"
```

**Step 1: Semantic Search finds:**
- `src/auth/password.py:12` - existing password validation
- `src/auth/utils.py:45` - password hashing utilities
- `.dev-aid/memory-bank/security.md` - password requirements
- `tests/test_auth.py:89` - password validation tests

**Step 2: Claude generates:**
```python
def validate_password(password: str) -> tuple[bool, str]:
    """Validate password meets security requirements.

    Based on existing pattern in src/auth/password.py
    Follows guidelines from .dev-aid/memory-bank/security.md
    """
    # Minimum 12 characters (per security guidelines)
    if len(password) < 12:
        return False, "Password must be at least 12 characters"

    # Must contain uppercase, lowercase, digit, special char
    # (Pattern from existing validation functions)
    ...
```

**Step 3: Gemini reviews:**
```
ISSUES FOUND: 2
SEVERITY: MEDIUM

1. Missing rate limiting check
   Location: Function entry
   Risk: Brute force vulnerability

2. No logging for failed attempts
   Location: Return statements
   Risk: Security monitoring blind spot

POSITIVE: Follows existing patterns, good length requirement
```

**Step 4: Claude refines:**
```python
def validate_password(password: str, user_id: str) -> tuple[bool, str]:
    """Validate password with rate limiting and logging."""

    # Rate limiting (addressing Gemini's feedback)
    if rate_limiter.is_exceeded(user_id, "password_validation"):
        logger.warning(f"Rate limit exceeded: {user_id}")
        return False, "Too many attempts, please try again later"

    # Validation logic...

    # Log failed attempts (addressing Gemini's feedback)
    if not is_valid:
        logger.info(f"Password validation failed: {user_id}")

    return is_valid, message
```

## 🎯 Best For

**Use this command when:**
- ✅ Security-critical features (auth, payments, data handling)
- ✅ Want to match existing codebase patterns
- ✅ Need to find similar implementations for reference
- ✅ Large codebase with many patterns to learn from
- ✅ Privacy matters (100% local)
- ✅ Cost-conscious (zero API fees)

**Use standard `/aid-router-challenger` when:**
- ⚠️ Small codebase (RAG won't find much context)
- ⚠️ Brand new feature (no existing patterns to reference)
- ⚠️ RAG not set up yet

## 📊 Performance

**Semantic search speed:**
- ~0.15 seconds (local FAISS)
- Zero API cost
- Works offline

**Context quality:**
- Finds relevant code you might have forgotten
- Surfaces security guidelines from memory bank
- Retrieves similar implementations automatically

## 🔒 Privacy & Cost

**Privacy:**
- ✅ 100% local semantic search
- ✅ Code never sent to embedding APIs
- ✅ Works completely offline
- ✅ claude-context-local (local EmbeddingGemma model)

**Cost:**
- ✅ Semantic search: $0 (local)
- ✅ Embeddings: $0 (local model)
- ⚠️ Claude generation: Standard API cost
- ⚠️ Gemini review: Standard API cost

**Net savings:**
- Traditional RAG: ~$0.02 per query (embedding API)
- This approach: $0 for RAG portion
- **Savings: 100% on RAG costs**

## 🧪 Technical Details

**RAG System:** claude-context-local (https://github.com/FarhanAliRaza/claude-context-local)

**How semantic search works:**
1. Your query → EmbeddingGemma (local 768-dim vectors)
2. FAISS similarity search (local index)
3. Returns top 5-10 most relevant code chunks
4. Injected into Claude's context automatically via MCP

**What gets indexed:**
- Python files (AST-parsed for functions/classes)
- JavaScript/TypeScript (tree-sitter parsed)
- Configuration files (JSON, TOML, YAML)
- Documentation (Markdown)
- Memory bank content

**What doesn't get indexed:**
- `node_modules/`, `.venv/`, `__pycache__/`
- `build/`, `dist/`, `.git/`
- Binary files, images

## 📚 Related Commands

- `/aid-router-challenger` - Standard challenger mode (no RAG)
- `/aid-router-ensemble-rag` - Smart routing with RAG
- `/aid-router-status` - View routing statistics

## 🔧 Troubleshooting

**"MCP tool 'code-search' not found"**
- Run: `./.dev-aid/scripts/setup-rag.sh`

**"No results found" or poor results**
- Reindex: `./.dev-aid/scripts/reindex-codebase.sh`
- Check indexed files: `./.dev-aid/scripts/rag-status.sh`

**Semantic search is slow**
- Check GPU acceleration: `./.dev-aid/scripts/rag-status.sh`
- On CPU: ~0.5s is normal, on GPU: ~0.1s

---

**Powered by:** claude-context-local • 100% Local • Zero Cost • Privacy-First
