# file: src/flask/src/flask/app.py:541-662
# asked: {"lines": [541, 543, 544, 545, 546, 606, 607, 608, 609, 613, 616, 618, 619, 622, 623, 626, 627, 629, 630, 632, 633, 635, 636, 637, 639, 641, 642, 643, 644, 646, 648, 649, 650, 652, 654, 656, 657, 662], "branches": [[606, 607], [606, 618], [607, 608], [607, 616], [618, 619], [618, 626], [622, 623], [622, 626], [626, 627], [626, 629], [632, 633], [632, 635], [635, 636], [635, 641], [636, 637], [636, 639], [641, 642], [641, 643], [643, 644], [643, 646]]}
# gained: {"lines": [541, 543, 544, 545, 546, 606, 607, 608, 609, 613, 616, 618, 619, 622, 623, 626, 627, 629, 630, 632, 633, 635, 636, 637, 639, 641, 642, 643, 644, 646, 648, 649, 650, 652, 654, 656, 657, 662], "branches": [[606, 607], [606, 618], [607, 608], [607, 616], [618, 619], [618, 626], [622, 623], [626, 627], [626, 629], [632, 633], [632, 635], [635, 636], [635, 641], [636, 637], [636, 639], [641, 642], [641, 643], [643, 644], [643, 646]]}

import pytest
import os
import typing as t
from unittest.mock import patch, MagicMock
from flask import Flask


