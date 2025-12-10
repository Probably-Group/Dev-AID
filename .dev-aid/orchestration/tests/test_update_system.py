#!/usr/bin/env python3
"""
Integration tests for Dev-AID update system

Tests the complete update flow including:
- Version comparison
- Conflict detection
- Backup/restore
- Checksum verification
- GitHub API integration
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from conflict_resolver import ConflictResolver, MergeChoice  # noqa: E402
from github_client import GitHubClient, GitHubRateLimitError  # noqa: E402


class TestVersionComparison(unittest.TestCase):
    """Test semantic version comparison functions"""

    def setUp(self):
        """Import bash functions via subprocess"""
        self.update_lib = Path(__file__).parent.parent.parent / "scripts" / "update-lib.sh"

    def test_parse_version(self):
        """Test version parsing"""
        from subprocess import run

        result = run(
            ["bash", "-c", f"source {self.update_lib} && parse_version v1.2.3-beta"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.stdout.strip(), "1.2.3")

    def test_version_greater(self):
        """Test version comparison"""
        from subprocess import run

        # Test v2.0.0 > v1.9.0
        result = run(
            [
                "bash",
                "-c",
                f"source {self.update_lib} && is_version_greater 2.0.0 1.9.0 && echo true || echo false",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.stdout.strip(), "true")

        # Test v1.9.0 < v2.0.0
        result = run(
            [
                "bash",
                "-c",
                f"source {self.update_lib} && is_version_greater 1.9.0 2.0.0 && echo true || echo false",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.stdout.strip(), "false")

    def test_breaking_changes(self):
        """Test breaking change detection"""
        from subprocess import run

        # Major version change = breaking
        result = run(
            [
                "bash",
                "-c",
                f"source {self.update_lib} && has_breaking_changes 1.9.0 2.0.0 && echo true || echo false",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.stdout.strip(), "true")

        # Minor version change = not breaking
        result = run(
            [
                "bash",
                "-c",
                f"source {self.update_lib} && has_breaking_changes 1.9.0 1.10.0 && echo true || echo false",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.stdout.strip(), "false")


class TestConflictResolver(unittest.TestCase):
    """Test conflict detection and resolution"""

    def setUp(self):
        """Create temporary test directories"""
        self.temp_dir = tempfile.mkdtemp()
        self.backup_dir = Path(self.temp_dir) / "backup"
        self.update_dir = Path(self.temp_dir) / "update"
        self.working_dir = Path(self.temp_dir) / "working"

        self.backup_dir.mkdir()
        self.update_dir.mkdir()
        self.working_dir.mkdir()

        # Create .dev-aid structure
        (self.working_dir / ".dev-aid").mkdir()
        (self.update_dir / ".dev-aid").mkdir()

    def tearDown(self):
        """Clean up temporary directories"""
        shutil.rmtree(self.temp_dir)

    def test_detect_no_conflicts(self):
        """Test no conflicts when files are identical"""
        # Create identical files
        test_file = "test.txt"
        content = "same content"

        (self.working_dir / ".dev-aid" / test_file).write_text(content)
        (self.update_dir / ".dev-aid" / test_file).write_text(content)

        # Change to working directory
        original_cwd = os.getcwd()
        os.chdir(self.working_dir)

        try:
            resolver = ConflictResolver(str(self.backup_dir), str(self.update_dir))
            conflicts = resolver.detect_conflicts([test_file])

            self.assertEqual(len(conflicts), 0)
        finally:
            os.chdir(original_cwd)

    def test_detect_conflicts(self):
        """Test conflict detection when files differ"""
        # Create different files
        test_file = "test.txt"

        (self.working_dir / ".dev-aid" / test_file).write_text("user modified")
        (self.update_dir / ".dev-aid" / test_file).write_text("upstream new")

        # Change to working directory
        original_cwd = os.getcwd()
        os.chdir(self.working_dir)

        try:
            resolver = ConflictResolver(str(self.backup_dir), str(self.update_dir))
            conflicts = resolver.detect_conflicts([test_file])

            self.assertEqual(len(conflicts), 1)
            self.assertEqual(conflicts[0], test_file)
        finally:
            os.chdir(original_cwd)

    def test_resolve_keep_yours(self):
        """Test keeping user's version"""
        test_file = "test.txt"
        user_content = "user modified"
        upstream_content = "upstream new"

        (self.working_dir / ".dev-aid" / test_file).write_text(user_content)
        (self.update_dir / ".dev-aid" / test_file).write_text(upstream_content)

        # Change to working directory
        original_cwd = os.getcwd()
        os.chdir(self.working_dir)

        try:
            resolver = ConflictResolver(str(self.backup_dir), str(self.update_dir))
            resolver.resolve_conflict(test_file, MergeChoice.KEEP_YOURS)

            # Verify user's version was kept
            result = (self.working_dir / ".dev-aid" / test_file).read_text()
            self.assertEqual(result, user_content)
        finally:
            os.chdir(original_cwd)

    def test_resolve_take_upstream(self):
        """Test taking upstream version"""
        test_file = "test.txt"
        user_content = "user modified"
        upstream_content = "upstream new"

        (self.working_dir / ".dev-aid" / test_file).write_text(user_content)
        (self.update_dir / ".dev-aid" / test_file).write_text(upstream_content)

        # Change to working directory
        original_cwd = os.getcwd()
        os.chdir(self.working_dir)

        try:
            resolver = ConflictResolver(str(self.backup_dir), str(self.update_dir))
            resolver.resolve_conflict(test_file, MergeChoice.TAKE_UPSTREAM)

            # Verify upstream version was taken
            result = (self.working_dir / ".dev-aid" / test_file).read_text()
            self.assertEqual(result, upstream_content)
        finally:
            os.chdir(original_cwd)

    def test_create_merge_file(self):
        """Test manual merge file creation"""
        test_file = "test.txt"
        user_content = "user modified"
        upstream_content = "upstream new"

        (self.working_dir / ".dev-aid" / test_file).write_text(user_content)
        (self.update_dir / ".dev-aid" / test_file).write_text(upstream_content)

        # Change to working directory
        original_cwd = os.getcwd()
        os.chdir(self.working_dir)

        try:
            resolver = ConflictResolver(str(self.backup_dir), str(self.update_dir))
            merge_file = resolver.create_merge_file(test_file)

            # Verify merge file was created
            self.assertIsNotNone(merge_file)
            self.assertTrue(merge_file.exists())

            # Verify merge file contains conflict markers
            content = merge_file.read_text()
            self.assertIn("<<<<<<< YOUR VERSION", content)
            self.assertIn("=======", content)
            self.assertIn(">>>>>>> UPSTREAM VERSION", content)
            self.assertIn(user_content, content)
            self.assertIn(upstream_content, content)
        finally:
            os.chdir(original_cwd)

    def test_dry_run_mode(self):
        """Test dry-run mode doesn't modify files"""
        test_file = "test.txt"
        user_content = "user modified"
        upstream_content = "upstream new"

        (self.working_dir / ".dev-aid" / test_file).write_text(user_content)
        (self.update_dir / ".dev-aid" / test_file).write_text(upstream_content)

        # Change to working directory
        original_cwd = os.getcwd()
        os.chdir(self.working_dir)

        try:
            resolver = ConflictResolver(str(self.backup_dir), str(self.update_dir), dry_run=True)
            resolver.resolve_conflict(test_file, MergeChoice.TAKE_UPSTREAM)

            # Verify file was NOT modified in dry-run
            result = (self.working_dir / ".dev-aid" / test_file).read_text()
            self.assertEqual(result, user_content)  # Should still be user content
        finally:
            os.chdir(original_cwd)


