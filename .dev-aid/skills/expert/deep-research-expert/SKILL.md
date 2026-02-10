---
name: deep-research-expert
version: 2.0.0
description: "Deep research workflows with Gemini, Tavily, and Perplexity for comprehensive technical investigation and synthesis. Use when conducting deep technical research, multi-source analysis, or comprehensive investigations. Do NOT use for web scraping (use browser-automation)."
risk_level: LOW
---

# Deep Research Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE providing guidance:**
1. Verify claims against authoritative sources
2. Distinguish between established practices and opinions
3. Never invent statistics, studies, or references
4. If unsure, state uncertainty explicitly

### 0.2 Risk Level: LOW

**Verification requirements:**
- Cross-reference recommendations with industry standards
- Cite sources when making specific claims
- Acknowledge when best practices vary by context

---

## 1. Security Principles

### 1.1 Source Verification (CWE-345)

**Principle:** Verify authenticity of all information sources. Cross-reference claims.

```python
# ❌ WRONG - Single source, no verification
async def research(query: str) -> str:
    result = await search_api.search(query)
    return result[0].content  # Trust first result!

# ✅ CORRECT - Multi-source verification
from dataclasses import dataclass
from typing import Optional
from enum import Enum

class SourceTier(Enum):
    PRIMARY = "primary"      # Official docs, academic papers
    SECONDARY = "secondary"  # Reputable news, expert blogs
    TERTIARY = "tertiary"    # Forums, social media

@dataclass
class Source:
    url: str
    tier: SourceTier
    retrieval_date: str
    content_hash: str

@dataclass
class VerifiedClaim:
    claim: str
    sources: list[Source]
    confidence: float  # 0.0-1.0
    contradictions: list[str]

async def research_with_verification(query: str) -> list[VerifiedClaim]:
    """Research with multi-source verification."""
    # Gather from multiple sources
    results = await asyncio.gather(
        search_scholarly(query),    # Academic sources
        search_official_docs(query), # Official documentation
        search_news(query),         # News sources
        search_forums(query),       # Community knowledge
    )

    claims = extract_claims(results)

    # Verify each claim across sources
    verified = []
    for claim in claims:
        supporting = find_supporting_sources(claim, results)
        contradicting = find_contradicting_sources(claim, results)

        if len(supporting) >= 2:  # Require 2+ sources
            confidence = calculate_confidence(
                supporting_count=len(supporting),
                contradiction_count=len(contradicting),
                source_tiers=[s.tier for s in supporting],
            )
            verified.append(VerifiedClaim(
                claim=claim,
                sources=supporting,
                confidence=confidence,
                contradictions=contradicting,
            ))

    return verified
```

### 1.2 API Key Security (CWE-798)

**Principle:** Never hardcode API keys for research services. Use environment variables.

```python
# ❌ WRONG - Hardcoded API keys
TAVILY_KEY = "tvly-xxxxx"
PERPLEXITY_KEY = "pplx-xxxxx"

# ✅ CORRECT - From environment with validation
import os
from pydantic_settings import BaseSettings

class ResearchConfig(BaseSettings):
    tavily_api_key: str
    perplexity_api_key: str
    serper_api_key: Optional[str] = None

    # Rate limiting
    max_requests_per_minute: int = 60
    max_cost_per_day_usd: float = 10.0

    class Config:
        env_prefix = "RESEARCH_"

config = ResearchConfig()  # Loads from RESEARCH_TAVILY_API_KEY, etc.
```

### 1.3 Content Sanitization (CWE-79)

**Principle:** Sanitize all retrieved content before display or storage.

### 1.4 Rate Limiting (CWE-770)

**Principle:** Implement rate limiting to prevent API abuse and cost overruns.

### 1.5 Citation Integrity (CWE-20)

**Principle:** Validate all citations. Never fabricate references.

### 1.6 Data Retention (CWE-359)

**Principle:** Respect robots.txt. Don't store copyrighted content beyond fair use.

---

## 2. Version Requirements

**ALWAYS use these minimum versions:**

```python
# Research APIs
tavily-python>=0.3.0
google-generativeai>=0.8.0  # For Gemini
anthropic>=0.40.0

# Data processing
beautifulsoup4>=4.12.0
trafilatura>=1.6.0  # Article extraction
newspaper3k>=0.2.8

# Validation
pydantic>=2.0.0
httpx>=0.27.0
```

---

## 3. Code Patterns

### 3.1 WHEN implementing multi-source research

