# Testing Status & Known Issues

## Current Test Results

### ✅ Passing Tests
- Type checking (mypy)
- Most unit tests (68 out of 80 tests passing)

### ❌ Known Failing Tests

The following tests have pre-existing failures that need investigation:

#### 1. API Client Tests
- `test_send_request_error_handling` - AttributeError: module 'router.api_clients' has no attribute 'anthropic'
- **Cause**: Test setup issue with mocking

#### 2. Config Loader Tests  
- `test_validate_provider_success` - Validation logic needs review
- **Cause**: Test expectations vs actual behavior mismatch

#### 3. Context Builder Tests
- `test_build_context_basic` - Context building logic issue
- `test_format_context` - Format output verification failure
- **Cause**: Integration test expectations

#### 4. Security Tests
- `test_control_characters` - Input sanitization edge case
- `test_template_injection_detection[{{7*7}}]` - Jinja2 template detection
- `test_template_injection_detection[{{config}}]` - Template variable detection
- **Cause**: Regex pattern matching needs tuning

#### 5. Task Classifier Tests
- `test_classify_security` - Classification algorithm issue
- **Cause**: Task classification logic

#### 6. Validator Tests
- `test_invalid_injection` - Injection detection
- `test_containment` - Path containment validation
- `test_invalid_program` - Program allowlist validation  
- `test_invalid_threshold` - Cost threshold validation
- **Cause**: Validation rule edge cases

## Test Coverage
- Current: 68/80 tests passing (85%)
- Target: 100% (all tests passing)

## Next Steps
1. Investigate each failing test individually
2. Fix test setup and mocking issues
3. Update validation logic where needed
4. Add missing test cases for edge conditions
5. Improve test documentation

## Running Tests
```bash
cd .dev-aid/orchestration
pytest tests/ -v
```

## Test Organization
- `tests/test_api_clients.py` - API client unit tests
- `tests/test_config_loader.py` - Configuration loading tests
- `tests/test_context_builder.py` - Context building tests
- `tests/test_security.py` - Security validation tests
- `tests/test_task_classifier.py` - Task classification tests
- `tests/test_validators.py` - Input validation tests

---
Last updated: 2025-12-06
