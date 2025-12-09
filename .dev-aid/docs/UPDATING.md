# Updating Dev-AID

Complete guide to updating Dev-AID in existing repositories.

---

## 🎯 Overview

Dev-AID uses semantic versioning and provides safe update mechanisms that preserve your:
- ✅ API keys (.env files)
- ✅ Memory bank (patterns, decisions, context)
- ✅ Logs (routing history, costs)
- ✅ Custom modifications

**Current version**: Check `.dev-aid/VERSION`

**Update frequency**: Monthly releases (bug fixes) + Quarterly features

---

## 🚀 Quick Update (Recommended)

### Automated Update Script

```bash
cd your-project

# Run update script
./.dev-aid/scripts/update-dev-aid.sh
```

**What it does**:
1. ✅ Checks current version
2. ✅ Creates automatic backup
3. ✅ Updates all Dev-AID components
4. ✅ Preserves your API keys and memory bank
5. ✅ Updates dependencies
6. ✅ Shows changelog

**Time**: 2-3 minutes

---

## 📋 Update Methods

### Method 1: Automated Script (Easiest)

```bash
# From project root
./.dev-aid/scripts/update-dev-aid.sh

# Choose option:
# 1. Pull from official repo (recommended)
# 2. Copy from local Dev-AID installation
# 3. Manual update (guide)
```

**Pros**:
- ✅ Automatic backup
- ✅ Preserves user data
- ✅ Updates dependencies
- ✅ Shows diff of changes

**Cons**:
- ❌ Requires internet (option 1)

---

### Method 2: Manual Copy (Full Control)

```bash
# 1. Create backup
cp -r .dev-aid .dev-aid-backup-$(date +%Y%m%d)

# 2. Download/clone latest Dev-AID
cd /tmp
git clone https://github.com/your-org/dev-aid.git

# 3. Copy updated files (excluding user data)
cd your-project
rsync -av --exclude='.env*' \
          --exclude='memory-bank/' \
          --exclude='logs/' \
          --exclude='.venv/' \
          /tmp/dev-aid/.dev-aid/ .dev-aid/

# 4. Update dependencies
cd .dev-aid/orchestration
source .venv/bin/activate
pip install -r requirements.txt --upgrade
deactivate
```

**Pros**:
- ✅ Full control over what's updated
- ✅ Can review changes before applying
- ✅ Works offline (if you have the files)

**Cons**:
- ❌ More manual steps
- ❌ Need to remember exclusions

---

### Method 3: Git Subtree (Advanced)

For teams managing Dev-AID as a subtree:

```bash
# Initial setup (one-time)
git remote add dev-aid-upstream https://github.com/your-org/dev-aid.git
git subtree add --prefix=.dev-aid dev-aid-upstream main --squash

# Update later
git subtree pull --prefix=.dev-aid dev-aid-upstream main --squash
```

**Pros**:
- ✅ Git tracks updates
- ✅ Easy to revert
- ✅ Team synchronization

**Cons**:
- ❌ Complex setup
- ❌ Need to resolve merge conflicts

---

## 📦 What Gets Updated

### Always Updated

| Component | Path | Why |
|-----------|------|-----|
| Router code | `.dev-aid/orchestration/router/` | Bug fixes, features |
| Scripts | `.dev-aid/scripts/` | New automation |
| Documentation | `.dev-aid/docs/` | Guides, references |
| Skills | `.dev-aid/providers/*/skills/` | New expert skills |
| Commands | `.dev-aid/providers/*/commands/` | New slash commands |
| Dependencies | `.dev-aid/orchestration/requirements.txt` | Security patches |

### Never Overwritten

| Component | Path | Why |
|-----------|------|-----|
| API keys | `.dev-aid/config/.env` | **SECURITY**: Your credentials |
| Memory bank | `.dev-aid/memory-bank/*.md` | Your team knowledge |
| Logs | `.dev-aid/logs/` | Your history |
| Venv | `.dev-aid/orchestration/.venv/` | Regenerated from requirements.txt |

### Merged (You Choose)

