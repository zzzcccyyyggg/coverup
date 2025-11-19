# file: src/flask/src/flask/app.py:529-539
# asked: {"lines": [529, 536, 537, 538, 539], "branches": [[537, 538], [537, 539]]}
# gained: {"lines": [529, 536, 537, 538, 539], "branches": [[537, 538], [537, 539]]}

import pytest
from flask import Flask, g
import typing as t

def test_make_shell_context_without_processors():
    """Test make_shell_context when no shell context processors are registered."""
    app = Flask(__name__)
    
    # Ensure no shell context processors are registered
    app.shell_context_processors = []
    
    context = app.make_shell_context()
    
    # Verify the basic context is returned
    assert context == {"app": app, "g": g}
    assert "app" in context
    assert "g" in context
    assert context["app"] is app
    assert context["g"] is g

def test_make_shell_context_with_processors():
    """Test make_shell_context when shell context processors are registered."""
    app = Flask(__name__)
    
    # Define test processors
    def processor1():
        return {"key1": "value1", "key2": 42}
    
    def processor2():
        return {"key3": [1, 2, 3], "key4": {"nested": "value"}}
    
    # Register the processors
    app.shell_context_processors = [processor1, processor2]
    
    context = app.make_shell_context()
    
    # Verify the basic context is present
    assert "app" in context
    assert "g" in context
    assert context["app"] is app
    assert context["g"] is g
    
    # Verify processor results are merged
    assert context["key1"] == "value1"
    assert context["key2"] == 42
    assert context["key3"] == [1, 2, 3]
    assert context["key4"] == {"nested": "value"}

def test_make_shell_context_with_overlapping_keys():
    """Test make_shell_context when processors have overlapping keys (later wins)."""
    app = Flask(__name__)
    
    def processor1():
        return {"common_key": "first_value", "unique1": "value1"}
    
    def processor2():
        return {"common_key": "second_value", "unique2": "value2"}
    
    app.shell_context_processors = [processor1, processor2]
    
    context = app.make_shell_context()
    
    # Verify later processor overwrites earlier one for common keys
    assert context["common_key"] == "second_value"
    assert context["unique1"] == "value1"
    assert context["unique2"] == "value2"

def test_make_shell_context_with_empty_processor():
    """Test make_shell_context with a processor that returns empty dict."""
    app = Flask(__name__)
    
    def empty_processor():
        return {}
    
    app.shell_context_processors = [empty_processor]
    
    context = app.make_shell_context()
    
    # Verify basic context is still present
    assert context == {"app": app, "g": g}
