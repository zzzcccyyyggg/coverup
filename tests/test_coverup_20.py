# file: src/flask/src/flask/templating.py:111-123
# asked: {"lines": [111, 112, 113, 114, 115, 117, 118, 119, 120, 121, 123], "branches": [[114, 115], [114, 117], [117, 118], [117, 123], [119, 117], [119, 120], [120, 117], [120, 121]]}
# gained: {"lines": [111, 112, 113, 114, 115, 117, 118, 119, 120, 121, 123], "branches": [[114, 115], [114, 117], [117, 118], [117, 123], [119, 117], [119, 120], [120, 117], [120, 121]]}

import pytest
from flask import Flask, Blueprint
from flask.templating import DispatchingJinjaLoader
from jinja2 import BaseLoader


class MockLoader(BaseLoader):
    def __init__(self, templates):
        self.templates = templates

    def list_templates(self):
        return self.templates


def test_dispatching_jinja_loader_list_templates_no_loaders():
    """Test list_templates when no loaders are available."""
    app = Flask(__name__)
    app.jinja_loader = None
    
    loader = DispatchingJinjaLoader(app)
    result = loader.list_templates()
    
    assert result == []


def test_dispatching_jinja_loader_list_templates_app_loader_only():
    """Test list_templates with only app loader."""
    app = Flask(__name__)
    app.jinja_loader = MockLoader(['app_template1.html', 'app_template2.html'])
    
    loader = DispatchingJinjaLoader(app)
    result = loader.list_templates()
    
    assert sorted(result) == ['app_template1.html', 'app_template2.html']


def test_dispatching_jinja_loader_list_templates_blueprint_loaders_only():
    """Test list_templates with only blueprint loaders."""
    app = Flask(__name__)
    app.jinja_loader = None
    
    # Create blueprints with loaders
    bp1 = Blueprint('bp1', __name__)
    bp1.jinja_loader = MockLoader(['bp1_template1.html', 'bp1_template2.html'])
    
    bp2 = Blueprint('bp2', __name__)
    bp2.jinja_loader = MockLoader(['bp2_template1.html'])
    
    app.register_blueprint(bp1)
    app.register_blueprint(bp2)
    
    loader = DispatchingJinjaLoader(app)
    result = loader.list_templates()
    
    expected = ['bp1_template1.html', 'bp1_template2.html', 'bp2_template1.html']
    assert sorted(result) == sorted(expected)


def test_dispatching_jinja_loader_list_templates_mixed_loaders():
    """Test list_templates with both app and blueprint loaders."""
    app = Flask(__name__)
    app.jinja_loader = MockLoader(['app_template1.html', 'common.html'])
    
    # Create blueprints with loaders
    bp1 = Blueprint('bp1', __name__)
    bp1.jinja_loader = MockLoader(['bp1_template1.html', 'common.html'])
    
    bp2 = Blueprint('bp2', __name__)
    bp2.jinja_loader = MockLoader(['bp2_template1.html'])
    
    app.register_blueprint(bp1)
    app.register_blueprint(bp2)
    
    loader = DispatchingJinjaLoader(app)
    result = loader.list_templates()
    
    expected = ['app_template1.html', 'common.html', 'bp1_template1.html', 'bp2_template1.html']
    assert sorted(result) == sorted(expected)


def test_dispatching_jinja_loader_list_templates_blueprint_without_loader():
    """Test list_templates with blueprints that don't have loaders."""
    app = Flask(__name__)
    app.jinja_loader = MockLoader(['app_template.html'])
    
    # Create blueprint without loader
    bp1 = Blueprint('bp1', __name__)
    bp1.jinja_loader = None
    
    # Create blueprint with loader
    bp2 = Blueprint('bp2', __name__)
    bp2.jinja_loader = MockLoader(['bp2_template.html'])
    
    app.register_blueprint(bp1)
    app.register_blueprint(bp2)
    
    loader = DispatchingJinjaLoader(app)
    result = loader.list_templates()
    
    expected = ['app_template.html', 'bp2_template.html']
    assert sorted(result) == sorted(expected)
