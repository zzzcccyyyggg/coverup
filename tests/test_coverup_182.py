# file: src/flask/src/flask/sansio/app.py:771-774
# asked: {"lines": [771, 772, 773, 774], "branches": []}
# gained: {"lines": [771, 772, 773], "branches": []}

import pytest
import typing as t
from flask import Flask
from flask.sansio.app import App

T_template_global = t.TypeVar("T_template_global")

class TestAppTemplateGlobalOverload:
    """Test cases for the template_global overload decorator."""
    
    def test_template_global_overload_signature(self):
        """Test that the template_global overload signature is accessible."""
        app = Flask(__name__)
        
        # This should not raise any errors and should match the overload signature
        # The overload is just for type checking, so we test that we can reference it
        assert hasattr(app, 'template_global')
        
        # Verify the method exists and is callable
        method = getattr(app, 'template_global')
        assert callable(method)
        
        # Clean up
        del app
    
    def test_template_global_overload_type_hint_access(self):
        """Test accessing the template_global overload type hints."""
        app = Flask(__name__)
        
        # The overload decorator should be present and accessible
        # We can't directly test the overload behavior since it's for static type checking
        # but we can verify the method exists and has the expected attributes
        
        # Get the method and verify it has annotations
        method = app.template_global
        assert hasattr(method, '__annotations__')
        
        # Clean up
        del app
