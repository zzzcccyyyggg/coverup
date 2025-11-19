# file: src/flask/src/flask/templating.py:138-150
# asked: {"lines": [138, 148, 149, 150], "branches": []}
# gained: {"lines": [138, 148, 149, 150], "branches": []}

import pytest
import typing as t
from unittest.mock import Mock, patch
from jinja2 import Template
from flask import Flask
from flask.templating import render_template, _render


class TestRenderTemplate:
    """Test cases for render_template function to achieve full coverage."""
    
    def test_render_template_with_template_object(self):
        """Test render_template with a Template object directly."""
        # Create a Flask app
        app = Flask(__name__)
        
        # Create a mock template
        mock_template = Mock()
        mock_template.render = Mock(return_value="rendered_template")
        
        # Mock jinja_env.get_or_select_template to return our mock template
        with patch.object(app.jinja_env, 'get_or_select_template', return_value=mock_template):
            with app.app_context():
                # Create a template object
                template_obj = Template("Hello {{ name }}")
                
                # Call render_template with template object
                result = render_template(template_obj, name="World")
                
                # Verify the template object was passed to get_or_select_template
                app.jinja_env.get_or_select_template.assert_called_once_with(template_obj)
                # Verify template.render was called and contains our context
                assert mock_template.render.called
                call_args = mock_template.render.call_args[0][0]
                assert call_args['name'] == 'World'
                # Verify result
                assert result == "rendered_template"
    
    def test_render_template_with_template_list(self):
        """Test render_template with a list of template names/objects."""
        # Create a Flask app
        app = Flask(__name__)
        
        # Create a mock template
        mock_template = Mock()
        mock_template.render = Mock(return_value="rendered_from_list")
        
        # Mock jinja_env.get_or_select_template to return our mock template
        with patch.object(app.jinja_env, 'get_or_select_template', return_value=mock_template):
            with app.app_context():
                # Create a list of templates
                template_list = ["template1.html", "template2.html"]
                
                # Call render_template with template list
                result = render_template(template_list, data="test")
                
                # Verify the template list was passed to get_or_select_template
                app.jinja_env.get_or_select_template.assert_called_once_with(template_list)
                # Verify template.render was called and contains our context
                assert mock_template.render.called
                call_args = mock_template.render.call_args[0][0]
                assert call_args['data'] == 'test'
                # Verify result
                assert result == "rendered_from_list"
    
    def test_render_template_with_mixed_template_list(self):
        """Test render_template with a mixed list of template names and Template objects."""
        # Create a Flask app
        app = Flask(__name__)
        
        # Create a mock template
        mock_template = Mock()
        mock_template.render = Mock(return_value="rendered_mixed")
        
        # Mock jinja_env.get_or_select_template to return our mock template
        with patch.object(app.jinja_env, 'get_or_select_template', return_value=mock_template):
            with app.app_context():
                # Create a mixed list of templates
                template1 = Template("Template 1")
                template2 = "template2.html"
                mixed_list = [template1, template2]
                
                # Call render_template with mixed template list
                result = render_template(mixed_list, value=42)
                
                # Verify the mixed template list was passed to get_or_select_template
                app.jinja_env.get_or_select_template.assert_called_once_with(mixed_list)
                # Verify template.render was called and contains our context
                assert mock_template.render.called
                call_args = mock_template.render.call_args[0][0]
                assert call_args['value'] == 42
                # Verify result
                assert result == "rendered_mixed"


class TestRenderFunction:
    """Test cases for _render function to achieve full coverage."""
    
    def test_render_function_complete_flow(self):
        """Test the complete flow of _render function."""
        # Create a mock app
        mock_app = Mock()
        mock_app.update_template_context = Mock()
        mock_app.ensure_sync = Mock(side_effect=lambda x: x)
        
        # Create a mock template
        mock_template = Mock()
        mock_template.render = Mock(return_value="final_rendered_content")
        
        # Create mock signals
        mock_before_signal = Mock()
        mock_rendered_signal = Mock()
        
        # Patch the signals
        with patch('flask.templating.before_render_template', mock_before_signal), \
             patch('flask.templating.template_rendered', mock_rendered_signal):
            
            # Call _render function
            context = {'key': 'value'}
            result = _render(mock_app, mock_template, context)
            
            # Verify app.update_template_context was called
            mock_app.update_template_context.assert_called_once_with(context)
            
            # Verify before_render_template signal was sent
            mock_before_signal.send.assert_called_once_with(
                mock_app, 
                _async_wrapper=mock_app.ensure_sync,
                template=mock_template, 
                context=context
            )
            
            # Verify template.render was called with updated context
            mock_template.render.assert_called_once_with(context)
            
            # Verify template_rendered signal was sent
            mock_rendered_signal.send.assert_called_once_with(
                mock_app,
                _async_wrapper=mock_app.ensure_sync,
                template=mock_template,
                context=context
            )
            
            # Verify the final result
            assert result == "final_rendered_content"
