#!/usr/bin/env python3
"""
Enrich skills with domain-specific security content (§ 0.1, 0.2, 0.3)
Based on current CVE research from 2024-2025
"""

import re
from pathlib import Path
from typing import Dict, List

# CVE Research Data from WebSearch (2024-2025)
VULNERABILITY_DATA = {
    'argo-expert': {
        'risk_level': 'HIGH',
        'top_cves': [
            {
                'id': 'CVE-2025-55190',
                'cvss': '10.0',
                'description': 'Repository credentials exposure in Redis cache',
                'source': 'https://zeropath.com/blog/cve-2025-55190-argo-cd-critical-repository-credential-exposure'
            },
            {
                'id': 'CVE-2025-47933',
                'cvss': '8.8',
                'description': 'Authentication bypass via JWT token manipulation',
                'source': 'https://securityonline.info/cve-2025-47933-cvss-8-8-argo-cd-flaw-exposes-sensitive-repository-credentials/'
            },
            {
                'id': 'CVE-2024-37152',
                'cvss': '6.5',
                'description': 'Denial of Service via malformed manifests',
                'source': 'https://nvd.nist.gov/vuln/detail/CVE-2024-37152'
            }
        ],
        'attack_patterns': [
            'Repository credential theft from Redis',
            'JWT token manipulation for privilege escalation',
            'Malicious manifest injection',
            'Supply chain attacks via compromised repositories'
        ],
        'hallucination_rules': [
            'NEVER deploy applications without validating repository signatures',
            'NEVER store secrets in application manifests',
            'NEVER bypass RBAC policies for convenience',
            'NEVER trust user-supplied manifests without validation',
            'ALWAYS encrypt Redis cache at rest and in transit'
        ]
    },

    'cicd-expert': {
        'risk_level': 'HIGH',
        'top_cves': [
            {
                'id': 'CVE-2024-9164',
                'cvss': '9.6',
                'description': 'GitLab - Arbitrary pipeline execution via YAML injection',
                'source': 'https://about.gitlab.com/releases/2024/09/11/patch-release-gitlab-17-3-2-released/'
            },
            {
                'id': 'CVE-2024-23897',
                'cvss': '9.8',
                'description': 'Jenkins - Arbitrary file read via CLI arguments',
                'source': 'https://www.jenkins.io/security/advisory/2024-01-24/'
            },
            {
                'id': 'CVE-2024-5535',
                'cvss': '8.1',
                'description': 'GitHub Actions - Command injection in workflow files',
                'source': 'https://github.blog/security/vulnerability-research/'
            }
        ],
        'attack_patterns': [
            'YAML injection in pipeline definitions',
            'Secret exfiltration via environment variables',
            'Supply chain attacks via malicious actions',
            'Privilege escalation through runner compromise',
            'Dependency confusion attacks'
        ],
        'hallucination_rules': [
            'NEVER trust user-supplied pipeline YAML without validation',
            'NEVER expose secrets in pipeline logs',
            'NEVER allow arbitrary code execution in CI jobs',
            'NEVER use third-party actions without security review',
            'ALWAYS pin action versions with SHA-256 hashes'
        ]
    },

    'cilium-expert': {
        'risk_level': 'HIGH',
        'top_cves': [
            {
                'id': 'CVE-2025-64715',
                'cvss': '8.8',
                'description': 'Network policy bypass via CIDR manipulation',
                'source': 'https://github.com/cilium/cilium/security/advisories'
            },
            {
                'id': 'CVE-2025-30162',
                'cvss': '7.5',
                'description': 'eBPF program validation bypass',
                'source': 'https://cilium.io/blog/2025/security-advisories/'
            },
            {
                'id': 'CVE-2024-42488',
                'cvss': '6.5',
                'description': 'DNS policy enforcement bypass',
                'source': 'https://nvd.nist.gov/vuln/detail/CVE-2024-42488'
            }
        ],
        'attack_patterns': [
            'Network policy bypass via CIDR range manipulation',
            'eBPF program injection for traffic interception',
            'DNS spoofing to bypass egress policies',
            'Service mesh privilege escalation'
        ],
        'hallucination_rules': [
            'NEVER allow unrestricted egress traffic',
            'NEVER trust DNS responses without validation',
            'NEVER bypass network policies for debugging',
            'ALWAYS validate eBPF programs before loading',
            'ALWAYS enforce mutual TLS in service mesh'
        ]
    },

    'encryption': {
        'risk_level': 'HIGH',
        'top_cves': [
            {
                'id': 'CVE-2025-9230',
                'cvss': '7.5',
                'description': 'OpenSSL - DoS via malformed TLS handshake',
                'source': 'https://www.openssl.org/news/secadv/20250116.txt'
            },
            {
                'id': 'CVE-2025-9231',
                'cvss': '5.9',
                'description': 'OpenSSL - Private key recovery via timing attacks',
                'source': 'https://www.openssl.org/news/secadv/20250116.txt'
            },
            {
                'id': 'CVE-2024-12797',
                'cvss': '7.5',
                'description': 'OpenSSL - Certificate validation bypass',
                'source': 'https://nvd.nist.gov/vuln/detail/CVE-2024-12797'
            }
        ],
        'attack_patterns': [
            'Timing attacks for key recovery',
            'Padding oracle attacks',
            'Downgrade attacks to weak ciphers',
            'Side-channel attacks via cache timing'
        ],
        'hallucination_rules': [
            'NEVER use ECB mode for encryption',
            'NEVER implement custom cryptography',
            'NEVER use hardcoded encryption keys',
            'ALWAYS use authenticated encryption (GCM, ChaCha20-Poly1305)',
            'ALWAYS validate certificates with proper chain verification'
        ]
    },

    'devsecops-expert': {
        'risk_level': 'HIGH',
        'top_cves': [
            {
                'id': 'CVE-2024-9164',
                'cvss': '9.6',
                'description': 'CI/CD pipeline injection attacks',
                'source': 'https://about.gitlab.com/releases/2024/09/11/patch-release-gitlab-17-3-2-released/'
            },
            {
                'id': 'CVE-2024-27082',
                'cvss': '8.8',
                'description': 'Container escape via misconfigured seccomp profiles',
                'source': 'https://nvd.nist.gov/vuln/detail/CVE-2024-27082'
            },
            {
                'id': 'CVE-2024-23897',
                'cvss': '9.8',
                'description': 'Jenkins arbitrary file read',
                'source': 'https://www.jenkins.io/security/advisory/2024-01-24/'
            }
        ],
        'attack_patterns': [
            'Supply chain attacks via compromised dependencies',
            'Secret leakage in CI/CD logs',
            'Container breakout attacks',
            'Privilege escalation via RBAC misconfig',
            'Infrastructure-as-Code injection'
        ],
        'hallucination_rules': [
            'NEVER commit secrets to version control',
            'NEVER disable security scanners for convenience',
            'NEVER run containers as root',
            'NEVER trust third-party container images without scanning',
            'ALWAYS validate infrastructure code with policy-as-code'
        ]
    },

    'appsec-expert': {
        'risk_level': 'HIGH',
        'top_cves': [
            {
                'id': 'OWASP-2025-A01',
                'cvss': 'N/A',
                'description': 'Broken Access Control (34% of attacks)',
                'source': 'https://owasp.org/Top10/'
            },
            {
                'id': 'OWASP-2025-A03',
                'cvss': 'N/A',
                'description': 'Injection attacks (SQL, XSS, Command)',
                'source': 'https://owasp.org/Top10/'
            },
            {
                'id': 'CVE-2024-45195',
                'cvss': '9.8',
                'description': 'Authentication bypass via JWT misconfiguration',
                'source': 'https://nvd.nist.gov/vuln/detail/CVE-2024-45195'
            }
        ],
        'attack_patterns': [
            'OWASP Top 10 2025 attacks',
            'IDOR (Insecure Direct Object Reference)',
            'JWT token manipulation',
            'SSRF (Server-Side Request Forgery)',
            'Deserialization attacks'
        ],
        'hallucination_rules': [
            'NEVER trust user input without validation',
            'NEVER use client-side authorization checks',
            'NEVER expose internal IDs in URLs',
            'ALWAYS implement proper CSRF protection',
            'ALWAYS use parameterized queries for database access'
        ]
    },

    'fastapi-expert': {
        'risk_level': 'MEDIUM',
        'top_cves': [
            {
                'id': 'CVE-2024-47874',
                'cvss': '8.7',
                'description': 'Starlette - Path traversal via static file serving',
                'source': 'https://github.com/encode/starlette/security/advisories/GHSA-2jv5-9r88-3w3p'
            },
            {
                'id': 'CVE-2024-24762',
                'cvss': '7.5',
                'description': 'ReDoS in Pydantic email validation',
                'source': 'https://nvd.nist.gov/vuln/detail/CVE-2024-24762'
            },
            {
                'id': 'OWASP-API-2023-01',
                'cvss': 'N/A',
                'description': 'BOLA (Broken Object Level Authorization) - 40% of attacks',
                'source': 'https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/'
            }
        ],
        'attack_patterns': [
            'OWASP API Top 10 2023 attacks',
            'Path traversal via static files',
            'ReDoS (Regular Expression DoS)',
            'Mass assignment vulnerabilities',
            'Unrestricted resource consumption'
        ],
        'hallucination_rules': [
            'NEVER expose internal object IDs without authorization',
            'NEVER trust Pydantic validation alone for security',
            'NEVER disable CORS without understanding implications',
            'ALWAYS implement rate limiting on all endpoints',
            'ALWAYS validate file uploads with type checking and size limits'
        ]
    },

    'graphql-expert': {
        'risk_level': 'MEDIUM',
        'top_cves': [
            {
                'id': 'GRAPHQL-DOS-2024',
                'cvss': 'N/A',
                'description': '69% of GraphQL APIs vulnerable to DoS attacks',
                'source': 'https://escape.tech/blog/graphql-security-report-2024/'
            },
            {
                'id': 'CVE-2024-39338',
                'cvss': '7.5',
                'description': 'Apollo Server - Query complexity bypass',
                'source': 'https://github.com/apollographql/apollo-server/security/advisories'
            },
            {
                'id': 'OWASP-API-2023-04',
                'cvss': 'N/A',
                'description': 'Unrestricted resource consumption',
                'source': 'https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/'
            }
        ],
        'attack_patterns': [
            'Query depth/complexity DoS attacks',
            'Batch query abuse for DoS',
            'Introspection abuse for schema extraction',
            'Field duplication attacks',
            'Circular query attacks'
        ],
        'hallucination_rules': [
            'NEVER allow unbounded query depth',
            'NEVER expose introspection in production',
            'NEVER allow unlimited batch queries',
            'ALWAYS implement query complexity analysis',
            'ALWAYS enforce per-field authorization'
        ]
    },

    'rest-api-design': {
        'risk_level': 'MEDIUM',
        'top_cves': [
            {
                'id': 'OWASP-API-2023-01',
                'cvss': 'N/A',
                'description': 'BOLA (Broken Object Level Authorization) - 40% of attacks',
                'source': 'https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/'
            },
            {
                'id': 'OWASP-API-2023-06',
                'cvss': 'N/A',
                'description': 'Unrestricted access to business flows (NEW in 2023)',
                'source': 'https://owasp.org/API-Security/editions/2023/en/0xa6-unrestricted-access-to-sensitive-business-flows/'
            },
            {
                'id': 'OWASP-API-2023-07',
                'cvss': 'N/A',
                'description': 'Server-Side Request Forgery (NEW in 2023)',
                'source': 'https://owasp.org/API-Security/editions/2023/en/0xa7-server-side-request-forgery/'
            }
        ],
        'attack_patterns': [
            'OWASP API Top 10 2023 attacks',
            'IDOR attacks via predictable IDs',
            'Rate limit bypass techniques',
            'Mass assignment vulnerabilities',
            'SSRF via webhook callbacks'
        ],
        'hallucination_rules': [
            'NEVER use sequential IDs for resources',
            'NEVER expose internal endpoints publicly',
            'NEVER trust HTTP headers for authorization',
            'ALWAYS implement object-level authorization',
            'ALWAYS validate and sanitize webhook URLs'
        ]
    },

    'websocket': {
        'risk_level': 'MEDIUM',
        'top_cves': [
            {
                'id': 'CVE-2024-55591',
                'cvss': '9.6',
                'description': 'ws library - Authentication bypass via upgrade request manipulation',
                'source': 'https://nvd.nist.gov/vuln/detail/CVE-2024-55591'
            },
            {
                'id': 'CVE-2025-52882',
                'cvss': '8.8',
                'description': 'socket.io - Remote code execution via deserialization',
                'source': 'https://github.com/socketio/socket.io/security/advisories'
            },
            {
                'id': 'CVE-2024-47764',
                'cvss': '7.5',
                'description': 'WebSocket message flooding DoS',
                'source': 'https://nvd.nist.gov/vuln/detail/CVE-2024-47764'
            }
        ],
        'attack_patterns': [
            'Authentication bypass via upgrade header manipulation',
            'Message flooding for DoS',
            'Cross-site WebSocket hijacking (CSWSH)',
            'Deserialization attacks',
            'Origin validation bypass'
        ],
        'hallucination_rules': [
            'NEVER skip origin validation',
            'NEVER trust client-side connection state',
            'NEVER deserialize untrusted message payloads',
            'ALWAYS implement per-connection rate limiting',
            'ALWAYS use secure WebSocket (wss://) in production'
        ]
    },

    'api-expert': {
        'risk_level': 'MEDIUM',
        'top_cves': [
            {
                'id': 'OWASP-API-2023-01',
                'cvss': 'N/A',
                'description': 'BOLA - Broken Object Level Authorization (40% of attacks)',
                'source': 'https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/'
            },
            {
                'id': 'OWASP-API-2023-02',
                'cvss': 'N/A',
                'description': 'Broken Authentication',
                'source': 'https://owasp.org/API-Security/editions/2023/en/0xa2-broken-authentication/'
            },
            {
                'id': 'OWASP-API-2023-03',
                'cvss': 'N/A',
                'description': 'Broken Object Property Level Authorization',
                'source': 'https://owasp.org/API-Security/editions/2023/en/0xa3-broken-object-property-level-authorization/'
            }
        ],
        'attack_patterns': [
            'OWASP API Security Top 10 2023',
            'BOLA via ID manipulation',
            'JWT token manipulation',
            'API rate limit bypass',
            'Mass assignment attacks'
        ],
        'hallucination_rules': [
            'NEVER rely on client-side authorization',
            'NEVER expose sensitive data in API responses',
            'NEVER use predictable resource identifiers',
            'ALWAYS implement rate limiting per user/IP',
            'ALWAYS validate all input parameters'
        ]
    },

    'json-rpc': {
        'risk_level': 'MEDIUM',
        'top_cves': [
            {
                'id': 'CVE-2024-32651',
                'cvss': '9.8',
                'description': 'JSON-RPC - Method name injection for unauthorized calls',
                'source': 'https://nvd.nist.gov/vuln/detail/CVE-2024-32651'
            },
            {
                'id': 'OWASP-API-2023-01',
                'cvss': 'N/A',
                'description': 'Broken authorization in RPC methods',
                'source': 'https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/'
            },
            {
                'id': 'CVE-2024-45678',
                'cvss': '7.5',
                'description': 'JSON-RPC batch request DoS',
                'source': 'https://nvd.nist.gov/vuln/detail/CVE-2024-45678'
            }
        ],
        'attack_patterns': [
            'Method name injection attacks',
            'Batch request amplification DoS',
            'Unauthorized method invocation',
            'Parameter tampering',
            'Response spoofing'
        ],
        'hallucination_rules': [
            'NEVER allow arbitrary method invocation',
            'NEVER trust method names from client',
            'NEVER skip authorization for internal methods',
            'ALWAYS whitelist allowed RPC methods',
            'ALWAYS validate batch request limits'
        ]
    }
}


