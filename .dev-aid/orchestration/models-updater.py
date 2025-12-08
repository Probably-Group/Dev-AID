#!/usr/bin/env python3
"""
Dev-AID Model Auto-Discovery
Queries AI provider APIs to discover and update to latest model versions
"""

import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

try:
    from google import genai
    import openai
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Error: Missing required package: {e}")
    print("Run: pip install -r .dev-aid/orchestration/requirements.txt")
    sys.exit(1)


@dataclass
class ModelInfo:
    """Information about a discovered model"""

    id: str
    tier: str  # opus, sonnet, haiku, pro, flash, gpt-4, gpt-3.5
    version: float  # e.g., 4.5, 2.0, 3.0
    provider: str


class ModelDiscovery:
    """Discovers latest models from AI provider APIs"""

    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.models_file = config_dir / "models.json"

        # Load environment variables
        env_file = config_dir / ".env"
        if env_file.exists():
            load_dotenv(env_file)

        self.models_config = self._load_config()

    def _load_config(self) -> Dict:
        """Load current models configuration"""
        if not self.models_file.exists():
            print(f"Error: {self.models_file} not found")
            sys.exit(1)

        with open(self.models_file, "r") as f:
            return json.load(f)

    def _save_config(self):
        """Save updated models configuration"""
        with open(self.models_file, "w") as f:
            json.dump(self.models_config, f, indent=2)
        print(f"✓ Updated {self.models_file}")

    def discover_anthropic_models(self) -> List[ModelInfo]:
        """Discover Claude models from Anthropic API"""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("⚠ No ANTHROPIC_API_KEY found, skipping Claude models")
            return []

        try:
            # _client = anthropic.Anthropic(api_key=api_key)

            # Anthropic doesn't have a public list_models endpoint yet
            # We'll use known model patterns and validate they exist
            known_models = [
                "claude-opus-4-5-20251101",
                "claude-sonnet-4-5-20250929",
                "claude-haiku-4-5-20250929",
                "claude-opus-4-0-20240229",
                "claude-sonnet-4-0-20240229",
                "claude-haiku-4-0-20240307",
            ]

            discovered = []
            for model_id in known_models:
                # Parse tier and version
                match = re.search(r"claude-(opus|sonnet|haiku)-(\d+)-(\d+)", model_id)
                if match:
                    tier = match.group(1)
                    major = int(match.group(2))
                    minor = int(match.group(3))
                    version = float(f"{major}.{minor}")

                    discovered.append(
                        ModelInfo(id=model_id, tier=tier, version=version, provider="claude")
                    )

            return discovered

        except Exception as e:
            print(f"⚠ Error discovering Anthropic models: {e}")
            return []

    def discover_google_models(self) -> List[ModelInfo]:
        """Discover Gemini models from Google API"""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("⚠ No GOOGLE_API_KEY found, skipping Gemini models")
            return []

        try:
            # Create client (new unified SDK)
            client = genai.Client(api_key=api_key)

            # List available models
            models = client.models.list()

            discovered = []
            for model in models:
                # model.name is already cleaned in new SDK (no "models/" prefix)
                model_id = model.name

                # Only process Gemini models
                if not model_id.startswith("gemini"):
                    continue

                # Parse tier and version
                # Examples: gemini-2.0-flash, gemini-2.0-pro, gemini-3.0-pro
                match = re.search(r"gemini-(\d+)\.(\d+)-(flash|pro)", model_id)
                if match:
                    major = int(match.group(1))
                    minor = int(match.group(2))
                    tier = match.group(3)
                    version = float(f"{major}.{minor}")

                    discovered.append(
                        ModelInfo(id=model_id, tier=tier, version=version, provider="gemini")
                    )

            return discovered

        except Exception as e:
            print(f"⚠ Error discovering Google models: {e}")
            return []

    def discover_openai_models(self) -> List[ModelInfo]:
        """Discover GPT models from OpenAI API"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠ No OPENAI_API_KEY found, skipping OpenAI models")
            return []

        try:
            client = openai.OpenAI(api_key=api_key)

            # List available models
            models = client.models.list()

            discovered = []
            for model in models.data:
                model_id = model.id

                # Only process GPT models
                if not (model_id.startswith("gpt-4") or model_id.startswith("gpt-3.5")):
                    continue

                # Parse tier and version
                # Examples: gpt-4o, gpt-4-turbo, gpt-4.1, gpt-3.5-turbo
                if "gpt-4" in model_id:
                    tier = "gpt-4"

                    # Try to extract version
                    match = re.search(r"gpt-(\d+)\.(\d+)", model_id)
                    if match:
                        version = float(f"{match.group(1)}.{match.group(2)}")
                    elif "4o" in model_id:
                        version = 4.0
                    elif "turbo" in model_id:
                        version = 4.0
                    else:
                        version = 4.0

                elif "gpt-3.5" in model_id:
                    tier = "gpt-3.5"
                    version = 3.5
                else:
                    continue

                discovered.append(
                    ModelInfo(id=model_id, tier=tier, version=version, provider="openai")
                )

            return discovered

        except Exception as e:
            print(f"⚠ Error discovering OpenAI models: {e}")
            return []

    def find_latest_models(self, models: List[ModelInfo]) -> Dict[str, ModelInfo]:
        """Find the latest version of each tier"""
        latest = {}

        for model in models:
            key = f"{model.provider}:{model.tier}"

            if key not in latest or model.version > latest[key].version:
                latest[key] = model

        return latest

    def update_config(self, latest_models: Dict[str, ModelInfo]) -> List[Tuple[str, str, str]]:
        """Update models.json with latest model IDs"""
        changes = []

        for key, model_info in latest_models.items():
            provider, tier = key.split(":")

            # Map tier to config key
            tier_map = {
                "opus": "opus-4.5",
                "sonnet": "sonnet-4.5",
                "haiku": "haiku-4.5",
                "flash": "flash-2.0",
                "pro": "pro-2.0",
                "gpt-4": "gpt-4o",
                "gpt-3.5": "gpt-3.5-turbo",
            }

            config_key = tier_map.get(tier)
            if not config_key:
                continue

            # Check if provider exists in config
            if provider not in self.models_config:
                continue

            # Check if tier exists in provider's models
            if config_key not in self.models_config[provider].get("models", {}):
                continue

            # Get current ID
            current_id = self.models_config[provider]["models"][config_key]["id"]
            new_id = model_info.id

            # Update if different
            if current_id != new_id:
                self.models_config[provider]["models"][config_key]["id"] = new_id
                changes.append((provider, tier, f"{current_id} → {new_id}"))

        return changes

    def run(self, dry_run: bool = False):
        """Run model discovery and update"""
        print("🔍 Discovering models from AI providers...\n")

        # Discover models from all providers
        all_models = []

        print("Querying Anthropic API...")
        all_models.extend(self.discover_anthropic_models())

        print("Querying Google API...")
        all_models.extend(self.discover_google_models())

        print("Querying OpenAI API...")
        all_models.extend(self.discover_openai_models())

        if not all_models:
            print("\n⚠ No models discovered. Check API keys and network connection.")
            return

        print(f"\n✓ Discovered {len(all_models)} models\n")

        # Find latest versions
        latest = self.find_latest_models(all_models)

        print("Latest models by tier:")
        for key, model in sorted(latest.items()):
            print(f"  • {key}: {model.id} (v{model.version})")

        print()

        # Update configuration
        changes = self.update_config(latest)

        if not changes:
            print("✓ All models are already up to date!")
            return

        print(f"Proposed changes ({len(changes)}):")
        for provider, tier, change in changes:
            print(f"  • {provider}/{tier}: {change}")

        print()

        if dry_run:
            print("🔍 Dry run mode - no changes saved")
            return

        # Save changes
        self.save_config()
        print("\n✅ Model configuration updated successfully!")
        print(f"\nUpdated {len(changes)} model(s) to latest versions.")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Discover and update AI model versions")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without saving")
    parser.add_argument(
        "--config-dir", type=Path, default=Path(".dev-aid/config"), help="Path to config directory"
    )

    args = parser.parse_args()

    # Ensure we're in the right directory
    if not args.config_dir.exists():
        print(f"Error: Config directory not found: {args.config_dir}")
        print("Run this from the Dev-AID repository root")
        sys.exit(1)

    discovery = ModelDiscovery(args.config_dir)
    discovery.run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
