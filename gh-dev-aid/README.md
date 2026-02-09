# gh-dev-aid

GitHub CLI extension for [Dev-AID](https://github.com/Probably-Group/Dev-AID) — install and manage Dev-AID with a single command.

## Install

```bash
gh extension install Probably-Group/gh-dev-aid
```

## Usage

```bash
# Add Dev-AID to your project (one-time)
cd ~/my-project
gh dev-aid init

# Update to latest version
gh dev-aid update

# Check health
gh dev-aid status

# Show versions
gh dev-aid version
```

## Commands

| Command | Description |
|---------|-------------|
| `gh dev-aid init [path]` | Install Dev-AID into a project directory (default: current dir) |
| `gh dev-aid update` | Update Dev-AID to the latest version |
| `gh dev-aid status` | Show version and run health check |
| `gh dev-aid version` | Show extension and Dev-AID versions |
| `gh dev-aid help` | Show usage info |

## How it works

- `init` clones Dev-AID via `gh repo clone` (uses your GitHub auth — works for private repos too), copies `.dev-aid/` into your project, and runs the interactive setup wizard.
- `update` delegates to the existing `.dev-aid/scripts/update-dev-aid.sh` which handles backup, version checking, and protected paths.
- `status` reads `.dev-aid/VERSION` and runs the health check script.

## Requirements

- [GitHub CLI](https://cli.github.com/) (`gh`) — authenticated
- Bash

## License

MIT — see [Dev-AID](https://github.com/Probably-Group/Dev-AID) for details.
