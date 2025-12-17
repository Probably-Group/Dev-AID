# CI Frequency Configuration Guide

## Overview

The Dev-AID CI generator supports three frequency profiles that control how often CI workflows run. Choose the profile that best balances thoroughness with cost for your project.

---

## 📊 Frequency Profiles

### 🔴 Aggressive (100% Cost - Maximum Thoroughness)

**Best for:** Mission-critical production code, open-source projects with many contributors

```bash
.dev-aid/scripts/generate-ci.sh . --frequency aggressive
```

**Configuration:**
- **Triggers:** Every push + every PR
- **Branches:** main, master, develop
- **Platforms:** Ubuntu + Windows + macOS
- **Draft PRs:** Included (runs on drafts too)
- **Path Filters:** None (runs on all file changes)
- **Concurrency Cancel:** Disabled (runs all builds)

**When it runs:**
- Every push to main/master/develop branches
- Every PR opened, synchronized, or reopened
- All file types trigger builds
- Runs on 3 OS platforms in parallel

**Cost estimate:** 100% baseline (highest cost)
**Minutes per run:** ~6-10 minutes (3 platforms)
**Runs per week:** ~50-100 (very frequent)

**Use when:**
- You need maximum confidence before merging
- Platform compatibility is critical (desktop apps, CLI tools)
- Multiple team members pushing frequently
- Budget for CI minutes is not a concern

---

### 🟡 Balanced (15-30% Cost - Recommended) ⭐

**Best for:** Most projects, active development teams, reasonable cost control

```bash
.dev-aid/scripts/generate-ci.sh . --frequency balanced  # Default
```

**Configuration:**
- **Triggers:** PRs only (not direct pushes)
- **Branches:** main, master, develop
- **Platforms:** Ubuntu only (single OS)
- **Draft PRs:** Skipped (saves CI on work-in-progress)
- **Path Filters:** Code files only (**.py, **.js, **.ts, **.go, **.rs)
- **Concurrency Cancel:** Enabled (cancels outdated runs)

**When it runs:**
- Every PR to main/master/develop
- Only when code files change (not docs/config)
- Skips draft PRs until marked ready for review
- Runs on Ubuntu only

**Cost estimate:** 15-30% of aggressive (recommended sweet spot)
**Minutes per run:** ~2-3 minutes (1 platform)
**Runs per week:** ~20-30 (moderate)

**Use when:**
- You want good coverage without excessive cost
- Ubuntu testing is sufficient for most development
- You use draft PRs for work-in-progress
- Code changes more frequently than docs

**Why recommended:**
- ✅ Catches 95% of issues while saving 70-85% of CI minutes
- ✅ Fast feedback (2-3 min vs 6-10 min)
- ✅ Automatic concurrency cancellation prevents wasted runs
- ✅ Path filters avoid unnecessary runs for docs/config changes

---

### 🟢 Minimal (5-10% Cost - Lowest Overhead)

**Best for:** Personal projects, low-traffic repos, extremely tight budgets

```bash
.dev-aid/scripts/generate-ci.sh . --frequency minimal
```

**Configuration:**
- **Triggers:** Pushes to main/master only
- **Branches:** main, master (no develop branch)
- **Platforms:** Ubuntu only
- **Draft PRs:** Skipped (N/A - no PR triggers)
- **Path Filters:** Code files only
- **Concurrency Cancel:** Enabled

**When it runs:**
- Only when code is pushed directly to main/master
- Only when code files change
- PRs do NOT trigger CI (manual testing expected)

**Cost estimate:** 5-10% of aggressive (lowest cost)
**Minutes per run:** ~2-3 minutes (1 platform)
**Runs per week:** ~5-10 (minimal)

**Use when:**
- You're a solo developer or very small team
- You manually test before merging to main
- CI budget is extremely limited
- You primarily use CI as a final safety net, not continuous validation

**Trade-offs:**
- ⚠️ No CI feedback on PRs (test locally first)
- ⚠️ Only catches issues after merge to main
- ⚠️ Requires strong local testing discipline

---

## 📈 Comparison Table

