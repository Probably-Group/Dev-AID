"""
Pytest configuration and fixtures for Dev-AID Router tests
"""

import tempfile
from pathlib import Path
from typing import Dict, Any
import json
import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_dev_aid_root(temp_dir):
    """Create a mock Dev-AID directory structure"""
    root = temp_dir / "dev-aid-test"
    root.mkdir()

    # Create .dev-aid structure
    dev_aid_dir = root / ".dev-aid"
    config_dir = dev_aid_dir / "config"
    logs_dir = dev_aid_dir / "logs"
    memory_bank_dir = dev_aid_dir / "memory-bank"

    for d in [dev_aid_dir, config_dir, logs_dir, memory_bank_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Create mock configuration files
    settings = {
        "project_name": "test-project",
        "orchestration_mode": "solo",
        "default_model": "claude-sonnet",
        "enabled_providers": ["claude"],
        "memory_bank": {"auto_load": ["activeContext.md"]}
    }

    routing = {
        "modes": {
            "solo": {"enabled": True},
            "ensemble": {"enabled": True},
            "challenger": {"enabled": True}
        },
        "fallback_chain": ["claude-sonnet"],
        "cost_limit_per_day": 100.0
    }

    models = {
        "claude": {
            "enabled": True,
            "api_key_env": "ANTHROPIC_API_KEY",
            "models": {
                "claude-sonnet": {
                    "id": "claude-sonnet-4",
                    "cost_per_1m_tokens": {"input": 3.0, "output": 15.0}
                }
            }
        }
    }

    orchestration = {
        "default_mode": "solo"
    }

    # Write config files
    (config_dir / "settings.json").write_text(json.dumps(settings, indent=2))
    (config_dir / "routing.json").write_text(json.dumps(routing, indent=2))
    (config_dir / "models.json").write_text(json.dumps(models, indent=2))
    (config_dir / "orchestration.json").write_text(json.dumps(orchestration, indent=2))

    # Create .env file
    (config_dir / ".env").write_text("ANTHROPIC_API_KEY=test-key-12345")

    # Create memory bank file
    (memory_bank_dir / "activeContext.md").write_text("# Test Context\n\nTest content")

    yield root


@pytest.fixture
def mock_api_key():
    """Mock API key for testing"""
    return "test-api-key-1234567890"


@pytest.fixture
def mock_model_config() -> Dict[str, Any]:
    """Mock model configuration"""
    return {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4",
        "cost_per_1m_tokens": {
            "input": 3.0,
            "output": 15.0
        },
        "max_tokens": 4096,
        "temperature": 0.7
    }


@pytest.fixture
def sample_messages():
    """Sample messages for API testing"""
    from router.api_clients import Message
    return [
        Message(role="user", content="Hello, how are you?")
    ]
