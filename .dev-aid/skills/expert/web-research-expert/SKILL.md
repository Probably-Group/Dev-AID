---
name: web-research-expert
version: 2.0.0
description: "Web research for finding solutions on GitHub, Stack Overflow, Reddit, and technical forums. Use when searching for technical solutions, debugging with community resources, or finding library comparisons. Do NOT use for deep research (use deep-research-expert)."
risk_level: LOW
token_budget: 3500
---
# Web Research Expert - Code Generation Rules

---

## 1. Security Principles

### 1.1 Source Validation (CWE-20)

**Principle:** Not all web sources are trustworthy. Validate and rank sources by reliability.

```python
# ❌ WRONG - Trusting all search results equally
def search(query: str) -> list[str]:
    results = google_search(query)
    return [r.snippet for r in results]

# ✅ CORRECT - Source validation and ranking
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse

class SourceTier(Enum):
    AUTHORITATIVE = 1  # Official docs, standards bodies
    HIGH = 2           # Academic, well-known tech blogs
    MEDIUM = 3         # Q&A sites with votes, GitHub issues
    LOW = 4            # Forums, personal blogs
    UNTRUSTED = 5      # Unknown sources

@dataclass
class SourceConfig:
    authoritative_domains: set[str]
    high_tier_domains: set[str]
    blocked_domains: set[str]

DEFAULT_CONFIG = SourceConfig(
    authoritative_domains={
        "docs.python.org", "developer.mozilla.org", "rust-lang.org",
        "docs.rs", "pkg.go.dev", "typescriptlang.org",
        "kubernetes.io", "tailwindcss.com", "vuejs.org",
    },
    high_tier_domains={
        "github.com", "stackoverflow.com", "arxiv.org",
        "martinfowler.com", "blog.cloudflare.com",
    },
    blocked_domains={
        "w3schools.com",  # Often outdated
        "geeksforgeeks.org",  # Quality varies significantly
    },
)

def get_source_tier(url: str, config: SourceConfig = DEFAULT_CONFIG) -> SourceTier:
    """Determine trustworthiness of a source."""
    domain = urlparse(url).netloc.lower()

    if domain in config.blocked_domains:
        return SourceTier.UNTRUSTED

    if domain in config.authoritative_domains:
        return SourceTier.AUTHORITATIVE

    if domain in config.high_tier_domains:
        return SourceTier.HIGH

    # GitHub repos from known orgs
    if domain == "github.com" and any(
        url.startswith(f"https://github.com/{org}/")
        for org in ["microsoft", "google", "facebook", "vercel"]
    ):
        return SourceTier.HIGH

    # Stack Overflow with high votes
    if "stackoverflow.com" in domain:
        return SourceTier.MEDIUM

    return SourceTier.LOW
```

### 1.2 Information Verification (CWE-345)

**Principle:** Cross-reference information from multiple sources. Don't trust single sources.

```python
# ❌ WRONG - Using first result as truth
def get_answer(query: str) -> str:
    results = search(query)
    return results[0].content

# ✅ CORRECT - Cross-reference multiple sources
from dataclasses import dataclass
from collections import Counter

@dataclass
class ResearchFinding:
    claim: str
    sources: list[str]
    confidence: float  # 0-1
    contradictions: list[str]

def verify_information(
    query: str,
    min_sources: int = 2,
    min_agreement: float = 0.6,
) -> ResearchFinding:
    """Verify information across multiple sources."""
    results = search_multiple_engines(query)

    # Group by extracted answer/claim
    claims = extract_claims(results)
    claim_sources = group_by_claim(claims)

    # Find most agreed-upon claim
    most_common = Counter(c.normalized for c in claims).most_common()

    if not most_common:
        return ResearchFinding(
            claim="No information found",
            sources=[],
            confidence=0.0,
            contradictions=[],
        )

    top_claim = most_common[0][0]
    supporting = claim_sources[top_claim]
    contradicting = [c for c in claims if c.normalized != top_claim]

    agreement_ratio = len(supporting) / len(claims)

    return ResearchFinding(
        claim=top_claim,
        sources=[s.url for s in supporting],
        confidence=agreement_ratio if len(supporting) >= min_sources else 0.0,
        contradictions=[c.text for c in contradicting[:3]],
    )
```

### 1.3 Date Awareness (CWE-1295)

**Principle:** Technical information has a shelf life. Check publication dates.

