# file: src/flask/src/flask/sansio/blueprints.py:255-271
# asked: {"lines": [255, 256, 269, 270, 271], "branches": [[269, 270], [269, 271]]}
# gained: {"lines": [255, 256, 269, 270, 271], "branches": [[269, 270], [269, 271]]}

import pytest
from flask.sansio.blueprints import Blueprint

class TestBlueprintRegisterBlueprint:
    def test_register_blueprint_on_itself_raises_error(self):
        """Test that registering a blueprint on itself raises ValueError."""
        blueprint = Blueprint('test', __name__)
        
        with pytest.raises(ValueError, match="Cannot register a blueprint on itself"):
            blueprint.register_blueprint(blueprint)
    
    def test_register_blueprint_successfully(self):
        """Test that registering a blueprint successfully adds it to _blueprints."""
        parent_blueprint = Blueprint('parent', __name__)
        child_blueprint = Blueprint('child', __name__)
        
        # Register child blueprint on parent with some options
        parent_blueprint.register_blueprint(child_blueprint, url_prefix='/child')
        
        # Verify the blueprint was added to _blueprints with correct options
        assert len(parent_blueprint._blueprints) == 1
        assert parent_blueprint._blueprints[0][0] is child_blueprint
        assert parent_blueprint._blueprints[0][1] == {'url_prefix': '/child'}
    
    def test_register_blueprint_with_multiple_options(self):
        """Test registering blueprint with multiple options."""
        parent_blueprint = Blueprint('parent', __name__)
        child_blueprint = Blueprint('child', __name__)
        
        # Register with multiple options
        parent_blueprint.register_blueprint(
            child_blueprint, 
            url_prefix='/api', 
            subdomain='api',
            name='custom_name'
        )
        
        # Verify the blueprint was added with all options
        assert len(parent_blueprint._blueprints) == 1
        assert parent_blueprint._blueprints[0][0] is child_blueprint
        assert parent_blueprint._blueprints[0][1] == {
            'url_prefix': '/api',
            'subdomain': 'api',
            'name': 'custom_name'
        }
