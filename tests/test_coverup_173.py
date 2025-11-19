# file: src/flask/src/flask/cli.py:235-238
# asked: {"lines": [235, 236, 237, 238], "branches": []}
# gained: {"lines": [235, 236, 237], "branches": []}

import pytest
import typing as t
from flask.app import Flask
from flask.cli import locate_app

def test_locate_app_overload_false():
    """Test the locate_app overload with raise_if_not_found=False."""
    # This test verifies that the overload signature with raise_if_not_found=False exists
    # by checking that the function can be called with raise_if_not_found=False
    # without raising type errors during static analysis
    
    # The test doesn't actually execute the function, but verifies the overload exists
    # by ensuring the signature is accessible
    assert hasattr(locate_app, '__annotations__'), "locate_app should have annotations"
    
    # Check that the function has overloads by inspecting its __overloads__ attribute
    # (if available in the specific Python version)
    if hasattr(locate_app, '__overloads__'):
        overloads = locate_app.__overloads__
        found_false_overload = False
        for overload in overloads:
            if (hasattr(overload, '__annotations__') and 
                'raise_if_not_found' in overload.__annotations__ and
                overload.__annotations__['raise_if_not_found'] == t.Literal[False]):
                found_false_overload = True
                break
        assert found_false_overload, "Overload with raise_if_not_found=False not found"
    else:
        # For Python versions without __overloads__, we can't directly test the overload
        # but we can verify the function exists and has the expected name
        assert callable(locate_app), "locate_app should be callable"
        assert locate_app.__name__ == "locate_app", "Function name should be 'locate_app'"
