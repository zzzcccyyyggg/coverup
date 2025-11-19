# file: src/click/src/click/shell_completion.py:456-463
# asked: {"lines": [456, 463], "branches": []}
# gained: {"lines": [456, 463], "branches": []}

import pytest
from click.shell_completion import get_completion_class, ShellComplete, add_completion_class


class TestGetCompletionClass:
    def test_get_completion_class_existing_shell(self):
        """Test that get_completion_class returns the correct class for a registered shell."""
        # Create a test completion class
        class TestShellComplete(ShellComplete):
            name = "test_shell"
            source_template = "test_template"
        
        # Register the test class
        add_completion_class(TestShellComplete, "test_shell")
        
        # Test that we can retrieve it
        result = get_completion_class("test_shell")
        assert result is TestShellComplete

    def test_get_completion_class_nonexistent_shell(self):
        """Test that get_completion_class returns None for an unregistered shell."""
        result = get_completion_class("nonexistent_shell")
        assert result is None

    def test_get_completion_class_empty_string(self):
        """Test that get_completion_class returns None for empty string shell name."""
        result = get_completion_class("")
        assert result is None
