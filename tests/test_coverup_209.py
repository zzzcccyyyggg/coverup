# file: src/flask/src/flask/sansio/app.py:546-557
# asked: {"lines": [546, 547, 557], "branches": []}
# gained: {"lines": [546, 547, 557], "branches": []}

import pytest
from flask import Flask

class TestAppDebugProperty:
    """Test cases for the App.debug property (lines 546-557)"""
    
    def test_debug_property_returns_false_by_default(self):
        """Test that debug property returns False when DEBUG config is not set."""
        app = Flask(__name__)
        assert app.debug is False
        
    def test_debug_property_returns_true_when_debug_enabled(self):
        """Test that debug property returns True when DEBUG config is set to True."""
        app = Flask(__name__)
        app.config["DEBUG"] = True
        assert app.debug is True
        
    def test_debug_property_returns_false_when_debug_disabled(self):
        """Test that debug property returns False when DEBUG config is explicitly set to False."""
        app = Flask(__name__)
        app.config["DEBUG"] = False
        assert app.debug is False
