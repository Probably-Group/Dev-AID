"""
Authentication Detection Module

Detects existing session-based authentication from CLI tools and
provides unified interface for both session auth and API keys.
"""

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class AuthCredentials:
    """Unified authentication credentials"""

    provider: str  # "claude", "gemini", "openai"
    auth_type: str  # "session", "api_key", "adc"
    credentials: Dict[str, Any]  # Provider-specific auth data
    source: str  # Where auth was found (e.g., "~/.config/claude/config.json")


class AuthDetector:
    """Detect and manage authentication across multiple providers"""

    def __init__(self):
        self.home = Path.home()

    def detect_all(self) -> Dict[str, Optional[AuthCredentials]]:
        """
        Detect authentication for all providers

        Returns:
            Dict mapping provider name to AuthCredentials (or None if not found)
        """
        return {
            "claude": self.detect_claude_auth(),
            "gemini": self.detect_gemini_auth(),
            "openai": self.detect_openai_auth(),
        }

    def detect_claude_auth(self) -> Optional[AuthCredentials]:
        """
        Detect Claude CLI session authentication

        Claude Code CLI stores session data in:
        - macOS/Linux: ~/.config/claude/config.json or ~/.claude/settings.json
        - Windows: %APPDATA%\\claude\\config.json

        Returns:
            AuthCredentials if session found, None otherwise
        """
        # Try standard Claude config locations
        config_paths = [
            self.home / ".config" / "claude" / "config.json",  # Linux/macOS standard
            self.home / "AppData" / "Roaming" / "claude" / "config.json",  # Windows
            self.home / ".claude" / "config.json",  # Alternative location
            self.home / ".claude" / "settings.json",  # Claude Code alternative
        ]

        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path) as f:
                        config = json.load(f)

                    # Extract session token (structure may vary by CLI version)
                    # Try multiple possible key names
                    session_token = (
                        config.get("sessionToken")
                        or config.get("session_token")
                        or config.get("sessionKey")
                        or config.get("session_key")
                    )

                    if session_token:
                        logger.info(f"Found Claude session auth at: {config_path}")
                        return AuthCredentials(
                            provider="claude",
                            auth_type="session",
                            credentials={"session_token": session_token},
                            source=str(config_path),
                        )
                except Exception as e:
                    logger.warning(f"Failed to read Claude config at {config_path}: {e}")
                    continue

        # Try keychain/keyring (macOS/Windows)
        if KEYRING_AVAILABLE:
            session_token = self._try_keyring_claude()
            if session_token:
                logger.info("Found Claude session token in system keychain")
                return AuthCredentials(
                    provider="claude",
                    auth_type="session",
                    credentials={"session_token": session_token},
                    source="system keychain (keyring)",
                )

        # Try API key as fallback
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            logger.info("Using Claude API key from environment")
            return AuthCredentials(
                provider="claude",
                auth_type="api_key",
                credentials={"api_key": api_key},
                source="ANTHROPIC_API_KEY environment variable",
            )

        logger.warning("No Claude authentication found (neither session nor API key)")
        return None

    def detect_gemini_auth(self) -> Optional[AuthCredentials]:
        """
        Detect Google/Gemini authentication

        Priority:
        1. Application Default Credentials (ADC) from gcloud CLI
        2. GOOGLE_API_KEY environment variable

        ADC locations:
        - macOS/Linux: ~/.config/gcloud/application_default_credentials.json
        - Windows: %APPDATA%\\gcloud\\application_default_credentials.json

        Returns:
            AuthCredentials if auth found, None otherwise
        """
        # Try ADC (Application Default Credentials)
        adc_paths = [
            self.home / ".config" / "gcloud" / "application_default_credentials.json",
            self.home / "AppData" / "Roaming" / "gcloud" / "application_default_credentials.json",
        ]

        for adc_path in adc_paths:
            if adc_path.exists():
                try:
                    with open(adc_path) as f:
                        adc_config = json.load(f)

                    # ADC file contains refresh token or service account credentials
                    if adc_config.get("type") or adc_config.get("refresh_token"):
                        logger.info(f"Found Google ADC at: {adc_path}")
                        return AuthCredentials(
                            provider="gemini",
                            auth_type="adc",
                            credentials={"adc_path": str(adc_path)},
                            source=str(adc_path),
                        )
                except Exception as e:
                    logger.warning(f"Failed to read Google ADC at {adc_path}: {e}")
                    continue

        # Try API key as fallback
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            logger.info("Using Google API key from environment")
            return AuthCredentials(
                provider="gemini",
                auth_type="api_key",
                credentials={"api_key": api_key},
                source="GOOGLE_API_KEY environment variable",
            )

        logger.warning("No Google/Gemini authentication found (neither ADC nor API key)")
        return None

    def detect_openai_auth(self) -> Optional[AuthCredentials]:
        """
        Detect OpenAI authentication

        Note: OpenAI is API-key only. ChatGPT Plus subscription does NOT
        provide API access. Users must purchase separate API credits.

        Returns:
            AuthCredentials if API key found, None otherwise
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            logger.info("Using OpenAI API key from environment")
            return AuthCredentials(
                provider="openai",
                auth_type="api_key",
                credentials={"api_key": api_key},
                source="OPENAI_API_KEY environment variable",
            )

        logger.warning(
            "No OpenAI API key found. "
            "Note: ChatGPT Plus does NOT include API access. "
            "Purchase API credits at: https://platform.openai.com/"
        )
        return None

    def _try_keyring_claude(self) -> Optional[str]:
        """
        Try to retrieve Claude session token from system keychain

        Claude Code may store session tokens in:
        - macOS: Keychain Access
        - Windows: Windows Credential Manager
        - Linux: Secret Service API (GNOME Keyring, KWallet, etc.)

        Returns:
            Session token if found, None otherwise
        """
        if not KEYRING_AVAILABLE:
            return None

        # Try common service/username combinations for Claude Code
        keyring_attempts = [
            ("claude-code", "session_token"),
            ("claude-code", "sessionToken"),
            ("claude", "session_token"),
            ("claude", "sessionToken"),
            ("anthropic", "session_token"),
            ("anthropic-claude", "session"),
            # Claude Code might use email or username as account
            ("claude-code", os.getenv("USER", "default")),
            ("claude-code", os.getenv("USERNAME", "default")),
        ]

        for service, username in keyring_attempts:
            try:
                token = keyring.get_password(service, username)
                if token and len(token) > 10:  # Basic sanity check
                    logger.debug(f"Found potential Claude token in keychain: service={service}, username={username}")
                    return token
            except Exception as e:
                # Keyring errors are common and not critical
                logger.debug(f"Keyring lookup failed for {service}/{username}: {e}")
                continue

        return None
