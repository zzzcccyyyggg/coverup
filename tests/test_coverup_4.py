# file: src/flask/src/flask/cli.py:41-91
# asked: {"lines": [41, 45, 48, 49, 51, 52, 55, 57, 58, 59, 60, 61, 62, 67, 68, 70, 71, 72, 74, 75, 76, 77, 78, 80, 81, 83, 85, 87, 88, 89], "branches": [[48, 49], [48, 55], [51, 48], [51, 52], [57, 58], [57, 59], [59, 60], [59, 67], [67, 68], [67, 87], [70, 67], [70, 71], [74, 67], [74, 75], [77, 78], [77, 80]]}
# gained: {"lines": [41, 45, 48, 49, 51, 52, 55, 57, 58, 59, 60, 61, 62, 67, 68, 70, 71, 72, 74, 75, 76, 77, 78, 80, 81, 83, 85, 87, 88, 89], "branches": [[48, 49], [48, 55], [51, 48], [51, 52], [57, 58], [57, 59], [59, 60], [59, 67], [67, 68], [67, 87], [70, 67], [70, 71], [74, 75], [77, 78], [77, 80]]}

import pytest
import types
from flask import Flask
from flask.cli import find_best_app, NoAppException

def test_find_best_app_direct_app():
    """Test finding app directly as 'app' attribute."""
    module = types.ModuleType("test_module")
    app = Flask(__name__)
    module.app = app
    result = find_best_app(module)
    assert result is app

def test_find_best_app_direct_application():
    """Test finding app directly as 'application' attribute."""
    module = types.ModuleType("test_module")
    app = Flask(__name__)
    module.application = app
    result = find_best_app(module)
    assert result is app

def test_find_best_app_single_flask_instance():
    """Test finding single Flask instance in module dict."""
    module = types.ModuleType("test_module")
    app = Flask(__name__)
    module.some_app = app
    result = find_best_app(module)
    assert result is app

def test_find_best_app_multiple_flask_instances():
    """Test error when multiple Flask instances found."""
    module = types.ModuleType("test_module")
    app1 = Flask(__name__)
    app2 = Flask(__name__)
    module.app1 = app1
    module.app2 = app2
    with pytest.raises(NoAppException, match="Detected multiple Flask applications"):
        find_best_app(module)

def test_find_best_app_create_app_factory():
    """Test finding app via create_app factory function."""
    module = types.ModuleType("test_module")
    app = Flask(__name__)
    def create_app():
        return app
    module.create_app = create_app
    result = find_best_app(module)
    assert result is app

def test_find_best_app_make_app_factory():
    """Test finding app via make_app factory function."""
    module = types.ModuleType("test_module")
    app = Flask(__name__)
    def make_app():
        return app
    module.make_app = make_app
    result = find_best_app(module)
    assert result is app

def test_find_best_app_factory_wrong_args():
    """Test factory function that requires arguments."""
    module = types.ModuleType("test_module")
    def create_app(config):
        return Flask(__name__)
    module.create_app = create_app
    with pytest.raises(NoAppException, match="could not call it without arguments"):
        find_best_app(module)

def test_find_best_app_factory_type_error_internal():
    """Test factory function that raises TypeError internally."""
    module = types.ModuleType("test_module")
    def create_app():
        raise TypeError("Internal error")
    module.create_app = create_app
    with pytest.raises(TypeError, match="Internal error"):
        find_best_app(module)

def test_find_best_app_no_app_found():
    """Test when no app or factory is found."""
    module = types.ModuleType("test_module")
    with pytest.raises(NoAppException, match="Failed to find Flask application"):
        find_best_app(module)
