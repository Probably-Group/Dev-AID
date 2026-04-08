"""Tests for security utilities"""

import os
import tempfile
from pathlib import Path

import pytest
from utils.security import safe_resolve_path, validate_directory_path


class TestSafeResolvePath:
    """Tests for safe_resolve_path"""

    def test_basic_relative_path(self, temp_dir):
        """Test resolving a basic relative path"""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")

        result = safe_resolve_path(temp_dir, "test.txt")
        assert result == test_file.resolve()

    def test_rejects_path_traversal(self, temp_dir):
        """Test that ../ traversal is rejected"""
        with pytest.raises(ValueError, match="Path traversal detected"):
            safe_resolve_path(temp_dir, "../etc/passwd")

    def test_rejects_absolute_path_outside_base(self, temp_dir):
        """Test that absolute paths outside base_dir are rejected"""
        with pytest.raises(ValueError, match="Path outside base directory"):
            safe_resolve_path(temp_dir, "/etc/passwd")

    def test_prefix_collision_rejected(self):
        """Test that prefix collisions are rejected (e.g., /tmp/user vs /tmp/userX)"""
        with tempfile.TemporaryDirectory() as base_str:
            base_dir = Path(base_str)
            # Create a sibling directory with a name that starts with the same prefix
            sibling = Path(base_str + "X")
            sibling.mkdir(exist_ok=True)
            try:
                sibling_file = sibling / "secret.txt"
                sibling_file.write_text("secret")

                # This should be rejected: sibling_file is outside base_dir
                # even though str(sibling_file) starts with str(base_dir)
                with pytest.raises(ValueError, match="Path outside base directory"):
                    safe_resolve_path(base_dir, str(sibling_file))
            finally:
                sibling_file.unlink(missing_ok=True)
                sibling.rmdir()

    def test_symlink_within_base_dir(self, temp_dir):
        """Test that symlinks within base_dir are allowed"""
        target = temp_dir / "target.txt"
        target.write_text("target content")

        link = temp_dir / "link.txt"
        link.symlink_to(target)

        result = safe_resolve_path(temp_dir, "link.txt")
        assert result == target.resolve()

    def test_symlink_outside_base_dir_rejected(self, temp_dir):
        """Test that symlinks pointing outside base_dir are rejected"""
        with tempfile.TemporaryDirectory() as outside_str:
            outside = Path(outside_str)
            outside_file = outside / "secret.txt"
            outside_file.write_text("secret")

            link = temp_dir / "evil_link"
            link.symlink_to(outside_file)

            with pytest.raises(ValueError, match="Path outside base directory"):
                safe_resolve_path(temp_dir, str(link))

    def test_must_exist_flag(self, temp_dir):
        """Test must_exist parameter"""
        with pytest.raises(ValueError, match="Path does not exist"):
            safe_resolve_path(temp_dir, "nonexistent.txt", must_exist=True)

    def test_valid_absolute_path_within_base(self, temp_dir):
        """Test valid absolute path within base_dir"""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")

        result = safe_resolve_path(temp_dir, str(test_file))
        assert result == test_file.resolve()


class TestValidateDirectoryPath:
    """Tests for validate_directory_path"""

    def test_valid_directory(self, temp_dir):
        """Test validating an existing directory"""
        result = validate_directory_path(str(temp_dir))
        assert result == temp_dir.resolve()

    def test_nonexistent_directory(self):
        """Test validating a non-existent directory"""
        with pytest.raises(ValueError, match="Directory does not exist"):
            validate_directory_path("/nonexistent/path/12345")

    def test_file_as_directory(self, temp_dir):
        """Test that a file path is rejected as directory"""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")

        with pytest.raises(ValueError, match="not a directory"):
            validate_directory_path(str(test_file))
