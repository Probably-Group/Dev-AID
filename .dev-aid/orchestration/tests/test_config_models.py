"""Tests for config_models validation"""

from router.config_models import (
    MemoryBankConfig,
    RoutingConfig,
    SettingsConfig,
    validate_routing,
    validate_settings,
)


class TestSettingsConfig:
    """Tests for SettingsConfig model"""

    def test_defaults(self):
        """Test default values"""
        config = SettingsConfig()
        assert config.orchestration_mode == "solo"
        assert config.default_model == "claude-sonnet-4.5"
        assert config.enabled_providers == ["claude"]

    def test_valid_modes(self):
        """Test all valid orchestration modes"""
        for mode in ["solo", "ensemble", "challenger", "architect"]:
            config = SettingsConfig(orchestration_mode=mode)
            assert config.orchestration_mode == mode

    def test_invalid_mode(self):
        """Test invalid orchestration mode"""
        result = validate_settings({"orchestration_mode": "invalid_mode"})
        assert result is None

    def test_with_project_name(self):
        """Test with optional project name"""
        config = SettingsConfig(project_name="my-project")
        assert config.project_name == "my-project"

    def test_with_memory_bank(self):
        """Test with memory bank config"""
        config = SettingsConfig(memory_bank=MemoryBankConfig(auto_load=["file1.md", "file2.md"]))
        assert config.memory_bank is not None
        assert len(config.memory_bank.auto_load) == 2


class TestRoutingConfig:
    """Tests for RoutingConfig model"""

    def test_defaults(self):
        """Test default values"""
        config = RoutingConfig()
        assert config.cost_limit_per_day == 100.0
        assert len(config.fallback_chain) == 3

    def test_custom_cost_limit(self):
        """Test custom cost limit"""
        config = RoutingConfig(cost_limit_per_day=50.0)
        assert config.cost_limit_per_day == 50.0

    def test_negative_cost_rejected(self):
        """Test negative cost limit is rejected"""
        result = validate_routing({"cost_limit_per_day": -10.0})
        assert result is None

    def test_custom_fallback_chain(self):
        """Test custom fallback chain"""
        config = RoutingConfig(fallback_chain=["model-a", "model-b"])
        assert config.fallback_chain == ["model-a", "model-b"]

    def test_with_modes(self):
        """Test with modes config"""
        config = RoutingConfig(modes={"solo": {"model": "claude-sonnet"}})
        assert config.modes is not None
        assert "solo" in config.modes


class TestValidateHelpers:
    """Tests for validate_settings and validate_routing helpers"""

    def test_validate_settings_valid(self):
        """Test valid settings data"""
        result = validate_settings({"orchestration_mode": "ensemble"})
        assert result is not None
        assert result.orchestration_mode == "ensemble"

    def test_validate_settings_empty(self):
        """Test empty dict uses defaults"""
        result = validate_settings({})
        assert result is not None
        assert result.orchestration_mode == "solo"

    def test_validate_routing_valid(self):
        """Test valid routing data"""
        result = validate_routing({"cost_limit_per_day": 200.0})
        assert result is not None
        assert result.cost_limit_per_day == 200.0

    def test_validate_routing_empty(self):
        """Test empty dict uses defaults"""
        result = validate_routing({})
        assert result is not None
