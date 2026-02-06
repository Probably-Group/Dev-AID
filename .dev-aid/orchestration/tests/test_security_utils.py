"""Tests for shared security_utils module"""

import tempfile
from pathlib import Path

import pytest

from router.security_utils import validate_safe_path


class TestValidateSafePath:
    """Tests for validate_safe_path"""

    def test_basic_resolution(self, temp_dir):
        """Test basic path resolution"""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")
        result = validate_safe_path(test_file)
        assert result == test_file.resolve()

    def test_containment_within_base_dir(self, temp_dir):
        """Test path within base_dir passes"""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")
        result = validate_safe_path(test_file, base_dir=temp_dir)
        assert result == test_file.resolve()

    def test_outside_base_dir_rejected(self, temp_dir):
        """Test path outside base_dir is rejected"""
        outside = Path("/etc/passwd")
        with pytest.raises(ValueError, match="Path outside base directory"):
            validate_safe_path(outside, base_dir=temp_dir)

    def test_prefix_collision_rejected(self):
        """Test that prefix collisions are caught (e.g., /tmp/user vs /tmp/userX)"""
        with tempfile.TemporaryDirectory() as base_str:
            base_dir = Path(base_str)
            sibling = Path(base_str + "X")
            sibling.mkdir(exist_ok=True)
            try:
                sibling_file = sibling / "secret.txt"
                sibling_file.write_text("secret")
                with pytest.raises(ValueError, match="Path outside base directory"):
                    validate_safe_path(sibling_file, base_dir=base_dir)
            finally:
                sibling_file.unlink(missing_ok=True)
                sibling.rmdir()

    def test_null_bytes_rejected(self, temp_dir):
        """Test that null bytes in paths are rejected"""
        with pytest.raises(ValueError):
            validate_safe_path(Path(str(temp_dir) + "/\0evil"))

    def test_require_absolute_rejects_relative(self):
        """Test require_absolute flag"""
        with pytest.raises(ValueError, match="Path must be absolute"):
            validate_safe_path(Path("relative/path"), require_absolute=True)

    def test_require_absolute_accepts_absolute(self, temp_dir):
        """Test require_absolute with absolute path"""
        result = validate_safe_path(temp_dir, require_absolute=True)
        assert result == temp_dir.resolve()

    def test_empty_path(self):
        """Test with empty path string"""
        # Path("") resolves to cwd, which is a valid absolute path
        result = validate_safe_path(Path(""))
        assert result.is_absolute()

    def test_symlink_within_base(self, temp_dir):
        """Test symlink resolving within base_dir"""
        target = temp_dir / "target.txt"
        target.write_text("content")
        link = temp_dir / "link.txt"
        link.symlink_to(target)
        result = validate_safe_path(link, base_dir=temp_dir)
        assert result == target.resolve()
