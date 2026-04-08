# Python Virtual Environment for Dev-AID Router

## Why Virtual Environment?

Python virtual environments solve a critical problem: **dependency isolation**.

### Problem Without Virtual Environment

```bash
# Installing directly to system Python
$ pip install anthropic==0.18.0
# This installs to /usr/lib/python3/...

# Later, another project needs different version
$ pip install anthropic==0.25.0
# Overwrites the first version!
# First project breaks! 💥
```

**Common issues**:
- ❌ Dependency conflicts between projects
- ❌ Version incompatibilities
- ❌ Permission errors (need sudo on Linux)
- ❌ Polluted system Python with hundreds of packages
- ❌ Hard to reproduce environments
- ❌ Can't test with different Python versions

### Solution: Virtual Environment

```bash
# Each project gets isolated environment
project1/.venv/
  └─ anthropic==0.18.0  ✅

project2/.venv/
  └─ anthropic==0.25.0  ✅

# System Python stays clean! ✅
```

---

## How It Works

### 1. Creation

```bash
$ python3 -m venv .venv
```

This creates:
```
.venv/
├── bin/
│   ├── python       # Isolated Python interpreter
│   ├── pip          # Isolated pip
│   └── activate     # Activation script
├── lib/
│   └── python3.X/
│       └── site-packages/  # Isolated packages go here
└── pyvenv.cfg       # Configuration
```

### 2. Activation

```bash
$ source .venv/bin/activate
(venv) $ which python
/path/to/project/.venv/bin/python  # Uses venv Python!

(venv) $ pip install anthropic
# Installs to .venv/lib/python3.X/site-packages
# NOT to system Python!
```

### 3. Usage

```bash
(venv) $ python -m router.cli execute "test"
# Uses packages from .venv/
```

### 4. Deactivation

```bash
(venv) $ deactivate
$ which python
/usr/bin/python  # Back to system Python
```

---

## Dev-AID Router Implementation

### Automated Virtual Environment

Dev-AID uses venv automatically - you don't need to think about it!

**Setup** (one-time):
```bash
$ cd .dev-aid/orchestration
$ ./setup-venv.sh
```

**Usage** (automatic):
```bash
$ ./router-cli.sh execute "Your request"
# Automatically activates .venv
# Runs the router
# Deactivates .venv when done
```

### How router-cli.sh Works

```bash
#!/bin/bash
# router-cli.sh

# Check if venv exists
if [ -d ".venv" ]; then
    # Activate it
    source .venv/bin/activate
fi

# Run router (uses venv Python if activated)
python3 -m router.cli "$@"

# Deactivate
deactivate
```

**Benefits**:
- ✅ User doesn't need to remember activation
- ✅ Always uses correct Python environment
- ✅ Graceful fallback if venv doesn't exist
- ✅ Clear error messages if dependencies missing

---

## Virtual Environment vs Anaconda/Conda

| Feature | venv (used by Dev-AID) | Anaconda/Conda |
|---------|------------------------|----------------|
| **Size** | ~10MB | ~3GB |
| **Installation** | Built into Python | Separate download |
| **Speed** | Fast | Slower |
| **Complexity** | Simple | More complex |
| **Best for** | Pure Python projects | Data science, complex deps |
| **Package source** | PyPI (pip) | Conda channels + PyPI |
| **Disk usage** | Minimal | Heavy |

**Why venv for Dev-AID?**
- ✅ Built into Python 3.3+ (no extra install)
- ✅ Lightweight (perfect for router dependencies)
- ✅ Standard Python packaging
- ✅ Fast activation/deactivation
- ✅ Easy to understand and debug

**When to use Conda instead?**
- You need conda-only packages (rare)
- You're doing data science (NumPy, TensorFlow, etc.)
- You need to manage Python versions (venv uses system Python)
- You want GUI package management

For Dev-AID router: **venv is perfect!**

---

## File Structure

```
.dev-aid/orchestration/
├── .venv/                    # Virtual environment (gitignored)
│   ├── bin/
│   │   ├── python            # Python 3.11+
│   │   ├── pip               # Package installer
│   │   └── activate          # Activation script
│   ├── lib/
│   │   └── python3.X/
│   │       └── site-packages/
│   │           ├── anthropic/
│   │           ├── google/
│   │           ├── openai/
│   │           └── ...
│   └── pyvenv.cfg
├── requirements.txt          # Dependency list
├── setup-venv.sh            # Setup script
└── router-cli.sh            # Wrapper (auto-activates venv)
```

---

## Common Operations

