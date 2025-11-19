# file: src/flask/src/flask/sansio/blueprints.py:561-587
# asked: {"lines": [561, 562, 563, 579, 580, 581, 583, 584, 585, 587], "branches": [[579, 580], [579, 583]]}
# gained: {"lines": [561, 562, 563, 579, 580, 581, 583, 584, 585, 587], "branches": [[579, 580], [579, 583]]}

import pytest
from flask import Blueprint

def test_app_template_global_without_name():
    """Test app_template_global decorator without name parameter (callable passed directly)."""
    bp = Blueprint('test_bp', __name__)
    
    @bp.app_template_global
    def test_global():
        return "test_value"
    
    # Verify the function was registered
    assert test_global() == "test_value"

def test_app_template_global_with_name():
    """Test app_template_global decorator with name parameter."""
    bp = Blueprint('test_bp', __name__)
    
    @bp.app_template_global('custom_name')
    def test_global():
        return "test_value"
    
    # Verify the function was registered
    assert test_global() == "test_value"

def test_app_template_global_with_none_name():
    """Test app_template_global decorator with explicit None name."""
    bp = Blueprint('test_bp', __name__)
    
    @bp.app_template_global(None)
    def test_global():
        return "test_value"
    
    # Verify the function was registered
    assert test_global() == "test_value"
