# file: src/flask/src/flask/helpers.py:288-307
# asked: {"lines": [288, 307], "branches": []}
# gained: {"lines": [288, 307], "branches": []}

import pytest
import tempfile
import os
from flask import Flask
from flask.helpers import get_template_attribute

def test_get_template_attribute_with_macro():
    """Test get_template_attribute with a macro from a template."""
    app = Flask(__name__)
    
    # Create a temporary directory for templates
    with tempfile.TemporaryDirectory() as temp_dir:
        template_dir = os.path.join(temp_dir, 'templates')
        os.makedirs(template_dir)
        
        # Create a template file with a macro
        template_path = os.path.join(template_dir, 'test_template.html')
        with open(template_path, 'w') as f:
            f.write("{% macro hello(name) %}Hello {{ name }}!{% endmacro %}")
        
        # Configure app to use the template directory
        app.template_folder = template_dir
        
        with app.app_context():
            # Get the macro using get_template_attribute
            hello_macro = get_template_attribute('test_template.html', 'hello')
            
            # Test that the macro works correctly
            result = hello_macro('World')
            assert result == 'Hello World!'

def test_get_template_attribute_with_variable():
    """Test get_template_attribute with a variable from a template."""
    app = Flask(__name__)
    
    # Create a temporary directory for templates
    with tempfile.TemporaryDirectory() as temp_dir:
        template_dir = os.path.join(temp_dir, 'templates')
        os.makedirs(template_dir)
        
        # Create a template file with a variable
        template_path = os.path.join(template_dir, 'test_template_var.html')
        with open(template_path, 'w') as f:
            f.write("{% set my_var = 'test_value' %}")
        
        # Configure app to use the template directory
        app.template_folder = template_dir
        
        with app.app_context():
            # Get the variable using get_template_attribute
            my_var = get_template_attribute('test_template_var.html', 'my_var')
            
            # Test that the variable has the correct value
            assert my_var == 'test_value'

def test_get_template_attribute_nonexistent_attribute():
    """Test get_template_attribute with a non-existent attribute raises AttributeError."""
    app = Flask(__name__)
    
    # Create a temporary directory for templates
    with tempfile.TemporaryDirectory() as temp_dir:
        template_dir = os.path.join(temp_dir, 'templates')
        os.makedirs(template_dir)
        
        # Create a simple template file
        template_path = os.path.join(template_dir, 'simple_template.html')
        with open(template_path, 'w') as f:
            f.write("Simple template")
        
        # Configure app to use the template directory
        app.template_folder = template_dir
        
        with app.app_context():
            # Attempt to get a non-existent attribute should raise AttributeError
            with pytest.raises(AttributeError):
                get_template_attribute('simple_template.html', 'nonexistent_attribute')

def test_get_template_attribute_with_complex_macro():
    """Test get_template_attribute with a more complex macro."""
    app = Flask(__name__)
    
    # Create a temporary directory for templates
    with tempfile.TemporaryDirectory() as temp_dir:
        template_dir = os.path.join(temp_dir, 'templates')
        os.makedirs(template_dir)
        
        # Create a template file with a complex macro
        template_path = os.path.join(template_dir, 'name_template.html')
        with open(template_path, 'w') as f:
            f.write("""
{% macro format_name(first, last) %}
    {{ last }}, {{ first }}
{% endmacro %}
""")
        
        # Configure app to use the template directory
        app.template_folder = template_dir
        
        with app.app_context():
            # Get the macro using get_template_attribute
            format_macro = get_template_attribute('name_template.html', 'format_name')
            
            # Test that the macro works correctly
            result = format_macro('John', 'Doe')
            assert result.strip() == 'Doe, John'
