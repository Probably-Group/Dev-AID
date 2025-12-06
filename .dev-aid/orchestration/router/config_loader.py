"""
Configuration Loader for Dev-AID Router

Loads and validates configuration from:
- .dev-aid/config/settings.json
- .dev-aid/config/routing.json
- .dev-aid/config/models.json
- .dev-aid/config/.env (API keys)
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv


class ConfigLoader:
    """Loads and provides access to Dev-AID configuration"""

    def __init__(self, dev_aid_root: Optional[Path] = None):
        """
        Initialize configuration loader

        Args:
            dev_aid_root: Root directory of Dev-AID (auto-detected if None)
        """
        if dev_aid_root is None:
            # Auto-detect: walk up from current directory
            dev_aid_root = self._find_dev_aid_root()

        self.root = Path(dev_aid_root)
        self.config_dir = self.root / ".dev-aid" / "config"

        # Load environment variables (API keys)
        env_file = self.config_dir / ".env"
        if env_file.exists():
            load_dotenv(env_file)

        # Load JSON configs
        self.settings = self._load_json("settings.json")
        self.routing = self._load_json("routing.json")
        self.models = self._load_json("models.json")
        self.orchestration = self._load_json("orchestration.json")

    def _find_dev_aid_root(self) -> Path:
        """Find Dev-AID root by looking for .dev-aid directory"""
        current = Path.cwd()

        # Check current directory and parents
        for path in [current] + list(current.parents):
            if (path / ".dev-aid").is_dir():
                return path

        # Fallback: current directory
        return current

    def _validate_safe_path(self, filepath: Path, base_dir: Path) -> Path:
        """
        Validate that filepath is safe and within base_dir

        Args:
            filepath: Path to validate
            base_dir: Base directory that filepath must be within

        Returns:
            Resolved safe path

        Raises:
            ValueError: If path is unsafe or traverses outside base_dir
        """
        try:
            # Resolve both paths
            resolved_file = filepath.resolve(strict=False)
            resolved_base = base_dir.resolve(strict=False)

            # Check containment
            if not str(resolved_file).startswith(str(resolved_base)):
                raise ValueError(f"Path traversal detected: {filepath} is outside {base_dir}")

            # Check for null bytes
            if "\0" in str(resolved_file):
                raise ValueError("Path contains null bytes")

            return resolved_file

        except (OSError, RuntimeError) as e:
            raise ValueError(f"Invalid path: {e}")

    def _load_json(self, filename: str) -> Dict[str, Any]:
        """Load and parse JSON configuration file"""
        # Validate filename doesn't contain traversal
        if ".." in filename or filename.startswith("/"):
            raise ValueError(f"Invalid filename: {filename}")

        filepath = self.config_dir / filename

        # Validate path is within config_dir
        safe_path = self._validate_safe_path(filepath, self.config_dir)

        if not safe_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {filename}\n"
                f"Make sure Dev-AID is properly initialized."
            )

        try:
            with open(safe_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse JSON
            data = json.loads(content)

            if not isinstance(data, dict):
                raise ValueError(f"Configuration must be a JSON object, got {type(data)}")

            return data

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {filename}. Please check your configuration file.")

    def get_orchestration_mode(self) -> str:
        """Get current orchestration mode (solo, ensemble, challenger)"""
        return self.settings.get("orchestration_mode", "solo")

    def get_default_model(self) -> str:
        """Get default model name"""
        return self.settings.get("default_model", "claude-sonnet-4.5")

    def get_enabled_providers(self) -> list[str]:
        """Get list of enabled providers"""
        return self.settings.get("enabled_providers", ["claude"])

    def is_provider_enabled(self, provider: str) -> bool:
        """Check if a provider is enabled"""
        return provider in self.get_enabled_providers()

    def get_model_config(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific model

        Args:
            model_name: Short name like "claude-sonnet" or full ID

        Returns:
            Model configuration dict or None if not found
        """
        # Check each provider
        for provider, config in self.models.items():
            if not isinstance(config, dict):
                continue

            models = config.get("models", {})

            # Check both short names and full IDs
            for short_name, model_config in models.items():
                if isinstance(model_config, dict):
                    model_id = model_config.get("id", "")
                    if model_name in [short_name, model_id, f"{provider}-{short_name}"]:
                        return {
                            "provider": provider,
                            "short_name": short_name,
                            "full_config": model_config,
                            **model_config,
                        }

        return None

    def get_api_key(self, provider: str) -> Optional[str]:
        """
        Get API key for a provider from environment

        Args:
            provider: Provider name (claude, gemini, openai)

        Returns:
            API key or None if not set
        """
        provider_config = self.models.get(provider, {})
        env_var = provider_config.get("api_key_env")

        if not env_var:
            return None

        return os.getenv(env_var)

    def validate_provider(self, provider: str) -> tuple[bool, str]:
        """
        Validate that a provider is properly configured

        Args:
            provider: Provider name

        Returns:
            (is_valid, error_message)
        """
        # Check if provider exists in models.json
        if provider not in self.models:
            return False, f"Provider '{provider}' not found in models.json"

        provider_config = self.models[provider]

        # Check if enabled
        if not provider_config.get("enabled", False):
            return False, f"Provider '{provider}' is not enabled in models.json"

        # Check if API key is set
        api_key = self.get_api_key(provider)
        if not api_key:
            env_var = provider_config.get("api_key_env", "UNKNOWN")
            return False, f"API key not set for '{provider}' (expected {env_var} in .env)"

        return True, ""

    def get_routing_config(self) -> Dict[str, Any]:
        """Get full routing configuration"""
        return self.routing

    def get_mode_config(self, mode: str) -> Dict[str, Any]:
        """Get configuration for a specific mode"""
        return self.routing.get("modes", {}).get(mode, {})

    def get_fallback_chain(self) -> list[str]:
        """Get fallback model chain"""
        return self.routing.get("fallback_chain", ["claude-sonnet", "gpt-4o", "gemini-flash"])

    def get_cost_limit(self) -> float:
        """Get daily cost limit"""
        return self.routing.get("cost_limit_per_day", 100.0)

    def get_memory_bank_files(self) -> list[str]:
        """Get list of memory bank files to auto-load"""
        memory_config = self.settings.get("memory_bank", {})
        return memory_config.get("auto_load", ["activeContext.md"])

    def get_memory_bank_path(self) -> Path:
        """Get path to memory bank directory"""
        return self.root / ".dev-aid" / "memory-bank"


def load_config(dev_aid_root: Optional[Path] = None) -> ConfigLoader:
    """
    Convenience function to load configuration

    Args:
        dev_aid_root: Root directory of Dev-AID (auto-detected if None)

    Returns:
        ConfigLoader instance

    Raises:
        FileNotFoundError: If configuration files not found
        ValueError: If configuration is invalid
    """
    return ConfigLoader(dev_aid_root)


# Example usage
if __name__ == "__main__":
    try:
        config = load_config()
        print(f"✅ Configuration loaded successfully")
        print(f"   Orchestration Mode: {config.get_orchestration_mode()}")
        print(f"   Default Model: {config.get_default_model()}")
        print(f"   Enabled Providers: {', '.join(config.get_enabled_providers())}")

        # Validate providers
        print(f"\n🔍 Provider Validation:")
        for provider in config.get_enabled_providers():
            is_valid, error = config.validate_provider(provider)
            if is_valid:
                print(f"   ✅ {provider}: Ready")
            else:
                print(f"   ❌ {provider}: {error}")

    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
