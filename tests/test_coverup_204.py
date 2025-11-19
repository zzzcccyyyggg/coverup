# file: src/flask/src/flask/sansio/blueprints.py:672-682
# asked: {"lines": [672, 673, 679, 680, 682], "branches": []}
# gained: {"lines": [672, 673, 679, 680, 682], "branches": []}

import pytest
from flask import Flask
from flask.sansio.blueprints import Blueprint

class TestBlueprintAppUrlValuePreprocessor:
    def test_app_url_value_preprocessor_registers_callback(self):
        """Test that app_url_value_preprocessor registers the callback function."""
        app = Flask(__name__)
        bp = Blueprint('test_bp', __name__)
        
        # Track if the callback was called
        callback_called = []
        
        def test_preprocessor(endpoint, values):
            callback_called.append((endpoint, values))
        
        # Register the preprocessor
        result = bp.app_url_value_preprocessor(test_preprocessor)
        
        # Verify the function is returned
        assert result is test_preprocessor
        
        # Mock the cli attribute to avoid AttributeError during registration
        bp.cli = type('MockCli', (), {'commands': []})()
        
        # Register the blueprint with the app to trigger deferred functions
        app.register_blueprint(bp)
        
        # Verify the preprocessor was registered in the app
        assert None in app.url_value_preprocessors
        assert test_preprocessor in app.url_value_preprocessors[None]

    def test_app_url_value_preprocessor_multiple_registrations(self):
        """Test that app_url_value_preprocessor can be called multiple times."""
        app = Flask(__name__)
        bp = Blueprint('test_bp', __name__)
        
        preprocessors = []
        
        def preprocessor1(endpoint, values):
            pass
            
        def preprocessor2(endpoint, values):
            pass
        
        # Register first preprocessor
        result1 = bp.app_url_value_preprocessor(preprocessor1)
        assert result1 is preprocessor1
        
        # Register second preprocessor  
        result2 = bp.app_url_value_preprocessor(preprocessor2)
        assert result2 is preprocessor2
        
        # Mock the cli attribute to avoid AttributeError during registration
        bp.cli = type('MockCli', (), {'commands': []})()
        
        # Register the blueprint with the app to trigger deferred functions
        app.register_blueprint(bp)
        
        # Verify both are registered
        assert None in app.url_value_preprocessors
        assert preprocessor1 in app.url_value_preprocessors[None]
        assert preprocessor2 in app.url_value_preprocessors[None]
