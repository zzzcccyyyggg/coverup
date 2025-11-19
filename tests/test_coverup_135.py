# file: src/flask/src/flask/app.py:722-737
# asked: {"lines": [722, 732, 734, 735, 737], "branches": [[734, 735], [734, 737]]}
# gained: {"lines": [722, 732, 734, 735, 737], "branches": [[734, 735], [734, 737]]}

import pytest
from flask import Flask
from flask.testing import FlaskCliRunner


class TestFlaskTestCliRunner:
    """Test cases for Flask.test_cli_runner method."""

    def test_test_cli_runner_default_class(self):
        """Test test_cli_runner returns FlaskCliRunner when test_cli_runner_class is None."""
        app = Flask(__name__)
        app.test_cli_runner_class = None
        
        runner = app.test_cli_runner()
        
        assert isinstance(runner, FlaskCliRunner)
        assert runner.app is app

    def test_test_cli_runner_custom_class(self):
        """Test test_cli_runner returns custom runner class when test_cli_runner_class is set."""
        app = Flask(__name__)
        
        class CustomCliRunner(FlaskCliRunner):
            def __init__(self, app, **kwargs):
                super().__init__(app, **kwargs)
                self.custom_attr = "custom"
        
        app.test_cli_runner_class = CustomCliRunner
        
        runner = app.test_cli_runner()
        
        assert isinstance(runner, CustomCliRunner)
        assert runner.app is app
        assert runner.custom_attr == "custom"

    def test_test_cli_runner_with_kwargs(self):
        """Test test_cli_runner passes kwargs to the runner constructor."""
        app = Flask(__name__)
        app.test_cli_runner_class = None
        
        runner = app.test_cli_runner(echo_stdin=True, charset='utf-16')
        
        assert isinstance(runner, FlaskCliRunner)
        assert runner.app is app
        # Verify kwargs were passed to CliRunner
        assert runner.echo_stdin is True
        assert runner.charset == 'utf-16'