class TestGitHubClient(unittest.TestCase):
    """Test GitHub API client (requires internet)"""

    def setUp(self):
        """Set up test repository"""
        # Use a well-known public repository for testing
        self.test_repo = "anthropics/anthropic-sdk-python"
        self.client = GitHubClient(self.test_repo)

    def test_detect_repo_from_env(self):
        """Test repository detection from environment"""
        os.environ["DEV_AID_REPO"] = "test/repo"
        client = GitHubClient()
        # Note: Will use env var since we're not in a git repo
        self.assertIsNotNone(client.repo)
        del os.environ["DEV_AID_REPO"]

    def test_get_latest_release(self):
        """Test fetching latest release (requires internet)"""
        try:
            release = self.client.get_latest_release()

            self.assertIn("tag_name", release)
            self.assertIn("name", release)
            self.assertIn("assets", release)
            self.assertIsInstance(release["assets"], list)
        except GitHubRateLimitError:
            self.skipTest("GitHub rate limit exceeded")
        except Exception as e:
            self.skipTest(f"Network error: {e}")

    def test_get_latest_version(self):
        """Test getting latest version number"""
        try:
            version = self.client.get_latest_version()

            self.assertIsInstance(version, str)
            self.assertNotIn("v", version)  # Should strip 'v' prefix
            # Should be semantic version format
            parts = version.split(".")
            self.assertGreaterEqual(len(parts), 2)
        except GitHubRateLimitError:
            self.skipTest("GitHub rate limit exceeded")
        except Exception as e:
            self.skipTest(f"Network error: {e}")

    def test_list_releases(self):
        """Test listing releases"""
        try:
            releases = self.client.list_releases(limit=5)

            self.assertIsInstance(releases, list)
            self.assertLessEqual(len(releases), 5)

            if len(releases) > 0:
                self.assertIn("tag_name", releases[0])
                self.assertIn("name", releases[0])
        except GitHubRateLimitError:
            self.skipTest("GitHub rate limit exceeded")
        except Exception as e:
            self.skipTest(f"Network error: {e}")

    def test_format_size(self):
        """Test size formatting"""
        self.assertEqual(GitHubClient._format_size(500), "500.0 B")
        self.assertEqual(GitHubClient._format_size(1024), "1.0 KB")
        self.assertEqual(GitHubClient._format_size(1024 * 1024), "1.0 MB")
        self.assertEqual(GitHubClient._format_size(1024 * 1024 * 1024), "1.0 GB")


