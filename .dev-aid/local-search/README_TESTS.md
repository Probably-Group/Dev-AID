# Local Search Tests

This directory contains comprehensive tests for the Dev-AID Local Search module.

## Running Tests

### Install Test Dependencies

```bash
pip install -e ".[dev]"
```

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=. --cov-report=html
```

### Run Specific Test Files

```bash
# Test chunker only
pytest tests/test_chunker.py

# Test index only
pytest tests/test_index.py

# Test embeddings only
pytest tests/test_embeddings.py
```

### Run Specific Tests

```bash
# Run a specific test function
pytest tests/test_chunker.py::TestMultiLanguageChunker::test_chunk_python_file

# Run all tests in a class
pytest tests/test_index.py::TestCodeSearchIndex
```

## Test Structure

```
tests/
├── __init__.py              # Package marker
├── conftest.py              # Shared fixtures
├── test_chunker.py          # Code chunking tests
├── test_index.py            # FAISS index tests
└── test_embeddings.py       # Embedding generation tests
```

## Test Coverage

The test suite covers:

### Chunker Tests (`test_chunker.py`)
- ✅ Language detection (Python, JavaScript, TypeScript, etc.)
- ✅ File chunking with size limits
- ✅ Directory chunking with exclusions
- ✅ Line number tracking
- ✅ Empty file handling
- ✅ Error handling for nonexistent files

### Index Tests (`test_index.py`)
- ✅ Index building and search
- ✅ Save/load operations
- ✅ **Pickle to JSON migration** (security)
- ✅ Empty index handling
- ✅ Score calculation
- ✅ Statistics and metadata
- ✅ Index clearing
- ✅ Corrupted data handling

### Embeddings Tests (`test_embeddings.py`)
- ✅ Device selection (CPU, CUDA, MPS)
- ✅ Batch embedding generation
- ✅ Query embedding
- ✅ Normalization
- ✅ Progress bar handling
- ✅ Empty input handling

## Security Tests

The test suite includes specific security checks:

1. **Pickle Migration** (`test_index.py::test_pickle_migration`)
   - Verifies that legacy pickle files are migrated to JSON
   - Ensures pickle files are deleted after migration

2. **JSON Format Security** (`test_index.py::test_json_format_security`)
   - Confirms that new saves use JSON, not pickle
   - Prevents RCE vulnerabilities from pickle deserialization

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -e ".[dev]"
    pytest --cov=. --cov-report=xml
```

## Adding New Tests

When adding new features:

1. Create test file in `tests/` directory
2. Add fixtures to `conftest.py` if reusable
3. Follow naming convention: `test_*.py`, `Test*`, `test_*`
4. Aim for >70% coverage
5. Include both happy path and error cases
