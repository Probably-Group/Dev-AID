# Windows Setup Guide

Dev-AID works on Windows through a combination of native Python and WSL (Windows Subsystem for Linux) for bash-based features.

---

## Prerequisites

- **Windows 10** build 19041 or later, or **Windows 11**
- **Python 3.11+** installed natively (from [python.org](https://www.python.org/downloads/) or Microsoft Store)
- **Git for Windows** (from [git-scm.com](https://git-scm.com/download/win))

---

## Feature Compatibility Matrix

| Feature | Native Windows | WSL Required |
|---------|---------------|-------------|
| **Python orchestration** (router, modes, API clients) | Yes | No |
| **Test suite** (`pytest`) | Yes | No |
| **Code formatting** (`black`, `flake8`, `mypy`) | Yes | No |
| **Setup wizard** (`setup-dev-aid.sh`) | No | Yes |
| **Pre-commit hooks** | No | Yes |
| **Security scanning** (Gitleaks, Trivy, Opengrep) | No | Yes |
| **Local search** (RAG pipeline) | Yes | No |
| **Memory bank** (reading/writing markdown) | Yes | No |
| **Cost tracking** | Yes | No |
| **TUI dashboard** | Yes | No |
| **Bash wrappers** (`router-cli.sh`) | No | Yes |
| **Supply chain verification** | No | Yes |

**Summary**: Core Python components work natively. Bash scripts (setup, hooks, security scans) require WSL.

---

## Option A: WSL Setup (Recommended)

WSL gives you full Linux compatibility for all Dev-AID features.

### 1. Install WSL

Open PowerShell as Administrator:

```powershell
wsl --install
```

This installs Ubuntu by default. Restart your computer when prompted.

### 2. Set Up WSL Environment

Open your WSL terminal (search for "Ubuntu" in Start menu):

```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Git
sudo apt install git -y
```

### 3. Clone and Set Up Dev-AID

```bash
# Clone the repo
cd ~
git clone https://github.com/Probably-Group/Dev-AID.git
cd Dev-AID

# Run the setup wizard
./setup-dev-aid.sh

# Verify
cd .dev-aid/orchestration
venv/bin/python -m pytest tests/ -v --tb=short
```

### 4. Access Windows Files from WSL

Your Windows drives are mounted under `/mnt/`:

```bash
# Access your Windows project
cd /mnt/c/Users/YourName/projects/my-project

# Copy Dev-AID into it
cp -r ~/Dev-AID/.dev-aid ./.dev-aid
```

---

## Option B: Native Windows (Python Only)

If you only need the Python orchestration features:

### 1. Set Up Python Environment

```powershell
# Clone the repo
git clone https://github.com/Probably-Group/Dev-AID.git
cd Dev-AID\.dev-aid\orchestration

# Create virtual environment
python -m venv venv

# Activate venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Router

```powershell
# Test configuration
python -m router.cli test

# Execute a request
python -m router.cli execute "Your prompt here" --mode solo

# View cost dashboard
python -m router.cli dashboard
```

### 3. Run Tests

```powershell
python -m pytest tests/ -v --tb=short
```

---

## Troubleshooting

### WSL won't install

**Error**: `WslRegisterDistribution failed with error: 0x80370102`

**Fix**: Enable virtualization in BIOS (usually under CPU settings > Intel VT-x or AMD-V).

### Python not found in WSL

```bash
# Check available versions
ls /usr/bin/python3*

# If not installed
sudo apt install python3.11 python3.11-venv -y

# Create symlink if needed
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
```

### Permission denied on scripts

```bash
# Make scripts executable
chmod +x setup-dev-aid.sh
chmod +x .dev-aid/scripts/*.sh
```

### venv activation fails in PowerShell

```powershell
# If you get "execution of scripts is disabled"
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then retry
.\venv\Scripts\Activate.ps1
```

### Line ending issues (CRLF vs LF)

Windows uses CRLF line endings which can break bash scripts:

```bash
# In WSL, configure Git to handle line endings
git config --global core.autocrlf input

# Fix existing files
sudo apt install dos2unix -y
find .dev-aid -name "*.sh" -exec dos2unix {} \;
```

### Slow file access in WSL

Accessing files on Windows drives (`/mnt/c/...`) is slow in WSL. For best performance, clone repos inside WSL's native filesystem (`~/`).

---

## IDE Integration

### VS Code + WSL

1. Install the [WSL extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-wsl)
2. Open VS Code from WSL: `code .`
3. All terminal commands run inside WSL automatically

### Cursor / Windsurf

These editors work natively on Windows with the Python components. For bash features, use their integrated terminal pointed at WSL.

---

## Next Steps

After setup, see:
- [Quick Start](../../README.md#-quick-start) for basic usage
- [Commands Reference](.dev-aid/docs/COMMANDS-REFERENCE.md) for all slash commands
- [Router Status](ROUTER-STATUS.md) for orchestration capabilities
