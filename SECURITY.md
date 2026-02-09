# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.5.x (beta) | Yes |
| < 1.5 | No |

## Reporting a Vulnerability

If you discover a security vulnerability in Dev-AID, please report it responsibly.

**Do NOT open a public GitHub issue for security vulnerabilities.**

### How to Report

1. Go to the [Security Advisories](https://github.com/Probably-Group/Dev-AID/security/advisories) page
2. Click "Report a vulnerability"
3. Provide:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- Acknowledgment within 48 hours
- Status update within 7 days
- Fix timeline depends on severity:
  - **Critical**: Patch within 72 hours
  - **High**: Patch within 7 days
  - **Medium/Low**: Next release cycle

### Scope

The following are in scope:
- Dev-AID scripts and configuration files
- Router orchestration code (`.dev-aid/orchestration/`)
- Git hooks and security scanners
- Agent framework (`.dev-aid/agents/`)
- Slash commands and skills

The following are out of scope:
- Third-party AI provider APIs (Anthropic, Google, OpenAI)
- Third-party tools (Gitleaks, Trivy, Opengrep)
- Dependencies in virtual environments (report upstream)

### Security Measures in Dev-AID

- Environment variable isolation for MCP servers
- Input validation with Pydantic strict mode
- Command blocklist for agent subprocess execution
- Pre-commit secret scanning (Gitleaks)
- Exact version pinning for all dependencies

See `.dev-aid/orchestration/SECURITY.md` for detailed internal security documentation.
