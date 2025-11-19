# file: src/flask/src/flask/sansio/scaffold.py:541-556
# asked: {"lines": [541, 542, 555, 556], "branches": []}
# gained: {"lines": [541, 542, 555, 556], "branches": []}

import pytest
from flask import Flask
from flask.blueprints import Blueprint

def test_scaffold_context_processor():
    """Test that context_processor decorator registers function correctly."""
    app = Flask(__name__)
    
    # Test that the function is registered in template_context_processors
    @app.context_processor
    def test_processor():
        return {'test_key': 'test_value'}
    
    assert test_processor in app.template_context_processors[None]
    # App should have default processor + our custom one
    assert len(app.template_context_processors[None]) == 2

def test_blueprint_context_processor():
    """Test that context_processor works on Blueprint objects."""
    bp = Blueprint('test_bp', __name__)
    
    @bp.context_processor
    def bp_processor():
        return {'bp_key': 'bp_value'}
    
    assert bp_processor in bp.template_context_processors[None]
    # Blueprint should also have default processor + our custom one
    assert len(bp.template_context_processors[None]) == 2

def test_context_processor_return_value():
    """Test that context_processor returns the original function."""
    app = Flask(__name__)
    
    def test_func():
        return {'key': 'value'}
    
    decorated_func = app.context_processor(test_func)
    
    assert decorated_func is test_func
    assert test_func in app.template_context_processors[None]
