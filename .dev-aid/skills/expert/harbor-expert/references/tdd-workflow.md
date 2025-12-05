# Harbor TDD Implementation Workflow

## Step 1: Write Failing Test First

Before implementing any Harbor configuration, write tests to verify expected behavior:

```python
# tests/test_harbor_config.py
import pytest
import requests
from unittest.mock import patch, MagicMock

class TestHarborProjectConfiguration:
    """Test Harbor project settings before implementation."""

    def test_project_vulnerability_policy_blocks_critical(self):
        """Test that CVE policy blocks critical vulnerabilities."""
        # Arrange
        project_config = {
            "prevent_vulnerable": True,
            "severity": "critical",
            "scan_on_push": True
        }

        # Act
        result = validate_vulnerability_policy(project_config)

        # Assert
        assert result["blocks_critical"] == True
        assert result["scan_enabled"] == True

    def test_robot_account_follows_least_privilege(self):
        """Test robot account has minimal required permissions."""
        # Arrange
        robot_permissions = {
            "namespace": "library",
            "access": [
                {"resource": "repository", "action": "pull"},
                {"resource": "repository", "action": "push"}
            ]
        }

        # Act
        result = validate_robot_permissions(robot_permissions)

        # Assert
        assert result["is_scoped"] == True
        assert result["has_admin"] == False
        assert len(result["permissions"]) <= 3

    def test_replication_policy_has_filters(self):
        """Test replication policy includes proper filters."""
        # Arrange
        replication_config = {
            "filters": [
                {"type": "name", "value": "library/app-*"},
                {"type": "tag", "value": "v*"}
            ],
            "trigger": {"type": "scheduled"}
        }

        # Act
        result = validate_replication_policy(replication_config)

        # Assert
        assert result["has_name_filter"] == True
        assert result["has_tag_filter"] == True
        assert result["is_scheduled"] == True


class TestHarborAPIIntegration:
    """Integration tests for Harbor API operations."""

    @pytest.fixture
    def harbor_client(self):
        """Create Harbor API client for testing."""
        return HarborClient(
            url="https://harbor.example.com",
            username="admin",
            password="test"
        )

    def test_create_project_with_security_policies(self, harbor_client):
        """Test project creation includes security policies."""
        # Arrange
        project_spec = {
            "project_name": "test-project",
            "public": False,
            "metadata": {
                "enable_content_trust": "true",
                "prevent_vul": "true",
                "severity": "high",
                "auto_scan": "true"
            }
        }

        # Act
        result = harbor_client.create_project(project_spec)

        # Assert
        assert result.status_code == 201
        project = harbor_client.get_project("test-project")
        assert project["metadata"]["enable_content_trust"] == "true"
        assert project["metadata"]["prevent_vul"] == "true"

    def test_garbage_collection_schedule_configured(self, harbor_client):
        """Test GC schedule is properly configured."""
        # Arrange
        gc_schedule = {
            "schedule": {
                "type": "Weekly",
                "cron": "0 2 * * 6"
            },
            "parameters": {
                "delete_untagged": True,
                "dry_run": False
            }
        }

        # Act
        result = harbor_client.set_gc_schedule(gc_schedule)

        # Assert
        assert result.status_code == 200
        current_schedule = harbor_client.get_gc_schedule()
        assert current_schedule["schedule"]["cron"] == "0 2 * * 6"
```

## Step 2: Implement Minimum to Pass

```python
# harbor_client.py
import requests
from typing import Dict, Any

class HarborClient:
    """Harbor API client with security-first defaults."""

    def __init__(self, url: str, username: str, password: str):
        self.url = url.rstrip('/')
        self.auth = (username, password)
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({"Content-Type": "application/json"})

    def create_project(self, spec: Dict[str, Any]) -> requests.Response:
        """Create project with security policies."""
        # Ensure security defaults
        if "metadata" not in spec:
            spec["metadata"] = {}

        spec["metadata"].setdefault("enable_content_trust", "true")
        spec["metadata"].setdefault("prevent_vul", "true")
        spec["metadata"].setdefault("severity", "high")
        spec["metadata"].setdefault("auto_scan", "true")

        return self.session.post(
            f"{self.url}/api/v2.0/projects",
            json=spec
        )

    def set_gc_schedule(self, schedule: Dict[str, Any]) -> requests.Response:
        """Configure garbage collection schedule."""
        return self.session.post(
            f"{self.url}/api/v2.0/system/gc/schedule",
            json=schedule
        )
```

## Step 3: Refactor If Needed

After tests pass, refactor for better error handling and performance:

```python
# Refactored with retry logic and connection pooling
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class HarborClient:
    def __init__(self, url: str, username: str, password: str):
        self.url = url.rstrip('/')
        self.auth = (username, password)
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create session with retry and connection pooling."""
        session = requests.Session()
        session.auth = self.auth
        session.headers.update({"Content-Type": "application/json"})

        # Configure retries for resilience
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=10
        )
        session.mount("https://", adapter)

        return session
```

## Step 4: Run Full Verification

```bash
# Run all tests
pytest tests/test_harbor_config.py -v

# Run with coverage
pytest tests/test_harbor_config.py --cov=harbor_client --cov-report=term-missing

# Validate actual Harbor configuration
curl -s "https://harbor.example.com/api/v2.0/systeminfo" \
  -u "admin:password" | jq '.harbor_version'

# Test scanner connectivity
curl -s "https://harbor.example.com/api/v2.0/scanners" \
  -u "admin:password" | jq '.[].is_default'

# Verify replication endpoints
curl -s "https://harbor.example.com/api/v2.0/registries" \
  -u "admin:password" | jq '.[].status'
```
