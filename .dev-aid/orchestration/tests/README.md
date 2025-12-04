# Dev-AID Router Tests

Comprehensive test suite for the Dev-AID Router following TDD and security best practices.

## Test Coverage

- **test_validators.py** - Input validation with Pydantic models
- **test_security.py** - Security tests (OWASP Top 10, injection, path traversal)
- **test_config_loader.py** - Configuration loading and path safety
- **test_api_clients.py** - API client functionality and error handling

## Running Tests

### Install Dependencies
```bash
cd /home/user/Dev-AID/.dev-aid/orchestration
pip install -r requirements.txt
```

### Run All Tests
```bash
pytest tests/ -v
```

### Run with Coverage
```bash
pytest tests/ --cov=router --cov-report=term-missing --cov-report=html
```

### Run Security Tests Only
```bash
pytest tests/test_security.py -v
```

### Run Specific Test Class
```bash
pytest tests/test_validators.py::TestExecuteRequest -v
```

## Security Scanning

### Static Analysis with Bandit
```bash
bandit -r router/ -ll
```

### Type Checking with MyPy
```bash
mypy router/ --strict
```

### Dependency Auditing
```bash
pip-audit
safety check
```

## Coverage Goals

- Minimum 80% code coverage
- 100% coverage on security-critical paths:
  - Input validation
  - Path traversal prevention
  - Command injection prevention
  - Error handling

## Test Categories

### Unit Tests
- Individual function/method testing
- Mocked dependencies
- Fast execution

### Security Tests
- Injection attack prevention
- Path traversal blocking
- Input sanitization
- Error message safety

### Integration Tests
- End-to-end workflows
- Real file system operations (in temp dirs)
- Configuration loading

## Adding New Tests

1. Create test file: `test_<module>.py`
2. Follow naming convention: `test_<feature>`
3. Use fixtures from `conftest.py`
4. Add docstrings explaining what is tested
5. Include both positive and negative test cases

## CI/CD Integration

Tests should run on:
- Every commit (pre-commit hook)
- Every pull request
- Before deployment

All security scans must pass before merging.
