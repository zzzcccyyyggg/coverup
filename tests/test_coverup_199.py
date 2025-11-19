# file: src/flask/src/flask/templating.py:201-213
# asked: {"lines": [201, 211, 212, 213], "branches": []}
# gained: {"lines": [201, 211, 212, 213], "branches": []}

import pytest
from flask import Flask
from flask.templating import stream_template_string
import typing as t


class TestStreamTemplateString:
    """Test cases for stream_template_string function."""

    def test_stream_template_string_basic(self):
        """Test basic functionality of stream_template_string."""
        # Create a test app
        app = Flask(__name__)
        
        with app.app_context():
            # Call the function
            result = stream_template_string("Hello {{ name }}!", name="World")
            
            # Verify it returns an iterator
            assert hasattr(result, '__iter__')
            
            # Convert to list and verify content
            result_list = list(result)
            # The result is a stream that yields chunks, not necessarily one string
            # Join all chunks and verify the final content
            content = "".join(str(chunk) for chunk in result_list)
            assert "Hello World!" in content

    def test_stream_template_string_with_context(self):
        """Test stream_template_string with complex context."""
        app = Flask(__name__)
        
        with app.app_context():
            # Test with multiple context variables
            result = stream_template_string(
                "{{ greeting }} {{ name }}! You are {{ age }} years old.",
                greeting="Hello",
                name="Alice", 
                age=25
            )
            
            result_list = list(result)
            content = "".join(str(chunk) for chunk in result_list)
            assert "Hello Alice!" in content
            assert "25 years old" in content

    def test_stream_template_string_empty_template(self):
        """Test stream_template_string with empty template."""
        app = Flask(__name__)
        
        with app.app_context():
            result = stream_template_string("", test_var="value")
            result_list = list(result)
            # Empty template should yield no chunks
            assert len(result_list) == 0

    def test_stream_template_string_no_context(self):
        """Test stream_template_string without any context variables."""
        app = Flask(__name__)
        
        with app.app_context():
            result = stream_template_string("Static content")
            result_list = list(result)
            content = "".join(str(chunk) for chunk in result_list)
            assert content == "Static content"

    def test_stream_template_string_template_syntax(self):
        """Test stream_template_string with Jinja2 template syntax."""
        app = Flask(__name__)
        
        with app.app_context():
            template_source = """
            {% for item in items %}
            - {{ item }}
            {% endfor %}
            """
            
            result = stream_template_string(
                template_source, 
                items=["apple", "banana", "cherry"]
            )
            
            result_list = list(result)
            content = "".join(str(chunk) for chunk in result_list)
            assert "apple" in content
            assert "banana" in content  
            assert "cherry" in content
            assert "-" in content
