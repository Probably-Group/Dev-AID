# Harbor Testing Guide

## Unit Testing Harbor Configurations

```python
# tests/test_harbor_policies.py
import pytest
from harbor_client import HarborClient, validate_project_config

class TestProjectPolicies:
    """Unit tests for Harbor project configuration."""

    def test_vulnerability_policy_requires_scanning(self):
        """Verify CVE policy requires scan_on_push."""
        config = {
            "prevent_vulnerable": True,
            "severity": "high",
            "scan_on_push": False  # Invalid combination
        }

        result = validate_project_config(config)
        assert result["valid"] == False
        assert "scan_on_push required" in result["errors"]

    def test_content_trust_requires_notary(self):
        """Verify content trust needs Notary configured."""
        config = {
            "enable_content_trust": True,
            "notary_url": None
        }

        result = validate_project_config(config)
        assert result["valid"] == False

    def test_retention_policy_validation(self):
        """Verify retention rules are valid."""
        policy = {
            "rules": [{
                "template": "latestPushedK",
                "params": {"latestPushedK": -1}  # Invalid
            }]
        }

        result = validate_retention_policy(policy)
        assert result["valid"] == False


class TestRobotAccounts:
    """Test robot account permission validation."""

    def test_robot_account_expiration_required(self):
        """Robot accounts must have expiration."""
        robot = {
            "name": "ci-pipeline",
            "duration": 0,  # Never expires - bad
            "permissions": [{"resource": "repository", "action": "push"}]
        }

        result = validate_robot_account(robot)
        assert result["valid"] == False
        assert "expiration required" in result["errors"]

    def test_robot_account_max_duration(self):
        """Robot account max duration is 90 days."""
        robot = {
            "name": "ci-pipeline",
            "duration": 365,  # Too long
            "permissions": [{"resource": "repository", "action": "push"}]
        }

        result = validate_robot_account(robot)
        assert result["valid"] == False
        assert "max duration 90 days" in result["errors"]
```

## Integration Testing with Harbor API

```python
# tests/integration/test_harbor_api.py
import pytest
import os
from harbor_client import HarborClient

@pytest.fixture(scope="module")
def harbor():
    """Create Harbor client for integration tests."""
    return HarborClient(
        url=os.getenv("HARBOR_URL", "https://harbor.example.com"),
        username=os.getenv("HARBOR_USER", "admin"),
        password=os.getenv("HARBOR_PASSWORD")
    )

class TestHarborAPIIntegration:
    """Integration tests against live Harbor instance."""

    def test_health_check(self, harbor):
        """Verify Harbor API is accessible."""
        result = harbor.health()
        assert result.status_code == 200
        assert result.json()["status"] == "healthy"

    def test_scanner_configured(self, harbor):
        """Verify Trivy scanner is default."""
        scanners = harbor.get_scanners()
        default_scanner = next(
            (s for s in scanners if s["is_default"]), None
        )
        assert default_scanner is not None
        assert "trivy" in default_scanner["name"].lower()

    def test_project_security_defaults(self, harbor):
        """Verify projects have security settings."""
        # Create test project
        project = harbor.create_project({
            "project_name": "test-security-defaults",
            "public": False
        })

        # Verify security defaults applied
        metadata = harbor.get_project("test-security-defaults")["metadata"]
        assert metadata.get("enable_content_trust") == "true"
        assert metadata.get("prevent_vul") == "true"
        assert metadata.get("auto_scan") == "true"

        # Cleanup
        harbor.delete_project("test-security-defaults")

    def test_gc_schedule_exists(self, harbor):
        """Verify garbage collection is scheduled."""
        schedule = harbor.get_gc_schedule()
        assert schedule["schedule"]["type"] in ["Weekly", "Daily", "Custom"]
        assert schedule["parameters"]["delete_untagged"] == True


class TestReplicationPolicies:
    """Test replication policy configurations."""

    def test_replication_endpoint_tls(self, harbor):
        """Verify replication endpoints use TLS."""
        endpoints = harbor.get_registries()
        for endpoint in endpoints:
            assert endpoint["url"].startswith("https://")
            assert endpoint["insecure"] == False

    def test_replication_has_filters(self, harbor):
        """Verify replication policies have filters."""
        policies = harbor.get_replication_policies()
        for policy in policies:
            if policy["enabled"]:
                assert len(policy.get("filters", [])) > 0, \
                    f"Policy {policy['name']} has no filters"
```

