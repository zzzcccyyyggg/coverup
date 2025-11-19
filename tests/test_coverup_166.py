# file: src/flask/src/flask/sansio/blueprints.py:213-221
# asked: {"lines": [213, 214, 215, 216, 217], "branches": [[214, 0], [214, 215]]}
# gained: {"lines": [213, 214, 215, 216, 217], "branches": [[214, 0], [214, 215]]}

import pytest
from flask import Flask
from flask.sansio.blueprints import Blueprint

class TestBlueprintSetupFinished:
    def test_check_setup_finished_raises_when_registered(self):
        """Test that _check_setup_finished raises AssertionError when blueprint has been registered."""
        bp = Blueprint('test_bp', __name__)
        bp._got_registered_once = True
        
        with pytest.raises(AssertionError) as exc_info:
            bp._check_setup_finished('test_method')
        
        expected_msg = (
            "The setup method 'test_method' can no longer be called on the blueprint 'test_bp'. "
            "It has already been registered at least once, any changes will not be applied consistently.\n"
            "Make sure all imports, decorators, functions, etc. needed to set up the blueprint are done before registering it."
        )
        assert str(exc_info.value) == expected_msg

    def test_check_setup_finished_passes_when_not_registered(self):
        """Test that _check_setup_finished passes when blueprint has not been registered."""
        bp = Blueprint('test_bp', __name__)
        bp._got_registered_once = False
        
        # This should not raise an exception
        bp._check_setup_finished('test_method')

    def test_setupmethod_decorator_triggers_check(self):
        """Test that methods decorated with @setupmethod call _check_setup_finished."""
        bp = Blueprint('test_bp', __name__)
        bp._got_registered_once = True
        
        # Try to call a setup method after registration
        with pytest.raises(AssertionError) as exc_info:
            bp.record(lambda state: None)
        
        assert "The setup method 'record'" in str(exc_info.value)
        assert "test_bp" in str(exc_info.value)

    def test_register_blueprint_after_registration_fails(self):
        """Test that register_blueprint fails after blueprint has been registered."""
        bp = Blueprint('test_bp', __name__)
        nested_bp = Blueprint('nested_bp', __name__)
        
        # Simulate registration by setting the flag directly
        bp._got_registered_once = True
        
        # Attempt to register a nested blueprint should fail
        with pytest.raises(AssertionError) as exc_info:
            bp.register_blueprint(nested_bp)
        
        assert "The setup method 'register_blueprint'" in str(exc_info.value)
        assert "test_bp" in str(exc_info.value)

    def test_add_url_rule_after_registration_fails(self):
        """Test that add_url_rule fails after blueprint has been registered."""
        bp = Blueprint('test_bp', __name__)
        
        # Simulate registration by setting the flag directly
        bp._got_registered_once = True
        
        # Attempt to add a URL rule should fail
        with pytest.raises(AssertionError) as exc_info:
            bp.add_url_rule('/test', 'test_endpoint')
        
        assert "The setup method 'add_url_rule'" in str(exc_info.value)
        assert "test_bp" in str(exc_info.value)
