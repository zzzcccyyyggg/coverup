# file: src/click/src/click/shell_completion.py:436-453
# asked: {"lines": [436, 437, 448, 449, 451, 453], "branches": [[448, 449], [448, 451]]}
# gained: {"lines": [436, 437, 448, 449, 451, 453], "branches": [[448, 449], [448, 451]]}

import pytest
from click.shell_completion import add_completion_class, ShellComplete

class TestShellComplete(ShellComplete):
    """Test completion class for testing add_completion_class."""
    name = "test_shell"
    source_template = "test_source_template"

    def source_vars(self):
        return {}

    def get_completion_args(self):
        return [], ""

    def get_completions(self, args, incomplete):
        return []

    def format_completion(self, item):
        return ""

    def complete(self):
        return ""

class TestAddCompletionClass:
    def test_add_completion_class_with_name(self, monkeypatch):
        """Test add_completion_class when name is explicitly provided."""
        # Clear any existing shells to avoid state pollution
        from click.shell_completion import _available_shells
        original_shells = _available_shells.copy()
        _available_shells.clear()
        
        try:
            # Test with explicit name
            result = add_completion_class(TestShellComplete, name="custom_name")
            
            # Verify the class was registered with the custom name
            assert "custom_name" in _available_shells
            assert _available_shells["custom_name"] is TestShellComplete
            
            # Verify the function returns the class
            assert result is TestShellComplete
        finally:
            # Restore original state
            _available_shells.clear()
            _available_shells.update(original_shells)

    def test_add_completion_class_without_name(self, monkeypatch):
        """Test add_completion_class when name is not provided (uses class name attribute)."""
        # Clear any existing shells to avoid state pollution
        from click.shell_completion import _available_shells
        original_shells = _available_shells.copy()
        _available_shells.clear()
        
        try:
            # Test without explicit name - should use class.name
            result = add_completion_class(TestShellComplete)
            
            # Verify the class was registered with its name attribute
            assert "test_shell" in _available_shells
            assert _available_shells["test_shell"] is TestShellComplete
            
            # Verify the function returns the class
            assert result is TestShellComplete
        finally:
            # Restore original state
            _available_shells.clear()
            _available_shells.update(original_shells)

    def test_add_completion_class_multiple_classes(self, monkeypatch):
        """Test adding multiple completion classes with different names."""
        # Clear any existing shells to avoid state pollution
        from click.shell_completion import _available_shells
        original_shells = _available_shells.copy()
        _available_shells.clear()
        
        try:
            # Define a second test class
            class AnotherTestShellComplete(ShellComplete):
                name = "another_shell"
                source_template = "another_template"

                def source_vars(self):
                    return {}

                def get_completion_args(self):
                    return [], ""

                def get_completions(self, args, incomplete):
                    return []

                def format_completion(self, item):
                    return ""

                def complete(self):
                    return ""
            
            # Add first class with explicit name
            result1 = add_completion_class(TestShellComplete, name="first_shell")
            assert "first_shell" in _available_shells
            assert _available_shells["first_shell"] is TestShellComplete
            assert result1 is TestShellComplete
            
            # Add second class without explicit name
            result2 = add_completion_class(AnotherTestShellComplete)
            assert "another_shell" in _available_shells
            assert _available_shells["another_shell"] is AnotherTestShellComplete
            assert result2 is AnotherTestShellComplete
            
            # Verify both are registered
            assert len(_available_shells) == 2
            assert _available_shells["first_shell"] is TestShellComplete
            assert _available_shells["another_shell"] is AnotherTestShellComplete
        finally:
            # Restore original state
            _available_shells.clear()
            _available_shells.update(original_shells)