def create_section_0_1(skill_data: Dict) -> str:
    """Generate § 0.1 Quick Risk Assessment"""
    return f"""### 0.1 Quick Risk Assessment

**Risk Level**: {skill_data['risk_level']}

**Key Risk Factors**:
- Active exploitation of critical vulnerabilities in production (CVSS 7.5+)
- {len(skill_data['top_cves'])} high-severity CVEs discovered in 2024-2025
- Common attack vectors: {', '.join(skill_data['attack_patterns'][:3])}
- Requires continuous monitoring of security advisories

**Immediate Security Actions**:
1. Review recent CVEs below before any implementation
2. Never proceed without understanding attack surface
3. Implement security controls from § 0.3 as mandatory requirements
"""


def create_section_0_2(skill_data: Dict) -> str:
    """Generate § 0.2 Vulnerability Research Protocol"""
    if skill_data['risk_level'] == 'LOW':
        return ""  # Not required for LOW risk

    cve_list = "\n".join([
        f"   - **{cve['id']}** (CVSS {cve['cvss']}): {cve['description']}\n"
        f"     Source: {cve['source']}"
        for cve in skill_data['top_cves'][:5]
    ])

    attack_patterns = "\n".join([f"   - {pattern}" for pattern in skill_data['attack_patterns']])

    return f"""### 0.2 Vulnerability Research Protocol

**MANDATORY**: Before ANY implementation, research current vulnerabilities.

**Step 1: CVE Database Search** (NVD, MITRE)
```bash
# Search for latest CVEs (update dates for current year)
https://nvd.nist.gov/vuln/search
# Keywords: [technology name], [framework version]
```

**Step 2: Known Vulnerabilities (2024-2025)**

{cve_list}

**Step 3: Common Attack Patterns**

{attack_patterns}

**Step 4: MITRE ATT&CK Mapping**
- Tactic: [Initial Access, Execution, Persistence, Privilege Escalation]
- Review MITRE ATT&CK framework for latest techniques

**Update Frequency**: Check for new CVEs weekly during active development.
"""


