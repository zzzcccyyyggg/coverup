# file: src/flask/src/flask/sansio/app.py:520-531
# asked: {"lines": [520, 531], "branches": []}
# gained: {"lines": [520, 531], "branches": []}

import pytest
from flask import Flask
from flask.templating import DispatchingJinjaLoader


def test_create_global_jinja_loader():
    """Test that create_global_jinja_loader returns a DispatchingJinjaLoader instance."""
    app = Flask(__name__)
    loader = app.create_global_jinja_loader()
    
    assert isinstance(loader, DispatchingJinjaLoader)
    assert loader.app is app


def test_create_global_jinja_loader_with_blueprints():
    """Test that create_global_jinja_loader works correctly when blueprints are registered."""
    app = Flask(__name__)
    
    # Register a blueprint
    from flask import Blueprint
    bp = Blueprint('test_bp', __name__)
    app.register_blueprint(bp)
    
    loader = app.create_global_jinja_loader()
    
    assert isinstance(loader, DispatchingJinjaLoader)
    assert loader.app is app