```python
# ❌ WRONG - Ignoring content freshness
def search_docs(query: str) -> list[Result]:
    return search(query)

# ✅ CORRECT - Filter by recency for technical topics
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class FreshnessConfig:
    max_age_days: int
    require_date: bool = False
    prefer_recent: bool = True

# Technology-specific freshness requirements
FRESHNESS_REQUIREMENTS = {
    "react": FreshnessConfig(max_age_days=365),
    "vue": FreshnessConfig(max_age_days=365),
    "kubernetes": FreshnessConfig(max_age_days=365),
    "python": FreshnessConfig(max_age_days=730),  # More stable
    "algorithms": FreshnessConfig(max_age_days=3650, require_date=False),  # Timeless
}

def filter_by_freshness(
    results: list[SearchResult],
    topic: str,
) -> list[SearchResult]:
    """Filter results by publication date."""
    config = FRESHNESS_REQUIREMENTS.get(
        topic.lower(),
        FreshnessConfig(max_age_days=730)  # Default 2 years
    )

    cutoff = datetime.now() - timedelta(days=config.max_age_days)
    filtered = []

    for result in results:
        if result.published_date:
            if result.published_date >= cutoff:
                filtered.append(result)
        elif not config.require_date:
            # Include undated if not required
            filtered.append(result)

    # Sort by recency if preferred
    if config.prefer_recent:
        filtered.sort(
            key=lambda r: r.published_date or datetime.min,
            reverse=True
        )

    return filtered
```

---

## 2. Version Requirements

```
# Search APIs
tavily-python>=0.3.0
duckduckgo-search>=4.0.0
# Web scraping (when needed)
httpx>=0.25.0
beautifulsoup4>=4.12.0
# NLP for extraction
spacy>=3.7.0
```

---

## 3. Code Patterns

### WHEN performing technical research, use structured queries

```python
# ❌ WRONG - Vague queries
results = search("how to fix error")

# ✅ CORRECT - Structured technical queries
from dataclasses import dataclass
from typing import Literal

@dataclass
class TechnicalQuery:
    technology: str
    version: str | None
    problem_type: Literal["error", "how-to", "best-practice", "comparison"]
    keywords: list[str]
    exclude: list[str] = None

def build_search_query(query: TechnicalQuery) -> str:
    """Build optimized search query for technical research."""
    parts = []

    # Technology with optional version
    if query.version:
        parts.append(f'"{query.technology} {query.version}"')
    else:
        parts.append(f'"{query.technology}"')

    # Problem-specific terms
    if query.problem_type == "error":
        parts.extend(["error", "fix", "solution"])
    elif query.problem_type == "how-to":
        parts.extend(["tutorial", "guide", "example"])
    elif query.problem_type == "best-practice":
        parts.extend(["best practice", "recommended", "production"])
    elif query.problem_type == "comparison":
        parts.extend(["vs", "comparison", "alternative"])

    # Keywords
    parts.extend(query.keywords)

    # Exclusions
    if query.exclude:
        parts.extend([f"-{term}" for term in query.exclude])

    return " ".join(parts)

# Example usage
query = TechnicalQuery(
    technology="Vue",
    version="3",
    problem_type="how-to",
    keywords=["composables", "typescript"],
    exclude=["Vue 2", "options API"],
)
search_string = build_search_query(query)
# "Vue 3" tutorial guide example composables typescript -"Vue 2" -"options API"
```

### WHEN aggregating GitHub issues, extract actionable information

```python
# ❌ WRONG - Just returning issue titles
def search_issues(repo: str, query: str) -> list[str]:
    issues = github.search_issues(f"repo:{repo} {query}")
    return [i.title for i in issues]

# ✅ CORRECT - Extract actionable information
from dataclasses import dataclass
from typing import Literal
import re

@dataclass
class IssueInsight:
    title: str
    url: str
    status: Literal["open", "closed"]
    has_solution: bool
    solution_summary: str | None
    related_prs: list[str]
    workarounds: list[str]
    affected_versions: list[str]

def analyze_github_issue(issue: GithubIssue) -> IssueInsight:
    """Extract actionable information from GitHub issue."""
    comments = issue.get_comments()

    # Look for solutions in comments
    solution = None
    workarounds = []

    for comment in comments:
        # Check for maintainer responses
        if comment.author_association in ["OWNER", "MEMBER", "COLLABORATOR"]:
            if any(word in comment.body.lower() for word in ["fixed", "solved", "released"]):
                solution = extract_solution(comment.body)

        # Check for workarounds
        if "workaround" in comment.body.lower():
            workarounds.append(extract_workaround(comment.body))

    # Find linked PRs
    related_prs = [
        event.source.url
        for event in issue.get_events()
        if event.event == "cross-referenced" and "pull" in event.source.url
    ]

    # Extract affected versions
    versions = re.findall(r'v?\d+\.\d+(?:\.\d+)?', issue.body or '')

    return IssueInsight(
        title=issue.title,
        url=issue.html_url,
        status="closed" if issue.closed_at else "open",
        has_solution=solution is not None,
        solution_summary=solution,
        related_prs=related_prs,
        workarounds=workarounds,
        affected_versions=versions,
    )
```

