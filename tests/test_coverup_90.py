# file: src/flask/src/flask/templating.py:101-109
# asked: {"lines": [101, 102, 103, 104, 106, 107, 108, 109], "branches": [[103, 104], [103, 106], [106, 0], [106, 107], [108, 106], [108, 109]]}
# gained: {"lines": [101, 102, 103, 104, 106, 107, 108, 109], "branches": [[103, 104], [103, 106], [106, 0], [106, 107], [108, 106], [108, 109]]}

import pytest
from flask import Flask, Blueprint
from flask.templating import DispatchingJinjaLoader
from jinja2 import BaseLoader

class MockLoader(BaseLoader):
    """Mock loader for testing"""
    def get_source(self, environment, template):
        return "test content", None, lambda: True

def test_iter_loaders_with_app_loader_only():
    """Test _iter_loaders when only app has a jinja_loader"""
    app = Flask(__name__)
    app.jinja_loader = MockLoader()
    
    loader = DispatchingJinjaLoader(app)
    result = list(loader._iter_loaders("test.html"))
    
    assert len(result) == 1
    assert result[0][0] is app
    assert result[0][1] is app.jinja_loader

def test_iter_loaders_with_blueprint_loaders():
    """Test _iter_loaders when blueprints have jinja_loaders"""
    app = Flask(__name__)
    app.jinja_loader = MockLoader()
    
    # Create blueprints with jinja_loaders
    bp1 = Blueprint('blueprint1', __name__)
    bp1.jinja_loader = MockLoader()
    app.register_blueprint(bp1)
    
    bp2 = Blueprint('blueprint2', __name__)
    bp2.jinja_loader = MockLoader()
    app.register_blueprint(bp2)
    
    # Create a blueprint without a jinja_loader
    bp3 = Blueprint('blueprint3', __name__)
    app.register_blueprint(bp3)
    
    loader = DispatchingJinjaLoader(app)
    result = list(loader._iter_loaders("test.html"))
    
    # Should include app loader and blueprints with loaders
    assert len(result) == 3
    assert result[0][0] is app
    assert result[0][1] is app.jinja_loader
    assert result[1][0] is bp1
    assert result[1][1] is bp1.jinja_loader
    assert result[2][0] is bp2
    assert result[2][1] is bp2.jinja_loader

def test_iter_loaders_without_app_loader():
    """Test _iter_loaders when app has no jinja_loader but blueprints do"""
    app = Flask(__name__)
    app.jinja_loader = None
    
    # Create blueprints with jinja_loaders
    bp1 = Blueprint('blueprint1', __name__)
    bp1.jinja_loader = MockLoader()
    app.register_blueprint(bp1)
    
    loader = DispatchingJinjaLoader(app)
    result = list(loader._iter_loaders("test.html"))
    
    # Should only include blueprints with loaders
    assert len(result) == 1
    assert result[0][0] is bp1
    assert result[0][1] is bp1.jinja_loader

def test_iter_loaders_no_loaders_at_all():
    """Test _iter_loaders when neither app nor blueprints have jinja_loaders"""
    app = Flask(__name__)
    app.jinja_loader = None
    
    # Create blueprint without jinja_loader
    bp1 = Blueprint('blueprint1', __name__)
    app.register_blueprint(bp1)
    
    loader = DispatchingJinjaLoader(app)
    result = list(loader._iter_loaders("test.html"))
    
    # Should return empty list
    assert len(result) == 0
