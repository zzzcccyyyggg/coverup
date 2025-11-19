# file: src/flask/src/flask/app.py:962-974
# asked: {"lines": [962, 971, 972, 974], "branches": [[971, 972], [971, 974]]}
# gained: {"lines": [962, 971, 972, 974], "branches": [[971, 972], [971, 974]]}

import pytest
import typing as t
from unittest.mock import Mock, patch
from inspect import iscoroutinefunction

def test_ensure_sync_with_sync_function():
    """Test ensure_sync with a regular synchronous function."""
    from flask import Flask
    
    app = Flask(__name__)
    
    def sync_function():
        return "sync result"
    
    result_func = app.ensure_sync(sync_function)
    
    # The function should be returned as-is
    assert result_func is sync_function
    # Verify it's not a coroutine function
    assert not iscoroutinefunction(result_func)
    # Verify it works correctly
    assert result_func() == "sync result"

def test_ensure_sync_with_async_function():
    """Test ensure_sync with an async function."""
    from flask import Flask
    
    app = Flask(__name__)
    
    async def async_function():
        return "async result"
    
    # Mock async_to_sync to avoid dependency on asgiref
    mock_async_to_sync = Mock(return_value=lambda: "converted result")
    with patch.object(app, 'async_to_sync', mock_async_to_sync):
        result_func = app.ensure_sync(async_function)
    
    # Verify async_to_sync was called with the async function
    mock_async_to_sync.assert_called_once_with(async_function)
    # Verify the returned function is what async_to_sync returned
    assert result_func() == "converted result"
    # Verify the original function is async
    assert iscoroutinefunction(async_function)