## End-to-End Testing

```bash
#!/bin/bash
# tests/e2e/test_harbor_workflow.sh

set -e

HARBOR_URL="${HARBOR_URL:-https://harbor.example.com}"
PROJECT="e2e-test-$(date +%s)"

echo "=== Harbor E2E Test Suite ==="

# Test 1: Create project with security defaults
echo "Test 1: Creating project with security defaults..."
curl -s -X POST "${HARBOR_URL}/api/v2.0/projects" \
  -u "${HARBOR_USER}:${HARBOR_PASSWORD}" \
  -H "Content-Type: application/json" \
  -d "{\"project_name\": \"${PROJECT}\", \"public\": false}" \
  -o /dev/null -w "%{http_code}" | grep -q "201"
echo "✓ Project created"

# Test 2: Verify security policies applied
echo "Test 2: Verifying security policies..."
METADATA=$(curl -s "${HARBOR_URL}/api/v2.0/projects/${PROJECT}" \
  -u "${HARBOR_USER}:${HARBOR_PASSWORD}" | jq '.metadata')

echo "$METADATA" | jq -e '.auto_scan == "true"' > /dev/null
echo "✓ Auto scan enabled"

echo "$METADATA" | jq -e '.prevent_vul == "true"' > /dev/null
echo "✓ Vulnerability prevention enabled"

# Test 3: Push and scan image
echo "Test 3: Pushing and scanning image..."
docker pull alpine:latest
docker tag alpine:latest "${HARBOR_URL}/${PROJECT}/alpine:test"
docker push "${HARBOR_URL}/${PROJECT}/alpine:test"

# Wait for scan
sleep 30

SCAN_STATUS=$(curl -s "${HARBOR_URL}/api/v2.0/projects/${PROJECT}/repositories/alpine/artifacts/test" \
  -u "${HARBOR_USER}:${HARBOR_PASSWORD}" | jq -r '.scan_overview.scan_status')

[ "$SCAN_STATUS" == "Success" ]
echo "✓ Image scanned successfully"

# Test 4: Create robot account
echo "Test 4: Creating robot account..."
ROBOT=$(curl -s -X POST "${HARBOR_URL}/api/v2.0/projects/${PROJECT}/robots" \
  -u "${HARBOR_USER}:${HARBOR_PASSWORD}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "e2e-test",
    "duration": 1,
    "permissions": [{"namespace": "'${PROJECT}'", "access": [{"resource": "repository", "action": "pull"}]}]
  }')

echo "$ROBOT" | jq -e '.secret' > /dev/null
echo "✓ Robot account created"

# Cleanup
echo "Cleaning up..."
curl -s -X DELETE "${HARBOR_URL}/api/v2.0/projects/${PROJECT}" \
  -u "${HARBOR_USER}:${HARBOR_PASSWORD}"
echo "✓ Cleanup complete"

echo "=== All E2E tests passed ==="
```

## Running Tests

```bash
# Run unit tests
pytest tests/test_harbor_policies.py -v

# Run integration tests (requires HARBOR_URL, HARBOR_USER, HARBOR_PASSWORD)
pytest tests/integration/ -v --tb=short

# Run E2E tests
./tests/e2e/test_harbor_workflow.sh

# Run all tests with coverage
pytest tests/ --cov=harbor_client --cov-report=html

# Specific test markers
pytest -m "not integration"  # Skip integration tests
pytest -m "security"         # Run only security tests
```
