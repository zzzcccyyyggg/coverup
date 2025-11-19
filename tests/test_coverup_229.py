# file: src/flask/src/flask/templating.py:182-198
# asked: {"lines": [182, 196, 197, 198], "branches": []}
# gained: {"lines": [182, 196, 197, 198], "branches": []}

import pytest
import typing as t
from unittest.mock import Mock, patch
from jinja2 import Template
from flask import Flask
from flask.templating import stream_template


class TestStreamTemplate:
    """Test cases for stream_template function to achieve full coverage."""
    
    def test_stream_template_with_template_name(self):
        """Test stream_template with a template name string."""
        # Create a Flask app with a mock jinja_env
        app = Flask(__name__)
        mock_template = Mock()
        mock_template.generate.return_value = iter(["chunk1", "chunk2"])
        app.jinja_env = Mock()
        app.jinja_env.get_or_select_template.return_value = mock_template
        
        # Test within app context
        with app.app_context():
            result = stream_template("test_template.html", test_var="value")
            
            # Verify the calls
            app.jinja_env.get_or_select_template.assert_called_once_with("test_template.html")
            
            # Verify the result
            assert list(result) == ["chunk1", "chunk2"]
    
    def test_stream_template_with_template_object(self):
        """Test stream_template with a Template object."""
        # Create a Flask app with a mock jinja_env
        app = Flask(__name__)
        mock_template = Mock(spec=Template)
        mock_template.generate.return_value = iter(["chunk1", "chunk2"])
        app.jinja_env = Mock()
        app.jinja_env.get_or_select_template.return_value = mock_template
        
        # Test within app context
        with app.app_context():
            result = stream_template(mock_template, test_var="value")
            
            # Verify the calls
            app.jinja_env.get_or_select_template.assert_called_once_with(mock_template)
            
            # Verify the result
            assert list(result) == ["chunk1", "chunk2"]
    
    def test_stream_template_with_template_list(self):
        """Test stream_template with a list of template names."""
        # Create a Flask app with a mock jinja_env
        app = Flask(__name__)
        mock_template = Mock()
        mock_template.generate.return_value = iter(["chunk1", "chunk2"])
        app.jinja_env = Mock()
        app.jinja_env.get_or_select_template.return_value = mock_template
        
        # Test within app context
        with app.app_context():
            template_list = ["template1.html", "template2.html"]
            result = stream_template(template_list, test_var="value")
            
            # Verify the calls
            app.jinja_env.get_or_select_template.assert_called_once_with(template_list)
            
            # Verify the result
            assert list(result) == ["chunk1", "chunk2"]
    
    def test_stream_template_with_mixed_template_list(self):
        """Test stream_template with a list containing both strings and Template objects."""
        # Create a Flask app with a mock jinja_env
        app = Flask(__name__)
        mock_template1 = Mock(spec=Template)
        mock_template2 = Mock(spec=Template)
        mock_selected_template = Mock()
        mock_selected_template.generate.return_value = iter(["chunk1", "chunk2"])
        app.jinja_env = Mock()
        app.jinja_env.get_or_select_template.return_value = mock_selected_template
        
        # Test within app context
        with app.app_context():
            template_list = ["template1.html", mock_template1, mock_template2]
            result = stream_template(template_list, test_var="value")
            
            # Verify the calls
            app.jinja_env.get_or_select_template.assert_called_once_with(template_list)
            
            # Verify the result
            assert list(result) == ["chunk1", "chunk2"]
