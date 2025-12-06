## 6. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```python
# tests/test_rpc_methods.py
import pytest
from jsonrpc_server import JSONRPCServer

class TestRPCMethods:
    @pytest.fixture
    def server(self):
        return JSONRPCServer()

    def test_method_not_found(self, server):
        response = server.handle_request({"jsonrpc": "2.0", "method": "nonexistent", "id": 1})
        assert response["error"]["code"] == -32601

    def test_invalid_params(self, server):
        server.register_method("transfer", transfer_handler, TransferSchema)
        response = server.handle_request({"jsonrpc": "2.0", "method": "transfer", "params": {"amount": "bad"}, "id": 1})
        assert response["error"]["code"] == -32602

    def test_batch_request_limit(self, server):
        requests = [{"jsonrpc": "2.0", "method": "ping", "id": i} for i in range(200)]
        response = server.handle_request(requests)
        assert response[0]["error"]["code"] == -32600

    def test_successful_method_call(self, server):
        server.register_method("add", lambda p: p["a"] + p["b"], AddSchema)
        response = server.handle_request({"jsonrpc": "2.0", "method": "add", "params": {"a": 2, "b": 3}, "id": 1})
        assert response["result"] == 5
```

### Step 2: Implement Minimum to Pass

```python
# jsonrpc_server.py
class JSONRPCServer:
    def __init__(self):
        self.methods = {}
        self.max_batch_size = 100

    def register_method(self, name, handler, schema):
        self.methods[name] = {"handler": handler, "schema": schema}

    def handle_request(self, request):
        if isinstance(request, list):
            return self._handle_batch(request)
        return self._handle_single(request)

    def _handle_single(self, request):
        method = request.get("method")
        if method not in self.methods:
            return self._error(request.get("id"), -32601, "Method not found")
        # ... implement validation and execution
```

### Step 3: Refactor with Full Patterns

Apply security patterns, error handling, and performance optimizations from sections below.

### Step 4: Run Full Verification

```bash
pytest tests/test_rpc_methods.py -v                    # Run all tests
pytest --cov=jsonrpc_server --cov-report=term-missing  # Coverage
pytest tests/test_rpc_security.py -v                   # Security tests
pytest tests/test_rpc_performance.py --benchmark-only  # Benchmarks
```

---