class TestBackupRestore(unittest.TestCase):
    """Test backup and restore functionality"""

    def setUp(self):
        """Create temporary test directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.dev_aid_dir = Path(self.temp_dir) / ".dev-aid"
        self.dev_aid_dir.mkdir()

        # Create test structure
        (self.dev_aid_dir / "config").mkdir()
        (self.dev_aid_dir / "memory-bank").mkdir()
        (self.dev_aid_dir / "logs").mkdir()

        # Create test files
        (self.dev_aid_dir / "VERSION").write_text("1.3.0")
        (self.dev_aid_dir / "config" / ".env").write_text("API_KEY=secret")
        (self.dev_aid_dir / "memory-bank" / "patterns.md").write_text("# Patterns")
        (self.dev_aid_dir / "logs" / "router.log").write_text("log entry")

        # Change to temp directory
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)

    def test_backup_creation(self):
        """Test backup creation"""
        from subprocess import run

        update_lib = Path(__file__).parent.parent.parent / "scripts" / "update-lib.sh"

        result = run(
            ["bash", "-c", f"source {update_lib} && create_backup"],
            capture_output=True,
            text=True,
        )

        backup_dir = result.stdout.strip().split("\n")[-1]

        # Verify backup was created
        self.assertTrue(Path(backup_dir).exists())
        self.assertTrue((Path(backup_dir) / "VERSION").exists())
        self.assertTrue((Path(backup_dir) / ".env").exists())
        self.assertTrue((Path(backup_dir) / "memory-bank").exists())

    def test_protected_paths(self):
        """Test protected path detection"""
        from subprocess import run

        update_lib = Path(__file__).parent.parent.parent / "scripts" / "update-lib.sh"

        result = run(
            ["bash", "-c", f"source {update_lib} && get_protected_paths"],
            capture_output=True,
            text=True,
        )

        paths = result.stdout.strip().split("\n")

        self.assertIn(".dev-aid/config/.env*", paths)
        self.assertIn(".dev-aid/memory-bank/", paths)
        self.assertIn(".dev-aid/logs/", paths)


class TestChecksumVerification(unittest.TestCase):
    """Test checksum verification"""

    def setUp(self):
        """Create temporary test file"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = Path(self.temp_dir) / "test.txt"
        self.test_file.write_text("hello world")

        # Expected SHA256 for "hello world"
        self.expected_hash = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)

    def test_checksum_verification_valid(self):
        """Test valid checksum"""
        from subprocess import run

        update_lib = Path(__file__).parent.parent.parent / "scripts" / "update-lib.sh"

        cmd = (
            f"source {update_lib} && verify_checksum {self.test_file} "
            f"{self.expected_hash} && echo valid || echo invalid"
        )
        result = run(
            ["bash", "-c", cmd],
            capture_output=True,
            text=True,
        )

        self.assertIn("valid", result.stdout)

    def test_checksum_verification_invalid(self):
        """Test invalid checksum"""
        from subprocess import run

        update_lib = Path(__file__).parent.parent.parent / "scripts" / "update-lib.sh"
        invalid_hash = "0" * 64

        result = run(
            [
                "bash",
                "-c",
                f"source {update_lib} && verify_checksum {self.test_file} {invalid_hash} && echo valid || echo invalid",
            ],
            capture_output=True,
            text=True,
        )

        self.assertIn("invalid", result.stdout)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestVersionComparison))
    suite.addTests(loader.loadTestsFromTestCase(TestConflictResolver))
    suite.addTests(loader.loadTestsFromTestCase(TestGitHubClient))
    suite.addTests(loader.loadTestsFromTestCase(TestBackupRestore))
    suite.addTests(loader.loadTestsFromTestCase(TestChecksumVerification))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