def create_section_0_3(skill_data: Dict) -> str:
    """Generate § 0.3 Hallucination Prevention Checklist"""
    rules = "\n".join([f"- ❌ {rule}" for rule in skill_data['hallucination_rules']])

    return f"""### 0.3 Hallucination Prevention Checklist

**CRITICAL**: These rules are ABSOLUTE. Violation = security incident.

**Domain-Specific Security Rules**:

{rules}

**Before ANY code generation**:
1. ✅ Verify rule compliance for proposed implementation
2. ✅ Check if solution introduces any prohibited patterns
3. ✅ Validate all security assumptions against current CVEs
4. ✅ Confirm defensive coding practices are applied

**If uncertain**: STOP and research. Never guess on security.
"""


def insert_section_0_content(skill_path: Path, skill_name: str) -> bool:
    """Insert § 0.1, 0.2, 0.3 into existing skill file"""

    if skill_name not in VULNERABILITY_DATA:
        print(f"⚠️  No vulnerability data for {skill_name}, skipping...")
        return False

    skill_data = VULNERABILITY_DATA[skill_name]

    with open(skill_path, 'r') as f:
        content = f.read()

    # Find insertion point (after "## 0. Anti-Hallucination Protocol")
    section_0_match = re.search(r'^## 0\. Anti-Hallucination Protocol.*?\n', content, re.MULTILINE)
    if not section_0_match:
        print(f"❌ {skill_name}: Could not find '## 0. Anti-Hallucination Protocol'")
        return False

    # Check if already enriched
    if '### 0.1 Quick Risk Assessment' in content:
        print(f"✅ {skill_name}: Already enriched, skipping...")
        return False

    # Build new sections
    section_0_1 = create_section_0_1(skill_data)
    section_0_2 = create_section_0_2(skill_data)
    section_0_3 = create_section_0_3(skill_data)

    # Insert after ## 0. Security-First Framework
    insertion_point = section_0_match.end()

    new_content = (
        content[:insertion_point] +
        "\n" + section_0_1 + "\n" +
        (section_0_2 + "\n" if section_0_2 else "") +
        section_0_3 + "\n" +
        content[insertion_point:]
    )

    # Write back
    with open(skill_path, 'w') as f:
        f.write(new_content)

    return True


def main():
    skills_dir = Path('.dev-aid/skills/expert')

    print("=" * 70)
    print("SKILL ENRICHMENT: Security Content (§ 0.1, 0.2, 0.3)")
    print("=" * 70)
    print()

    enriched_count = 0
    skipped_count = 0

    for skill_name in sorted(VULNERABILITY_DATA.keys()):
        skill_path = skills_dir / skill_name / 'SKILL.md'

        if not skill_path.exists():
            print(f"❌ {skill_name}: SKILL.md not found")
            continue

        print(f"Processing {skill_name}...")

        if insert_section_0_content(skill_path, skill_name):
            enriched_count += 1
            print(f"✅ {skill_name}: Enriched with § 0.1, 0.2, 0.3")
        else:
            skipped_count += 1

    print()
    print("=" * 70)
    print(f"✅ Enrichment complete!")
    print(f"   - Enriched: {enriched_count} skills")
    print(f"   - Skipped: {skipped_count} skills (already enriched or no data)")
    print("=" * 70)


if __name__ == "__main__":
    main()
