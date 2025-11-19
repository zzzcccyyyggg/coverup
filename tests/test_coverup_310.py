# file: src/flask/src/flask/app.py:541-662
# asked: {"lines": [], "branches": [[622, 626]]}
# gained: {"lines": [], "branches": [[622, 626]]}

import os
import pytest
from unittest.mock import patch, MagicMock
from flask import Flask


class TestFlaskRun:
    """Test cases for Flask.run method to achieve full coverage."""
    
    def test_run_with_flask_debug_env_var(self, monkeypatch):
        """Test that FLASK_DEBUG environment variable sets debug flag when load_dotenv is True."""
        # Mock environment to have FLASK_DEBUG set
        monkeypatch.setenv('FLASK_DEBUG', '1')
        monkeypatch.delenv('FLASK_RUN_FROM_CLI', raising=False)
        
        app = Flask(__name__)
        app.debug = False  # Start with debug disabled
        
        # Mock cli.load_dotenv to avoid actual file loading
        with patch('flask.cli.load_dotenv'):
            # Mock run_simple to avoid starting actual server
            with patch('werkzeug.serving.run_simple') as mock_run:
                # Mock get_debug_flag to return True
                with patch('flask.helpers.get_debug_flag', return_value=True):
                    app.run(load_dotenv=True)
        
        # Verify that debug was set from FLASK_DEBUG environment variable
        assert app.debug is True
    
    def test_run_with_debug_parameter_overrides_env_var(self, monkeypatch):
        """Test that debug parameter overrides FLASK_DEBUG environment variable."""
        # Mock environment to have FLASK_DEBUG set
        monkeypatch.setenv('FLASK_DEBUG', '1')
        monkeypatch.delenv('FLASK_RUN_FROM_CLI', raising=False)
        
        app = Flask(__name__)
        app.debug = False  # Start with debug disabled
        
        # Mock cli.load_dotenv to avoid actual file loading
        with patch('flask.cli.load_dotenv'):
            # Mock run_simple to avoid starting actual server
            with patch('werkzeug.serving.run_simple') as mock_run:
                # Mock get_debug_flag to return True
                with patch('flask.helpers.get_debug_flag', return_value=True):
                    # Pass debug=False which should override FLASK_DEBUG
                    app.run(debug=False, load_dotenv=True)
        
        # Verify that debug parameter overrode FLASK_DEBUG environment variable
        assert app.debug is False
    
    def test_run_with_debug_parameter_true(self, monkeypatch):
        """Test that debug=True parameter sets debug flag."""
        monkeypatch.delenv('FLASK_RUN_FROM_CLI', raising=False)
        
        app = Flask(__name__)
        app.debug = False  # Start with debug disabled
        
        # Mock run_simple to avoid starting actual server
        with patch('werkzeug.serving.run_simple') as mock_run:
            app.run(debug=True)
        
        # Verify that debug was set from parameter
        assert app.debug is True
    
    def test_run_with_debug_parameter_false(self, monkeypatch):
        """Test that debug=False parameter sets debug flag."""
        monkeypatch.delenv('FLASK_RUN_FROM_CLI', raising=False)
        
        app = Flask(__name__)
        app.debug = True  # Start with debug enabled
        
        # Mock run_simple to avoid starting actual server
        with patch('werkzeug.serving.run_simple') as mock_run:
            app.run(debug=False)
        
        # Verify that debug was set from parameter
        assert app.debug is False
    
    def test_run_without_flask_debug_env_var(self, monkeypatch):
        """Test that when FLASK_DEBUG is not in environment, it doesn't affect debug flag."""
        monkeypatch.delenv('FLASK_DEBUG', raising=False)
        monkeypatch.delenv('FLASK_RUN_FROM_CLI', raising=False)
        
        app = Flask(__name__)
        original_debug = app.debug
        
        # Mock cli.load_dotenv to avoid actual file loading
        with patch('flask.cli.load_dotenv'):
            # Mock run_simple to avoid starting actual server
            with patch('werkzeug.serving.run_simple') as mock_run:
                app.run(load_dotenv=True)
        
        # Verify that debug flag remains unchanged when FLASK_DEBUG is not set
        assert app.debug == original_debug
