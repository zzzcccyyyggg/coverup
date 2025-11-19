# file: src/flask/src/flask/templating.py:57-58
# asked: {"lines": [57, 58], "branches": []}
# gained: {"lines": [57, 58], "branches": []}

import pytest
from flask.templating import DispatchingJinjaLoader
from flask import Flask

def test_dispatching_jinja_loader_init():
    """Test that DispatchingJinjaLoader can be initialized with an app."""
    app = Flask(__name__)
    loader = DispatchingJinjaLoader(app)
    assert loader.app is app
