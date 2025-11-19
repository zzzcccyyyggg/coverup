# file: src/flask/src/flask/config.py:366-367
# asked: {"lines": [366, 367], "branches": []}
# gained: {"lines": [366, 367], "branches": []}

import pytest
from flask import Config


def test_config_repr():
    """Test that Config.__repr__ returns the expected format."""
    config = Config("/some/path")
    config["DEBUG"] = True
    config["SECRET_KEY"] = "test_key"
    
    result = repr(config)
    
    assert result.startswith("<Config ")
    assert "DEBUG" in result
    assert "SECRET_KEY" in result
    assert result.endswith(">")
