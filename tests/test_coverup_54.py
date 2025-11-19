# file: src/flask/src/flask/templating.py:22-36
# asked: {"lines": [22, 26, 27, 29, 30, 32, 33, 34, 36], "branches": [[29, 30], [29, 36], [32, 33], [32, 36]]}
# gained: {"lines": [22, 26, 27, 29, 30, 32, 33, 34, 36], "branches": [[29, 30], [29, 36], [32, 33], [32, 36]]}

import pytest
import typing as t
from flask.globals import _cv_app
from flask.templating import _default_template_ctx_processor

class MockAppContext:
    def __init__(self, g=None, has_request=False, request=None, session=None):
        self.g = g
        self.has_request = has_request
        self.request = request
        self.session = session

def test_default_template_ctx_processor_no_context():
    """Test _default_template_ctx_processor when no app context is set."""
    # Ensure no app context is set
    if _cv_app.get(None) is not None:
        pytest.skip("App context is already set, cannot test no context scenario")
    
    result = _default_template_ctx_processor()
    assert result == {}

def test_default_template_ctx_processor_with_context_no_request():
    """Test _default_template_ctx_processor with app context but no request."""
    mock_g = type('MockG', (), {})()
    mock_ctx = MockAppContext(g=mock_g, has_request=False)
    
    # Set the app context
    token = _cv_app.set(mock_ctx)
    try:
        result = _default_template_ctx_processor()
        assert result == {"g": mock_g}
    finally:
        _cv_app.reset(token)

def test_default_template_ctx_processor_with_context_and_request():
    """Test _default_template_ctx_processor with app context and request."""
    mock_g = type('MockG', (), {})()
    mock_request = type('MockRequest', (), {})()
    mock_session = type('MockSession', (), {})()
    mock_ctx = MockAppContext(
        g=mock_g, 
        has_request=True, 
        request=mock_request, 
        session=mock_session
    )
    
    # Set the app context
    token = _cv_app.set(mock_ctx)
    try:
        result = _default_template_ctx_processor()
        expected = {
            "g": mock_g,
            "request": mock_request,
            "session": mock_session
        }
        assert result == expected
    finally:
        _cv_app.reset(token)
