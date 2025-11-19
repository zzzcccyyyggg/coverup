# file: src/flask/src/flask/testing.py:100-106
# asked: {"lines": [100, 103, 104, 106], "branches": [[103, 104], [103, 106]]}
# gained: {"lines": [100, 103, 104, 106], "branches": [[103, 104], [103, 106]]}

import pytest
import importlib.metadata
from flask.testing import _get_werkzeug_version

class TestGetWerkzeugVersion:
    def test_get_werkzeug_version_first_call(self, monkeypatch):
        """Test that _get_werkzeug_version calls importlib.metadata.version on first call"""
        # Mock the global variable to ensure it's None initially
        monkeypatch.setattr('flask.testing._werkzeug_version', None)
        
        # Mock importlib.metadata.version to return a test version
        mock_version = "2.3.7"
        monkeypatch.setattr(importlib.metadata, 'version', lambda pkg: mock_version)
        
        # Call the function
        result = _get_werkzeug_version()
        
        # Verify the result
        assert result == mock_version
        
        # Verify the global variable was set
        from flask.testing import _werkzeug_version
        assert _werkzeug_version == mock_version

    def test_get_werkzeug_version_cached_call(self, monkeypatch):
        """Test that _get_werkzeug_version uses cached value on subsequent calls"""
        # Set up a cached value
        cached_version = "2.3.6"
        monkeypatch.setattr('flask.testing._werkzeug_version', cached_version)
        
        # Mock importlib.metadata.version to fail if called (shouldn't be called)
        def mock_version_fail(pkg):
            raise RuntimeError("importlib.metadata.version should not be called when cached")
        monkeypatch.setattr(importlib.metadata, 'version', mock_version_fail)
        
        # Call the function multiple times
        result1 = _get_werkzeug_version()
        result2 = _get_werkzeug_version()
        
        # Verify the cached value is returned
        assert result1 == cached_version
        assert result2 == cached_version

    def test_cleanup_after_tests(self, monkeypatch):
        """Clean up the global variable after tests to avoid state pollution"""
        monkeypatch.setattr('flask.testing._werkzeug_version', None)