class TestFlaskRunCoverage:
    """Test cases to cover lines 541-662 in Flask.run() method."""
    
    def test_run_with_flask_run_from_cli_and_not_reloader(self, monkeypatch):
        """Test lines 606-616: FLASK_RUN_FROM_CLI=true and not running from reloader."""
        app = Flask(__name__)
        
        # Set environment to simulate running from CLI
        monkeypatch.setenv("FLASK_RUN_FROM_CLI", "true")
        monkeypatch.delenv("WERKZEUG_RUN_MAIN", raising=False)
        
        with patch('click.secho') as mock_secho:
            app.run()
            
        # Verify warning message was shown
        mock_secho.assert_called_once()
        args, kwargs = mock_secho.call_args
        assert "Ignoring a call to 'app.run()'" in args[0]
        assert kwargs.get("fg") == "red"
    
    def test_run_with_flask_run_from_cli_and_reloader(self, monkeypatch):
        """Test lines 606-616: FLASK_RUN_FROM_CLI=true and running from reloader."""
        app = Flask(__name__)
        
        # Set environment to simulate running from CLI with reloader
        monkeypatch.setenv("FLASK_RUN_FROM_CLI", "true")
        monkeypatch.setenv("WERKZEUG_RUN_MAIN", "true")
        
        with patch('click.secho') as mock_secho:
            app.run()
            
        # Verify no warning message was shown when running from reloader
        mock_secho.assert_not_called()
    
    def test_run_load_dotenv_with_flask_debug(self, monkeypatch):
        """Test lines 618-623: load_dotenv=True with FLASK_DEBUG env var."""
        app = Flask(__name__)
        app.debug = False  # Start with debug disabled
        
        # Set up environment
        monkeypatch.delenv("FLASK_RUN_FROM_CLI", raising=False)
        monkeypatch.setenv("FLASK_DEBUG", "true")
        monkeypatch.setenv("FLASK_SKIP_DOTENV", "false")  # Enable dotenv loading
        
        with patch('flask.cli.load_dotenv') as mock_load_dotenv:
            mock_load_dotenv.return_value = None
            with patch('werkzeug.serving.run_simple') as mock_run:
                app.run(load_dotenv=True)
        
        # Verify debug was set from environment variable
        assert app.debug is True
    
    def test_run_with_debug_parameter_override(self, monkeypatch):
        """Test lines 626-627: debug parameter overrides other sources."""
        app = Flask(__name__)
        app.debug = False  # Start with debug disabled
        
        # Set up conflicting environment
        monkeypatch.delenv("FLASK_RUN_FROM_CLI", raising=False)
        monkeypatch.setenv("FLASK_DEBUG", "false")
        monkeypatch.setenv("FLASK_SKIP_DOTENV", "true")  # Skip dotenv loading
        
        with patch('werkzeug.serving.run_simple') as mock_run:
            app.run(debug=True)
        
        # Verify debug parameter took precedence
        assert app.debug is True
    
    def test_run_server_name_configuration(self, monkeypatch):
        """Test lines 629-646: SERVER_NAME configuration parsing."""
        app = Flask(__name__)
        app.config["SERVER_NAME"] = "example.com:8080"
        
        monkeypatch.delenv("FLASK_RUN_FROM_CLI", raising=False)
        monkeypatch.setenv("FLASK_SKIP_DOTENV", "true")
        
        with patch('werkzeug.serving.run_simple') as mock_run:
            app.run()
            
        # Verify run_simple was called with correct host and port from SERVER_NAME
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert args[0] == "example.com"  # host
        assert args[1] == 8080  # port
    
    def test_run_default_host_and_port(self, monkeypatch):
        """Test lines 635-646: default host and port when no SERVER_NAME."""
        app = Flask(__name__)
        # Ensure no SERVER_NAME is set
        if "SERVER_NAME" in app.config:
            del app.config["SERVER_NAME"]
        
        monkeypatch.delenv("FLASK_RUN_FROM_CLI", raising=False)
        monkeypatch.setenv("FLASK_SKIP_DOTENV", "true")
        
        with patch('werkzeug.serving.run_simple') as mock_run:
            app.run()
            
        # Verify default host and port
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert args[0] == "127.0.0.1"  # default host
        assert args[1] == 5000  # default port
    
    def test_run_custom_host_and_port(self, monkeypatch):
        """Test lines 641-646: custom host and port parameters."""
        app = Flask(__name__)
        
        monkeypatch.delenv("FLASK_RUN_FROM_CLI", raising=False)
        monkeypatch.setenv("FLASK_SKIP_DOTENV", "true")
        
        with patch('werkzeug.serving.run_simple') as mock_run:
            app.run(host="0.0.0.0", port=8000)
            
        # Verify custom host and port were used
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert args[0] == "0.0.0.0"
        assert args[1] == 8000
    
    def test_run_options_defaults_with_debug(self, monkeypatch):
        """Test lines 648-650: default options when debug is True."""
        app = Flask(__name__)
        app.debug = True
        
        monkeypatch.delenv("FLASK_RUN_FROM_CLI", raising=False)
        monkeypatch.setenv("FLASK_SKIP_DOTENV", "true")
        
        with patch('werkzeug.serving.run_simple') as mock_run:
            app.run()
            
        # Verify default options for debug mode
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert kwargs["use_reloader"] is True
        assert kwargs["use_debugger"] is True
        assert kwargs["threaded"] is True
    
    def test_run_options_defaults_without_debug(self, monkeypatch):
        """Test lines 648-650: default options when debug is False."""
        app = Flask(__name__)
        app.debug = False
        
        monkeypatch.delenv("FLASK_RUN_FROM_CLI", raising=False)
        monkeypatch.setenv("FLASK_SKIP_DOTENV", "true")
        
        with patch('werkzeug.serving.run_simple') as mock_run:
            app.run()
            
        # Verify default options for non-debug mode
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert kwargs["use_reloader"] is False
        assert kwargs["use_debugger"] is False
        assert kwargs["threaded"] is True
    
    def test_run_server_banner_called(self, monkeypatch):
        """Test line 652: server banner is shown."""
        app = Flask(__name__)
        
        monkeypatch.delenv("FLASK_RUN_FROM_CLI", raising=False)
        monkeypatch.setenv("FLASK_SKIP_DOTENV", "true")
        
        with patch('flask.cli.show_server_banner') as mock_banner:
            with patch('werkzeug.serving.run_simple'):
                app.run()
            
        # Verify server banner was called
        mock_banner.assert_called_once_with(False, app.name)
    
    def test_run_finally_block_reset_got_first_request(self, monkeypatch):
        """Test lines 656-662: finally block resets _got_first_request."""
        app = Flask(__name__)
        app._got_first_request = True  # Set to True initially
        
        monkeypatch.delenv("FLASK_RUN_FROM_CLI", raising=False)
        monkeypatch.setenv("FLASK_SKIP_DOTENV", "true")
        
        with patch('werkzeug.serving.run_simple'):
            app.run()
            
        # Verify _got_first_request was reset to False
        assert app._got_first_request is False
    
    def test_run_exception_in_run_simple_still_resets(self, monkeypatch):
        """Test lines 656-662: finally block executes even on exception."""
        app = Flask(__name__)
        app._got_first_request = True  # Set to True initially
        
        monkeypatch.delenv("FLASK_RUN_FROM_CLI", raising=False)
        monkeypatch.setenv("FLASK_SKIP_DOTENV", "true")
        
        with patch('werkzeug.serving.run_simple', side_effect=Exception("Test error")):
            with pytest.raises(Exception, match="Test error"):
                app.run()
            
        # Verify _got_first_request was reset to False even on exception
        assert app._got_first_request is False
