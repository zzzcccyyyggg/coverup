# file: src/flask/src/flask/templating.py:39-49
# asked: {"lines": [39, 40, 45, 46, 47, 48, 49], "branches": [[46, 47], [46, 48]]}
# gained: {"lines": [39, 40, 45, 46, 47, 48, 49], "branches": [[46, 47], [46, 48]]}

import pytest
from flask.templating import Environment
from flask import Flask
from jinja2 import BaseLoader


class MockLoader(BaseLoader):
    def get_source(self, environment, template):
        return "test content", None, lambda: True


def test_environment_init_without_loader():
    """Test Environment.__init__ when loader is not provided in options."""
    app = Flask(__name__)
    
    # Create environment without providing loader
    env = Environment(app)
    
    # Verify that app was stored
    assert env.app is app
    # Verify that a loader was created by the app
    assert env.loader is not None


def test_environment_init_with_loader():
    """Test Environment.__init__ when loader is provided in options."""
    app = Flask(__name__)
    mock_loader = MockLoader()
    
    # Create environment with explicit loader
    env = Environment(app, loader=mock_loader)
    
    # Verify that app was stored
    assert env.app is app
    # Verify that the provided loader was used
    assert env.loader is mock_loader


def test_environment_init_with_other_options():
    """Test Environment.__init__ with additional options passed through."""
    app = Flask(__name__)
    
    # Create environment with additional Jinja2 options
    env = Environment(app, autoescape=True, trim_blocks=True)
    
    # Verify that app was stored
    assert env.app is app
    # Verify that loader was created
    assert env.loader is not None
    # Verify that additional options were passed through
    assert env.autoescape is True
    assert env.trim_blocks is True
