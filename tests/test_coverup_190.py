# file: src/flask/src/flask/sansio/app.py:854-863
# asked: {"lines": [854, 855, 862, 863], "branches": []}
# gained: {"lines": [854, 855, 862, 863], "branches": []}

import pytest
from flask import Flask

def test_shell_context_processor_registration():
    """Test that shell_context_processor registers a function correctly."""
    app = Flask(__name__)
    
    # Define a shell context processor function
    def test_processor():
        return {'test_key': 'test_value'}
    
    # Register the processor
    registered_func = app.shell_context_processor(test_processor)
    
    # Verify the function was added to the list
    assert test_processor in app.shell_context_processors
    assert len(app.shell_context_processors) == 1
    
    # Verify the function was returned
    assert registered_func is test_processor

def test_shell_context_processor_decorator():
    """Test that shell_context_processor works as a decorator."""
    app = Flask(__name__)
    
    # Use as decorator
    @app.shell_context_processor
    def test_processor():
        return {'test_key': 'test_value'}
    
    # Verify the function was added to the list
    assert test_processor in app.shell_context_processors
    assert len(app.shell_context_processors) == 1

def test_shell_context_processor_multiple():
    """Test registering multiple shell context processors."""
    app = Flask(__name__)
    
    def processor1():
        return {'key1': 'value1'}
    
    def processor2():
        return {'key2': 'value2'}
    
    # Register multiple processors
    app.shell_context_processor(processor1)
    app.shell_context_processor(processor2)
    
    # Verify both were added
    assert processor1 in app.shell_context_processors
    assert processor2 in app.shell_context_processors
    assert len(app.shell_context_processors) == 2
