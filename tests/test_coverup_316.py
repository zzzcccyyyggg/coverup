# file: src/flask/src/flask/cli.py:380-402
# asked: {"lines": [], "branches": [[396, 400]]}
# gained: {"lines": [], "branches": [[396, 400]]}

import pytest
import click
from flask import Flask
from flask.cli import with_appcontext, ScriptInfo
from flask.globals import current_app

def test_with_appcontext_no_current_app():
    """Test that with_appcontext decorator creates app context when current_app is None."""
    
    # Create a simple function to be decorated
    def test_function():
        # This should execute within an app context
        assert current_app is not None
        return "success"
    
    # Apply the decorator
    decorated_function = with_appcontext(test_function)
    
    # Create a mock context with ScriptInfo
    ctx = click.Context(click.Command('test'))
    
    # Create a mock app and ScriptInfo
    app = Flask(__name__)
    script_info = ScriptInfo()
    script_info._loaded_app = app  # Manually set the loaded app
    
    # Set the ScriptInfo in the context
    ctx.obj = script_info
    
    # We need to push the context to make it available for click.pass_context
    with ctx.scope():
        # Invoke the decorated function - this should trigger the branch
        # where current_app is None and create a new app context
        result = decorated_function()
        
        # Verify the function executed successfully
        assert result == "success"

def test_with_appcontext_with_current_app():
    """Test that with_appcontext decorator uses existing current_app."""
    
    # Create a simple function to be decorated
    def test_function():
        # This should execute with the existing app context
        assert current_app is not None
        return "success"
    
    # Apply the decorator
    decorated_function = with_appcontext(test_function)
    
    # Create a mock context
    ctx = click.Context(click.Command('test'))
    
    # Create an app and push its context
    app = Flask(__name__)
    
    with app.app_context():
        # current_app should be available now
        assert current_app is not None
        
        # Push the click context
        with ctx.scope():
            # Invoke the decorated function - should not create new context
            result = decorated_function()
            
            # Verify the function executed successfully
            assert result == "success"
