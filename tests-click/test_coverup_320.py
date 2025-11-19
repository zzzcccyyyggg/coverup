# file: src/click/src/click/shell_completion.py:359-360
# asked: {"lines": [359, 360], "branches": []}
# gained: {"lines": [359, 360], "branches": []}

import pytest
from click.shell_completion import BashComplete, CompletionItem
from click.core import Command

class TestBashComplete:
    def test_format_completion_with_type_and_value(self):
        """Test that format_completion returns the correct string format."""
        bash_complete = BashComplete(None, None, None, "_TEST_COMPLETE")
        item = CompletionItem("test_value", type="file")
        result = bash_complete.format_completion(item)
        assert result == "file,test_value"

    def test_format_completion_with_different_type(self):
        """Test format_completion with a different type."""
        bash_complete = BashComplete(None, None, None, "_TEST_COMPLETE")
        item = CompletionItem("directory_path", type="dir")
        result = bash_complete.format_completion(item)
        assert result == "dir,directory_path"

    def test_format_completion_with_plain_type(self):
        """Test format_completion with plain type (default)."""
        bash_complete = BashComplete(None, None, None, "_TEST_COMPLETE")
        item = CompletionItem("plain_value", type="plain")
        result = bash_complete.format_completion(item)
        assert result == "plain,plain_value"
