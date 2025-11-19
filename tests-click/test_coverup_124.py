# file: src/click/src/click/core.py:698-716
# asked: {"lines": [698, 708, 709, 711, 712, 714, 716], "branches": [[708, 709], [708, 716], [711, 712], [711, 714]]}
# gained: {"lines": [698, 708, 709, 711, 712, 714, 716], "branches": [[708, 709], [708, 716], [711, 712], [711, 714]]}

import pytest
from click.core import Context
from click._utils import UNSET

class MockCommand:
    def __init__(self):
        self.allow_extra_args = False
        self.allow_interspersed_args = True
        self.ignore_unknown_options = False

def test_lookup_default_without_default_map():
    """Test lookup_default when default_map is None."""
    ctx = Context(command=MockCommand())
    ctx.default_map = None
    
    result = ctx.lookup_default("test_param")
    assert result is UNSET

def test_lookup_default_with_default_map_missing_key():
    """Test lookup_default when default_map exists but key is missing."""
    ctx = Context(command=MockCommand())
    ctx.default_map = {"other_param": "value"}
    
    result = ctx.lookup_default("test_param")
    assert result is UNSET

def test_lookup_default_with_default_map_callable_call_true():
    """Test lookup_default when default_map has a callable and call=True."""
    ctx = Context(command=MockCommand())
    
    def mock_callable():
        return "called_value"
    
    ctx.default_map = {"test_param": mock_callable}
    
    result = ctx.lookup_default("test_param", call=True)
    assert result == "called_value"

def test_lookup_default_with_default_map_callable_call_false():
    """Test lookup_default when default_map has a callable and call=False."""
    ctx = Context(command=MockCommand())
    
    def mock_callable():
        return "called_value"
    
    ctx.default_map = {"test_param": mock_callable}
    
    result = ctx.lookup_default("test_param", call=False)
    assert result is mock_callable

def test_lookup_default_with_default_map_non_callable():
    """Test lookup_default when default_map has a non-callable value."""
    ctx = Context(command=MockCommand())
    ctx.default_map = {"test_param": "static_value"}
    
    result = ctx.lookup_default("test_param")
    assert result == "static_value"

def test_lookup_default_with_default_map_none_value():
    """Test lookup_default when default_map has None value."""
    ctx = Context(command=MockCommand())
    ctx.default_map = {"test_param": None}
    
    result = ctx.lookup_default("test_param")
    assert result is None
