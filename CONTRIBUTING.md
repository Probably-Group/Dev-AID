# Contributing to Dev-AID

Thank you for your interest in contributing to Dev-AID!

## How to Contribute

### Reporting Issues

- Check existing issues first
- Provide clear reproduction steps
- Include your configuration (orchestration mode, providers, etc.)
- Share relevant logs (sanitize any secrets!)

### Suggesting Features

- Explain the use case
- Describe expected behavior
- Consider how it affects existing features

### Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test thoroughly (try install.sh and reconfigure.sh)
5. Update documentation if needed
6. Commit with clear messages
7. Submit a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/dev-aid
cd dev-aid

# Test the installer
./.dev-aid/scripts/install.sh

# Test reconfiguration
./.dev-aid/scripts/reconfigure.sh
```

## Code Style

- Shell scripts: Follow existing style, use shellcheck
- Documentation: Clear, concise, with examples
- Configuration: JSON with comments where helpful

## Testing Checklist

- [ ] Install script works from scratch
- [ ] All orchestration modes work
- [ ] Reconfiguration preserves memory bank
- [ ] Documentation is updated
- [ ] No secrets in commits

## Questions?

Open an issue for discussion before major changes.
