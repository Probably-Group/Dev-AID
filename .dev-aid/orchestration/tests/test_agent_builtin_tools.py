"""Tests for built-in agent tools (file, git, search)."""

from pathlib import Path

import pytest
from agents.tools.file_tools import edit_file, glob_files, list_directory, read_file, write_file
from agents.tools.search_tools import find_files


class TestReadFile:
    """Tests for read_file tool."""

    def test_read_existing_file(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("line 1\nline 2\nline 3\n")
        result = read_file(str(f))
        assert "line 1" in result
        assert "line 3" in result

    def test_read_with_offset(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("line 1\nline 2\nline 3\n")
        result = read_file(str(f), offset=2)
        assert "line 1" not in result
        assert "line 2" in result

    def test_read_with_limit(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("line 1\nline 2\nline 3\n")
        result = read_file(str(f), limit=1)
        assert "line 1" in result
        assert "line 2" not in result

    def test_read_with_offset_and_limit(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("line 1\nline 2\nline 3\nline 4\n")
        result = read_file(str(f), offset=2, limit=2)
        assert "line 1" not in result
        assert "line 2" in result
        assert "line 3" in result
        assert "line 4" not in result

    def test_read_nonexistent(self) -> None:
        with pytest.raises(FileNotFoundError):
            read_file("/nonexistent/file.txt")


class TestWriteFile:
    """Tests for write_file tool."""

    def test_write_new_file(self, tmp_path: Path) -> None:
        path = str(tmp_path / "new.txt")
        result = write_file(path, "hello world")
        assert "Successfully wrote" in result
        assert Path(path).read_text() == "hello world"

    def test_write_creates_parents(self, tmp_path: Path) -> None:
        path = str(tmp_path / "sub" / "dir" / "file.txt")
        write_file(path, "content")
        assert Path(path).read_text() == "content"

    def test_write_overwrites(self, tmp_path: Path) -> None:
        f = tmp_path / "existing.txt"
        f.write_text("old content")
        write_file(str(f), "new content")
        assert f.read_text() == "new content"


class TestListDirectory:
    """Tests for list_directory tool."""

    def test_list_directory(self, tmp_path: Path) -> None:
        (tmp_path / "file1.py").touch()
        (tmp_path / "file2.js").touch()
        (tmp_path / "subdir").mkdir()
        result = list_directory(str(tmp_path))
        assert "f file1.py" in result
        assert "f file2.js" in result
        assert "d subdir" in result

    def test_list_empty_directory(self, tmp_path: Path) -> None:
        empty = tmp_path / "empty"
        empty.mkdir()
        result = list_directory(str(empty))
        assert result == "(empty directory)"

    def test_list_hides_dotfiles(self, tmp_path: Path) -> None:
        (tmp_path / ".hidden").touch()
        (tmp_path / "visible.txt").touch()
        result = list_directory(str(tmp_path))
        assert ".hidden" not in result
        assert "visible.txt" in result

    def test_list_nonexistent(self) -> None:
        with pytest.raises(NotADirectoryError):
            list_directory("/nonexistent/dir")


class TestGlobFiles:
    """Tests for glob_files tool."""

    def test_glob_pattern(self, tmp_path: Path) -> None:
        (tmp_path / "a.py").touch()
        (tmp_path / "b.py").touch()
        (tmp_path / "c.js").touch()
        result = glob_files("*.py", str(tmp_path))
        assert "a.py" in result
        assert "b.py" in result
        assert "c.js" not in result

    def test_glob_recursive(self, tmp_path: Path) -> None:
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "deep.py").touch()
        (tmp_path / "top.py").touch()
        result = glob_files("**/*.py", str(tmp_path))
        assert "deep.py" in result
        assert "top.py" in result

    def test_glob_no_matches(self, tmp_path: Path) -> None:
        result = glob_files("*.xyz", str(tmp_path))
        assert "No files found" in result


class TestFindFiles:
    """Tests for find_files tool."""

    def test_find_by_pattern(self, tmp_path: Path) -> None:
        (tmp_path / "test_one.py").touch()
        (tmp_path / "test_two.py").touch()
        (tmp_path / "main.py").touch()
        result = find_files("test_*.py", str(tmp_path))
        assert "test_one.py" in result
        assert "test_two.py" in result
        assert "main.py" not in result

    def test_find_recursive(self, tmp_path: Path) -> None:
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "deep.txt").touch()
        result = find_files("*.txt", str(tmp_path))
        assert "deep.txt" in result

    def test_find_skips_hidden(self, tmp_path: Path) -> None:
        hidden = tmp_path / ".hidden"
        hidden.mkdir()
        (hidden / "secret.py").touch()
        (tmp_path / "visible.py").touch()
        result = find_files("*.py", str(tmp_path))
        assert "visible.py" in result
        assert "secret.py" not in result

    def test_find_no_matches(self, tmp_path: Path) -> None:
        result = find_files("*.nonexistent", str(tmp_path))
        assert "No files found" in result


class TestEditFile:
    """Tests for edit_file tool."""

    def test_edit_replaces_unique_string(self, tmp_path: Path) -> None:
        f = tmp_path / "test.py"
        f.write_text("def hello():\n    return 'hello'\n")
        result = edit_file(str(f), "return 'hello'", "return 'world'")
        assert "Successfully edited" in result
        assert f.read_text() == "def hello():\n    return 'world'\n"

    def test_edit_nonexistent_file(self) -> None:
        with pytest.raises(FileNotFoundError):
            edit_file("/nonexistent/file.py", "old", "new")

    def test_edit_string_not_found(self, tmp_path: Path) -> None:
        f = tmp_path / "test.py"
        f.write_text("def hello():\n    pass\n")
        with pytest.raises(ValueError, match="String not found"):
            edit_file(str(f), "nonexistent string", "replacement")

    def test_edit_ambiguous_match(self, tmp_path: Path) -> None:
        f = tmp_path / "test.py"
        f.write_text("pass\npass\npass\n")
        with pytest.raises(ValueError, match="appears 3 times"):
            edit_file(str(f), "pass", "return")

    def test_edit_preserves_surrounding(self, tmp_path: Path) -> None:
        f = tmp_path / "test.py"
        original = "line 1\nTARGET LINE\nline 3\n"
        f.write_text(original)
        edit_file(str(f), "TARGET LINE", "REPLACED LINE")
        assert f.read_text() == "line 1\nREPLACED LINE\nline 3\n"
