# file: src/flask/src/flask/sansio/app.py:775-804
# asked: {"lines": [775, 776, 777, 796, 797, 798, 800, 801, 802, 804], "branches": [[796, 797], [796, 800]]}
# gained: {"lines": [775, 776, 777, 796, 797, 798, 800, 801, 802, 804], "branches": [[796, 797], [796, 800]]}

import pytest
from unittest.mock import Mock, MagicMock
from flask.sansio.app import App

class TestAppTemplateGlobal:
    def test_template_global_without_name_decorator(self, monkeypatch):
        """Test template_global decorator without name parameter."""
        # Create a minimal App instance by mocking necessary attributes
        app = App.__new__(App)
        app.import_name = 'test_app'
        app._got_first_request = False  # Required for setupmethod decorator
        app._name = 'test_app'
        
        # Mock the jinja_env and its globals
        app.jinja_env = Mock()
        app.jinja_env.globals = {}
        
        # Test decorator without parentheses (lines 796-798)
        @app.template_global
        def double(n):
            return 2 * n
        
        # Verify add_template_global was called correctly
        assert 'double' in app.jinja_env.globals
        assert app.jinja_env.globals['double'] == double
        
        # Verify the function still works
        assert double(5) == 10

    def test_template_global_with_name_decorator(self, monkeypatch):
        """Test template_global decorator with name parameter."""
        # Create a minimal App instance by mocking necessary attributes
        app = App.__new__(App)
        app.import_name = 'test_app'
        app._got_first_request = False  # Required for setupmethod decorator
        app._name = 'test_app'
        
        # Mock the jinja_env and its globals
        app.jinja_env = Mock()
        app.jinja_env.globals = {}
        
        # Test decorator with name parameter (lines 800-804)
        @app.template_global('custom_name')
        def triple(n):
            return 3 * n
        
        # Verify add_template_global was called correctly
        assert 'custom_name' in app.jinja_env.globals
        assert app.jinja_env.globals['custom_name'] == triple
        
        # Verify the function still works
        assert triple(4) == 12

    def test_template_global_direct_call(self, monkeypatch):
        """Test template_global when called directly with a callable."""
        # Create a minimal App instance by mocking necessary attributes
        app = App.__new__(App)
        app.import_name = 'test_app'
        app._got_first_request = False  # Required for setupmethod decorator
        app._name = 'test_app'
        
        # Mock the jinja_env and its globals
        app.jinja_env = Mock()
        app.jinja_env.globals = {}
        
        # Test direct call with callable (lines 796-798)
        def quadruple(n):
            return 4 * n
        
        result = app.template_global(quadruple)
        
        # Verify add_template_global was called correctly
        assert 'quadruple' in app.jinja_env.globals
        assert app.jinja_env.globals['quadruple'] == quadruple
        assert result == quadruple
        assert quadruple(3) == 12
