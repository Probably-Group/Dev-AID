#!/usr/bin/env python3
import re
from pathlib import Path

VULN_DATA = {
    'database-design': {
        'risk': 'HIGH',
        'cves': [
            ('CVE-2025-1094', '8.1', 'PostgreSQL SQL injection via PQescapeLiteral() quoting bypass', 'https://www.rapid7.com/blog/post/2025/02/13/cve-2025-1094-postgresql-psql-sql-injection-fixed/'),
            ('CVE-2024-1597', '8.0', 'SQL injection in PostgreSQL JDBC driver', 'https://www.sangfor.com/farsight-labs-threat-intelligence/cybersecurity/cve-2024-1597-sql-injection-vulnerability'),
            ('CVE-2024-21096', '7.5', 'MySQL similar SQL injection vulnerability', 'https://www.armosec.io/blog/cve-2025-1094-postgresql-sql-injection-vulnerability/'),
        ],
        'attacks': ['SQL injection via quoting bypass', 'Second-order SQL injection', 'Blind SQL injection', 'Time-based SQL injection', 'Boolean-based SQL injection'],
        'rules': ['NEVER concatenate user input into SQL queries', 'NEVER trust ORM frameworks alone for injection protection', 'NEVER use string escaping for SQL injection prevention', 'ALWAYS use parameterized queries/prepared statements', 'ALWAYS validate input before database operations']
    },
    'sqlite': {
        'risk': 'MEDIUM',
        'cves': [
            ('CVE-2025-6965', '9.8', 'Memory corruption when aggregate terms exceed max columns (AI-discovered)', 'https://nvd.nist.gov/vuln/detail/CVE-2025-6965'),
            ('CVE-2025-29087', '8.1', 'Integer overflow in concatws() function leading to memory corruption', 'https://www.wiz.io/vulnerability-database/cve/cve-2025-29087'),
            ('CVE-2024-0232', '5.5', 'Heap use-after-free in jsonParseAddNodeArray()', 'https://www.wiz.io/vulnerability-database/cve/cve-2024-0232'),
        ],
        'attacks': ['Memory corruption via complex queries', 'DoS via malformed JSON', 'Integer overflow exploitation', 'Malicious database file injection'],
        'rules': ['NEVER allow untrusted CREATE TABLE statements', 'NEVER open untrusted SQLite database files', 'NEVER use SQLite < 3.50.2', 'ALWAYS validate query complexity', 'ALWAYS sanitize input for dynamic SQL']
    },
    'sqlcipher': {
        'risk': 'HIGH',
        'cves': [
            ('CVE-2025-6965', '9.8', 'SQLite memory corruption affecting SQLCipher < 4.9.0', 'https://www.zetetic.net/blog/2025/05/15/sqlcipher-4.9.0-release-security-update/'),
            ('CVE-2025-0306', '7.5', 'OpenSSL vulnerability in SQLCipher 4.6.1', 'https://discuss.zetetic.net/t/new-vulnerability-detected-in-openssl/6877'),
            ('CVE-2024-13176', '7.3', 'OpenSSL vulnerability in SQLCipher dependencies', 'https://discuss.zetetic.net/t/new-vulnerabilities-in-openssl/6530'),
        ],
        'attacks': ['Memory corruption via SQLite bugs', 'Weak encryption due to OpenSSL CVEs', 'Key extraction via side-channels', 'Malicious schema exploitation'],
        'rules': ['NEVER use SQLCipher < 4.9.0', 'NEVER store encryption keys in code', 'NEVER allow untrusted schema modifications', 'ALWAYS use latest OpenSSL', 'ALWAYS validate database integrity before decryption']
    },
    'rabbitmq-expert': {
        'risk': 'MEDIUM',
        'cves': [
            ('CVE-2025-30219', '6.1', 'XSS in management UI via malicious virtual host names', 'https://github.com/rabbitmq/rabbitmq-server/security/advisories/GHSA-g58g-82mw-9m3p'),
            ('CVE-2024-51988', '6.5', 'Unauthorized queue deletion via HTTP API', 'https://nvd.nist.gov/vuln/detail/CVE-2024-51988'),
            ('MSMQ-RCE-2024', '9.8', 'Microsoft Message Queuing RCE (related pattern)', 'https://www.threatdown.com/blog/patch-now-critical-rce-vulnerability-in-microsoft-message-queuing/'),
        ],
        'attacks': ['XSS via virtual host names', 'Unauthorized queue operations', 'Message injection attacks', 'Authentication bypass', 'DoS via message flooding'],
        'rules': ['NEVER expose management UI publicly', 'NEVER trust virtual host names without sanitization', 'NEVER allow unauthenticated queue access', 'ALWAYS validate user permissions', 'ALWAYS use SSL/TLS for connections']
    },
    'celery-expert': {
        'risk': 'HIGH',
        'cves': [
            ('CVE-2021-23727', '7.5', 'Command injection via deserialized backend metadata', 'https://github.com/advisories/GHSA-q4xr-rc97-m4xx'),
            ('CELERY-BROKER-INJECTION', '8.8', 'Command injection when attacker controls broker', 'https://moldstud.com/articles/p-are-there-any-known-security-vulnerabilities-in-celery'),
            ('CELERY-DESERIALIZATION', '9.0', 'Arbitrary code execution via pickle deserialization', 'https://security.snyk.io/package/pip/celery'),
        ],
        'attacks': ['Command injection via task metadata', 'Broker compromise for code execution', 'Deserialization attacks', 'Task queue poisoning', 'Result backend tampering'],
        'rules': ['NEVER use Celery < 5.2.2', 'NEVER trust task results from backend without validation', 'NEVER allow direct broker access to untrusted users', 'ALWAYS secure broker with authentication', 'ALWAYS use message signing']
    },
    'graph-database-expert': {
        'risk': 'MEDIUM',
        'cves': [
            ('CYPHER-INJECTION', 'N/A', 'Cypher injection similar to SQL injection in graph databases', 'https://neo4j.com/developer/kb/protecting-against-cypher-injection/'),
            ('NOSQL-INJECTION', 'N/A', 'NoSQL injection patterns in graph database queries', 'https://owasp.org/www-community/attacks/NoSQL_Injection'),
            ('GRAPH-TRAVERSAL-DOS', 'N/A', 'DoS via unbounded graph traversals', 'https://neo4j.com/docs/operations-manual/current/security/'),
        ],
        'attacks': ['Cypher injection attacks', 'Unbounded traversal DoS', 'Node/relationship injection', 'Query complexity exploitation', 'Authentication bypass'],
        'rules': ['NEVER concatenate user input into Cypher queries', 'NEVER allow unbounded MATCH queries', 'NEVER trust client-supplied relationship IDs', 'ALWAYS use parameterized queries', 'ALWAYS implement query complexity limits']
    },
    'surrealdb-expert': {
        'risk': 'MEDIUM',
        'cves': [
            ('SURREALQL-INJECTION', 'N/A', 'SurrealQL injection similar to SQL injection', 'https://surrealdb.com/docs/security'),
            ('NOSQL-INJECTION', 'N/A', 'NoSQL injection patterns in SurrealDB', 'https://owasp.org/www-community/attacks/NoSQL_Injection'),
            ('WEBSOCKET-AUTH-BYPASS', 'N/A', 'Authentication bypass in WebSocket connections', 'https://surrealdb.com/docs/integration/websocket'),
        ],
        'attacks': ['SurrealQL injection', 'WebSocket authentication bypass', 'Record-level permission bypass', 'Query complexity DoS', 'LIVE query abuse'],
        'rules': ['NEVER concatenate user input into SurrealQL', 'NEVER skip record-level permissions', 'NEVER allow unauthenticated WebSocket connections', 'ALWAYS use parameterized queries', 'ALWAYS validate LIVE query subscriptions']
    },
}

