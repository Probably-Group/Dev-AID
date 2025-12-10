#!/usr/bin/env python3
"""
GitHub API Client for Dev-AID Updates

Fetches release information, downloads assets, and retrieves checksums
from GitHub releases without requiring authentication.

Features:
- Fetch latest release metadata
- Download release assets
- Verify checksums (SHA256)
- Rate limit handling
- Timeout protection

Usage:
    python3 github_client.py get-latest-version
    python3 github_client.py download-asset dev-aid.tar.gz /tmp/dev-aid.tar.gz
    python3 github_client.py get-checksums

Environment Variables:
    GITHUB_TOKEN - Optional, increases rate limit from 60 to 5000 requests/hour
    DEV_AID_REPO - Override default repository (default: auto-detect from git remote)
"""

import json
import sys
import os
import time
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from typing import Dict, Optional, List


class Color:
    """ANSI color codes"""

    GREEN = "\033[0;32m"
    BLUE = "\033[0;34m"
    YELLOW = "\033[1;33m"
    RED = "\033[0;31m"
    NC = "\033[0m"


class GitHubRateLimitError(Exception):
    """Raised when GitHub API rate limit is exceeded"""

    pass


class GitHubClient:
    """GitHub API client for fetching Dev-AID releases"""

    def __init__(self, repo: Optional[str] = None):
        """
        Initialize GitHub client

        Args:
            repo: Repository in format "owner/repo". If None, auto-detect from git remote
        """
        self.repo = repo or self._detect_repo()
        self.api_base = f"https://api.github.com/repos/{self.repo}"
        self.token = os.getenv("GITHUB_TOKEN")

        # Rate limit tracking
        self.rate_limit_remaining = None
        self.rate_limit_reset = None

    def _detect_repo(self) -> str:
        """
        Auto-detect repository from git remote

        Returns:
            Repository in format "owner/repo"
        """
        try:
            import subprocess

            result = subprocess.run(
                ["git", "remote", "get-url", "origin"], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                url = result.stdout.strip()

                # Parse GitHub URL
                # https://github.com/owner/repo.git -> owner/repo
                # git@github.com:owner/repo.git -> owner/repo
                if "github.com" in url:
                    if url.startswith("https://"):
                        parts = url.replace("https://github.com/", "").replace(".git", "")
                    elif url.startswith("git@"):
                        parts = url.replace("git@github.com:", "").replace(".git", "")
                    else:
                        parts = url

                    return parts

        except Exception:
            pass

        # Fallback to environment variable or error
        repo = os.getenv("DEV_AID_REPO")
        if not repo:
            print(f"{Color.RED}❌ Could not detect repository{Color.NC}", file=sys.stderr)
            print(
                "   Set DEV_AID_REPO environment variable or run from git repository",
                file=sys.stderr,
            )
            sys.exit(1)

        return repo

    def _make_request(self, url: str, timeout: int = 10) -> dict:
        """
        Make authenticated GitHub API request

        Args:
            url: API endpoint URL
            timeout: Request timeout in seconds

        Returns:
            Parsed JSON response

        Raises:
            GitHubRateLimitError: If rate limit exceeded
            HTTPError: On HTTP errors
            URLError: On network errors
        """
        req = Request(url)
        req.add_header("Accept", "application/vnd.github.v3+json")

        # Add authentication if token available
        if self.token:
            req.add_header("Authorization", f"token {self.token}")

        try:
            with urlopen(req, timeout=timeout) as response:
                # Track rate limit
                self.rate_limit_remaining = response.headers.get("X-RateLimit-Remaining")
                self.rate_limit_reset = response.headers.get("X-RateLimit-Reset")

                data = json.loads(response.read())
                return data

        except HTTPError as e:
            if e.code == 403 and "rate limit" in e.reason.lower():
                reset_time = int(self.rate_limit_reset) if self.rate_limit_reset else 0
                wait_time = max(0, reset_time - int(time.time()))

                raise GitHubRateLimitError(
                    f"GitHub API rate limit exceeded. Reset in {wait_time} seconds. "
                    f"Set GITHUB_TOKEN environment variable for higher limits."
                )
            elif e.code == 404:
                print(f"{Color.RED}❌ Repository not found: {self.repo}{Color.NC}", file=sys.stderr)
                print("   Check DEV_AID_REPO environment variable", file=sys.stderr)
                sys.exit(1)
            else:
                print(
                    f"{Color.RED}❌ GitHub API error: {e.code} {e.reason}{Color.NC}",
                    file=sys.stderr,
                )
                raise

        except URLError as e:
            print(f"{Color.RED}❌ Network error: {e}{Color.NC}", file=sys.stderr)
            sys.exit(1)

    def get_latest_release(self) -> dict:
        """
        Fetch latest release metadata

        Returns:
            Release metadata dictionary containing:
            - tag_name: Version tag (e.g., "v1.4.0")
            - name: Release name
            - body: Release notes
            - assets: List of downloadable files
            - published_at: Release date
        """
        url = f"{self.api_base}/releases/latest"
        return self._make_request(url)

    def get_release_by_tag(self, tag: str) -> dict:
        """
        Fetch specific release by tag

        Args:
            tag: Version tag (e.g., "v1.4.0")

        Returns:
            Release metadata dictionary
        """
        url = f"{self.api_base}/releases/tags/{tag}"
        return self._make_request(url)

    def get_latest_version(self) -> str:
        """
        Get latest version number (without 'v' prefix)

        Returns:
            Version string (e.g., "1.4.0")
        """
        release = self.get_latest_release()
        return release["tag_name"].lstrip("v")

    def list_releases(self, limit: int = 10) -> List[dict]:
        """
        List recent releases

        Args:
            limit: Maximum number of releases to return

        Returns:
            List of release metadata dictionaries
        """
        url = f"{self.api_base}/releases?per_page={limit}"
        return self._make_request(url)

    def download_asset(
        self, asset_name: str, output_path: Path, show_progress: bool = True
    ) -> None:
        """
        Download a specific release asset

        Args:
            asset_name: Name of the asset to download
            output_path: Where to save the downloaded file
            show_progress: Whether to show download progress

        Raises:
            FileNotFoundError: If asset not found in release
        """
        release = self.get_latest_release()

        # Find asset
        asset = next((a for a in release["assets"] if a["name"] == asset_name), None)

        if not asset:
            available = [a["name"] for a in release["assets"]]
            print(f"{Color.RED}❌ Asset not found: {asset_name}{Color.NC}", file=sys.stderr)
            print(f"Available assets: {', '.join(available)}", file=sys.stderr)
            raise FileNotFoundError(f"Asset not found: {asset_name}")

        url = asset["browser_download_url"]
        size = asset["size"]

        if show_progress:
            print(
                f"{Color.BLUE}📥 Downloading {asset_name} ({self._format_size(size)})...{Color.NC}"
            )

        # Download with progress
        req = Request(url)
        if self.token:
            req.add_header("Authorization", f"token {self.token}")

        try:
            with urlopen(req, timeout=300) as response:
                # Ensure parent directory exists
                output_path.parent.mkdir(parents=True, exist_ok=True)

                # Download in chunks with progress
                chunk_size = 8192
                downloaded = 0

                with open(output_path, "wb") as f:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break

                        f.write(chunk)
                        downloaded += len(chunk)

                        if show_progress and size > 0:
                            percent = (downloaded / size) * 100
                            self._show_progress(downloaded, size, percent)

            if show_progress:
                print(f"\n{Color.GREEN}✅ Downloaded to {output_path}{Color.NC}")

        except Exception as e:
            # Cleanup partial download
            if output_path.exists():
                output_path.unlink()

            print(f"{Color.RED}❌ Download failed: {e}{Color.NC}", file=sys.stderr)
            raise

    def get_checksums(self) -> Dict[str, str]:
        """
        Fetch SHA256 checksums for release assets

        Returns:
            Dictionary mapping filename to SHA256 checksum

        Note:
            Expects a checksums.txt or SHA256SUMS file in the release assets
        """
        release = self.get_latest_release()

        # Look for checksum files
        checksum_names = ["checksums.txt", "SHA256SUMS", "sha256sums.txt"]
        checksum_asset = None

        for name in checksum_names:
            checksum_asset = next((a for a in release["assets"] if a["name"] == name), None)
            if checksum_asset:
                break

        if not checksum_asset:
            print(f"{Color.YELLOW}⚠️  No checksum file found in release{Color.NC}", file=sys.stderr)
            return {}

        # Download and parse checksums
        url = checksum_asset["browser_download_url"]

        try:
            with urlopen(url, timeout=10) as response:
                content = response.read().decode("utf-8")
        except Exception as e:
            print(f"{Color.YELLOW}⚠️  Could not fetch checksums: {e}{Color.NC}", file=sys.stderr)
            return {}

        # Parse checksums (format: "HASH  filename" or "HASH *filename")
        checksums = {}
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue

            # Split on whitespace
            parts = line.split(None, 1)
            if len(parts) == 2:
                hash_val = parts[0]
                filename = parts[1].lstrip("*")  # Remove * from binary mode indicator
                checksums[filename] = hash_val

        return checksums

    def get_release_notes(self, version: Optional[str] = None) -> str:
        """
        Get release notes for a version

        Args:
            version: Version tag (e.g., "v1.4.0"). If None, uses latest

        Returns:
            Release notes markdown
        """
        if version:
            release = self.get_release_by_tag(version)
        else:
            release = self.get_latest_release()

        return release.get("body", "No release notes available")

    def check_rate_limit(self) -> dict:
        """
        Check current GitHub API rate limit status

        Returns:
            Dictionary with rate limit info
        """
        url = "https://api.github.com/rate_limit"
        data = self._make_request(url)

        core = data["resources"]["core"]
        return {
            "limit": core["limit"],
            "remaining": core["remaining"],
            "reset": core["reset"],
            "reset_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(core["reset"])),
        }

    @staticmethod
    def _format_size(bytes: int) -> str:
        """Format byte size as human-readable string"""
        for unit in ["B", "KB", "MB", "GB"]:
            if bytes < 1024.0:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.1f} TB"

    @staticmethod
    def _show_progress(downloaded: int, total: int, percent: float) -> None:
        """Show download progress bar"""
        bar_length = 50
        filled = int(bar_length * percent / 100)
        bar = "=" * filled + " " * (bar_length - filled)

        print(
            f"\r[{bar}] {percent:.1f}% ({GitHubClient._format_size(downloaded)}/{GitHubClient._format_size(total)})",
            end="",
            flush=True,
        )


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: github_client.py <command> [args]")
        print("")
        print("Commands:")
        print("  get-latest-version")
        print("  get-release-notes [version]")
        print("  list-releases [limit]")
        print("  download-asset <asset-name> <output-path>")
        print("  get-checksums")
        print("  check-rate-limit")
        print("")
        print("Environment Variables:")
        print("  GITHUB_TOKEN - Optional token for higher rate limits")
        print("  DEV_AID_REPO - Override repository (default: auto-detect)")
        print("")
        print("Examples:")
        print("  python3 github_client.py get-latest-version")
        print("  python3 github_client.py download-asset dev-aid.tar.gz /tmp/dev-aid.tar.gz")
        sys.exit(1)

    client = GitHubClient()
    command = sys.argv[1]

    try:
        if command == "get-latest-version":
            print(client.get_latest_version())

        elif command == "get-release-notes":
            version = sys.argv[2] if len(sys.argv) > 2 else None
            print(client.get_release_notes(version))

        elif command == "list-releases":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            releases = client.list_releases(limit)
            for release in releases:
                print(f"{release['tag_name']}: {release['name']}")

        elif command == "download-asset":
            if len(sys.argv) != 4:
                print("Usage: github_client.py download-asset <asset-name> <output-path>")
                sys.exit(1)
            asset_name = sys.argv[2]
            output_path = Path(sys.argv[3])
            client.download_asset(asset_name, output_path)

        elif command == "get-checksums":
            checksums = client.get_checksums()
            print(json.dumps(checksums, indent=2))

        elif command == "check-rate-limit":
            rate_limit = client.check_rate_limit()
            print(f"Rate Limit: {rate_limit['remaining']}/{rate_limit['limit']}")
            print(f"Resets at: {rate_limit['reset_time']}")

        else:
            print(f"{Color.RED}❌ Unknown command: {command}{Color.NC}")
            sys.exit(1)

    except GitHubRateLimitError as e:
        print(f"{Color.RED}{e}{Color.NC}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}Cancelled by user{Color.NC}")
        sys.exit(1)
    except Exception as e:
        print(f"{Color.RED}❌ Error: {e}{Color.NC}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