```python
# ❌ WRONG - Sequential, single-source
def research(query):
    return google_search(query)[0]

# ✅ CORRECT - Parallel multi-source with ranking
import asyncio
from dataclasses import dataclass, field
from typing import AsyncIterator
import httpx

@dataclass
class ResearchResult:
    query: str
    findings: list[VerifiedClaim]
    sources_consulted: int
    research_depth: str  # "quick", "standard", "deep"
    timestamp: str

class DeepResearcher:
    def __init__(self, config: ResearchConfig):
        self.config = config
        self.tavily = TavilyClient(api_key=config.tavily_api_key)
        self.http = httpx.AsyncClient(timeout=30.0)

    async def research(
        self,
        query: str,
        depth: str = "standard",
        max_sources: int = 10,
    ) -> ResearchResult:
        """Conduct multi-source research with verification."""

        # Phase 1: Initial broad search
        initial_results = await self._broad_search(query, depth)

        # Phase 2: Extract key claims
        claims = await self._extract_claims(initial_results)

        # Phase 3: Deep dive on each claim
        verified_claims = []
        for claim in claims:
            verification = await self._verify_claim(claim)
            if verification.confidence >= 0.7:
                verified_claims.append(verification)

        # Phase 4: Synthesize findings
        return ResearchResult(
            query=query,
            findings=verified_claims,
            sources_consulted=len(initial_results),
            research_depth=depth,
            timestamp=datetime.utcnow().isoformat(),
        )

    async def _broad_search(self, query: str, depth: str) -> list[dict]:
        """Search multiple sources in parallel."""
        search_tasks = [
            self._search_tavily(query, depth),
            self._search_scholarly(query),
            self._search_official_docs(query),
        ]

        if depth == "deep":
            search_tasks.extend([
                self._search_news(query),
                self._search_patents(query),
            ])

        results = await asyncio.gather(*search_tasks, return_exceptions=True)
        return [r for r in results if not isinstance(r, Exception)]

    async def _search_tavily(self, query: str, depth: str) -> list[dict]:
        """Search using Tavily API."""
        search_depth = "advanced" if depth == "deep" else "basic"

        response = self.tavily.search(
            query=query,
            search_depth=search_depth,
            include_answer=True,
            include_raw_content=True,
            max_results=10,
        )

        return [
            {
                "title": r["title"],
                "url": r["url"],
                "content": r["content"],
                "score": r["score"],
                "tier": self._classify_source(r["url"]),
            }
            for r in response["results"]
        ]

    def _classify_source(self, url: str) -> SourceTier:
        """Classify source reliability tier."""
        domain = urlparse(url).netloc.lower()

        primary_domains = {
            "arxiv.org", "doi.org", "pubmed.ncbi.nlm.nih.gov",
            "docs.python.org", "developer.mozilla.org",
            "kubernetes.io", "rust-lang.org",
        }

        secondary_domains = {
            "github.com", "stackoverflow.com", "medium.com",
            "dev.to", "martinfowler.com",
        }

        if any(d in domain for d in primary_domains):
            return SourceTier.PRIMARY
        elif any(d in domain for d in secondary_domains):
            return SourceTier.SECONDARY
        return SourceTier.TERTIARY
```

### 3.2 WHEN using Gemini for research synthesis

```python
# ❌ WRONG - No grounding, hallucination risk
def synthesize(findings: list[str]) -> str:
    response = model.generate_content(f"Summarize: {findings}")
    return response.text

# ✅ CORRECT - Grounded synthesis with citations
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

class GeminiResearchSynthesizer:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config={
                "temperature": 0.2,  # Low for factual accuracy
                "top_p": 0.8,
                "max_output_tokens": 4096,
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            },
        )

    async def synthesize_with_grounding(
        self,
        query: str,
        sources: list[VerifiedClaim],
    ) -> str:
        """Synthesize findings with mandatory citations."""

        # Format sources for grounding
        grounding_context = self._format_sources(sources)

        prompt = f"""You are a research assistant. Synthesize the following verified information
to answer the query. You MUST:
1. Only use information from the provided sources
2. Cite sources using [1], [2], etc.
3. Clearly state when sources disagree
4. Never add information not in the sources
5. Say "insufficient evidence" if sources don't answer the query

Query: {query}

Verified Sources:
{grounding_context}

Provide a comprehensive synthesis with citations:"""

        response = await self.model.generate_content_async(prompt)

        # Validate citations exist
        synthesis = response.text
        self._validate_citations(synthesis, len(sources))

        return synthesis

    def _format_sources(self, sources: list[VerifiedClaim]) -> str:
        """Format sources for context injection."""
        formatted = []
        for i, source in enumerate(sources, 1):
            formatted.append(f"""[{i}] Claim: {source.claim}
    Confidence: {source.confidence:.0%}
    Sources: {', '.join(s.url for s in source.sources)}
    Contradictions: {source.contradictions or 'None'}
""")
        return "\n".join(formatted)

    def _validate_citations(self, text: str, max_citation: int):
        """Ensure all citations reference valid sources."""
        import re
        citations = re.findall(r'\[(\d+)\]', text)
        for cit in citations:
            if int(cit) > max_citation or int(cit) < 1:
                raise ValueError(f"Invalid citation [{cit}]")
```