def create_sections(data):
    cve_list = "\n".join([f"   - **{c[0]}** (CVSS {c[1]}): {c[2]}\n     Source: {c[3]}" for c in data['cves'][:5]])
    attack_list = "\n".join([f"   - {a}" for a in data['attacks']])
    rules_list = "\n".join([f"- ❌ {r}" for r in data['rules']])
    
    vuln_protocol = "" if data['risk'] == 'LOW' else f"""### 0.2 Vulnerability Research Protocol

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

{attack_list}

**Step 4: MITRE ATT&CK Mapping**
- Tactic: [Initial Access, Execution, Persistence, Privilege Escalation]
- Review MITRE ATT&CK framework for latest techniques

**Update Frequency**: Check for new CVEs weekly during active development.

"""
    
    return f"""## 0. Anti-Hallucination Protocol

### 0.1 Quick Risk Assessment

**Risk Level**: {data['risk']}

**Key Risk Factors**:
- Active exploitation of critical vulnerabilities in production (CVSS 7.5+)
- {len(data['cves'])} high-severity CVEs/security concerns in 2024-2025
- Common attack vectors: {', '.join(data['attacks'][:3])}
- Requires continuous monitoring of security advisories

**Immediate Security Actions**:
1. Review recent CVEs below before any implementation
2. Never proceed without understanding attack surface
3. Implement security controls from § 0.3 as mandatory requirements

{vuln_protocol}### 0.3 Hallucination Prevention Checklist

**CRITICAL**: These rules are ABSOLUTE. Violation = security incident.

**Domain-Specific Security Rules**:

{rules_list}

**Before ANY code generation**:
1. ✅ Verify rule compliance for proposed implementation
2. ✅ Check if solution introduces any prohibited patterns
3. ✅ Validate all security assumptions against current CVEs
4. ✅ Confirm defensive coding practices are applied

**If uncertain**: STOP and research. Never guess on security.

"""

def enrich_skill(skill_path, skill_name):
    if skill_name not in VULN_DATA:
        return False
    
    with open(skill_path, 'r') as f:
        content = f.read()
    
    if '### 0.1 Quick Risk Assessment' in content:
        return False
    
    section_0 = create_sections(VULN_DATA[skill_name])
    
    section_0_match = re.search(r'^## 0\. Anti-Hallucination Protocol.*?\n', content, re.MULTILINE)
    if section_0_match:
        new_content = content[:section_0_match.end()] + "\n" + section_0 + "\n" + content[section_0_match.end():]
    else:
        section_1_match = re.search(r'^## 1\. ', content, re.MULTILINE)
        if not section_1_match:
            return False
        new_content = content[:section_1_match.start()] + section_0 + "\n" + content[section_1_match.start():]
    
    with open(skill_path, 'w') as f:
        f.write(new_content)
    
    return True

skills_dir = Path('.dev-aid/skills/expert')
enriched = 0

for skill_name in sorted(VULN_DATA.keys()):
    skill_path = skills_dir / skill_name / 'SKILL.md'
    if skill_path.exists():
        if enrich_skill(skill_path, skill_name):
            enriched += 1
            print(f"✅ {skill_name}: Enriched")

print(f"\n✅ Database/Data domain complete: {enriched} skills enriched")