| Component | Path | Behavior |
|-----------|------|----------|
| Configuration | `.dev-aid/config/*.json` | Script asks which to keep |
| Custom skills | User-created skills | Preserved by default |
| Memory bank | New vs old versions | Keeps newer file |

---

## 🔍 Version Compatibility

### Semantic Versioning

Dev-AID follows [SemVer](https://semver.org/):

```
MAJOR.MINOR.PATCH
  1  .  0  .  0

MAJOR: Breaking changes (manual migration needed)
MINOR: New features (backward compatible)
PATCH: Bug fixes (always safe)
```

### Compatibility Matrix

| From Version | To Version | Safe? | Notes |
|--------------|------------|-------|-------|
| 1.0.x → 1.0.y | ✅ Always | Automatic, no changes needed |
| 1.0.x → 1.1.x | ✅ Usually | Check CHANGELOG for new features |
| 1.x.x → 2.0.0 | ⚠️ Manual | Read migration guide, breaking changes |

---

## 🛡️ Safe Update Process

### Pre-Update Checklist

```bash
# 1. Check current version
cat .dev-aid/VERSION
# Output: 1.0.0

# 2. Commit your work (if in Git)
git add .
git commit -m "Save before Dev-AID update"

# 3. Verify API keys are NOT in Git
git status --ignored | grep .env
# Should see: .dev-aid/config/.env (ignored)

# 4. Note current router status
./.dev-aid/orchestration/router-cli.sh status > /tmp/router-status-before.txt
```

### Update

```bash
# Run update script
./.dev-aid/scripts/update-dev-aid.sh
```

### Post-Update Verification

```bash
# 1. Check new version
cat .dev-aid/VERSION
# Output: 1.1.0

# 2. Verify configuration
./.dev-aid/orchestration/router-cli.sh test

# 3. Test router
./.dev-aid/orchestration/router-cli.sh execute "test" --verbose

# 4. Check API keys still present
ls -la .dev-aid/config/.env
# Should exist

# 5. Verify memory bank preserved
ls -la .dev-aid/memory-bank/
# Should have your files

# 6. Check routing logs preserved
ls -la .dev-aid/logs/
# Should have your history
```

### Rollback (If Needed)

```bash
# If update fails, restore from backup
BACKUP_DIR=.dev-aid-backup-YYYYMMDD-HHMMSS

rm -rf .dev-aid
mv $BACKUP_DIR .dev-aid

# Or if using Git:
git checkout .dev-aid/
```

---

## 🔄 Update Scenarios

### Scenario 1: Patch Update (1.0.0 → 1.0.1)

**Example**: Bug fixes, security patches

```bash
# Simple update
./.dev-aid/scripts/update-dev-aid.sh

# Choose option 1 (pull from repo)
# Done! ✅
```

**Changes**: Code fixes only, no configuration changes

**Time**: 2 minutes

---

### Scenario 2: Minor Update (1.0.0 → 1.1.0)

**Example**: New features, new skills, new commands

```bash
# Update as usual
./.dev-aid/scripts/update-dev-aid.sh

# Check CHANGELOG for new features
cat .dev-aid/CHANGELOG.md

# Test new features
./.dev-aid/orchestration/router-cli.sh status
```

**Changes**: New capabilities added, existing features unchanged

**Time**: 5 minutes (includes reading changelog)

---

### Scenario 3: Major Update (1.x.x → 2.0.0)

**Example**: Breaking changes, API changes, config format changes

```bash
# READ MIGRATION GUIDE FIRST!
# Check CHANGELOG.md for breaking changes

# Create backup
cp -r .dev-aid .dev-aid-v1-backup

# Run update
./.dev-aid/scripts/update-dev-aid.sh

# Run migration script (if provided)
./.dev-aid/scripts/migrate-to-v2.sh

# Manually update configuration (if needed)
nano .dev-aid/config/routing.json
```

**Changes**: May require configuration updates, API key changes, etc.

**Time**: 15-30 minutes (includes migration)

---

## 📊 Multi-Project Updates

### Update All Projects at Once

If you have Dev-AID in multiple projects:

```bash
# Create update script
cat > ~/update-all-dev-aid.sh << 'EOF'
#!/bin/bash
PROJECTS=(
    ~/work/project-a
    ~/work/project-b
    ~/personal/project-c
)

for project in "${PROJECTS[@]}"; do
    echo "Updating: $project"
    cd "$project"

    if [ -d ".dev-aid" ]; then
        ./.dev-aid/scripts/update-dev-aid.sh
        echo "✓ Updated $project"
    else
        echo "⚠ No Dev-AID in $project"
    fi
    echo ""
done
EOF

chmod +x ~/update-all-dev-aid.sh

# Run
~/update-all-dev-aid.sh
```

---

## 🔔 Stay Updated

### Check for Updates

```bash
# Manual check
curl -s https://raw.githubusercontent.com/your-org/dev-aid/main/.dev-aid/VERSION

# Compare with your version
cat .dev-aid/VERSION
```

### Subscribe to Releases

**GitHub**:
1. Go to repository
2. Click "Watch" → "Custom" → "Releases"
3. Get email notifications for new versions

**RSS Feed**:
```
https://github.com/your-org/dev-aid/releases.atom
```

---

## 🐛 Troubleshooting

### "Update script not found"

```bash
# Download update script manually
curl -o .dev-aid/scripts/update-dev-aid.sh \
  https://raw.githubusercontent.com/your-org/dev-aid/main/.dev-aid/scripts/update-dev-aid.sh

chmod +x .dev-aid/scripts/update-dev-aid.sh
```

### "Dependencies failed to update"

```bash
# Recreate virtual environment
cd .dev-aid/orchestration
rm -rf .venv
./setup-venv.sh
```

### "Router not working after update"

```bash
# Check configuration
./.dev-aid/orchestration/router-cli.sh test

# Compare with backup
diff -r .dev-aid/config/ .dev-aid-backup-*/config/

# Restore config if needed
cp .dev-aid-backup-*/config/routing.json .dev-aid/config/
```

### "Memory bank got overwritten"

```bash
# Restore from backup
cp -r .dev-aid-backup-*/memory-bank/* .dev-aid/memory-bank/
```

---

## 📚 Best Practices

### For Individual Developers

1. **Update monthly**: Check for patches and security fixes
2. **Read CHANGELOG**: Understand what changed
3. **Test after update**: Run `router-cli.sh test`
4. **Keep backups**: Don't delete backup for at least a week

### For Teams

1. **Coordinate updates**: Update together to avoid config drift
2. **Test in staging**: Update dev environment first
3. **Document custom changes**: Track what you modified
4. **Use version pinning**: Agree on version (add to README)

### For CI/CD

```yaml
# .github/workflows/update-dev-aid.yml
name: Check Dev-AID Updates

on:
  schedule:
    - cron: '0 0 * * 1'  # Every Monday

jobs:
  check-update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Check version
        run: |
          CURRENT=$(cat .dev-aid/VERSION)
          LATEST=$(curl -s https://raw.githubusercontent.com/your-org/dev-aid/main/.dev-aid/VERSION)

          if [ "$CURRENT" != "$LATEST" ]; then
            echo "::warning::Dev-AID update available: $CURRENT → $LATEST"
          fi
```

---

## 🔗 Related Documentation

- [CHANGELOG.md](../../CHANGELOG.md) - What's new in each version
- [STORAGE-LOCATIONS.md](./STORAGE-LOCATIONS.md) - Where files are stored
- [DEPENDENCY-ISOLATION.md](./DEPENDENCY-ISOLATION.md) - Virtual environment updates
- [Skills Architecture](./SKILLS-ARCHITECTURE.md) - Skills system updates

---

## 📞 Support

**Update issues?**
- Check [Troubleshooting](#-troubleshooting) above
- Read [CHANGELOG.md](../CHANGELOG.md) for known issues
- Open issue: [GitHub Issues](https://github.com/your-org/dev-aid/issues)

**Breaking changes?**
- Check `MIGRATION-vX.md` guides
- Ask in [Discussions](https://github.com/your-org/dev-aid/discussions)

---

**Summary**: Update Dev-AID safely with `./.dev-aid/scripts/update-dev-aid.sh`. The script preserves your API keys, memory bank, and logs while updating code and dependencies. Always read the CHANGELOG and test after updating.