### Create New Virtual Environment

```bash
cd .dev-aid/orchestration
./setup-venv.sh
```

### Remove Virtual Environment

```bash
rm -rf .dev-aid/orchestration/.venv
# That's it! Clean slate.
```

### Reinstall Everything

```bash
cd .dev-aid/orchestration
rm -rf .venv
./setup-venv.sh
```

### Update a Package

```bash
source .dev-aid/orchestration/.venv/bin/activate
pip install --upgrade anthropic
deactivate
```

### Add New Package

```bash
# 1. Activate venv
source .dev-aid/orchestration/.venv/bin/activate

# 2. Install package
pip install new-package

# 3. Update requirements.txt
pip freeze > requirements.txt

# 4. Deactivate
deactivate
```

### Check What's Installed

```bash
source .dev-aid/orchestration/.venv/bin/activate
pip list
deactivate
```

---

## Troubleshooting

### Problem: "source: not found"

You're using `sh` instead of `bash`:

```bash
# Wrong
$ sh .venv/bin/activate

# Right
$ source .venv/bin/activate
# OR
$ . .venv/bin/activate
```

### Problem: venv directory is huge

Virtual environments only hold packages, not data:

```bash
# Check size
$ du -sh .dev-aid/orchestration/.venv
# Should be ~50-100MB for router dependencies

# If much larger, check for:
$ find .venv -type f -size +10M
# Large files shouldn't be in venv
```

### Problem: Permission denied

Don't use sudo with venv:

```bash
# Wrong
$ sudo source .venv/bin/activate

# Right
$ source .venv/bin/activate
# No sudo needed!
```

### Problem: Python version mismatch

venv uses the Python it was created with:

```bash
# Check venv Python version
$ .venv/bin/python --version

# Recreate with different Python
$ rm -rf .venv
$ python3.11 -m venv .venv  # Use specific version
```

---

## Best Practices

### ✅ DO

- **Gitignore .venv/**: Always exclude from version control
- **Use requirements.txt**: Track dependencies, not the venv itself
- **One venv per project**: Don't share across projects
- **Use setup scripts**: Like `setup-venv.sh` for automation
- **Activate for manual work**: When adding packages or debugging

### ❌ DON'T

- **Commit .venv/** to git: Too large, system-specific
- **Activate permanently**: Only activate when needed
- **Mix system and venv packages**: Leads to confusion
- **Use sudo**: Defeats the purpose of isolation
- **Share venvs**: Each project should have its own

---

## Technical Details

### Activation Script

What happens when you run `source .venv/bin/activate`:

```bash
# 1. Saves old PATH
export _OLD_VIRTUAL_PATH="$PATH"

# 2. Prepends venv/bin to PATH
export PATH="/path/to/.venv/bin:$PATH"

# 3. Sets environment variable
export VIRTUAL_ENV="/path/to/.venv"

# 4. Changes prompt
export PS1="(venv) $PS1"

# Now 'python' and 'pip' resolve to venv versions!
```

### Deactivation

What happens when you run `deactivate`:

```bash
# 1. Restores original PATH
export PATH="$_OLD_VIRTUAL_PATH"

# 2. Unsets variables
unset VIRTUAL_ENV
unset _OLD_VIRTUAL_PATH

# 3. Restores original prompt
export PS1="$_OLD_VIRTUAL_PS1"
```

---

## Comparison with Other Solutions

| Solution | Isolation | Complexity | Best For |
|----------|-----------|------------|----------|
| **venv** | ✅ Good | Low | Single Python projects |
| **virtualenv** | ✅ Good | Low | Legacy Python (< 3.3) |
| **conda** | ✅ Excellent | Medium | Data science |
| **poetry** | ✅ Good | Medium | Modern Python apps |
| **pipenv** | ✅ Good | Medium | Web apps |
| **docker** | ✅ Excellent | High | Full isolation |
| **System pip** | ❌ None | Very low | NOT recommended |

**Dev-AID uses venv because**:
- Built into Python 3.3+
- Simple and reliable
- Perfect for router's needs
- No external dependencies

---

## Summary

**Virtual environments are essential for Python development.**

Dev-AID's router uses venv to:
1. ✅ Isolate dependencies from system Python
2. ✅ Prevent version conflicts
3. ✅ Keep installation clean and reversible
4. ✅ Make setup reproducible

**You don't need to manage it manually** - `setup-venv.sh` and `router-cli.sh` handle everything automatically!

**Key takeaway**: Think of venv as a **sandbox for Python packages** - install, test, and remove without affecting your system. 🎉