### WHEN researching errors, search for stack traces

```python
# ❌ WRONG - Searching full error message
def search_error(error_message: str):
    return search(error_message)  # Too specific, few results

# ✅ CORRECT - Extract and normalize error patterns
import re
from dataclasses import dataclass

@dataclass
class ErrorPattern:
    error_type: str
    message_template: str
    file_info: str | None
    searchable_query: str

def extract_error_pattern(error: str) -> ErrorPattern:
    """Extract searchable pattern from error message."""

    # Extract error type (Python)
    type_match = re.search(r'^(\w+Error|\w+Exception):', error, re.MULTILINE)
    error_type = type_match.group(1) if type_match else "Error"

    # Remove file paths and line numbers
    normalized = re.sub(r'File "[^"]+", line \d+', '', error)
    normalized = re.sub(r'at .+:\d+:\d+', '', normalized)  # JS stack traces

    # Remove variable values (keep structure)
    normalized = re.sub(r"'[^']{20,}'", "'...'", normalized)
    normalized = re.sub(r'"[^"]{20,}"', '"..."', normalized)

    # Extract core message
    lines = [l.strip() for l in normalized.split('\n') if l.strip()]
    core_message = lines[0] if lines else error[:100]

    # Build searchable query
    query_parts = [f'"{error_type}"']
    # Extract key phrases
    key_phrases = re.findall(r"(?:cannot|could not|failed to|unable to|no such) \w+", error.lower())
    query_parts.extend([f'"{p}"' for p in key_phrases[:2]])

    return ErrorPattern(
        error_type=error_type,
        message_template=core_message,
        file_info=None,
        searchable_query=" ".join(query_parts),
    )
```

### WHEN documenting research, track provenance

```python
# ❌ WRONG - Notes without sources
def research_topic(topic: str) -> str:
    return "The best practice is to use X because Y"

# ✅ CORRECT - Full provenance tracking
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

@dataclass
class Citation:
    url: str
    title: str
    author: str | None
    published_date: datetime | None
    accessed_date: datetime
    quote: str | None = None

@dataclass
class ResearchNote:
    topic: str
    summary: str
    confidence: Literal["high", "medium", "low"]
    citations: list[Citation]
    methodology: str
    caveats: list[str] = field(default_factory=list)
    last_verified: datetime = field(default_factory=datetime.now)

def create_research_note(
    topic: str,
    findings: list[SearchResult],
    analysis: str,
) -> ResearchNote:
    """Create research note with full provenance."""
    citations = [
        Citation(
            url=f.url,
            title=f.title,
            author=f.author,
            published_date=f.published_date,
            accessed_date=datetime.now(),
            quote=f.relevant_quote,
        )
        for f in findings
        if f.tier in [SourceTier.AUTHORITATIVE, SourceTier.HIGH]
    ]

    # Determine confidence based on source quality
    authoritative_count = sum(1 for c in citations if is_authoritative(c.url))
    confidence = (
        "high" if authoritative_count >= 2 else
        "medium" if len(citations) >= 3 else
        "low"
    )

    return ResearchNote(
        topic=topic,
        summary=analysis,
        confidence=confidence,
        citations=citations,
        methodology=f"Searched {len(findings)} sources, verified across {len(citations)} high-quality references",
        caveats=["Information may be outdated", "Test in your specific environment"],
    )
```

---

## 4. Anti-Patterns

Do not:
- Trust a single source for technical information
- Use results without checking publication date
- Ignore source credibility when presenting findings
- Search for full error messages (normalize first)
- Present research without citing sources
- Mix authoritative and low-quality sources equally
- Ignore contradicting information

---

## 5. Testing

```python
import pytest
from datetime import datetime, timedelta
from web_research import (
    get_source_tier,
    SourceTier,
    filter_by_freshness,
    extract_error_pattern,
# ... (additional test cases follow same pattern)
```

---

## 6. Pre-Generation Checklist

Before generating research code:

- [ ] Source ranking: Implemented tier system for credibility
- [ ] Cross-reference: Minimum 2 sources for claims
- [ ] Date filtering: Freshness requirements per technology
- [ ] Error normalization: Patterns extracted, not full messages
- [ ] Provenance: All findings cite sources
- [ ] Confidence scoring: Based on source quality and agreement
- [ ] Blocked sources: Known low-quality sites filtered
- [ ] Version awareness: Technology versions tracked

---
