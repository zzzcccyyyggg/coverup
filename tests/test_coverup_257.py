# file: src/flask/src/flask/sansio/app.py:925-933
# asked: {"lines": [925, 933], "branches": []}
# gained: {"lines": [925, 933], "branches": []}

import pytest
from flask import Flask
import sys

class TestAppShouldIgnoreError:
    """Test cases for the should_ignore_error method in Flask App class."""
    
    def test_should_ignore_error_returns_false_by_default(self):
        """Test that should_ignore_error returns False by default for any error."""
        app = Flask(__name__)
        
        # Test with None
        result = app.should_ignore_error(None)
        assert result is False
        
        # Test with a regular exception
        result = app.should_ignore_error(ValueError("test error"))
        assert result is False
        
        # Test with a system exit
        result = app.should_ignore_error(SystemExit(1))
        assert result is False
        
        # Test with a keyboard interrupt
        result = app.should_ignore_error(KeyboardInterrupt())
        assert result is False

    def test_should_ignore_error_with_custom_app_override(self):
        """Test that a custom app can override should_ignore_error method."""
        class CustomApp(Flask):
            def should_ignore_error(self, error: BaseException | None) -> bool:
                # Custom implementation that ignores specific errors
                if isinstance(error, ValueError):
                    return True
                return False
        
        app = CustomApp(__name__)
        
        # Test with ValueError - should be ignored
        result = app.should_ignore_error(ValueError("test"))
        assert result is True
        
        # Test with other exception - should not be ignored
        result = app.should_ignore_error(TypeError("test"))
        assert result is False
        
        # Test with None - should not be ignored
        result = app.should_ignore_error(None)
        assert result is False
