# file: src/flask/src/flask/ctx.py:234-256
# asked: {"lines": [234, 256], "branches": []}
# gained: {"lines": [234, 256], "branches": []}

import pytest
from flask.ctx import has_app_context
from flask.globals import _cv_app

class TestHasAppContext:
    def test_has_app_context_false_when_no_context(self):
        """Test has_app_context returns False when no app context is active."""
        # Ensure no app context is active
        assert not has_app_context()
    
    def test_has_app_context_true_when_context_active(self):
        """Test has_app_context returns True when an app context is active."""
        from flask import Flask
        
        app = Flask(__name__)
        
        with app.app_context():
            assert has_app_context()
