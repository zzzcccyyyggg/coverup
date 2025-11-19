# file: src/flask/src/flask/templating.py:153-162
# asked: {"lines": [153, 160, 161, 162], "branches": []}
# gained: {"lines": [153, 160, 161, 162], "branches": []}

import pytest
from flask import Flask, current_app
from flask.templating import render_template_string
import flask.templating


def test_render_template_string_basic():
    """Test basic template string rendering."""
    app = Flask(__name__)
    
    with app.app_context():
        result = render_template_string("Hello {{ name }}!", name="World")
        assert result == "Hello World!"


def test_render_template_string_with_context():
    """Test template string rendering with complex context."""
    app = Flask(__name__)
    
    with app.app_context():
        context = {
            'items': ['apple', 'banana', 'cherry'],
            'count': 3,
            'nested': {'key': 'value'}
        }
        result = render_template_string(
            "Items: {{ items|join(', ') }}, Count: {{ count }}, Nested: {{ nested.key }}",
            **context
        )
        assert result == "Items: apple, banana, cherry, Count: 3, Nested: value"


def test_render_template_string_empty():
    """Test template string rendering with empty template."""
    app = Flask(__name__)
    
    with app.app_context():
        result = render_template_string("")
        assert result == ""


def test_render_template_string_no_context():
    """Test template string rendering without any context variables."""
    app = Flask(__name__)
    
    with app.app_context():
        result = render_template_string("Static content")
        assert result == "Static content"


def test_render_template_string_jinja_filters():
    """Test template string rendering using Jinja filters."""
    app = Flask(__name__)
    
    with app.app_context():
        result = render_template_string("{{ text|upper }}", text="hello world")
        assert result == "HELLO WORLD"


def test_render_template_string_current_app_usage(monkeypatch):
    """Test that render_template_string uses current_app correctly."""
    app = Flask(__name__)
    
    # Mock the _render function to verify it's called correctly
    mock_render_called = False
    original_render = flask.templating._render
    
    def mock_render(app_obj, template, context):
        nonlocal mock_render_called
        mock_render_called = True
        assert app_obj is app
        # Test that the template renders correctly instead of checking source
        assert template.render(context) == "Test value"
        assert context == {'var': 'value'}
        return "Test value"
    
    monkeypatch.setattr(flask.templating, '_render', mock_render)
    
    with app.app_context():
        result = render_template_string("Test {{ var }}", var="value")
        assert mock_render_called
        assert result == "Test value"