| Feature | Aggressive | Balanced | Minimal |
|---------|-----------|----------|---------|
| **Triggers** | Push + PR | PR only | Push to main only |
| **Platforms** | 3 (U+W+M) | 1 (Ubuntu) | 1 (Ubuntu) |
| **Draft PRs** | Runs | Skipped ✅ | N/A |
| **Path Filters** | None | Code files ✅ | Code files ✅ |
| **Concurrency Cancel** | No | Yes ✅ | Yes ✅ |
| **Cost** | 100% | 15-30% | 5-10% |
| **Minutes/Run** | 6-10 min | 2-3 min | 2-3 min |
| **Runs/Week** | 50-100 | 20-30 | 5-10 |
| **Annual Minutes** | ~3,000 | ~450-900 | ~150-300 |

---

## 💰 Cost Examples

### Scenario: 5-developer team, 20 PRs/week

**Aggressive:**
- 20 PRs × 5 pushes/PR × 3 OS × 3 min = **900 min/week**
- Annual: 46,800 minutes

**Balanced:**
- 20 PRs × 3 pushes/PR × 1 OS × 2 min = **120 min/week**
- Annual: 6,240 minutes
- **Savings: 87% reduction**

**Minimal:**
- 5 merges/week × 1 OS × 2 min = **10 min/week**
- Annual: 520 minutes
- **Savings: 98% reduction**

---

## 🎯 Choosing the Right Profile

### Choose **Aggressive** if:
- ✅ You have a large team (10+ developers)
- ✅ You ship software that runs on Windows/macOS/Linux
- ✅ You have budget for GitHub Actions minutes
- ✅ You need maximum confidence before merging

### Choose **Balanced** if: ⭐ (Recommended)
- ✅ You want good CI coverage without excessive cost
- ✅ Your software primarily targets Linux/containers
- ✅ You use PRs for code review (most teams)
- ✅ You use draft PRs for work-in-progress

### Choose **Minimal** if:
- ✅ You're a solo developer or very small team
- ✅ You have tight budget constraints
- ✅ You test locally before pushing to main
- ✅ You need CI mainly as a safety net

---

## 🔧 Usage Examples

### Generate with default (balanced):
```bash
.dev-aid/scripts/generate-ci.sh /path/to/project
```

### Generate with optimized performance + minimal cost:
```bash
.dev-aid/scripts/generate-ci.sh /path/to/project --optimize --frequency minimal
```

### Generate aggressive CI for open-source project:
```bash
.dev-aid/scripts/generate-ci.sh /path/to/project --optimize --frequency aggressive
```

### View help:
```bash
.dev-aid/scripts/generate-ci.sh --help
```

---

## 🔄 Switching Profiles

You can regenerate your CI workflow anytime to switch profiles:

```bash
# Currently using aggressive? Switch to balanced:
.dev-aid/scripts/generate-ci.sh . --frequency balanced

# Backup old workflow first (optional):
cp .github/workflows/ci.yml .github/workflows/ci.yml.backup

# Generate new workflow:
.dev-aid/scripts/generate-ci.sh . --frequency balanced
```

---

## 📊 Monitoring CI Usage

Track your GitHub Actions usage:
```bash
# View CI minute consumption
gh api repos/:owner/:repo/actions/metrics/usage

# View workflow runs
gh run list --limit 20
```

---

## 🎓 Best Practices

1. **Start with Balanced** - It's the sweet spot for most teams
2. **Use Draft PRs** - Mark PRs as draft while working to skip CI
3. **Monitor Usage** - Check your Actions usage monthly
4. **Test Locally First** - Use the Local CI Validation system before pushing
5. **Upgrade to Aggressive** - When nearing a major release for extra confidence

---

## 🔗 Related Documentation

- [Local CI Validation](./LOCAL-CI-VALIDATION.md) - Run CI checks locally before pushing
- [CI Optimization Guide](./CI-OPTIMIZATION-GUIDE.md) - Performance optimization tips
- [GitHub Actions Pricing](https://docs.github.com/en/billing/managing-billing-for-github-actions/about-billing-for-github-actions)

---

**Status:** ✅ Production Ready
**Version:** 1.0.0
**Last Updated:** 2025-12-16
