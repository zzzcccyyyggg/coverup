# file: src/flask/src/flask/sansio/app.py:594-599
# asked: {"lines": [594, 599], "branches": []}
# gained: {"lines": [594, 599], "branches": []}

import pytest
from flask import Flask
from flask.sansio.blueprints import Blueprint

class TestAppIterBlueprints:
    """Test cases for App.iter_blueprints method."""
    
    def test_iter_blueprints_empty(self):
        """Test iter_blueprints returns empty values view when no blueprints registered."""
        app = Flask(__name__)
        blueprints = app.iter_blueprints()
        assert len(list(blueprints)) == 0
        assert isinstance(blueprints, type(app.blueprints.values()))
    
    def test_iter_blueprints_with_registered_blueprints(self):
        """Test iter_blueprints returns all registered blueprints in order of registration."""
        app = Flask(__name__)
        
        # Create multiple blueprints
        bp1 = Blueprint('bp1', __name__)
        bp2 = Blueprint('bp2', __name__)
        bp3 = Blueprint('bp3', __name__)
        
        # Register blueprints by directly adding to the blueprints dict
        # This avoids the complex registration process that requires CLI
        app.blueprints['bp1'] = bp1
        app.blueprints['bp2'] = bp2
        app.blueprints['bp3'] = bp3
        
        # Get blueprints through iter_blueprints
        blueprints = app.iter_blueprints()
        blueprint_list = list(blueprints)
        
        # Verify we get all blueprints
        assert len(blueprint_list) == 3
        assert bp1 in blueprint_list
        assert bp2 in blueprint_list
        assert bp3 in blueprint_list
        
        # Verify the order matches insertion order (Python 3.7+ dicts maintain insertion order)
        assert blueprint_list[0] == bp1
        assert blueprint_list[1] == bp2
        assert blueprint_list[2] == bp3
    
    def test_iter_blueprints_after_blueprint_addition(self):
        """Test iter_blueprints reflects changes when blueprints are added."""
        app = Flask(__name__)
        
        bp1 = Blueprint('bp1', __name__)
        bp2 = Blueprint('bp2', __name__)
        
        # Add first blueprint
        app.blueprints['bp1'] = bp1
        
        # Verify first blueprint is present
        blueprints = list(app.iter_blueprints())
        assert len(blueprints) == 1
        assert bp1 in blueprints
        
        # Add second blueprint
        app.blueprints['bp2'] = bp2
        
        # Verify both blueprints are present
        blueprints_after = list(app.iter_blueprints())
        assert len(blueprints_after) == 2
        assert bp1 in blueprints_after
        assert bp2 in blueprints_after
    
    def test_iter_blueprints_return_type(self):
        """Test iter_blueprints returns the correct type (ValuesView)."""
        app = Flask(__name__)
        
        bp1 = Blueprint('bp1', __name__)
        app.blueprints['bp1'] = bp1
        
        blueprints = app.iter_blueprints()
        
        # Verify it returns a ValuesView
        assert hasattr(blueprints, '__iter__')
        assert isinstance(blueprints, type(app.blueprints.values()))
        
        # Verify we can iterate over it
        blueprint_list = list(blueprints)
        assert len(blueprint_list) == 1
        assert blueprint_list[0] == bp1
