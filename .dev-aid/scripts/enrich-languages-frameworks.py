#!/usr/bin/env python3
"""
Enrich Languages/Frameworks skills with domain-specific security content (§ 0.1, 0.2, 0.3)
Based on current CVE research from 2024-2025
"""

import re
from pathlib import Path
from typing import Dict

# CVE Research Data from WebSearch (2024-2025) - Languages/Frameworks Domain
VULNERABILITY_DATA = {
    'python': {
        'risk_level': 'HIGH',
        'top_cves': [
            {
                'id': 'CVE-2024-12254',
                'cvss': '7.5',
                'description': 'Python asyncio module memory exhaustion vulnerability',
                'source': 'https://linuxsecurity.com/news/security-vulnerabilities/new-python-memory-exhaustion-bug'
            },
            {
                'id': 'CVE-2024-12718',
                'cvss': '9.8',
                'description': 'Critical tarfile module vulnerability allowing RCE',
                'source': 'https://www.sweet.security/blog/python-tar-file-vulnerability-cve-2024-12718-what-you-need-to-know'
            },
            {
                'id': 'CVE-2025-27607',
                'cvss': '9.8',
                'description': 'RCE affecting 43 million Python installations via msgspec-python313-pre',
                'source': 'https://gbhackers.com/over-43-million-python-installations-vulnerable/'
            }
        ],
        'attack_patterns': [
            'Memory exhaustion via asyncio.writelines()',
            'Tarfile extraction path traversal',
            'Supply chain attacks via missing dependencies',
            'Zipfile infinite loop DoS',
            'Deserialization attacks in pickle/msgspec'
        ],
        'hallucination_rules': [
            'NEVER use pickle for untrusted data deserialization',
            'NEVER extract archives without path validation',
            'NEVER ignore dependency security warnings',
            'ALWAYS validate tarfile filter parameters',
            'ALWAYS use virtual environments with pinned dependencies'
        ]
    },

    'rust': {
        'risk_level': 'MEDIUM',
        'top_cves': [
            {
                'id': 'CVE-2024-24576',
                'cvss': '10.0',
                'description': 'BatBadBut - Windows command injection via improper argument escaping',
                'source': 'https://blog.rust-lang.org/2024/04/09/cve-2024-24576.html'
            },
            {
                'id': 'CVE-2025-62518',
                'cvss': '8.1',
                'description': 'TARmageddon - async-tar library RCE via file overwriting',
                'source': 'https://www.csoonline.com/article/4077445/serious-vulnerability-found-in-rust-library.html'
            },
            {
                'id': 'CVE-2024-43402',
                'cvss': '7.5',
                'description': 'Standard library vulnerability in batch file handling',
                'source': 'https://blog.rust-lang.org/2024/09/04/cve-2024-43402.html'
            }
        ],
        'attack_patterns': [
            'Command injection via std::process::Command on Windows',
            'TAR archive path traversal attacks',
            'Logic bugs in unsafe code blocks',
            'Supply chain attacks via crates.io'
        ],
        'hallucination_rules': [
            'NEVER use std::process::Command with untrusted input on Windows without validation',
            'NEVER extract TAR archives without path sanitization',
            'NEVER assume Rust prevents all security vulnerabilities',
            'ALWAYS validate external command arguments',
            'ALWAYS audit unsafe blocks for logic errors'
        ]
    },

    'javascript-expert': {
        'risk_level': 'HIGH',
        'top_cves': [
            {
                'id': 'CVE-2025-55182',
                'cvss': '10.0',
                'description': 'React Server Components RCE via payload decoding flaw',
                'source': 'https://thehackernews.com/2025/12/critical-rsc-bugs-in-react-and-nextjs.html'
            },
            {
                'id': 'CVE-2025-66478',
                'cvss': '10.0',
                'description': 'Next.js RCE affecting default configurations',
                'source': 'https://www.endorlabs.com/learn/critical-remote-code-execution-rce-vulnerabilities-in-react-and-next-js'
            },
            {
                'id': 'CVE-2025-12735',
                'cvss': '9.8',
                'description': 'expr-eval library RCE via malicious input (800k weekly downloads)',
                'source': 'https://www.bleepingcomputer.com/news/security/popular-javascript-library-expr-eval-vulnerable-to-rce-flaw/'
            }
        ],
        'attack_patterns': [
            'React Server Component payload manipulation',
            'Prototype pollution attacks',
            'Expression evaluation RCE',
            'NPM supply chain attacks (2.6B downloads compromised Sept 2025)',
            'Client-side XSS via framework bypasses'
        ],
        'hallucination_rules': [
            'NEVER trust client-side validation alone',
            'NEVER use eval() or Function() with user input',
            'NEVER install NPM packages without integrity checks',
            'ALWAYS sanitize React dangerouslySetInnerHTML',
            'ALWAYS validate Server Component payloads'
        ]
    },

    'typescript-expert': {
        'risk_level': 'MEDIUM',
        'top_cves': [
            {
                'id': 'CVE-2025-55182',
                'cvss': '10.0',
                'description': 'React/Next.js RCE affecting TypeScript projects',
                'source': 'https://thehackernews.com/2025/12/critical-rsc-bugs-in-react-and-nextjs.html'
            },
            {
                'id': 'NPM-SUPPLY-CHAIN-2025',
                'cvss': 'N/A',
                'description': '18 popular NPM packages compromised (chalk, debug, ansi-styles)',
                'source': 'https://blog.qualys.com/vulnerabilities-threat-research/2025/09/10/when-dependencies-turn-dangerous-responding-to-the-npm-supply-chain-attack'
            },
            {
                'id': 'CVE-2023-6293',
                'cvss': '7.5',
                'description': 'Prototype pollution in sequelize-typescript',
                'source': 'https://security.snyk.io/vuln/SNYK-JS-SEQUELIZETYPESCRIPT-6085300'
            }
        ],
        'attack_patterns': [
            'Type confusion vulnerabilities',
            'Prototype pollution via Object.assign',
            'NPM dependency confusion attacks',
            'TypeScript compiler bypass techniques'
        ],
        'hallucination_rules': [
            'NEVER trust type assertions for runtime security',
            'NEVER use "any" type for security-critical code',
            'NEVER assume TypeScript types prevent injection',
            'ALWAYS validate runtime data regardless of types',
            'ALWAYS use strict TypeScript configuration'
        ]
    },

    'typescript': {
        'risk_level': 'MEDIUM',
        'top_cves': [
            {
                'id': 'CVE-2025-55182',
                'cvss': '10.0',
                'description': 'React/Next.js RCE affecting TypeScript projects',
                'source': 'https://thehackernews.com/2025/12/critical-rsc-bugs-in-react-and-nextjs.html'
            },
            {
                'id': 'NPM-SUPPLY-CHAIN-2025',
                'cvss': 'N/A',
                'description': '18 popular NPM packages compromised',
                'source': 'https://blog.qualys.com/vulnerabilities-threat-research/2025/09/10/when-dependencies-turn-dangerous-responding-to-the-npm-supply-chain-attack'
            },
            {
                'id': 'CVE-2023-6293',
                'cvss': '7.5',
                'description': 'Prototype pollution in sequelize-typescript',
                'source': 'https://security.snyk.io/vuln/SNYK-JS-SEQUELIZETYPESCRIPT-6085300'
            }
        ],
        'attack_patterns': [
            'Type confusion vulnerabilities',
            'Prototype pollution',
            'NPM supply chain attacks',
            'TypeScript type system bypass'
        ],
        'hallucination_rules': [
            'NEVER rely on TypeScript types for security',
            'NEVER use "any" for untrusted data',
            'NEVER skip runtime validation',
            'ALWAYS validate external inputs',
            'ALWAYS use strict mode'
        ]
    },

    'bash-expert': {
        'risk_level': 'HIGH',
        'top_cves': [
            {
                'id': 'CVE-2014-6271',
                'cvss': '10.0',
                'description': 'Shellshock - Command injection via environment variables (still exploited in 2024)',
                'source': 'https://blog.barracuda.com/2024/03/06/threat-spotlight-shellshock-bugs-miners'
            },
            {
                'id': 'CVE-2014-7169',
                'cvss': '10.0',
                'description': 'Shellshock variant - Incomplete fix bypass',
                'source': 'https://access.redhat.com/articles/1200223'
            },
            {
                'id': 'COMMAND-INJECTION-2024',
                'cvss': 'N/A',
                'description': 'Command injection remains top web app vulnerability in 2024',
                'source': 'https://www.aikido.dev/blog/command-injection-in-2024-unpacked'
            }
        ],
        'attack_patterns': [
            'Shellshock environment variable injection',
            'Command injection via unsanitized input',
            'Path traversal in file operations',
            'Privilege escalation via SUID scripts',
            'Race conditions in temporary file creation'
        ],
        'hallucination_rules': [
            'NEVER execute user input without validation',
            'NEVER use eval or source with untrusted data',
            'NEVER construct commands via string concatenation',
            'ALWAYS quote variables to prevent word splitting',
            'ALWAYS use array syntax for command arguments'
        ]
    },

    'async-expert': {
        'risk_level': 'MEDIUM',
        'top_cves': [
            {
                'id': 'CVE-2024-6387',
                'cvss': '8.1',
                'description': 'OpenSSH race condition in signal handling leading to RCE',
                'source': 'https://medium.com/@yanivx32/the-chase-for-time-race-condition-vulnerabilities-and-how-to-exploit-them-a-live-example-from-c1cc66086617'
            },
            {
                'id': 'CVE-2024-58248',
                'cvss': '7.5',
                'description': 'nopCommerce race condition in order placement',
                'source': 'https://medium.com/pythoneers/avoiding-race-conditions-in-python-in-2025-best-practices-for-async-and-threads-4e006579a622'
            },
            {
                'id': 'ASYNCIO-DEADLOCK-2025',
                'cvss': 'N/A',
                'description': 'Python asyncio cancellation deadlocks with TaskGroup',
                'source': 'https://x.com/mitsuhiko/status/1920384040005173320'
            }
        ],
        'attack_patterns': [
            'Race conditions in async signal handlers',
            'TOCTOU (Time-of-check-time-of-use) attacks',
            'Deadlocks via improper lock ordering',
            'Resource exhaustion via async task spawning',
            'State corruption in concurrent operations'
        ],
        'hallucination_rules': [
            'NEVER assume async operations are atomic',
            'NEVER use shared state without synchronization',
            'NEVER cancel tasks without proper cleanup',
            'ALWAYS use proper locking for shared resources',
            'ALWAYS implement timeout mechanisms'
        ]
    },

    'async-programming': {
        'risk_level': 'MEDIUM',
        'top_cves': [
            {
                'id': 'CVE-2024-6387',
                'cvss': '8.1',
                'description': 'Race condition in async signal handling',
                'source': 'https://medium.com/@yanivx32/the-chase-for-time-race-condition-vulnerabilities-and-how-to-exploit-them-a-live-example-from-c1cc66086617'
            },
            {
                'id': 'CVE-2024-58248',
                'cvss': '7.5',
                'description': 'Race condition in async order processing',
                'source': 'https://medium.com/pythoneers/avoiding-race-conditions-in-python-in-2025-best-practices-for-async-and-threads-4e006579a622'
            },
            {
                'id': 'RACE-CONDITION-GENERAL',
                'cvss': 'N/A',
                'description': 'Race conditions in distributed systems and async frameworks',
                'source': 'https://www.yeswehack.com/learn-bug-bounty/ultimate-guide-race-condition-vulnerabilities'
            }
        ],
        'attack_patterns': [
            'TOCTOU race conditions',
            'Concurrent state manipulation',
            'Deadlock-based DoS',
            'Async resource exhaustion'
        ],
        'hallucination_rules': [
            'NEVER assume async operations are thread-safe',
            'NEVER share mutable state without locks',
            'NEVER ignore cancellation signals',
            'ALWAYS use atomic operations for counters',
            'ALWAYS implement proper error handling in async code'
        ]
    },
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

    # Check if already enriched
    if '### 0.1 Quick Risk Assessment' in content:
        print(f"✅ {skill_name}: Already enriched, skipping...")
        return False

    # Build new sections
    section_0_1 = create_section_0_1(skill_data)
    section_0_2 = create_section_0_2(skill_data)
    section_0_3 = create_section_0_3(skill_data)

    # Case A: Skills that already have "## 0. Anti-Hallucination Protocol"
    section_0_match = re.search(r'^## 0\. Anti-Hallucination Protocol.*?\n', content, re.MULTILINE)
    if section_0_match:
        # Insert after ## 0. Anti-Hallucination Protocol
        insertion_point = section_0_match.end()

        new_content = (
            content[:insertion_point] +
            "\n" + section_0_1 + "\n" +
            (section_0_2 + "\n" if section_0_2 else "") +
            section_0_3 + "\n" +
            content[insertion_point:]
        )
    else:
        # Case B: Skills missing the entire ## 0 section - add before ## 1
        section_1_match = re.search(r'^## 1\. ', content, re.MULTILINE)
        if not section_1_match:
            print(f"❌ {skill_name}: Could not find insertion point")
            return False

        insertion_point = section_1_match.start()

        section_0_complete = (
            "## 0. Anti-Hallucination Protocol\n\n" +
            section_0_1 + "\n" +
            (section_0_2 + "\n" if section_0_2 else "") +
            section_0_3 + "\n\n"
        )

        new_content = content[:insertion_point] + section_0_complete + content[insertion_point:]

    # Write back
    with open(skill_path, 'w') as f:
        f.write(new_content)

    return True


def main():
    skills_dir = Path('.dev-aid/skills/expert')

    print("=" * 70)
    print("LANGUAGES/FRAMEWORKS DOMAIN ENRICHMENT")
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
    print(f"   - Skipped: {skipped_count} skills")
    print("=" * 70)


if __name__ == "__main__":
    main()
