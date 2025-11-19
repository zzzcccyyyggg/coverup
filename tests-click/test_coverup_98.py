# file: src/click/src/click/shell_completion.py:57-91
# asked: {"lines": [57, 58, 76, 78, 81, 82, 85, 86, 87, 88, 90, 91], "branches": []}
# gained: {"lines": [57, 58, 76, 78, 81, 82, 85, 86, 87, 88, 90, 91], "branches": []}

import pytest
import typing as t
from click.shell_completion import CompletionItem


class TestCompletionItem:
    def test_completion_item_creation_with_defaults(self):
        """Test creating CompletionItem with only required value parameter."""
        item = CompletionItem("test_value")
        assert item.value == "test_value"
        assert item.type == "plain"
        assert item.help is None
        assert item._info == {}

    def test_completion_item_creation_with_all_params(self):
        """Test creating CompletionItem with all explicit parameters."""
        item = CompletionItem("test_value", type="file", help="Test help text")
        assert item.value == "test_value"
        assert item.type == "file"
        assert item.help == "Test help text"
        assert item._info == {}

    def test_completion_item_creation_with_kwargs(self):
        """Test creating CompletionItem with additional kwargs metadata."""
        item = CompletionItem("test_value", custom_attr="custom_value", another_attr=42)
        assert item.value == "test_value"
        assert item.type == "plain"
        assert item.help is None
        assert item._info == {"custom_attr": "custom_value", "another_attr": 42}

    def test_completion_item_getattr_existing_kwarg(self):
        """Test __getattr__ accessing existing kwargs attribute."""
        item = CompletionItem("test_value", custom_attr="custom_value", another_attr=42)
        assert item.custom_attr == "custom_value"
        assert item.another_attr == 42

    def test_completion_item_getattr_nonexistent_kwarg(self):
        """Test __getattr__ accessing non-existent kwargs attribute returns None."""
        item = CompletionItem("test_value")
        assert item.nonexistent_attr is None

    def test_completion_item_getattr_nonexistent_kwarg_with_empty_info(self):
        """Test __getattr__ accessing non-existent kwargs attribute when _info is empty."""
        item = CompletionItem("test_value")
        assert item.some_random_attribute is None

    def test_completion_item_getattr_mixed_kwargs(self):
        """Test __getattr__ with mixed existing and non-existing kwargs."""
        item = CompletionItem("test_value", existing_attr="exists")
        assert item.existing_attr == "exists"
        assert item.non_existing_attr is None
