# file: src/flask/src/flask/app.py:501-527
# asked: {"lines": [516], "branches": [[515, 516], [523, 522]]}
# gained: {"lines": [516], "branches": [[515, 516]]}

import pytest
from flask import Flask, Blueprint
from flask.globals import _cv_app
from unittest.mock import patch

class TestFlaskUpdateTemplateContext:
    def test_update_template_context_with_blueprints_and_processors(self):
        """Test line 516 and branch 523->522 with blueprints and template context processors."""
        app = Flask(__name__)
        
        # Create blueprints and register them
        test_blueprint = Blueprint('test_blueprint', __name__)
        
        # Register blueprint with the app
        app.register_blueprint(test_blueprint)
        
        # Create a mock request context with blueprints
        with app.test_request_context():
            # Mock the blueprints property at the module level to avoid property issues
            with patch('flask.wrappers.Request.blueprints', 
                      new_callable=lambda: property(lambda self: ['test_blueprint'])):
                
                # Add template context processors for None and the blueprint
                none_processor_called = False
                blueprint_processor_called = False
                
                def none_processor():
                    nonlocal none_processor_called
                    none_processor_called = True
                    return {'none_key': 'none_value'}
                
                def blueprint_processor():
                    nonlocal blueprint_processor_called
                    blueprint_processor_called = True
                    return {'blueprint_key': 'blueprint_value'}
                
                app.template_context_processors[None] = [none_processor]
                app.template_context_processors['test_blueprint'] = [blueprint_processor]
                
                # Initial context
                context = {'original_key': 'original_value'}
                
                # Call the method
                app.update_template_context(context)
                
                # Verify the context was updated correctly
                assert context['original_key'] == 'original_value'  # Original preserved
                assert context['none_key'] == 'none_value'  # From None processor
                assert context['blueprint_key'] == 'blueprint_value'  # From blueprint processor
                
                # Verify processors were called
                assert none_processor_called
                assert blueprint_processor_called

    def test_update_template_context_with_blueprints_no_processors(self):
        """Test line 516 and branch 523->522 with blueprints but no matching processors."""
        app = Flask(__name__)
        
        # Create blueprints and register them
        test_blueprint = Blueprint('non_existent_blueprint', __name__)
        
        # Register blueprint with the app
        app.register_blueprint(test_blueprint)
        
        # Create a mock request context with blueprints
        with app.test_request_context():
            # Mock the blueprints property at the module level to avoid property issues
            with patch('flask.wrappers.Request.blueprints', 
                      new_callable=lambda: property(lambda self: ['non_existent_blueprint'])):
                
                # Only add processor for None, not for the blueprint
                processor_called = False
                
                def none_processor():
                    nonlocal processor_called
                    processor_called = True
                    return {'none_key': 'none_value'}
                
                app.template_context_processors[None] = [none_processor]
                
                # Initial context
                context = {'original_key': 'original_value'}
                
                # Call the method
                app.update_template_context(context)
                
                # Verify the context was updated correctly
                assert context['original_key'] == 'original_value'  # Original preserved
                assert context['none_key'] == 'none_value'  # From None processor
                assert 'blueprint_key' not in context  # No blueprint processor
                
                # Verify only None processor was called
                assert processor_called
