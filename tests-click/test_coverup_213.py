# file: src/click/src/click/exceptions.py:298-308
# asked: {"lines": [298, 299, 305, 307, 308], "branches": []}
# gained: {"lines": [298, 299, 305, 307, 308], "branches": []}

import pytest
from click.exceptions import Exit

class TestExit:
    def test_exit_default_code(self):
        """Test Exit exception with default code (0)."""
        exc = Exit()
        assert exc.exit_code == 0
        assert isinstance(exc, RuntimeError)
    
    def test_exit_custom_code(self):
        """Test Exit exception with custom code."""
        exc = Exit(42)
        assert exc.exit_code == 42
        assert isinstance(exc, RuntimeError)
    
    def test_exit_negative_code(self):
        """Test Exit exception with negative code."""
        exc = Exit(-1)
        assert exc.exit_code == -1
        assert isinstance(exc, RuntimeError)