### 3.3 WHEN implementing research caching

```python
# ❌ WRONG - No caching, repeated API calls
async def search(query: str) -> list:
    return await api.search(query)  # Expensive!

# ✅ CORRECT - Intelligent caching with freshness
import hashlib
from datetime import datetime, timedelta
from typing import Optional
import json

class ResearchCache:
    def __init__(
        self,
        cache_dir: Path,
        default_ttl: timedelta = timedelta(hours=24),
    ):
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_key(self, query: str, source: str) -> str:
        """Generate deterministic cache key."""
        content = f"{query}:{source}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    async def get_or_fetch(
        self,
        query: str,
        source: str,
        fetch_fn,
        ttl: Optional[timedelta] = None,
    ):
        """Get from cache or fetch fresh."""
        key = self._cache_key(query, source)
        cache_file = self.cache_dir / f"{key}.json"

        # Check cache
        if cache_file.exists():
            with open(cache_file) as f:
                cached = json.load(f)

            cached_at = datetime.fromisoformat(cached["timestamp"])
            effective_ttl = ttl or self.default_ttl

            if datetime.utcnow() - cached_at < effective_ttl:
                return cached["data"]

        # Fetch fresh
        data = await fetch_fn()

        # Cache result
        with open(cache_file, "w") as f:
            json.dump({
                "timestamp": datetime.utcnow().isoformat(),
                "query": query,
                "source": source,
                "data": data,
            }, f)

        return data

    def invalidate(self, query: str, source: str):
        """Invalidate specific cache entry."""
        key = self._cache_key(query, source)
        cache_file = self.cache_dir / f"{key}.json"
        cache_file.unlink(missing_ok=True)
```

### 3.4 WHEN extracting content from web pages

```python
# ❌ WRONG - Raw HTML parsing
def extract(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()  # Includes nav, ads, etc.

# ✅ CORRECT - Clean article extraction
import trafilatura
from trafilatura.settings import use_config

def create_extraction_config():
    """Configure trafilatura for research extraction."""
    config = use_config()
    config.set("DEFAULT", "EXTRACTION_TIMEOUT", "30")
    config.set("DEFAULT", "MIN_OUTPUT_SIZE", "100")
    config.set("DEFAULT", "MIN_OUTPUT_COMM_SIZE", "50")
    return config

async def extract_article_content(
    url: str,
    http_client: httpx.AsyncClient,
) -> Optional[dict]:
    """Extract clean article content from URL."""
    try:
        # Fetch with timeout and size limit
        response = await http_client.get(
            url,
            follow_redirects=True,
            timeout=15.0,
        )
        response.raise_for_status()

        # Limit content size (prevent memory issues)
        if len(response.content) > 5_000_000:  # 5MB
            return None

        html = response.text

        # Extract with trafilatura
        config = create_extraction_config()
        result = trafilatura.extract(
            html,
            config=config,
            include_comments=False,
            include_tables=True,
            include_links=True,
            output_format="json",
            with_metadata=True,
        )

        if result:
            data = json.loads(result)
            return {
                "title": data.get("title", ""),
                "author": data.get("author", ""),
                "date": data.get("date", ""),
                "content": data.get("text", ""),
                "url": url,
                "word_count": len(data.get("text", "").split()),
            }

    except (httpx.HTTPError, json.JSONDecodeError) as e:
        logger.warning(f"Failed to extract {url}: {e}")

    return None
```

### 3.5 WHEN generating citations

