# file: src/flask/src/flask/ctx.py:504-516
# asked: {"lines": [504, 505, 507, 508, 509, 511, 512, 514, 516], "branches": [[507, 508], [507, 516]]}
# gained: {"lines": [504, 505, 507, 508, 509, 511, 512, 514, 516], "branches": [[507, 508], [507, 516]]}

import pytest
import warnings
import flask.ctx


def test_getattr_requestcontext_deprecation():
    """Test that accessing RequestContext triggers deprecation warning and returns AppContext."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = getattr(flask.ctx, "RequestContext")
        
        # Check that deprecation warning was raised
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "'RequestContext' has merged with 'AppContext'" in str(w[0].message)
        assert "Flask 4.0" in str(w[0].message)
        
        # Check that AppContext class is returned
        assert result is flask.ctx.AppContext


def test_getattr_unknown_attribute():
    """Test that accessing unknown attributes raises AttributeError."""
    with pytest.raises(AttributeError, match="unknown_attr"):
        getattr(flask.ctx, "unknown_attr")
