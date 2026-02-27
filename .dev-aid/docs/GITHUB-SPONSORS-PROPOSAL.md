# GitHub Sponsors Setup Proposal for Dev-AID

## Overview

This document proposes a GitHub Sponsors configuration for Dev-AID to fund ongoing development, infrastructure costs, and community support.

---

## Prerequisites

1. **Enable GitHub Sponsors** for the `Probably-Group` organization at https://github.com/sponsors/Probably-Group
2. **Stripe account** connected to the GitHub Sponsors dashboard
3. **FUNDING.yml** already created at `.github/FUNDING.yml`

---

## Proposed Tier Structure

### Tier 1: Supporter ($5/month)

**Target**: Individual developers who use Dev-AID

**Benefits**:
- Sponsor badge on GitHub profile
- Name listed in SPONSORS.md
- Access to sponsors-only Discord channel (if applicable)

### Tier 2: Pro User ($15/month)

**Target**: Professional developers relying on Dev-AID daily

**Benefits**:
- Everything in Tier 1
- Priority issue responses (48-hour SLA for bug reports)
- Early access to new skills and features (pre-release branch access)
- Vote on feature roadmap priorities

### Tier 3: Team ($50/month)

**Target**: Small teams (2-10 developers)

**Benefits**:
- Everything in Tier 2
- Company logo in README sponsors section
- Quarterly architecture consultation (30-min video call)
- Custom skill development guidance

### Tier 4: Enterprise ($200/month)

**Target**: Larger organizations using Dev-AID across teams

**Benefits**:
- Everything in Tier 3
- Prominent logo placement in README
- Monthly support call (1 hour)
- Custom skill development (1 skill per quarter)
- Priority feature requests
- Private Slack/Discord channel

### Tier 5: Founding Sponsor ($500/month)

**Target**: Organizations wanting to shape Dev-AID's direction

**Benefits**:
- Everything in Tier 4
- Advisory board seat
- Co-creation of enterprise features
- Dedicated integration support
- Custom provider integration

---

## One-Time Sponsorship Options

| Amount | Recognition |
|--------|-------------|
| $10 | Thank-you mention in release notes |
| $50 | Name in SPONSORS.md |
| $100 | Name + link in SPONSORS.md |
| $500 | Logo in README for 3 months |

---

## Fund Allocation Plan

| Category | Allocation | Purpose |
|----------|-----------|---------|
| **Development** | 50% | New features, skill development, bug fixes |
| **Infrastructure** | 20% | CI/CD, testing, hosting, API costs for testing |
| **Community** | 15% | Documentation, tutorials, community support |
| **Security** | 15% | Security audits, dependency monitoring, CVE response |

---

## README Badge Integration

Add the Sponsor button badge to README.md (near the top, after existing badges):

```markdown
[![Sponsor](https://img.shields.io/badge/Sponsor-Dev--AID-ea4aaa?logo=github-sponsors)](https://github.com/sponsors/Probably-Group)
```

---

## Sponsor Recognition

### SPONSORS.md File

Create a `SPONSORS.md` at repo root to recognize sponsors:

```markdown
# Sponsors

Thank you to all our sponsors who support Dev-AID development!

## Founding Sponsors

*Be the first founding sponsor!*

## Enterprise Sponsors

*Your company here*

## Team Sponsors

*Your team here*

## Pro Users

*Your name here*

## Supporters

*Your name here*
```

### README Section

Add a "Sponsors" section to the README between "Contributing" and "License":

```markdown
## Sponsors

Dev-AID is supported by these amazing sponsors:

<!-- sponsors -->
*Become the first sponsor! [Sponsor Dev-AID](https://github.com/sponsors/Probably-Group)*
<!-- sponsors -->
```

---

## Implementation Checklist

- [x] Create `.github/FUNDING.yml` with `github: [Probably-Group]`
- [ ] Enable GitHub Sponsors for `Probably-Group` organization
- [ ] Connect Stripe account
- [ ] Configure tier structure in GitHub Sponsors dashboard
- [ ] Create `SPONSORS.md` at repo root
- [ ] Add sponsor badge to README.md
- [ ] Add sponsor recognition section to README.md
- [ ] Set up sponsor-only Discord channel (optional)
- [ ] Configure automated sponsor welcome message
- [ ] Set up monthly sponsor update newsletter (optional)

---

## Competitive Analysis

| Project | Sponsorship Model | Monthly Tiers |
|---------|-------------------|---------------|
| **Ruff** | GitHub Sponsors | $5-$500/mo |
| **FastAPI** | GitHub Sponsors + OpenCollective | $5-$2000/mo |
| **Astral** | Corporate sponsorship | Custom |
| **Dev-AID** (proposed) | GitHub Sponsors | $5-$500/mo |

---

## Timeline

1. **Week 1**: Enable Sponsors, configure tiers, connect Stripe
2. **Week 2**: Create SPONSORS.md, update README with badge
3. **Week 3**: Announce on social media and relevant communities
4. **Month 2**: Evaluate tier adoption, adjust pricing if needed
5. **Month 3**: Add automated sponsor integration (auto-update SPONSORS.md)

---

**Created**: 2026-02-27
**Status**: Proposal — awaiting organization admin approval