```python
# ❌ WRONG - Inconsistent citation format
def cite(source):
    return f"Source: {source['url']}"

# ✅ CORRECT - Structured citations with multiple formats
from dataclasses import dataclass
from datetime import date
from enum import Enum

class CitationStyle(Enum):
    APA = "apa"
    MLA = "mla"
    CHICAGO = "chicago"
    BIBTEX = "bibtex"

@dataclass
class Citation:
    authors: list[str]
    title: str
    url: str
    publication: Optional[str]
    date_published: Optional[date]
    date_accessed: date

    def format(self, style: CitationStyle) -> str:
        """Format citation in specified style."""
        if style == CitationStyle.APA:
            return self._format_apa()
        elif style == CitationStyle.MLA:
            return self._format_mla()
        elif style == CitationStyle.BIBTEX:
            return self._format_bibtex()
        raise ValueError(f"Unsupported style: {style}")

    def _format_apa(self) -> str:
        """APA 7th edition format."""
        authors = self._format_authors_apa()
        year = self.date_published.year if self.date_published else "n.d."
        return f"{authors} ({year}). {self.title}. {self.publication or ''} {self.url}"

    def _format_authors_apa(self) -> str:
        if not self.authors:
            return ""
        if len(self.authors) == 1:
            return self.authors[0]
        elif len(self.authors) == 2:
            return f"{self.authors[0]} & {self.authors[1]}"
        else:
            return f"{self.authors[0]} et al."

    def _format_bibtex(self) -> str:
        """BibTeX format."""
        key = self._generate_bibtex_key()
        authors = " and ".join(self.authors) if self.authors else "Unknown"
        year = self.date_published.year if self.date_published else ""

        return f"""@online{{{key},
    author = {{{authors}}},
    title = {{{self.title}}},
    url = {{{self.url}}},
    year = {{{year}}},
    urldate = {{{self.date_accessed.isoformat()}}}
}}"""

    def _generate_bibtex_key(self) -> str:
        """Generate unique BibTeX key."""
        author_part = self.authors[0].split()[-1].lower() if self.authors else "unknown"
        year_part = self.date_published.year if self.date_published else "nd"
        title_part = self.title.split()[0].lower() if self.title else "untitled"
        return f"{author_part}{year_part}{title_part}"
```

---

## 4. Anti-Patterns

**NEVER:**
- Trust a single source without verification
- Fabricate or hallucinate citations
- Ignore source recency (prefer recent sources)
- Skip content extraction validation
- Store full copyrighted articles
- Exceed API rate limits
- Use research APIs without cost tracking
- Present uncertain findings as facts

---

## 5. Testing

**ALWAYS test research functionality:**

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_multi_source_verification():
    """Test that claims require multiple sources."""
    researcher = DeepResearcher(config)

    # Mock search results
    with patch.object(researcher, '_broad_search') as mock_search:
        mock_search.return_value = [
            {"content": "Python 3.12 released", "tier": SourceTier.PRIMARY},
            {"content": "Python 3.12 is out", "tier": SourceTier.SECONDARY},
        ]

        result = await researcher.research("Python 3.12 release")

        # Should have verified claim with 2 sources
        assert len(result.findings) >= 1
        assert result.findings[0].confidence >= 0.7

@pytest.mark.asyncio
async def test_citation_validation():
    """Test that invalid citations are rejected."""
    synthesizer = GeminiResearchSynthesizer(api_key="test")

    # Text with invalid citation
    text_with_invalid = "According to [5], this is true."
    sources = [VerifiedClaim(claim="test", sources=[], confidence=0.8, contradictions=[])]

    with pytest.raises(ValueError, match="Invalid citation"):
        synthesizer._validate_citations(text_with_invalid, max_citation=1)

@pytest.mark.asyncio
async def test_source_tier_classification():
    """Test correct source tier assignment."""
    researcher = DeepResearcher(config)

    assert researcher._classify_source("https://arxiv.org/paper") == SourceTier.PRIMARY
    assert researcher._classify_source("https://stackoverflow.com/q") == SourceTier.SECONDARY
    assert researcher._classify_source("https://random-blog.com") == SourceTier.TERTIARY

@pytest.mark.asyncio
async def test_cache_freshness():
    """Test cache respects TTL."""
    cache = ResearchCache(Path("/tmp/test_cache"), default_ttl=timedelta(seconds=1))

    # First fetch
    result1 = await cache.get_or_fetch("test", "source", lambda: "data1")
    assert result1 == "data1"

    # Should return cached
    result2 = await cache.get_or_fetch("test", "source", lambda: "data2")
    assert result2 == "data1"

    # Wait for TTL expiry
    await asyncio.sleep(1.5)

    # Should fetch fresh
    result3 = await cache.get_or_fetch("test", "source", lambda: "data3")
    assert result3 == "data3"
```

---

## 6. Pre-Generation Checklist

**BEFORE generating any research code:**

- [ ] Multiple sources configured (not single API)
- [ ] Source verification implemented
- [ ] Citation format standardized
- [ ] API keys from environment variables
- [ ] Rate limiting configured
- [ ] Cost tracking implemented
- [ ] Cache with TTL for repeated queries
- [ ] Content extraction validates output
- [ ] Grounding prevents hallucination
- [ ] Error handling for API failures

---

**Performance**: Quality over speed. Verify all code examples compile. Never skip security checks. See `template-references/performance-notes.md` for full guidelines.