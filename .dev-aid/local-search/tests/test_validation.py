"""Tests for MCP request validation models (audit A-2: these were at 0%)."""

import pytest
from pydantic import ValidationError

from mcp_server.validation import IndexDirectoryRequest, SearchCodeRequest


class TestSearchCodeRequest:
    def test_valid(self, tmp_path):
        req = SearchCodeRequest(query="find handler", project_path=str(tmp_path), top_k=5)
        assert req.query == "find handler"
        assert req.top_k == 5

    def test_query_stripped(self, tmp_path):
        req = SearchCodeRequest(query="  spaced  ", project_path=str(tmp_path))
        assert req.query == "spaced"

    def test_empty_query_rejected(self, tmp_path):
        with pytest.raises(ValidationError):
            SearchCodeRequest(query="   ", project_path=str(tmp_path))

    def test_query_length_bounded(self, tmp_path):
        with pytest.raises(ValidationError):
            SearchCodeRequest(query="x" * 10001, project_path=str(tmp_path))

    def test_relative_path_rejected(self):
        with pytest.raises(ValidationError):
            SearchCodeRequest(query="q", project_path="relative/dir")

    @pytest.mark.parametrize("bad_k", [0, -1, 101])
    def test_top_k_bounds(self, tmp_path, bad_k):
        with pytest.raises(ValidationError):
            SearchCodeRequest(query="q", project_path=str(tmp_path), top_k=bad_k)


class TestIndexDirectoryRequest:
    def test_valid_dir(self, tmp_path):
        req = IndexDirectoryRequest(directory=str(tmp_path))
        assert req.directory == str(tmp_path.resolve())

    def test_missing_dir_rejected(self, tmp_path):
        with pytest.raises(ValidationError):
            IndexDirectoryRequest(directory=str(tmp_path / "nope"))

    def test_file_not_dir_rejected(self, tmp_path):
        f = tmp_path / "a.txt"
        f.write_text("hi")
        with pytest.raises(ValidationError):
            IndexDirectoryRequest(directory=str(f))
